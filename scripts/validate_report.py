#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

SENTIMENTS = ("【正向】", "【负向】", "【中性】")
UXR_LABELS = {
    "高品质商品", "正品品牌商品", "可信赖的卖家", "商品种类丰富", "价格有竞争力", "运费有竞争力", "潮流商品", "商品独特且有趣", "有许多我喜欢的品牌",
    "有吸引力的可购物内容", "相关推荐", "不过度重复", "真实可信的价格与促销", "视频/直播中的真实折扣", "可信赖的电商视频/直播", "信息丰富的电商视频/直播介绍", "有娱乐性的电商视频/直播", "发现商品/品牌", "多样且丰富的内容", "高质量内容（音频与灯光）", "内容不过度夸张",
    "简单易懂的促销/优惠券规则", "有吸引力的促销/折扣", "易于使用的购物功能", "易于搜索商品/卖家", "有帮助的评论与评分",
    "整体配送速度快", "包裹安全完好", "易于追踪配送", "顺畅退款与退货", "支付安全", "易于联系客户服务", "对消费者友好的政策", "保护我的信息", "购后政策沟通", "对退款有信心", "顺畅退款/退货/换货", "易于发起", "容易获批", "流程与退款速度快", "易于追踪", "退货方便", "免费退货", "卖家客服有帮助", "平台客服有帮助",
}


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
        payload = line.removeprefix("**UXR关联指标：**").strip()
        labels = [part.strip() for part in payload.split(" / ") if part.strip()]
        count = len(labels)
        if count not in (3, 4):
            errors.append(f"UXR_METRIC_COUNT:{index}:{count}")
        for label in labels:
            if label not in UXR_LABELS:
                errors.append(f"UXR_LABEL_INVALID:{index}:{label}")
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
