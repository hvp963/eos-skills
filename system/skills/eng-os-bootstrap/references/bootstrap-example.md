# Bootstrap Worked Example — On-Call Rotation Tracker

A concrete run through the Bootstrap Sequence for a small internal tool: **"a small internal
tool for tracking on-call rotations"**: who's on call for which service, when shifts hand off,
and reminders before a handoff.

## Step 0 — Bail-out check

Inspecting the repo:

- `package.json` exists, with real dependencies: `express`, `pg`, `node-cron`, `react`,
  `vite`, plus a `tests` script wired to `vitest`.
- Source is split across `src/api/`, `src/db/`, `src/web/`, more than one file, clear
  separation of concerns (API layer, persistence, front end). `src/web/` itself is not yet
  split along MVC/app-shell lines (Standard 13, `eng-os-design-system` App Shell): flagged below as
  a gap to close during bootstrap, not a reason to disqualify the project from the full template.
- There's a `migrations/` folder with two migrations already applied, and a `README.md`
  describing a roadmap ("v2: Slack reminders", "v3: multi-team support").

Conclusion: this **is** a real, ongoing project, a small one, but with a framework, a database,
a UI, and evidence of intended growth (versioned migrations, a stated roadmap). It does not
qualify for the trivial-script bail-out. Proceed with the full CLAUDE.md template rather than an
N/A-heavy minimal version.

## Step 1 — Tech stack and domains touched

- Language: TypeScript (Node.js backend, React frontend), single repo.
- Has an API (`src/api/`, Express), a database (Postgres via `src/db/`, migrations present), a
  UI (`src/web/`, React), a scheduled job (`node-cron` for handoff reminders), no AI components,
  and a lightweight CI pipeline (GitHub Actions running lint + tests).
- No multi-app suite: this is a standalone internal tool.

## Step 2 — Product Brief check

No `eng-os-plan-app` Product Brief exists for this project (it predates adoption of the Engineering OS
and was bootstrapped retroactively). Sections below are populated by inspecting the existing
schema, routes, and UI directly, and confirming with the user where the code was ambiguous.

## Step 3 — Select the exact Active Skills set

Mapped from Step 1 findings:

- `eng-os-core`: always active.
- `eng-os-api-design`: exposes a REST API (`/rotations`, `/services`, `/shifts`) consumed by the React
  frontend.
- `eng-os-database-design`: Postgres schema with migrations already in active use.
- `eng-os-security-practices`: the app has a login (internal SSO-backed), and shift data implies
  who is reachable when, access should be read-restricted appropriately.
- `eng-os-reliability-engineering`: the reminder job calls an outbound notification service, so
  timeouts, a single retry layer with jitter, and a bounded queue apply to that call path.
- `eng-os-privacy-and-governance`: engineers' phone numbers and emails are stored to deliver
  reminders; that is personal data, so classification, retention, and deletion apply.
- `eng-os-observability`: the cron-based reminder job is exactly the kind of "silently stops firing"
  failure mode that needs a metric/log, not just try/catch.
- `eng-os-testing-strategy`: `vitest` suite already exists and is CI-enforced.
- `eng-os-coding-standards-nodejs`: TypeScript throughout, both API and frontend.
- `eng-os-design-system`: has a React front end with its own component styling (this app is
  standalone, so it originates its own design system rather than inheriting one).
- `eng-os-deployment-practices`: GitHub Actions CI pipeline exists and deploys to a small internal
  host.
- **Omitted:** `eng-os-system-design`; one deployable service and one database, so there is no
  service boundary or capacity-by-cell question yet; revisit when v3 multi-team changes that.
- **Omitted:** `eng-os-data-strategy`; no pipelines beyond the reminder job.
- **Omitted:** `eng-os-platform-infrastructure`; a single small internal host, no regions or
  cells; revisit if it moves to managed infrastructure.
- **Omitted:** `eng-os-ai-ids-authoring`; no AI components anywhere in this tool.
- **Omitted:** `eng-os-team-practices`; this is a two-person internal tool with no formal on-call
  process of its own (ironic, but true) or PR/incident process worth codifying yet; revisit if
  the team or process around the tool grows.
- **Omitted:** `eng-os-model-optimization`; no AI workflow exists to tune.

## Step 4 — `## Active Skills` written into CLAUDE.md

```markdown
## Active Skills

- eng-os-core — always active
- eng-os-api-design — REST API for rotations, services, and shifts consumed by the React UI
- eng-os-database-design — Postgres schema and migrations for rotations/services/shifts
- eng-os-security-practices — internal SSO auth; shift/contact data needs read restriction
- eng-os-reliability-engineering — reminder job calls an outbound notification service
- eng-os-privacy-and-governance — engineer phone numbers and emails stored for reminders
- eng-os-observability — cron-based handoff reminders must be observable, not silent-failure-prone
- eng-os-testing-strategy — vitest suite, CI-enforced
- eng-os-coding-standards-common + eng-os-coding-standards-nodejs — TypeScript across API and frontend
- eng-os-design-system — React frontend; this app originates its own design system (standalone, no suite)
- eng-os-deployment-practices — GitHub Actions CI/CD to internal host
- (omitted: eng-os-system-design — one service, one database, no boundary question yet)
- (omitted: eng-os-data-strategy — no pipelines beyond the reminder job)
- (omitted: eng-os-platform-infrastructure — single small host, no regions or cells)
- (omitted: eng-os-ai-ids-authoring — no AI components in this project)
- (omitted: eng-os-team-practices — no formal team process to codify yet at this size)
- (omitted: eng-os-model-optimization — no AI workflow exists to tune)
```

## Step 5 — `## Scale Targets` in numbers

No Product Brief supplied numbers, so they come from the user and from the data already in the
database, with every guess marked as an assumption:

```markdown
## Scale Targets

| Target | Value |
|---|---|
| Users and traffic | ~150 engineers; peak about 2 requests per second; reminder job runs every minute |
| Data | 25 Services and 25 Rotations; ~1,300 Shifts per year; ~2,600 per year if v3 multi-team doubles the Services (assumed) |
| Latency and availability | schedule view p50 200 ms, p99 800 ms; a HandoffReminder delivered within 5 minutes of its scheduled time; 99.5% availability per month |
| Recovery | RPO 24 hours (nightly backup), RTO 4 hours |
| Tenancy | single-tenant; Teams are a grouping, not a tenant boundary |
| Data classification | Confidential (engineer phone numbers and emails); no Restricted data |
```

The availability figure is 99.5% because the tool is not the pager: a missed reminder is a
convenience failure, and the paging system stays the system of record. Had reminders been the only
handoff signal, the target and the `eng-os-reliability-engineering` SLO would both be tighter.

## Step 6 — Excerpt of populated CLAUDE.md sections

```markdown
## Platform Context

Standalone internal tool. Not part of a multi-app suite. Runs at a single internal URL
(oncall.internal.example.com); no sibling apps, no shared design tokens or auth service beyond
the company's existing SSO, which this app consumes but does not own.

## Core Entities

- **Service** — a system or team-owned component that requires on-call coverage (e.g.
  "Payments API", "Data Pipeline"). Has a name and an owning team.
- **Rotation** — an ordered, repeating sequence of Engineers assigned to cover a Service over
  time (e.g. weekly rotation). Belongs to exactly one Service.
- **Shift** — one concrete, dated instance of coverage: one Engineer, one Rotation, a start and
  end timestamp. Generated from a Rotation's pattern but individually editable (for swaps).
- **Engineer** — a person who can be assigned to Shifts. Has contact info (used for reminders)
  and belongs to one or more Rotations.
- **HandoffReminder** — a scheduled notification sent to the outgoing and incoming Engineer
  ahead of a Shift boundary. Generated from a Shift, not stored as independent user input.

## Terminology Lock

- **"Shift"** is canonical for one dated coverage instance; rejected alternatives: "slot" (too
  generic, collides with UI calendar-slot terminology), "assignment" (implies a one-time task,
  not recurring coverage).
- **"Rotation"** is canonical for the repeating pattern; rejected alternative: "schedule" (too
  broad; the UI also has a literal calendar "schedule view" that shows Shifts, so reusing
  "schedule" for the pattern itself would collide).
- **"Handoff"** is the canonical verb/noun for the transition between two Shifts — rejected
  alternative: "transfer" (sounds financial in this domain, was confusing in early UI copy
  review).
- **"Engineer"** is canonical for a person who can be on call — rejected alternative: "user"
  (too generic; this app also has read-only "viewers" who are users but never Engineers).
```

## Result

Only after Steps 1-6 (including confirming every section above and the remaining template
sections: Audience and Framing, Screens and Flows, Design System Carryover marked N/A since
this app is standalone and originates its own system, Mock Data Scale, Project Structure,
Non-Obvious Constraints, Dependency Notes, are populated with no placeholders left) is
CLAUDE.md considered live, and `eng-os-core`'s checkpoint table becomes enforceable for this
project.

Project Structure is populated using the web-app example in `eng-os-bootstrap`'s own template
(MVC layering plus the four-region app shell), since `src/web/` here is a React frontend, not a
static/report page:

```
src/web/
  models/       Rotation/Shift/Engineer data shape and business rules
  views/
    shell/      AppHeader, AppFooter, NavPanel
    pages/      RotationsPage, ScheduleView, EngineerDetail — the application-panel content
    components/ ShiftCard, HandoffBadge — shared across 2+ pages
  controllers/  Route handlers; call models/, select a view, no business logic inline
  constants/    ROTATIONS_LABELS, ROTATIONS_MESSAGES, etc., sectioned by area
```

Retrofitting `src/web/`'s existing flat structure into this layout is itself a task the task
list (`eng-os-execute-feature`) should carry as an explicit early item, not something silently implied
by the CLAUDE.md update: moving files without a tracked task is exactly the kind of drift this
OS exists to prevent.

## Step 7 — Architecture Practices Gate

Run before marking bootstrap done, since this project has a UI (`src/web/`) and will emit
operational messages (handoff reminders, save confirmations):

| Practice | Concrete answer written into CLAUDE.md |
|---|---|
| Constants sectioned by area | `src/web/constants/rotations.ts`, `constants/engineers.ts`, `constants/shifts.ts` — one file per Core Entity area, each exporting `{AREA}_LABELS` and `{AREA}_MESSAGES` |
| User-facing strings are constants | Every label/heading/message in `views/pages/` and `views/shell/` reads from the constants files above; no inline literal strings in JSX |
| Message code prefix, shared sequence | `## Message Area Codes` table: `ROT` = Rotations, `ENG` = Engineers, `SHF` = Shifts, `HDR` = HandoffReminder. Single project-wide counter starts at `000001` |
| Business logic in Model layer | `src/web/models/rotation.ts`, `models/shift.ts`, `models/engineer.ts` — retry/reminder scheduling logic moves here, out of `src/api/` route handlers |
| Global CSS, no hardcoded styles | `src/web/styles/tokens.css`, following `eng-os-design-system` skill's token set; components reference tokens only |
| Four-region app shell | `views/shell/AppHeader.tsx`, `AppFooter.tsx`, `NavPanel.tsx` (links: Rotations, Schedule, Engineers); `views/pages/*.tsx` render into the application panel |
| Reusable components | `views/components/ShiftCard.tsx`, `HandoffBadge.tsx` — extracted since both already appear on 2+ pages in the existing code |
| MVC (any app type) | Controllers = `src/controllers/*.ts` (renamed from the existing flat `src/api/` route handlers during the retrofit task); Views = `views/`; Models = `models/` |
| Responsive breakpoints | Existing CSS uses fixed `960px` containers — flagged as a retrofit item to convert to `minmax()`/`%`-based layout for the 768px/1024px breakpoints |
| Config/env file | `src/config.ts` already exists and is correct; no change needed |

This table itself is what gets transcribed into CLAUDE.md's Project Structure, Message Area
Codes, and Non-Obvious Constraints sections, not kept as a separate scratch document. The
responsive-breakpoints row and the MVC-retrofit row both feed directly into the `eng-os-execute-feature`
task list as tracked items, since neither is true of the codebase yet at bootstrap time.
