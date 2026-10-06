# Standard Data Models

These shapes define the required structure for each signal type. Replace placeholder field values
with production-validated field names and conventions when available.

## Log Record

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

## Metric Shape

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

Naming convention: `{service}.{operation}.{unit}`, e.g., `order.processing.duration_ms`, `pipeline.validation.error_count`.

## Trace Context

```
{
  "trace_id":   "abc123",    // generated once at system entry; propagated unchanged
  "span_id":    "def456",    // unique per operation; new at each hop
  "parent_id":  "ghi789",    // null at root; caller's span_id otherwise
  "service":    "order-service",
  "operation":  "process_order",
}
```

`trace_id` is generated once at the outermost entry point and propagated through every downstream
call, log record, and AI invocation. It is never regenerated mid-flow.

## Core Patterns

### Structured Logging

Initialize the logger once with service context. Bind `trace_id` and operation identifiers at
request entry. Pass the bound child logger into downstream functions; do not rebind identifiers
at every call site.

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

**Failure mode:** Creating a new logger instance per request or per function call instead of
passing a child logger loses the bound `trace_id` and makes cross-service log correlation impossible.

### Trace Correlation

Generate `trace_id` once at the system entry point. Propagate it in headers to every downstream
service and in every log record and AI call. Each hop generates its own `span_id` but inherits
`trace_id` unchanged.

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

**Failure mode:** Generating a new `trace_id` at each service boundary instead of propagating the
original makes it impossible to reconstruct a complete request path across services.

### Signal Design by Boundary (implementation)

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

**Failure mode:** Emitting signals only inside business logic instead of at boundaries means a
boundary failure (network timeout, schema rejection) produces no observable signal and is
diagnosed by absence of expected signals, the hardest class of failure to debug.

### AI Metrics Recording

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
