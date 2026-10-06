# Spec Feature Templates

Blank starting points for the three files `eng-os-spec-feature` writes under
`.specs/<feature-slug>/`. Text in `<angle brackets>` is replaced; text after `Guidance:` is
instruction to the author and is deleted from the finished file.

## requirements.md

```markdown
# Requirements: <Feature name, in Terminology Lock terms>

Status: Draft
Source: <Product Brief phase, or the standalone request, in one line>

## Problem
<Two to four sentences: who has the problem, what happens today, why it matters.>

## R1 — <User story: As a <role>, I want <capability>, so that <outcome>>
- R1.1 WHEN <event> THE SYSTEM SHALL <response with a concrete value>
- R1.2 IF <unwanted condition> THEN THE SYSTEM SHALL <response>

Guidance: one story per user goal. Every input and every outbound dependency gets at least one
IF/THEN criterion. One behavior per criterion. No mechanism words (table, cache, queue, class).

## Out of scope
- <Something a reader might assume is included, and the phase or decision that excludes it>

## Open questions
- <Question> → <answer and the criterion it became, or "blocking">

Guidance: every question is resolved before Gate 1. Delete this section only when it is empty.
```

## design.md

```markdown
# Design: <Feature name>

Status: Draft
Requirements: requirements.md (Approved <date>)

## Overview
<The approach in one paragraph. Name the main alternative considered and why it was not chosen.>

## Components and interfaces
| Component | Responsibility | Contract |
|---|---|---|
| <name> | <one responsibility> | <signature, route, or event, linked to its contract doc> |

## Data model
<Entities, fields that matter, relationships. Omit when no schema changes.>

## Error handling
| Criterion | Behavior in this design | User-facing message code |
|---|---|---|
| R1.2 | <what the component does> | <code from Message Area Codes, or "none shown"> |

## Test strategy
| Layer | Covers |
|---|---|
| <unit / integration / contract / component> | <criterion ids> |

## Checkpoints
<The eng-os-core checkpoint-table skills this feature crosses. Name any decision that meets the
ADR threshold and the ADR that records it.>

## Traceability
| Requirement | Design element |
|---|---|
| R1.1 | <component or section> |

Guidance: every requirement appears in this table. A design element that appears in no row is
scope creep.
```

## tasks.md

```markdown
# Tasks: <Feature name>

Status: Draft
Requirements: requirements.md (Approved <date>)
Design: design.md (Approved <date>)

- [ ] **T1 — <one thing this task does>**
  - Depends on: none
  - Checkpoints: <eng-os-* skills this task will invoke>
  - Requirements: <R1.1, R1.2>
  - Definition of Done: <an observable check: a named test passes, an endpoint returns a
    specific status, a migration reverses cleanly>

## Traceability check
| Check | Result |
|---|---|
| Every criterion appears in a task | <pass, or the uncovered ids and the fix> |
| Every task lists a requirement | <pass, or the offending task and the fix> |
| Every Definition of Done is runnable | <pass, or the offending task and the fix> |

Guidance: slice vertically, so each task is demoable and revertible alone. A task name that
needs "and" is probably two tasks. Order by dependency; mark independent tasks as
parallel-eligible in a note under the list.
```
