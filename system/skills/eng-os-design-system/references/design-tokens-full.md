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
--primary-light:  #8b5cf6;   /* hover state for primary elements */
--primary-glow:   rgba(124,58,237,0.10);  /* tinted backgrounds, badge fills */
```

### 1.2 Color — Semantic

Semantic colors carry meaning. Use them consistently: amber always means caution, red always
means error or required action, green always means success or value. Mixing them destroys the
vocabulary.

```css
--green:       #059669;
--green-soft:  rgba(5,150,105,0.08);    /* tip callouts, value lists */

--amber:       #d97706;
--amber-soft:  rgba(217,119,6,0.08);    /* warnings, behavioral changes */

--red:         #dc2626;
--red-soft:    rgba(220,38,38,0.06);    /* errors, breaking changes */

--cyan:        #0891b2;                 /* informational, secondary accent */
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
--text-muted: #64748b;  /* secondary — labels, metadata, supporting copy */
--text-dim:   #94a3b8;  /* tertiary — disabled, placeholder, decorative */
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
transform: translateY(-1px);
transition: all 0.15s;
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
.badge-improved { background: var(--primary-glow); color: var(--primary); }
.badge-new      { background: var(--green-soft);   color: var(--green); }
.badge-behavior { background: var(--amber-soft);   color: var(--amber); }
.badge-breaking { background: var(--red-soft);     color: var(--red); }
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
border: 1px solid rgba(5,150,105,0.2);
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
