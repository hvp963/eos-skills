# ETL Template

**Authors:** Haresh V. Parekh

## Purpose
Starter checklist for data ingestion and transformation pipelines.

## Inputs
- source systems
- schema contracts
- freshness requirements
- correctness expectations

---

## Checklist

### Contracts
- input schema defined
- output schema defined
- versioning strategy defined

### Correctness
- idempotency addressed
- de-duplication strategy defined
- replay/backfill implications understood

### Scale
- partitioning strategy defined
- bottlenecks identified
- throughput expectations stated

### Quality
- validation checks defined
- freshness expectations defined
- completeness expectations defined

### Observability
- throughput metrics defined
- freshness metrics defined
- error and validation failure metrics defined

### Failure Modes
- duplicate data
- schema drift
- stale data
- hot partitions

## Output
A pipeline should not be promoted until correctness, scale, and observability are addressed explicitly.
