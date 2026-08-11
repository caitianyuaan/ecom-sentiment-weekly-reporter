# Coverage QA and Blank-space Diagnostics

Use this reference to distinguish a genuinely quiet news week from incomplete search coverage. Coverage QA is internal by default and must not alter the compact public report unless the user explicitly enables `coverage_qa.include_in_report`.

## Required inputs

### Executed-query log

Record one object per query that was actually executed:

```json
{
  "market": "US",
  "platform": "Amazon",
  "topic": "returns and refunds",
  "query": "Amazon US returns refunds 2026-08",
  "executed_at": "2026-08-12T09:30:00+08:00",
  "result_count": 8,
  "inspected_count": 3
}
```

Do not log planned but unexecuted queries. `result_count` is the search provider's returned count when available; `inspected_count` is the number of results actually opened or otherwise inspected.

Candidate records must retain `market`, `platform`, `topic`, `source`, and final status. Rejected candidates must retain a `reason_code`. Historical weekly QA records are optional, but required for consecutive-week gap detection.

## Coverage states

Classify every configured market/platform/topic slice into exactly one state:

- `not_searched`: no executed query covered the slice;
- `searched_no_candidates`: one or more queries ran, but no inspected result became a candidate;
- `candidates_rejected`: candidates were created, but none were selected;
- `selected`: at least one candidate was selected.

Do not describe `not_searched` or `searched_no_candidates` as "no relevant news this week." Use "coverage incomplete" or "no verifiable candidate found in executed searches."

## Required metrics

Report counts by market, platform, and topic for:

- executed queries;
- inspected results;
- candidates;
- selected items;
- rejected items, grouped by rejection reason.

Also report:

- platforms and topics with zero executed queries;
- platforms and topics with zero inspected candidates;
- platforms and topics with zero selected items;
- consecutive weeks with zero selected items by topic, when comparable history exists;
- top-source share among candidates and selected items.

Calculate top-source share as the largest count from one source divided by the total count in that population. Warn when the population has at least `coverage_qa.source_concentration_min_items` items and the share is greater than or equal to `coverage_qa.source_concentration_warning_share`. Do not raise concentration warnings from tiny or empty samples.

## Interpretation rules

- Zero selected items plus `not_searched` means a search-process gap.
- Zero selected items plus `searched_no_candidates` means searches ran but produced no inspected, usable candidate; consider query or source expansion.
- Zero selected items plus `candidates_rejected` means the rejection log must explain the gap.
- Repeated topic gaps require comparable historical QA records with the same market/topic definition. Do not infer consecutive gaps when history is missing or configuration changed materially.
- Source concentration is a warning, not an automatic rejection rule.

## Output behavior

Save a machine-readable QA JSON file when possible, using a filename such as `<MARKET>_coverage-qa_<YYYY-MM-DD>.json`. Keep it separate from the canonical report. Return a concise internal warning summary to the operator when any configured slice was not searched, any repeated gap threshold was reached, or source concentration exceeded the configured threshold.
