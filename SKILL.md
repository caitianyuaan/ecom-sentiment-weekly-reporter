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
- `report_language`: must be `zh-CN`. Treat Chinese narrative output as an invariant, not a per-run choice. Keep only the UXR metric labels in English.

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
   - Ask which markets, platforms, topics, and sources they want to add/remove.
   - Require their own Feishu destinations and sender attribution.

3. **Fully customize**
   - Ask for markets, platforms, topics, source profile or source list, Feishu group, Feishu doc, and sender name.
   - Create a complete config from scratch.

When writing the config file for the current user, use `scripts/init_user_config.py` with the chosen mode when possible. Do not put another person's Feishu group, document, or sender name into a teammate's saved config unless the teammate explicitly provides it.

## Running with saved config

For a scheduled task, the prompt should be short and configuration-driven:

`Run ecom-sentiment-weekly-reporter with my saved config`

When this prompt is received:
1. Run `scripts/preflight.py` against `~/.ecom-sentiment-weekly-reporter/config.json`.
2. Stop with its explicit reason code when status is `blocked`; never fail silently.
3. Record the run state with `scripts/run_state.py`.
4. Generate, validate, archive, and send according to the state-gated workflow below.

## Report format

Produce one complete report per configured market.

### News item format

Use exactly this Chinese structure for every item:

`【平台】标题。摘要（2-3句，100%纯中文）。时间节点：YYYY/MM/DD [链接](url)【正向/负向/中性】【标签】`

Next line:

`**UXR关联指标：** 指标1 / 指标2 / 指标3`

Do not switch the narrative to English because a source, platform, previous run, or user interface is English. Only the exact UXR metric labels remain in English.

### Report structure

Follow this exact outbound order:

1. Market title line.
2. Grouped platform sections using bold platform headers.
3. 3-5 items per platform when enough valid items exist. After the available items for a platform, write `本周可验证样本不足` when fewer than three valid items exist.
4. `**本周速览**` summary with the columns `维度`, `平台`, and `信号`.
5. One complete-report document link after successful archival.
6. Exactly one sender attribution line derived from `sender_name`.

For Chinese outbound messages, the final sender line is:

`消息由 {sender_name} 通过 Aime 个人助理 发送`

For English outbound messages, use:

`Message sent by {sender_name} via Aime personal assistant`

## Execution workflow

Use this state order: `START -> CONFIG_VALIDATED -> WEEK_RESOLVED -> NEWS_COLLECTED -> REPORT_RENDERED -> REPORT_VALIDATED -> DOC_ARCHIVED -> MESSAGE_SENT -> COMPLETE`. On any failure, record `FAILED` with a reason code. Never send before `REPORT_VALIDATED`; never mark complete before `MESSAGE_SENT`.

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
- append 3-4 UXR metric labels. Prefer three and use four when the item clearly spans four distinct UXR implications;
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
2. grouped platform sections;
3. weekly summary;
4. complete-report document link;
5. sender attribution line.

Use this Chinese weekly-summary header:

`**本周速览**`

Summarize the main cross-platform signals with exactly these three columns:
- `维度`
- `平台`
- `信号`

When formatting for Feishu, prefer a clean Markdown or HTML table that renders well in chat/doc contexts.

### Step 9: Archive to the Feishu document

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

After archival succeeds, add exactly one document link between `**本周速览**` and the sender attribution:

`**完整报告文档：** [点击查看]({feishu_doc_url})`

Use the current user's configured `feishu_doc_url`. Do not add the link before archival succeeds, do not substitute another user's document, and do not repeat the link.

### Step 10: Validate the final outbound report

Save the final market report to a temporary UTF-8 text file and run:

`python3 scripts/validate_report.py --report <REPORT_FILE> --config <CONFIG_FILE> --archived`

If validation fails, regenerate once using the returned error codes. If it still fails, record `FAILED` and do not send. Validation is a hard gate, not advisory guidance.

### Step 11: Send the Feishu group message

Only after validation succeeds, use an available Feishu messaging skill, connector, or tool to send the complete report to `feishu_group_id`. Do not send a teaser or abstract. After success, record `MESSAGE_SENT` and then `COMPLETE`.

If no Feishu messaging capability is available, record `FAILED` with `FEISHU_SEND_CAPABILITY_MISSING`, return the complete report in the conversation, and do not claim it was sent.

## Quality bar

Before any external send, run `scripts/validate_report.py`; do not rely on visual inspection alone. The validator must enforce all of the following:
- the config was loaded from the current user's saved config or current explicit parameters;
- no creator-specific Feishu group, document, market list, or sender name was used unless explicitly configured by this user;
- every item has one link and one sentiment label;
- every item has a UXR metric line immediately after it;
- every item has 3-4 UXR metric labels;
- all UXR metric labels exactly match the taxonomy above;
- grouping is by configured platform, with clear bold section headers;
- the weekly summary uses only the columns `维度`, `平台`, and `信号`;
- after successful archival, the complete-report document link appears exactly once immediately before the sender attribution;
- each market report ends with exactly one configured sender attribution line;
- outbound titles and archive title use the resolved week from `scripts/build_week_config.py`.

## Reference files

- Use `references/source-playbook.md` as the default source universe and query-planning reference when `source_profile` is `default`.
- Use `references/sample-config.template.json` when onboarding teammates or creating a new per-user config.

## Attribution

Created by 蔡田园.
