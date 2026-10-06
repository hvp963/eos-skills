# Worked Example — Minimal Pipeline for Daily Order Exports

Hypothetical dataset: a daily batch pipeline that extracts orders placed in the last 24 hours from
the OLTP orders database, transforms them into a denormalized `fact_orders` shape, and loads them
into the analytics warehouse. Applies the checklist from
`../../../micro/templates/etl-template.md` plus this skill's notes on correctness.

## Checklist Walkthrough

- **Contracts:** input schema is the OLTP `orders` and `order_items` tables (versioned via the
  source DB's own migration history); output schema is `fact_orders` with an explicit column list
  and types, versioned via a schema registry entry so downstream dashboards can detect
  breaking changes.
- **Correctness:** idempotency is handled by keying the load step on `order_id` +
  `extract_date` and using an upsert (`MERGE`) into `fact_orders` rather than an append, so
  re-running the same day's job twice does not create duplicate rows. De-duplication additionally
  checks for orders that were updated (not just inserted) within the window. Replay/backfill: the
  pipeline accepts an explicit `--date` parameter so any historical day can be re-run safely
  because of the same idempotent upsert.
- **Scale:** partitioned by `extract_date` in the warehouse table; expected throughput is a few
  hundred thousand rows/day, well within a single-node extract's capacity, so no further
  partitioning of the extract step itself is needed yet.
- **Quality:** validation checks row counts extracted vs. loaded (must match), checks for null
  `order_id` (reject and alert if any), and checks freshness (job must complete within 2 hours of
  its scheduled start).
- **Observability:** metrics emitted: rows extracted, rows loaded, validation failures, job
  duration; a freshness metric (`hours_since_last_successful_load`) feeds an alert if it exceeds 26
  hours.
- **Failure modes:** duplicate data (mitigated by upsert-on-order_id), schema drift (mitigated by
  validating extracted column set against the expected schema before transforming; fail loudly
  rather than silently dropping a renamed column), stale data (mitigated by the freshness alert),
  hot partitions (not applicable at current volume, but `extract_date` partitioning keeps any
  future backfill from touching unrelated partitions).

## Minimal Real Pipeline Structure

```
order-export-pipeline/
  extract.py      # pulls orders + order_items for a given date from OLTP source
  transform.py    # joins/denormalizes into fact_orders rows, validates schema
  load.py         # upserts into warehouse fact_orders table, keyed on order_id
  run.py          # orchestrates extract -> transform -> load for a given --date
  test/
    test_idempotency.py   # asserts running load.py twice for the same date is a no-op on row count
```

## Idempotency Handling (the part most pipelines get wrong)

```python
# load.py
def load(rows: list[dict], extract_date: str) -> None:
    """
    Upserts rows into fact_orders, keyed on order_id. Safe to call multiple times
    for the same extract_date, re-running does not create duplicates or double-count
    revenue, because this is a MERGE, not an INSERT.
    """
    warehouse.execute(
        """
        MERGE INTO fact_orders AS target
        USING (SELECT * FROM UNNEST(@rows)) AS source
        ON target.order_id = source.order_id
        WHEN MATCHED THEN
            UPDATE SET
                status = source.status,
                total_amount = source.total_amount,
                updated_at = source.updated_at
        WHEN NOT MATCHED THEN
            INSERT (order_id, extract_date, status, total_amount, created_at, updated_at)
            VALUES (source.order_id, source.extract_date, source.status,
                    source.total_amount, source.created_at, source.updated_at)
        """,
        params={"rows": rows},
    )


def run_for_date(extract_date: str) -> None:
    rows = extract(extract_date)
    validate_schema(rows)          # fail loudly on schema drift before transforming
    transformed = transform(rows)
    load(transformed, extract_date)  # safe to re-run: see docstring above
```

Re-running `run.py --date 2026-06-30` five times in a row produces the same `fact_orders` row
count as running it once: that's the concrete, testable definition of idempotent this scaffold's
correctness checklist item requires, not just an assertion that "idempotency is addressed."
