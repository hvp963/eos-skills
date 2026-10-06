---
name: eng-os-design-system
description: "Use when building UI: design tokens, typography, component patterns, color/elevation system, the four-region app shell (header/footer/nav/application panel), responsive breakpoints, or when a new app should inherit visual language from a sibling app."
sources:
  - meso/design-system.md
globs: ["**/*.css", "**/*.tsx", "**/*.jsx", "**/components/**"]
always_apply: false
verified_platforms: [claude-code]
---

# Design System

Apply these rules when building or reviewing web UI: internal tools, documents, or product
screens that should share a consistent visual language.

## Principles

- **Explicitness over implicitness.** Visual decisions are named tokens, not magic numbers. A hex value inline is an undeclared intent; a token like `--primary` is a contract.
- **Contracts as source of truth.** The token file is the contract between visual intent and implementation. All components reference the same tokens.
- **Consistency as a quality attribute.** Similar-looking components are built from the same primitives. Divergence signals a missing pattern, not a justified exception.

## Rule versus Profile

The OS-level rule holds for every project regardless of its values: declare one token file as
the single source of truth for color, elevation, typography, and radius, and reference only
tokens from components; declare one typographic scale and add no sizes outside it; declare the
four-region app shell and the three breakpoints; record which profile the project uses in
CLAUDE.md. The concrete values (token names, the type scale, header height, content width) are
the **default profile** in `references/profile-default.md`, which a project adopts unchanged,
inherits from a sibling app, or replaces with its own. Changing values is a project decision;
skipping the declaration is a violation.

## Component Patterns

- **Cards**: primary container for discrete content (3+ structured fields). `shadow-sm` at rest, `shadow-md` + slight lift on hover. Not for uniform short lists (use a table) or prose (use sections).
- **Badges**: inline state/category marker, always paired with a readable label, never the sole indicator. Semantic variants only: `badge-improved`, `badge-new`, `badge-behavior`, `badge-breaking`, `badge-fixed`.
- **Tables**: structured data, 3+ comparable columns. Not for 2-column label/value pairs (use a definition list or card).
- **Callouts**: left-border or inline-tip variants, colored per semantic meaning (purple=info, green=tip, amber=warning, red=breaking/error). Use sparingly; overuse flattens urgency.
- **Sticky nav header**: brand left, metadata right; no primary actions in a document header; height and elevation per the declared profile.

## App Shell

Every application (not a single static document/report page) is composed of exactly four regions,
each a separate reusable component, never inlined per-page:

- **Common header**: one component, shared across every page/screen. Brand, global search,
  account/session controls. Per the `eng-os-system-design` UX rule, no create/action flows live here.
- **Common footer**: one component, shared across every page/screen. Legal/version/links only;
  never duplicated or re-styled per page.
- **Navigation panel**: the primary/sidebar nav. Destinations only (links to views), never
  action triggers: see `eng-os-system-design`'s "Nav items are destinations, not actions" rule.
- **Application panel**: the main content region where each page's actual view renders. This is
  the only region that changes between routes/screens; header, footer, and nav panel do not
  re-render or re-implement per page.

Failure mode: header/footer markup copy-pasted into each page instead of extracted as shared
components drifts silently; a nav link added on one page and forgotten on another, or a footer
year/link updated in three of five places.

## Responsive Design

Every screen must be usable at three baseline breakpoints, not just the designer's desktop
viewport:

- **Desktop**: ≥1024px: full layout, nav panel expanded/visible.
- **Tablet**: 768–1023px: nav panel may collapse to icons or an overlay; application panel
  reflows to available width, not a fixed desktop pixel width.
- **Mobile phone**: <768px: nav panel collapses behind a toggle (hamburger or equivalent);
  header/footer stay usable at reduced width; no fixed-width element wider than the viewport;
  no horizontal scroll on the page body.

Use relative units (`%`, `rem`, `fr`, `minmax()`) and flex/grid layouts, not fixed pixel widths,
for any container whose content is variable-length. A component is not done until it has been
checked at all three breakpoints, not just the one it was built at.

## UX and Information Architecture

These are UI constraints, not system-boundary ones.

- **Nav items are destinations, not actions.** Primary navigation links to views; create/action flows live on the relevant list page. Failure mode: users hunt the nav bar for actions and the nav's meaning becomes inconsistent.
- **Atomic multi-entity saves.** When one user action writes several related records in one database, commit them in one transaction. Across services, use a saga or outbox (`eng-os-system-design`, `eng-os-database-design`). Failure mode: partial writes leave an entity without its children or its audit entry.
- **Consider** making dashboard stat cards clickable to the screen where the number is explained; a dead-end number erodes trust once a user has a question.
- **Compute layout offsets from rendered content**, never fixed stride times index, for any variable-size grouped UI. Failure mode: overlaps and gaps appear only with real, variable-length data.

## Accessibility

Every screen meets WCAG 2.2 Level AA as a Definition-of-Done row: keyboard reachable and
operable with a visible focus state; contrast 4.5:1 (3:1 for large text and UI components);
color never the only carrier of meaning; accessible names on images, meaningful icons, and
controls; `prefers-reduced-motion` respected; reflow to 320px without horizontal scroll. Run an
automated checker (axe or equivalent) in CI on every page and a keyboard-only pass per screen.
- Failure mode: an application millions use that a keyboard-only or screen-reader user cannot operate is a legal exposure, and every retrofit costs more than building it in.

## Internationalization Readiness

Build so adding a language is a content change: every user-facing string is a constant
(`eng-os-coding-standards-common` Standard 3); dates, numbers, and currencies go through the locale
API; layouts use logical properties and are checked once in a right-to-left locale; no text in
images; no layout assumes English string length.
- Failure mode: the first non-English market becomes a UI rewrite.

UI copy itself (labels, headings, messages, empty states) is checked by `eng-os-prose-style` before a screen is called done.

## Reference Implementation

Canonical CSS: `micro/templates/base-styles.css`, a copy-paste starting point, not a compiled
output. Copy it into a project, extend with project-specific classes referencing the same tokens,
and put any token override in a separate `:root` block rather than editing the source tokens.

## Design System Inheritance

When a new app is visually part of a suite/family (e.g. multiple sibling apps sharing one brand),
the canonical token set and component class list must be declared **once**, in
`references/design-tokens-full.md` here, or in a shared design-system source file the team
maintains, and every sibling app's project docs must **point to that canonical source by
reference/path**, not retype the values.

**Failure mode:** hand-retyped tokens drift silently. A color or class-name typo introduced while
copying values into app 3's docs does not get caught until a visual QA pass, if ever, and by then
sibling apps have visibly diverged without anyone deciding they should.

Concretely: when bootstrapping or documenting a new sibling app, link to this skill (or its
`references/design-tokens-full.md`) and to the shared CSS file (e.g.
`micro/templates/base-styles.css` or a project's canonical `globals.css`) instead of pasting the
token block into the new app's CLAUDE.md or design notes.

**Scope of path/pointer-based inheritance:** referencing the canonical source by file path (as
described above) works cleanly only inside a monorepo or single-team context with shared
filesystem/package access; every consumer can resolve the path and sees updates immediately.
For a real cross-team or multi-repo production org, a raw file-path reference is fragile (paths
break across repos, updates don't propagate, and there's no version pinning). In that context,
publish the tokens as a versioned package instead (an npm package, or equivalent for the stack)
that sibling apps declare as a dependency and bump deliberately. Use path/pointer references
within one repo or team; use a versioned published package once teams or repos diverge.

## Failure Modes

- hardcoded hex values scattered in component styles: a brand change requires grep, not a variable update
- inconsistent border-radius across components: visible at a glance, signals an unmanaged system
- `shadow-md` on static elements: elevates everything equally, removes depth hierarchy
- semantic colors used arbitrarily: destroys the vocabulary
- font sizes added ad-hoc: breaks the typographic scale
- more than three heading levels on one screen: hierarchy collapses
- `--surface` as page background: cards become invisible, layout loses structure
- tokens/classes hand-retyped per sibling app instead of referenced from one canonical source: silent drift
- header/footer markup duplicated per page instead of one shared component: nav links, legal text, or version numbers drift out of sync across pages
- layout built and tested only at desktop width: breaks silently on tablet/mobile until a real user hits it
- a screen operable only by mouse, or a state carried by color alone: excluded users and legal exposure
- strings, date formats, and left-to-right assumptions spread across components: the first new locale is a rewrite
- nav items that trigger actions; multi-entity saves that are not atomic within one transaction

## Definition of Done

- [ ] All colors reference CSS custom properties; no hardcoded hex values in component styles
- [ ] All font sizes map to the defined typographic scale
- [ ] Cards use `shadow-sm` at rest and `shadow-md` on hover
- [ ] Badges use only the defined semantic color variants
- [ ] Page background is `--bg`, content surfaces are `--surface`
- [ ] Content width, header height, and elevation values match the declared profile
- [ ] Token file is the single source of truth; overrides are in a separate block, not inline
- [ ] If this app is part of a multi-app suite, its docs point to the canonical token/component source rather than retyping values
- [ ] For applications (not single static pages): common header, common footer, navigation panel, and application panel each exist as one shared component, not duplicated per page
- [ ] Layout is checked and usable at desktop (≥1024px), tablet (768–1023px), and mobile (<768px); no fixed-width element exceeds the viewport; no horizontal page scroll
- [ ] Every screen meets WCAG 2.2 AA (keyboard operable with visible focus, 4.5:1 contrast, meaning never by color alone, accessible names); an automated checker runs in CI
- [ ] Strings, dates, numbers, and currencies are locale-ready; layout checked once in a right-to-left locale
- [ ] Nav items are destinations only; multi-entity saves are atomic within one transaction; variable-size grouped UI computes offsets from content
- [ ] CLAUDE.md declares which design profile this project uses (default, inherited sibling, or its own)

For a worked example, see `references/example.md`.
