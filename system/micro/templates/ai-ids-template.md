# AI-IDS Specification — [Task Name]

**Authors:** Haresh V. Parekh

## File Metadata

```
Name:     [kebab-case-task-name]          # matches the .ids filename
Version:  1.0
Status:   Draft | Review | Approved
Owner:    [name or team]
Created:  [YYYY-MM-DD]
Updated:  [YYYY-MM-DD]
```

---

## How to Use

Copy this file to `ids/<task-name>.ids`. Populate every section before deployment.
For section-by-section guidance, see `meso/ai-ids-template.md`.
For file placement and harness conventions, see `micro/project-structure.md` Section 4.

**Precedence order (highest to lowest):** GUARDRAILS → OBJECTIVE → DERIVED LOGIC → REASONING POLICY → ASSUMPTIONS → STRUCTURE OF OUTPUT → STRUCTURE OF INPUT → ROLE → GUIDELINES & INSTRUCTIONS → FEW SHOT EXAMPLES → DEFINITIONS

---

## DEFINITIONS

```
[Term]   — [execution-time meaning]
[Term]   — [execution-time meaning]
```

*Define terms whose meaning affects logic or constraints. Do not add instructions here.*

---

## ROLE

```
[One paragraph. Describe the system's responsibility, operational context,
and the perspective the output should take.]
```

---

## OBJECTIVE

```
[One sentence. The single measurable outcome this system must achieve.]
```

---

## GUARDRAILS

```
1. [Hard constraint — if violated, output is unacceptable]
2. [Hard constraint]
3. [Hard constraint]
```

*If something belongs in GUIDELINES, it is not a guardrail. Move it.*

---

## STRUCTURE OF INPUT

```
Required:
  [field_name]   [type]   [description]
  [field_name]   [type]   [description]

Optional:
  [field_name]   [type]   [description; behavior when absent]
```

---

## STRUCTURE OF OUTPUT

```
{
  "[field]": [type],    // [description]
  "[field]": [type],    // [description]
}
```

Determinism boundary: [Describe what "equivalent inputs" means for this task and what structural equivalence the output must satisfy. Example: equivalent inputs → structurally identical JSON after normalization; surface phrasing may vary.]

---

## DERIVED LOGIC

```
1. [First deterministic step]
2. [Second deterministic step]
3. [...]
```

*Write as a finite ordered sequence. No vague judgment. No branching without explicit conditions.*

---

## ASSUMPTIONS

```
1. If [condition], assume [bounded value or fallback].
2. If [condition], assume [bounded value or fallback].
```

*Only allowed inference goes here. Unbounded reasoning is not an assumption: it is a guardrail violation.*

---

## REASONING POLICY

```
1. If [ambiguous condition], [resolution rule].
2. If [tie], prefer [ordering criterion].
```

*Tie-breaking and prioritization only. No new constraints. No new assumptions.*

---

## GUIDELINES & INSTRUCTIONS

```
- [Tone or phrasing preference]
- [Readability guidance]
- [Presentation preference]
```

*Influence only, not authority. Hard constraints belong in GUARDRAILS.*

---

## FEW SHOT EXAMPLES

```
Input:
  [field]: [value]
  [field]: [value]

Output:
{
  "[field]": "[value]"
}
```

*Examples illustrate intended shape. They are not authoritative. GUARDRAILS and DERIVED LOGIC take precedence over any pattern observed here.*

---

## Author Review Checklist

Run before marking this spec ready for deployment.

- [ ] All important terms defined in DEFINITIONS
- [ ] Exactly one primary objective stated
- [ ] All hard constraints in GUARDRAILS: none hidden in GUIDELINES or examples
- [ ] Input contract explicit with types and required/optional distinction
- [ ] Output contract explicit with field types and determinism boundary stated
- [ ] All deterministic logic in DERIVED LOGIC as a finite ordered sequence
- [ ] All allowed assumptions bounded: no open-ended inference permitted
- [ ] Ambiguity resolution explicit in REASONING POLICY
- [ ] FEW SHOT EXAMPLES could be removed without changing system requirements
- [ ] Prompt registry entry created in `docs/prompts/<name>.md`
- [ ] If any pre-processing gate (skip conditions) or post-processing step exists outside this
      call, the spec names it and points to where it lives, without absorbing its logic

---

## Scope

- Level: Micro
- Layer: templates
- Applies To: Every AI task requiring bounded, deterministic behavior
- See Also: `meso/ai-ids-template.md`; section-by-section guidance and worked example
