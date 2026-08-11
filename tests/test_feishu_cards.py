#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_feishu_cards", ROOT / "scripts" / "render_feishu_cards.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


REPORT = {
    "title": "US/UK 电商舆情周报",
    "subtitle": "2026/08/10–2026/08/16",
    "full_report_url": "https://example.com/report.html",
    "sender_name": "cty",
    "takeaways": ["价格与履约压力上升", "平台治理信号集中"],
    "markets": [
        {
            "flag": "🇺🇸",
            "name": "美国",
            "summary": "本周重点关注价格与履约。",
            "items": [
                {
                    "platform": "Amazon",
                    "type": "新闻",
                    "sentiment": "中性",
                    "headline": "测试标题",
                    "key_fact": "测试重点",
                    "summary": "测试摘要。",
                    "metrics": ["价格有竞争力", "整体配送速度快"],
                    "date": "2026/08/10",
                    "source_url": "https://example.com/news",
                }
            ],
        }
    ],
}


class FeishuCardTests(unittest.TestCase):
    def test_renders_overview_and_market_cards(self):
        cards = MODULE.render_cards(REPORT)
        self.assertEqual(len(cards), 2)
        self.assertTrue(all(card["schema"] == "2.0" for card in cards))
        self.assertEqual(cards[0]["header"]["title"]["content"], REPORT["title"])

    def test_market_item_is_a_separate_component(self):
        market = MODULE.render_cards(REPORT)[1]
        markdown = [element for element in market["body"]["elements"] if element["tag"] == "markdown"]
        self.assertIn("### 测试标题", markdown[0]["content"])
        self.assertNotIn("HTML/Rich Card", str(market))
        self.assertEqual(str(market).count("发送人：cty"), 1)

    def test_full_report_uses_button_not_raw_html(self):
        overview = MODULE.render_cards(REPORT)[0]
        buttons = [element for element in overview["body"]["elements"] if element["tag"] == "button"]
        self.assertEqual(buttons[0]["behaviors"][0]["default_url"], REPORT["full_report_url"])
        self.assertNotIn("<html", str(overview).lower())


if __name__ == "__main__":
    unittest.main()
