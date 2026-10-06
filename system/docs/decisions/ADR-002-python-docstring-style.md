# Architecture Decision Record: Python Docstring Style

**Authors:** Haresh V. Parekh

---

## Metadata

| Field | Value |
|---|---|
| ADR Number | ADR-002 |
| Status | Accepted |
| Date | 2026-09-01 |
| Owner | Haresh V. Parekh |
| Supersedes | none |

## Context

`micro/coding-standards/python.md` Section 9 requires JSDoc-style tags (`@param {type}`,
`@returns`, `@throws`) inside Python docstrings, so that Python and TypeScript share one
documentation vocabulary. Python's ecosystem (Sphinx, pdoc, mkdocstrings, IDE hover, PEP 257
tooling) parses Google, NumPy, or reStructuredText docstring styles; none parses JSDoc tags.
The consequence is that generated documentation and IDE tooltips render the tags as plain text,
and every Python hire is surprised.

This was inherited from a two-language team's preference, not recorded as a decision.

## Decision

Switch the Python house style to Google style (`Args:`, `Returns:`, `Raises:`),
which every mainstream Python doc generator and IDE parses, and keep JSDoc for TypeScript. The
shared vocabulary the JSDoc rule was protecting (document purpose, every parameter, the return
value, and every raised error) is a rule in `common.md` Standard 11 and is unchanged; only the
per-language syntax differs. Type annotations remain mandatory in signatures, so the `{type}`
tag is redundant in Python.

Accepted by the Owner on 2026-09-02. `micro/coding-standards/python.md`, `skills/coding-standards/python`,
`micro/coding-standards/common.md`, `meta/glossary.md`, and `meta/architecture.md` carry the new rule;
all JSDoc-in-Python examples across the canonical layer and the skills layer are updated to
Google style.

## Consequences

### Accepted Trade-offs
- An engineer switching languages switches docstring syntax.

### Doors Closed
- One docstring syntax shared across Python and TypeScript. The shared vocabulary stays (purpose, every parameter, the return value, every raised error); the JSDoc tags do not.

### Benefits
- Generated docs and IDE hover work without custom parsers; standard onboarding.

---

## Alternatives Considered

### Alternative 1: Keep JSDoc tags in Python docstrings (status quo)

**What it is:** `@param {type}`, `@returns`, and `@throws` inside Python docstrings.

**Why rejected:** one vocabulary across languages, but Sphinx, pdoc, mkdocstrings, and IDE hover render the tags as plain text.

### Alternative 2: Adopt reStructuredText field lists

**What it is:** Sphinx-style `:param:` and `:returns:` fields.

**Why rejected:** tooling supports it, but it is more verbose than Google style and less common in application code.

---

## Validation

Revisit if a Python doc tool with JSDoc support becomes standard in the team's stack.

## References

- `micro/coding-standards/python.md` Section 9
- `micro/coding-standards/common.md` Standard 11
