# CLAUDE.md Template

Copy this into the project root as `CLAUDE.md` and populate every section. Guidance in square
brackets is replaced, not kept. Canonical source: `../../../meta/claude-code-usage.md` Section 2.

```markdown
# Claude Code: Project Instructions

## Engineering Standards

All code in this project follows the Engineering OS at:
[absolute path to engineering-os]
Engineering OS version: [the release tag this project is pinned to, e.g. 1.7.0]

Skills are installed per `tools/install.*` in that repository; `eng-os-core` loads first.

## Active Skills

[The exact set of Engineering OS skills that apply to this project, selected in Bootstrap Step 3.
List every skill in use with a one-line reason. This is the drift-check artifact: a reviewer
audits new work against this list. Update it if the project's scope changes.]

Example:
- eng-os-core: always active
- api-design: this service exposes a public REST API
- database-design: Postgres schema and migrations
- reliability-engineering: has availability and latency SLOs
- security-practices: handles user auth and PII
- privacy-and-governance: stores personal data
- testing-strategy: CI-enforced test suite
- coding-standards-nodejs: TypeScript codebase
- design-system: has a React front end
- (omitted: ai-ids-authoring, no AI components in this project)
- (omitted: platform-infrastructure, single-region managed platform with no infrastructure repo yet)

---

## Platform Context

[If this app is part of a multi-app suite, name the sibling apps, their paths, and their ports.
State what is shared across the suite (design tokens, auth, a shared library) versus what is
unique to this app. If standalone, say so explicitly.]

## Audience and Framing

[Who is this for? What pillars, themes, or positioning must every feature reinforce?]

## Core Entities

[The domain model, defined before code exists. Name each core entity, what it represents, and
its key relationships. Entity names are decided once; see Terminology Lock.]

## Screens and Flows

[One entry per screen or page: what it shows, what data it needs, what actions it enables. For a
non-UI project state that explicitly and skip the detail; do not leave a placeholder.]

## Scale Targets

[Numbers, not adjectives. Expected and peak requests per second; data volume now and growth per
year; largest single tenant; latency (p50/p99) and availability targets; RPO/RTO; tenancy model;
data classification level; regulatory scope. Every design review, capacity model, load test,
and cost budget is checked against these. "N/A" only for a library or a trivial script, with a
reason.]

Example:
| Target | Value |
|---|---|
| Users (year 1 / year 3) | 200,000 / 2,000,000 |
| Peak RPS | 800 (year 1), 6,000 (year 3) |
| Data volume | 40 GB now, +60 GB/year |
| Largest tenant | 15% of traffic |
| Latency | p50 120ms, p99 400ms |
| Availability | 99.9% monthly |
| RPO / RTO | 15 min / 1 hour |
| Tenancy | shared tables, `tenant_id` on every row |
| Data classification | Confidential (names, emails); no Restricted |
| Regulatory scope | GDPR |

## Design System Carryover

[If this app inherits its visual language from a sibling app, point to that sibling's design
system declaration by path instead of retyping tokens. If it uses the Engineering OS default
profile, say so and name the token file path. If it defines its own, populate it here.]

## Mock Data Scale

[Seed volumes for demos and local development, e.g. "50 sample accounts, 500 transactions
spanning 90 days." Omit only if the project has no seed data concept.]

## Terminology Lock

[Canonical names for the core nouns and verbs, decided before implementation. A deliberate,
versioned rename in one complete pass is acceptable; incremental drift is not. Changing a term
after this point requires an ADR.]

## Message Area Codes

[Declared once per project. Every success/warning/info/error message gets `{CODE}{6-digit
sequence}`: 3-letter area code plus one counter shared across the whole project. Adding an area
later is fine; reassigning or reusing a code is not, and requires an ADR.]

Example:
| Area | Code |
|---|---|
| Customer | CST |
| Order | ORD |
| Auth | AUT |

Next sequence number (single project-wide counter): 000001

---

## Project Structure

[Every folder and its purpose, per micro/project-structure.md. For any project with a UI, the
structure reflects MVC (coding-standards-common Standard 13) and the four-region app shell
(design-system App Shell).]

Example (backend/pipeline project):
ids/        AI-IDS specification files (.ids), plain text, at project root
src/        Source modules
  config.py All environment variables read here; never call os.getenv() elsewhere
input/      Input files (declare whether gitignored or versioned)
output/     Pipeline output (gitignored)
logs/       Structured log files (gitignored)
docs/
  decisions/  Architecture Decision Records
  contracts/  Data contracts and output schemas
  prompts/    Prompt registry entries for every .ids file
tests/      pytest or equivalent test suite
main.py     Entry point

Example (web app project, MVC + app shell):
src/
  models/       Data shape, persistence, business rules; no rendering, no framework I/O
  views/
    shell/      AppHeader, AppFooter, NavPanel: the three shared shell regions
    pages/      Application-panel content per route: the fourth region
    components/ Reusable UI components shared across 2+ pages
  controllers/  Route/page handlers; orchestrate Model + View only
  constants/    Sectioned by app area: labels, messages, config, business constants
  config.ts     All env vars read here; never read process.env elsewhere
  styles/       Global CSS/tokens; no hardcoded styles in components
docs/
  decisions/    Architecture Decision Records
tests/

---

## AI-IDS Rules

[Populate only if the project uses AI systems, otherwise "N/A, no AI components."]

- Every AI task specification lives in ids/<name>.ids as plain text, with a version header
- .ids files follow the template in meso/ai-ids-template.md exactly
- Harness code loads the .ids file at startup and logs its version per inference
- The harness contains no cleaning or decision logic, only call mechanics
- Prompt registry entry and evaluation fixtures exist for every .ids file
- Never embed an AI-IDS spec as a string constant in code

---

## Definition of Done

Run every applicable checklist (from each Active Skill above) before marking any task complete.
See eng-os-core's Meta Definition of Done for the enforcement rule.

---

## Non-Obvious Constraints

[Project-specific constraints that would surprise a future engineer or agent: framework quirks,
external system behaviors driving local choices, known false positive/negative risks in AI
logic, any place the obvious implementation would be wrong.]

## Dependency Notes

[Pinned versions, known incompatibilities, required install steps.]
```
