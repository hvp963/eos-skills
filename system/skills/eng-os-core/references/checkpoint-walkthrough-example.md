# Checkpoint Walkthrough: Worked Example

A concrete run through the Checkpoint Table for one task: **"Add a new `POST /v1/customers`
endpoint that creates a customer record with a phone-number field."**

This assumes a project already bootstrapped with Active Skills including
`eng-os-coding-standards-common`, `eng-os-coding-standards-nodejs`, `eng-os-api-design`,
`eng-os-database-design`, `eng-os-security-practices`, `eng-os-privacy-and-governance`,
`eng-os-reliability-engineering`, `eng-os-observability`, `eng-os-testing-strategy`,
`eng-os-code-conventions`, and `eng-os-documentation-standards`. A checkpoint fires whether or not
its skill is listed; one that fires for a missing skill adds that skill to Active Skills in the
same change.

## Sequence of checkpoints hit

1. **New capability, and its first source files**: `customers` does not exist yet.
   - Invoke: `eng-os-coding-standards-common` Standard 13, plus `eng-os-coding-standards-nodejs`.
   - Verify: all five layer folders are created together, each file named for its layer:
     `src/capabilities/customers/controllers/customers.controller.ts`,
     `services/customers.service.ts`, `repositories/customers.repository.ts`,
     `models/customer.model.ts`, and `views/customer.view.ts`. The service receives the
     repository by injection from `src/app.ts`, the composition root; it never builds one.
   - **Failing check example:** one file `src/routes/customers.ts` validates, writes to the
     database, and formats the response. It works, and it is business logic, persistence, and
     rendering in one route handler.

2. **Any naming decision**: the field name for the phone number.
   - Invoke: `eng-os-code-conventions` (Terminology Lock).
   - Verify: check the Terminology Lock and the existing schema first. Suppose CLAUDE.md's
     Terminology Lock already says "phone" (not "phoneNumber" or "mobile") is canonical. The
     field is named `phone`, matching existing usage, not invented fresh.
   - **Failing check example:** an agent names the field `mobileNumber` because that felt natural
     in isolation. This is a checkpoint failure even though the code works: it introduces a
     synonym for an already-decided term.

3. **Endpoint contract**: the endpoint itself is being defined.
   - Invoke: `eng-os-api-design`.
   - Verify: the route is versioned (`/v1/customers`); every error uses the one envelope and the
     status rule in Error Contract; this is additive (a new endpoint), so no migration concern.
   - **Passing check example:** `201` with the created customer on success. A phone that is not
     E.164 fails the controller's schema, a shape error, so the response is `400`:

     ```json
     {
       "error": {
         "type": "validation_error",
         "code": "invalid_phone",
         "message": "Enter the phone number in international format, e.g. +14155550100.",
         "message_code": "CST000004",
         "field": "phone",
         "api_version": "v1",
         "request_id": "req_7c21"
       }
     }
     ```

     A second customer with an email already on file is a state conflict: `409` with `type:
     "conflict"`, raised by the repository's unique constraint, not by a read-then-write check.
   - **Failing check example:** `200` with a bare string `"invalid phone"`, or a `422` for the
     malformed phone. Neither tells the client whether to fix its request or accept a refusal.

4. **Table, index, or migration**: `customers` needs a `phone` column.
   - Invoke: `eng-os-database-design`.
   - Verify: the migration is reversible (a paired `down` drops the column) and runs as its own
     gated pipeline stage before the deploy; adding `phone` as `NOT NULL` to a populated table is
     flagged as unsafe without a backfill or a default.

5. **Input validation, auth, or a trust boundary**: the endpoint accepts external input and
   sits behind auth.
   - Invoke: `eng-os-security-practices`.
   - Verify: the phone is validated for type, format, and length at the controller, before any
     business logic or database call; the route uses the same authentication and authorization
     as the other customer-mutation routes; a validation failure logs the field name, never the
     rejected value.
   - **Failing check example:** the handler passes the raw request body to the ORM's `create()`
     and relies on the database's `NOT NULL` constraint. That catches a missing field and nothing
     else.

6. **Personal data**: a phone number identifies a person.
   - Invoke: `eng-os-privacy-and-governance`.
   - Verify: the `customers` dataset is classified Confidential in the data dictionary, with an
     owner, a purpose, a retention period, and its deletion procedure; the phone never appears in
     logs, metric labels, or error messages (the 400 above names the field, not the value).

7. **New user-facing message**: the validation message is shown to the user.
   - Invoke: `eng-os-coding-standards-common` Standard 3.
   - Verify: the text is a named constant in `src/shared/constants/customers.ts`
     (`CUSTOMERS_MESSAGES.INVALID_PHONE`) with the code `CST000004`, the next number in the
     project-wide sequence from CLAUDE.md's Message Area Codes; the counter advances to 000005.

8. **Outbound call, timeout, or retry**: the repository calls the database.
   - Invoke: `eng-os-reliability-engineering`.
   - Verify: the pool's acquire and query timeouts derive from the request's remaining deadline;
     an insert is not retried (it is not idempotent without a key), so no retry layer is added.

9. **Public function complete**: the controller handler and `createCustomer(input): Customer`.
   - Invoke: `eng-os-coding-standards-nodejs`.
   - Verify: type annotations on `input` and the return value; JSDoc with `@param`, `@returns`,
     and `@throws` for each error; the database call is wrapped so a connection failure surfaces
     as a typed error, not an unhandled rejection.

10. **Test file**: `tests/capabilities/customers/controllers/customers.controller.test.ts` and
    the service and repository tests at their mirrored paths.
    - Invoke: `eng-os-testing-strategy`.
    - Verify: a happy-path test (valid phone, expect 201) and failure paths (malformed phone,
      expect 400 with `CST000004`; duplicate email, expect 409; missing auth, expect 401). The
      service test injects a fake repository; the repository test runs against a real database
      inside a rolled-back transaction.

11. **Log, metric, trace, or alert**: customer creation is worth observing.
    - Invoke: `eng-os-observability`.
    - Verify: the log line on creation carries the Standard 6 minimum fields (`timestamp`,
      `level`, `message`, `trace_id`, `span_id`, `service`) and the new customer's ID, never the
      phone; the request is measured by `http.server.request.duration` with `http.route:
      /v1/customers`; a custom counter `customers.create.count` is added now, before an incident
      makes its absence obvious.

12. **Contract doc or other doc file**: the API reference gains the endpoint.
    - Invoke: `eng-os-documentation-standards` + `eng-os-prose-style`.
    - Verify: `Status:` and `Owner:` present; the doc describes the endpoint's actual behavior
      (fields, status codes, the error envelope), not aspirational behavior.

13. **Marking the task done**: run the Meta Definition of Done.
    - For every skill invoked above, confirm that its **Per change** DoD items ran and passed,
      not just that code was written. A **Standing** item found missing along the way (say,
      the runbook has no entry for the customers service) is recorded as a gap in the task
      summary, not a blocker.

14. **Session ends**: `eng-os-documentation-standards` again: does any decision meet the ADR
    threshold? "Use `phone`, E.164 format" confirms a locked term and is below it. Had the task
    also decided "customers are keyed by email, not a new `customer_id`", that decision would be
    expensive to reverse and would need an ADR.

## What this shows about the table

Checkpoints fire interleaved with implementation, in the order the work touches them:
capability → naming → contract → schema → security → personal data → message → outbound call →
function → test → observability → docs → task done → session end. Several fire more than once in
spirit (naming recurs throughout). Going straight from "write the route" to "write the test"
without the contract, security, and privacy checkpoints in between is the drift the table exists
to prevent, even if the final code happens to work.
