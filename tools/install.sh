#!/usr/bin/env sh
# Registers every Engineering OS skill with Claude Code by symlinking one directory per skill
# into ~/.claude/skills (and optionally <project>/.claude/skills). Claude Code discovers skills
# at <root>/.claude/skills/<name>/SKILL.md; nested skills register under their frontmatter name
# (eng-os-coding-standards/common -> eng-os-coding-standards-common). Re-run after adding a skill.
#
#   tools/install.sh                       # user-level
#   tools/install.sh --project /path/app   # also into that project
#   tools/install.sh --remove              # remove the links

set -eu
repo_root=$(cd "$(dirname "$0")/.." && pwd)
skills_src="$repo_root/system/skills"
project=""
remove=0
while [ $# -gt 0 ]; do
  case "$1" in
    --project) project="$2"; shift 2 ;;
    --remove)  remove=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

skill_name() { sed -n 's/^name:[[:space:]]*\(.*\)[[:space:]]*$/\1/p' "$1" | head -n 1; }

install_into() {
  target="$1"; mkdir -p "$target"; n=0
  find "$skills_src" -name SKILL.md | while read -r f; do
    name=$(skill_name "$f"); [ -n "$name" ] || { echo "no name: in $f" >&2; exit 1; }
    link="$target/$name"
    [ -L "$link" ] && rm "$link"
    if [ "$remove" -eq 0 ]; then ln -s "$(dirname "$f")" "$link"; fi
  done
  if [ "$remove" -eq 0 ]; then echo "linked skills into $target"; else echo "removed skill links from $target"; fi
}

install_into "$HOME/.claude/skills"
[ -n "$project" ] && install_into "$project/.claude/skills"
[ "$remove" -eq 0 ] && echo "Start a new Claude Code session and confirm the eng-os-* skills appear in its skill list."
exit 0
