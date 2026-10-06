# AI-IDS Template

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guided template for authoring an AI-IDS specification that engineers and AI agents can use consistently.

### What This Is Not
- not a free-form prompt
- not a style guide
- not a place to hide logic in examples

## Scope
- Level: Meso
- Applies To: Any production AI task requiring explicit behavior and bounded variability

---

## Applied Principles

- **Explicitness over implicitness.** Every term the instructions depend on is defined in DEFINITIONS; a term left implicit is read differently by each model and each author.
- **Determinism within defined boundaries.** STRUCTURE OF OUTPUT and DERIVED LOGIC fix what the model may vary and what it may not; anything outside those boundaries belongs in code.
- **Bounded inference for AI systems.** GUARDRAILS and REASONING POLICY state what the model must not infer, so a gap in the input produces a refusal or a flag rather than a guess.

## How to Use This Template

1. Define meaning before behavior
2. Define the single outcome before style or examples
3. Put hard constraints in guardrails, not guidelines
4. Put contracts in input/output sections, not prose
5. Put deterministic logic in derived logic only
6. Put allowed inference in assumptions only
7. Put ambiguity resolution in reasoning policy only
8. Use guidelines and examples only as influence, never authority

---

## Template

### DEFINITIONS
Define execution-time meaning of important terms.

#### What Belongs Here
- domain terms
- special terms used later
- terms whose meaning affects logic or constraints
- a one- or two-sentence pointer to a pre-processing gate or post-processing step that exists
  outside this spec, naming where the real logic lives, if one applies (see the Worked Example
  below); the condition itself is not restated here, only that it exists and where

#### What Does Not Belong Here
- instructions
- constraints
- style guidance
- the pre-processing or post-processing logic itself, restated or duplicated: DEFINITIONS points
  to it, it does not absorb it

#### Prompting Guidance
Define "customer impact", "sensitive data", or "priority level" before using those terms elsewhere.

---

### ROLE
Define the system perspective, scope, and responsibility.

#### What Belongs Here
- the system's responsibility
- the operational context
- the perspective the output should take

#### What Does Not Belong Here
- style preferences
- output structure
- business wish lists

---

### OBJECTIVE
Define the single measurable outcome.

#### What Belongs Here
- one intended result
- one success definition

#### What Does Not Belong Here
- multiple unrelated goals
- optional preferences
- complex branching logic

---

### GUARDRAILS
Define non-negotiable constraints and failure conditions.

#### What Belongs Here
- forbidden content
- policy constraints
- safety constraints
- disclosure limitations

#### What Does Not Belong Here
- optional style guidance
- soft preferences
- computation steps

#### Rule
If violating a statement should make the output unacceptable, it belongs here.

---

### STRUCTURE OF INPUT
Define the input contract.

#### What Belongs Here
- required fields
- optional fields
- field meaning when needed
- scope of acceptable input

#### What Does Not Belong Here
- hidden assumptions about undeclared input
- business logic
- output formatting

---

### STRUCTURE OF OUTPUT
Define the output contract and determinism boundary.

#### What Belongs Here
- schema or shape
- required fields
- ordering requirements
- cardinality limits
- determinism expectations

#### What Does Not Belong Here
- style-only guidance
- hidden business logic
- assumptions

---

### DERIVED LOGIC
Define ordered deterministic computation.

#### What Belongs Here
- normalization steps
- extraction steps
- filtering steps
- ordering rules
- truncation rules
- fallback behavior
- named constants or thresholds when required

#### What Does Not Belong Here
- vague judgment
- hidden computation embedded in prose elsewhere
- probabilistic selection rules without explicit boundary

#### Rule
Write derived logic as a finite ordered sequence.

---

### ASSUMPTIONS
Define explicitly allowed inference when inputs are incomplete.

#### What Belongs Here
- allowed fallback interpretations
- bounded inferred values
- conditions under which inference is permitted

#### What Does Not Belong Here
- broad unbounded reasoning
- guesses not grounded in input
- preference rules

---

### REASONING POLICY
Define deterministic ambiguity resolution.

#### What Belongs Here
- tie-breaking logic
- resolution ordering
- prioritization rules among allowed interpretations

#### What Does Not Belong Here
- new constraints
- new input assumptions
- style guidance

---

### GUIDELINES & INSTRUCTIONS
Define non-authoritative influence on phrasing or presentation.

#### What Belongs Here
- tone
- clarity preferences
- readability guidance
- presentation preferences

#### What Does Not Belong Here
- hard constraints
- deterministic logic
- assumptions
- output schema rules

---

### FEW SHOT EXAMPLES
Provide illustrative input/output pairs where useful.

#### What Belongs Here
- examples that help phrasing
- examples that demonstrate the intended shape

#### What Does Not Belong Here
- rules that exist only in examples
- authoritative constraints
- hidden logic not written elsewhere

---

## Worked Example — Incident Summary Generation

This example shows every section populated for a concrete production use case: generating an external-facing summary of a resolved service incident.

---

### DEFINITIONS

```
Customer Impact    — a degradation in service availability, response time, or data correctness
                     visible to end users or downstream consumers.
Severity Level     — P1 (total outage), P2 (partial outage), P3 (degraded performance).
Resolution         — the incident is resolved when the root cause is remediated and
                     service metrics return to within SLA thresholds.
Sensitive Data     — internal system names, employee names, vendor identities,
                     cost figures, and unreleased product details.
Pre-processing gate — if `end_time` is null (the incident is still ongoing), the caller skips
                     this call entirely rather than asking the model to summarize an unresolved
                     incident; see `incident-service`'s `isResolved()`.
```

---

### ROLE

```
External incident communication component for a production SaaS platform.
Produces customer-facing summaries of resolved incidents suitable for
publication in a customer status page or incident report.
Perspective: vendor communicating transparently with affected customers.
```

---

### OBJECTIVE

```
Produce a single structured incident summary that accurately describes what
happened, what the customer impact was, and what was done to resolve it,
in plain language suitable for a non-technical audience.
```

---

### GUARDRAILS

```
1. Must not include internal system names, team names, or employee names.
2. Must not include root cause hypotheses not confirmed in the incident report.
3. Must not include cost figures, SLA credit amounts, or financial exposure estimates.
4. Must not include speculative language about future incidents ("this won't happen again").
5. Must not include technical implementation details beyond what is needed to explain customer impact.
6. If customer impact is not determinable from the input, the summary must state
   "impact is under investigation"; it must not invent an impact statement.
```

---

### STRUCTURE OF INPUT

```
Required:
  incident_id       string     unique identifier for the incident
  severity          enum       P1 | P2 | P3
  start_time        datetime   ISO 8601
  end_time          datetime   ISO 8601; null if not yet resolved
  affected_services list       one or more service names (customer-facing names only)
  customer_impact   string     description of what customers experienced; may be null

Optional:
  root_cause        string     confirmed root cause; may be null if still under investigation
  resolution_steps  string     what was done to restore service
  timeline          list       key events with timestamps
```

---

### STRUCTURE OF OUTPUT

```
{
  "incident_id":      string,
  "severity":         string,         // P1 | P2 | P3
  "duration_minutes": integer,        // derived from start_time and end_time
  "summary":          string,         // 2–4 sentences; plain language; no markdown
  "customer_impact":  string,         // one sentence; what customers experienced
  "root_cause":       string | null,  // one sentence; null if not confirmed
  "resolution":       string,         // one sentence; what restored service
  "status":           string          // "resolved" | "monitoring" | "investigating"
}
```

Determinism boundary: equivalent inputs produce structurally identical JSON after normalization. Surface phrasing may vary; field presence and values must not.

---

### DERIVED LOGIC

```
1. Compute duration_minutes = (end_time - start_time) in whole minutes.
   If end_time is null, set status = "investigating" and duration_minutes = null.

2. Set status:
   - "resolved" if end_time is present and resolution_steps is present
   - "monitoring" if end_time is present but resolution_steps is absent
   - "investigating" if end_time is null

3. Build customer_impact:
   - if customer_impact input is present: normalize to one sentence, strip internal terms
   - if customer_impact input is null: set to "Impact is under investigation."

4. Build root_cause:
   - if root_cause input is present: normalize to one sentence
   - if root_cause input is null: set field to null

5. Build summary: combine severity, duration, affected services, and customer_impact
   into 2–4 plain-language sentences. Do not add information not present in the input.

6. Validate output against STRUCTURE OF OUTPUT schema before returning.
   Reject and raise if any required field is missing or violates its constraint.
```

---

### ASSUMPTIONS

```
1. If severity is not provided, assume P2.
2. If affected_services contains internal names not recognizable to customers,
   replace with "one or more platform services."
3. If timeline is provided but root_cause is not, do not infer root_cause from timeline events.
```

---

### REASONING POLICY

```
1. If the input contains conflicting descriptions of customer impact, use the
   more conservative (broader) statement.
2. If duration_minutes is less than 1, report as "less than one minute."
3. If multiple resolution steps are listed, summarize as a single action describing
   the primary restoration action; do not enumerate all steps.
```

---

### GUIDELINES & INSTRUCTIONS

```
- Use plain language. Assume the reader is a non-technical customer.
- Prefer active voice.
- Avoid jargon: "our infrastructure" not "our Kubernetes cluster."
- Be factual and neutral in tone: neither apologetic nor dismissive.
- Keep the summary field under 100 words.
```

---

### FEW SHOT EXAMPLES

```
Input:
  severity: P1
  start_time: 2026-05-30T09:00:00Z
  end_time: 2026-05-30T10:12:00Z
  affected_services: ["Order API"]
  customer_impact: "Customers were unable to place orders."
  root_cause: "A configuration change caused the order routing layer to reject all requests."
  resolution_steps: "The configuration change was reverted."

Output:
{
  "incident_id": "INC-2026-0530",
  "severity": "P1",
  "duration_minutes": 72,
  "summary": "On May 30, 2026, the Order API experienced a P1 outage lasting 72 minutes. Customers were unable to place orders during this period. The issue was caused by a configuration change that was subsequently reverted to restore service.",
  "customer_impact": "Customers were unable to place orders.",
  "root_cause": "A configuration change caused the order routing layer to reject all requests.",
  "resolution": "The configuration change was reverted.",
  "status": "resolved"
}
```

Note: this example illustrates the intended shape and tone. It is not authoritative. Guardrails and derived logic take precedence over any pattern observed in this example.

---

## Failure Modes

- **Worked example copied verbatim.** The Incident Summary example shows shape, not content; a spec that keeps its terms, thresholds, or few-shot examples describes a different system.
- **Empty or implicit DEFINITIONS.** Terms the spec uses but never defines are interpreted per call, so the same input yields different results across runs and models.
- **Logic hidden in examples.** A rule that exists only in a FEW SHOT EXAMPLE is not a rule the validator or a reviewer can find; state it in DERIVED LOGIC or GUIDELINES.
- **Undocumented processing boundary.** A pre-processing gate or post-processing step in the calling code that the spec never points to (ledger E-28); the spec must name it and say where it lives.

## Author Review Checklist

- [ ] Are all important terms defined in DEFINITIONS?
- [ ] Is there exactly one primary objective?
- [ ] Are all hard constraints in GUARDRAILS, not in GUIDELINES?
- [ ] Are input and output contracts explicit with types and required/optional distinction?
- [ ] Is deterministic logic written only in DERIVED LOGIC as an ordered sequence?
- [ ] Are allowed assumptions bounded explicitly, no open-ended inference?
- [ ] Is ambiguity resolution explicit in REASONING POLICY?
- [ ] Could FEW SHOT EXAMPLES be removed without changing system requirements?
- [ ] Does the output schema include a determinism boundary statement?
- [ ] If any pre-processing gate (skip conditions) or post-processing step exists outside this
      call, does the spec name it and point to where it lives, without absorbing its logic?

---

## Definition of Done

An IDS spec is complete when:
- semantics are explicit
- constraints are explicit
- contracts are explicit
- allowed inference is bounded
- deterministic logic is visible
- examples are optional rather than authoritative
