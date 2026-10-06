# ADR Example — Filled In

An actual instance of the ADR skeleton from `SKILL.md`, filled in for a real-shaped decision. The
blank template with full authoring guidance is canonical at `../../../micro/templates/adr-template.md`;
this file shows what a completed one looks like.

---

# Architecture Decision Record — Adopt Event-Driven Export for Accounting Integrations

**Authors:** Data Platform Team

## Metadata

| Field | Value |
|---|---|
| ADR Number | ADR-014 |
| Status | Accepted |
| Date | 2026-04-02 |
| Owner | Data Platform Team |
| Supersedes | — |

## Context

The expense-approval platform needs to push approved expenses to customer-owned QuickBooks and
Xero accounts. QuickBooks' API has a documented ~2% transient failure rate under load and Xero
rate-limits aggressively per tenant. The current synchronous call from the approval endpoint to
the accounting API means an approval can hang or fail because of a third-party outage that has
nothing to do with our own system's correctness. We need a decision before the Xero integration
ships, since it will double the number of synchronous third-party calls in the approval path.

## Decision

Move accounting export off the synchronous approval path onto an asynchronous, event-driven
worker: approving an expense emits an `expense.approved` event; a separate Export Worker consumes
it and pushes to QuickBooks/Xero with its own retry and backoff policy. This is chosen over
keeping the call synchronous because it decouples approval latency/availability from third-party
uptime, and it optimizes for the approval flow being the fast, always-available path since it is
the higher-frequency, higher-visibility user action. It assumes eventual (not immediate)
consistency between "approved in our system" and "visible in QuickBooks/Xero" is acceptable to
finance users, which was confirmed with the finance admin persona during discovery.

## Consequences

### Accepted Trade-offs
- Export is no longer instantaneous; there will be a visible lag (seconds to low minutes) between
  approval and the expense appearing in the external accounting system.
- We now own a queue and a worker's operational surface (monitoring, dead-letter handling) that
  didn't exist before.

### Doors Closed
- Any future feature that needs a synchronous "yes, this is in QuickBooks now" confirmation at
  approval time would require additional work (e.g., polling or a callback), since the decision
  assumes async is acceptable everywhere export matters.

### Benefits
- Third-party API outages (QuickBooks/Xero) no longer block or fail expense approvals.
- Retry and idempotency logic is isolated to one component instead of duplicated at every call
  site that might need to export.

## Alternatives Considered

### Alternative 1: Keep synchronous call, add client-side retry
**What it is:** Retain the direct call from the approval endpoint, wrap it in a retry-with-backoff
library.
**Why rejected:** Retries still hold the approval request open, so p99 approval latency would
still be dominated by the worst-case third-party response time; it does not solve the coupling
problem, only masks it up to a retry budget.

### Alternative 2: Nightly batch export instead of event-driven
**What it is:** Accumulate approved expenses and push them to QuickBooks/Xero in a single nightly
batch job.
**Why rejected:** Finance admins said same-day visibility in the external accounting system
matters for reconciliation; a nightly batch introduces up to a 24-hour lag, which is worse than
the acceptable "seconds to low minutes" lag of an event-driven design.

## Validation

We'll know this was correct if p99 approval latency stops correlating with QuickBooks/Xero
response-time incidents in our metrics (it should be independent), and if the Export Worker's
dead-letter queue stays near zero under normal third-party degradation. Revisit if finance users
report the async lag is actually a workflow problem, not just a cosmetic delay.

## References

- `../../../micro/templates/adr-template.md`: blank template this instance was filled from
- `../../eng-os-system-design/references/example.md`: service-boundary reasoning that led to isolating
  the Export Worker as its own container
