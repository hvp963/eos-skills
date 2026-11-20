# Spec Feature Worked Example: Runbook Coverage Tracker, Phase 1

Continues the `eng-os-plan-app` worked example (`../../eng-os-plan-app/references/plan-example.md`)
and feeds the `eng-os-execute-feature` worked example
(`../../eng-os-execute-feature/references/execute-feature-example.md`), which runs the task list
this example produces. The Product Brief is approved and the project is bootstrapped. The
exchanges below are a plausible illustration, in the same spirit as the plan-app example. Names and
times are invented.

Scope entering this skill: **Phase 1, Track and see staleness.** Service and Runbook entities,
and a Service List screen with a red/yellow/green/missing indicator on the fixed 90-day default.
Folder: `.specs/service-freshness-list/`.

## Phase 0: Intake

CLAUDE.md read: Terminology Lock fixes "Runbook," "stale/fresh," and "review interval." The
Active Skills include the database, API, security, testing, observability, design-system, and
Node.js standards skills. The Phase 1 brief says "red/yellow/green/missing" but gives a rule only
for stale ("every 90 days"), so the yellow threshold is undefined.

Spec warranted: yes. The feature takes five tasks, adds an endpoint and two tables, and has
boundary behavior. The undefined yellow threshold is exactly the kind of gap a spec exists to
surface before code does.

`.specs/config.json` does not exist, so the agent asks for the user's handle and writes it:

```json
{
  "identities": { "dana.okafor": "human", "claude-sonnet-5-5": "agent" },
  "approval": { "requirements": "manual", "design": "manual", "tasks": "manual" }
}
```

## Phase 1: Requirements, `requirements.md`

Every requirement is one EARS sentence, and every requirement gets scenarios. The author is the
person who owns it. The agent drafted the rows for Dana, and Dana is the author.

```markdown
## R1 As an on-call engineer, I want each Service's Runbook freshness shown, so that I find a missing or stale Runbook before an incident
| ID | Requirement | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|
| R1.1 | WHEN the Service List loads THE SYSTEM SHALL show every Service with exactly one freshness state | dana.okafor | 2026-10-02 09:10:00 +00:00 | Product Brief Phase 1 | none |
| R1.2 | WHEN a Service has no Runbook THE SYSTEM SHALL show the state "missing" | dana.okafor | 2026-10-02 09:11:00 +00:00 | Product Brief Phase 1 | none |
| R1.3 | WHEN a Service's Runbook was last reviewed fewer than 75 whole days ago THE SYSTEM SHALL show the state "green" | dana.okafor | 2026-10-02 09:12:00 +00:00 | Product Brief Phase 1 | none |
| R1.4 | WHEN a Service's Runbook was last reviewed 75 to 89 whole days ago THE SYSTEM SHALL show the state "yellow" | dana.okafor | 2026-10-02 09:13:00 +00:00 | Product Brief Phase 1 | none |
| R1.5 | WHEN a Service's Runbook was last reviewed 90 or more whole days ago THE SYSTEM SHALL show the state "red" | dana.okafor | 2026-10-02 09:14:00 +00:00 | Product Brief Phase 1 | none |
| R1.6 | THE SYSTEM SHALL label each state with text as well as color | dana.okafor | 2026-10-02 09:15:00 +00:00 | Product Brief Phase 1 | none |

### Scenarios for R1
| ID | Scenario | Requirements | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|---|
| S4 | Given a Runbook reviewed 0 whole days ago, when the Service List loads, then the state is "green". | R1.3 | dana.okafor | 2026-10-02 09:12:30 +00:00 | Product Brief Phase 1 | none |
| S5 | Given a Runbook reviewed 74 whole days ago, when the Service List loads, then the state is "green". | R1.3 | dana.okafor | 2026-10-02 09:12:30 +00:00 | Product Brief Phase 1 | none |
| S6 | Given a Runbook reviewed 75 whole days ago, when the Service List loads, then the state is "yellow". | R1.4 | dana.okafor | 2026-10-02 09:13:30 +00:00 | Product Brief Phase 1 | none |
| S7 | Given a Runbook reviewed 89 whole days ago, when the Service List loads, then the state is "yellow". | R1.4 | dana.okafor | 2026-10-02 09:13:30 +00:00 | Product Brief Phase 1 | none |
| S8 | Given a Runbook reviewed exactly 90 whole days ago, when the Service List loads, then the state is "red". | R1.5 | dana.okafor | 2026-10-02 09:14:30 +00:00 | Product Brief Phase 1 | none |
```

The scenarios for R1.1, R1.2, R1.6, and the rest follow, 21 in all, and R2 (sessions) and R3
(signals) follow in the same form. The open question "where does yellow start?" is answered while
writing: the final 15 days of the interval, so 75 to 89 days (R1.4). The scenarios make that
decision visible to the person approving it: S5 says 74 days is green, S6 says 75 is yellow, S7
says 89 is yellow, and S8 says exactly 90 days is red, per "every 90 days." Each number in a
requirement has a scenario on it and one beside it.

Closing the phase, the agent gets the time from the shell, appends a `proposed` line for each of the
nine rows, walks the check list, and presents:

```
{"ts":"2026-10-02 09:10:00 +00:00","entry":"R1.1","action":"proposed","by":"dana.okafor"}
{"ts":"2026-10-02 09:11:00 +00:00","entry":"R1.2","action":"proposed","by":"dana.okafor"}
```

The check list shows the nine requirements have no design row, task, or test yet, which is
expected this early. The summary names the one decision the reader may want to change: the 15-day
yellow window. Dana replies "yellow from 75 days is right, approved," so the agent appends an
`approved` line per row with her name and mode `manual`, and starts Phase 2 without waiting for
anything else:

```
{"ts":"2026-10-02 10:00:00 +00:00","entry":"R1.1","action":"approved","by":"dana.okafor","mode":"manual"}
```

## Phase 2: Design, `design.md`

```markdown
## Components and interfaces
| ID | Element | Responsibility and contract | Requirements | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|---|---|
| D1 | `services` and `runbooks` tables | Hold Service and Runbook metadata. Schema in Data model | R1.1 | claude-sonnet-5-5 | 2026-10-02 10:20:00 +00:00 | none | none |
| D2 | `computeFreshness(service, runbook, now)` | Map dates to one of four states. Returns `"green" \| "yellow" \| "red" \| "missing"` | R1.2, R1.3, R1.4, R1.5 | claude-sonnet-5-5 | 2026-10-02 10:21:00 +00:00 | none | none |
| D3 | `GET /v1/services` | Return each Service with its computed state. Versioned under `/v1/`, behind the existing auth middleware | R1.1, R2.1 | claude-sonnet-5-5 | 2026-10-02 10:22:00 +00:00 | none | none |
| D4 | Service List screen | Render one indicator per Service with a text label. Consumes `GET /v1/services` | R1.1, R1.6 | claude-sonnet-5-5 | 2026-10-02 10:23:00 +00:00 | none | none |
| D5 | List-handler telemetry | Emit the log line and the gauge. Fields per `eng-os-observability` | R3.1, R3.2 | claude-sonnet-5-5 | 2026-10-02 10:24:00 +00:00 | none | none |
```

The Overview says freshness is computed at read time by a pure function. Considered and rejected: a
nightly job that stores the state in a column. A stored state is stale between runs, which defeats
a tool about staleness, and adds a job to operate. No ADR: computing at read time is local and
cheap to reverse, so the rejected alternative is recorded in this file only. Architecture impact
says none. The Test strategy maps every scenario to a layer from `eng-os-testing-strategy`:

```markdown
## Test strategy
| Layer | Scope | Scenarios | Requirements |
|---|---|---|---|
| Unit | `computeFreshness`, no I/O | S3, S4, S5, S6, S7, S8, S9 | R1.2, R1.3, R1.4, R1.5 |
| Unit | Service List component, endpoint mocked | S10 | R1.6 |
| Integration | The endpoint with the database | S1, S17, S18, S19, S20, S21 | R1.1, R2.1, R3.1, R3.2 |
| Integration | End to end, seeded database to the screen | S2 | R1.1, R1.6 |
```

There is no separate end-to-end layer: Integration covers end-to-end behavior. Each test in the code
will be named for its scenario, for example `S8 exactly 90 days is red`.

The agent appends `proposed` lines for D1 to D5 and walks the check list. Every requirement now has
scenarios, a design row, and a place in the Test strategy, and none has a task yet. Dana approves
the design, which the agent records, and Phase 3 starts.

## Phase 3: Tasks, `tasks.md`

First draft of T4's Definition of Done read "renders four distinct indicators using design-system
tokens." Walking the check list then turned up, at items 5 and 9: **R1.6 and its scenario S10
appeared in no task.** Color alone would have satisfied the draft Definition of Done and shipped an
indicator that fails the requirement's text-label rule. The fix added R1.6 and S10 to T4 and changed
its Definition of Done to require the component test for the listed scenarios.

```markdown
| ID | Task | Depends on | Requirements | Design | Scenarios | Checkpoints | Definition of Done | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | `services` and `runbooks` tables | none | R1.1, R1.2 | D1 | none | eng-os-database-design | Migration creates both tables with a nullable FK from `runbooks.service_id`; a paired `down` migration drops them cleanly | claude-sonnet-5-5 | 2026-10-02 11:10:00 +00:00 | none | none |
| T2 | Freshness computation function | T1 | R1.2, R1.3, R1.4, R1.5 | D2 | S3, S4, S5, S6, S7, S8, S9 | eng-os-coding-standards-nodejs | `computeFreshness` returns the four states; unit tests for the listed scenarios pass | claude-sonnet-5-5 | 2026-10-02 11:11:00 +00:00 | none | none |
```

T1 has no testable behavior, so it lists `none` and its Definition of Done names another check. T3
(endpoint), T4 (screen), and T5 (signals) follow, each listing the scenarios its tests prove. S2, the
end-to-end scenario from the seeded database to the screen, can only pass once the screen exists, so
it is listed on T4, the last task it needs. Order: T1, T2, T3, T5, T4. T4 and T5 both depend only on
T3, so T5 goes first and observability is not left until the UI works.

Closing the phase, the agent appends the `proposed` lines and walks the check list, which now turns
up nothing. The summary names the failure and the fix. Dana approves, and the agent hands off to
`eng-os-execute-feature`.

## What the events hold

Nothing above was typed into a status field. `events.jsonl` has one line per action:

```
{"ts":"2026-10-02 10:00:00 +00:00","entry":"R1.1","action":"approved","by":"dana.okafor","mode":"manual"}
{"ts":"2026-10-02 11:00:00 +00:00","entry":"D1","action":"approved","by":"dana.okafor","mode":"manual"}
{"ts":"2026-10-03 09:00:00 +00:00","entry":"T1","action":"started","by":"claude-sonnet-5-5"}
{"ts":"2026-10-03 10:45:00 +00:00","entry":"T1","action":"done","by":"claude-sonnet-5-5"}
```

Reading the log gives each entry's status: R1.1 and D1 are `approved`, and T1 is `done`. T1 being
done freezes T1, D1, and R1.1, and R1.2 as well, since T1 cites it, along with the scenarios of
those requirements.

## Later: a bug, then a change

On 2026-11-04 a Service whose Runbook has a future `last_reviewed_at` (a clock-skewed import) shows
a negative age, and no requirement says what state that is. T2 is done, so R1.2 to R1.5 and D2 are
frozen. The new behavior is a new requirement with its own scenarios, and the design and task that
build it are new rows that amend the ones they replace:

- R1.7 (author dana.okafor): IF a Runbook's last-reviewed date is in the future THEN THE SYSTEM
  SHALL treat its age as 0 days and show the state "green". Its scenarios S11 (30 days ahead) and
  S12 (tomorrow) cover the unwanted path.
- D6, with `Reference` "Amends D2", which lists R1.2, R1.5, and R1.7.
- T6, with `Reference` "Amends T2", which depends on T2 and lists R1.2, R1.5, and R1.7 and the
  scenarios for them, so the requirements and scenarios T2 covered are still covered.

On 2026-12-01 the yellow window changes to 70 days. R1.3 and R1.4 are frozen, so R1.9 amends R1.3 and
R1.8 amends R1.4, each with new scenarios: S13 (70 days, yellow), S14 (89 days, yellow), S15 (69
days, green), and S16 (0 days, green). The scenarios S4 to S7 stay as history. D6 and T6 have not
been built on yet, so they are edited in place instead of amended again: an `edited` line for D6 and
for T6, and a new approval for each. T6 now lists R1.8 and R1.9 and their scenarios as well. The old
rows stay as they were, and are superseded by the rows that amend them.

Reading the log and the tables after the change gives:

```
Progress      4 of 5 active tasks done, 1 started (T6)
Superseded    D2 by D6, R1.3 by R1.9, R1.4 by R1.8, T2 by T6
Awaiting      nothing
```

## What this shows

The undefined yellow threshold was found while writing requirements, and the scenarios put the exact
boundary in front of the person approving it, not found while testing T2. The check list caught an
uncovered requirement and scenario (R1.6 and S10) before any code existed to get it wrong. The design rejected
one alternative in writing and declined an ADR for it by applying the threshold. Approvals were
recorded and never held anything up. When behavior changed after work was done, the old rows stayed,
the new rows said what they replaced and who wrote them, and the amending task carried forward what
the old task covered.
