# Architecture Decision Record: TypeScript Identifier Casing

**Authors:** Haresh V. Parekh

---

## Metadata

| Field | Value |
|---|---|
| ADR Number | ADR-001 |
| Status | Accepted |
| Date | 2026-09-01 |
| Owner | Haresh V. Parekh |
| Supersedes | none |

## Context

`meso/code-conventions.md` sets `snake_case` as the default for TypeScript variables and
functions, "for consistency with Python," with camelCase permitted when declared project-wide.
Every TypeScript linter preset, framework (React, Next, Express, NestJS), library type
definition, and the language's own standard library use camelCase. A project that adopts the
OS default therefore fights its tooling (`@typescript-eslint/naming-convention` must be
reconfigured), mixes casing at every library boundary (`response.json()` next to
`load_checkpoint()`), and surprises every TypeScript hire. The benefit claimed is
cross-language consistency for teams that switch between Python and TypeScript.

This was an inherited convention, not a recorded decision. The 2026-09-01 architecture review
asked for it to be decided explicitly, whichever way.

## Decision

Change the TypeScript default to camelCase for variables, functions, and
properties, keeping PascalCase for classes and types and UPPER_SNAKE_CASE for constants.
Cross-language consistency is preserved where it matters, at the wire: JSON field names,
database columns, and environment variables stay `snake_case` in both languages, and TypeScript
code maps at the boundary (`zod` transforms or a serializer), which is where the OS already
requires validation.

A project may still declare `snake_case` for TypeScript in its CLAUDE.md; the rule that casing
is declared once and never mixed within a file is unchanged.

Accepted by the Owner on 2026-09-01. `meso/code-conventions.md` and `skills/code-conventions`
carry the new rule; `micro/coding-standards/nodejs.md` examples already use camelCase.

## Side-by-Side Example

The same feature under each option. Wire contract, database columns, env vars, and message codes
are snake_case in both.

### Option A: current rule, snake_case in TypeScript

```typescript
// src/controllers/order-controller.ts
const create_order_request = z.object({
  customer_id: z.string().uuid(),
  line_items: z.array(z.object({ sku: z.string(), quantity: z.number().int() })),
});

export async function handle_create_order(req: Request, res: Response) {
  const parsed = create_order_request.parse(req.body);        // library API is camelCase
  const trace_id = req.header('x-trace-id') ?? crypto.randomUUID();
  const order = await create_order(parsed, trace_id);
  log.info({ order_id: order.id, trace_id }, 'order created');
  res.status(201).json(order);
}

// src/views/pages/OrderPage.tsx
export function OrderPage({ order_id, on_refresh }: { order_id: string; on_refresh: () => void }) {
  const [is_loading, set_is_loading] = useState(false);       // hook API camelCase, our names snake_case
  return <button onClick={on_refresh} disabled={is_loading}>{ORDER_LABELS.REFRESH}</button>;
}
```

```json
"@typescript-eslint/naming-convention": [
  "error",
  { "selector": "variableLike", "format": ["snake_case", "UPPER_CASE"] },
  { "selector": "property", "format": null }
]
```

Every line mixes two casings; React props in snake_case diverge from every component library;
the lint preset is overridden per project.

### Option B: accepted, camelCase in TypeScript, snake_case at the wire

```typescript
// src/controllers/order-controller.ts
const createOrderRequest = z.object({
  customer_id: z.string().uuid(),
  line_items: z.array(z.object({ sku: z.string(), quantity: z.number().int() })),
}).transform(({ customer_id, line_items }) => ({ customerId: customer_id, lineItems: line_items }));

export async function handleCreateOrder(req: Request, res: Response) {
  const input = createOrderRequest.parse(req.body);           // mapped once, at the validated boundary
  const order = await createOrder(input);                     // traceId from AsyncLocalStorage
  log.info({ orderId: order.id }, 'order created');           // mixin adds trace_id
  res.status(201).json(toWire(order));                        // { order_id, customer_id, ... }
}

// src/views/pages/OrderPage.tsx
export function OrderPage({ orderId, onRefresh }: { orderId: string; onRefresh: () => void }) {
  const [isLoading, setIsLoading] = useState(false);
  return <button onClick={onRefresh} disabled={isLoading}>{ORDER_LABELS.REFRESH}</button>;
}
```

```json
"extends": ["plugin:@typescript-eslint/recommended"]
```

One casing per file; the stock lint preset applies; the Python consumer of the API still sees
`customer_id`.

## Consequences

### Accepted Trade-offs
- Python and TypeScript code in the same team read differently at the identifier level.

### Doors Closed
- None; the boundary-mapping rule keeps contracts language-neutral.

### Benefits
- No linter reconfiguration, no casing seams at library calls, standard onboarding.

---

## Alternatives Considered

### Alternative 1: Keep `snake_case` as the default (status quo)

**What it is:** `snake_case` identifiers in TypeScript, as in Python.

**Why rejected:** consistent across languages, but costs tooling friction and library-boundary mixing on every TypeScript project.

### Alternative 2: No default, every project chooses

**What it is:** the OS states no casing default for TypeScript.

**Why rejected:** avoids the argument, but loses the benefit of a default for small projects.

---

## Validation

Revisit if the ecosystem's tooling begins to default to snake_case, or if a project reports
that the boundary mapping is a recurring source of bugs.

## References

- `meso/code-conventions.md`
- Internal architecture review of 2026-09-01 (not published), Section 4 F5 and Section 7 A
