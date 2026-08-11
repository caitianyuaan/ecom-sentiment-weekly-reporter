# Compact consulting HTML report

Use this format when the user requests HTML, a consulting-company style, a polished visual report, or a report that teammates should scan quickly in a group chat.

## Output contract

- Produce one self-contained `.html` file with embedded CSS and no required build step.
- Combine markets into one file by default. Respect the configured market order; for US and UK, render US first and UK second.
- Use a restrained editorial appearance: white background, dark navy text, one accent color, thin dividers, and limited rounded decoration.
- Use system fonts so the file works offline and renders Chinese reliably.
- Default to no images. Include an image only when explicitly requested, it depicts the exact event, and its source is credited.
- Support desktop and mobile widths without horizontal scrolling.

## Information hierarchy

Render in this order:

1. One compact title block with report name, exact date range, sample counts, and scope note.
2. At most three bold cross-market conclusions.
3. One market section at a time.
4. A sample-shortfall note when verified items do not reach the requested target.
5. A minimal footer with sender attribution and evidence hierarchy.

Do not add decorative dashboards, large statistic cards, repeated overview tables, oversized gradients, or side-by-side market columns.

## News item anatomy

Use one full-width item row. Do not reserve a fixed left sidebar for the title.

1. Metadata row: platform, evidence type, topic, sentiment.
2. Headline: concise and factual.
3. Key fact: one bold sentence containing the most decision-useful number, rule, or change.
4. Summary: 2-4 factual sentences. Include mechanism, scope, and user/seller implication when supported by the source.
5. Bottom row: collapsible or visually quiet UXR metrics on the left; date and source link on the right.

Keep the complete item compact by reducing padding, not by deleting evidence. Use the full content width for the headline and summary.

## Evidence labels

Use one of these labels:

- `新闻`
- `政策信号`
- `平台卖家政策`
- `用户舆情`
- `行业数据`

For community or complaint evidence, state that it is an individual signal and cannot be generalized to the platform. For regional signals used in a market report, state whether local application is confirmed or remains an early warning.

## Date integrity

- Display the actual publication date or the explicit in-window effective date.
- Do not include older background research merely to reach an item target.
- Do not replace an older publication date with the report-week date.
- When samples are insufficient, state: `严格有效样本为 N 条；未使用周外材料补数。`

## Density and responsive behavior

- Desktop content width: approximately 1000-1120 px.
- Item vertical padding: approximately 12-16 px.
- Body text: approximately 13-14 px with 1.5-1.65 line height.
- Keep metadata, headline, key fact, and summary full width.
- On desktop, UXR and date/source may share the bottom row.
- On mobile, stack all item elements naturally in one column.
- Avoid fixed-width title columns; they produce empty space when summaries vary in length.

## Quality checks

Before delivery, verify:

- only one H1 exists;
- every selected item appears exactly once in its intended market section;
- every item has a valid source link, sentiment, and exact UXR labels;
- all displayed dates are inside the reporting window or are explicit in-window effective dates;
- no image remains when the user requested no images;
- the page has no fixed side column or unused blank area at common desktop widths;
- CSS includes a mobile breakpoint that stacks content;
- the HTML parses without structural errors.
