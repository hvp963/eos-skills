# Spec Format

The formats `eng-os-spec-feature` writes. Nothing here needs code: the agent reads and writes the
files with its ordinary file tools, and works out status by reading the event log.

## Layout

```
.specs/
  config.json                 project settings: identities, approval mode per file
  <feature-slug>/
    requirements.md           requirement and scenario ledgers, plus prose
    design.md                 ledger table, plus prose
    tasks.md                  ledger table
    events.jsonl              append-only: who did what and when
```

The markdown files hold content and carry no status, revision, or approver. `events.jsonl` is the
only place status is recorded.

## Ledger tables

The markdown files hold tables whose header row begins with `ID`. A header matches its table
exactly, with these columns in this order:

| Table | Columns |
|---|---|
| requirements (`requirements.md`, one per story) | ID, Requirement, Author, Created (UTC), Source, Reference |
| scenarios (`requirements.md`, one per story, under `### Scenarios for R<n>`) | ID, Scenario, Requirements, Author, Created (UTC), Source, Reference |
| design (`design.md`) | ID, Element, Responsibility and contract, Requirements, Author, Created (UTC), Source, Reference |
| tasks (`tasks.md`) | ID, Task, Depends on, Requirements, Design, Scenarios, Checkpoints, Definition of Done, Author, Created (UTC), Source, Reference |

- A table is its header row, a separator row (`|---|---|`), and the rows after it. Other tables in
  the same file (a Test strategy table, an Error handling table) are not ledgers.
- **IDs**: requirements `R<story>.<n>` (R1.1), design `D<n>`, tasks `T<n>`, scenarios `S<n>`. An ID
  is never reused, renumbered, or deleted once approved.
- **Link columns are named for what they hold.** `Requirements` holds requirement IDs, in the design,
  scenario, and tasks tables alike. `Design` holds design IDs, `Scenarios` holds scenario IDs, and
  `Depends on` holds task IDs. A cell holding several IDs is comma separated, and `none` means none.
- **`Source`** is free text saying where the row came from: a Product Brief phase, a bug, a change
  request.
- **`Reference`** names existing rows this row refers to: `Amends <ID>` (for example `Amends R1.4`)
  when it replaces an earlier row of the same table, the bare ID when it only relates to another
  row, and `none` when it has no link. The checks read the `Amends` form, and nothing else, to find
  what is superseded.
- A literal pipe inside a cell is written `\|`.
- `Author` is a name from `identities` in the config.
- Every requirement is one EARS sentence: it starts with WHEN, WHILE, IF, WHERE, or THE SYSTEM and
  contains SHALL.
- Every scenario is one concrete example of behavior, written Given, when, then, with the values
  filled in. One scenario can list several requirements.
- A task's tests are part of the task. Its Definition of Done says the tests for the listed
  scenarios pass. A task with no testable behavior, such as a schema migration, lists `none` and
  names another check.

## Timestamps

Every timestamp is UTC with the offset written out: `yyyy-mm-dd hh24:mi:ss +00:00`, for example
`2026-12-01 10:05:00 +00:00`. Get the current time from the shell. Never type one from memory.

```
bash, zsh:    date -u +"%Y-%m-%d %H:%M:%S +00:00"
PowerShell:   [DateTime]::UtcNow.ToString("yyyy-MM-dd HH:mm:ss") + " +00:00"
```

## config.json

```json
{
  "identities": { "dana.okafor": "human", "claude-sonnet-5-5": "agent" },
  "approval": { "requirements": "manual", "design": "manual", "tasks": "manual" },
  "auto_approval": { "allowed_by": "dana.okafor", "allowed_on": "2026-12-01 10:00:00 +00:00" }
}
```

- `identities` maps every author and every actor to `human` or `agent`.
- `approval` is `manual` (default) or `auto` for each of requirements, design, and tasks.
- `auto_approval` is present only when a file is `auto`. It names the human who allowed it.

## events.jsonl

One JSON object per line, appended and never edited or removed. Keys, in this order: `ts`,
`entry`, `action`, `by`, and for an approval `mode`.

```
{"ts":"2026-12-01 09:00:00 +00:00","entry":"R1.8","action":"proposed","by":"sam.lee"}
{"ts":"2026-12-01 09:30:00 +00:00","entry":"R1.8","action":"approved","by":"dana.okafor","mode":"manual"}
{"ts":"2026-12-02 08:15:00 +00:00","entry":"T6","action":"started","by":"claude-sonnet-5-5"}
```

| Action | Append it when |
|---|---|
| `proposed` | a requirement, design, or task row is added. Every such row gets one, first |
| `approved` | someone approves a row. Add `"mode":"manual"` or `"mode":"auto"` |
| `edited` | an approved row's content changes. This withdraws its approval |
| `editorial` | a wording-only fix is made to a frozen row. It keeps the approval |
| `started` | work on a task begins |
| `done` | work on a task is finished |
| `verified` | a requirement or design row is confirmed against the shipped behavior |
| `withdrawn` | a row is dropped. The row stays in its ledger |

One line per entry per action. To act on several rows, append several lines. `by` is a name from
`identities`. Append the lines in time order, in one write, and never rewrite earlier lines.

**Scenarios have no events.** A scenario follows the requirements it lists. Adding, editing, or
removing a scenario of an approved requirement is an `edited` line for that requirement, and the
requirement needs approving again.

## Reading status

Status is not stored anywhere else. Work it out from the log.

- **Status**: the action of an entry's latest event, ignoring `editorial`. An entry with no event
  has not been registered: append its `proposed` line and treat it as `proposed`.
- **Work state of a task**: `done` if it has a `done` event, `started` if it has a `started` event
  and no `done`. Later `edited` and `approved` events change its approval, not its work state.
- **Approval state of an entry**: the latest of its `proposed`, `approved`, `edited`, and
  `withdrawn` events. A started task can be `edited` and need approving again. Its status word is
  then `edited` or `started`, whichever event came last, and its approval state is `edited`.

| Status | Applies to | Meaning |
|---|---|---|
| `proposed` | all | Added and not yet approved. Edits before the first approval need no event |
| `approved` | all | Approved |
| `edited` | all | Changed since it was approved, so it needs approving again |
| `started` | tasks | Work has begun |
| `done` | tasks | Work is finished |
| `verified` | requirements, design | Confirmed against the shipped behavior |
| `withdrawn` | all | Dropped |

No other value is valid. These are worked out when needed and never written down:

- **frozen**: a task is frozen when it has a `done` event. A requirement or design row is frozen
  when any task that cites it is. A scenario is frozen when any requirement it lists is. A frozen
  row is never edited.
- **superseded**: a row is superseded when a row that amends it (its Reference says `Amends <ID>`)
  has been approved.
- **active**: not superseded and not `withdrawn`. A scenario is active when at least one requirement
  it lists is. Superseded rows are history, and the checks ignore them.
- **progress**: of the active tasks, how many are done, how many started, and how many have not
  started.
- **reviewed by a human**: the row's latest `approved` event has mode `manual` and `by` is
  registered as `human`.

## Amending

A row is edited in place until a task that cites it is done. After that, a change is a new row
with `Amends <ID>` in its Reference naming the row it replaces, and a new task. A new requirement
brings its own scenarios, and the scenarios of the requirement it replaces stay as history. The
amending row carries forward every still-active link of the row it replaces, so coverage does not
disappear with the old row. An approved row is never deleted: a `withdrawn` event keeps it. A
wording-only fix on a frozen row is an `editorial` event.

When you edit a row, look at the rows that cite it. If one no longer holds, edit it too and append
its `edited` line. Rows you leave alone are still correct, and you say so in the summary.

## Test strategy

The design's `## Test strategy` section is a table that maps scenarios to the test layers:

| Layer | Scope | Scenarios | Requirements |
|---|---|---|---|
| Unit | `computeFreshness`, no I/O | S3, S8, S9 | R1.2, R1.5 |
| Integration | The endpoint with the database | S1, S17 | R1.1, R2.1 |

Layers are the ones in `eng-os-testing-strategy`: Unit, Integration, Contract, Property/Behavioral,
AI Evaluation, and Load/Soak. Integration already covers end-to-end behavior, so there is no
separate end-to-end layer. Each test in the code is named for the scenario it proves, for example
`S8 exactly 90 days is red`.

## Checking the spec

Walk this list after each phase and after any change to the spec. Each item names what to look
for. Report what you find in the phase summary and fix it, or explain it. A finding never blocks
work.

1. **Tables.** Every header matches its table exactly. IDs are well formed and unique. Every row has
   every cell, and `Created (UTC)` is a full timestamp.
2. **Events.** Every requirement, design, and task row has a `proposed` line first. No line names an
   ID that is not one of those rows. Every author and actor is in `identities`. Timestamps do not
   go backwards.
3. **Links.** Every ID in a `Requirements`, `Design`, `Scenarios`, or `Depends on` cell is a row of
   the right kind. An `Amends <ID>` in a Reference names an earlier row of the same table, never the
   row itself.
4. **EARS.** Every active requirement is an EARS sentence with SHALL.
5. **Traceability**, over active rows only:
   - every requirement has a design row that lists it, a task that lists it, and a mention in the
     design's Test strategy section;
   - every design row lists an active requirement and has a task that builds it, and the tasks that
     build it together list every requirement it lists;
   - every task lists a requirement and a design row, and each design row it lists lists at least
     one requirement the task lists.
6. **Frozen and superseded rows.** No frozen row has an `edited` line after the `done` line of a
   task that cites it. No active row that is not frozen cites a superseded row.
7. **Approvals.** List every task that has started, or is done, while its approval state, or that of
   a row it cites, is `proposed` or `edited`. Every approval fits the config: `auto` only for a file
   set to `auto`, and no agent approving a row it authored in `manual` mode.
8. **Tasks.** A done task's dependencies are done. A `verified` row's tasks are done. A withdrawn row
   with a done task has a later task that removes the behavior.
9. **Scenarios.**
   - Every active requirement has at least one scenario that lists it.
   - A number in a requirement (a threshold or a limit) has a scenario on it or beside it.
   - Every active scenario is named in the Test strategy, and the Test strategy names no scenario
     that does not exist.
   - Every active scenario is in the `Scenarios` cell of an active task, and a task that lists a
     scenario lists every requirement the scenario lists.
   - Tests in the code are named for their scenarios. The files cannot show this, so it is checked
     when a task is verified and in the audit.
