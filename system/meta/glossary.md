# Engineering Glossary

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A canonical vocabulary for the Engineering OS.
It defines terms used across product, data, distributed systems, and AI systems.

### What This Is Not
- not a tutorial
- not a textbook
- not a substitute for design guidance

## Scope
- Level: Meta
- Applies To: All layers

---

# Core Systems Terms

## Availability
The percentage of time a system is operational and accessible when needed.

### Example
A service that remains reachable during node failures because failover is configured.

### Notes
Availability is improved through redundancy, failover, health checks, and fault isolation.

---

## Resiliency
The ability of a system to continue functioning or recover gracefully under failure.

### Example
A service retries a transient dependency failure and degrades non-critical features instead of failing completely.

### Notes
Resiliency is not the same as availability.
A system may be available but not resilient if it cannot recover predictably from partial failure.

---

## Scalability
The ability of a system to handle increased load without unacceptable degradation.

### Example
A service scales horizontally by adding instances behind a load balancer.

### Notes
Scalability usually requires partitioning, statelessness, and careful control of shared bottlenecks.

---

## Latency
The time required to respond to a request or complete an operation.

### Example
An API responds within 50 ms at p95 under expected load.

### Notes
Latency should be evaluated at multiple percentiles, not just averages.

---

## Throughput
The amount of work processed in a given time period.

### Example
A streaming pipeline processes 2 million events per minute.

### Notes
Higher throughput can increase latency if the system is not balanced correctly.

---

## Efficiency
The degree to which compute, storage, memory, and cost are used effectively.

### Example
A pipeline reduces cloud cost by compacting data and minimizing unnecessary reprocessing.

### Notes
Efficiency must not be optimized at the expense of correctness or operability.

---

## Consistency
The degree to which data remains correct, uniform, and synchronized across the system.

### Example
A user sees the same account balance across services after a committed transaction.

### Notes
Consistency can be strong, bounded, or eventual depending on system requirements.

---

## Fault Isolation
The containment of failures within defined boundaries so they do not cascade.

### Example
One failing consumer group does not bring down unrelated message processing paths.

### Notes
Isolation is achieved through partitioning, timeouts, resource boundaries, bulkheads, and decoupling.

---

## Observability
The ability to understand system behavior through measurable signals.

### Example
Latency spikes can be traced to a specific service dependency using metrics, logs, and traces.

### Notes
Observability is not just monitoring dashboards; it includes debugability and explanation.

---

## Adaptability
The ability of a system to evolve safely as requirements, scale, or usage patterns change.

### Example
An API supports additive schema evolution without breaking existing consumers.

### Notes
Adaptability often requires modular design, explicit contracts, and versioning.

---

# Principles and Architecture Terms

## Explicit Contract
A formal definition of inputs, outputs, structure, and expectations between system boundaries.

### Example
A versioned API schema or a versioned event schema in a registry.

### Notes
Contracts reduce ambiguity and prevent drift between producers and consumers.

---

## Idempotency
The property that repeated execution of the same operation produces the same intended result.

### Example
Replaying an ETL job does not duplicate records because writes are keyed and deduplicated.

### Notes
Idempotency is essential for retries, replays, and distributed recovery.

---

## De-duplication
The process of identifying and eliminating duplicate records or duplicate side effects.

### Example
Using a unique event identifier to prevent multiple writes for the same logical event.

### Notes
De-duplication is often a mechanism for achieving idempotency.

---

## Partitioning
Dividing data, traffic, or computation into independent segments that can be processed separately.

### Example
Sharding events by date and tenant.

### Notes
Partitioning is the primary path to scale and fault isolation in distributed systems.

---

## Decoupling
Reducing unnecessary direct dependencies between components.

### Example
Services communicate via events rather than synchronous chains for every interaction.

### Notes
Decoupling improves adaptability and fault isolation, but can complicate debugging and consistency.

---

## Separation of Concerns
Assigning a clear, single responsibility to each component or layer.

### Example
Keeping validation logic out of presentation formatting logic.

### Notes
This reduces coupling and makes systems easier to evolve and test.

---

## Component
A single unit of code (a function, class, or module) with one exported responsibility and one
reason to change. A component is identified by what it owns (a piece of state, a side effect, a
transformation), not by its file extension or its paradigm (functional and class-based components
are both valid). Two call sites that need the same behavior call the same component; they do not
each contain their own copy of it.

### Example
`getAnthropicClient()` is a component: every module that needs an Anthropic client calls it,
instead of each constructing its own `new Anthropic(...)`.

### Notes
"Component" in UI contexts (see `eng-os-design-system` skill) is a specialization of this general
definition, scoped to a renderable unit with props as its interface.

---

## Reusable Unit
A component built to be called from more than one place without modification: its behavior is
fully determined by its parameters and documented contract, not by which caller invoked it or
what state existed before the call. A unit used from exactly one call site is not required to be
reusable; forcing reusability on a single-use unit is premature abstraction (see
`eng-os-coding-standards-common` "no speculative generality").

### Example
`callAiIdsWithRetry()` is a reusable unit: it takes the model, spec text, content, and validator as
parameters and makes no assumption about which AI-IDS spec or pipeline is calling it.

### Notes
The signal that something should become a reusable unit is not "this might be needed again"; it
is "this logic now exists, unchanged, at two or more call sites." Extract on the second occurrence,
not in anticipation of a third.

---

## Object-Oriented Design
A code style that models a responsibility as an instantiated object carrying its own state,
exposing behavior as methods on that state, rather than as free functions operating on data passed
in through parameters. In this Engineering OS, OOD is a tool selected per responsibility, not a
default; see `eng-os-coding-standards-common` §12 for when to reach for it versus a plain function/module.

### Example
A `Job` class wrapping a job's lifecycle transitions (`start()`, `fail(error)`, `complete()`) is
OOD; a `transitionJob(job, event)` free function operating on a plain `Job` record is not. Both
are acceptable, and the choice is a per-responsibility judgment, not a house style applied
uniformly across a codebase.

### Notes
A codebase is not "more correct" for being more object-oriented. Judge OOD choices against Standard
12's triggers, not against a paradigm preference stated once and applied everywhere.

---

## Model-View-Controller (MVC)
A mandatory three-layer separation for any application, web or otherwise: **Model** (data shape,
persistence, business/domain rules; no rendering, no I/O framing), **View** (presentation only;
rendering, layout, formatting for the output medium; no business logic), **Controller** (thin
orchestration of a single request/command/action: reads input, calls the Model, invokes the View).
See `eng-os-coding-standards-common` §13. Not web-specific; a CLI tool or backend service applies the same
separation with its own equivalents (a command handler is a Controller; console/JSON output
formatting is a View).

### Example
A route handler (`Controller`) that validates a request, calls `createRotation()` (`Model`) to
apply a business rule, and calls `renderRotationCreated()` (`View`) to format the response, rather
than validating, persisting, and formatting all inline in the handler itself.

### Notes
The layers are named by responsibility, not by literal folder name: a state-store-based frontend
(hooks/store instead of a classic "Controller" object) still complies as long as data/business
rules, presentation, and orchestration stay in three separate places. The failure mode this
standard exists to prevent is folding all three into one file/function, not the absence of a
folder literally named `controllers/`.

---

## Validation at Boundaries
The practice of validating inputs and outputs whenever they cross a system boundary.

### Example
An API validates request schema before processing and validates response schema before publishing.

### Notes
Boundary validation prevents downstream corruption and simplifies failure diagnosis.

---

## Stateless Service
A service that does not depend on local in-memory state across requests.

### Example
Any request can be handled by any service instance because state is externalized.

### Notes
Statelessness is a major enabler of scalability and resiliency.

---

## Event-Driven Architecture
A design approach where components communicate through events rather than tightly coupled synchronous calls.

### Example
A billing system emits payment events consumed independently by analytics and notifications.

### Notes
Event-driven systems improve decoupling but require careful attention to ordering, retries, and idempotency.

---

## API Gateway
A single entry point that centralizes routing, authentication, throttling, and common concerns for client access.

### Example
A gateway authenticates clients and routes requests to downstream services.

### Notes
Gateways simplify clients but can become bottlenecks if overloaded or poorly designed.

---

## C4 Model
A hierarchical model for expressing software architecture through four levels: Context, Container, Component, and Code.

### Example
A design review shows system boundaries at Context level and service/data-store composition at Container level.

### Notes
C4 improves design communication and reviewability.

---

# Data Systems Terms

## Data Contract
An explicit agreement between data producers and consumers regarding schema, structure, semantics, and compatibility expectations.

### Example
A producer publishes a versioned event schema that consumers validate against.

### Notes
Data contracts should be versioned and enforced.

---

## Schema Evolution
The controlled change of schemas over time without breaking dependent systems.

### Example
Adding an optional field to an event schema while preserving compatibility.

### Notes
Breaking changes require migration strategy, not just schema modification.

---

## Backfill
The reprocessing of historical data to correct, recompute, or enrich datasets.

### Example
Replaying 90 days of events after a transformation bug is fixed.

### Notes
Backfills must be safe, bounded, and ideally idempotent.

---

## Replay
The re-execution of previously captured inputs or events.

### Example
Re-consuming a message topic from a previous offset.

### Notes
Replay is often operationally distinct from backfill, though related.

---

## Data Freshness
How recently the data reflects real-world state.

### Example
A dashboard reflects events delayed by less than five minutes.

### Notes
Freshness is a critical SLA for operational analytics and AI feedback systems.

---

## Medallion Architecture
A layered data architecture commonly expressed as raw, refined, and curated zones.

### Example
Bronze stores raw inputs, silver stores cleaned records, gold stores consumption-ready datasets.

### Notes
Useful for separating ingestion fidelity from business-ready representations.

---

## Data Mesh
A decentralized approach where domains own data as a product.

### Example
The subscriptions domain owns and publishes its curated datasets and schema contracts.

### Notes
Data mesh requires strong standards, governance, and platform support to work well.

---

## Normalization
The process of converting data into a consistent, expected representation.

### Example
Trimming whitespace, standardizing timestamps, and canonicalizing field values.

### Notes
Normalization can refer to both relational schema design and value standardization depending on context.

---

## Denormalization
Intentionally duplicating or restructuring data to optimize query access or read performance.

### Example
Precomputing user-profile aggregates to serve low-latency reads.

### Notes
Denormalization improves performance but increases update complexity.

---

## Sharding
A form of partitioning in which a dataset is split across multiple storage partitions or nodes.

### Example
User records are distributed by hashed user ID.

### Notes
Shard selection and rebalancing strategy are critical design decisions.

---

## Hot Partition
A partition receiving disproportionately high load relative to others.

### Example
A tenant-based partition key causes one tenant to overload a single shard.

### Notes
Hot partitions undermine scalability and latency goals.

---

## Index
A data structure used to accelerate lookup and query performance.

### Example
An index on `event_time` improves range queries.

### Notes
Indexes improve reads but increase storage and write cost.

---

## Cache
A fast-access storage layer used to reduce repeated computation or repeated data retrieval.

### Example
An API caches frequently requested user settings in Redis.

### Notes
Caching improves latency and throughput but introduces invalidation and staleness challenges.

---

## Cache Invalidation
The process of expiring, updating, or removing stale cache entries.

### Example
Invalidate a product record in cache when the source-of-truth database changes.

### Notes
Cache invalidation is often the hardest part of caching design.

---

# AI and IDS Terms

## Instruction Specification
A structured definition of AI behavior that separates semantics, constraints, contracts, inference, and deterministic computation.

### Example
An AI-IDS document that defines guardrails, input schema, output schema, assumptions, and derived logic.

### Notes
An instruction specification should be treated like an engineering artifact, not an informal prompt.

---

## AI-IDS
Artificial Intelligence Instruction Design Set.
A deterministic instruction architecture for production AI systems.

### Example
A specification that defines exactly how an incident summary should be produced for identical inputs.

### Notes
AI-IDS is model-agnostic and provides a structured layer above runtime and decoding controls.

---

## Definitions (IDS)
The section that establishes execution-time meaning of terms used elsewhere in the specification.

### Example
Defining what "customer impact" means before it is used in guardrails or reasoning.

### Notes
Definitions explain meaning, not procedure.

---

## Role (IDS)
The section that defines the system perspective, scope, and responsibility.

### Example
"Customer-facing incident communication component."

### Notes
Role constrains framing and perspective.

---

## Objective (IDS)
The section that defines the single measurable outcome the system must produce.

### Example
"Produce a deterministic incident summary suitable for external communication."

### Notes
Objective is not the same as style preference or broad mission.

---

## Guardrails (IDS)
Non-negotiable constraints and failure conditions that override lower-precedence sections.

### Example
"Do not include personal data."

### Notes
Guardrails are authoritative and must not be weakened by examples or guidelines.

---

## Structure of Input (IDS)
The section that defines the input contract, including required and optional inputs.

### Example
`incident_report` required, `timeline` optional.

### Notes
Inputs not declared in the contract should not influence execution.

---

## Structure of Output (IDS)
The section that defines the output contract and determinism boundary.

### Example
"One paragraph, maximum three sentences, plain text."

### Notes
Output schema determines what downstream systems can safely consume.

---

## Derived Logic (IDS)
The section that defines deterministic computation as a finite, ordered sequence of explicit steps.

### Example
Normalize -> extract -> remove disallowed content -> order -> truncate -> validate.

### Notes
Derived logic must not rely on hidden judgment or randomness.

---

## Assumptions (IDS)
The section that declares explicitly permitted inference when inputs are incomplete.

### Example
"If time context is missing, assume immediate publication."

### Notes
Undeclared inference is a design error.

---

## Reasoning Policy (IDS)
The section that defines deterministic ambiguity resolution.

### Example
"If multiple causes are possible, prioritize customer impact when causality is indeterminate."

### Notes
Reasoning policy chooses among allowed interpretations; it does not introduce new logic arbitrarily.

---

## Guidelines and Instructions (IDS)
Non-authoritative guidance that may influence generation but never override contracts, constraints, or deterministic logic.

### Example
"Prefer plain language over technical language."

### Notes
Guidelines affect phrasing, not meaning or execution order.

---

## Few Shot Examples (IDS)
Illustrative input/output pairs used to influence generation without becoming authoritative rules.

### Example
A sample incident report paired with a compliant summary.

### Notes
Examples must never override guardrails, contracts, or logic.

---

## Precedence Order (IDS)
The authoritative order used to resolve conflicts across IDS sections.

### Example
Definitions -> Role -> Objective -> Guardrails -> Input -> Assumptions -> Reasoning Policy -> Derived Logic -> Output -> Guidelines -> Examples.

### Notes
Precedence is distinct from document formatting order.

---

## Execution Dependency Chain (IDS)
The dependency-driven sequence by which IDS sections influence runtime execution.

### Example
Definitions inform role, role constrains objective, objective is bounded by guardrails, and so on.

### Notes
Execution is driven by dependency, not just section placement.

---

## Bounded Inference
Inference that is explicitly allowed and constrained.

### Example
A system may infer qualitative resolution status only when that assumption is declared.

### Notes
Bounded inference is essential for reliable AI behavior.

---

## Determinism Boundary
The defined limit within which outputs must remain equivalent for identical inputs.

### Example
Equivalent JSON output after normalization and ordering.

### Notes
A determinism boundary may tolerate surface phrasing differences while enforcing structural equivalence.

---

## Output Normalization
Post-generation processing used to make outputs conform to a consistent contract.

### Example
Whitespace trimming, lowercasing where appropriate, ordering fields, deduplicating repeated items.

### Notes
Normalization supports practical determinism at the contract layer.

---

## Hallucination
Generated content not grounded in the allowed inputs, logic, or assumptions.

### Example
An AI system invents a root cause not supported by the incident report.

### Notes
Hallucination often results from implicit reasoning, weak constraints, or poor validation.

---

## Determinism Rate
The percentage of repeated runs over equivalent inputs that produce equivalent outputs within the defined boundary.

### Example
97% of repeated executions produce structurally equivalent JSON.

### Notes
Determinism rate is a practical operational metric, not an abstract property only.

---

## Constraint Violation Rate
The percentage of outputs that violate defined guardrails or contracts.

### Example
2% of outputs contain forbidden fields.

### Notes
This metric is essential for safety and operational review.

---

## Schema Compliance Rate
The percentage of outputs that conform to the expected input or output schema.

### Example
99.5% of generated outputs validate against the JSON schema.

### Notes
Schema compliance is a minimum reliability measure for production AI outputs.

---

## Output Variance
The amount of variability observed across equivalent runs.

### Example
Ordering differences, phrasing variation, or omitted fields across repeated executions.

### Notes
Variance should be bounded and measured, not guessed.

---

# Documentation Terms

## Architecture Decision Record (ADR)
A document that captures a significant technical or architectural decision, the context in which it was made, the alternatives considered, and the consequences accepted.

### Example
ADR-012 records the decision to use event sourcing for the orders domain, why CQRS was rejected, and what trade-offs were accepted.

### Notes
ADRs are immutable once accepted. Superseded ADRs are not deleted: they are marked as deprecated and reference the ADR that replaces them.

---

## Documentation Lifecycle
The defined states a documentation artifact progresses through: Draft, Current, Deprecated, Archived.

### Example
A runbook transitions from Current to Deprecated when the system it describes is decommissioned.

### Notes
Undeclared lifecycle state is the primary cause of stale documentation being treated as authoritative.

---

## Data Dictionary
A reference document that defines the canonical meaning of fields within a domain or data product, including field names, types, allowed values, and business semantics.

### Example
The orders data dictionary defines that `total_cents` is an integer representing the order total in the smallest currency unit and must never be stored as a float.

### Notes
A data dictionary complements a data contract. The contract governs compatibility; the dictionary governs meaning.

---

## Model Card
A documentation artifact that describes a deployed ML or AI model: its purpose, training data, performance characteristics, known limitations, and usage policy.

### Example
A model card for a churn prediction model documents that it was trained on 12 months of subscription data, achieves 82% precision at the operating threshold, and must not be used for credit decisions.

### Notes
Model cards are a prerequisite for responsible AI deployment. They make model behavior visible to teams who consume the model but did not build it.

---

## Prompt Registry
A versioned catalog of AI prompts used in production, including each prompt's intent, input schema, output schema, and most recent evaluation results.

### Example
The prompt registry entry for `incident-summary-v3` records that it expects a structured incident report as input, produces a plain-text summary, and achieved 96% schema compliance and 94% determinism rate in the last evaluation run.

### Notes
A prompt registry treats prompts as engineering artifacts with versions, ownership, and review history, not as informal configuration.

---

## Runbook
An operational guide that enables an engineer to diagnose, operate, or recover a system during an incident or routine task without needing to read the source code.

### Example
The orders-pipeline runbook describes how to confirm the pipeline is healthy, what consumer lag thresholds indicate a problem, and the step-by-step recovery procedure for each known failure mode.

### Notes
A runbook is only useful if it can be acted on by an engineer who did not write the system. Test it by having someone unfamiliar with the system follow it.

---

## Docstring
A structured comment attached to a function, class, or module that describes its purpose, parameters, return value, and error conditions. Part of the code artifact, not optional for public interfaces.

### Example
TypeScript, JSDoc: `@param orderId - The order to retrieve.`, `@returns Order total in cents.`, `@throws {NotFoundError} If the order does not exist.` Python, Google-style: `Args: order_id: The order to retrieve.`, `Returns: Order total in cents.`, `Raises: NotFoundError: If the order does not exist.`

### Notes
The documentation contract (purpose, every parameter, the return value, every raised error) is uniform across languages; the tag syntax is per-language, decided in `docs/decisions/ADR-002-python-docstring-style.md`: TypeScript uses JSDoc tags (`@param`, `@returns`, `@throws`), parsed by its own tooling; Python uses Google-style docstrings (`Args:`, `Returns:`, `Raises:`), parsed by Sphinx/pdoc/mkdocstrings and IDE hover. Type annotations describe the shape at compile time; docstrings describe the contract for anyone reading or generating documentation.

---

# Project Structure Terms

## CLAUDE.md
A project-root file that captures binding engineering standards, project structure, Definition of Done checklists, and non-obvious constraints for Claude Code to apply during an engagement. It is instantiated from the template in `meta/claude-code-usage.md` before any implementation begins.

### Example
A `CLAUDE.md` that declares the folder layout, references engineering-os standards, and lists every DoD checklist item that must pass before a task is marked complete.

### Notes
CLAUDE.md is a contract, not a summary. It is loaded automatically by Claude Code at session start. An empty or placeholder CLAUDE.md is equivalent to no standards guidance. See `meta/claude-code-usage.md` for the full template and bootstrap protocol.

---

## Bootstrap Protocol
The mandatory sequence an AI agent must complete before writing any code: read all Engineering OS files, create and populate CLAUDE.md, confirm completeness, declare project structure, then begin implementation.

### Example
Step 1: read all meta/, macro/, meso/, micro/ files. Step 2: create CLAUDE.md from the template. Step 3: confirm all sections populated. Step 4: declare folder layout. Step 5: begin implementation.

### Notes
Skipping the bootstrap protocol is the primary cause of standards drift in AI-assisted engineering. See `meta/claude-code-usage.md`.

---

## IDS File
A plain-text file with a `.ids` extension that contains an AI-IDS specification. Lives in the `ids/` folder at the project root. Contains no code; only the specification sections defined in `meso/ai-ids-template.md`.

### Example
`ids/content-cleaner.ids` contains the DEFINITIONS, ROLE, OBJECTIVE, GUARDRAILS, and other sections for a content-cleaning AI task. The Python harness `src/ai_cleaner.py` reads this file at startup.

### Notes
The `.ids` file is the source of truth for what the AI model should do. The harness module contains no specification logic, only API call mechanics. Changes to a `.ids` file are engineering changes that require review.

---

## Project Root Convention
The standard that every folder in a project has a declared purpose before the first file is created. Folders are named by artifact type (`ids/`, `lib/`, `input/`, `output/`, `docs/`, `tests/`) not by team or date.

### Example
A project declaring `src/` for source modules, `ids/` for AI-IDS specs, `input/` for raw data, `output/` for pipeline results, and `docs/` for ADRs and contracts, all before writing any code.

### Notes
See `micro/project-structure.md` for the canonical folder layout by project type.

---

## Dependency Direction
The rule that dependencies between modules flow in one direction only, from higher-level entry points down to lower-level utilities and config. Circular imports are forbidden.

### Example
`main.py` imports from `src/order_processor.py`, which imports from `src/config.py`. `src/config.py` imports nothing from src. This forms an acyclic graph.

### Notes
Violation of dependency direction creates circular imports and prevents independent testing. See `micro/project-structure.md` Section 8 and `micro/coding-standards/python.md` Section 10.

---

## Value Object
A domain concept represented as a named, typed, immutable data container: a dataclass in Python or an interface/type in TypeScript. Preferred over untyped dictionaries for domain data.

### Example
`@dataclass class OrderItem: order_id: str; sku: str; quantity: int; unit_price_cents: int` is a value object. `{"order_id": ..., "sku": ...}` is not: it loses the contract.

### Notes
Value objects make the data contract visible at the type level. They are independently testable and self-documenting. See `micro/coding-standards/python.md` Section 10.

---

## Reliability, Scale, and Governance Terms

## Service Level Objective (SLO)
A numeric target for a Service Level Indicator over a window (e.g. 99.9% of requests succeed over 30 days).

### Example
`checkout-availability: 99.9% over 30d` with an error budget of 43 minutes.

### Notes
The error budget (allowed failure within the window) is what turns the objective into a decision rule: when it is spent, reliability work takes priority. See `meso/reliability.md`.

---

## Error Budget
The amount of failure an SLO permits within its window; spending it pauses feature releases until it recovers.

### Example
0.1% of a 30-day window is 43 minutes and 12 seconds of failed-request-equivalent.

### Notes
Alert on burn rate (budget exhausted before the window ends), not raw error rate.

---

## Circuit Breaker
A wrapper around a dependency that fails fast for a cool-down period once the dependency's failure rate crosses a threshold, then lets a trial request through.

### Example
The recommendations breaker trips at 50% failures over 30 seconds; checkout serves without the sidebar for 60 seconds, then retries.

### Notes
Tripping is a signal, and the path behind the breaker must have a defined degraded response. See `meso/reliability.md`.

---

## Bulkhead
Separate pools (threads, connections, queues) per dependency or workload class so saturation in one cannot starve the others.

### Example
Batch export workers run in their own pool of four and never share the interactive request pool.

### Notes
Named after ship compartments. See `meso/reliability.md`.

---

## Backpressure
The mechanism by which a slower consumer makes its producer slow down instead of letting a queue grow without bound.

### Example
The intake queue is bounded at 10,000 messages; at the bound the producer receives a nack and the client is asked to retry.

### Notes
Paired with load shedding: the deliberate rejection of work at a declared bound, in priority order.

---

## Load Shedding
Rejecting work deliberately, in a declared priority order, when a bound is reached, rather than accepting work that will time out.

### Example
At the pool bound, waiters are rejected with `503` and `Retry-After` after 100ms.

### Notes
A system that accepts everything degrades for everyone. See `meso/reliability.md`.

---

## Full Jitter
Randomizing each retry delay between zero and the exponential backoff ceiling so that clients that failed together do not retry together.

### Example
`delay = random(0, min(10s, 100ms * 2^attempt))`.

### Notes
Required by `micro/coding-standards/common.md` Standard 5, together with a cap and a total budget.

---

## Deadline Propagation
Carrying a request's absolute deadline (or remaining budget) through every downstream call so per-hop timeouts derive from what the caller will still wait for.

### Example
A request with 400ms left calls the database with a 250ms timeout, not the database client's default.

### Notes
See `meso/api-design.md`.

---

## Bounded Context
The boundary inside which one domain model and one vocabulary hold without translation; the unit a service should own.

### Example
`Ordering` and `Fulfillment` are separate contexts; each has its own `Order` model and they exchange through an event contract.

### Notes
Draw contexts before services. See `meso/system-design.md`.

---

## Cell-Based Architecture
Partitioning users or tenants into independent full-stack cells, each with its own data store, so a failure or bad deploy affects one cell.

### Example
Tenants hash to cell A or cell B; a canary deploys to cell A first.

### Notes
The control plane (routing, identity) is shared and must be more available than any cell. See `meso/system-design.md`, `meso/infrastructure.md`.

---

## Capacity Model
The numeric statement of expected load, data volume, and growth, and the derived sizing of pools, partitions, and instances, including which component saturates first.

### Example
800 peak RPS, 40 GB growing 60 GB/year, largest tenant 15%; the Postgres pool saturates first at roughly 2,400 RPS.

### Notes
Lives in the project's Scale Targets. See `meso/system-design.md`.

---

## Scale Targets
The CLAUDE.md section holding a project's non-functional requirements in numbers: users, peak RPS, data volume, latency, availability, RPO/RTO, tenancy, classification, regulatory scope.

### Example
See the example table in `skills/eng-os-bootstrap/references/claude-md-template.md`.

### Notes
Populated from the Product Brief (`eng-os-plan-app` Phase 2b). Every capacity model, SLO, load test, and cost budget is checked against it.

---

## Expand/Contract Migration
A schema change performed in three steps (add the new structure backward-compatibly, migrate code and data, remove the old structure later) so no deploy requires old and new code to switch at once.

### Example
Add `phone_e164` nullable; dual-write; backfill in batches; drop `phone` two releases later.

### Notes
See `meso/database-design.md`, `meso/deployment.md`.

---

## Metric Cardinality
The number of distinct time series a metric produces, equal to the product of its labels' distinct values.

### Example
`http_requests_total{route, status}` with 40 routes and 8 statuses is 320 series; adding `user_id` makes it unbounded.

### Notes
Unbounded identifiers belong on logs and traces, never on metric labels. See `meso/observability.md`.

---

## Infrastructure as Code (IaC)
Declaring every infrastructure resource in versioned code applied by a pipeline, so environments are reproducible and nothing exists that is not declared.

### Example
`infra/envs/prod.tfvars` differs from `stage.tfvars` only in cell count, sizes, and secret references.

### Notes
See `meso/infrastructure.md`.

---

## Data Classification
The sensitivity level assigned to every dataset (Public, Internal, Confidential, Restricted) that decides its encryption, access, logging, retention, and transfer rules.

### Example
`customers.phone` is Confidential, field-level encrypted, and never logged.

### Notes
Derived data inherits the highest level of its inputs. See `meso/data-governance.md`.

---

## Data Lineage
The record of which sources and transformations produced a dataset, queryable upstream and downstream.

### Example
`customers_dim` is produced by the nightly job from `customers`, run id stamped per row.

### Notes
Captured by the pipeline, not maintained by hand. See `meso/data-governance.md`.

---

## Watermark
The event-time bound past which late-arriving events are handled by a declared policy rather than included in a window's primary computation.

### Example
A daily aggregate closes 3 hours after midnight; later events go to a correction pass.

### Notes
See `meso/data-strategy.md`.

---

## Design Profile
A concrete set of design-system values (tokens, type scale, layout sizes) a project adopts, inherits, or declares, as distinct from the OS-level rule that one profile must be declared.

### Example
The default profile in `skills/eng-os-design-system/references/profile-default.md`.

### Notes
See `meso/design-system.md` Section 3.11.

---

## Evidence Ledger
The table in `evidence/ledger.md` recording the failure or comparison that justified each evidence-based rule.

### Example
E-18: fixed retry schedule with no jitter, found in the 2026-09-01 review, justifies Standard 5's jitter rule.

### Notes
Cited by id from `skills/MINDMAP.md` and ADRs.

---

## Pre-Processing Gate
A deterministic decision, made in code before an AI-IDS model call, about whether to make the call at all or what subset of data it should see. Distinct from DERIVED LOGIC, which describes what the model computes once called, not whether it is called.

### Example
A scoring module's `allRunsTiedOn()` check skips the AI call entirely when every run already has the identical score for a score type, since a zero-delta tie could never clear the spec's own `gap_threshold`.

### Notes
Correctly lives outside the spec, but the spec must point to it (name it and say where it lives) per `meso/ai-deterministic-systems.md`'s Undocumented Processing Boundary failure mode; see E-28.

---

## Post-Processing Step
A deterministic operation, in code, performed on an AI-IDS model's output after the call returns: arithmetic, a lookup, or a threshold classification. Distinct from DERIVED LOGIC, which the model itself executes as part of being called.

### Example
Rounding a model-produced confidence score to two decimal places before storing it, or mapping a returned label to a stored enum value.

### Notes
Correctly lives outside the spec, but the spec must point to it (name it and say where it lives) per `meso/ai-deterministic-systems.md`'s Undocumented Processing Boundary failure mode; see E-28.

---

## Terminology Lock
The set of canonical nouns and verbs a project fixes before implementation, with the rejected alternatives and the reason for each, so a core concept is never renamed mid-build.

### Example
A lock that picks "Runbook" and rejects "playbook" because "playbook" already means incident-response playbooks elsewhere in the organization.

### Notes
Produced in `eng-os-plan-app` Phase 4, recorded in CLAUDE.md, and enforced by `eng-os-code-conventions`. A rename after the lock is a single complete pass across code, UI, docs, and tests.

---

## Checkpoint Table
The table in `eng-os-core` that maps a trigger (a new endpoint, a migration, a test file) to the skill that must run before work continues.

### Example
A new route handler hits the rows for API contracts, MVC placement, and input validation, so three skills run before the task is called done.

### Notes
Each row is a stop condition, not a suggestion. A skipped checkpoint is drift regardless of output quality.

---

## Vertical Slice
A task that cuts through every layer a behavior needs (data, logic, interface, test), so it is demoable and revertible on its own.

### Example
One task that adds a column, the endpoint that reads it, and the test that covers it, instead of three tasks that each leave the system non-functional until all land.

### Notes
The decomposition rule in `eng-os-execute-feature`. A layer-by-layer split fails it.

---

## Feature Spec
The three approved files under `.specs/<feature>/` (requirements, design, tasks) that define one feature before implementation starts.

### Example
`.specs/service-freshness-list/` holding `requirements.md`, `design.md`, and `tasks.md`, each marked `Approved` with a date.

### Notes
Written by `eng-os-spec-feature` and run by `eng-os-execute-feature`. A change approved during execution is written back into the files.

---

## Acceptance Criterion
One numbered, testable statement of behavior in a feature's requirements, written in EARS notation with a concrete value.

### Example
R1.5: WHEN a Service's Runbook was last reviewed 90 or more whole days ago THE SYSTEM SHALL show the state "red".

### Notes
One behavior per criterion. A criterion with no check that could fail it is not yet an acceptance criterion.

---

## EARS
Easy Approach to Requirements Syntax: a set of sentence templates (event-driven, state-driven, unwanted behavior, optional feature, ubiquitous) that give each requirement a visible trigger and one response.

### Example
IF a request has no valid session THEN THE SYSTEM SHALL return 401 and no Service data.

### Notes
Used for acceptance criteria by `eng-os-spec-feature`. Templates are in that skill's Phase 1.

---

## Approval Gate
A hard stop after a planning artifact where work waits for an explicit approval before the next artifact starts.

### Example
After `requirements.md` is presented, the design is not started until the user says "approved," and the file's `Status:` becomes `Approved <date>`.

### Notes
Silence, a question, or partial feedback is not approval. A change to an earlier file reopens the later ones.

---

## Traceability Check
A check that every acceptance criterion appears in at least one task and every task lists at least one criterion.

### Example
A screen task that satisfied no criterion for text labels was caught here: the labeling criterion had no task until it was added.

### Notes
Run before the tasks gate in `eng-os-spec-feature`. A task that serves no criterion is scope creep.

---
