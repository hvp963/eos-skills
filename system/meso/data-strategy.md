# Data Strategy

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for designing and operating data systems that support ingestion, processing, storage, and consumption at scale.

### What This Is Not
- not a single ETL implementation guide
- not a tool inventory
- not a substitute for database design

## Scope
- Level: Meso
- Applies To: Batch, streaming, analytical, and AI-feedback data systems

---

## Applied Principles

### Idempotency by Default
Pipelines must be safe to rerun, replay, or retry.

### Contracts as Source of Truth
Data producers and consumers must share explicit schema and semantic expectations.

### Scalability Through Partitioning
Data movement and computation must scale through partitioning.

### Validation at Boundaries
Data quality must be checked at ingestion, transformation, and publication boundaries.

### Observability as a First-Class Concern
Freshness, throughput, failures, and quality must be measurable.

---

## Core Data Patterns

### Layered Data Architecture
Separate raw, refined, and curated representations.

#### Why
Preserves fidelity while allowing safe transformation and consumption-ready outputs.

#### Failure Mode
Mixing raw and curated logic destroys auditability and reprocessing clarity.

---

### Batch and Streaming Hybrid
Use batch and streaming together when latency and throughput requirements differ.

#### Why
Streaming supports freshness; batch supports large recomputation and stable aggregation.

#### Failure Mode
Using only one mode for all problems causes either excessive latency or excessive complexity.

---

### Schema Versioning
Treat schema evolution as a first-class concern.

#### Why
Uncontrolled changes break downstream consumers and corrupt historical interpretation.

#### Failure Mode
Schema drift causes pipeline failures or silent misinterpretation.

---

### De-duplication at Multiple Boundaries
Deduplicate where duplicates are likely to emerge.

#### Why
Duplicates can arise at ingestion, replay, retry, and downstream joins.

#### Failure Mode
Duplicate records distort analytics and AI feedback loops.

---

### Caching for Repeated Access
Use caching where repeated access patterns justify lower-latency retrieval.

#### Why
Can reduce repeated expensive reads for reference data, profiles, and frequently accessed aggregates.

#### Failure Mode
Cached stale data silently undermines trust if invalidation is weak.

---

### Idempotent Write

Upsert by stable natural key. On match, merge or skip. On replay, produce the same result.

```
function writeRecord(record):
    existing = db.findByKey(natural_key=record.external_id)

    if existing is null:
        db.insert(record)
        log.info("record inserted", id=record.external_id)

    elif existing.updated_at >= record.updated_at:
        log.info("record skipped — not newer", id=record.external_id)
        return  // idempotent: replay of older or equal data is a no-op

    else:
        db.update(id=existing.id, fields=record.diffFrom(existing))
        log.info("record updated", id=record.external_id)
```

The natural key must be stable and sourced from the upstream system, not a database-generated ID assigned at write time. If the upstream system has no natural key, derive one deterministically (e.g., hash of source + record identifiers).

#### Failure Mode
Writing without a uniqueness check on replay inserts duplicates on every rerun. Using an auto-increment primary key as the deduplication key means every insert is treated as new.

---

### Schema Evolution

Treat schema changes as additive first. Breaking changes require a version bump and a migration script. Consumers must validate the version they receive.

```
// additive change — safe; no version bump
// before: { "id": "123", "amount": 99.99 }
// after:  { "id": "123", "amount": 99.99, "currency": "USD" }
// downstream consumers that do not read "currency" are unaffected

// breaking change — requires version bump and migration
schema_version_2:
    changed: "amount" (float) → "amount_cents" (integer)
    reason:  floating point precision errors in financial calculations
    migration:
        script: migrate_v1_to_v2.sql
        steps:
            - add column "amount_cents" integer
            - backfill: amount_cents = round(amount * 100)
            - deprecate "amount" (keep for one release cycle)
            - remove "amount" after all consumers updated

// consumer — validate schema version at read time
function readRecord(raw):
    if raw.schema_version > SUPPORTED_VERSION:
        log.error("unsupported schema version", received=raw.schema_version, supported=SUPPORTED_VERSION)
        raise SchemaVersionError("consumer must be updated")
    return parseV(raw.schema_version, raw)
```

Breaking changes must not be deployed until all consumers are updated or a compatibility shim is in place. Removing a field before consumers stop reading it is a production outage.

#### Failure Mode
Renaming or removing a field without bumping the schema version silently breaks consumers that expected the old field, with no error until data is read or processed.

---

### Freshness SLA

Timestamp each stage output. Emit data age as a metric. Alert when age exceeds the SLA. Consumers must not silently treat stale data as fresh.

```
// producer — stamp every record and every pipeline output
record.produced_at   = utcNow()
record.pipeline_run  = pipeline.run_id

// freshness metric — emit at each pipeline boundary
metric.gauge(
    name  = "pipeline.output_age_seconds",
    value = (utcNow() - lastSuccessfulRun.completed_at).seconds,
    tags  = { pipeline: pipeline.name, stage: stage.name },
)

// alert rule
alert "pipeline_stale":
    condition: pipeline.output_age_seconds > FRESHNESS_SLA_SECONDS for 5m
    severity:  warning
    notify:    data-on-call

// consumer — check age before using data
function loadReferenceData():
    data = cache.get("reference_data")
    ageSeconds = (utcNow() - data.produced_at).seconds

    if ageSeconds > FRESHNESS_SLA_SECONDS:
        log.warn("reference data exceeds freshness SLA", age_seconds=ageSeconds, sla=FRESHNESS_SLA_SECONDS)
        // depending on use case: raise, use-with-warning, or refresh
        raise StaleDataError("reference data is too old to use safely")

    return data
```

The freshness SLA must be defined per dataset, not as a system-wide default. A financial pricing feed has a different tolerance than a weekly product catalog.

#### Failure Mode
A pipeline that fails silently continues to serve its last successful output as if it were fresh. Without a freshness metric and alert, consumers operate on stale data indefinitely with no signal.

---

### UI/Consumer-Facing Freshness

A freshness SLA that stops at a backend metric has not actually reached the consumer. Where a field or dataset has a declared freshness SLA, the staleness signal must travel with the data all the way to the point where it is rendered or consumed, instead of staying buried in a pipeline dashboard.

This rule applies only to fields and datasets with a declared freshness SLA. It is not a blanket requirement to badge every value in every UI; data with no declared SLA is out of scope until an SLA is defined for it.

```
// API response — freshness travels with the data, not just to a metrics backend
GET /api/products/prod_881/price

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

// UI — reuses freshness.stale, the same field computed for the backend alert,
// instead of a second staleness check that lives only in the frontend
if response.freshness.stale:
    render badge("Price as of " + formatTime(response.freshness.as_of) + " (stale)")
```

When a displayed value fuses multiple sources with different freshness characteristics: for example an online/offline fusion score blending a real-time signal with a batch-computed signal: a single collapsed timestamp is not sufficient. Report freshness per sub-source so a stale component cannot hide behind a fresh one:

```
"freshness": {
    "realtime": { "as_of": "2026-07-01T14:09:50Z", "stale": false },
    "batch":    { "as_of": "2026-06-30T02:00:00Z", "stale": true }
}
```

Treat a missing freshness indicator on a screen that renders SLA'd data as a shippable bug, not a follow-up nice-to-have.

#### Failure Mode
A stale badge silently omitted from the UI is functionally equivalent to a silent pipeline failure: the backend may have a correct metric and alert, but the end user (the actual consumer of the data) has no way to know the value in front of them may be stale. This is most dangerous in fusion displays: an online/offline fusion score shown as one confident-looking number gives no indication that its batch-computed portion stopped updating hours or days ago.

---

### Canonical/Shadow Divergence Tracking

Some entities need a lightweight way to say "this record is a duplicate or derived copy of that other record, and here is whether the two have drifted apart": without standing up a full reconciliation system. Model this with a self-referential foreign key to the canonical record plus a flag marking divergence: `canonical_id` + `has_diverged`, or equivalently `duplicate_of_id` + `is_reconciled`.

```
// canonical record — the trusted copy
{ "id": "cust_9f8a1c", "email": "j.rivera@example.com", "canonical_id": null, "has_diverged": false }

// shadow record — ingested from a second source system, points back at the canonical record
{ "id": "cust_3b71e0", "email": "jrivera@example.com", "canonical_id": "cust_9f8a1c", "has_diverged": true }
```

A consumer reading the shadow record can cheaply answer two questions without a reconciliation engine: which record to trust (follow `canonical_id`), and whether the two have drifted (`has_diverged`).

This is a simplified stand-in for real master-data-management or golden-record reconciliation, not a production-ready MDM solution by itself. It does not handle multi-way merges, survivorship rules, confidence scoring, or conflict resolution across more than two records. Use it for lightweight in-app "is this a duplicate or stale copy" signaling. Reach for a dedicated MDM/golden-record system once merge history, survivorship rules, or reconciliation logic across more than two records becomes non-trivial.

#### Failure Mode
Treating `canonical_id` + `has_diverged` as a substitute for real reconciliation causes teams to skip building actual survivorship or merge logic: the flag tells you divergence exists but never resolves it, so unreconciled shadow records accumulate indefinitely with no owner or process to fix them.

---

### Late-Arriving Data and Watermarks

Events arrive out of order and late. Every time-windowed computation declares an event-time
watermark (how late an event may arrive and still be included), what happens to events later
than that (a correction pass, a late-arrivals table, or a documented drop), and whether
downstream outputs are recomputed when late data lands. Consumers of a windowed output must be
told whether the window is provisional or final.

- Failure mode: a daily aggregate computed at midnight from data that keeps arriving until 3am
  is silently wrong every day, and nobody can say by how much.

### Delivery Semantics

Every pipeline boundary declares its delivery guarantee: at-most-once, at-least-once, or
effectively-once (at-least-once delivery plus idempotent consumption keyed on a stable
identifier). Assume at-least-once from every external source and design the consumer to be
idempotent; do not build on a broker's exactly-once promise across a boundary it does not own.

- Failure mode: a consumer that assumes exactly-once double-counts on every broker rebalance,
  redeploy, or retry.

## Data Quality Strategy

Data quality should be validated across:
- structure
- required fields
- semantic correctness where feasible
- freshness
- completeness
- uniqueness when relevant

Failure to define quality criteria leads to systems that "run" but cannot be trusted.

---

## Failure Modes

- duplicate data causes incorrect metrics and model training inputs
- schema drift breaks transformations or changes meaning silently
- weak partitioning creates scale limits
- missing lineage obscures source of corruption
- replay without idempotency compounds bad outputs
- poor freshness controls make downstream decisions stale
- a freshness badge omitted from the consuming UI makes staleness invisible to the end user
- treating canonical/shadow divergence flags as a substitute for real reconciliation lets drift accumulate unresolved
- windowed outputs computed before late data lands are silently wrong with no provisional/final marker
- consumers that assume exactly-once delivery double-count on every retry or rebalance

---

## Definition of Done

Data strategy is complete when:
- producer and consumer contracts are explicit
- partitioning strategy is defined
- idempotency and de-duplication are addressed
- batch versus streaming choices are justified
- quality checks are defined
- freshness expectations are explicit
- for any field or dataset with a declared freshness SLA, every UI or API response rendering it (including fused data) surfaces a freshness/staleness indicator at the point of consumption
- canonical/shadow divergence tracking, where used, is documented as a lightweight signal and not mistaken for full MDM reconciliation
- reprocessing and replay implications are understood
- every time-windowed computation declares its watermark, its late-data handling, and whether outputs are provisional or final
- every pipeline boundary declares its delivery guarantee, and consumers are idempotent under at-least-once delivery
- retention, lineage, and classification of each dataset are declared per `meso/data-governance.md`
