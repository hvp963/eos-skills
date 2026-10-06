# Reliability Engineering

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
The design guide for keeping a system within its stated availability and latency targets under
load, partial failure, and dependency degradation: objectives, timeouts, retries, isolation,
shedding, degradation, and the practice of proving those mechanisms work before an incident does.

### What This Is Not
- not the observability guide (that defines the signals; this defines the targets and the reactions)
- not the deployment guide (that defines how a release moves; this defines how a running system survives)
- not incident response process (see `meso/team-practices.md`)

## Scope
- Level: Meso
- Applies To: every production service, pipeline, and AI system with a stated availability or latency target
- See Also: `meso/system-design.md`, `meso/observability.md`, `meso/deployment.md`, `meso/api-design.md`, `macro/system-quality-attributes.md`

---

## Applied Principles

### Fault Isolation Over Global Stability
Every mechanism here exists to keep a failure local: a slow dependency, a hot tenant, or a bad
deploy affects one bulkhead, one cell, one code path, never the whole system.

### Explicitness Over Implicitness
Targets are numbers. Timeouts are declared. Degraded modes are designed, named, and tested, not
discovered.

### Observability as a First-Class Concern
An objective that is not measured is a wish. Every target below has a signal that reports it and
an alert that fires on it.

---

## 1. Service Level Objectives

Every user-facing capability declares:

- **SLIs**: the measured signals (availability as the ratio of good requests to total; latency
  as the p99 within a window; freshness for data products; correctness for AI outputs)
- **SLOs**: the target per SLI over a window (e.g. 99.9% of requests succeed over 30 days; p99
  under 300ms over 1 hour), sized from the Scale Targets and the business impact of a miss
- **Error budget**: the allowed failure within the window (0.1% of 30 days is 43 minutes).
  When the budget is spent, feature releases pause and reliability work takes priority until it
  recovers. This is the mechanism that makes the objective real.

```
slo: checkout-availability
  sli:      count(status < 500) / count(all)   over rolling 30d
  target:   99.9%
  budget:   43m 12s of failed-request-equivalent per 30d
  alert:    burn rate > 14.4x over 1h  (page)  |  > 6x over 6h (ticket)
```

Alert on burn rate, not on raw error rate: a burn-rate alert fires when the budget will be
exhausted before the window ends, which is the only condition that needs a human at 3am.

- Failure mode: a system with "high availability" as a goal and no number has no way to decide
  whether today's incident matters, and no way to say no to the next risky launch.

## 2. Timeouts and Deadlines

Every outbound call has a timeout. The timeout is derived from the caller's remaining deadline
(see `meso/api-design.md`, Deadline Propagation), not chosen per call site, and is always
shorter than the caller's own timeout. Connection timeouts are short (hundreds of milliseconds);
request timeouts match the dependency's p99 plus headroom, never its worst case.

- Failure mode: a client default of "no timeout" on one HTTP library turns a hung dependency
  into a hung service; every thread and connection waits forever for a reply that is not coming.

## 3. Retries

Retry only idempotent operations, only on transient failures, with full jitter, a cap, and a
budget (`micro/coding-standards/common.md` Standard 5). Retry at one layer, not every layer: if
the client, the gateway, and the service each retry three times, one failure becomes
twenty-seven attempts. Declare which layer owns retry for each call path.

- Failure mode: stacked retries amplify a brief outage into a self-inflicted denial of service
  that outlasts the original fault.

## 4. Circuit Breakers

Wrap every dependency in a breaker that tracks failure rate over a window and, when it trips,
fails fast for a cool-down period before letting a trial request through. A tripped breaker is
a signal (metric plus log), and the code path behind it must have a defined degraded response
(Section 6), not an exception.

- Failure mode: without a breaker, a dependency at 100% failure still receives every request,
  each waiting a full timeout, so the caller's latency and thread usage are maximal precisely
  when the dependency is least able to recover.

## 5. Bulkheads and Load Shedding

- **Bulkheads**: separate thread pools, connection pools, and queues per dependency and per
  workload class (interactive vs. batch, premium vs. free tier, tenant cohorts at scale). A
  saturated pool affects only its own class.
- **Load shedding**: when a bounded queue or pool is full, reject immediately with a retryable
  status (`503` plus `Retry-After`, or a queue nack) rather than accept work that will time out.
  Shed lowest-priority work first; the priority order is declared per service.
- **Admission control**: limit concurrent in-flight work per instance to what the capacity model
  says it can serve within SLO; excess is shed, not queued indefinitely.

- Failure mode: a system that accepts everything degrades for everyone; a system that sheds
  deliberately stays within SLO for the work it accepts and tells the rest to come back.

## 6. Graceful Degradation

For every dependency, declare what the system does when it is unavailable: serve from cache
with a staleness marker, skip a non-critical enrichment, return a partial result flagged as
partial, or fail the request. The degraded path is code that is tested and exercised, not a
catch block. Rank dependencies as critical (fail the request) or non-critical (degrade), and
review the ranking when a new dependency is added.

- Failure mode: a recommendations sidebar that takes the checkout page down with it because
  nobody decided it was optional.

## 7. Proving It: Chaos and Game Days

Mechanisms that have never fired do not work. On a schedule, in stage and then in production
with a blast-radius limit: kill instances, inject latency into a dependency, exhaust a pool,
fail a region or a cell, expire a certificate. Each exercise has a hypothesis ("the breaker
trips within 10s and the degraded path serves cached results"), a measured outcome, and a
ticket for every gap. Rollback drills (`meso/deployment.md`) and DR drills
(`meso/infrastructure.md`) are the same discipline applied to other mechanisms.

- Failure mode: the first time the failover runs is the outage, and it does not work.

---

## Failure Modes

- no numeric SLO, so no error budget and no way to prioritize reliability against features
- alerts on raw error rate that page for blips and sleep through slow burns
- missing or per-call-site timeouts turn a hung dependency into a hung service
- retries stacked at every layer amplify an outage
- no circuit breaker, so a dead dependency consumes maximal caller resources
- shared pools let one workload class starve the rest
- unbounded queues accept work that will time out
- degraded paths that exist only as catch blocks and have never been exercised
- failover and rollback that have never been run outside an incident

## Definition of Done

Reliability design is complete when:
- every user-facing capability has SLIs, SLOs, and an error budget with burn-rate alerts
- every outbound call has a timeout derived from the propagated deadline
- retry is owned by one declared layer per call path, with jitter, cap, and budget
- every dependency is behind a circuit breaker with a defined degraded response
- pools and queues are bounded per workload class; load shedding order is declared
- dependencies are ranked critical or non-critical, and each non-critical one has a tested degraded path
- chaos exercises run on a schedule with hypotheses, measured outcomes, and tracked gaps
