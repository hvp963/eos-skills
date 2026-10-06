# OpenAI — Model Optimization Tactics

## Reasoning-Effort Parameter Equivalents

OpenAI's reasoning models expose a `reasoning_effort` (or equivalent) parameter analogous to
Claude's effort levels. The same allocation principle applies: default to low/medium for
mechanical or well-specified tasks, and reserve high effort for ambiguous, multi-constraint, or
high-stakes work. Because reasoning tokens are billed and add latency even when not shown in the
visible output, mismatched effort on a simple task is a pure cost/latency tax with no quality
upside.

## System/Developer Message Caching Behavior

OpenAI's automatic prompt caching keys off a stable prefix, same principle as other providers:
place system/developer instructions and static tool definitions first, and keep them byte-stable
across requests to maximize cache hits. Avoid regenerating the system/developer message per
request with small formatting differences (varying whitespace, reordered keys in an embedded
JSON block, timestamps) since that silently defeats caching. Where the platform exposes explicit
cache controls, use them; where caching is automatic, the discipline is the same: stable content
first, volatile content last.

## Function-Calling Schema Constraints

Keep function/tool schemas minimal and non-overlapping: the same tool-definition-minimalism
principle applies, but OpenAI's function calling is additionally sensitive to:

- Strict JSON Schema constraints (`strict: true` mode) reduce malformed tool calls but require
  every field to be fully specified (no implicit optionality); decide up front whether strict
  mode's rigidity or looser schema's flexibility better fits the tool.
- Deeply nested or highly overloaded parameter objects increase the chance the model picks wrong
  fields or omits required ones. Flatten where possible.
- Large numbers of available tools compete for the model's attention in the same way oversized
  context does; prune unused tools from the active set rather than leaving them always
  available "just in case."

## Structured-Output Modes

Prefer native structured-output modes (JSON schema-constrained generation) over prompting the
model to "return JSON" and hoping. This removes a validation round trip and reduces retries due
to malformed output, which is itself a cost and latency saving. Structured outputs also make the
determinism boundary of a task explicit and machine-checkable, which aligns with the Engineering
OS validation-at-boundaries principle.
