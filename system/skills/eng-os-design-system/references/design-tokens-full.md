# Design Tokens — Full Reference

This file mirrors the token table and component CSS in `meso/design-system.md` so an agent can load
them without the whole guide. Where the two differ, the meso guide wins; edit it first, then
re-copy here. Sibling apps in a suite should point to this file (or to the project's canonical
`globals.css` that implements it) by reference, rather than retyping these values into per-app
docs. See "Design System Inheritance" in `../SKILL.md`.

## 1. Design Tokens

Design tokens are the foundational layer of the visual language. They are named constants that
express *design decisions*, not implementation details.

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

Never set a page background to `--surface`. The contrast between `--bg` and `--surface` is what
makes cards readable.

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

Use `shadow-sm` as the default resting elevation for cards and panels. Use `shadow-md` on hover or
for modals. Never invent `box-shadow` values outside these two levels.

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

Typography communicates structure before content is read. Every screen or document must have a
single clear primary heading. Hierarchy is established through weight and size first: color
reinforces it, not replaces it.

```
Page Title      26–28px  weight 700  letter-spacing -0.4px  color: --text
Section Title   16–18px  weight 700  color: --text  bottom border: 1px --border
Card Title      14–15px  weight 600  color: --text
Body            14–15px  weight 400  color: --text  line-height: 1.6
Secondary body  13–14px  weight 400  color: --text-muted
Label / Eyebrow 10–12px  weight 600–700  uppercase  letter-spacing: 0.05–0.08em
```

**Rule:** Do not introduce a font size outside this scale. Ad-hoc sizes create visual noise and
resist systematic change.

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

**Use cards for:** numbered items, feature descriptions, decisions, breaking change details,
anything with 3+ fields of structured content.

**Do not use cards for:** simple lists of uniform short items (use a table), continuous prose (use
sections).

### 3.2 Badges

Badges communicate state or category inline. Always pair with a human-readable section title;
never use a badge as the sole indicator.

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

Do not use tables for 2-column label/value pairs; use a definition list or card with `dl/dt/dd`.

### 3.4 Callouts

Callouts draw attention to information that must not be missed. Use sparingly; overuse makes
everything appear equally urgent.

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

Keep sticky headers minimal: brand on the left, metadata on the right. Do not put primary actions
in the header of a document; use in-content CTAs or footer links.

---

## 4. Layout Principles

**Max content width:** 820–860px. Do not let prose and cards stretch full-width; it breaks
reading rhythm and makes table columns difficult to scan.

**Page padding:** 40–48px top/bottom, 24px horizontal. The outer `--bg` background provides
breathing room around the white content area. Never set the page body background to `--surface`.

**Section spacing:** 44–48px between major sections. This exceeds normal line-height enough to
signal a topic boundary without requiring a decorative rule on every section.

**Hierarchy through weight, not color:** Establish visual hierarchy with font weight and size
first. A bold 15px heading and a 13px muted label create hierarchy without color. Color then
reinforces (it does not create) that hierarchy.

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

This file is a copy-paste starting point, not a compiled output. It contains all CSS custom
properties, base reset, body styles, scrollbar styles, and the component classes described above.

**How to use:**
1. Copy `base-styles.css` to your project's stylesheet root
2. Rename or prefix if merging with an existing stylesheet
3. Extend by adding project-specific classes that reference the existing tokens
4. If overriding a token for a project (e.g. different brand color), define the override in a
   separate `:root` block; do not edit the token file directly

**Production example:** a web app's `globals.css` and a release-notes system's stylesheet both implement this token set.
