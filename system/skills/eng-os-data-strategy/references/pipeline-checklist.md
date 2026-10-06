# Pipeline Checklist

Starter checklist for a new ETL or data pipeline, part of `eng-os-data-strategy`. The base checklist is canonical in `../../../micro/templates/etl-template.md`; work through it before building the pipeline.

## Notes

- **Correctness is the category most often shortchanged in a first pass.** Idempotency and
  de-duplication must be designed in from the start, not retrofitted: a pipeline that isn't
  idempotent can't safely be replayed or backfilled, which blocks the most common recovery path
  for bad data.
- **Failure modes to design against explicitly:** duplicate data, schema drift, stale data, hot
  partitions. Each should map to a specific mitigation in the Correctness/Scale/Quality sections
  above, not just be acknowledged.

See `pipeline-checklist-example.md` for a minimal real pipeline structure (extract/transform/load steps
with idempotency handling) applying this checklist to a hypothetical dataset.

## Definition of Done

A pipeline is ready to promote when every applicable item in
`../../../micro/templates/etl-template.md` is addressed, plus the skill-specific notes above:
contracts, correctness, scale, quality, and observability are all explicit, not merely implied by
the implementation.

## Governance

- every dataset the pipeline produces has a classification, retention, and lineage record per `eng-os-privacy-and-governance`
- delivery semantics and watermark policy are declared per `eng-os-data-strategy`
