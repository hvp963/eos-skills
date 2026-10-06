# Code Conventions

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Standards for naming and commenting code so it remains readable, consistent, and self-describing across languages and contributors.

### What This Is Not
- not a style guide for documents (see meta/document-authoring-guidelines.md)
- not a sentence-level prose style guide (see meso/prose-style.md)
- not a language-specific linting ruleset (see micro/coding-standards/python.md, nodejs.md)
- not a substitute for readable code structure

## Scope
- Level: Meso
- Applies To: All production code, scripts, and specification artifacts that contain code blocks
- See Also: `micro/coding-standards/common.md` for operational standards; `micro/coding-standards/python.md` and `nodejs.md` for language-specific implementations

---

## Applied Principles

### Explicitness Over Implicitness
Names must communicate intent without requiring a comment or external lookup.

### Separation of Concerns
Naming conventions separate structural metadata (constants, classes) from runtime values (variables, functions) through consistent casing.

### Contracts as Source of Truth
Environment variable names are part of the deployment contract. They must follow the same naming discipline as code.

---

## Naming Conventions

Rules are language-agnostic. Where casing differs by idiomatic language convention, both are stated explicitly.

---

### Variables and Functions

Rule: the language's idiomatic casing, declared once per project

- Python:     `snake_case`: `input_filename`, `load_checkpoint`, `generate_phrase`
- TypeScript: `camelCase` for variables, functions, and properties: `inputFilename`, `loadCheckpoint`, `generatePhrase`. Decided in `docs/decisions/ADR-001-typescript-casing.md` (Accepted 2026-09-01): TypeScript follows its ecosystem's idiom, and cross-language consistency is kept where it is contractual. JSON field names, database columns, environment variables, and message codes stay `snake_case` in both languages, and TypeScript maps between wire and code exactly once, at the validated boundary (`zod` transform or serializer). A project may declare `snake_case` for TypeScript in its CLAUDE.md; it then applies everywhere in that project.

Do not mix snake_case and camelCase within a single file.

#### Example
```python
# Python
input_filename = os.getenv("INPUT_FILENAME", "")
def load_checkpoint(path: str) -> dict: ...
def generate_phrase(sentence: str) -> str: ...
```
```typescript
// TypeScript (camelCase in code; snake_case at the wire)
const inputFilename = process.env.INPUT_FILENAME ?? "";
function loadCheckpoint(path: string): Record<string, unknown> { ... }
// wire boundary: { customer_id } in JSON becomes { customerId } once, in the zod transform
```

#### Failure Mode
Mixed casing within a file signals undeclared conventions and creates ambiguity for contributors and AI agents.

---

### Constants

Rule: UPPER_SNAKE_CASE in all languages

- Python:     `RETRY_MAX_ATTEMPTS`, `AI_MODEL`, `DEFAULT_TIMEOUT_SECS`
- TypeScript: `RETRY_MAX_ATTEMPTS`, `AI_MODEL`, `DEFAULT_TIMEOUT_SECS`

#### Example
```python
RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", "5"))
DEFAULT_TIMEOUT_SECS = 30.0
AI_MODEL = "model-family-version"
```
```typescript
const RETRY_MAX_ATTEMPTS: number = parseInt(process.env.RETRY_MAX_ATTEMPTS ?? "5");
const DEFAULT_TIMEOUT_SECS = 30.0;
```

#### Failure Mode
Constants that look like variables are silently mutated or overridden.

---

### Classes

Rule: PascalCase in all languages

- Python:     `MediaAgent`, `CheckpointManager`
- TypeScript: `MediaAgent`, `CheckpointManager`

#### Failure Mode
Classes named in snake_case are indistinguishable from modules or functions by inspection.

---

### Files and Modules

Rule: snake_case for Python; kebab-case for TypeScript/Node

- Python:     `media_agent.py`, `checkpoint_manager.py`
- TypeScript: `media-agent.ts`, `checkpoint-manager.ts`

Declare one convention per project and apply it consistently.

#### Failure Mode
Mixed file naming conventions break import resolution in case-sensitive environments.

---

### Environment Variables

Rule: UPPER_SNAKE_CASE, prefixed by domain where ambiguity is possible.
Applies equally in all languages because environment variables are OS-level.

- `AI_MODEL`, `AI_TEMPERATURE`, `AI_TIMEOUT_SECS`
- `IMAGE_API_KEY`, `IMAGE_API_SECRET`
- `SEARCH_API_KEY`
- `RETRY_MAX_ATTEMPTS`, `RETRY_BASE_DELAY_SECS`

Prefix by domain (AI_, IMAGE_, SEARCH_) when multiple external integrations share similar key names.

See `micro/coding-standards/common.md` Standard 2 for secrets and env var validation requirements.

#### Failure Mode
Generic names like `API_KEY` or `SECRET` collide across integrations and cause silent misconfiguration.

---

### Booleans

Rule: Prefix with `is_`, `has_`, `can_`, or `allow_` in all languages.

- `is_valid`, `is_active`, `is_complete`
- `has_checkpoint`, `has_completed`
- `can_publish`, `can_retry`
- `allow_retry`, `allow_override`

#### Example
```python
is_valid = validate_input(record)
has_checkpoint = checkpoint_path.exists()
allow_retry = attempt < RETRY_MAX_ATTEMPTS
```

#### Failure Mode
Booleans named without a prefix (e.g. `active`, `valid`) are ambiguous: they could be a state, a count, or an object reference.

---

### Naming Rule

Names must be self-describing.
A name that requires a comment to explain what it is has failed the naming requirement.
Avoid generic names like `data`, `value`, `result`, `temp`, `obj` without a qualifying prefix.

---

## Inline Comment Conventions

---

### When to Comment

Write a comment only when the WHY is not obvious from the code itself.

Acceptable reasons:
- a non-obvious constraint or invariant
- a deliberate workaround for a specific external limitation
- a default or threshold value whose origin is not self-evident

Do not write comments that restate what the code already says.

#### Example
```python
# Bad — restates the obvious
i += 1  # increment i

# Good — explains why
retry_delay *= 2  # exponential backoff — doubles on each attempt
```

#### Failure Mode
Self-evident comments add noise, train readers to skip comments, and cause the genuinely important ones to be missed.

---

### Placement

Place explanatory comments on the line above the code they describe.
Use inline end-of-line comments only for brief value annotations.

```python
# Acceptable inline — brief unit annotation
retry_max_delay = float(os.getenv("RETRY_MAX_DELAY_SECS", "60.0"))  # seconds

# Prefer above-line for anything longer than a short label
# Skip rows already processed in a prior run to support safe resume.
if idx in checkpoint:
    continue
```

---

### Style

- Use a single `#` with one space before the comment text
- Use sentence fragments for inline value annotations
- Use full sentences for above-line explanatory comments

---

### Do Not Use

- Multi-line block comments for logic that should be self-describing code
- Comments that name the caller or feature ("added for X flow", "used by Y agent"): these belong in commit messages, not code
- TODO/FIXME comments in production specifications: these indicate incomplete design, not acceptable uncertainty

---

## Terminology Lock

### Applied Principle

Core domain nouns and verbs are naming decisions, not writing decisions. The same discipline that governs variable and file names in this document applies one level up, to the words that name the domain itself: entity names, key action names, page and section titles. These words appear in code identifiers, database columns, API fields, UI copy, and documentation simultaneously. A change to one of them is never local.

Treat the canonical term for every core entity, action, and major UI surface as a decision requiring explicit sign-off before implementation begins, not a first-draft guess that gets refined as the build progresses. Opportunistic mid-build renaming is the failure mode this pattern exists to prevent, not renaming itself.

### Evidence

A real project renamed the same core concept three times mid-build. Each rename touched the whole codebase: code identifiers, UI copy, docs, and tests all referenced the old name, so each pass required a full sweep rather than a single edit. The cost was not the rename; it was that none of the three renames were planned, so each one arrived as unplanned rework layered on top of the last.

### The Relaxation

A rename is not forbidden. A rename is acceptable when it is executed as one deliberate, complete pass:
- the new term is introduced and the old term is explicitly marked deprecated in the same change
- a transition window is declared with an end date
- during the transition, both terms may coexist only inside a deprecation shim, never in fresh code, fresh UI copy, or fresh docs
- after the declared date, the old term is removed everywhere, including comments

The distinction that matters: a single declared pass with a start and an end is a controlled change. Renaming a little bit at a time, whenever it's convenient, with no declared end state, is drift, and drift is what produces the three-rename scenario above.

#### Example — Term-Lock Table

| Decided term | Rejected alternatives | Locked at |
|---|---|---|
| `cancellation_request` | `termination`, `unsubscribe_event`, `churn_record` | Design review, before implementation |
| `effective_date` | `end_date`, `cancel_date` | same |
| "Cancel Subscription" (UI label) | "End Plan", "Stop Billing" | same |

Once locked, `cancellation_request` is the only term used in code identifiers, DB columns, API fields, UI copy, and docs. The rejected alternatives do not appear anywhere in the implementation, not even as aliases or comments.

#### Example — Deprecation Timeline

```
Day 0    ADR approved: rename cancellation_request -> subscription_cancellation.
         Reason: collided with an unrelated "account termination" flow. New name
         declared final.

Day 0    New term introduced alongside old in the same change:
         - subscription_cancellation is the canonical name going forward
         - cancellation_request kept only as a deprecated alias, annotated with
           the removal date
         - all new code, UI text, and docs use subscription_cancellation only

Day 0-45 Transition window: existing call sites migrated incrementally, but each
         migration touches code + UI + docs + tests together — never a partial
         rename left mid-file. Both terms exist only inside the alias shim.

Day 45   cancellation_request removed entirely. A search for the old term returns
         nothing outside the ADR and changelog history.
```

#### Failure Mode

Renaming a core term without a declared transition leaves two names for the same concept live at once, with no way for a reader (human or agent) to tell which is current. Each subsequent contributor guesses, and guesses inconsistently, which is how a concept gets renamed a second and third time.

---

## Failure Modes

- mixed casing within a file signals undeclared or inconsistent conventions
- generic names require comments to be understood, defeating the naming requirement
- boolean names without prefixes create ambiguity at call sites
- environment variable name collisions cause silent misconfiguration
- self-evident comments train readers to skip all comments, including the important ones
- unlocked core terminology drifts mid-project, leaving old and new terms coexisting with no clear signal of which is current

---

## Definition of Done

Code conventions are applied correctly when:
- all names are self-describing without a supporting comment
- casing follows the declared convention for the language and construct type
- environment variables are domain-prefixed where integration overlap exists
- boolean names carry an explicit `is_`, `has_`, `can_`, or `allow_` prefix
- comments explain only the non-obvious WHY, not the visible WHAT
- no TODO/FIXME comments exist in production code or specifications
- core domain terminology (entity names, key actions, page/section titles) was decided and locked before implementation began
- any rename of a locked term was executed as a single deliberate pass with a declared deprecation and removal date; no term exists in two unresolved forms indefinitely
