#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

STATES = ["START", "CONFIG_VALIDATED", "WEEK_RESOLVED", "NEWS_COLLECTED", "REPORT_RENDERED", "REPORT_VALIDATED", "DOC_ARCHIVED", "MESSAGE_SENT", "COMPLETE", "FAILED"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"runs": {}}


def main():
    parser = argparse.ArgumentParser(description="Track idempotent weekly report runs")
    parser.add_argument("--state", required=True)
    parser.add_argument("--week", required=True, help="Week start in YYYY-MM-DD")
    parser.add_argument("--set", choices=STATES)
    parser.add_argument("--reason")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = Path(args.state).expanduser()
    data = load(path)
    if args.check:
        print(json.dumps(data["runs"].get(args.week, {"status": "MISSING"}), ensure_ascii=False, indent=2))
        return
    if not args.set:
        raise SystemExit("--set is required unless --check is used")
    if args.set == "FAILED" and not args.reason:
        raise SystemExit("--reason is required for FAILED")
    existing = data["runs"].get(args.week)
    if existing and existing.get("status") == "COMPLETE" and args.set != "COMPLETE":
        raise SystemExit("RUN_ALREADY_COMPLETE")
    data["runs"][args.week] = {"status": args.set, "reason": args.reason, "updated_at": datetime.now(timezone.utc).isoformat()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["runs"][args.week], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
