<!-- lint-os: allow-em-dash -->  This file documents the em dash rule and must show the banned pattern.
# Prose Style

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
Standards for the sentence-level and structural texture of prose written by an AI agent or edited alongside AI-assisted work: UI copy, documentation, commit messages, PR descriptions, README content, marketing/landing copy, and any user-facing text. Names the specific patterns that make text read as machine-generated regardless of whether the content itself is correct, and gives the direct rewrite for each.

### What This Is Not
- not a document *structure* standard (see `meta/document-authoring-guidelines.md` for section boundaries, required structure by layer, and the independently-useful-file rule)
- not a code naming or comment standard (see `meso/code-conventions.md`)
- not a grammar or general writing guide
- not a ban on every pattern named below in all circumstances: the rule is against overuse as a crutch, not against the construction existing at all (see Section 12). The one exception is Section 3's em dash rule, which is a hard ban on clause-joining use in flowing prose, not a judgment call.

## Scope
- Level: Meso
- Applies To: All prose content produced or edited by an AI agent: documentation, UI copy, commit messages, PR descriptions, code comments' prose portions, marketing/landing copy, chat responses that get persisted
- See Also: `meta/document-authoring-guidelines.md` for structural rules this guide does not duplicate; `meso/code-conventions.md` for naming and code-comment rules; `meso/documentation.md` for what belongs in a doc, as distinct from how its sentences read

---

## Applied Principles

### Explicitness Over Implicitness
A sentence that hedges instead of stating a fact ("this is essentially," "this basically means") is less explicit than the direct claim. Say the thing, not an approximation of the thing.

### Consistency as a Quality Attribute
A handful of AI-tell patterns, once present, tend to recur throughout a document because they are reached for as defaults rather than chosen per-sentence. Fixing one instance and leaving the pattern in place elsewhere in the same file is incomplete work.

### Failure Modes Are First-Class
Every pattern below is named because it has a concrete failure mode: it either wastes the reader's attention, or it signals unedited AI output to a reader who has learned to recognize the tell, undermining trust in content that may otherwise be accurate.

### Substance Over Polish
The strongest single tell is rarely one flagged word. It is the accumulation of generic phrasing, predictable contrasts, excessive structure, and repeated conclusions with no concrete example, name, number, date, or decision anywhere in the passage. A pass that removes every flagged word but leaves the content generic has not fixed the actual problem.

---

## The Patterns

### 1. Contrastive Negation as a Crutch ("X, not Y")

**Pattern:** Reaching for "it does X, not Y," "X rather than Y," "not just A, it's B," "less about X and more about Y," "not only X but also Y," "the question isn't whether X, but how" as the default way to add emphasis or precision, to the point that it recurs multiple times in the same paragraph or across consecutive list items or headings.

**Why it happens:** The construction is genuinely useful for a real, single contrast, but AI-generated text overuses it as a rhythm, applying it even where a direct positive statement would say the same thing with less friction. It is one of the single most recognizable AI tells, especially in headlines and section titles.

**Rewrite approach:** State the fact directly. Reserve the contrastive form for the rare case where the reader's likely wrong assumption needs to be named and corrected in the same breath.

**Example**

```
Bad (three uses in one paragraph, none of them load-bearing):
"Meta defines how to navigate the OS, not how to sequence a build. Macro holds
non-negotiable principles, not guidance. Micro has templates, not principles."

Good:
"Meta defines how to navigate the OS. Macro holds non-negotiable principles.
Micro provides templates and checklists that implement the pattern above them."
```

```
Bad (headline): "A new layer, not a feature"
Good (headline): "Creation tools ask 'does it look right'; this asks 'is it real'"
```

One genuine contrastive use elsewhere in the same document (e.g. "the schema is authoritative over the implementation, not the other way around") is fine; the failure mode is repetition as a tic, not the construction's existence.

#### Failure Mode
A reader who sees this construction three or more times in a short span recognizes it as a generation artifact, which shifts attention from the content to the fact that it was AI-written: the opposite of what confident, direct prose is for.

---

### 2. Filler Intensifiers and Minimizers ("just," "simply," "only," "really," "actually," "actual," "basically," "merely," "all you need to do is")

**Pattern:** Using these words as throwaway intensifiers, minimizers, or hedges rather than for their literal restrictive or contrastive meaning. "Actual" and "actually" are the same tell in adjective and adverb form ("the actual relationship," "the actual strength"), reached for as filler emphasis where the noun alone already carries the full claim. "It's as easy as," "with just a few steps," and "you can easily" belong to the same family: they assert ease rather than letting the described steps demonstrate it.

**Distinction that matters:** "Required **only** for fields with a declared SLA" is a precise, load-bearing restriction; that use is correct and should stay. "**Just** implement the current task" and "confirm it **actually** passes" use the same words as filler with no restrictive meaning; removing them changes nothing about what the sentence claims.

**Test:** Remove the word. If the sentence's truth value is unchanged, the word was filler and should stay removed. If removing it changes what the sentence claims (a real restriction, a real emphasis earned by contrast with a stated alternative), keep it.

**Example**

```
Bad (filler): "Simply implement the current task. This just triggers every
checkpoint skill, and it actually passes the verify gate. It's as easy as
running one command."

Good: "Implement the current task. This triggers every checkpoint skill and
passes the verify gate by running one command."

Correct restrictive use, unchanged: "Freshness badges are required only for
fields with a declared SLA."
```

#### Failure Mode
Filler intensifiers add no information and read as a verbal tic under repetition, the prose equivalent of a code comment that restates the line beneath it. Asserted ease ("it's easy," "you can easily") that is not backed by the actual step count reads as reassurance rather than information.

---

### 3. Em Dash Banned as a Clause-Joining Default

**Pattern:** Reaching for an em dash (—) to join two clauses, itemize, or add emphasis in flowing prose: the AI-generated-text default in place of a period, comma, colon, or semicolon that would show the real relationship with less visual noise. The em dash is a legitimate mark in English prose generally (Dickinson, Austen, and daily journalism all use it); the problem is specific to how current AI systems reach for it by default far more often than a human writer choosing punctuation deliberately would.

**Rule:** In flowing prose (docs, UI copy, commit messages, PR descriptions, chat responses, marketing copy), the em dash is not used to join two independent or explanatory clauses. This is a hard rule, not a per-sentence judgment call: treat any clause-joining em dash as a required fix, the same way a lint rule treats a banned pattern, rather than weighing it case by case.

**Rewrite:** choose based on the real relationship between the two parts.
- A new, complete sentence follows: use a period.
- The second clause explains or itemizes the first: use a colon.
- The clauses are independent but closely related: use a semicolon.
- Neither of the above fits and the second part is a genuine parenthetical aside, removable without changing the sentence's core claim: use parentheses, not an em dash.

**The only three surviving legitimate uses**, all non-prose or non-clause-joining:
1. A true parenthetical aside so short and so clearly a side comment that parentheses would read as fussier than the dash (rare: most asides should use parentheses per the rule above, not this exception).
2. A short label preceding a definition in a compact, tabular, or tooltip context (not flowing prose): a dash-separated `Label — definition` format is an acceptable, distinct convention from prose. This exception covers only the dash separating the label from its value, not any em dash that happens to appear inside the definition text itself; that text is ordinary flowing prose and is still subject to the ban above.
3. A title-bar convention (`Page Name — Site Name`): a labeling convention, not prose.

**Example**

```
Bad: "The checkpoint table governs compliance while a task runs — it never
said how to sequence multiple tasks — which is the gap this skill closes."

Good: "The checkpoint table governs compliance while a task runs. It never
said how to sequence multiple tasks, which is the gap this skill closes."
```

#### Failure Mode
An em dash used for every clause boundary erases the distinction between "this is a new thought," "this defines the prior term," and "this is a minor aside": three different relationships collapsed into one mark, forcing the reader to infer which one was meant, and reading as unedited AI output to anyone who has learned the tell.

---

### 4. AI-Cliché Vocabulary

**Pattern:** A closed set of words and phrases disproportionately common in AI-generated text relative to normal technical writing.

- **Inflated/promotional:** *powerful, robust, seamless(ly), cutting-edge, groundbreaking, transformative, game-changing, revolutionize/revolutionary, best-in-class, next-generation, state-of-the-art, world-class, unparalleled, unlock, elevate, supercharge, harness, leverage, empower, drive innovation, maximize impact, future-proof, at scale*
- **Vague business language:** *enhance efficiency, improve outcomes, streamline workflows, deliver value, enable alignment, drive meaningful impact, foster collaboration, support informed decision-making, provide actionable insights, optimize the user experience, meet evolving needs, navigate complexity, accelerate the journey, create a holistic approach, build a comprehensive solution.* These feel artificial whenever they are not immediately followed by a concrete action, metric, owner, or result.
- **Overused vocabulary:** *delve, realm, landscape, tapestry, nuanced, multifaceted, pivotal, crucial, vital, meticulous, intricate, dynamic, evolving, holistic, comprehensive, underscores, showcases, highlights, serves as a testament, sheds light on, plays a crucial role, marks a significant milestone*
- **Stock transitions:** *"it's worth noting," "it's important to remember that," "in today's [X] landscape / fast-paced world," "in conclusion," "to summarize," "furthermore," "moreover," "additionally," "consequently," "nevertheless," "that said," "with that in mind," "on the other hand," "in contrast," "by the same token," "moving forward," "ultimately," "at the end of the day," "when it comes to"*

**Rewrite approach:** Replace with the plain word that names the thing, or delete the transition and let the next sentence stand on its own. "Leverage the API" is "use the API." "A comprehensive standard" is a standard that names what it covers. "It's worth noting that X" is "X."

**Example**

```
Bad: "This leverages a comprehensive, best-in-class framework to seamlessly
streamline the workflow. Moreover, it's worth noting that this drives
meaningful impact at scale."

Good: "This uses a framework covering API design, data strategy, and security
under one set of principles to remove the manual steps in the workflow. It
cut deployment time from three days to four hours."
```

**Pattern — vague placeholder noun standing in for the concrete thing (not limited to the fixed word list above):** A single abstract noun (commonly "intelligence," "insights," "solutions," "capabilities," "experience") reused repeatedly across headings and body copy in place of naming the actual object the document is about (a score, a tag, a metadata field, a record). Any one word can be a legitimate name; the tell is the same noun doing the job of several different concrete nouns across a document because naming each one was skipped.

**Test:** For every recurring instance of the candidate noun, substitute the specific thing it refers to in that sentence. If the substitution is easy and the sentence gets more specific without getting longer, the abstract noun was standing in for something the writer already knew and should name.

**Example**

```
Bad (same word standing in for three different concrete things):
"Scoring produces structured intelligence that stays with the asset.
See the same intelligence through the API. Intelligence for every visual
asset."

Good:
"Scoring produces filterable score and compliance fields that stay attached
to the asset. See the same scores and signals through the API. A trust
score for every visual asset."
```

#### Failure Mode
Cliché vocabulary substitutes a vague, high-register word for a specific claim, so the sentence sounds authoritative while saying less than a plain restatement would. A reused placeholder noun compounds this across an entire document: every heading sounds like it introduces something new, but a reader who substitutes the concrete referent at each instance finds the same underspecified claim repeated under different headings.

---

### 5. Openings, Reassurance, and Artificial Friendliness

**Pattern — openings and fillers:** "Certainly!", "Absolutely!", "Of course!", "Great question.", "I'd be happy to help.", "Let's dive in.", "Let's break this down.", "Here's the thing." Throat-clearing before the actual content starts.

**Pattern — unnecessary reassurance:** "Don't worry.", "You're not alone.", "The good news is…", "Rest assured…", "The key is to…", "The bottom line is…" Comfort phrases inserted regardless of whether the reader signaled needing reassurance.

**Pattern — artificial friendliness:** excessive exclamation marks, frequent emojis in professional communication, overenthusiastic agreement, unrequested praise, calling basic ideas "excellent," "thoughtful," or "insightful," "You've got this!", "Happy writing!", "Hope this helps!", "Feel free to reach out if you have any questions."

**Rewrite approach:** Delete the opener and start with the actual answer. Delete reassurance that was not requested and was not earned by a preceding hard problem. Match tone to the register of the surrounding document: professional and technical content does not need cheerleading.

**Example**

```
Bad: "Great question! Let's dive in. Don't worry, this is easier than it
looks. The bottom line is that you'll want to configure the retry policy
first. Hope this helps!"

Good: "Configure the retry policy first."
```

#### Failure Mode
These phrases add no information and mark the surrounding text as a chat transcript rather than authored content, which is jarring in documentation, PR descriptions, or UI copy meant to be read as if a person wrote it once, deliberately.

---

### 6. Excessive Qualification and Forced Balance

**Pattern — excessive qualification:** "Generally speaking…", "In many cases…", "Depending on the context…", "It may be helpful to…", "You might want to consider…", "Potentially…", "Arguably…", "To some extent…", "While results may vary…", "There is no one-size-fits-all answer…" Hedges stacked on a claim that could be stated plainly, or substituted for an actual recommendation.

**Pattern — forced balance:** presenting equal arguments when the evidence strongly favors one; giving several options with no recommendation; avoiding a direct conclusion; adding "pros and cons" when the user asked for a decision; treating a weak alternative and a strong one as equally credible for the sake of appearing neutral.

**Rewrite approach:** Make the call. If the evidence favors one option, say so and name the trade-off being accepted. Hedge only when the uncertainty is real and material to the reader's decision, not as a reflexive disclaimer.

**Example**

```
Bad: "There are several ways to handle retries, and the best choice depends
on your specific needs. You might want to consider exponential backoff, but
in some cases a fixed delay could also work."

Good: "Use exponential backoff with jitter. A fixed delay is only
appropriate for a single-instance, low-QPS client where thundering-herd
retries cannot occur; most services should not use it."
```

#### Failure Mode
A reader asking for a decision receives a survey of options instead, and has to do the actual reasoning work the request was meant to offload.

---

### 7. Fake Precision, Authority, and Generic Conclusions

**Pattern — fake precision/authority:** "Research shows…", "Experts agree…", "Studies suggest…", "Industry best practices recommend…", "It is widely recognized that…", "Many organizations have found…", or an unsupported percentage/performance claim, all stated with no named source, study, or number that could be checked.

**Pattern — generic conclusions:** "The best choice depends on your specific needs.", "Ultimately, the decision is yours.", "By following these steps, you'll be well on your way…", "With the right approach, success is within reach.", "This can help you make a more informed decision.", "The possibilities are endless.", "The future looks promising." Closing lines that could be appended to any document on any topic without change.

**Pattern — unsupported certainty:** An absolute or guaranteed outcome stated with no check behind it: "always," "never," "automatically," "guarantees," "fully," "satisfies the requirement," "no competitor does this," "ensures compliance." The sentence reads as confident, and the writer never confirmed it against the code, the data, or the source. In a document that describes a real system, the usual sign is a claim that is stronger than what the system does today (a capability described as live when the signal behind it is not wired, a result described as verified when the check is optional).

**Rewrite approach:** Name the actual source, or drop the claim if there is none to name. Replace a generic closing line with a specific one: the actual next step, the actual number, the actual decision made. For an absolute, check it against the code or source before keeping it; if it holds only in part, state the scope and the known gap ("flags likely AI-generated content; a probability signal, not a forensic determination") instead of the guarantee.

**Example**

```
Bad: "Studies suggest that caching improves performance significantly. By
following these steps, you'll be well on your way to a faster system."

Good: "Caching the user-profile lookup cut p95 latency from 340ms to 40ms in
this service's load test. Deploy the cache layer behind the existing
read-through path; no schema change is required."
```

#### Failure Mode
A claim with no checkable source cannot be verified or disputed, so the reader either takes it on faith or discounts the whole document; a generic conclusion signals the writer had nothing more specific to say, undermining the specific content above it. An unchecked absolute is worse than either: a reader who relies on it (an auditor, an integrator, an investor) acts on a capability that does not exist.

---

### 8. Overexplaining

**Pattern:** Restating the user's request before answering it; explaining a term the stated audience already understands; repeating the conclusion in several different phrasings; appending a summary after an answer that was already short; giving background before the requested answer instead of after it; explaining the rationale for every individual edit made; adding generic "benefits" text to a feature whose value is already obvious from its description.

**Rewrite approach:** Answer first. Cut restatement of the question. Cut a summary that adds no information beyond what preceded it. If background is genuinely needed, place it after the direct answer, not before it, and only include what changes the reader's next action.

**Example**

```
Bad: "You asked how to add a database index. Adding a database index is a
common way to improve query performance. Here's how: run `CREATE INDEX
idx_users_email ON users(email);`. This creates an index, which will make
queries filtering on email faster. In summary, this command adds an index
on the email column to speed up lookups."

Good: "Run `CREATE INDEX idx_users_email ON users(email);`. This is the
column the slow query in `getUserByEmail` filters on."
```

#### Failure Mode
Overexplaining triples the reading time of a one-line answer and buries the actual instruction in restatement, forcing the reader to find the one sentence that mattered.

---

### 9. Mechanical Formatting

**Pattern:** A heading for every short paragraph; far more bullets than a simple point needs; every bullet in a list following the identical grammatical pattern; excessive bolding; symmetrical three-item sections regardless of what the content actually supports; colon-heavy titles; repeated "Key takeaway," "Why it matters," and "Next steps" boilerplate at the end of every section; ending every section with a mini-summary of the section just read.

**Rewrite approach:** Let content length determine structure. A two-sentence point does not need its own `##` heading. Vary list-item grammar to match what each item actually says instead of forcing parallel phrasing where the content isn't parallel. Use a fixed three-part structure only where the content genuinely has three parts, not as a default template. Drop a section summary unless the section is long enough that a reader could lose the thread without one.

**Example**

```
Bad:
## Overview
This is a brief overview.
## Why It Matters
This matters because it does.
## Key Takeaway
The key takeaway is to remember the overview above.

Good:
This library replaces manual retry loops with a single configurable policy,
which is why the three call sites in `payments/` should migrate to it.
```

**Pattern — verbatim or near-verbatim duplicate content (hard check, not a judgment call):** The same sentence or paragraph reused word-for-word (or with only the heading changed) under two or more different headings, cards, or sections in the same file or across sibling pages meant to be distinct (e.g. per-persona pages, per-card grids, FAQ answers). This is a stronger failure than templated *shape*: it means the content itself was never actually written per-section, only the scaffolding around it. It most often shows up as a placeholder paragraph pasted under several headings during drafting and never replaced.

**Test:** For every section/card/page that shares a heading pattern or grid position with siblings, diff its body text against every sibling's body text. Any two bodies that are identical, or identical apart from swapping one or two words, are a required fix, the same severity as the em-dash rule: fix regardless of how good the individual sentence reads in isolation.

**Rewrite approach:** Write distinct body content for each heading that is actually about that heading's specific claim. If two sections genuinely have nothing different to say, that is a sign one of the sections should be deleted or merged, not left duplicated.

**Example**

```
Bad (three cards, one page, identical body under different headings):
### One evaluation
A completed workflow does not confirm the asset contains the right
disclosure or clear usage rights. The platform evaluates it directly.
### Compliance stays with the asset
A completed workflow does not confirm the asset contains the right
disclosure or clear usage rights. The platform evaluates it directly.
### Always based on the latest result
A completed workflow does not confirm the asset contains the right
disclosure or clear usage rights. The platform evaluates it directly.

Good:
### One evaluation
Every regulatory check runs in the same pass as the score, no separate
governance tool required.
### Compliance stays with the asset
The record travels in the file's own metadata, not a spreadsheet that goes
stale the day the asset changes.
### Always based on the latest result
Re-score the asset and the compliance record updates with it; nothing is
cached from the original run.
```

#### Failure Mode
A document that imposes the same heading/bullet/summary skeleton on every section regardless of content reads as templated rather than authored, and the repeated boilerplate headings train the reader to skip them, hiding real content that happened to land under one. Verbatim duplicate bodies are worse: they are legible evidence, to any reader who compares two sections, that the page was never finished, which damages trust in the surrounding content more than any single word-level tell.

---

### 10. Repetitive Sentence Structures

**Pattern:** Starting successive sentences with "This ensures…", "This enables…", "This allows…", "This helps…", "This provides…", "By doing so…"; reflexively structuring comparisons as "Whether you're X or Y…" or "From X to Y…" or "Both X and Y…"; repeating a three-part list in every paragraph; opening consecutive sentences or paragraphs with the same noun or phrase.

**Pattern — symmetry, triads, and stock verbs:** Every list has exactly three items; matched pairs ("X for the reviewer, Y for the campaign") and parallel clauses of equal length in every paragraph; the same small set of stock verbs and adjectives doing the work of different facts ("ensure," "enable," "support," "provide," "streamline," "robust," "seamless").

**Rewrite approach:** Vary the sentence opener and the underlying grammatical shape from one sentence to the next. If several consecutive sentences all describe an effect of the same cause, combine them into one sentence with a list, rather than repeating the templated opener each time. Give a list the number of items the content has (two, four, or five are normal), and name the specific action a stock verb stood in for ("checks," "rejects," "stores," "returns").

**Example**

```
Bad: "This ensures data consistency. This enables safe retries. This allows
concurrent writers to proceed without conflict."

Good: "The idempotency key makes retries, concurrent writers, and replayed
messages all converge on the same final state."
```

#### Failure Mode
Uniform sentence openers across a paragraph create a singsong, templated rhythm that a reader recognizes as generated text before they finish reading the content.

---

### 11. Punctuation and Content-Level Signals

**Pattern — punctuation:** heavy em-dash use (see Section 3, now a hard ban in flowing prose rather than a judgment call); semicolons in casual, non-technical writing where a period reads more naturally; quotation marks placed around ordinary phrases for no reason; a parenthetical aside in every paragraph; frequent colons introducing statements that were not actually itemized or defined; perfectly uniform sentence lengths and perfectly uniform bullet construction throughout a passage.

**Pattern — content-level:** no concrete examples anywhere in the passage; no names, dates, numbers, or decisions; observations generic enough to apply to any company or any system; a response that repeats the prompt back in different words instead of answering it; invented context added to make an answer sound more complete than the writer's actual knowledge supports; smooth prose that carefully avoids taking a position; benefits described with no corresponding trade-off; every topic forced into a "framework"; a one-line message inflated into a multi-section strategy document; an unsolicited offer to do more work appended to the end of a finished answer.

**Rewrite approach:** Vary sentence length and bullet phrasing naturally, driven by what each sentence needs to say. Add the specific example, name, date, number, or decision that the generic version was standing in for. If there is no real trade-off, say so explicitly rather than omitting the trade-off question. Match response scope to request scope: a one-line question gets a one-line answer, not a document.

#### Failure Mode
Content with no concrete detail is unfalsifiable and unmemorable. The reader cannot check it, act on it, or distinguish it from a plausible-sounding answer about a different system entirely.

---

### 12. When These Patterns Are Legitimate

Every rule above has a stated exception, restated together here so the guide doesn't read as an absolute ban that ignores real usage:

- **Contrastive negation:** legitimate for one genuine correction of a likely wrong reader assumption, not as a repeated rhythm or as a headline template.
- **Filler-word candidates:** legitimate when the word is doing real restrictive or scoping work (Section 2's test: does removing it change the claim?).
- **Em dash:** the only legitimate uses are the three named in Section 3: a rare, genuinely short parenthetical aside; a `Label — definition` pairing in a compact, non-prose context (a UI tooltip, a table cell, a mind-map node); and a title-bar convention like `Page Name — Site Name`. Every other use in flowing prose is a required fix, not a judgment call.
- **Cliché vocabulary:** a term on the list is not banned if it is the industry's actual proper noun for the thing (e.g. a product literally named "Cutting Edge"). The rule targets the word used as vague praise, not as a literal reference.
- **Reassurance and friendliness:** a genuine congratulation for a hard, verified accomplishment, or a content warning that is actually needed, is not the pattern this guide restricts. The failure mode is reflexive insertion regardless of context, not warmth existing at all.
- **Qualification and balance:** a real "it depends" is legitimate when the two paths genuinely diverge on facts not yet known (e.g. depends on data the reader has and the writer doesn't). The failure mode is hedging to avoid commitment on a question the writer does have enough information to answer.
- **Mechanical formatting:** a heading per section, a three-part structure, or a closing summary is correct when the content actually has that shape and is long enough to need it. The failure mode is imposing the skeleton regardless of content.

Applying this guide is a judgment call at the sentence level, not a mechanical find-and-replace across a whole file. A pass that removes every instance of "only" including the restrictive ones has overcorrected and introduced a factual gap. A pass that deletes every heading from a genuinely long, multi-topic document has overcorrected in the other direction.

---

## Editing Existing Prose: Minimum Change

The patterns above apply when drafting and when editing. Editing someone else's prose adds constraints the patterns do not state, because the goal is to remove the machine-like texture and leave the author's document intact.

- **Preserve what the author said and how they said it.** Meaning, facts, terminology, names, acronyms, capitalization, structure, level of detail, degree of confidence, directness, emphasis, and voice stay as written. An intentional idiosyncrasy or natural informality is part of the voice; do not smooth it.
- **Match the conventions of the audience and purpose.** Do not make professional writing casual, technical writing conversational, concise writing more elaborate, or direct writing more diplomatic unless the original meaning requires it.
- **Make the smallest change that removes the pattern.** A sentence with no pattern is not edited. Replace the offending word, clause, or punctuation, and leave the rest of the sentence alone.
- **Add nothing.** No new claims, examples, interpretations, conclusions, transitions, stylistic flourishes, or emphasis that the original did not carry. Section 11's advice to add the concrete example applies when drafting; when editing, take the detail from the author's own text or source, and where it is missing, flag the gap to the author instead of inventing it.
- **Do not soften, hedge, neutralize, embellish, or over-polish.** Removing an AI tell must not lower the author's confidence or raise the register. Keep the stated certainty unless it is unsupported (Section 7).
- **Do not simulate human error.** Choppy fragments, forced informality, deliberate quirks, and planted imperfection are themselves a tell. The target is natural authorship, and sentence length and cadence vary because the content varies.
- **Re-read the result after any scripted change.** A find-and-replace on punctuation or a word list leaves nested parentheses, fragments, stray separators, and sentences whose grammar depended on the removed mark. Read the output as the reader sees it (the rendered page, not the source), then do a last pass for any generic, templated, or over-polished phrasing that remains.

**Example**

```
Original: "The platform ensures comprehensive compliance — it's not just a
checklist, it's a living record."

Bad (over-edited): "The platform keeps a compliance record that updates
itself, giving teams peace of mind."

Good (minimum change): "The platform keeps a living compliance record, one
per run."
```

The bad version adds a claim ("updates itself") and a flourish ("peace of mind") the original never made. The good version removes the cliché, the em dash, and the contrastive frame, and states only what the system does.

#### Failure Mode
An edit that rewrites whole paragraphs to remove a handful of tells replaces the author's voice with a different uniform one, which is the same machine-like texture in a new form. It also silently changes claims, so the document no longer says what its author checked.

---

## Failure Modes

- contrastive negation repeated as a rhythm rather than used for one genuine correction, especially in headlines and section titles
- filler intensifiers and minimizers removed inconsistently: some instances fixed, the same tic left elsewhere in the same document
- em dashes used to join clauses anywhere in flowing prose, not just "used too often": any clause-joining instance is a required fix
- cliché vocabulary and vague business language substituted for a specific claim, so the sentence sounds authoritative while saying less
- reflexive openers, reassurance, and enthusiasm inserted regardless of whether the reader signaled needing them
- hedging or forced balance substituted for an actual recommendation the writer had enough information to make
- unsupported "research shows" / "experts agree" claims with no checkable source, or a generic closing line that could apply to any document
- an unchecked absolute ("always," "automatically," "no competitor," "satisfies") that is stronger than what the system or source actually supports
- overexplaining: restating the question, explaining known terms, or repeating the conclusion in multiple phrasings
- mechanical formatting imposed regardless of content shape: a heading per short paragraph, a forced three-part structure, boilerplate section summaries
- verbatim or near-verbatim duplicate body text reused under two or more different headings, cards, or sibling pages, left over from drafting and never replaced with section-specific content
- a single vague placeholder noun (e.g. "intelligence," "insights," "solutions") reused across a document in place of naming the specific, concrete thing each instance actually refers to
- repetitive sentence openers ("This ensures… This enables… This allows…") across consecutive sentences
- every list built as exactly three parallel items, or the same few stock verbs standing in for different facts
- content with no concrete example, name, number, date, or decision: generic enough to apply to any system
- over-correction: mechanically stripping every instance of a flagged word or pattern, including legitimate restrictive, labeling, or structural uses, introducing a factual gap or breaking an established convention
- over-editing: rewriting beyond the pattern, adding claims or flourishes, softening or raising the author's stated confidence, or planting deliberate imperfection to look human
- an automated punctuation or word replacement shipped without re-reading the output, leaving nested parentheses, fragments, and stray separators

---

## Definition of Done

A prose pass is complete when:
- no paragraph or heading contains contrastive negation ("X, not Y") more than once unless each instance is independently load-bearing
- filler intensifiers and minimizers (just, simply, only, really, actually, actual, basically, merely) have been tested per-instance against the removal test in Section 2, and only the load-bearing ones remain
- no em dash joins two clauses anywhere in flowing prose; every instance has been replaced with the punctuation matching the real relationship (period, colon, semicolon, or parentheses), except for the three named exceptions in Section 3 (rare true parenthetical, label-definition, or title-bar convention)
- no AI-cliché, inflated-promotional, or vague-business-language term from Section 4 remains where a plain word or a concrete result would say the same thing
- no reflexive opener, unrequested reassurance, or artificial-friendliness phrase from Section 5 remains
- no excessive qualification or forced-balance construction from Section 6 stands in place of an actual, information-backed recommendation
- no unsupported "research shows" / "experts agree" claim or generic, content-free closing line from Section 7 remains, and every absolute ("always," "automatically," "no competitor," "satisfies") was checked against the code or source or reduced to its true scope
- the passage answers the request directly before any background, and contains no restated question, no explanation of an already-known term, and no repeated conclusion (Section 8)
- heading, bullet, and summary structure matches what the content actually needs, not a default template (Section 9)
- every section/card/page sharing a heading pattern or grid position with siblings has been diffed against those siblings; no two are identical or near-identical in body text (Section 9's duplicate-content check, a hard check like the em-dash rule, not a judgment call)
- any abstract noun (e.g. "intelligence," "insights," "solutions") that recurs three or more times across the document has been tested by substituting the concrete referent at each instance (Section 4); it was replaced wherever the substitution reads more specifically
- no run of consecutive sentences shares the same templated opener, and no list was forced to three items, no paragraph to matched pairs, by habit (Section 10)
- the passage contains at least one concrete example, name, number, date, or decision where the topic supports one, and states a real trade-off rather than only benefits (Section 11)
- the pass was applied at the sentence level with judgment, not as a mechanical find-and-replace that could strip a legitimate restrictive, labeling, or structural use
- when editing existing prose: meaning, facts, terminology, structure, voice, and stated confidence match the original; nothing was added that the original or its source did not carry; no deliberate imperfection was introduced; and the output was re-read as the reader sees it after any scripted replacement (Editing Existing Prose)
