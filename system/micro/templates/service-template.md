# Service Template

**Authors:** Haresh V. Parekh

## Purpose
Starter checklist for designing or implementing a service.

## Inputs
- business capability
- upstream dependencies
- downstream consumers
- expected traffic profile

---

## Checklist

### Boundary
- service responsibility is explicit
- inputs and outputs are explicit
- ownership is explicit

### Contracts
- request contract defined
- response contract defined
- error contract defined
- versioning strategy defined where needed

### Reliability
- retry behavior defined
- idempotency addressed
- timeouts defined
- fault isolation considered

### Performance
- expected latency target identified
- expected throughput target identified
- caching strategy considered where relevant

### Observability
- metrics defined
- structured logs defined
- trace correlation strategy defined if relevant

### Failure Modes
- top failure modes identified
- blast radius understood

## Output
A service design or implementation should not proceed until each applicable item is addressed.
