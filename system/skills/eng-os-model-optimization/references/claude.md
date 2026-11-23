# Claude / Anthropic — Model Optimization Tactics

Checked: 2026-11-22 against the provider's documentation. Provider facts change: re-check them at each release (`../../PORTABILITY.md`).

## CLAUDE.md as the Cacheable System-Prompt Layer

CLAUDE.md (and any skill content loaded at session start) sits at the front of the prompt and is
the same for every turn in a session: it is exactly the kind of static content that should be
placed first for prompt-cache reuse. Do not interpolate turn-specific or timestamp-like values
into CLAUDE.md or into always-loaded skill bodies; doing so busts the cache prefix for every
subsequent turn even though the "meaningful" content didn't change.

## Prompt-Cache TTL

Anthropic's prompt cache defaults to a 5-minute lifetime, refreshed at no cost each time the cached content is used, and a 1-hour TTL is available (`"ttl": "1h"` in `cache_control`) at a higher cache-write cost: a 5-minute write costs 1.25 times the base input price, a 1-hour write 2 times. Check which TTL the session or API call actually uses before applying the points below; a 1-hour TTL moves the idle-gap threshold from minutes to an hour. Implications:

- A session that goes idle past the TTL pays a full cache-miss cost on the next turn: a full
  reload of the entire cached prefix. There is no benefit to "saving up" requests if the gap
  between them exceeds the TTL.
- For workflows with bursty, spaced-out interaction (e.g., waiting on a long-running build
  between prompts), consider whether it's cheaper to keep the session warm with a lightweight
  no-op turn, or accept the periodic miss. Don't restructure the whole prompt to chase a
  TTL that will be missed anyway when the user is naturally slow.
- Cache-friendly session design front-loads stable content (CLAUDE.md, skill bodies, tool
  definitions) once and keeps appending rather than re-sending or reordering that prefix on
  later turns.

## Effort Levels

Claude models expose five effort levels (`low`, `medium`, `high`, `xhigh`, `max`; `xhigh` and `max`
are available on some models only), set with `output_config.effort`. The default differs by model
(`high` on most, `medium` on some), so set it explicitly rather than relying on it. Changing the
top-level effort between requests can invalidate the prompt cache; where a model supports
per-message effort, change it that way instead. Match the level to the task, not to a blanket
default:

- **Low/medium**: mechanical, well-specified, high-volume work: formatting, simple refactors,
  boilerplate generation, straightforward lookups. Spend effort here only if correctness is
  in question.
- **High**: non-trivial implementation work, debugging, multi-file changes where correctness
  depends on holding several constraints in mind at once.
- **xhigh/max**: judgment-heavy, ambiguous, or high-stakes work: architecture decisions,
  security review, adversarial verification, anything where a wrong answer is expensive to
  discover later. Reserve for tasks that need it: spending max effort on a mechanical
  task wastes latency and cost without improving the answer.

## Subagent Isolation Choices

- **Continue/fork an existing agent** when the task shares context with prior work: a fork
  inherits the full conversation and shares the parent's prompt cache, so it is materially
  cheaper than a fresh agent for anything that needs the same background.
- **Spawn a fresh agent** when the task is genuinely independent, when you want a second,
  unbiased opinion (e.g., adversarial review), or when the prior context is irrelevant noise that
  would only dilute the fresh agent's focus.
- Prefer forking over "explain everything again in a new prompt": re-explaining costs tokens
  and risks losing detail the original context already had exactly right.

## Model Tiering

Use a cheaper/faster model for mechanical or high-volume work (bulk file edits, simple
extraction, repetitive classification) and reserve the strongest model for judgment-heavy work
(architecture calls, ambiguous debugging, adversarial review, anything where the cost of being
wrong exceeds the cost difference between models). Tiering by task type, not by blanket
project-wide model choice, is usually where the largest cost savings live without sacrificing
quality where it matters.
