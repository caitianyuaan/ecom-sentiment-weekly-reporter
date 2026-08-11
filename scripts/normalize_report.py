#!/usr/bin/env python3
"""Normalize deterministic formatting errors before final report validation."""

import argparse
import json
import re
from pathlib import Path

from validate_report import UXR_LABELS


def normalize_slash_labels(report: str) -> str:
    """Restore canonical taxonomy labels when a renderer spaces internal slashes."""
    for label in sorted(UXR_LABELS, key=len, reverse=True):
        if "/" not in label:
            continue
        spaced_pattern = re.escape(label).replace(r"/", r"\s*/\s*")
        report = re.sub(spaced_pattern, label, report)
    return report


def normalize_sender(report: str, sender_name: str) -> str:
    """Ensure a market report ends with exactly one configured sender line."""
    sender_line = f"消息由 {sender_name} 通过 Aime 个人助理 发送"
    lines = [line for line in report.splitlines() if line.strip() != sender_line]
    while lines and not lines[-1].strip():
        lines.pop()
    lines.append(sender_line)
    return "\n".join(lines) + "\n"


def normalize(report: str, config: dict) -> str:
    report = normalize_slash_labels(report)
    return normalize_sender(report, config["sender_name"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize a rendered Chinese weekly report before final validation")
    parser.add_argument("--report", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", help="Output path; defaults to replacing --report")
    args = parser.parse_args()

    report_path = Path(args.report).expanduser()
    output_path = Path(args.output).expanduser() if args.output else report_path
    config = json.loads(Path(args.config).expanduser().read_text(encoding="utf-8"))
    normalized = normalize(report_path.read_text(encoding="utf-8"), config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(normalized, encoding="utf-8")
    print(json.dumps({"status": "normalized", "output": str(output_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
