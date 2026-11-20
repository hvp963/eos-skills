# Architecture Decision Record: Living Specs as a Ledger and Event Log, C4 Architecture Views, and Documentation Sync

**Authors:** Haresh V. Parekh

---

## Metadata

| Field | Value |
|---|---|
| ADR Number | ADR-005 |
| Status | Accepted |
| Date | 2026-11-18 |
| Owner | Haresh V. Parekh |
| Supersedes | none |
| Note | Revised before any release. Earlier drafts (amend a requirement in place with a Revision number and Based-on pin on each file; then a ledger with row hashes and a validator in Python and Node) were never published and are described under Alternatives Considered. |

## Context

`eng-os-spec-feature` already writes `.specs/<feature>/requirements.md`, `design.md`, and
`tasks.md`, as AWS Kiro does. The owner reported that the spec files were not driving the work over
the life of an app. Reading the skills showed three gaps, none yet confirmed in a downstream project:

1. The only trigger was a new feature above the spec threshold. A later bug fix or behavior
   change had no checkpoint sending it back to the spec, so the spec froze at ship.
2. The CLAUDE.md template and `micro/project-structure.md` did not name `.specs/`, so a fresh
   session had no pointer to the files.
3. The audit check for specs ran only "if the project has `.specs/`", so a project that never
   created one passed.

Closing those gaps raised a design question: how should a spec change after work has started? A
first design amended requirements in place and kept a Revision number, an approver, and a pin to
the file above in each file's header. The owner rejected it. The requirements the owner set instead:

- Each requirement, design element, and task keeps its own author, created time, source, and
  reference, including the entry it amends, so lineage is per row and not per file.
- Content is an immutable ledger, and status is live tracking kept apart from it.
- Agents must be able to read status and act on it.
- Humans and agents are both authors and approvers, each under a unique name.
- Approval is recorded and never blocks work.
- The whole process runs without version control, hooks, or CI. The skills govern it.
- The OS stays skills only. No code ships with it, and adopting it needs nothing but the skills.
- Test scenarios are the most fundamental basis of validating a feature, so each one must trace to a
  requirement, a test layer, and a task, in columns like every other link.

A second design met the first requirements with a validator in Python and Node, row hashes, and a
derived status file. The owner rejected that too, because shipped scripts mean the OS is no longer
skills only and complicate adoption.

Separately, `eng-os-system-design` required C4 modeling to Context and Container level but gave
the model no place to live, and `eng-os-documentation-standards` had no notion of a document
being kept current against the code, apart from ADRs and release notes that are deliberately frozen.
The owner asked whether C4 belongs in an ADR or a separate skill, and whether documentation
belongs in an existing skill or a new one.

## Decision

1. **A shipped spec changes through its ledger.** A change that alters the behavior of a feature
   with a `.specs/` entry, a bug fix included, starts in the spec. A row can be edited until a task
   that cites it is done. After that the row is frozen, and a change is a new row with
   `Amends <ID>` in its Reference and a new task. Any edit to an approved row needs a new
   approval. A wording-only fix on a frozen row is an `editorial` event. An approved row is never deleted, only withdrawn. A change
   to built work therefore cascades: a new requirement, a design element that amends the old one,
   and a task that amends the old one. The trigger is a row in the `eng-os-core` checkpoint table
   and a section, Changing a Shipped Feature, in `eng-os-spec-feature`.
2. **The three spec files are ledgers.** Each is a table with one row per entry: ID, author,
   `Created (UTC)`, `Source` (where the row came from), and `Reference`, plus the columns of the
   table. A row that replaces an earlier one writes `Amends <ID>` in its Reference. Link columns
   are named for what they hold: `Requirements` wherever a row links to requirements (design,
   scenarios, tasks), and `Design`, `Scenarios`, and `Depends on` in tasks. IDs are never reused.
   Authors are unique names, registered in `.specs/config.json` as human or agent, so the tables
   have no Kind column. The markdown carries no status, revision, or approver, and tasks have no
   checkboxes.
3. **Scenarios are the basis of validating a feature.** Under each story's requirements is a table
   of scenarios (`S1`, `S2`, ...): one concrete example of behavior, written Given, when, then, with
   the values filled in, and a `Requirements` column naming what it validates. Every requirement has
   scenarios, and a number in a requirement has a scenario on it and one beside it. Scenarios have
   no events of their own: they follow their requirements, are approved with them, and are frozen
   with them, so a change after build is a new requirement with new scenarios. The design maps each
   scenario to a layer from `eng-os-testing-strategy`, a task's `Scenarios` column lists the
   scenarios its tests prove, and each test in the code is named for its scenario. The tests are
   part of the task. A scenario that passes only once several tasks are done is listed on the last
   of them.
4. **Status is live tracking in an append-only event log.** `events.jsonl` records who did what and
   when, one JSON object per line, and for an approval its mode. There is no second status file:
   an entry's status is its latest event. Status is one word, the name of the event that set it:
   `proposed`, `approved`, `edited`, `started`, `done`, `verified`, or `withdrawn`. An `edited`
   event withdraws an approval and leaves a task's work state alone. Whether a row is frozen or
   superseded, and the progress of the feature, are worked out when needed and never stored. Every
   timestamp is UTC, written `yyyy-mm-dd hh24:mi:ss +00:00`, and taken from the shell.
5. **Approval has a mode per file, and it never blocks work.** The mode is `manual` (default) or
   `auto`. In manual mode anyone may approve for now, a human may approve a row they authored, and
   an agent may not approve its own row. `auto` is a human's decision, recorded in an
   `auto_approval` block, and the agent then records the approval itself. At the end of each phase
   the agent presents a summary and what it assumed, then continues. An unapproved row is allowed,
   and the summary names what was built on one.
6. **The process is skills only.** No code ships. The agent appends events with its ordinary file
   tools, takes the time from a one-line shell command (bash and PowerShell forms are in the
   skill), and walks a check list after each phase and after any change. The formats and the check
   list are in `eng-os-spec-feature/references/spec-format.md`. Findings are reported in the
   summary and never block work.
7. **C4 views are files in `docs/architecture/`, owned by `eng-os-system-design`.** They are text
   diagrams (Mermaid C4 by default): `context.md`, `containers.md`, and `components-<container>.md`
   where internals matter. A boundary change updates them in the same PR. They are not part of an
   ADR; an ADR links to the view it changes. No new skill is added.
8. **Documentation extends `eng-os-documentation-standards`.** Documents are split into living
   (README, C4 views, contracts, runbooks: edited in place) and record (ADRs, release notes:
   frozen; specs: changed only through new ledger rows). Each fact has one home.
   `eng-os-execute-feature` gains Phase 7, a living-document sync run after feature verify. No new
   skill is added.
9. `.specs/`, `.specs/config.json`, and `docs/architecture/` are added to the project layout and
   the CLAUDE.md template, and the audit checks C16, C18, and the new C19 cover them.

## Consequences

### Accepted Trade-offs
- Nothing mechanical catches a missed event or an approved row edited without an `edited` line.
  The check list can only notice what the files show, and the log is only as complete as the
  agent's discipline. This is the same limit the rest of the OS already has.
- Without row hashes, a row that others were approved against can change with no flag on them. The
  rule is to look at the rows that cite a row when it changes, and to say so in the summary.
- Scenarios add rows to `requirements.md`, and they are approved with the requirements, so changing
  one before build is an `edited` line for each requirement it lists.
- A late change to built work costs new rows in all three files. That is the price of keeping the
  lineage.
- A reader of the markdown alone cannot see status. They read the log, where the latest event of an
  entry is its status.
- Work may proceed on unapproved rows. The summary names it and nothing prevents it.
- Names are self-declared. The registry classifies a name as human or agent and does not
  authenticate it. In `auto` mode nobody reviews the rows, and the risk rests with the human who
  allowed it.
- Every behavior change to a specced feature now costs a read of the spec first. This is
  the intended cost, paid before code instead of as rework after it.
- Mermaid C4 is experimental in renderers and has limited styling. It is chosen because it renders
  in the repository host and diffs in review, and a project may declare another text format.
- Projects bootstrapped under 1.8.0 have no `.specs/config.json`, `docs/architecture/`, or Living
  Documents section and will fail the new audit rows until a task adds them.

### Doors Closed
- Status as checkboxes or a Status header in the spec markdown is no longer used.
- Hard approval gates that stop work would need a new ADR.
- C4 diagrams kept only as exported images are no longer acceptable.

### Benefits
- Every requirement, design element, and task has its own history: who wrote it, when, why, and
  what it replaced. A later reader does not need the version history to answer that.
- The behavior a person approves includes concrete values, boundaries included, and every test
  traces to a scenario, a requirement, and a task.
- Adopting the spec process needs nothing but the skills, so it works in any tool that loads them,
  with no runtime and nothing to install or keep in agreement.
- Agents read one short append-only file and act on it, and nothing depends on version control.
- The spec stays true after ship, and a new session finds it from CLAUDE.md.
- The system's shape is reviewable and current, and a boundary change cannot merge without it.
- The skill count stays at 28, and no new description competes for trigger attention.

---

## Alternatives Considered

### Alternative 1: C4 inside the ADR

**What it is:** each ADR carries the C4 diagram of the decision it records.

**Why rejected:** an accepted ADR is immutable, so its diagram goes stale the first time the system changes. The reader then has no current view and several historical ones.

### Alternative 2: A separate C4 skill and a separate documentation skill

**What it is:** `eng-os-architecture-views` and `eng-os-living-docs` as new skills.

**Why rejected:** the C4 rules already live in `eng-os-system-design` and the documentation rules in `eng-os-documentation-standards`. Splitting them leaves two skills describing one practice, and the checkpoint table gains rows that route to the wrong one.

### Alternative 3: Regenerate specs from code on demand

**What it is:** treat the spec as disposable and rebuild it from the code when needed.

**Why rejected:** requirements record intent, and intent is not recoverable from code. A regenerated spec would describe what the code does, including its bugs, as what it should do.

### Alternative 4: Kiro-style steering files (product, tech, structure)

**What it is:** three always-loaded files holding project-wide context.

**Why rejected:** CLAUDE.md already holds that content, through Platform Context, Active Skills, and Project Structure. A second place for it would drift.

### Alternative 5: Amend in place, with a Revision number and Based-on pin per file

**What it is:** a changed requirement is edited in the file, a dated line is added to a Revisions section, and design and tasks record which revision of the file above they were written against.

**Why rejected:** history of one requirement lived only in version control. A Revision number says a file changed, not which requirement or why, and a behind pin marks a whole file stale for a change to one row. The approver was a header and not a property of each row, and the design needed hard approval gates and version control to work.

### Alternative 6: Status written in the markdown

**What it is:** a Status header per file and checkboxes for tasks.

**Why rejected:** status changes constantly and nobody approves it. Writing it into the files edits approved content on every change and mixes the record of what was agreed with tracking. The owner wanted the ledger immutable and status live.

### Alternative 7: A derived status file beside the log

**What it is:** a `status.json` holding each entry's current status, rebuilt from the events.

**Why rejected:** without code to rebuild it, the agent would write two files by hand on every change, and they would drift apart. The latest event of an entry already is its status.

### Alternative 8: Row hashes to detect edits and stale approvals

**What it is:** each event records a hash of the row it concerns, and a mismatch shows an edit that no event recorded.

**Why rejected:** an agent cannot compute a SHA-256 reliably without running code. The rule is discipline instead: append an `edited` line when an approved row changes, and look at the rows that cite it.

### Alternative 9: Hard approval gates

**What it is:** each phase stops until a human says "approved".

**Why rejected:** the owner decided that status informs and never blocks work. Approval is requested and recorded, and the risk of building on an unapproved row is made visible and accepted.

### Alternative 10: A validator in code, in Python and Node

**What it is:** single-file scripts that record events, rebuild a status file, and run the checks, with the format defined once and proved by shared conformance cases so a Java or Go version could follow. It was built, tested against 60 cases, and fault-injected.

**Why rejected:** shipping code means the OS is no longer skills only. Full adoption would need a runtime, a tool whose agent cannot run code loses the status and the checks, and two implementations must be kept in agreement for as long as the OS lives. The owner chose the simpler design: plain files, a check list the agent walks, and the limits listed above.

### Alternative 11: Scenarios in the design only

**What it is:** requirements stay as EARS rows, and the scenarios live in the design's test strategy, as Kiro's correctness properties do.

**Why rejected:** scenarios are examples of behavior that a person should agree when approving the requirement, boundary values included. Kiro derives its properties from the EARS criteria with tooling, which the OS does not have.

### Alternative 12: A fourth ledger file, `tests.md`

**What it is:** scenarios and test cases in their own file, with their own rows and events.

**Why rejected:** one more ledger to keep in step with the other three, and the tests themselves already live in the code.

### Alternative 13: Separate test tasks, or scenarios with their own events

**What it is:** a task per group of tests, as Kiro's optional property-test tasks are, or an event line for every scenario.

**Why rejected:** a task is not done with its tests missing, so the tests belong to the task. Events per scenario would roughly triple the log, and an agent appends it by hand.

### Alternative 14: Enforcement through git hooks and CI

**What it is:** a pre-commit hook and a CI job check the spec files.

**Why rejected:** they make the process depend on version control, which the owner ruled out.

---

## Validation

Revisit if audits find frozen rows edited in more than one project, if events are routinely
missing from the log or rows lack a `proposed` line, if requirements ship without scenarios or
scenarios without a test named for them, if `auto` approvals lead to rework on rows no
human saw, or if `events.jsonl` is lost or edited by hand. Also revisit if `docs/architecture/`
views fail audit C18 in more than one project, or if the Phase 7 sync is reported as a rubber
stamp (every row "no change" with no reason).

## References

- `skills/eng-os-spec-feature/SKILL.md` Files, Recording What Happens, Changing a Shipped Feature
- `skills/eng-os-spec-feature/references/spec-format.md`, `references/spec-feature-templates.md`
- `skills/eng-os-testing-strategy/SKILL.md` Testing Rules and Test Layers
- `skills/eng-os-system-design/SKILL.md` Persisting the Model, `micro/templates/architecture-template.md`
- `skills/eng-os-documentation-standards/SKILL.md` Living Documents and Record Documents
- `skills/eng-os-execute-feature/SKILL.md` Phases 1 to 7
- `evidence/ledger.md` E-31 and E-32
- ADR-004
