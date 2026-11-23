# Design System

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for building consistent, readable web interfaces and documents using a shared visual language, covering design tokens, typography, component patterns, and layout principles.

### What This Is Not
- not a component library or compiled framework
- not a replacement for a product design team on complex product UIs
- not specific to any CSS framework or build tool
- not exhaustive: it covers the patterns that recur across internal tools, documents, and lightweight web UIs

## Scope
- Level: Meso
- Applies To: Web applications, internal tools, customer-facing documents (release notes, reports, portals)
- See Also: `macro/principles.md` (Explicitness Over Implicitness), `meso/documentation.md`, `micro/templates/base-styles.css`

---

## Applied Principles

### Explicitness Over Implicitness
Visual decisions must be expressed as named tokens, not magic numbers. A hex value used directly is an implementation detail with no declared intent. A token like `--primary` is a contract: changing it in one place updates all consumers.

### Contracts as Source of Truth
The token file is the contract between visual intent and implementation. All components reference the same tokens. When a brand color changes, it changes in one place.

### Consistency as a Quality Attribute
A consistent visual language reduces cognitive load for users and maintenance cost for teams. Components that look similar should be built from the same primitives. Divergence is a signal that a pattern is missing, not that an exception is justified.

---

## 1. Design Tokens

Design tokens are the foundational layer of the visual language. They are named constants that express *design decisions*, not implementation details.

### 1.1 Color — Brand

```css
--primary:        #7c3aed;   /* primary action, focus rings, active states */
--primary-hover:  #6d28d9;   /* hover state for primary fills; white on it is 7.10:1 */
--primary-text:   #6d28d9;   /* primary-hued text on a tint (badges): 5.56:1 on primary-glow over --bg */
--primary-light:  #8b5cf6;   /* non-text accents only; white on it is 4.23:1, below 4.5:1 */
--primary-glow:   rgba(124,58,237,0.10);  /* tinted backgrounds, badge fills, input focus halo */
--on-primary:     #ffffff;   /* text and icons on primary fills (5.70:1) */
```

### 1.2 Color — Semantic

Semantic colors carry meaning. Use them consistently: amber always means caution, red always means error or required action, green always means success or value. Mixing them destroys the vocabulary.

Each hue has two roles. The base hue is for fills, borders, icons, and callout bars, where 3:1 against the background is enough (non-text contrast). Text in that hue uses its `-text` token, which reaches 4.5:1 on white, on `--bg`, and on its own tint (1.9).

```css
--green:        #059669;                 /* fills, borders, bars */
--green-text:   #047857;                 /* green text: 4.52:1 on green-soft over --bg */
--green-soft:   rgba(5,150,105,0.08);    /* tip callouts, value lists */
--green-border: rgba(5,150,105,0.2);     /* border of a green-soft surface */

--amber:        #d97706;
--amber-text:   #92400e;                 /* amber text: 5.92:1 on amber-soft over --bg */
--amber-soft:   rgba(217,119,6,0.08);    /* warnings, behavioral changes */

--red:          #dc2626;
--red-text:     #b91c1c;                 /* red text: 5.37:1 on red-soft over --bg */
--red-soft:     rgba(220,38,38,0.06);    /* errors, breaking changes */

--cyan:         #0891b2;                 /* informational, secondary accent (fills only: 3.68:1 on white) */
--cyan-text:    #155e75;                 /* cyan text: 7.27:1 on white, 6.01:1 on cyan-glow over --bg */
--cyan-glow:    rgba(8,145,178,0.08);    /* informational tint */
```

### 1.3 Color — Surface

```css
--bg:        #f0f4f9;   /* page background — light blue-grey, reduces eye fatigue */
--surface:   #ffffff;   /* card and panel surface */
--surface-2: #f8fafc;   /* hover state, alternating rows */
--surface-3: #f1f5f9;   /* input background, table header */
```

Never set a page background to `--surface`. The contrast between `--bg` and `--surface` is what makes cards readable.

### 1.4 Color — Text

```css
--text:       #0f172a;  /* primary body — near-black, high contrast */
--text-muted: #475569;  /* secondary: labels, metadata, placeholders, supporting copy (7.58:1 on white, 6.86:1 on --bg) */
--text-dim:   #94a3b8;  /* disabled and decorative only (WCAG exempts disabled controls); never body text or placeholders */
```

### 1.5 Color — Border

```css
--border:        #e2e8f0;  /* default border */
--border-bright: #cbd5e1;  /* hover/focus, emphasis */
```

### 1.6 Elevation — Shadows

```css
--shadow-sm: 0 1px 3px rgba(15,23,42,0.08), 0 1px 2px rgba(15,23,42,0.04);
--shadow-md: 0 4px 12px rgba(15,23,42,0.08), 0 2px 4px rgba(15,23,42,0.04);
```

Use `shadow-sm` as the default resting elevation for cards and panels. Use `shadow-md` on hover or for modals. Never invent `box-shadow` values outside these two levels.

### 1.7 Typography

```css
/* Font stack */
font-family: 'Google Sans Flex', 'Inter', system-ui, sans-serif;
/* Load via: https://fonts.googleapis.com/css2?family=Google+Sans+Flex:wght@100..700 */
/* Fallback: https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700 */
```

### 1.8 Border Radius

| Scale | Value | Use |
|---|---|---|
| sm | `6px` | Badges, chips, small inputs |
| md | `8px` | Callouts, inner tables |
| lg | `10–12px` | Cards, panels, containers — **preferred default** |
| full | `99px` | Pills, tags, avatar rings |

### 1.9 Contrast

Every text token reaches 4.5:1 on the surfaces it is used on. Ratios use the WCAG 2.x relative-luminance formula, with tints blended at their declared alpha and rounded to 8-bit colour, as a browser renders them. A tint is translucent, so it is measured over both surfaces it sits on: a card (white) and the page (`--bg`). A value change re-runs this table, and the accessibility check, before it ships.

| Text token | Value | On white | On `--bg` | On `--surface-3` | On its tint over white | On its tint over `--bg` |
|---|---|---:|---:|---:|---:|---:|
| `--text` | `#0f172a` | 17.85 | 16.16 | 16.30 | n/a | n/a |
| `--text-muted` | `#475569` | 7.58 | 6.86 | 6.92 | n/a | n/a |
| `--primary` | `#7c3aed` | 5.70 | 5.16 | 5.20 | n/a | n/a |
| `--primary-text` | `#6d28d9` | 7.10 | 6.43 | 6.49 | 6.12 | 5.56 |
| `--green-text` | `#047857` | 5.48 | 4.97 | 5.01 | 5.00 | 4.52 |
| `--amber-text` | `#92400e` | 7.09 | 6.42 | 6.47 | 6.51 | 5.92 |
| `--red-text` | `#b91c1c` | 6.47 | 5.86 | 5.91 | 5.90 | 5.37 |
| `--cyan-text` | `#155e75` | 7.27 | 6.58 | 6.63 | 6.60 | 6.01 |

Fill pairs: `--on-primary` on `--primary` is 5.70, and on `--primary-hover` 7.10. The focus ring (`--primary`) is 5.70 on white and 5.16 on `--bg`, above the 3:1 required for UI components. `--text-dim` (2.56 on white) passes nothing and is used only where WCAG exempts it: disabled controls and decoration.

---

## 2. Typography Hierarchy

Typography communicates structure before content is read. Every screen or document must have a single clear primary heading. Hierarchy is established through weight and size first: color reinforces it, not replaces it.

```
Page Title      26–28px  weight 700  letter-spacing -0.4px  color: --text
Section Title   16–18px  weight 700  color: --text  bottom border: 1px --border
Card Title      14–15px  weight 600  color: --text
Body            14–15px  weight 400  color: --text  line-height: 1.6
Secondary body  13–14px  weight 400  color: --text-muted
Label / Eyebrow 10–12px  weight 600–700  uppercase  letter-spacing: 0.05–0.08em
```

**Rule:** Do not introduce a font size outside this scale. Ad-hoc sizes create visual noise and resist systematic change.

---

## 3. Component Patterns

### 3.1 Cards

Cards are the primary container for content with a discrete identity.

```css
/* resting */
background: var(--surface);
border: 1px solid var(--border);
border-radius: 12px;
padding: 20–24px;
box-shadow: var(--shadow-sm);

/* hover */
border-color: var(--border-bright);
box-shadow: var(--shadow-md);

/* motion only when the user has not asked to reduce it (3.9) */
@media (prefers-reduced-motion: no-preference) {
  transform: translateY(-1px);
  transition: box-shadow 0.15s, border-color 0.15s, transform 0.15s;
}
```

**Use cards for:** numbered items, feature descriptions, decisions, breaking change details, anything with 3+ fields of structured content.

**Do not use cards for:** simple lists of uniform short items (use a table), continuous prose (use sections).

### 3.2 Badges

Badges communicate state or category inline. Always pair with a human-readable section title, and never use a badge as the sole indicator.

```css
/* base */
font-size: 10–11px;
font-weight: 700;
padding: 2px 8px;
border-radius: 99px;
text-transform: uppercase;
letter-spacing: 0.04–0.06em;

/* semantic variants */
.badge-improved { background: var(--primary-glow); color: var(--primary-text); }
.badge-new      { background: var(--green-soft);   color: var(--green-text); }
.badge-behavior { background: var(--amber-soft);   color: var(--amber-text); }
.badge-breaking { background: var(--red-soft);     color: var(--red-text); }
.badge-fixed    { background: var(--surface-3);    color: var(--text-muted); border: 1px solid var(--border); }
```

### 3.3 Tables

Use tables for structured data with 3+ columns where rows are comparable.

```css
/* container */
border: 1px solid var(--border);
border-radius: 10px;
overflow: hidden;  /* clips radius on inner cells */

/* header row */
font-size: 10–11px; text-transform: uppercase; letter-spacing: 0.06em;
color: var(--text-muted); background: var(--surface-3);
padding: 10px 14px; border-bottom: 1px solid var(--border);

/* data rows */
padding: 10px 14px; border-bottom: 1px solid var(--border);
/* omit border on last row */
/* hover: */ background: var(--surface-2);
```

Do not use tables for 2-column label/value pairs: use a definition list or card with `dl/dt/dd`.

### 3.4 Callouts

Callouts draw attention to information that must not be missed. Use sparingly: overuse makes everything appear equally urgent.

**Left-border callout** (overview, summary):
```css
background: var(--surface);
border: 1px solid var(--border);
border-left: 3px solid [semantic color];
border-radius: 0 10px 10px 0;
padding: 16px 20px;
box-shadow: var(--shadow-sm);
```

**Inline tip / note**:
```css
background: var(--green-soft);
border: 1px solid var(--green-border);
border-radius: 10px;
padding: 13px 16px;
/* include a leading icon glyph for scannability */
```

**Callout color semantics:**
| Color | Token | Use |
|---|---|---|
| Purple | `--primary` | General information, overview |
| Green | `--green` | Tips, recommendations, success |
| Amber | `--amber` | Warnings, behavioral changes, heads-up |
| Red | `--red` | Breaking changes, errors, required action |

### 3.5 Navigation Header (Sticky)

```css
height: 56px;
background: var(--surface);
border-bottom: 1px solid var(--border);
box-shadow: var(--shadow-sm);
position: sticky; top: 0; z-index: 10;
```

Keep sticky headers minimal: brand on the left, metadata on the right. Do not put primary actions in the header of a document: use in-content CTAs or footer links.

### 3.6 App Shell

Every application (not a single static document/report page) is composed of exactly four regions,
each a separate reusable component, never inlined per-page:

- **Common header**: one component, shared across every page/screen. Brand, global search,
  account/session controls. Per `meso/system-design.md`'s UX rule, no create/action flows live
  here.
- **Common footer**: one component, shared across every page/screen. Legal/version/links only;
  never duplicated or re-styled per page.
- **Navigation panel**: the primary/sidebar nav. Destinations only (links to views), never action
  triggers: see `meso/system-design.md`'s "Nav items are destinations, not actions" rule.
- **Application panel**: the main content region where each page's actual view renders. This is
  the only region that changes between routes/screens; header, footer, and nav panel do not
  re-render or re-implement per page.

**Failure mode:** header/footer markup copy-pasted into each page instead of extracted as shared
components drifts silently; a nav link added on one page and forgotten on another, or a
footer year/link updated in three of five places.

---

## 3.7 Responsive Design

Every screen must be usable at three baseline breakpoints, not just the designer's desktop
viewport:

- **Desktop**: ≥1024px: full layout, nav panel expanded/visible.
- **Tablet**: 768–1023px: nav panel may collapse to icons or an overlay; application panel
  reflows to available width, not a fixed desktop pixel width.
- **Mobile phone**: <768px: nav panel collapses behind a toggle (hamburger or equivalent);
  header/footer stay usable at reduced width; no fixed-width element wider than the viewport; no
  horizontal scroll on the page body.

Use relative units (`%`, `rem`, `fr`, `minmax()`) and flex/grid layouts, not fixed pixel widths,
for any container whose content is variable-length. A component is not done until it has been
checked at all three breakpoints, not just the one it was built at.

Check it in a real browser, not by reading the CSS: load each page at the three widths and fail
when the page body scrolls sideways, naming the elements that stick out. An element with a scroll
area of its own (a table, a tab row, a diagram) is fine; one that pushes the whole page sideways
is the failure. Fixed-column grids and rows that do not wrap are what this finds.

---

## 3.8 UX and Information Architecture

Multi-screen product systems accumulate a set of recurring structural decisions that are not covered by container/service boundaries but are still architectural, not cosmetic: they determine whether the system's navigation, data-writing, and layout logic stay coherent as screens are added. Treat them as design constraints subject to the same review rigor as a service boundary.

### 3.8.1 Nav Items Are Destinations, Not Actions
Primary navigation (sidebar, top nav, tab bar) must link only to views. It must never trigger a create/edit/mutate flow directly.

#### Why
A navigation element that sometimes navigates and sometimes mutates state breaks the user's mental model of what navigation does. Once one nav item behaves like a button, every nav item becomes suspect.

#### When to Use
- any primary or persistent navigation surface
- multi-screen apps with both "browse" and "create" flows

#### Example
```
nav_items = [
  { label: "Dashboard", route: "/dashboard" },
  { label: "Customers", route: "/customers" },
  { label: "Reports",   route: "/reports" }
]
// "New Customer" is NOT a nav item.
// It lives as an action button on the /customers list screen:
render(CustomersListScreen):
  render(NewCustomerButton -> opens create flow)
  render(CustomerTable)
```

#### Failure Mode
Action buttons placed in primary navigation create an inconsistent mental model of what navigation does: users hunt the nav bar for create actions instead of the list page, and some nav items navigate while others mutate state.

---

### 3.8.2 Metrics as Doorways
Where a dashboard shows KPI or stat cards, prefer making each card clickable, linking to the screen where that metric is explained or actionable.

This is recommended UX practice, not a correctness principle. Unlike the other patterns in this section, violating it does not corrupt data or break a mental model. It is a default worth applying, not a rule to enforce in review.

#### Why
A user who develops a question about a number ("why did this drop?") needs somewhere to go. A stat card with no destination is a dead end that erodes trust in the dashboard over repeated use.

#### When to Use
- dashboard or summary screens with KPI/stat cards
- any metric that has a corresponding detail or explanatory screen

#### Example
```
render(StatCard):
  value = metric.value
  label = metric.label
  onClick = navigate(metric.detailRoute)  // prefer over a static, unclickable card
```

#### Failure Mode
A metric card with no destination becomes a dead end: a user with a question about the number has nowhere to go, which quietly erodes trust in the dashboard over time. (Lower severity than the other patterns here: a missed doorway is a UX gap, not a correctness defect.)

---

### 3.8.3 Atomic Multi-Entity Saves
When one user action creates or updates multiple related records that live in the same database, commit them in a single transaction.

#### Why
A sequence of independent writes can partially fail, leaving an entity created without its children or without an audit trail: corruption that is silent and hard to reproduce because it only shows up when the failure lands between two of the writes.

#### When to Use
- one user action spans multiple related records (entity + child records + audit log entry) in one database

#### Example
```
begin_transaction():
  insert(expense)
  insert(audit_log_entry, ref=expense.id)
  insert(notification_task, ref=expense.id)
commit()
// all three rows exist, or none do
```

#### Failure Mode
Independent, non-transactional writes partially fail, leaving an entity without its children or its audit trail: silent, hard-to-reproduce data corruption.

**Boundary condition:** this pattern applies only within a single database/transaction boundary. See `database-design.md`'s Transactions and Consistency pattern for that single-database case. Across service boundaries, no single ACID transaction is available; use a saga (compensating actions) or an outbox pattern instead. Reaching for a distributed transaction across services is itself a design smell, not a fix.

---

### 3.8.4 Dynamic Layout Offset Computation
For any UI laying out a variable number of grouped or nested items (graphs, diagrams, dynamic lists), compute each group's height or offset from its actual rendered content, never from a fixed stride multiplied by index.

#### Why
Fixed-size assumptions hold only until real data varies in size. A demo with uniform items hides the bug; production data does not.

#### When to Use
- graph/diagram renderers with variable-height nodes or groups
- dynamic lists where item height depends on content

#### Example
```
// wrong: assumes every group is the same height
offset(i) = i * FIXED_GROUP_HEIGHT

// correct: accumulate actual measured/computed height
offset = 0
for group in groups:
  group.renderOffset = offset
  offset += measureHeight(group)  // actual content height, not a constant
```

#### Failure Mode
Fixed-stride layouts silently overlap or leave gaps the moment any group's size deviates from the assumed constant, a bug that appears only with real, variable-length data, never in the demo case.

These four rules are product and UI
constraints, and the system-design guide keeps only the system-boundary concern (the
transaction-boundary rule in 3.8.3 still cross-references `meso/database-design.md`).

## 3.9 Accessibility

Every screen meets WCAG 2.2 Level AA. This is a Definition-of-Done row, not a follow-up:

- every interactive element is reachable and operable by keyboard, with a visible focus state
- text and essential UI contrast meets 4.5:1 (3:1 for large text and UI components)
- color is never the only carrier of meaning (pair every semantic color with a label or icon)
- images, icons that carry meaning, and form controls have accessible names
- motion respects `prefers-reduced-motion`; nothing flashes more than three times per second
- content reflows to 320px width without horizontal scroll and zooms to 200% without loss

Run an automated checker (axe or equivalent) in CI on every page, and a keyboard-only manual pass
per screen before it is marked done.

The automated pass also includes a keyboard pass: tab through each page and fail when a focused
control shows no visible focus indicator, in addition to axe. Run both against a production
build, not a development server, whose overlay adds findings that are not the app's. Known
violations live in a list that may only shrink (`eng-os-testing-strategy`, Ratchet Baselines).

- Failure mode: an application serving millions of users that a keyboard-only or screen-reader
  user cannot operate is a legal exposure in most jurisdictions, and every retrofit costs more
  than building it in.

## 3.10 Internationalization Readiness

Whether or not the first release ships in more than one language, build so that adding one is a
content change, not a code change:

- every user-facing string is a constant (per `micro/coding-standards/common.md` Standard 3),
  so a locale table can replace it without touching components
- dates, numbers, and currencies are formatted through the platform's locale API, never by
  string concatenation
- layouts use logical properties (`margin-inline-start`, not `margin-left`) and are checked once
  in a right-to-left locale, since RTL breaks fixed-direction layouts silently
- no text is baked into images; no layout assumes English string length

- Failure mode: the first non-English market becomes a full UI rewrite because strings, date
  formats, and left-to-right assumptions are spread across every component.

## 3.11 Rule versus Profile

Sections 1 to 5 of this guide carry concrete values: named tokens, a typographic scale,
pixel sizes for the header and content width. Those values are the **default profile**, shipped so
a new project has a complete, coherent system on day one. The **rule** at OS level is narrower and
holds for every project regardless of its values:

- declare one token file as the single source of truth for color, elevation, typography, and
  radius, and reference only tokens from components
- declare one typographic scale and add no sizes outside it
- declare the four-region app shell and the three breakpoints
- declare the primitive set, the catalog, and the conformance check that holds them (3.12)
- record the chosen values in the project's CLAUDE.md Design System section, or point to the
  profile or sibling app they are inherited from

A project may adopt the default profile unchanged, inherit a sibling app's, or declare its own.
Changing values is a project decision; skipping the declaration is a violation.

## 3.12 Component Layer

A design system that stops at tokens leaves every screen to rebuild its buttons, inputs, and
tables by hand. The tokens hold, and the markup around them drifts: three paddings for the same
button, five radii, a status colour written as a hex value. The component layer closes that gap
and is enforced the same way the layering rules are, by a test.

**Primitives.** The project declares a set of primitives, one component for each recurring piece
of UI, and a screen is assembled from them. The default set is in `profile-default.md`: button,
icon button, badge, card, heading, stat, empty state, form field with its text, select, and
multi-line inputs, and data table. A raw control (`<button>`, `<input>`, `<select>`,
`<textarea>`, `<table>`) outside the primitives folder is a violation. A control with no primitive
yet carries a marker comment on the line before it, `ds-raw: <reason>`, and a marker with no
reason does not count.

**Variants.** A primitive has a variant only where the difference has a purpose: an action kind,
a tone, a size. A difference with no purpose (`px-2` on one screen and `px-3` on another) is
unified onto the default, which is taken from the markup the screens use most, and is listed in
the change so a reviewer sees what moved. A primitive is built from tokens only: no hex colour
and no inline style inside it.

**Adopting it on an existing app.** Build each primitive from the classes the screens already
use, so adopting one changes nothing a user sees apart from the listed unifications. Move the
shell, the shared components, and the entity screens first, then each area in turn.

**The declaration is data.** The scales (type sizes, radii, elevations) and the colour token
names are written once, in one source file in the project's language, which the conformance
check and the reference page both read. A token named in the declaration but absent from the
stylesheet fails a test. Nothing retypes a value.

**The catalog.** Each primitive, and each older shared component the system adopts as it is, has
a catalog entry: name, kind (`primitive` or `existing`), file, variants, what it is for, and what
it is not for and what to use instead. The not-for line is what stops a second component being
written for a case the first already covers. A reference page draws every scale, token, and
component by rendering the real component in each variant. A file in the primitives folder with
no catalog entry fails a test, and so does an entry with no example.

**The conformance check.** One test scans the source and counts, per file and per rule: hex
colours, text sizes outside the scale, radii outside the scale, inline colour styles, and raw
controls. It compares each count with a committed baseline using the ratchet in
`eng-os-testing-strategy` (Ratchet Baselines): a count may not rise, and a baseline above the
count fails, so a fix obliges lowering its entry. Reference content such as a documentation
section may carry its own baseline and fall at its own pace. The scan reads text, so it is a net
for drift and not a parser: a class assembled from parts at run time is not seen, which is
another reason to write utility classes out in full. `references/component-layer.md` has the
rule list, the entry shape, and the adoption sequence.

- Failure mode: a token file with no component layer and no check. The app passes review
  one screen at a time while raw controls, off-scale sizes, and inline colours accumulate until
  a theme or brand change has to touch hundreds of places.

## 3.13 Themes and Palettes

A dark theme and any alternate palettes are override blocks that redeclare the same token names,
never a second set of components. Because a component draws only tokens, every theme and palette
restyles it for free; a component that uses a hex colour or an inline colour style opts out and
breaks in the other theme. Contrast is checked per theme and per palette, not once. Text tokens
reach 4.5:1 on white, on `--bg`, and on their own tints over either surface; base hues are for fills and borders (3:1).
Each pair is listed in the contrast table (1.9) and rechecked when a value changes, and a new
value is checked with the accessibility check before it ships. The saved theme is applied before
first paint, so a reload does not flash the wrong one.

- Failure mode: a palette that passes in the light theme and fails contrast in the dark one, or a
  hard-coded colour that stays light on a dark page, found by a user and not by a check.

## 4. Layout Principles

**Max content width:** 820–860px. Do not let prose and cards stretch full-width: it breaks reading rhythm and makes table columns difficult to scan.

**Page padding:** 40–48px top/bottom, 24px horizontal. The outer `--bg` background provides breathing room around the white content area. Never set the page body background to `--surface`.

**Section spacing:** 44–48px between major sections. This exceeds normal line-height enough to signal a topic boundary without requiring a decorative rule on every section.

**Hierarchy through weight, not color:** Establish visual hierarchy with font weight and size first. A bold 15px heading and a 13px muted label create hierarchy without color. Color then reinforces (it does not create) that hierarchy.

**Scrollbar:** Narrow scrollbars (5px) reduce visual bulk on data-heavy layouts.
```css
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--surface-2); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }
```

---

## 5. Reference Implementation

The canonical CSS implementation of these tokens and patterns:

**`micro/templates/base-styles.css`**

This file is a copy-paste starting point, not a compiled output. It contains all CSS custom properties, base reset, body styles, scrollbar styles, and the component classes described above.

**How to use:**
1. Copy `base-styles.css` to your project's stylesheet root
2. Rename or prefix if merging with an existing stylesheet
3. Extend by adding project-specific classes that reference the existing tokens
4. If overriding a token for a project (e.g. different brand color), define the override in a separate `:root` block; do not edit the token file directly

**Production example:** a web app's `globals.css` and a release-notes system's stylesheet both implement this token set.

---

## 6. Design System Inheritance

When a new app is visually part of a suite or family (multiple sibling apps sharing one brand), the canonical token set and component class list must be declared once, and every sibling app must reference that source rather than retype it. Where that canonical source lives, and how a sibling points to it, depends on organizational context.

### 6.1 Path/Pointer Reference (Monorepo or Single-Team Context)

Within a monorepo or a single team with shared filesystem access, a sibling app's project docs should point at the canonical file by path. The reference resolves at read time, so updates to the canonical source are visible immediately to every consumer.

```markdown
## Design System
This app inherits its visual language from the shared design system. Canonical source:
- Tokens & component patterns: ../../shared/design-system.md
- Base CSS: ../../shared/templates/base-styles.css

Do not redeclare token values here. Project-specific overrides go in
`src/app/globals.css` under a separate `:root` block, referencing the canonical file above.
```

### 6.2 Versioned Published Package (Cross-Team or Multi-Repo Context)

Once sibling apps live in separate repos or are owned by separate teams, a raw file path is fragile: paths break across repos, updates don't propagate, and there is no version pinning. In that context, publish the tokens as a versioned package (an npm package, or the stack's equivalent) that each sibling app declares as a dependency and bumps deliberately.

```json
// package.json
{
  "dependencies": {
    "@acme/design-tokens": "^2.3.0"
  }
}
```

```markdown
## Design System
This app inherits its visual language from the shared design system, published as
`@acme/design-tokens`. Current pinned version: 2.3.0 (see package.json). Do not hand-copy
token values; bump the package version deliberately and re-review affected components on
major bumps.
```

Use the path/pointer form within one repo or team. Use the versioned-package form once teams or repos diverge. The difference is not stylistic: a path resolves live and shares blast radius with the canonical source, while a version bump is a deliberate, reviewable act.

#### Failure Mode
Hand-retyped tokens drift silently. A color or class-name typo introduced while copying values into a sibling app's docs is not caught until a visual QA pass, if ever, by which point sibling apps have visibly diverged without anyone deciding they should.

---

## Failure Modes

- hardcoded hex values scattered in component styles: a brand change requires grep, not a variable update
- inconsistent border-radius across components: visible at a glance, signals an unmanaged system
- `shadow-md` on static elements: elevates everything equally, removes depth hierarchy
- semantic colors used arbitrarily (amber on a success state, red on a warning): destroys the vocabulary
- font sizes added ad-hoc: breaks the typographic scale and compounds over time
- more than three heading levels on a single screen: hierarchy collapses, nothing reads as primary
- `--surface` as page background: cards are invisible against white, layout loses structure
- tokens or component classes hand-retyped per sibling app instead of referenced from one canonical source: drift goes undetected until a visual QA pass
- header/footer markup duplicated per page instead of one shared component: nav links, legal text, or version numbers drift out of sync across pages
- layout built and tested only at desktop width: breaks silently on tablet/mobile until a real user hits it
- a screen operable only by mouse, or a semantic state carried by color alone: excluded users and legal exposure
- strings, date formats, and left-to-right assumptions spread across components: the first new locale is a rewrite
- nav items that trigger actions, and multi-entity saves that are not atomic within one transaction (see 3.8)
- raw controls, off-scale sizes, and inline colours written screen by screen with no primitive and no check: every screen passes review alone and the system drifts in total (3.12)
- an accidental difference frozen into a primitive as a variant: today's drift becomes the API
- a theme or palette tested for contrast once, in the light theme only (3.13)

---

## Definition of Done

A UI or document is built to this standard when:

### Per change

- all colors reference CSS custom properties; no hardcoded hex values in component styles
- all font sizes map to the defined typographic scale
- elevation, badge variants, surface tokens, content width, and header height match the declared profile (3.11)
- every text token passes the contrast table (1.9): 4.5:1 on each surface it is used on
- token file is the single source of truth: overrides are in a separate block, not inline
- if this app is part of a multi-app suite, its docs reference the canonical token/component source by path (same repo/team) or versioned package (cross-team/multi-repo) rather than retyping values
- for applications (not single static pages): common header, common footer, navigation panel, and application panel each exist as one shared component, not duplicated per page
- layout is checked and usable at desktop (≥1024px), tablet (768–1023px), and mobile (<768px); no fixed-width element exceeds the viewport; no horizontal page scroll
- every screen meets WCAG 2.2 AA: keyboard operable with visible focus, contrast at 4.5:1, meaning never carried by color alone, accessible names on controls; an automated checker runs in CI
- strings, dates, numbers, and currencies are locale-ready, and the layout has been checked once in a right-to-left locale
- UX and information-architecture rules in 3.8 hold: nav items are destinations only; multi-entity saves are atomic within one transaction boundary; variable-size grouped UI computes offsets from content
- recurring UI is built from the declared primitives; a raw control carries a `ds-raw: <reason>` marker; a primitive holds no hex colour and no inline style (3.12)
- every theme and palette is token overrides only and has been checked for contrast (3.13)

### Standing (release and audit)

- the project's CLAUDE.md declares which design profile it uses (the default profile, an inherited sibling, or its own) rather than leaving values implicit
- the scales and token names are declared once as data, with a catalog and a reference page that render every entry; the conformance check runs on every build against a baseline that only falls (3.12)
