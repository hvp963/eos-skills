# Architecture Decision Record: Workflow Skill Naming and Who Owns Task Breakdown

**Authors:** Haresh V. Parekh

---

## Metadata

| Field | Value |
|---|---|
| ADR Number | ADR-004 |
| Status | Accepted |
| Date | 2026-10-02 |
| Owner | Haresh V. Parekh |
| Supersedes | none |

## Context

A spec stage (requirements, design, tasks) in front of the task loop raises two questions. First,
what to call the two skills so the pair reads as one lifecycle. Second, which skill decomposes a
feature into tasks: both could, and two places defining the task format would drift.

The skill set already has two kinds of name. Domain skills hold standards an agent consults and
are named for their subject (`eng-os-api-design`, `eng-os-observability`). Workflow skills are
procedures run in sequence and are named for the action (`eng-os-plan-app`, `eng-os-bootstrap`,
`eng-os-audit`). The two feature skills need names that follow the workflow pattern.

## Decision

1. Workflow skills are named verb-first: `eng-os-plan-app`, `eng-os-bootstrap`,
   `eng-os-spec-feature`, `eng-os-execute-feature`, `eng-os-audit`. Domain skills stay named for
   their subject.
2. The pair is `eng-os-spec-feature` (what to build) and `eng-os-execute-feature` (build it,
   task by task).
3. When an approved spec exists, `eng-os-spec-feature` owns task breakdown and writes `tasks.md`.
   `eng-os-execute-feature` adopts it in Phase 1 and decomposes inline only when there is no
   spec. The task fields and the vertical-slice rule stay defined once, in
   `eng-os-execute-feature` Phase 1; the spec skill adds one field, Requirements.

## Consequences

### Accepted Trade-offs
- The always-loaded checkpoint table in `eng-os-core` gains a second row for the feature stage.

### Doors Closed
- Renaming either skill later costs a hand edit of every CLAUDE.md that adopted the name, because no alias or stub is offered.

### Benefits
- The lifecycle reads in order by name (plan, spec, execute), and the task format has one definition.

---

## Alternatives Considered

### Alternative 1: Noun-style names, `eng-os-feature-execution` and `eng-os-feature-spec`

**What it is:** the two names sort together because they share a noun prefix.

**Why rejected:** it gives the workflow skills domain-style names and no rule for the next workflow skill's name.

### Alternative 2: `eng-os-exec-feature` or `eng-os-execution-feature`

**What it is:** a verb-first or noun-first variant of the pair that abbreviates or nominalizes "execute".

**Why rejected:** an abbreviation is inconsistent with the rest of the set, and "execution" is a noun where the other workflow names are verbs.

### Alternative 3: Both skills decompose independently

**What it is:** `eng-os-spec-feature` writes requirements and design, and each skill breaks scope into tasks itself.

**Why rejected:** two definitions of the task format would drift, and a spec's traceability depends on its tasks being the ones that run.

---

## Validation

Revisit if audits find agents invoking the wrong skill of the pair, or if a project's
`tasks.md` and its execution-time task list disagree.

## References

- `meta/claude-code-usage.md` 2.2
- `evidence/ledger.md` E-06 and E-29
- `skills/eng-os-spec-feature/SKILL.md`, `skills/eng-os-execute-feature/SKILL.md`
