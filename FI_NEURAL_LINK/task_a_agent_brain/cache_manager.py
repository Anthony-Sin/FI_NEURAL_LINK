import json
import os
import re
import fnmatch
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple

class CacheManager:
    def __init__(self, cache_file: str = os.path.join("FI_NEURAL_LINK", "data", "command_cache.json")):
        # Ensure data directory exists
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        self.cache_file = cache_file
        # key: pattern, value: {hits, last_used, compact_plan, variables}
        self.cache: Dict[str, Dict[str, Any]] = {}
        # key: pattern, value: {hits, last_used, compact_plan, variables}
        self.pending: Dict[str, Dict[str, Any]] = {}
        self.max_entries = 15
        self.promotion_threshold = 3

    def normalize_goal(self, goal: str) -> str:
        """Lowercase and strip punctuation."""
        if not goal: return ""
        # Remove punctuation except * which is our wildcard and . for URLs
        clean = re.sub(r'[^\w\s\*\.]', '', goal.lower())
        return " ".join(clean.split())

    def _get_compact_name(self, name: str) -> str:
        mapping = {
            "launch_app": "la",
            "smart_web_action": "swa",
            "type_text": "tt",
            "open_url": "ou",
            "click_element": "ce",
            "type_in_element": "te",
            "save_webpage_structure": "sws"
        }
        return mapping.get(name, name)

    def _get_full_name(self, compact_name: str) -> str:
        mapping = {
            "la": "launch_app",
            "swa": "smart_web_action",
            "tt": "type_text",
            "ou": "open_url",
            "ce": "click_element",
            "te": "type_in_element",
            "sws": "save_webpage_structure"
        }
        return mapping.get(compact_name, compact_name)

    def _serialize_call(self, call: Dict[str, Any], variables: Dict[str, str]) -> str:
        """Converts a function call to a compact string."""
        name = self._get_compact_name(call["name"])
        args = call.get("args", {})

        # Define arg order for each tool for consistent serialization
        arg_order = {
            "la": ["path", "args"],
            "wait": ["seconds"],
            "swa": ["url_domain", "instruction", "expected_title_re"],
            "click": ["x", "y"],
            "tt": ["text", "interval"],
            "ou": ["url"],
            "ce": ["window_title", "control_title"],
            "te": ["window_title", "control_title", "text", "enter"],
            "sws": ["url", "filename"]
        }

        parts = [name]
        for arg_name in arg_order.get(name, args.keys()):
            val = args.get(arg_name, "")

            # Check if this value (or part of it) is one of our variables
            str_val = str(val)
            for var_name, var_val in variables.items():
                if var_val and var_val in str_val:
                    str_val = str_val.replace(var_val, f"{{{var_name}}}")

            # For lists, join with comma
            if isinstance(val, list):
                # Apply variable replacement to list items too
                list_vals = []
                for item in val:
                    s_item = str(item)
                    for var_name, var_val in variables.items():
                        if var_val and var_val in s_item:
                            s_item = s_item.replace(var_val, f"{{{var_name}}}")
                    list_vals.append(s_item)
                str_val = ",".join(list_vals)

            parts.append(str_val)

        return ":".join(parts)

    def _deserialize_call(self, compact_str: str, slots: Dict[str, str]) -> Dict[str, Any]:
        """Converts a compact string back to a function call, filling slots."""
        parts = compact_str.split(":")
        name = self._get_full_name(parts[0])
        raw_args = parts[1:]

        # Fill slots in raw args
        filled_args = []
        for arg in raw_args:
            for slot_name, val in slots.items():
                arg = arg.replace(f"{{{slot_name}}}", val)
            filled_args.append(arg)

        arg_mapping = {
            "launch_app": ["path", "args"],
            "wait": ["seconds"],
            "smart_web_action": ["url_domain", "instruction", "expected_title_re"],
            "click": ["x", "y"],
            "type_text": ["text", "interval"],
            "open_url": ["url"],
            "click_element": ["window_title", "control_title"],
            "type_in_element": ["window_title", "control_title", "text", "enter"],
            "save_webpage_structure": ["url", "filename"]
        }

        call_args = {}
        expected_args = arg_mapping.get(name, [])
        for i, arg_val in enumerate(filled_args):
            if i < len(expected_args):
                arg_name = expected_args[i]

                # Type conversion
                if arg_name == "args": # List for launch_app
                    call_args[arg_name] = arg_val.split(",") if arg_val else []
                elif arg_name in ["seconds", "x", "y", "interval"]:
                    try: call_args[arg_name] = float(arg_val) if "." in arg_val else int(arg_val)
                    except: call_args[arg_name] = arg_val
                elif arg_name == "enter":
                    call_args[arg_name] = arg_val.lower() == "true"
                else:
                    call_args[arg_name] = arg_val

        return {"name": name, "args": call_args}

    def record_success(self, goal: str, function_calls: List[Dict[str, Any]]) -> None:
        """Tracks a successful goal and its plan, promoting to cache if threshold met."""
        norm_goal = self.normalize_goal(goal)
        if not norm_goal: return

        # 1. Identify variables (values in calls that are also in goal)
        variables = {}
        temp_goal = norm_goal

        # Simple heuristic: look for strings longer than 3 chars in args that are in goal
        # Sort candidates by length to avoid partial matches
        candidates = []
        for call in function_calls:
            for arg_name, arg_val in call.get("args", {}).items():
                vals = arg_val if isinstance(arg_val, list) else [arg_val]
                for v in vals:
                    s_v = str(v)
                    if len(s_v) > 3 and s_v in temp_goal:
                        candidates.append((s_v, arg_name))

        candidates.sort(key=lambda x: len(x[0]), reverse=True)

        for s_v, arg_name in candidates:
            # Important: Replace occurrences one-by-one to keep vars synced with *
            while s_v in temp_goal:
                # Map descriptive names if possible
                var_base = arg_name
                if arg_name == "args": var_base = "url"
                if arg_name == "text": var_base = "q"

                # Ensure uniqueness
                var_name = var_base
                counter = 1
                while var_name in variables:
                    var_name = f"{var_base}{counter}"
                    counter += 1

                variables[var_name] = s_v
                # Replace only FIRST occurrence with *
                temp_goal = temp_goal.replace(s_v, "*", 1)

        pattern = temp_goal
        compact_plan = [self._serialize_call(c, variables) for c in function_calls]
        var_names = list(variables.keys())

        # Check if we already have this pattern
        if pattern in self.cache:
            self.cache[pattern]["hits"] += 1
            self.cache[pattern]["last_used"] = datetime.now().isoformat()
            # Update plan in case it changed/improved?
            # For now keep original.
        else:
            # Check if pending
            if pattern in self.pending:
                self.pending[pattern]["hits"] += 1
                self.pending[pattern]["last_used"] = datetime.now().isoformat()

                if self.pending[pattern]["hits"] >= self.promotion_threshold:
                    # Promote!
                    self._promote(pattern)
            else:
                self.pending[pattern] = {
                    "hits": 1,
                    "last_used": datetime.now().isoformat(),
                    "compact_plan": compact_plan,
                    "variables": var_names
                }
                # If only 1 hit threshold (for testing), promote immediately
                if self.promotion_threshold <= 1:
                    self._promote(pattern)

    def _promote(self, pattern: str) -> None:
        if pattern not in self.pending: return

        # Eviction logic if cache full
        if len(self.cache) >= self.max_entries:
            # Evict entry with lowest hit count
            lowest_pattern = min(self.cache.keys(), key=lambda k: self.cache[k]["hits"])
            del self.cache[lowest_pattern]

        self.cache[pattern] = self.pending.pop(pattern)

    def match_and_reconstruct(self, goal: str) -> Optional[List[Dict[str, Any]]]:
        """Matches a goal against the cache and returns a reconstructed plan."""
        norm_goal = self.normalize_goal(goal)

        # Sort cache by hit count descending for prioritization
        sorted_patterns = sorted(self.cache.keys(), key=lambda k: self.cache[k]["hits"], reverse=True)

        for pattern in sorted_patterns:
            if fnmatch.fnmatch(norm_goal, pattern):
                # Found a hit!
                entry = self.cache[pattern]

                # Extract slot values
                slots = self._extract_slots(norm_goal, pattern, entry["variables"])
                if slots is None: continue

                # Reconstruct plan
                try:
                    reconstructed = [self._deserialize_call(c, slots) for c in entry["compact_plan"]]

                    # Update usage stats
                    entry["hits"] += 1
                    entry["last_used"] = datetime.now().isoformat()
                    return reconstructed
                except Exception:
                    continue

        return None

    def _extract_slots(self, goal: str, pattern: str, var_names: List[str]) -> Optional[Dict[str, str]]:
        """Extracts values from goal based on glob pattern and variable names."""
        # Convert glob pattern to regex with capturing groups
        # Escaping regex special chars in pattern, then replacing \* with (.*)
        regex_pattern = re.escape(pattern).replace(r"\*", "(.*)")
        match = re.match(f"^{regex_pattern}$", goal)

        if not match: return None

        captured_groups = match.groups()
        if len(captured_groups) != len(var_names):
            return None # Should not happen if pattern and variables are synced

        return {var_names[i]: captured_groups[i] for i in range(len(var_names))}

    def get_cache_block(self) -> str:
        """Returns a compact string representation of the top 5 cache entries."""
        top_5 = sorted(self.cache.items(), key=lambda x: x[1]["hits"], reverse=True)[:5]
        if not top_5: return ""

        lines = ["CACHE:"]
        for i, (pattern, entry) in enumerate(top_5, 1):
            plan_str = ",".join(entry["compact_plan"])
            line = f"{i}. {pattern} → [{plan_str}]"
            lines.append(line)

        return "\n".join(lines)

    def save_cache(self, filepath: Optional[str] = None) -> None:
        path = filepath or self.cache_file
        data = {
            "cache": self.cache,
            "pending": self.pending
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_cache(self, filepath: Optional[str] = None) -> None:
        path = filepath or self.cache_file
        if not os.path.exists(path): return

        with open(path, 'r') as f:
            data = json.load(f)
            self.cache = data.get("cache", {})
            self.pending = data.get("pending", {})

        # Eviction of old entries (> 30 days)
        now = datetime.now()
        expiry_limit = now - timedelta(days=30)

        to_delete = []
        for pattern, entry in self.cache.items():
            last_used = datetime.fromisoformat(entry["last_used"])
            if last_used < expiry_limit:
                to_delete.append(pattern)

        for p in to_delete:
            del self.cache[p]
