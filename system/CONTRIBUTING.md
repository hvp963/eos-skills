# Contributing

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

---

## Reporting an Inaccuracy

This material is one practitioner's point of view (see the Notice and Disclaimer in `README.md`), so some of it will not match your experience or will have gone out of date. If a statement is wrong, outdated, or misdescribes a product or a practice, open an issue that names the file, quotes the sentence, and links a source or describes what you observed. Corrections to third-party facts (release dates, supported platforms, counts) are the most useful because those change fastest.

---

## How Changes Are Accepted

This repository is the published copy of the maintainer's working repository, so pull requests are not merged directly. A pull request is welcome as a proposal. If the change is accepted, the maintainer applies it in the working repository and it ships in the next tagged release, with your name added to the file's `Authors:` line and to the CHANGELOG entry. For anything larger than a fix, open an issue first so the direction is agreed before you write it. Security reports go through the private route in `SECURITY.md`, not a public issue.

---

## What This Is

The Engineering OS is a structured body of knowledge, not a code library or a wiki. Contributions must fit the layer model, follow the authoring style, and add clear value without adding bulk.

---

## Before You Contribute

Read these files first:

1. `meta/mental-model.md`: understand the four layers and what belongs in each
2. `meta/document-authoring-guidelines.md`: the style rules all content must follow
3. `meta/glossary.md`: use canonical terms; do not introduce synonyms

---

## Types of Contributions

### Adding a new meso guide
- Use the structure: Definition → Scope → Applied Principles → Core Patterns → Failure Modes → Definition of Done
- Patterns must include pseudocode: no vague prose without a structural example
- Each pattern must include a **Failure Mode** showing what goes wrong when the pattern is skipped
- Do not redefine concepts already covered in another guide; cross-reference instead

### Adding a new micro standard or template
- `micro/coding-standards/`: implementation of a rule already stated in `common.md`; must show real code in a supported language (Python or Node.js/TypeScript)
- `micro/templates/`: scaffolding artifacts for a specific workload type; must be minimal and immediately usable
- Do not add a language-specific standard for a rule not first stated in `common.md`

### Updating an existing guide
- Additive changes (new pattern, new failure mode, new example) are low risk: follow the existing structure
- Changes to Applied Principles or Definition of Done require justification; these are the load-bearing parts of each guide
- Do not remove a failure mode without replacing it with a more precise one

### Fixes
- Factual corrections, broken pseudocode, outdated tool references: always welcome
- Style corrections must conform to `meta/document-authoring-guidelines.md`

### Adding or updating a skill (`skills/`)
- Follow `skills/eng-os-doc-authoring-rules/SKILL.md`: the Skill-Specific Notes section governs frontmatter, progressive disclosure, and independence from `meta/document-authoring-guidelines.md`
- `skills/` must not re-embed canonical content wholesale; condense it and link to the canonical file (`sources:` field, or a direct relative path from the skill body). Wholesale copies drift from their source; don't reintroduce them.
- Skills do carry condensed and mirrored canonical text on purpose: the rules in `SKILL.md`, larger blocks in `references/`, so an agent can load a rule without the whole guide. Two conditions apply. The canonical file must be listed in the skill's `sources:` (`tools/lint-os.py` check 10 fails a 220-character paragraph copied from a doc the skill does not cite). And the canonical file is edited first, then re-copied; where a copy and its source differ, the canonical file wins. A condensed copy that has drifted from its source is a defect to fix, not a second opinion.
- **A rule discovered while building or using a skill belongs in the canonical `meso`/`micro` document first, then in the skill.** If you find yourself adding a new pattern, caveat, or failure mode directly into a `SKILL.md` because it's faster than updating the source doc, that's a signal the source doc is now behind the skill: file the addition in the canonical layer in the same change, not as a follow-up.
- Every skill must have a concrete, grounded worked example: either inline (`## Example`) if brief, or `references/example.md` if longer. Abstract rule restatement is not an example.
- Update `skills/MINDMAP.md` if the change affects routing or relationships between skills.

---

### Tooling that runs on every contribution
- `python tools/lint-os.py` must pass before a commit; CI runs it on every push and pull request. It checks skill frontmatter (including a double-quoted `description`), `sources:` paths, skill counts across the index files, relative links, backticked file paths, that every `references/` file is named in its `SKILL.md`, that text copied from a canonical doc is sourced, the em-dash rule, and the message-code format.
- A new rule, gate, or pattern adds a row to `evidence/ledger.md` in the same change, and `skills/MINDMAP.md` cites it by id if it changes a tier.
- A decision that meets the threshold in `meso/documentation.md` 2.1 gets an ADR in `docs/decisions/`.
- After adding a skill, re-run `tools/install.ps1` or `tools/install.sh` and confirm the skill appears in a fresh session before widening its `verified_platforms`.
- Releases are tagged with the `VERSION` value; downstream projects pin that tag in their CLAUDE.md.

---

## What Does Not Belong

- tool-specific tutorials (e.g., "how to configure Datadog")
- company-specific content (internal URLs, team names, proprietary systems)
- content that duplicates an existing guide without adding a new layer of precision
- style guides or formatting preferences: this is about operational standards, not aesthetics
- AI-generated content submitted without review: every contribution must be read and validated by a human

---

## Authoring Checklist

Before submitting, verify:

- [ ] The file is in the correct layer (`meta/`, `macro/`, `meso/`, or `micro/`)
- [ ] The Definition section states clearly what the guide is and is not
- [ ] Every principle is backed by a concrete pattern or example
- [ ] Every pattern has a Failure Mode
- [ ] No content is duplicated; cross-references used instead
- [ ] No hardcoded values, company-specific references, or tool-specific steps
- [ ] The Definition of Done is verifiable: each item can be checked by a reviewer
- [ ] Language follows `meta/glossary.md` canonical terms
- [ ] If this change should also update a `skills/` file (new pattern, new failure mode), that skill file was updated in the same contribution, not left to drift

---

## Attribution

This work was originally authored by **Haresh V. Parekh**. When copying, adapting, or extending any part of this repository, you must credit the original author in a visible location using the form specified in the repository-root `LICENSE`.

Every file carries an `**Authors:**` line directly below its title. When you make a meaningful contribution to a file, add your name to that line. "Meaningful" means substantive additions or corrections, not typo fixes.

Contributions do not transfer authorship of the original work. The `Authors:` line records who shaped the content, not who owns it.

---

## License

By contributing, you agree that your contribution is licensed under the license that covers the files you change: CC BY 4.0 for `system/`, MIT for `tools/` and `.github/` (see the repository-root `LICENSE`).
