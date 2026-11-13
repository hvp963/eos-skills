# Project Structure

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Language-agnostic standards for project folder layout, module organization, object-oriented design at the file level, and naming conventions. These standards apply to every project regardless of language, framework, or size.

### What This Is Not
- not a framework-specific scaffold: frameworks impose their own layouts; this standard expresses defaults and the principles behind them
- not class-level or function-level design guidance: that lives in `coding-standards/python.md` and `coding-standards/nodejs.md`
- not a build tooling guide

## Scope
- Level: Micro
- Applies To: All projects regardless of language or runtime
- Prerequisite: `micro/coding-standards/common.md`
- See Also: `meta/claude-code-usage.md`, `meso/documentation.md`, `meso/ai-deterministic-systems.md`

---

## Applied Principles

### Explicitness Over Implicitness
Every folder's purpose is declared. No engineer or agent should have to infer where a file belongs.

### Separation of Concerns
Each folder owns one class of artifact. Source modules, configuration, specifications, inputs, outputs, documentation, and tests do not share folders.

### Contracts as Source of Truth
The project structure is a contract. Files placed outside their declared folder violate the contract, regardless of whether they work.

### Validation at Boundaries
Input and output directories are explicit system boundaries. What enters and exits the system is visible by folder convention.

---

## 1. Project Root Layout

Every project must declare the following folder structure before any files are created. Not all folders are required for every project type: declare and create only those that apply. Undeclared folders must not be used.

```
project-root/
├── CLAUDE.md         ← AI agent instructions — must exist before implementation begins
├── ids/              ← AI-IDS specification files (.ids) — present only in AI projects
│                       lives at the root because it is a specification artifact, not code
├── src/              ← all source modules, organized per Section 2 (capabilities, layers)
├── database/         ← schema.sql, migrations/, seed.sql — present when the project owns a database
├── input/            ← raw input files consumed by the project
├── output/           ← files produced by the project
├── logs/             ← runtime log files
├── docs/
│   ├── decisions/    ← Architecture Decision Records
│   ├── contracts/    ← data contracts and output schemas
│   ├── prompts/      ← prompt registry entries for every .ids file
│   └── runbooks/     ← operational runbooks
├── tests/            ← test suite, mirrors src/ layer for layer (Section 7)
├── requirements.txt  ← or package.json / pyproject.toml
├── .env.example      ← environment variable documentation
├── .env              ← local secrets (always gitignored)
└── .gitignore
```

`src/` is the canonical source folder name across all languages: Python, TypeScript, Java, Rust all default to it. `ids/` lives at the project root alongside `docs/` and `tests/` because it is a specification artifact, not source code. A domain expert editing a `.ids` spec should not need to navigate a source tree to find it.

**Required declarations before first file:**
1. Confirm `src/` as the source folder (framework overrides must be declared explicitly in CLAUDE.md)
2. The list of capabilities known at the start, each with its five layer folders (Section 2)
3. Which of `input/`, `output/`, `logs/` are needed and whether they are gitignored

#### Why

Declaring the structure before creating files prevents the most common drift pattern: files placed wherever convenient, then reorganized later (or never). A declared structure is a checkpoint: every new file has exactly one correct location.

**Log file layout (batch and AI pipeline jobs).**
When running batch or AI pipeline tasks, must create a `logs/` folder and write timestamped files:

```
logs/
  {prefix}_plan_{yyyymmddhhmiss}.log
  {prefix}_reasoning_{yyyymmddhhmiss}.log
  {prefix}_execution_{yyyymmddhhmiss}.log
```

- `prefix` identifies the job or workflow (e.g., `keyword_gen`, `etl_orders`)
- log level applies to all three files based on EXECUTION_MODE

#### Failure Mode

Ad-hoc folder creation, mixed concerns in a single folder, or structure invented mid-implementation with no declared rationale. Symptom: `utils.py` in the root, config values scattered across modules, output files alongside source code.


---

## 2. Source Module Organization (`src/`)

The source folder is organized by capability first and by layer second, per
`coding-standards/common.md` Standard 13. A capability is one business concern with its own
data, rules, and entry points (`orders`, `billing`, `shipments`). Every capability has the same
five layer folders from its first file, whether the application is an HTTP API, a UI, a CLI, a
worker, or a mix. There is no size threshold: the layout is identical for a capability with one
file per layer and one with fifty.

```
src/
├── main.py / server.ts      ← entry point: starts the process, nothing else
├── app.py / app.ts          ← composition root: builds repositories, injects them into services,
│                              mounts controllers; the only place that wires layers together
├── config/                  ← ALL environment variables read here (Standard 2 of common.md)
│   ├── env                  ← validated environment settings
│   └── database             ← connection pool initialization
├── capabilities/
│   └── <capability>/        ← e.g. orders/
│       ├── controllers/     ← entry point: route/command/message binding + shape validation
│       ├── services/        ← business rules, orchestration, transaction boundary
│       ├── repositories/    ← all data access
│       ├── models/          ← record structures and domain types
│       └── views/           ← output shapes (whitelisted fields)
├── workflows/               ← orchestration across two or more capabilities
│   └── <workflow-name>
└── shared/                  ← used by two or more capabilities, no capability-specific rules
    ├── errors/              ← typed domain errors
    ├── middleware/
    ├── events/              ← internal event bus for asynchronous side effects
    └── utils/
```

**Rules:**
- Every capability has all five layer folders, created together when the capability is created; an empty folder is correct, a missing one is a defect
- Dependency flows `controllers` to `services` to `repositories` to `models`; `views` are called by controllers. A lower layer never imports a higher one
- Services receive repositories by injection; `app` is the only module that constructs both
- A capability never imports another capability's `controllers/`, `repositories/`, `models/`, or `views/`. It calls that capability's `services/` or publishes to `shared/events/`
- Two or more capabilities coordinated synchronously, or two services that would import each other, go in `workflows/`
- `shared/` holds code used by two or more capabilities. Code used by one capability stays in that capability, and extracting it to `shared/` happens on the second user, not before
- The config module is the only module every other module may import
- Circular imports are forbidden: dependency must be acyclic
- `main` and `app` are the only modules that import from every layer; nothing imports from them

**The same layout for each transport.** The five folders do not change; only what the controller
binds to and what the view produces.

```
HTTP API:        controllers/ = route + handler    views/ = response payload
UI application:  controllers/ = page/route handler  views/ = pages and components
                 shared/views/shell/ = header, footer, nav panel (the app shell)
                 shared/views/components/ = components used on 2+ pages
CLI:             controllers/ = command handler     views/ = terminal output formatting
Worker:          controllers/ = queue/topic/schedule handler
                                                    views/ = result record, outbound payload
```

**File naming.** The layer is visible in every file's name, in the form each language standard
defines (`coding-standards/nodejs.md` and `coding-standards/python.md`). The capability name is
plural or singular consistently across a project, as declared in the Terminology Lock.

| Layer | Node.js / TypeScript | Python |
|---|---|---|
| Controller | `<capability>.controller.ts` | `<capability>_controller.py` |
| Service | `<capability>.service.ts` | `<capability>_service.py` |
| Repository | `<capability>.repository.ts` | `<capability>_repository.py` |
| Model | `<capability>.model.ts` | `<capability>_model.py` |
| View | `<capability>.view.ts` | `<capability>_view.py` |
| Test | `<capability>.<layer>.test.ts` | `test_<capability>_<layer>.py` |

A capability with several files in one layer names each by the thing it holds
(`order-line.model.ts`, `order_line_model.py`); the layer suffix stays.

#### Failure Mode

`helpers.py` or `utils.py` containing unrelated functions from multiple domains. God modules that own too many responsibilities. A layer folder omitted because the capability "is small," so the next change has to restructure it. A capability importing another's repository. Services that build their own database client. Circular imports that prevent independent testing.

---

## 3. Configuration Module

All environment variables and configuration constants must be read in a single configuration module, `src/config/` (`env.py` or `env.ts`). This module is the only place in the codebase where `os.getenv()` or `process.env` is read.

```python
# src/config/env.py

import os

# Required — raises at startup if absent
DATABASE_URL = os.environ["DATABASE_URL"]

# Optional — explicit default
TIMEOUT_SECS = float(os.getenv("TIMEOUT_SECS", "30.0"))
```

**Rules:**
- Required values: use `os.environ["KEY"]`; raises `KeyError` at startup if absent
- Optional values: use `os.getenv("KEY", "default")`; always provide an explicit default
- No `os.getenv()` calls outside this module
- `.env.example` must list every variable declared in the config module with description and default value

#### Failure Mode

Configuration values read at call sites (`os.getenv("X")` inside a function). Silent failures when a required value is absent: the system degrades instead of failing fast at startup.

---

## 4. AI-IDS Specifications (`ids/`)

AI-IDS specification files live in a dedicated `ids/` folder at the project root. They are plain text files with a `.ids` extension. They contain no code.

```
ids/
├── content-cleaner.ids     ← one file per AI task
├── keyword-generator.ids
└── ...
```

**Rules:**
- One `.ids` file per distinct AI task, not one file for the entire project
- `.ids` files follow the template in `meso/ai-ids-template.md` exactly: DEFINITIONS, ROLE, OBJECTIVE, GUARDRAILS, STRUCTURE OF INPUT, STRUCTURE OF OUTPUT, DERIVED LOGIC, ASSUMPTIONS, REASONING POLICY, GUIDELINES & INSTRUCTIONS, FEW SHOT EXAMPLES
- The Python or TypeScript harness module (`src/ai_cleaner.py`) reads the `.ids` file at startup using a `_load_ids(name)` function: it contains no specification content
- A prompt registry entry in `docs/prompts/<name>.md` is required for every `.ids` file
- `.ids` files are versioned in source control: changes to them are engineering changes that require review

```
Correct:

ids/content-cleaner.ids        ← specification (plain text, at project root)
src/ai_cleaner.py              ← harness (loads the spec, calls the API)
docs/prompts/
  prompt-001-content-cleaner.md  ← registry entry

Forbidden:

src/ai_cleaner.py              ← contains the IDS spec as a string constant _IDS_SYSTEM = """..."""
```

#### Why

An `.ids` file is a specification artifact: it should be reviewable, versionable, and editable by domain experts without requiring Python or TypeScript knowledge. Embedding it in code couples the specification to the execution harness and makes independent review impossible.

#### Failure Mode

AI-IDS specification embedded as a string constant in the harness module. Changes to the specification require code changes. Specification is not independently reviewable. No prompt registry entry exists.

---

## 5. Input and Output Directories

Pipelines and ETL jobs must declare explicit input and output directories. These are the system's external boundaries.

```
input/       ← files consumed by the pipeline (source data, config files, seed data)
output/      ← files produced by the pipeline (CSVs, reports, transformed datasets)
logs/        ← runtime log files written by the pipeline
```

**Rules:**
- `input/` and `output/` must not contain source code
- `output/` and `logs/` are always gitignored: they contain runtime artifacts, not source artifacts
- `input/` is gitignored by default; declare explicitly if input files are versioned (e.g., small seed datasets)
- Place a `.gitkeep` file in each empty directory that must exist at runtime but is gitignored
- The output path must be configurable via environment variable and never hardcoded

```
# Correct: output path from config
OUTPUT_CSV = os.getenv("OUTPUT_CSV", "output/output.csv")

# Forbidden: hardcoded output path
with open("output/results.csv", "w") as f: ...
```

#### Failure Mode

Output files written to the project root or alongside source code. Output committed to version control. Input and output directories sharing the same folder, making the boundary invisible.

---

## 6. Documentation Structure (`docs/`)

Documentation is organized by artifact type, not by team or date. Every subfolder maps to a documentation type defined in `meso/documentation.md`.

```
docs/
├── decisions/      ← Architecture Decision Records (ADR-NNN-title.md)
├── contracts/      ← Data contracts and output schema definitions
├── prompts/        ← Prompt registry entries (one per .ids file)
└── runbooks/       ← Operational guides for production systems
```

**Rules:**
- Every significant technical decision requires an ADR in `docs/decisions/`
- Every data output produced by the system requires a contract in `docs/contracts/`
- Every `.ids` file requires a prompt registry entry in `docs/prompts/`
- All documentation files must carry `Status:` and `Owner:` frontmatter
- Runbooks are required for systems that go to production

#### Failure Mode

Design decisions recorded only in Slack threads or PR descriptions. No data contract for pipeline output. `.ids` files with no corresponding prompt registry entry. Documentation files without lifecycle state declared.

---

## 7. Test Organization

Tests live in a top-level `tests/` directory that mirrors `src/` layer for layer, with one test file per source file.

```
tests/
├── conftest.py / setup.ts                ← shared fixtures, database transactions, teardown
├── capabilities/
│   └── <capability>/
│       ├── controllers/<capability>.controller.test.ts   (Python: test_<capability>_controller.py)
│       ├── services/<capability>.service.test.ts
│       ├── repositories/<capability>.repository.test.ts
│       ├── models/<capability>.model.test.ts
│       └── views/<capability>.view.test.ts
├── workflows/<workflow-name>.workflow.test.ts
└── shared/
    └── middleware/
```

**Rules:**
- Every capability and workflow added to `src/` gets its mirrored test folder in the same task
- One test file per source file, at the same relative path under `tests/`
- Tests must not live inside `src/`: they are not source modules
- Service tests inject a fake or in-memory repository; they never need a database
- Repository tests run against a real database inside a transaction that rolls back
- Every external dependency (network calls, file I/O, API calls) must be mocked in unit tests
- Integration tests may use real dependencies within a controlled environment and must be in a separate subfolder (`tests/integration/`)
- Test filenames and function names must be descriptive: `test_process_order_raises_when_invalid` is correct; `test_case_1` is not

#### Failure Mode

Tests mixed into `src/`. No test file for a source file, discovered only at review. A test tree whose shape differs from `src/`, so no one can tell what is untested. Service tests that need a live database because the service builds its own repository. Integration tests and unit tests in the same file, breaking environment isolation.

---

## 8. Object-Oriented Organization

Object-oriented design at the module level follows these conventions. Class-level conventions for each language are in `coding-standards/python.md` and `coding-standards/nodejs.md`.

### Module = Unit of Encapsulation

A module owns one cohesive cluster of related types and functions. All classes in a module share a common purpose. A module that contains `UserFetcher`, `PaymentProcessor`, and `EmailFormatter` has no cohesion: split it.

```
Correct — one module, one concern:
src/capabilities/orders/models/orders_model.py     OrderItem (dataclass)
src/csv_writer.py          write_csv()
src/ai_cleaner.py          AICleanerError, clean_text_with_ai()

Forbidden — mixed concerns:
src/utils.py          everything that didn't have a home
```

### Class Naming

| Concept | Convention | Example |
|---|---|---|
| Domain entity | PascalCase noun | `OrderItem`, `UserProfile` |
| Exception | PascalCase noun ending in `Error` | `FetchError`, `AICleanerError` |
| Abstract base | PascalCase noun, no suffix needed | `BaseRepository` |
| Data class / value object | PascalCase noun | `CleaningResult`, `CleanedRecord` |

### Dependency Direction Rule

Dependencies flow in one direction only. A violation is a design error, not a style preference.

```
app                                        ← composition root; wires everything
  capabilities/orders/controllers          ← imports its own services, views, shared/errors
    capabilities/orders/services           ← imports its own repositories (injected), models, shared
      capabilities/orders/repositories     ← imports its own models, config/database
        capabilities/orders/models         ← imports nothing from src/
  config/                                  ← imports nothing from src/
```

Lower layers (models, repositories, config, shared utilities) must not import from higher layers
(services, controllers, entry points). If a lower layer needs something from a higher one, the
dependency direction is wrong: restructure. Across capabilities the only permitted import is
`<other-capability>/services/` (or `shared/events/`).

### Dataclasses and Value Objects

Prefer dataclasses or simple classes for data containers. Do not use dictionaries as domain objects: they lose the contract.

```python
# Correct — named contract
@dataclass
class OrderItem:
    order_id: str
    sku: str
    quantity: int
    unit_price_cents: int

# Forbidden — unnamed, untyped, unenforceable
entry = {"order_id": "...", "sku": "...", "quantity": 0, "unit_price_cents": 0}
```

#### Failure Mode

A `utils.py` module that every other module imports from, creating a coupling hub. Classes named `Manager`, `Handler`, or `Processor` with no domain noun, accumulating unrelated methods. Dictionaries used as domain objects, losing contract visibility.

---

## 9. Naming Conventions

| Artifact | Convention | Example |
|---|---|---|
| Folder | kebab-case or snake_case (consistent per project) | `src/`, `ids/`, `docs/decisions/` |
| Python module | snake_case noun, layer suffix | `orders_service.py`, `orders_repository.py` |
| TypeScript module | kebab-case, dotted layer suffix | `orders.service.ts`, `order-line.model.ts` |
| Python class | PascalCase noun | `OrderItem`, `FetchError` |
| TypeScript class/interface | PascalCase noun | `OrderItem`, `FetchError` |
| Python function / method | snake_case verb phrase | `process_order()`, `validate_record()` |
| TypeScript function / method | camelCase verb phrase | `processOrder()`, `validateRecord()` |
| Private function / method | leading underscore (Python) | `_strip_html_noise()` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES`, `BACKOFF_MS` |
| Environment variable | UPPER_SNAKE_CASE | `API_NUM_RETRIES`, `OUTPUT_CSV` |
| ADR file | `adr-NNN-kebab-title.md` | `adr-001-content-cleaning-strategy.md` |
| IDS file | kebab-case noun phrase | `content-cleaner.ids`, `keyword-generator.ids` |
| Prompt registry file | `prompt-NNN-kebab-title.md` | `prompt-001-content-cleaner.md` |
| Test function | `test_<function>_<scenario>` | `test_process_order_raises_when_invalid` |

#### Failure Mode

Inconsistent naming within a project (some modules snake_case, some PascalCase). Folders named by team ownership rather than artifact type. Test functions named `test_1`, `test_case_a`. IDS files named with spaces or version suffixes baked into the filename rather than tracked in frontmatter.

---

## Failure Modes

- Structure invented mid-implementation and never declared: file placement becomes arbitrary
- `utils.py` or `helpers.py` created as a catch-all: accumulates unrelated code, creates coupling
- Config values read at call sites instead of in `src/config/`: configuration drift
- `.ids` files embedded as string constants in harness code: specification not independently reviewable
- `output/` committed to version control: runtime artifacts pollute source history
- Test files inside `src/`: source and test concerns mixed
- A capability missing one or more of its five layer folders: the structure differs capability to capability and the next change restructures it
- Cross-capability imports of repositories, models, controllers, or views: hidden coupling
- ADRs for significant decisions never written: rationale is lost
- `docs/` folder flat with no subfolders: artifact types mixed, impossible to navigate

---

## Definition of Done

A project structure meets this standard when:
- Every folder is declared and its purpose documented in CLAUDE.md before the first file is created
- `src/` is the sole location for source modules; no source code in the project root
- `src/config/` is the only place that reads environment variables
- `ids/` exists and contains only `.ids` files if the project uses AI systems
- `input/`, `output/`, and `logs/` are present and gitignored if the project is a pipeline
- `docs/decisions/`, `docs/contracts/`, and `docs/prompts/` are populated as work progresses
- every capability has `controllers/`, `services/`, `repositories/`, `models/`, and `views/` under `src/capabilities/<capability>/`
- `tests/` mirrors `src/` layer for layer with one test file per source file
- No `utils.py` or `helpers.py` catch-all modules exist
- All classes follow the naming conventions in Section 9
- Dependency direction is acyclic and flows controllers, services, repositories, models, with no cross-capability imports except through services or events
