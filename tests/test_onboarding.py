#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SPEC = importlib.util.spec_from_file_location("init_user_config", ROOT / "scripts" / "init_user_config.py")
INIT_MODULE = importlib.util.module_from_spec(INIT_SPEC)
INIT_SPEC.loader.exec_module(INIT_MODULE)


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "references" / "sample-config.template.json").read_text(encoding="utf-8"))

    def test_recommended_template_is_local_ready(self):
        self.assertEqual(INIT_MODULE.validate_config(self.config), [])
        self.assertTrue(self.config["delivery"]["local"])
        self.assertFalse(self.config["delivery"]["feishu_group"])
        self.assertFalse(self.config["delivery"]["feishu_archive"])
        self.assertTrue(self.config["observation_metrics"])

    def test_local_preflight_does_not_require_feishu(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "preflight.py"),
                    "--config",
                    str(config_path),
                    "--no-can-send-feishu",
                    "--no-can-archive-feishu",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["blockers"], [])

    def test_feishu_delivery_requires_only_selected_destinations(self):
        self.config["delivery"]["feishu_group"] = True
        errors = INIT_MODULE.validate_config(self.config)
        self.assertIn("Missing field required for Feishu group delivery: feishu_group_id", errors)
        self.assertIn("Missing field required for Feishu group delivery: sender_name", errors)
        self.assertFalse(any("feishu_doc_url" in error for error in errors))

    def test_v1_config_migrates_html_to_enabled(self):
        legacy = json.loads(json.dumps(self.config))
        legacy["version"] = 1
        legacy.pop("observation_metrics")
        legacy.pop("delivery")
        legacy["output"].pop("markdown")
        legacy["output"]["html"]["enabled"] = False
        legacy["feishu_group_id"] = "oc_existing"
        legacy["feishu_doc_url"] = "https://example.com/doc"
        migrated, changes = INIT_MODULE.migrate_config(legacy)
        self.assertEqual(migrated["version"], 2)
        self.assertTrue(migrated["output"]["html"]["enabled"])
        self.assertTrue(migrated["delivery"]["feishu_group"])
        self.assertTrue(migrated["delivery"]["feishu_archive"])
        self.assertTrue(migrated["observation_metrics"])
        self.assertIn("output.html.enabled:false->true", changes)

    def test_current_config_is_not_rewritten(self):
        current, changes = INIT_MODULE.migrate_config(self.config)
        self.assertEqual(changes, [])
        self.assertEqual(current, self.config)


if __name__ == "__main__":
    unittest.main()
