# Technical Debt Management

Source: `meso/team-practices.md` §5

Technical debt is the gap between the current state of the codebase and the state it would need to
be in to support future work safely and efficiently. Not all debt is bad: deliberate, time-bounded
debt can be a rational trade-off. Untracked, unowned debt is the problem.

## Classification

```
deliberate_debt:
    definition: a conscious trade-off made under time or resource constraints
    example:    "We are shipping with in-process caching instead of Redis to meet
                 the launch date. This will not scale past 3 instances. We have a
                 ticket to replace it in Q3."
    requirement: documented decision with owner and timeline at the point it is incurred

accidental_debt:
    definition: degradation that accumulated without a conscious decision
    example:    a module that started as a utility file and grew into a god class
    requirement: identified, filed as a ticket, and triaged when discovered

blocking_debt:
    definition: debt that actively prevents safe feature development or operation
    example:    no integration tests exist for the payment module; every change
                carries unquantifiable risk; the team has slowed to 1 PR/week
    requirement: escalated; prioritized above new feature work
```

## Logging Requirements

```
every debt item must have:
    description:    what the current state is and why it is suboptimal
    impact:         what it makes harder, slower, or riskier
    owner:          who is responsible for resolving it
    created:        when it was identified
    priority:       critical | high | medium | low (see criteria below)
    adr_reference:  required for deliberate debt; link to the decision that incurred it

// deliberate debt that is not logged at the point of incurrence
// is indistinguishable from accidental debt one sprint later
```

## Prioritization Criteria

```
critical:   blocks safe operation or delivery; must be resolved before next feature work
            example: no tests for a module being actively changed; security vulnerability
                     with a known exploit; data corruption risk

high:       significantly slows delivery or increases operational risk
            example: a component that takes 4 hours to deploy manually because
                     automation was never built; a schema that cannot be migrated
                     without a full outage

medium:     noticeable friction; degraded but manageable
            example: a module with low cohesion that slows every PR that touches it;
                     manual steps in a process that should be automated

low:        cosmetic or minor; negligible impact on velocity or risk
            example: inconsistent naming in a rarely-touched file;
                     outdated comments that do not affect behavior
```

## Debt Budget

```
allocation:
    sustainable_rate:   10–20% of sprint capacity reserved for debt reduction
    minimum:            5%; below this, critical and high debt will accumulate
                        faster than it is resolved
    escalation:         if blocking_debt items exist, they are prioritized above
                        new feature work for that sprint regardless of budget

// debt budget is not the ceiling; it is the floor
// teams that invest 0% in debt reduction are borrowing against future velocity
```

## When Debt Becomes a Blocker

```
escalation_triggers:
    - a debt item directly prevents a feature from being safely implemented
    - the debt is a security vulnerability with a known exploit
    - the debt causes more than 2 incidents per month
    - the team's sustained delivery velocity has dropped measurably due to a specific debt item

escalation_process:
    1. engineering lead files a blocker ticket with measured impact
    2. blocker is brought to the next planning session as a first-class agenda item
    3. team agrees a resolution timeline before any new features in the affected area begin
    4. resolution is tracked with the same rigor as a feature milestone
```

## Example

```
// Deliberate debt — correctly logged at point of incurrence
Ticket: DEBT-041
Description:   The search service uses an in-process LRU cache instead of a shared
               cache layer. This is sufficient for a single-instance deployment.
Impact:        Cannot scale beyond 1 instance without cache inconsistency. Cache is
               invalidated on restart, causing cold-start latency spikes.
Owner:         platform-team
Created:       2026-05-12
Priority:      high
ADR:           docs/decisions/adr-007-in-process-cache-tradeoff.md
               (decision: acceptable until we exceed 3 instances; revisit in Q3 2026)
Resolution target: Q3 2026

// Accidental debt — discovered during a PR review
Ticket: DEBT-042
Description:   The notification module has grown to 800 lines with 6 unrelated
               responsibilities. Every PR that touches notifications takes 3x longer
               to review than equivalent changes elsewhere.
Impact:        Slows delivery; high risk of regressions on notification changes.
Owner:         backend-team
Created:       2026-06-01
Priority:      medium
ADR:           none, this was not a deliberate decision
```

## Failure Mode

Deliberate debt that is not logged at incurrence becomes invisible and unowned within one sprint.
Debt backlogs with no owners or priorities are never resolved. Teams that reserve 0% capacity for
debt reduction find that every feature takes longer as the codebase degrades, but cannot point to
why, because they have no record of what they are paying interest on.

## Definition of Done (technical debt)

- [ ] Every technical debt item has a description, owner, priority, and creation date
- [ ] Deliberate debt has an ADR and a resolution target at the point it is incurred
- [ ] The team reserves a defined percentage of sprint capacity for debt reduction
