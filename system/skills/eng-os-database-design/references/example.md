# Worked Example: Orders Domain Schema

A concrete schema for `customers`, `orders`, and `order_items`, showing key/FK design, an
index added for a real query pattern, the Dual/Parallel Classification Axes pattern, and an
expand/contract schema change on a large table.

## Schema

```sql
CREATE TABLE customers (
    id          UUID PRIMARY KEY,                -- app-generated UUID; portable, pre-write identity
    email       TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    CONSTRAINT PK_customers PRIMARY KEY (id)
);

CREATE TABLE orders (
    id           UUID PRIMARY KEY,
    customer_id  UUID NOT NULL,                   -- FK to customers.id
    status       TEXT NOT NULL,                   -- pending | paid | shipped | cancelled
    tier         TEXT NOT NULL,                   -- business-significance axis: standard | priority | vip
    quality_layer TEXT NOT NULL,                  -- data-quality axis: bronze | silver | gold
    placed_at    TIMESTAMP NOT NULL,
    deleted_at   TIMESTAMP NULL,                  -- soft delete
    CONSTRAINT FK_orders_customers FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

CREATE TABLE order_items (
    id         UUID PRIMARY KEY,
    order_id   UUID NOT NULL,                     -- FK to orders.id
    sku        TEXT NOT NULL,
    quantity   INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    CONSTRAINT FK_order_items_orders FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    -- CASCADE is correct here: an order_item has no independent meaning once its parent order is gone
);

-- real query pattern: "show a customer's recent orders", the dashboard's most frequent query
CREATE INDEX idx_orders_customer_placed ON orders (customer_id, placed_at DESC)
    WHERE deleted_at IS NULL;   -- partial index: soft-deleted orders never appear in this lookup
```

`orders.customer_id` is indexed as part of `idx_orders_customer_placed`, so the
`orders INNER JOIN customers ON orders.customer_id = customers.id` join used in the order-history
report doesn't force a full scan of `orders` as the table grows.

## Dual/Parallel Classification Axes — RIGHT (separate columns)

```sql
tier           TEXT NOT NULL,   -- standard | priority | vip           (business significance)
quality_layer  TEXT NOT NULL,   -- bronze   | silver   | gold          (data-quality stage)
```

A `vip` order can independently be `bronze` (just landed, not yet enriched) and later become
`gold` once enrichment completes; `tier` never has to change for that to happen. Adding a new
tier (e.g. `enterprise`) touches only the `tier` column's allowed values; it does not require
touching `quality_layer` at all.

## Dual/Parallel Classification Axes — WRONG (conflated compound enum)

```sql
classification TEXT NOT NULL
-- allowed values: 'standard_bronze', 'standard_silver', 'standard_gold',
--                  'priority_bronze', 'priority_silver', 'priority_gold',
--                  'vip_bronze',      'vip_silver',      'vip_gold'
```

This is a 3x3 combinatorial explosion for just two axes with three values each; adding one new
`tier` value means adding three new compound strings, and every query that means to filter on
`quality_layer` alone (`WHERE classification LIKE '%_gold'`) now depends on string parsing instead
of an indexed equality check on a dedicated column.

## Schema Change at Scale (Expand/Contract)

Task: add `orders.fulfillment_status`, required on every row, to a 40-million-row `orders` table
that takes writes all day. Three releases, each safe to roll back until the last. The SQL is
PostgreSQL; other engines have an online equivalent for each step.

**Release 1, expand.** Add the structure without touching existing rows or readers.

```sql
ALTER TABLE orders ADD COLUMN fulfillment_status TEXT NULL;   -- nullable, no default: no table rewrite
```

**Release 2, migrate.** Deploy code that writes both shapes, then backfill and verify.

```
-- application: every insert and update sets fulfillment_status as well as the legacy status
-- backfill job: idempotent (safe to rerun), throttled, resumable
repeat:
    ids = SELECT id FROM orders WHERE fulfillment_status IS NULL ORDER BY id LIMIT 5000
    UPDATE orders SET fulfillment_status = derive_status(status) WHERE id IN (ids)
    sleep 200ms                         -- leave headroom for live writes and replica lag
until no rows have fulfillment_status IS NULL

-- verify before moving on: zero NULL rows, and a sampled check that
-- derive_status(status) == fulfillment_status for 10,000 random rows
```

Reads switch to the new column behind a flag, so rolling back is a flag flip, not a migration.

**Release 3, contract.** Enforce the rule, then retire the old structure in a later release.

```sql
ALTER TABLE orders ADD CONSTRAINT orders_fulfillment_status_nn
    CHECK (fulfillment_status IS NOT NULL) NOT VALID;          -- takes effect for new writes at once
ALTER TABLE orders VALIDATE CONSTRAINT orders_fulfillment_status_nn;   -- scans without blocking writes
-- one full release cycle later: DROP COLUMN status   (forward-only; recorded in the release notes)
```

The wrong version is one migration: `ALTER TABLE orders ADD COLUMN fulfillment_status TEXT NOT NULL
DEFAULT 'pending'` followed by a single `UPDATE orders SET ...` over all 40 million rows. Depending
on the engine, the first statement rewrites the table under a lock, and the single `UPDATE`
holds row locks for its whole run, floods replication, and queues every live write behind it. Old
and new application code also have to switch at the same instant, so there is no safe rollback
point. Ordering of migrations against deploys: `eng-os-deployment-practices`.
