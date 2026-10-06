# Coding Standards — Python

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Python-specific implementation of the rules defined in `common.md`.

### What This Is Not
- not a Python tutorial or style guide
- not a replacement for `common.md`: read both
- not exhaustive Python best practices

## Scope
- Level: Micro
- Applies To: All Python code in this system
- Prerequisite: `common.md`

---

## 1. Execution Mode

```python
import os

# Read once at module load — never re-read at call sites
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "dev")

LOG_LEVEL_MAP = {
    "dev":   "DEBUG",
    "stage": "INFO",
    "prod":  "WARN",
}
LOG_LEVEL = LOG_LEVEL_MAP.get(EXECUTION_MODE, "DEBUG")
```

---

## 2. Configuration Module

Create `config.py` (or `settings.py`) at the project root. Load once at startup.

```python
# config.py
import os

# --- required (no default — raises at startup if absent) ---
DATABASE_URL    = os.environ["DATABASE_URL"]          # raises KeyError if missing
SERVICE_API_KEY = os.environ["SERVICE_API_KEY"]

# --- optional (explicit defaults) ---
EXECUTION_MODE  = os.getenv("EXECUTION_MODE", "dev")
TIMEOUT_SECS    = float(os.getenv("API_TIMEOUT_SECS", "30.0"))
POOL_SIZE       = int(os.getenv("DB_POOL_SIZE", "10"))
BATCH_SIZE      = int(os.getenv("BATCH_SIZE", "100"))

# --- retry (configurable per area) ---
API_NUM_RETRIES     = int(os.getenv("API_NUM_RETRIES", "3"))
DB_NUM_RETRIES      = int(os.getenv("DB_NUM_RETRIES", "3"))
BACKOFF_MS          = [50, 100, 200, 500]
```

Use `pydantic BaseSettings` as an alternative when schema validation on config is required.

---

## 3. Secrets

```python
import os

# Required secret — fail fast at startup if missing
api_key = os.environ["OPENAI_API_KEY"]  # KeyError surfaces immediately

# Never do this
api_key = "sk-abc123"                   # forbidden — hardcoded secret
api_key = os.getenv("OPENAI_API_KEY")   # risky — returns None silently if missing
```

Validate all required secrets at startup, not on first use.

```python
# startup validation pattern
REQUIRED_SECRETS = ["DATABASE_URL", "SERVICE_API_KEY", "OPENAI_API_KEY"]

def validate_env():
    missing = [k for k in REQUIRED_SECRETS if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")
```

---

## 4. Error Handling

```python
# define a base exception for this application
class AppError(Exception):
    pass

class ServiceUnavailableError(AppError):
    pass

# wrap all external calls; catch specific types
def fetch_data(record_id: str) -> dict:
    try:
        response = external_client.get(record_id, timeout=config.TIMEOUT_SECS)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        log.error("http error fetching record", record_id=record_id, status=e.response.status_code)
        raise AppError(f"fetch failed for {record_id}") from e
    except requests.Timeout as e:
        log.warn("timeout fetching record", record_id=record_id)
        raise ServiceUnavailableError("service timeout") from e
```

Never use bare `except:` or `except Exception:` without re-raising or a documented reason.

---

## 5. Retry with Exponential Backoff

Use `tenacity` or implement a lightweight utility. Must use full jitter, a cap, and a total budget per `common.md` Standard 5.

```python
import random
import time
from config import RETRY_BASE_MS, RETRY_CAP_MS, RETRY_BUDGET_MS

def call_with_retry(operation, num_retries: int = 3):
    """
    Retry a callable up to num_retries times with exponential backoff.
    Raises on non-retryable errors immediately.
    """
    retryable = (ServiceUnavailableError, ConnectionError, TimeoutError)

    started = time.monotonic()
    for attempt in range(num_retries):
        try:
            return operation()
        except retryable as e:
            spent_ms = (time.monotonic() - started) * 1000
            if attempt == num_retries - 1 or spent_ms >= RETRY_BUDGET_MS:
                raise
            # full jitter: random(0, min(cap, base * 2^attempt))
            delay = random.uniform(0, min(RETRY_CAP_MS, RETRY_BASE_MS * 2 ** attempt)) / 1000
            log.warn("retrying", attempt=attempt + 1, delay_s=delay, error=str(e))
            time.sleep(delay)
        except Exception:
            raise  # non-retryable — surface immediately
```

Using `tenacity`:
```python
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_random_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(config.API_NUM_RETRIES) | stop_after_delay(config.RETRY_BUDGET_MS / 1000),
    wait=wait_random_exponential(multiplier=config.RETRY_BASE_MS / 1000, max=config.RETRY_CAP_MS / 1000),  # full jitter
    retry=retry_if_exception_type(ServiceUnavailableError),
)
def call_api(payload: dict) -> dict:
    return client.post(payload)
```

---

## 6. Structured Logging

Use `structlog` (preferred) or stdlib `logging` with a JSON formatter.

```python
import structlog

log = structlog.get_logger()

# configure once at startup (in main or config)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

# usage — always include context identifiers
log.info("processing started", trace_id=trace_id, record_id=record_id)
log.error("fetch failed", trace_id=trace_id, error=str(e))
```

#### Log Files (pipeline / AI-adjacent jobs)
```python
import logging
import os
from datetime import datetime

def setup_file_logging(prefix: str, log_dir: str = "logs") -> None:
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")

    for log_type in ["plan", "reasoning", "execution"]:
        handler = logging.FileHandler(f"{log_dir}/{prefix}_{log_type}_{ts}.log")
        handler.setLevel(LOG_LEVEL)
        logging.getLogger(f"{prefix}.{log_type}").addHandler(handler)
```

---

#### Trace Context Propagation
Bind `trace_id` and `span_id` once at the entry point and carry them through every call
without threading them through function signatures, using `contextvars`:

```python
import contextvars
import structlog

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")

def add_trace_context(logger, method, event_dict):
    event_dict["trace_id"] = trace_id_var.get()
    return event_dict

# configure once: add_trace_context goes before JSONRenderer in the processor list

# at the entry point (request handler, job start, message consumer)
trace_id_var.set(incoming_trace_id or new_trace_id())

# anywhere downstream: no trace_id argument needed
log.info("record processed", record_id=record_id)
```

`contextvars` values follow `asyncio` tasks and thread-pool executors created after the set,
so the id survives `await` and `run_in_executor`. Propagate the same id to outbound HTTP calls
and queue messages in the header or envelope named in `meso/observability.md`.

## 7. Type Annotations

All function signatures must include type hints.

```python
from typing import Optional

# correct
def process_record(record_id: str, retries: int = 3) -> dict:
    ...

def find_user(user_id: str) -> Optional[dict]:
    ...

# forbidden — no annotations
def process_record(record_id, retries=3):
    ...
```

`Any` is a code smell. Use it only with a comment explaining why a more specific type is not possible.

---

## 8. Testing

Use `pytest`. External dependencies must be mocked in unit tests.

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

---

## 9. Documentation

Decided in `docs/decisions/ADR-002-python-docstring-style.md` (Accepted 2026-09-02): Python uses Google-style docstrings (`Args:`, `Returns:`, `Raises:`), parsed natively by Sphinx, pdoc, mkdocstrings, and IDE hover tooling. TypeScript keeps JSDoc tags (`@param`, `@returns`, `@throws`), since the TypeScript compiler and its tooling parse those. The two languages share the same documentation requirement, not the same tag syntax: every public function, class, and module documents its purpose, every parameter, the return value, and every error it can raise (`common.md` Standard 11). Type hints in the signature are the source of truth for types; a docstring does not repeat them.

**Module-level docstring**: one sentence describing the module's purpose:
```python
"""Order processing pipeline: transforms raw order events into warehouse records."""
```

**Function docstring:**
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

**Class docstring**: describe the class purpose and its constructor parameters:
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

**Inline comments: why, not what:**
```python
# forbidden — restates the code
# multiply price by quantity to get line total
line_total = item.price_cents * item.quantity

# correct — explains a non-obvious constraint
# prices are stored in cents to prevent float rounding errors at aggregation time
line_total = item.price_cents * item.quantity
```

**Do not document:**
- internal single-use helpers whose names are self-explanatory
- `__init__` method body when the class docstring already documents the parameters

---

---

## 10. Object-Oriented Conventions

Follow these conventions when organizing classes and modules. For folder-level organization see `micro/project-structure.md`.

**Class naming:**
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

**Dataclasses for value objects:**
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

**One module, one responsibility:**
```python
# correct — order_processor.py owns only order-processing concerns
from lib.order_processor import process_order, OrderItem

# forbidden — utils.py accumulates unrelated helpers from multiple domains
from lib.utils import process_order, validate_record, write_csv, load_config
```

**Dependency direction:**
```python
# correct — lower modules do not import from higher modules
# src/ai_cleaner.py
from . import config         # config is a lower dependency

# forbidden — reversed direction
# src/config.py
from .ai_cleaner import ...  # config must not depend on business logic
```

---

## Failure Modes

- `except Exception: pass` silently swallows all errors and makes debugging impossible
- mutable default arguments (`def f(items=[])`) create shared state across calls
- reading `os.getenv()` at call sites instead of `config.py` causes configuration drift
- using `print()` for logging bypasses log level control and structured output
- missing type hints on public functions break IDE tooling and contract visibility
- `utils.py` catch-all modules accumulate unrelated code and create coupling hubs
- dictionaries used as domain objects lose the contract: use dataclasses instead

---

## Definition of Done

Python code meets this standard when:
- `config.py` exists and all env vars are read there
- required secrets raise `EnvironmentError` at startup if missing
- all external calls use try/catch with specific exception types
- retry logic is applied to transient calls
- all logs use structlog or JSON formatter and exclude secrets
- all public functions have type annotations
- tests use `pytest` with mocked external dependencies
- all public functions, classes, and modules have Google-style docstrings (`Args:`, `Returns:`, `Raises:`)
- inline comments explain why, not what
- classes are PascalCase nouns; exceptions end in `Error`
- dataclasses are used for value objects instead of untyped dictionaries
- no `utils.py` or catch-all modules exist
- project folder layout follows `micro/project-structure.md` with `src/` as the source folder
