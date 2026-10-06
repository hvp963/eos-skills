# Engineering OS — Claude Code Usage

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

Engineering standards only have value if they govern every decision, including decisions made by AI agents. Without an explicit bootstrap protocol, an AI agent reading a standards reference behaves like a new engineer who skimmed the wiki: applying some rules, missing others, and drifting progressively as context accumulates.

This document defines how Claude Code must use the Engineering OS. It covers the bootstrap sequence that must run before any code is written, the CLAUDE.md template that captures standards in every project, and the checkpoint protocol that enforces compliance throughout implementation.

---

## Definition

### What This Is
- The authoritative guide for how Claude Code interacts with and applies the Engineering OS
- A bootstrap protocol that must complete before implementation begins
- A CLAUDE.md template that is instantiated at the start of every project
- A checkpoint map that defines when each standard must be verified

### What This Is Not
- not a general AI prompting guide
- not optional: it is as binding as any other Engineering OS document
- not a substitute for reading the underlying standards: it references them; it does not replace them
- not specific to any single project or language

## Scope
- Level: Meta
- Applies To: Every project where Claude Code is used as an engineering agent
- See Also: `meta/architecture.md`, `micro/project-structure.md`, `micro/coding-standards/common.md`, `meso/documentation.md`, `meso/ai-ids-template.md`

---

## Applied Principles

### Explicitness Over Implicitness
Every standard that should govern an agent's decisions must be explicit in the project's CLAUDE.md. An agent cannot apply a standard it has not been given context for.

### Validation at Boundaries
Compliance with standards must be verified at defined checkpoints, not assumed at the end of implementation. The Definition of Done checklists are boundary checks, not retrospective audits.

### Contracts as Source of Truth
CLAUDE.md is a contract between the project and the agent. Its contents are not suggestions: they are binding for the duration of the engagement.

---

## 1. Bootstrap Protocol

The bootstrap protocol is a mandatory sequence that must complete before any code, documentation, or artifact is produced. It exists because the primary cause of standards drift is starting implementation before the standards are fully understood and captured.

**The bootstrap sequence:**

```
Step 0: Bail-out check: is this an ongoing/real software project?
  Before forcing the full CLAUDE.md template onto a codebase, check for a real
  dependency manifest (package.json, requirements.txt, pyproject.toml, go.mod,
  etc.), a real source structure (more than one file, some separation of
  concerns), and evidence the project is meant to grow over time.
  If instead this is a single hardcoded utility script with no framework and
  no intended expansion, do not force the full template's structure onto it.
  Populate a minimal CLAUDE.md where most template sections are explicitly
  marked N/A, each with a one-line reason (e.g. "N/A — single-file script, no
  screens/entities/API exist").
  Forcing false structure onto a trivial script is not harmless boilerplate:
  it actively misleads whoever reads it next into believing structure exists
  that does not.
  If the project passes this check, proceed to Step 1 in full.

Step 1: Load the Engineering OS
  With Skills support (Claude Code and any tool reading SKILL.md): ensure the
  skills are installed (tools/install.ps1 or tools/install.sh) and load
  eng-os-core; its checkpoint table routes to every other skill on demand.
  Without Skills support: read every file in meta/, macro/, meso/, micro/.
  Do not start with the files most relevant to the current task; unknown
  standards are the ones that get missed.

Step 2: Create CLAUDE.md at the project root
  Instantiate the CLAUDE.md template (Section 2 of this document)
  Populate every section; do not leave placeholders
  The CLAUDE.md must capture binding standards, not summarise them

Step 3: Confirm CLAUDE.md is complete
  Check every template section is populated
  Check every Definition of Done checklist is present
  Check the project structure section reflects the intended layout
  For a project with a UI or with operational messages, run the Architecture Practices Gate
  in skills/eng-os-bootstrap/SKILL.md: a general "populate the template" pass has proven
  insufficient on its own — thin, generic prose can fill a section without actually binding
  the project to the practice it names. The gate requires a concrete answer (an actual path,
  folder, or component name) or an explicit reasoned skip for each of: constants/messages
  sectioned by area with a project-wide message-code sequence, all user-facing strings as
  constants, business logic in the Model layer, global CSS with no hardcoded styles, the
  four-region app shell (header/footer/nav/application panel), reusable components, MVC for
  any app type, responsive breakpoints, and the config/env file location.

Step 4: Define the project structure
  Apply micro/project-structure.md to specify the folder layout
  Agree on folder names before creating any files
  Record non-obvious structural decisions as inline comments or ADRs

Step 5: Begin implementation
  Every implementation decision is checked against CLAUDE.md
  Every new file is placed in the folder declared in Step 4
  Every task is marked complete only after its DoD checklist passes
```

**Bootstrap is not optional.** If an agent begins producing code before completing Steps 0–4, any resulting output is not compliant with this OS, regardless of the quality of the output. Step 0 does not exempt a project from bootstrap; it changes what a completed bootstrap looks like for a project too small to carry the full template honestly.

---

## 2. CLAUDE.md Template

The following template must be instantiated at the project root before any implementation begins. Every section must be populated: sections with placeholder text indicate an incomplete bootstrap.

```markdown
# Claude Code — Project Instructions

## Engineering Standards

All code in this project follows the engineering standards at:
[absolute path to engineering-os]
Engineering OS version: [tag this project is pinned to, e.g. 1.7.0]

**Before writing any code:** load the `eng-os-core` skill (installed per `tools/install.*`), or,
without Skills support, read every file in meta/, macro/, meso/, micro/.

Treat all standards as non-negotiable requirements, not references.

---

## Project Type
[pipeline | service | AI system | library | other]

## Project Structure

[Populated from micro/project-structure.md; list every folder and its purpose]

Example:
ids/        AI-IDS specification files (.ids); plain text, at project root not inside src/
src/        Source modules
  config.py All environment variables read here; never call os.getenv() elsewhere
input/      Input files (gitignored or versioned; declare explicitly)
output/     Pipeline output (gitignored)
logs/       Structured log files (gitignored)
docs/
  decisions/  Architecture Decision Records
  contracts/  Data contracts and output schemas
  prompts/    Prompt registry entries for every .ids file
tests/      pytest or equivalent test suite
main.py     Entry point; loads .env, orchestrates pipeline

---

## Scale Targets

[Populated from the Product Brief's Scale Targets (plan-app Phase 2b), or directly at
bootstrap. Numbers, not adjectives: expected and peak requests per second; data volume now and
growth per year; largest single tenant; latency (p50/p99) and availability targets; RPO/RTO;
tenancy model; data classification level; regulatory scope. Every design review, load test,
capacity model, and cost budget in this project is checked against these. "N/A" is acceptable
only for a library or a trivial script, with a reason.]

---

## AI-IDS Rules

[Populate only if the project uses AI systems]

- Every AI task specification lives in ids/<name>.ids as plain text
- .ids files follow the template in meso/ai-ids-template.md exactly
- Python or TypeScript harness code loads the .ids file at startup
- The harness contains no cleaning or decision logic — only call mechanics
- Prompt registry entry required in docs/prompts/ for every .ids file
- Never embed an AI-IDS spec as a string constant in code

---

## Definition of Done

Run every applicable checklist before marking any task complete.

### Code (common.md + python.md or nodejs.md)

- [ ] All env vars read in config.py; no os.getenv() at call sites
- [ ] Required secrets raise EnvironmentError at startup if absent
- [ ] Optional secrets emit a startup warning when absent
- [ ] All external calls (network, file I/O, API) wrapped in try/catch with specific types
- [ ] Retry with exponential backoff on all transient external calls
- [ ] All logs use structlog or equivalent; no secrets in logs
- [ ] All public functions have type annotations
- [ ] All public functions, classes, and modules have JSDoc docstrings
- [ ] Inline comments explain WHY only, never WHAT
- [ ] Every public function has at least one happy-path and one failure-path test
- [ ] External dependencies mocked in unit tests

### AI-IDS (ai-ids-template.md Author Review Checklist)

- [ ] All important terms defined in DEFINITIONS
- [ ] Exactly one primary objective
- [ ] All hard constraints in GUARDRAILS, not in GUIDELINES
- [ ] Input and output contracts explicit with types and required/optional distinction
- [ ] Deterministic logic in DERIVED LOGIC as an ordered sequence
- [ ] Allowed assumptions explicitly bounded, no open-ended inference
- [ ] Ambiguity resolution explicit in REASONING POLICY
- [ ] FEW SHOT EXAMPLES removable without changing system requirements
- [ ] Output schema includes a determinism boundary statement

### Documentation (documentation.md Review Checklist)

- [ ] Describes current behaviour, not intended behaviour
- [ ] Owner declared in frontmatter
- [ ] Lifecycle state declared (Status: Current | Draft | Deprecated)
- [ ] All boundary conditions and failure modes covered
- [ ] An engineer can act on this without reading the source code
- [ ] References related documentation (ADRs, contracts, runbooks)
- [ ] ADR exists for every significant technical decision
- [ ] Data contract exists for every output dataset

---

## Non-Obvious Constraints

[Populate with project-specific constraints that would surprise a future engineer or agent]

Examples of what belongs here:
- Framework-specific quirks that affect implementation decisions
- External system behaviours that drive local design choices
- Known false positive / false negative risks in AI cleaning logic
- Specific error patterns encountered during development
- Any place where the obvious implementation would be wrong

---

## Dependency Notes

[Populate with any pinned versions, known incompatibilities, or required install steps]
```

---

## 2.1 The Product Brief

For a new application, the CLAUDE.md sections Platform Context, Audience and Framing, Core
Entities, Screens and Flows, Scale Targets, Design System Carryover, Mock Data Scale, and
Terminology Lock are not invented at bootstrap time. They are transcribed from a Product Brief
produced before any code exists, through a planning conversation with eight phases: discovery,
domain modeling, scale targets, screens and flows, terminology lock, phased milestones, design
system carryover, and mock data scale, ending in an explicit approval gate (the skill numbers these Phases 1 to 7, with Scale Targets as Phase 2b, and the gate as Phase 8). The skill
`skills/eng-os-plan-app/SKILL.md` runs that conversation and its Output Contract matches these section
names one-to-one so the bootstrap transcribes rather than reformats.

---

## 2.2 The Feature Spec and the Execution Loop

Once a feature's scope is approved (a Product Brief phase, or a standalone request on a
bootstrapped project), the work runs in two stages, each with its own skill.

**Spec stage** (`skills/eng-os-spec-feature/SKILL.md`). For a feature that takes three or more tasks,
adds or changes a contract or an entity, has user-visible behavior with edge cases, or has
ambiguous scope, three files are written under `.specs/<feature-slug>/` in this order, each stopping at an explicit approval gate
before the next is started:

1. `requirements.md`: user stories, each with numbered acceptance criteria in EARS notation
   (a trigger, a state, or an unwanted condition, then a response), plus an out-of-scope list
   and no unresolved open questions.
2. `design.md`: the components, data model, interfaces, error handling, test strategy, and
   checkpoint-table skills the feature touches, with every requirement mapped to the part of the
   design that satisfies it.
3. `tasks.md`: vertical-slice tasks, each naming its dependencies, checkpoints, observable
   Definition of Done, and the requirements it satisfies. A traceability check runs before this
   gate: every requirement has a task, and every task has a requirement.

**Execution stage** (`skills/eng-os-execute-feature/SKILL.md`). The task list, adopted from
`tasks.md` or decomposed inline when no spec exists, is run one task at a time: implement,
verify against the task's Definition of Done and the requirements it lists, commit, then start
the next. When the work shows a spec file is wrong, the spec file is amended and re-approved
before work continues, so the spec never disagrees with the code that ships. A feature is
verified against every acceptance criterion in `requirements.md` before it is called done.

A change that is genuinely one task skips the spec stage and the decomposition both.

---

## 3. Checkpoint Protocol

Checkpoints define when standards must be verified during implementation. They are not optional review moments: they are stop conditions. An agent must not proceed past a checkpoint until the corresponding standard passes.

| Checkpoint | Trigger | Standard to Verify |
|---|---|---|
| Before Step 1 | Bootstrap starting | Step 0 bail-out check completed: project classified as real/ongoing or trivial-script |
| Before first file | Bootstrap complete | All CLAUDE.md sections populated (or explicitly marked N/A with a reason, if Step 0 classified the project as trivial) |
| Before any design review, capacity decision, or load test | Scale-relevant decision | Checked against the Scale Targets section, which must be populated |
| Before implementing a feature | Scope approved | `.specs/<feature>/` approved through all three gates, or the feature judged below the spec threshold (`eng-os-spec-feature` Phase 0) |
| Before each module | New source file created | Folder placement matches project-structure.md |
| Before each public function | Function complete | Type annotations, JSDoc docstring, error handling |
| Before each test file | Test file created | Happy-path and failure-path tests present; deps mocked |
| Before each .ids file | IDS file created | AI-IDS Author Review Checklist passes |
| Before each doc file | Doc file created | Status, Owner, lifecycle declared |
| Before marking a task done | Task complete | Full DoD checklist for the applicable standard |
| Before the session ends | Work complete | ADR for every significant decision made this session |

**Checkpoint failures are not warnings.** They are blockers. An agent that skips a checkpoint has drifted from this OS.

---

## 4. Drift Patterns and How to Prevent Them

Drift is not caused by bad decisions: it is caused by missing structure at the moment a decision is made. The following patterns are the most common causes of drift when AI agents apply this OS.

### Standards Treated as References

**Symptom:** Agent reads the engineering-os as background context and applies parts selectively.

**Cause:** The word "reference" in the initial instruction gives the agent license to skip.

**Prevention:** CLAUDE.md must say "treat as non-negotiable requirements"; never "use as a reference". Bootstrap Step 1 requires reading every file, not just relevant files.

---

### AI-IDS Spec Embedded in Code

**Symptom:** The AI-IDS specification is stored as a string constant in a Python or TypeScript file.

**Cause:** Bootstrap Step 4 was skipped; the agent did not know where `.ids` files belong.

**Prevention:** CLAUDE.md must include the AI-IDS rules section. The project structure must declare `ids/` before any AI files are created.

---

### Definition of Done Not Run

**Symptom:** Tasks marked complete without checklist verification; violations discovered during review.

**Cause:** No checkpoint requiring DoD execution before completion.

**Prevention:** The DoD checklist must appear in CLAUDE.md and the checkpoint protocol must explicitly block task completion until the checklist passes.

---

### Inline Comment Drift

**Symptom:** Comments describe what code does (restate the code) rather than why.

**Cause:** No checkpoint specifically targeting inline comment quality.

**Prevention:** The DoD checklist item "Inline comments explain WHY only, never WHAT" must be enforced at the before-task-done checkpoint.

---

### Missing ADRs

**Symptom:** Significant design decisions are made during implementation with no recorded rationale.

**Cause:** ADRs are associated with planning, not implementation. During fast implementation, they are skipped.

**Prevention:** The session-end checkpoint must require an ADR for every significant decision made during the session.

---

## Failure Modes

- Bootstrap skipped because the task felt simple: the simplest tasks often contain the hardest-to-find drifts
- CLAUDE.md created but not populated: empty sections are not a bootstrap; they are a drift guarantee
- Standards read at the start but not referenced mid-session: context accumulates; early reads decay
- Checkpoint treated as a review rather than a stop condition: reviews catch drift after it happens; checkpoints prevent it
- Agent confirms compliance without running the checklist: confirmation without evidence is not verification

---

## Definition of Done

A project using Claude Code meets this standard when:
- Step 0's bail-out check was run and the project was correctly classified as an ongoing/real project or a trivial single-file script before the template was applied
- CLAUDE.md exists at the project root and every section is populated before any code is written; or, for a project classified as trivial in Step 0, every inapplicable section is explicitly marked N/A with a one-line reason rather than left to imply structure that doesn't exist
- For a project with a UI or operational messages, the Architecture Practices Gate ran with a concrete answer (a real path/folder/component name) or an explicit reasoned skip for every row, not a bare "yes" or "N/A"
- Bootstrap Steps 0–4 completed and confirmed before Step 5 began
- Every DoD checklist ran to completion before each task was marked done
- Every checkpoint was treated as a blocker, not a review
- ADRs exist for every significant technical decision made during the session
- No AI-IDS specification is embedded as a code constant; all specs live in `ids/*.ids`
