# Spec Feature Templates

Blank starting points for what `eng-os-spec-feature` writes under `.specs/`. Text in `<angle
brackets>` is replaced. Text after `Guidance:` is instruction to the author and is deleted from the
finished file. The column names must match exactly. The full rules are in `spec-format.md`.

## .specs/config.json

Created once per project. Ask the user for the handle they want recorded, and use your own name,
such as the model id, for the agent. Set `auto` only when a human has asked for it, and then add
the `auto_approval` block.

```json
{
  "identities": {
    "<person-handle>": "human",
    "<agent-name>": "agent"
  },
  "approval": {
    "requirements": "manual",
    "design": "manual",
    "tasks": "manual"
  }
}
```

## events.jsonl

Start with an empty file. Append one line per event and never edit an earlier line. The time comes
from the shell, with the commands in `spec-format.md` under Timestamps.

```
{"ts":"<time>","entry":"<ID>","action":"proposed","by":"<author>"}
{"ts":"<time>","entry":"<ID>","action":"approved","by":"<approver>","mode":"manual"}
{"ts":"<time>","entry":"<ID>","action":"edited","by":"<name>"}
{"ts":"<time>","entry":"<ID>","action":"editorial","by":"<name>"}
{"ts":"<time>","entry":"<task ID>","action":"started","by":"<name>"}
{"ts":"<time>","entry":"<task ID>","action":"done","by":"<name>"}
{"ts":"<time>","entry":"<ID>","action":"verified","by":"<name>"}
{"ts":"<time>","entry":"<ID>","action":"withdrawn","by":"<name>"}
```

Guidance: use `"mode":"auto"` only for a file a human has set to `auto`. Requirement, design, and
task rows get events. Scenarios do not: a change to one is an `edited` line for the requirements it
lists.

## requirements.md

```markdown
# Requirements: <Feature name, in Terminology Lock terms>

Status and approvals: events.jsonl

## Problem
<Two to four sentences: who has the problem, what happens today, why it matters.>

## R1 <User story: As a <role>, I want <capability>, so that <outcome>>
| ID | Requirement | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|
| R1.1 | WHEN <event> THE SYSTEM SHALL <response with a concrete value> | <name> | <yyyy-mm-dd hh24:mi:ss +00:00> | <source> | none |
| R1.2 | IF <unwanted condition> THEN THE SYSTEM SHALL <response> | <name> | <yyyy-mm-dd hh24:mi:ss +00:00> | <source> | none |

### Scenarios for R1
| ID | Scenario | Requirements | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|---|
| S1 | Given <state with values>, when <action>, then <result with values>. | R1.1 | <name> | <yyyy-mm-dd hh24:mi:ss +00:00> | <source> | none |
| S2 | Given <state beside the boundary>, when <action>, then <result>. | R1.1, R1.2 | <name> | <yyyy-mm-dd hh24:mi:ss +00:00> | <source> | none |

Guidance: one story per user goal, one requirements table and one scenarios table per story. Every
input and every outbound dependency gets at least one IF/THEN requirement. One behavior per
requirement. No mechanism words (table, cache, queue, class). Every requirement has at least one
scenario. A number in a requirement has a scenario on it and one beside it. A scenario can list
several requirements, and its IDs run S1, S2, ... across the whole file. `Source` is the Product
Brief phase, a bug, or a change request. `Reference` is `none`, or `Amends <ID>` for a row that
replaces an earlier one.

## Out of scope
- <Something a reader might assume is included, and the phase or decision that excludes it>

## Open questions
- <Question> and its answer, with the requirement it became, or "blocking"

Guidance: every question is resolved before the phase closes. Delete this section only when it is
empty.
```

## design.md

```markdown
# Design: <Feature name>

Status and approvals: events.jsonl

## Overview
<The approach in one paragraph. Name the main alternative considered and why it was not chosen.>

## Components and interfaces
| ID | Element | Responsibility and contract | Requirements | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|---|---|
| D1 | <name> | <one responsibility, and the signature, route, or event, linked to its contract doc> | <R1.1, R1.2> | <name> | <yyyy-mm-dd hh24:mi:ss +00:00> | <source> | none |

Guidance: an ID is never reused or renumbered. Every requirement is listed by at least one row.
A row that lists no requirement is scope creep.

## Data model
<Entities, fields that matter, relationships. Omit when no schema changes.>

## Architecture impact
<The `docs/architecture/` views this feature adds to or changes (new container, external dependency,
trust boundary), or "none." Name the change; the diagram is updated in the PR.>

## Error handling
| Requirement | Behavior in this design | User-facing message code |
|---|---|---|
| R1.2 | <what the component does> | <code from Message Area Codes, or "none shown"> |

## Test strategy
| Layer | Scope | Scenarios | Requirements |
|---|---|---|---|
| <Unit / Integration / Contract / ...> | <what the tests exercise, and what is mocked> | <S1, S2> | <R1.1, R1.2> |

Guidance: use the layers in `eng-os-testing-strategy`. There is no separate end-to-end layer:
Integration covers end-to-end behavior. Name every scenario and every requirement. The check list
flags one that this section never names. Each test in the code is named for its scenario, for
example `S8 exactly 90 days is red`.

## Checkpoints
<The eng-os-core checkpoint-table skills this feature crosses. Name any decision that meets the
ADR threshold and the ADR that records it.>
```

## tasks.md

```markdown
# Tasks: <Feature name>

Status and approvals: events.jsonl

| ID | Task | Depends on | Requirements | Design | Scenarios | Checkpoints | Definition of Done | Author | Created (UTC) | Source | Reference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | <one thing this task does> | none | <R1.1, R1.2> | <D1> | <S1, S2> | <eng-os-* skills this task will invoke> | <an observable check: the tests for the listed scenarios pass, a migration reverses cleanly> | <name> | <yyyy-mm-dd hh24:mi:ss +00:00> | <source> | none |

Order: <T1, T2, ...>. <Note which tasks may run in parallel lanes.>

Guidance: slice vertically, so each task is demoable and revertible alone. A task name that needs
"and" is probably two tasks. The tests are part of the task: the Definition of Done says the tests
for the listed scenarios pass. A task with no testable behavior lists `none` under Scenarios and
names another check. The tasks that build a design row together list every requirement it lists,
and a task that lists a scenario lists every requirement the scenario lists. There are no checkboxes:
progress is an event.
```
