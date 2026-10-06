# Spec Feature Worked Example — Runbook Coverage Tracker, Phase 1

Continues the `eng-os-plan-app` worked example (`../../eng-os-plan-app/references/plan-example.md`)
and feeds the `eng-os-execute-feature` worked example
(`../../eng-os-execute-feature/references/execute-feature-example.md`), which runs the task list
this example produces. The Product Brief is approved and the project is bootstrapped. The
exchanges below are a plausible illustration, in the same spirit as the plan-app example.

Scope entering this skill: **Phase 1, Track and see staleness.** Service and Runbook entities,
and a Service List screen with a red/yellow/green/missing indicator on the fixed 90-day default.
Folder: `.specs/service-freshness-list/`.

## Phase 0 — Intake

CLAUDE.md read: Terminology Lock fixes "Runbook," "stale/fresh," and "review interval." The
Active Skills include the database, API, security, testing, observability, design-system, and
Node.js standards skills. The Phase 1 brief says "red/yellow/green/missing" but gives a rule only
for stale ("every 90 days"), so the yellow threshold is undefined.

Spec warranted: yes. The feature takes five tasks, adds an endpoint and two tables, and has
boundary behavior. The undefined yellow threshold is exactly the kind of gap a spec exists to
surface before code does.

## Phase 1 — Requirements, `requirements.md`

```markdown
# Requirements: Service Freshness List

Status: Approved 2026-10-02
Source: Product Brief Phase 1, "Track and see staleness"

## Problem
On-call engineers learn a Runbook is missing or stale during an incident. They need to see, for
every Service, whether its Runbook is fresh before that happens.

## R1 — As an on-call engineer, I want each Service's Runbook freshness shown, so that I find a missing or stale Runbook before an incident
- R1.1 WHEN the Service List loads THE SYSTEM SHALL show every Service with exactly one
  freshness state
- R1.2 WHEN a Service has no Runbook THE SYSTEM SHALL show the state "missing"
- R1.3 WHEN a Service's Runbook was last reviewed fewer than 75 whole days ago THE SYSTEM SHALL
  show the state "green"
- R1.4 WHEN a Service's Runbook was last reviewed 75 to 89 whole days ago THE SYSTEM SHALL show
  the state "yellow"
- R1.5 WHEN a Service's Runbook was last reviewed 90 or more whole days ago THE SYSTEM SHALL
  show the state "red"
- R1.6 THE SYSTEM SHALL label each state with text as well as color

## R2 — As an engineering manager, I want Service data restricted to signed-in users, so that internal Runbook links are not exposed
- R2.1 IF a request has no valid session THEN THE SYSTEM SHALL return 401 and no Service data

## R3 — As the team that operates this tool, I want freshness signals emitted, so that missing coverage is visible without opening the UI
- R3.1 WHEN the Service List is served THE SYSTEM SHALL write one structured log line named
  `service_freshness_computed`
- R3.2 WHEN the Service List is served THE SYSTEM SHALL set the gauge
  `services_missing_runbook_total` to the number of Services in state "missing"

## Out of scope
- Per-service review-interval override (Phase 3 of the Product Brief). Every Service uses 90 days.
- Marking a Runbook reviewed (Phase 2). Phase 1 data comes from seeded rows.
- Data store outage behavior. The project's shared error handler already returns 503.

## Open questions
- Where does "yellow" start? → Answered at Gate 1: the final 15 days of the interval, so 75 to
  89 days (R1.4). A Runbook reviewed exactly 90 days ago is stale (R1.5), per "every 90 days."
```

**Gate 1.** The agent presents the file and names the decision it made that the reader may want
to change: the 15-day yellow window. The user replies "yellow from 75 days is right, approved."
That is explicit approval, so `Status:` becomes `Approved 2026-10-02` and Phase 2 starts.

## Phase 2 — Design, `design.md`

```markdown
# Design: Service Freshness List

Status: Approved 2026-10-02
Requirements: requirements.md (Approved 2026-10-02)

## Overview
Freshness is computed at read time by a pure function from the Runbook's last-reviewed date and
the current date. Considered and rejected: a nightly job that stores the state in a column. A
stored state is stale between runs, which defeats a tool about staleness, and adds a job to
operate.

## Components and interfaces
| Component | Responsibility | Contract |
|---|---|---|
| `services` and `runbooks` tables | Hold Service and Runbook metadata | Section below |
| `computeFreshness(service, runbook, now)` | Map dates to one of four states | Returns `"green" \| "yellow" \| "red" \| "missing"` |
| `GET /v1/services` | Return each Service with its computed state | Versioned under `/v1/`, behind the existing auth middleware |
| Service List screen | Render one indicator per Service | Consumes `GET /v1/services` |
| List-handler telemetry | Emit the log line and gauge | Fields per `eng-os-observability` |

## Data model
`services(id, name, owning_team)`. `runbooks(id, service_id, link_url, last_reviewed_at)`. A
Service has zero or one Runbook; no row is the "missing" state.

## Error handling
| Criterion | Behavior in this design | User-facing message code |
|---|---|---|
| R2.1 | The existing auth middleware rejects the request before the handler runs | none shown |

## Test strategy
| Layer | Covers |
|---|---|
| Unit | R1.2, R1.3, R1.4, R1.5 through `computeFreshness`, including the 74/75 and 89/90 day boundaries |
| Integration | R1.1, R2.1, R3.1, R3.2 through the endpoint |
| Component | R1.1, R1.6 on the Service List screen |

## Checkpoints
`eng-os-database-design` (tables), `eng-os-coding-standards-nodejs` (function),
`eng-os-api-design` and `eng-os-security-practices` (endpoint), `eng-os-design-system` and
`eng-os-testing-strategy` (screen), `eng-os-observability` (signals). No ADR: computing at read
time is local and cheap to reverse, so the rejected alternative is recorded in this file only.

## Traceability
| Requirement | Design element |
|---|---|
| R1.1 | Tables, `GET /v1/services`, Service List screen |
| R1.2, R1.3, R1.4, R1.5 | `computeFreshness` |
| R1.6 | Service List screen |
| R2.1 | Auth middleware on `GET /v1/services` |
| R3.1, R3.2 | List-handler telemetry |
```

**Gate 2.** Presented with the rejected alternative called out. The user approves. Every
requirement has a row in Traceability, and no design element lacks a requirement, so no gap or
scope creep is found.

## Phase 3 — Tasks, `tasks.md`

First draft of T4's Definition of Done read "renders four distinct indicators using design-system
tokens." The traceability check then failed its first test: **R1.6 appeared in no task.** Color
alone would have satisfied the draft DoD and shipped an indicator that fails the requirement's
text-label rule. The fix added R1.6 to T4 and changed its Definition of Done to require
"correctly labeled" text.

```markdown
# Tasks: Service Freshness List

Status: Approved 2026-10-02
Requirements: requirements.md (Approved 2026-10-02)
Design: design.md (Approved 2026-10-02)

- [ ] **T1 — `services` and `runbooks` tables**
  - Depends on: none
  - Checkpoints: eng-os-database-design
  - Requirements: R1.1, R1.2
  - Definition of Done: Migration creates both tables with a nullable FK from
    `runbooks.service_id`; a paired `down` migration drops them cleanly
- [ ] **T2 — Freshness computation function**
  - Depends on: T1
  - Checkpoints: eng-os-coding-standards-nodejs
  - Requirements: R1.2, R1.3, R1.4, R1.5
  - Definition of Done: `computeFreshness(service, runbook, now)` returns
    `"green" | "yellow" | "red" | "missing"`; unit tests cover all four states plus the exact
    75-day and 90-day boundaries
- [ ] **T3 — `GET /v1/services` endpoint**
  - Depends on: T1, T2
  - Checkpoints: eng-os-api-design, eng-os-security-practices
  - Requirements: R1.1, R2.1
  - Definition of Done: Returns each service with its computed freshness state; a request with
    no valid session gets 401 and no data; response is versioned under `/v1/`
- [ ] **T4 — Service List screen**
  - Depends on: T3
  - Checkpoints: eng-os-design-system, eng-os-testing-strategy
  - Requirements: R1.1, R1.6
  - Definition of Done: Renders every service's indicator using design-system tokens (not ad hoc
    hex values); a component test confirms all four states render distinct, correctly labeled
    indicators
- [ ] **T5 — Structured logging + freshness metric**
  - Depends on: T3
  - Checkpoints: eng-os-observability
  - Requirements: R3.1, R3.2
  - Definition of Done: A `service_freshness_computed` structured log line and a
    `services_missing_runbook_total` gauge are emitted on each list-endpoint call

Order: T1, T2, T3, T5, T4. T4 and T5 both depend only on T3; T5 goes first so observability is
not left until the UI is visually working.

## Traceability check
| Check | Result |
|---|---|
| Every criterion appears in a task | Pass after fix: R1.6 added to T4 |
| Every task lists a requirement | Pass |
| Every Definition of Done is runnable | Pass after fix: T4 requires labeled indicators, T3 requires the 401 case |
```

**Gate 3.** The task list is presented with the failure and the fix named. The user approves,
and all three files now carry `Status: Approved 2026-10-02`.

## Handoff

The agent tells the user the spec is ready and invokes `eng-os-execute-feature`, which adopts
`tasks.md` in its Phase 1. Five tasks run one at a time, each ticking its own checkbox in the
same commit that lands it, and Phase 6 walks the nine acceptance criteria R1.1 through R3.2.

## What this shows

The undefined yellow threshold was found while writing criteria, not while testing T2. The
traceability check caught an uncovered criterion (R1.6) before any code existed to get it
wrong. The design rejected one alternative in writing and declined an ADR for it by applying the
threshold. Three gates, each with an explicit approval,
produced files the execution loop could run and check without asking what "done" meant.
