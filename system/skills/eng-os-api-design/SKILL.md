---
name: eng-os-api-design
description: "In a project governed by the Engineering OS, use when defining or reviewing an HTTP/RPC CONTRACT itself: request/response schemas, versioning, idempotency keys, pagination, rate limiting, caching headers. For overall service architecture decisions, see `eng-os-system-design`. For scaffolding a new service end-to-end, see `eng-os-system-design/references/service-checklist.md`."
sources:
  - meso/api-design.md
globs: ["**/api/**", "**/routes/**"]
always_apply: false
verified_platforms: [claude-code]
---

# API Design

Apply these rules when designing a new API surface or reviewing an existing one.

## Principles

- **Contracts as source of truth.** Define request, response, error, and versioning behavior explicitly; never leave any of these implicit.
- **Validate at boundaries.** Validate structure and required fields before processing, on both requests and responses.
- **Explicitness over implicitness.** Never rely on undocumented defaults or hidden behavior.
- **Idempotency by default.** Any retryable operation must be safe to repeat.
- **Observability as a first-class concern.** Expose latency, error rate, and usage signals for every endpoint.

## Core Patterns

### Error Contract
Every error response, on every endpoint, carries one envelope, declared here as part of the API contract:

```json
{
  "error": {
    "type":         "business_rule_error",
    "code":         "insufficient_stock",
    "message":      "SKU-1002 has 0 units available.",
    "message_code": "ORD000014",
    "field":        "items[1].sku",
    "api_version":  "v1",
    "request_id":   "req_3fa8c1"
  }
}
```

- `type`: one of the types in the table below.
- `code`: the machine code, stable for that error, that clients branch on.
- `message`: human-readable text; never internals, stack traces, or SQL.
- `message_code`: present when the message is shown to a user; the `{AAA}{NNNNNN}` code from `eng-os-coding-standards-common` Standard 3.
- `field`: present when one input field caused the error.
- `api_version` and `request_id`: always present, so a client report can be traced.

The layer that rejects a request decides its status (`eng-os-coding-standards-common` Standard 13), and the one error-handling middleware maps the error type to the status and the envelope:

| Status | `type` | Raised as | When |
|---|---|---|---|
| `400` | `validation_error` | `ValidationError`, by the controller's schema | The request is malformed or fails shape validation (a missing field, a wrong type, a value out of range) |
| `422` | `business_rule_error` | `BusinessRuleError`, by the service | The request is well-formed but fails a business rule (not enough stock, a retired service) |
| `409` | `conflict` | `ConflictError`, by the service or repository | The request conflicts with current state (a version mismatch, a duplicate key, an invalid state transition) |
| `429` | `rate_limited` | the rate limiter | The caller exceeded its rate limit; the response carries `Retry-After` |

`401`, `403`, `404`, and `5xx` responses use the same envelope (`unauthenticated`, `forbidden`, `not_found`, `internal_error`, `unavailable`); a `5xx` message is generic and a `503` carries `Retry-After` when the wait is known.
- Failure mode: several error shapes across one API make every client write several parsers; a status chosen by habit leaves clients unable to tell "fix your request" from "valid but refused".

### Idempotent Mutation
Use request identifiers or stable operation identity so retries are safe when the caller cannot know if the first attempt succeeded.

### Caching
Cache read-heavy, stable data only when invalidation rules are explicit.
- Failure mode: caching without explicit invalidation returns stale data and confuses clients.

### Rate Limiting
Apply a token bucket at the request boundary, keyed explicitly (`api_key | user_id | ip_address`; never an implicit default). Return `429` with a `Retry-After` header and document the bucketing key in the API contract.

```
function handleRequest(request):
    key    = resolveKey(request)   // explicit, never implicit
    bucket = rateLimiter.get(key)

    if not bucket.consume(tokens=1):
        retryAfter = bucket.secondsUntilRefill()
        return Response(status=429,
            headers={"Retry-After": retryAfter, "X-RateLimit-Limit": bucket.limit},
            body={"error": {"type": "rate_limited", "code": "rate_limit_exceeded",
                            "message": "Too many requests. Retry after " + retryAfter + " seconds.",
                            "api_version": API_VERSION, "request_id": request.id}})

    return processRequest(request)
```
- Failure mode: keying by IP rejects all users behind a NAT as one caller; omitting `Retry-After` forces clients to guess.

### Pagination Contract
Use cursor-based pagination for large/changing datasets, offset-based for small/stable ones; never mix within one API.
- `has_more` is required in the response; never make clients infer it from `len(data) == page_size`.
- `total_count` is optional; omit it if the count query is expensive.
- Cursors must be opaque; never encode internal state (row IDs, offsets) that a client could persist and depend on.
- Failure mode: computing `total_count` via full-table scan on every page adds O(n) cost per request.

### Versioning Migration
Additive changes (new optional fields) require no version bump; consumers must ignore unknown fields. Breaking changes (renaming/removing/restructuring fields) require a new version plus a migration guide. Announce deprecation via response headers on every response of the deprecated version, not only in release notes: `Deprecation: @1798761600` (RFC 9745, a Unix time), `Sunset: Fri, 01 Jan 2027 00:00:00 GMT` (RFC 8594, an HTTP-date), and a `Link` with `rel="deprecation"` to the migration guide.
- Failure mode: announcing deprecation only in docs/email misses consumers who don't read them; a machine-readable `Sunset` header lets clients alert automatically.

See `references/example.md` for a full worked contract (`POST /api/orders`, error shape,
idempotency key, versioned breaking change, cursor pagination) with right/wrong versions side by side.

### Authentication and Authorization per Endpoint
Every endpoint's contract declares its auth mechanism and its authorization rule: which principal types may call it, which resource scope they must hold (tenant, account), which action they must be permitted. Authorization is evaluated inside the service on every call against the resource in the request, never inferred from the network path or the gateway alone.
```
endpoint: GET /api/v1/orders/{order_id}
auth:     bearer (OAuth2)
authz:    principal.tenant_id == order.tenant_id AND principal.can("orders:read")
```
- Failure mode: "is authenticated" without "owns this resource" leaks every tenant's data to any logged-in caller.
- The authorization model, threat modeling, and audit logging behind these rules: `eng-os-security-practices`.

### Deadline Propagation
Every request carries a deadline (absolute time or remaining-budget header such as `X-Request-Deadline`). Each downstream call subtracts elapsed time and passes the remainder; a call whose remaining budget is below its minimum useful timeout fails fast. Per-hop timeouts derive from the deadline, never independently per layer.
- Failure mode: independent 30s timeouts at gateway, service, and database let a request run 90s after the caller gave up at 30s.
- The timeouts, retries, and circuit breakers that consume this deadline: `eng-os-reliability-engineering`.

### Bulk and Batch Contracts
High-volume collections get a batch endpoint with a documented maximum batch size, per-item result status, and the single-item idempotency semantics applied per item.
- Failure mode: no batch contract pushes clients into N+1 loops the rate limiter then rejects.

## Failure Modes

- breaking changes shipped without a migration plan
- undocumented defaults cause client drift
- missing validation lets bad input corrupt downstream logic
- non-idempotent mutations multiply side effects on retry
- missing error contract makes recovery logic inconsistent
- endpoints that authenticate but do not authorize against the requested resource leak cross-tenant data
- per-hop timeouts with no propagated deadline keep working after the caller has given up

## Definition of Done

All items are Per change: this domain has no Standing (release and audit) items.

- [ ] Request and response contracts are explicit
- [ ] Versioning strategy is clear (additive vs. breaking, deprecation headers)
- [ ] Error behavior is defined: every error uses the one envelope and the status rule in Error Contract (400 shape, 422 business rule, 409 conflict, 429 rate limited)
- [ ] Idempotency is addressed for all mutable operations
- [ ] Caching behavior, including invalidation, is defined where caching is used
- [ ] Rate limit keying is explicit and documented
- [ ] Pagination contract is consistent (cursor or offset, not mixed) and `has_more` is present
- [ ] Observable signals exist for latency, errors, and usage
- [ ] Every endpoint declares its authentication mechanism and authorization rule (principal, scope, action)
- [ ] Deadlines propagate through downstream calls; per-hop timeouts derive from the remaining budget
- [ ] High-volume collections have a batch contract with a maximum size and per-item status
