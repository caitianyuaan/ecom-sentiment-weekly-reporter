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
- `observation_metrics`: metric groups or exact metrics used to prioritize and interpret evidence, including product and selection, content and discovery, promotions and pricing, shopping experience, delivery and fulfillment, after-sales and trust, and business scale and growth.
- `source_profile`: named profile such as `default`, `official_first`, `media_first`, or `custom`.
- `sources`: object with `include` and `exclude` source lists.
- `feishu_group_id`: target Feishu group chat ID for outbound reports.
- `feishu_doc_url`: Feishu document URL for weekly archive.
- `sender_name`: attribution shown in the final sender line.
- `report_language`: must be `zh-CN`. Treat all narrative text and UXR metric labels as Chinese-only invariants, not per-run choices.

Optional configurable fields:
- `date_range`: explicit reporting window; otherwise use current week in local time.
- `items_per_platform`: recommended range is 3-5 when enough valid items exist.
- `output.html`: HTML output toggle, output directory, and layout. Default `enabled` to `true` and use `consulting_compact` unless the user explicitly requests Markdown-only output.

## First-run onboarding

If `~/.ecom-sentiment-weekly-reporter/config.json` is missing or incomplete, read `references/onboarding-zh.md` and run its guided onboarding. Never lead with a missing-file error or expose raw JSON fields as the first interaction.

Offer a one-step recommended setup and a four-round custom setup covering: markets/platforms, topics/observation metrics, source strategy, and output/delivery. Treat file format and delivery channel as separate choices. Ask for Feishu destinations and sender attribution only when the user chooses the corresponding Feishu delivery.

When writing the config file, use `scripts/init_user_config.py` when possible. Do not put another person's Feishu group, document, or sender name into a teammate's saved config unless the teammate explicitly provides it. After saving, immediately run preflight and continue the requested report; do not require another user turn just to say “run”.

## Running with saved config

For a scheduled task, the prompt should be short and configuration-driven:

`Run ecom-sentiment-weekly-reporter with my saved config`

When this prompt is received:
1. Inspect the config `version`. If it is missing or lower than `2`, run `python3 scripts/init_user_config.py --migrate` before preflight. The migration creates a backup, preserves scope and destinations, and enables the new default HTML output.
2. Run `scripts/preflight.py` against `~/.ecom-sentiment-weekly-reporter/config.json`.
3. Stop with its explicit reason code when status is `blocked`; never fail silently.
4. Record the run state with `scripts/run_state.py`.
5. Generate, validate, archive, and send according to the state-gated workflow below.

Do not continue with a version-1 config whose `output.html.enabled` still reflects the former default `false`. Migrate first; do not silently fall back to Markdown/Post.

## Report format

Produce one complete report per configured market.

### News item format

Use exactly this Chinese structure for every item:

`【平台】标题。摘要（2-3句，100%纯中文）。时间节点：YYYY/MM/DD [链接](url)【正向/负向/中性】【标签】`

Next line:

`**UXR关联指标：** 指标1 / 指标2 / 指标3`

Do not switch the narrative or UXR metric labels to English because a source, platform, previous run, or user interface is English.

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
- `observation_metrics`
- `source_profile` or `sources`
- `report_language`

Require `feishu_group_id` and `sender_name` only when Feishu group delivery is enabled. Require `feishu_doc_url` and `sender_name` only when Feishu archive delivery is enabled. If any core field is missing, run guided onboarding instead of stopping with a missing-config error.

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

Use `observation_metrics` to prioritize candidate evidence and UXR interpretation. Business-scale metrics such as GMV, traffic, orders, sellers, conversion, or repeat purchase must appear only when the inspected source provides a reliable number or explicitly attributable directional claim; never infer them from general platform news.

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

Treat the date window as a hard integrity constraint. A requested item count is a target, not permission to add older background reports, stale consumer studies, or later follow-up news. If the verified sample is smaller than the target, render the smaller sample and state the shortfall. Never relabel an older publication with an in-window date merely because its topic remains relevant.

### Step 6: Write each item

For every selected item:
- infer the platform label used in `【平台】` or its localized equivalent;
- write a concise headline in the configured report language;
- write a 2-3 sentence summary in the configured report language;
- assign one sentiment label only: `正向` / `负向` / `中性` for Chinese, or `Positive` / `Negative` / `Neutral` for English;
- assign a concise tag in the configured report language;
- append 3-4 UXR metric labels. Prefer three and use four when the item clearly spans four distinct UXR implications;
- use only the exact Chinese labels from the taxonomy below.

### Step 7: Map to exact UXR metric labels

Only use these exact labels.

**商品与供给**
- 高品质商品
- 正品品牌商品
- 可信赖的卖家
- 商品种类丰富
- 价格有竞争力
- 运费有竞争力
- 潮流商品
- 商品独特且有趣
- 有许多我喜欢的品牌

**内容与发现**
- 有吸引力的可购物内容
- 相关推荐
- 不过度重复
- 真实可信的价格与促销
- 视频/直播中的真实折扣
- 可信赖的电商视频/直播
- 信息丰富的电商视频/直播介绍
- 有娱乐性的电商视频/直播
- 发现商品/品牌
- 多样且丰富的内容
- 高质量内容（音频与灯光）
- 内容不过度夸张

**促销与价格**
- 简单易懂的促销/优惠券规则
- 有吸引力的促销/折扣
- 真实可信的价格与促销

**购物体验**
- 易于使用的购物功能
- 易于搜索商品/卖家
- 有帮助的评论与评分

**配送与履约**
- 整体配送速度快
- 包裹安全完好
- 易于追踪配送
- 运费有竞争力

**售后与信任**
- 顺畅退款与退货
- 支付安全
- 易于联系客户服务
- 对消费者友好的政策
- 保护我的信息
- 购后政策沟通
- 对退款有信心
- 顺畅退款/退货/换货
- 易于发起
- 容易获批
- 流程与退款速度快
- 易于追踪
- 退货方便
- 免费退货
- 卖家客服有帮助
- 平台客服有帮助

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

### Step 8A: Render compact HTML when requested

When the user requests HTML, a visually polished report, a consulting-style brief, or a report intended for fast scanning in a group chat, read `references/report-format-html.md` and render one combined HTML report unless the user asks for separate market files.

For a combined US/UK report:
- place the US section before the UK section;
- use one restrained single-column page, not side-by-side market columns;
- lead with three or fewer cross-market conclusions;
- render each item with one full-width metadata row, headline, bold key fact, 2-4 sentence factual summary, compact UXR disclosure, date, and source;
- use available horizontal width and avoid fixed sidebars that create empty space;
- default to no images; add images only when the user asks and the image belongs to the exact event;
- preserve the full evidence content even when the visual treatment is compact;
- keep mobile rendering single-column and readable without horizontal scrolling.

HTML is a presentation of the same selected evidence, not a second analysis. Its item set, dates, sentiment labels, UXR metrics, and links must match the validated report evidence.

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

After archival and after inserting the document link and sender attribution, save each final market report to a temporary UTF-8 text file. Normalize deterministic rendering errors first:

`python3 scripts/normalize_report.py --report <REPORT_FILE> --config <CONFIG_FILE>`

The normalizer restores exact taxonomy labels whose internal `/` was accidentally spaced by a renderer and collapses duplicate configured sender lines to exactly one final line. Do not normalize a combined multi-market blob; normalize and validate each market report before combining or sending.

Then run validation on that exact final outbound file:

`python3 scripts/validate_report.py --report <REPORT_FILE> --config <CONFIG_FILE> --archived`

If validation fails, regenerate once using the returned error codes. If it still fails, record `FAILED` and do not send. Validation is a hard gate, not advisory guidance.

Do not modify, append to, or re-render the report after validation. The bytes that pass validation must be the bytes sent to Feishu and archived as the final version. If any delivery adapter changes the content, run normalization and validation again on the resulting text before sending.

### Step 11: Send the Feishu group message

Only after validation succeeds, use an available Feishu messaging skill, connector, or tool to send the complete report to `feishu_group_id`. Do not send a teaser or abstract.

When `output.html.enabled` is `true`, use this delivery order:
1. generate the validated `consulting_compact` HTML report;
2. send it as a Feishu interactive card or HTMLBox when the available Feishu integration supports either format;
3. verify that the card contains the complete report content and exactly one sender attribution;
4. only when interactive card / HTMLBox delivery is unavailable, fall back to a Markdown-derived Feishu `post` message and explicitly report that fallback in the run result.

Do not silently choose Markdown `post` merely because it is easier to send. HTML/card delivery is the default presentation path. Do not paste raw HTML source into a plain-text or Markdown message.

After success, record `MESSAGE_SENT` and then `COMPLETE`.

If no Feishu messaging capability is available, record `FAILED` with `FEISHU_SEND_CAPABILITY_MISSING`, return the complete report in the conversation, and do not claim it was sent.

## Quality bar

Before any external send, run `scripts/validate_report.py`; do not rely on visual inspection alone. The validator must enforce all of the following:
- the config was loaded from the current user's saved config or current explicit parameters;
- no creator-specific Feishu group, document, market list, or sender name was used unless explicitly configured by this user;
- every item has one link and one sentiment label;
- a source URL with an embedded publication date does not contradict the displayed `时间节点`; treat a mismatch as evidence that an old article may have been relabeled;
- every item has a UXR metric line immediately after it;
- every item has 3-4 UXR metric labels;
- all UXR metric labels are Chinese and exactly match the taxonomy above;
- grouping is by configured platform, with clear bold section headers;
- the weekly summary uses only the columns `维度`, `平台`, and `信号`;
- after successful archival, the complete-report document link appears exactly once immediately before the sender attribution;
- each market report ends with exactly one configured sender attribution line;
- outbound titles and archive title use the resolved week from `scripts/build_week_config.py`.
- when HTML output is enabled, the Feishu send used interactive card / HTMLBox or the run result explicitly disclosed the Markdown `post` fallback.

## Reference files

- Use `references/source-playbook.md` as the default source universe and query-planning reference when `source_profile` is `default`.
- Use `references/sample-config.template.json` when onboarding teammates or creating a new per-user config.
- Read `references/onboarding-zh.md` for every first-run or incomplete-config experience.
- Use `references/report-format-html.md` for compact consulting-style HTML reports designed for group scanning.

## Attribution

Created by 蔡田园.
