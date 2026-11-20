---
name: eng-os-execute-feature
description: "Use once scope is approved and before implementation starts: either the `.specs/<feature>/tasks.md` ledger from eng-os-spec-feature, or a small feature request on an already-bootstrapped project that needs no spec. Adopts the spec's task list when one exists, otherwise breaks the scope into an ordered task list, each task with its own Definition of Done and commit, and requires a pass/fail verify gate before the next task starts. Governs the sequencing of a build; eng-os-core's checkpoint table governs what standard each task must meet while it runs."
sources:
  - meta/mental-model.md
  - meta/claude-code-usage.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Execute Feature

The Engineering OS's checkpoint table (`eng-os-core`) governs standards compliance while a task
is being implemented; it never governed how a multi-step feature gets broken into tasks in the
first place, or what happens between one task finishing and the next one starting. An agent was
free to build a whole feature in one giant pass or twelve small ones, with nothing in
`meta`/`macro`/`meso`/`micro` expressing an opinion. This skill closes that gap: it owns the loop
around the checkpoint table, not a replacement for it.

Do not use this for the initial planning of a whole new app; that's `eng-os-plan-app`, which produces
the Product Brief. Do not use it to decide what a feature must do or how it is designed; that's
`eng-os-spec-feature`, which produces the requirements, design, and `tasks.md` this skill runs.
Use this once scope for one feature (a full Product Brief phase, or a single feature request on a
project that already has a CLAUDE.md) is approved and before the first line of implementation
code is written.

## Phase 1 — Decompose

**If the change alters behavior of a shipped feature that has a `.specs/<feature>/` entry**, stop
and run `eng-os-spec-feature` Changing a Shipped Feature first. The task list follows the changed
requirements.

**If a spec exists** (`.specs/<feature>/` with its three ledgers), adopt its task list instead of
decomposing again. First read the event log and walk the check list in `eng-os-spec-feature`. A
table that cannot be read goes back to `eng-os-spec-feature` to fix. Findings are reported, not
blockers: note any row still awaiting approval, and any task that would start on one, in your plan,
and carry on. Then check that every task has the seven fields below
(Requirements, Design, and Scenarios are the spec's added fields), that no dependency points at a
later task,
and that every Definition of Done is observable. Send a gap back to `eng-os-spec-feature` to fix in
the ledgers. Then go to Phase 2.

**If no spec exists**, produce an ordered task list from the approved scope. Each task must be
small enough to implement, verify, and commit in one pass; if a task description needs "and" to
describe what it does, it is probably two tasks. For each task, capture:

- **Name**: a short, specific description of the one thing this task does
- **Depends on**: which earlier tasks (by name) must be complete first; tasks with no
  dependency on each other may be reordered freely, but do not hide a real dependency by skipping
  this field
- **Checkpoints it will hit**: name the specific `eng-os-core` checkpoint-table skills this task
  is expected to invoke (e.g. a new endpoint task names `eng-os-api-design`, `eng-os-security-practices`,
  `eng-os-testing-strategy`; a schema-only task names `eng-os-database-design`). This is decided at
  decomposition time, not discovered mid-task, so the task's scope is bounded before work starts.
- **Definition of Done**: the specific, observable condition that makes this one task complete.
  Not "it works"; a concrete check: a specific test passes, a specific endpoint returns a
  specific status code, a specific migration is reversible.
- **Requirements** (spec only): the numbered requirements this task builds.
- **Design** (spec only): the design element IDs this task builds.
- **Scenarios** (spec only): the scenario IDs whose tests this task writes and makes pass, or
  `none` for a task with no testable behavior, such as a schema migration. A task list built
  without a spec leaves these three fields out.

The tests are part of the task, never separate test tasks, so a task's Definition of Done says the
tests for its listed scenarios pass.

Do not decompose by layer (e.g. "write all the models," then "write all the endpoints," then
"write all the tests"); decompose by vertical slice, so each task is independently demoable and
independently revertible. A task that touches a model, its endpoint, and its test together is
preferred over three tasks that each leave the system in a non-functional state until all three
land.

## Phase 2 — Sequence

Order the task list by dependency, not by convenience. A task with no unmet dependency is
eligible to run next; among eligible tasks, prefer the one that most reduces risk or ambiguity
for the tasks behind it (e.g. the schema task before the endpoint task that reads it). Present
the ordered list back for confirmation before executing the first task: this is a cheap point to
catch a wrong decomposition, before any code exists to reflect it. An adopted spec's task list
was already approved at its own gate; confirm only the order and any change made since.

### Parallel Lanes

Tasks with no dependency on each other may run in parallel lanes (separate agents, worktrees, or
branches), which is the `eng-os-model-optimization` default for independent work. The rules do not
relax: each lane runs Phase 3 to 5 for its own task, each task still verifies before its own
commit, and a task that depends on a lane's output waits for that lane's Verify, not its start.
Merge order follows dependency order. Serial execution is the choice to justify ("task 4 reads
the schema task 2 creates"), not the default. Lanes record their own events, each appending its own
lines to `events.jsonl` and never rewriting an earlier one.

## Phase 3 — Execute One Task

For the current task only:

1. Implement it, invoking every `eng-os-core` checkpoint-table skill named for this task in
   Phase 1: this is where the checkpoint table itself does its work; this skill does not
   duplicate that table, it triggers it per task instead of leaving the triggering to chance.
   With a spec, record the start by appending a `started` line for the task, and read the task's
   requirements and listed scenarios in `requirements.md` and the design rows it builds in
   `design.md` first. Write each test named for its scenario (`S8 exactly 90 days is red`) as part
   of the task, at the layer the Test strategy gives it.
2. If the work shows the spec is wrong or incomplete, stop and change the spec as
   `eng-os-spec-feature` Changing a Shipped Feature describes: edit rows that are not frozen, add
   amending rows for frozen ones, and record the change. Then continue. Diverging from the spec in
   code while leaving the spec unchanged leaves the next task to build on a document that is no
   longer true.
3. Do not begin the next task's implementation before this task's Verify step (Phase 4) passes.
   Working ahead on a later task while an earlier one is unverified is the exact failure mode
   this skill exists to prevent: a later task built on an unverified earlier one compounds the
   rework when the earlier one turns out to be wrong.

## Phase 4 — Verify

Before a task is considered complete:

- Run the task's own Definition of Done condition from Phase 1 and confirm it actually passes,
  not "should pass."
- With a spec, confirm that every scenario the task lists has a test named for it and that the test
  passes, as well as the task's own Definition of Done, and walk the check list to see whether the
  task left anything out of step.
- Run the Meta Definition of Done from `eng-os-core`: for every checkpoint-table skill this task
  invoked, confirm that skill's own DoD checklist ran and passed.
- If verification fails, fix the current task before moving on. Do not proceed to the next task
  with a known-failing verify gate and plan to "come back to it": that is exactly how partial,
  half-working feature branches accumulate.

## Phase 5 — Commit

One commit per completed, verified task, not one commit for the whole feature, and not
multiple commits within a single task. This keeps `git bisect` meaningful (a bisect lands on one
task's change, not a tangle of several) and gives the task list a durable audit trail: task list
order should read as commit-log order when the feature is done. The commit message names the
task, not the whole feature. With a spec, append a `done` line for the task first, so the
commit holds the code together with the updated `events.jsonl`, and the log always shows which
tasks have landed.

Return to Phase 3 for the next eligible task. Repeat until the task list is exhausted.

## Phase 6 — Feature Verify

Once every task is complete, verify the feature as a whole, not just its parts: the vertical
slices compose correctly together, and the original approved scope (the Product Brief phase or
feature request that started this skill) is now satisfied; not just that every
individual task's narrow DoD passed in isolation. With a spec, run the tests for every active
scenario of the feature together, including the scenarios that span several tasks. Then walk every
active requirement in `requirements.md` and record each one whose scenarios all passed with a
`verified` line, naming the tests that proved it; a requirement with no passing scenario is a gap
to fix.

## Phase 7 — Sync Living Documents

A feature is not done while the documents that describe the system disagree with the code. After
Phase 6 passes, check each living document against what shipped, and update the ones that changed
in the same PR (the rule in `eng-os-documentation-standards`):

| Document | Update when the feature |
|---|---|
| README and onboarding steps | Changed how the project is installed, configured, run, or tested |
| `docs/architecture/` C4 views | Added, removed, or split a service, data store, queue, external dependency, or trust boundary (`eng-os-system-design` Persisting the Model) |
| API reference and `docs/contracts/` | Changed an endpoint, event, schema, or error code |
| Runbook | Added a failure mode, an alert, a dependency, or a recovery step |
| ADR | Made a decision meeting the threshold (new ADR; never edit an accepted one) |
| `.specs/<feature>/` | Phase 6 or a later change left a requirement, a design row, or a task out of step with the code (change the rows as `eng-os-spec-feature` describes, then walk the check list) |
| CHANGELOG or release notes | Changed anything a user or integrator can see |

Record the result as one line per row in the final commit or PR description: updated, or "no
change" with the reason. A row with neither is an unfinished task.

## When Not to Use the Full Loop

A single-file, single-concern change (a copy fix, a config value, a one-line bug fix with an
obvious cause) does not need a decomposed task list; Phase 1 through 6 for a one-line change is
overhead with no payoff. Use judgment: if the change is genuinely one task, treat that one task as
already decomposed and go straight to Phase 3. The bar is the same one `eng-os-bootstrap` uses for
its own bail-out check; do not force ceremony onto work that does not carry real multi-step risk.

## Definition of Done

Feature execution is complete when: every task from Phase 1 has a passing Definition of Done and
a corresponding commit; the Meta Definition of Done passed for every checkpoint-table skill any
task invoked; the Phase 6 feature-level verify passed against the original approved scope (with a
spec, every active scenario's test passed and every active requirement is recorded as verified); no task
was left in a partially-verified state when work stopped; with a spec, the log shows every active
task done, the check list turns up nothing unexplained, and no ledger disagrees with the code that
shipped; and the
Phase 7 living-document check ran, with each row updated or marked "no change" with a reason.

For a full worked example of this seven-phase loop applied to one concrete feature, see
`references/execute-feature-example.md`.
