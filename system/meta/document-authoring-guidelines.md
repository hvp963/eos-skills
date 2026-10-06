# Document Authoring Guidelines

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Standards for writing and maintaining Engineering OS documents so they remain useful to engineers and AI agents.

### What This Is Not
- not a general writing guide
- not a documentation style manual
- not a grammar standard
- not a sentence-level prose style guide (see `meso/prose-style.md` for the full set of AI-tell patterns: contrastive-negation overuse, filler words, em dash as a clause joiner (hard ban), cliché vocabulary, reflexive openers, forced balance, fake precision, overexplaining, mechanical formatting, repetitive sentence structure, generic content)

## Scope
- Level: Meta
- Applies To: All files in this repository
- See Also: `meso/prose-style.md` for how sentences should read, as distinct from this file's rules for how documents should be structured

---

## Core Rules

### 1. Write for execution
Every file must help a reader do something.
If a file cannot influence a design, decision, implementation, or review, it is too abstract.

### 2. Make each file independently useful
A file may reference other files, but it must not depend on them for basic usefulness.
Avoid thin "see other document" content.

### 3. Define boundaries clearly
Every file should define:
- what it is
- what it is not
- where it applies
- what it does not cover

### 4. Apply principles in context
Do not merely list principles.
Explain how a principle changes decisions in the context of that file.

### 5. Include patterns and failure modes
Every meso and micro artifact should explain:
- recommended patterns
- common mistakes
- likely failure modes
- expected validation criteria

### 6. Use glossary terms consistently
Defined terms should be reused consistently.
Do not introduce alternate names for the same concept unless the distinction matters.

### 7. Separate rules from guidance
Rules belong in:
- principles
- quality attributes
- contracts
- guardrails

Guidance belongs in:
- design patterns
- examples
- usage notes

### 8. Separate semantics from execution
Especially for AI-IDS:
- semantics describe what sections mean
- execution defines precedence and dependency
Do not mix these casually.

### 9. Avoid over-duplication
Do not copy entire definitions from the glossary into every file.
Do explain how terms apply in context.

### 10. Prefer concise depth over shallow breadth
A smaller number of complete, useful sections is better than many thin sections.

---

## Required Structure by Layer

### Meta Files
Should include:
- definition
- scope
- operating model or rules
- failure mode or misuse warnings when relevant

### Macro Files
Should include:
- definition
- scope
- non-negotiable rules or evaluation dimensions
- implications
- failure modes or trade-offs

### Meso Files
Should include:
- definition
- scope
- applied principles
- design patterns
- failure modes
- definition of done

### Micro Files
Should include:
- purpose
- inputs
- steps or checklist
- expected output
- review criteria

---

## Language Rules

- Prefer short declarative sentences
- Use "must" for required behavior
- Use "must not" for forbidden behavior
- Use "may" for optional behavior
- Use ordered lists when sequence matters
- Use grouped lists when category matters
- Avoid vague phrases like "best effort" unless bounded explicitly

---

## Anti-Patterns

- thin reference-only files
- generic advice without trade-offs
- mixing constraints and examples
- repeating glossary definitions without contextual value
- using templates with no guidance
- treating AI examples as authoritative rules
- describing systems without review criteria

---

## Guiding Standard

Each file should answer this question:

"If an engineer or AI agent used only this file plus the glossary, could they make materially better decisions?"

If the answer is no, the file needs more substance.
