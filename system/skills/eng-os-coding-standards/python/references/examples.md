# Coding Standards — Python: Examples

## 2. Configuration Module

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
class AppError(Exception):
    pass

class ServiceUnavailableError(AppError):
    pass

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

## 5. Retry with Exponential Backoff

```python
import time
from config import BACKOFF_MS

def call_with_retry(operation, num_retries: int = 3):
    """
    Retry a callable up to num_retries times with exponential backoff.
    Raises on non-retryable errors immediately.
    """
    retryable = (ServiceUnavailableError, ConnectionError, TimeoutError)

    for attempt in range(num_retries):
        try:
            return operation()
        except retryable as e:
            if attempt == num_retries - 1:
                raise
            delay = BACKOFF_MS[min(attempt, len(BACKOFF_MS) - 1)] / 1000
            log.warn("retrying", attempt=attempt + 1, delay_s=delay, error=str(e))
            time.sleep(delay)
        except Exception:
            raise  # non-retryable — surface immediately
```

Using `tenacity`:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(config.API_NUM_RETRIES),
    wait=wait_exponential(multiplier=0.05, min=0.05, max=0.5),
    retry=retry_if_exception_type(ServiceUnavailableError),
)
def call_api(payload: dict) -> dict:
    return client.post(payload)
```

## 6. Structured Logging

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

```python
# Log files (pipeline / AI-adjacent jobs)
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

## 7. Type Annotations

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
# src/ai_cleaner.py
from . import config         # config is a lower dependency

# forbidden — reversed direction
# src/config.py
from .ai_cleaner import ...  # config must not depend on business logic
```
