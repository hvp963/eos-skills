# Engineering Principles

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Non-negotiable rules that govern how systems are designed, built, and operated.

### What This Is Not
- not best practices
- not optional advice
- not domain-specific implementation guidance

## Scope
- Level: Macro
- Applies To: Product, Data, and AI systems

---

## 1. Explicitness Over Implicitness

### Rule
All system behavior must be explicitly defined.

### Why
Implicit behavior creates ambiguity, hidden coupling, and operational risk.

### Applies To
- API contracts
- data schemas
- AI specifications
- service responsibilities
- system boundaries

### Implications
- define inputs and outputs explicitly
- define assumptions explicitly
- define constraints explicitly
- avoid hidden defaults that materially change behavior

### Example
An API contract specifies every field, its type, whether it is required, and what constitutes a valid value. A consumer implements against the contract without reading the server implementation. When a field is removed, it is a versioned breaking change, not a silent omission.

### Failure Mode
Undeclared assumptions and hidden behavior cause unpredictable outcomes.

---

## 2. Determinism Within Defined Boundaries

### Rule
Systems must produce predictable outputs for identical inputs within a clearly defined boundary.

### Why
Predictability is required for testing, debugging, trust, and repeatable operations.

### Applies To
- data pipelines
- APIs
- workflow orchestration
- AI systems through IDS, validation, and normalization

### Implications
- preserve stable ordering where relevant
- eliminate hidden computation
- define determinism boundaries explicitly for AI systems

### Example
An ETL pipeline run on the same input dataset always produces the same output records in the same order. The determinism boundary is declared: identical inputs → structurally equivalent output after normalization. For AI systems, the boundary is stated as: equivalent inputs → structurally equivalent JSON output, surface phrasing differences permitted.

### Failure Mode
Inconsistent behavior makes debugging and validation unreliable.

---

## 3. Idempotency by Default

### Rule
Operations must be safe to retry.

### Why
Retries, replays, and duplicate deliveries are normal in distributed systems.

### Applies To
- data ingestion
- batch jobs
- stream consumers
- APIs
- workflow steps

### Implications
- use stable identifiers
- deduplicate at appropriate boundaries
- separate logical operation identity from transport identity

### Example
An order ingestion pipeline uses `order_id` as the upsert key. Replaying the same batch twice produces the same set of order records: no duplicates, no missing records, no side-effect amplification. A second delivery of the same event is a no-op, not an error.

### Failure Mode
Repeated execution corrupts state or produces duplicate side effects.

---

## 4. Contracts as Source of Truth

### Rule
All system interactions must be governed by explicit, versioned contracts.

### Why
Contracts are the only scalable way to align producers, consumers, and reviewers.

### Applies To
- APIs
- events
- datasets
- AI input and output schemas

### Implications
- validate schemas at boundaries
- treat breaking changes as migrations
- use contracts to govern compatibility

### Example
A payment event schema is registered in a shared schema registry. The producer's CI asserts against it before deployment. The consumer's CI asserts it can parse the registered schema. Neither side deploys without a passing contract assertion. A field rename is a breaking change: it requires a new schema version and a migration window.

### Failure Mode
Schema drift and incompatible changes cause downstream breakage.

---

## 5. Validation at Boundaries

### Rule
Inputs and outputs must be validated whenever they cross a meaningful boundary.

### Why
Unchecked invalid data propagates and amplifies failures downstream.

### Applies To
- service requests and responses
- event publication and consumption
- ETL stage transitions
- AI inputs and outputs

### Implications
- validate structure
- validate required fields
- validate allowed values when necessary
- fail fast on invalid boundary crossings

### Example
An API validates every request field (type, length, and allowed values) before passing it to any business logic. A request with a missing required field returns 400 immediately, before any database call is made. An AI output is validated against its declared schema before it is passed to downstream logic: invalid output is rejected, not silently used.

### Failure Mode
Invalid data reaches downstream systems and corrupts state or outputs.

---

## 6. Observability as a First-Class Concern

### Rule
Every system must be measurable, debuggable, and explainable in operation.

### Why
Unobservable systems cannot be trusted, improved, or safely operated.

### Applies To
- latency
- error rates
- throughput
- data freshness
- AI determinism and violations

### Implications
- define metrics before production
- log structured contextual information
- provide tracing across boundaries when appropriate

### Example
Before a new pipeline goes to production, its design review requires: throughput metric, error rate metric, freshness metric, and a structured log record at the output boundary with trace_id. These are defined in the design artifact, not added after the first incident.

### Failure Mode
Blind systems cause slow detection, slow diagnosis, and repeated incidents.

---

## 7. Fault Isolation Over Global Stability

### Rule
Failures must be contained within defined boundaries rather than allowed to cascade.

### Why
Distributed systems fail partially, not uniformly.

### Applies To
- services
- partitions
- pipelines
- consumers
- caches
- AI evaluation stages

### Implications
- isolate dependencies
- use timeouts and circuit breakers
- separate blast radius by partition, tenant, or workload

### Example
A multi-tenant pipeline partitions work by tenant ID. A single tenant's data spike or malformed payload does not affect processing for other tenants. The blast radius of a failure is bounded by partition. One failing consumer group does not affect unrelated consumer groups on the same topic.

### Failure Mode
A single component failure causes system-wide instability.

---

## 8. Scalability Through Partitioning

### Rule
Systems must scale by dividing work into independent units.

### Why
Centralized bottlenecks eventually dominate throughput and latency.

### Applies To
- traffic
- storage
- compute
- event streams
- tenant workloads

### Implications
- choose meaningful partition keys
- avoid global scans where possible
- monitor hot partitions

### Example
An event stream is partitioned by region. Each region's events are processed independently by dedicated consumer instances. Adding a new region means adding a partition and consumer group: no changes to existing partitions, no rebalancing of unrelated work.

### Failure Mode
Load concentrates on a bottleneck, causing performance collapse.

---

## 9. Separation of Concerns

### Rule
Each component must have a clear, limited responsibility.

### Why
Coupled responsibilities increase complexity, slow change, and amplify failure impact.

### Applies To
- service boundaries
- layers
- pipelines
- AI logic versus presentation
- business logic versus orchestration

### Implications
- avoid embedding unrelated logic in the same component
- isolate formatting from computation
- isolate policy from execution

### Example
An order service owns order state transitions. It does not send emails, generate invoices, or update inventory. Those concerns belong to separate services that consume order events. Each service has exactly one reason to change. Changing the email template does not touch the order service.

### Failure Mode
Tight coupling makes local changes risky and expensive.

---

## 10. Bounded Inference for AI Systems

### Rule
All inference in AI systems must be explicitly allowed and limited.

### Why
Unbounded inference leads to hallucination, inconsistency, and unsafe outputs.

### Applies To
- assumptions
- reasoning policy
- output validation
- specification design

### Implications
- declare assumptions explicitly
- define reasoning policy deterministically
- do not allow examples or style guidance to introduce logic

### Example
An AI system that generates incident summaries declares in its ASSUMPTIONS section: "If the root cause field is missing, assume the incident is still under investigation." Any other inference about root cause is not permitted. The output schema is validated after every generation. A violation, such as an invented root cause, is caught before the output reaches the communication channel.

### Failure Mode
The system invents unsupported conclusions or behaves unpredictably.

---

## 11. Security as a Design Constraint

### Rule
Every system must treat security as a design constraint, not a feature. Access must be minimized, inputs validated, secrets isolated, and trust boundaries explicit at every boundary crossing.

### Why
Security violations are often irreversible: data breaches, privilege escalation, and injection attacks cannot be undone by a patch. A system that defers security to a later phase has already accepted a structural vulnerability.

### Applies To
- service and API boundaries
- data inputs and outputs
- secrets and credentials
- AI inputs and outputs
- user authentication and authorization
- inter-service communication

### Implications
- validate all external input at the boundary where it enters the system
- never pass raw user input to queries, commands, file paths, or AI prompts
- secrets must never appear in source code, logs, or error messages
- grant only the access required for the operation, not the access that is convenient
- trust boundaries must be explicit, never assumed because a request originated inside the network

### Example
A service exposes an API endpoint that accepts a user ID. The user ID is validated as a UUID before any database call is made. The query uses parameterized statements. The service's database role has SELECT access on the specific tables it needs, not schema-level access. Secrets are loaded from environment variables at startup and never logged. A failed authentication attempt emits a structured audit log event.

### Failure Mode
Raw input passed to queries, commands, or AI prompts. Secrets hardcoded in source code or present in log output. Services granted broad database or cloud permissions by default. Trust assumed because a request arrived from inside the network.

---

## 12. Testability as a Design Property

### Rule
Systems must be designed to be testable. Testability is not added after implementation: it shapes how components are structured, how dependencies are managed, and how boundaries are defined.

### Why
A system that cannot be tested cannot be verified. When testability is deferred, coupling accumulates with every implementation decision until the cost of achieving it becomes structural and permanent.

### Applies To
- module and service boundaries
- external dependency management
- AI system outputs and determinism boundaries
- data pipeline transformation stages
- configuration and environment separation

### Implications
- external dependencies must be injectable or mockable at unit test boundaries
- functions must have defined inputs and outputs; no hidden state reads at call sites
- AI systems must define a testable determinism boundary
- environments must be separable so tests do not require production access or credentials
- test coverage is a first-class output of implementation, not a separate phase

### Example
A pipeline stage that calls an external API is designed with the API client injected as a parameter, not instantiated inside the function. The stage is unit-tested with a mock client in isolation. The AI system it feeds defines a determinism boundary: equivalent inputs produce structurally equivalent JSON output. A contract test verifies the output schema after every model or instruction change. The test suite runs in CI against a stage environment, not production credentials.

### Failure Mode
Functions that call external services directly with no injection point. AI outputs with no declared testable boundary. Test suites that require production credentials or live external services to pass. Testing planned as a final phase, after all coupling decisions have been made.

---

## Guiding Principle
Reduce ambiguity. Enable determinism. Enforce correctness.
