# Engineering OS: Skills

**Status:** Current
**Owner:** Haresh V. Parekh

This is the Skills adapter for the Engineering OS. The canonical prose standards live in `../meta/`, `../macro/`, `../meso/`, `../micro/`; this directory is a thin, selectively-loaded routing layer over them, built for how AI coding agents consume context: a little always, more on demand, never all 36 canonical files up front.

New here? Read in this order:
1. **`MINDMAP.md`**: how the 28 skills relate, which matter most, and their known scope limits.
2. **`eng-os-core/SKILL.md`**: the always-on root skill. Everything else is reached through its checkpoint table.
3. **`eng-os-plan-app/SKILL.md`**: for a new app or feature, this runs before any code exists.
4. **`eng-os-spec-feature/SKILL.md`**: once scope is approved, this turns it into approved requirements, design, and a task list.
5. **`eng-os-execute-feature/SKILL.md`**: this runs the task list one verified task at a time.

---

## Installing the skills

A skill only routes automatically when the agent runtime can see it. Claude Code discovers skills at `<home>/.claude/skills/<name>/SKILL.md` (user level, every project) and `<project>/.claude/skills/<name>/SKILL.md` (one project). The installers create one link per skill, named by the skill's frontmatter `name` (nested skills such as `eng-os-coding-standards/common` become `eng-os-coding-standards-common`). Run once per machine, and again after adding a skill.

| Platform | Command | Link type | Notes |
|---|---|---|---|
| Windows 10/11 | `tools\install.ps1` <br> `tools\install.ps1 -Project C:\path\to\app` | Directory junction | No administrator rights or Developer Mode needed. Home is `%USERPROFILE%\.claude\skills`. Remove with `-Remove`. |
| macOS | `tools/install.sh` <br> `tools/install.sh --project /path/to/app` | Symlink | Home is `~/.claude/skills`. If the repo lives on an external or case-sensitive volume, keep it mounted when Claude Code starts. Remove with `--remove`. |
| Linux | `tools/install.sh` <br> `tools/install.sh --project /path/to/app` | Symlink | Same as macOS. In CI, run it before the agent step (see `.github/workflows/lint.yml`). |
| WSL | run `tools/install.sh` inside WSL | Symlink | Claude Code running in WSL reads the Linux home, not the Windows one; install from the side you run the agent on. A repo cloned under `/mnt/c` works but is slower; prefer a clone in the Linux filesystem. |

Verify in a fresh session that the skills appear in the agent's skill list; `verified_platforms` in each skill's frontmatter records where that has actually been confirmed.

**Other agents that read `SKILL.md` natively** need no transform, only a path. Copilot, Cursor, Windsurf, and Cline also read `.claude/skills/`, so the installer's links already reach them. Codex CLI reads `.agents/skills/`, Gemini CLI reads `.gemini/skills/` or `.agents/skills/`; link or copy the whole `system/skills/` folder there. Only Aider needs a lossy export. Paths, the date they were checked, and the caveats are in `PORTABILITY.md`.

---

## Quick start

| If you're... | Invoke | Because |
|---|---|---|
| Starting a brand-new app or major feature | `eng-os-plan-app` | Turns an idea into a Product Brief (entities, screens, Scale Targets, phased scope, terminology) before anything is scaffolded; hands off to `eng-os-bootstrap` |
| Retrofitting governance onto an existing app with no CLAUDE.md | `eng-os-bootstrap` | Has a bail-out check for trivial scripts; records Scale Targets; runs the Architecture Practices Gate |
| Scope approved for a feature of three or more tasks, a new or changed contract or entity, edge-case behavior, or ambiguous scope | `eng-os-spec-feature` | Writes `.specs/<feature>/` requirements (EARS criteria), design, and tasks, with an explicit approval gate after each |
| Ready to build: a spec is approved, or the change is small enough to need none | `eng-os-execute-feature` | Adopts the spec's task list (or decomposes the scope), runs one task at a time with a verify gate between tasks, and parallel lanes for independent ones |
| Already mid-project, writing code | `eng-os-core` (already active) | Its checkpoint table routes to the right domain skill at each point |
| Setting SLOs, timeouts, retries, queue bounds, or a degraded path | `eng-os-reliability-engineering` | Owns how the running system stays within its targets under load and partial failure |
| Provisioning infrastructure, laying out regions or cells, or setting up backups | `eng-os-platform-infrastructure` | Owns what the pipeline deploys onto |
| Handling personal or regulated data, retention, deletion, or a third-party transfer | `eng-os-privacy-and-governance` | Classification, retention, lineage, access review, audit |
| Checking whether a project has actually stayed compliant | `eng-os-audit` | Read-only sweep against the project's own CLAUDE.md and the checkpoint table, ending in a report |
| Tuning cost or speed of the agent workflow itself | `eng-os-model-optimization` | Provider-agnostic core plus `references/claude.md`, `references/openai.md`, `references/custom-oss.md` |
| Writing or reviewing prose before marking it done | `eng-os-prose-style` | Thirteen patterns that read as unedited AI output, with a rewrite for each |

---

## What's in here

```
skills/
  eng-os-core/            always-on: principles + checkpoint router
  eng-os-bootstrap/       one-time: CLAUDE.md scaffolding, Scale Targets, Active Skills (template in references/)
  eng-os-plan-app/               one-time, pre-code: Product Brief for greenfield apps
  eng-os-spec-feature/           per-feature, pre-code: requirements, design, tasks, each behind an approval gate
  eng-os-execute-feature/        per-feature, pre-code to done: task loop with verify gate and one commit per task
  eng-os-audit/           periodic, read-only: compliance sweep + report
  eng-os-model-optimization/     cross-cutting: token/latency/quality tuning (Claude, OpenAI, custom-OSS)
  eng-os-api-design/             HTTP/RPC contracts, auth/authz per endpoint, deadlines
  eng-os-database-design/        schema, indexing, migrations at scale, tenancy
  eng-os-data-strategy/          pipelines, freshness SLAs, watermarks, delivery semantics (+ pipeline checklist)
  eng-os-system-design/          boundaries, C4, bounded contexts, capacity, cells (+ service checklist)
  eng-os-reliability-engineering/ SLOs, timeouts, retries, breakers, bulkheads, shedding, chaos
  eng-os-security-practices/     input validation, secrets, authz model, threat model, audit log
  eng-os-privacy-and-governance/ classification, personal data, retention, lineage, access review
  eng-os-observability/          logs, metrics, traces, cardinality, sampling, OpenTelemetry
  eng-os-testing-strategy/       unit/integration/contract/property/AI-eval/load layers, flaky policy
  eng-os-deployment-practices/   CI/CD, environments, expand/contract ordering, rollback, rotation
  eng-os-platform-infrastructure/ IaC, environment parity, regions and cells, backup and restore
  eng-os-design-system/          rule vs. profile, app shell, responsive, accessibility, i18n, UX/IA
  eng-os-documentation-standards/ ADRs (with threshold), contracts, runbooks
  eng-os-team-practices/         code review, PR standards (+ incident/on-call/tech-debt in references/)
  eng-os-code-conventions/       naming, comments, terminology lock
  eng-os-prose-style/            sentence-level prose: no AI-tell patterns
  eng-os-coding-standards/
    common/               language-agnostic implementation rules
    python/               Python specifics
    nodejs/               Node/TypeScript specifics
  eng-os-ai-ids-authoring/       AI-IDS 11-section framework, lifecycle, observability UI (in references/)
  eng-os-doc-authoring-rules/    maintainer-only: how to write/extend these skills
```

Every `SKILL.md` has a `sources:` field pointing back to the canonical prose doc(s) it was condensed from. For the full rationale, follow that pointer.

---

## Frontmatter contract

| Field | Purpose |
|---|---|
| `name` | matches the folder path, kebab-case (nested skills use `-` not `/`, e.g. `eng-os-coding-standards-nodejs`) |
| `description` | what the agent uses to decide relevance; written as "Use when..." |
| `sources` | root-relative paths back to the canonical `meta/macro/meso/micro` docs; never empty |
| `globs` | file patterns this skill's domain applies to; feeds glob-based platforms (see `PORTABILITY.md`) |
| `always_apply` | `true` only for `eng-os-core` |
| `verified_platforms` | which AI coding tools this skill has actually been exercised on and confirmed to load |

`tools/lint-os.py` enforces this contract, checks that every `sources:` path exists, that skill counts in the docs match the folders on disk, that relative links resolve, and that no em dash joins two clauses in flowing prose. CI runs it on every push.

---

## Extending this skill set

1. Check `MINDMAP.md` first: does this belong inside an existing skill, or does it need a new one? Most additions belong inside an existing skill's body or a new `references/*.md`.
2. Write the rule in the canonical `meso`/`micro` doc first, then in the skill (`../CONTRIBUTING.md`).
3. Ground every new rule in evidence and add a row to `../evidence/ledger.md`.
4. State the rule's scope limit explicitly if it doesn't hold unconditionally at production scale.
5. Update `MINDMAP.md` if the change affects routing or relationships.
6. Update `eng-os-core`'s checkpoint table if the new skill should be routed to automatically.
7. Run `python tools/lint-os.py` before committing.

---

## Cross-platform use

See `PORTABILITY.md`.
