#!/usr/bin/env python3
"""Summarize internal search coverage from query, candidate, and selection JSON."""

import argparse
import json
from collections import Counter
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def top_source_share(items):
    counts = Counter(item.get("source") or "unknown" for item in items)
    if not counts:
        return {"source": None, "count": 0, "total": 0, "share": None}
    source, count = counts.most_common(1)[0]
    return {"source": source, "count": count, "total": sum(counts.values()), "share": round(count / sum(counts.values()), 4)}


def summarize(config, queries, candidates, selection):
    selected = selection.get("selected", [])
    rejected = selection.get("rejected", [])
    selected_ids = {item.get("id") for item in selected}
    rejection_counts = Counter(item.get("reason_code", "unknown") for item in rejected)
    qa_config = config.get("coverage_qa", {})
    threshold = qa_config.get("source_concentration_warning_share", 0.6)
    concentration_min_items = qa_config.get("source_concentration_min_items", 3)
    dimensions = {}
    warnings = []

    for dimension in ("market", "platform", "topic"):
        configured = config.get(f"{dimension}s", [])
        rows = []
        for value in configured:
            matching_queries = [q for q in queries if q.get(dimension) == value]
            matching_candidates = [c for c in candidates if c.get(dimension) == value]
            matching_selected = [c for c in matching_candidates if c.get("id") in selected_ids]
            matching_rejected_ids = {r.get("id") for r in rejected}
            matching_rejected = [c for c in matching_candidates if c.get("id") in matching_rejected_ids]
            if matching_selected:
                state = "selected"
            elif matching_candidates:
                state = "candidates_rejected"
            elif matching_queries:
                state = "searched_no_candidates"
            else:
                state = "not_searched"
            row = {
                dimension: value,
                "state": state,
                "executed_queries": len(matching_queries),
                "inspected_results": sum(int(q.get("inspected_count", 0)) for q in matching_queries),
                "candidates": len(matching_candidates),
                "selected": len(matching_selected),
                "rejected": len(matching_rejected),
            }
            rows.append(row)
            if state != "selected":
                warnings.append(f"{dimension}:{value}={state}")
        dimensions[dimension] = rows

    candidate_concentration = top_source_share(candidates)
    selected_concentration = top_source_share(selected)
    for population, result in (("candidates", candidate_concentration), ("selected", selected_concentration)):
        if result["total"] >= concentration_min_items and result["share"] >= threshold:
            warnings.append(f"source_concentration:{population}:{result['source']}={result['share']:.1%}")

    return {
        "summary": {
            "executed_queries": len(queries),
            "inspected_results": sum(int(q.get("inspected_count", 0)) for q in queries),
            "candidates": len(candidates),
            "selected": len(selected),
            "rejected": len(rejected),
        },
        "dimensions": dimensions,
        "rejection_reasons": dict(sorted(rejection_counts.items())),
        "source_concentration": {"candidates": candidate_concentration, "selected": selected_concentration},
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--queries", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = summarize(load(args.config), load(args.queries), load(args.candidates), load(args.selection))
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
