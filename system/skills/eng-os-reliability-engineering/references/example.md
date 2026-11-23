# Reliability Engineering: Worked Example

One service, `order-api`, with Scale Targets of 800 peak RPS, p99 400ms, 99.9% monthly
availability.

## SLO declaration (`docs/slo/order-api.yaml`)

```yaml
service: order-api
slos:
  - name: availability
    sli: sum(http_server_request_duration_seconds_count{http_response_status_code!~"5.."}) / sum(http_server_request_duration_seconds_count)
    window: 30d
    target: 0.999
    alerts:
      - { burn_rate: 14.4, lookback: 1h, severity: page }
      - { burn_rate: 6,    lookback: 6h, severity: ticket }
  - name: latency
    sli: sum(http_server_request_duration_seconds_bucket{le="0.4"}) / sum(http_server_request_duration_seconds_count)
    window: 30d
    target: 0.99
```

Both SLIs are good events over total events from the OpenTelemetry HTTP histogram
(`http.server.request.duration`, exported to Prometheus as `http_server_request_duration_seconds`).
`good` and `total` are counters; the SLO tool takes their increase over `window`. The histogram
declares a 0.4s bucket boundary, so the latency SLI counts requests that took 400ms or less.

The budget for availability is 43 minutes per 30 days. In the last quarter it was spent twice;
both times the release train paused for reliability work, which is the mechanism working.

## Dependency ranking and breaker configuration (`src/config/env.ts`)

```typescript
export const dependencies = {
  postgres:        { critical: true,  timeoutMs: 250, breaker: { failureRate: 0.5, window: '30s', cooldown: '10s' } },
  paymentGateway:  { critical: true,  timeoutMs: 2000, breaker: { failureRate: 0.3, window: '60s', cooldown: '30s' } },
  recommendations: { critical: false, timeoutMs: 150, breaker: { failureRate: 0.5, window: '30s', cooldown: '60s' },
                     degraded: 'omit section, set X-Degraded: recommendations' },
  pricingCache:    { critical: false, timeoutMs: 50,  breaker: { failureRate: 0.5, window: '30s', cooldown: '30s' },
                     degraded: 'read pricing from postgres (fresh, no staleness marker needed)' },
} as const;
```

Wrong version, for contrast: every call used the HTTP client's default of no timeout, and
`recommendations` had no `critical` flag, so its outage in March took checkout down for 11
minutes. The degraded path above now serves checkout without the sidebar and the breaker trips
within 30 seconds.

## Pool and queue bounds

| Resource | Bound | At bound |
|---|---|---|
| Postgres pool (per pod) | 20 connections | queue up to 50 waiters, 100ms max wait, then `503` |
| Order intake queue | 10,000 messages | producer receives nack; client shown "try again" (`ORD000031`) |
| Batch export workers | separate pool of 4 | never shares the interactive pool |

## Game day record (2026-08-14)

| Hypothesis | Method | Outcome | Gap |
|---|---|---|---|
| Recommendations outage degrades, does not fail checkout | inject 100% errors for 5 min in stage | breaker tripped at 28s; checkout p99 unchanged | none |
| Postgres pool exhaustion sheds rather than hangs | hold 20 connections open per pod | waiters rejected with `503` after 100ms; alert fired | dashboard lacked pool-wait histogram; added |
| Loss of cell A is contained to cell A's tenants | stop cell A's compute in stage | cell A's tenants saw errors; cell B p99 unchanged, no cross-cell spillover | none |
| Region failover to the standby region completes within RTO (1h) | fail the stage region over to its standby | 14 minutes to full traffic in the standby region | runbook step 3 referenced an old DNS name; fixed |
