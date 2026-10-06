# Observability UI: Scoring Run Indicator

This is a product requirement specific to user-facing AI-IDS inference. Canonical source: `../../../meso/ai-deterministic-systems.md`, Observability UI Contract. The signal design that feeds it (AI-specific metrics, boundary signals) stays in `eng-os-observability`.


Backend metrics are not sufficient for AI-heavy products: the user facing the result also needs
visible provenance, not just the engineering team via dashboards.

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

See `../../eng-os-observability/references/example.md` for a mocked-up Scoring Run card for one real AI call, plus the
scale-caveat sampling adaptation applied to a hypothetical high-QPS scenario.
