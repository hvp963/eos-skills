# Cross-Platform Portability

**Status:** Current
**Owner:** Haresh V. Parekh
**Scope:** what it takes to use this skill set outside Claude Code.

Source of truth stays here: `SKILL.md` files plus the canonical `meta/macro/meso/micro` prose. Where a tool reads `SKILL.md` natively, the skill folder works as-is and nothing is exported. Where it does not, the tool consumes an **exported, transformed copy**, never a fork maintained by hand, because hand-maintained copies drift apart the way separately edited CLAUDE.md files do.

**This changed materially between December 2025 and March 2026.** Anthropic published `SKILL.md` as an open, model-agnostic standard on 2025-12-18 (specification at [agentskills.io](https://agentskills.io/specification)). As of 2026-10-06, each tool in the table below except Aider documents native `SKILL.md` support. Most of them also read `.claude/skills/` or the shared `.agents/skills/` folder, so one set of links reaches several tools.

---

## Per-platform reality

Paths are what each tool's own documentation lists, checked 2026-10-06. Tools change their discovery paths often; confirm against the current docs before relying on one.

| Platform | Native `SKILL.md`? | Discovery paths (project, then user) | What this repo needs to do |
|---|---|---|---|
| **Claude Code** | Yes | `.claude/skills/`, `~/.claude/skills/` | Nothing; run `tools/install.ps1` or `tools/install.sh`. |
| **OpenAI Codex CLI** | Yes | `.agents/skills/` (current directory and repository root), `~/.agents/skills/`, plus admin and built-in locations | Link or copy `skills/` into `.agents/skills/`. The installer does not target this path. |
| **Google Gemini CLI** | Yes | `.gemini/skills/` or `.agents/skills/`, `~/.gemini/skills/` | Link or copy `skills/` into one of those paths. |
| **GitHub Copilot** (VS Code agent mode, Copilot CLI, cloud agent) | Yes | `.github/skills/`, `.claude/skills/`, `.agents/skills/`; `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | Nothing if the installer already linked `.claude/skills/`; otherwise copy into `.github/skills/`. |
| **Cursor** | Yes | `.cursor/skills/`, `.agents/skills/`, and for compatibility `.claude/skills/` and `.codex/skills/`; user-level `~/.cursor/skills/`, `~/.agents/skills/` | Nothing if the installer already linked `.claude/skills/`. |
| **Windsurf** | Yes (documented under Devin's skills format) | `.devin/skills/`, `.windsurf/skills/` (legacy), `.agents/skills/`, `.claude/skills/`; global `~/.codeium/windsurf/skills/` | Nothing if the installer already linked `.claude/skills/`. |
| **Cline** | Yes | `.cline/skills/` (recommended), `.clinerules/skills/`, `.claude/skills/`; global `~/.cline/skills/` | Nothing if the installer already linked `.claude/skills/`. |
| **Aider** | No `SKILL.md` support found | Single `CONVENTIONS.md`, always fully in context | Concatenate a subset into one file. This is the one lossy target: there is no selective loading, so export only the Tier 1 and Tier 2 skills from `MINDMAP.md` rather than all 28, or context grows on every turn. |

**Confidence note (checked 2026-10-06):** Native support and discovery paths for Cursor, Windsurf, Cline, and Codex CLI were read from each tool's own documentation on that date. Gemini CLI paths come from the earlier 2026-10-02 check, and Copilot paths were rechecked on 2026-10-06. No search turned up `SKILL.md` support in Aider; treat that as unconfirmed rather than as proof it is absent. Documentation says a tool supports the format; it does not show that this repo's 28 skills load and route correctly in it. Re-run this check at each release.

---

## What is lost in each direction

- **Every tool marked Yes above**: nothing structural, because the file format and progressive-disclosure model are the same. The remaining risks are discovery-path changes and how each tool treats the extra frontmatter keys (`globs`, `always_apply`, `verified_platforms`). Check both on first use.
- **Aider**: loses all conditional loading. Exporting everything produces one large always-in-context file, so the fix is to export less, not to export losslessly. A skill written to trigger on "use when reviewing an incident" has no equivalent trigger in this format.
- No platform round-trips back into Claude Code. An export, where one is needed, is one-directional, so there is no bidirectional-sync problem to design for.

---

## Why the frontmatter carries extra fields

`globs`, `always_apply`, and `verified_platforms` were added to every skill so a tool that needs a transform has the data without re-deriving it:

- `globs` maps to the glob trigger of rules-based formats (Cursor `.mdc` rules, Windsurf rules). Tools that read `SKILL.md` natively do not need it.
- `always_apply` maps to `alwaysApply` (Cursor rules) or "Always On" (Windsurf rules); it is `true` only on `eng-os-core`.
- `verified_platforms` records which platforms a skill has been exercised on and confirmed to load. It is a record of testing and not a list of intended targets. All skills list only `[claude-code]` because that is the only platform this content has been run on. Broaden a skill's list only after testing it elsewhere; Codex CLI, Gemini CLI, Copilot, Cursor, Windsurf, and Cline are the next candidates, since they need no transform to test. An export script can also use it to skip Claude-Code-specific skills that reference `.ids` files or `CLAUDE.md` conventions (`eng-os-bootstrap`, `eng-os-ai-ids-authoring`) when exporting to a tool where those conventions do not exist.

These fields are additive. Claude Code ignores unknown frontmatter keys, so none of this changes its behavior.

---

## What does not exist yet

- No export script exists for Aider.
- No automated test loads these skills in any tool other than Claude Code; CI verifies the installer's links and the lint checks only.
- Trying this repo's `skills/` folder directly in Codex CLI, Gemini CLI, Copilot, Cursor, Windsurf, or Cline is low-cost and the right next step before building any exporter.
