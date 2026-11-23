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

`EXECUTION_MODE` is read once, in the config module (§2), and imported everywhere else. It is required: startup fails if it is unset or not one of `dev`, `stage`, `prod`, and there is no fallback mode (`common.md` Standard 1). The log-level map lives beside it in the config module.

```python
# anywhere outside the config module
from config import env as config

if config.EXECUTION_MODE == "dev":
    ...
```

---

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

# --- retries after the first call, per integration area (common.md Standard 5) ---
API_NUM_RETRIES = int(os.getenv("API_NUM_RETRIES", "2"))
DB_NUM_RETRIES  = int(os.getenv("DB_NUM_RETRIES", "2"))
```

The retry timing values (`RETRY_BASE_MS`, `RETRY_CAP_MS`, `RETRY_BUDGET_MS`) are constants, not config: they live in `src/shared/constants/` (`common.md` Standard 3).

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
    """Retryable: timeouts, connection resets, and the statuses in common.md Standard 5."""

    def __init__(self, message: str, retry_after_ms: float | None = None):
        super().__init__(message)
        self.retry_after_ms = retry_after_ms

RETRYABLE_STATUSES = {408, 429, 502, 503, 504}   # common.md Standard 5

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

---

## 5. Retry with Exponential Backoff

The rule is `common.md` Standard 5; this loop is its one Python form, and it mirrors the Node wrapper. `tenacity` is not used, because its wait cannot honor `Retry-After` without a custom wait function. One layer owns retry: a vendor SDK with built-in retry owns its calls (set its retry count from config and do not wrap them).

```python
# src/shared/retry/retry.py
import random
import time

from config import env as config
from shared.constants import RETRY_BASE_MS, RETRY_BUDGET_MS, RETRY_CAP_MS
from shared.errors import ServiceUnavailableError

RETRYABLE = (ServiceUnavailableError, ConnectionError, TimeoutError)

def call_with_retry(operation, num_retries: int = config.API_NUM_RETRIES, deadline_ms: float | None = None):
    """Call `operation`, retrying transient failures per common.md Standard 5.

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

---

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

All function signatures must include type hints.

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

Decided in `docs/decisions/ADR-002-python-docstring-style.md` (Accepted 2026-09-02): Python uses Google-style docstrings (`Args:`, `Returns:`, `Raises:`), parsed natively by Sphinx, pdoc, mkdocstrings, and IDE hover tooling. TypeScript keeps JSDoc tags (`@param`, `@returns`, `@throws`), since the TypeScript compiler and its tooling parse those. The two languages share the same documentation requirement, not the same tag syntax: every public function, class, and module documents its purpose, every parameter, the return value, and every error it can raise (`common.md` Standard 10). Type hints in the signature are the source of truth for types; a docstring does not repeat them.

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
# src/capabilities/content_cleaning/repositories/ai_cleaner_repository.py
from config import env as config     # config is a lower dependency

# forbidden — reversed direction
# src/config/env.py
from capabilities.content_cleaning.repositories.ai_cleaner_repository import ...  # config must not depend on a capability
```

---

## 11. Capability Layout (MVCS)

Applies `common.md` Standard 13 to Python. The five layer folders per capability, the dependency
direction, and the composition root are defined there and in `project-structure.md` Section 2;
this section adds only the Python specifics.

- **file names:** snake_case `<topic>_<layer>.py`, where the topic is the concept the file is about, not necessarily the capability's name. `_controller.py` is a route or command handler named for the resource (plural for the collection route `/orders`, singular for one item `/orders/{id}`; an uncountable noun keeps one form). `_page.py` is a page handler in a UI framework (Streamlit, NiceGUI, a Flask or Django view serving a template) named for the last segment of the URL it serves (`checkout_page.py` serves `/checkout`). `_service.py`, `_repository.py` and `_model.py` are named for the concept (`orders_service.py`). In `views/` a UI component is `<name>_component.py`, an output shape is `<name>_view.py`, other data or helpers are snake_case `.py` with no layer suffix. Tests are `test_<same name>.py` at the mirrored path
- **page and view (UI):** the page handler (`_page.py`) is the controller. It reads the route or query parameters, resolves them with a service function, owns the state that must survive navigation (the framework's session or page state), and passes data and callbacks to the view. A component in `views/` receives arguments and keeps only presentation state (expanded or collapsed, hover, a draft not yet submitted). It reads no query parameter, calls no service, and holds nothing the page needs after navigation
- **controller:** binds the route or command and validates input with a `pydantic` model, then calls one service
- **service:** a class taking its repositories in `__init__`. It imports no framework request, response, or status code, and raises typed errors from `src/shared/errors/`
- **repository:** the only layer that imports the database driver; parameterized statements only (`%s` or named parameters), never f-string SQL
- **model:** `dataclass` or `pydantic` types, not dictionaries (see `project-structure.md` Section 8)
- **error mapping:** one exception handler registered in `app` translates domain errors (`ValidationError` 400, `NotFoundError` 404, `ConflictError` 409, `BusinessRuleError` 422) to the transport's response and, for HTTP, the one error envelope (`meso/api-design.md`, Error Contract); handlers do not
- **enforcement:** declare the layer order and capability independence in `import-linter` (a `layers` contract for controllers, services, repositories, models, and `independence` or `forbidden` contracts between capabilities, with `services` as the allowed entry) and run it in CI. Add a test that walks `src/capabilities/` and fails on a file whose name breaks the rule for its layer folder, with an exception list that may only shrink

```python
# src/capabilities/orders/controllers/orders_controller.py
class OrdersController:
    def __init__(self, orders_service: OrdersService) -> None:
        self._orders_service = orders_service

    def create_order(self, payload: CreateOrderRequest) -> OrderResponse:   # shape validated by pydantic
        order = self._orders_service.create_order(payload.to_new_order())    # business rules in the service
        return to_order_response(order)                                      # view whitelists the fields
```

#### Failure Mode
A route function that opens a database connection, or a service that imports `fastapi` or `flask`.
An `import-linter` config that exists but is not run in CI.

---

## Failure Modes

- `except Exception: pass` silently swallows all errors and makes debugging impossible
- mutable default arguments (`def f(items=[])`) create shared state across calls
- reading `os.getenv()` at call sites instead of `src/config/env.py` causes configuration drift
- using `print()` for logging bypasses log level control and structured output
- missing type hints on public functions break IDE tooling and contract visibility
- `utils.py` catch-all modules accumulate unrelated code and create coupling hubs
- dictionaries used as domain objects lose the contract: use dataclasses instead
- a route function that opens a database connection, or a service that imports the web framework, defeats the layering that makes services testable without a server or a database

---

## Definition of Done

Python code meets this standard when:

All items are Per change: this domain has no Standing (release and audit) items.

- `src/config/env.py` exists and all env vars are read there, `EXECUTION_MODE` included
- required values raise `EnvironmentError` at startup if missing; an unset or invalid `EXECUTION_MODE` fails startup, with no fallback mode
- all external calls use try/catch with specific exception types
- retry follows `common.md` Standard 5 (full jitter, cap, budget, `Retry-After`, one owning layer)
- all logs use structlog or JSON formatter and exclude secrets
- all public functions have type annotations
- tests use `pytest` with mocked external dependencies
- all public functions, classes, and modules have Google-style docstrings (`Args:`, `Returns:`, `Raises:`)
- inline comments explain why, not what
- classes are PascalCase nouns; exceptions end in `Error`
- dataclasses are used for value objects instead of untyped dictionaries
- no `utils.py` or catch-all modules exist
- project folder layout follows `micro/project-structure.md` with `src/` as the source folder
