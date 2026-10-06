# Database Design

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for designing durable, scalable, and correct storage systems and schemas.

### What This Is Not
- not a vendor-specific tuning guide
- not ORM documentation
- not a list of SQL tips only

## Scope
- Level: Meso
- Applies To: Relational, NoSQL, analytical, and hybrid persistence systems

---

## Applied Principles

### Contracts as Source of Truth
Schemas, keys, and compatibility expectations must be explicit.

### Validation at Boundaries
Writes and reads should be validated at meaningful boundaries.

### Scalability Through Partitioning
Partitioning strategy must be deliberate, not accidental.

### Idempotency by Default
Data writes must support safe retries where operations may repeat.

### Observability as a First-Class Concern
Database behavior must be measurable through latency, contention, errors, and growth patterns.

---

## Core Design Areas

### Schema Design
Decide where normalization or denormalization is appropriate.

#### Normalize When
- consistency and update correctness matter most
- duplication would cause frequent update anomalies

#### Denormalize When
- read performance dominates
- precomputed access patterns materially reduce latency
- the duplication is deliberate and manageable

#### Example
A user preferences table is normalized: preferences are stored as key-value rows referencing the users table. Adding a new preference type inserts a new row, not a schema migration. For a leaderboard, scores are denormalized into a summary table, written on update, read without joins. Both decisions are documented with justification; neither is accidental.

#### Failure Mode
Over-normalization causes slow read paths; over-denormalization causes update inconsistency.

---

### Naming Conventions
Use consistent naming so schema objects are unambiguous without consulting external documentation.

#### Table Names
snake_case, plural noun.
Examples: `users`, `media_assets`, `audit_events`

#### Column Names
snake_case throughout.
Examples: `user_id`, `created_at`, `is_active`

#### Boolean Columns
Prefix with `is_`, `has_`, `can_`, or `allow_`.
Examples: `is_active`, `has_completed`, `can_publish`

#### Timestamp Columns
Suffix `_at` for point-in-time values. Suffix `_on` for date-only values.
Examples: `created_at`, `updated_at`, `published_on`, `deleted_at`

#### Join and Association Tables
`<table_a>_<table_b>` in alphabetical order.
Examples: `article_authors`, `media_tags`

#### Rule
Column names must be unambiguous without consulting the table definition.
Avoid generic names like `name`, `type`, `value`, `data` without a qualifying prefix.

#### Failure Mode
Inconsistent or generic column names require documentation to interpret and produce ambiguous query results.

---

### Key Design
Choose primary keys and uniqueness constraints that support idempotency, portability, and access patterns.

#### Primary Keys
Default to a time-ordered UUID (UUIDv7, or ULID where the driver lacks v7 support) as the primary key type.
A UUID ensures consistency across environments, portability across systems, and safe key generation at the application layer before the database write. Time-ordered variants keep inserts append-only in B-tree indexes; random UUIDv4 keys scatter inserts across the index and, at hundreds of millions of rows, cost measurable write amplification and cache misses. Never use UUIDv4 as a clustered or primary key on a large, write-heavy table.

Use UUID when:
- record identity must be portable across systems or environments
- keys are generated before database write (application or event layer)
- multi-tenant or distributed systems require non-sequential, non-guessable IDs

Auto-increment integers are permissible only when:
- the key never leaves the database boundary
- storage efficiency is a documented constraint
- sequential ordering by insert is operationally required

Composite primary keys are permitted only when:
- no surrogate key can be assigned
- the composite uniqueness constraint is semantically meaningful and stable
- the composite key does not create write hotspots

#### Column Naming for Keys
Do not prefix column names with `PK_` or `FK_`. Column names communicate the relationship through naming convention alone.

- Primary key column on any table: `id`
- Foreign key column on a child table: `<referenced_table_singular>_id`

Example schema:
```
Table: users
  id          UUID       PRIMARY KEY   -- surrogate PK
  email       TEXT       NOT NULL
  created_at  TIMESTAMP  NOT NULL

Table: orders
  id          UUID       PRIMARY KEY   -- surrogate PK
  user_id     UUID       NOT NULL      -- FK to users.id
  placed_at   TIMESTAMP  NOT NULL
```

#### Constraint Naming
Use `PK_` and `FK_` as prefixes on constraint names, not column names.
Constraint names are internal database identifiers that appear in error messages and schema diffs.

- Primary key constraint: `PK_<table>`
- Foreign key constraint: `FK_<child_table>_<parent_table>`

```sql
CONSTRAINT PK_users PRIMARY KEY (id)
CONSTRAINT FK_orders_users FOREIGN KEY (user_id) REFERENCES users(id)
```

#### Foreign Key Enforcement
Enforce foreign key relationships at both layers.

Database layer: declare FK constraints explicitly in the schema.
Declarative constraints protect against orphaned records from any access path: application code, migration scripts, or direct database access.

Application layer: validate referential integrity before writes.
Application enforcement catches errors earlier, produces better error messages, and handles distributed contexts where cross-shard FK constraints are not enforceable at the database layer.

When database-layer FK constraints are not enforceable (e.g. cross-shard, cross-service), application-level enforcement is mandatory and must be documented as a deliberate architectural choice.

#### Referential Integrity Strategies

ON DELETE RESTRICT (default)
Use when orphaned parent deletion would corrupt business logic. Require explicit justification to override.

ON DELETE CASCADE
Use only when child records have no meaning independent of the parent and deletion is always intentional and bounded.
Failure mode: accidental parent deletion silently destroys child data.

ON DELETE SET NULL
Use when child records remain meaningful after parent removal and the FK column is nullable by design.

ON DELETE SET DEFAULT
Rarely appropriate. Use only when a sentinel value is semantically correct for the orphaned state.

#### Soft Deletes
When soft delete (`deleted_at IS NOT NULL`) is used:
- FK constraints still reference the full row, not the logical state
- Application logic must filter soft-deleted rows explicitly
- Use a partial index `WHERE deleted_at IS NULL` on active-record queries where the database supports it
- Soft delete does not substitute for archival; large soft-deleted datasets must have a defined purge strategy

#### Example
An orders table uses `id` (UUID generated at the application layer) as the primary key. A unique constraint on `(external_order_id, source_system)` prevents duplicates from different integrations. The orders table declares `CONSTRAINT FK_orders_users FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT`: an order cannot exist without a valid user. The application validates that `user_id` resolves to an active user before inserting. Both layers enforce the same constraint; the database layer catches any path that bypasses the application.

#### Failure Mode
Weak key strategy causes duplicate records, lookup inefficiency, or hot partitions.
Undeclared soft delete behavior causes referential confusion and incorrect query results.

---

### Indexing
Use indexes to optimize common query paths.

#### Guidance
- index actual critical query paths
- monitor write amplification and storage overhead
- remove unused indexes

#### Example
The three most common queries on the orders table filter by `(customer_id, created_at DESC)`. A composite index on these two fields is added and confirmed to be used by the query plan. An unused index on `shipping_address` from a prior feature is removed; it was adding write overhead with no active read benefit. Index usage is reviewed quarterly.

#### Failure Mode
Missing indexes cause full scans; excessive indexes increase write cost and complexity.

---

### Partitioning and Sharding
Distribute data intentionally.

#### Guidance
- choose partition keys aligned to access patterns
- anticipate hot partitions
- design for rebalancing where required

#### Example
An events table is range-partitioned by `event_date` with monthly partitions. Old partitions are compressed and archived after 90 days. Queries filtered by date range benefit from partition pruning: they scan only the relevant month's partition. A tenant-based partition key is evaluated and rejected: one tenant's volume would create a hot partition.

#### Failure Mode
Bad partition strategy creates hotspots, poor distribution, and scale ceilings.

---

### Transactions and Consistency
Define where transactional integrity is required and where eventual consistency is acceptable.

#### Guidance
- use strong transactional guarantees where correctness depends on atomic change
- use eventual consistency only when reconciliation is explicit and acceptable

#### Example
A funds transfer writes a debit to one account and a credit to another inside a single transaction. Either both succeed or neither does; no partial state. The downstream notification (email confirmation) is triggered by an event published after the transaction commits, not inside it. The boundary between strong consistency and eventual propagation is explicit and documented.

#### Failure Mode
Overusing strong transactions harms scale; underusing them corrupts correctness.

---

### Caching Around Datastores
Use caches to protect databases from repeated read load.

#### Guidance
- define cache keys explicitly
- define invalidation strategy explicitly
- never let cache semantics replace source-of-truth semantics

#### Example
A user profile cache is keyed by `user_id` with a 10-minute TTL. When the profile is updated, the cache key is invalidated immediately, not left to expire. The database remains the source of truth for all writes. No write path goes through the cache. Read-through fallback is handled by the application layer, not implicitly by the cache client.

#### Failure Mode
A cache masks stale or inconsistent data without clear policy.

---

### Dual/Parallel Classification Axes
Model independent classification dimensions as separate columns, never as one conflated field.

#### Guidance
- identify when an entity is being classified along two or more axes that evolve independently of each other
- give each axis its own column and its own enum
- do not merge axes into a single compound field, even when the combination looks small today

#### Example
An `orders` table needs a business-significance classification (`tier`: standard, priority, vip) and an independent data-quality classification (`quality_layer`: bronze, silver, gold) marking how far the record has progressed through enrichment. These are modeled as two columns:

```sql
tier           TEXT NOT NULL,   -- standard | priority | vip           (business significance)
quality_layer  TEXT NOT NULL,   -- bronze   | silver   | gold          (data-quality stage)
```

A `vip` order can independently be `bronze` on arrival and become `gold` once enrichment completes; `tier` never changes for that to happen. Adding a new tier value later touches only the `tier` column.

The wrong version conflates both axes into one compound field:

```sql
classification TEXT NOT NULL
-- allowed values: 'standard_bronze', 'standard_silver', 'standard_gold',
--                  'priority_bronze', 'priority_silver', 'priority_gold',
--                  'vip_bronze',      'vip_silver',      'vip_gold'
```

This is already a 3x3 combinatorial explosion for two axes with three values each. Adding one new tier value means adding three new compound strings, and a query that means to filter on `quality_layer` alone now depends on string matching (`WHERE classification LIKE '%_gold'`) instead of an indexed equality check on a dedicated column.

#### Failure Mode
Conflating two independent classification dimensions into one field forces awkward compound enum values and produces a combinatorial explosion as either axis grows. It breaks when either axis's taxonomy changes independently: a new value on one axis should never require touching the other.

---

### Join Design
Use joins explicitly and deliberately.

#### Rules

Always use explicit JOIN syntax. Never use implicit join syntax (comma-separated tables resolved in WHERE).
- Bad:  `SELECT * FROM orders, users WHERE orders.user_id = users.id`
- Good: `SELECT * FROM orders INNER JOIN users ON orders.user_id = users.id`

Join on indexed columns. FK columns used in joins must be indexed. An unindexed join column causes a full table scan on the joined table at scale.

Declare join cardinality in design documents. State whether a join is one-to-one, one-to-many, or many-to-many. Undeclared cardinality is a design error.

Avoid fan-out joins in analytical paths. A one-to-many join without aggregation multiplies rows before counting, producing inflated results. Aggregate before joining, or use CTEs to bound the row set first.

Limit join depth in OLTP queries. More than three to four table joins in a single query signals the query should be redesigned, broken into steps, or served from a pre-computed read model.

Use LEFT JOIN deliberately, not by default. LEFT JOIN returns NULLs for non-matching rows. Use it only when the absence of a match is a valid and expected result. INNER JOIN is the default when a match is required for correctness.

#### Example
A report joins `orders` to `users` (one-to-one on `user_id`) and to `order_items` (one-to-many on `order_id`). The cardinality is declared in the design doc. To avoid row multiplication, `order_items` is aggregated in a CTE before joining to `orders`: the CTE produces one row per order, then the outer join to `users` is clean. `user_id` on `orders` is indexed; the join does not scan the full users table.

#### Failure Mode
Implicit join syntax hides conditions and makes cross-joins possible by omission.
Unindexed FK columns cause full scans that degrade with table size.
Undeclared cardinality produces silent row multiplication that distorts aggregations.
Excessive join depth creates fragile queries that break on schema change.

---

## Schema Change at Scale (Expand/Contract)

No migration may lock a large table or require the old and new code to switch at the same
instant. Every change is three steps: expand (add the new structure, nullable or defaulted,
backward-compatible), migrate (dual-write from code, backfill in throttled idempotent batches,
verify), contract (drop the old structure in a later release once nothing reads it). Index
builds on large tables run concurrently/online. The pipeline ordering and the rollback rules are
in `meso/deployment.md` Section 7.

- Failure mode: `ALTER TABLE ... ADD COLUMN NOT NULL DEFAULT` on a billion-row table holds a lock
  for an hour; the deploy that needed it times out and every write queues behind it.

## Read Scaling and Connection Management

- **Read replicas**: route read-only, staleness-tolerant queries to replicas and declare the
  tolerated replication lag per query path; reads that must see a just-committed write go to
  the primary (read-your-writes). Monitor lag as a first-class metric.
- **Connection pooling**: every service uses a bounded pool sized from the capacity model, and
  the database's total connection ceiling is divided among services deliberately. Use a proxy
  pooler (PgBouncer or equivalent) in front of databases that pay per connection.
- **Query budgets**: declare a per-request maximum number of queries and reject N+1 patterns at
  review; an ORM lazy load inside a loop is a defect, not a style issue.

- Failure mode: a hundred pods each opening fifty connections exhaust the database's connection
  limit during a deploy, so the healthy instances cannot connect either.

## Multi-Tenant Data Isolation

Choose and document one tenancy model: shared tables with a `tenant_id` column on every
tenant-owned row (plus row-level security or a mandatory query predicate), schema-per-tenant, or
database-per-tenant for the largest or regulated tenants. In the shared model, `tenant_id` is
part of every index that serves a tenant-scoped query, every unique constraint, and every
partition key; a query with no tenant predicate is rejected at the data-access layer.

- Failure mode: one query missing its tenant predicate returns another tenant's rows; at scale
  this is a breach, not a bug.

## Failure Modes

- hot partitions
- lock contention
- poor query plans
- schema drift between services
- duplicate writes from non-idempotent operations
- accidental fan-out queries from undeclared join cardinality
- stale cache returning invalid business state
- inconsistent naming requiring documentation to interpret
- orphaned records from unenforced referential integrity
- conflated classification axes producing compound enums that break as either axis evolves
- random UUID primary keys fragmenting B-tree indexes on large write-heavy tables
- a locking migration on a large table stalling every write during a deploy
- connection exhaustion from unbounded per-service pools
- a tenant-scoped query missing its tenant predicate, returning another tenant's data

---

## Definition of Done

Database design is complete when:
- key and schema choices are justified
- indexing strategy aligns to real access patterns
- partitioning strategy is explicit
- consistency requirements are stated
- idempotent write behavior is supported where needed
- cache strategy is explicit if caching is used
- independent classification dimensions are modeled as separate columns, not conflated into one compound field
- expected failure modes are understood
- primary keys on large tables are time-ordered (UUIDv7/ULID), never random UUIDv4
- every schema change follows expand/contract; index builds on large tables are online
- read paths declare replica tolerance and replication lag is monitored; connection pools are bounded and sized from the capacity model; per-request query budgets are enforced
- the tenancy model is declared, and in the shared model every tenant-owned row, index, and constraint carries `tenant_id`
