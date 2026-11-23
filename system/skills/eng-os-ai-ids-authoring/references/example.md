Copied from `meso/ai-ids-template.md` Worked Example; canon wins on any difference.

# Worked Example: Incident Summary Spec, Complete

The Incident Summary Generation spec from the canon, shown as a deployable `.ids` file: its
metadata block (every field the template requires), all eleven sections, one conflict resolved
under the authority rules, and the evaluation fixtures the metadata points to.

## File Metadata

```
Name:       incident-summary                # ids/incident-summary.ids
Version:    1.3                             # bumped on any section change
Status:     Approved
Owner:      platform-comms
Created:    2026-05-30
Updated:    2026-11-22
Version-bump rule: any section change
Evaluation: tests/ids/incident-summary/fixtures/; thresholds schema>=1.00, violations<=0, determinism>=0.95 over 10 runs
Budget:     max_input_tokens=1500, max_output_tokens=400, p95_ms=2500   # 2,000 calls/day from Scale Targets
Exposes:    spec name+version, timestamp, token counts, provenance (Observability UI Contract)
Accepts classification: Public, Internal    # incident records carry no Confidential fields
```

## Specification

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
  end_time          datetime   ISO 8601; never null: the pre-processing gate skips unresolved incidents
  affected_services list       one or more service names; internal names are normalized in DERIVED LOGIC step 1
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
  "status":           string          // "resolved" | "monitoring"
}
```

Determinism boundary: equivalent inputs produce structurally identical JSON after normalization. Surface phrasing may vary; field presence and values must not.

---

### DERIVED LOGIC

```
CUSTOMER_FACING_SERVICES = ["Order API", "Checkout", "Account Portal", "Status Page"]

1. Normalize affected_services: keep each name in CUSTOMER_FACING_SERVICES; replace every
   other name with "one or more platform services", listed once.

2. Compute duration_minutes = (end_time - start_time) in whole minutes.

3. Set status:
   - "resolved" if resolution_steps is present
   - "monitoring" if resolution_steps is absent

4. Build customer_impact:
   - if customer_impact input is present: normalize to one sentence, strip internal terms
   - if customer_impact input is null: set to "Impact is under investigation."

5. Build root_cause:
   - if root_cause input is present: normalize to one sentence
   - if root_cause input is null: set field to null

6. Build summary: combine severity, duration, normalized affected services, and customer_impact
   into 2–4 plain-language sentences. Do not add information not present in the input.

7. Validate output against STRUCTURE OF OUTPUT schema before returning.
   Reject and raise if any required field is missing or violates its constraint.
```

---

### ASSUMPTIONS

```
1. If timeline is provided but root_cause is not, do not infer root_cause from timeline events.
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
  incident_id: INC-2026-0530
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

## A Conflict Resolved by Authority

A draft of this spec added a GUIDELINES line: "Name the component that failed, so customers
understand the cause." It conflicts with GUARDRAILS 5, which forbids technical implementation
details beyond what is needed to explain customer impact. Under the authority rules, GUARDRAILS
holds the highest constraint authority and guidance never overrides a constraint, so GUARDRAILS
governs. The rules settle which section wins, but leaving both lines in place would leave the
model to resolve the tension on every call, so the author rewrote the guideline as "Describe
what customers experienced, not which component failed" and the two sections now agree. The
checklist row "No two sections give different instructions for the same case unless the
authority rules settle which governs" is the one that catches this draft.

## Evaluation Fixtures

The fixture set `tests/ids/incident-summary/fixtures/` named in the metadata. Each fixture states
the structural property the output must have; phrasing is not compared.

| Fixture | Input | Expected structural property |
|---|---|---|
| `normal-p1` | The few-shot input above | All eight fields present; `status` is `"resolved"`; `duration_minutes` is `72` |
| `root-cause-absent` | `root_cause` omitted | `root_cause` is `null`; `summary` names no cause |
| `internal-service-name` | `affected_services: ["order-router-v2"]` | Output names "one or more platform services"; `order-router-v2` appears nowhere (DERIVED LOGIC step 1) |
| `conflicting-impact` | `customer_impact` says "some customers" and `timeline` says "all customers" | `customer_impact` uses the broader statement (REASONING POLICY 1) |
| `sub-minute` | `end_time` 40 seconds after `start_time` | `duration_minutes` is `0` and `summary` says "less than one minute" (REASONING POLICY 2) |

Thresholds: schema compliance 100% (every run validates against STRUCTURE OF OUTPUT), constraint
violations 0 (no GUARDRAILS breach in any run), determinism at least 0.95 (structural equality of
the normalized JSON across 10 runs of each fixture). The evaluation runs in CI on every spec,
model, or provider change, and a result below any threshold blocks promotion.

Each run appends one line to the evaluation log:

```
{"ts":"2026-11-22T10:04:00Z","spec":"incident-summary","version":"1.3","model":"claude-sonnet-5-5","fixtures":5,"runs":10,"schema":1.00,"violations":0,"determinism":0.98,"result":"pass"}
```
