# MVCS Layout Reference

Companion to `eng-os-coding-standards-common` Standard 13. The standard states the rules; this file
shows the fixed layout, one tree per transport, and how the layers are wired together. The layout is
the same for every project: all five layer folders exist for every capability from its first file.

## Fixed layout

```
src/
  main | server           Entry point: starts the process, nothing else
  app                     Composition root: builds repositories, injects them into services,
                          mounts controllers. The only module that wires layers together
  config/                 env (all environment variables read here), database (pool setup)
  capabilities/
    <capability>/
      controllers/        Binding + shape validation, one service call, one view call
      services/           Business rules, orchestration, transaction boundary
      repositories/       All data access
      models/             Record structures and domain types
      views/              Output shapes (whitelisted fields)
  workflows/              Orchestration across two or more capabilities
  shared/                 errors/, middleware/, events/, constants/, views/, styles/, and one named
                          module per shared concern (dates/, retry/); never utils/  (used by 2+ capabilities)
database/                 schema.sql, migrations/, seed.sql
tests/                    Mirrors src/ layer for layer
```

## One tree per transport

HTTP API (`orders` capability):

```
src/capabilities/orders/
  controllers/orders.controller.ts      POST /orders -> createOrder; validates body with a schema
  services/orders.service.ts            createOrder(input, ordersRepository)
  repositories/orders.repository.ts     insertOrder(tx, record); findOrder(tx, id)
  models/orders.model.ts                Order, NewOrder
  views/orders.view.ts                  toOrderResponse(order): whitelisted fields only
```

Worker consuming a queue (`shipments` capability):

```
src/capabilities/shipments/
  controllers/shipments_controller.py   subscribes to "order.paid"; validates the message shape
  services/shipments_service.py         schedule_shipment(message, shipments_repository)
  repositories/shipments_repository.py  insert_shipment(tx, record)
  models/shipments_model.py             Shipment, NewShipment
  views/shipments_view.py               to_shipment_event(shipment): outbound payload, whitelisted
```

CLI (`reports` capability): `controllers/` holds the command handler, `views/` holds terminal
output formatting, the other three folders are unchanged.

UI application (`checkout` capability): `controllers/` holds the page handler and any controller hook, `views/` holds the components. The four-region app shell and components used on two or more pages live in `shared/views/shell/` and `shared/views/components/`. `repositories/` holds the API client or local-store access for the capability, injected into its services like any other repository.

```
src/capabilities/checkout/
  controllers/checkout.page.tsx        serves /checkout: reads ?step= and ?coupon=, resolves them with
                                       checkoutSelection(), passes step, onStepChange, onApplyCoupon down
  controllers/useCartPolling.ts        a hook that fetches through a client service: controller work
  services/checkout.service.ts         checkoutSelection(): unknown step falls back to the first
  services/checkout-client.service.ts  browser-side fetch wrappers, injected like a repository
  views/CheckoutSteps.tsx              receives step and callbacks; holds only which panel is hovered
  views/OrderSummary.tsx               PascalCase component; renders props
  views/checkout.view.ts               output shape, if the page also serves an API
```

## Wiring: the composition root

The service receives its repository and a transaction runner; it never builds either. `app` is the only place they are named. The service owns the transaction boundary: it opens the transaction, and controllers never see one. An empty order is a shape error, rejected by the controller's schema with a 400; the service checks the business rule (enough stock) and makes the stock reservation and the order insert one atomic unit.

```typescript
// src/capabilities/orders/services/orders.service.ts
export function makeOrdersService(ordersRepository: OrdersRepository, runInTransaction: TransactionRunner) {
  return {
    async createOrder(input: NewOrder): Promise<Order> {
      return runInTransaction(async (tx) => {
        // conditional decrement: UPDATE stock SET qty = qty - :n WHERE sku = :sku AND qty >= :n
        const reserved = await ordersRepository.reserveStock(tx, input.lineItems)
        if (!reserved) throw new BusinessRuleError(ORDERS_MESSAGES.INSUFFICIENT_STOCK)   // 422; the transaction rolls back
        return ordersRepository.insertOrder(tx, input)
      })
    },
  }
}

// src/app.ts  (composition root)
const ordersService = makeOrdersService(ordersRepository, database.runInTransaction)
mountOrdersRoutes(server, makeOrdersController(ordersService))
```

```python
# src/capabilities/orders/services/orders_service.py
class OrdersService:
    def __init__(self, orders_repository: OrdersRepository, run_in_transaction: TransactionRunner) -> None:
        self._orders_repository = orders_repository
        self._run_in_transaction = run_in_transaction

    def create_order(self, new_order: NewOrder) -> Order:
        with self._run_in_transaction() as tx:
            if not self._orders_repository.reserve_stock(tx, new_order.line_items):
                raise BusinessRuleError(ORDERS_MESSAGES.INSUFFICIENT_STOCK)   # 422; the transaction rolls back
            return self._orders_repository.insert_order(tx, new_order)

# src/app.py  (composition root)
orders_service = OrdersService(OrdersRepository(database_pool), database_pool.run_in_transaction)
register_orders_routes(app, OrdersController(orders_service))
```

A service test passes a fake `OrdersRepository` and a transaction runner that calls its function; no database is involved. That the stock reservation and the insert roll back together is proven once, in the repository tests against a real database.

## Cross-capability calls

| Situation | Where it goes |
|---|---|
| `billing` needs an order's total | `billing` services call `orders` services (the only permitted import across capabilities) |
| An order being paid must start a shipment, with no result needed back | `orders` publishes an event on `shared/events/`; `shipments` subscribes |
| Placing an order must reserve stock and charge a card, and either failure rolls the other back | a workflow in `src/workflows/place-order` coordinating the `inventory` and `billing` services |
| `orders` services and `billing` services would each import the other | move the coordination into a workflow; neither imports the other |

## Reviewer checks

- All five folders exist under every capability, including ones that hold a single file or none yet
- No file in `controllers/` contains a branch on business state or a data-store call
- No file in `services/` imports a request, response, status code, CLI context, or database client
- No `repositories/` file contains a business rule or imports upward
- No import reaches into another capability's `controllers/`, `repositories/`, `models/`, or `views/`
- `app` is the only module that constructs both a repository and the service that receives it
- `tests/` has a file at the mirrored path for every file in `src/`
- No file in `views/` reads or writes a route or query parameter, calls a service, or holds state the page needs after navigation
- Every file name matches the naming rule for its layer folder (the test named in the language skill passes with an empty or shrinking exception list)
