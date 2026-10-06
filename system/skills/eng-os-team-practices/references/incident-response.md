# Incident Response

Source: `meso/team-practices.md` §3

An incident is any event that degrades service availability, data correctness, or user experience
beyond defined thresholds. Incident response is a structured practice, not an improvised reaction.

## Severity Classification

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

## Roles

```
incident_commander (IC):
    - one per incident; owns the response
    - coordinates work; makes decisions when the team is blocked
    - drives communication cadence
    - is not the person debugging; they are managing the process

technical_lead (TL):
    - leads diagnosis and remediation
    - reports status updates to the IC
    - escalates when the issue is outside their scope

communications_lead:
    - required for P1 and P2
    - owns external communication (status page, customer notification)
    - does not diagnose; communicates only what is confirmed

// for small teams, IC and TL may be the same person for P3/P4
// IC and communications_lead must not be the same person for P1/P2
```

## Response Protocol

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

## Escalation Path

```
escalation_triggers:
    - root cause not identified within 30 minutes (P1) / 60 minutes (P2)
    - issue scope is expanding: more services or users affected than initially assessed
    - the technical lead requires access or knowledge outside their scope
    - a rollback is being considered; IC must approve all production rollbacks

escalation_steps:
    1. TL notifies IC that escalation is needed
    2. IC pages secondary responder (see on-call rotation)
    3. IC documents escalation event in incident channel with timestamp and reason
    4. incoming responder receives context handoff before touching anything
```

## Communication Standards

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

## Postmortem Requirements

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
    - postmortems are blameless: name systems and processes, not people
    - corrective actions are commitments, not suggestions; they require owners and due dates
    - postmortem is published within 5 business days of incident resolution
    - corrective action tickets are created before the postmortem is closed
```

## Example — P1 Timeline

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

## Failure Mode

Incidents without assigned roles produce response by whoever speaks first, creating confusion
about who is making decisions. Communication updates that stop during diagnosis leave customers
without information. Postmortems without corrective action owners produce written records of
failures that recur.

## Definition of Done (incident response)

- [ ] Incident severity levels are defined and the response protocol for each is documented
- [ ] Every P1/P2 postmortem is published within 5 business days with owned, dated corrective actions
