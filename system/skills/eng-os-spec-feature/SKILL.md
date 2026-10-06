---
name: eng-os-spec-feature
description: "Use when a feature is approved in scope (a Product Brief phase from plan-app, or a standalone request on a bootstrapped project) and takes three or more tasks, adds or changes a contract or entity, has user-visible edge-case behavior, or has ambiguous scope. Writes `.specs/<feature>/requirements.md` (EARS acceptance criteria), `design.md`, and `tasks.md`, stopping at an explicit approval gate after each, then hands tasks.md to eng-os-execute-feature. Not for planning a whole new app (eng-os-plan-app) or for a one-task change."
sources:
  - meta/mental-model.md
  - meta/claude-code-usage.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Spec Feature

`eng-os-plan-app` ends at an approved Product Brief, which says what an app is. It does not say what
one feature must do in testable terms, how it will be built, or which tasks build it. Without
that, `eng-os-execute-feature` has a task list to run but nothing agreed to check it against, and
disagreements about behavior surface as rework after the code exists. This skill writes those
three agreed artifacts, in order, with a human approval between each.

It is not a replacement for `eng-os-plan-app` (whole app, before a CLAUDE.md exists), for
`eng-os-execute-feature` (running the tasks), or for `eng-os-core`'s checkpoint table (the
standards each task must meet). It stops once `tasks.md` is approved.

## Files

Specs live in the project repo, versioned with the code:

```
.specs/<feature-slug>/
  requirements.md   what the feature must do, as testable criteria
  design.md         how it will be built, mapped back to the requirements
  tasks.md          ordered vertical-slice tasks, each tracing to requirements
```

The slug is kebab-case and uses the project's Terminology Lock terms. Each file starts with a
`Status:` line (`Draft` or `Approved <date>`) so a later session can tell which gates passed.
Spec files stay current: a change approved during execution is written back into them.

## Phase 0 — Intake

1. Read the project's CLAUDE.md: Terminology Lock, Active Skills, Scale Targets, Message Area
   Codes. Read the approved Product Brief phase if one exists, and the existing code the feature
   touches.
2. Decide whether a spec is warranted. Write one when any of these holds: the feature will take
   three or more tasks; it adds or changes an API, event, schema, or entity; its user-visible
   behavior has edge cases (empty, boundary, failure); or scope is still ambiguous. Otherwise
   hand straight to `eng-os-execute-feature`. A spec for a one-task change is overhead.
3. Create `.specs/<feature-slug>/` and start Phase 1.

## Phase 1 — Requirements

Write `requirements.md`: a short statement of the problem and the source scope, then numbered
user stories (R1, R2, ...), each with acceptance criteria numbered under it (R1.1, R1.2, ...).

Write every criterion in EARS notation, so each one has a visible trigger and one response:

| Pattern | Template | Use for |
|---|---|---|
| Event-driven | WHEN `<event>` THE SYSTEM SHALL `<response>` | Behavior triggered by an action or input |
| State-driven | WHILE `<state>` THE SYSTEM SHALL `<response>` | Behavior that holds for the duration of a state |
| Unwanted behavior | IF `<condition>` THEN THE SYSTEM SHALL `<response>` | Errors, invalid input, failures, abuse |
| Optional feature | WHERE `<feature is present>` THE SYSTEM SHALL `<response>` | Behavior that exists only in some configurations |
| Ubiquitous | THE SYSTEM SHALL `<response>` | Always-true properties |

Criteria rules:

- One behavior per criterion. A criterion with "and" joining two responses is two criteria.
- Testable with a concrete value: "within 200 ms at p95," "returns 401," "shows the label
  `missing`." Never "fast," "user-friendly," or "handles errors gracefully."
- Cover the unwanted path for every input and every outbound dependency, as well as the happy path.
- Use locked terms exactly. A new term for an existing concept is a Terminology Lock violation.
- State behavior, not implementation. "THE SYSTEM SHALL store the date in a column" belongs in
  the design.

End the file with an **Out of scope** list (what a reader might assume is included but is not)
and **Open questions**. Every open question must be answered and moved into a criterion before
the gate; an unanswered question blocks approval.

**Gate 1.** Present the requirements and stop (see Approval Gates). Do not start the design.

## Phase 2 — Design

Write `design.md` against the approved requirements:

- **Overview**: the approach in a short paragraph, and why this approach over the main
  alternative considered.
- **Components and interfaces**: each new or changed component, its responsibility, and its
  contract. Contract detail follows `eng-os-api-design`; this file names the contract and
  links it rather than restating the standard.
- **Data model**: entities, fields that matter, relationships, per `eng-os-database-design` when
  a schema changes.
- **Error handling**: what each unwanted-behavior criterion does in the design, including the
  user-facing message code from the project's Message Area Codes where one is shown.
- **Test strategy**: which layers cover which criteria, per `eng-os-testing-strategy`.
- **Checkpoints**: the `eng-os-core` checkpoint-table skills this feature will cross, so tasks
  can name them. Flag any decision that meets the ADR threshold in
  `eng-os-documentation-standards`, and write that ADR before the gate.
- **Traceability**: a table mapping every requirement to the design element that satisfies it.

A requirement with no design element is a gap. A design element with no requirement is scope
creep: delete it or go back and add the requirement.

**Gate 2.** Present the design and stop.

## Phase 3 — Tasks

Write `tasks.md` as the ordered task list that `eng-os-execute-feature` runs. Use the task
fields and the vertical-slice rule defined in that skill's Phase 1, plus one added field:

- **Requirements**: the numbered criteria this task satisfies (e.g. R1.2, R2.1).

Each task is a checkbox line so progress is visible in the file. Order by dependency, and note
tasks that may run in parallel lanes. Copy the blank format from `references/spec-feature-templates.md`.

Before Gate 3, run the traceability check and fix every failure:

1. Every criterion appears in at least one task's Requirements field.
2. Every task lists at least one requirement. A task that serves none is scope creep.
3. Every task's Definition of Done is a check someone could run, and it exercises the criteria
   the task lists.

**Gate 3.** Present the task list with the traceability result and stop.

## Approval Gates

A gate is a hard stop.

- Present a short summary of the file, the decisions you made that the reader may want to
  change, and what happens next on approval. Then wait.
- Accept only an explicit approval ("approved," "yes, proceed"). Silence, a question, or
  feedback on part of the file is not approval; revise and present again.
- On approval, set the file's `Status:` to `Approved <date>`.
- A change to an earlier file reopens the later ones. If requirements change after the design
  is approved, re-check the design and tasks against the change and re-present them.

## Handoff

When all three files are approved, tell the user the spec is ready and invoke
`eng-os-execute-feature`, which adopts `tasks.md` in its Phase 1 instead of decomposing again.
During execution, any change to a requirement, the design, or a task goes back through the
relevant gate before work continues.

## Failure Modes

| Failure | What it looks like | Prevention |
|---|---|---|
| Rubber-stamped gate | The agent proceeds on "looks good" to a different question, or on no reply | Accept explicit approval only; set `Status:` on approval |
| Criteria that cannot fail | "The page loads quickly" | Concrete value in every criterion; the testable-with-a-value rule |
| Requirements written as implementation | "Use a Redis cache" in requirements.md | Behavior only in Phase 1; mechanisms go in the design |
| Design that restates the code | A component list with no reasoning or alternatives | The Overview names the alternative rejected and why |
| Untraceable tasks | A task that satisfies no criterion, or a criterion no task covers | The Phase 3 traceability check, run before Gate 3 |
| Spec drift | Code diverges, spec files stay frozen | Execution amends and re-approves the spec when work disproves it |
| Ceremony on small work | Three files for a copy fix | Phase 0 threshold; hand straight to `eng-os-execute-feature` |

## Definition of Done

Spec work is complete when: Phase 0 judged the feature warranted a spec; `requirements.md` has
EARS criteria with concrete values, an out-of-scope list, and no open questions; `design.md`
maps every requirement to a design element and names the checkpoint skills the feature crosses;
`tasks.md` passed the traceability check; all three files carry `Status: Approved <date>`
from an explicit approval; any ADR the design triggered exists; and `eng-os-prose-style` was
run on the three files.

For a worked example, with all three files for one feature and a traceability failure caught
and fixed, see `references/spec-feature-example.md`. Blank templates for the three files are in
`references/spec-feature-templates.md`.
