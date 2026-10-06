---
name: eng-os-plan-app
description: "Use at the very start of a new app or major feature, before any code is written or CLAUDE.md is created. Turns a one-paragraph idea into a Product Brief covering entities, screens, phased scope, and terminology. Feeds directly into the eng-os-bootstrap skill."
sources:
  - meta/claude-code-usage.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Plan App

This skill runs a planning conversation before a single file is created. It exists because
teams repeatedly started implementation from a one-paragraph idea, then discovered mid-build
that entities, screens, and core terminology were never agreed on. This caused rewrites and, in
at least one real project, three separate mid-build renames of the same core concept, each of
which touched the whole codebase. Asking the questions below up front is strictly cheaper than
that.

Do not scaffold, generate schema, or write any code during this skill. The only output is a
Product Brief, presented back to the user for approval.

## Phase 1 — Discovery

Given a one-paragraph app idea, do not assume; ask. At minimum:

- **Audience**: who uses this app? Who is it presented to or approved by? (These can differ:
  e.g. an internal tool used by analysts but demoed to an executive.)
- **Suite membership**: is this a standalone app or part of a multi-app suite? If part of a
  suite: what already exists, what port/URL does it claim, what does it inherit (design system,
  entities, terminology) vs. what is genuinely new here?
- **Core problem**: what problem does this app solve, in one sentence, independent of how it's
  built? What does the world look like if this app didn't exist?

Do not proceed to Phase 2 until these are answered or explicitly deferred by the user.

## Phase 2 — Domain Modeling

Produce a **Core Entities** list before any schema or code exists. For each entity capture:

- **Name**: the canonical name (see Phase 4; do not let this drift later)
- **Purpose**: one sentence, why this entity exists
- **Key fields**: the fields that matter to the mental model, not a full schema

Keep this at the mental-model level. Relationships between entities matter more here than field
types or constraints.

## Phase 2b — Scale Targets

Before screens, put numbers on the non-functional requirements. Adjectives ("fast", "lots of
users") are placeholders, not answers. Capture:

- **Users and traffic**: expected users at launch and in three years; peak requests per second
- **Data**: volume now and growth per year; the largest single tenant's share
- **Latency and availability**: p50/p99 targets per key flow; availability target per month
- **Recovery**: RPO and RTO
- **Tenancy**: single-tenant, shared tables with `tenant_id`, schema-per-tenant, or per-tenant databases
- **Data classification**: highest level held (Public / Internal / Confidential / Restricted) and regulatory scope

These become the `## Scale Targets` section of CLAUDE.md and are what `eng-os-system-design`'s
capacity model, `eng-os-reliability-engineering`'s SLOs, `eng-os-testing-strategy`'s load tests, and
`eng-os-platform-infrastructure`'s backups are checked against. If the user genuinely does not know a
number, record the assumption and mark it as one; an assumed number can be revised, an absent
one cannot be checked.

## Phase 3 — Screens and Flows

Enumerate every screen/page before any UI code exists. For each screen capture:

- **Name**: the canonical screen/page title
- **Data requirements**: which Core Entities (from Phase 2) it reads or writes
- **Primary user action**: the one thing this screen exists for the user to do

If a screen doesn't map to at least one entity and one clear action, question whether it's
actually needed or is scope creep.

## Phase 4 — Terminology Lock

For every core noun and verb in the domain (entity names, key actions, page titles), decide
and record the canonical term now. This is a deliberate, explicit decision, not a first-draft
guess: once locked, the team commits to not renaming opportunistically mid-build.

- Write each term down alongside any rejected alternatives, so the reasoning is preserved and
  a repeat debate doesn't resurface the same alternative later.
- If a rename is later found to be genuinely necessary, it must be executed as one deliberate,
  complete pass across the whole codebase in a single change, never as incremental drift where
  old and new names coexist.
- Flag any term that is a close synonym of a term used in a sibling app in the suite (e.g.
  "asset" vs. "entity" vs. "record") and resolve the ambiguity now.

## Phase 5 — Phased Milestones

Break scope into phases, not one big-bang delivery. For each phase capture:

- **Name/number** and **one-line goal**
- **Scope**: which entities and screens (from Phases 2–3) are included
- **Definition of done**: an observable, checkable condition, not "it works"

Prefer 3-5 phases for a first app. Each phase should be independently demoable.

## Phase 6 — Design System Carryover (only if part of a multi-app suite)

If Phase 1 established this app is part of a suite:

- Declare which sibling app's design system this inherits from, **by reference/path** (e.g.
  "same visual language as `data-catalog`, see its CLAUDE.md Design System section"),
  never by retyping color tokens, component classes, or CSS variables into this brief.
- Note anything genuinely new/different from the inherited system, and why.

If this app is standalone, mark this section **N/A** rather than skipping it silently.

## Phase 7 — Mock Data Scale (if applicable)

If the app needs seed/demo data:

- How many records per entity are needed for a convincing demo?
- Any specific edge cases the mock data must include (e.g. an entity with no owner, a
  deprecated version, an empty state)?

If not applicable, mark **N/A**.

## Phase 8 — Approval Gate

Assemble everything above into the Product Brief (see Output Contract below) and present it
back to the user for explicit confirmation. Do not proceed to `eng-os-bootstrap` or write any
scaffolding until the user approves. If the user requests changes, revise and re-present; do
not partially proceed on an unapproved brief.

## Output Contract

Structure the Product Brief with these headings, in this order, so it can be transcribed
directly into CLAUDE.md by `eng-os-bootstrap` rather than reformatted:

1. **Platform Context** (from Phase 1: suite membership, sibling apps, ports)
2. **Audience and Framing** (from Phase 1: audience, framing pillars/problem statement)
3. **Core Entities** (from Phase 2)
4. **Screens and Flows** (from Phase 3)
5. **Scale Targets** (from Phase 2b)
6. **Design System Carryover** (from Phase 6, or `N/A`)
7. **Mock Data Scale** (from Phase 7, or `N/A`)
8. **Terminology Lock** (from Phase 4)

Phased Milestones (Phase 5) accompanies the brief as delivery planning but is not itself a
CLAUDE.md section. Hand it to `eng-os-bootstrap` alongside the brief so phase 1 scaffolding
matches phase 1 scope.

## Failure Modes

- **Adjectives in place of numbers.** "Fast" and "lots of users" cannot be checked later; Phase 2b records numbers and marks guesses as assumptions (ledger E-17: systems sized by guesswork found their bottleneck at launch).
- **Terminology left unlocked.** A concept renamed mid-build touches code, UI, docs, and tests (E-02: one app renamed a core concept three times); Phase 4 fixes the nouns and verbs before any exist.
- **A screen with no entity or action.** Every screen reads or writes at least one entity and has one primary action; a screen with neither is scope creep from Phase 3.
- **Phases too large to demo.** A phase that cannot be demonstrated alone has no Definition of Done a user can check; prefer three to five phases for a first app.
- **Proceeding on an unapproved brief.** Scaffolding or code before the Phase 8 approval locks in decisions the user has not confirmed.

## Definition of Done

Before invoking `eng-os-bootstrap`, confirm: every section above is populated or explicitly
marked N/A, the user has approved the brief, and no implementation code has been written yet.

For a full worked example of this nine-step flow (Phases 1 to 8 plus Phase 2b) on a concrete app idea, see
`references/plan-example.md`.
