# Evidence Ledger

**Status:** Current
**Owner:** Haresh V. Parekh

One row per rule that exists because of a specific, named failure or comparison. A rule with no
row here is a convention, not evidence-based; a rule whose evidence is two releases old with no
recurrence is a candidate for retirement. `MINDMAP.md` cites rows by id. Add a row in the same
change as any new rule.

| Id | Rule | Where it lives | Evidence | Source | Date |
|---|---|---|---|---|---|
| E-01 | Product Brief before code | `eng-os-plan-app` | Four apps independently hand-wrote the same brief shape | Audit of six production apps | 2026-07 |
| E-02 | Terminology Lock | `eng-os-plan-app` Phase 4, `eng-os-code-conventions` | One app renamed a core concept three times mid-build (Campaigns→Events→again; Evaluate→Analyze; Documentation→Platform Guide) | App changelog | 2026-07 |
| E-03 | Always-on checkpoint router instead of "read everything first" | `eng-os-core` | Early reads decayed over long sessions; standards silently skipped | `meta/claude-code-usage.md` drift catalogue | 2026-06 |
| E-04 | Bootstrap bail-out for trivial scripts | `eng-os-bootstrap` Step 0 | One of six apps was a single script; full template would have misled | Audit of six production apps | 2026-07 |
| E-05 | Architecture Practices Gate | `eng-os-bootstrap` | Stated practices (constants by area, MVC, app shell, responsive) kept drifting despite being in the OS; a general "populate" pass was insufficient | User report across new projects | 2026-08 |
| E-06 | Decompose, sequence, verify loop | `eng-os-execute-feature` | Every compared framework (BMAD, Spec Kit, OpenSpec, Kiro, GSD) had one; the OS did not | Framework comparison | 2026-08 |
| E-07 | Design tokens by reference, not retyped | `eng-os-design-system` Inheritance | Four or more sibling apps retyped identical tokens by hand and drifted | Audit of six production apps | 2026-07 |
| E-08 | MVC as a named standard | `eng-os-coding-standards-common` 13 | Business logic in route handlers recurred despite Separation of Concerns | User report | 2026-08 |
| E-09 | Scoring Run provenance on AI results | `ai-ids-authoring/references/observability-ui.md` | Every AI-IDS app converged on it after users lost trust at the first wrong answer | Audit of AI-IDS apps | 2026-07 |
| E-10 | Freshness indicator for SLA'd data | `eng-os-data-strategy` | Online/offline fusion score shown with no staleness signal while the batch half was stale | Production observation | 2026-07 |
| E-11 | Prose-style patterns | `eng-os-prose-style` | Audit of a published documentation site found the patterns on every page; an investor-facing page shipped a contrastive headline | Documentation-site audit; downstream app | 2026-08 |
| E-12 | Message code prefix sized 3 letters + 6 digits | `eng-os-coding-standards-common` 3 | 4-digit project-wide sequence "may run out easily" on a long-lived app | Downstream project retrofit | 2026-08 |
| E-13 | Centralized third-party client; extract on second occurrence | `eng-os-coding-standards-common` 12 | Two files instantiated the same client and duplicated a retry harness | video2clips | 2026-07 |
| E-14 | Dual classification axes as separate columns | `eng-os-database-design` | Compound tier/quality enums exploded combinatorially | Production schema | 2026-07 |
| E-15 | Bootstrap must actually bind (paths, not "yes") | `eng-os-bootstrap` Gate | "Follows MVC" sentences satisfied "no placeholders" while binding nothing | User report | 2026-08 |
| E-16 | Skills registered with the runtime, not linked by `.lnk` | `tools/install.*` | None of the 26 skills appeared in a live session's skill list; the shortcut was never followed | 2026-09-01 architecture review | 2026-09 |
| E-17 | Scale Targets in numbers before design | `eng-os-plan-app` 2b, `eng-os-bootstrap` | No planning phase held a single number; capacity, SLOs, and load tests had nothing to check against | 2026-09-01 architecture review | 2026-09 |
| E-18 | Timeouts, jittered single-layer retry, bounded queues, degraded paths | `eng-os-reliability-engineering`, `eng-os-coding-standards-common` 5 | Fixed `[50,100,200,500ms]` schedule with no jitter; no timeout, breaker, or shedding guidance anywhere in the OS | 2026-09-01 architecture review | 2026-09 |
| E-19 | WCAG 2.2 AA as a Definition-of-Done row | `eng-os-design-system` | Zero mentions of accessibility in the canonical layer | 2026-09-01 architecture review | 2026-09 |
| E-20 | Authorization model, tenant isolation first, audit log | `eng-os-security-practices`, `eng-os-api-design` | Authn covered, authz absent; no tenant scoping rule | 2026-09-01 architecture review | 2026-09 |
| E-21 | UUIDv7, expand/contract, pooling, tenant predicate | `eng-os-database-design`, `eng-os-deployment-practices` | UUIDv4 default; no online migration pattern; no pool bounds | 2026-09-01 architecture review | 2026-09 |
| E-22 | Metric cardinality budget, trace sampling, OpenTelemetry | `eng-os-observability` | No cardinality rule; no sampling policy; no interop standard | 2026-09-01 architecture review | 2026-09 |
| E-23 | Self-lint and CI for the OS itself | `tools/lint-os.py` | Stale `{AREA}{NNNN}`, three different skill counts, 393 em dashes against the OS's own ban | 2026-09-01 architecture review | 2026-09 |
| E-24 | ADR threshold | `eng-os-documentation-standards`, ADR-003 | "Every significant decision" produced unread ADRs | 2026-09-01 architecture review | 2026-09 |
| E-25 | Classification, retention, lineage, deletion across copies | `eng-os-privacy-and-governance` | PII mentioned three times in the canonical layer; no retention or deletion rule | 2026-09-01 architecture review | 2026-09 |
| E-26 | Log persistence: durable sink, rotation, retention, level policy | `eng-os-observability` | A downstream project built full structured logging (shape, `trace_id` propagation) across two runtimes and passed the skill's own DoD with logs reaching stdout only; the skill had no requirement that a log actually persist anywhere | Downstream project session | 2026-09 |
| E-27 | Constants vs. config vs. secrets three-way split; multi-process and multi-language guidance | `eng-os-coding-standards-common` Standard 3a | A downstream project had no `.env`/constants split at all in one of its two languages, an undocumented shared env var, and a proposed fix (move a fixed constant into a database to avoid cross-language duplication) that was wrong by the project's own later correction; the OS had the constants-vs-config split but no secrets-as-third-category framing, no multi-process guidance, and no multi-language guidance. Sourced from 12factor.net/config, OWASP's Secrets Management Cheat Sheet, and Google Cloud's Secret-Manager-vs-Parameter-Manager split | Downstream project session | 2026-09 |
| E-28 | Pre/AI/post processing boundary must be pointed to from the spec | `eng-os-ai-ids-authoring`, `meso/ai-deterministic-systems.md` | A downstream project's own plan document had already established the pre/AI/post pattern for one scorer; a later session on the same project independently reinvented a pre-processing gate for a different scorer and, absent a standing rule, the first proposed fix moved the gate's logic into the spec (the wrong direction), caught only because the user recalled the unrelated prior session | Downstream project session (tie-skip audit) | 2026-09 |
| E-29 | Requirements, design, and tasks written and approved in that order before implementation | `eng-os-spec-feature` | The E-06 comparison found the task loop in every framework; Kiro, BMAD, and Spec Kit each also split the work into separately reviewed requirements, design, and task artifacts, while the OS had a task loop but nothing agreed to check it against. Without it, undefined behavior (for example a threshold the Product Brief names but never defines) first surfaces as test failure or rework. No downstream incident recorded yet; the worked example's undefined yellow threshold and its uncovered criterion are illustrations | Framework comparison (E-06) and a user request | 2026-10 |
