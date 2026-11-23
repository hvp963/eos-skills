# Observability

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for making systems measurable, debuggable, and explainable.

### What This Is Not
- not dashboards alone
- not logging alone
- not a monitoring tool list

## Scope
- Level: Meso
- Applies To: Product, data, and AI systems

---

## Applied Principles

### Observability as a First-Class Concern
Signals must be designed, not added after the fact.

### Validation at Boundaries
Validation failures should surface as observable events.

### Fault Isolation Over Global Stability
Signals should make blast radius visible.

### Determinism Within Defined Boundaries
AI systems must expose determinism-related metrics explicitly.

---

## Core Signals

### Metrics
Use metrics for trend, health, saturation, throughput, latency, and violation rates.

### Logs
Use structured logs for contextual diagnosis.

### Traces
Use traces where request or workflow path matters across boundaries.

### Audit and Validation Events
Record contract violations, schema failures, policy violations, and safety enforcement.

---

## Standard Data Models

> These shapes define the required structure for each signal type. Replace placeholder field values with production-validated field names and conventions when available.

### Log Record

```
{
  "timestamp":  "2026-05-30T14:22:01.345Z",   // ISO 8601, millisecond precision
  "level":      "INFO",                         // DEBUG | INFO | WARN | ERROR
  "message":    "order processing started",
  "trace_id":   "abc123",                       // propagated from entry point; never null
  "span_id":    "def456",                       // the current operation's span; never null
  "service":    "order-service",
  "version":    "1.4.2",
  "env":        "prod",
  "order_id":   "ord-456",                      // the operation's identifiers: top-level fields,
  "customer_id": "cust-789"                     // caller-defined, varying by operation
}
```

Rules:
- `trace_id` and `span_id` are required on every record; never omit (the minimum fields every record carries are `timestamp`, `level`, `message`, `trace_id`, `span_id`, `service`, per `micro/coding-standards/common.md` Standard 6; this shape is the one full record)
- the operation's identifiers (`order_id`, `customer_id`) are top-level fields beside the standard ones, never a catch-all dump of the request; they never reuse a standard field's name
- secrets, tokens, and PII must never appear in any field

### Metric Shape

```
{
  "name":       "order.processing.duration_ms",
  "value":      142,
  "type":       "histogram",                    // counter | gauge | histogram
  "timestamp":  "2026-05-30T14:22:01Z",
  "tags": {
      "service":  "order-service",
      "env":      "prod",
      "status":   "success",                    // always tag outcome
  }
}
```

Naming convention: metric names follow the OpenTelemetry semantic conventions where one exists (`http.server.request.duration`, unit seconds, with the `http.route` and `http.response.status_code` attributes). The local `{service}.{operation}.{unit}` rule applies only to custom metrics: e.g., `order.processing.duration_ms`, `pipeline.validation.error_count`. A rate is computed at query time, never emitted as its own metric.

### Trace Context

```
{
  "trace_id":   "abc123",    // generated once at system entry; propagated unchanged
  "span_id":    "def456",    // unique per operation; new at each hop
  "parent_id":  "ghi789",    // null at root; caller's span_id otherwise
  "service":    "order-service",
  "operation":  "process_order",
}
```

`trace_id` is generated once at the outermost entry point and propagated through every downstream call, log record, and AI invocation. It is never regenerated mid-flow.

---

## Core Patterns

### Structured Logging

Initialize the logger once with service context. Bind trace context once at entry in the language's context store (`eng-os-coding-standards-python` §6 `contextvars`, `eng-os-coding-standards-nodejs` §6 `AsyncLocalStorage`); downstream functions take no logger argument, and every log line reads the bound ids from the store.

```
// initialize once at startup
log = createLogger(service="order-service", version=SERVICE_VERSION, env=EXECUTION_MODE)

// at request entry: extract the caller's trace context, start a span, bind once
function handleRequest(request):
    parent = otel.propagation.extract(request.headers)        // W3C traceparent / tracestate
    span   = tracer.startSpan("handle_request", parent=parent)
    bindLogContext(trace_id=span.traceId, span_id=span.spanId, order_id=request.order_id)

    log.info("request received")

    try:
        result = processOrder(request)                        // no logger argument
        log.info("request completed", duration_ms=elapsed())
        return result
    catch ValidationError as e:
        log.warn("validation failed", field=e.field, reason=e.message)
        raise
    catch Exception as e:
        log.error("request failed", error=e.message)
        raise
    finally:
        span.end()
```

#### Failure Mode
Threading a logger through every function signature means any function that forgets the argument logs without `trace_id`; creating a new logger per call loses the bound ids. Either way cross-service correlation breaks. Binding once in the context store removes both.

---

### Trace Correlation

Generate `trace_id` once at the system entry point. Propagate it to every downstream service with the W3C `traceparent` and `tracestate` headers, through the OpenTelemetry propagator API, and carry it in every log record and AI call. Each hop gets its own `span_id` and inherits `trace_id` unchanged. Inbound context is extracted the same way. `X-Trace-Id` appears only as a legacy header accepted on input when a caller cannot send `traceparent`; it is never emitted.

```
// entry point: continue the caller's trace, or start one when there is none
function entryPoint(request):
    parent = otel.propagation.extract(request.headers)   // reads traceparent; a legacy X-Trace-Id is accepted only as a fallback
    span   = tracer.startSpan("process_order", parent=parent)   // new trace_id only when there is no parent
    bindLogContext(trace_id=span.traceId, span_id=span.spanId)
    return processRequest(request)

// downstream call: the propagator writes traceparent and tracestate for the current span
function callDownstream(endpoint, payload):
    headers = {}
    otel.propagation.inject(headers)
    return httpClient.post(endpoint, payload, headers=headers)

// AI call: the invocation gets its own child span; log lines carry the bound ids automatically
function callAIModel(prompt):
    with tracer.startSpan("ai.generate", attributes={ "ai.model": MODEL_ID }):
        log.info("ai call started", model=MODEL_ID)
        start  = now()
        result = model.generate(prompt)
        log.info("ai call completed", duration_ms=now() - start)
        return result
```

#### Failure Mode
Generating a new `trace_id` at each service boundary instead of propagating the original makes it impossible to reconstruct a complete request path across services.

---

### Signal Design by Boundary

Emit observability signals at every boundary where behavior, latency, or correctness can change. Define what to emit at each boundary type; do not rely on ad hoc logging in logic code.

```
// REQUEST BOUNDARY — every inbound request (OpenTelemetry semantic convention)
function emitRequestSignals(request, response, duration_seconds):
    // http.route is the route template (/orders/{id}), never the raw path (/orders/8812)
    metric.histogram("http.server.request.duration", duration_seconds,
        attributes={ "http.route": request.route, "http.response.status_code": response.status })
    // request count is the histogram's count; no separate counter
    if response.status >= 500:
        log.error("request error", status=response.status, duration_seconds=duration_seconds)

// PUBLISH / CONSUME BOUNDARY — every event produced or consumed
function emitEventSignals(event, direction, success):
    metric.counter("event." + direction + ".count", 1,
        tags={ topic: event.topic, success: success })
    if not success:
        log.error("event processing failed", topic=event.topic, event_id=event.id)

// TRANSFORMATION BOUNDARY — every pipeline stage
function emitPipelineSignals(stage, input_count, output_count, error_count, age_seconds):
    metric.gauge("pipeline.output_count",      output_count,  tags={ stage: stage })
    metric.gauge("pipeline.error_count",       error_count,   tags={ stage: stage })
    metric.gauge("pipeline.output_age_seconds", age_seconds,  tags={ stage: stage })

// VALIDATION BOUNDARY — every schema or contract check
function emitValidationSignals(schema_name, passed, violations):
    metric.counter("validation.result", 1,
        tags={ schema: schema_name, passed: passed })
    if not passed:
        log.warn("validation failed", schema=schema_name, violations=violations)

// AI GENERATION BOUNDARY — every model call (log lines carry the bound trace ids)
function emitAISignals(model, duration_ms, schema_valid, constraint_violated):
    metric.histogram("ai.call.duration_ms", duration_ms, tags={ model: model })
    metric.counter("ai.schema_compliance",    1, tags={ model: model, valid: schema_valid })
    metric.counter("ai.constraint_violation", 1, tags={ model: model, violated: constraint_violated })
    if constraint_violated:
        log.warn("ai output violated constraint", model=model)
```

#### Failure Mode
Emitting signals only inside business logic instead of at boundaries means a boundary failure (network timeout, schema rejection) produces no observable signal and is diagnosed by absence of expected signals, the hardest class of failure to debug.

---

## AI-Specific Observability

Track at minimum:
- determinism rate
- schema compliance rate
- constraint violation rate
- output variance
- assumption usage frequency where material

```
// record after every AI call — before downstream use
function recordAIMetrics(run_id, model, output, expected_schema, guardrails):
    schema_valid        = validate(output, expected_schema)
    constraint_violated = checkGuardrails(output, guardrails)

    // rates (compliance %, violation %) are computed at query time from these counters
    metric.counter("ai.schema_compliance",    1,
        tags={ model: model, valid: schema_valid })
    metric.counter("ai.constraint_violation", 1,
        tags={ model: model, violated: constraint_violated })
    metric.histogram("ai.output_token_count", len(output.tokens),
        tags={ model: model })

    log.info("ai run recorded",
        run_id=run_id,
        model=model,
        schema_valid=schema_valid,
        constraint_violated=constraint_violated,
    )

    // block downstream use if output is invalid
    if not schema_valid:
        raise AIOutputValidationError("output failed schema validation", run_id=run_id)
```

These metrics are not optional if AI output affects downstream systems or decisions.

---

## Metric Cardinality Budget

Every metric label is a multiplier on storage and query cost. Declare, per metric, the labels
it carries and the maximum distinct values each label may take. Never put an unbounded value
(user id, tenant id at scale, request id, URL with parameters, free text) on a metric label;
those belong on logs and traces, which are designed for high cardinality. Set a per-service
budget for total active time series and alert when it is exceeded.

- Failure mode: one metric labeled by `user_id` in a system with a hundred million users creates
  a hundred million time series, takes down the metrics backend, and blinds every other service
  that shares it.

## Log Persistence

A structured log record that meets this guide's shape requirements is not yet observability if
it only ever reaches stdout: stdout is not a store, and a process restart, a killed terminal, or
a supervisor's own log truncation can erase the only copy of the evidence a debugging session
needs. Every service must send its logs to a durable sink beyond the process's own stdout/stderr,
chosen from (not limited to): a rotating file handler on local disk, a managed log-aggregation
service (a process supervisor's own capture, e.g. PM2's log files, counts as this sink; it is not
a substitute for choosing one), or a database table for a domain-scoped audit trail (structured
rows keyed to a specific entity, e.g. one row per outbound call against a specific order or
request, queryable directly rather than only by log search). A database table is a deliberate
choice for a domain-scoped audit trail, distinct from and additive to general request/operation
logging; it does not replace file or managed-service persistence for signals with no natural
domain-entity key to hang off (e.g. the trace-bound log lines of a full poll cycle).

Whichever sink is chosen, declare explicitly:
- **Rotation policy**: a size or time trigger (e.g. daily, or at a fixed file size) and a retained
  file count, so a single long-lived process's log file cannot grow unbounded on local disk.
- **Retention window**: how long a log record survives before deletion or archival, driven by the
  system's actual debugging/audit need, not left as "however long the disk holds out."
- **Level policy across environments**: the minimum emitted level per `EXECUTION_MODE` (dev/stage/
  prod), consistent with `micro/coding-standards/common.md` Standard 1, so a production deployment
  is not silently drowning in debug-level volume, nor a dev environment silently missing the
  detail a live debugging session needs.

- Failure mode: a service logs correctly-shaped JSON to stdout only, with no declared sink,
  rotation, or retention; the process restarts during an incident and every log line from the
  minutes before the crash is gone, taking the only evidence with it.

## Trace Sampling

At production volume, tracing every request is neither affordable nor useful. Declare a
sampling policy: head-based sampling at a fixed rate for the baseline, plus tail-based or
rule-based sampling that keeps every trace that errored, exceeded its latency SLO, or carries a
debug flag. The sampling decision is made once at the entry point and propagated with the trace
context so every hop keeps or drops the same trace.

- Failure mode: uniform 1% sampling keeps the traces nobody needs and drops the one slow request
  the on-call engineer is looking for.

## Interoperability Standard

Emit metrics, logs, and traces through OpenTelemetry (the API and the semantic conventions), so
the signal shape in this guide is portable across backends and vendors. The standard record
shapes above map onto OpenTelemetry attributes; use the semantic-convention names where one
exists (`http.request.method`, `db.system`, `service.name`) rather than inventing a local alias.

- Failure mode: signal shapes tied to one vendor's agent make the next backend migration a
  rewrite of every instrumentation call site.

## AI-IDS Observability UI

The Scoring Run indicator and provenance drill-down for user-facing AI inference live in
`meso/ai-deterministic-systems.md`, Observability UI Contract: it is a product
requirement specific to AI-IDS systems, and this guide keeps the signal design that feeds it
(the AI-specific metrics above).

## Failure Modes

- missing metrics cause blind operation: failures become visible only through user reports
- unstructured logs prevent diagnosis: fields cannot be queried or correlated
- no validation events hide correctness failures: pipelines appear healthy while producing bad data
- no AI-specific metrics makes variance invisible: model degradation is undetectable until impact is large
- too much low-signal telemetry creates noise instead of clarity: signal-to-noise ratio matters as much as coverage
- `trace_id` not propagated to downstream calls: request paths cannot be reconstructed across service boundaries
- AI results shown to end users with no visible scorer/model/token provenance: unauditable the moment the result is wrong
- an unbounded label on a metric creates millions of time series and takes the metrics backend down for everyone
- uniform trace sampling keeps traces nobody needs and drops the slow, failed ones
- logs sent only to stdout with no declared sink/rotation/retention are lost the moment the process
  restarts, exactly when an incident makes them irreplaceable

---

## Definition of Done

Observability is complete when:

### Per change

- critical user and system flows have measurable signals
- validation and contract failures are surfaced as observable events
- latency, throughput, and errors are measurable at every boundary
- `trace_id` is generated at entry and propagated with W3C `traceparent` through all downstream calls, and bound once so every log line carries it
- log records carry the Standard 6 minimum fields (`timestamp`, `level`, `message`, `trace_id`, `span_id`, `service`) in the standard shape above
- metric attributes use route templates, never raw paths; names follow OpenTelemetry semantic conventions where one exists
- AI-specific correctness metrics exist where AI is used and gate downstream use on schema validity
- for AI-IDS systems, the Observability UI Contract in `meso/ai-deterministic-systems.md` is satisfied
- debugging a major failure is feasible without guesswork
- every metric declares its labels and their maximum cardinality; no unbounded identifier is a metric label; a per-service series budget is alerted on
- a trace sampling policy is declared that always keeps errored and SLO-breaching traces, decided once at entry and propagated
- instrumentation uses OpenTelemetry APIs and semantic conventions

### Standing (release and audit)

- every service's logs reach a durable sink beyond process stdout, with a declared rotation policy, retention window, and per-`EXECUTION_MODE` level policy
