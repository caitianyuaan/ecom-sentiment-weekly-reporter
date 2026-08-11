#!/usr/bin/env python3
import argparse
import json
from datetime import date, datetime, timedelta


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def current_week_range(today: date) -> tuple[date, date]:
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def format_market_title(market: str, start: date, report_language: str) -> str:
    market_code = market.upper()
    zh_mapping = {
        "US": "🇺🇸 美国电商舆情周报｜Week of {start}",
        "UK": "🇬🇧 英国电商舆情周报｜Week of {start}",
    }
    en_mapping = {
        "US": "🇺🇸 US E-commerce Sentiment Weekly Report | Week of {start}",
        "UK": "🇬🇧 UK E-commerce Sentiment Weekly Report | Week of {start}",
    }
    if report_language.lower().startswith("zh"):
        template = zh_mapping.get(market_code, f"{market_code} 电商舆情周报｜Week of {{start}}")
    else:
        template = en_mapping.get(market_code, f"{market_code} E-commerce Sentiment Weekly Report | Week of {{start}}")
    return template.format(start=start.isoformat())


def main() -> None:
    parser = argparse.ArgumentParser(description="Build week config for e-commerce sentiment weekly reporting")
    parser.add_argument("--start", help="Week start date, format YYYY-MM-DD")
    parser.add_argument("--end", help="Week end date, format YYYY-MM-DD")
    parser.add_argument("--markets", nargs="+", required=True, help="Market codes from user config")
    parser.add_argument("--report-language", default="zh-CN", help="Report language or locale")
    args = parser.parse_args()

    if args.report_language != "zh-CN":
        raise SystemExit("REPORT_LANGUAGE_MISMATCH: report_language must be zh-CN")

    if args.start and args.end:
        start = parse_date(args.start)
        end = parse_date(args.end)
    elif args.start or args.end:
        raise SystemExit("Both --start and --end are required when specifying an explicit range.")
    else:
        start, end = current_week_range(date.today())

    if end < start:
        raise SystemExit("End date must be on or after start date.")

    if args.report_language.lower().startswith("zh"):
        archive_title = f"📅 {start.strftime('%Y年%m月%d日')} - {end.strftime('%m月%d日')}"
    else:
        archive_title = f"📅 {start.strftime('%Y/%m/%d')} - {end.strftime('%Y/%m/%d')}"

    payload = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "archive_title": archive_title,
        "week_of": start.isoformat(),
        "report_language": args.report_language,
        "markets": [],
    }

    for market in args.markets:
        payload["markets"].append(
            {
                "market": market.upper(),
                "message_title": format_market_title(market, start, args.report_language),
            }
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
