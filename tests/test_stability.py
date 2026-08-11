#!/usr/bin/env python3
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_report", ROOT / "scripts" / "validate_report.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
sys.modules["validate_report"] = MODULE

NORMALIZE_SPEC = importlib.util.spec_from_file_location("normalize_report", ROOT / "scripts" / "normalize_report.py")
NORMALIZE_MODULE = importlib.util.module_from_spec(NORMALIZE_SPEC)
NORMALIZE_SPEC.loader.exec_module(NORMALIZE_MODULE)

CONFIG = {
    "platforms": ["Amazon"],
    "sender_name": "测试用户",
    "feishu_doc_url": "https://example.com/report",
}

VALID_REPORT = """🇬🇧 英国电商舆情周报｜Week of 2026-06-01
**Amazon**
【Amazon】平台推出新的配送服务。该服务提升英国消费者的履约体验，并强化日常购物的便利性。时间节点：2026/06/02 [链接](https://example.com/news)【正向】【物流/便利性】
**UXR关联指标：** 整体配送速度快 / 包裹安全完好 / 易于追踪配送
**本周速览**
| 维度 | 平台 | 信号 |
| --- | --- | --- |
| 履约 | Amazon | 配送体验提升 |
**完整报告文档：** [点击查看](https://example.com/report)
消息由 测试用户 通过 Aime 个人助理 发送
"""


class StabilityTests(unittest.TestCase):
    def test_golden_report_passes(self):
        self.assertEqual(MODULE.validate(VALID_REPORT, CONFIG, archived=True), [])

    def test_english_report_is_rejected(self):
        report = VALID_REPORT.replace("平台推出新的配送服务。该服务提升英国消费者的履约体验，并强化日常购物的便利性。", "Amazon launched a faster delivery service for UK shoppers.")
        self.assertIn("REPORT_LANGUAGE_MISMATCH", MODULE.validate(report, CONFIG, archived=True))

    def test_duplicate_sender_is_rejected(self):
        report = VALID_REPORT + "消息由 测试用户 通过 Aime 个人助理 发送\n"
        self.assertIn("SENDER_LINE_COUNT", MODULE.validate(report, CONFIG, archived=True))

    def test_english_uxr_label_is_rejected(self):
        report = VALID_REPORT.replace("整体配送速度快", "Fast overall delivery")
        errors = MODULE.validate(report, CONFIG, archived=True)
        self.assertTrue(any(error.startswith("UXR_LABEL_INVALID") for error in errors))

    def test_unarchived_report_must_not_include_link(self):
        self.assertIn("DOCUMENT_LINK_COUNT", MODULE.validate(VALID_REPORT, CONFIG, archived=False))

    def test_normalizer_repairs_spaced_taxonomy_slashes_and_duplicate_sender(self):
        broken = VALID_REPORT.replace("整体配送速度快", "发现商品 / 品牌")
        broken += "消息由 测试用户 通过 Aime 个人助理 发送\n"
        normalized = NORMALIZE_MODULE.normalize(broken, CONFIG)
        self.assertIn("发现商品/品牌", normalized)
        self.assertNotIn("发现商品 / 品牌", normalized)
        self.assertEqual(normalized.count("消息由 测试用户 通过 Aime 个人助理 发送"), 1)
        self.assertTrue(normalized.endswith("消息由 测试用户 通过 Aime 个人助理 发送\n"))

    def test_source_url_date_mismatch_is_rejected(self):
        report = VALID_REPORT.replace(
            "https://example.com/news",
            "https://example.com/2026/07/31/old-news/",
        )
        errors = MODULE.validate(report, CONFIG, archived=True)
        self.assertTrue(any(error.startswith("ITEM_SOURCE_DATE_MISMATCH") for error in errors))


if __name__ == "__main__":
    unittest.main()
