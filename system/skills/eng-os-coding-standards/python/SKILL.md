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

`EXECUTION_MODE` is read once, in `src/config/env.py`, and imported everywhere else. It is required:
startup fails if it is unset or not one of `dev`, `stage`, `prod`, with no fallback mode. The
log-level map lives beside it.

```python
# src/config/env.py
EXECUTION_MODE = os.environ.get("EXECUTION_MODE", "")
if EXECUTION_MODE not in ("dev", "stage", "prod"):
    raise EnvironmentError(f"EXECUTION_MODE must be one of dev, stage, prod; got {EXECUTION_MODE!r}")
LOG_LEVEL = {"dev": "DEBUG", "stage": "INFO", "prod": "WARN"}[EXECUTION_MODE]
```

## 2. Configuration Module

Create `src/config/env.py`. Load once at startup.
- `load_dotenv()` loads `.env` when the file exists; it never overrides a variable already set, so in stage and prod the real environment wins; `.env` is never part of the build artifact
- required values: read via `os.environ["KEY"]` (raises `KeyError` if missing); never `os.getenv` for required values
- optional values: `os.getenv("KEY", "default")` with an explicit default
- retry counts: configurable per area, e.g. `API_NUM_RETRIES`, `DB_NUM_RETRIES`, each counting the retries after the first call (default 2); the retry timing values are constants in `src/shared/constants/`
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

The rule is `eng-os-coding-standards-common` Standard 5. Use the one loop in canon §5 (`call_with_retry` in `src/shared/retry/retry.py`): at most `num_retries + 1` calls, full jitter `random.uniform(0, min(RETRY_CAP_MS, RETRY_BASE_MS * 2 ** attempt))`, a wait of the larger of that delay and the error's `retry_after_ms`, and a stop when the wait would pass `RETRY_BUDGET_MS` or the caller's deadline. `RETRY_BASE_MS`, `RETRY_CAP_MS`, and `RETRY_BUDGET_MS` are constants (`src/shared/constants/`). Only retry the defined tuple of retryable exception types (`ServiceUnavailableError`, `ConnectionError`, `TimeoutError`); non-retryable exceptions re-raise immediately without consuming a retry. `tenacity` is not used: its wait cannot honor `Retry-After`. A vendor SDK with built-in retry owns its calls: set its retry count from config and do not wrap them.

## 6. Structured Logging

- use `structlog` (preferred) or stdlib `logging` with a JSON formatter, configured once at startup
- at the entry point, extract the caller's context with the OpenTelemetry propagator (`propagate.extract`, W3C `traceparent`), start a span, and bind `trace_id` and `span_id` once with `structlog.contextvars.bind_contextvars`; the built-in `structlog.contextvars.merge_contextvars` processor adds them to every line, so no function threads them through its signature, and they follow `asyncio` tasks and executors
- call sites pass only the operation's identifiers: `log.info("processing started", record_id=record_id)`; never `trace_id=` at a call site
- outbound calls write `traceparent` with `propagate.inject`; `X-Trace-Id` is never emitted
- for pipeline/AI-adjacent jobs, set up file logging per the `logs/{prefix}_{plan,reasoning,execution}_{timestamp}.log` convention from the common skill

## 7. Type Annotations

All function signatures must include type hints, including return types.
```python
def process_record(record_id: str) -> ProcessedRecord: ...
def find_user(user_id: str) -> Optional[User]: ...
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
- **dependency direction:** lower modules (e.g. `src/config/env.py`) must never import from higher/business-logic modules

See `references/examples.md` for full code samples of each rule above and the MVCS layout reference in `eng-os-coding-standards-common` for the layout.

## 11. Capability Layout (MVCS)

Applies `eng-os-coding-standards-common` Standard 13 to Python. Layers, folders, and dependency
direction are defined there; this section adds only the Python specifics.

- file names are snake_case `<topic>_<layer>.py`, where the topic is the concept the file is about, not necessarily the capability's name:
  - `_controller.py`: a route handler or command handler, topic is the resource; plural for the collection route (`/orders`), singular for one item (`/orders/{id}`); an uncountable noun keeps one form
  - `_page.py`: a page handler in a UI framework (Streamlit, NiceGUI, Flask or Django view serving a template), topic is the last segment of the URL it serves (`checkout_page.py` serves `/checkout`, whichever capability owns it)
  - `_service.py`, `_repository.py`, `_model.py`: topic is the concept (`orders_service.py`)
  - in `views/`: a UI component or template helper is `<name>_component.py`, an output shape is `<name>_view.py`, other data or helpers are snake_case `.py` with no layer suffix
  - tests are `test_<same name>.py` at the mirrored path
- controller: binds the route or command and validates input with a `pydantic` model, then calls one service
- service: a class taking repositories in `__init__`; imports no framework request, response, or status code; raises typed errors from `src/shared/errors/`
- repository: the only layer that imports the database driver; parameterized statements only (`%s` or named parameters), never f-string SQL
- model: `dataclass` or `pydantic` types, not dictionaries
- page and view (UI): the page handler (`_page.py`) is the controller. It reads the route or query parameters, resolves them with a service function, owns the state that must survive navigation (the framework's session or page state), and passes data and callbacks to the view. A component in `views/` receives arguments and keeps only presentation state (expanded or collapsed, hover, a draft not yet submitted). It reads no query parameter, calls no service, and holds nothing the page needs after navigation
- error mapping: one exception handler registered in `app` translates domain errors to the transport's response
- enforcement: declare the layer order and capability independence in `import-linter` (`layers` and `independence` or `forbidden` contracts) and run it in CI; add a test that walks `src/capabilities/` and fails on a file whose name breaks the rule for its layer folder, with an exception list that may only shrink

## Failure Modes

- `except Exception: pass` silently swallows all errors and makes debugging impossible
- mutable default arguments (`def f(items=[])`) create shared state across calls
- reading `os.getenv()` at call sites instead of `src/config/env.py` causes configuration drift
- using `print()` for logging bypasses log level control and structured output
- missing type hints on public functions break IDE tooling and contract visibility
- `utils.py` catch-all modules accumulate unrelated code and create coupling hubs
- dictionaries used as domain objects lose the contract: use dataclasses instead
- a route function that opens a database connection, or a service that imports the web framework, defeats the layering that makes services testable without a server or a database
- a UI component that reads a query parameter, validates it and writes it back, or holds state the page needs after navigation, is a controller written inside a view: it passes the import check and still cannot be reused or tested without rendering

## Definition of Done

All items are Per change: this domain has no Standing (release and audit) items.

- [ ] `src/config/env.py` exists and all env vars are read there, `EXECUTION_MODE` included
- [ ] required values raise `EnvironmentError` at startup if missing; an unset or invalid `EXECUTION_MODE` fails startup, with no fallback mode
- [ ] all external calls use try/catch with specific exception types
- [ ] retry follows `eng-os-coding-standards-common` Standard 5 (full jitter, cap, budget, `Retry-After`, one owning layer)
- [ ] all logs use structlog or JSON formatter and exclude secrets
- [ ] all public functions have type annotations
- [ ] tests use `pytest` with mocked external dependencies
- [ ] all public functions, classes, and modules have Google-style docstrings (`Args:`, `Returns:`, `Raises:`)
- [ ] inline comments explain why, not what
- [ ] classes are PascalCase nouns; exceptions end in `Error`
- [ ] dataclasses are used for value objects instead of untyped dictionaries
- [ ] no `utils.py` or catch-all modules exist
- [ ] every capability has `controllers/`, `services/`, `repositories/`, `models/`, and `views/` with `<topic>_<layer>.py` names, a test fails on a file whose name breaks the rule for its folder, and the layer order and capability independence are enforced by `import-linter` (or equivalent) in CI
- [ ] no file in `views/` reads a route or query parameter, calls a service, or holds state the page needs after navigation
- [ ] project folder layout follows `micro/project-structure.md` with `src/` as the source folder
- [ ] `trace_id` is carried in a `ContextVar` from the entry point, not passed through signatures
