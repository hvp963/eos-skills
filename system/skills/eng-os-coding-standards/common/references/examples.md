# Coding Standards — Common: Examples

Illustrative, language-agnostic pseudocode for each standard in `SKILL.md`.

## 1. Execution Mode

```
EXECUTION_MODE = getenv("EXECUTION_MODE")   // required: no default
if EXECUTION_MODE not in ("dev", "stage", "prod"):
    fail startup: "EXECUTION_MODE must be one of dev, stage, prod"

if EXECUTION_MODE == "dev":    LOG_LEVEL = DEBUG
if EXECUTION_MODE == "stage":  LOG_LEVEL = INFO
if EXECUTION_MODE == "prod":   LOG_LEVEL = WARN
```

## 2. Secrets and Environment Variables

```
API_KEY = getenv("SERVICE_API_KEY")  // required — raise error if absent
TIMEOUT = getenv("SERVICE_TIMEOUT_MS", default="5000")  // optional with default
```

## 3. Constants and Configuration

```
// constants module: fixed per release, identical in every environment
RETRY_BASE_MS    = 100
RETRY_CAP_MS     = 10000
RETRY_BUDGET_MS  = 30000

// config module: environment-derived or deployment-tunable
API_NUM_RETRIES  = getenv("API_NUM_RETRIES", default=2)    // retries after the first call
API_TIMEOUT_MS   = getenv("API_TIMEOUT_MS", default=5000)
BATCH_SIZE       = getenv("BATCH_SIZE", default=100)        // tuned by operators (runbook), so config
```

User-facing strings (labels, messages, headings) are constants too, sectioned by app area. Every
success/warning/info/error message additionally carries a unique `{AREA}{NNNNNN}` code (3-letter
area, 6-digit sequence: sized for enterprise-scale growth, not a small project's minimum), assigned
once and never reused. The 6-digit sequence is **one counter shared across the whole project**,
not restarted per area, so `ROT` (Rotations) and `ENG` (Engineers) messages interleave in one
sequence based on creation order, not two independent `000001`-starting series:

```
// src/shared/constants/rotations.ts
export const ROTATIONS_LABELS = {
    PAGE_TITLE:      "Rotations",
    CREATE_BUTTON:   "New Rotation",
}
export const ROTATIONS_MESSAGES = {
    SAVE_SUCCESS:    { code: "ROT000001", text: "Rotation saved." },
    SAVE_ERROR:      { code: "ROT000002", text: "Could not save rotation. Try again." },
    DELETE_CONFIRM:  { code: "ROT000004", text: "Delete this rotation? This cannot be undone." },
    SERVICE_RETIRED: { code: "ROT000005", text: "This service is retired. Choose an active service." },
}

// src/shared/constants/engineers.ts — created between ROT000002 and ROT000004 above, so it takes the
// ROT000003 slot's place in the sequence
export const ENGINEERS_MESSAGES = {
    CONTACT_INVALID: { code: "ENG000003", text: "Enter a valid phone number or email." },
}

// forbidden — literal strings inline in a component, messages with no code, or an area
// restarting its own sequence at 000001 instead of taking the next project-wide number
function RotationPage() {
    return <h1>Rotations</h1>  // should read ROTATIONS_LABELS.PAGE_TITLE
}
showToast("Rotation saved.")   // should read ROTATIONS_MESSAGES.SAVE_SUCCESS (code + text)
```

## 4. Error Handling

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

## 5. Retry Logic

```
// constants: RETRY_BASE_MS = 100, RETRY_CAP_MS = 10_000, RETRY_BUDGET_MS = 30_000
// config:    {AREA}_NUM_RETRIES, default 2 (retries after the first call)

function callWithRetry(operation, numRetries = config.{AREA}_NUM_RETRIES, deadlineMs = none):
    started = monotonicNow()
    budget  = min(RETRY_BUDGET_MS, deadlineMs) if deadlineMs else RETRY_BUDGET_MS
    for attempt in range(numRetries + 1):            // the first call plus numRetries retries
        try:
            return operation()
        catch ServiceUnavailableError as e:          // timeouts, resets, 408, 429, 502, 503, 504
            if attempt == numRetries: raise
            delay = random(0, min(RETRY_CAP_MS, RETRY_BASE_MS * 2^attempt))   // full jitter
            wait  = max(delay, e.retryAfterMs or 0)                          // honor Retry-After
            if elapsedMs(started) + wait > budget: raise                     // budget or deadline reached
            log.warn("retrying", attempt=attempt+1, delay_ms=wait, error=e)
            sleep(wait)
        // any other error is non-retryable and propagates immediately
```

## 6. Structured Logging

```
// trace_id and span_id were bound once at the entry point; the logger adds them, with
// timestamp, level, message, and service, to every record
log.info("processing started", order_id=order.id, item_count=order.items.length)

// never
console.log("processing " + order.id)   // unstructured, no level, no trace_id
```
- Failure mode: unstructured log lines can't be filtered by level or correlated by `trace_id` across services, so incident response falls back to manual grepping.

## 7. No Hardcoding

| Hardcoded (forbidden) | Correct |
|---|---|
| `url = "https://api.prod.example.com"` | `url = getenv("SERVICE_URL")` |
| `timeout = 30` | `timeout = config.API_TIMEOUT_MS` |
| `retries = 3` | `retries = config.API_NUM_RETRIES` (default 2, set in the config module) |
| `key = "sk-abc123"` | `key = getenv("OPENAI_API_KEY")` |

## 8. Default Values

```
// required — no default; startup fails if absent
DB_URL = getenv("DATABASE_URL")

// optional — explicit default
POOL_SIZE    = int(getenv("DB_POOL_SIZE", "10"))
TIMEOUT_SECS = float(getenv("API_TIMEOUT_SECS", "30.0"))
```

## 9. Testing Baseline

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

## 10. Security Baseline

```
// forbidden — raw input passed directly to query and logged with token
function lookupUser(request):
    log.info("lookup", token=request.auth_token)              // logs secret
    return db.query("SELECT * FROM users WHERE id = " + request.user_id)  // injection

// correct — validate first, parameterize query, exclude secrets from logs
function lookupUser(request):
    if not isUUID(request.user_id):
        raise ValidationError("invalid user_id format")

    log.info("lookup", user_id=request.user_id)               // no secret in log
    return db.query("SELECT * FROM users WHERE id = ?", [request.user_id])  // parameterized
```

## 11. Documentation Baseline

```
// forbidden — describes what, not why
// loop through all items and add to total
total = sum(item.price for item in items)

// correct — explains a non-obvious constraint
// prices are stored in cents to avoid floating-point drift; divide only at display time
total_cents = sum(item.price_cents for item in items)
```

The content is uniform across languages (purpose, every parameter, the return value, every raised
error); the tag syntax is per-language, per `docs/decisions/ADR-002-python-docstring-style.md`.

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

## 13. Capability-Based MVCS Layering

```
// forbidden: business logic, persistence, and rendering in the route handler
function handleCreateRotation(request, response):
    if len(request.body.name) < 3: throw ValidationError("name too short")
    rotation = db.insert("rotations", { name: request.body.name, service_id: request.body.service_id })
    response.send("<div>Created rotation " + rotation.name + "</div>")

// correct: each layer does one job; the service receives its repository
// rotations/models/rotation.ts
type Rotation = { id, name, serviceId }

// rotations/repositories/rotation-repository.ts
function insertRotation(tx, input): Rotation
    return tx.insert("rotations", { name: input.name, service_id: input.serviceId })
function findService(tx, serviceId): Service | null
    return tx.selectOne("services", { id: serviceId })

// rotations/services/rotation-service.ts: owns the business rules and the transaction boundary
function createRotation(input, rotationRepository, runInTransaction):
    return runInTransaction(tx =>
        service = rotationRepository.findService(tx, input.serviceId)
        if service is null or service.retired:
            throw BusinessRuleError(ROTATIONS_MESSAGES.SERVICE_RETIRED)   // business rule: 422
        return rotationRepository.insertRotation(tx, input))

// rotations/views/rotation-view.ts
function toRotationResponse(rotation):
    return { id: rotation.id, name: rotation.name }          // whitelist

// rotations/controllers/rotation-controller.ts: never sees a transaction
function handleCreateRotation(request, response):
    input = parseCreateRotation(request.body)                 // shape validation (name 3 to 80 chars): 400
    rotation = rotationService.createRotation(input)          // repository and transaction runner injected
    response.status(201).send(toRotationResponse(rotation))   // view
```

The fixed layout, one tree per transport, and the composition-root wiring are in `mvcs-layout.md`.
