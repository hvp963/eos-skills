---
name: eng-os-bootstrap
description: "Use once at the start of a new project (or when governance is being retrofitted onto an existing one) to scaffold CLAUDE.md, record Scale Targets, and declare which Engineering OS skills apply to this project."
sources:
  - meta/architecture.md
  - micro/project-structure.md
  - meta/claude-code-usage.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Engineering OS: Bootstrap

Run this once per project: at the start of a new project, or the first time an existing project
is brought under Engineering OS governance. Do not re-run it on every task; `eng-os-core` handles
ongoing enforcement via its checkpoint table. Do not use it to plan a new app's entities, screens, and phases (that is `eng-os-plan-app`, which runs first and feeds this one), or to check an already-bootstrapped project for drift (that is `eng-os-audit`).

## Bootstrap Sequence

This is deliberately not "read every file in engineering-os end to end." That does not scale and
produces a CLAUDE.md nobody can audit against. Instead:

0. **Bail-out check: is this a real, growing software project?** Look for a dependency manifest
   (package.json, requirements.txt, pyproject.toml, go.mod), a source structure with more than
   one file and some separation of concerns, and evidence it is meant to grow. If it is a single
   hardcoded utility script, do not force the full template onto it: populate a minimal CLAUDE.md
   with most sections explicitly marked `N/A` with a one-line reason each. Forcing false
   structure onto a trivial script misleads every later reader.
1. **Identify the tech stack and the domains the project touches.** Service, pipeline, AI
   system, library, or UI app; languages; whether it has an API, a database, a UI, AI
   components, a deployment pipeline, personal data, an SLO.
2. **Check for a Product Brief from `eng-os-plan-app`.** If one exists, transcribe its sections directly
   into CLAUDE.md (Platform Context, Audience and Framing, Core Entities, Screens and Flows,
   Scale Targets, Design System Carryover, Mock Data Scale, Terminology Lock). If none exists,
   populate those sections by asking the user or inspecting the codebase.
3. **Select the exact set of domain skills that apply**, not all of them. A Node.js API with
   Postgres, a React UI, and user accounts implies `eng-os-api-design`, `eng-os-database-design`,
   `eng-os-reliability-engineering`, `eng-os-security-practices`, `eng-os-privacy-and-governance`, `eng-os-testing-strategy`,
   `eng-os-coding-standards-nodejs`, `eng-os-design-system`. A pure ETL pipeline implies `eng-os-database-design`,
   `eng-os-data-strategy`, `eng-os-observability`, `eng-os-testing-strategy`, `eng-os-coding-standards-python`, and skips
   `eng-os-design-system` and `eng-os-api-design` if there is no UI or public API. Add
   `eng-os-platform-infrastructure` when the project owns infrastructure code or runs in more than one
   region.
4. **Write the `## Active Skills` section** listing exactly that set with a one-line reason each.
   This is the drift-check artifact: a reviewer audits future work against it.
5. **Populate `## Scale Targets` in numbers.** From the Product Brief if there is one, otherwise
   by asking. A target of "fast" or "lots of users" is a placeholder, not an answer. For a library
   or a trivial script, write `N/A` with a reason.
6. **Populate the rest of the template** (`references/claude-md-template.md`) and declare the
   project folder structure per `../../micro/project-structure.md`. Pin the Engineering OS
   version tag the project follows.
7. **Run the Architecture Practices Gate** (below) for any project with a UI or with operational
   messages. This is a separate, mandatory pass: "populate the template" alone has proven
   insufficient, because a section can hold enough prose to look filled in while binding the
   project to nothing checkable.
7a. **For a JS/TS project, add a formatter config in the same pass** if CLAUDE.md declares a
    print-width or other formatting convention: a `.prettierrc` (or equivalent) enforcing it, not
    follow-up work. A stated-but-unenforced width drifts silently: see the `eng-os-audit` finding
    class this is meant to prevent.
8. **Confirm every section is populated.** An unpopulated section is an incomplete bootstrap,
   not a "fill in later."

Only then is CLAUDE.md live and `eng-os-core`'s checkpoint table enforceable.

## Architecture Practices Gate

For any project with a UI (skip UI rows for a pure API, pipeline, or library) or with any
operational message, answer each row concretely, in writing, in CLAUDE.md. "Yes" is not an
answer; a path, folder, or component name is.

| Practice | Required concrete answer |
|---|---|
| No hardcoding; constants sectioned by area | The constants module path(s) and the first area section (e.g. `src/constants/customer.ts` with `CUSTOMER_LABELS`, `CUSTOMER_MESSAGES`) |
| All user-facing strings are constants | Confirmation that no literal label/message/heading appears inline in a component, plus the exception list (test names, log messages, comments) |
| Message code prefix, single project-wide sequence | The `## Message Area Codes` table with the areas known now, each with its 3-letter code, and the shared counter's start (`000001` for a new project) |
| Business logic in the Model layer | The actual `models/` (or equivalent) path |
| Global CSS, no hardcoded styles | The global stylesheet or token file path, and which design profile it follows |
| Four-region app shell | The four component paths (header, footer, nav panel, and where per-route content renders) |
| Reusable components | The shared-components folder path |
| MVC for any app type | How Model, View, and Controller map onto this project's actual folders, even for a CLI or backend service |
| Responsive: desktop, tablet, mobile | Confirmation the three breakpoints will be honored and the layout mechanism (Grid/Flexbox breakpoints, a responsive framework) |
| Accessibility | Confirmation WCAG 2.2 AA is a Definition-of-Done row and which automated checker runs in CI |
| Config/env file | The config module path |

If a row's honest answer is "this project has no UI, skip" or "no operational messages, skip,"
write that explicitly. An explicit skip with a reason is a completed row; silence is not.

**Failure mode this gate prevents:** a bootstrap that writes "Follows MVC" or "Uses a design
system" as a one-line assertion with no path a later reviewer can check code against. That
sentence satisfies "no placeholders" while binding the build to nothing, which is exactly how
prior projects drifted from practices the OS already named.

Worked example of the full sequence on a small app: `references/bootstrap-example.md`.
The template itself: `references/claude-md-template.md`.

## Handoff

When the Definition of Done below passes, the next skill depends on the work. For a feature that meets the spec threshold (three or more tasks, a contract or entity change, edge-case behavior, or ambiguous scope), run `eng-os-spec-feature`. For a small change, run `eng-os-execute-feature` directly. On a retrofit, the first task list carries the structure items bootstrap found (see `references/bootstrap-example.md`), because moving files without a tracked task is the drift this OS exists to prevent.

## Definition of Done

Bootstrap is complete when:
- `## Active Skills` lists the exact, minimal set of domain skills, each with a reason
- `## Scale Targets` holds numbers (or a reasoned `N/A` for a library or trivial script)
- the Engineering OS version tag the project follows is recorded
- every template section is populated; no placeholder text remains
- the project folder structure is declared and matches `micro/project-structure.md`
- if part of a suite, `## Design System Carryover` points to the source app or names the profile rather than retyping tokens
- `## Terminology Lock` and `## Message Area Codes` are populated (or explicitly `N/A` with a reason) before any code, UI copy, or messages exist
- if a Product Brief existed, its content was transcribed, not re-invented
- the Architecture Practices Gate ran with a concrete answer or a reasoned skip for every row, and each answer appears in the CLAUDE.md section where a reviewer will look
- the next step was stated: `eng-os-spec-feature` for a feature at the spec threshold, `eng-os-execute-feature` for a small change
