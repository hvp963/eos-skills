# Coding Standards — Node.js / TypeScript

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Node.js/TypeScript-specific implementation of the rules defined in `common.md`.

### What This Is Not
- not a JavaScript guide: TypeScript is required, not optional
- not a replacement for `common.md`: read both
- not a framework tutorial (Express, Fastify, NestJS, etc.)

## Scope
- Level: Micro
- Applies To: All Node.js/TypeScript code in this system
- Prerequisite: `common.md`

---

## 1. TypeScript Configuration

`strict: true` is required in `tsconfig.json`. No exceptions.

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "target": "ES2022",
    "module": "CommonJS",
    "outDir": "dist"
  }
}
```

`any` is forbidden without a documented justification comment. Use `unknown` when the type is genuinely unknown and narrow it explicitly.

---

## 2. Configuration Module

Create `src/config.ts`. Export typed constants. Read env vars once at module load.

```typescript
// src/config.ts
import * as dotenv from 'dotenv';

// load .env in dev only — never in stage or prod
if (process.env.EXECUTION_MODE === 'dev' || !process.env.EXECUTION_MODE) {
    dotenv.config();
}

// --- required (throws at startup if missing) ---
function requireEnv(key: string): string {
    const value = process.env[key];
    if (!value) throw new Error(`Missing required environment variable: ${key}`);
    return value;
}

export const config = {
    executionMode:   process.env.EXECUTION_MODE ?? 'dev',
    databaseUrl:     requireEnv('DATABASE_URL'),
    serviceApiKey:   requireEnv('SERVICE_API_KEY'),

    // optional with explicit defaults
    timeoutMs:       parseInt(process.env.API_TIMEOUT_MS ?? '5000', 10),
    poolSize:        parseInt(process.env.DB_POOL_SIZE ?? '10', 10),
    batchSize:       parseInt(process.env.BATCH_SIZE ?? '100', 10),

    // retry — configurable per area
    apiNumRetries:   parseInt(process.env.API_NUM_RETRIES ?? '3', 10),
    dbNumRetries:    parseInt(process.env.DB_NUM_RETRIES ?? '3', 10),
    backoffMs:       [50, 100, 200, 500] as const,
} as const;
```

Import from `config.ts` everywhere. Never call `process.env` at call sites.

---

## 3. Secrets

```typescript
// correct — validated at startup via requireEnv()
const apiKey = config.serviceApiKey;

// forbidden — hardcoded
const apiKey = 'sk-abc123';

// risky — silent undefined if missing, fails later
const apiKey = process.env.SERVICE_API_KEY;
```

Never commit `.env` files. Use `.env.example` with placeholder values for documentation.

---

## 4. Error Handling

Define typed error classes. All async functions must be wrapped in try/catch.

```typescript
// errors.ts
export class AppError extends Error {
    constructor(message: string, public readonly code?: string) {
        super(message);
        this.name = 'AppError';
    }
}

export class ServiceUnavailableError extends AppError {
    constructor(message: string) {
        super(message, 'SERVICE_UNAVAILABLE');
        this.name = 'ServiceUnavailableError';
    }
}

// usage
async function fetchRecord(recordId: string): Promise<Record<string, unknown>> {
    try {
        const response = await client.get(`/records/${recordId}`);
        return response.data;
    } catch (err) {
        if (isAxiosError(err) && err.response?.status === 503) {
            log.warn('service unavailable', { recordId });
            throw new ServiceUnavailableError(`fetch failed for ${recordId}`);
        }
        log.error('unexpected error fetching record', { recordId, error: err });
        throw err;
    }
}
```

All Promise chains must include `.catch()` or be inside `async/await` with try/catch. Unhandled promise rejections must be treated as fatal.

```typescript
// register global handler in main entry point
process.on('unhandledRejection', (reason) => {
    log.error('unhandled promise rejection', { reason });
    process.exit(1);
});
```

---

## 5. Retry with Exponential Backoff

Use `p-retry` or implement a typed utility. Must use full jitter, a cap, and a total budget per `common.md` Standard 5.

```typescript
import pRetry, { AbortError } from 'p-retry';
import { config } from './config';

async function callWithRetry<T>(
    operation: () => Promise<T>,
    numRetries: number = config.apiNumRetries,
): Promise<T> {
    return pRetry(operation, {
        retries: numRetries,
        factor: 2,
        minTimeout: config.retryBaseMs,   // 100
        maxTimeout: config.retryCapMs,    // 10_000
        randomize: true,                  // full jitter
        maxRetryTime: config.retryBudgetMs, // 30_000 total across attempts
        onFailedAttempt: (error) => {
            log.warn('retrying after failure', {
                attempt: error.attemptNumber,
                retriesLeft: error.retriesLeft,
                error: error.message,
            });
            // abort immediately for non-retryable errors
            if (error.message.includes('401') || error.message.includes('403')) {
                throw new AbortError(error.message);
            }
        },
    });
}
```

---

## 6. Structured Logging

Use `pino` (preferred) or `winston`. Output must be JSON. Level must be driven by `config.executionMode`.

```typescript
// logger.ts
import pino from 'pino';
import { config } from './config';

const levelMap: Record<string, string> = {
    dev:   'debug',
    stage: 'info',
    prod:  'warn',
};

export const log = pino({
    level: levelMap[config.executionMode] ?? 'debug',
    base: {
        service: process.env.SERVICE_NAME ?? 'unknown',
        env: config.executionMode,
    },
    timestamp: pino.stdTimeFunctions.isoTime,
});

// usage — always bind context identifiers
const reqLog = log.child({ traceId: 'abc123', recordId: '456' });
reqLog.info('processing started');
reqLog.error({ error: err.message }, 'fetch failed');
```

Secrets must never appear in log payloads. Sanitize before logging objects that may contain sensitive fields.

#### Log Files (pipeline / AI-adjacent jobs)
```typescript
import pino from 'pino';
import { createWriteStream } from 'fs';
import { mkdirSync } from 'fs';
import { format } from 'date-fns';

function setupFileLogging(prefix: string, logDir = 'logs') {
    mkdirSync(logDir, { recursive: true });
    const ts = format(new Date(), 'yyyyMMddHHmmss');

    return {
        plan:      pino({}, createWriteStream(`${logDir}/${prefix}_plan_${ts}.log`)),
        reasoning: pino({}, createWriteStream(`${logDir}/${prefix}_reasoning_${ts}.log`)),
        execution: pino({}, createWriteStream(`${logDir}/${prefix}_execution_${ts}.log`)),
    };
}
```

---

#### Trace Context Propagation
Bind `traceId` once at the entry point and read it from any depth without passing it through
every function, using `AsyncLocalStorage`:

```typescript
// trace-context.ts
import { AsyncLocalStorage } from 'node:async_hooks';

export const traceContext = new AsyncLocalStorage<{ traceId: string; spanId: string }>();

// at the entry point (HTTP middleware, job start, message consumer)
app.use((req, res, next) => {
    const traceId = req.header('x-trace-id') ?? newTraceId();
    traceContext.run({ traceId, spanId: newSpanId() }, () => next());
});

// logger.ts: mixin reads the store, so every log line carries the ids automatically
export const log = pino({
    mixin: () => traceContext.getStore() ?? {},
});
```

The store follows `await`, timers, and promise chains started inside `run`. Propagate the same
`traceId` on outbound HTTP calls and queue messages in the header or envelope named in
`meso/observability.md`.

## 7. Runtime Schema Validation

Use `zod` or equivalent to validate external data at boundaries (API requests, API responses, events, DB reads).

```typescript
import { z } from 'zod';

const RecordSchema = z.object({
    id:        z.string().uuid(),
    status:    z.enum(['active', 'inactive']),
    createdAt: z.string().datetime(),
    metadata:  z.record(z.string()).optional(),
});

type Record = z.infer<typeof RecordSchema>;

async function fetchRecord(id: string): Promise<Record> {
    const raw = await client.get(`/records/${id}`);
    return RecordSchema.parse(raw.data);  // throws ZodError if invalid
}
```

---

## 8. Testing

Use `jest` or `vitest`. External calls must be mocked in unit tests.

```typescript
// processor.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchRecord } from './processor';
import * as client from './client';

describe('fetchRecord', () => {
    beforeEach(() => { vi.clearAllMocks(); });

    it('returns parsed record on success', async () => {
        vi.spyOn(client, 'get').mockResolvedValueOnce({
            data: { id: 'abc-123', status: 'active', createdAt: '2026-01-01T00:00:00Z' },
        });

        const result = await fetchRecord('abc-123');

        expect(result.id).toBe('abc-123');
        expect(result.status).toBe('active');
    });

    it('throws AppError when service returns 500', async () => {
        vi.spyOn(client, 'get').mockRejectedValueOnce(new Error('500'));

        await expect(fetchRecord('abc-123')).rejects.toThrow();
    });
});
```

---

## 9. Centralized Third-Party Client Instantiation

Do not instantiate a third-party SDK client separately in every route or file that needs it: an AI provider client, a payment SDK, a queue client. Create one module that constructs the client once and export the instance. Every call site imports the shared instance; none of them call the SDK's constructor themselves.

```typescript
// wrong — every route builds its own client with its own config
// routes/summarize.ts
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// routes/classify.ts
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY, maxRetries: 5 }); // drifted config
```

```typescript
// right — lib/anthropic.ts, instantiated once, imported everywhere
import Anthropic from '@anthropic-ai/sdk';
import { config } from '../config';

export const anthropic = new Anthropic({
    apiKey: config.anthropicApiKey,
    maxRetries: config.apiNumRetries,
    timeout: config.timeoutMs,
});
```

```typescript
// routes/summarize.ts
import { anthropic } from '../lib/anthropic';

export async function summarizeHandler(req: Request): Promise<Response> {
    const result = await anthropic.messages.create({ /* ... */ });
    // ...
}
```

---

## 10. Documentation

Use JSDoc for all public functions, classes, and modules: `@param`, `@returns`, `@throws`. TypeScript tooling (the compiler, IDE hover) parses this format natively. Python uses Google-style docstrings instead, per `docs/decisions/ADR-002-python-docstring-style.md`; both languages document the same content (purpose, params, return value, errors), just with per-language syntax.

**Module-level JSDoc**: one sentence at the top of each file:
```typescript
/**
 * Order processing pipeline: transforms raw order events into warehouse records.
 */
```

**Function JSDoc:**
```typescript
/**
 * Returns the total value of an order in cents.
 *
 * @param orderId - The order to retrieve.
 * @param db - Injected database client.
 * @returns Order total in smallest currency unit (cents).
 * @throws {NotFoundError} If no order exists for the given orderId.
 * @throws {DatabaseError} If the database call fails after retries.
 */
async function getOrderTotal(orderId: string, db: DatabaseClient): Promise<number> { ... }
```

**Interface and type JSDoc:**
```typescript
/** Represents a confirmed order ready for fulfillment. */
interface Order {
    /** System-generated UUID. */
    id: string;
    /** Order total in cents; never use floating-point for currency. */
    totalCents: number;
    /** ISO 8601 timestamp in UTC. */
    createdAt: string;
}
```

**Inline comments: why, not what:**
```typescript
// forbidden — restates the code
// multiply price by quantity to get line total
const lineTotal = item.priceCents * item.quantity;

// correct — explains a non-obvious constraint
// stored in cents to avoid floating-point rounding at aggregation boundaries
const lineTotal = item.priceCents * item.quantity;
```

**Do not document:**
- internal single-call helpers whose names are self-explanatory
- constructor bodies when the class JSDoc already describes all properties

---

## Failure Modes

- unhandled promise rejections crash the process silently in older Node; always register a global handler
- `any` types defeat TypeScript's compile-time contract enforcement and hide schema violations
- calling `process.env` at call sites instead of `config.ts` creates configuration drift
- committing `.env` files exposes secrets in version history even after deletion
- missing `.catch()` on a Promise chain that throws causes silent failures
- instantiating a third-party SDK client per-file instead of centrally lets call sites drift out of sync: different retry config, different API version, a forgotten timeout override

---

## Definition of Done

Node.js/TypeScript code meets this standard when:
- `tsconfig.json` has `strict: true`
- `src/config.ts` exists and all env vars are read there
- required env vars throw at startup if missing
- all async functions have try/catch with typed error classes
- retry logic is applied to transient external calls
- all logs use pino/winston JSON format and exclude secrets
- `zod` or equivalent validates external data at boundaries
- tests use jest/vitest with mocked external dependencies
- third-party SDK clients are instantiated once in a shared module and imported, not re-instantiated per route/file
- all public functions, classes, interfaces, and modules have JSDoc
- inline comments explain why, not what
