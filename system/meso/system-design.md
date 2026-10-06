# System Design

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for designing distributed systems using explicit principles, quality attributes, modeling, and architecture patterns.

### What This Is Not
- not implementation code
- not vendor-specific infrastructure guidance
- not a replacement for domain-specific playbooks

## Scope
- Level: Meso
- Applies To: Product, platform, data-adjacent, and AI-adjacent distributed systems

---

## Applied Principles

### Explicitness Over Implicitness
Define system boundaries, inputs, outputs, dependencies, and ownership explicitly.

### Contracts as Source of Truth
Every major boundary should have a defined interface, schema, or service contract.

### Fault Isolation Over Global Stability
Design boundaries so one component can fail without collapsing the whole system.

### Scalability Through Partitioning
Assume scale will require partitioned compute, state, or traffic.

### Separation of Concerns
Separate user-facing logic, orchestration, persistence, asynchronous processing, and policy logic where meaningful.

---

## System Modeling (C4)

### Context
Define the system boundary, external actors, and adjacent systems.

### Container
Define major services, data stores, queues, and execution environments.

### Component
Define internal responsibilities inside a service or container.

### Code
Define implementation-level structure only when needed.

### Rule
Every production design should be explainable at least to Context and Container level.
Component level should be added when service internals materially affect correctness, scale, or reviewability.

---

## Core Design Patterns

### Stateless Services
Use stateless services where possible.

#### Why
Statelessness improves scalability, deployment flexibility, and failover.

#### When to Use
- synchronous APIs
- worker fleets
- orchestration layers

#### Example
A search API fleet where any instance can handle any request. When load increases, 5 new instances are added behind the load balancer in seconds. When an instance fails, in-flight requests are retried transparently. Session state lives in a shared cache, not in the instance, so no instance is irreplaceable.

#### Failure Mode
Hidden state inside service instances causes scaling and recovery issues.

---

### Event-Driven Architecture
Use events to decouple producers and consumers when direct synchronous dependency is unnecessary.

#### Why
Improves decoupling, adaptability, and workload independence.

#### When to Use
- downstream fan-out
- audit/event trails
- asynchronous enrichment
- eventual propagation

#### Example
When an order is fulfilled, the order service publishes an `OrderFulfilled` event. Three independent consumers (inventory, billing, notification) each consume it from their own consumer group. Adding a fourth consumer (analytics) requires no change to the order service or any existing consumer. Each consumer fails independently.

#### Failure Mode
Poor event contracts and non-idempotent consumers cause inconsistency.

---

### API Gateway
Use a centralized entry point for cross-cutting client concerns.

#### Why
Centralizes authentication, throttling, routing, and protocol translation.

#### When to Use
- multiple downstream services
- external client access
- shared policy enforcement

#### Example
An external-facing gateway handles authentication, rate limiting, and routing for 6 downstream services. Clients call one endpoint. The gateway resolves token identity once and passes a scoped claim downstream; no downstream service re-authenticates. Adding a new downstream service is a routing rule change, not a client contract change.

#### Failure Mode
The gateway becomes a bottleneck or an overly complex orchestration engine.

---

### Retry with Idempotency
Use bounded retries only when operations are safe to repeat.

#### Why
Retries are necessary for transient failure; idempotency makes them safe.

#### When to Use
- transient downstream errors
- queue-driven workloads
- workflow orchestration

#### Example
A payment webhook handler retries up to 3 times with exponential backoff on network errors. Before processing, the handler checks an `idempotency_key` against a processed-events table. A second delivery of the same webhook is a no-op: no double charge, no error. The retry and the idempotency check are designed together, not independently.

#### Failure Mode
Non-idempotent retries multiply side effects.

---

### Caching
Store frequently accessed data closer to computation.

#### Why
Reduces repeated computation and latency.

#### When to Use
- read-heavy access patterns
- repeated configuration lookup
- profile or metadata retrieval
- precomputed expensive results

#### Example
A product catalog API caches category listings in Redis with an explicit 5-minute TTL. Cache keys are namespaced by category ID. When a product is updated, the relevant cache key is invalidated immediately, not left to expire. Cold-cache performance is acceptable because the origin database query is indexed and within latency SLA.

#### Risks
- stale data
- invalidation complexity
- hidden dependency on cache warmness

#### Failure Mode
Serving inconsistent or stale results without clear cache policy.

---

### Bulkheading and Isolation
Separate high-risk or high-volume workloads from each other.

#### Why
Protects unrelated workloads from shared failure or starvation.

#### When to Use
- multi-tenant systems
- mixed-priority workloads
- latency-sensitive plus batch workloads

#### Example
A reporting pipeline and a real-time order processing pipeline share the same infrastructure account but use separate worker pools, separate queues, and separate database connection pools. A reporting job that triggers a slow query does not affect order processing latency. A reporting worker crash does not touch the order consumer group.

#### Failure Mode
One workload consumes all shared capacity.

---

## Bounded Contexts and Decomposition

A bounded context is the boundary inside which one domain model and one vocabulary hold
without translation. Draw bounded contexts before drawing services: a service should own one
bounded context, or a coherent part of one, and never straddle two. When two contexts must
exchange data, the exchange goes through an explicit contract (an API, an event schema) with a
translation at the boundary, not through a shared database or a shared domain model.

Decompose a monolith along bounded-context seams, in the order that reduces the most
coupling for the least migration risk. Do not decompose by technical layer (all controllers
in one service, all persistence in another); that produces a distributed monolith.

- Failure mode: services that share tables or shared domain classes cannot deploy, scale, or
  fail independently; every schema change becomes a coordinated multi-service release.

## Capacity Model

Every production design states its capacity assumptions in numbers, recorded in the project's
Scale Targets: expected and peak requests per second, data volume and growth rate, largest
single tenant, fan-out ratio per request, and the latency and availability targets. Derive
from these the sizing of connection pools, queue partitions, cache memory, and database
instances, and record which component hits its ceiling first and at what load. Revisit the
model when any input changes by more than a factor of two.

- Failure mode: a system sized by guesswork discovers its first bottleneck during a launch,
  and the bottleneck is usually the one component nobody wrote a number down for.

## Multi-Region and Cell-Based Architecture

Beyond a single region, isolate blast radius in two dimensions:

- **Regions**: deploy the full stack independently per region; replicate data with a declared
  consistency model (active-passive with a stated RPO, or active-active with conflict
  resolution). Route users to a home region; fail over per region, not per component.
- **Cells**: within a region, partition users or tenants into independent cells that each run
  a complete copy of the stack with its own data store. A failure, a bad deploy, or a noisy
  tenant affects one cell. Deploy to one cell first; a cell is the unit of canary.

Shared control-plane components (routing, identity, configuration) are the exception and must
be designed for higher availability than any cell.

- Failure mode: one global database, one global cache, and one global queue mean one global
  incident; the same architecture at ten times the users has ten times the blast radius.

## Backpressure and Load Shedding

Every queue, worker pool, and connection pool has an explicit bound. When a bound is reached,
the system sheds load deliberately (reject with a retryable status, drop the lowest-priority
work, degrade to a cheaper code path) rather than growing unbounded memory or latency. Producers
observe consumer lag and slow down; a slow consumer must never be able to take down its
producer. See `meso/reliability.md` for the full pattern set (timeouts, circuit breakers,
bulkheads, shedding, graceful degradation).

- Failure mode: an unbounded in-memory queue absorbs a traffic spike for several minutes,
  then the process runs out of memory and loses every queued item at once.

## Design Process

1. Define business and operational requirements
2. Identify correctness boundaries and critical constraints
3. Model the system with C4
4. Choose interaction style: synchronous, asynchronous, or hybrid
5. Define contracts and ownership boundaries
6. Evaluate trade-offs against quality attributes
7. Identify likely failure modes and blast radius
8. Define observability requirements before implementation

---

## Failure Modes

- tight coupling across services causes cascading failures
- synchronous chains create latency amplification
- shared bottlenecks limit scale
- hidden contracts create breakage during change
- weak isolation expands blast radius
- no explicit ownership causes design drift
- services that share tables or domain classes form a distributed monolith that cannot deploy or fail independently
- unbounded queues and pools turn a traffic spike into an out-of-memory crash that loses in-flight work

---

## Definition of Done

A system design is complete when:
- boundaries are explicit
- C4 modeling is clear at Context and Container level
- contracts are defined
- major patterns are justified
- quality attribute trade-offs are explicit
- likely failure modes are identified
- observability expectations are defined
- bounded contexts are drawn before services, and no service straddles two contexts or shares a database with another
- a capacity model states peak load, data volume, largest tenant, and which component saturates first
- blast-radius isolation is explicit: single region with a stated RPO/RTO, or multi-region and/or cell-based with the routing and failover model declared
- every queue and pool is bounded and the load-shedding behavior at the bound is defined
- UX and information-architecture constraints for any UI are covered by `meso/design-system.md` Section 3.8
