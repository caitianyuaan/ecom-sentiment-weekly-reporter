#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

SENTIMENTS = ("【正向】", "【负向】", "【中性】")


def chinese_ratio(text):
    narrative = re.sub(r"https?://\S+|\*\*UXR关联指标：\*\*.*", "", text)
    letters = re.findall(r"[A-Za-z\u4e00-\u9fff]", narrative)
    return sum("\u4e00" <= c <= "\u9fff" for c in letters) / max(1, len(letters))


def validate(report, config, archived):
    errors = []
    if chinese_ratio(report) < 0.70:
        errors.append("REPORT_LANGUAGE_MISMATCH")
    if report.count("**本周速览**") != 1:
        errors.append("WEEKLY_SUMMARY_COUNT")
    for header in ("维度", "平台", "信号"):
        if header not in report:
            errors.append(f"WEEKLY_SUMMARY_COLUMN_MISSING:{header}")
    sender = f"消息由 {config['sender_name']} 通过 Aime 个人助理 发送"
    if report.count(sender) != 1:
        errors.append("SENDER_LINE_COUNT")
    doc_prefix = "**完整报告文档：**"
    expected_docs = 1 if archived else 0
    if report.count(doc_prefix) != expected_docs:
        errors.append("DOCUMENT_LINK_COUNT")
    if archived and config["feishu_doc_url"] not in report:
        errors.append("DOCUMENT_LINK_MISMATCH")
    for platform in config["platforms"]:
        if f"**{platform}**" not in report:
            errors.append(f"PLATFORM_SECTION_MISSING:{platform}")
    item_lines = [line for line in report.splitlines() if line.startswith("【") and "时间节点：" in line]
    if not item_lines:
        errors.append("NO_NEWS_ITEMS")
    for index, line in enumerate(item_lines, 1):
        if "[\u94fe\u63a5](http" not in line:
            errors.append(f"ITEM_LINK_MISSING:{index}")
        if sum(s in line for s in SENTIMENTS) != 1:
            errors.append(f"ITEM_SENTIMENT_INVALID:{index}")
    metric_lines = [line for line in report.splitlines() if line.startswith("**UXR关联指标：**")]
    if len(metric_lines) != len(item_lines):
        errors.append("UXR_LINE_COUNT")
    for index, line in enumerate(metric_lines, 1):
        count = len([part for part in line.split("：", 1)[1].split("/") if part.strip()])
        if count not in (3, 4):
            errors.append(f"UXR_METRIC_COUNT:{index}:{count}")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate a rendered Chinese weekly report before external writes")
    parser.add_argument("--report", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--archived", action="store_true")
    args = parser.parse_args()
    report = Path(args.report).read_text(encoding="utf-8")
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    errors = validate(report, config, args.archived)
    print(json.dumps({"status": "valid" if not errors else "invalid", "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
