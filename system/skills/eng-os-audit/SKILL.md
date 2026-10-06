---
name: eng-os-audit
description: "Use to check an existing, already-bootstrapped project's actual state against the Engineering OS it claims to follow, and produce a written compliance report. Run it periodically, before a release, or any time you want to know where a project (or the agent working on it) has drifted from CLAUDE.md and the checkpoint table, not just whether code runs. Does not modify code; read-only audit that ends in a report artifact."
sources:
  - meta/mental-model.md
  - meta/glossary.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Engineering OS — Audit

`eng-os-core`'s checkpoint table is enforced turn by turn, in the moment a file is touched. That
works only as well as the agent applying it in that moment. The OS is a set of instructions an
agent has to apply; it is "not a compiler or lint rule that mechanically blocks a bad change."
This skill is the compensating check: a point-in-time,
read-only sweep of a project's **current state** against everything it committed to at bootstrap
and everything the checkpoint table should have enforced since. It does not trust "I followed the
process": it re-derives compliance from the files on disk.

Use this:
- Periodically on a long-running project, to catch drift before it compounds
- Before a release or a handoff
- Any time you suspect a prior session skipped a checkpoint
- As a second opinion on another agent session's work in this project

Do not use this mid-task as a substitute for the checkpoint table itself: it audits what already
exists, it does not replace invoking `eng-os-api-design`, `eng-os-security-practices`, etc. while writing new
code.

## Prerequisites

The project must already be bootstrapped (`## Engineering Standards` section in CLAUDE.md
pointing at an engineering-os path, and `## Active Skills` populated). If it is not, stop and run
`eng-os-bootstrap` instead: auditing against a project's own CLAUDE.md is meaningless if that
CLAUDE.md was never written per the bootstrap sequence. Note this in the report rather
than silently redirecting.

## Audit Sequence

1. **Read the project's CLAUDE.md in full.** This is the baseline the audit checks against, not
   a generic reading of the Engineering OS, but this specific project's own declared commitments
   (Active Skills list, Terminology Lock, Message Area Codes, Project Structure, Architecture
   Practices Gate answers).
2. **Resolve the engineering-os path** named in `## Engineering Standards`. If it is not reachable
   from this machine, note that as a finding (the audit can still proceed using this skill's own
   condensed checklist below, but flag that source-of-truth files could not be cross-checked).
3. **Work through the checklist below section by section.** Each row names what to check and
   where to look. Do not mark a row Pass on the strength of a CLAUDE.md sentence alone: verify
   against the actual files (grep, read, list) the way the row describes. A CLAUDE.md that
   *claims* MVC but a codebase with business logic in route handlers is a Fail, not a Pass.
4. **Classify every row** as one of:
   - **Pass**: concretely verified against real files
   - **Fail**: concretely verified absent or violated; cite the file/line
   - **Partial**: present but inconsistent (e.g. followed in 3 of 5 modules); cite both sides
   - **N/A**: legitimately doesn't apply to this project (no UI, no AI components, etc.); the row
     must have been explicitly marked N/A in CLAUDE.md itself, not silently skipped by the auditor
   - **Unknown**: could not be determined (source unreachable, ambiguous evidence); never round
     an Unknown up to Pass
5. **Write the report** (template below) as a file the user can review, and as a published
   Artifact if the user wants something shareable/visual: a compliance report is exactly the
   finished-deliverable-with-an-audience case, so publish it rather than leaving it only in
   terminal output.
6. **Do not silently fix findings while auditing.** This skill is diagnostic. If the user wants
   fixes applied, that is a separate, explicit follow-up step after they've seen the report:
   auditing and remediating in the same pass hides how bad the starting state was and
   removes the user's chance to decide priority and scope.

## Checklist

### A. Bootstrap Integrity

| # | Check | Verify against |
|---|---|---|
| A1 | `## Engineering Standards` section exists, points at a real engineering-os path, and pins an Engineering OS version tag | CLAUDE.md |
| A2 | `## Active Skills` lists a specific, non-trivial set with a reason per skill (not "all of them," not empty) | CLAUDE.md |
| A3 | Active Skills list still matches the project's actual scope — no skill checked in that the project no longer touches (e.g. `eng-os-design-system` listed but no UI code exists), and no skill missing that the codebase clearly needs (e.g. a public API with no `eng-os-api-design` on the list) | CLAUDE.md vs. actual source tree |
| A4 | `## Platform Context`, `## Audience and Framing`, `## Core Entities`, `## Screens and Flows`, `## Mock Data Scale` are populated or explicitly marked N/A with a reason — none left as blank template placeholders | CLAUDE.md |
| A5 | `## Terminology Lock` is populated before-the-fact style (canonical nouns/verbs), and code/UI/API actually use those exact terms — grep for near-synonyms of each locked term to catch drift | CLAUDE.md vs. source, UI copy, API field names |
| A6 | `## Message Area Codes` table exists with area/3-letter-code pairs and a stated next-sequence counter; no two areas share a code; no code was reassigned | CLAUDE.md |
| A7 | `## Project Structure` section names real folders that exist in the repo, matching `project-structure.md` conventions (MVC layers, app shell regions where there's a UI) | CLAUDE.md vs. actual folder tree |
| A8 | `## Definition of Done` and `## Non-Obvious Constraints` are populated, not placeholder text | CLAUDE.md |
| A9 | `## Scale Targets` holds numbers (users, peak RPS, data volume, latency, availability, RPO/RTO, tenancy, classification), or a reasoned N/A for a library or trivial script | CLAUDE.md |

### B. Architecture Practices Gate (skip UI/message rows only if the project truly has none — state that explicitly, don't skip silently)

| # | Check | Verify against |
|---|---|---|
| B1 | Constants sectioned by area exist at the path CLAUDE.md names; no hardcoded label/message/heading strings inline in components — grep for quoted string literals in JSX/template/view files | Named constants module(s) |
| B2 | Every operational message in code carries a `{AREA}{6-digit}` code from the declared Message Area Codes table; no code is reused; grep all `throw`/`log`/toast/notification calls for bare strings with no code | Source, against CLAUDE.md's Message Area Codes table |
| B3 | Business logic lives in Model layer files, not inline in route/controller/handler files — spot-check the largest handlers for inline business rules | `models/` (or stack equivalent) vs. `controllers/`/handlers |
| B4 | Global CSS/token file exists at the named path; components reference tokens/classes, not inline hardcoded colors/spacing | Named stylesheet/token file vs. component styles |
| B5 | Four-region app shell present as named components (header, footer, nav panel, one application-panel-per-route) — not duplicated per page | Named shell component paths |
| B6 | Shared/reusable components actually live in the named shared folder, not copy-pasted across pages — grep for near-duplicate JSX/markup blocks across 2+ page files | Named shared-components folder |
| B7 | MVC (or stack equivalent) mapping stated in CLAUDE.md matches reality: Models contain no rendering, Views contain no business logic, Controllers are thin orchestration only | Actual source layering |
| B8 | Responsive breakpoints (desktop/tablet/mobile) are actually implemented in the named layout mechanism, not asserted only | CSS/layout files |
| B9 | Config/env file exists at the named path; grep the whole codebase for direct `os.getenv`/`process.env` calls outside that one file | Named config module vs. rest of source |
| B10 | Accessibility: an automated WCAG checker runs in CI and shell components are keyboard operable with visible focus | CI config, shell components |
| B11 | The declared design profile (default, inherited, or own) exists at the named path and components reference its tokens | Named token file vs. component styles |
| B12 | Generic/specific split: every specific-section bullet passes `eng-os-doc-authoring-rules` Core Rule 11's duplicate test against the generic section | The doc's own generic vs. specific sections |

### C. Checkpoint-Table Compliance (spot-check recent work, not full history)

For each row, sample the most recently changed files in that category (via `git log`) rather than
attempting to review everything ever written: an audit that tries to re-review the entire history
of a mature project will never finish and isn't what this skill is for.

| # | Domain | Check | Sample from |
|---|---|---|---|
| C1 | Naming (`eng-os-code-conventions`) | Recent identifiers match convention and Terminology Lock | Recently changed files |
| C1a | Comment discipline (`eng-os-code-conventions`) | Comment-to-code ratio isn't a runaway outlier in recently changed files; no comment block runs past two sentences; grep recent `//`/`#` comments for changelog-narration markers (`PLAN-\d+`, `ADR-\d+`, "used to," "originally," "the incident this") | Recently changed files, comment lines only (not commit messages or ADRs, where this content belongs) |
| C2 | Coding standards | Type annotations, docstrings, external-call error handling, no secrets logged, one cohesive responsibility per new module | Recently added modules |
| C3 | Duplication (Standard 12) | No logic duplicated a third time — recently added code that resembles existing code should have been extracted, not copied | `git log` recent diffs vs. rest of codebase |
| C4 | `eng-os-api-design` | New/changed endpoints have a stated version, explicit error schema; breaking changes look like migrations, not silent field removals | API route/schema files |
| C5 | `eng-os-database-design` | New tables/migrations are reversible or the irreversibility is justified in a comment/ADR; indexes have a stated rationale | Migration files |
| C6 | `eng-os-security-practices` | Input validated at boundaries; least-privilege access; no secrets in code or logs; trust boundaries explicit | Auth/input-handling code |
| C7 | `eng-os-observability` | Structured logs carry `trace_id`/`span_id`/`severity`/`service`; metrics defined, not just logs | Logging call sites |
| C8 | `eng-os-testing-strategy` | Test files exist per feature; happy-path and failure-path both covered; external deps mocked | Test directory vs. source directory (ratio + gaps) |
| C9 | `eng-os-deployment-practices` | Environments separated; health checks hit real dependencies, not stubs; a rollback path exists | CI/CD config |
| C10 | `eng-os-prose-style` | Recent README/PR/commit prose: no repeated contrastive negation, no filler intensifiers, no em dash joining two clauses, no clichés, no fake precision or generic closers | README, recent commit messages, docs |
| C11 | `eng-os-documentation-standards` | ADRs exist for significant decisions made since the last audit (new dependency, contract change, deviation from a documented pattern) | `docs/decisions/` vs. `git log` for matching decision points |
| C12 | `eng-os-ai-ids-authoring` (if applicable) | Every `.ids` file follows the template; none embedded as a string constant in code; prompt registry entry exists per `.ids` file | `ids/` vs. `docs/prompts/` |
| C13 | `eng-os-reliability-engineering` | Outbound calls have timeouts; retries use jitter and a budget in one layer; queues and pools are bounded; SLOs exist for user-facing flows | Client wrappers, config, SLO docs |
| C14 | `eng-os-platform-infrastructure` (if applicable) | Every production resource is in the infrastructure repo; backups have a restore drill record | Infra repo vs. cloud inventory |
| C15 | `eng-os-privacy-and-governance` (if applicable) | Every dataset has classification, retention, and lineage; no personal data in logs or metric labels; deletion procedure covers every copy | Data dictionary, logging call sites, runbooks |
| C16 | `eng-os-spec-feature` and `eng-os-execute-feature` (if the project has `.specs/` or multi-task features) | Every feature spec has `Status: Approved <date>` on all three files; every acceptance criterion in `requirements.md` appears in a task and has a test or check; `tasks.md` checkboxes match the commit log (one commit per ticked task, in task order); the latest feature's criteria still match its shipped behavior | `.specs/` vs. `git log` and the test directory |
| C17 | `eng-os-data-strategy` (if applicable) | Each pipeline is idempotent under re-run and declares its delivery guarantee and late-data handling; fields with a declared freshness SLA show their staleness to the consumer | Pipeline code, scheduler config, API responses or UI badges |
| C18 | `eng-os-system-design` (if applicable) | A capacity model exists and agrees with `## Scale Targets`; no service shares a database with another or straddles two bounded contexts; every queue and pool is bounded | Architecture docs, service configs |

## Report Template

Write the report to a file (and publish as an Artifact if the user wants it shareable). Structure:

```markdown
# Engineering OS Compliance Report — {project name}

**Audited:** {date}
**Project CLAUDE.md:** {path}
**Engineering OS reference:** {path or "unreachable — noted as limitation"}

## Summary

{One paragraph: overall compliance posture. Lead with the most consequential gaps, not a list of
everything checked. State the Pass/Fail/Partial/N/A/Unknown counts.}

## Findings by Section

### A. Bootstrap Integrity
| # | Status | Evidence |
|---|---|---|
| A1 | Pass/Fail/Partial/N/A/Unknown | {specific file/line or absence cited} |
...

### B. Architecture Practices Gate
{same table shape}

### C. Checkpoint-Table Compliance
{same table shape}

## Where The Agent Has Been Drifting

{This is the section that makes the report useful as feedback on agent behavior, not just project
state. For each Fail/Partial, name the *pattern*, not just the instance: e.g. "message codes are
being skipped specifically on toast notifications, consistently, across 6 files: this looks like a
checkpoint an agent keeps missing on this category of change, not a one-off." Group repeat
patterns together rather than listing every file.}

## Recommended Next Actions

{Ordered by risk/blast-radius, not by file order. Do not fix anything here — this is a punch list
for the user to hand back for remediation, separate from this audit.}
```

## Failure Modes

- **Passing a row on CLAUDE.md prose alone.** A CLAUDE.md that claims MVC beside route handlers full of business logic is a Fail; every row is verified against files, not statements.
- **Rounding Unknown up to Pass.** An unreachable engineering-os path or ambiguous evidence stays Unknown, with the limit named in the report.
- **N/A assigned by the auditor.** A row is N/A only when the project's own CLAUDE.md marked it so; otherwise it is a finding.
- **Auditing the whole history.** Section C samples recent work; a pass over every commit of a mature project never finishes and buries the pattern.
- **Fixing while auditing.** Remediation in the same pass hides how bad the starting state was and removes the user's choice of priority and scope.

## Definition of Done

The audit is complete when: every checklist row has a status backed by cited evidence (not
inferred from CLAUDE.md prose alone); every N/A row was N/A in the project's own CLAUDE.md, not
assumed by the auditor; the report's "Where The Agent Has Been Drifting" section identifies patterns
across findings, not just a flat restatement of the tables; and the report was written to a file
(and published if the user wants it shareable) rather than left only as chat output.

For a worked example, see `references/example.md`.
