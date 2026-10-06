# Architecture Decision Record: When an ADR Is Required

**Authors:** Haresh V. Parekh

---

## Metadata

| Field | Value |
|---|---|
| ADR Number | ADR-003 |
| Status | Accepted |
| Date | 2026-09-01 |
| Owner | Haresh V. Parekh |
| Supersedes | none |

## Context

`eng-os-core`'s Session-End Rule required an ADR for "every significant decision made during the
session," with "significant" defined broadly enough (any choice between two viable approaches)
that a normal session produced several ADRs of little future value, and the volume made the
important ones hard to find.

## Decision

An ADR is required when at least one holds: the decision is expensive to reverse; it deviates
from a documented pattern in the OS or the project's CLAUDE.md; it changes a Terminology Lock
term, a Message Area Code, or a Scale Target; or two or more viable approaches were considered
and a later reader could reasonably ask why. Decisions that are local, cheap to reverse, and
follow the documented pattern are recorded in the commit message. The test: would a new
engineer six months from now need this to avoid re-litigating it?

Recorded in `meso/documentation.md` 2.1, `skills/documentation-standards`, and
`skills/eng-os-core`.

## Consequences

### Accepted Trade-offs
- Some borderline decisions will be recorded only in commit history.

### Doors Closed
- None; the threshold can be tightened or loosened by amending the Decision.

### Benefits
- The ADR log stays readable, and the decisions in it are the ones that matter.

---

## Alternatives Considered

### Alternative 1: Keep "every significant decision"

**What it is:** the original Session-End Rule, where "significant" meant any choice between two viable approaches.

**Why rejected:** complete but unread; the volume made the important ADRs hard to find.

### Alternative 2: ADRs only at design time

**What it is:** require ADRs when a design is written, and not during implementation.

**Why rejected:** it misses decisions made during implementation, which the drift catalogue in `meta/claude-code-usage.md` identifies as the ones most often lost.

---

## Validation

Revisit if audits find threshold-level decisions with no ADR, or if the ADR folder grows faster
than one per feature on average.

## References

- `meso/documentation.md`
- Internal architecture review of 2026-09-01 (not published), Section 7 A
