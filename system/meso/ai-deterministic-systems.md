# AI Deterministic Systems

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for building production AI systems whose behavior is bounded, reviewable, and operationally reliable through explicit instruction architecture.

### What This Is Not
- not a general prompt-writing guide
- not a model-training guide
- not a guarantee that the underlying runtime is perfectly deterministic

## Scope
- Level: Meso
- Applies To: Production AI systems that require reliability, reviewability, and explicit behavior control

---

## Applied Principles

### Explicitness Over Implicitness
All meaningful behavior should be specified, not inferred accidentally. This includes what
happens around the model call, not only inside it: a decision made **before** the model is
called (should it be called at all, what subset of data should it see) or **after** it responds
(arithmetic on its output, a lookup, a threshold classification) is pre-processing or
post-processing, not part of the spec's own contract, so it correctly lives outside DEFINITIONS
through FEW SHOT EXAMPLES. Correctly keeping that logic out of the spec is not the same as
leaving no trace of it: a spec that can silently be skipped, or whose output is silently
transformed afterward, is implicit behavior even when every section it does contain is
individually explicit. The fix is a pointer, not absorption: DEFINITIONS (or a short dedicated
subsection) names that a pre-processing gate or post-processing step exists, in one or two
sentences, and says where the real logic lives, without restating the condition or duplicating
the logic into the spec's own authoritative sections.

### Determinism Within Defined Boundaries
Equivalent inputs should produce equivalent outputs within an explicit boundary.

### Contracts as Source of Truth
Input and output schemas must be explicit and validated.

### Validation at Boundaries
Generated outputs must be validated before use.

### Bounded Inference for AI Systems
Assumptions and reasoning must be explicit and limited.

### Observability as a First-Class Concern
AI correctness and variance must be measurable.

---

## Why AI-IDS Exists

Informal prompts frequently mix:
- intent
- preference
- constraints
- inference
- style
- computation

This causes ambiguity, weak reviewability, and unstable behavior.
AI-IDS separates these concerns into explicit sections with defined semantics, precedence, and execution dependency.

---

## Production Evidence

AI-IDS has been empirically evaluated in a production-validated media retrieval pipeline, deployed across more than 400,000 video productions and 7.2 million keyword generations.

Controlled evaluation: 9 articles, 161 sentences, 25 repeated executions.

| Metric | Baseline | AI-IDS | Change |
|---|---|---|---|
| Composite operational consistency | 0.12363 | 0.35985 | +23.6 pp |
| Operational error rate | 2.2% | 0% | −100% |
| Lexical consistency (Jaccard) | 0.446 | 0.569 | +12.2% |
| Iterations to production-grade output | 17.1 | 4.1 | −76% |

Key finding: runtime controls alone (temperature, model selection) were insufficient to close the gap. The ablation showed temperature reduction improved baseline consistency from 0.311 to 0.427, but AI-IDS at the same runtime settings reached 0.359. Structural separation contributed independently to operational consistency beyond what decoding parameters provided.

The zero error rate was not an aggregate artifact; it held in every individual iteration across all 25 rounds, compared to a baseline error rate that ranged from 1.1% to 3.5% per iteration.

Reference: Parekh, H.V. *AI Instruction Design Set (AI-IDS): A Structured Instruction Architecture for High Determinism and Low Operational Variance in Production AI Systems* (arXiv: cs.AI, cs.CL, cs.SE).

---

## AI-IDS Section Model

### Core Profile
These sections are required in all conformant specifications:
- DEFINITIONS
- ROLE
- OBJECTIVE
- GUARDRAILS
- STRUCTURE OF INPUT
- STRUCTURE OF OUTPUT
- GUIDELINES & INSTRUCTIONS

### Extended Profile
These sections are conditional and used when specific behavior is required:
- DERIVED LOGIC
- ASSUMPTIONS
- REASONING POLICY
- FEW SHOT EXAMPLES

---

## Section Semantics

### DEFINITIONS
Defines execution-time meaning of terms.

### ROLE
Defines system perspective, scope, and responsibility.

### OBJECTIVE
Defines the single intended outcome.

### GUARDRAILS
Defines non-negotiable constraints and failure conditions.

### STRUCTURE OF INPUT
Defines the input contract.

### STRUCTURE OF OUTPUT
Defines output contract and determinism boundary.

### DERIVED LOGIC
Defines explicit deterministic computation.

### ASSUMPTIONS
Defines explicitly allowed inference for incomplete inputs.

### REASONING POLICY
Defines deterministic ambiguity resolution.

### GUIDELINES & INSTRUCTIONS
Provides non-authoritative guidance that may influence phrasing but not override constraints or logic.

### FEW SHOT EXAMPLES
Provides illustrative examples that are non-authoritative.

---

## Authoritative Precedence Order

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

### Important Distinction
Section ordering in a document is not the same as runtime dependency or authority.
Semantics define meaning.
Precedence defines conflict resolution.
Execution dependency defines runtime flow.

---

## Execution Dependency Chain

1. Resolve definitions and role
2. Fix intended scope and objective
3. Apply guardrails
4. Validate input contract
5. Apply allowed assumptions where inputs are incomplete
6. Resolve ambiguity using reasoning policy
7. Execute derived logic deterministically
8. Enforce output contract
9. Allow guidelines and examples to influence phrasing only where they do not conflict with any higher section

---

## Determinism Strategy

Determinism is enforced through:
- explicit section semantics
- explicit precedence
- bounded inference
- deterministic derivation
- schema-constrained outputs
- runtime controls
- post-generation normalization

Runtime controls such as low temperature or fixed seeds reduce variance, but do not replace specification quality.

---

## AI Design Patterns

### Validation Layer
Always validate output before downstream use.

#### Why
An apparently plausible response can still violate contract or safety requirements.

#### Failure Mode
Invalid structured output corrupts downstream systems.

---

### Normalization Layer
Normalize output after generation when contract stability matters.

#### Examples
- trim whitespace
- canonicalize ordering
- deduplicate repeated items
- schema validation

#### Failure Mode
Equivalent outputs appear inconsistent because normalization is missing.

---

### Spec-Driven Generation
Use a structured specification instead of a free-form prompt.

#### Why
Separates constraints, logic, examples, and style into reviewable parts.

#### Failure Mode
A single free-form prompt becomes unreviewable and fragile.

---

### Bounded Assumptions
Declare exactly what may be inferred when inputs are incomplete.

#### Why
Prevents silent invention of unsupported content.

#### Failure Mode
The system hallucinates or fills gaps inconsistently.

---

## Common Failure Modes

### Undeclared Assumptions
Symptom: inconsistent outputs across similar inputs
Cause: inference not bounded explicitly

### Missing Guardrails
Symptom: unsafe or policy-violating outputs
Cause: constraints are weak or absent

### Hidden Computation
Symptom: output contains unexpected transformations
Cause: logic is embedded implicitly in prose rather than derived logic

### Undocumented Processing Boundary
Symptom: a spec reader cannot tell the call is sometimes skipped, or that its output is
transformed afterward, without reading the calling code
Cause: pre-processing (call-gating logic) or post-processing (arithmetic, lookups on the
model's output) correctly lives outside the spec, but the spec has no pointer to where it lives
or what condition it applies

### Example-Driven Authority
Symptom: model imitates examples even when they conflict with requirements
Cause: examples are treated as rules

### Weak Output Contract
Symptom: structurally inconsistent results
Cause: output schema is underspecified

---

## Observability for AI Systems

Track at minimum:
- determinism rate
- schema compliance rate
- constraint violation rate
- output variance
- validation failure rate
- assumption usage frequency where important

These are not optional if AI output affects downstream systems.

### Observability UI Contract

Measurability is a runtime concern; declaring what must be measurable is a spec-authoring
concern, and the two are easy to conflate. An AI-IDS spec must declare, as part of its output
contract, what the implementing harness has to expose for observability:

- scorer/spec name and version
- timestamp of the inference
- input and output token counts

This is a contract-declaration requirement, not a UI specification: the spec states what must be
exposed; it does not describe how it is rendered. For the UI pattern that consumes this
declaration (the Scoring Run indicator and its provenance drill-down, plus the scale caveat for
high-QPS systems), see `observability.md`'s "AI-IDS Observability UI" section.

---

### Scoring Run Indicator and Provenance Drill-Down

Backend metrics satisfy the engineering team. They do not satisfy the person looking at an
AI-generated result on a screen. When AI output reaches an end user directly (a grade, a
recommendation, a summary) the observability contract extends to that surface: the user (or the
support engineer looking over their shoulder) needs to see where the result came from without
filing a ticket to have someone query a trace.

#### Pattern: Scoring Run Indicator

Every live AI inference call exposed to an end user must surface, at the point of use, a compact
provenance indicator, not buried in a log viewer or an admin-only page. At minimum it shows:

- scorer or model name (and version, if the system is spec-driven)
- timestamp of the inference
- input and output token counts

For systems built on AI-IDS specifically, the indicator must also support an on-demand
drill-down into full provenance: which ROLE, OBJECTIVE, GUARDRAILS, and input values produced
this exact output. The drill-down is reachable directly from the result: a "view provenance"
affordance next to it, not a separate lookup requiring the viewer to already know the `trace_id`.

```
// render alongside the AI-generated result, not in a separate dashboard
function renderScoringRunIndicator(run_id, model, timestamp, input_tokens, output_tokens):
    display({
        scorer:    model,
        run_at:    timestamp,
        tokens:    input_tokens + " in / " + output_tokens + " out",
    })
    onClick("view_provenance", () => fetchProvenance(run_id))

// full provenance is looked up on demand — not pre-rendered by default
function fetchProvenance(run_id):
    record = provenanceStore.get(run_id)
    return {
        role:       record.role,
        objective:  record.objective,
        guardrails: record.guardrails,
        input:      record.input,
        output:     record.output,
    }
```

#### Example

A dataset-quality scorer grades an uploaded dataset. The result "Quality grade: B+" is shown with
an inline indicator:

```
Scorer: dataset-quality-assessor v1.2
Run at: 2026-07-01 14:32:07 UTC
Tokens: 412 in / 89 out
[ View provenance ]
```

"View provenance" opens the ROLE, OBJECTIVE, GUARDRAILS, and exact input/output for that run,
reachable from the result itself, with no manual `trace_id` correlation required.

#### Failure Mode
An AI-generated result with no visible provenance is unauditable. It erodes user trust the moment
it is wrong once: with no way for the user or support to inspect what produced it, every
subsequent result becomes suspect too, even the correct ones.

#### Scale Boundary

Always rendering full inline Scoring Run metadata on every result does not scale at high
query-per-second volumes: a real-time feed scorer running at thousands of QPS cannot afford a
full inline card on every item without flooding both the UI and the metadata backend. This is a
real boundary condition, not a corner case to design around later.

Acceptable adaptations at scale:
- sample a subset of results for full inline detail (e.g., 1 in 200) rather than every result
- make full provenance available on-demand by `run_id` lookup for any result, sampled or not,
  rather than pre-rendering it inline

Either adaptation preserves the rule's intent (provenance must remain reachable) without paying
the inline-rendering cost on every request. Silently dropping provenance entirely at scale, rather
than adapting how it's surfaced, is not an acceptable trade-off.

(The signal design that feeds this UI lives in `meso/observability.md`.)

## Specification Lifecycle

### Versioning

Every `.ids` file carries a version in its metadata header, bumped on any change to a Core
Profile section (a GUARDRAILS edit is a breaking change to the system's behavior even if the
output schema is unchanged). The harness logs the spec version on every inference so an output
can always be attributed to the exact spec text that produced it. Old versions are retained in
version control and in the prompt registry; a rollback of a spec is a redeploy of a prior
version, not an edit.

### Evaluation Harness Linkage

Every spec names its evaluation fixture set (versioned inputs with expected structural
properties) and the thresholds it must meet: schema compliance rate, constraint violation rate,
determinism rate across N repeated runs. The evaluation runs in CI on every spec change and on
every model or provider change; a regression below threshold blocks promotion. The results are
appended to the evaluation log (`meso/documentation.md` 2.5).

### Cost and Latency Budget

Every spec declares a per-call budget: maximum input tokens, maximum output tokens, and a p95
latency target, sized from the Scale Targets (calls per day multiplied by tokens per call is
the monthly spend). The harness enforces the token ceilings and emits the actual counts as
metrics. Exceeding the budget is a failed evaluation, not a surprise on the invoice.

- Failure mode: a spec edit that adds two few-shot examples doubles input tokens on a path
  called a million times a day; with no budget, the first signal is the bill.

## Definition of Done

An AI deterministic system is ready when:
- IDS sections are complete and semantically correct
- precedence and execution behavior are clear
- input and output contracts are explicit
- bounded inference is declared where needed
- deterministic logic is explicit where needed
- outputs are validated before downstream use
- correctness and variance are measurable
- the output contract declares what must be exposed for observability (scorer/spec name and version, timestamp, and token counts) per the Observability UI Contract
- the spec carries a version, bumped on any Core Profile change, and the harness logs it per inference
- the spec names its evaluation fixtures and thresholds, and the evaluation runs in CI on spec, model, or provider change
- the spec declares input/output token ceilings and a p95 latency target derived from the Scale Targets, enforced by the harness
