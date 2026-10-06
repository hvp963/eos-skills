# Execute Feature Worked Example — Runbook Coverage Tracker, Phase 1

Continues the `eng-os-spec-feature` worked example
(`../../eng-os-spec-feature/references/spec-feature-example.md`), which itself continues the
`eng-os-plan-app` worked example (`../../eng-os-plan-app/references/plan-example.md`). The
Product Brief and Phased Milestones are approved, the spec in `.specs/service-freshness-list/`
is approved through all three gates, and the project is already bootstrapped via
`eng-os-bootstrap` with Active Skills including `eng-os-database-design`, `eng-os-api-design`,
`eng-os-security-practices`, `eng-os-testing-strategy`, `eng-os-observability`, `eng-os-coding-standards-nodejs`,
`eng-os-code-conventions`, `eng-os-documentation-standards`, `eng-os-design-system`.

Scope entering this skill: **Phase 1; Track and see staleness.** Service and Runbook entities;
Service List screen with a red/yellow/green/missing indicator using the fixed 90-day default.

## Phase 1 — Decompose

An approved `tasks.md` exists, so this phase adopts it instead of decomposing again. Every task
has all five fields, no dependency points at a later task, and every Definition of Done is
observable, so nothing goes back to the spec. (With no spec, this phase would build the same table
from the approved scope, minus the Requirements column.)

| Task | Depends on | Checkpoints it will hit | Requirements | Definition of Done |
|---|---|---|---|---|
| T1 — `services` and `runbooks` tables | none | `eng-os-database-design` | R1.1, R1.2 | Migration creates both tables with a nullable FK from `runbooks.service_id`; a paired `down` migration drops them cleanly |
| T2 — Freshness computation function | T1 | `eng-os-coding-standards-nodejs` | R1.2, R1.3, R1.4, R1.5 | `computeFreshness(service, runbook, now)` returns `"green" \| "yellow" \| "red" \| "missing"`; unit tests cover all four states plus the exact 75-day and 90-day boundaries |
| T3 — `GET /v1/services` endpoint | T1, T2 | `eng-os-api-design`, `eng-os-security-practices` | R1.1, R2.1 | Returns each service with its computed freshness state; a request with no valid session gets 401 and no data; response is versioned under `/v1/` |
| T4 — Service List screen | T3 | `eng-os-design-system`, `eng-os-testing-strategy` | R1.1, R1.6 | Renders every service's indicator using design-system tokens (not ad hoc hex values); a component test confirms all four states render distinct, correctly labeled indicators |
| T5 — Structured logging + freshness metric | T3 | `eng-os-observability` | R3.1, R3.2 | A `service_freshness_computed` structured log line and a `services_missing_runbook_total` gauge are emitted on each list-endpoint call |

Note T4 needing "and" in its own name check: it does two things (render indicator, per-state
styling) but both are the same vertical slice at the same layer for the same screen. This is
judged acceptable because splitting it further would leave an intermediate task with no
independently checkable DoD, unlike, say, "build the endpoint and write the UI," which genuinely
is two tasks (T3 and T4 here).

## Phase 2 — Sequence

T1 → T2 → T3 → (T4 and T5 in either order, both depend only on T3). T5 is chosen to run before T4
here because the freshness metric is cheap to verify in isolation and de-risks nothing about the
UI. Either order is valid; this order is picked to keep observability from being an
afterthought once the UI is visually working and attention drifts.

The spec's order, T1 → T2 → T3 → T5 → T4, is confirmed before implementation starts. Nothing has
changed since the spec's Gate 3.

## Phase 3 – 5, per task

**T1:** Migration written. Checkpoint hit: `eng-os-database-design`; verify reversibility and confirm
no unsafe `NOT NULL` addition to a populated table (both tables are new, so this doesn't apply,
and that's stated explicitly rather than silently skipped).
*Verify (Phase 4):* migration runs up and down cleanly against a test database; DoD passes.
*Commit (Phase 5):* `feat: add services and runbooks tables`.

**T2:** Function written with unit tests for green/yellow/red/missing and the boundaries at 74/75
and 89/90 days (a runbook reviewed exactly 90 days ago is red, per R1.5 and the Product Brief's
"every 90 days" language; each boundary decision is written into a test name, not left implicit).
*Verify:* all boundary tests pass, and each of R1.2 to R1.5 has a test that names it.
*Commit:* `feat: add freshness computation with 90-day boundary`, with T2's checkbox ticked in
`tasks.md`.

**T3:** Endpoint written under `/v1/services`, reuses the auth middleware already protecting
other read endpoints (checkpoint: `eng-os-security-practices`; verify least privilege, confirm no PII
in the response beyond what the Product Brief's entity list already scoped as necessary).
*Verify:* integration test hits the endpoint, gets versioned, authenticated, correctly shaped
response, and a second test with no session gets 401 and no data (R2.1); DoD passes.
*Commit:* `feat: add GET /v1/services endpoint`.

**T5:** Log line and gauge added at the point T3's handler computes freshness for each service.
*Verify:* log line includes `trace_id`, `span_id`, `severity`, `service` per the observability
skill's structured-field requirement; gauge value matches a seeded fixture's known missing-count.
*Commit:* `feat: add freshness observability signals`.

**T4:** Component built consuming T3's endpoint, using the design system's existing status-color
tokens rather than introducing new ad hoc colors (checkpoint: `eng-os-design-system`; verify token
reuse).
*Verify:* component test renders all four states with visually distinct, correctly labeled
indicators; DoD passes.
*Commit:* `feat: add Service List screen with freshness indicators`.

Each commit also ticks its task's checkbox in `tasks.md`, so the file never disagrees with the log.
Five tasks, five commits, each independently revertible: a `git bisect` landing on T4's commit
means the UI broke, not "somewhere in this feature."

## Phase 6 — Feature Verify

With all five tasks complete: load the Service List screen against the seeded mock data set from
the Product Brief's Phase 7 (missing runbook, reviewed-yesterday green, deep-red overdue,
30-day-override case; though the override case is explicitly out of scope for Phase 1 per the
Phased Milestones, so it is confirmed to render using the 90-day default rather than silently
applying an override that shouldn't exist yet). Confirm the whole slice (table through UI)
composes correctly, not just that each task's isolated DoD passed. Then walk all nine acceptance
criteria in `requirements.md` (R1.1 to R1.6, R2.1, R3.1, R3.2) and mark each passed with the check
that proved it: R1.3 to R1.5 by the T2 boundary tests, R1.6 by the T4 component test, R2.1 by the
T3 no-session test, and so on. No criterion is left without a check. This satisfies Phase 1's
Product Brief Definition of Done: "a seeded set of services with varying last-reviewed dates
renders the correct color for each, verified against the 90-day threshold."

## What this shows

Decomposition happened once, up front, in the spec, before any code existed, and this skill
adopted it rather than redoing it. Nothing was discovered task by task mid-build. Every task named its checkpoints in advance, so nothing was invoked by accident or
skipped by omission. No task started before the previous one's Verify step passed, and each task
left exactly one commit: the sequence T1→T2→T3→T5→T4 in the commit log reads as the task list
in Phase 2, not as a reconstruction after the fact.
