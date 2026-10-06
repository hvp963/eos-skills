---
name: eng-os-reliability-engineering
description: "Use when defining SLOs or error budgets, setting timeouts or retries on an outbound call, bounding a queue or pool, adding a circuit breaker or degraded path, or planning a chaos exercise. Owns how a running system stays within its targets under load and partial failure."
sources:
  - meso/reliability.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Reliability Engineering

Apply these rules to any code path that calls a dependency, accepts load, or carries an
availability or latency target. `eng-os-observability` defines the signals; this skill defines the
targets and the reactions. `eng-os-deployment-practices` defines how a release moves; this defines how
the running system survives.

Not for the HTTP contract itself (`eng-os-api-design` owns request and response shape, versioning, and the deadline header), the log and metric shapes (`eng-os-observability`), or the infrastructure the targets run on (`eng-os-platform-infrastructure`).

## Principles

- **Fault isolation over global stability.** A slow dependency, a hot tenant, or a bad deploy affects one bulkhead, one cell, one code path.
- **Explicitness over implicitness.** Targets are numbers; timeouts are declared; degraded modes are designed and tested.
- **Observability as a first-class concern.** Every target has a signal and an alert.

## Service Level Objectives

Every user-facing capability declares SLIs (availability ratio, p99 latency, freshness,
AI correctness), an SLO per SLI over a window sized from the Scale Targets, and the resulting
error budget. When the budget is spent, feature work pauses until it recovers. Alert on burn
rate (budget exhausted before window end), not raw error rate.

```
slo: checkout-availability
  sli:     count(status < 500) / count(all)  over rolling 30d
  target:  99.9%          budget: 43m 12s / 30d
  alert:   burn rate > 14.4x over 1h (page) | > 6x over 6h (ticket)
```
- Failure mode: "high availability" with no number cannot decide whether today's incident matters or say no to the next risky launch.

## Timeouts, Deadlines, Retries

- Every outbound call has a timeout derived from the caller's propagated deadline (`eng-os-api-design`), shorter than the caller's own; connection timeouts in the hundreds of milliseconds, request timeouts at the dependency's p99 plus headroom.
- Retry only idempotent operations on transient failures, with full jitter, cap, and budget (`eng-os-coding-standards-common` Standard 5). One layer owns retry per call path; stacked retries at client, gateway, and service turn one failure into twenty-seven attempts.
- Failure mode: a library default of "no timeout" turns a hung dependency into a hung service.

## Circuit Breakers, Bulkheads, Load Shedding

- **Breaker** per dependency: trips on failure rate over a window, fails fast during cool-down, lets a trial request through; tripping is a metric and a log, and the path behind it has a defined degraded response.
- **Bulkheads**: separate pools and queues per dependency and per workload class (interactive vs. batch, tier, tenant cohort).
- **Shedding**: every queue and pool is bounded; at the bound, reject with a retryable status (`503` + `Retry-After`) in declared priority order rather than accept work that will time out. Admission control caps in-flight work per instance to what the capacity model says fits within SLO.
- Failure mode: a system that accepts everything degrades for everyone; one that sheds deliberately stays within SLO for what it accepts.

## Graceful Degradation

Rank every dependency critical (fail the request) or non-critical (degrade: cached with a
staleness marker, skipped enrichment, partial result flagged as partial). The degraded path is
tested code, not a catch block. Re-rank when a dependency is added.
- Failure mode: a recommendations sidebar takes the checkout page down because nobody decided it was optional.

## Proving It

Chaos exercises on a schedule, stage then production with a blast-radius limit: kill instances,
inject latency, exhaust a pool, fail a cell or region, expire a certificate. Each has a
hypothesis, a measured outcome, and a ticket per gap. Rollback drills (`eng-os-deployment-practices`)
and restore drills (`eng-os-platform-infrastructure`) are the same discipline.
- Failure mode: the first time the failover runs is the outage, and it does not work.

See `references/example.md` for one service's SLO declaration, breaker configuration, and a
game-day record.

## Failure Modes

- no numeric SLO, so no error budget and no basis to prioritize reliability over features
- alerts on raw error rate that page for blips and sleep through slow burns
- missing or per-call-site timeouts
- retries stacked at every layer
- shared pools that let one workload class starve the rest
- unbounded queues that accept work destined to time out
- degraded paths that exist only as catch blocks
- failover never run outside an incident

## Definition of Done

- [ ] Every user-facing capability has SLIs, SLOs, and an error budget with burn-rate alerts
- [ ] Every outbound call has a timeout derived from the propagated deadline
- [ ] Retry is owned by one declared layer per call path, with jitter, cap, and budget
- [ ] Every dependency is behind a circuit breaker with a defined degraded response
- [ ] Pools and queues are bounded per workload class; shedding order is declared
- [ ] Dependencies are ranked critical or non-critical; each non-critical one has a tested degraded path
- [ ] Chaos exercises run on a schedule with hypotheses, measured outcomes, and tracked gaps
