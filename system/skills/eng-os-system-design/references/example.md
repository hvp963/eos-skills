# Worked Example — Service Boundaries for a Small Multi-Tenant App

Scenario: a 4-person team is building a multi-tenant expense-approval SaaS. Tenants are small
companies (10-200 employees each). Core flows: employees submit expenses, managers approve them,
finance exports approved expenses to accounting systems (QuickBooks, Xero) monthly. The team
wants to know: how many services, split where, and why.

This walks the reasoning, not just the end diagram, applying the C4 and Core Design Patterns
sections of this skill.

## 1. Problem Definition First

- Problem: employees need to submit and track expenses; managers need to approve/reject; finance
  needs to reconcile approved expenses against external accounting systems.
- Out of scope (explicitly): payroll, tax reporting, multi-currency conversion (v1 is single
  currency per tenant).
- Quality attributes that matter most, in order: **tenant data isolation** (a leak between
  tenants is an existential trust failure, not a bug), correctness of the approval audit trail,
  then latency (this is not a high-QPS system; dozens of requests/second at most).

Because tenant isolation outranks everything else, it becomes the primary boundary-drawing
constraint below, not team size, not deployment convenience.

## 2. Context Level (C4)

External actors: employees, managers, finance admins, and two external accounting APIs
(QuickBooks, Xero). The system boundary is one thing from the outside: "Expense Approval
Platform." At Context level there is no reason yet to talk about internal services; resist the
urge to jump to Container level before this is written down, because it's what keeps "add a
service" decisions honest later (does the new piece serve one of these actors/integrations, or is
it internal plumbing that belongs inside an existing container?).

## 3. Container-Level Reasoning — Why These Boundaries and Not Others

**Tempting wrong answer:** four microservices split by CRUD resource (`users-service`,
`expenses-service`, `approvals-service`, `exports-service`). This looks clean on a diagram but
fails the "explicit ownership + fault isolation" principles: approvals and expenses are the same
transaction boundary (approving an expense mutates the expense's state), so splitting them forces a
distributed transaction or a saga for what is fundamentally one atomic write. That's a design
smell this skill's UX/IA section calls out directly: reaching for a distributed transaction across
services when one database would do is itself the mistake, not a sign you need a saga.

**Better boundary, derived from the actual coupling:**

1. **Core Expense Service**: owns employees, expenses, and approvals in one database. These three
   entities are written together in single transactions (submit expense → notify manager; approve
   expense → write audit log entry) and read together constantly (an approval screen needs the
   expense and the employee in the same query). Per this skill's "Atomic multi-entity saves"
   rule, keeping them in one transaction boundary is correct, not a shortcut.
2. **Tenant/Identity Service**: owns tenant records, user-to-tenant mapping, and auth. Split out
   from Core Expense specifically *because* of the isolation requirement: every other service's
   queries must be scoped by tenant_id, and centralizing "which tenant does this user/token belong
   to" in one place means there's exactly one place that can get tenant-scoping wrong, not four.
   This is fault isolation in the "blast radius" sense; a bug in expense logic can't leak
   cross-tenant data if it was never holding unscoped tenant data in the first place.
3. **Export/Integration Worker**: asynchronous, event-driven, consumes "expense approved" events
   and pushes to QuickBooks/Xero. Split out because: (a) it talks to flaky external third-party
   APIs and must retry/backoff independently without blocking the approval flow (bulkheading; a
   QuickBooks outage should never make an employee unable to submit an expense), and (b) its
   failure mode (a stuck export) has a completely different blast radius and recovery procedure
   than a bug in approval logic.

So: **three containers, not four, and not one.** The split follows transaction coupling and
blast-radius isolation, not resource-per-service dogma.

## 4. Pattern Choices and Why

- **Event-driven** between Core Expense Service and the Export Worker: an "expense approved"
  event, not a synchronous call, because the export worker's job is inherently async (monthly
  batch + retry-heavy) and a synchronous call here would make expense approval latency depend on
  QuickBooks' API being up.
- **Stateless** Core Expense Service and Tenant Service: both sit behind a load balancer with no
  in-memory session state, so either can scale horizontally as tenant count grows.
- **Retry with idempotency** on the Export Worker specifically: each export event carries an
  idempotency key (expense_id + export_attempt) so a retried QuickBooks push after a timeout
  doesn't double-post the same expense.

## 5. Failure Modes Identified

- Tenant Service down → nobody can log in, but in-progress approval data isn't corrupted (blast
  radius: availability, not correctness).
- Export Worker stuck → approvals still work; finance sees a growing backlog in a dashboard, not a
  silent data loss (this is why export is decoupled: a stuck worker degrades gracefully instead
  of blocking the core flow).
- Core Expense Service bug scoping a query without tenant_id → this is the failure this
  architecture is built to make loud and rare: because Tenant Service is the sole source of
  tenant-scoping truth, all cross-service calls pass a verified tenant_id, and Core Expense DB
  queries are reviewed specifically for missing tenant_id filters (a design-review checklist item
  in this scenario, not just a code-review one).

## Takeaway

The lesson generalizes beyond this scenario: draw container boundaries at transaction-coupling and
blast-radius lines, not at resource-name lines. A clean-looking CRUD-per-service diagram that
ignores which writes must be atomic together will force distributed transactions later; the
C4/boundary exercise's job is to catch that before it's baked into four separate deployments.
