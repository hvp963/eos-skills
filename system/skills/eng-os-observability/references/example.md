# Worked Example: One Service's Signals

Source: illustrates `../SKILL.md` Signal Design by Boundary, Metric Cardinality Budget, Trace
Sampling, Log Persistence, and Interoperability Standard, applied to one service: `order-api`, an
HTTP API with a Postgres database and one downstream call to a payment provider. Record shapes
follow `standard-data-models.md`.

## Metric Declarations (`src/shared/telemetry/metrics.ts`)

Every metric is declared once, with its labels and the most distinct values each label may take.

| Metric | Type, unit | Labels (maximum distinct values) | Why bounded |
|---|---|---|---|
| `http.server.request.duration` | histogram, seconds (buckets 0.05, 0.1, 0.2, 0.4, 0.8, 1.6) | `http.route` (40), `http.request.method` (5), `http.response.status_code` (12) | route template `/orders/{id}`, never the raw path `/orders/8812` |
| `http.client.request.duration` | histogram, seconds | `server.address` (3), `http.response.status_code` (12) | three named downstream hosts |
| `db.client.operation.duration` | histogram, seconds | `db.operation.name` (6) | fixed statement kinds |
| `order.placement.result_count` | counter | `result` (4: `placed`, `rejected_stock`, `rejected_payment`, `failed`) | custom metric: `{service}.{operation}.{unit}` |

Series budget: 40 × 5 × 12 × 7 buckets is 16,800 series for the request histogram; the service total
is held under 25,000 active series. An alert fires at 80% of the budget, and a new label needs a
row in this table first. `customer_id` and `order_id` are never labels: they go on logs and traces.

## Trace Sampling Policy

- Head-based: keep 10% of traces, decided once at the entry point and carried in `traceparent`, so
  every hop keeps or drops the same trace.
- Tail rules at the collector: keep every trace with an error status, every trace whose root span
  exceeded the 400ms latency SLO, and every trace carrying a debug flag.

## One Hop, Traced

The inbound request carries `traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`.
The service extracts it with the OpenTelemetry propagator, starts a server span as its child, and
binds `trace_id` and `span_id` once in the context store. The payment call writes a new
`traceparent` with the same trace id and the client span's id, through `propagation.inject`. Every
log line on both sides carries the same `trace_id` with no argument threading:

```
{"timestamp":"2026-11-22T10:15:02.114Z","level":"INFO","message":"order placed","trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","span_id":"00f067aa0ba902b7","service":"order-api","version":"2.3.0","env":"prod","order_id":"ord-8812"}
```

## Log Persistence

| `EXECUTION_MODE` | Minimum level | Sink | Rotation | Retention |
|---|---|---|---|---|
| `dev` | DEBUG | rotating file `logs/order-api.log` | daily, keep 7 files | 7 days |
| `stage` | INFO | managed log service | by the service | 14 days |
| `prod` | WARN | managed log service | by the service | 30 days, then archived 1 year |

Standard out alone is never the sink: a restart mid-incident would erase the only copy.
