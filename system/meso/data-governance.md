# Privacy and Data Governance

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
The design guide for knowing what data a system holds, how sensitive it is, where it came from,
who may touch it, how long it lives, and how it is removed: classification, personal data
handling, retention and deletion, lineage, access review, and the audit trail that proves all of
it.

### What This Is Not
- not legal advice; it defines the engineering controls that regulations require, not the regulations
- not the security guide (that defends the boundary; this governs what is inside it)
- not the data-strategy guide (that moves and shapes data; this decides what is allowed)

## Scope
- Level: Meso
- Applies To: every system that stores or processes data about a person, a customer, or a regulated subject
- See Also: `meso/security.md`, `meso/data-strategy.md`, `meso/database-design.md`, `meso/documentation.md`

---

## Applied Principles

### Explicitness Over Implicitness
Every dataset has a declared classification, owner, retention, and lineage. Unknown is not a category.

### Validation at Boundaries
Data crossing into a lower-classification zone, an external party, or an AI model is checked
against policy at the crossing.

### Observability as a First-Class Concern
Access to sensitive data is an audited event.

---

## 1. Data Classification

Every dataset, table, topic, and file store carries one classification, recorded in the data
dictionary (`meso/documentation.md` 2.3):

| Level | Meaning | Examples |
|---|---|---|
| Public | May be disclosed freely | published docs, marketing content |
| Internal | Business data, no personal or regulated content | aggregate metrics, non-personal configuration |
| Confidential | Personal data or business-sensitive data | names, emails, addresses, contracts, pricing |
| Restricted | Data whose exposure causes serious harm or regulatory breach | credentials, payment data, health data, government identifiers, precise location |

The classification decides encryption, access control, logging rules, retention defaults, and
whether the data may be sent to a third party or an AI model. Derived data inherits the highest
classification of its inputs unless a documented anonymization step lowers it.

- Failure mode: a "temporary" analytics table joining two Confidential sources becomes the
  most sensitive dataset in the company with no owner and no controls.

## 2. Personal Data Handling

- **Minimization**: collect only fields with a stated purpose; a field with no consumer is
  removed, not kept "in case"
- **Purpose binding**: the purpose is recorded with the field; using it for another purpose is a
  decision with an ADR, not a query
- **Pseudonymization**: analytical and AI workloads use a stable pseudonymous key, never the
  direct identifier, unless the workload's purpose requires it
- **Encryption**: Confidential and Restricted data is encrypted in transit always and at rest
  with keys managed outside the application; Restricted fields are encrypted at the field level
- **Logs and AI prompts**: personal data never appears in logs, traces, metrics labels, error
  messages, or prompts sent to a model that is not under the same classification controls

- Failure mode: a debug log line with a full request body puts Restricted data into a log
  platform with a wider audience and a longer retention than the source system.

## 3. Retention and Deletion

Every dataset declares a retention period sized to its purpose and its regulatory floor, and a
deletion mechanism that actually removes the data (including from backups after the backup's
own retention, from replicas, from caches, and from derived datasets). Subject deletion requests
(erasure) are satisfied by a tested procedure with a stated completion time, and the procedure
is exercised on a schedule.

- Failure mode: "we delete on request" that removes the primary row and leaves the data in
  three caches, a warehouse table, and every backup for seven years.

## 4. Lineage

For every dataset, record which sources produced it and which transformations were applied,
at the granularity of a pipeline stage. Lineage is captured by the pipeline (stamped run id and
source ids, per `meso/data-strategy.md`), not maintained by hand, and is queryable both
upstream (where did this value come from) and downstream (what consumes this field, so a
classification or deletion can propagate).

- Failure mode: a source is found to be corrupt or unlawfully collected, and nobody can list
  the datasets, models, and reports built on it.

## 5. Access Control and Review

Access to Confidential and Restricted data is granted per role with a stated purpose, expires,
and is reviewed on a schedule (quarterly for Restricted). Every read of Restricted data by a
human, and every bulk export of Confidential data, is an audit event (`meso/security.md`
Section 8). Service accounts follow the same rule; a service that can read every table is a
finding.

- Failure mode: standing read access granted for one investigation two years ago, still active
  for an engineer who has since changed teams.

## 6. Third Parties and AI Models

Sending data to a vendor, a partner, or a model provider is a boundary crossing: the receiving
party's classification controls must be at least as strict as the sender's, the data sent is the
minimum for the purpose, and the transfer is recorded in the data dictionary. AI-IDS inputs
(`meso/ai-deterministic-systems.md`) declare which classification levels they accept.

- Failure mode: customer records pasted into a prompt to a model whose provider retains inputs
  for training.

---

## Failure Modes

- datasets with no classification, owner, or retention, so no control can be applied
- derived data that silently carries a higher classification than its controls
- personal data in logs, metric labels, or prompts
- deletion that removes the primary copy and none of the others
- no lineage, so a bad source cannot be traced to its consumers
- standing access that is never reviewed

## Definition of Done

Data governance is complete when:
- every dataset has a classification, an owner, a purpose, a retention period, and a lineage record in the data dictionary
- Confidential and Restricted data is encrypted in transit and at rest, and never appears in logs, metric labels, error messages, or unprotected prompts
- a tested deletion procedure covers primary, replicas, caches, derived datasets, and backups, with a stated completion time
- lineage is captured by the pipeline and queryable upstream and downstream
- access to sensitive data is role-based, purpose-bound, expiring, reviewed on a schedule, and audited
- every third-party or model transfer is recorded with the receiving party's controls confirmed
