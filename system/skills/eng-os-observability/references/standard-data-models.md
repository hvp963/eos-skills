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
  "span_id":    "def456",                       // the current operation's span; never null
  "service":    "order-service",
  "version":    "1.4.2",
  "env":        "prod",
  "order_id":   "ord-456",                      // the operation's identifiers: top-level fields,
  "customer_id": "cust-789"                     // caller-defined, varying by operation
}
```

Rules:
- `trace_id` and `span_id` are required on every record; never omit (the minimum fields every record carries are `timestamp`, `level`, `message`, `trace_id`, `span_id`, `service`, per `eng-os-coding-standards-common` Standard 6; this shape is the one full record)
- the operation's identifiers (`order_id`, `customer_id`) are top-level fields beside the standard ones, never a catch-all dump of the request; they never reuse a standard field's name
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

Naming convention: metric names follow the OpenTelemetry semantic conventions where one exists (`http.server.request.duration`, unit seconds, with the `http.route` and `http.response.status_code` attributes). The local `{service}.{operation}.{unit}` rule applies only to custom metrics: e.g., `order.processing.duration_ms`, `pipeline.validation.error_count`. A rate is computed at query time, never emitted as its own metric.

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

**Failure mode:** Threading a logger through every function signature means any function that forgets the argument logs without `trace_id`; creating a new logger per call loses the bound ids. Either way cross-service correlation breaks. Binding once in the context store removes both.

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

**Failure mode:** Generating a new `trace_id` at each service boundary instead of propagating the original makes it impossible to reconstruct a complete request path across services.

### Signal Design by Boundary (implementation)

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

**Failure mode:** Emitting signals only inside business logic instead of at boundaries means a boundary failure (network timeout, schema rejection) produces no observable signal and is diagnosed by absence of expected signals, the hardest class of failure to debug.

### AI Metrics Recording

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
