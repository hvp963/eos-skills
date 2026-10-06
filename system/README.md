# Engineering OS

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

Most engineering teams have standards, but they live in scattered wikis, stale Confluence pages, and institutional memory that leaves with the people who hold it. When a new engineer joins, when a system grows beyond its original scope, or when AI enters the stack, the gaps become visible fast.

The Engineering OS is a structured body of knowledge that gives a team shared language, non-negotiable principles, design patterns, and implementation standards, in one place, at the right level of detail for each decision. It covers both traditional and AI engineering as equal disciplines under the same principles.

---

## Structure

```
meta/       Language, authoring rules, and glossary — read first
macro/      Non-negotiable principles and quality attributes — the foundation
meso/       Design guides and domain playbooks — how to think about a problem
micro/      Implementation standards and review templates — how to build it
skills/     Skills adapter (open SKILL.md format) — selectively-loaded routing layer over the above
docs/       Architecture Decision Records for the OS itself
evidence/   Ledger of the failures behind each evidence-based rule
```

Each layer builds on the one above. `meso/` guides apply `macro/` principles. `micro/` standards implement `meso/` patterns in real code. `skills/` doesn't add new standards; it's a thin, on-demand-loading adapter over `meta/macro/meso/micro`, built for how AI coding agents consume context.

See `meta/architecture.md` for a visual diagram of the full layer structure, and `skills/MINDMAP.md` for how the skills relate to each other.

---

## How to Start

**Reading the OS as prose (human, or an agent without Skills support):**
1. Read `meta/architecture.md`: orient visually to the layer structure
2. Read `meta/mental-model.md`: understand how the layers relate
3. Read `meta/glossary.md`: get the shared vocabulary
4. Read `macro/principles.md`: internalize the non-negotiables
5. Find the relevant `meso/` guide for the domain you are working in
6. Use `micro/` standards and templates to implement and review

**Using Claude Code as an engineering agent?** Start at `skills/README.md`, not `meta/claude-code-usage.md` directly: the Skills layer is now the primary way Claude Code should consume this OS. Starting a new app or feature invokes `skills/eng-os-plan-app` before any code exists; an existing project without governance invokes `skills/eng-os-bootstrap` directly. `meta/claude-code-usage.md` remains as the canonical prose description of the bootstrap protocol and CLAUDE.md template that `skills/eng-os-bootstrap` implements.

---

## What Is Covered

### Design Guides (`meso/`)
- `api-design.md`: contracts, versioning, rate limiting, pagination
- `code-conventions.md`: naming conventions and comment rules across languages
- `data-strategy.md`: pipelines, schema evolution, idempotency, freshness
- `database-design.md`: schema design, indexing, migration patterns
- `documentation.md`: documentation as a first-class engineering discipline across all disciplines
- `system-design.md`: architecture patterns, C4 model, trade-off analysis
- `observability.md`: logging, metrics, tracing, alerting
- `security.md`: input validation, secrets management, least privilege, AI security
- `testing-strategy.md`: unit, integration, contract, property, AI evaluation
- `deployment.md`: environments, CI/CD, feature flags, rollback, health checks
- `team-practices.md`: code review, pull request standards, incident response, on-call, technical debt
- `ai-deterministic-systems.md`: AI instruction design (AI-IDS framework)
- `prose-style.md`: sentence-level and structural prose quality across thirteen patterns: contrastive-negation overuse, filler words, em dash as a clause joiner (a hard ban), cliché/inflated vocabulary, vague placeholder nouns, reflexive openers, forced balance, fake precision, overexplaining, mechanical formatting, verbatim duplicate content (a hard check), repetitive sentence structure, generic content
- `reliability.md`: SLOs and error budgets, timeouts and deadlines, retries, circuit breakers, bulkheads, load shedding, degradation, chaos
- `infrastructure.md`: infrastructure as code, environment parity, regions and cells, backup and restore, cost attribution
- `data-governance.md`: data classification, personal data, retention and deletion, lineage, access review

### Implementation Standards (`micro/`)
- `project-structure.md`: canonical folder layout, source module organization, `ids/`/`lib/`/`input/`/`output/`/`logs/`/`docs/`/`tests/`, OOP module conventions, naming
- `coding-standards/common.md`: language-agnostic rules: config, user-facing string/message-code constants, error handling, retry, logging, testing, security, documentation, Model-View-Controller layering
- `coding-standards/python.md`: Python implementation: config, error handling, retry, logging, type annotations, testing, docstrings, OOP conventions
- `coding-standards/nodejs.md`: Node.js/TypeScript implementation of common standards including JSDoc

### Templates (`micro/`)
- `design-review-template.md`: structured design review artifact
- `templates/adr-template.md`: Architecture Decision Record template
- `templates/service-template.md`: service scaffolding
- `templates/etl-template.md`: ETL pipeline scaffolding
- `templates/ai-ids-template.md`: blank AI-IDS specification to copy into `ids/` (section-by-section guidance, a worked example, and the review checklist are in `meso/ai-ids-template.md`)

### Claude Code Skills (`skills/`)
28 skills adapting the layers above into the open `SKILL.md` format: an always-on core skill plus 27 selectively-loaded domain, planning, execution, audit, and optimization skills, each with a worked example. Install them with `tools/install.ps1` or `tools/install.sh` so the agent runtime routes to them; `tools/lint-os.py` (run by CI) keeps the skills, their sources, and the counts in this file consistent. See `skills/README.md` for the full list and `skills/MINDMAP.md` for how they relate and which carry the most weight. Not a second standard: a routing layer over the same `meta/macro/meso/micro` content, built for how AI agents consume context.

---

## The AI-IDS Framework

The AI Instruction Design Set (AI-IDS) is a formal framework for authoring AI system instructions the way you would design a software contract, with defined roles, objectives, guardrails, input and output structure, derived logic, and a reasoning policy.

It treats AI instruction design as an engineering discipline, not a prompting art. See `meso/ai-deterministic-systems.md` for the full guide and `meso/ai-ids-template.md` for the authoring template.

---

## AI Agent Usage

**Claude Code:** start at `skills/README.md`, not this section: the Skills layer (`skills/eng-os-core`, `skills/eng-os-bootstrap`, `skills/eng-os-plan-app`) is the primary way Claude Code should consume this OS now, and it supersedes manually reading all 36 prose files.

**Any other AI agent, or reading this as prose:** start at `meta/claude-code-usage.md`. It provides:
- A bootstrap protocol that must complete before any code is written
- A CLAUDE.md template to instantiate at the project root
- A checkpoint map that defines when each standard must be verified
- The drift patterns that cause standards to be missed and how to prevent them

See `skills/PORTABILITY.md` for what it takes to bring the Skills layer to Cursor, GitHub Copilot, OpenAI's Codex CLI, Windsurf, Cline, or Aider.

---

## Notice and Good-Faith Disclaimer

This material is the author's individual point of view, written in good faith and informed by production workloads serving millions of users. It does not represent any employer or organization, and it is not legal, security, compliance, or other professional advice.

Every company's approach differs. Scale, regulation, team size, risk tolerance, and existing architecture all change which standard fits, and some standards here will need adjusting or will not apply at all. Use them as a starting point, and apply your own judgment before relying on any of them in a production or regulated system. The content is provided "as is," without warranty (see `LICENSE`).

Facts about third parties (other frameworks, skill collections, and AI coding tools: their release dates, supported platforms, and figures) were checked against public sources on the dates stated in the text and change quickly. Product and company names belong to their owners, and mentioning one implies no affiliation or endorsement. Comparisons are the author's reading of public documentation.

If anything here has missed the mark, whether it is inaccurate, out of date, or misdescribes your product or approach, please say so by opening an issue (see `CONTRIBUTING.md`, "Reporting an Inaccuracy"), and it will be reviewed and updated.

---

## Contributing

See `CONTRIBUTING.md`.

---

## License

Creative Commons Attribution 4.0 International (CC BY 4.0) for everything under `system/`.
You are free to use, adapt, and redistribute with attribution to the original author.
Code in `tools/` and `.github/` is MIT. See the repository-root `LICENSE` for both texts and the required attribution form.
