---
name: eng-os-core
description: "Always active for any code change in a project governed by the Engineering OS. Holds the non-negotiable principles, the Meta Definition of Done, and the checkpoint table that routes each trigger (new file, contract, schema, pipeline, test, screen, doc, finished task) to the domain skill that must run at that moment. Load this skill first, before touching any file, module, function, test, .ids file, or doc file."
sources:
  - macro/principles.md
  - macro/system-quality-attributes.md
  - meta/mental-model.md
  - meta/glossary.md
  - meta/claude-code-usage.md
globs: ["**/*"]
always_apply: true
verified_platforms: [claude-code]
---

# Engineering OS: Core

The always-loaded root skill. It does not replace the domain skills; it says when to invoke them. Every checkpoint below is a stop condition. Verification criteria live in each domain skill's Definition of Done, so this file stays small.

## Core Principles

Full text: `../../macro/principles.md`.

1. Explicitness over implicitness
2. Determinism within defined boundaries
3. Idempotency by default
4. Contracts as source of truth
5. Validation at boundaries
6. Observability as a first-class concern
7. Fault isolation over global stability
8. Scalability through partitioning
9. Separation of concerns
10. Bounded inference for AI systems
11. Security as a design constraint
12. Testability as a design property

Quality attributes: `../../macro/system-quality-attributes.md`. Vocabulary: `../../meta/glossary.md`.

## The Checkpoint Table

Invoke the named skill when the trigger is hit, run its Definition of Done, then proceed. Worked example: `references/checkpoint-walkthrough-example.md`.

| Trigger | Invoke |
|---|---|
| Project has no CLAUDE.md with `## Engineering Standards` | `eng-os-bootstrap` |
| Feature scope approved at the spec threshold (3+ tasks, contract or entity change, edge cases, or ambiguity), no `.specs/<feature>/` yet | `eng-os-spec-feature` |
| Spec approved (`tasks.md` exists), or the change is small enough to need no spec | `eng-os-execute-feature` |
| Any design review, capacity decision, load test, or cost budget | check `## Scale Targets` in CLAUDE.md; `eng-os-system-design` |
| New source file | `eng-os-coding-standards-common` + `eng-os-coding-standards-python` or `eng-os-coding-standards-nodejs` |
| Any naming decision (variable, file, class, constant, env var, term) | `eng-os-code-conventions` (Terminology Lock) |
| New user-facing message | `eng-os-coding-standards-common` Standard 3: unique `{AAA}{NNNNNN}` code from the project's Message Area Codes |
| Public function complete | language coding-standards skill |
| Route, page, or command handler, or its business logic | `eng-os-coding-standards-common` Standard 13 (MVC) |
| Endpoint, event, or schema contract | `eng-os-api-design` |
| Table, index, or migration | `eng-os-database-design` |
| Data pipeline, batch or streaming job, ingestion, or a freshness SLA | `eng-os-data-strategy` |
| Outbound call, timeout, retry, queue bound, or SLO | `eng-os-reliability-engineering` |
| Input validation, auth, authz, secrets, or a trust boundary | `eng-os-security-practices` |
| Personal, regulated, or classified data; retention; deletion; third-party transfer | `eng-os-privacy-and-governance` |
| Log, metric, trace, or alert | `eng-os-observability` |
| Test file | `eng-os-testing-strategy` |
| Pipeline, environment, flag, migration ordering, or rollback | `eng-os-deployment-practices` |
| Infrastructure resource, region or cell layout, backup | `eng-os-platform-infrastructure` |
| Screen, component, style, or UI copy | `eng-os-design-system` + `eng-os-prose-style` |
| ADR, contract doc, runbook, model card, prompt registry entry | `eng-os-documentation-standards` + `eng-os-prose-style` |
| README, commit message, PR description, or any persisted prose | `eng-os-prose-style` |
| Code review, PR, incident, or on-call process | `eng-os-team-practices` |
| `.ids` file | `eng-os-ai-ids-authoring` |
| Tuning the agent workflow's cost, latency, or context | `eng-os-model-optimization` |
| Generic vs. project-specific split in any doc | `eng-os-doc-authoring-rules` Core Rule 11 |
| Marking a task done | Meta Definition of Done below, plus `eng-os-execute-feature` Verify and Commit if a task list is active |
| Session ends | `eng-os-documentation-standards`: an ADR for every decision meeting its threshold |

**Checkpoint failures are blockers, not warnings.** Skipping a checkpoint is drift, regardless of output quality.

## Meta Definition of Done

Before marking any task complete, for every skill invoked during that task:

> Did you run that skill's own Definition of Done, and did it pass?

A task is done only when every checkpoint it crossed had its skill's Definition of Done run and passing.

## Session-End Rule

Write an ADR for every decision that meets the threshold in `eng-os-documentation-standards`; cheaper local choices go in the commit message.
