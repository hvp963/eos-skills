# Engineering OS Audit: Worked Example

An abbreviated compliance report for a fictional bootstrapped web app, `fleet-console`, showing
the report shape and the "Where The Agent Has Been Drifting" section that makes it useful as
feedback on agent behavior rather than a file list.

```markdown
# Engineering OS Compliance Report: fleet-console

**Audited:** 2026-09-01
**Project CLAUDE.md:** C:/apps/fleet-console/CLAUDE.md
**Engineering OS reference:** ~/src/engineering-os (pinned 1.7.0)

## Summary

The project is bootstrapped and its Active Skills list matches its scope, but three practices
it committed to at bootstrap have not held: message codes are missing on every toast
notification, business logic has accumulated in two route handlers, and Scale Targets were
never filled in, so the load test that ran before launch had no pass criteria.
Counts: Pass 24, Fail 5, Partial 3, N/A 4, Unknown 0.

## Findings by Section

### A. Bootstrap Integrity
| # | Status | Evidence |
|---|---|---|
| A1 | Pass | CLAUDE.md line 5 points at the OS path and pins 1.7.0 |
| A2 | Pass | 9 skills listed, each with a reason |
| A5 | Partial | Terminology Lock says "Vehicle"; `src/models/asset.ts` and 3 API fields say "asset" |
| A6 | Pass | 4 areas, codes unique, next sequence 000041 |
| A9 | Fail | `## Scale Targets` contains "TBD after launch" |

### B. Architecture Practices Gate
| # | Status | Evidence |
|---|---|---|
| B2 | Fail | 11 of 11 toast calls in `src/views/pages/*.tsx` pass bare strings; no `FLT0000nn` code |
| B3 | Fail | `src/controllers/dispatch.ts` lines 40 to 138 compute routing eligibility inline |
| B10 | Pass | axe runs in CI (`.github/workflows/ui.yml`); shell components keyboard-tested |

### C. Checkpoint-Table Compliance
| # | Status | Evidence |
|---|---|---|
| C7 | Partial | Logs carry `trace_id` in 6 of 8 modules; `src/models/geo.ts` logs without it |
| C13 | Fail | `src/lib/maps-client.ts` has no timeout; retry loop has no jitter or budget |

## Where The Agent Has Been Drifting

- **Message codes skipped specifically on toast notifications**, in every one of 11 call sites
  across 5 files, while every `throw` carries a code. The checkpoint fires on "user-facing
  message" and the agent has been treating toasts as UI, not messages.
- **Business logic written in the handler when the model file did not yet exist.** Both
  failing handlers date from tasks where no `models/` file for that concept existed; the agent
  implemented inline rather than creating the model first.
- **Scale Targets treated as a launch-time deliverable.** The section was left as a placeholder
  at bootstrap and nothing later forced it, so the capacity model and load test had no numbers.

## Recommended Next Actions

1. Populate Scale Targets (blocks every reliability check downstream).
2. Add a timeout, jitter, and budget to the maps client (outage risk).
3. Extract dispatch eligibility into `src/models/dispatch.ts`.
4. Assign `FLT` codes to the 11 toasts in one pass; update the sequence counter.
5. Resolve the Vehicle/asset drift with one complete rename and an ADR.
```
