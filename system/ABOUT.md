# About the Engineering OS

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

---

The Engineering OS is a structured body of knowledge for engineering teams building product, data, and AI systems. It brings shared language, non-negotiable principles, domain design guides, and implementation standards into a single coherent framework, organized so that the right guidance is findable at the right level of detail, when it is needed.

It was built on a simple conviction: engineering knowledge should be as well-designed as the systems it produces. That means explicit structure, verifiable standards, concrete examples, and a design that scales with the team rather than becoming a maintenance burden.

---

## Design Philosophy

### A Layered Architecture

The OS is organized into four layers, each with a defined scope and purpose:

- **meta/**: shared vocabulary, authoring rules, and the mental model for navigating the OS
- **macro/**: non-negotiable principles and quality attributes that govern all design decisions
- **meso/**: domain design guides covering the major disciplines of engineering practice
- **micro/**: implementation standards and review templates that translate design patterns into working code

Each layer builds on the one above. The structure reflects how engineers reason: from shared language and principles, through domain patterns, down to implementation. Every file is designed to be independently useful: a reader who opens any single guide should be able to make materially better decisions from it alone.

### Traditional and AI Engineering as Equal Disciplines

Engineering practice has always evolved alongside the tools and systems it produces. The Engineering OS treats product engineering, data engineering, and AI engineering as three disciplines under the same principles, quality attributes, and design rigour, not as separate bodies of knowledge held together loosely.

AI engineering has its own design guide, instruction template, observability requirements, security patterns, and testing strategy. These are integrated into the same framework as API design and database design, governed by the same principles, and held to the same definition of done.

### Failure Modes as a First-Class Concern

Every principle, design pattern, and implementation standard in the OS carries a Failure Mode: a concrete description of what breaks and how when the standard is not applied. This reflects a view that a standard is only useful if it helps a team recognize when they are drifting from it. Good standards name the failure, not just the ideal.

### An Agent-Native Adapter, Not a Second Standard

`meta/macro/meso/micro` are written for a human (or any agent) reading prose end to end. `skills/` is a Claude Code Skills adapter over that same content, built for how AI coding agents consume context: a small always-loaded core, the rest loaded selectively at the moment it's needed, never all 36 files up front. It doesn't introduce a second set of standards; every skill's `sources:` field points back to the canonical document it was condensed from. See `skills/README.md` and `skills/MINDMAP.md`.

---

## The AI-IDS Framework

The AI Instruction Design Set (AI-IDS) is a formal framework for authoring AI system instructions as engineering artifacts, with defined semantics, an explicit precedence order for conflict resolution, an execution dependency chain, and a measurable determinism boundary.

The framework provides 11 defined sections:

| Section | Purpose |
|---------|---------|
| DEFINITIONS | Execution-time meaning of terms used throughout the spec |
| ROLE | System perspective, scope, and responsibility |
| OBJECTIVE | The single measurable outcome |
| GUARDRAILS | Non-negotiable constraints and failure conditions |
| STRUCTURE OF INPUT | The input contract |
| STRUCTURE OF OUTPUT | The output contract and determinism boundary |
| DERIVED LOGIC | Ordered deterministic computation |
| ASSUMPTIONS | Explicitly allowed inference for incomplete inputs |
| REASONING POLICY | Deterministic ambiguity resolution |
| GUIDELINES & INSTRUCTIONS | Non-authoritative influence on phrasing |
| FEW SHOT EXAMPLES | Illustrative pairs that influence output and never hold authority |

Sections have defined precedence: when two sections conflict, the higher-precedence section wins. This is documented explicitly, not left to interpretation. The framework includes a worked example showing every section populated for a real production use case, and an author review checklist for verifying a spec before deployment.

AI-IDS is model-agnostic. It operates as a structured specification layer above runtime and decoding controls, making AI behavior reviewable, testable, and measurable in the same way any other system component would be.

### Empirical Validation

The framework has been empirically evaluated in a production-validated media retrieval pipeline and deployed at scale across more than 400,000 video productions generating over 7.2 million keywords.

In a controlled evaluation across 9 articles, 161 sentences, and 25 repeated executions, AI-IDS demonstrated:

- **Composite operational consistency**: 0.35985 vs. 0.12363 for an unstructured baseline, a +23.6 percentage point improvement
- **Operational error rate**: 0% across all 25 rounds vs. 2.2% for the baseline, consistent across every individual iteration
- **Lexical consistency**: +12.2% improvement (Jaccard similarity)
- **Convergence efficiency**: 4.1 iterations to production-grade output vs. 17.1 for the baseline, a 76% reduction

A critical finding: runtime controls alone (temperature reduction, model selection) were insufficient to close the consistency gap. Structural instruction separation contributed independently to operational consistency beyond what decoding parameters provided.

The evaluation methodology, composite scoring formula, and full results are published in: Parekh, H.V. *AI Instruction Design Set (AI-IDS): A Structured Instruction Architecture for High Determinism and Low Operational Variance in Production AI Systems* (arXiv: cs.AI, cs.CL, cs.SE).

---

## What Is Covered

| Domain | Coverage |
|--------|----------|
| API Design | contracts, rate limiting, pagination, versioning migration |
| Data Strategy | pipelines, idempotency, schema evolution, freshness SLA |
| Database Design | schema, keys, indexing, partitioning, transactions, caching |
| System Design | C4 modeling, architecture patterns, design process |
| Observability | standard data models, log/metric/trace shapes, signal design by boundary |
| Security | input validation, secrets management, least privilege, AI-specific threats |
| Testing | unit, integration, contract, property, AI evaluation |
| Deployment | environments, CI/CD pipeline, feature flags, rollback, health checks, canary/blue-green, expand/contract ordering, secret rotation |
| Reliability | SLOs and error budgets, timeouts and deadlines, retries with jitter, circuit breakers, bulkheads, load shedding, chaos |
| Infrastructure | infrastructure as code, environment parity, regions and cells, backup and restore |
| Privacy and Governance | classification, personal data, retention and deletion, lineage, access review |
| AI Engineering | AI-IDS framework, deterministic instruction design, AI observability |
| Code Conventions | naming rules (variables, constants, classes, files, env vars, booleans) and comment conventions |
| Coding Standards | language-agnostic rules: config, error handling, retry, logging, testing, security |

---

## What It Supports

**Navigability.** The layer model means an engineer looking for guidance on a specific problem can find the right level of detail without reading everything. Principles live in macro, domain patterns in meso, and implementation in micro: each independently useful, each pointing to the others where relevant.

**Consistent decisions across teams.** Shared principles, a canonical glossary, and domain guides with explicit patterns mean design choices are more predictable and traceable across teams and over time, without requiring constant coordination or tribal knowledge.

**Earlier recognition of drift.** Failure modes in every standard help teams recognize when they are moving away from a sound pattern before it surfaces in production. A standard that only describes the ideal is harder to apply than one that also names the failure.

**AI engineering at the same rigour as traditional engineering.** The AI-IDS framework and integrated AI guides give teams a structured way to design, review, and measure AI system behavior, using the same vocabulary and quality bar applied to APIs, data pipelines, and services.

**A standard that grows with the team.** The authoring guidelines define what belongs in each layer and how to write it. The contribution model means new guides, patterns, and examples can be added without breaking the structure or lowering the quality bar.

---

## Who It Is For

Engineering teams building across product, data, and AI who want a single coherent standard rather than discipline-specific silos. Teams who want AI engineering held to the same design rigour as the rest of their stack. Teams who want a living standard they can adopt, extend, and contribute to as their practice evolves.

---

## Research Behind the Design

Before the skills were written, the author reviewed what already existed and what had gone wrong on real projects. This section records that research and what each part of it changed. It describes other work as that work documents itself and does not rank it. Third-party facts were checked on the dates stated and change quickly.

### Existing Engineering Material

Four categories of published material were reviewed. Each covers one concern well.

| Category | Typical scope | What it left open for this work |
|---|---|---|
| Engineering handbooks | Company culture, process, and values | A technical standard that applies the same way to product, data, and AI work |
| Engineering playbooks | Project-level checklists and engagement practices | A layer model, a shared glossary, and a verifiable Definition of Done per guide |
| Language style guides | Formatting and conventions for one language | Language-agnostic principles that sit above any single language |
| AI guides | Prompting and model-usage technique | A formal instruction-design framework with measured results (AI-IDS, see Empirical Validation) |

The layer model (meta, macro, meso, micro), the single glossary, and the treatment of AI engineering as a discipline under the same principles as the rest were designed with those open areas in mind.

### The Author's Own Projects and Spec-Driven Frameworks

Two reviews shaped the workflow skills. Both are recorded in `evidence/ledger.md`, which lists the evidence behind each rule.

- **An audit of six production apps (2026-07).** Four apps had independently hand-written the same brief shape, one renamed a core concept three times mid-build, and one was a single script that a full template would have misled. These became `eng-os-plan-app`, its Terminology Lock, and the bootstrap bail-out (E-01, E-02, E-04).
- **A comparison of five spec-driven frameworks (2026-08).** BMAD, Spec Kit, OpenSpec, Kiro, and GSD each had a decompose, sequence, and verify loop, which this OS did not, so `eng-os-execute-feature` was added (E-06). Kiro, BMAD, and Spec Kit also split work into separately reviewed requirements, design, and task artifacts, which led to `eng-os-spec-feature` (E-29).

### Skill Collections

The Agent Skills format (`SKILL.md`) was published by Anthropic as an open standard in December 2025 and has since been adopted natively across Claude Code, OpenAI's Codex CLI, Google's Gemini CLI, GitHub Copilot, Cursor, Windsurf, and Cline. Five collections built on it were reviewed to understand the ecosystem this OS would join.

| Collection | What it is | How it relates to this OS |
|---|---|---|
| [Anthropic Skills](https://github.com/anthropics/skills) | The reference implementation of the `SKILL.md` format and specification, plus a demonstration set of example skills | The format this OS is built on. The specification is the authority. |
| [OpenAI Skills](https://github.com/openai/skills) | The official Codex CLI catalog of curated, task-specific skills | Reads the same `SKILL.md` format, which is why the OS documents a Codex CLI path in `skills/PORTABILITY.md` |
| [Superpowers](https://github.com/obra/superpowers) | A software development methodology (brainstorm, design, plan, TDD, review) implemented as composable skills | Covers how a feature gets built in one session. This OS covers what standard the result must meet across API design, data strategy, security, observability, and AI systems. A team could use both. |
| [VoltAgent Awesome Agent Skills](https://github.com/VoltAgent/awesome-agent-skills) | An aggregator with about 1,500 skills (as of 2026-10) from official teams and community contributors | A place to find an existing skill for a specific tool or task. This OS addresses cross-cutting standards instead. |
| [heilcheng Awesome Agent Skills](https://github.com/heilcheng/awesome-agent-skills) | A curated directory of skills used by real teams, with multi-language documentation | A curated way to discover vetted skills. Because this OS uses the same open format, it could be listed in directories like this one. |

The skills layer (`skills/README.md`) applies the format at the scope of a full engineering standard rather than a single library or project. Its design follows from the review above:

- Skills derive from a governed, versioned source of truth, and skill content must not outpace its canonical source doc (enforced in `CONTRIBUTING.md`).
- Rules that rest on a named failure or comparison have that evidence recorded in `evidence/ledger.md`.
- Patterns carry production-scale caveats that say where a rule stops holding.
- An always-on router skill holds a checkpoint table that names which skill fires when.
- Every skill has a worked example, and `skills/MINDMAP.md` shows how the skills relate and what each is worth.
- A cross-platform path is documented for Codex CLI, Gemini CLI, Copilot, Cursor, Windsurf, Cline, and Aider alongside native Claude Code support.

### What the Research Did Not Establish

- **Adoption.** This OS has been used only on the author's own projects. The collections above, Superpowers in particular, have much wider real-world use.
- **Platforms.** `SKILL.md` reads natively on the platforms listed, so the skills should load there without an export step according to each platform's documentation (see `skills/PORTABILITY.md`). Only Claude Code has been exercised end to end. Aider would need an export, and none has been built.
- **Breadth.** At 28 skills, this OS is narrow next to a directory of about 1,500 (as of 2026-10). The choice was coherence and governance under one standard over breadth.
- **Evidence strength.** Some rules rest on comparison alone. `eng-os-spec-feature` has no recorded downstream incident yet (E-29), and the ledger says so.

---

## Notice

This is one practitioner's point of view, written in good faith from experience with production systems serving millions of users. Other companies' approaches differ, and nothing here is professional advice. Third-party facts were checked on the dates stated and change quickly. If something has missed the mark, open an issue and it will be reviewed and updated. The full notice is in `README.md`.

---

## License

Creative Commons Attribution 4.0 International (CC BY 4.0) for the standards and skills; MIT for the code in `tools/` and `.github/`. See the repository-root `LICENSE`.
Originally authored by Haresh V. Parekh.
Free to use, adapt, and redistribute with attribution.
