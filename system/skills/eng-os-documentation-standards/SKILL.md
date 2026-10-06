---
name: eng-os-documentation-standards
description: "Use when writing ADRs, API/data contracts, release notes, or runbooks; defines what documentation is required per discipline and its Definition of Done."
sources: [meso/documentation.md, micro/templates/adr-template.md, micro/templates/release-notes-template.md]
globs: ["**/docs/**", "**/README*", "**/runbooks/**", "**/decisions/**"]
always_apply: false
verified_platforms: [claude-code]
---

# Documentation Standards

Documentation ships with the work, not after it. **The core rule: if a system change affects
behavior, its documentation changes in the same commit or PR.** Every doc must declare an owner
and a lifecycle state (`Draft` / `Current` / `Deprecated` / `Archived`) at the top:

```
Status: Current
Last Reviewed: 2026-05-31
Owner: commerce-data-team
```

Deprecated docs must reference what supersedes them. Never delete a doc from version control;
archive it.

## What to Write, by Discipline

| Type | Discipline | Where It Lives |
|---|---|---|
| ADR | All | `docs/decisions/` or `adr/` |
| API Reference | Software | OpenAPI spec, README, or docs site |
| Data Contract | Data | Schema registry, `docs/contracts/` |
| Data Dictionary | Data | `docs/data/` or warehouse docs |
| Runbook | Ops / Infra | `docs/runbooks/` or ops wiki |
| Model Card | ML / AI | `docs/models/` or model registry |
| Prompt Registry | AI | `docs/prompts/` or AI system registry |
| Evaluation Log | AI | `docs/eval/` or experiment tracker |
| Onboarding Guide | All | `docs/onboarding/` or team wiki |
| Design Document | All | `docs/design/` or linked in PRs |
| Release Notes | Product / Platform | Customer portal, docs site, email |
| API Changelog | Software | Docs site, `CHANGELOG.md`, API reference |
| Migration Guide | Software / Platform | Docs site, linked from release notes |

Organize by decision layer, not by team: **Decision** (ADRs, trade-off records) → **Design**
(diagrams, design docs) → **Contract** (API specs, data contracts, SLAs) → **Operational**
(runbooks, playbooks) → **Code** (docstrings, inline comments, module READMEs). A runbook does not
belong in a design document; an ADR does not belong in a docstring.

## When an ADR Is Required

Write an ADR when:
- choosing between two or more non-trivial technical approaches
- adopting or deprecating a platform, library, or pattern
- making a trade-off with long-term consequences (consistency vs. availability, build vs. buy)
- establishing a standard that will govern future work

ADRs are immutable once accepted. If a decision changes, write a new ADR that supersedes the old
one; mark the old one `Superseded by ADR-NNN`, do not delete it.

### ADR Template (skeleton)

Shape only; full section-by-section guidance lives in the canonical template.

```markdown
# Architecture Decision Record — [Title]
## Metadata          (ADR number, status, date, owner, supersedes)
## Context            (forces, constraints, why now)
## Decision           (the decision + why over alternatives)
## Consequences       (Accepted Trade-offs / Doors Closed / Benefits)
## Alternatives Considered
## Validation         (signals that would indicate revisiting it)
## References
```

Full template: `../../micro/templates/adr-template.md`. See `references/example.md` for a
filled-in instance.

### When an ADR Is Not Required

An ADR is required when at least one holds: expensive to reverse (schema shape, storage engine,
public contract, a dependency others build on); deviates from a documented pattern in this OS or
the project's CLAUDE.md; changes a Terminology Lock term, a Message Area Code, or a Scale Target;
or two or more viable approaches were considered and a later reader could reasonably ask why. A
local, cheap-to-reverse choice that follows the pattern goes in the commit message. Test: "would
a new engineer six months from now need this to avoid re-litigating it?"

## Contract, API, and Runbook Minimums

- **API docs** must be co-located with or linked from the code, versioned, complete (every
  endpoint/field/error code/auth mechanism), and reviewed whenever behavior changes.
- **Data Contract** must define: schema (names/types/nullability), semantics, compatibility policy
  (additive-only / backward-compatible / versioned-breaking), SLA (freshness, availability,
  quality), and owner.
- **Data Dictionary** must define: canonical field name, business definition, allowed values or
  range, source system/derivation, known issues.
- **Runbook** must include: what the system does (one paragraph, no assumed context), how to
  confirm health, common failure symptoms and causes, step-by-step recovery per known failure
  mode, and an escalation path. See `references/runbook-example.md` for a worked example.
- **Model Card** (ML/AI) must include: purpose/intended use, training data summary and known
  biases, performance characteristics, known limitations/failure modes, usage policy.
- **Prompt Registry** entries must include: version id, intent, input/output schema, evaluation
  results (determinism rate, constraint violation rate, schema compliance rate), change history.
- **Evaluation Log** entries must include: date and model version, input dataset, metrics,
  pass/fail against thresholds, known regressions.

## External / Customer-Facing Documentation

External readers have no access to the codebase, incident history, or team: state every
assumption and describe impact in customer terms, not implementation terms.

- **Lead with customer value.** Answer "what can I do now that I couldn't before?" not "what did
  we refactor."
- **Distinguish behavioral changes (automatic, no action needed) from breaking changes (customer
  must act or it fails).** Conflating them erodes trust.
- **Hide empty sections entirely.** An empty "Known Issues" with a dash means "we checked"; an
  omitted section is honest, a visible-but-empty one looks like negligence.
- **Cap "Why It Matters" at three bullets**, ranked by impact.

| Section | Include when | Label |
|---|---|---|
| New Features | Net-new capabilities | `NEW` |
| Enhancements | Improvements to existing behavior | `IMPROVED` |
| Updated Behavior | Automatic behavior change; may surprise users | `HEADS UP` |
| Bug Fixes | Issues resolved | `FIXED` |
| Breaking Changes | Customer must act to avoid breakage | `ACTION REQUIRED` |
| Deprecations | Features phased out with an end-of-life date | `DEPRECATING` |
| Known Issues | Outstanding issues at ship time | `KNOWN` |
| Why It Matters | Always, max 3 bullets | (n/a) |

Full authoring template (with authoring notes and section-inclusion rules): see
`../../micro/templates/release-notes-template.md`.

## Review Standards

A PR that changes system behavior must include the doc changes in the same PR. Documentation-only
PRs need review by an engineer with operational knowledge of the system.

```
□ Does it describe current behavior, not intended behavior?
□ Is the owner declared?
□ Is the lifecycle state declared?
□ Are all boundary conditions and failure modes covered?
□ Can an engineer act on this without reading the source code?
□ Does it reference related documentation (contracts, runbooks, ADRs)?
```

This checklist covers what the doc contains and its structure. It does not cover how the sentences
themselves read: before marking any doc done, also run the `eng-os-prose-style` skill's Definition of
Done on its prose.

## Definition of Done

- [ ] Every production-facing interface has current contract documentation
- [ ] At least one ADR exists capturing the primary technology and architecture choices
- [ ] A runbook exists with at minimum: health check, one failure recovery procedure, escalation path
- [ ] All documentation declares owner and lifecycle state
- [ ] Documentation was reviewed in the same PR as the code change that affected behavior
- [ ] AI systems have a current prompt registry entry and at least one evaluation log
- [ ] ADRs exist for every decision meeting the threshold above; cheaper local choices are recorded in commit messages instead
