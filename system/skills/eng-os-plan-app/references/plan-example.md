# Plan-App Worked Example — Runbook Coverage Tracker

Starting idea, as given by the user in one paragraph:

> "We want a small tool for teams to track which of their services have runbooks and when they
> were last reviewed, so we stop finding out a runbook is stale during an actual incident."

## Phase 1 — Discovery (a plausible clarifying exchange)

**Agent:** A few questions before we go further.

1. Audience: who uses this day to day, and who (if anyone) is this reported up to? For example,
   is this purely for the on-call engineers maintaining runbooks, or does an eng manager also
   need a rollup view?
2. Suite membership: is this standalone, or does it live alongside other internal tools (e.g.
   an existing on-call or incident tool) that it should share a look-and-feel or data with?
3. Core problem, one sentence: is it fair to say: "engineers don't know a runbook is missing or
   stale until they need it during an incident"?

**User:** Audience is on-call engineers day to day, but yes, eng managers want a rollup: like
"which of my team's services are red/yellow/green on runbook freshness." It's standalone, no
existing suite. And yes, your one-sentence problem statement is exactly it.

**Agent:** Two follow-ups. What counts as "stale"? Is there a fixed review interval (e.g. every
90 days), or does it vary per service? And does this tool *host* runbook content, or just track
metadata about runbooks that live elsewhere (e.g. a Confluence/Notion link)?

**User:** Fixed default of 90 days, but a team should be able to override it per service if their
service is lower-risk. And no, don't host content: just track metadata and a link out to wherever
the runbook actually lives.

Discovery is answered enough to proceed.

## Phase 2 — Core Entities

- **Service**: a system or component that should have a runbook. Fields that matter to the
  mental model: name, owning team, review-interval override (defaults to the global 90 days).
- **Runbook**: metadata about the actual runbook document, which lives externally. Fields: link
  URL, last-reviewed date, reviewed-by (an Engineer). Belongs to exactly one Service (a Service
  has zero or one Runbook; zero is a valid, important state, since a missing runbook is the
  whole point of the tool).
- **Team**: a group that owns one or more Services, used for the manager rollup view.
- **Engineer**: a person who can be recorded as having reviewed a Runbook. Belongs to a Team.
- **ReviewEvent**: a historical record each time a Runbook is marked reviewed (not just the
  latest date), needed so the manager rollup can show a trend, not just current state.

## Phase 2b — Scale Targets

**Agent:** Before screens, I need numbers in place of adjectives. How many people use this, how
many Services will it track, and what happens if it is down for a day?

**User:** About 400 engineers and 120 Services at launch, maybe 300 in three years. It is
advisory: if it is down for a day, nobody gets paged late, they just cannot check coverage.
Engineers look at it around standup and managers open the rollup weekly.

Recorded as the brief's Scale Targets (assumptions marked):

| Target | Value |
|---|---|
| Users and traffic | ~400 engineers; peak about 3 requests per second (standup refresh); ~600 users in year 3 (assumed) |
| Data | 120 Services and about 120 Runbooks now, ~300 in year 3 (assumed); ReviewEvents ~480 per year now, ~1,200 per year at 300 Services (four reviews per Service per year); the largest Team owns about a quarter of Services |
| Latency and availability | Service List p50 150 ms, p99 600 ms; 99.5% availability per month (about 3.6 hours of downtime) |
| Recovery | RPO 24 hours (daily backup), RTO 8 hours |
| Tenancy | single-tenant (one organization); no `tenant_id` column |
| Data classification | Internal (owning team names, Runbook URLs); no personal data beyond an Engineer's name; no regulatory scope |

The numbers also rule things out. At about 3 requests per second and a few thousand rows, no
partitioning, read replica, or cell layout is justified, and `eng-os-testing-strategy`'s load
test needs only a few hundred seeded rows to exercise the p99 target. The assumed year-3 figures
are marked so a later review revises them rather than treating them as fact.

## Phase 3 — Screens and Flows

- **Service List** (primary landing screen): reads Service + Runbook. Shows every Service
  with a red/yellow/green freshness indicator computed from Runbook.last-reviewed vs. the
  Service's review interval, or a distinct "missing" state if no Runbook exists. Primary action:
  drill into a Service.
- **Service Detail**: reads/writes Service and Runbook. Shows the runbook link, last-reviewed
  date, review interval, and review history (ReviewEvent list). Primary action: "Mark Reviewed
  Today" (creates a ReviewEvent, updates Runbook.last-reviewed) or "Add Runbook Link" if none
  exists yet.
- **Team Rollup**: reads Service + Runbook + Team, aggregated. Shows, per team, the count of
  green/yellow/red/missing services. Primary action for an eng manager: identify which team/
  service needs attention, then drill into Service Detail.
- **Settings**: reads/writes Service (review-interval override) and the global default
  interval. Primary action: change the default or a per-service override.

Every screen maps to at least one entity and one clear action; no scope creep identified at
this stage (e.g. no separate "notifications" screen was requested, so none is added).

## Phase 4 — Terminology Lock

| Term | Decision | Rejected alternatives | Why |
|---|---|---|---|
| Runbook | canonical noun for the tracked document metadata | "playbook" | "Runbook" was the term used in the original ask; "playbook" is a close synonym that would create ambiguity with incident-response playbooks used elsewhere in the org |
| Stale / Fresh | canonical adjectives for review status | "expired" / "current" | "Expired" implies a hard cutoff/lockout, which this tool doesn't enforce; it's advisory, so softer "stale" fits |
| Review interval | canonical term for the freshness window | "TTL", "cadence" | "TTL" is developer jargon that won't read well in manager-facing rollup UI; "cadence" implies a recurring scheduled action rather than a threshold |
| Mark Reviewed | canonical action name/button label | "Confirm", "Attest" | "Mark Reviewed" is unambiguous and matches the ReviewEvent entity name directly |

No suite membership, so no cross-app synonym collision to resolve.

## Phase 5 — Phased Milestones

1. **Phase 1: Track and see staleness.** Scope: Service, Runbook entities; Service List screen
   with red/yellow/green/missing indicator using the fixed 90-day default only (no per-service
   override yet). DoD: a seeded set of services with varying last-reviewed dates renders the
   correct color for each, verified against the 90-day threshold.
2. **Phase 2: Review workflow.** Scope: ReviewEvent entity; Service Detail screen with "Mark
   Reviewed Today" and "Add Runbook Link" actions. DoD: marking a service reviewed updates its
   color on the Service List without a page reload being required to see stale data, and a
   ReviewEvent row is persisted.
3. **Phase 3: Per-service override + manager rollup.** Scope: Team, Engineer entities; Settings
   screen (per-service interval override); Team Rollup screen. DoD: overriding one service's
   interval to 30 days changes only that service's color computation, and the Team Rollup
   correctly aggregates counts per team.
4. **Phase 4: History and trend.** Scope: expose ReviewEvent history on Service Detail as a
   list, not just the latest date. DoD: a service with 3+ historical reviews shows all of them
   in reverse-chronological order.

Each phase is independently demoable: Phase 1 alone is already useful (visibility into
staleness) even before any write actions exist.

## Phase 6 — Design System Carryover

N/A. Standalone app, not part of a multi-app suite. This app originates its own design system.

## Phase 7 — Mock Data Scale

- ~15 services across 3 teams for a convincing demo.
- Edge cases to include: at least one service with no Runbook at all (the "missing" state), one
  Runbook reviewed yesterday (green), one overdue by a wide margin (deep red, not just
  borderline yellow), and one service with a custom 30-day override that would otherwise show
  green under the 90-day default (to prove the override actually changes the computed color).

## Phase 8 — Approval Gate

The Product Brief (Phases 1-4, 2b, 6-7 assembled under Output Contract headings) is presented back to
the user along with the Phased Milestones from Phase 5. Only after the user explicitly confirms
("yes, this matches what we want") does the flow proceed to `eng-os-bootstrap`. No scaffolding
or code exists yet at this point.
