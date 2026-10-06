---
name: eng-os-team-practices
description: "Use when doing code review or writing PR descriptions. For incident response, on-call, or tech-debt triage, see this skill's references/."
sources: [meso/team-practices.md]
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Team Practices — Code Review & PR Standards

Code review has two purposes: verifying correctness before a change merges, and transferring
knowledge about what changed and why. A review that catches a bug but teaches nothing is
incomplete; a review that is educational but misses a security flaw is dangerous.

## Reviewer Assignment

```
minimum_reviewers:      1 for routine changes; 2 for architectural or security changes
author_cannot_approve:  true (self-approval is not permitted)
reviewer_selection:
    primary:    an engineer familiar with the affected domain
    secondary:  required for: schema changes, security-touching code,
                AI-IDS changes, public API changes
response_sla:
    routine:    within 1 business day
    urgent:     within 2 hours (flag in PR description)
    blocking:   communicate blockage to author; do not let PRs sit silently
```

## Review Comment Taxonomy

Every comment must be labeled; authors should never have to infer whether a comment blocks merge.

```
[BLOCKING]      must be resolved before merge
                correctness bugs, security issues, standards violations, missing tests,
                breaking contract changes

[SUGGESTION]    non-blocking improvement; author's call
                alternative approaches, style improvements, simplification opportunities

[QUESTION]      seeking understanding; non-blocking unless the answer reveals an issue
                design decisions not explained in the PR description or code

[PRAISE]        explicit acknowledgment of a good decision
                non-obvious improvements, elegant solutions, clear documentation
```

Example:
```
[BLOCKING] raw user_id is passed directly into the query on line 42.
This allows SQL injection. Use a parameterized query:
    db.query("SELECT * FROM orders WHERE id = ?", [user_id])

[SUGGESTION] the three retry conditions on lines 55–58 could be extracted into
a named constant RETRYABLE_STATUS_CODES for readability, not required.
```

## What to Review

```
correctness:  right output for valid inputs? edge cases handled? errors surface correctly?

security:     external input validated at the boundary? secrets from environment (not
              hardcoded)? queries parameterized? no sensitive data logged?

testability:  code structured to be tested in isolation? dependencies injectable?
              happy path + at least one failure path covered? integration tests isolated
              from unit tests?

standards:    meets micro/coding-standards/ for the language? naming consistent with
              code-conventions skill? public functions have JSDoc-style docstrings?

contracts:    if a public API/event schema/data contract changed, is it versioned?
              is there an ADR for any significant design decision in this change?
```

**What not to review:** formatting/indentation/import order (linter's job; if no formatter is
configured, that's the fix, not a PR comment); personal style preferences not grounded in a
declared convention; architecture decisions already agreed in the design phase (relitigating in
review blocks shipping; raise before implementation).

## PR Description Requirements

```
title:  imperative mood, present tense, under 72 chars
        correct:    "Add retry logic to payment service client"
        incorrect:  "added retry logic", "retry stuff", "WIP"

body:
    ## What changed  (one paragraph or bullet list)
    ## Why            (motivation, links to tickets/ADRs)
    ## How to verify  (test commands, curl examples, or manual steps)
    ## Notes (optional) (limitations, follow-ups, conscious trade-offs)
```

Example: a filled-in PR description following the template above:

```markdown
Title: Add retry logic to payment service client

## What changed
Wraps calls to the payment service client in an exponential-backoff retry (3 attempts,
base delay 200ms). Retries only on the status codes in RETRYABLE_STATUS_CODES (502, 503, 504).

## Why
Payment provider has intermittent 503s under load (see INCIDENT-2026-0512). Retrying
transient failures instead of surfacing them to the customer reduces false checkout failures.
Ticket: PROJ-1821.

## How to verify
1. `npm test -- payment-client.test.ts`: covers retry-then-succeed and retry-exhausted paths
2. Manually: set `PAYMENT_MOCK_FAILURE_RATE=0.5` locally and run a checkout; confirm retries
   appear in logs and the request eventually succeeds or fails cleanly after 3 attempts

## Notes
Does not retry on 4xx (client errors are not transient). Follow-up: add a circuit breaker
if 503 rate stays elevated; tracked in PROJ-1830, not part of this PR.
```

## PR Size

```
target:     under 400 lines of logic code changed
acceptable: up to 800 lines with clear justification in the description
exceptions: auto-generated code, lock file updates, large no-logic-change refactors

split_strategy when too large:
    1. preparatory refactor PR (no behavior change)
    2. feature or fix PR
    3. cleanup / follow-up PR
```
Large PRs are not faster to ship: they get shallower review and are harder to revert.

## Branch Naming

```
pattern:  <type>/<short-description>   type: feat | fix | refactor | chore | docs | test | hotfix
examples: feat/add-payment-retry, fix/order-total-rounding, hotfix/null-pointer-on-empty-cart
```

## Draft PRs

Use for: work needing early feedback on direction; blocked by an unmerged dependency;
incremental large changes wanting CI feedback. Rules: never merge a draft; mark ready before
requesting formal review; don't leave a draft open longer than one sprint without a status comment.

## Elsewhere in This Skill

- `references/incident-response.md`: severity classification, roles (IC/TL/comms), response
  protocol timelines, escalation, communication formats, postmortem requirements. Open this when
  triaging or running an incident, or writing a postmortem.
- `references/oncall.md`: rotation structure, runbook requirements, alert quality standards,
  toil tracking, rotation handoff format. Open this when setting up or running an on-call rotation.
- `references/tech-debt.md`: debt classification (deliberate/accidental/blocking), logging
  requirements, prioritization criteria, debt budget. Open this when triaging technical debt or
  deciding whether to log/escalate it.

## Failure Modes

- Review comments with no label, so the author cannot tell what blocks the merge (Review Comment Taxonomy).
- Self-approval, or one reviewer on a schema, security, AI-IDS, or public API change (Reviewer Assignment).
- A PR description with no why or how-to-verify, which makes the reviewer reconstruct intent from the diff.
- A PR past 800 lines of logic with no justification: it gets shallower review and is harder to revert.
- A PR waiting silently past its response SLA instead of the blockage being communicated to the author.

## Definition of Done

**PR, before requesting review:**
```
- [ ] CI passes (lint, tests, build)
- [ ] PR description is complete (what, why, how to verify)
- [ ] self-review completed: read the diff as if you are the reviewer
- [ ] no debugging artifacts (print statements, commented-out code, TODO/FIXME)
- [ ] ADR created if this PR contains a significant architectural decision
```

**Team practices in place when:**
- [ ] Code review criteria are written down and labeling conventions are used on every review
- [ ] PRs consistently include what/why/how-to-verify
- [ ] (see references/ for incident, on-call, and tech-debt DoD items)
