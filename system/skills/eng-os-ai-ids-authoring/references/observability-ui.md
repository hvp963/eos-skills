# Observability UI: Scoring Run Indicator

This is a product requirement specific to user-facing AI-IDS inference. Canonical source: `../../../meso/ai-deterministic-systems.md`, Observability UI Contract. The signal design that feeds it (AI-specific metrics, boundary signals) stays in `eng-os-observability`.

Backend metrics are not sufficient for AI-heavy products: the user facing the result also needs
visible provenance.

- **Every live AI inference call in a user-facing product must surface, at the point of use,** the
  scorer/model name, timestamp, and input/output token counts. Render this as a "Scoring Run" card
  (or equivalent) next to the AI-generated result, not buried in a log viewer or a separate admin page.
- **For AI systems built on the AI-IDS framework**, offer a full provenance view on demand: which
  ROLE, OBJECTIVE, GUARDRAILS, inputs, and outputs produced this specific result. This should be
  reachable from the result itself (e.g., "View reasoning" / "View provenance"), not require
  correlating a `trace_id` across systems by hand.
- **Failure mode:** an AI-generated result with no visible provenance is unauditable, and it erodes
  user trust the moment it's wrong once. With no way for the user (or support) to inspect what
  produced it, every subsequent result becomes suspect too.
- **Scale caveat:** always rendering full inline Scoring Run metadata (scorer, timestamp, token
  counts) on every single result does not scale well at high query-per-second volumes in
  production. An acceptable adaptation is to sample a subset for full inline detail, or to make
  full metadata available on-demand/drill-down rather than always inline; this is not an
  unconditional "always inline everything" rule.

## Worked Example: Scoring Run Card

The rules above applied to one real AI call, then the scale caveat applied to a high-QPS scorer.
The log and metric records emitted for each call follow `eng-os-observability`
(`../../eng-os-observability/references/standard-data-models.md`, AI generation boundary) and are not repeated here.

### Scenario

A data-catalog product runs a `dataset-quality-assessor` scorer against an uploaded dataset to
produce a quality grade shown to the user.

### Scoring Run card — rendered inline next to the result

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

### Scale caveat applied to a high-QPS example

The dataset-quality-assessor above runs once per manual upload, so inline detail on every result is
free. Contrast with a hypothetical real-time feed-scoring scorer (`feed-relevance-scorer`) called
on every item in an infinite-scroll feed at ~2,000 QPS: rendering a full inline Scoring Run card on
every single item would flood the UI and the backend that serves card metadata.

Adaptation for that case: render no inline card by default; sample roughly 1 in every 200 results
(~10 QPS) for full inline detail, and make full provenance available on-demand via "View
provenance" for *any* result, sampled or not, by looking up its `run_id` on request rather than
pre-rendering it. This satisfies the rule's intent (provenance must be reachable, not
unauditable) without paying the inline-rendering cost on every one of 2,000 results per second.
