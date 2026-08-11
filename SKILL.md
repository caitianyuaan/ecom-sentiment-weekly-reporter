---
name: ecom-sentiment-weekly-reporter
description: Generate configurable weekly e-commerce competitor-sentiment reports for selected markets, platforms, topics, and source profiles; synthesize public news into UXR-ready briefs, distribute to user-configured Feishu groups, and archive to user-configured Feishu docs. Use for recurring e-commerce news monitoring, competitor intelligence, public-opinion tracking, team-shared weekly UXR reporting automation, or first-run setup of teammate-specific report configurations.
---

# E-commerce Sentiment Weekly Reporter

Generate weekly e-commerce competitor sentiment reports from a teammate's saved configuration. Search recent public news, filter to the requested reporting week, summarize each item in the configured report language, map each item to the required exact English UXR metric labels, then distribute and archive the final reports to that teammate's configured Feishu destinations.

## Use this skill when

Trigger this skill when the user asks to:
- generate a weekly e-commerce news / sentiment / competitor-intelligence report;
- monitor e-commerce platforms such as Amazon, Temu, SHEIN, TikTok Shop, eBay, Meta / Instagram, Walmart, Google, or other configured platforms;
- set up or customize a recurring e-commerce sentiment report;
- push a complete market report to a Feishu group;
- archive weekly reports into a Feishu document;
- run `ecom-sentiment-weekly-reporter` with saved config.

## Configuration-first operation

This skill is team-shareable. Do not rely on hardcoded personal defaults for markets, platforms, topics, sources, Feishu destinations, or sender attribution.

Before generating a report, resolve configuration in this order:
1. Explicit user-provided parameters in the current request.
2. Saved per-user config at `~/.ecom-sentiment-weekly-reporter/config.json`.
3. First-run onboarding if the config file is missing or incomplete.

Required configurable fields:
- `markets`: list of market codes, e.g. `["US", "UK"]`.
- `platforms`: list of platforms to monitor.
- `topics`: list of monitoring themes such as returns, delivery, seller governance, pricing, content commerce, trust and safety, payment safety.
- `source_profile`: named profile such as `default`, `official_first`, `media_first`, or `custom`.
- `sources`: object with `include` and `exclude` source lists.
- `feishu_group_id`: target Feishu group chat ID for outbound reports.
- `feishu_doc_url`: Feishu document URL for weekly archive.
- `sender_name`: attribution shown in the final sender line.
- `report_language`: report language; use `zh-CN` for Chinese UXR briefs, `en` for English briefs, or another explicit locale when requested.

Optional configurable fields:
- `date_range`: explicit reporting window; otherwise use current week in local time.
- `items_per_platform`: recommended range is 3-5 when enough valid items exist.

## First-run onboarding

If `~/.ecom-sentiment-weekly-reporter/config.json` is missing, incomplete, or contains placeholder values, help the teammate create it. Offer three setup modes:

1. **Follow creator's settings**
   - Copy the creator-style monitoring scope from `references/sample-config.template.json`.
   - Require the teammate to fill their own `feishu_group_id`, `feishu_doc_url`, and `sender_name` before sending or archiving.

2. **Build on creator's settings**
   - Start from the sample template.
   - Ask which markets, platforms, topics, sources, and report language they want to add/remove.
   - Require their own Feishu destinations and sender attribution.

3. **Fully customize**
   - Ask for markets, platforms, topics, source profile or source list, Feishu group, Feishu doc, sender name, and report language.
   - Create a complete config from scratch.

When writing the config file for the current user, use `scripts/init_user_config.py` with the chosen mode when possible. Do not put another person's Feishu group, document, or sender name into a teammate's saved config unless the teammate explicitly provides it.

## Running with saved config

For a scheduled task, the prompt should be short and configuration-driven:

`Run ecom-sentiment-weekly-reporter with my saved config`

When this prompt is received:
1. Load `~/.ecom-sentiment-weekly-reporter/config.json`.
2. Validate required fields are present and not placeholders.
3. Resolve the reporting week with `scripts/build_week_config.py` using configured markets and optional date range.
4. Generate, send, and archive reports according to the saved config.

## Report format

Produce one complete report per configured market.

### News item format

For Chinese reports (`report_language: zh-CN`), use exactly this structure for every item:

`【平台】标题。摘要（2-3句，100%纯中文）。时间节点：YYYY/MM/DD [链接](url)【正向/负向/中性】【标签】`

Next line:

`**UXR关联指标：** 指标1 / 指标2 / 指标3`

For non-Chinese reports, keep the same information architecture, translate narrative text into the configured language, and keep UXR metric labels in exact English.

### Report structure

1. Market title line.
2. Date range line.
3. Grouped platform sections using bold platform headers.
4. 3-5 items per platform when enough valid items exist; state when verifiable samples are insufficient.
5. Weekly summary table.
6. Sender attribution line derived from `sender_name`.

For Chinese outbound messages, the final sender line is:

`消息由 {sender_name} 通过 Aime 个人助理 发送`

For English outbound messages, use:

`Message sent by {sender_name} via Aime personal assistant`

## Execution workflow

### Step 1: Load and validate configuration

Load the per-user config. Validate all required fields:
- `markets`
- `platforms`
- `topics`
- `source_profile` or `sources`
- `feishu_group_id`
- `feishu_doc_url`
- `sender_name`
- `report_language`

If any required field is missing, empty, or still a placeholder, run first-run onboarding instead of generating or sending the report.

### Step 2: Resolve the reporting week and outbound titles

Run `scripts/build_week_config.py` to normalize the date range and derive:
- reporting window start date;
- reporting window end date;
- week label for outbound messages;
- archive block title;
- message title per configured market.

Run with:
- `python3 scripts/build_week_config.py --markets <MARKET...>` for current week;
- `python3 scripts/build_week_config.py --start YYYY-MM-DD --end YYYY-MM-DD --markets <MARKET...>` for an explicit week.

### Step 3: Prepare market, platform, topic, and source scope

Use the configured `markets`, `platforms`, `topics`, `source_profile`, and `sources`. Do not silently expand to creator-specific defaults.

If `source_profile` is `default`, use `references/source-playbook.md` as the starting source universe and apply configured include/exclude lists.

### Step 4: Search recent public news

Use an available public-web search capability. If a dedicated search skill is installed, follow it; otherwise use Codex's built-in web search. Do not block report generation merely because a named search skill is unavailable.

Search by market, platform, topic, and week using public sources only. Search themes should come from config topics, commonly including:
- policy, fees, logistics, returns, enforcement, trust, safety, seller governance;
- ads, discovery, recommendation, live shopping, content commerce;
- pricing, promotions, consumer offers, marketplace competition;
- delivery, fulfillment, customer service, refunds, payment safety;
- brand partnerships, assortment, product authenticity, seller quality.

Do not rely on a single source. Build coverage from multiple reputable outlets and official / semi-official platform channels when available.

### Step 5: Filter and select items

Include only items that satisfy all of the following:
- published within the requested reporting week or directly tied to that week;
- relevant to the configured market;
- clearly connected to one configured platform or a market-wide competitive signal;
- materially useful for UXR interpretation;
- aligned to at least one configured topic unless it is a major market-wide event.

Selection rules:
- prefer original reporting, official announcements, newsroom posts, company blogs, community updates, or clearly attributable analysis;
- avoid duplicate rewrites of the same news unless they add meaningful new details;
- if multiple articles cover the same event, keep the strongest source and use one link;
- keep the tone factual and balanced.

### Step 6: Write each item

For every selected item:
- infer the platform label used in `【平台】` or its localized equivalent;
- write a concise headline in the configured report language;
- write a 2-3 sentence summary in the configured report language;
- assign one sentiment label only: `正向` / `负向` / `中性` for Chinese, or `Positive` / `Negative` / `Neutral` for English;
- assign a concise tag in the configured report language;
- append exactly three UXR metric labels unless the event strongly supports fewer; when fewer are truly justified, use at least two;
- use the exact English labels from the taxonomy below with original capitalization and punctuation.

### Step 7: Map to exact UXR metric labels

Only use these exact labels.

**Product & Selection**
- High quality products
- Authentic branded products
- Trustworthy sellers
- Variety of products
- Competitive prices
- Shipping fee Competitiveness
- Trendy products
- Products are unique & Interesting
- Many brands I like

**Content & Discovery**
- Engaging Shoppable content
- Relevant recommendations
- Not overly repetitive
- Genuine/trustworthy price & promotions
- Genuine discounts in video/LIVEs
- Trustworthy EC video/LIVEs
- Informative EC video/LIVEs introduction
- Entertaining EC video/LIVEs
- Discover product/brand
- Diverse and rich content
- High content quality (audio & light)
- Content not exaggerated

**Promotions & Pricing**
- Simple sales/coupon rules
- Compelling sales/discounts
- Genuine/trustworthy price & promotions

**Shopping Experience**
- Shopping features are easy to use
- Easy to search products/sellers
- Helpful reviews & ratings

**Delivery & Fulfillment**
- Fast overall delivery
- Secure intact packages
- Easy to track delivery
- Shipping fee Competitiveness

**After-sales & Trust**
- Smooth refund and return
- Secure payment
- Easy to contact CS
- Customer friendly policies
- Protects my info
- Post purchase policy communication
- Confident in Refund
- Smooth refund/return exchange
- Ease to initiate
- Easy approval
- Fast process & refund
- Ease of tracking
- Convenient return
- Free returns
- Seller CS helpfulness
- Platform CS helpfulness

### Step 8: Assemble each market report

Structure each market report in this order:
1. market title line;
2. date range line;
3. grouped platform sections;
4. weekly summary table;
5. sender attribution line.

For the weekly summary table, include at minimum these columns:
- Platform
- # of items
- Net sentiment
- Key themes
- Main UXR metrics impacted

When formatting for Feishu, prefer a clean Markdown or HTML table that renders well in chat/doc contexts.

### Step 9: Send Feishu group messages

Use an available Feishu messaging skill, connector, or tool to send the final market report to the configured `feishu_group_id`.

Send the complete report body, not a teaser or abstract.

If no Feishu messaging capability is available, do not claim the report was sent. Return the complete report in the conversation, state that delivery was skipped, and explain which capability is missing.

### Step 10: Archive to the Feishu document

Use an available Feishu/Lark document skill, connector, or tool to update the configured `feishu_doc_url`.

Archive all configured market reports under a new collapsible section titled:
- `📅 YYYY年MM月DD日 - MM月DD日` for Chinese;
- `📅 YYYY/MM/DD - YYYY/MM/DD` for English or other languages unless the user requests another format.

Archive behavior:
- add a new weekly block rather than overwriting prior weeks;
- place all configured market reports under the same weekly archive block;
- preserve historical content;
- if the archive doc already contains the same week block, update that block instead of duplicating it.

If no Feishu/Lark document capability is available, do not claim the report was archived. Preserve the complete archive-ready content in the response and state that archival was skipped.

## Quality bar

Before sending or archiving, verify all of the following:
- the config was loaded from the current user's saved config or current explicit parameters;
- no creator-specific Feishu group, document, market list, or sender name was used unless explicitly configured by this user;
- every item has one link and one sentiment label;
- every item has a UXR metric line immediately after it;
- all UXR metric labels exactly match the taxonomy above;
- grouping is by configured platform, with clear bold section headers;
- each market report ends with the configured sender attribution;
- outbound titles and archive title use the resolved week from `scripts/build_week_config.py`.

## Reference files

- Use `references/source-playbook.md` as the default source universe and query-planning reference when `source_profile` is `default`.
- Use `references/sample-config.template.json` when onboarding teammates or creating a new per-user config.

## Attribution

Created by 蔡田园.
