# Engineering OS

A layered body of engineering standards (principles, design guides, implementation standards, templates) for teams building product, data, and AI systems, plus 28 skills that let AI coding agents load the right standard at the right moment.

**Author:** Haresh V. Parekh · **Version:** see `system/VERSION` · **License:** CC BY 4.0 for `system/`, MIT for `tools/` and `.github/` (see `LICENSE`)

## Where things are

| Path | Contents |
|---|---|
| `system/` | The standards. Start at `system/README.md`; `system/ABOUT.md` explains the design and the research behind it. |
| `system/skills/` | The 28 skills in the open `SKILL.md` format, with `README.md`, `MINDMAP.md`, and `PORTABILITY.md`. |
| `tools/` | `install.ps1` and `install.sh` register the skills with Claude Code; `lint-os.py` checks the repository against its own rules (CI runs it). |

## Quick start

- **Get it:** `git clone https://github.com/hvp963/eos-skills`, or download the latest release as a ZIP.
- **Read it as prose:** follow "How to Start" in `system/README.md`.
- **Use it with Claude Code:** run `tools/install.ps1` (Windows) or `tools/install.sh` (macOS, Linux), start a new session, and confirm the `eng-os-*` skills appear. Other agents that read `SKILL.md` are covered in `system/skills/PORTABILITY.md`.
- **Check the repository:** `python tools/lint-os.py`

## Start a project with it

Installing the skills makes them available. To have every new project governed from its first file, add this to your user-level instructions (for Claude Code, `~/.claude/CLAUDE.md`), replacing the path with where you cloned this repository:

```markdown
## Bootstrap every new project into the Engineering OS

Before writing the first line of code on a new project (a fresh repo, or an existing repo whose
CLAUDE.md has no `## Engineering Standards` section), run the `eng-os-bootstrap` skill. The
Engineering OS is at <path-to-your-clone>.
```

`eng-os-bootstrap` checks whether the project is worth the full template, picks the skills that apply, and writes the project's `CLAUDE.md`. Its steps are in `system/skills/eng-os-bootstrap/SKILL.md`.

## Notice

This is one practitioner's point of view, written in good faith from experience with production workloads serving millions of users. It does not represent any employer, it is not professional advice, and every company's approach differs. Facts about third-party tools were checked on the dates stated in the text and change quickly. If something has missed the mark, open an issue and it will be reviewed and updated. The full notice is in `system/README.md`.
