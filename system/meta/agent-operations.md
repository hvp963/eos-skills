# Agent Operations

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
How an AI coding agent working under this OS should manage its own cost, latency, context, and
scope. It governs the agent's behavior as a worker, not the standard the code must meet.

### What This Is Not
- not an engineering standard for the product being built
- not a prompting tutorial or a provider manual
- not a substitute for `meta/claude-code-usage.md`, which defines bootstrap and checkpoints

## Scope
- Level: Meta
- Applies To: every session in which an AI agent applies this OS
- See Also: `meta/claude-code-usage.md`, `skills/eng-os-model-optimization/SKILL.md`

---

## 1. Context Budget

The always-loaded portion of any instruction set is a recurring cost on every turn. Keep it
small: a router and the rules that apply to every turn. Everything else loads on demand at the
moment it is needed and is dropped afterward. Re-audit the always-loaded set on every release;
content that was essential at the start of a project becomes dead weight once its pattern is
established.

- Failure mode: instructions that grow by accretion until every turn pays for guidance that
  applies to one turn in fifty.

## 2. Prompt Structure and Caching

Order every prompt static-first: system and persona, stable project context, stable tool
definitions, then the cache boundary, then conversation history, then this turn's volatile input.
Any volatile value placed before the boundary invalidates the cache for everything after it.

## 3. Tool Definitions

Fewer, well-scoped tools beat many overlapping ones. Before adding a tool, extend an existing
one's parameters. Overlap costs tokens on every turn and increases the chance of the wrong tool
being chosen.

## 4. Parallelism and Continuity

Run independent sub-tasks in parallel; serialize only where a real dependency exists and say
what it is. Continue an existing session for a follow-up task that depends on its history;
start fresh only for genuinely independent work or when isolation from prior context is the
point.

## 5. Scope Containment

- read only the files the task touches; no speculative repository sweeps
- make the smallest correct change; unrelated refactors are a separate task
- add no dependency, abstraction, or alternative that was not asked for
- state an assumption once and proceed; ask only when the ambiguity blocks progress
- after two failed attempts at the same approach, stop and report the blocker
- stop when the task's Definition of Done is met
- when a new request is unrelated to the session's history, recommend a fresh session

- Failure mode: unbounded exploration and unbounded polish spend tokens and review time with
  no corresponding gain, and bundle unrequested risk into the change.

## 6. Provider Specifics

Provider-specific tactics (Claude, OpenAI, self-hosted models) live in
`skills/eng-os-model-optimization/references/` and change faster than this document; this document
holds only what is true regardless of provider.

---

## Failure Modes

- always-loaded instructions that grow without a corresponding move of detail to on-demand references
- volatile values placed before the cache boundary
- overlapping tools that cost tokens and cause wrong-tool selection
- serial execution of independent work by default
- exploration and change scope that exceed the request

## Definition of Done

An agent is operating to this standard when:
- the always-loaded instruction set was reviewed this release and detail moved to references
- prompts are ordered static-first with volatile input last
- tools were checked for overlap before any was added
- independent sub-tasks ran in parallel and continuation tasks reused their session
- exploration, changes, and retries stayed within the bounds in Section 5
