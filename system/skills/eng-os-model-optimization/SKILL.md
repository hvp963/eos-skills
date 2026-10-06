---
name: eng-os-model-optimization
description: "Use when tuning an AI-assisted coding workflow for token cost, latency, or output quality: prompt caching, context budgeting, effort/reasoning settings, subagent parallelization, tool-use shaping. Provider-specific tactics in references/."
sources:
  - meta/agent-operations.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Model Optimization

Provider-agnostic tactics for tuning an AI-assisted engineering workflow. Provider-specific
detail lives in `references/`; load only the one relevant to the current stack.

- `references/claude.md`: Claude/Anthropic-specific tactics
- `references/openai.md`: OpenAI-specific tactics
- `references/custom-oss.md`: self-hosted / open-weight model tactics

## Progressive Disclosure

Keep a small, always-loaded core and push detail to on-demand references or subagent calls. This
skill set is the worked example: `eng-os-core` is always loaded and cheap; the checkpoint table
routes to domain skills (this one included) only when needed, and each domain skill
pushes its own bulk content into `references/*.md` that loads only when read. Never inline
material "just in case": every always-loaded token is a recurring cost on every single turn.

## Context-Budget Discipline

- Treat the always-loaded portion of any skill, prompt, or system instruction as a scarce
  resource; budget it, don't let it grow by accretion.
- When a skill or doc grows past a quick scan, move the bulk to `references/` and leave a router
  paragraph plus a link behind.
- Prefer a fresh on-demand agent call over inlining large reference material "in case it's
  needed": most invocations won't need it, and the cost is paid on every turn regardless.
- Re-audit always-loaded content periodically: content that was essential at project start often
  becomes dead weight once patterns are established.

## Prompt Structure Ordering

Put static, reusable content first; put volatile, turn-specific content last. This is not only
tidiness: on providers with prompt caching, cache hits are keyed on a stable prefix. Any
volatile content placed before the stable block (a timestamp, a turn counter, a freshly
interpolated variable) invalidates the cache for everything after it. Order every prompt as:
system/persona → stable project context → stable tool definitions → (cache boundary) →
conversation history → this turn's volatile input.

## Tool-Definition Minimalism

Fewer, well-scoped tools beat many overlapping ones. Every tool definition is always-loaded
context competing for the same budget as everything else. Before adding a new tool, check
whether an existing tool's parameters can be extended instead. Overlapping tools also increase
the model's chance of picking the wrong one, which costs more than the tokens saved by not
consolidating.

## Parallelize Independent Work

Default to parallel subagents/forks for independent sub-tasks rather than a serial single-agent
loop. Use a synchronization barrier only at the point a later step genuinely needs all prior
results together, not preemptively. Serial execution should be the exception you can justify
("step 2 depends on step 1's output"), not the default.

## Reuse Context Instead of Re-Deriving It

When a follow-up task is a continuation of prior work, continue or fork the agent/session that
already holds the relevant history rather than spawning a fresh one and re-explaining
background. Re-deriving context costs both tokens (re-stating everything) and quality (the fresh
agent may reconstruct the situation slightly wrong). Spawn fresh only when the task is genuinely
independent of what came before, or when isolation from prior context is the point (e.g., an
adversarial second opinion).

## Task Scope Containment

Unbounded exploration and unbounded polish are both economy failures, not only quality
failures: every extra file read, every unrelated refactor, and every retry past the point of
diminishing returns is a token and latency cost with no corresponding gain.

- **Bound exploration to the request.** Read only the files the current task touches.
  Do not scan the repository speculatively "to be safe": if the task doesn't name or imply a
  location, ask or infer from the most direct evidence, don't sweep.
- **Bound the change to the request.** Solve the stated problem with the smallest correct
  change. Unrelated refactoring, renaming, or file moves are a separate task even when they
  look like an improvement; bundling them in means the requester didn't ask for the risk or
  the review surface they now have.
- **Don't add what wasn't asked for.** New dependencies, new abstractions, alternative
  implementations offered "just in case," and defensive handling for scenarios that can't occur
  all cost tokens and review time without being requested. Add them only when the task requires
  them or the requester asks.
- **State assumptions once, briefly, and move on.** When a requirement is underspecified, make
  the most reasonable assumption, say what it was in one line, and proceed. Escalate to a
  clarifying question only when the ambiguity blocks progress, not for every gap.
- **Stop after two failed attempts at the same approach.** Retrying the same fix a third time
  rarely succeeds where two didn't; it spends more tokens finding that out. After two
  failed attempts, stop, summarize the blocker and the likely cause, and recommend the next
  investigation instead of continuing to iterate blindly.
- **Stop when the requested outcome is met.** Completion is a state, not a checkpoint to
  optimize past. Once the task's own Definition of Done is satisfied, stop: don't keep
  refactoring, don't run extra passes "while you're in there," and don't perform cleanup that
  wasn't part of the request.
- **Recognize session drift.** When a new request is substantially unrelated to the work the
  current session has been carrying, recommend starting a fresh session rather than continuing
  to carry irrelevant history forward; the old context adds cost and dilutes relevance without
  helping the new task.

## Failure Modes

- A timestamp, turn counter, or interpolated variable placed ahead of the stable prompt block invalidates the cache prefix for everything after it, on every turn.
- Always-loaded content grows by accretion until it is the largest recurring cost in the session, and nobody re-audits it.
- Overlapping tool definitions raise the chance of the wrong tool being picked, which costs more than the tokens saved by leaving them unconsolidated.
- Independent sub-tasks run serially by default, or a synchronization barrier is placed before a later step needs the results.
- A continuation task goes to a fresh agent that re-derives the background and reconstructs it slightly wrong.
- Exploration and polish run past the request: speculative repository sweeps, unrelated refactors, a third retry of an approach that failed twice.

## Example

**Before (violates cache-ordering and context-budget guidance):**

```
System: You are a coding assistant.
Current timestamp: 2026-07-01T14:32:07Z
Request ID: 8f3a1c2e

Full project context:
<15,000 tokens of CLAUDE.md, architecture notes, and API reference inlined here,
 re-sent identically on every single turn>

Turn count: 47

User: Add a `phone` field to the customer creation endpoint.
```

Two problems:

1. The timestamp and request ID are volatile values placed *before* the large stable context
   block. On a provider with prompt caching, this busts the cache prefix for the entire 15,000
   tokens of project context on every turn, even though that content never changed;
   the model pays full input-token cost every time instead of a cache-hit discount.
2. The full 15,000-token project context is inlined unconditionally, "just in case" it's needed,
   even for a small, well-scoped task like adding one field. That's a recurring cost paid on
   every turn regardless of whether this turn's task touches most of that material.

**After (follows the guidance):**

```
System: You are a coding assistant.

[stable project context: ~1,500 token summary (core entities, active skills, key
 conventions) with a pointer: "full architecture notes: docs/architecture.md,
 read on demand if this task touches system design"]

[stable tool definitions]

--- cache boundary ---

[conversation history so far]

User: Add a `phone` field to the customer creation endpoint.
Current timestamp: 2026-07-01T14:32:07Z
```

Fixes applied: volatile values (timestamp, request ID) moved to the very end, after the cache
boundary, so they never invalidate the stable prefix. The large reference material was moved out
of the always-loaded block into an on-demand file, with only a small, genuinely-always-needed
summary kept inline, consistent with Progressive Disclosure. The result: cache hits are
preserved turn-to-turn for the stable prefix, and the per-turn token cost only grows when a task
needs the deeper reference material, not by default.

## Definition of Done

- Static/cacheable content is ordered before volatile content in every prompt structure touched
- No always-loaded file grew without a corresponding attempt to move detail to `references/`
- Independent sub-tasks in this session ran in parallel, not serially, unless a stated dependency required otherwise
- A continuation task reused an existing agent/session rather than re-deriving context from scratch
- Tool definitions in play were checked for overlap before adding a new one
- Exploration and changes stayed bounded to what the task required: no speculative repo
  scans, no unrelated refactoring, no unrequested dependencies or alternative implementations
- Any assumption made was stated once, briefly, rather than escalated into a blocking question
- If two attempts at the same fix failed, work stopped and the blocker was summarized rather than
  continuing to iterate
