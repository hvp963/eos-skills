# Default Design Profile

The concrete values the Engineering OS ships as its default visual system. A project adopts
this profile unchanged, inherits a sibling app's, or declares its own; the rule at OS level is
only that one profile is declared in CLAUDE.md and referenced from every component
(`SKILL.md`, Rule versus Profile). Canonical source: `../../../meso/design-system.md` Sections 1,
2, and 4; full token table: `design-tokens-full.md`; reference CSS:
`../../../micro/templates/base-styles.css`.

## Design Tokens (condensed)

Full token table (colors, elevation, typography, radius): `design-tokens-full.md`.

- Brand: `--primary`, `--primary-light`, `--primary-glow`
- Semantic: `--green`/`--amber`/`--red` (+ `-soft` tints); meaning is fixed (green=success, amber=caution, red=error/breaking); never mix
- Surface: `--bg` (page) vs `--surface` (cards); never set page background to `--surface`
- Text: `--text` / `--text-muted` / `--text-dim`
- Border: `--border` / `--border-bright`
- Elevation: `--shadow-sm` (resting) / `--shadow-md` (hover, modals); no other box-shadow values
- Radius: `sm 6px` (badges/chips) · `md 8px` (callouts/inner tables) · `lg 10–12px` (cards, preferred default) · `full 99px` (pills)

## Typography Hierarchy

One clear primary heading per screen/document. Hierarchy comes from weight and size first; color
reinforces it, never replaces it. Fixed scale: Page Title (26–28px/700) → Section Title (16–18px/700)
→ Card Title (14–15px/600) → Body (14–15px/400) → Secondary body (13–14px/400, muted) →
Label/Eyebrow (10–12px/600–700, uppercase). Do not introduce sizes outside this scale.

## Sticky Navigation Header

56px, `shadow-sm`, `z-index: 10`. Brand left, metadata right; no primary actions in a document header.

## Layout Principles

Max content width 820–860px. Page padding 40–48px vertical / 24px horizontal, on `--bg`, never
`--surface`. Section spacing 44–48px. Hierarchy through weight/size first, color second. Narrow
(5px) scrollbars on data-heavy layouts.
