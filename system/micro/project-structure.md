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
├── src/              ← all source modules
├── input/            ← raw input files consumed by the project
├── output/           ← files produced by the project
├── logs/             ← runtime log files
├── docs/
│   ├── decisions/    ← Architecture Decision Records
│   ├── contracts/    ← data contracts and output schemas
│   ├── prompts/      ← prompt registry entries for every .ids file
│   └── runbooks/     ← operational runbooks
├── tests/            ← test suite
├── main.py / app.py  ← entry point (one per project)
├── requirements.txt  ← or package.json / pyproject.toml
├── .env.example      ← environment variable documentation
├── .env              ← local secrets (always gitignored)
└── .gitignore
```

`src/` is the canonical source folder name across all languages: Python, TypeScript, Java, Rust all default to it. `ids/` lives at the project root alongside `docs/` and `tests/` because it is a specification artifact, not source code. A domain expert editing a `.ids` spec should not need to navigate a source tree to find it.

**Required declarations before first file:**
1. Confirm `src/` as the source folder (framework overrides must be declared explicitly in CLAUDE.md)
2. Whether `config.py` lives inside `src/` or in a separate `config/` folder
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

The source folder contains all application logic. It is a Python package (with `__init__.py`) or a TypeScript module tree. The config module is its only internal dependency that is not also a source module.

```
src/
├── __init__.py          ← makes src/ a package (Python); leave empty unless re-exporting
├── config.py            ← ALL environment variables read here (Standard 2 of common.md)
├── [domain_noun].py     ← one module per cohesive responsibility
├── [domain_noun].py
└── ...
```

**Rules:**
- One module = one cohesive responsibility, not one module per function
- Module names are snake_case nouns describing what the module is, not what it does (`order_processor`, not `process_orders`)
- The config module is the only module every other module may import: it has no siblings as dependencies
- Circular imports are forbidden: dependency must be acyclic
- `main.py` or `app.py` at the project root imports from `src/`; modules inside `src/` do not import from `main.py`

```
Correct dependency direction:

main.py
  └── imports src.order_processor
        └── imports src.config
        └── imports src.record_validator
              └── imports src.config

Forbidden:

src.order_processor imports src.csv_writer   ← unrelated modules coupled
src.config imports src.order_processor       ← direction reversed
main.py imports config directly               ← bypasses src package boundary
```

#### Failure Mode

`helpers.py` or `utils.py` containing unrelated functions from multiple domains. God modules that own too many responsibilities. Circular imports that prevent independent testing.

---

## 3. Configuration Module

All environment variables and configuration constants must be read in a single configuration module: `src/config.py` or `config/config.py`. This module is the only place in the codebase where `os.getenv()` is called.

```python
# src/config.py

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
- `.env.example` must list every variable declared in `config.py` with description and default value

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

Tests live in a top-level `tests/` directory that mirrors the structure of `src/`.

```
tests/
├── __init__.py
├── test_config.py          ← if config has startup validation logic
├── test_order_processor.py ← mirrors src/order_processor.py
├── test_record_validator.py ← mirrors src/record_validator.py
└── ...
```

**Rules:**
- One test file per source module: `test_<module_name>.py` matches `src/<module_name>.py`
- Tests must not live inside `src/`: they are not source modules
- Every external dependency (network calls, file I/O, API calls) must be mocked in unit tests
- Integration tests may use real dependencies within a controlled environment and must be in a separate subfolder (`tests/integration/`)
- Test filenames and function names must be descriptive: `test_process_order_raises_when_invalid` is correct; `test_case_1` is not

#### Failure Mode

Tests mixed into `src/`. No test file for a module, discovered only at review. Integration tests and unit tests in the same file, breaking environment isolation.

---

## 8. Object-Oriented Organization

Object-oriented design at the module level follows these conventions. Class-level conventions for each language are in `coding-standards/python.md` and `coding-standards/nodejs.md`.

### Module = Unit of Encapsulation

A module owns one cohesive cluster of related types and functions. All classes in a module share a common purpose. A module that contains `UserFetcher`, `PaymentProcessor`, and `EmailFormatter` has no cohesion: split it.

```
Correct — one module, one concern:
src/order_processor.py     OrderItem (dataclass), process_order()
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
main.py                     ← entry point; imports from src/
  src/order_processor.py   ← imports config, record_validator
  src/record_validator.py  ← imports config, ai_cleaner
  src/ai_cleaner.py        ← imports config only
  src/config.py            ← imports nothing from src/
```

Lower modules (config, shared utilities) must not import from higher modules (business logic, entry points). If a lower module needs something from a higher one, the dependency direction is wrong: restructure.

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
| Python module | snake_case noun | `order_processor.py`, `record_validator.py` |
| TypeScript module | camelCase or kebab-case (match framework) | `orderProcessor.ts`, `record-validator.ts` |
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
- Config values read at call sites instead of in `config.py`: configuration drift
- `.ids` files embedded as string constants in harness code: specification not independently reviewable
- `output/` committed to version control: runtime artifacts pollute source history
- Test files inside `src/`: source and test concerns mixed
- ADRs for significant decisions never written: rationale is lost
- `docs/` folder flat with no subfolders: artifact types mixed, impossible to navigate

---

## Definition of Done

A project structure meets this standard when:
- Every folder is declared and its purpose documented in CLAUDE.md before the first file is created
- `src/` is the sole location for source modules; no source code in the project root
- `src/config.py` (or `config/config.py`) is the only file that calls `os.getenv()`
- `ids/` exists and contains only `.ids` files if the project uses AI systems
- `input/`, `output/`, and `logs/` are present and gitignored if the project is a pipeline
- `docs/decisions/`, `docs/contracts/`, and `docs/prompts/` are populated as work progresses
- `tests/` mirrors `src/` with one test file per source module
- No `utils.py` or `helpers.py` catch-all modules exist
- All classes follow the naming conventions in Section 9
- Dependency direction is acyclic and flows from `main.py` → `src/` → `src/config.py`
