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

Create `src/config.ts`. Export typed constants. Read env vars once at module load; never
call `process.env` at call sites.
- required values: a `requireEnv(key)` helper that throws at startup if missing
- optional values: `process.env.X ?? 'default'` with an explicit default
- load `.env` via `dotenv` in dev only; never in stage or prod

## 3. Secrets

- correct: read via `config.serviceApiKey` (validated at startup through `requireEnv()`)
- forbidden: hardcoded literal (`const apiKey = 'sk-abc123'`)
- risky, avoid: `process.env.SERVICE_API_KEY` directly; silently `undefined` if missing, fails later instead of at startup
- never commit `.env` files; use `.env.example` with placeholder values

## 4. Error Handling

- define typed error classes extending a base `AppError extends Error` (with a `code` field), and specific subclasses (e.g. `ServiceUnavailableError`)
- all async functions wrapped in try/catch; all Promise chains have `.catch()` or live inside async/await try/catch
- register a global `process.on('unhandledRejection', ...)` handler in the entry point that logs and calls `process.exit(1)`; unhandled rejections must be treated as fatal

## 5. Retry with Exponential Backoff

Use `p-retry` (or a typed equivalent) with `randomize: true` (full jitter), `minTimeout`/`maxTimeout` from
`config.retryBaseMs`/`config.retryCapMs`, and `maxRetryTime` as the total budget from `config.retryBudgetMs`. Use `AbortError` to stop retrying
immediately on non-retryable errors (e.g. 401/403).

## 6. Structured Logging

Use `pino` (preferred) or `winston`. Output must be JSON; level driven by `config.executionMode`
(`dev`→debug, `stage`→info, `prod`→warn). Bind `traceId` and `spanId` once at request entry in an `AsyncLocalStorage` store and read it from a
pino `mixin`, so every log line carries them with no argument threading; never rebind at every call site. Sanitize objects before
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
client) separately in every route/file that needs it. Centralize instantiation in one module
(e.g. `lib/anthropic.ts`) and import the shared instance everywhere it's needed.
- Failure mode: per-file instantiation duplicates config/auth logic and makes it easy for one
  call site to drift out of sync with the others (different retry config, different API version,
  a forgotten timeout override, etc.).

## 10. Documentation

JSDoc for all public functions, classes, interfaces, and modules: house standard shared with
Python (`@param`, `@returns`, `@throws`), same tags in both languages.
- module-level JSDoc: one sentence at the top of the file
- function JSDoc: `@param`, `@returns`, `@throws {ErrorType}` per thrown error
- interface/type JSDoc: doc comment on the type plus one per property
- inline comments: why, never what
- do not document internal single-call helpers with self-explanatory names, or constructor bodies already covered by the class JSDoc

See `references/examples.md` for full code samples of each rule above.

## Failure Modes

- unhandled promise rejections crash the process silently in older Node; always register a global handler
- `any` types defeat TypeScript's compile-time contract enforcement and hide schema violations
- calling `process.env` at call sites instead of `config.ts` creates configuration drift
- committing `.env` files exposes secrets in version history even after deletion
- missing `.catch()` on a Promise chain that throws causes silent failures
- instantiating a third-party SDK client per-file instead of centrally causes config/auth drift across call sites

## Definition of Done

- [ ] `tsconfig.json` has `strict: true`
- [ ] `src/config.ts` exists and all env vars are read there
- [ ] required env vars throw at startup if missing
- [ ] all async functions have try/catch with typed error classes
- [ ] retry logic is applied to transient external calls
- [ ] all logs use pino/winston JSON format and exclude secrets
- [ ] `zod` or equivalent validates external data at boundaries
- [ ] tests use jest/vitest with mocked external dependencies
- [ ] third-party SDK clients are instantiated once in a shared module and imported, not re-instantiated per route/file
- [ ] all public functions, classes, interfaces, and modules have JSDoc
- [ ] inline comments explain why, not what
- [ ] `traceId` is carried in `AsyncLocalStorage` from the entry point, not passed through signatures
