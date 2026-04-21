import json
import os
from datetime import datetime

class FailureMemory:
    def __init__(self, memory_file: str = os.path.join("FI_NEURAL_LINK", "data", "failure_memory.json")):
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        self.memory_file = memory_file
        self.failures = {} # key: domain, value: list of failures
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.failures = json.load(f)
            except:
                self.failures = {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.failures, f, indent=2)

    def record_failure(self, domain: str, instruction: str, error: str):
        if domain not in self.failures:
            self.failures[domain] = []

        self.failures[domain].append({
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "error": error
        })
        # Keep only last 5 failures per domain
        self.failures[domain] = self.failures[domain][-5:]
        self.save_memory()

    def get_failures(self, domain: str) -> list:
        return self.failures.get(domain, [])

    def get_failure_block(self, domain: str) -> str:
        domain_failures = self.get_failures(domain)
        if not domain_failures:
            return ""

        lines = [f"PREVIOUS FAILURES ON {domain}:"]
        for f in domain_failures:
            lines.append(f"- Instruction: {f['instruction']} | Error: {f['error']}")
        return "\n".join(lines)
