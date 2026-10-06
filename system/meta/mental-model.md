# Mental Model

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
The conceptual model for how the Engineering OS is structured and how its layers work together.

### What This Is Not
- not a glossary
- not a design guide
- not a template

## Scope
- Level: Meta
- Applies To: Entire Engineering OS

---

## Layer Model

See `meta/architecture.md` for a visual diagram of the four-layer structure.

### Meta
Defines language, structure, and authoring discipline.
Files in this layer explain how the OS should be understood and maintained.

### Macro
Defines non-negotiable rules and system evaluation dimensions.
Files in this layer constrain decisions across all domains.

### Meso
Defines design guidance for specific domains.
Files in this layer translate principles into patterns, architecture, and trade-offs.

### Micro
Defines execution artifacts.
Files in this layer help engineers build, review, and operationalize systems.

---

## Relationship Between Layers

- Meta defines how to read and write the system
- Macro constrains what is acceptable
- Meso translates macro constraints into domain-specific design choices
- Micro supports implementation and review

---

## Flow of Work

1. Understand the problem and domain
2. Use Meta to align language and structure
3. Use Macro to identify constraints and trade-offs
4. Use Meso to choose patterns and architecture
5. Use Micro to implement and review
6. Capture friction and feed improvements back into Meso, Macro, or Meta as needed

---

## AI Systems Within the Model

AI systems follow the same layered model, but with an additional execution chain:

Input -> Instruction Specification (IDS) -> Model -> Validation -> Output

Determinism is not achieved at the model layer alone.
It is achieved by:
- explicit instruction structure
- bounded inference
- deterministic derivation
- output validation
- runtime controls
- normalization

---

## Key Insight

A strong engineering system requires all four of the following:
- clear language
- clear rules
- clear design guidance
- clear execution artifacts

If any one of these is weak, the overall system drifts.
