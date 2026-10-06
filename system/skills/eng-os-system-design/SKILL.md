---
name: eng-os-system-design
description: "Use when architecting a new system or service BOUNDARY and its trade-offs: C4 modeling, stateless vs. stateful design, fault isolation patterns, event-driven vs. request-response choice. For the checklist to scaffold an already-decided service, see `references/service-checklist.md`. For HTTP/RPC contract specifics, see `eng-os-api-design`."
sources:
  - meso/system-design.md
  - micro/design-review-template.md
  - micro/templates/service-template.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# System Design

Apply these rules when designing a distributed system or service boundary, or when reviewing one.

## Principles

- **Explicitness over implicitness.** Define system boundaries, inputs, outputs, dependencies, and ownership explicitly.
- **Contracts as source of truth.** Every major boundary has a defined interface, schema, or service contract.
- **Fault isolation over global stability.** Design boundaries so one component can fail without collapsing the whole system.
- **Scalability through partitioning.** Assume scale will require partitioned compute, state, or traffic.
- **Separation of concerns.** Separate user-facing logic, orchestration, persistence, async processing, and policy logic where meaningful.

## System Modeling (C4)

- **Context**: system boundary, external actors, adjacent systems.
- **Container**: major services, data stores, queues, execution environments.
- **Component**: internal responsibilities inside a service, when internals materially affect correctness, scale, or reviewability.
- **Code**: implementation-level structure, only when needed.

Rule: every production design must be explainable at least to Context and Container level.

## Core Design Patterns

- **Stateless services**: for synchronous APIs, worker fleets, orchestration layers. Session state lives in a shared cache, not the instance. Failure mode: hidden instance state breaks scaling and recovery.
- **Event-driven architecture**: for downstream fan-out, audit trails, async enrichment. Failure mode: poor event contracts and non-idempotent consumers cause inconsistency.
- **API gateway**: centralizes auth, throttling, routing for multiple downstream services. Failure mode: the gateway becomes a bottleneck or an overly complex orchestration engine.
- **Retry with idempotency**: bounded retries only when the operation is safe to repeat; pair every retry policy with an idempotency key check. Failure mode: non-idempotent retries multiply side effects.
- **Caching**: for read-heavy, repeated-lookup, or precomputed-expensive-result access patterns, with explicit keys and TTL, invalidated on write. Failure mode: serving stale/inconsistent results with no clear cache policy.
- **Bulkheading and isolation**: separate worker pools, queues, and connection pools for high-risk or high-volume workloads sharing infrastructure. Failure mode: one workload consumes all shared capacity.

## Design Process

1. Define business and operational requirements
2. Identify correctness boundaries and critical constraints
3. Model the system with C4
4. Choose interaction style: synchronous, asynchronous, or hybrid
5. Define contracts and ownership boundaries
6. Evaluate trade-offs against quality attributes
7. Identify likely failure modes and blast radius
8. Define observability requirements before implementation

## Bounded Contexts and Decomposition
Draw bounded contexts (one domain model, one vocabulary, no translation inside) before drawing services. A service owns one context or a coherent part of one, never two; contexts exchange data through explicit contracts with translation at the boundary, never a shared database or shared domain classes. Decompose a monolith along context seams, never by technical layer.
- Failure mode: services sharing tables form a distributed monolith that cannot deploy, scale, or fail independently.

## Capacity Model
State capacity assumptions in numbers, in the project's `## Scale Targets`: expected and peak RPS, data volume and growth, largest tenant, fan-out per request, latency and availability targets. Derive pool sizes, partitions, cache memory, and instance counts from them, and record which component saturates first and at what load. Revisit when any input changes by more than a factor of two.
- Failure mode: the first bottleneck is discovered at launch, in the component nobody wrote a number for.

## Multi-Region and Cell-Based Architecture
Isolate blast radius in two dimensions. **Regions**: the full stack per region, data replicated under a declared consistency model (active-passive with a stated RPO, or active-active with conflict resolution), failover per region. **Cells**: within a region, users or tenants partitioned into independent full-stack cells with their own data store; a cell is the unit of canary and of failure. Shared control-plane components (routing, identity, configuration) are designed for higher availability than any cell. Physical layout: `eng-os-platform-infrastructure`.
- Failure mode: one global database, cache, and queue make one global incident; ten times the users is ten times the blast radius.

## Backpressure and Load Shedding
Every queue, worker pool, and connection pool has an explicit bound; at the bound the system sheds deliberately (retryable rejection, drop lowest priority, cheaper code path) rather than growing memory or latency without limit. Producers observe consumer lag and slow down. Full pattern set (timeouts, breakers, bulkheads, degradation): `eng-os-reliability-engineering`.
- Failure mode: an unbounded in-memory queue absorbs a spike for minutes, then the process dies and every queued item is lost at once.

## Service Checklist
For scaffolding a new backend service once its boundary is decided, work through `references/service-checklist.md`, which cross-references `eng-os-api-design` for the wire contract and `eng-os-reliability-engineering` for outbound-call behavior.

## UX and Information Architecture
The nav-as-destination, atomic-save, metric-as-doorway, and dynamic-offset rules live in `eng-os-design-system`; they are UI constraints. The transaction-boundary half of the atomic-save rule (single DB vs. saga/outbox across services) still applies here and in `eng-os-database-design`.

## Design Review

For structured review of a design (new system, service boundary, or architectural change), work through the full checklist in `../../micro/design-review-template.md`. It covers: problem definition, boundaries/C4 model, principles check, patterns check, failure modes, observability, contracts/validation, and a final approve / approve-with-changes / rework decision. Every review must end in explicit action items, not vague concerns.

For a worked example applying this skill's C4/boundary reasoning to a concrete scenario, see `references/example.md`.

## Failure Modes

- tight coupling across services causes cascading failures
- synchronous chains create latency amplification
- shared bottlenecks limit scale
- hidden contracts create breakage during change
- weak isolation expands blast radius
- no explicit ownership causes design drift
- services sharing tables or domain classes form a distributed monolith
- unbounded queues and pools turn a traffic spike into an out-of-memory crash

## Definition of Done

- [ ] Boundaries are explicit
- [ ] C4 modeling is clear at Context and Container level
- [ ] Contracts are defined
- [ ] Major patterns are justified
- [ ] Quality attribute trade-offs are explicit
- [ ] Likely failure modes are identified with blast radius
- [ ] Observability expectations are defined
- [ ] Cross-service multi-entity updates use a saga or outbox pattern, not a distributed transaction (the single-transaction case is a `eng-os-database-design` and `eng-os-design-system` 3.8 concern)
- [ ] Bounded contexts are drawn before services; no service straddles two or shares a database with another
- [ ] A capacity model states peak load, data volume, largest tenant, and which component saturates first
- [ ] Blast-radius isolation is explicit: single region with stated RPO/RTO, or multi-region and/or cells with routing and failover declared
- [ ] Every queue and pool is bounded and its load-shedding behavior is defined

A worked example of the checklist: `references/service-checklist-example.md`.
