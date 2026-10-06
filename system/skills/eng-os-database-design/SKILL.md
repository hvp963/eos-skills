---
name: eng-os-database-design
description: "Use when designing schemas, indexes, migrations, or partitioning strategy, or reviewing database access patterns."
sources:
  - meso/database-design.md
globs: ["**/*.sql", "**/migrations/**", "**/models/**", "**/schema/**"]
always_apply: false
verified_platforms: [claude-code]
---

# Database Design

Apply these rules when designing or reviewing schemas, keys, indexes, partitioning, joins, or transactional boundaries.

## Principles

- **Contracts as source of truth.** Schemas, keys, and compatibility expectations must be explicit.
- **Validation at boundaries.** Validate writes and reads at meaningful boundaries.
- **Scalability through partitioning.** Partitioning must be deliberate, never accidental.
- **Idempotency by default.** Writes must support safe retries.
- **Observability as a first-class concern.** Latency, contention, errors, and growth must be measurable.

## Schema Design

Normalize when consistency/update correctness matters most. Denormalize when read performance dominates and the duplication is deliberate and manageable. Document the justification either way; never let it be accidental.
- Failure mode: over-normalization causes slow read paths; over-denormalization causes update inconsistency.

## Naming Conventions

- Tables: `snake_case`, plural noun (`users`, `media_assets`).
- Columns: `snake_case` (`user_id`, `created_at`, `is_active`).
- Booleans: prefix `is_`, `has_`, `can_`, `allow_`.
- Timestamps: suffix `_at` for point-in-time, `_on` for date-only.
- Join tables: `<table_a>_<table_b>` alphabetically.
- Avoid generic names (`name`, `type`, `value`, `data`) without a qualifying prefix; a column name must be unambiguous without opening the schema.

## Key Design

- Default primary key type: time-ordered UUID (UUIDv7, or ULID where the driver lacks v7), generated at the application layer; never random UUIDv4 as the primary key of a large write-heavy table, since it scatters inserts across the B-tree and costs write amplification and cache misses at scale. Use a UUID when identity must be portable, keys are generated before the DB write, or the system is multi-tenant/distributed.
- Auto-increment integers only when the key never leaves the DB boundary, storage efficiency is a documented constraint, or sequential insert ordering is operationally required.
- Composite keys only when no surrogate key fits, the composite is semantically stable, and it does not create write hotspots.
- Column naming: `id` for PK, `<referenced_table_singular>_id` for FK. Never prefix columns with `PK_`/`FK_`; reserve those prefixes for constraint names (`PK_<table>`, `FK_<child>_<parent>`), which appear in error messages and diffs.

### Foreign Key Enforcement
Enforce at both layers: declare FK constraints in the schema (protects every access path), and validate referential integrity in application code (better error messages, and mandatory where DB-level FKs are unenforceable, e.g. cross-shard/cross-service; document that as a deliberate choice).

### Referential Integrity Strategies
- `ON DELETE RESTRICT`: default; requires explicit justification to override.
- `ON DELETE CASCADE`: only when child rows have no independent meaning and deletion is always intentional and bounded. Failure mode: accidental parent deletion silently destroys child data.
- `ON DELETE SET NULL`: when child rows remain meaningful after parent removal.
- `ON DELETE SET DEFAULT`: rarely appropriate.

### Soft Deletes
FK constraints still reference the full row regardless of `deleted_at`. Application logic must filter soft-deleted rows explicitly. Use a partial index `WHERE deleted_at IS NULL` where supported. Soft delete is not archival: define a purge strategy for large soft-deleted sets.

## Indexing

Index actual critical query paths; monitor write amplification; remove unused indexes on a regular cadence (e.g., quarterly review).
- Failure mode: missing indexes cause full scans; excessive indexes increase write cost and complexity.

## Partitioning and Sharding

Choose partition keys aligned to real access patterns, anticipate hot partitions, and design for rebalancing. Reject partition keys that would concentrate volume on one value (e.g., a single high-volume tenant).
- Failure mode: bad partition strategy creates hotspots, poor distribution, and a scale ceiling.

## Transactions and Consistency

Use strong transactional guarantees where correctness depends on atomic change (e.g., a funds transfer debit+credit). Use eventual consistency only when reconciliation is explicit: e.g., trigger downstream notifications from a post-commit event, not inside the transaction.
- Failure mode: overusing strong transactions harms scale; underusing them corrupts correctness.

## Caching Around Datastores

Define cache keys and invalidation explicitly. Invalidate on write; never rely on TTL expiry alone for correctness-sensitive data. The database remains the source of truth; no write path goes through the cache.
- Failure mode: a cache masks stale or inconsistent data without clear policy.

## Dual/Parallel Classification Axes

An entity sometimes needs two independent, orthogonal classification axes simultaneously: e.g.
a "Tier" classification (business/commercial significance) and a separate "Medallion/quality-layer"
classification (bronze/silver/gold data-quality stage) on the same record, where each axis evolves
independently of the other. Model each axis as its own column/enum (`tier`, `quality_layer`),
never conflate them into a single compound field.

- Failure mode: conflating two independent classification dimensions into one field forces
  awkward compound enum values (e.g. `tier1_gold`, `tier2_silver`, `tier1_bronze`, a combinatorial
  explosion) and breaks when either axis's taxonomy changes independently (adding a new tier
  shouldn't require touching every quality-layer value, and vice versa).

## Join Design

- Always use explicit `JOIN ... ON` syntax; never comma-separated tables resolved in `WHERE`.
- FK columns used in joins must be indexed, or the joined table gets a full scan at scale.
- Declare join cardinality (one-to-one, one-to-many, many-to-many) in the design doc; undeclared cardinality is a design error.
- Aggregate before joining (or use a CTE) to avoid fan-out joins multiplying rows in analytical paths.
- More than three to four joins in an OLTP query signals it should be redesigned or served from a pre-computed read model.
- Use `LEFT JOIN` deliberately, only when absence of a match is valid; `INNER JOIN` is the default when a match is required for correctness.
- Failure mode: implicit join syntax hides conditions and enables accidental cross-joins; unindexed FK joins degrade with table size; undeclared cardinality causes silent row multiplication in aggregations.

See `references/example.md` for a worked `customers`/`orders`/`order_items` schema showing
key/FK design, a real index for a query pattern, and the Dual/Parallel Classification Axes
pattern with right/wrong versions side by side.

## Schema Change at Scale (Expand/Contract)
No migration locks a large table or requires old and new code to switch at once. Expand (add nullable or defaulted structure), migrate (dual-write, throttled idempotent backfill, verify), contract (drop the old structure in a later release). Index builds on large tables run online. Pipeline ordering and rollback rules: `eng-os-deployment-practices`.
- Failure mode: `ALTER TABLE ... ADD COLUMN NOT NULL DEFAULT` on a billion rows holds a lock for an hour and every write queues behind it.

## Read Scaling and Connection Management
- Route read-only, staleness-tolerant queries to replicas with a declared lag tolerance per path; read-your-writes goes to the primary; monitor lag as a first-class metric.
- Every service uses a bounded pool sized from the capacity model; the database's connection ceiling is divided among services deliberately; use a proxy pooler where connections are expensive.
- Declare a per-request query budget and reject N+1 at review; an ORM lazy load in a loop is a defect.
- Failure mode: a hundred pods each opening fifty connections exhaust the database during a deploy, so healthy instances cannot connect either.

## Multi-Tenant Data Isolation
Declare one tenancy model: shared tables with `tenant_id` on every tenant-owned row plus row-level security or a mandatory predicate; schema-per-tenant; or database-per-tenant for the largest or regulated tenants. In the shared model, `tenant_id` is in every index serving a tenant-scoped query, every unique constraint, and every partition key, and a query without a tenant predicate is rejected at the data-access layer.
- Failure mode: one query missing its tenant predicate returns another tenant's rows; at scale that is a breach.

## Failure Modes

- hot partitions and lock contention
- poor query plans from missing or excessive indexes
- schema drift between services
- duplicate writes from non-idempotent operations
- accidental fan-out from undeclared join cardinality
- stale cache returning invalid business state
- orphaned records from unenforced referential integrity
- random UUID primary keys fragmenting B-tree indexes on large write-heavy tables
- a locking migration stalling every write during a deploy
- connection exhaustion from unbounded per-service pools
- a tenant-scoped query missing its tenant predicate

## Definition of Done

- [ ] Key and schema choices are justified (normalize/denormalize, UUID/int/composite)
- [ ] Naming is consistent and unambiguous without external docs
- [ ] Foreign keys are enforced at both DB and application layer (or the gap is documented)
- [ ] Indexing strategy aligns to real access patterns; unused indexes are removed
- [ ] Partitioning strategy is explicit and avoids known hot-key risks
- [ ] Consistency requirements (strong vs. eventual) are stated per operation
- [ ] Idempotent write behavior is supported where retries/replays are possible
- [ ] Cache strategy, including invalidation, is explicit if caching is used
- [ ] Join cardinality is declared and fan-out risk is checked
- [ ] Primary keys on large tables are time-ordered (UUIDv7/ULID), never random UUIDv4
- [ ] Every schema change follows expand/contract; large-table index builds are online
- [ ] Read paths declare replica tolerance and lag is monitored; pools are bounded from the capacity model; per-request query budgets are enforced
- [ ] The tenancy model is declared; in the shared model every tenant-owned row, index, and constraint carries `tenant_id`
