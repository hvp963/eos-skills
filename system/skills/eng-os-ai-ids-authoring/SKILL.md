---
name: eng-os-ai-ids-authoring
description: "Use when designing, writing, or reviewing an AI system prompt/instruction set: the AI-IDS 11-section framework, section precedence, and the author review checklist."
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
with defined semantics, precedence, and execution order. Use it instead of a free-form prompt
whenever an AI system's output must be reviewable, bounded, and operationally consistent.

Empirical result (production media retrieval pipeline, 400K+ productions, 7.2M keyword
generations; controlled eval of 9 articles / 161 sentences / 25 repeated executions):
composite operational consistency +23.6pp, operational error rate 2.2% → 0%, iterations to
production-grade output 17.1 → 4.1. Structural separation contributed independently of runtime
controls (temperature, seeds); those reduce variance but do not replace specification quality.

## The 11 Sections

**Core Profile: required in every conformant spec:**

1. **DEFINITIONS**: execution-time meaning of terms used later. No instructions, constraints, or style guidance here.
2. **ROLE**: the system's responsibility, operational context, and the perspective the output should take. No style preferences or output structure here.
3. **OBJECTIVE**: the single measurable outcome. One result, one success definition; no multiple unrelated goals or branching logic.
4. **GUARDRAILS**: non-negotiable constraints and failure conditions. Rule of thumb: if violating a statement should make the output unacceptable, it belongs here, not in GUIDELINES.
5. **STRUCTURE OF INPUT**: the input contract: required/optional fields, types, meaning, acceptable scope. No hidden assumptions about undeclared input.
6. **STRUCTURE OF OUTPUT**: the output contract and determinism boundary: schema/shape, required fields, ordering, cardinality limits, and an explicit statement of what "equivalent inputs" must produce structurally.
7. **GUIDELINES & INSTRUCTIONS**: non-authoritative influence on tone, clarity, and presentation. Must never carry hard constraints, logic, or assumptions.

**Extended Profile: conditional, used when the behavior is required:**

8. **DERIVED LOGIC**: explicit deterministic computation, written as a finite ordered sequence (normalization, extraction, filtering, ordering, truncation, fallback, named constants/thresholds). No vague judgment, no computation hidden in prose elsewhere.
9. **ASSUMPTIONS**: explicitly allowed, bounded inference for incomplete inputs (allowed fallback interpretations, conditions under which inference is permitted). Never open-ended reasoning or guesses ungrounded in input.
10. **REASONING POLICY**: deterministic ambiguity resolution: tie-breaking and prioritization among already-allowed interpretations. Never introduces new constraints or new assumptions.
11. **FEW SHOT EXAMPLES**: illustrative input/output pairs. Non-authoritative: must be removable without changing system requirements. Never the sole place a rule exists.

## Authoritative Precedence Order

When sections conflict, resolve in this order (highest wins):

1. DEFINITIONS
2. ROLE
3. OBJECTIVE
4. GUARDRAILS
5. STRUCTURE OF INPUT
6. ASSUMPTIONS
7. REASONING POLICY
8. DERIVED LOGIC
9. STRUCTURE OF OUTPUT
10. GUIDELINES & INSTRUCTIONS
11. FEW SHOT EXAMPLES

Section ordering in the document is not the same as this precedence, and neither is the same
as runtime execution order. Semantics define meaning; precedence defines conflict resolution;
execution dependency defines runtime flow:

1. Resolve definitions and role
2. Fix intended scope and objective
3. Apply guardrails
4. Validate input contract
5. Apply allowed assumptions where inputs are incomplete
6. Resolve ambiguity using reasoning policy
7. Execute derived logic deterministically
8. Enforce output contract
9. Allow guidelines and examples to influence phrasing only where they don't conflict with any higher section

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

- [ ] All important terms defined in DEFINITIONS
- [ ] Exactly one primary objective stated
- [ ] All hard constraints in GUARDRAILS, none hidden in GUIDELINES or examples
- [ ] Input contract explicit with types and required/optional distinction
- [ ] Output contract explicit with field types and determinism boundary stated
- [ ] All deterministic logic in DERIVED LOGIC as a finite ordered sequence
- [ ] All allowed assumptions bounded, no open-ended inference permitted
- [ ] Ambiguity resolution explicit in REASONING POLICY
- [ ] FEW SHOT EXAMPLES could be removed without changing system requirements
- [ ] Prompt registry entry created (e.g. `docs/prompts/<name>.md`)
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
input values actually produced the displayed output, so a user or reviewer can trace an output
back to the spec sections and inputs responsible for it.

This skill owns the spec-authoring side (write ROLE/OBJECTIVE/GUARDRAILS/input structure so a run
can be attributed cleanly) and the UI pattern too: `references/observability-ui.md`
holds the Scoring Run card pattern, the provenance drill-down, and the high-QPS sampling
adaptation. The `eng-os-observability` skill keeps the metrics that feed it.

Scale note: always-inline full metadata doesn't hold up at high query-per-second volumes; see the
observability skill's scale caveat for the full explanation and acceptable adaptations (sampling,
on-demand/drill-down).

## Specification Lifecycle

- **Versioning**: every `.ids` file carries a version in its metadata header, bumped on any Core Profile change (a GUARDRAILS edit is a behavior change even if the output schema is unchanged). The harness logs the spec version on every inference; rollback is a redeploy of a prior version, not an edit.
- **Evaluation harness**: every spec names its versioned fixture set and thresholds (schema compliance rate, constraint violation rate, determinism rate over N runs). The evaluation runs in CI on every spec, model, or provider change; a regression blocks promotion; results go to the evaluation log.
- **Cost and latency budget**: every spec declares maximum input tokens, maximum output tokens, and a p95 latency target sized from the Scale Targets (calls per day times tokens per call is the monthly spend). The harness enforces the ceilings and emits actual counts as metrics; exceeding the budget is a failed evaluation.
- Failure mode: two added few-shot examples double input tokens on a path called a million times a day, and the first signal is the invoice.

## References

- `../../micro/templates/ai-ids-template.md`: copy-pasteable blank spec template with file metadata and author review checklist
- `../../meso/ai-ids-template.md`, section "Worked Example: Incident Summary Generation": fully populated worked example, every section filled for a concrete production use case

## Definition of Done

An IDS spec is complete when:
- [ ] semantics are explicit for every section used
- [ ] constraints are explicit and live only in GUARDRAILS
- [ ] input and output contracts are explicit, typed, and include a determinism boundary statement
- [ ] allowed inference is bounded (ASSUMPTIONS) and ambiguity resolution is explicit (REASONING POLICY)
- [ ] deterministic logic is visible as an ordered sequence in DERIVED LOGIC
- [ ] examples are optional/removable rather than authoritative
- [ ] outputs are validated against the output contract before downstream use
- [ ] the spec declares what must be exposed for observability (spec name/version, timestamp, token counts, and attributable ROLE/OBJECTIVE/GUARDRAILS/inputs) per the Observability UI Contract above; see the `eng-os-observability` skill for the UI implementation detail
- [ ] the spec carries a version, bumped on any Core Profile change, and the harness logs it per inference
- [ ] the spec names its evaluation fixtures and thresholds, run in CI on spec, model, or provider change
- [ ] the spec declares token ceilings and a p95 latency target from the Scale Targets, enforced by the harness
