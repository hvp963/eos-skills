# Worked Example — Order Creation Endpoint

Source: illustrates `../SKILL.md` Test Layers table applied to one real feature.

Feature: `POST /api/orders`, creates an order for a customer, validates stock, charges payment,
and returns the created order.

## Layer 1 — Unit (pure function, all dependencies mocked)

Target: `calculate_order_total(line_items, discount_code)`, a pure function with no I/O.

```python
# Happy path
def test_calculate_order_total_applies_percentage_discount():
    line_items = [{"sku": "WIDGET-1", "qty": 2, "unit_price": 10.00}]
    total = calculate_order_total(line_items, discount_code="SAVE10")
    assert total == 18.00  # 20.00 - 10%

# Failure path
def test_calculate_order_total_rejects_expired_discount_code():
    line_items = [{"sku": "WIDGET-1", "qty": 1, "unit_price": 10.00}]
    with pytest.raises(ExpiredDiscountError):
        calculate_order_total(line_items, discount_code="EXPIRED2024")
```
No network, DB, or file I/O; `discount_code` validity is looked up via an injected in-memory
fixture, not a real discount service call.

## Layer 2 — Integration (hits a real test DB)

Target: `OrderRepository.create_order(...)` against a containerized Postgres test instance,
state reset between tests.

```python
# Happy path
def test_create_order_persists_order_and_line_items(test_db):
    order = order_repository.create_order(customer_id="cust_1", line_items=[...])
    fetched = order_repository.get_order(order.id)
    assert fetched.status == "pending"
    assert len(fetched.line_items) == 1

# Failure path
def test_create_order_rolls_back_on_insufficient_stock(test_db):
    seed_stock(test_db, sku="WIDGET-1", quantity=0)
    with pytest.raises(InsufficientStockError):
        order_repository.create_order(customer_id="cust_1", line_items=[{"sku": "WIDGET-1", "qty": 1}])
    assert order_repository.count_orders_for_customer("cust_1") == 0  # no partial row left behind
```
Payment provider is mocked at this boundary (external third-party call); only the DB is real.

## Layer 3 — Contract (validates the API response schema)

Target: the `POST /api/orders` response body against the schema registered in the shared
contract store, run in CI on every build.

```json
// contract: order-created-v2.schema.json
{
  "type": "object",
  "required": ["id", "status", "total", "created_at"],
  "properties": {
    "id": { "type": "string", "pattern": "^ord_" },
    "status": { "enum": ["pending", "confirmed", "failed"] },
    "total": { "type": "number", "minimum": 0 },
    "created_at": { "type": "string", "format": "date-time" }
  }
}
```
Both the order service (producer) and the checkout UI (consumer) test against this same
`order-created-v2.schema.json` artifact; a schema change that isn't reflected on both sides
fails CI before merge.

## Where an AI-evaluation test would apply

If this feature used AI-IDS (e.g. an AI-generated order summary or fraud-risk explanation)
attached to the order, that output would need its own Layer 5 test: versioned fixture orders
fed through the summarizer, asserting schema compliance (summary has required fields) and a
bounded hallucination/violation rate, not an exact string match. Plain order creation as
described above has no AI component, so no AI-evaluation layer applies here.
