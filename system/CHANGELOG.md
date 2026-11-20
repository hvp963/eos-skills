# Changelog

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

---

## [1.9.0] — 2026-11-19

### Added
- **Specs are ledgers with an event log.** `eng-os-spec-feature` now writes `requirements.md`, `design.md`, and `tasks.md` as tables with one row per entry: an ID, an author, a `Created (UTC)` time, a `Source`, and a `Reference` (`Amends <ID>` for a row that replaces an earlier one). Link columns are named for what they hold: `Requirements` in the design, scenario, and tasks tables, and `Design`, `Scenarios`, and `Depends on` in tasks. The markdown carries no status, revision, or approver, and tasks have no checkboxes. Status is one word (`proposed`, `approved`, `edited`, `started`, `done`, `verified`, `withdrawn`), the name of the event that set it, and lives in `events.jsonl`, which is append-only. An entry's status is its latest event, so there is no second status file. Frozen, superseded, and progress are worked out when needed and never stored. Every timestamp is UTC, `yyyy-mm-dd hh24:mi:ss +00:00`, taken from the shell.
- **A shipped spec changes through its ledger.** A row is edited until a task that cites it is done. After that, a change is a new row with `Amends`, a new design row, and a new task, which carry forward everything they replace. An edit to an approved row needs a new approval, a wording-only fix on a frozen row is an `editorial` event, and an approved row is withdrawn, never deleted. The trigger is an `eng-os-core` checkpoint row and the section Changing a Shipped Feature.
- **Scenarios are the basis of validating a feature.** Each story's requirements get a table of scenarios (`S1`, `S2`, ...): one concrete example of behavior, Given, when, then, with the values filled in, and a `Requirements` column. Every requirement has scenarios, and a number in a requirement has a scenario on it and one beside it. They have no events of their own and follow their requirements. The design's Test strategy maps each scenario to a layer from `eng-os-testing-strategy`, tasks gain a `Scenarios` column and keep their tests inside the task, and each test in the code is named for its scenario. A scenario that passes only once several tasks are done is listed on the last of them, and feature verify runs every active scenario together.
- **Approval is tracked and never blocks work.** Each file has a mode in `.specs/config.json`: `manual` (default) or `auto`, which a human sets and records. Authors and approvers are unique names registered as human or agent. At the end of each phase the agent presents a summary and what it assumed, records approval according to the mode, and continues.
- **Skills only.** No code ships with the spec process. The agent appends events with its ordinary file tools, takes the time from a one-line shell command (bash and PowerShell forms are in the skill), and walks a check list (`references/spec-format.md`, Checking the spec) after each phase and after any change. There are no row hashes and no derived status file, so a missed event or an approved row edited without an `edited` line is caught by the check list and the agent's discipline, not by a tool. Nothing depends on version control, hooks, or CI.
- **Persisted C4 views.** `eng-os-system-design` gained Persisting the Model: Context, Container, and (where internals matter) Component views live as text diagrams in `docs/architecture/` and change in the same PR as any boundary change. New template `micro/templates/architecture-template.md` (Mermaid C4, file header, inventory table with a trust-boundary column, and a table of which change updates which view). `meso/system-design.md` carries the same rule.
- **Living and record documents.** `eng-os-documentation-standards` and `meso/documentation.md` split documents into living (README, C4 views, contracts, runbooks) and record (ADRs, release notes, specs), give each fact one home, and add Architecture Views, Feature Spec, and README to the document types.
- `eng-os-execute-feature` Phase 7, Sync Living Documents: after feature verify, each living document is updated or marked "no change" with a reason.
- `eng-os-core` checkpoint rows for a behavior change to a specced feature, a boundary change, and finishing a feature. The matching rows are in `meta/claude-code-usage.md` Section 3.
- CLAUDE.md template gained a `## Living Documents` section pointing at `.specs/`, `docs/architecture/`, ADRs, and the current-state docs. `micro/project-structure.md` added `.specs/` and `docs/architecture/` to the root layout and documentation structure.
- `eng-os-audit` C16 now walks the spec check list, flags frozen rows edited and rows built on unapproved ones, and lists rows no human reviewed; C18 checks `docs/architecture/` against the code; new row C19 checks README and living-document currency.
- `eng-os-testing-strategy` and `meso/testing-strategy.md` gained a rule: name a test for the scenario it proves.
- Glossary: Ledger Entry, Scenario, Spec Event, Frozen Entry, Approval Tracking, Spec Amendment, Living Document, Architecture Views. ADR-005 and evidence ledger E-31 and E-32.

### Changed
- **File names are topic first, layer second.** `<capability>.<layer>` becomes `<topic>.<layer>` (`.ts`) and `<topic>_<layer>` (`.py`), where the topic is the concept the file is about. Pages (`.page.tsx`, `_page.py`) are controllers, UI components are `<Name>.tsx`, and tests share their file's name. Updated in the common, Node.js, and Python coding standards, `mvcs-layout.md`, and `micro/project-structure.md`.

### Notes
- Projects with specs written in the 1.8.0 format (checkboxes, Status headers) have none known downstream, and no migration is provided.
- No skill was added; the three requests extend `eng-os-spec-feature`, `eng-os-system-design`, and `eng-os-documentation-standards` (ADR-005).
- Projects bootstrapped under 1.8.0 have no `docs/architecture/` or Living Documents section and fail audit C18 and C19 until a task adds them. No existing rule was removed.

---

## [1.8.0] — 2026-11-13

### Changed (breaking)
- **Standard 13 is now Capability-Based MVCS** (`eng-os-coding-standards-common`, `micro/coding-standards/common.md`). It replaces Model-View-Controller layering. Code is grouped by capability, and every capability has the same five layer folders from its first file: `controllers/`, `services/`, `repositories/`, `models/`, `views/`. There is no size threshold and no layer folder that is added later.
- Dependencies flow controllers, services, repositories, models only. Services receive repositories by injection from one composition root, own the transaction boundary, and import no transport types. Capabilities reach each other only through services or events; cross-capability orchestration lives in `workflows/`. Repositories and record structures are always separate.
- Applies to every application type, including workers, consumers, CLIs, and UIs. The controller's binding and the view's output change per transport; the layers do not.
- `micro/project-structure.md` Section 2 (source layout), Section 7 (tests mirror `src/` layer for layer), Section 8 (dependency direction), and the root layout (`database/`, entry point and config inside `src/`) were rewritten to match. The config module moved from `src/config.ts` / `config.py` to `src/config/env.ts` / `src/config/env.py`.
- `micro/coding-standards/nodejs.md` and `python.md` gained Section 11, Capability Layout (MVCS): file naming, validation library, error mapping, and the dependency-direction tool (`dependency-cruiser`, `import-linter`).

### Added
- `eng-os-coding-standards-common/references/mvcs-layout.md`: the fixed layout, one tree per transport, a composition-root example in TypeScript and Python, and reviewer checks.
- `eng-os-bootstrap` Step 3a, the language skill gate: a language with no coding-standards skill gets one, verified against the real project, before code is written in it. Java and Go have no skill or examples yet by design.
- `eng-os-bootstrap` Architecture Practices Gate rows: capabilities and the five layers, composition root, dependency direction enforced in CI. The layering rows apply to every project with source code, UI or not.
- `eng-os-audit` rows B13 to B16: five folders per capability, dependency direction and its enforcing tool, injected repositories, mirrored tests.
- Glossary entries: Capability-Based MVCS (replaces Model-View-Controller), Capability, Repository, Composition Root, Workflow. Evidence ledger E-30.

### Notes
- Backported to: both language standards, `eng-os-bootstrap` (skill, template, worked example), `eng-os-audit` (skill and example), `eng-os-core` checkpoint table, MINDMAP, glossary, `meta/architecture.md`, `meta/claude-code-usage.md`, README.
- Existing projects bootstrapped under the old Standard 13 will fail audit rows B13 to B16 until retrofitted. The retrofit is a tracked task list item (`eng-os-execute-feature`), not an implied side effect.

---

## [1.7.0] — 2026-10-06

First public release.

### Included
- 36 documents in four layers (meta, macro, meso, micro) under `system/`: a shared glossary, principles, domain design guides, implementation standards, and templates.
- 28 skills in the open `SKILL.md` format under `system/skills/`: an always-on router (`eng-os-core`), planning and workflow skills (`eng-os-plan-app`, `eng-os-bootstrap`, `eng-os-spec-feature`, `eng-os-execute-feature`, `eng-os-audit`), and domain skills for coding standards, API and data design, security, observability, testing, deployment, and prose style.
- An evidence ledger (`system/evidence/`) and architecture decision records (`system/docs/decisions/`).
- Installers for Claude Code (`tools/install.ps1`, `tools/install.sh`) and a self-check (`tools/lint-os.py`) that CI runs on every push.
- Licenses: CC BY 4.0 for `system/`, MIT for `tools/` and `.github/`. See `LICENSE`.
