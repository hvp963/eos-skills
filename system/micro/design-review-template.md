# Design Review Template

**Authors:** Haresh V. Parekh

## Purpose
Use this template to review whether a system design is complete, consistent, and operationally credible.

## Applies To
- service designs
- data systems
- AI systems
- architectural changes

---

## 1. Problem Definition
- What problem is being solved?
- What is explicitly out of scope?
- What quality attributes matter most?

---

## 2. Boundaries and Model
- Has the system been modeled at least to C4 Context and Container level?
- Are ownership boundaries explicit?
- Are inputs and outputs explicit?

---

## 3. Principles Check
- Is behavior explicit?
- Is idempotency addressed where retries or replays exist?
- Are contracts explicit?
- Is validation performed at boundaries?
- Is fault isolation addressed?
- Is partitioning addressed where scale matters?
- If AI is involved, is inference bounded?

---

## 4. Patterns Check
- What design patterns are being used?
- Why were these patterns chosen?
- What obvious alternatives were rejected and why?

---

## 5. Failure Modes
- What are the top likely failure modes?
- What is the blast radius of each?
- What prevents cascading failure?

---

## 6. Observability
- What metrics will prove the system is healthy?
- What logs or traces are required for diagnosis?
- If AI is used, what correctness or variance metrics are defined?

---

## 7. Contracts and Validation
- Are schemas or contracts explicit?
- Is versioning addressed?
- Are invalid inputs and outputs rejected meaningfully?

---

## 8. Decision
- Approve
- Approve with changes
- Rework required

## Output
A completed review should result in explicit action items, not vague concerns.
