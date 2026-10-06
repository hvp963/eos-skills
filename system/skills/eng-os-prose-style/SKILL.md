---
name: eng-os-prose-style
description: "Use before marking any doc file, README, UI copy, commit message, PR description, or other user-facing prose as done. Checks for the full set of patterns that make text read as unedited AI output (contrastive-negation headlines, filler words, em-dash clause-joining, cliché/inflated vocabulary, reflexive openers and reassurance, forced balance, fake precision, overexplaining, mechanical formatting, repetitive sentence structure, verbatim duplicate content across sections, vague placeholder nouns, generic content with no concrete example) and rewrites them directly."
sources:
  - meso/prose-style.md
globs: ["**/*.md", "**/*.html", "**/*.mdx", "**/README*"]
always_apply: false
verified_platforms: [claude-code]
---
<!-- lint-os: allow-em-dash -->  This file documents the em dash rule and must show the banned pattern.

# Prose Style

Applies to prose, including the sentence-level voice of inline code comments — cliché vocabulary,
filler words, and reflexive tone are checked here the same way in a comment as in a doc page. Code
comments' placement, structure, and length ceiling are `eng-os-code-conventions`'s job instead;
the two skills' Definitions of Done are both run against a comment before it's considered done, one
for voice and one for shape. Thirteen patterns, plus a row of legitimate exceptions. Eleven are a judgment call at the sentence level: is this
instance load-bearing, or is it a tic? Two are hard rules checked mechanically, not by feel: em
dash as a clause joiner (never use it in flowing prose), and verbatim or near-verbatim duplicate
body text reused across sibling sections or pages (always a required fix once found by diffing). The canonical `meso/prose-style.md` numbers 12 sections: its Section 4 holds the vague-placeholder-noun pattern (row 13 here), Section 9 holds duplicate content (row 12), and Section 12 holds the exceptions (row 14).

## The Patterns

| # | Pattern | The tell | The test | The fix |
|---|---|---|---|---|
| 1 | Contrastive negation | "X, not Y" / "not just A, it's B" / "less about X, more about Y," especially as a headline | Is each instance independently load-bearing (a real reader misconception being corrected), or is it rhythm? | State the fact directly; drop "not Y" unless it corrects a specific wrong assumption |
| 2 | Filler intensifiers/minimizers | just, simply, only, really, actually, actual, basically, merely, "all you need to do is," "you can easily" | Remove the word: does the sentence's truth value change? | If unchanged, delete it. If changed, it was a real restriction; keep it |
| 3 | Em dash as a clause joiner | `—` joining two clauses, itemizing, or adding emphasis anywhere in flowing prose | Is this an em dash joining two clauses in prose? If yes, it fails regardless of how good the sentence otherwise reads | Period, colon, semicolon, or parentheses, matched to the real relationship — no exceptions in flowing prose |
| 4 | AI-cliché / inflated / vague-business vocabulary | leverage, seamless, robust, cutting-edge, game-changing, unlock, elevate, empower, streamline, "drive meaningful impact," "deliver value," delve, realm, landscape, tapestry, holistic, comprehensive, "it's worth noting," furthermore, moreover | Is there a plainer word, or a concrete result, that says the same thing? | Replace with the specific word or the actual metric/outcome |
| 5 | Reflexive openers / reassurance / artificial friendliness | "Certainly!", "Great question.", "Let's dive in.", "Don't worry.", "Hope this helps!", excessive exclamation/emoji | Was this earned by the surrounding context, or inserted by default? | Delete; start with the actual content |
| 6 | Excessive qualification / forced balance | "Generally speaking," "it depends," listing options with no recommendation when one is clearly better | Does the writer actually have enough information to make a call? | Make the call; name the trade-off being accepted |
| 7 | Fake precision / unsupported certainty / generic conclusions | "Research shows…", "Experts agree…" with no named source; an absolute ("always," "automatically," "satisfies," "no competitor does this") never checked against the code or source; "The possibilities are endless." | Can the claim be traced to an actual source or number? Does the system really do what the absolute says? Could the closer apply to any document? | Name the source or drop the claim; check each absolute and state its true scope and known gap; replace generic closers with the specific next step |
| 8 | Overexplaining | Restating the question, explaining a known term, repeating the conclusion, background before the answer | Does this sentence add information beyond what's already been said? | Answer first; cut restatement and redundant summary |
| 9 | Mechanical formatting | A heading per short paragraph, forced 3-part symmetry, "Key takeaway"/"Why it matters" boilerplate every section | Does the content actually have this shape, or is a template being imposed? | Let content length and shape drive structure, not a default template |
| 10 | Repetitive sentence structure | Consecutive sentences opening "This ensures… This enables… This allows…"; every list exactly three items; matched pairs and equal-length parallel clauses; the same stock verbs ("ensure," "enable," "provide") standing in for different facts | Do 2+ consecutive sentences share the same opener/shape? Does every list have three items by habit? | Vary the opener; combine repeated-cause sentences into one; give a list the count the content has; name the specific action behind a stock verb |
| 11 | Punctuation/content-level signals | Uniform sentence lengths, no concrete example/name/number/date/decision anywhere, benefits with no trade-off | Could this paragraph be pasted into a document about a different system unchanged? | Add the specific detail; state a real trade-off, not just upside |
| 12 | Duplicate content across sections (hard check) | The same paragraph, or one differing by only a word or two, reused under two or more different headings, cards, or sibling pages | Diff each section's body against every sibling sharing its heading pattern or grid position: are any two identical or near-identical? | Write distinct, section-specific body content for each heading; merge or delete a section that truly has nothing different to say |
| 13 | Vague placeholder noun reused for concrete things | One abstract noun ("intelligence," "insights," "solutions," "capabilities," "experience") standing in for several different concrete things (a score, a tag, a field, a record) across a document | Substitute the specific referent at each instance: does the sentence get more specific without getting longer? | Name the concrete thing at each instance instead of reusing the abstract noun |
| 14 | Legitimate exceptions | See below | n/a | n/a |

## Legitimate Exceptions (don't over-correct)

- One genuine contrastive use per document, correcting a real likely misreading, is fine.
- A restrictive "only" ("required **only** for fields with a declared SLA") is a real scope limit, not filler. Keep it.
- Em dash has exactly three legitimate uses, none of them clause-joining: a rare, genuinely short parenthetical aside where parentheses would read as fussier; a `Label — definition` pairing in a table cell, tooltip, or mind-map node (a distinct compact convention, not flowing prose); and a title-bar convention (`Page Name — Site Name`). Every other em dash in flowing prose is a required fix, not a judgment call.
- A term from the cliché list used as a literal proper noun (an actual product name) is not banned.
- A genuine congratulation for a hard, verified accomplishment is not reflexive praise.
- A real "it depends" is legitimate when two paths genuinely diverge on facts the writer doesn't yet have. It is not legitimate when used to dodge a call the writer could make.
- A heading, three-part structure, or closing summary is correct when the content actually has that shape and is long enough to need it.
- Sibling sections that are genuinely, substantively the same thing (e.g. a legal boilerplate clause repeated by requirement) are not a duplicate-content violation; the check targets copy that was supposed to differ per section and doesn't, not copy that is required to be identical.
- A recurring abstract noun that always resolves to the same one concrete thing, named once nearby, is a normal product term, not a placeholder; the failure mode is the same word covering several different referents across the document.

Stripping every instance mechanically, including the legitimate ones above, is itself a failure.
It can delete real information (a restrictive scope) or break an established formatting
convention.

## Editing Existing Prose: Minimum Change

When the prose belongs to someone else, removing the tells is not enough; the author's document has to survive.

- Preserve meaning, facts, terminology, names, acronyms, capitalization, structure, level of detail, degree of confidence, directness, emphasis, and voice. Keep intentional idiosyncrasy and natural informality.
- Match the audience's conventions: do not make professional writing casual, technical writing conversational, concise writing elaborate, or direct writing diplomatic.
- Make the smallest change that removes the pattern; leave a sentence with no pattern alone.
- Add nothing: no new claims, examples, interpretations, conclusions, transitions, flourishes, or emphasis. When editing, take concrete detail from the author's text or source; if it is missing, flag the gap instead of inventing it.
- Do not soften, hedge, neutralize, embellish, or over-polish. Keep the stated certainty unless it is unsupported (pattern 7).
- Do not simulate human error. Forced fragments, informality, and planted quirks are a tell; cadence varies because the content varies.
- After any scripted punctuation or word replacement, re-read the output as the reader sees it (the rendered page). Automated passes leave nested parentheses, fragments, and stray separators. Finish with one pass for any remaining generic or over-polished phrasing.

```
Original: "The platform ensures comprehensive compliance — it's not just a
checklist, it's a living record."
Bad (over-edited): "The platform keeps a compliance record that updates
itself, giving teams peace of mind."
Good (minimum change): "The platform keeps a living compliance record, one
per run."
```

The bad version adds a claim ("updates itself") and a flourish ("peace of mind") the original never made.

## Worked Example

```
Before: "Great question! This leverages a comprehensive framework — it's
essentially a way to seamlessly streamline the workflow, not just automate
it. This ensures consistency. This enables safe retries. The system is only
actually useful once you've simply configured it, and the best part is the
possibilities are endless. Hope this helps!"

After: "The framework uses a shared idempotency key so retries, concurrent
writers, and replayed messages all converge on the same final state. It
covers the whole workflow rather than automating one step. The system
becomes useful once configured, which took this service from 340ms to 40ms
p95 latency in testing."
```

Every flagged word above was either filler (just, simply, actually), cliché (leverages,
comprehensive, seamlessly, streamline), a reflexive opener/closer ("Great question!", "Hope this
helps!"), a repetitive sentence-opener pair ("This ensures… This enables…"), an unsupported
"possibilities are endless" generic closer, or an em dash joining two clauses. The em dash became
a period, and the vague praise was replaced with a concrete result (the actual latency numbers).
The one surviving contrastive clause ("covers the whole workflow rather than automating one step")
is load-bearing: it corrects a real, specific misreading rather than adding rhythm.

A second common failure this same pass must catch, not shown above because it needs multiple
sections to demonstrate: three feature cards on one page, each with a different heading, sharing
one identical body paragraph verbatim. That is pattern 12, caught only by diffing sibling
sections against each other, not by reading any one card in isolation.

See `references/example.md` for a longer before/after pass on real flagged documentation content.

## Definition of Done

- [ ] No paragraph or heading contains contrastive negation more than once unless each instance independently corrects a specific likely misreading
- [ ] Every filler/minimizer candidate (just, simply, only, really, actually, actual, basically, merely) was tested with the removal test; only load-bearing ones remain
- [ ] No em dash joins two clauses anywhere in flowing prose; every instance was replaced with the punctuation matching the real relationship, except for the three named exceptions (rare true parenthetical, label-definition, title-bar convention)
- [ ] No AI-cliché, inflated-promotional, or vague-business-language term remains where a plain word or concrete result says the same thing
- [ ] No reflexive opener, unrequested reassurance, or artificial-friendliness phrase remains
- [ ] No forced-balance or excessive-qualification construction stands in place of an actual, information-backed recommendation
- [ ] No unsupported "research shows"/"experts agree" claim or generic content-free closing line remains, and every absolute ("always," "automatically," "no competitor," "satisfies") was checked against the code or source or reduced to its true scope
- [ ] The passage answers directly before background, with no restated question and no repeated conclusion
- [ ] Heading/bullet/summary structure matches what the content needs, not a default template
- [ ] No run of consecutive sentences shares the same templated opener, and no list was forced to three items or a paragraph to matched pairs by habit
- [ ] Every section/card/page sharing a heading pattern or grid position with its siblings was diffed against those siblings; no two are identical or near-identical in body text — required, not a judgment call
- [ ] Any abstract noun recurring three or more times across the document was tested by substituting its concrete referent at each instance, and replaced wherever that substitution reads more specifically
- [ ] At least one concrete example, name, number, date, or decision is present where the topic supports one, and a real trade-off is stated rather than only benefits
- [ ] The pass was applied with sentence-level judgment on the eleven judgment-call patterns, and with hard, non-negotiable checks on em dash and duplicate content: no restrictive "only," no legitimate tabular/tooltip dash convention, no genuinely-shaped heading, no literal proper noun, and no required-identical boilerplate clause was stripped or flagged by mistake
- [ ] When editing existing prose: meaning, facts, terminology, structure, voice, and stated confidence match the original, nothing was added that the original or its source did not carry, no deliberate imperfection was introduced, and the output was re-read as the reader sees it after any scripted replacement
