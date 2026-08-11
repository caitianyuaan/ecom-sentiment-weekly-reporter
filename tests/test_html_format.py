#!/usr/bin/env python3
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HTMLFormatTests(unittest.TestCase):
    def test_sample_config_exposes_compact_html_defaults(self):
        config = json.loads((ROOT / "references" / "sample-config.template.json").read_text(encoding="utf-8"))
        html = config["output"]["html"]
        self.assertEqual(html["layout"], "consulting_compact")
        self.assertTrue(html["combine_markets"])
        self.assertFalse(html["include_images"])

    def test_html_reference_preserves_density_and_date_integrity(self):
        reference = (ROOT / "references" / "report-format-html.md").read_text(encoding="utf-8")
        self.assertIn("Do not reserve a fixed left sidebar", reference)
        self.assertIn("2-4 factual sentences", reference)
        self.assertIn("Do not include older background research", reference)
        self.assertIn("Default to no images", reference)


if __name__ == "__main__":
    unittest.main()
