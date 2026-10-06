# Coding Standards — Common

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Language-agnostic coding rules that apply to all implementation code in this system.

### What This Is Not
- not a style guide or formatting preference
- not a language-specific implementation guide
- not optional: these are non-negotiable operational standards

## Scope
- Level: Micro
- Applies To: All implementation code regardless of language or runtime
- See Also: `python.md`, `nodejs.md` for language-specific implementations
- See Also: `micro/project-structure.md` for folder layout and module organization

---

## Applied Principles

### Explicitness Over Implicitness
All configuration, behavior, and error conditions must be explicit. No hidden defaults that change behavior.

### Validation at Boundaries
All external inputs must be validated before use. All external calls must be wrapped with error handling.

### Observability as a First-Class Concern
Logging and error tracking must be built in, not added after the fact.

### Determinism Within Defined Boundaries
Configuration must be resolved once at startup. Behavior must not vary based on uncontrolled state.

---

## Standards

### 1. Execution Mode

Every codebase must define `EXECUTION_MODE` with three valid values: `dev`, `stage`, `prod`.

- must read from environment at startup
- must drive log level, error verbosity, and feature behavior
- must default to `dev` if not set
- must not be hardcoded anywhere in logic code

```
EXECUTION_MODE = getenv("EXECUTION_MODE", default="dev")

if EXECUTION_MODE == "dev":    LOG_LEVEL = DEBUG
if EXECUTION_MODE == "stage":  LOG_LEVEL = INFO
if EXECUTION_MODE == "prod":   LOG_LEVEL = WARN
```

---

### 2. Secrets and Environment Variables

Secrets and environment-specific values must come from the environment or a secrets manager.

- must not be hardcoded in source code
- must not be committed to version control
- must be validated at startup; fail fast if a required secret is absent
- must not appear in logs, traces, or error messages

```
API_KEY = getenv("SERVICE_API_KEY")  // required — raise error if absent
TIMEOUT = getenv("SERVICE_TIMEOUT_MS", default="5000")  // optional with default
```

---

### 3. Constants and Configuration

Named values that vary per deployment or integration area must live in a dedicated config or constants module.

- must not appear as inline literals in logic code
- must be defined once and imported where needed
- must have explicit defaults where appropriate
- naming convention: `{AREA}_{PROPERTY}` in UPPER_SNAKE_CASE

```
// constants module
MAX_RETRIES      = 3
RETRY_BASE_MS    = 100
RETRY_CAP_MS     = 10000
RETRY_BUDGET_MS  = 30000
TIMEOUT_MS       = 5000
BATCH_SIZE       = 100
```

**Which module: constants vs config.** A project may have both a `constants` module and a
`config` module; the split is not cosmetic and must be applied consistently:

- **constants module** (e.g. `constants.ts`): values fixed at build time, identical in every
  environment and every deployment: app name, taglines, enum-like string literals, format strings.
  Never reads `process.env` / `os.environ`.
- **config module** (e.g. `config.ts`): every value that is environment-derived, deployment-tunable,
  or read from `.env`: retry counts, timeouts, model identifiers, feature thresholds, ports. This is
  the only place `process.env` / `os.environ` may be read for these values (see Standard 2 for
  secrets specifically).

If a project has only one such module, both kinds of values may live there; the rule is "one
location per kind, never split across more than one file per kind," not "exactly two files always."

**All user-facing strings are constants.** Every label, button/link text, heading, placeholder,
tooltip, and success/warning/info/error message a user can see is a named export in the constants
module, sectioned by app area (`{AREA}_LABELS`, `{AREA}_MESSAGES`, etc.), never a literal string
inline in a component or page. This holds even when the string appears at only one call site: it
still moves out of the component, per the single-use placement rule above (top of the constants
file's section, not the top of the component file, since UI strings are page/component content,
not business logic). Exception: internal identifiers that are not user-facing; test names, log
messages, code comments (governed by `meso/code-conventions.md`); stay out of this rule.

**Message code prefix.** Every success, warning, info, and error message (any `{AREA}_MESSAGES`
entry) carries a unique alphanumeric code as part of its constant value: 3 uppercase letters
identifying the functional area, then 6 sequence digits, e.g. `CST000001` for a Customer-area
message. This sizing (17,576 possible area codes, 999,999 sequence values) is deliberately chosen
to outlast an enterprise-scale application across years of growth; a tighter 2-letter/4-digit
scheme (9,999 total codes shared project-wide) proved too small a ceiling in practice for a large,
long-lived codebase. Once messages exist against a code format, changing the format is exactly as
disruptive as a locked Terminology Lock term (see `meso/code-conventions.md`): decide the sizing
deliberately at project start rather than shrinking it later for a "small project" and hitting the
ceiling as the project grows. The code is assigned once, at creation, and never reused or
renumbered: even if the message text later changes or the message is deprecated, its code is
retired, not reassigned to a different message. Format: `"{CODE}: {message text}"` or
`{ code, text }` as an object; either is acceptable as long as it is consistent project-wide within
one codebase. Area prefixes are declared once per project (e.g. `CST` = Customer, `ORD` = Order,
`AUT` = Auth) alongside the Terminology Lock in CLAUDE.md, so two areas never collide on the same
3-letter code. The 6-digit sequence is a single counter shared across the entire project, not
per-area: the area prefix identifies where a message lives, the sequence number is the next
unused value project-wide (e.g. after `CST000001`, the next message created anywhere, even in the
Order area, is `ORD000002`, not `ORD000001`). Never reset or reuse a sequence number, and never let
two areas independently restart at `000001`.

```
// constants/rotations.ts
export const ROTATIONS_LABELS = {
    PAGE_TITLE:      "Rotations",
    CREATE_BUTTON:   "New Rotation",
}
export const ROTATIONS_MESSAGES = {
    SAVE_SUCCESS:    { code: "ROT000001", text: "Rotation saved." },
    SAVE_ERROR:      { code: "ROT000002", text: "Could not save rotation. Try again." },
}
// constants/engineers.ts — created between ROT000002 and the next rotations message,
// so it takes the next project-wide number, not a fresh ENG000001
export const ENGINEERS_MESSAGES = {
    CONTACT_INVALID: { code: "ENG000003", text: "Enter a valid phone number or email." },
}

// forbidden — literal strings inline in a component, and a message with no code
function RotationPage() {
    return <h1>Rotations</h1>  // should read ROTATIONS_LABELS.PAGE_TITLE
}
```

---

### 3a. Constants vs. Config vs. Secrets: the Three-Way Split

Standard 2 and Standard 3 together define two categories (secrets, and constants-vs-config). In
practice a codebase needs all three named explicitly, since "config" and "secret" are not the same
axis: a value can vary per deployment without being sensitive (`LOG_LEVEL`), or be sensitive without
varying (an API key that is the same across every deploy of a shared account is still a secret).
This standard makes the third category explicit and gives the litmus test for choosing between all
three, sourced from the authorities every major platform already builds on: the Twelve-Factor App
methodology's Config factor (12factor.net/config), OWASP's Secrets Management Cheat Sheet
(cheatsheetseries.owasp.org), and Google Cloud's own Secret-Manager-vs-Parameter-Manager split
(cloud.google.com/secret-manager/docs/best-practices). See `evidence/ledger.md` E-27 for the full
citation trail behind this standard.

| | Varies per deploy? | Sensitive? | Where it lives | Litmus test |
|---|---|---|---|---|
| **Constant** | No | No | Constants module (Standard 3) | Would this value differ if the same commit were deployed to a different account/environment? No → constant. |
| **Config** | Yes | No | Config module, env-derived (Standard 2/3) | Does it change per deploy, but leaking it would compromise nothing? |
| **Secret** | Yes | Yes | Env var or a dedicated secret store, never defaulted, never logged, never committed | Would this leaking compromise something? Yes → secret. |

Twelve-Factor's own litmus test for the config/constant boundary specifically: **"could the
codebase be made open source at any moment, without compromising any credentials?"** A value that
fails this test is never a constant, however convenient inlining it would be.

```
// constants.ts — fixed, identical for every deployment, never reads process.env/os.environ
export const RETRY_BASE_MS = 100
export const RETENTION_DAYS = 30

// config.ts — env-derived, varies per deploy, not sensitive, safe to default/document
export const logLevel = process.env.LOG_LEVEL ?? 'info'

// secrets — env-derived, varies per deploy, sensitive: never defaulted, never logged
export const apiKey = requireEnv('SERVICE_API_KEY')  // throws at startup if missing
```

#### Multiple Processes in One Application

An application with more than one long-lived process (a web server plus a worker, a Node service
plus a Python job) does not get one shared in-process config object; Twelve-Factor's Config factor
is explicit that env vars are "granular controls, each fully orthogonal to other env vars... never
grouped together as 'environments'... independently managed for each deploy." Apply this per value,
not per process wholesale:

- A value only one process needs (a broker credential only the order-execution process talks to)
  lives in that process's own `.env`/config module. Do not push it up to a shared location "for
  consistency" when only one process reads it.
- A value every process needs identically (an `EXECUTION_MODE` that must mean the same thing
  everywhere) lives in exactly one place both processes read, never copied by hand into each
  process's own file. A value duplicated across files with no shared source of truth is exactly the
  drift risk Twelve-Factor's config/code separation and the general "single source of truth"
  configuration-management principle both exist to prevent (E-27). In a single-repo multi-process
  project, this is a project-root `.env`/config file each process's own loader reads in addition to
  its own; in a multi-repo/deployed-separately setup, it is whatever the deployment platform's
  shared secret/config store provides (see Standard 2's "secrets manager" language). The point is
  one place to change it, not one specific mechanism.
- Shared *state* (not config) between processes belongs in a backing service (a database, a queue),
  never in a shared config file. Twelve-Factor's Backing Services factor treats "any service the
  app consumes over the network" as an attached resource, which is the correct mechanism for
  cross-process facts that change at runtime, not build/deploy time.
- Do not promote a value to the shared location just because it happens to be duplicated across two
  processes' code. A rotation policy, a timeout, or any other genuinely fixed constant that is
  merely copy-pasted into two languages' constants modules is a maintenance risk (a drift-guard
  test, or a documented single source-of-truth comment in each copy, addresses that), not evidence
  it needed to become configurable or database-backed. Moving a non-tunable, non-displayed value
  into a database to "avoid duplication" trades a copy-paste risk for a new runtime dependency
  (what happens when that lookup fails before the first log line is even written) and is a worse
  design, not a fix.

#### Multiple Languages in One Application

No mechanism lets a `.py` module natively import a `.ts` module's constants or vice versa; there is
no authoritative source recommending a single physical file shared across languages for this. Two
mechanisms are legitimate, both already implied by Standards 2/3 applied per-language:

- **Same env var, read independently by each language's own config module.** This is the actual
  Twelve-Factor mechanism for a value every process/language needs identically: one shared `.env`
  key, validated and typed by each language's own config loader, never a copied literal.
- **A shared backing service (typically the database) as the single source of truth** for any value
  that must never drift AND is runtime-tunable and/or needs to be read or displayed by more than
  one language's runtime (a trading parameter both a Python engine and a web UI read and display).
  This does not apply to a value with no tunability or display need. See the constants guidance
  above.

Never hand-duplicate the same fixed constant's literal value across two languages' constants
modules without at least a comment in each file pointing at the other as the reason the values must
stay identical; a drift-guard test (asserting both languages' values match) is stronger than a
comment alone and is preferred when the project already has cross-language test infrastructure.

---

### 4. Error Handling

Every external call must be wrapped in error handling. Errors must be caught at the boundary where context is available.

- must use try/catch (or equivalent) around all I/O, API calls, and database operations
- must catch specific error types; never use a bare catch-all silently
- must log the error with context before re-raising or returning
- must not swallow errors without a deliberate, documented reason

```
try:
    result = external_service.call(payload)
    return result
catch ServiceError as e:
    log.error("service call failed", error=e, payload_id=payload.id)
    raise
catch NetworkError as e:
    log.warn("transient network error", error=e, attempt=attempt)
    // apply retry logic
```

---

### 5. Retry Logic

All transient external calls must implement retry with exponential backoff.

- must default to 3 attempts
- must be configurable per integration area: `{AREA}_NUM_RETRIES`
- must use exponential backoff with full jitter: `delay = random(0, min(cap, base * 2^attempt))`; default `base = 100ms`, `cap = 10s`
- must have a total retry budget (default 30s) after which the call fails regardless of attempts remaining
- must honor a `Retry-After` header or an explicit deadline from the caller when either is present
- must not retry non-retryable errors: 4xx responses, authentication failures, validation errors
- must log each retry attempt with attempt number and delay

Why jitter: a fixed schedule makes every client that failed at the same instant retry at the same instant, so a brief dependency blip becomes a synchronized retry storm that keeps the dependency down. Full jitter spreads the retries; the cap bounds the wait; the budget bounds the total time a caller can spend retrying.

```
RETRIES  = getenv("{AREA}_NUM_RETRIES", default=3)
BASE_MS  = 100
CAP_MS   = 10_000
BUDGET   = 30_000  // total milliseconds across all attempts
// delay for attempt n: random(0, min(CAP_MS, BASE_MS * 2^n))  (full jitter)

function callWithRetry(operation):
    for attempt in range(RETRIES):
        try:
            return operation()
        catch TransientError as e:
            if attempt == RETRIES - 1: raise
            delay = BACKOFF[min(attempt, len(BACKOFF) - 1)]
            log.warn("retry", attempt=attempt+1, delay_ms=delay, error=e)
            sleep(delay)
```

---

### 6. Structured Logging

All logs must be machine-parseable, timestamped, and level-controlled.

- must emit structured (JSON) logs
- must include: `timestamp`, `level`, `message`, and relevant context identifiers
- must control log level via `EXECUTION_MODE` (see Standard 1)
- must not log secrets, tokens, or personally identifiable information

#### Log Files
File-based log layout for batch and AI pipeline jobs (the `logs/` folder and its per-run file naming) is a project-structure concern; see `micro/project-structure.md` Section 5. Log level for those files still follows Standard 1.

#### Standard Log Record Shape
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

---

### 7. No Hardcoding

Environment-specific values, secrets, URLs, timeouts, thresholds, and feature switches must not appear as literals in logic code.

| Hardcoded (forbidden) | Correct |
|---|---|
| `url = "https://api.prod.example.com"` | `url = getenv("SERVICE_URL")` |
| `timeout = 30` | `timeout = TIMEOUT_MS` (from constants) |
| `retries = 3` | `retries = getenv("API_NUM_RETRIES", 3)` |
| `key = "sk-abc123"` | `key = getenv("OPENAI_API_KEY")` |

---

### 8. Default Values

Every `getenv()` call must specify a default unless the value is strictly required.

- required values: fail at startup if absent; do not provide a default
- optional values: always provide a sensible default
- defaults must be constants, not expressions or computed values

```
// required — no default; startup fails if absent
DB_URL = getenv("DATABASE_URL")

// optional — explicit default
POOL_SIZE    = int(getenv("DB_POOL_SIZE", "10"))
TIMEOUT_SECS = float(getenv("API_TIMEOUT_SECS", "30.0"))
```

---

### 9. Testing Baseline

Every public function must have tests covering at minimum:

- one test for the expected (happy-path) behavior
- one test for the primary failure condition

Additional requirements:
- must not make real network calls in unit tests
- must mock or stub all external dependencies in unit tests
- integration tests may use real dependencies within a controlled boundary

```
// function under test
function getOrderTotal(order_id, db):
    order = db.findById(order_id)
    if order is null: raise NotFoundError("order not found")
    return sum(item.price * item.quantity for item in order.items)

// happy-path test
test "getOrderTotal returns correct sum for valid order":
    mockDb = stub(findById: returns { id: "123", items: [{ price: 10, quantity: 2 }, { price: 5, quantity: 1 }] })

    result = getOrderTotal("123", db=mockDb)

    assert result == 25
    mockDb.findById.assert_called_once_with("123")

// failure-path test
test "getOrderTotal raises NotFoundError when order does not exist":
    mockDb = stub(findById: returns null)

    assert_raises NotFoundError:
        getOrderTotal("missing-id", db=mockDb)
```

---

### 10. Documentation Baseline

Every public function, module, class, and service boundary must be documented. Documentation is a code artifact: it ships with the change that introduces or modifies the thing it describes.

**What must be documented:**
- every public function: purpose, parameters, return value, and error conditions
- every public class or module: what it does and what it is responsible for
- every non-obvious design choice: explain why, not what
- every service or pipeline entry point: a module-level summary for the next engineer

**What must not be cluttered with comments:**
- code that already reads clearly from its names and structure
- internal helper functions with obvious single-line behavior

**Inline comments: use sparingly:**
- comment the why, never the what
- a comment that describes what the code does is a signal to rename the code instead

```
// forbidden — describes what, not why
// loop through all items and add to total
total = sum(item.price for item in items)

// correct — explains a non-obvious constraint
// prices are stored in cents to avoid floating-point drift; divide only at display time
total_cents = sum(item.price_cents for item in items)
```

**Docstring style: uniform content, per-language syntax.**
The documentation requirement is the same regardless of language: purpose, every parameter, the return value, and every error a function can raise. The tag syntax is per-language, per `docs/decisions/ADR-002-python-docstring-style.md`: TypeScript uses JSDoc (`@param`, `@returns`, `@throws`); Python uses Google-style docstrings (`Args:`, `Returns:`, `Raises:`), parsed natively by its own tooling. Language-specific implementations are in `python.md` and `nodejs.md`.

TypeScript (JSDoc):
```
/**
 * Returns the total value of an order in cents.
 *
 * @param orderId - The order to retrieve.
 * @param db - Injected database client.
 * @returns Order total in smallest currency unit (cents).
 * @throws {NotFoundError} If no order exists for the given order_id.
 */
```

Python (Google-style):
```python
def get_order_total(order_id: str, db: DatabaseClient) -> int:
    """Returns the total value of an order in cents.

    Args:
        order_id: The order to retrieve.
        db: Injected database client.

    Returns:
        Order total in smallest currency unit (cents).

    Raises:
        NotFoundError: If no order exists for the given order_id.
    """
```

---

### 11. Security Baseline

- must validate all external input for type, length, and allowed values before use
- must not pass raw user input to queries, commands, AI prompts, or file paths
- must not log secrets, tokens, passwords, or PII
- must not include secrets in error messages or stack traces

```
// forbidden — raw input passed directly to query and logged with token
function lookupUser(request):
    log.info("lookup", token=request.auth_token)              // logs secret
    return db.query("SELECT * FROM users WHERE id = " + request.user_id)  // injection

// correct — validate first, parameterize query, exclude secrets from logs
function lookupUser(request):
    if not isUUID(request.user_id):
        raise ValidationError("invalid user_id format")
    if len(request.user_id) > 36:
        raise ValidationError("user_id exceeds maximum length")

    log.info("lookup", user_id=request.user_id)               // no secret in log
    return db.query("SELECT * FROM users WHERE id = ?", [request.user_id])  // parameterized
```

---

### 12. Component Boundaries, Reuse, and Object-Oriented Design

See `../../meta/glossary.md` for the definitions of **Component**, **Reusable Unit**, and
**Object-Oriented Design** referenced below.

**Duplication is the trigger, not a style preference.** The moment the same logic (not just
similar-looking code: the same responsibility, same inputs/outputs) exists unchanged at a second
call site, extract it into one component and have both call sites import it. Do not wait for a
third occurrence, and do not extract in anticipation of a call site that does not exist yet
(speculative generality is itself a violation: see `Applied Principles`, Explicitness Over
Implicitness).

- must extract to a shared component on the second identical (or near-identical, same-responsibility)
  occurrence of a block of logic: a bug fixed in one copy and not the other is the failure this
  standard exists to prevent
- must give every component exactly one reason to change (Separation of Concerns, `../../macro/principles.md` #9)
- must not instantiate a third-party SDK/client per call site: one component constructs and
  exports it (this generalizes coding-standards-nodejs's "Centralized Third-Party Client
  Instantiation" rule to all languages)

**When to reach for Object-Oriented Design specifically** (a class/instance, not a plain function):
reach for it only when at least one of these is true for the responsibility being built —
- it owns **mutable state across multiple method calls** that must stay internally consistent
  (a connection pool, a running job's lifecycle, an in-memory cache with eviction)
- it needs **multiple interchangeable implementations behind one interface** (a strategy/adapter
  pattern, e.g. swappable storage backends)
- the domain concept has **several operations that only make sense bound to the same piece of
  state** (a `Job` with `start()`/`fail()`/`complete()` all operating on the same lifecycle record)

Do not default to a class when a plain function suffices: a stateless transformation, a one-shot
I/O call, or a pure validator is a function, not a class, even in an otherwise object-oriented
codebase. Mixing styles per-responsibility is correct; forcing one paradigm project-wide is not
what this standard asks for.

**Recording the choice.** If a project deliberately commits to one dominant style (e.g. "this
service is class-based throughout because it is a stateful job-lifecycle engine"), record that as
a `Code Paradigm` line in the project's Product Brief / CLAUDE.md (see `eng-os-plan-app` skill), same
tier as the Terminology Lock, so every session, human or agent, makes the same per-responsibility
calls consistently instead of re-deciding it file by file.

```
// forbidden — same client construction duplicated at two call sites
// file: boundary-detection.ts
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
// file: metadata-generation.ts
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

// correct — one component, imported everywhere
// file: anthropic-client.ts
let cached = null
function getAnthropicClient() {
  if (!cached) cached = new Anthropic({ apiKey: config.anthropicApiKey })
  return cached
}
```

```
// correct OOD trigger — multiple operations bound to the same lifecycle state
class Job {
  start() { this.status = "running"; this.startedAt = now() }
  fail(error) { this.status = "failed"; this.error = error }
  complete() { this.status = "complete"; this.completedAt = now() }
}

// correct non-OOD — a one-shot pure transformation stays a function
function computeRelevanceScore(clip, queryText) { ... }
```

---

### 13. Model-View-Controller Layering

Every application, regardless of type (web, desktop, CLI, mobile, or a backend service with a UI)
or stack, separates code into three layers. This is not a web-specific pattern; a CLI tool or
backend service benefits from the same separation and follows it too.

- **Model**: data shape, persistence, and business/domain rules. No rendering, no I/O framing, no
  knowledge of how it is presented.
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

```
// forbidden — business logic and rendering mixed into the route handler
function handleCreateRotation(request, response):
    if len(request.body.name) < 3: throw ValidationError("name too short")
    rotation = db.insert("rotations", { name: request.body.name, service_id: request.body.service_id })
    response.send("<div>Created rotation " + rotation.name + "</div>")

// correct — Controller orchestrates only; Model owns the rule; View owns rendering
// models/rotation.ts
function createRotation(input, db):
    if len(input.name) < 3: throw ValidationError(ROTATIONS_MESSAGES.NAME_TOO_SHORT)
    return db.insert("rotations", { name: input.name, service_id: input.service_id })

// views/pages/RotationCreated.ts
function renderRotationCreated(rotation):
    return template("rotation-created", { name: rotation.name })

// controllers/rotations.ts
function handleCreateRotation(request, response):
    rotation = createRotation(request.body, db)          // Model
    response.send(renderRotationCreated(rotation))        // View
```

---

## Failure Modes

- bare catch-all error handlers suppress failures silently and make debugging impossible
- reading env vars at call sites instead of a config module creates configuration drift
- missing defaults cause cryptic startup failures in some environments but not others
- logging secrets in debug mode creates security exposure in stage and prod
- inline magic numbers make threshold changes require code search and multiple edits
- letting identical logic exist at two or more call sites lets them silently drift apart:
  a fix applied to one copy and forgotten in the other is a correctness bug, not just a style issue
- defaulting to Object-Oriented Design project-wide out of habit, rather than per-responsibility
  against the triggers above, adds ceremony (instantiation, `this` binding) with no corresponding
  benefit for stateless logic
- hardcoded UI strings (labels, messages, headings) scattered across components make copy changes,
  localization, and terminology-lock enforcement require a code-wide grep instead of a single-file
  edit
- messages without a stable unique code make it impossible for support/QA/logs to reference "which
  message" without pasting the full text, and reassigning a code after the fact breaks any existing
  reference to it (a support ticket, a log search, a test assertion)
- business logic written directly in a page/route/command handler instead of a Model it calls makes
  the same rule impossible to reuse or test in isolation, and re-derives it with drift the next
  time it is needed elsewhere

---

## Definition of Done

Code meets this standard when:
- `EXECUTION_MODE` drives log level and error behavior
- no secrets or environment-specific values are hardcoded
- all constants are in a config or constants module, split consistently between build-time
  constants and environment-derived config if a project has both
- every value is classified as constant, config, or secret against Standard 3a's litmus test, not
  placed by convenience or copied pattern
- in a multi-process application, a value shared by more than one process lives in exactly one
  place, not hand-duplicated per process; a value only one process needs stays local to it
- in a multi-language application, a shared value is read from the same env var by each language's
  own config module, or sourced from a shared backing service when genuinely runtime-tunable or
  cross-language-displayed; never a hand-copied literal with no drift guard or documented
  single-source-of-truth pointer
- every user-facing string (label, button/link text, heading, placeholder, tooltip,
  success/warning/info/error message) is a named constant sectioned by app area, not an inline
  literal in a component or page
- every success/warning/info/error message carries a unique `{3-letter area}{6-digit sequence}`
  code (e.g. `CST000001`), assigned once and never reused or renumbered; area prefixes are declared
  once per project with no collisions; the 6-digit sequence is one counter shared across the whole
  project, not restarted per area
- all external calls have try/catch with specific error types
- retry logic with exponential backoff is applied to transient calls
- logs are structured and free of secrets
- every public function has at least one happy-path and one failure-path test
- every public function has a docstring covering purpose, params, return value, and errors
- inline comments explain why, never what
- no identical (or near-identical, same-responsibility) logic exists at two or more call sites:
  it has been extracted into one component and imported everywhere it's used
- every third-party SDK/client is constructed in exactly one component, not per call site
- Object-Oriented Design was chosen per-responsibility against the triggers in Standard 12, not
  applied or avoided as a blanket project-wide style
- Model/View/Controller layers are separated and named as such (or the stack's equivalent
  folders), for every app type, not only web apps
- every route/page/command handler (Controller) delegates business logic to a Model it calls,
  rather than implementing that logic inline
