# Testing Strategy

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for designing a layered test suite that provides confidence in correctness, contracts, and system behavior.

### What This Is Not
- not a tool tutorial (pytest, jest, etc.)
- not a QA process guide
- not a metric target (coverage %): coverage is a proxy, not a goal

## Scope
- Level: Meso
- Applies To: All services, pipelines, APIs, and AI-adjacent code
- See Also: `micro/coding-standards/common.md`; testing baseline requirements
- See Also: `meso/observability.md`; AI output metrics and evaluation signals

---

## Applied Principles

### Explicitness Over Implicitness
Test behavior must be explicitly defined. Contracts between producers and consumers must be machine-verified, not assumed. Thresholds and pass/fail criteria must be stated, not left to judgment.

### Validation at Boundaries
Tests validate correctness at the points where behavior, contracts, and data cross meaningful boundaries: service boundaries, schema boundaries, AI output boundaries.

### Determinism Within Defined Boundaries
Tests must produce the same result on every run. Property tests require fixed seeds. AI evaluation tests structural and behavioral properties, not exact string output, because the determinism boundary for AI is structural equivalence, not verbatim reproduction.

### Contracts as Source of Truth
Producer/consumer schema agreements are specification artifacts. Contract tests verify them automatically on every build; they are not assumed to be stable.

---

## Testing Principles

These rules govern how tests are designed within the layer model above.

**Test behavior, not implementation.** Tests verify what a function does, not how it is internally structured. Implementation can change; behavior contracts should not.

**Fast feedback first.** Unit tests run in milliseconds. Integration tests run in seconds. Tests that block the commit loop will be skipped.

**Mock at the boundary, not inside.** Mock external dependencies at the point they cross a system boundary. Do not mock internal helpers: that hides real failures.

**AI outputs are probabilistic; evaluate properties.** AI test assertions check structural properties and behavioral invariants, not exact strings. Exact-string assertions track model verbatim, not model quality.

---

## Test Layers

### Layer 1 — Unit Tests

Scope: one function or class. All external dependencies mocked.

```
test "processOrder returns fulfilled status on valid input":
    mockInventory = stub(checkStock: returns TRUE)
    mockPayment   = stub(charge: returns { status: "ok", txn_id: "abc" })

    result = processOrder(order=validOrder, inventory=mockInventory, payment=mockPayment)

    assert result.status == "fulfilled"
    assert result.txn_id == "abc"
    mockPayment.charge.assert_called_once_with(amount=validOrder.total)

test "processOrder raises InsufficientStockError when stock check fails":
    mockInventory = stub(checkStock: returns FALSE)
    mockPayment   = stub()

    assert_raises InsufficientStockError:
        processOrder(order=validOrder, inventory=mockInventory, payment=mockPayment)

    mockPayment.charge.assert_not_called()
```

Requirements:
- every public function has at least one happy-path and one failure-path test
- no real network calls, no real database writes, no file I/O
- tests are deterministic: same output every run

#### Failure Mode
A test suite that calls real APIs runs slowly, fails intermittently, and couples test reliability to external service availability.

---

### Layer 2 — Integration Tests

Scope: multiple components operating together against real (or containerized) dependencies.

```
test "order pipeline writes to database and emits event on success":
    // uses real test database and real event bus (containerized)
    db     = testDatabase()
    events = testEventBus()

    result = runOrderPipeline(order=validOrder, db=db, events=events)

    dbRecord = db.query("SELECT * FROM orders WHERE id = ?", validOrder.id)
    assert dbRecord.status == "fulfilled"

    emittedEvents = events.drain()
    assert len(emittedEvents) == 1
    assert emittedEvents[0].type == "order.fulfilled"
```

Requirements:
- real components, controlled boundary: no calls to external third-party services
- database and message bus state reset between tests
- verify end-to-end behavior, not just internal state

#### Failure Mode
Integration tests that share mutable state between test cases produce order-dependent failures that are difficult to diagnose.

---

### Layer 3 — Contract Tests

Scope: producer/consumer schema agreement. Runs without both services running simultaneously.

```
// producer side — assert the schema it publishes matches the registered contract
test "order-service publishes OrderFulfilled event matching registered contract":
    event = buildOrderFulfilledEvent(order=sampleOrder)
    assertMatchesContract("order-service", "OrderFulfilled", event)

// consumer side — assert the consumer can parse what the producer claims to emit
test "fulfillment-service can parse OrderFulfilled contract":
    contractPayload = loadContractFixture("order-service", "OrderFulfilled")
    parsed = FulfillmentService.parseOrderEvent(contractPayload)
    assert parsed.order_id is not null
    assert parsed.status == "fulfilled"
```

Requirements:
- contracts registered in a shared schema store (file-based or registry)
- both producer and consumer tests run against the same registered contract artifact
- contract tests run in CI on every build

#### Failure Mode
Assuming contracts are stable without verifying them means a producer change silently breaks a consumer in a different service, often discovered only in production.

---

### Layer 4 — Behavioral / Property Tests

Scope: invariants and edge cases across a range of generated inputs.

```
// property: output total always equals sum of line items, regardless of input
property "order total equals sum of line item prices":
    for each generated order in generateOrders(count=500):
        result = calculateTotal(order)
        expected = sum(item.price * item.quantity for item in order.items)
        assert result.total == expected

// property: serialization roundtrip preserves all fields
property "record serializes and deserializes without data loss":
    for each generated record in generateRecords(count=200):
        serialized   = serialize(record)
        deserialized = deserialize(serialized)
        assert record == deserialized
```

Use when:
- the function must hold an invariant across all valid inputs
- edge cases are hard to enumerate manually (numeric ranges, unicode, boundary values)
- a correctness property can be stated more easily than a specific expected output

#### Failure Mode
Property tests without a fixed random seed produce non-reproducible failures that are difficult to reproduce in CI.

---

### Layer 5 — AI Evaluation

Scope: AI pipeline outputs. Evaluate structural properties and behavioral invariants, not exact strings.

```
evaluation "keyword_gen produces valid keyword records":
    outputs = runPipeline(inputs=evaluationSet, model=currentModel)

    for each output in outputs:
        assert OutputSchema.isValid(output)           // structural: schema compliance
        assert output.keywords is not empty           // behavioral: non-empty result
        assert len(output.keywords) <= MAX_KEYWORDS   // behavioral: within bounds

    schemaPassRate = count(valid) / count(outputs)
    assert schemaPassRate >= 0.95                     // aggregate threshold
```

Metrics to track (do not redefine: see `meso/observability.md`):
- schema compliance rate
- violation rate by category
- output variance across equivalent inputs
- latency and token cost per call

Requirements:
- evaluation inputs are versioned fixtures, not live production data
- thresholds are explicit and documented
- evaluation runs on every model change or prompt change
- regressions block promotion to stage

#### Failure Mode
Evaluating AI output against exact expected strings fails on equivalent paraphrases and creates a maintenance burden as models improve.

---

### Layer 6 — Load and Soak Tests

**Scope:** the whole system, or one service with its real dependencies, under synthetic traffic
shaped like production.

**Rules:**
- load targets come from the project's Scale Targets (peak requests per second, largest tenant,
  data volume); a load test with no stated target is a demo, not a test
- run at least: a step test to the stated peak, a spike test to twice the peak, and a soak at
  sustained expected load for long enough to expose leaks (hours, not minutes)
- pass criteria are the latency and error-rate SLOs; a run that stays up but breaches p99 fails
- run in stage against production-shaped data volume before any launch that changes the
  traffic profile, and on a schedule thereafter; never for the first time in production

- Failure mode: a system that passed every unit and integration test falls over at a tenth of
  its launch traffic because the first real load it ever saw was the launch.

### Flaky Test Policy

A test that fails intermittently on unchanged code is quarantined the same day: moved to a
separate, non-blocking suite with an owner and a fix-by date, and never retried-until-green in
the main pipeline. A quarantined test older than two weeks is either fixed or deleted.

- Failure mode: retry-on-failure in CI hides real intermittent bugs (race conditions, order
  dependence) behind green builds and teaches the team to ignore red ones.

## Test Pyramid

```
     [Load / Soak Tests]           — run in stage before launch and on a schedule
         [AI Evaluation]         — run on model/prompt change
        [Property Tests]         — run in CI; seed-fixed
      [Contract Tests]           — run in CI every build
    [Integration Tests]          — run in CI on branch merge
  [Unit Tests]                   — run in CI on every commit
```

Invert the pyramid (many integration tests, few unit tests) and the suite becomes slow, fragile, and expensive to maintain.

---

## Failure Modes

- mocking internal helpers instead of boundary dependencies hides real integration failures
- integration tests with shared mutable state produce order-dependent, non-reproducible failures
- contract assumptions not machine-verified break silently across service boundaries
- AI evaluations against exact strings fail on equivalent outputs and track model verbatim, not model quality
- property tests without a fixed random seed fail non-reproducibly in CI
- no load test against the stated Scale Targets, so the first real load the system sees is the launch
- flaky tests retried until green in CI hide real race conditions and erode trust in every red build

---

## Definition of Done

Testing strategy is complete when:
- every public function has at least one happy-path and one failure-path unit test
- unit tests mock only at the external boundary and make no real network calls
- integration tests use real components in a controlled, reset environment
- producer/consumer schema contracts are machine-verified in CI
- AI evaluation asserts structural and behavioral properties with explicit thresholds
- the test suite runs in CI on every commit with a defined pass/fail gate
- load, spike, and soak tests run in stage against the Scale Targets before launch and on a schedule, with SLO-based pass criteria
- flaky tests are quarantined to a non-blocking suite with an owner and fix-by date; no retry-until-green in the main pipeline
