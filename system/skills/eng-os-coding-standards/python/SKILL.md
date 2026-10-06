---
name: eng-os-coding-standards-python
description: "Use when writing Python code in a project governed by the Engineering OS: config, error handling, retry, logging, type annotations, testing, docstrings, OOP conventions."
sources:
  - micro/coding-standards/python.md
globs: ["**/*.py"]
always_apply: false
verified_platforms: [claude-code]
---

# Coding Standards — Python

Python-specific implementation of the rules in `eng-os-coding-standards-common`. Load that skill
alongside this one; read both, this file does not restate the "why."

## 1. Execution Mode

```python
import os

# Read once at module load; never re-read at call sites
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "dev")

LOG_LEVEL_MAP = {"dev": "DEBUG", "stage": "INFO", "prod": "WARN"}
LOG_LEVEL = LOG_LEVEL_MAP.get(EXECUTION_MODE, "DEBUG")
```

## 2. Configuration Module

Create `config.py` (or `settings.py`) at the project root. Load once at startup.
- required values: read via `os.environ["KEY"]` (raises `KeyError` if missing); never `os.getenv` for required values
- optional values: `os.getenv("KEY", "default")` with an explicit default
- retry counts: configurable per area, e.g. `API_NUM_RETRIES`, `DB_NUM_RETRIES`
- use `pydantic BaseSettings` as an alternative when schema validation on config is required

## 3. Secrets

- required secret: `api_key = os.environ["OPENAI_API_KEY"]`, fails fast if missing
- forbidden: hardcoded literals (`api_key = "sk-abc123"`)
- risky, avoid: `os.getenv("OPENAI_API_KEY")` for a required secret; returns `None` silently if missing
- validate all required secrets at startup (not on first use) via a `validate_env()` that collects all missing keys and raises `EnvironmentError` once

## 4. Error Handling

- define a base `AppError(Exception)` and specific subclasses (e.g. `ServiceUnavailableError`)
- wrap all external calls; catch specific exception types, log with context, `raise ... from e` to preserve the chain
- never use bare `except:` or `except Exception:` without re-raising or a documented reason

## 5. Retry with Exponential Backoff

Use `tenacity` (`wait_random_exponential` for full jitter, `stop_after_attempt | stop_after_delay` for the budget) or a lightweight utility respecting `RETRY_BASE_MS`, `RETRY_CAP_MS`, `RETRY_BUDGET_MS` from `config.py`. Only retry a defined tuple of retryable exception types; non-retryable exceptions re-raise immediately without consuming a retry attempt.

## 6. Structured Logging

- use `structlog` (preferred) or stdlib `logging` with a JSON formatter, configured once at startup
- always include context identifiers on each call: `log.info("processing started", trace_id=trace_id, record_id=record_id)`
- bind `trace_id` once at the entry point in a `contextvars.ContextVar` and add it through a structlog processor, so no function threads it through its signature; it follows `asyncio` tasks and executors
- for pipeline/AI-adjacent jobs, set up file logging per the `logs/{prefix}_{plan,reasoning,execution}_{timestamp}.log` convention from the common skill

## 7. Type Annotations

All function signatures must include type hints, including return types.
```python
def process_record(record_id: str, retries: int = 3) -> dict: ...
def find_user(user_id: str) -> Optional[dict]: ...
```
`Any` is a code smell; use only with a comment explaining why a more specific type isn't possible. Never leave a signature unannotated.

## 8. Testing

Use `pytest`. Mock/stub all external dependencies in unit tests (`unittest.mock.MagicMock`/`patch`). Cover one happy path and one failure path per public function minimum (see common skill Standard 9).

## 9. Documentation

Google-style docstrings (`Args:`, `Returns:`, `Raises:`), decided in `../../../docs/decisions/ADR-002-python-docstring-style.md`: parsed natively by Sphinx, pdoc, mkdocstrings, and IDE hover, unlike JSDoc tags which nothing in the Python ecosystem understands. TypeScript keeps JSDoc (`eng-os-coding-standards-nodejs`); both languages document the same content, not the same syntax. Type hints in the signature are the source of truth for types; a docstring does not repeat them.

- module-level docstring: one sentence describing the module's purpose
- function docstring: purpose, then `Args:` (one `name: description` line per parameter), `Returns:` (the return value), `Raises:` (one `ErrorType: condition` line per error the function can raise)
- class docstring: purpose, then `Args:` for constructor parameters
- inline comments: why, never what
- do not document internal single-use helpers with self-explanatory names, or `__init__` bodies already covered by the class docstring

## 10. Object-Oriented Conventions

- **class naming:** domain entities are PascalCase nouns (`OrderItem`); exceptions are PascalCase nouns ending in `Error` (`FetchError`, `TransientFetchError`)
- **dataclasses for value objects:** use `@dataclass` for named, typed domain objects; never an untyped dict as a domain object
- **one module, one responsibility:** e.g. `order_processor.py` owns only order-processing concerns; never accumulate unrelated helpers into a `utils.py`
- **dependency direction:** lower modules (e.g. `config.py`) must never import from higher/business-logic modules

See `references/examples.md` for full code samples of each rule above.

## Failure Modes

- `except Exception: pass` silently swallows all errors and makes debugging impossible
- mutable default arguments (`def f(items=[])`) create shared state across calls
- reading `os.getenv()` at call sites instead of `config.py` causes configuration drift
- using `print()` for logging bypasses log level control and structured output
- missing type hints on public functions break IDE tooling and contract visibility
- `utils.py` catch-all modules accumulate unrelated code and create coupling hubs
- dictionaries used as domain objects lose the contract: use dataclasses instead

## Definition of Done

- [ ] `config.py` exists and all env vars are read there
- [ ] required secrets raise `EnvironmentError` at startup if missing
- [ ] all external calls use try/catch with specific exception types
- [ ] retry logic is applied to transient calls
- [ ] all logs use structlog or JSON formatter and exclude secrets
- [ ] all public functions have type annotations
- [ ] tests use `pytest` with mocked external dependencies
- [ ] all public functions, classes, and modules have Google-style docstrings (`Args:`, `Returns:`, `Raises:`)
- [ ] inline comments explain why, not what
- [ ] classes are PascalCase nouns; exceptions end in `Error`
- [ ] dataclasses are used for value objects instead of untyped dictionaries
- [ ] no `utils.py` or catch-all modules exist
- [ ] project folder layout follows `micro/project-structure.md` with `src/` as the source folder
- [ ] `trace_id` is carried in a `ContextVar` from the entry point, not passed through signatures
