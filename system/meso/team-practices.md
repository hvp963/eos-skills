# Team Practices

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for the recurring practices that determine how an engineering team reviews code, ships safely, responds to incidents, operates on-call, and manages technical debt, consistently, regardless of team size or project type.

### What This Is Not
- not a project management or sprint methodology guide
- not a hiring or performance review guide
- not a tool tutorial (GitHub, PagerDuty, Jira, etc.)
- not a substitute for the domain guides: this governs how teams work, not how systems are designed

## Scope
- Level: Meso
- Applies To: All engineering teams building product, data, or AI systems
- See Also: `meso/documentation.md`; ADR standards referenced in code review and incident postmortems
- See Also: `meso/observability.md`; signal design required before on-call rotation is effective
- See Also: `meso/deployment.md`; rollback and health check standards referenced in incident response
- See Also: `micro/templates/adr-template.md`; ADR format for significant decisions

---

## Applied Principles

### Explicitness Over Implicitness
Review criteria, severity definitions, escalation paths, and debt thresholds must be written down. Practices that live in people's heads disappear when those people leave and are applied inconsistently in the meantime.

### Validation at Boundaries
Code review is a validation boundary. Incident response is a boundary between degraded state and restored state. Both require explicit pass/fail criteria, not judgment calls applied differently by each reviewer or responder.

### Separation of Concerns
A pull request should own one concern. An on-call engineer should own one incident at a time. A postmortem should address one failure. Mixing concerns at these boundaries produces unclear reviews, confused incident response, and postmortems that reach no actionable conclusions.

### Observability as a First-Class Concern
An on-call rotation without observable systems is a rotation of guesswork. Alerts without runbooks produce improvised responses that make incidents worse. Every practice in this guide that touches production assumes the observability standards in `meso/observability.md` are already in place.

### Testability as a Design Property
Code review verifies testability as a design property, not as an afterthought. A PR that introduces untestable code fails the review, regardless of whether tests were written.

### Security as a Design Constraint
Code review is the last human checkpoint before a change enters the codebase. Security review is not a separate pass: it is part of every review.

---

## 1. Code Review

Code review has two purposes: verifying correctness before a change merges, and transferring knowledge about what changed and why. Both matter. A review that catches a bug but teaches nothing is incomplete. A review that is educational but misses a security flaw is dangerous.

### Reviewer Assignment

```
rules:
    minimum_reviewers:      1 for routine changes; 2 for architectural or security changes
    author_cannot_approve:  true — self-approval is not permitted
    reviewer_selection:
        primary:    an engineer familiar with the affected domain
        secondary:  required for: schema changes, security-touching code,
                    AI-IDS changes, public API changes
    response_sla:
        routine:    within 1 business day
        urgent:     within 2 hours (flag in PR description)
        blocking:   communicate blockage to author; do not let PRs sit silently
```

### Review Comment Taxonomy

Every comment must be labeled with its intent. Authors should not have to infer whether a comment blocks the merge.

```
[BLOCKING]      — must be resolved before merge
                  use for: correctness bugs, security issues, standards violations,
                           missing tests, breaking contract changes

[SUGGESTION]    — non-blocking improvement; author's call
                  use for: alternative approaches, style improvements,
                           simplification opportunities

[QUESTION]      — seeking understanding; non-blocking unless the answer reveals an issue
                  use for: design decisions that are not explained in the PR description or code

[PRAISE]        — explicit acknowledgment of a good decision
                  use for: non-obvious improvements, elegant solutions,
                           clear documentation
```

### What to Review

```
correctness:
    - does the logic produce the right output for valid inputs?
    - are edge cases handled?
    - do error conditions surface correctly?

security:
    - is all external input validated at the boundary?
    - are secrets read from environment, not hardcoded?
    - are queries parameterized?
    - is no sensitive data logged?

testability and tests:
    - is the code structured so it can be tested in isolation?
    - are external dependencies injectable?
    - do tests cover the happy path and at least one failure path?
    - are integration tests isolated from unit tests?

standards compliance:
    - does the code meet micro/coding-standards/ for the relevant language?
    - is the naming consistent with meso/code-conventions.md?
    - are public functions documented with JSDoc-style docstrings?

contracts:
    - if a public API, event schema, or data contract changed, is it versioned?
    - is there an ADR for any significant design decision made in this change?
```

### What Not to Review

```
- formatting, indentation, or import ordering: these are enforced by linters and formatters
  (if a formatter is not configured, that is the fix, not a PR comment)
- personal style preferences not grounded in a declared convention
- architecture decisions that were made and agreed in the design phase: relitigating them
  in a PR review is too late and blocks shipping; raise them before implementation
```

### Example

```
// Correct — labeled, actionable, explains why
[BLOCKING] raw user_id is passed directly into the query on line 42.
This allows SQL injection. Use a parameterized query:
    db.query("SELECT * FROM orders WHERE id = ?", [user_id])

[SUGGESTION] the three retry conditions on lines 55–58 could be extracted into
a named constant RETRYABLE_STATUS_CODES for readability, not required.

[QUESTION] why is the fallback set to an empty list rather than raising here?
If that's intentional (caller handles empty), a comment explaining why would
prevent the next reader from "fixing" it.

[PRAISE] the decision to inject the database client rather than instantiate it
inside the function makes this easy to test — good call.

// Incorrect — ambiguous, no label, unhelpful
This looks wrong.
Can you change this?
Why did you do it this way?
```

#### Failure Mode
Unlabeled comments that authors interpret as blocking when they are suggestions, or as suggestions when they are blocking, causing either rework on non-issues or merges with real problems unfixed. Reviews that focus on style and miss correctness issues. Reviews that are thorough but arrive three days after the PR was opened.

---

## 2. Pull Request Standards

A pull request is a unit of reviewable change. Its description is a contract with reviewers and with future engineers reading the git history.

### PR Description Requirements

Every PR must include:

```
title:
    format:     imperative mood, present tense, under 72 characters
    correct:    "Add retry logic to payment service client"
    incorrect:  "added retry logic", "retry stuff", "WIP"

body:
    ## What changed
    [What was added, modified, or removed. One paragraph or bullet list.]

    ## Why
    [The motivation. Why was this change necessary? Links to tickets or ADRs.]

    ## How to verify
    [Steps to confirm the change works. Include test commands, curl examples,
     or manual steps if automated tests do not cover the full behavior.]

    ## Notes (optional)
    [Anything a reviewer should know that is not obvious from the diff:
     known limitations, follow-up tickets, conscious trade-offs made.]
```

### PR Size

```
guidance:
    target:     under 400 lines of logic code changed
    acceptable: up to 800 lines with a clear justification in the PR description
    exceptions: auto-generated code, lock file updates, large refactors with no logic change

// when a PR is too large:
split_strategy:
    1. one PR for the preparatory refactor (no behavior change)
    2. one PR for the feature or fix
    3. one PR for the cleanup or follow-up

// large PRs are not faster — they take longer to review, receive shallower feedback,
// and are harder to revert if a problem is found post-merge
```

### Branch Naming

```
pattern:    <type>/<short-description>
            type:  feat | fix | refactor | chore | docs | test | hotfix

examples:
    feat/add-payment-retry
    fix/order-total-rounding
    refactor/extract-config-module
    hotfix/null-pointer-on-empty-cart
```

### Draft PRs

```
use_when:
    - work in progress that needs early feedback on direction
    - blocked by a dependency that has not merged yet
    - implementing a large change incrementally and want CI feedback

rules:
    - draft PRs must not be merged
    - mark as ready for review before requesting a formal review
    - do not leave a draft PR open longer than one sprint without a comment on its status
```

### Definition of Done — PR

```
before requesting review:
    - [ ] CI passes (lint, tests, build)
    - [ ] PR description is complete (what, why, how to verify)
    - [ ] self-review completed: read the diff as if you are the reviewer
    - [ ] no debugging artifacts (print statements, commented-out code, TODO/FIXME)
    - [ ] ADR created if this PR contains a significant architectural decision
```

#### Failure Mode
PRs with no description force reviewers to infer intent from the code, producing reviews that address what the code does rather than whether it does the right thing. Oversized PRs receive rubber-stamp approvals because the reviewer cannot hold the entire change in mind at once.

---

## 3. Incident Response

An incident is any event that degrades service availability, data correctness, or user experience beyond defined thresholds. Incident response is a structured practice, not an improvised reaction.

### Severity Classification

```
P1 — Critical:   total service outage; all users affected; data at risk
                 example: the order API returns 500 for all requests

P2 — High:       significant degradation; majority of users affected or key flow broken
                 example: checkout succeeds but order confirmation emails are not sent

P3 — Moderate:   partial degradation; subset of users affected; workaround exists
                 example: the analytics dashboard is stale by 4 hours; data pipeline delayed

P4 — Low:        minor issue; no user-visible impact; or cosmetic / informational
                 example: a non-critical background job is failing silently
```

### Roles

```
incident_commander (IC):
    - one per incident; owns the response
    - coordinates work; makes decisions when the team is blocked
    - drives communication cadence
    - is not the person debugging — they are managing the process

technical_lead (TL):
    - leads diagnosis and remediation
    - reports status updates to the IC
    - escalates when the issue is outside their scope

communications_lead:
    - required for P1 and P2
    - owns external communication (status page, customer notification)
    - does not diagnose — communicates only what is confirmed

// for small teams, IC and TL may be the same person for P3/P4
// IC and communications_lead must not be the same person for P1/P2
```

### Response Protocol

```
P1 response:
    00:00   alert fires → on-call engineer acknowledges within 5 minutes
    00:05   declare P1; assign IC and TL; open incident channel
    00:10   first customer status page update: "We are aware of an issue affecting [service]. Investigation is underway."
    00:15   IC posts first internal status update in incident channel
    00:30   customer update cadence begins: every 30 minutes until resolved
    00:30   escalate to second responder if root cause not identified
    [resolution]  IC declares incident resolved; resolution update posted
    +24h    postmortem scheduled

P2 response:
    00:00   alert fires → acknowledge within 10 minutes
    00:10   declare P2; assign IC; open incident channel
    00:20   first internal update; assess need for external communication
    01:00   escalate if not resolved
    [resolution]  IC declares resolved
    +48h    postmortem scheduled

P3/P4 response:
    acknowledge within 1 business hour
    track in ticketing system; assign owner
    no dedicated incident channel required unless escalated
    postmortem optional; judgment call by IC
```

### Escalation Path

```
escalation_triggers:
    - root cause not identified within 30 minutes (P1) / 60 minutes (P2)
    - issue scope is expanding: more services or users affected than initially assessed
    - the technical lead requires access or knowledge outside their scope
    - a rollback is being considered: IC must approve all production rollbacks

escalation_steps:
    1. TL notifies IC that escalation is needed
    2. IC pages secondary responder (see on-call rotation, Section 4)
    3. IC documents escalation event in incident channel with timestamp and reason
    4. incoming responder receives context handoff before touching anything
```

### Communication Standards

```
internal_update_format:
    Time:     [HH:MM UTC]
    Status:   Investigating | Identified | Monitoring | Resolved
    Summary:  [one sentence: what is known]
    Impact:   [who and what is affected]
    Next:     [what is being done and when the next update will come]

external_update_format (status page):
    [Service name] — [brief description of user-visible impact]
    Status: [Investigating | Identified | Monitoring | Resolved]
    We are [investigating / have identified / are monitoring a fix for] an issue
    affecting [description]. We will provide an update by [time].

    // Do not include: internal team names, root cause hypotheses, financial figures,
    // speculative timelines, or language that assigns blame
```

### Postmortem Requirements

```
required_for:   all P1 incidents; all P2 incidents; repeated P3 incidents

content:
    - incident timeline (objective, timestamped)
    - root cause (confirmed, not hypothesized)
    - contributing factors (system, process, or human factors that allowed the failure)
    - customer impact (scope, duration)
    - what went well (effective detection, fast communication, clean rollback)
    - corrective actions (each with: what, owner, due date)
    - signals that should have fired earlier but did not

rules:
    - postmortems are blameless — name systems and processes, not people
    - corrective actions are commitments, not suggestions; they require owners and due dates
    - postmortem is published within 5 business days of incident resolution
    - corrective action tickets are created before the postmortem is closed
```

### Example — P1 Timeline

```
09:03   Alert fires: "Order API error rate > 5% for 2 consecutive minutes"
09:05   On-call engineer acknowledges; declares P1
09:06   IC assigned: Ana. TL assigned: Ben. Incident channel opened: #inc-2026-0603
09:08   Status page updated: "We are investigating an issue affecting order placement."
09:10   Ben identifies increased error rate began at 09:01 following a deployment at 09:00
09:12   Ana approves rollback; Ben executes
09:15   Rollback complete; error rate returns to baseline
09:18   Status page updated: "The issue affecting order placement has been resolved."
09:20   IC declares P1 resolved; all-clear posted in incident channel
09:20   Postmortem scheduled for 2026-06-05

[Postmortem finding]
Root cause: the 09:00 deployment contained a misconfigured database connection pool
that exhausted under load within 60 seconds of startup.
Corrective actions:
    1. Add connection pool exhaustion alert to deployment health check — Ben — 2026-06-10
    2. Add connection pool metrics to deployment canary criteria — Ana — 2026-06-10
    3. Extend pre-prod load test to cover connection pool behavior — Carlos — 2026-06-17
```

#### Failure Mode
Incidents without assigned roles produce response by whoever speaks first, creating confusion about who is making decisions. Communication updates that stop during diagnosis leave customers without information. Postmortems without corrective action owners produce written records of failures that recur.

---

## 4. On-Call

On-call is the operational practice of ensuring a qualified engineer is reachable and ready to respond to production issues at all times. An on-call rotation without observable systems and tested runbooks is a rotation of guesswork.

### Rotation Structure

```
rotation:
    unit:           one engineer per rotation period
    period:         1 week; Monday 09:00 → following Monday 09:00 (local time)
    handoff:        written handoff required at rotation end (see below)
    coverage:       24/7 for P1/P2; business hours for P3/P4 unless escalated
    backup:         secondary on-call always defined; auto-escalated after 5-minute non-response

eligibility:
    - must have completed an incident response shadowing session before solo on-call
    - must have read all runbooks for services in their rotation scope
    - must have production access required to execute runbooks before rotation begins
```

### Runbook Requirements

Every alert that can fire during on-call must have a corresponding runbook. No alert without a runbook. A runbook that has not been tested is not a runbook: it is a hypothesis.

```
runbook_structure:
    name:           [alert name, must match the alert exactly]
    severity:       P1 | P2 | P3 | P4
    service:        [service name]
    owner:          [team]
    last_tested:    [YYYY-MM-DD]

    What this alert means:
        [One paragraph. What condition triggered the alert. What it indicates.]

    Immediate steps (first 5 minutes):
        1. [First action, specific command or dashboard link]
        2. [Second action]
        3. [Decision point: if X → go to step 4; if Y → escalate]

    Diagnostic steps:
        1. [How to confirm the root cause]
        2. [Queries, commands, or dashboards to run]

    Remediation:
        option_a:   [description] → [commands or steps]
        option_b:   [description] → [commands or steps]
        escalate_if: [condition under which to page the secondary]

    Verification:
        [How to confirm the issue is resolved: specific metric or check]

    Links:
        dashboard:  [URL]
        logs:       [query or log group]
        postmortem: [link to any prior postmortems for this alert]
```

### Alert Quality Standards

```
a good alert:
    - fires when something actionable has happened or is imminently about to happen
    - has a single, unambiguous meaning
    - has a runbook linked in the alert body
    - specifies the affected service and severity in its title
    - fires no more often than it is investigated

a bad alert:
    - fires when something might eventually become a problem but no action is possible now
    - fires on a symptom so general that diagnosis always starts from scratch
    - has no runbook: "figure it out"
    - fires repeatedly without being investigated or acknowledged

alert_hygiene_rule:
    if an alert fires and is not investigated, it is noise
    if an alert fires and is always resolved the same way, it should be automated
    if an alert fires and is never actionable, it should be deleted
```

### Toil Tracking

```
toil:
    definition: manual, repetitive operational work that could be automated or eliminated
    examples:   manually restarting a service after every deploy
                manually reprocessing failed jobs in a queue
                manually rotating a key because no automation exists

tracking:
    every toil item identified during on-call is filed as a ticket
    toil tickets carry: description, frequency, estimated time cost per occurrence, owner
    toil backlog is reviewed at the start of each quarter
    toil reduction is a first-class engineering investment, not a nice-to-have

threshold:
    if on-call toil exceeds 25% of an engineer's rotation time, it is a system problem,
    not a people problem; escalate to engineering leadership
```

### Rotation Handoff

```
handoff_contents:
    week_summary:
        - incidents that occurred (link to postmortem if written)
        - alerts that fired but did not escalate to incidents (and why)
        - runbooks that were executed and any gaps found
    known_issues:
        - degraded but non-incident conditions the incoming engineer should watch
        - deployments scheduled during the incoming rotation
        - services under elevated risk
    toil_logged:
        - list of toil tickets filed during the rotation
    notes:
        - anything the incoming engineer needs to know that is not in a ticket
```

### Example

```
// Bad alert — fails alert quality standards
Alert: "High CPU on order-service-prod"
Runbook: none
Fires: 12 times per day; usually resolves in 3 minutes

// Why this is bad:
// - CPU spikes that self-resolve are noise
// - no runbook means every response is improvised
// - fires 12 times/day = toil; the on-call engineer learns to ignore it

// Good alert — meets alert quality standards
Alert: "order-service error rate > 2% for 5 consecutive minutes [P2]"
Runbook: https://docs.internal/runbooks/order-service-high-error-rate
Fires: when the defined threshold is breached for a sustained window

// Why this is good:
// - fires on a meaningful, actionable condition
// - sustained window eliminates transient spikes
// - linked runbook defines exactly what to do
// - fires rarely enough to be investigated every time
```

#### Failure Mode
Alerts without runbooks produce improvised responses where each on-call engineer reinvents the diagnosis from scratch. Alert noise desensitises engineers until they stop investigating, so real incidents go unresponded to. Rotations without written handoffs leave the incoming engineer blind to known risks.

---

## 5. Technical Debt Management

Technical debt is the gap between the current state of the codebase and the state it would need to be in to support future work safely and efficiently. Not all debt is bad: deliberate, time-bounded debt can be a rational trade-off. Untracked, unowned debt is the problem.

### Classification

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

### Logging Requirements

```
every debt item must have:
    description:    what the current state is and why it is suboptimal
    impact:         what it makes harder, slower, or riskier
    owner:          who is responsible for resolving it
    created:        when it was identified
    priority:       critical | high | medium | low (see criteria below)
    adr_reference:  required for deliberate debt — link to the decision that incurred it

// deliberate debt that is not logged at the point of incurrence
// is indistinguishable from accidental debt one sprint later
```

### Prioritization Criteria

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

### Debt Budget

```
allocation:
    sustainable_rate:   10–20% of sprint capacity reserved for debt reduction
    minimum:            5%; below this, critical and high debt will accumulate
                        faster than it is resolved
    escalation:         if blocking_debt items exist, they are prioritized above
                        new feature work for that sprint regardless of budget

// debt budget is not the ceiling: it is the floor
// teams that invest 0% in debt reduction are borrowing against future velocity
```

### When Debt Becomes a Blocker

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

### Example

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
ADR:           none — this was not a deliberate decision
```

#### Failure Mode
Deliberate debt that is not logged at incurrence becomes invisible and unowned within one sprint. Debt backlogs with no owners or priorities are never resolved. Teams that reserve 0% capacity for debt reduction find that every feature takes longer as the codebase degrades, but cannot point to why, because they have no record of what they are paying interest on.

---

## Failure Modes

- review comments without labels produce ambiguity about what is blocking and what is a suggestion, causing both unnecessary rework and merges with real issues unresolved
- PRs without descriptions force reviewers to infer intent; shallow reviews result
- oversized PRs receive rubber-stamp approvals; issues are found post-merge
- incidents without assigned roles produce response by whoever speaks first
- on-call alerts without runbooks produce improvised, inconsistent responses
- alert noise that is never addressed desensitises engineers until real incidents go uninvestigated
- postmortems without corrective action owners produce written records of failures that recur
- technical debt logged with no owner or priority is never resolved and accumulates invisibly
- deliberate debt not logged at the point of incurrence is indistinguishable from negligence one sprint later

---

## Definition of Done

Team practices are in place when:
- code review criteria are written down and applied consistently: labeling conventions are used on every review
- PRs consistently include a description covering what changed, why, and how to verify
- incident severity levels are defined and the response protocol for each is documented
- every alert has an assigned severity and a tested runbook before going to production
- on-call rotation handoffs are written and cover incidents, known issues, and toil
- toil items identified during on-call are filed as tickets and reviewed quarterly
- every technical debt item has a description, owner, priority, and creation date
- deliberate debt has an ADR and a resolution target at the point it is incurred
- the team reserves a defined percentage of sprint capacity for debt reduction
