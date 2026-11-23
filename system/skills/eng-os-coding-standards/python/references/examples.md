# Coding Standards — Python: Examples

## 2. Configuration Module

Create `src/config/env.py`. Load once at startup.

```python
# src/config/env.py
import os

from dotenv import load_dotenv

# Load .env when the file exists (local development). load_dotenv never overrides a variable that
# is already set, so in stage and prod the real environment wins. `.env` is never part of the build artifact.
load_dotenv()

# --- required (no default: startup fails if absent or invalid) ---
EXECUTION_MODE = os.environ.get("EXECUTION_MODE", "")
if EXECUTION_MODE not in ("dev", "stage", "prod"):
    raise EnvironmentError(f"EXECUTION_MODE must be one of dev, stage, prod; got {EXECUTION_MODE!r}")
DATABASE_URL    = os.environ["DATABASE_URL"]          # raises KeyError if missing
SERVICE_API_KEY = os.environ["SERVICE_API_KEY"]
SERVICE_NAME    = os.environ["SERVICE_NAME"]          # the `service` field on every log record

LOG_LEVEL = {"dev": "DEBUG", "stage": "INFO", "prod": "WARN"}[EXECUTION_MODE]

# --- optional (explicit defaults) ---
TIMEOUT_SECS    = float(os.getenv("API_TIMEOUT_SECS", "30.0"))
POOL_SIZE       = int(os.getenv("DB_POOL_SIZE", "10"))
BATCH_SIZE      = int(os.getenv("BATCH_SIZE", "100"))

# --- retries after the first call, per integration area (eng-os-coding-standards-common Standard 5) ---
API_NUM_RETRIES = int(os.getenv("API_NUM_RETRIES", "2"))
DB_NUM_RETRIES  = int(os.getenv("DB_NUM_RETRIES", "2"))
```

The retry timing values (`RETRY_BASE_MS`, `RETRY_CAP_MS`, `RETRY_BUDGET_MS`) are constants, not config: they live in `src/shared/constants/` (`eng-os-coding-standards-common` Standard 3).

Use `pydantic BaseSettings` as an alternative when schema validation on config is required.

## 3. Secrets

```python
import os

# Required secret — fail fast at startup if missing
api_key = os.environ["OPENAI_API_KEY"]  # KeyError surfaces immediately

# Never do this
api_key = "sk-abc123"                   # forbidden — hardcoded secret
api_key = os.getenv("OPENAI_API_KEY")   # risky — returns None silently if missing
```

```python
# startup validation pattern
REQUIRED_SECRETS = ["DATABASE_URL", "SERVICE_API_KEY", "OPENAI_API_KEY"]

def validate_env():
    missing = [k for k in REQUIRED_SECRETS if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")
```

## 4. Error Handling

```python
# define a base exception for this application
class AppError(Exception):
    pass

class ServiceUnavailableError(AppError):
    """Retryable: timeouts, connection resets, and the statuses in eng-os-coding-standards-common Standard 5."""

    def __init__(self, message: str, retry_after_ms: float | None = None):
        super().__init__(message)
        self.retry_after_ms = retry_after_ms

RETRYABLE_STATUSES = {408, 429, 502, 503, 504}   # eng-os-coding-standards-common Standard 5

# wrap all external calls; catch specific types and map them to typed errors
def fetch_data(record_id: str) -> RecordData:
    try:
        response = external_client.get(record_id, timeout=config.TIMEOUT_SECS)
        response.raise_for_status()
        return RecordData.from_json(response.json())   # a dataclass parsed at the boundary
    except requests.HTTPError as e:
        status = e.response.status_code
        if status in RETRYABLE_STATUSES:
            raise ServiceUnavailableError(
                f"fetch failed for {record_id}", parse_retry_after_ms(e.response.headers.get("Retry-After"))
            ) from e
        log.error("http error fetching record", record_id=record_id, status=status)
        raise AppError(f"fetch failed for {record_id}") from e
    except (requests.Timeout, requests.ConnectionError) as e:
        log.warn("transient failure fetching record", record_id=record_id)
        raise ServiceUnavailableError("service timeout or connection reset") from e
```

`parse_retry_after_ms` reads either form of `Retry-After` (seconds or an HTTP date) and returns `None` when the header is absent.

Never use bare `except:` or `except Exception:` without re-raising or a documented reason.

## 5. Retry with Exponential Backoff

The rule is `eng-os-coding-standards-common` Standard 5; this loop is its one Python form, and it mirrors the Node wrapper. `tenacity` is not used, because its wait cannot honor `Retry-After` without a custom wait function. One layer owns retry: a vendor SDK with built-in retry owns its calls (set its retry count from config and do not wrap them).

```python
# src/shared/retry/retry.py
import random
import time

from config import env as config
from shared.constants import RETRY_BASE_MS, RETRY_BUDGET_MS, RETRY_CAP_MS
from shared.errors import ServiceUnavailableError

RETRYABLE = (ServiceUnavailableError, ConnectionError, TimeoutError)

def call_with_retry(operation, num_retries: int = config.API_NUM_RETRIES, deadline_ms: float | None = None):
    """Call `operation`, retrying transient failures per eng-os-coding-standards-common Standard 5.

    Args:
        operation: Zero-argument callable that performs one external call.
        num_retries: Retries after the first call, so at most num_retries + 1 calls.
        deadline_ms: The caller's remaining time in milliseconds, when it has one.

    Returns:
        Whatever `operation` returns.

    Raises:
        The last retryable error once retries, the budget, or the deadline run out; any
        non-retryable error at once.
    """
    budget_ms = RETRY_BUDGET_MS if deadline_ms is None else min(RETRY_BUDGET_MS, deadline_ms)
    started = time.monotonic()
    for attempt in range(num_retries + 1):
        try:
            return operation()
        except RETRYABLE as e:
            if attempt == num_retries:
                raise
            delay_ms = random.uniform(0, min(RETRY_CAP_MS, RETRY_BASE_MS * 2 ** attempt))  # full jitter
            wait_ms = max(delay_ms, getattr(e, "retry_after_ms", None) or 0)              # honor Retry-After
            if (time.monotonic() - started) * 1000 + wait_ms > budget_ms:
                raise                                                                      # budget or deadline
            log.warn("retrying", attempt=attempt + 1, delay_ms=round(wait_ms), error=str(e))
            time.sleep(wait_ms / 1000)
```

## 6. Structured Logging

Use `structlog` (preferred) or stdlib `logging` with a JSON formatter.

```python
import logging

import structlog

from config import env as config

def standard_level(logger, method_name, event_dict):
    # the standard record's level values: DEBUG | INFO | WARN | ERROR
    level = event_dict["level"].upper()
    event_dict["level"] = "WARN" if level == "WARNING" else level
    return event_dict

# configure once at startup (in main or config); field names follow the standard record shape
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,   # adds trace_id and span_id bound at entry
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.stdlib.add_log_level,
        standard_level,
        structlog.processors.EventRenamer("message"),   # structlog's "event" key becomes "message"
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelNamesMapping()[config.LOG_LEVEL]),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger().bind(service=config.SERVICE_NAME, env=config.EXECUTION_MODE)

# usage: the trace ids come from the bound context, never from the call site
log.info("processing started", record_id=record_id)
log.error("fetch failed", record_id=record_id, error=str(e))
```

#### Log Files (pipeline / AI-adjacent jobs)
```python
import logging
import os
from datetime import datetime

from config import env as config

def setup_file_logging(prefix: str, log_dir: str = "logs") -> None:
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")

    for log_type in ["plan", "reasoning", "execution"]:
        handler = logging.FileHandler(f"{log_dir}/{prefix}_{log_type}_{ts}.log")
        handler.setLevel(config.LOG_LEVEL)
        logging.getLogger(f"{prefix}.{log_type}").addHandler(handler)
```

---

#### Trace Context Propagation
Bind `trace_id` and `span_id` once at the entry point and carry them through every call
without threading them through function signatures, using structlog's `contextvars` support.
Inbound and outbound context travels as W3C `traceparent`/`tracestate` through the OpenTelemetry
propagator API (`meso/observability.md`, Trace Correlation); `X-Trace-Id` is never emitted.

```python
import structlog
from opentelemetry import propagate, trace

tracer = trace.get_tracer("order-service")

# at the entry point (request handler, job start, message consumer)
def handle_request(request):
    parent = propagate.extract(request.headers)                      # reads traceparent
    with tracer.start_as_current_span("handle_request", context=parent) as span:
        ids = span.get_span_context()
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            trace_id=format(ids.trace_id, "032x"), span_id=format(ids.span_id, "016x"))
        return process_record(request.record_id)

# anywhere downstream: no trace_id argument needed
log.info("record processed", record_id=record_id)

# outbound call: write traceparent and tracestate for the current span
headers: dict[str, str] = {}
propagate.inject(headers)
```

`contextvars` values follow `asyncio` tasks and thread-pool executors created after the bind,
so the ids survive `await` and `run_in_executor`. Queue messages carry the same context in their
envelope, written with `propagate.inject`.

## 7. Type Annotations

```python
from typing import Optional

# correct: typed parameters and a typed return value (a dataclass, never a bare dict)
def process_record(record_id: str) -> ProcessedRecord:
    ...

def find_user(user_id: str) -> Optional[User]:
    ...

# forbidden — no annotations, and an untyped dict as the result
def process_record(record_id):
    ...
```

Retry is not a parameter of a business function: the repository that makes the external call
wraps it in `call_with_retry` (§5), whose count comes from config.

## 8. Testing

```python
# test_processor.py
import pytest
from unittest.mock import MagicMock, patch
from myapp.processor import process_record
from myapp.errors import AppError

def test_process_record_success():
    mock_client = MagicMock()
    mock_client.get.return_value = {"id": "123", "status": "ok"}

    result = process_record("123", client=mock_client)

    assert result["status"] == "ok"
    mock_client.get.assert_called_once_with("123")

def test_process_record_raises_on_http_error():
    mock_client = MagicMock()
    mock_client.get.side_effect = requests.HTTPError(response=MagicMock(status_code=500))

    with pytest.raises(AppError):
        process_record("123", client=mock_client)
```

## 9. Documentation

```python
"""Order processing pipeline: transforms raw order events into warehouse records."""
```

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
        DatabaseError: If the database call fails after retries.
    """
```

```python
class OrderProcessor:
    """Processes order events and writes enriched records to the warehouse.

    Args:
        db: Database client for order lookups.
        client: Downstream warehouse write client.
    """

    def __init__(self, db: DatabaseClient, client: WarehouseClient):
        self.db = db
        self.client = client
```

```python
# forbidden — restates the code
# multiply price by quantity to get line total
line_total = item.price_cents * item.quantity

# correct — explains a non-obvious constraint
# prices are stored in cents to prevent float rounding errors at aggregation time
line_total = item.price_cents * item.quantity
```

## 10. Object-Oriented Conventions

```python
# domain entity — PascalCase noun
@dataclass
class OrderItem:
    order_id: str
    sku: str

# exception — PascalCase noun ending in Error
class FetchError(Exception):
    pass

class TransientFetchError(FetchError):
    pass
```

```python
# correct — named, typed, enforceable
@dataclass
class CleanedRecord:
    record_id: str
    title: str
    word_count: int

# forbidden — unnamed, untyped dictionary as a domain object
record = {"record_id": "...", "title": "...", "word_count": 0}
```

```python
# correct — order_processor.py owns only order-processing concerns
from lib.order_processor import process_order, OrderItem

# forbidden — utils.py accumulates unrelated helpers from multiple domains
from lib.utils import process_order, validate_record, write_csv, load_config
```

```python
# correct — lower modules do not import from higher modules
# src/capabilities/content_cleaning/repositories/ai_cleaner_repository.py
from config import env as config     # config is a lower dependency

# forbidden — reversed direction
# src/config/env.py
from capabilities.content_cleaning.repositories.ai_cleaner_repository import ...  # config must not depend on a capability
```
