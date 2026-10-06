---
name: eng-os-code-conventions
description: "Use when naming variables, files, classes, constants, or env vars, or applying comment conventions. Language-agnostic."
sources:
  - meso/code-conventions.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Code Conventions

Names must communicate intent without requiring a comment or external lookup. Rules are
language-agnostic; where casing differs by idiomatic language convention, both are stated.

## Naming Conventions

| Construct | Rule | Examples |
|---|---|---|
| Variables / functions | `snake_case` in Python; `camelCase` in TypeScript (ADR-001). Wire names (JSON fields, DB columns, env vars, message codes) stay `snake_case` in both; TypeScript maps once at the validated boundary | `load_checkpoint` / `loadCheckpoint`; JSON `customer_id` becomes `customerId` in the zod transform |
| Constants | `UPPER_SNAKE_CASE` in all languages | `RETRY_MAX_ATTEMPTS`, `AI_MODEL`, `DEFAULT_TIMEOUT_SECS` |
| Classes | `PascalCase` in all languages | `MediaAgent`, `CheckpointManager` |
| Files / modules | `snake_case` (Python), `kebab-case` (TypeScript/Node) — pick one per project | `media_agent.py`, `media-agent.ts` |
| Env vars | `UPPER_SNAKE_CASE`, domain-prefixed where ambiguity possible | `AI_MODEL`, `IMAGE_API_KEY`, `RETRY_MAX_ATTEMPTS` |
| Booleans | prefix `is_`, `has_`, `can_`, or `allow_` | `is_valid`, `has_checkpoint`, `can_retry`, `allow_override` |

Never mix snake_case and camelCase within a single file. Never use generic names (`data`, `value`,
`result`, `temp`, `obj`) without a qualifying prefix; if a name needs a comment to explain what it
is, it has failed the naming requirement. Generic env var names (`API_KEY`, `SECRET`) collide
across integrations and cause silent misconfiguration; always domain-prefix when more than one
external integration is in play.

TypeScript casing was decided in `../../docs/decisions/ADR-001-typescript-casing.md` (Accepted
2026-09-01): camelCase in code, snake_case at the wire, mapped once at the boundary. A project
may declare snake_case for TypeScript in its CLAUDE.md; either way the choice is declared once
and never mixed within a file.

## Inline Comment Conventions

Write a comment only when the WHY is not obvious from the code itself:
- a non-obvious constraint or invariant
- a deliberate workaround for a specific external limitation
- a default/threshold value whose origin isn't self-evident

Do not restate what the code already says:
```python
# Bad — restates the obvious
i += 1  # increment i

# Good — explains why
retry_delay *= 2  # exponential backoff — doubles on each attempt
```

**Placement:** explanatory comments go on the line above the code; inline end-of-line comments
only for brief value annotations (e.g. `# seconds`). **Style:** single `#` with one space; full
sentences above-line, sentence fragments inline.

**Length:** an explanatory comment fits in one or two sentences above the line it documents. If
stating the WHY needs a third sentence, the constraint is complex enough to belong in an ADR or
design doc, referenced by a short pointer comment (`# see ADR-019 for why this excludes brand
scoring`), not restated in full at the call site.

**Do not use:** multi-line block comments for logic that should be self-describing; comments that
name the caller or feature ("added for X flow"); comments narrating the code's own revision
history (referencing plan/ADR/ticket numbers, "this used to...", "originally this was...", "the
bug this fixes," "the incident this closes"): that content belongs in the commit message and the
ADR itself, not living permanently in source as a comment block; a comment explains the code as it
stands today, not how it got here; TODO/FIXME in production specifications: these indicate
incomplete design, not acceptable uncertainty.

```python
# Bad — narrates revision history instead of present-day rationale
# PLAN-29 originally used one call here, but that exceeded the SDK's 60s
# timeout and silently dropped fields, so ADR-025 split it into 6 calls.
# See the incident this closed in docs/incidents/sdk-timeout.md.
results = run_parallel_calls(specs)

# Good — states the current constraint in one line, points elsewhere for history
results = run_parallel_calls(specs)  # split to stay under the SDK's 60s per-call timeout; see ADR-025
```

## Terminology Lock

Core domain nouns and verbs (entity names, key action names, page/section titles) are structural,
not cosmetic. Decide the canonical term for every core entity, action, and major UI surface
**before implementation begins**, and treat that list as part of the design, on par with a schema.
Canonical rationale: see `eng-os-plan-app` skill, Phase 4 (Terminology Lock).

A deliberate, versioned rename done in a single complete pass (code identifiers, UI text, docs,
comments, and tests updated together) is fine. The failure mode is not renaming itself: it's
incremental, unplanned drift, a name changed "in passing" while doing unrelated work, left to
coexist with the old name across the codebase with no one able to tell which is current. A rename
of a core term still warrants an ADR (see `eng-os-documentation-standards` skill) recording why the old
name was inadequate and confirming the new name is final.

## Failure Modes

- mixed casing within a file signals undeclared or inconsistent conventions
- generic names require comments to be understood, defeating the naming requirement
- boolean names without prefixes create ambiguity at call sites
- environment variable name collisions cause silent misconfiguration
- self-evident comments train readers to skip all comments, including the important ones
- changelog-narration comments (plan/ADR numbers, "this used to," "originally") accumulate
  permanently in source instead of living once in the commit message or ADR where they belong,
  and read as an AI (or a human) narrating its own diff rather than documenting the code
- unlocked terminology drifts mid-project, leaving old and new terms coexisting and confusing both
  humans and agents about which is current

## Definition of Done

- [ ] All names are self-describing without a supporting comment
- [ ] Casing follows the declared convention for the language and construct type
- [ ] Environment variables are domain-prefixed where integration overlap exists
- [ ] Boolean names carry an explicit `is_`, `has_`, `can_`, or `allow_` prefix
- [ ] Comments explain only the non-obvious WHY, not the visible WHAT
- [ ] No comment narrates its own revision history (plan/ADR/ticket numbers, "this used to,"
  "the incident this closes"); that content lives in the commit message and ADR instead
- [ ] No explanatory comment runs longer than two sentences; a longer rationale is moved to an
  ADR or design doc and referenced by a short pointer
- [ ] No TODO/FIXME comments exist in production code or specifications
- [ ] Core domain terminology was decided before implementation and has not silently drifted; any rename was a single complete pass across code, UI, docs, and tests

For a worked example, see `references/example.md`.
