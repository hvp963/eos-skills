---
name: eng-os-api-design
description: "Use when defining or reviewing an HTTP/RPC CONTRACT itself: request/response schemas, versioning, idempotency keys, pagination, rate limiting, caching headers. For overall service architecture decisions, see `eng-os-system-design`. For scaffolding a new service end-to-end, see `eng-os-system-design/references/service-checklist.md`."
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
            body={"error": "rate_limit_exceeded", "retry_after_seconds": retryAfter})

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
Additive changes (new optional fields) require no version bump; consumers must ignore unknown fields. Breaking changes (renaming/removing/restructuring fields) require a new version plus a migration guide. Announce deprecation via response headers (`Deprecation`, `Sunset`, `Link`) on every response of the deprecated version, not only in release notes.
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

- [ ] Request and response contracts are explicit
- [ ] Versioning strategy is clear (additive vs. breaking, deprecation headers)
- [ ] Error behavior is defined
- [ ] Idempotency is addressed for all mutable operations
- [ ] Caching behavior, including invalidation, is defined where caching is used
- [ ] Rate limit keying is explicit and documented
- [ ] Pagination contract is consistent (cursor or offset, not mixed) and `has_more` is present
- [ ] Observable signals exist for latency, errors, and usage
- [ ] Every endpoint declares its authentication mechanism and authorization rule (principal, scope, action)
- [ ] Deadlines propagate through downstream calls; per-hop timeouts derive from the remaining budget
- [ ] High-volume collections have a batch contract with a maximum size and per-item status
