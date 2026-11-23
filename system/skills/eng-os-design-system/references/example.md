# Worked Example — Tokens, a Component Class, and Inheritance Declarations

Source: illustrates `../SKILL.md` Design Tokens and Design System Inheritance sections with
concrete declarations. Full token table lives in `design-tokens-full.md`.

## Concrete Tokens (as declared)

```css
:root {
  --bg:      #f0f4f9;  /* page background */
  --surface: #ffffff;  /* card/panel surface */
  --primary: #7c3aed;  /* primary action, focus rings */
  --primary-hover: #6d28d9;  /* hover on primary fills; white on it is 7.10:1 */
  --on-primary: #ffffff;     /* text on primary fills: 5.70:1 */
  --text:    #0f172a;  /* primary body text */
}
```

## Concrete Component Class

```css
.btn-primary {
  background: var(--primary);
  color: var(--on-primary);
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--primary-hover);
  box-shadow: var(--shadow-md);
}
```
Note what makes this compliant: every colour is a token (`var(--primary)` and `var(--on-primary)`,
never `#7c3aed` or `#ffffff`, inside the component rule), the hover fill is `--primary-hover`
because white on `--primary-light` is only 4.23:1, the radius comes from the defined scale (`8px` =
`md`), and both shadows come from the two-level elevation system. Hex values appear only in the
token declarations above. Keyboard focus comes from the shared `:focus-visible` rule in
`base-styles.css`, so the component does not remove the outline.

## Design System Inheritance — Path-Reference vs. Versioned-Package

**Case A: sibling app in the same monorepo (path-reference version).**
App 3's project docs (`CLAUDE.md` or design notes) should declare inheritance like this,
pointing at the canonical source, not retyping it:

```markdown
## Design System
This app inherits its visual language from the shared design system. Canonical source:
- Tokens & component patterns: <path-to-engineering-os>/system/skills/eng-os-design-system/references/design-tokens-full.md
- Base CSS: <path-to-engineering-os>/system/micro/templates/base-styles.css

Do not redeclare token values here. Project-specific overrides (if any) go in
`src/app/globals.css` under a separate `:root` block, referencing the canonical file above.
```

**Case B: cross-team / multi-repo (versioned-package version).**
Once app 3 lives in a separate repo/team with no shared filesystem access, the same intent is
declared as a dependency instead of a path:

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
`@acme/design-tokens`. Current pinned version: 2.3.0 (see package.json). Do not hand-copy token
values; bump the package version deliberately and re-review affected components on major bumps.
```

The difference: Case A resolves at read-time via a filesystem path and updates immediately when
the canonical file changes (fine within one team's blast radius); Case B resolves at
install-time via a pinned semver version, requires a deliberate bump to pick up changes, and
survives the source and consumer living in different repos.
