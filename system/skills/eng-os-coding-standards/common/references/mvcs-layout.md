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
  shared/                 errors/, middleware/, events/, utils/  (used by 2+ capabilities)
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

UI application (`rotations` capability): `controllers/` holds the page or route handler, `views/`
holds the page and its components. The four-region app shell and components used on two or more
pages live in `shared/views/shell/` and `shared/views/components/`. `repositories/` holds the API
client or local-store access for the capability, injected into its services like any other
repository.

## Wiring: the composition root

The service receives its repository; it never builds one. `app` is the only place both are named.

```typescript
// src/capabilities/orders/services/orders.service.ts
export function makeOrdersService(ordersRepository: OrdersRepository) {
  return {
    async createOrder(input: NewOrder, tx: Transaction): Promise<Order> {
      if (input.lineItems.length === 0) throw new ValidationError(ORDERS_MESSAGES.EMPTY_ORDER)
      return ordersRepository.insertOrder(tx, input)
    },
  }
}

// src/app.ts  (composition root)
const ordersService = makeOrdersService(ordersRepository)
mountOrdersRoutes(server, makeOrdersController(ordersService))
```

```python
# src/capabilities/orders/services/orders_service.py
class OrdersService:
    def __init__(self, orders_repository: OrdersRepository) -> None:
        self._orders_repository = orders_repository

    def create_order(self, tx: Transaction, new_order: NewOrder) -> Order:
        if not new_order.line_items:
            raise ValidationError(ORDERS_MESSAGES.EMPTY_ORDER)
        return self._orders_repository.insert_order(tx, new_order)

# src/app.py  (composition root)
orders_service = OrdersService(OrdersRepository(database_pool))
register_orders_routes(app, OrdersController(orders_service))
```

A service test passes a fake `OrdersRepository`; no database is involved.

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
