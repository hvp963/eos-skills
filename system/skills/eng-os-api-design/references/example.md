# Worked Example: `POST /api/orders` and `GET /api/orders`

A concrete contract for a single resource, showing the rules in `SKILL.md` applied together:
idempotency, explicit error contract, versioning, and cursor pagination.

## Creating an order — RIGHT

```
POST /v1/orders
Headers:
  Content-Type: application/json
  Idempotency-Key: 00000000-0000-4000-8000-000000000001   // client-generated, required for this endpoint

Request body:
{
  "customer_id": "cust_9f8a1c",
  "items": [
    { "sku": "SKU-1001", "quantity": 2 },
    { "sku": "SKU-1002", "quantity": 1 }
  ],
  "shipping_address_id": "addr_44d1"
}

Success response: 201 Created
{
  "id": "ord_7e2b1a90",
  "status": "pending",
  "customer_id": "cust_9f8a1c",
  "items": [
    { "sku": "SKU-1001", "quantity": 2, "unit_price_cents": 1999 },
    { "sku": "SKU-1002", "quantity": 1, "unit_price_cents": 4999 }
  ],
  "total_cents": 8997,
  "created_at": "2026-07-01T14:22:01.345Z"
}
```

Server behavior: the server stores `Idempotency-Key` scoped to the customer/API-key and, on a
retried request with the same key, returns the original `201` response body unchanged instead of
creating a second order, even if the retry arrives after the first request already succeeded.

### Same endpoint — WRONG (no idempotency key)

```
POST /v1/orders
Headers:
  Content-Type: application/json
  // no Idempotency-Key: a network timeout + client retry now creates two separate orders,
  // double-charging the customer with no way for the server to know the second request was a retry
```

## Error contract — RIGHT (versioned, explicit shape)

```
Response: 422 Unprocessable Entity
{
  "error": {
    "type": "validation_error",
    "code": "invalid_sku",
    "message": "SKU-1002 does not exist in catalog",
    "field": "items[1].sku",
    "api_version": "v1",
    "request_id": "req_3fa8c1"
  }
}
```

Every error response carries the same envelope (`type`, `code`, `message`, `api_version`,
`request_id`) regardless of endpoint: clients write one error-parsing path, not one per endpoint.

### Same failure — WRONG (unversioned, inconsistent shape)

```
Response: 400 Bad Request
{ "msg": "bad sku" }
// no machine-readable code, no field pointer, no api_version, no request_id:
// client cannot branch on error type or correlate with server logs
```

## Breaking change example — RIGHT (versioned with migration path)

```
// v1 (existing): "items[].quantity" is required to be a positive integer
GET /v1/orders/ord_7e2b1a90
{ "id": "ord_7e2b1a90", "items": [{ "sku": "SKU-1001", "quantity": 2 }] }

// v2 (breaking): quantity moves under a "line" object to support fractional units (e.g. weight-based SKUs)
GET /v2/orders/ord_7e2b1a90
{ "id": "ord_7e2b1a90", "items": [{ "sku": "SKU-1001", "line": { "quantity": 2, "unit": "each" } }] }

// every v1 response carries deprecation headers until sunset
Deprecation: true
Sunset: 2027-01-01
Link: </v2/orders>; rel="successor-version"
```

### Same change — WRONG (breaking change shipped silently, no version bump)

```
// "quantity" restructured in place on the existing /v1/orders/{id} endpoint
// every v1 client parsing items[].quantity as an integer now gets a KeyError/undefined:
// no Deprecation header, no Sunset date, no migration guide, discovered only when clients start failing in production
```

## Paginated list endpoint — RIGHT

```
GET /v1/orders?cursor=eyJpZCI6Im9yZF83ZTJiMWE5MCJ9&page_size=25

Response: 200 OK
{
  "data": [
    { "id": "ord_7e2b1a90", "status": "pending", "total_cents": 8997 },
    { "id": "ord_6a1c0f21", "status": "shipped",  "total_cents": 4200 }
  ],
  "next_cursor": "eyJpZCI6Im9yZF82YTFjMGYyMSJ9",
  "has_more": true,
  "page_size": 25
}
```

The cursor (`eyJpZCI6...`) is an opaque, base64-encoded token; clients must not decode or
construct it themselves. `has_more` is returned explicitly rather than inferred.

### Same endpoint — WRONG (offset pagination mixed with cursor semantics, opaque contract broken)

```
GET /v1/orders?offset=50&limit=25

Response: 200 OK
{
  "data": [ ... ],
  "cursor": 75   // client now sees a raw integer offset as a "cursor" and starts
                 // constructing cursor=100, cursor=125 itself — internal state (row offsets)
                 // leaked through a field that was supposed to be opaque, and inserts/deletes
                 // between requests will now skip or duplicate rows
}
```
