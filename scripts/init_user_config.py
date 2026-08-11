#!/usr/bin/env python3
import argparse
import json
import os
import shutil
from pathlib import Path

REQUIRED_FIELDS = [
    "markets",
    "platforms",
    "topics",
    "feishu_group_id",
    "feishu_doc_url",
    "sender_name",
    "report_language",
]

PLACEHOLDER_PREFIX = "REPLACE_WITH_"


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_config_path() -> Path:
    return Path.home() / ".ecom-sentiment-weekly-reporter" / "config.json"


def load_template() -> dict:
    template_path = skill_root() / "references" / "sample-config.template.json"
    with template_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_placeholder(value) -> bool:
    if isinstance(value, str):
        return not value.strip() or value.strip().startswith(PLACEHOLDER_PREFIX)
    if isinstance(value, list):
        return len(value) == 0
    return value is None


def validate_config(config: dict) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in config or is_placeholder(config[field]):
            errors.append(f"Missing or placeholder required field: {field}")
    if not config.get("source_profile") and not config.get("sources"):
        errors.append("Missing source_profile or sources")
    coverage_qa = config.get("coverage_qa")
    if coverage_qa is not None:
        if not isinstance(coverage_qa, dict):
            errors.append("coverage_qa must be an object")
        else:
            share = coverage_qa.get("source_concentration_warning_share", 0.6)
            if not isinstance(share, (int, float)) or isinstance(share, bool) or not 0 <= share <= 1:
                errors.append("coverage_qa.source_concentration_warning_share must be a number from 0 to 1")
            for field in ("source_concentration_min_items", "consecutive_zero_selected_weeks"):
                value = coverage_qa.get(field)
                if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
                    errors.append(f"coverage_qa.{field} must be a positive integer")
    return errors


def write_config(config: dict, path: Path, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise SystemExit(f"Config already exists: {path}. Use --overwrite to replace it.")
    with path.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or validate per-user config for ecom-sentiment-weekly-reporter")
    parser.add_argument("--mode", choices=["follow_creator_settings", "build_on_creator_settings", "fully_customize"], default="follow_creator_settings")
    parser.add_argument("--config", default=str(default_config_path()), help="Path to per-user config file")
    parser.add_argument("--from-template", action="store_true", help="Create config from the bundled sample template")
    parser.add_argument("--validate", action="store_true", help="Validate an existing config")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing config when creating from template")
    parser.add_argument("--print-template", action="store_true", help="Print the bundled template to stdout")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser()

    if args.print_template:
        print(json.dumps(load_template(), ensure_ascii=False, indent=2))
        return

    if args.validate:
        if not config_path.exists():
            raise SystemExit(f"Config not found: {config_path}")
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
        errors = validate_config(config)
        if errors:
            print("INVALID")
            for error in errors:
                print(f"- {error}")
            raise SystemExit(1)
        print("VALID")
        return

    if args.from_template:
        config = load_template()
        config["setup_mode"] = args.mode
        if args.mode == "fully_customize":
            config["markets"] = []
            config["platforms"] = []
            config["topics"] = []
            config["sources"]["include"] = []
        write_config(config, config_path, args.overwrite)
        print(f"Created config template: {config_path}")
        print("Please replace placeholder Feishu destinations and sender_name before running reports.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
