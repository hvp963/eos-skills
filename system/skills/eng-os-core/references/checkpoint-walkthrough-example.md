# Checkpoint Walkthrough — Worked Example

A concrete run through the Checkpoint Table for one task: **"Add a new `POST /customers`
endpoint that creates a customer record with a phone-number field."**

This assumes a project already bootstrapped with Active Skills including `eng-os-api-design`,
`eng-os-database-design`, `eng-os-security-practices`, `eng-os-observability`, `eng-os-testing-strategy`,
`eng-os-coding-standards-nodejs`, `eng-os-code-conventions`, `eng-os-documentation-standards`.

## Sequence of checkpoints actually hit

1. **Before each module**: a new route/controller file, e.g. `src/routes/customers.ts`, is
   about to be created.
   - Invoke: `eng-os-coding-standards-common` + `eng-os-coding-standards-nodejs`.
   - Verify: the file goes in `src/routes/`, not mixed into an existing unrelated module; it has
     one responsibility (handling the customer-creation route), not also handling e.g. billing.

2. **Before naming any variable, file, class, constant, or env var**: deciding the field name
   for the phone number.
   - Invoke: `eng-os-code-conventions`.
   - Verify: check the Terminology Lock / existing schema first. Suppose the project's CLAUDE.md
     Terminology Lock already says "phone" (not "phoneNumber" or "mobile") is canonical for this
     domain. The field is named `phone`, matching existing usage, not invented fresh.
   - **Failing check example:** an agent names the field `mobileNumber` because that felt natural
     in isolation, without checking the Terminology Lock. This is a checkpoint failure even
     though the code works: it introduces a synonym for an already-decided term.

3. **Before each API endpoint or contract change**: the endpoint itself is being defined.
   - Invoke: `eng-os-api-design`.
   - Verify: versioning strategy declared (e.g. route lives under `/v1/customers`, not bare
     `/customers`); error schema explicit for validation failures (e.g. a 422 with a structured
     `{ field, message }` array, not a bare string); this is additive (new endpoint), so no
     migration concern.
   - **Passing check example:** the endpoint returns `201` with the created customer body on
     success, and on an invalid phone number returns `422 { errors: [{ field: "phone", message:
     "must be E.164 format" }] }`, explicit, versioned, structurally consistent with other
     endpoints in the service.
   - **Failing check example:** the endpoint returns `200` with a bare string `"invalid phone"`
     on bad input, with no field-level structure and no version prefix. This passes a manual
     smoke test but fails the checkpoint: error schema isn't explicit or consistent, and the
     route isn't versioned.

4. **Before each schema or migration**: the `customers` table needs a new `phone` column (or a
   new table if `customers` doesn't exist yet).
   - Invoke: `eng-os-database-design`.
   - Verify: migration is reversible (a paired `down` migration drops the column cleanly); if
     `phone` is added as `NOT NULL` to an existing populated table, that's flagged as unsafe
     without a backfill step or a default; the migration must justify how existing rows are
     handled.

5. **Before touching input validation, auth, secrets, or an external trust boundary**: this
   endpoint accepts external input (phone number) and is presumably behind auth.
   - Invoke: `eng-os-security-practices`.
   - Verify: phone number is validated (format, length) at the boundary before it reaches
     business logic or the database; the route requires the same auth/authorization as other
     mutating customer endpoints (least privilege; an unauthenticated caller cannot create
     customers); no part of the phone number or customer PII is logged in plaintext at
     `info`/`debug` level.
   - **Passing check example:** input validation rejects `phone: "not-a-number"` with a 422
     before any DB write is attempted, and the auth middleware used is the same one already
     protecting other customer-mutation routes.
   - **Failing check example:** the handler passes the raw request body straight to the ORM
     `create()` call with no validation, relying on the database's `NOT NULL` constraint alone
     to catch bad input. This technically "works" for missing fields but not for malformed ones
     (e.g. `phone: 12345` as a number, or a phone string with SQL-breaking characters if
     validation is skipped entirely). Validation-at-the-boundary is a stated Core Principle,
     not optional.

6. **Before each public function**: the controller function and any new service-layer function
   (e.g. `createCustomer(input): Customer`).
   - Invoke: `eng-os-coding-standards-common` + `eng-os-coding-standards-nodejs`.
   - Verify: type annotations present on `input` and return type; a docstring explaining what
     the function does and its error conditions; the external DB call is wrapped so a connection
     failure surfaces as a typed error, not an unhandled rejection; no secrets logged.

7. **Before each test file**: `src/routes/customers.test.ts` is created.
   - Invoke: `eng-os-testing-strategy`.
   - Verify: a happy-path test (valid phone, expect 201) and at least one failure-path test
     (invalid phone format, expect 422; missing auth, expect 401); external dependencies (the DB)
     are mocked or use a test database, not the real production connection.

8. **Before adding logs, metrics, or traces**: this is a new operation worth observability.
   - Invoke: `eng-os-observability`.
   - Verify: a structured log line on customer creation includes `trace_id`, `span_id`,
     `severity`, `service`, and the new customer's ID (not the raw phone number, per the security
     checkpoint above); a counter metric like `customers_created_total` is added now, before any
     incident makes its absence obvious.

9. **Before each doc file**: if an API contract doc or changelog entry is added for this new
   endpoint.
   - Invoke: `eng-os-documentation-standards`.
   - Verify: `Status:` and `Owner:` frontmatter present; the doc describes the endpoint's actual
     current behavior (fields, status codes) rather than aspirational behavior.

10. **Before marking a task done**: run the Meta Definition of Done: for every skill invoked
    above (`eng-os-coding-standards-nodejs`, `eng-os-code-conventions`, `eng-os-api-design`, `eng-os-database-design`,
    `eng-os-security-practices`, `eng-os-testing-strategy`, `eng-os-observability`, `eng-os-documentation-standards`),
    confirm that skill's own DoD checklist was actually run and passed, not just that code was
    written.

11. **Before the session ends**: `eng-os-documentation-standards` again: was an ADR needed? Here, "use
    `phone` as the canonical field name, E.164 format" is arguably a small terminology
    confirmation rather than a new architectural decision, but if this task also decided, say,
    "customers are keyed by email, not a new customerId," that would be a significant decision
    requiring an ADR under the Session-End Rule.

## What this shows about the table

The checkpoint table isn't a checklist run once at the end; checkpoints fire interleaved with
implementation, in the order the work naturally touches them (module → naming → contract →
schema → security → function → test → observability → docs), and several skills are invoked more
than once conceptually (naming decisions recur throughout). Skipping straight from "write the
route" to "write the test" without the `eng-os-api-design` and `eng-os-security-practices` checkpoints in
between is the drift the table exists to prevent, even if the final code happens to work.
