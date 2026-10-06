# Changelog

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

---

## [1.7.0] — 2026-10-06

First public release.

### Included
- 36 documents in four layers (meta, macro, meso, micro) under `system/`: a shared glossary, principles, domain design guides, implementation standards, and templates.
- 28 skills in the open `SKILL.md` format under `system/skills/`: an always-on router (`eng-os-core`), planning and workflow skills (`eng-os-plan-app`, `eng-os-bootstrap`, `eng-os-spec-feature`, `eng-os-execute-feature`, `eng-os-audit`), and domain skills for coding standards, API and data design, security, observability, testing, deployment, and prose style.
- An evidence ledger (`system/evidence/`) and architecture decision records (`system/docs/decisions/`).
- Installers for Claude Code (`tools/install.ps1`, `tools/install.sh`) and a self-check (`tools/lint-os.py`) that CI runs on every push.
- Licenses: CC BY 4.0 for `system/`, MIT for `tools/` and `.github/`. See `LICENSE`.
