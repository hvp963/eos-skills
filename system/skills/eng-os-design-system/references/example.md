# Worked Example — Tokens, a Component Class, and Inheritance Declarations

Source: illustrates `../SKILL.md` Design Tokens and Design System Inheritance sections with
concrete declarations. Full token table lives in `design-tokens-full.md`.

## Concrete Tokens (as actually declared)

```css
:root {
  --bg:      #f0f4f9;  /* page background */
  --surface: #ffffff;  /* card/panel surface */
  --primary: #7c3aed;  /* primary action, focus rings */
  --text:    #0f172a;  /* primary body text */
}
```

## Concrete Component Class

```css
.btn-primary {
  background: var(--primary);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--primary-light);
  box-shadow: var(--shadow-md);
}
```
Note what makes this compliant: no hardcoded hex values (`var(--primary)`, not `#7c3aed`, inside
the component rule), radius from the defined scale (`8px` = `md`), and shadow from the two-level
elevation system only.

## Design System Inheritance — Path-Reference vs. Versioned-Package

**Case A: sibling app in the same monorepo (path-reference version).**
App 3's project docs (`CLAUDE.md` or design notes) should declare inheritance like this,
pointing at the canonical source, not retyping it:

```markdown
## Design System
This app inherits its visual language from the shared design system. Canonical source:
- Tokens & component patterns: <path-to-engineering-os>/system/skills/design-system/references/design-tokens-full.md
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
