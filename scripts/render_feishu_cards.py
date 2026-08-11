#!/usr/bin/env python3
"""Render structured report JSON into native Feishu Card JSON 2.0 payloads."""

import argparse
import json
from pathlib import Path


def md(content, size="normal_v2", margin="0px 0px 0px 0px"):
    return {"tag": "markdown", "content": content, "text_size": size, "margin": margin}


def divider():
    return {"tag": "hr", "margin": "10px 0px 10px 0px"}


def button(label, url):
    return {
        "tag": "button",
        "text": {"tag": "plain_text", "content": label},
        "type": "primary",
        "width": "fill",
        "size": "medium",
        "behaviors": [{"type": "open_url", "default_url": url}],
        "margin": "12px 0px 0px 0px",
    }


def card(title, subtitle, elements, template="blue"):
    return {
        "schema": "2.0",
        "config": {"update_multi": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "subtitle": {"tag": "plain_text", "content": subtitle},
            "template": template,
            "padding": "12px 12px 12px 12px",
        },
        "body": {
            "direction": "vertical",
            "padding": "12px 14px 14px 14px",
            "elements": elements,
        },
    }


def render_item(item):
    meta = " · ".join(part for part in [item.get("platform"), item.get("type"), item.get("sentiment")] if part)
    metrics = " / ".join(item.get("metrics", []))
    source = f"[查看来源]({item['source_url']})" if item.get("source_url") else ""
    footer = " · ".join(part for part in [item.get("date"), source] if part)
    parts = [
        f"**{meta}**" if meta else "",
        f"### {item['headline']}",
        f"**重点：** {item['key_fact']}" if item.get("key_fact") else "",
        item.get("summary", ""),
        f"**UXR：** {metrics}" if metrics else "",
        footer,
    ]
    return md("\n".join(part for part in parts if part), margin="0px 0px 4px 0px")


def render_cards(report):
    cards = []
    overview = []
    takeaways = report.get("takeaways", [])[:3]
    if takeaways:
        overview.append(md("\n".join(f"- **{item}**" for item in takeaways)))
    for market in report.get("markets", []):
        label = " ".join(part for part in [market.get("flag"), market.get("name")] if part)
        overview.append(md(f"**{label}**\n{market.get('summary', '')}", margin="8px 0px 0px 0px"))
    if report.get("full_report_url"):
        overview.append(button("查看完整 HTML 报告", report["full_report_url"]))
    cards.append(card(report["title"], report.get("subtitle", ""), overview))

    for market in report.get("markets", []):
        label = " ".join(part for part in [market.get("flag"), market.get("name")] if part)
        elements = []
        for index, item in enumerate(market.get("items", [])):
            if index:
                elements.append(divider())
            elements.append(render_item(item))
        if report.get("full_report_url"):
            elements.append(button("查看完整 HTML 报告", report["full_report_url"]))
        if report.get("sender_name"):
            elements.append(md(f"发送人：{report['sender_name']}", size="notation", margin="10px 0px 0px 0px"))
        cards.append(card(f"{label}电商舆情周报", report.get("subtitle", ""), elements, template="wathet"))
    return cards


def main():
    parser = argparse.ArgumentParser(description="Render native Feishu Card JSON 2.0 payloads")
    parser.add_argument("--input", required=True, help="Structured report JSON")
    parser.add_argument("--output", required=True, help="Output JSON containing cards")
    args = parser.parse_args()
    report = json.loads(Path(args.input).read_text(encoding="utf-8"))
    payload = {"msg_type": "interactive", "cards": render_cards(report)}
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "rendered", "cards": len(payload["cards"]), "output": args.output}, ensure_ascii=False))


if __name__ == "__main__":
    main()
