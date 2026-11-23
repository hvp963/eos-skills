# Worked Example — Minimal Pipeline for Daily Order Exports

Hypothetical dataset: a daily batch pipeline that extracts orders created or updated in the last 24
hours (selected by `updated_at`) from the OLTP orders database, transforms them into a denormalized
`fact_orders` shape, and loads them into the analytics warehouse. Applies the checklist from
`../../../micro/templates/etl-template.md` plus this skill's notes on correctness.

## Checklist Walkthrough

- **Contracts:** input schema is the OLTP `orders` and `order_items` tables (versioned via the
  source DB's own migration history); output schema is `fact_orders` with an explicit column list
  and types, versioned via a schema registry entry so downstream dashboards can detect
  breaking changes.
- **Correctness:** the load is keyed on `order_id` alone, the natural key from the source, which has
  a unique constraint in `fact_orders`. The extract selects by `updated_at` within the window, so an
  order placed last week and cancelled today is picked up today. The batch is de-duplicated to the
  latest version per `order_id` before the `MERGE`, and the `MERGE` updates a row only when the
  incoming `updated_at` is newer. Replay/backfill: the pipeline accepts an explicit `--date`
  parameter, and re-running any historical day, even after a newer day has loaded, leaves every
  row unchanged.
- **Scale:** partitioned by `extract_date` in the warehouse table (set when a row is first inserted
  and never changed by a later update, so partitions stay stable); expected throughput is a few
  hundred thousand rows/day, well within a single-node extract's capacity, so no further
  partitioning of the extract step itself is needed yet.
- **Quality:** validation reconciles three counts: rows extracted, rows after de-duplication, and
  rows inserted plus updated plus skipped as not newer (the last two must equal the second). It
  also checks for null `order_id` (reject and alert if any), and checks freshness (job must
  complete within 2 hours of its scheduled start).
- **Observability:** metrics emitted: rows extracted, rows inserted, rows updated, rows skipped as
  not newer, validation failures, job duration; a freshness metric
  (`hours_since_last_successful_load`) feeds an alert if it exceeds 26 hours.
- **Failure modes:** duplicate data (mitigated by the unique key and the atomic `MERGE`), a backfill
  regressing newer rows (mitigated by the version guard), schema drift (mitigated by validating the
  extracted column set against the expected schema before transforming; fail loudly rather than
  silently dropping a renamed column), stale data (mitigated by the freshness alert), hot partitions
  (not applicable at current volume, but `extract_date` partitioning keeps any future backfill from
  touching unrelated partitions).

## Minimal Real Pipeline Structure

A scheduled job is a capability like any other (`eng-os-coding-standards-common` Standard 13): the
scheduler entry point is its controller.

```
src/capabilities/order_export/
  controllers/run_export_controller.py     # parses --date, calls the service; bound to the schedule
  services/export_service.py               # extract -> validate -> transform -> de-duplicate -> load
  repositories/oltp_orders_repository.py   # reads orders + order_items changed in the window
  repositories/warehouse_repository.py     # the guarded MERGE into fact_orders
  models/fact_order_row.py                 # FactOrderRow dataclass
  views/                                   # none: a batch job renders nothing
tests/capabilities/order_export/
  services/export_service_test.py          # fake repositories: de-duplication keeps the latest version
  repositories/warehouse_repository_test.py  # real warehouse test schema: replay leaves rows unchanged
```

## Idempotency Handling (the part most pipelines get wrong)

```python
# models/fact_order_row.py
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FactOrderRow:
    order_id: str
    extract_date: str
    status: str
    total_amount: str        # decimal string; never a float
    created_at: datetime
    updated_at: datetime
```

```python
# services/export_service.py
def latest_per_order(rows: list[FactOrderRow]) -> list[FactOrderRow]:
    """Keep only the newest version of each order; a MERGE rejects two source rows per key."""
    latest: dict[str, FactOrderRow] = {}
    for row in rows:
        kept = latest.get(row.order_id)
        if kept is None or row.updated_at > kept.updated_at:
            latest[row.order_id] = row
    return list(latest.values())


def run_for_date(extract_date: str) -> None:
    rows = oltp_orders_repository.changed_in_window(extract_date)
    validate_schema(rows)                          # fail loudly on schema drift before transforming
    batch = latest_per_order(transform(rows, extract_date))
    warehouse_repository.load(batch)               # safe to re-run: see the guard below
```

```python
# repositories/warehouse_repository.py
from dataclasses import asdict


def load(rows: list[FactOrderRow]) -> None:
    """Upsert rows into fact_orders, keyed on order_id.

    Safe to call any number of times, in any order of dates: a row is updated only when the
    incoming version is newer, so a replay of an older or equal version changes nothing.
    """
    warehouse.execute(
        """
        MERGE INTO fact_orders AS target
        USING (SELECT * FROM UNNEST(@rows)) AS source
        ON target.order_id = source.order_id
        WHEN MATCHED AND (target.updated_at IS NULL OR source.updated_at > target.updated_at) THEN
            UPDATE SET
                status = source.status,
                total_amount = source.total_amount,
                updated_at = source.updated_at
        WHEN NOT MATCHED THEN
            INSERT (order_id, extract_date, status, total_amount, created_at, updated_at)
            VALUES (source.order_id, source.extract_date, source.status,
                    source.total_amount, source.created_at, source.updated_at)
        """,
        params={"rows": [asdict(row) for row in rows]},
    )
```

The idempotency test proves the version guard, not just the row count: load 2026-06-30, then
2026-07-01 (which carries a newer version of some of the same orders), then re-run 2026-06-30. The
test asserts that the row count is unchanged and that every order's `status`, `total_amount`, and
`updated_at` still hold the 2026-07-01 values. A test that checks only the row count would pass
against an unguarded `MERGE` that silently regressed those orders.
