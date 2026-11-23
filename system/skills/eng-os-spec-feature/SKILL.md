---
name: eng-os-spec-feature
description: "In a project governed by the Engineering OS, use when a feature is approved in scope (a Product Brief phase from plan-app, or a standalone request on a bootstrapped project) and takes three or more tasks, adds or changes a contract or entity, has user-visible edge-case behavior, or has ambiguous scope. Writes `.specs/<feature>/requirements.md` (EARS requirements with their scenarios), `design.md`, and `tasks.md` as ledgers with one row per entry, and records who did what in an append-only `events.jsonl`, with approval tracked and never blocking work. Also use it to change the spec before any later change alters the behavior of a feature that has a `.specs/` entry. Not for planning a whole new app (eng-os-plan-app) or for a one-task change to a feature that has no spec."
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
three artifacts, in order, and keeps them true after the feature ships.

It is not a replacement for `eng-os-plan-app` (whole app, before a CLAUDE.md exists), for
`eng-os-execute-feature` (running the tasks), or for `eng-os-core`'s checkpoint table (the
standards each task must meet). It stops once `tasks.md` is written and recorded.

## Files

Specs live in the project, next to the code:

```
.specs/
  config.json                 project settings: identities, approval mode per file
  <feature-slug>/
    requirements.md           what the feature must do, with the scenarios that prove it
    design.md                 how it will be built, and how it will be tested
    tasks.md                  ordered vertical-slice tasks
    events.jsonl              append-only: who did what and when
```

The slug is kebab-case and uses the project's Terminology Lock terms. The three markdown files are
ledgers: content only, no status, revision, or approver. Status lives in `events.jsonl`. There is
no code to run: you read and write these files with your ordinary file tools. The exact formats are
in `references/spec-format.md`, blank files are in `references/spec-feature-templates.md`, and a
worked example is in `references/spec-feature-example.md`.

## The Ledger

Each file holds tables with one row per entry. Every row has an ID, an author, a `Created (UTC)`
time, a `Source`, and a `Reference`, plus the columns of its table:

- **requirements.md**: `R1.1`, `R1.2`, and so on, grouped by user story (one table per story). The
  row is one EARS requirement. Under each story's requirements is a `### Scenarios` table: `S1`,
  `S2`, and so on, each one concrete example of behavior with its values filled in, and a
  `Requirements` column naming what it validates.
- **design.md**: `D1`, `D2`, and so on. The row is a component or interface, with a `Requirements`
  column naming the requirements it covers. Overview, Data model, Architecture impact, Error
  handling, Test strategy, and Checkpoints stay as prose sections, and the Test strategy is a
  table that maps scenarios to test layers.
- **tasks.md**: `T1`, `T2`, and so on. The row is a task with its dependencies, the `Requirements`,
  `Design`, and `Scenarios` it builds and proves, its checkpoints, and its Definition of Done.

Rules for every row:

- **IDs are never reused.** A row that is removed is withdrawn, not deleted.
- **Link columns are named for what they hold.** `Requirements` holds requirement IDs wherever it
  appears, and `Design`, `Scenarios`, and `Depends on` hold design, scenario, and task IDs.
- **Author is a unique name** from `identities` in `.specs/config.json`: a person or an agent.
  Whether it is a human or an agent is looked up there, so the tables carry no Kind column.
- **`Created (UTC)` is a full UTC timestamp**, `yyyy-mm-dd hh24:mi:ss +00:00`, taken from the shell
  (see Recording What Happens). Never type one from memory.
- **`Source` is free text**: the Product Brief phase, a bug, a change request.
- **`Reference` names existing rows this row refers to.** A row that replaces an earlier row of the
  same table writes `Amends R1.4` (or the ID it replaces). A row with no link writes `none`.

## Recording What Happens

Status is not written in the markdown. Each entry has one status word, the name of the event that
set it: `proposed`, `approved`, `edited`, `started`, `done`, `verified`, or `withdrawn`.

Record each event by appending one JSON line to the feature's `events.jsonl`:

```
{"ts":"2026-12-01 09:30:00 +00:00","entry":"R1.8","action":"approved","by":"dana.okafor","mode":"manual"}
{"ts":"2026-12-02 08:15:00 +00:00","entry":"T6","action":"started","by":"claude-sonnet-5-5"}
```

- Get the time from the shell, in bash `date -u +"%Y-%m-%d %H:%M:%S +00:00"` and in PowerShell
  `[DateTime]::UtcNow.ToString("yyyy-MM-dd HH:mm:ss") + " +00:00"`.
- Append only. Never edit or remove an earlier line. Several entries are several lines.
- Every requirement, design, and task row gets a `proposed` line when it is added. `by` is a name
  from `identities`. Scenarios have no events: they follow the requirements they list, so adding,
  editing, or removing a scenario of an approved requirement is an `edited` line for that
  requirement.
- An approval covers the row as it stood. Editing an approved row withdraws that approval: append
  `edited`, and it needs approving again. A wording-only fix on a frozen row is `editorial`, which
  keeps the approval.
- To see where something stands, read the log: the latest event of an entry is its status. Frozen,
  superseded, and progress are worked out when needed and never written down
  (`references/spec-format.md`, Reading status).

## Configuration

`.specs/config.json` is created at Phase 0 if it does not exist. It holds the registry of names and
the approval mode for each file:

- **identities** maps every author and approver to `human` or `agent`. Use your own name, such as the
  model id, for the agent. Ask the user once for the handle they want recorded.
- **approval** is `manual` or `auto` for requirements, design, and tasks. The default is `manual`.
  `auto` is a human's decision, recorded in an `auto_approval` block with who allowed it and when.
  Never set `auto` on your own.

## Phase 0: Intake

1. Read the project's CLAUDE.md: Terminology Lock, Active Skills, Scale Targets, Message Area
   Codes. Read the approved Product Brief phase if one exists, and the existing code the feature
   touches.
2. Decide whether a spec is warranted. Write one when any of these holds: the feature will take
   three or more tasks; it adds or changes an API, event, schema, or entity; its user-visible
   behavior has edge cases (empty, boundary, failure); or scope is still ambiguous. Otherwise
   hand straight to `eng-os-execute-feature`. A spec for a one-task change is overhead.
3. Create `.specs/<feature-slug>/` and the three files from the templates, an empty
   `events.jsonl`, and `.specs/config.json` if it is missing.

## Phase 1: Requirements

Write the problem statement, then the user stories (R1, R2, ...) as headings, each with a ledger
table of its requirements (R1.1, R1.2, ...) and, under it, a `### Scenarios` table (S1, S2, ...).
Write every requirement in EARS notation, so each one has a visible trigger and one response:

| Pattern | Template | Use for |
|---|---|---|
| Event-driven | WHEN `<event>` THE SYSTEM SHALL `<response>` | Behavior triggered by an action or input |
| State-driven | WHILE `<state>` THE SYSTEM SHALL `<response>` | Behavior that holds for the duration of a state |
| Unwanted behavior | IF `<condition>` THEN THE SYSTEM SHALL `<response>` | Errors, invalid input, failures, abuse |
| Optional feature | WHERE `<feature is present>` THE SYSTEM SHALL `<response>` | Behavior that exists only in some configurations |
| Ubiquitous | THE SYSTEM SHALL `<response>` | Always-true properties |

Requirement rules:

- One behavior per requirement. A requirement with "and" joining two responses is two requirements.
- Testable with a concrete value: "within 200 ms at p95," "returns 401," "shows the label
  `missing`." Never "fast," "user-friendly," or "handles errors gracefully."
- Cover the unwanted path for every input and every outbound dependency, as well as the happy path.
- Use locked terms exactly. A new term for an existing concept is a Terminology Lock violation.
- State behavior, not implementation. "THE SYSTEM SHALL store the date in a column" belongs in
  the design.

Scenarios are the basis of validating the feature. Each is one concrete example of a requirement,
written Given, when, then, with the values filled in, and its `Requirements` column names what it
validates:

- **Every requirement has at least one scenario**, covering the normal case, and for an IF/THEN
  requirement the unwanted path it describes.
- **A number in a requirement has a scenario on it and one beside it.** A requirement that says 75 to
  89 days gets scenarios at 75 and 89, and at 74 and 90 beside them, so the boundary is a decision
  a person agreed, not one the code chose.
- **One scenario can validate several requirements**, such as a flow from the database to the screen.
- **Scenarios are approved with their requirements.** They are part of what the person agrees.

End the file with an **Out of scope** list (what a reader might assume is included but is not)
and **Open questions**. Answer every open question and move it into a requirement before closing
the phase. Then close the phase (see Closing a Phase).

## Phase 2: Design

Write `design.md` against the requirements. The ledger table holds the components and interfaces,
and the prose sections hold the rest:

- **Overview**: the approach in a short paragraph, and why this approach over the main
  alternative considered.
- **Components and interfaces** (ledger): each new or changed component, its responsibility and
  contract, and the requirements it covers in its `Requirements` column. Contract detail follows
  `eng-os-api-design`; the row names the contract and links it.
- **Data model**: entities, fields that matter, relationships, per `eng-os-database-design` when
  a schema changes.
- **Architecture impact**: the `docs/architecture/` views this feature adds to or changes (a new
  container, external dependency, or trust boundary), or "none." The view is updated in the
  feature's PR, per `eng-os-system-design` Persisting the Model.
- **Error handling**: what each unwanted-behavior requirement does, including the user-facing
  message code from the project's Message Area Codes where one is shown.
- **Test strategy**: a table of `Layer | Scope | Scenarios | Requirements` that says which layer
  proves each scenario. Use the layers in `eng-os-testing-strategy` (Unit, Integration, Contract,
  and so on). Integration already covers end-to-end behavior, so there is no separate end-to-end
  layer. Name every scenario and every requirement. The check list flags one the section never names.
  Each test in the code will be named for its scenario, for example `S8 exactly 90 days is red`.
- **Checkpoints**: the `eng-os-core` checkpoint-table skills this feature will cross. Flag any
  decision that meets the ADR threshold in `eng-os-documentation-standards`, and write that ADR.

The `Requirements` column is the traceability from requirements to design. A requirement no design
row lists is a gap. A design row that lists no requirement is scope creep.

## Phase 3: Tasks

Write `tasks.md` as the ordered task list that `eng-os-execute-feature` runs. Use the task fields
and the vertical-slice rule defined in that skill's Phase 1. Each row also lists the requirements it
builds, the design elements it builds, and the scenarios its tests prove. Order by dependency, and
note tasks that may run in parallel lanes below the table.

A task that serves no requirement is scope creep. The tasks that build a design row together list
every requirement it lists. Every task's Definition of Done is a check someone could run.

- **The tests are part of the task.** They are not separate test tasks. The Definition of Done says
  the tests for the listed scenarios pass, and a task is not done with its tests missing.
- **Every scenario of an active requirement is in some task's `Scenarios`**, and a task that lists a
  scenario lists every requirement the scenario lists.
- **A task with no testable behavior**, such as a schema migration, lists `none` and its Definition
  of Done names another check.
- **A scenario that passes only once several tasks are done** is listed on the last of them. A
  project with several such scenarios adds a final task for them.

## Closing a Phase

At the end of each phase, in this order:

1. **Register the rows.** Append a `proposed` line for each new requirement, design, and task row.
2. **Check.** Walk the list in `references/spec-format.md`, Checking the spec, and fix what it
   turns up. State any finding that remains in the summary.
3. **Present a short summary**: what the file says, the decisions you made that the reader may want
   to change, what you assumed, and what happens next.
4. **Record approval according to the mode** (see Approval Tracking), then start the next phase.
   Do not wait for it.

## Approval Tracking

Approval is recorded, and it never blocks work. An unapproved row is allowed. The summary and the
check list say what was built on one.

- **manual** (default): a person approves when ready by telling you. Append an `approved` line with
  `"mode":"manual"` and the name they give. Never approve a row you authored yourself in manual
  mode.
- **auto**: where a human has set the file to `auto`, append an `approved` line with
  `"mode":"auto"` and your own name at the end of the phase.
- A row approved in `auto` mode, or by an agent, is not reviewed by a human. List those rows when
  asked where the spec stands.

A change to an approved row needs a new approval.

## Handoff

When the three ledgers are written, tell the user where the spec stands (read the log) and invoke
`eng-os-execute-feature`, which adopts `tasks.md` in its Phase 1 instead of decomposing again.
During execution, `eng-os-execute-feature` records each task as it starts and finishes.

## Changing a Shipped Feature

A spec does not end at ship. The ledgers are the record of what the feature does, so any later
change that alters that behavior starts there. This applies to a bug fix and to a one-task change
as well as to a new phase. A change that alters no behavior (a refactor, a performance fix within
the stated values) does not touch the spec.

Before changing code, list `.specs/` and find the entry for the feature the change touches. If
there is none, the feature either never met the Phase 0 threshold or predates the spec practice:
continue without one, unless this change now meets the threshold.

1. Read the rows the change touches, and the events behind them.
2. Classify the change:
   - **Behavior matches a requirement and the code is wrong** (a bug): no change to the spec. Add the
     failing case as a test named for the scenario it belongs to (or the requirement, if no scenario
     covers it), then fix the code.
   - **Behavior is undefined, or the requirement is wrong** (a gap or a change of mind): change the
     spec, as follows.
3. For each row the change touches, decide whether it is frozen: a task that cites it has a `done`
   event. A scenario is frozen when a requirement it lists is.
   - **Not frozen**: edit the row in place and append an `edited` line. Changing a scenario is an
     `edited` line for the requirements it lists. Look at the rows that cite it, and edit and mark
     those that no longer hold. Each edited row needs approving again.
   - **Frozen**: add a new row with the next ID and `Amends <ID>` in its Reference, naming the row
     it replaces. A new requirement brings its own scenarios, needs a design row that amends the
     design row it replaces, and a task that amends the task it replaces. The old scenarios stay as
     history. Never edit a frozen row. A wording-only fix is an `editorial` line.
4. A new row carries forward every still-active link of the row it replaces, so the requirements
   and scenarios the old task covered are still covered. Append a `proposed` line for each new
   requirement, design, and task row.
5. Walk the check list, present a summary, record approval according to the mode, and continue to
   `eng-os-execute-feature` without waiting.

A single behavior change that is one task is three short rows, one per file, not a new spec.

## Failure Modes

| Failure | What it looks like | Prevention |
|---|---|---|
| Status written into the markdown | A Status header, a checkbox, or "Approved" in a ledger file | Status lives in `events.jsonl`; append a line |
| Edited event log | An earlier line changed or removed, or a timestamp typed from memory | Append only; time from the shell |
| Missed event | A row edited, a task started, or an approval given, with no line | Append the line in the same step as the change; the check list notices a task that is done with no `started`, and a row with no `proposed` line |
| Edit to a frozen row | R1.4 reworded after its task shipped | `Amends <ID>`: a new row, a new design row, a new task |
| Requirements that cannot fail | "The page loads quickly" | Concrete value in every requirement; the testable-with-a-value rule |
| Requirement with no scenario | A requirement the tests can be written for in any way the author likes | Every requirement has scenarios, with the boundary values filled in |
| Boundary left to the code | "75 to 89 days" and no scenario at 74, 75, 89, or 90 | A number in a requirement has a scenario on it and one beside it |
| Tests not tied to scenarios | A test suite that passes while a scenario has no test | Each test is named for its scenario, and a task's Definition of Done lists the scenarios |
| Tests split from the task | A "write the tests" task done after the feature task | The tests are part of each task; a task is not done with its tests missing |
| Requirements written as implementation | "Use a Redis cache" in requirements.md | Behavior only in Phase 1; mechanisms go in the design |
| Design that restates the code | A component list with no reasoning or alternatives | The Overview names the alternative rejected and why |
| Untraceable rows | A task that lists no requirement, or a requirement or scenario no task covers | The check list, items 5 and 9 |
| An amending row drops coverage | The new task omits requirements the old task covered | Carry forward every still-active link of the row replaced |
| Approving your own row | An agent approves what it wrote, in manual mode | The check list, item 7; ask a person |
| Ceremony on small work | Three files for a copy fix | Phase 0 threshold; hand straight to `eng-os-execute-feature` |

## Definition of Done

Spec work is complete when: Phase 0 judged the feature warranted a spec; the three ledgers have
valid tables, with EARS requirements that carry concrete values, an out-of-scope list, and no open
questions; every requirement has scenarios (with the boundary values filled in), a design row, and
a task, every scenario is mapped to a layer in the Test strategy and listed by a task, and every
design row lists a requirement; every requirement, design, and task row has a `proposed` line and
an approval recorded according to the config, or is listed as awaiting approval; the check list was walked and each finding is fixed or
explained in the summary; any ADR the design triggered exists; any C4 view the design changes is
named in `design.md` and updated per `eng-os-system-design`; and `eng-os-prose-style` was run on
the three files. A change to a shipped feature is complete when it left new rows, not edited
frozen ones, and the check list was walked after it.

For a worked example, with the ledgers and scenarios for one feature, the events behind them, and a
later change, see `references/spec-feature-example.md`. Blank files and the config are in
`references/spec-feature-templates.md`. The formats and the check list are in
`references/spec-format.md`.
