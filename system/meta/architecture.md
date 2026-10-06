# Engineering OS — Architecture

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

Most engineering teams have standards, but they scatter across wikis, live in people's heads, and collapse the moment the team grows or AI enters the stack. The Engineering OS solves this by separating *what is non-negotiable* (principles) from *how to think about a domain* (design guides) from *how to build it* (implementation standards), each layer explicit, versioned, and independently useful. When all four layers are coherent, a new engineer or an AI agent can make correct decisions without tribal knowledge.

Each layer constrains the one below it. Principles govern quality attributes. Quality attributes govern design guides. Design guides govern implementation standards. The flow is always top-down; overrides are explicit violations, not ambiguities.

This document is the authoritative structural reference. It explains what each layer is, what lives in it, how layers relate to each other, how cross-cutting concerns are handled, and how to route any engineering decision to the right starting point.

## Definition

### What This Is
The structural reference for the Engineering OS: what each of the four layers (meta, macro, meso, micro) holds, how they constrain one another, and how cross-cutting concerns and the AI-IDS framework cut across them.

### What This Is Not
- not a standard itself: it points to the layer documents that carry the rules
- not an installation guide for the skills (see `skills/README.md`)
- not a changelog or a decision log (see `CHANGELOG.md` and `docs/decisions/`)

## Scope
- Level: Meta
- Applies To: anyone adding, reading, or reorganizing OS documents, and agents deciding which layer a rule belongs in
- See Also: `meta/mental-model.md`, `meta/document-authoring-guidelines.md`, `meta/glossary.md`

---

## Layer Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║  META LAYER  —  How to Navigate and Maintain the OS                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  mental-model.md  ·  glossary.md  ·  document-authoring-guidelines   ║
║  architecture.md (this file)  ·  claude-code-usage.md               ║
╚══════════════════════════════════════════════════════════════════════╝
                                    │
                               constrains
                                    │
                                    ▼
╔══════════════════════════════════════════════════════════════════════╗
║  MACRO LAYER  —  Non-Negotiable Principles and Quality Dimensions    ║
╠══════════════════════════════════════════════════════════════════════╣
║  principles.md (12 principles)  ·  system-quality-attributes.md      ║
╚══════════════════════════════════════════════════════════════════════╝
                                    │
                               constrains
                                    │
                                    ▼
╔══════════════════════════════════════════════════════════════════════╗
║  MESO LAYER  —  Domain Design Guides and Patterns                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  api-design         system-design       data-strategy                ║
║  database-design    observability       security                     ║
║  testing-strategy   deployment          documentation                ║
║  ai-deterministic-systems  (AI-IDS)     ai-ids-template              ║
║  code-conventions   team-practices     design-system                 ║
╚══════════════════════════════════════════════════════════════════════╝
                                    │
                               constrains
                                    │
                                    ▼
╔══════════════════════════════════════════════════════════════════════╗
║  MICRO LAYER  —  Implementation Standards and Templates              ║
╠══════════════════════════════════════════════════════════════════════╣
║  project-structure.md                                                ║
║  coding-standards/                                                   ║
║    common.md  ·  python.md  ·  nodejs.md                             ║
║  templates/                                                          ║
║    adr-template  ·  service-template  ·  etl-template                ║
║    release-notes-template  ·  base-styles.css                        ║
║  design-review-template  ·  ai-ids-template                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Design Philosophy

The Engineering OS is built on a single premise: **most engineering drift comes from missing or misaligned abstraction layers, not from individual bad decisions.**

When principles are tacit, every team invents its own. When design guides are absent, every system re-solves the same problems. When implementation standards are unwritten, code quality is person-dependent. This OS makes all three layers explicit, versioned, and navigable.

Three rules govern the architecture:

**1. Each layer has one job.**
Meta is not Macro. Macro is not design guidance. Design guidance is not code standards. Mixing layers creates confusion about what is negotiable and what is not.

**2. Constraints flow downward; feedback flows upward.**
A meso guide cannot override a macro principle. A micro standard cannot override a meso pattern. However, friction surfaced at the micro level (a pattern that cannot be implemented cleanly, a trade-off that breaks a principle) is a signal to revise the layer above.

**3. Every file must be independently executable.**
No file should require reading another file to be useful. References are navigation aids, not dependencies. If a meso guide requires you to have read three other documents to apply it, it is incomplete.

---

## Layer Reference

### META - Language, Structure, and Authoring Discipline

**Purpose:** Defines how the Engineering OS should be understood, navigated, and maintained. Meta files do not make engineering decisions: they govern how the OS governs itself.

**Start here when:** You are new to the OS, you are onboarding someone, or you are adding or revising content.

| File | What It Contains |
| --- | --- |
| `architecture.md` | Full structural reference - layers, files, constraints, cross-cutting concerns, decision routing |
| `mental-model.md` | Conceptual model - how layers relate and how work flows through them |
| `document-authoring-guidelines.md` | Rules for writing and maintaining OS documents: structure, language, anti-patterns |
| `glossary.md` | 100+ defined terms; the shared vocabulary for all other layers |
| `claude-code-usage.md` | Bootstrap protocol, CLAUDE.md template, and checkpoint map for AI agent engagements |
| `agent-operations.md` | How an AI agent manages its own context, cost, parallelism, and scope while applying the OS |

**Key rule:** Every document in the OS must pass this test: *"If an engineer or AI agent used only this file plus the glossary, could they make materially better decisions?"* If no, the file needs more substance.

---

### MACRO - Non-Negotiable Principles and Evaluation Dimensions

**Purpose:** Establishes the rules no downstream layer can override. Macro does not describe how to build systems: it defines the constraints all systems must satisfy. A design guide that violates a macro principle is wrong, not different.

**Start here when:** You are making an architectural decision, evaluating a trade-off, or reviewing a design for compliance.

| File | What It Contains |
| --- | --- |
| `principles.md` | 12 foundational principles; each with: Rule, Why, Applies To, Implications, Example, Failure Mode |
| `system-quality-attributes.md` | 11 quality dimensions (e.g., availability, observability, security); each with: Definition, Design Levers, Trade-Offs, Example, Review Questions |

**Key rule:** Macro files contain constraints, not guidance. If something is negotiable depending on context, it belongs in a meso guide, not in Macro.

**How Macro constrains Meso: example:**
If a principle states "all system boundaries must be observable," then every meso guide (API design, data strategy, deployment, AI systems) must address how that domain satisfies observability. A meso guide that ignores the constraint is incomplete.

---

### MESO - Domain Design Guides and Patterns

**Purpose:** Translates macro constraints into domain-specific design patterns, trade-off analysis, and architectural guidance. Meso is where principles become actionable. All patterns are expressed in pseudocode or prose, never in language-specific code (that lives in Micro).

**Start here when:** You are designing a system, API, pipeline, database schema, AI instruction set, deployment strategy, or any domain artifact.

| File | Domain | What It Covers |
| --- | --- | --- |
| `api-design.md` | API Engineering | Contracts, versioning, rate limiting, pagination, error schemas, backwards compatibility |
| `system-design.md` | Architecture | C4 model usage, architecture patterns, trade-off analysis, decomposition strategies |
| `data-strategy.md` | Data Engineering | Pipeline design, schema evolution, idempotency, data freshness, lineage |
| `database-design.md` | Data Persistence | Schema design, indexing, migration patterns, normalization trade-offs |
| `observability.md` | Operations | Structured logging, metrics, distributed tracing, alerting, SLO design |
| `security.md` | Security | Input validation, secrets management, least privilege, AI-specific security, threat modeling |
| `testing-strategy.md` | Quality | Unit, integration, contract, property-based, AI evaluation, test pyramid |
| `deployment.md` | Platform/Ops | Environments, CI/CD pipelines, feature flags, rollback, health check standards |
| `documentation.md` | Documentation | ADRs, API contracts, data contracts, runbooks, model cards, prompt registries, release notes, lifecycle ownership |
| `design-system.md` | UI / Documents | Design tokens, typography hierarchy, component patterns (cards, badges, tables, callouts), the four-region app shell (header/footer/nav/application panel), responsive breakpoints, layout principles, reference CSS |
| `code-conventions.md` | Code Style | Naming conventions, comment rules, cross-language style consistency |
| `ai-deterministic-systems.md` | AI Engineering | AI-IDS framework - full guide for authoring deterministic AI instruction sets |
| `ai-ids-template.md` | AI Engineering | Authoring template for AI-IDS artifacts (also mirrored in micro/templates/) |
| `team-practices.md` | Team Operations | Code review standards, pull request standards, incident response, on-call, technical debt management |
| `prose-style.md` | Writing Quality | Thirteen patterns of prose that reads as unedited AI output: contrastive-negation overuse, filler intensifiers, em dash joining clauses (a hard ban), cliché/inflated vocabulary, vague placeholder nouns, reflexive openers, forced balance, fake precision, overexplaining, mechanical formatting, verbatim duplicate content (a hard check), repetitive sentence structure, and generic content with no concrete example |
| `reliability.md` | Reliability Engineering | SLOs and error budgets, timeouts and deadlines, retries, circuit breakers, bulkheads, load shedding, graceful degradation, chaos exercises |
| `infrastructure.md` | Platform Infrastructure | Infrastructure as code, environment parity, regions and cells, backup and restore, cost attribution |
| `data-governance.md` | Privacy and Data Governance | Classification, personal data handling, retention and deletion, lineage, access review, third-party and AI-model transfers |

**Key rule:** Meso files contain patterns and trade-offs, not rules. They explain how to make decisions in a domain, not which single decision is always correct. When a meso guide reads like a policy document, it has drifted into macro territory.

**How Meso constrains Micro: example:**
If the observability guide specifies that structured logs must include `trace_id`, `span_id`, and `severity`, then the Python and Node.js coding standards must implement those fields consistently. A coding standard that uses different field names is non-compliant.

---

### MICRO - Implementation Standards and Templates

**Purpose:** Provides the execution artifacts engineers use when writing code, reviewing designs, and scaffolding systems. Micro files contain real code, checklists, and templates, not principles or patterns.

**Start here when:** You are writing code, reviewing a PR, scaffolding a new service or pipeline, or preparing a design review.

#### Structure and Organization

| File | What It Covers |
| --- | --- |
| `project-structure.md` | Canonical project folder layout: `src/` for source, `ids/` at project root for AI-IDS specs, `input/`/`output/`/`logs/` as pipeline boundaries, OOP module-level conventions, naming conventions |

#### Coding Standards

| File | What It Covers |
| --- | --- |
| `coding-standards/common.md` | 13 language-agnostic standards: configuration (incl. user-facing string/message-code constants), error handling, retry logic, logging, security, testing, documentation baseline, component boundaries/OOD, Model-View-Controller layering |
| `coding-standards/python.md` | Full Python implementation of common standards; Section 9 = Google-style docstrings; Section 10 = OOP conventions: class naming, dataclasses, dependency direction |
| `coding-standards/nodejs.md` | Full TypeScript implementation of common standards; Section 9 = JSDoc with same tags (omitting `{type}` since the compiler enforces types) |

**Docstring standard:** both languages document the same content (purpose, every parameter, the return value, every raised error), per-language syntax decided in `docs/decisions/ADR-002-python-docstring-style.md`. TypeScript uses JSDoc tags (`@param`, `@returns`, `@throws`), parsed by the compiler and IDE tooling. Python uses Google-style docstrings (`Args:`, `Returns:`, `Raises:`), parsed by Sphinx, pdoc, mkdocstrings, and IDE hover.

#### Templates

| File | What It Produces |
| --- | --- |
| `design-review-template.md` | Structured artifact for design reviews: problem, constraints, options considered, decision, risks, follow-up |
| `templates/adr-template.md` | Architecture Decision Record: context, decision, status, consequences |
| `templates/service-template.md` | Service scaffolding with standard structure |
| `templates/etl-template.md` | ETL pipeline scaffolding |
| `ai-ids-template.md` | AI instruction design set authoring template |

---

## Cross-Cutting Concerns

Some engineering concerns appear across multiple layers. This section maps where each concern lives at each layer so there is no ambiguity about which file governs what.

### Observability

| Layer | File | What It Addresses |
| --- | --- | --- |
| Macro | `principles.md` | Non-negotiable: all system boundaries must be observable |
| Macro | `system-quality-attributes.md` | Observability as a quality dimension; design levers and trade-offs |
| Meso | `observability.md` | Structured logging patterns, trace propagation, metric naming, alerting design |
| Micro | `coding-standards/common.md` | Logging standard (what to log, what not to log, required fields) |
| Micro | `coding-standards/python.md` | Python logging implementation |
| Micro | `coding-standards/nodejs.md` | Node.js/TypeScript logging implementation |

### Security

| Layer | File | What It Addresses |
| --- | --- | --- |
| Macro | `principles.md` | Non-negotiable: security is not a feature; it is a constraint |
| Macro | `system-quality-attributes.md` | Security as a quality dimension |
| Meso | `security.md` | Threat modeling, input validation, secrets management, least privilege, AI security |
| Micro | `coding-standards/common.md` | Security standard: no hardcoded secrets, input validation rules |
| Micro | `coding-standards/python.md` | Python-specific security implementation |
| Micro | `coding-standards/nodejs.md` | Node.js/TypeScript-specific security implementation |

### Documentation

| Layer | File | What It Addresses |
| --- | --- | --- |
| Meta | `document-authoring-guidelines.md` | How to write OS documents |
| Meta | `glossary.md` | Shared vocabulary |
| Meso | `documentation.md` | Documentation as a first-class engineering discipline: ADRs, API contracts, data contracts, runbooks, model cards, prompt registries, lifecycle ownership |
| Meso | `prose-style.md` | How the sentences in that documentation read: no unedited-AI tells |
| Micro | `coding-standards/common.md` | Standard 10: Documentation Baseline - what every function must document |
| Micro | `coding-standards/python.md` | Python docstring format (Google-style) |
| Micro | `coding-standards/nodejs.md` | TypeScript JSDoc format |
| Micro | `templates/adr-template.md` | ADR artifact |

### Testing

| Layer | File | What It Addresses |
| --- | --- | --- |
| Macro | `principles.md` | Non-negotiable: testability is a design property, not an afterthought |
| Meso | `testing-strategy.md` | Test pyramid, test types, AI evaluation, contract testing |
| Micro | `coding-standards/common.md` | Testing standard: what requires test coverage, naming conventions |
| Micro | `coding-standards/python.md` | Python test patterns |
| Micro | `coding-standards/nodejs.md` | TypeScript test patterns |

### Project Structure and AI Agent Compliance

| Layer | File | What It Addresses |
| --- | --- | --- |
| Meta | `claude-code-usage.md` | Bootstrap protocol, CLAUDE.md template, checkpoint map; prevents standards drift when Claude Code is used as an engineering agent |
| Micro | `project-structure.md` | Canonical folder layout: `src/`, `ids/` at project root, `input/`, `output/`, `logs/`, `docs/`, `tests/`; OOP module conventions; naming |
| Micro | `coding-standards/python.md` | Section 10: OOP class naming, dataclasses, dependency direction |
| Micro | `coding-standards/common.md` | Definition of Done checklists instantiated in every project's CLAUDE.md |

---

## The AI-IDS Framework

The AI Instruction Design Set (AI-IDS) is the anchor differentiator of the Engineering OS. It treats AI instruction design as an engineering discipline with the same rigor as API design or database schema design, not as a prompting art.

**Where AI-IDS lives in the architecture:**

| Layer | File | Role |
| --- | --- | --- |
| Meso | `ai-deterministic-systems.md` | Full framework guide: roles, objectives, guardrails, input/output structure, derived logic, reasoning policy, bounded inference |
| Meso | `ai-ids-template.md` | Authoring-level template for producing an AI-IDS artifact |
| Micro | `templates/ai-ids-template.md` | Blank scaffold for use during implementation — copy to `ids/<name>.ids` and populate; see meso version for section-by-section guidance |
| Meta | `glossary.md` | AI-IDS terms defined in the shared vocabulary |

**The AI execution chain:**

```
Input
  │
  ▼
Instruction Specification (IDS)
  │  (roles, objectives, guardrails, input/output contracts)
  │  (bounded inference rules, derived logic, reasoning policy)
  ▼
Model (inference)
  │
  ▼
Validation
  │  (output structure check, guardrail enforcement, normalization)
  ▼
Output
```

Determinism in AI systems is not achieved at the model layer alone. It is achieved by the structure around the model: explicit instruction design, bounded inference, deterministic derivation rules, output validation, and runtime controls. The AI-IDS framework provides all of these in a reusable authoring format.

**AI systems follow the same four-layer model as all other systems.** A principle violation in an AI system is still a principle violation. An AI pipeline without observability is still non-compliant with the observability quality attribute. The framework does not create a separate rule set for AI: it extends the same architecture into the AI execution chain.

---

## Decision Routing

Use this table to find the right starting file for any common engineering decision.

| If you are... | Start at |
| --- | --- |
| Starting a project with Claude Code | `skills/README.md` (install, then `eng-os-plan-app` or `eng-os-bootstrap`); protocol prose in `meta/claude-code-usage.md` |
| Onboarding to the Engineering OS | `meta/mental-model.md` then `meta/glossary.md` |
| Making an architectural decision | `macro/principles.md` then relevant `meso/` guide |
| Evaluating a design trade-off | `macro/system-quality-attributes.md` |
| Designing an API | `meso/api-design.md` |
| Designing a data pipeline | `meso/data-strategy.md` |
| Designing a database schema | `meso/database-design.md` |
| Designing a new service | `meso/system-design.md` then `micro/templates/service-template.md` |
| Designing an AI system or instruction set | `meso/ai-deterministic-systems.md` then `meso/ai-ids-template.md` |
| Planning observability for a system | `meso/observability.md` |
| Doing a security review | `meso/security.md` |
| Planning a testing approach | `meso/testing-strategy.md` |
| Planning a deployment pipeline | `meso/deployment.md` |
| Deciding what to document and how | `meso/documentation.md` |
| Cleaning up prose that reads like unedited AI output | `meso/prose-style.md` |
| Setting SLOs, timeouts, retries, or a degraded path | `meso/reliability.md` |
| Provisioning infrastructure or planning regions, cells, and backups | `meso/infrastructure.md` |
| Classifying data, handling personal data, retention, or deletion | `meso/data-governance.md` |
| Tuning an AI agent's own cost, context, and scope | `meta/agent-operations.md` |
| Designing a web UI, internal tool, or customer document | `meso/design-system.md` then `micro/templates/base-styles.css` |
| Writing release notes for customers | `meso/documentation.md` Section 2.6 then `micro/templates/release-notes-template.md` |
| Setting up or improving code review | `meso/team-practices.md` Section 1 |
| Defining incident response for a team | `meso/team-practices.md` Section 3 |
| Setting up on-call rotation | `meso/team-practices.md` Section 4 |
| Managing technical debt | `meso/team-practices.md` Section 5 |
| Defining project folder layout | `micro/project-structure.md` |
| Writing Python code | `micro/coding-standards/common.md` then `micro/coding-standards/python.md` |
| Writing TypeScript/Node.js code | `micro/coding-standards/common.md` then `micro/coding-standards/nodejs.md` |
| Reviewing a design | `micro/design-review-template.md` |
| Recording an architecture decision | `micro/templates/adr-template.md` |
| Scaffolding a new ETL pipeline | `micro/templates/etl-template.md` |
| Adding or revising an OS document | `meta/document-authoring-guidelines.md` |

---

## Constraint Flow — Worked Example

The following example shows how a single principle propagates through all four layers, using observability as the thread.

**Macro / Principle:**
> All system boundaries must be observable. A system that cannot be inspected cannot be trusted.

**Macro / Quality Attribute:**
> Observability: the degree to which the internal state of a system can be inferred from its external outputs. Design levers: structured logging, distributed tracing, metric instrumentation, alerting. Trade-off: instrumentation adds latency and complexity; under-instrumented systems fail silently in production.

**Meso / observability.md:**
> Structured logs must include `trace_id`, `span_id`, `severity`, `service`, and `timestamp` as top-level fields. Logs must not include raw PII. Trace context must be propagated across all service boundaries.

**Micro / coding-standards/common.md:**
> Standard 6, Logging: Every function that crosses a service boundary must emit a structured log entry. Required fields: `trace_id`, `span_id`, `severity`, `service`. Forbidden fields: passwords, tokens, full SSNs.

**Micro / coding-standards/python.md:**
> Python implementation of Standard 6 using `structlog` with correlation context propagated via `contextvars`. Code examples provided.

**Micro / coding-standards/nodejs.md:**
> TypeScript implementation of Standard 6 using `pino` with `AsyncLocalStorage` for context propagation. Code examples provided.

The constraint originates at Macro and terminates as concrete code at Micro. At no point does a lower layer override or ignore the constraint above it.

---

## File Inventory

Complete list of all content files by layer.

```
meta/
  architecture.md                    This file
  mental-model.md
  document-authoring-guidelines.md
  glossary.md
  claude-code-usage.md               Bootstrap protocol and CLAUDE.md template for AI agent engagements
  agent-operations.md                Agent context, cost, parallelism, and scope discipline

macro/
  principles.md
  system-quality-attributes.md

meso/
  ai-deterministic-systems.md
  ai-ids-template.md
  api-design.md
  code-conventions.md
  data-governance.md
  data-strategy.md
  database-design.md
  deployment.md
  documentation.md
  infrastructure.md
  observability.md
  prose-style.md
  reliability.md
  security.md
  system-design.md
  team-practices.md
  testing-strategy.md

micro/
  project-structure.md               Canonical folder layout, module organization, OOP conventions, naming
  design-review-template.md
  coding-standards/
    common.md
    python.md
    nodejs.md
  templates/
    adr-template.md
    service-template.md
    etl-template.md
    release-notes-template.md
    base-styles.css
    ai-ids-template.md

docs/decisions/                      Architecture Decision Records for the OS itself
evidence/ledger.md                   Why each evidence-based rule exists
skills/                              Skills adapter (see skills/README.md)

root/
  README.md
  CONTRIBUTING.md
  CHANGELOG.md
  VERSION

repository root:
  LICENSE, SECURITY.md                  CC BY 4.0 for system/, MIT for tools/ and .github/
  tools/install.ps1, tools/install.sh   Register skills with the agent runtime
  tools/lint-os.py                      Self-lint run by CI (.github/workflows/lint.yml)
```

---

## What This Architecture Does Not Cover

Explicitly out of scope in the current version:

- **Worked examples**: a complete AI pipeline scaffolded end-to-end using AI-IDS + coding standards + testing strategy, showing all layers working as a system
- **Platform-specific tooling guides**: cloud provider runbooks, Kubernetes configurations, CI system specifics; these are team-deployment artifacts, not OS-layer content

When these are added, they will slot into the existing layer model. Worked examples are Micro-level. Platform tooling guides are Meso or Micro depending on whether they contain design patterns or execution steps.
