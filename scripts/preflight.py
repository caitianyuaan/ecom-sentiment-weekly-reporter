#!/usr/bin/env python3
import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path

REQUIRED = ["markets", "platforms", "topics", "feishu_group_id", "feishu_doc_url", "sender_name"]
PLACEHOLDER_PREFIX = "REPLACE_WITH_"


def invalid(value):
    return value is None or value == [] or (isinstance(value, str) and (not value.strip() or value.startswith(PLACEHOLDER_PREFIX)))


def week_range(today):
    start = today - timedelta(days=today.weekday())
    return start, start + timedelta(days=6)


def main():
    parser = argparse.ArgumentParser(description="Build a deterministic weekly-report run plan")
    parser.add_argument("--config", required=True)
    parser.add_argument("--today", help="Override today with YYYY-MM-DD for testing")
    parser.add_argument("--can-search", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--can-send-feishu", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--can-archive-feishu", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    config = json.loads(Path(args.config).expanduser().read_text(encoding="utf-8"))
    errors = [f"CONFIG_MISSING:{field}" for field in REQUIRED if field not in config or invalid(config[field])]
    if not config.get("source_profile") and not config.get("sources"):
        errors.append("CONFIG_MISSING:source_profile_or_sources")

    today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else date.today()
    start, end = week_range(today)
    blockers = []
    if not args.can_search:
        blockers.append("SEARCH_CAPABILITY_MISSING")
    if not args.can_send_feishu:
        blockers.append("FEISHU_SEND_CAPABILITY_MISSING")
    if not args.can_archive_feishu:
        blockers.append("FEISHU_ARCHIVE_CAPABILITY_MISSING")

    payload = {
        "status": "blocked" if errors or blockers else "ready",
        "errors": errors,
        "blockers": blockers,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": "Asia/Shanghai",
        "report_language": "zh-CN",
        "narrative_language": "Chinese only",
        "uxr_metric_language": "English",
        "markets": config.get("markets", []),
        "platforms": config.get("platforms", []),
        "sender_name": config.get("sender_name"),
        "feishu_group_id": config.get("feishu_group_id"),
        "feishu_doc_url": config.get("feishu_doc_url"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0 if payload["status"] == "ready" else 1)


if __name__ == "__main__":
    main()
