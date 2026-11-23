---
name: eng-os-observability
description: "In a project governed by the Engineering OS, use when adding logging, metrics, tracing, or alerting; defines standard log/metric/trace record shapes and signal design by system boundary."
sources:
  - meso/observability.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Observability

Apply these rules when adding or reviewing logs, metrics, traces, or alerts. Signals must be
designed at the point behavior is written, not bolted on after an incident.

## Principles

- **Observability as a first-class concern.** Design signals alongside the code, not after the fact.
- **Validation at boundaries.** Every schema, contract, or policy violation must surface as an observable event.
- **Fault isolation over global stability.** Signals must make blast radius visible.
- **Determinism within defined boundaries.** AI systems must expose determinism-related metrics explicitly (schema compliance, constraint violations, output variance).

## Core Signals

- **Metrics**: trend, health, saturation, throughput, latency, violation rates.
- **Logs**: structured, for contextual diagnosis. Every record carries `trace_id` and `span_id`, bound once at entry in the language's context store (downstream functions take no logger argument); the operation's identifiers are top-level fields beside the standard ones, never a catch-all dump of the request.
- **Traces**: generate `trace_id` once at system entry and propagate it unchanged with W3C `traceparent`/`tracestate` through the OpenTelemetry propagator API, to every downstream call, log, and AI invocation; each hop gets its own `span_id`. `X-Trace-Id` is accepted on input only, as a legacy fallback when a caller cannot send `traceparent`.
- **Audit/validation events**: contract violations, schema failures, policy violations, safety enforcement.

Full record shapes (log, metric, trace context) and field-by-field rules: `references/standard-data-models.md`.

## Signal Design by Boundary

Emit signals at every boundary where behavior, latency, or correctness can change, not ad hoc inside business logic. An emitting-in-logic-only approach means boundary failures (timeouts, schema rejections) produce no signal at all, diagnosed only by absence, the hardest failure class to debug.

| Boundary | Emit |
|---|---|
| Request | `http.server.request.duration` histogram (seconds) with `http.route` (the route template, never the raw path) and `http.response.status_code`; the count is the histogram's count; error log on 5xx |
| Publish/consume | count counter by direction/topic/success, error log on failure |
| Transformation (pipeline stage) | output count, error count, output age gauges per stage |
| Validation | pass/fail counter tagged by schema, warn log with violations on failure |
| AI generation | call duration, `ai.schema_compliance` counter (`valid` attribute), `ai.constraint_violation` counter (`violated` attribute); warn log on violation |

## AI-Specific Observability

Track at minimum: determinism rate, schema compliance rate, constraint violation rate, output
variance, assumption usage frequency where material. These are not optional if AI output affects
downstream systems or decisions; block downstream use when schema validation fails. Rates are computed at query time from the counters, never emitted as `_rate` metrics.

## Metric Cardinality Budget
Declare, per metric, its labels and the maximum distinct values each may take. Never put an unbounded value (user id, request id, parameterized URL, free text, tenant id at scale) on a metric label; those belong on logs and traces. Set a per-service budget for active time series and alert when exceeded.
- Failure mode: one metric labeled by `user_id` at a hundred million users takes the metrics backend down for every service sharing it.

## Log Persistence
Structured JSON to stdout alone is not durable: a restart or a killed terminal erases it. Every service must send logs to a durable sink beyond stdout: a rotating file handler, a managed log-aggregation service (a process supervisor's own capture, e.g. PM2's log files, counts as this; it is not a substitute for choosing one), or a database table for a domain-scoped audit trail (rows keyed to a specific entity, queryable directly; additive to general logging, not a replacement for signals with no natural entity key). Declare explicitly: a rotation policy (size/time trigger, retained file count), a retention window matched to real debugging/audit need, and the minimum emitted level per `EXECUTION_MODE` (dev/stage/prod).
- Failure mode: correctly-shaped JSON logged to stdout only, no declared sink/rotation/retention; the process restarts mid-incident and the only evidence is gone.

## Trace Sampling
Declare a policy: head-based sampling at a fixed rate for the baseline, plus tail- or rule-based sampling that keeps every trace that errored, breached its latency SLO, or carries a debug flag. Decide once at entry and propagate with the trace context so every hop keeps or drops the same trace.
- Failure mode: uniform 1% sampling keeps traces nobody needs and drops the one slow request on-call is looking for.

## Interoperability Standard
Emit through OpenTelemetry (API and semantic conventions) so signal shapes are portable across backends; use convention names (`http.server.request.duration`, `http.route`, `http.request.method`, `db.system`, `service.name`) rather than local aliases; the local `{service}.{operation}.{unit}` naming applies only to custom metrics. Language mechanics for carrying `trace_id` without threading it through signatures: `eng-os-coding-standards-python` (`contextvars`) and `eng-os-coding-standards-nodejs` (`AsyncLocalStorage`).
- Failure mode: vendor-specific instrumentation makes the next backend migration a rewrite of every call site.

## AI-IDS Observability UI
The Scoring Run indicator and provenance drill-down for user-facing AI inference live in `eng-os-ai-ids-authoring/references/observability-ui.md`. This skill keeps the AI-specific metrics that feed it.

## Failure Modes

- missing metrics cause blind operation: failures surface only via user reports
- unstructured logs prevent diagnosis: fields cannot be queried or correlated
- no validation events hide correctness failures: pipelines look healthy while producing bad data
- no AI-specific metrics make model degradation invisible until impact is large
- too much low-signal telemetry creates noise instead of clarity
- `trace_id` not propagated downstream: request paths cannot be reconstructed across services
- AI results shipped with no visible scorer/model/token provenance: unauditable once wrong
- an unbounded label on a metric creates millions of time series and takes the metrics backend down
- uniform trace sampling keeps traces nobody needs and drops the slow, failed ones
- logs sent only to stdout with no declared sink/rotation/retention are lost the moment the process restarts, exactly when an incident makes them irreplaceable

## Definition of Done

### Per change

- [ ] Critical user and system flows have measurable signals
- [ ] Validation and contract failures are surfaced as observable events
- [ ] Latency, throughput, and errors are measurable at every boundary
- [ ] `trace_id` is generated at entry and propagated with W3C `traceparent` through all downstream calls, and bound once so every log line carries it
- [ ] Log records carry the `eng-os-coding-standards-common` Standard 6 minimum fields (`timestamp`, `level`, `message`, `trace_id`, `span_id`, `service`) in the shape in `references/standard-data-models.md`
- [ ] Metric attributes use route templates, never raw paths; names follow OpenTelemetry semantic conventions where one exists
- [ ] AI-specific correctness metrics exist where AI is used and gate downstream use on schema validity
- [ ] For AI-IDS systems, `eng-os-ai-ids-authoring`'s Observability UI Contract is satisfied
- [ ] Debugging a major failure is feasible without guesswork
- [ ] Every metric declares its labels and maximum cardinality; no unbounded identifier is a label; a per-service series budget is alerted on
- [ ] A trace sampling policy always keeps errored and SLO-breaching traces, decided once at entry and propagated
- [ ] Instrumentation uses OpenTelemetry APIs and semantic conventions

### Standing (release and audit)

- [ ] Every service's logs reach a durable sink beyond process stdout, with a declared rotation policy, retention window, and per-`EXECUTION_MODE` level policy

For a worked example (one service's metric declarations with cardinality caps, its sampling policy, a traced hop, and its log persistence), see `references/example.md`.
