---
name: eng-os-privacy-and-governance
description: "Use when a system stores or processes personal, regulated, or classified data; when declaring a dataset's classification, retention, or lineage; when implementing deletion or subject-access requests; or when sending data to a third party or an AI model."
sources:
  - meso/data-governance.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Privacy and Data Governance

Apply these rules to any dataset, table, topic, log, or prompt that can contain data about a
person or a regulated subject. `eng-os-security-practices` defends the boundary; this skill governs
what is inside it.

## Principles

- **Explicitness over implicitness.** Every dataset has a declared classification, owner, purpose, retention, and lineage. Unknown is not a category.
- **Validation at boundaries.** Data crossing into a lower-classification zone, a third party, or an AI model is checked against policy at the crossing.
- **Observability as a first-class concern.** Access to sensitive data is an audited event.

## Classification

Every dataset carries one level, recorded in the data dictionary: **Public**, **Internal**,
**Confidential** (personal or business-sensitive data), or **Restricted** (credentials, payment,
health, government identifiers, precise location). The level decides encryption, access, logging,
retention defaults, and whether the data may leave. Derived data inherits the highest level of
its inputs unless a documented anonymization step lowers it.
- Failure mode: a "temporary" analytics table joining two Confidential sources becomes the most sensitive dataset in the company with no owner.

## Personal Data Handling

- collect only fields with a stated purpose; a field with no consumer is removed
- using a field for a new purpose is an ADR, not a query
- analytical and AI workloads use a stable pseudonymous key, never the direct identifier, unless the purpose requires it
- Confidential and Restricted data is encrypted in transit and at rest with externally managed keys; Restricted fields at the field level
- personal data never appears in logs, traces, metric labels, error messages, or prompts to a model outside the same controls
- Failure mode: a debug log with a full request body puts Restricted data into a log platform with a wider audience and longer retention than the source.

## Retention and Deletion

Every dataset declares a retention period and a deletion mechanism that removes the data from
primary, replicas, caches, derived datasets, and (after their own retention) backups. Subject
erasure requests run through a tested procedure with a stated completion time, exercised on a
schedule.
- Failure mode: "we delete on request" removes the primary row and leaves three caches, a warehouse table, and seven years of backups.

## Lineage

The pipeline stamps every output with its run id and source ids (`eng-os-data-strategy`), so lineage is
queryable upstream (where did this come from) and downstream (what consumes it, so a
classification change or deletion propagates).
- Failure mode: a source is found unlawful and nobody can list the models and reports built on it.

## Access Review and Third Parties

Access to Confidential and Restricted data is role-based, purpose-bound, expiring, reviewed on a
schedule (quarterly for Restricted), and audited (`eng-os-security-practices`, Audit Logging). Sending
data to a vendor, partner, or model provider requires the receiver's controls to be at least as
strict, the minimum data for the purpose, and a record in the data dictionary. AI-IDS specs
declare which classification levels they accept.
- Failure mode: customer records pasted into a prompt to a provider that retains inputs for training.

See `references/example.md` for a data dictionary entry with classification, retention, and
lineage, and a deletion procedure that covers every copy.

## Failure Modes

- datasets with no classification, owner, or retention
- derived data carrying a higher classification than its controls
- personal data in logs, metric labels, or prompts
- deletion that removes the primary copy only
- no lineage
- standing access never reviewed

## Definition of Done

- [ ] Every dataset has a classification, owner, purpose, retention, and lineage record in the data dictionary
- [ ] Confidential and Restricted data is encrypted in transit and at rest and never appears in logs, metric labels, error messages, or unprotected prompts
- [ ] A tested deletion procedure covers primary, replicas, caches, derived datasets, and backups, with a stated completion time
- [ ] Lineage is captured by the pipeline and queryable both directions
- [ ] Access to sensitive data is role-based, purpose-bound, expiring, reviewed, and audited
- [ ] Every third-party or model transfer is recorded with the receiver's controls confirmed
