---
name: eng-os-coding-standards-common
description: "Use when implementing any code: language-agnostic rules for config loading, error handling, retry, structured logging, testing, security, documentation, user-facing string constants, and Model-View-Controller layering. Always load alongside the language-specific coding-standards skill for this project's stack."
sources:
  - micro/coding-standards/common.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Coding Standards — Common

Language-agnostic rules for all implementation code. Load the matching language skill
(`eng-os-coding-standards-python` or `eng-os-coding-standards-nodejs`) alongside this one: this skill
defines the rule, the language skill defines the concrete implementation.

## Applied Principles

- **Explicitness over implicitness.** No hidden defaults that change behavior.
- **Validation at boundaries.** Validate all external input before use; wrap all external calls with error handling.
- **Observability as a first-class concern.** Logging and error tracking are built in, not bolted on.
- **Determinism within defined boundaries.** Configuration is resolved once at startup; behavior must not vary based on uncontrolled state.

## Standards

### 1. Execution Mode
Every codebase must define `EXECUTION_MODE` with values `dev`, `stage`, `prod`.
- read from environment at startup; default to `dev` if unset
- drives log level and error verbosity (`dev`→DEBUG, `stage`→INFO, `prod`→WARN)
- must never be hardcoded in logic code

### 2. Secrets and Environment Variables
- must come from environment or a secrets manager; never hardcoded or committed
- required secrets must be validated at startup; fail fast if absent
- must never appear in logs, traces, or error messages

### 3. Constants and Configuration
- named values that vary per deployment/integration live in a dedicated config/constants module, never as inline literals
- naming convention: `{AREA}_{PROPERTY}` in UPPER_SNAKE_CASE
- defined once, imported where needed, with explicit defaults where appropriate
- documentation/prose pages that describe a config value (a default, a limit, a threshold) must interpolate the real constant/config export at render or build time; never hand-type a copy of the number/string; a docs page is a consumer of the config module like any other call site
- **constants vs config split**: a `constants` module holds build-time-fixed values that never read
  `process.env`/`os.environ` (app name, taglines, enum literals); a `config` module holds every
  environment-derived or deployment-tunable value. One location per kind; never split a kind
  across more than one file. A project with only one such module may hold both kinds in it.
- **all user-facing strings are constants**: every label, button/link text, heading, placeholder,
  tooltip, and success/error/validation message a user can see is a named export in the constants
  module, sectioned by app area (`{AREA}_LABELS`, `{AREA}_MESSAGES`, etc.), never a literal string
  inline in a component or page. This applies even when the string appears at only one call site:
  it still moves out of the component, per the single-use placement rule above (top of the
  constants file section, not top of the component file, since UI strings are page/component
  content, not business logic). Exception: `eng-os-code-conventions`/`eng-os-prose-style` internal identifiers
  (test names, log messages, code comments) are not user-facing and stay out of this rule.
- **message code prefix**: every success, warning, info, and error message (any `{AREA}_MESSAGES`
  entry) carries a unique alphanumeric code as part of its constant value: 3 uppercase letters
  identifying the functional area, then 6 sequence digits, e.g. `CST000001` for the first
  Customer-area message. This sizing (17,576 possible area codes, 999,999 sequence values) is
  chosen to comfortably outlast an enterprise-scale application over years of growth; a smaller
  2-letter/4-digit scheme (9,999 total codes shared project-wide) is adequate for a small
  short-lived project but was found to be too tight a ceiling for a large, long-lived one: do not
  shrink this format for a "small project" without deliberately re-deciding it, since the code
  format itself, once messages exist against it, is exactly as hard to change as a locked
  Terminology term (see `eng-os-code-conventions` Terminology Lock). The code is assigned once, at
  creation, and never reused or renumbered: even if the message text later changes or the message
  is deprecated, its code is retired, not reassigned to a different message. Format:
  `"{CODE}: {message text}"` or `{ code, text }` as an object, either is acceptable as long as it's
  consistent project-wide within one codebase. Area prefixes are declared once per project (e.g.
  `CST` = Customer, `ORD` = Order, `AUT` = Auth) alongside the Terminology Lock in CLAUDE.md, so
  two areas never collide on the same 3-letter code. The 6-digit sequence is a single counter
  shared across the entire project, not per-area: the area prefix identifies where a message
  lives, the sequence number is the next unused value project-wide (e.g. `CST000001` then
  the next message created anywhere, even in the Order area, is `ORD000002`, not `ORD000001`).
  Never reset or reuse a sequence number, and never let two areas independently restart at
  `000001`.

### 3a. Constants vs. Config vs. Secrets

Three categories, not two: a value can vary per deploy without being sensitive (config), or be
sensitive without varying (secret). Litmus test, sourced from 12factor.net/config, OWASP's Secrets
Management Cheat Sheet, and Google Cloud's Secret-Manager-vs-Parameter-Manager split (`evidence/ledger.md`
E-27):

| | Varies per deploy? | Sensitive? | Where |
|---|---|---|---|
| Constant | No | No | Constants module |
| Config | Yes | No | Config module, env-derived |
| Secret | Yes | Yes | Env var / secret store, never defaulted, never logged |

Twelve-Factor's test for the config/constant line: could the codebase go open source right now
without compromising a credential? Fails → not a constant.

**Multiple processes**: a value only one process needs stays in that process's own `.env`/config;
a value every process needs identically lives in exactly one shared location, never hand-copied
per process (drift risk). Shared *state* between processes belongs in a backing service (database,
queue), not a shared config file. Do not promote a genuinely fixed, non-tunable constant to a
shared/DB-backed location just because it is duplicated across two processes' code; that trades a
copy-paste risk for a new runtime dependency and is a worse design.

**Multiple languages**: no mechanism shares one physical constants file across languages. Either
read the same env var independently in each language's own config module (a value every language
needs identically), or use a shared backing service as the source of truth (only when the value is
runtime-tunable and/or needs cross-language display, e.g. a trading parameter). A fixed constant
with neither property stays a duplicated-but-documented literal in each language, ideally backed by
a drift-guard test.

### 4. Error Handling
- every external call (I/O, API, DB) wrapped in try/catch or equivalent
- catch specific error types; never a silent bare catch-all
- log the error with context before re-raising or returning
- never swallow errors without a deliberate, documented reason

### 5. Retry Logic
- transient external calls must retry with exponential backoff
- default 3 attempts, configurable per integration area as `{AREA}_NUM_RETRIES`
- exponential backoff with full jitter: `delay = random(0, min(cap, base * 2^attempt))`, default `base = 100ms`, `cap = 10s`, total budget 30s; honor `Retry-After` or a caller deadline when present
- retry is owned by one declared layer per call path (`eng-os-reliability-engineering`); never stacked at client, gateway, and service
- never retry non-retryable errors: 4xx responses, auth failures, validation errors
- log every retry attempt with attempt number and delay

### 6. Structured Logging
- logs must be structured (JSON), timestamped, level-controlled
- every record includes `timestamp`, `level`, `message`, and relevant context identifiers
- log level controlled via `EXECUTION_MODE`
- never log secrets, tokens, or PII

Standard log record shape:
```
{
  "timestamp": "2026-05-30T14:22:01Z",
  "level":     "INFO",
  "message":   "processing started",
  "trace_id":  "abc123",
  "service":   "order-pipeline",
  "context":   { ... relevant fields ... }
}
```

File-based log layout for batch and AI pipeline jobs (`logs/` folder, per-run file naming) is a project-structure concern: `../../../micro/project-structure.md` Section 5.

### 7. No Hardcoding
Environment-specific values, secrets, URLs, timeouts, thresholds, and feature switches must never appear as literals in logic code. Use env vars or the constants module instead.

### 8. Default Values
Every config read must specify a default unless the value is strictly required.
- required values: no default; fail at startup if absent
- optional values: always provide a sensible, constant (not computed) default

### 9. Testing Baseline
Every public function needs at minimum:
- one happy-path test
- one primary-failure-condition test

Unit tests must not make real network calls; mock/stub all external dependencies. Integration tests may use real dependencies within a controlled boundary.

### 10. Security Baseline
- validate all external input for type, length, allowed values before use
- never pass raw user input to queries, commands, AI prompts, or file paths
- never log secrets, tokens, passwords, or PII
- never include secrets in error messages or stack traces

### 11. Documentation Baseline
Documentation ships with the change that introduces or modifies the thing it describes.
- document every public function (purpose, parameters, return value, error conditions), every public class/module (responsibility), every non-obvious design choice (why, not what), every service/pipeline entry point (module-level summary)
- do not clutter self-evident code or obvious single-line helpers with comments
- inline comments explain why, never what; a comment describing what the code does is a signal to rename the code instead
- **docstring content is uniform across languages, syntax is per-language** (`docs/decisions/ADR-002-python-docstring-style.md`): document purpose, every parameter, the return value, and every error a function can raise, everywhere. TypeScript uses JSDoc tags (`@param`, `@returns`, `@throws`); Python uses Google-style (`Args:`, `Returns:`, `Raises:`), the syntax each language's own tooling actually parses.

### 12. Component Boundaries, Reuse, and Object-Oriented Design
See `../../../meta/glossary.md` for **Component**, **Reusable Unit**, **Object-Oriented Design**.
- extract to a shared component on the **second** identical or same-responsibility occurrence of a block of logic; never wait for a third, never extract speculatively before a second call site exists
- every component gets one reason to change (Separation of Concerns)
- never instantiate a third-party SDK/client per call site; one component constructs and exports it (generalizes the nodejs skill's "Centralized Third-Party Client Instantiation" rule to all languages)
- reach for Object-Oriented Design (a class/instance) only when the responsibility: owns mutable state across multiple method calls that must stay internally consistent; needs multiple interchangeable implementations behind one interface; or has several operations that only make sense bound to the same piece of state
- a stateless transformation, one-shot I/O call, or pure validator stays a function even in an otherwise class-based codebase; mixing styles per-responsibility is correct, forcing one paradigm project-wide is not
- if a project commits to one dominant paradigm deliberately, record it as a `Code Paradigm` line in the Product Brief/CLAUDE.md (`eng-os-plan-app` skill), same tier as the Terminology Lock

### 13. Model-View-Controller Layering
Every application, regardless of type (web, desktop, CLI, mobile, service with a UI) or stack,
separates code into three layers. This is not a web-specific pattern; a CLI tool or backend
service benefits from the same separation and follows it too.
- **Model**: data shape, persistence, and business/domain rules. No rendering, no I/O framing,
  no knowledge of how it's presented.
- **View**: presentation only; rendering, layout, formatting for the output medium (HTML/UI
  components, CLI output formatting, API response serialization). No business logic, no direct
  data-store access.
- **Controller**: orchestrates a single request/command/action; reads input, calls the Model,
  selects/invokes the View. Thin by design; logic that grows here beyond orchestration belongs in
  the Model.
- A page/route/command handler is a Controller. Business logic reached from it lives in a Model
  module it calls, never inline in the handler itself: this is the concrete form of "business
  logic lives in the appropriate layer," not the page/component file.
- Naming the layers explicitly (`models/`, `views/` or `components/`, `controllers/` or
  `handlers/`/`routes/`) is required; folding all three into one file/function for anything beyond
  a trivial script is the failure mode this standard exists to prevent.

See `references/examples.md` for illustrative code for each standard.

## Failure Modes

- bare catch-all error handlers suppress failures silently and make debugging impossible
- reading env vars at call sites instead of a config module creates configuration drift
- docs pages hardcoding a described config value (e.g. "Default: 6") drift silently from the real constant the same way duplicated code literals do
- missing defaults cause cryptic startup failures in some environments but not others
- logging secrets in debug mode creates security exposure in stage and prod
- inline magic numbers make threshold changes require code search and multiple edits
- hardcoded UI strings (labels, messages, headings) scattered across components make copy changes, localization, and terminology-lock enforcement require a code-wide grep instead of a single-file edit
- messages without a stable unique code make it impossible for support/QA/logs to reference "which message" without pasting the full text, and reassigning a code after the fact breaks any existing reference to it (a support ticket, a log search, a test assertion)
- letting identical logic exist at two or more call sites lets them silently drift apart: a fix applied to one copy and forgotten in the other is a correctness bug, not a style issue
- defaulting to Object-Oriented Design project-wide out of habit, rather than per-responsibility against the Standard 12 triggers, adds instantiation/`this`-binding ceremony with no benefit for stateless logic
- business logic written directly in a page/route/command handler instead of a Model it calls makes the same rule impossible to reuse or test in isolation, and re-derives it with drift the next time it's needed elsewhere

## Definition of Done

- [ ] `EXECUTION_MODE` drives log level and error behavior
- [ ] no secrets or environment-specific values are hardcoded
- [ ] all constants live in a config or constants module, split consistently between build-time constants and environment-derived config if a project has both
- [ ] every value is classified as constant, config, or secret against Standard 3a's litmus test, not placed by convenience or copied pattern
- [ ] in a multi-process application, a value shared by more than one process lives in exactly one place, never hand-duplicated per process; a value only one process needs stays local to it
- [ ] in a multi-language application, a shared value is read from the same env var by each language's own config module, or sourced from a shared backing service only when genuinely runtime-tunable or cross-language-displayed; never a hand-copied literal with no drift guard or documented single-source-of-truth pointer
- [ ] every user-facing string (label, button/link text, heading, placeholder, tooltip, success/error/validation message) is a named constant sectioned by app area, not an inline literal in a component or page
- [ ] every success/warning/info/error message carries a unique `{3-letter area}{6-digit sequence}` code (e.g. `CST000001`), assigned once and never reused or renumbered; area prefixes are declared once per project with no collisions; the 6-digit sequence is one counter shared across the whole project, not restarted per area
- [ ] docs/prose pages describing a config value reference the real constant, not a hardcoded copy
- [ ] all external calls have try/catch with specific error types
- [ ] retry logic with full-jitter exponential backoff, a cap, and a total budget applied to transient calls, owned by one layer per call path
- [ ] logs are structured and free of secrets
- [ ] every public function has at least one happy-path and one failure-path test
- [ ] every public function has a docstring covering purpose, params, return value, and errors
- [ ] inline comments explain why, never what
- [ ] no identical or near-identical same-responsibility logic exists at two or more call sites
- [ ] every third-party SDK/client is constructed in exactly one component, not per call site
- [ ] Object-Oriented Design was chosen per-responsibility against the Standard 12 triggers, not applied or avoided as a blanket project-wide style
- [ ] Model/View/Controller layers are separated and named as such (or the stack's equivalent folders), for every app type, not only web apps
- [ ] every route/page/command handler (Controller) delegates business logic to a Model it calls, rather than implementing that logic inline
