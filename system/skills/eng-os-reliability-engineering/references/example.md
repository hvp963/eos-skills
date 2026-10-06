# Reliability Engineering: Worked Example

One service, `order-api`, with Scale Targets of 800 peak RPS, p99 400ms, 99.9% monthly
availability.

## SLO declaration (`docs/slo/order-api.yaml`)

```yaml
service: order-api
slos:
  - name: availability
    sli: sum(http_requests_total{status!~"5.."}) / sum(http_requests_total)
    window: 30d
    target: 0.999
    alerts:
      - { burn_rate: 14.4, lookback: 1h, severity: page }
      - { burn_rate: 6,    lookback: 6h, severity: ticket }
  - name: latency
    sli: histogram_quantile(0.99, http_request_duration_seconds) < 0.4
    window: 1h
    target: 0.99
```

The budget for availability is 43 minutes per 30 days. In the last quarter it was spent twice;
both times the release train paused for reliability work, which is the mechanism working.

## Dependency ranking and breaker configuration (`src/config.ts`)

```typescript
export const dependencies = {
  postgres:        { critical: true,  timeoutMs: 250, breaker: { failureRate: 0.5, window: '30s', cooldown: '10s' } },
  paymentGateway:  { critical: true,  timeoutMs: 2000, breaker: { failureRate: 0.3, window: '60s', cooldown: '30s' } },
  recommendations: { critical: false, timeoutMs: 150, breaker: { failureRate: 0.5, window: '30s', cooldown: '60s' },
                     degraded: 'omit section, set X-Degraded: recommendations' },
  pricingCache:    { critical: false, timeoutMs: 50,  degraded: 'read pricing from postgres, mark stale=false' },
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
| Cell failover completes within RTO (1h) | drain cell A routing | 14 minutes to full traffic on cell B | runbook step 3 referenced an old DNS name; fixed |
