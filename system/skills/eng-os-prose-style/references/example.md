<!-- lint-os: allow-em-dash -->  This file documents the em dash rule and must show the banned pattern.
# Prose Style Worked Example — Documentation Site Cleanup

A before/after pass, drawn from a real audit of a published documentation site (a
downstream project's docs). Shows each pattern caught, why the fix was correct, and one case where the
original text was correctly left alone.

## Case 1 — Contrastive negation repeated as rhythm

**Before:**
> "Walking the OS's four governance layers against this gap directly: meta defines how to
> navigate the OS, not how to sequence a build. Macro holds non-negotiable principles — none of
> them is about task decomposition or verification loops. Micro has templates but they scaffold a
> codebase shape, not a sequence of execution steps with a verify gate after each one."

Three separate "X, not Y" constructions across three sentences, none of them correcting a specific
stated misreading: each is habitual phrasing.

**After:**
> "Walking the OS's four governance layers against this gap directly: meta covers how to navigate
> the OS, a different question than how to sequence a build. Macro holds non-negotiable
> principles, and none of them touched task decomposition or verification loops. Micro has
> templates that scaffold a codebase shape; none of them sequenced execution steps with a verify
> gate after each one."

Same claims, no repeated tic, and the em dash in the middle sentence became a comma since the
clause was a simple continuation, not a definition or aside. This fix stands regardless of Section
3's later hardening to a full ban on clause-joining em dashes; a comma was always the right call
here.

## Case 2 — Filler intensifier vs. real restriction, side by side

**Before (mixed — one real, two filler):**
> "Freshness badges are required only for fields with a declared SLA, not for every field."
>
> "Confirm the vertical slices compose correctly together and the original approved scope is
> actually satisfied."
>
> "Implement the current task only, invoking every checkpoint-table skill named for it."

Applying the removal test to each:
- "required **only** for fields with a declared SLA": removing "only" changes the claim from a
  real scope limit to "required for all fields." **Keep it.**
- "is **actually** satisfied": removing "actually" changes nothing about what's being claimed.
  **Filler, remove it.**
- "the current task **only**": removing "only" changes nothing; the sentence already says "the
  current task," singular. **Filler, remove it.**

**After:**
> "Freshness badges are required only for fields with a declared SLA."
>
> "Confirm the vertical slices compose correctly together and the original approved scope is
> satisfied."
>
> "Implement the current task, invoking every checkpoint-table skill named for it."

The first sentence's "only" survived because it is doing real restrictive work. This is the case
this skill's Definition of Done exists to protect against over-correction: a mechanical pass that
stripped all three "only"s equally would have introduced a factual error in the first sentence.

## Case 3 — Em dash doing three different jobs, all of them banned in flowing prose

**Before:**
> "The checkpoint table governs compliance while a task runs — it never said how to sequence
> multiple tasks — which is the gap this skill closes."

Two em dashes, two different relationships: the first joins an independent, closely related
clause; the second introduces a result/conclusion. Under an earlier, softer version of this rule,
a short result/conclusion clause like the second one might have survived as a "legitimate
parenthetical aside." That exception is gone: Section 3 now bans the em dash as a clause joiner
outright, with no case-by-case judgment call, because it is one of the single most recognizable AI
tells and a softer rule kept getting reasoned around.

**After:**
> "The checkpoint table governs compliance while a task runs. It never said how to sequence
> multiple tasks; that gap is what this skill closes."

The first dash became a period (a genuinely new, complete thought). The second became a semicolon
(the clauses are independent but closely related) rather than staying an em dash, since it was
still joining two clauses in flowing prose, not fitting any of the three named exceptions (a rare
true parenthetical aside, a label-definition pairing, or a title-bar convention).

## Case 4 — A label-definition dash, with a second dash hiding inside the definition text

**Before:**
> `{ label: "GUARDRAILS", desc: "Non-negotiable constraints and failure conditions — what the
> system must never do." }`

Two different dashes here, only one of them legitimate. The `desc:` field's own value is short
flowing prose, and its internal em dash is joining two clauses exactly the way Section 3 bans; it
is not the field-level `label` / `desc` pairing itself.

**After:**
> `{ label: "GUARDRAILS", desc: "Non-negotiable constraints and failure conditions: what the
> system must never do." }`

The field-level structure (a `label` key and a `desc` key in the same object) is the actual
`Label — definition` convention this skill exempts, and it needed no change. The dash living
inside the `desc` string's own prose is a different thing entirely: ordinary flowing text that
happens to sit inside a tooltip, still subject to the same ban as any other sentence. A colon fits
the relationship here (the second clause defines the first).

## Case 5 — A contrastive-negation headline, and the two other patterns hiding beside it

**Before (a docs-page section header and its intro line):**
> ## A new layer, not a feature
>
> This leverages a comprehensive, best-in-class scoring taxonomy to seamlessly
> streamline provenance verification. It's worth noting that this ensures
> trust. This enables compliance. This allows every downstream system to
> benefit. The possibilities are endless.

Four separate patterns stacked in four sentences: a contrastive-negation headline with no
specific misreading to correct, cliché/inflated vocabulary ("leverages," "comprehensive,"
"best-in-class," "seamlessly streamline"), a reflexive stock transition ("it's worth noting
that"), three consecutive sentences opening with the identical "This ensures / This enables /
This allows" template, and a generic, content-free closing line that could be pasted into any
product's docs unchanged.

**After:**
> ## Creation tools ask "does it look right"; this asks "is it real"
>
> The scoring taxonomy maps 22 weighted dimensions to specific regulatory
> clauses, so a trust score, a compliance record, and a distribution-ready
> metadata set are all generated from the same pass and stay consistent for
> every downstream system that consumes them.

The headline states the actual distinction instead of a template contrast. The vocabulary became
specific (22 weighted dimensions, regulatory clauses) instead of vague praise. The three
repetitive-opener sentences collapsed into one sentence naming the real relationship between the
three outputs. The generic closer was replaced with the concrete claim it was standing in for.

## What this shows

The pass is not "delete every instance of only," and it is not "delete every contrastive headline
or every use of 'this.'" On em dash specifically, the pass is exactly "delete every clause-joining
instance": that one rule has no case-by-case judgment call, unlike the other eleven patterns in
this skill. For everything else, identify the relationship or claim actually being made, and use
the punctuation, structure, and vocabulary that matches it exactly, replacing vague praise and
templated rhythm with the specific fact, number, or distinction the sentence was standing in for.
This sometimes means removing a flagged pattern, and sometimes means confirming it was already
correct and leaving it untouched.
