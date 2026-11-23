# Worked Example — Order Creation Endpoint

Source: illustrates `../SKILL.md` Test Layers table applied to one real feature.

Feature: `POST /api/orders`, creates an order for a customer, validates stock, charges payment,
and returns the created order.

## Layer 1 — Unit (pure function, all dependencies mocked)

Target: `calculate_order_total(line_items, discount_code)`, a pure function with no I/O. Money is
integer cents in a typed `LineItem`, never a float.

```python
@dataclass(frozen=True)
class LineItem:
    sku: str
    qty: int
    unit_price_cents: int

# Happy path
def test_calculate_order_total_applies_percentage_discount():
    line_items = [LineItem(sku="WIDGET-1", qty=2, unit_price_cents=1000)]
    total_cents = calculate_order_total(line_items, discount_code="SAVE10")
    assert total_cents == 1800  # 2000 - 10%

# Failure path
def test_calculate_order_total_rejects_expired_discount_code():
    line_items = [LineItem(sku="WIDGET-1", qty=1, unit_price_cents=1000)]
    with pytest.raises(ExpiredDiscountError):
        calculate_order_total(line_items, discount_code="EXPIRED2024")
```
No network, DB, or file I/O; `discount_code` validity is looked up via an injected in-memory
fixture, not a real discount service call.

## Layer 1, Service — the business rule, with a fake repository

Target: `OrdersService.place_order(...)`, which owns the stock rule and the transaction
boundary (`eng-os-coding-standards-common` Standard 13). The test injects a fake repository and a
transaction runner that calls its function, so it needs no database.

```python
# Failure path: not enough stock is a business rule, so the service raises before any insert
def test_place_order_rejects_insufficient_stock():
    repository = FakeOrdersRepository(stock={"WIDGET-1": 0})
    service = OrdersService(repository, run_in_transaction=run_directly)
    with pytest.raises(InsufficientStockError):
        service.place_order(customer_id="cust_1", line_items=[LineItem("WIDGET-1", 1, 1000)])
    assert repository.inserted_orders == []
```

## Layer 2 — Integration (repository against a real test DB)

Target: `OrdersRepository` against a containerized Postgres test instance, inside a transaction
that rolls back after each test (`micro/project-structure.md` Section 7: repository tests are the
integration tests).

```python
# Happy path
def test_insert_order_persists_order_and_line_items(test_db):
    order = orders_repository.insert_order(test_db, customer_id="cust_1",
                                           line_items=[LineItem("WIDGET-1", 1, 1000)])
    fetched = orders_repository.get_order(test_db, order.id)
    assert fetched.status == "pending"
    assert len(fetched.line_items) == 1

# Failure path: a failure inside the service's transaction runner leaves no partial rows
def test_failed_placement_leaves_no_rows(test_db):
    seed_stock(test_db, sku="WIDGET-1", quantity=0)
    service = OrdersService(orders_repository, run_in_transaction=test_db.run_in_transaction)
    with pytest.raises(InsufficientStockError):
        service.place_order(customer_id="cust_1", line_items=[LineItem("WIDGET-1", 1, 1000)])
    assert orders_repository.count_orders_for_customer(test_db, "cust_1") == 0
    assert orders_repository.count_order_items_for_customer(test_db, "cust_1") == 0
```
Payment provider is mocked at this boundary (external third-party call); only the DB is real.

## Layer 3 — Contract (validates the API response schema)

Target: the `POST /api/orders` response body against the schema registered in the shared
contract store, run in CI on every build.

```json
// contract: order-created-v2.schema.json
{
  "type": "object",
  "required": ["id", "status", "total_cents", "created_at"],
  "properties": {
    "id": { "type": "string", "pattern": "^ord_" },
    "status": { "enum": ["pending", "confirmed", "failed"] },
    "total_cents": { "type": "integer", "minimum": 0 },
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
