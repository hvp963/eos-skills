---
name: eng-os-data-strategy
description: "Use when building data pipelines: batch/streaming design, schema evolution, idempotent ingestion, freshness SLAs."
sources:
  - meso/data-strategy.md
  - micro/templates/etl-template.md
globs: ["**/*.sql", "**/migrations/**", "**/models/**", "**/schema/**"]
always_apply: false
verified_platforms: [claude-code]
---

# Data Strategy

Apply these rules when designing or reviewing ingestion, transformation, or publication of data pipelines (batch, streaming, or hybrid).

## Principles

- **Idempotency by default.** Pipelines must be safe to rerun, replay, or retry.
- **Contracts as source of truth.** Producers and consumers must share explicit schema and semantic expectations.
- **Scalability through partitioning.** Data movement and computation scale through deliberate partitioning.
- **Validation at boundaries.** Check data quality at ingestion, transformation, and publication boundaries.
- **Observability as a first-class concern.** Freshness, throughput, failures, and quality must be measurable.

## Core Patterns

### Layered Data Architecture
Separate raw, refined, and curated representations. Mixing raw and curated logic destroys auditability and reprocessing clarity.

### Batch and Streaming Hybrid
Use streaming for freshness, batch for large recomputation/stable aggregation. Using only one mode for every problem causes either excessive latency or excessive complexity.

### De-duplication at Multiple Boundaries
Duplicates can arise at ingestion, replay, retry, and downstream joins; deduplicate at each point where they're likely to emerge, not just at the source.

### Idempotent Write

Upsert by a stable natural key sourced from the upstream system (never a DB-generated ID). If no natural key exists upstream, derive one deterministically (e.g., hash of source + record identifiers).

```
function writeRecord(record):
    existing = db.findByKey(natural_key=record.external_id)
    if existing is null:
        db.insert(record)
    elif existing.updated_at >= record.updated_at:
        return  // idempotent no-op: replay of older/equal data
    else:
        db.update(id=existing.id, fields=record.diffFrom(existing))
```
- Failure mode: writing without a uniqueness check on replay inserts duplicates on every rerun; using an auto-increment PK as the dedup key treats every insert as new.

### Schema Evolution

Treat changes as additive first (new optional field, no version bump, consumers ignore unknown fields). Breaking changes (rename, type change, removal) require a version bump, a migration script, and consumer validation of the version they receive. Do not deploy a breaking change until all consumers are updated or a compatibility shim exists; removing a field before consumers stop reading it is a production outage.
- Failure mode: renaming/removing a field without a version bump silently breaks consumers with no error until data is read.

### Freshness SLA

Stamp every stage's output with a produced-at timestamp and pipeline run ID. Emit data age as a metric at each pipeline boundary. Alert when age exceeds the SLA, defined per dataset (a pricing feed and a weekly catalog have different tolerances). Consumers must check age before treating cached/reference data as fresh, and fail or warn explicitly if stale.
- Failure mode: a pipeline that fails silently keeps serving its last successful output as if fresh; without a freshness metric and alert, consumers operate on stale data indefinitely with no signal.

## UI/Consumer-Facing Freshness

Freshness is not only a backend metric: where a pipeline output is rendered to a user, the staleness signal must travel with it all the way to the UI.

**Rule:** This rule applies only to fields/datasets that have a DECLARED freshness SLA; it is not a blanket rule requiring a freshness badge on all data everywhere. Any UI element that displays data with a defined freshness SLA must show a freshness indicator (badge, "as of" timestamp, or explicit stale/degraded state) at the point of consumption. Omitting the badge on the UI is not a cosmetic gap: it is functionally equivalent to a silent pipeline failure, because the consumer of the data (the end user) has no way to know the data may be stale. Data with no declared SLA is out of scope for this rule until an SLA is defined for it.

- Do not add a freshness metric/alert on the backend and stop there; verify the signal is surfaced at the screen where the value is shown.
- If a displayed value is a fusion of multiple sources with different freshness (e.g., an "online/offline fusion" score blending a real-time signal with a batch-computed signal), the UI must indicate which portion is stale or on what cadence each portion refreshes, not only an overall single timestamp that hides a stale sub-component.
- Treat "freshness badge missing from a screen that renders SLA'd data" as a shippable bug, not a follow-up nice-to-have.

#### Failure Mode Example
An online/offline fusion score is displayed to a user as a single number with no indicator of which inputs are real-time vs. batch. The batch component silently stops updating (upstream job failure) but the UI keeps showing a confident-looking score with no stale badge. The user acts on a number that is, in part, hours or days old, with no way to know it.

## Canonical/Shadow Divergence Tracking

A lightweight pattern for entities that have a "canonical vs. shadow/divergent" relationship to
another record of the same type: a self-referential foreign key pointing to the canonical record,
plus a boolean/flag marking whether the two have diverged (e.g. `canonical_id` + `has_diverged`,
or `duplicate_of_id` + `is_reconciled`). This lets consumers cheaply tell "which record is the
one to trust" and "has this record drifted from its canonical counterpart" without a full
reconciliation engine.

**Caveat:** this is a simplified stand-in for real master-data-management/golden-record
reconciliation, not a production-ready MDM solution by itself. It does not handle multi-way
merges, survivorship rules, confidence scoring, or conflict resolution across more than two
records. Use it for lightweight in-app "is this a duplicate/stale copy" signaling; reach for a
dedicated MDM/golden-record system when reconciliation logic, merge history, or cross-source
survivorship rules become non-trivial.

See `references/example.md` for a worked freshness-badge API response shape and a
Canonical/Shadow Divergence record example.

### Late-Arriving Data and Watermarks
Every time-windowed computation declares its event-time watermark (how late an event may arrive and still count), what happens to later events (correction pass, late-arrivals table, or documented drop), and whether outputs are recomputed when late data lands. Consumers are told whether a window is provisional or final.
- Failure mode: a daily aggregate computed at midnight from data that keeps arriving until 3am is silently wrong every day.

### Delivery Semantics
Every pipeline boundary declares at-most-once, at-least-once, or effectively-once (at-least-once plus idempotent consumption on a stable key). Assume at-least-once from every external source; never build on a broker's exactly-once promise across a boundary it does not own.
- Failure mode: a consumer assuming exactly-once double-counts on every rebalance or retry.

### Pipeline Checklist
For scaffolding a new pipeline, work through `references/pipeline-checklist.md`. Classification, retention, and lineage of every output dataset: `eng-os-privacy-and-governance`.

## Data Quality Strategy

Validate: structure, required fields, semantic correctness where feasible, freshness, completeness, and uniqueness when relevant. Failing to define quality criteria produces systems that "run" but cannot be trusted.

## Failure Modes

- duplicate data causes incorrect metrics and model training inputs
- schema drift breaks transformations or changes meaning silently
- weak partitioning creates scale limits
- missing lineage obscures the source of corruption
- replay without idempotency compounds bad outputs
- poor freshness controls make downstream decisions stale
- freshness badges omitted from consuming UI make staleness invisible to the end user
- windowed outputs computed before late data lands, with no provisional/final marker
- consumers assuming exactly-once delivery double-count on retry

## Definition of Done

- [ ] Producer and consumer contracts are explicit
- [ ] Partitioning strategy is defined
- [ ] Idempotency and de-duplication are addressed at every boundary where duplicates can arise
- [ ] Batch vs. streaming choice is justified
- [ ] Quality checks (structure, required fields, freshness, completeness, uniqueness) are defined
- [ ] Freshness SLA is explicit per dataset, with a metric and an alert
- [ ] For any field/dataset with a DECLARED freshness SLA, any UI rendering it (including fused data) surfaces a freshness/staleness indicator at the point of consumption
- [ ] Reprocessing and replay implications are understood
- [ ] Every time-windowed computation declares its watermark, late-data handling, and provisional/final status
- [ ] Every pipeline boundary declares its delivery guarantee, and consumers are idempotent under at-least-once
- [ ] Every output dataset has a classification, retention, and lineage record per `eng-os-privacy-and-governance`

A worked example of the checklist: `references/pipeline-checklist-example.md`.
