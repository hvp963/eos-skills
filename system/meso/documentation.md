# Documentation

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A discipline guide for treating documentation as a first-class engineering output, with the same lifecycle, ownership, and review standards as code.

### What This Is Not
- not a writing style guide
- not a formatting preference
- not limited to code comments: documentation spans all engineering disciplines
- not optional for production systems

## Scope
- Level: Meso
- Applies To: Software, data, ML/AI, infrastructure, and platform engineering
- See Also: `macro/principles.md` (Explicitness Over Implicitness), `micro/coding-standards/common.md` (Standard 10), `micro/templates/adr-template.md`, `meso/prose-style.md` (sentence-level prose quality, distinct from this document's content/structure requirements)

---

## Applied Principles

### Explicitness Over Implicitness
Undocumented behavior is implicit behavior. Documentation makes decisions, constraints, and assumptions visible to anyone who was not in the room when they were made.

### Contracts as Source of Truth
Documentation of system interfaces (APIs, events, data schemas) is itself a contract. It must be versioned, reviewed, and treated as authoritative.

### Observability as a First-Class Concern
A system is not observable if humans cannot understand what it is supposed to do, why it was built that way, and how to operate it. Documentation is a prerequisite for operational observability.

---

## 1. Documentation as a System Output

Documentation is not a byproduct of engineering work: it is a deliverable that ships with the work.

**The core rule:** if a system change affects behavior, its documentation changes in the same commit or PR.

This means:
- docs are reviewed with the code that changes behavior
- docs have owners (teams or named individuals), not just authors
- docs go stale the same way code does: through neglect, not malice
- deprecated docs must be marked deprecated, not left as authoritative guides

A useful test: if an engineer joins tomorrow and reads only the documentation for a system, can they understand what it does, why it was built that way, and how to operate it? If not, the documentation is incomplete.

---

## 2. Documentation Types by Discipline

Each engineering discipline produces different documentation artifacts. The table below maps disciplines to their primary documentation types and where each artifact lives.

| Type | Discipline | Purpose | Where It Lives |
|---|---|---|---|
| Architecture Decision Record (ADR) | All | Captures a significant design decision and its rationale | `docs/decisions/` or `adr/` |
| API Reference | Software | Defines endpoints, schemas, error codes, auth model | OpenAPI spec, README, or docs site |
| Data Contract | Data | Defines schema, semantics, ownership, and compatibility expectations | Schema registry, `docs/contracts/` |
| Data Dictionary | Data | Defines field names, types, meanings, and allowed values | `docs/data/` or warehouse documentation |
| Runbook | Operations / Infra | Step-by-step guide for operating, diagnosing, or recovering a system | `docs/runbooks/` or ops wiki |
| Model Card | ML / AI | Documents a model's purpose, training data, performance, limitations, and usage policy | `docs/models/` or model registry |
| Prompt Registry | AI | Catalogs versioned prompts with intent, inputs, outputs, and evaluation results | `docs/prompts/` or AI system registry |
| Evaluation Log | AI | Records results of AI system evaluation runs against defined quality metrics | `docs/eval/` or experiment tracker |
| Onboarding Guide | All | Helps a new engineer become productive — system overview, local setup, key concepts | `docs/onboarding/` or team wiki |
| Design Document | All | Explains the design of a system at a level above code — trade-offs, patterns, constraints | `docs/design/` or linked in PRs |
| Release Notes | Product / Platform | Communicates system changes, behavioral updates, deprecations, and migration steps to external customers | Customer portal, docs site, or email |
| API Changelog | Software | Versioned log of API changes: additions, modifications, deprecations, breaking changes | Docs site, `CHANGELOG.md`, or API reference |
| Migration Guide | Software / Platform | Step-by-step instructions for customers moving from a deprecated interface to its replacement | Docs site, linked from release notes |

---

## 2.1 Architecture Decision Records

An ADR captures a significant design choice that would otherwise exist only in someone's memory or in a long Slack thread.

**Write an ADR when:**
- choosing between two or more non-trivial technical approaches
- adopting or deprecating a platform, library, or pattern
- making a trade-off with long-term consequences (consistency vs. availability, build vs. buy)
- establishing a standard that will govern future work

**An ADR must include:**
- the context: what was the problem and what constraints applied
- the decision: what was chosen and why
- the consequences: what trade-offs were accepted, what doors were closed
- alternatives considered: what was rejected and why

ADRs are immutable once accepted. If a decision changes, a new ADR supersedes the old one. The old ADR is not deleted: it is marked `Superseded by ADR-NNN`.

See `micro/templates/adr-template.md` for the authoring template.

---

### When an ADR Is Not Required

The rule "an ADR for every significant decision" needs a threshold, or ADRs become a log of
every choice and nobody reads them. A decision requires an ADR when at least one holds:

- it is expensive to reverse (a schema shape, a storage engine, a public contract, a
  dependency other services will build on)
- it deviates from a documented pattern in this OS or the project's CLAUDE.md
- it changes a Terminology Lock term, a Message Area Code, or a Scale Target
- two or more viable approaches were considered and a later reader could reasonably ask why

A decision that is local, cheap to reverse, and follows the documented pattern (which library
function to call, how to name a private helper, the order of two independent tasks) is recorded
in the commit message, not an ADR. When unsure, ask: "would a new engineer six months from now
need this to avoid re-litigating it?" If yes, write the ADR.

## 2.2 API and Contract Documentation

API documentation defines the contract between producers and consumers. It must be:
- co-located with or linked from the API code
- versioned: a new API version requires updated documentation
- complete: every endpoint, field, error code, and auth mechanism must be described
- reviewed when the API changes behavior

```
// minimum API documentation for an endpoint
GET /orders/{order_id}

Path Parameters:
  order_id  string (UUID)  required  (the order to retrieve)

Response 200:
  { "id": string, "status": "pending|confirmed|shipped|delivered", "total_cents": integer }

Response 404:
  { "error": "order_not_found", "order_id": string }

Response 401:
  Returned when the Authorization header is missing or invalid.
```

---

## 2.3 Data Documentation

Data engineering produces two primary documentation artifacts:

**Data Contract**: the formal agreement between data producers and consumers. Must define:
- schema with field names, types, and nullability
- semantics: what each field means in business terms
- compatibility policy: additive-only, backward-compatible, or versioned-breaking
- SLA: freshness, availability, and quality expectations
- owner: who is responsible for changes and breakage notifications

**Data Dictionary**: the canonical reference for field meanings within a domain or data product. Must define:
- field name (canonical)
- business definition
- allowed values or range
- source system or derivation
- known issues or caveats

```
// data contract excerpt
table: orders
owner: commerce-data-team
freshness_sla: < 5 minutes from event time
compatibility: additive-only (adding fields is non-breaking; removing fields requires versioning)

fields:
  order_id       string  required  (system-generated UUID for this order)
  status         string  required  (enum: pending, confirmed, shipped, delivered, cancelled)
  total_cents    integer required  (order total in smallest currency unit, avoid floating point)
  customer_id    string  required  (references customers.customer_id)
  created_at     timestamp required (event time in UTC ISO 8601)
```

---

## 2.4 Operational Documentation (Runbooks)

A runbook gives an operator enough information to act during an incident or routine operation without hunting for context.

**A runbook must include:**
- what the system does (one paragraph, no assumptions about prior knowledge)
- how to confirm it is healthy
- common failure symptoms and their likely causes
- step-by-step recovery procedures for each known failure mode
- escalation path: who to contact and when

```
// runbook structure
# Runbook: Orders Pipeline

## System Summary
Consumes order events from Kafka, enriches with customer profile, writes to orders warehouse table.
Expected throughput: 2,000 events/minute.

## Health Check
- Grafana: orders-pipeline dashboard → throughput > 1,500 events/min, error rate < 0.1%
- Check consumer lag: `kafka-consumer-groups --describe --group orders-pipeline`

## Failure: Consumer Lag Growing
Likely cause: downstream warehouse write latency spike.
Steps:
  1. Check warehouse write latency on Grafana orders-pipeline dashboard
  2. If latency > 2s p95, check warehouse cluster health
  3. If healthy, reduce batch size in config: BATCH_SIZE=50 (default: 100)
  4. Restart pipeline service

## Escalation
SLA breach (lag > 10 min): page #data-oncall
```

---

## 2.5 ML and AI Documentation

AI systems require additional documentation artifacts beyond what traditional software needs, because the behavior of an AI system depends on training data, prompting decisions, and evaluation criteria that are not visible in code alone.

**Model Card** documents a deployed model. Must include:
- model purpose and intended use cases
- training data summary and known biases
- performance characteristics (accuracy, latency, throughput)
- known limitations and failure modes
- usage policy: what the model must not be used for

**Prompt Registry** catalogs versioned AI prompts used in production. Each entry must include:
- prompt version identifier
- intent: what the prompt is designed to accomplish
- input schema: what context is required
- output schema: what structure is expected
- evaluation results: last known determinism rate, constraint violation rate, schema compliance rate
- change history: what changed between versions and why

**Evaluation Log** records results of each evaluation run:
- date and model version
- input dataset used
- metrics: determinism rate, constraint violation rate, schema compliance rate
- pass/fail against defined thresholds
- known regressions

These artifacts are not a substitute for AI-IDS specifications: they complement them. The AI-IDS defines how a system should behave; the model card and prompt registry document what it actually does in production.

---

## 2.6 External and Customer-Facing Documentation

External documentation differs from internal engineering documentation in one critical way: the reader has no access to the codebase, the incident history, or the team. Every assumption must be stated. Every behavioral change must be explained in terms of its customer impact, not its implementation.

**Document types in this category:**

- **Release Notes**: communicate what changed in a release: new features, enhancements, behavioral changes, breaking changes, deprecations, known issues
- **API Changelog**: versioned log of API surface changes; consumed by integration teams who must decide when and how to update their integrations
- **Migration Guide**: step-by-step instructions for customers moving from a deprecated interface, schema, or behavior to its replacement

**Principles for external documentation:**

**Lead with customer value, not engineering detail.** The overview of a release note answers "what can I do now that I couldn't before?" not "what did we refactor." Engineers write about what changed; customers read about what they gain.

**Distinguish behavioral changes from breaking changes.** A breaking change requires the customer to take action: it fails if they do not. A behavioral change is automatic: the system changes on their behalf. These are different customer experiences and must be labeled differently. Conflating them erodes trust.

**Hide empty sections entirely.** An empty "Known Issues" section with a dash communicates "we checked." An empty section left visible communicates "we forgot." Remove sections with no content from the published document.

**Cap "Why It Matters" at three bullets.** B2B readers forward release notes to colleagues. If the value is not clear in three bullets, it will not be read past the overview. Rank by impact and cut the rest.

**Release note structure: what each section requires:**

| Section | Include when | Label |
|---|---|---|
| New Features | Net-new capabilities | `NEW` |
| Enhancements | Improvements to existing behavior | `IMPROVED` |
| Updated Behavior | System changes behavior automatically; may surprise users | `HEADS UP` |
| Bug Fixes | Issues resolved | `FIXED` |
| Breaking Changes | Customer must take action to avoid breakage | `ACTION REQUIRED` |
| Deprecations | Features phased out with a defined end-of-life date | `DEPRECATING` |
| Known Issues | Outstanding issues at ship time that customers will encounter | `KNOWN` |
| Why It Matters | Always — max 3 bullets | — |

See `micro/templates/release-notes-template.md` for the authoring template.

---

## 3. Documentation Lifecycle

Every documentation artifact has a lifecycle. The lifecycle must be explicit: undeclared state is the primary cause of stale documentation being treated as authoritative.

| State | Meaning |
|---|---|
| `Draft` | Being authored; not yet authoritative |
| `Current` | Authoritative; reflects the production system |
| `Deprecated` | Superseded or no longer applies; retained for historical reference |
| `Archived` | Removed from active use; kept in version control only |

**Lifecycle rules:**
- every document must declare its state at the top (in a `Status:` line or equivalent)
- a document transitions to `Deprecated` when the system it describes changes materially
- a deprecated document must reference what supersedes it
- documents must not be deleted from version control, only archived

```
// document state header (top of any documentation artifact)
Status: Current
Last Reviewed: 2026-05-31
Owner: commerce-data-team
```

---

## 4. What Lives Where

Documentation is organized by its decision layer, not by the team that wrote it.

| Layer | What Goes Here |
|---|---|
| **Decision layer** | ADRs, trade-off analyses, "why not X" records |
| **Design layer** | Architecture diagrams, design documents, system overviews |
| **Contract layer** | API specs, data contracts, event schemas, SLAs |
| **Operational layer** | Runbooks, alert playbooks, on-call guides |
| **Code layer** | Docstrings, inline comments, module READMEs |

A runbook does not belong in a design document. An ADR does not belong in a docstring. Misplaced documentation gets lost because engineers look in the wrong layer.

---

## 5. Ownership and Freshness

**Every document must have a named owner.** The owner is the team or individual responsible for keeping it current. If a document has no owner, it has no one to notice when it goes stale.

**Freshness signals**: a document is likely stale when:
- the system it describes has shipped a new major version
- an incident revealed a gap between the documentation and actual behavior
- the owner has changed teams and no new owner was assigned
- the document has not been reviewed in more than 6 months for actively-operated systems

**Freshness enforcement:**
- production runbooks must be reviewed and confirmed current after every major incident
- data contracts must be reviewed when the producing system changes its schema
- ADRs do not expire (they describe a point-in-time decision) but must be marked deprecated when superseded

---

## 6. Review Standards

Documentation changes must follow the same review process as code changes:
- a PR that changes system behavior must include corresponding documentation changes in the same PR
- documentation-only PRs must be reviewed by at least one engineer with operational knowledge of the system
- reviewers must check: accuracy, completeness, owner declaration, lifecycle state

**Documentation review checklist:**
```
□ Does it describe current behavior, not intended behavior?
□ Is the owner declared?
□ Is the lifecycle state declared?
□ Are all boundary conditions and failure modes covered?
□ Can an engineer act on this without reading the source code?
□ Does it reference related documentation (contracts, runbooks, ADRs)?
```

---

## 7. Pattern: Documentation Coverage by System Maturity

Systems at different stages require different documentation coverage.

```
// minimum viable documentation — any system entering production
□ Onboarding summary (what is this, how do I run it locally)
□ API or data contract documentation
□ At least one ADR for the primary technology choice
□ Basic runbook (health check + one recovery procedure)

// production-stable system
□ All of the above plus:
□ Full runbooks for all known failure modes
□ Data dictionary for all output datasets
□ Evaluation logs for AI systems
□ Architecture design document

// platform or shared infrastructure
□ All of the above plus:
□ Versioned API reference documentation
□ Consumer migration guide for breaking changes
□ SLA documentation
```

---

## Failure Modes

- documentation written after the fact is almost always incomplete because context is lost
- undeclared ownership means nobody notices when documentation goes stale
- runbooks written by the author assume too much context and fail at 2am during an incident
- ADRs not written because "everyone remembers the decision": they do not, after 18 months
- AI system behavior documented by describing prompts, not by documenting actual production behavior
- documentation that passes review because reviewers skim it the way they skim code comments

---

## Definition of Done

A system is documented to this standard when:
- every production-facing interface has current contract documentation
- at least one ADR exists capturing the primary technology and architecture choices
- a runbook exists with at minimum: health check, one failure recovery procedure, escalation path
- all documentation declares owner and lifecycle state
- documentation was reviewed in the same PR as the code change that affected behavior
- AI systems have a current prompt registry entry and at least one evaluation log
- ADRs exist for every decision that meets the threshold in 2.1 (expensive to reverse, deviates from a pattern, changes a locked term or target, or chose between viable alternatives); cheaper local choices are recorded in commit messages instead
