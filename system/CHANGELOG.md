# Changelog

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

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
