# On-Call

Source: `meso/team-practices.md` §4

On-call is the operational practice of ensuring a qualified engineer is reachable and ready to
respond to production issues at all times. An on-call rotation without observable systems and
tested runbooks is a rotation of guesswork.

## Rotation Structure

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

## Runbook Requirements

Every alert that can fire during on-call must have a corresponding runbook. No alert without a
runbook. A runbook that has not been tested is not a runbook; it is a hypothesis.

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

## Alert Quality Standards

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

## Toil Tracking

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

## Rotation Handoff

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

## Example

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

## Failure Mode

Alerts without runbooks produce improvised responses where each on-call engineer reinvents the
diagnosis from scratch. Alert noise desensitises engineers until they stop investigating, so real
incidents go unresponded to. Rotations without written handoffs leave the incoming engineer blind
to known risks.

## Definition of Done (on-call)

- [ ] Every alert has an assigned severity and a tested runbook before going to production
- [ ] On-call rotation handoffs are written and cover incidents, known issues, and toil
- [ ] Toil items identified during on-call are filed as tickets and reviewed quarterly
