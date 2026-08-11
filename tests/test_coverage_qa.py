#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("summarize_coverage", ROOT / "scripts" / "summarize_coverage.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CoverageQATests(unittest.TestCase):
    def test_distinguishes_rejected_from_not_searched(self):
        config = {
            "markets": ["US"],
            "platforms": ["Amazon", "Temu"],
            "topics": ["returns", "delivery"],
            "coverage_qa": {"source_concentration_warning_share": 0.6},
        }
        queries = [{"market": "US", "platform": "Amazon", "topic": "returns", "inspected_count": 2}]
        candidates = [{"id": "a", "market": "US", "platform": "Amazon", "topic": "returns", "source": "Reuters"}]
        selection = {"selected": [], "rejected": [{"id": "a", "reason_code": "outside_window"}]}

        result = MODULE.summarize(config, queries, candidates, selection)
        platform_states = {row["platform"]: row["state"] for row in result["dimensions"]["platform"]}
        self.assertEqual(platform_states, {"Amazon": "candidates_rejected", "Temu": "not_searched"})
        self.assertEqual(result["rejection_reasons"], {"outside_window": 1})

    def test_source_concentration_ignores_tiny_samples(self):
        config = {
            "markets": ["US"],
            "platforms": ["Amazon"],
            "topics": ["returns"],
            "coverage_qa": {
                "source_concentration_warning_share": 0.6,
                "source_concentration_min_items": 3,
            },
        }
        candidates = [{"id": "a", "market": "US", "platform": "Amazon", "topic": "returns", "source": "Reuters"}]
        result = MODULE.summarize(config, [], candidates, {"selected": [], "rejected": []})
        self.assertFalse(any(warning.startswith("source_concentration:") for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
