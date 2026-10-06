# API Design

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for designing stable, explicit, and evolvable service interfaces.

### What This Is Not
- not frontend UI design
- not only REST conventions
- not transport-specific documentation only

## Scope
- Level: Meso
- Applies To: Internal and external service interfaces

---

## Applied Principles

### Contracts as Source of Truth
APIs must define request, response, error, and versioning behavior explicitly.

### Validation at Boundaries
Requests and responses must be validated.

### Explicitness Over Implicitness
Do not rely on undocumented defaults or hidden behavior.

### Idempotency by Default
Retryable operations must be safe where repeats are possible.

### Observability as a First-Class Concern
APIs must expose meaningful latency, error, and usage signals.

---

## Core Patterns

### Explicit Schema Validation
Validate structure and required fields before processing.

### Versioning
Use additive evolution when possible and plan explicitly for breaking changes.

### Idempotent Mutation
Use request identifiers or stable operation identity when retries can occur.

### Caching
Use response or object caching for read-heavy, stable data when freshness semantics are clear.

#### Failure Mode
Caching an API without explicit invalidation rules returns stale data and confuses clients.

---

### Rate Limiting

Apply a token bucket at the request boundary. Return `429` with a `Retry-After` header. Key must be explicit, not implicit.

```
// token bucket per caller
function handleRequest(request):
    key    = resolveKey(request)   // explicit: api_key | user_id | ip_address — never implicit
    bucket = rateLimiter.get(key)

    if not bucket.consume(tokens=1):
        retryAfter = bucket.secondsUntilRefill()
        log.warn("rate limit exceeded", key=key, retry_after=retryAfter)
        return Response(
            status  = 429,
            headers = { "Retry-After": retryAfter, "X-RateLimit-Limit": bucket.limit },
            body    = { "error": "rate_limit_exceeded", "retry_after_seconds": retryAfter },
        )

    return processRequest(request)
```

Rate limit keys must be documented in the API contract: callers must know what they are bucketed by. Do not silently bucket by IP if the API key is available.

#### Failure Mode
A rate limiter keyed by IP rejects all users behind a NAT as a single caller. A rate limiter with no `Retry-After` header forces clients to guess the retry interval.

---

### Pagination Contract

Return a consistent envelope for all paginated responses. Use cursor or offset consistently; do not mix.

```
// cursor-based (preferred for large or frequently changing datasets)
GET /orders?cursor=<opaque_token>&page_size=50

response:
{
    "data":        [...],
    "next_cursor": "<opaque_token>",   // null when no further pages
    "has_more":    true,
    "page_size":   50
}

// offset-based (acceptable for small, stable datasets)
GET /products?offset=100&limit=50

response:
{
    "data":   [...],
    "offset": 100,
    "limit":  50,
    "has_more": true
    // total count: omit unless the count query is cheap and accurate
}
```

Rules:
- `has_more` is required; do not make clients infer from `len(data) == page_size`
- `total_count` is optional and should be omitted if the query is expensive
- `page_size` in the response reflects what was actually returned, not what was requested
- cursors must be opaque to callers; never encode internal state (offsets, row IDs) in a cursor that clients may persist

#### Failure Mode
Returning `total_count` via a full-table scan on every paginated request adds O(n) cost per page and degrades under load.

---

### Versioning Migration

Additive changes do not require a new version. Breaking changes require an explicit version bump and a migration guide. Deprecated versions must announce sunset via a response header.

```
// additive change — no version bump required
// before: { "id": "123", "status": "active" }
// after:  { "id": "123", "status": "active", "created_at": "2026-01-01T00:00:00Z" }
// consumers ignore unknown fields — safe to add

// breaking change — requires new version
// v1: { "name": "John Smith" }                     // single name field
// v2: { "first_name": "John", "last_name": "Smith" }  // split — v1 consumers break

GET /v2/users/123
response: { "first_name": "John", "last_name": "Smith" }

// migration path
migration_guide:
    from_version: v1
    to_version:   v2
    changed:      "name" field replaced by "first_name" + "last_name"
    adapter:      v1 compatibility shim available until sunset_date

// deprecation announcement — on every v1 response
headers:
    "Deprecation":  "true"
    "Sunset":       "2027-01-01"
    "Link":         '</v2/users>; rel="successor-version"'
```

Deprecation header must appear on every response of the deprecated version, not only in documentation.

#### Failure Mode
Announcing version deprecation only in release notes or emails misses consumers who do not read them. The `Sunset` header is machine-readable and can trigger automated alerts in API clients.

---

### Authentication and Authorization per Endpoint

Every endpoint declares, in its contract, the authentication mechanism it accepts and the
authorization rule it enforces: which principal types may call it, which resource scope they
must hold (tenant, account, project), and which action they must be permitted to perform.
Authorization is evaluated inside the service on every call, keyed on the resource in the
request, never inferred from the network path or from the gateway alone.

```
endpoint: GET /api/v1/orders/{order_id}
auth:     bearer (OAuth2 access token)
authz:    principal.tenant_id == order.tenant_id AND principal.can("orders:read")
```

- Failure mode: a tenant-scoped endpoint that checks "is authenticated" but not "owns this
  resource" leaks every tenant's data to any logged-in caller. This is the most common
  high-severity bug class in multi-tenant APIs.

### Deadline Propagation

Every request carries a deadline (an absolute time, or a remaining-budget header such as
`X-Request-Deadline`). Each downstream call subtracts elapsed time and passes the remainder;
a call whose remaining budget is below its minimum useful timeout fails fast instead of
starting work that cannot complete in time. Per-hop timeouts are derived from the deadline,
not hardcoded independently at every layer.

- Failure mode: independent per-hop timeouts (30s gateway, 30s service, 30s database) let a
  request run for 90s of real work after the caller gave up at 30s, holding connections and
  threads for a result nobody will read. Under load this is the difference between graceful
  degradation and collapse.

### Bulk and Batch Contracts

For collections that clients read or write at volume, provide a batch endpoint with an
explicit, documented maximum batch size, per-item result status (a batch is not all-or-nothing
unless the contract says so), and the same idempotency key semantics as the single-item
endpoint applied per item.

- Failure mode: no batch contract pushes clients into N+1 request loops that the rate limiter
  then rejects; a batch contract with no per-item status forces a full retry of the batch when
  one item fails.

## Failure Modes

- breaking changes without migration plan
- undocumented defaults create client drift
- no validation lets bad inputs corrupt downstream logic
- non-idempotent mutations multiply side effects
- missing error contract makes recovery logic inconsistent
- endpoints that authenticate but do not authorize against the requested resource leak cross-tenant data
- per-hop timeouts with no propagated deadline keep doing work after the caller has given up

---

## Definition of Done

API design is complete when:
- request and response contracts are explicit
- versioning strategy is clear
- error behavior is defined
- idempotency is addressed for mutable operations
- caching behavior is defined where used
- observable signals exist for latency, errors, and usage
- every endpoint declares its authentication mechanism and its authorization rule (principal, scope, action)
- deadlines propagate through every downstream call; per-hop timeouts derive from the remaining budget
- high-volume collections have a batch contract with a maximum size and per-item result status
