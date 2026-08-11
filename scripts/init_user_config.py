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
    "observation_metrics",
    "report_language",
]

PLACEHOLDER_PREFIX = "REPLACE_WITH_"
CURRENT_CONFIG_VERSION = 2


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
    delivery = config.get("delivery", {})
    if delivery.get("feishu_group"):
        for field in ("feishu_group_id", "sender_name"):
            if is_placeholder(config.get(field)):
                errors.append(f"Missing field required for Feishu group delivery: {field}")
    if delivery.get("feishu_archive"):
        for field in ("feishu_doc_url", "sender_name"):
            if is_placeholder(config.get(field)):
                errors.append(f"Missing field required for Feishu archive delivery: {field}")
    return errors


def migrate_config(config: dict) -> tuple[dict, list[str]]:
    """Upgrade legacy configs without overwriting user-selected scope or destinations."""
    version = int(config.get("version", 1))
    changes = []
    if version >= CURRENT_CONFIG_VERSION:
        return config, changes

    template = load_template()
    config.setdefault("observation_metrics", template["observation_metrics"])
    config.setdefault("delivery", {
        "local": True,
        "feishu_group": not is_placeholder(config.get("feishu_group_id")),
        "feishu_archive": not is_placeholder(config.get("feishu_doc_url")),
    })
    output = config.setdefault("output", {})
    output.setdefault("markdown", template["output"]["markdown"])
    html = output.setdefault("html", {})
    if not html.get("enabled"):
        html["enabled"] = True
        changes.append("output.html.enabled:false->true")
    for key, value in template["output"]["html"].items():
        html.setdefault(key, value)
    config["version"] = CURRENT_CONFIG_VERSION
    changes.append(f"version:{version}->{CURRENT_CONFIG_VERSION}")
    return config, changes


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
    parser.add_argument("--migrate", action="store_true", help="Back up and migrate an existing legacy config")
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

    if args.migrate:
        if not config_path.exists():
            raise SystemExit(f"Config not found: {config_path}")
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
        config, changes = migrate_config(config)
        if not changes:
            print("ALREADY_CURRENT")
            return
        backup_path = config_path.with_suffix(config_path.suffix + ".v1.bak")
        shutil.copy2(config_path, backup_path)
        write_config(config, config_path, overwrite=True)
        print(json.dumps({"status": "migrated", "backup": str(backup_path), "changes": changes}, ensure_ascii=False, indent=2))
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
        print(f"Created local-ready config: {config_path}")
        print("Feishu fields are required only if Feishu group delivery or archive is enabled.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
