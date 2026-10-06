# Worked Example: AI-IDS Observability UI — Scoring Run Card

This shows the AI-IDS Observability UI rules from `SKILL.md` applied to one real AI call. The
underlying log/metric record shapes emitted for this call follow `standard-data-models.md`
(AI generation boundary), not repeated here.

## Scenario

A data-catalog product runs a `dataset-quality-assessor` scorer against an uploaded dataset to
produce a quality grade shown to the user.

## Scoring Run card — rendered inline next to the result

```
┌─ Scoring Run ──────────────────────────────────────────────┐
│ Scorer: dataset-quality-assessor v1.2                      │
│ Run at: 2026-07-01 14:32:07 UTC                             │
│ Tokens: 412 in / 89 out                                     │
│ Result: Quality grade B+ (schema_valid: true)               │
│ [ View provenance ]                                          │
└──────────────────────────────────────────────────────────────┘
```

This card sits directly beside the "Quality grade: B+" result on the dataset detail page, not in
a separate admin dashboard. Clicking "View provenance" opens the full AI-IDS record for this run:
ROLE, OBJECTIVE, GUARDRAILS, the exact input passed to the scorer, and its raw output, reachable
without the user or support engineer needing to look up a `trace_id` by hand.

## Scale caveat applied to a high-QPS example

The dataset-quality-assessor above runs once per manual upload, so inline detail on every result is
free. Contrast with a hypothetical real-time feed-scoring scorer (`feed-relevance-scorer`) called
on every item in an infinite-scroll feed at ~2,000 QPS: rendering a full inline Scoring Run card on
every single item would flood the UI and the backend that serves card metadata.

Adaptation for that case: render no inline card by default; sample roughly 1 in every 200 results
(~10 QPS) for full inline detail, and make full provenance available on-demand via "View
provenance" for *any* result, sampled or not, by looking up its `run_id` on request rather than
pre-rendering it. This satisfies the rule's intent (provenance must be reachable, not
unauditable) without paying the inline-rendering cost on every one of 2,000 results per second.
