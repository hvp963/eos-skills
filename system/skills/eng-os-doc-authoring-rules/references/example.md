# Before/After Example — Rule 5: "Include patterns and failure modes"

Rule 5 states: every meso/micro artifact should cover recommended patterns, common mistakes,
likely failure modes, and expected validation criteria. Below is a small meso-layer doc section
(a fictional "Retry Policy" standard) shown before and after applying this rule.

## Before (violates Rule 5)

```markdown
## Retry Policy

Retries should be used for transient failures. Use exponential backoff. Set a reasonable max
retry count. This helps with reliability.
```

Why this fails Rule 5 (and, incidentally, Rule 4, "apply principles in context"):

- It states a recommendation ("use exponential backoff") with no concrete pattern showing what
  that means in practice: no base delay, no jitter, no example.
- It names no common mistake or failure mode. A reader has no way to know what goes wrong if
  they get this slightly wrong: e.g. retrying non-idempotent operations, retrying on the wrong
  error class, or omitting jitter and causing a thundering-herd retry storm against a recovering
  dependency.
- It gives no validation criteria: there's no way for a reviewer to check whether an
  implementation actually satisfies this standard or just superficially "has a retry loop."
- "Reasonable max retry count" is exactly the kind of vague, unbounded phrase the Language Rules
  section warns against ("avoid vague phrases like 'best effort' unless bounded explicitly").

## After (follows Rule 5)

```markdown
## Retry Policy

Retries apply only to operations that are idempotent (see Glossary: Idempotency) and to
failures classified as transient (timeouts, 502/503/504, connection resets), never to 4xx
client errors or to non-idempotent writes without an idempotency key.

**Pattern:** exponential backoff with jitter. Base delay 100ms, multiplier 2x, full jitter
(random value between 0 and the computed delay), capped at 5 retries and a 10s max delay per
attempt.

**Common mistake:** retrying immediately with a fixed delay and no jitter. Under a partial
outage, every failed caller retries in lockstep, which produces a synchronized retry spike
("thundering herd") against a dependency that was starting to recover, often turning a partial
outage into a full one.

**Failure mode:** retrying a non-idempotent write (e.g. "create order") without an idempotency
key on ambiguous failures (e.g. a timeout where the write may have actually succeeded
server-side) produces duplicate records. This is why the idempotency precondition above is
stated first, not as an aside.

**Validation criteria:** a reviewer checks: (1) the retried operation is confirmed idempotent
or guarded by an idempotency key, (2) backoff includes jitter, not a fixed interval, (3) a
max-retry cap and max-delay cap are both set to explicit numbers, not left open-ended, (4) the
retry only fires on the transient-failure class defined above, not blanket on any exception.
```

Why this satisfies Rule 5: it names the recommended pattern concretely (base delay, multiplier,
jitter, caps: actual numbers, not "reasonable"), states a specific common mistake and why it's
harmful, states a specific failure mode with a causal explanation, and gives a reviewer a
checklist to verify compliance rather than a vague aspiration.
