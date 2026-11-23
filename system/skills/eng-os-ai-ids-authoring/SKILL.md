---
name: eng-os-ai-ids-authoring
description: "In a project governed by the Engineering OS, use when designing, writing, or reviewing an AI system prompt/instruction set: the AI-IDS 11-section framework, its three orders (document, execution, authority), and the author review checklist."
sources:
  - meso/ai-deterministic-systems.md
  - micro/templates/ai-ids-template.md
  - meso/ai-ids-template.md
globs: ["ids/**/*.ids"]
always_apply: false
verified_platforms: [claude-code]
---

# AI-IDS Authoring

AI-IDS (AI Instruction Design Set) is a structured instruction architecture for production AI
systems that separates intent, constraints, contracts, logic, and style into explicit sections
with defined semantics, execution order, and authority rules. Use it instead of a free-form prompt
whenever an AI system's output must be reviewable, bounded, and operationally consistent.

Empirical result (production media retrieval pipeline, 400K+ productions, 7.2M keyword
generations; controlled eval of 9 articles / 161 sentences / 25 repeated executions):
composite operational consistency +23.6pp, operational error rate 2.2% → 0%, iterations to
production-grade output 17.1 → 4.1. Structural separation contributed independently of runtime
controls (temperature, seeds); those reduce variance but do not replace specification quality.

## The 11 Sections

Every spec contains all eleven sections. A section that does not apply contains `None` and one
line saying why; it is never omitted. ROLE, OBJECTIVE, and STRUCTURE OF OUTPUT are never `None`.

**Core Profile: meaning, intent, constraints, and contracts:**

1. **DEFINITIONS**: execution-time meaning of terms used later. No instructions, constraints, or style guidance here.
2. **ROLE**: the system's responsibility, operational context, and the perspective the output should take. No style preferences or output structure here.
3. **OBJECTIVE**: the single measurable outcome. One result, one success definition; no multiple unrelated goals or branching logic.
4. **GUARDRAILS**: non-negotiable constraints and failure conditions. Rule of thumb: if violating a statement should make the output unacceptable, it belongs here, not in GUIDELINES.
5. **STRUCTURE OF INPUT**: the input contract: required/optional fields, types, meaning, acceptable scope. No hidden assumptions about undeclared input.
6. **STRUCTURE OF OUTPUT**: the output contract and determinism boundary: schema/shape, required fields, ordering, cardinality limits, and an explicit statement of what "equivalent inputs" must produce structurally.

**Extended Profile: computation, bounded inference, ambiguity resolution, and guidance. Core sections govern Extended sections:**

7. **DERIVED LOGIC**: explicit deterministic computation, written as a finite ordered sequence (normalization, extraction, filtering, ordering, truncation, fallback, named constants/thresholds). No vague judgment, no computation hidden in prose elsewhere.
8. **ASSUMPTIONS**: explicitly allowed, bounded inference for incomplete inputs (allowed fallback interpretations, conditions under which inference is permitted). Never open-ended reasoning or guesses ungrounded in input.
9. **REASONING POLICY**: deterministic ambiguity resolution: tie-breaking and prioritization among already-allowed interpretations. Never introduces new constraints or new assumptions.
10. **GUIDELINES & INSTRUCTIONS**: non-authoritative influence on tone, clarity, and presentation. Must never carry hard constraints, logic, or assumptions.
11. **FEW SHOT EXAMPLES**: illustrative input/output pairs. Non-authoritative: must be removable without changing system requirements. Never the sole place a rule exists.

## Three Orders

AI-IDS has three separate orders. Reading one as another is the most common authoring error: the
execution order is not a vote order, and the document order is not a ranking.

**Document order** is how a spec is written and read: the eleven sections in the order listed
above. It reflects semantic definition, not runtime execution.

**Execution order** is set by data dependencies, not by document order:

1. Resolve definitions and role
2. Fix the objective
3. Apply guardrails
4. Validate the input contract
5. Apply allowed assumptions
6. Resolve ambiguity by reasoning policy
7. Execute derived logic
8. Enforce the output contract

GUIDELINES & INSTRUCTIONS and FEW SHOT EXAMPLES are influence only and never override a constraint
or computation.

**Authority** decides which section governs a conflict:

- GUARDRAILS holds the highest constraint authority and overrides all lower-precedence sections.
- Core sections govern Extended sections; an Extended section never overrides a Core section.
- Constraints override preference and stylistic guidance.
- GUIDELINES & INSTRUCTIONS and FEW SHOT EXAMPLES never override constraints or execution logic, and examples never define a constraint or logic.
- A conflict these rules do not settle is a defect in the specification: rewrite the sections so they agree. Never leave the choice to the model.

## Common Failure Modes to Check For

- **Undeclared assumptions**: inference not bounded explicitly → inconsistent outputs across similar inputs.
- **Missing guardrails**: constraints weak or absent → unsafe or policy-violating outputs.
- **Hidden computation**: logic embedded implicitly in prose rather than DERIVED LOGIC → unexpected transformations in output.
- **Example-driven authority**: examples treated as rules → model imitates examples even when they conflict with requirements.
- **Weak output contract**: output schema underspecified → structurally inconsistent results.
- **Undocumented processing boundary**: a call-gating decision (pre-processing) or an
  arithmetic/lookup step on the model's output (post-processing) exists in code with no pointer
  from the spec → a spec reader cannot audit real behavior from the spec alone.

## Author Review Checklist

Run before marking a spec ready for deployment:

- [ ] All eleven sections present; a section that does not apply contains `None` and one line saying why (ROLE, OBJECTIVE, and STRUCTURE OF OUTPUT are never `None`)
- [ ] All important terms defined in DEFINITIONS
- [ ] Exactly one primary objective stated
- [ ] All hard constraints in GUARDRAILS: none hidden in GUIDELINES or examples
- [ ] Input contract explicit with types and required/optional distinction
- [ ] Output contract explicit with field types and determinism boundary stated
- [ ] All deterministic logic in DERIVED LOGIC as a finite ordered sequence
- [ ] All allowed assumptions bounded: no open-ended inference permitted
- [ ] Ambiguity resolution explicit in REASONING POLICY
- [ ] No two sections give different instructions for the same case unless the authority rules settle which governs
- [ ] FEW SHOT EXAMPLES could be removed without changing system requirements
- [ ] Metadata declares the version-bump rule (any section change), the evaluation fixtures and thresholds, the token and latency budget, the observability exposure, and the data classifications the spec accepts
- [ ] Prompt registry entry created in `docs/prompts/prompt-NNN-kebab-title.md`
- [ ] If any pre-processing gate (skip conditions) or post-processing step exists outside this
      call, the spec names it and points to where it lives, without absorbing its logic

## Observability UI Contract

This section is not in the original AI-IDS source docs; it is a requirement derived from
production apps that ship live AI-IDS inference to end users.

Every live AI-IDS inference exposed to an end user must be paired, at the point of use, with a
visible **"Scoring Run" indicator** showing:

- scorer/spec name and version (which `.ids` file and version produced this output)
- timestamp of the inference
- input and output token counts

Ideally, the indicator supports a drill-down that shows which ROLE, OBJECTIVE, GUARDRAILS, and
input values produced the displayed output, so a user or reviewer can trace an output
back to the spec sections and inputs responsible for it.

This skill owns the spec-authoring side (write ROLE/OBJECTIVE/GUARDRAILS/input structure so a run
can be attributed cleanly) and the UI pattern too: `references/observability-ui.md`
holds the Scoring Run card pattern, the provenance drill-down, and the high-QPS sampling
adaptation. The `eng-os-observability` skill keeps the metrics that feed it.

Scale note: always-inline full metadata doesn't hold up at high query-per-second volumes; see the
scale caveat in `references/observability-ui.md` for the full explanation and acceptable
adaptations (sampling, on-demand/drill-down).

## Specification Lifecycle

- **Versioning**: every `.ids` file carries a version in its metadata header, bumped on any section change (a GUARDRAILS edit is a behavior change even if the output schema is unchanged, and so is a GUIDELINES or FEW SHOT EXAMPLES edit). The harness logs the spec version on every inference; rollback is a redeploy of a prior version, not an edit.
- **Evaluation harness**: every spec names its versioned fixture set and thresholds (schema compliance rate, constraint violation rate, determinism rate over N runs). The evaluation runs in CI on every spec, model, or provider change; a regression blocks promotion; results go to the evaluation log.
- **Cost and latency budget**: every spec declares maximum input tokens, maximum output tokens, and a p95 latency target sized from the Scale Targets (calls per day times tokens per call is the monthly spend). The harness enforces the ceilings and emits actual counts as metrics; exceeding the budget is a failed evaluation.
- Failure mode: two added few-shot examples double input tokens on a path called a million times a day, and the first signal is the invoice.

## References

- `../../micro/templates/ai-ids-template.md`: copy-pasteable blank spec template with file metadata and author review checklist
- `../../meso/ai-ids-template.md`, section "Worked Example: Incident Summary Generation": fully populated worked example, every section filled for a concrete production use case
- `references/example.md`: the same worked example with its metadata block, a conflict resolved under the authority rules, and its evaluation fixtures

## Definition of Done

An IDS spec is complete when:

All items are Per change: this domain has no Standing (release and audit) items.

- [ ] the Author Review Checklist above passes; it covers the spec text itself: all eleven sections, the three orders, the contracts, and the metadata fields
- [ ] outputs are validated against the output contract before downstream use
- [ ] the harness logs the spec version on every inference
- [ ] the evaluation runs in CI on every spec, model, or provider change, against the fixtures and thresholds the metadata names
- [ ] the harness enforces the token budget the metadata declares and emits the actual counts as metrics
- [ ] the observability exposure the metadata declares is implemented, per the Observability UI Contract above and `references/observability-ui.md`
