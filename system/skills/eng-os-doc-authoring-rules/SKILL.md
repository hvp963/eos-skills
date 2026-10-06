---
name: eng-os-doc-authoring-rules
description: "Use only when writing or editing an Engineering OS document/skill itself (maintainer-facing, not for application code)."
sources:
  - meta/document-authoring-guidelines.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Doc Authoring Rules

Standards for writing and maintaining Engineering OS documents (and skills derived from them)
so they remain useful to engineers and AI agents. This is maintainer-facing: it governs how
to write the OS documents/skills themselves, not application code.

## Core Rules

1. **Write for execution.** Every file must help a reader do something. If a file cannot influence a design, decision, implementation, or review, it is too abstract.
2. **Make each file independently useful.** A file may reference others but must not depend on them for basic usefulness. Avoid thin "see other document" content.
3. **Define boundaries clearly.** Every file should state what it is, what it is not, where it applies, and what it does not cover.
4. **Apply principles in context.** Don't just list principles; explain how a principle changes decisions in the context of that file.
5. **Include patterns and failure modes.** Every meso/micro artifact should cover recommended patterns, common mistakes, likely failure modes, and expected validation criteria.
6. **Use glossary terms consistently.** Reuse defined terms; don't introduce alternate names for the same concept unless the distinction matters.
7. **Separate rules from guidance.** Rules belong in principles/quality attributes/contracts/guardrails. Guidance belongs in design patterns/examples/usage notes.
8. **Separate semantics from execution.** Especially for AI-IDS: semantics describe what sections mean, execution defines precedence and dependency; don't mix these casually.
9. **Avoid over-duplication.** Don't copy entire glossary definitions into every file; explain how terms apply in context instead.
10. **Prefer concise depth over shallow breadth.** A smaller number of complete, useful sections beats many thin sections.
11. **No restated-generic bullets in a specific section.** Test: for every bullet in a "project-specific" section, strip proper nouns, file paths, and values from its claim and search the generic section for the same stripped claim. A match means the bullet is a duplicate: delete it or replace it with a one-line pointer ("resolves to `<path>` here").

## Required Structure by Layer

| Layer | Must include |
|---|---|
| Meta | definition, scope, operating model or rules, failure mode/misuse warnings when relevant |
| Macro | definition, scope, non-negotiable rules or evaluation dimensions, implications, failure modes/trade-offs |
| Meso | definition, scope, applied principles, design patterns, failure modes, definition of done |
| Micro | purpose, inputs, steps or checklist, expected output, review criteria |

## Language Rules

- prefer short declarative sentences
- use "must" for required behavior, "must not" for forbidden behavior, "may" for optional behavior
- use ordered lists when sequence matters, grouped lists when category matters
- avoid vague phrases like "best effort" unless bounded explicitly

## Anti-Patterns

- thin reference-only files
- generic advice without trade-offs
- mixing constraints and examples
- repeating glossary definitions without contextual value
- using templates with no guidance
- treating AI examples as authoritative rules
- describing systems without review criteria

## Skill-Specific Notes

When converting a doc into a Skill (SKILL.md):
- keep the YAML frontmatter `description` as a specific "Use when..." trigger phrase: this is what routes the skill, treat it with the same rigor as a section boundary statement above
- large illustrative content (code samples, worked examples, blank templates) belongs in `references/*.md`, linked from SKILL.md; apply Rule 10 (concise depth) to the SKILL.md body itself
- a skill body must still be independently useful (Rule 2): an agent using only SKILL.md should be able to act correctly without opening the references

For a concrete before/after showing one of these rules (Rule 5) applied to a small doc section,
see `references/example.md`.

## Guiding Standard

Each file (or skill) should answer: **"If an engineer or AI agent used only this file plus the
glossary, could they make materially better decisions?"** If the answer is no, the file needs
more substance.

## Definition of Done

- [ ] the file states what it is, what it is not, where it applies
- [ ] principles are applied in context, not merely listed
- [ ] patterns and failure modes are present where the layer requires them (see table above)
- [ ] terminology matches the glossary; no unexplained synonyms introduced
- [ ] rules and guidance are kept in separate sections
- [ ] the file is independently useful without requiring another file to be open simultaneously
- [ ] the file passes the guiding-standard question above
- [ ] every specific-section bullet passed the Core Rule 11 duplicate test against the generic section
