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

```typescript
// register global handler in main entry point
process.on('unhandledRejection', (reason) => {
    log.error('unhandled promise rejection', { reason });
    process.exit(1);
});
```

## 5. Retry with Exponential Backoff

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
        minTimeout: config.backoffMs[0],
        maxTimeout: config.backoffMs[config.backoffMs.length - 1],
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

## 6. Structured Logging

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

```typescript
// Log files (pipeline / AI-adjacent jobs)
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

## 7. Runtime Schema Validation

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

## 8. Testing

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

## 9. Centralized Third-Party Client Instantiation

```typescript
// lib/anthropic.ts — instantiated once, imported everywhere
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
