# Worked Example: Freshness Badge and Canonical/Shadow Divergence

## Freshness SLA surfaced to the UI/API

Backend pipeline stamps `produced_at` and emits `pipeline.output_age_seconds` per the Freshness SLA
pattern in `SKILL.md`. That signal must travel to the consumer, not stop at the metric. A pricing
feed with a 15-minute SLA returns:

```json
GET /api/products/prod_881/price

{
  "data": {
    "product_id": "prod_881",
    "price_cents": 4299,
    "currency": "USD"
  },
  "freshness": {
    "as_of": "2026-07-01T14:10:00Z",
    "sla_minutes": 15,
    "stale": false
  }
}
```

If the upstream pricing job has failed silently for the last 40 minutes, the same endpoint must
still report it rather than keep serving the last good price as if current:

```json
{
  "data": {
    "product_id": "prod_881",
    "price_cents": 4299,
    "currency": "USD"
  },
  "freshness": {
    "as_of": "2026-07-01T13:32:00Z",
    "sla_minutes": 15,
    "stale": true
  }
}
```

The UI renders a "Price as of 1:32 PM (stale)" badge next to the price whenever `freshness.stale`
is `true`, the same field the backend already computed for the alert, reused at the point of
consumption instead of a second, separate staleness check living only in the UI. For a fused
online/offline score, `freshness` would carry one entry per sub-source (e.g.
`{"realtime": {"as_of": ..., "stale": false}, "batch": {"as_of": ..., "stale": true}}`) rather than
a single collapsed timestamp, so a stale batch component can't hide behind a fresh realtime one.

## Canonical/Shadow Divergence Tracking

**Caveat (restated from `SKILL.md`):** this is a simplified stand-in for real MDM/golden-record
reconciliation: no multi-way merges, survivorship rules, or confidence scoring. Use it only for
lightweight "which copy do I trust" signaling.

A `customers` table with a self-referential FK plus a divergence flag:

```json
// canonical record — the trusted copy
{
  "id": "cust_9f8a1c",
  "email": "j.rivera@example.com",
  "canonical_id": null,
  "has_diverged": false
}

// shadow record — a duplicate ingested from a second source system, pointing back at the canonical record
{
  "id": "cust_3b71e0",
  "email": "jrivera@example.com",
  "canonical_id": "cust_9f8a1c",
  "has_diverged": true
}
```

A consumer reading `cust_3b71e0` can cheaply tell two things without a reconciliation engine: which
record to trust (follow `canonical_id` to `cust_9f8a1c`), and that the two have drifted
(`has_diverged: true`, here because the email formatting differs between the two source records).
