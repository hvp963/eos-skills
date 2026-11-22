# Component Layer: Rules, Catalog Entry, and Adoption

Detail behind `SKILL.md` (Component Layer) and `meso/design-system.md` 3.12 and 3.13. Examples use
a web stack (React, Tailwind, Jest) because that is where the pattern was proven; the rules do not
depend on it.

## The conformance check: five rules

The check reads each source file as text and counts, per file:

| Rule | What it counts | Notes |
|---|---|---|
| `hex` | A hex colour value | Skip anchors and ids (`href="#top"`, `url(#gradient)`) and comment lines |
| `type-size` | A text size outside the declared scale | An arbitrary value (`text-[13px]`) or a size above the scale |
| `radius` | A corner radius outside the declared steps | Arbitrary values and steps the scale omits |
| `inline-colour` | A colour set through an inline `style` object | A computed value (a template with `${}`) is allowed: dynamic values may stay inline |
| `raw-control` | A raw `<button>`, `<input>`, `<select>`, `<textarea>`, or `<table>` | Not counted inside the primitives folder, or when the previous line has `ds-raw: <reason>` |

Allowed homes for a hex colour are named explicitly (the palette table, the constants file, and
reference-content pages that carry their own baseline). Everything else is allowed none.

The shell, the shared components, and the entity screens are held stricter than the baseline: no
raw control except a marked one, and no inline colour at all. Off-scale sizes and radii are
allowed nowhere. Only the unmigrated screens ride the baseline.

## Catalog entry shape

| Field | Content |
|---|---|
| name | The component name |
| kind | `primitive` (a file in the primitives folder) or `existing` (an older shared component adopted as it is) |
| file | Source path from the project root |
| variants | The variants the reference page draws, in order |
| use | What it is for |
| not for | What it is not for, and what to use instead |

Two tests keep it honest: a file in the primitives folder with no `primitive` entry fails, and an
entry whose file does not exist or that has no example on the reference page fails.

## Adoption sequence on an existing app

1. Count what exists (raw controls by tag, off-scale sizes and radii, hex colours, inline colour
   styles) so the baseline starts from a real number.
2. Write the declaration (scales, token names) and a test that every token it names is in the
   stylesheet.
3. Build the primitives from the classes the screens already use. List each unification of an
   accidental difference.
4. Write the catalog and the reference page.
5. Add the check and write the baseline once. From here it can only fall.
6. Migrate the shell, the shared components, and the entity screens, move every off-scale size,
   radius, and hex colour onto the scales and tokens, then migrate one area at a time, lowering
   baseline entries as each file is fixed.

## Ratchet wiring

The check follows `eng-os-testing-strategy` Ratchet Baselines. A baseline is a committed JSON
file of `{ file: { rule: count } }`; the test fails on a count above it, on a count below it with
"lower the baseline to N", and on an entry whose file no longer exists. A command (an environment
flag on the same test) rewrites the file from the tree, for adoption only.

## Themes

Declare the base tokens, then each palette and the dark theme as override blocks of the same
names. A palette changes the accent tokens; the dark theme redeclares surfaces, text, borders,
semantic colours, and shadows, and each palette gets a dark value too. Run the accessibility check
once per theme and palette, since a value that reaches 4.5:1 in one can fail in another.
