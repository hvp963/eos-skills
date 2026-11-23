# Default Design Profile

The concrete values the Engineering OS ships as its default visual system. A project adopts
this profile unchanged, inherits a sibling app's, or declares its own; the rule at OS level is
only that one profile is declared in CLAUDE.md and referenced from every component
(`SKILL.md`, Rule versus Profile). Canonical source: `../../../meso/design-system.md` Sections 1
to 5; full token table: `design-tokens-full.md`; reference CSS:
`../../../micro/templates/base-styles.css`.

## Design Tokens (condensed)

Full token table (colors, elevation, typography, radius): `design-tokens-full.md`.

- Brand: `--primary`, `--primary-hover` (hover on primary fills), `--primary-text` (primary-hued text on a tint), `--primary-light` (non-text accents), `--primary-glow`, `--on-primary` (text on primary fills)
- Semantic: `--green`/`--amber`/`--red`/`--cyan` for fills, borders, and bars, each with a `-text` token for text in that hue and a `-soft` (or `-glow`) tint; meaning is fixed (green=success, amber=caution, red=error/breaking, cyan=information); never mix
- Surface: `--bg` (page) vs `--surface` (cards); never set page background to `--surface`
- Text: `--text` / `--text-muted` (secondary text and placeholders) / `--text-dim` (disabled and decorative only); every text token's contrast is in the canon's table (Section 1.9)
- Border: `--border` / `--border-bright`
- Elevation: `--shadow-sm` (resting) / `--shadow-md` (hover, modals); no other box-shadow values
- Radius: `sm 6px` (badges/chips) · `md 8px` (callouts/inner tables) · `lg 10–12px` (cards, preferred default) · `full 99px` (pills)

## Typography Hierarchy

One clear primary heading per screen/document. Hierarchy comes from weight and size first; color
reinforces it, never replaces it. Fixed scale: Page Title (26–28px/700) → Section Title (16–18px/700)
→ Card Title (14–15px/600) → Body (14–15px/400) → Secondary body (13–14px/400, muted) →
Label/Eyebrow (10–12px/600–700, uppercase). Do not introduce sizes outside this scale.

## Badge Variants

Seven semantic variants, matching the classes `base-styles.css` ships. Each pairs a tint with its
hue's `-text` token, so the label reaches 4.5:1 on its own fill.

| Class | Fill | Text | Use |
|---|---|---|---|
| `badge-improved` | `--primary-glow` | `--primary-text` | An improvement to something that exists |
| `badge-new` | `--green-soft` | `--green-text` | Something added |
| `badge-behavior` | `--amber-soft` | `--amber-text` | A behavior change to notice |
| `badge-breaking` | `--red-soft` | `--red-text` | A breaking change |
| `badge-fixed` | `--surface-3` | `--text-muted` | A fix |
| `badge-deprec` | `--amber-soft` | `--amber-text` | A deprecation |
| `badge-info` | `--cyan-glow` | `--cyan-text` | Information |

## Sticky Navigation Header

56px, `shadow-sm`, `z-index: 10`. Brand left, metadata right; no primary actions in a document header.

## Layout Principles

Max content width 820–860px. Page padding 40–48px vertical / 24px horizontal, on `--bg`, never
`--surface`. Section spacing 44–48px. Hierarchy through weight/size first, color second. Narrow
(5px) scrollbars on data-heavy layouts.

## Primitive Set

The default set of primitives a project declares (`SKILL.md`, Component Layer), each with a
catalog entry. A project may add to it; a recurring piece of UI that appears a second time becomes
a primitive and gets an entry.

| Primitive | For | Not for |
|---|---|---|
| Button | An action the user starts: primary (one per view), ghost, danger, link | Navigation (use a link); an icon with no words (IconButton) |
| IconButton | An action shown only as an icon; the label is required and becomes the accessible name | An action with room for words |
| Badge | A short state or category marker; always carries words | A count or a figure (Stat) |
| Card | One discrete piece of content of three or more fields; optional title, accent, link | A uniform list (table) or prose |
| Heading | Level 2 to 4 inside a page; level chooses the element, variant the look | The one level 1 heading (the page header) |
| Stat | One figure with its label, read as a term and its definition | A list of many figures |
| EmptyState | What a view shows when there is nothing yet, with the next step as an action | A loading state or an error |
| Field with TextInput, SelectInput, TextArea | One control with its label, hint, and error tied together for assistive technology | A control that is its own label |
| DataTable | Rows with three or more comparable columns, scrolling sideways inside its wrapper | Two-column label/value pairs (definition list) |
