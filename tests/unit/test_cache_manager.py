import pytest
import os
import json
from datetime import datetime, timedelta
from services.cache import CacheManager

@pytest.fixture
def cache_mgr(tmp_path):
    cache_file = tmp_path / "test_cache.json"
    return CacheManager(cache_file=str(cache_file))

def test_normalize_goal(cache_mgr):
    assert cache_mgr.normalize_goal("Open Edge, and go to google.com!") == "open edge and go to google.com"
    assert cache_mgr.normalize_goal("Search * for stuff") == "search * for stuff"

def test_record_and_promote(cache_mgr):
    goal = "open edge and go to google.com"
    calls = [
        {"name": "launch_app", "args": {"path": "msedge.exe", "args": ["google.com"]}},
        {"name": "wait", "args": {"seconds": 5}}
    ]

    # Hits: 1
    cache_mgr.record_success(goal, calls)
    assert len(cache_mgr.cache) == 0
    assert len(cache_mgr.pending) == 1

    # Hits: 2
    cache_mgr.record_success(goal, calls)
    assert len(cache_mgr.cache) == 0

    # Hits: 3 -> Promote
    cache_mgr.record_success(goal, calls)
    assert len(cache_mgr.cache) == 1
    assert len(cache_mgr.pending) == 0

    # Check pattern (google.com should be replaced with *)
    pattern = list(cache_mgr.cache.keys())[0]
    assert "*" in pattern
    assert "google" not in pattern

def test_match_and_reconstruct(cache_mgr):
    # Setup cache manually for testing
    cache_mgr.cache["open edge and go to *"] = {
        "hits": 5,
        "last_used": datetime.now().isoformat(),
        "compact_plan": ["la:msedge.exe:{var0}", "wait:5"],
        "variables": ["var0"]
    }

    reconstructed = cache_mgr.match_and_reconstruct("open edge and go to bing.com")
    assert reconstructed is not None
    assert len(reconstructed) == 2
    assert reconstructed[0]["name"] == "launch_app"
    assert reconstructed[0]["args"]["args"] == ["bing.com"]
    assert reconstructed[1]["args"]["seconds"] == 5

def test_eviction_hit_count(cache_mgr):
    cache_mgr.max_entries = 2

    # Fill cache
    cache_mgr.cache["p1"] = {"hits": 10, "last_used": datetime.now().isoformat(), "compact_plan": [], "variables": []}
    cache_mgr.cache["p2"] = {"hits": 5, "last_used": datetime.now().isoformat(), "compact_plan": [], "variables": []}

    # Add p3 via promotion (hits=1 for testing promotion)
    cache_mgr.promotion_threshold = 1
    cache_mgr.record_success("p3", [])

    assert len(cache_mgr.cache) == 2
    assert "p1" in cache_mgr.cache
    assert "p3" in cache_mgr.cache
    assert "p2" not in cache_mgr.cache # Evicted (lowest hits)

def test_eviction_expiry(cache_mgr, tmp_path):
    cache_file = tmp_path / "expiry_cache.json"
    old_date = (datetime.now() - timedelta(days=31)).isoformat()

    data = {
        "cache": {
            "old": {"hits": 100, "last_used": old_date, "compact_plan": [], "variables": []},
            "new": {"hits": 1, "last_used": datetime.now().isoformat(), "compact_plan": [], "variables": []}
        },
        "pending": {}
    }

    with open(cache_file, 'w') as f:
        json.dump(data, f)

    cache_mgr.load_cache(str(cache_file))
    assert "old" not in cache_mgr.cache
    assert "new" in cache_mgr.cache

def test_get_cache_block(cache_mgr):
    cache_mgr.cache["search google for *"] = {"hits": 10, "compact_plan": ["la:msedge:google.com", "swa:google:{var0}"], "variables": ["var0"]}
    cache_mgr.cache["open *"] = {"hits": 20, "compact_plan": ["la:{var0}"], "variables": ["var0"]}

    block = cache_mgr.get_cache_block()
    assert "CACHE:" in block
    assert "1. open * → [la:{var0}]" in block
    assert "2. search google for * → [la:msedge:google.com,swa:google:{var0}]" in block
