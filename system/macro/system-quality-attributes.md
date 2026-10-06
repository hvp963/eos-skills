# System Quality Attributes

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A framework for evaluating system behavior and managing trade-offs.

### What This Is Not
- not a list of definitions only
- not a set of optional preferences
- not a replacement for principles

## Scope
- Level: Macro
- Applies To: Product, Data, and AI systems

---

## 1. Availability

### Definition
The system is operational and reachable when needed.

### Design Levers
- redundancy
- failover
- health checks
- dependency isolation

### Typical Trade-Offs
Higher availability often increases infrastructure cost and architectural complexity.

### Example
A service deployed across three availability zones with automatic failover. If one zone becomes unreachable, traffic routes to the remaining two within 30 seconds. Health checks verify real dependency connectivity (not just process liveness) before gating traffic.

### Review Questions
- what makes the system unavailable?
- what fails over automatically?
- what dependencies dominate availability?

---

## 2. Resiliency

### Definition
The system continues functioning or degrades safely when failures occur.

### Design Levers
- retries with bounds
- circuit breakers
- graceful degradation
- fallback paths

### Typical Trade-Offs
Resiliency mechanisms can add latency, complexity, and operational overhead.

### Example
A service retries transient upstream failures up to 3 times with exponential backoff. On persistent failure, it returns a degraded response using cached data rather than a hard error, and emits a warning metric. Callers are not aware of the degradation unless they inspect the response flag.

### Review Questions
- how does the system behave under partial failure?
- what is retried, and what is not?
- what degrades instead of failing hard?

---

## 3. Scalability

### Definition
The system handles increased load without unacceptable degradation.

### Design Levers
- partitioning
- horizontal scaling
- stateless services
- queue-based buffering

### Typical Trade-Offs
Scalable systems often introduce coordination complexity and more distributed failure modes.

### Example
An ingestion service partitions work by tenant ID. Adding capacity means adding consumer instances per partition: no change to the routing layer. A new tenant onboarding adds a partition without touching existing partitions or rebalancing in-flight work.

### Review Questions
- what is the scaling unit?
- what is the likely bottleneck?
- where do hot partitions occur?

---

## 4. Latency

### Definition
The time needed to complete a request or operation.

### Design Levers
- caching
- efficient computation
- locality
- reduced synchronous dependency chains

### Typical Trade-Offs
Reducing latency can increase cost, complexity, or inconsistency if aggressive caching is used.

### Example
A product search API caches frequently queried result sets with an explicit TTL. p95 latency under peak load is 45ms: within the 100ms SLA target. The cache TTL and invalidation rule are documented in the design contract, not left as an operational assumption.

### Review Questions
- what is the p95 and p99 target?
- what dependencies dominate latency?
- what work can be made asynchronous?

---

## 5. Throughput

### Definition
The amount of work completed over time.

### Design Levers
- parallelism
- batching
- partitioning
- asynchronous processing

### Typical Trade-Offs
Increasing throughput can increase queueing delay or reduce fairness across workloads.

### Example
A batch pipeline processes 500K records per hour with 10 parallel workers, each consuming an independent partition. Adding 5 workers increases throughput proportionally because partitioning is clean and there are no shared bottlenecks. Backpressure is handled by the queue depth, not by dropping work.

### Review Questions
- what is the maximum expected sustained load?
- what controls backpressure?
- what work is batched and why?

---

## 6. Efficiency

### Definition
The degree to which cost and resources are used effectively.

### Design Levers
- workload tuning
- caching
- storage tiering
- right-sizing
- minimizing duplicate processing

### Typical Trade-Offs
Efficiency optimizations can reduce flexibility or resiliency if over-optimized.

### Example
A nightly pipeline previously recomputed all records from scratch. Switching to delta ingestion (processing only changed records since the last run) reduces compute cost by 70% with no change in output correctness or freshness SLA.

### Review Questions
- what are the main cost drivers?
- what is redundant?
- what work can be eliminated or deferred?

---

## 7. Consistency

### Definition
The correctness and synchronization of data and state across the system.

### Design Levers
- transactional boundaries
- contract validation
- reconciliation
- ordering controls

### Typical Trade-Offs
Higher consistency can increase latency and reduce availability under partition or failure.

### Example
An inventory service uses optimistic locking with a version field on every record. Concurrent updates from two callers return a conflict error on the second writer. The caller retries with the latest version. No silent overwrites occur. Reconciliation runs nightly to catch any divergence from external systems.

### Review Questions
- where is strong consistency required?
- where is eventual consistency acceptable?
- how is reconciliation handled?

---

## 8. Fault Isolation

### Definition
The containment of failures so they do not expand across the system.

### Design Levers
- isolation boundaries
- tenant separation
- workload separation
- circuit breakers
- bulkheads

### Typical Trade-Offs
More isolation can increase design complexity and duplicate infrastructure.

### Example
A failing analytics consumer does not affect the order-processing consumer on the same event topic. They use separate consumer groups, separate error handling, and separate alerting. A timeout in the analytics path triggers a circuit breaker that opens for 60 seconds: order processing continues unaffected.

### Review Questions
- what is the blast radius of a failure?
- can one tenant or workload starve another?
- what fails independently?

---

## 9. Observability

### Definition
The ability to measure, trace, and explain system behavior.

### Design Levers
- metrics
- structured logs
- traces
- audit records
- validation events

### Typical Trade-Offs
Higher observability adds storage, processing, and signal-management overhead.

### Example
A pipeline's throughput, error rate, and freshness metrics are defined in the design review before launch. When a schema change causes a 20% validation failure rate in stage, the alert fires within 2 minutes: before promotion to production. Debugging the failure requires only the trace_id from the alert to find the exact record and validation error in the logs.

### Review Questions
- how is correctness measured?
- what would make debugging impossible?
- how are violations surfaced?

---

## 10. Adaptability

### Definition
The ability of the system to evolve safely as scale, requirements, or interfaces change.

### Design Levers
- versioned contracts
- modular design
- configuration-driven behavior
- explicit boundaries

### Typical Trade-Offs
Adaptable systems often require more upfront structure and design discipline.

### Example
An API uses additive versioning: new optional fields are added without a version bump and existing consumers are unaffected. When a breaking change is unavoidable, a new version endpoint is published alongside v1, which begins returning a `Sunset` header. v1 is removed only after all consumers have migrated and the migration window has passed.

### Review Questions
- what changes are expected most often?
- what makes future change expensive?
- how does the design support additive evolution?

---

## 11. Security

### Definition
The degree to which a system resists unauthorized access, data leakage, injection, and misuse: at every boundary and for every actor.

### Design Levers
- input validation and safe output encoding at every external boundary
- parameterized queries and command argument isolation
- least privilege: grant only the access required, not the access that is convenient
- secrets managed via environment variables or a vault, never in source code
- explicit authentication and authorization on all service and API calls
- structured audit logs for security-relevant events (access denied, authentication failure, privilege escalation attempt)

### Typical Trade-Offs
Strict input validation adds latency at boundaries. Least-privilege access models require more granular IAM and permission management. Sanitizing AI prompt inputs can reduce output flexibility. Security controls often add operational overhead that becomes invisible: until an incident makes it visible.

### Example
An internal service-to-service API uses mutual TLS: no service can call another without a valid certificate. The order service's database role has INSERT and SELECT on order tables only, not UPDATE or DELETE on unrelated tables. Security-relevant events (failed authentication, access denied, input rejected) are logged with timestamp, actor ID, and resource: without payload content or credentials. AI prompt inputs are sanitized before injection into an instruction specification. The blast radius of a compromised service is bounded by the scope of its credentials.

### Review Questions
- what is the trust model at each boundary?
- what is the blast radius if a single service credential is compromised?
- are secrets ever passed through application logic or visible in logs?
- how are security-relevant events logged and alerted?
- what input validation exists at every external boundary?

---

## How to Use This File

Use these attributes in design reviews to evaluate trade-offs.
Principles define what must be true.
Quality attributes help judge whether the chosen design is acceptable.
