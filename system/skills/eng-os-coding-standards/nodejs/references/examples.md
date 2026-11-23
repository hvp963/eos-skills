# Coding Standards — Node.js / TypeScript: Examples

## 1. TypeScript Configuration

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

## 2. Configuration Module

Create `src/config/env.ts`. Parse every env var once at module load through one schema, and export a typed object.

```typescript
// src/config/env.ts
import * as dotenv from 'dotenv';
import { z } from 'zod';

// Load .env when the file exists (local development). dotenv never overrides a variable that is
// already set, so in stage and prod the real environment wins. `.env` is never part of the build artifact.
dotenv.config();

const EnvSchema = z.object({
    // required: startup fails if any is missing or invalid
    EXECUTION_MODE:    z.enum(['dev', 'stage', 'prod']),
    DATABASE_URL:      z.string().min(1),
    SERVICE_API_KEY:   z.string().min(1),
    ANTHROPIC_API_KEY: z.string().min(1),
    SERVICE_NAME:      z.string().min(1),

    // optional, with explicit defaults
    API_TIMEOUT_MS:    z.coerce.number().int().positive().default(5000),
    DB_POOL_SIZE:      z.coerce.number().int().positive().default(10),
    BATCH_SIZE:        z.coerce.number().int().positive().default(100),

    // retries after the first call, per integration area (eng-os-coding-standards-common Standard 5)
    API_NUM_RETRIES:   z.coerce.number().int().min(0).default(2),
    DB_NUM_RETRIES:    z.coerce.number().int().min(0).default(2),
});

// one error at startup lists every missing or invalid variable
const env = EnvSchema.parse(process.env);

export const config = {
    executionMode:   env.EXECUTION_MODE,
    databaseUrl:     env.DATABASE_URL,
    serviceApiKey:   env.SERVICE_API_KEY,
    anthropicApiKey: env.ANTHROPIC_API_KEY,
    serviceName:     env.SERVICE_NAME,
    timeoutMs:       env.API_TIMEOUT_MS,
    poolSize:        env.DB_POOL_SIZE,
    batchSize:       env.BATCH_SIZE,
    apiNumRetries:   env.API_NUM_RETRIES,
    dbNumRetries:    env.DB_NUM_RETRIES,
} as const;
```

Import from `config/env.ts` everywhere. Never call `process.env` at call sites. An unchecked `parseInt` turns `"abc"` into `NaN` without an error, so numeric values go through the schema. The retry timing values (`RETRY_BASE_MS`, `RETRY_CAP_MS`, `RETRY_BUDGET_MS`) are constants, not config: they live in `src/shared/constants/` (`eng-os-coding-standards-common` Standard 3).

## 3. Secrets

```typescript
// correct — validated at startup via requireEnv()
const apiKey = config.serviceApiKey;

// forbidden — hardcoded
const apiKey = 'sk-abc123';

// risky — silent undefined if missing, fails later
const apiKey = process.env.SERVICE_API_KEY;
```

## 4. Error Handling

Define typed error classes. Every external call inside an async function is wrapped and mapped to a typed error. Other errors propagate to the one error-handling middleware or the entry point's handler; do not catch an error only to rethrow it. Every Promise is awaited or has `.catch()`.

```typescript
// errors.ts
export class AppError extends Error {
    constructor(message: string, public readonly code?: string) {
        super(message);
        this.name = 'AppError';
    }
}

// retryable: raised for timeouts, connection resets, and the statuses in eng-os-coding-standards-common Standard 5
export class ServiceUnavailableError extends AppError {
    constructor(message: string, public readonly retryAfterMs?: number) {
        super(message, 'SERVICE_UNAVAILABLE');
        this.name = 'ServiceUnavailableError';
    }
}

// usage: the external call is wrapped, and each failure maps to a typed error (RecordSchema and RecordDto: §7)
const RETRYABLE_STATUSES = new Set([408, 429, 502, 503, 504]);   // eng-os-coding-standards-common Standard 5

async function fetchRecord(recordId: string): Promise<RecordDto> {
    try {
        const response = await client.get(`/records/${recordId}`);
        return RecordSchema.parse(response.data);
    } catch (err) {
        if (isAxiosError(err)) {
            const status = err.response?.status;
            const transient = err.code === 'ECONNABORTED' || err.code === 'ECONNRESET'
                || (status !== undefined && RETRYABLE_STATUSES.has(status));
            if (transient) {
                throw new ServiceUnavailableError(`fetch failed for ${recordId}`,
                    parseRetryAfterMs(err.response?.headers['retry-after']));
            }
        }
        throw new AppError(`fetch failed for ${recordId}`, 'FETCH_FAILED');
    }
}
```

`parseRetryAfterMs` reads either form of `Retry-After` (seconds or an HTTP date) and returns `undefined` when the header is absent.

All Promise chains must include `.catch()` or be inside `async/await` with try/catch. Unhandled promise rejections must be treated as fatal.

```typescript
// register global handler in main entry point
process.on('unhandledRejection', (reason) => {
    log.error('unhandled promise rejection', { reason });
    process.exit(1);
});
```

## 5. Retry with Exponential Backoff

The rule is `eng-os-coding-standards-common` Standard 5; this is its Node form. Retry libraries such as `p-retry` multiply the delay by a random factor (1x to 2x), which is not full jitter, and cannot honor `Retry-After` within the budget, so use this short wrapper. It mirrors the Python loop: same formula, budget, `Retry-After` handling, and count.

One layer owns retry. For a vendor SDK with built-in retry, the SDK owns it: set its retry count and timeout from config (§9) and do not wrap its calls. `callWithRetry` is for clients that do not retry on their own.

```typescript
// src/shared/retry/retry.ts
import { config } from '../../config/env';
import { RETRY_BASE_MS, RETRY_CAP_MS, RETRY_BUDGET_MS } from '../constants';
import { ServiceUnavailableError } from '../errors/errors';
import { log } from '../logging/logger';

const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

export async function callWithRetry<T>(
    operation: () => Promise<T>,
    numRetries: number = config.apiNumRetries,   // retries after the first call
    deadlineMs?: number,                         // the caller's remaining time, when it has one
): Promise<T> {
    const started = performance.now();
    const budget = deadlineMs === undefined ? RETRY_BUDGET_MS : Math.min(RETRY_BUDGET_MS, deadlineMs);
    for (let attempt = 0; ; attempt++) {
        try {
            return await operation();
        } catch (err) {
            // only the typed retryable error is retried; anything else propagates unchanged
            if (!(err instanceof ServiceUnavailableError) || attempt === numRetries) throw err;
            const delay = Math.random() * Math.min(RETRY_CAP_MS, RETRY_BASE_MS * 2 ** attempt); // full jitter
            const wait = Math.max(delay, err.retryAfterMs ?? 0);                                 // honor Retry-After
            if (performance.now() - started + wait > budget) throw err;                         // budget or deadline
            log.warn({ attempt: attempt + 1, delayMs: Math.round(wait), error: err.message }, 'retrying');
            await sleep(wait);
        }
    }
}
```

## 6. Structured Logging

Use `pino` (preferred) or `winston`. Output must be JSON. Level must be driven by `config.executionMode`.

```typescript
// logger.ts
import pino from 'pino';
import { config } from './config';
import { traceContext } from './trace-context';

const levelMap: Record<string, string> = {
    dev:   'debug',
    stage: 'info',
    prod:  'warn',
};

export const log = pino({
    level: levelMap[config.executionMode],   // the mode is validated at startup, so no fallback
    base: {
        service: config.serviceName,
        env: config.executionMode,
    },
    // field names follow the standard record shape: timestamp, level (DEBUG | INFO | WARN | ERROR), message
    timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
    messageKey: 'message',
    formatters: { level: (label) => ({ level: label === 'warn' ? 'WARN' : label.toUpperCase() }) },
    mixin: () => traceContext.getStore() ?? {},   // trace_id and span_id on every line (below)
});

// usage: the trace ids come from the context store, never from the call site
log.info({ recordId }, 'processing started');
log.error({ recordId, error: err.message }, 'fetch failed');
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
Bind the trace context once at the entry point and read it from any depth without passing it
through every function, using `AsyncLocalStorage`. Inbound and outbound context travels as W3C
`traceparent`/`tracestate` through the OpenTelemetry propagator API (`meso/observability.md`,
Trace Correlation); `x-trace-id` is never emitted.

```typescript
// trace-context.ts
import { AsyncLocalStorage } from 'node:async_hooks';
import { context, propagation, trace } from '@opentelemetry/api';

// keys match the standard log record's field names (wire names stay snake_case, ADR-001)
export const traceContext = new AsyncLocalStorage<{ trace_id: string; span_id: string }>();
const tracer = trace.getTracer('order-service');

// at the entry point (HTTP middleware, job start, message consumer)
app.use((req, res, next) => {
    const parent = propagation.extract(context.active(), req.headers);   // reads traceparent
    const span = tracer.startSpan('http.request', undefined, parent);
    const { traceId, spanId } = span.spanContext();
    res.on('finish', () => span.end());
    context.with(trace.setSpan(parent, span), () =>
        traceContext.run({ trace_id: traceId, span_id: spanId }, () => next()));
});

// outbound call: write traceparent and tracestate for the current span
const headers: Record<string, string> = {};
propagation.inject(context.active(), headers);
```

The store follows `await`, timers, and promise chains started inside `run`, so the logger's mixin
(§6) adds `trace_id` and `span_id` to every line. Queue messages carry the same context in their
envelope, written with `propagation.inject`.

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

type RecordDto = z.infer<typeof RecordSchema>;   // not `Record`, which would shadow the built-in type

async function fetchRecord(id: string): Promise<RecordDto> {
    const raw = await client.get(`/records/${id}`);
    return RecordSchema.parse(raw.data);  // throws ZodError if invalid
}
```

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

        // 500 is not retryable (eng-os-coding-standards-common Standard 5), so it maps to AppError, not ServiceUnavailableError
        await expect(fetchRecord('abc-123')).rejects.toBeInstanceOf(AppError);
    });
});
```

## 9. Centralized Third-Party Client Instantiation

```typescript
// right — src/shared/anthropic/client.ts: built once, imported only by repositories
import Anthropic from '@anthropic-ai/sdk';
import { config } from '../../config/env';

export const anthropic = new Anthropic({
    apiKey: config.anthropicApiKey,
    maxRetries: config.apiNumRetries,   // the SDK owns retry (§5); it counts retries after the first call
    timeout: config.timeoutMs,
});
```

```typescript
// src/capabilities/summaries/repositories/summaries.repository.ts: the one layer that calls the SDK
import { anthropic } from '../../../shared/anthropic/client';
import { AppError } from '../../../shared/errors/errors';

export async function createSummary(text: string): Promise<string> {
    try {
        const message = await anthropic.messages.create({ /* model, max_tokens, messages built from text */ });
        return extractText(message);
    } catch (err) {
        // the SDK has already retried; what is left maps to a typed error (§4)
        throw new AppError('summary generation failed', 'SUMMARY_PROVIDER_ERROR');
    }
}
```

```typescript
// src/capabilities/summaries/controllers/summaries.controller.ts: never touches the SDK
export function makeSummariesController(summariesService: SummariesService) {
    return async function handleCreateSummary(req: Request, res: Response): Promise<void> {
        const input = CreateSummarySchema.parse(req.body);           // shape validation: 400
        const summary = await summariesService.summarize(input);     // the service calls the repository
        res.status(201).json(toSummaryView(summary));
    };
}
```

```typescript
// forbidden — every route builds its own client with its own config
// routes/summarize.ts
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// routes/classify.ts
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY, maxRetries: 5 }); // drifted config
```

## 10. Documentation

```typescript
/**
 * Order processing pipeline: transforms raw order events into warehouse records.
 */
```

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

```typescript
// forbidden — restates the code
// multiply price by quantity to get line total
const lineTotal = item.priceCents * item.quantity;

// correct — explains a non-obvious constraint
// stored in cents to avoid floating-point rounding at aggregation boundaries
const lineTotal = item.priceCents * item.quantity;
```
