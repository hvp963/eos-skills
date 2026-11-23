---
name: eng-os-coding-standards-nodejs
description: "Use when writing Node.js/TypeScript code in a project governed by the Engineering OS: config, error handling, retry, logging, JSDoc, testing conventions."
sources:
  - micro/coding-standards/nodejs.md
globs: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
always_apply: false
verified_platforms: [claude-code]
---

# Coding Standards — Node.js / TypeScript

Node.js/TypeScript-specific implementation of the rules in `eng-os-coding-standards-common`. Load
that skill alongside this one; read both. TypeScript is required, not optional.

## 1. TypeScript Configuration

`strict: true` is required in `tsconfig.json`, no exceptions, along with `noImplicitAny`,
`strictNullChecks`, `noUnusedLocals`, `noUnusedParameters`.

`any` is forbidden without a documented justification comment. Use `unknown` when the type
is genuinely unknown and narrow it explicitly.

## 2. Configuration Module

Create `src/config/env.ts`. Parse every env var once at module load through one `zod` schema
(`EnvSchema.parse(process.env)`) and export a typed `config` object; never call `process.env` at
call sites.
- required values, `EXECUTION_MODE` among them (`z.enum(['dev', 'stage', 'prod'])`, no default): startup fails, with one error listing every missing or invalid variable
- optional values: an explicit `.default(...)` in the schema; numbers through `z.coerce.number().int()`, never an unchecked `parseInt` (which turns `"abc"` into `NaN`)
- `dotenv.config()` loads `.env` when the file exists; it never overrides a variable already set, so in stage and prod the real environment wins; `.env` is never part of the build artifact
- retry counts (`API_NUM_RETRIES`, default 2) are config; the retry timing values are constants in `src/shared/constants/`

## 3. Secrets

- correct: read via `config.serviceApiKey` (validated at startup by the config schema)
- forbidden: hardcoded literal (`const apiKey = 'sk-abc123'`)
- risky, avoid: `process.env.SERVICE_API_KEY` directly; silently `undefined` if missing, fails later instead of at startup
- never commit `.env` files; use `.env.example` with placeholder values

## 4. Error Handling

- define typed error classes extending a base `AppError extends Error` (with a `code` field), and specific subclasses (e.g. `ServiceUnavailableError`)
- every external call inside an async function is wrapped and mapped to a typed error (`ServiceUnavailableError` for the retryable failures in `eng-os-coding-standards-common` Standard 5, carrying `retryAfterMs`; `AppError` otherwise); other errors propagate to the one error-handling middleware or the entry point's handler, never caught only to be rethrown
- every Promise is awaited or has `.catch()`
- register a global `process.on('unhandledRejection', ...)` handler in the entry point that logs and calls `process.exit(1)`; unhandled rejections must be treated as fatal

## 5. Retry with Exponential Backoff

The rule is `eng-os-coding-standards-common` Standard 5. Use a short typed `callWithRetry`
(`src/shared/retry/retry.ts`) that mirrors the Python loop: at most `numRetries + 1` calls, full
jitter `Math.random() * Math.min(RETRY_CAP_MS, RETRY_BASE_MS * 2 ** attempt)`, a wait of the larger of
that delay and the error's `retryAfterMs`, and a stop when the wait would pass `RETRY_BUDGET_MS` or
the caller's deadline. It retries only `err instanceof ServiceUnavailableError`, never by matching
message text. Do not use `p-retry`: its `randomize` multiplies the delay by 1x to 2x, which is not
full jitter, and it cannot honor `Retry-After` within the budget.

One layer owns retry. A vendor SDK with built-in retry owns its calls: set its retry count and
timeout from config (`maxRetries: config.apiNumRetries`; the SDK also counts retries after the
first call) and do not wrap them. `callWithRetry` is for clients that do not retry on their own.

## 6. Structured Logging

Use `pino` (preferred) or `winston`. Output must be JSON; level driven by `config.executionMode`
(`dev`→debug, `stage`→info, `prod`→warn); `service` comes from `config.serviceName`. At request entry, extract the caller's
context with the OpenTelemetry propagator (`propagation.extract`, W3C `traceparent`), start a span, and bind `trace_id` and `span_id`
once in an `AsyncLocalStorage` store that the one logger reads through a pino `mixin`, so every log line carries them with no
argument threading; never pass trace ids at a call site. Outbound calls write `traceparent` with `propagation.inject`;
`x-trace-id` is never emitted. Sanitize objects before
logging to strip sensitive fields. File-based log layout for pipeline jobs: `micro/project-structure.md` Section 5.

## 7. Runtime Schema Validation

Use `zod` (or equivalent) to validate external data at every boundary: API requests, API
responses, events, DB reads. Parse into a typed object (`Schema.parse(raw)`); never trust
an external payload's shape implicitly.

## 8. Testing

Use `jest` or `vitest`. Mock all external calls in unit tests (`vi.spyOn`, `vi.mock`). Cover
one happy path and one failure path per public function minimum (see common skill Standard 9).

## 9. Centralized Third-Party Client Instantiation

Do not instantiate a third-party SDK client (e.g. an AI provider client, a payment SDK, a queue
client) separately in every route/file that needs it. Centralize instantiation in one module under
`src/shared/<provider>/` (e.g. `src/shared/anthropic/client.ts`) and import the shared instance only
from repositories: an external client is a repository's job (`eng-os-coding-standards-common`
Standard 13), so controllers and services never call the SDK.
- Failure mode: per-file instantiation duplicates config/auth logic and makes it easy for one
  call site to drift out of sync with the others (different retry config, different API version,
  a forgotten timeout override, etc.).

## 10. Documentation

JSDoc for all public functions, classes, interfaces, and modules (`@param`, `@returns`, `@throws`).
Python documents the same content in Google style (ADR-002).
- module-level JSDoc: one sentence at the top of the file
- function JSDoc: `@param`, `@returns`, `@throws {ErrorType}` per thrown error
- interface/type JSDoc: doc comment on the type plus one per property
- inline comments: why, never what
- do not document internal single-call helpers with self-explanatory names, or constructor bodies already covered by the class JSDoc

See `references/examples.md` for full code samples of each rule above and the MVCS layout reference in `eng-os-coding-standards-common` for the layout.

## 11. Capability Layout (MVCS)

Applies `eng-os-coding-standards-common` Standard 13 to TypeScript. Layers, folders, and dependency
direction are defined there; this section adds only the TypeScript specifics.

- file names are kebab-case `<topic>.<layer>.ts`, where the topic is the concept the file is about, not necessarily the capability's name:
  - `.controller.ts`: a route handler, topic is the resource; plural for the collection route (`/api/orders`), singular for one item (`/api/orders/[id]`); an uncountable noun keeps one form
  - `.page.tsx` (and `.layout.tsx`, `.loading.tsx`, `.error.tsx`, `.not-found.tsx`): a page, topic is the last segment of the URL it serves (`checkout.page.tsx` serves `/checkout`, whichever capability owns it)
  - `.service.ts`, `.repository.ts`, `.model.ts`: topic is the concept (`orders.service.ts`)
  - in `views/`: a component is PascalCase `.tsx` (`OrderTable.tsx`); an output shape is `<name>.view.ts`; any other data or helper is kebab-case `.ts`
  - a hook is `use<Name>.ts` or `.tsx`; see the hook rule below for its folder
  - tests are `<same name>.test.ts` at the mirrored path; identifier casing follows ADR-001
- controller: binds the route and validates `body`, `query`, and `params` with a `zod` schema, mapping snake_case wire fields to camelCase once at that boundary, then calls one service
- service: a factory function (`makeOrdersService(ordersRepository)`) or a class taking repositories in the constructor; imports no `Request`, `Response`, or status code; throws typed errors from `src/shared/errors/`
- repository: the only layer that imports the database client; parameterized statements only (`$1`, `$2`)
- page and view (React): the page (`.page.tsx`) is the controller. It reads the route parameters, resolves them with a service function, owns the state that must survive navigation, and passes data and callbacks down as props. A component in `views/` receives props and keeps only presentation state. A hook that does controller work (fetching through a client service, subscribing, reading the URL) lives in `controllers/`; a hook shared by two or more capabilities lives in `shared/views/` (a hook is not a component)
- framework routing folders: where the framework routes by file location (Next.js `app/`), each routing file is a one-line re-export of the capability's `.page.tsx` or `.layout.tsx`; the routing folder is declared in CLAUDE.md as a framework override, and the naming test skips it
- error mapping: one error-handling middleware translates domain errors to status codes and the one error envelope (`ValidationError` 400, `BusinessRuleError` 422, `ConflictError` 409; `eng-os-api-design`, Error Contract)
- enforcement: declare the dependency direction in `dependency-cruiser` (`forbidden` rules) or `eslint-plugin-boundaries` and run it in CI; add a test that walks `src/capabilities/` and fails on a file whose name breaks the rule for its layer folder, with an exception list that may only shrink

## Failure Modes

- unhandled promise rejections crash the process silently in older Node; always register a global handler
- `any` types defeat TypeScript's compile-time contract enforcement and hide schema violations
- calling `process.env` at call sites instead of `config/env.ts` creates configuration drift
- committing `.env` files exposes secrets in version history even after deletion
- missing `.catch()` on a Promise chain that throws causes silent failures
- a handler that reaches the database client directly, or a service that imports the HTTP framework, defeats the layering that makes services testable without a server or a database
- instantiating a third-party SDK client per-file instead of centrally causes config/auth drift across call sites

## Definition of Done

All items are Per change: this domain has no Standing (release and audit) items.

- [ ] `tsconfig.json` has `strict: true`
- [ ] `src/config/env.ts` exists and all env vars are parsed there through one schema; `EXECUTION_MODE` is required, with no fallback
- [ ] required env vars throw at startup if missing
- [ ] external calls have try/catch with typed error classes; nothing else catches only to rethrow
- [ ] retry follows `eng-os-coding-standards-common` Standard 5 (full jitter, cap, budget, `Retry-After`, one owning layer)
- [ ] all logs use pino/winston JSON format and exclude secrets
- [ ] `zod` or equivalent validates external data at boundaries
- [ ] tests use jest/vitest with mocked external dependencies
- [ ] every capability has `controllers/`, `services/`, `repositories/`, `models/`, and `views/` with `<topic>.<layer>.ts` names, a test fails on a file whose name breaks the rule for its folder, and the dependency direction is enforced by `dependency-cruiser` (or equivalent) in CI
- [ ] no file in `views/` reads or writes a route parameter, calls a service, or holds state the page needs after navigation
- [ ] third-party SDK clients are instantiated once in `src/shared/<provider>/` and imported only by repositories, never re-instantiated per route/file
- [ ] all public functions, classes, interfaces, and modules have JSDoc
- [ ] inline comments explain why, not what
- [ ] `traceId` is carried in `AsyncLocalStorage` from the entry point, not passed through signatures
