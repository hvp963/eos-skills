# Observability

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for making systems measurable, debuggable, and explainable.

### What This Is Not
- not just dashboards
- not just logging
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
  "service":    "order-service",
  "version":    "1.4.2",
  "env":        "prod",
  "context": {                                  // caller-defined; varies by operation
      "order_id":    "ord-456",
      "customer_id": "cust-789",
  }
}
```

Rules:
- `trace_id` is required on every record; never omit
- `context` carries the identifiers relevant to the operation, not a catch-all
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

Naming convention: `{service}.{operation}.{unit}`; e.g., `order.processing.duration_ms`, `pipeline.validation.error_count`.

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

Initialize the logger once with service context. Bind `trace_id` and operation identifiers at request entry. Pass the bound child logger into downstream functions: do not rebind identifiers at every call site.

```
// initialize once at startup
log = createLogger(service="order-service", version=SERVICE_VERSION, env=EXECUTION_MODE)

// at request entry — bind trace context and operation identifiers
function handleRequest(request):
    traceId = request.headers.get("X-Trace-Id") ?? generateUUID()
    reqLog  = log.child(trace_id=traceId, order_id=request.order_id)

    reqLog.info("request received")

    try:
        result = processOrder(request, log=reqLog)
        reqLog.info("request completed", duration_ms=elapsed())
        return result
    catch ValidationError as e:
        reqLog.warn("validation failed", field=e.field, reason=e.message)
        raise
    catch Exception as e:
        reqLog.error("request failed", error=e.message)
        raise
```

#### Failure Mode
Creating a new logger instance per request or per function call instead of passing a child logger loses the bound `trace_id` and makes cross-service log correlation impossible.

---

### Trace Correlation

Generate `trace_id` once at the system entry point. Propagate it in headers to every downstream service and in every log record and AI call. Each hop generates its own `span_id` but inherits `trace_id` unchanged.

```
// entry point — generate trace_id if not provided by upstream caller
function entryPoint(request):
    traceId  = request.headers.get("X-Trace-Id") ?? generateUUID()
    spanId   = generateUUID()
    parentId = null

    context = TraceContext(trace_id=traceId, span_id=spanId, parent_id=parentId)
    return processWithContext(request, context)

// downstream call — propagate trace context in headers
function callDownstream(endpoint, payload, context):
    headers = {
        "X-Trace-Id":  context.trace_id,    // unchanged across all hops
        "X-Span-Id":   generateUUID(),       // new per hop
        "X-Parent-Id": context.span_id,      // caller's span_id becomes parent
    }
    return httpClient.post(endpoint, payload, headers=headers)

// AI call — trace_id applies; AI invocation gets its own span
function callAIModel(prompt, context):
    aiSpanId = generateUUID()
    log.info("ai call started",
        trace_id=context.trace_id,
        ai_span_id=aiSpanId,
        model=MODEL_ID,
    )

    start  = now()
    result = model.generate(prompt)

    log.info("ai call completed",
        trace_id=context.trace_id,
        ai_span_id=aiSpanId,
        duration_ms=now() - start,
    )
    return result
```

#### Failure Mode
Generating a new `trace_id` at each service boundary instead of propagating the original makes it impossible to reconstruct a complete request path across services.

---

### Signal Design by Boundary

Emit observability signals at every boundary where behavior, latency, or correctness can change. Define what to emit at each boundary type; do not rely on ad hoc logging in logic code.

```
// REQUEST BOUNDARY — every inbound request
function emitRequestSignals(request, response, duration_ms, trace_id):
    metric.histogram("request.duration_ms", duration_ms,
        tags={ endpoint: request.path, status: response.status, env: ENV })
    metric.counter("request.count", 1,
        tags={ endpoint: request.path, status: response.status })
    if response.status >= 500:
        log.error("request error",
            trace_id=trace_id, status=response.status, duration_ms=duration_ms)

// PUBLISH / CONSUME BOUNDARY — every event produced or consumed
function emitEventSignals(event, direction, success, trace_id):
    metric.counter("event." + direction + ".count", 1,
        tags={ topic: event.topic, success: success })
    if not success:
        log.error("event processing failed",
            trace_id=trace_id, topic=event.topic, event_id=event.id)

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

// AI GENERATION BOUNDARY — every model call
function emitAISignals(trace_id, model, duration_ms, schema_valid, constraint_violated):
    metric.histogram("ai.call.duration_ms", duration_ms, tags={ model: model })
    metric.counter("ai.schema_compliance",    1, tags={ model: model, valid: schema_valid })
    metric.counter("ai.constraint_violation", 1, tags={ model: model, violated: constraint_violated })
    if constraint_violated:
        log.warn("ai output violated constraint",
            trace_id=trace_id, model=model)
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
function recordAIMetrics(run_id, model, output, expected_schema, guardrails, trace_id):
    schema_valid        = validate(output, expected_schema)
    constraint_violated = checkGuardrails(output, guardrails)

    metric.counter("ai.schema_compliance_rate",   1,
        tags={ model: model, valid: schema_valid })
    metric.counter("ai.constraint_violation_rate", 1,
        tags={ model: model, violated: constraint_violated })
    metric.histogram("ai.output_token_count", len(output.tokens),
        tags={ model: model })

    log.info("ai run recorded",
        run_id=run_id,
        trace_id=trace_id,
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
domain-entity key to hang off (e.g. `traceMixin` output for a full poll cycle).

Whichever sink is chosen, declare explicitly:
- **Rotation policy**: a size or time trigger (e.g. daily, or at a fixed file size) and a retained
  file count, so a single long-lived process's log file cannot grow unbounded on local disk.
- **Retention window**: how long a log record survives before deletion or archival, driven by the
  system's actual debugging/audit need, not left as "however long the disk holds out."
- **Level policy across environments**: the minimum emitted level per `EXECUTION_MODE` (dev/stage/
  prod), consistent with `logger.ts`'s/`logging_config.py`'s own execution-mode mapping elsewhere
  in this guide, so a production deployment is not silently drowning in debug-level volume, nor a
  dev environment silently missing the detail a live debugging session needs.

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
- critical user and system flows have measurable signals
- validation and contract failures are surfaced as observable events
- latency, throughput, and errors are measurable at every boundary
- `trace_id` is generated at entry and propagated through all downstream calls and logs
- log records conform to the standard shape: timestamp, level, message, trace_id, service, context
- AI-specific correctness metrics exist where AI is used and gate downstream use on schema validity
- for AI-IDS systems, the Observability UI Contract in `meso/ai-deterministic-systems.md` is satisfied
- debugging a major failure is feasible without guesswork
- every metric declares its labels and their maximum cardinality; no unbounded identifier is a metric label; a per-service series budget is alerted on
- a trace sampling policy is declared that always keeps errored and SLO-breaching traces, decided once at entry and propagated
- instrumentation uses OpenTelemetry APIs and semantic conventions
- every service's logs reach a durable sink beyond process stdout, with a declared rotation policy, retention window, and per-`EXECUTION_MODE` level policy
