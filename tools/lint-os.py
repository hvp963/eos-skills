#!/usr/bin/env python3
"""Lint the Engineering OS against its own contracts.

Checks (all fail the run):
  1. Every SKILL.md has frontmatter with name, description, sources, globs, always_apply,
     verified_platforms; name matches its folder path (nested folders joined with '-');
     sources is a non-empty list; always_apply is true only for eng-os-core.
  2. Every sources: path exists relative to system/.
  3. Every SKILL.md has a '## Definition of Done' section and either an inline '## Example'
     or a references/ folder.
  4. The skill count stated in README.md, ABOUT.md, skills/README.md, skills/MINDMAP.md,
     skills/PORTABILITY.md matches the number
     of SKILL.md files on disk, and the stated document count matches the .md files under
     meta/, macro/, meso/, and micro/; every skill named in MINDMAP.md's diagram exists.
  5. Every relative markdown link ([text](path)) resolves to a file.
  6. No em dash joins two clauses in flowing prose (letters on both sides of ' — '),
     outside headings, code blocks, and frontmatter. Table cells are checked too; a cell may
     use the `Label — definition` form, where the label before the dash is three words or
     fewer. A demonstration of the banned pattern sits between
     `<!-- lint-os: allow-em-dash-begin -->` and `<!-- lint-os: allow-em-dash-end -->`.
  7. The message-code format is stated consistently as 3 letters + 6 digits (no {AREA}{NNNN}).
  8. Backticked file paths in the normative docs resolve: layer paths (meta/, macro/, meso/,
     micro/, skills/) from system/, `../` paths from the file, `references/` paths from the skill.
  9. Every references/*.md file is named in its skill's SKILL.md, so an agent reading only
     the skill body can find it.
 10. Text copied verbatim from a canonical doc into a skill file (a paragraph of 220+ characters)
     comes from a doc listed in that skill's `sources:`. A copy with no declared source has
     no owner to keep it in sync.
 11. Every skill description is a double-quoted YAML string, so a ": " or " #" inside it cannot
     break a strict parser.
 12. No retired term returns: `JSDoc-style`, `BACKOFF_MS`, `backoffMs`, the fixed
     `[50, 100, 200, 500]` schedule, `MAX_ATTEMPTS`, `MAX_RETRIES`, or `severity` in a log-field
     list beside `trace_id`. History (CHANGELOG.md, docs/decisions/, evidence/) is exempt.
 13. Every "Standard N" citation names a standard that exists in micro/coding-standards/common.md,
     and a title written beside it matches that standard's heading.

Usage: python tools/lint-os.py [--fix-counts]
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SYS = ROOT / "system"
errors = []

def err(path, line, msg):
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    errors.append(f"{rel}:{line}: {msg}")

# ---------- 1-3: skill frontmatter and structure ----------
skills = sorted(SYS.glob("skills/**/SKILL.md"))
skill_names = set()
skill_sources = {}
REQUIRED = ["name", "description", "sources", "globs", "always_apply", "verified_platforms"]
for sk in skills:
    text = sk.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(sk, 1, "missing YAML frontmatter"); continue
    fm = m.group(1)
    fields = {}
    cur = None
    for ln in fm.split("\n"):
        if ln.startswith("#"): continue
        km = re.match(r"^([a-z_]+):\s*(.*)$", ln)
        if km:
            cur = km.group(1); fields[cur] = km.group(2).strip()
        elif cur and ln.strip().startswith("- "):
            fields[cur] = (fields[cur] + "\n" if fields[cur] else "") + ln.strip()[2:]
    for f in REQUIRED:
        if f not in fields: err(sk, 1, f"frontmatter missing `{f}`")
    rel_folder = sk.parent.relative_to(SYS / "skills")
    expected = "-".join(rel_folder.parts)
    if fields.get("name") != expected:
        err(sk, 2, f"name `{fields.get('name')}` does not match folder `{expected}`")
    skill_names.add(fields.get("name", expected))
    srcs = fields.get("sources", "")
    src_list = [s.strip() for s in re.split(r"[\n,]", srcs.strip("[] ")) if s.strip()]
    if not src_list:
        err(sk, 1, "sources: is empty; every skill needs a canonical source doc")
    for s in src_list:
        if not (SYS / s).exists(): err(sk, 1, f"sources path does not exist: {s}")
    dv = fields.get("description", "")
    if not (len(dv) > 1 and dv.startswith('"') and dv.endswith('"')):
        err(sk, 3, "description must be a double-quoted YAML string")
    skill_sources[sk.parent] = set(src_list)
    aa = fields.get("always_apply", "")
    if aa == "true" and expected != "eng-os-core": err(sk, 1, "always_apply: true is reserved for eng-os-core")
    if expected == "eng-os-core" and aa != "true": err(sk, 1, "eng-os-core must have always_apply: true")
    if not re.search(r"^## .*Definition of Done", text, re.M): err(sk, 1, "no `## ... Definition of Done` section")
    if "## Example" not in text and not (sk.parent / "references").is_dir():
        err(sk, 1, "no inline `## Example` and no references/ folder")

n_skills = len(skills)

# ---------- 4: counts and MINDMAP names ----------
# Any bare "N skill(s)" mention in these files must equal n_skills. A general pattern
# rather than a per-phrasing whitelist, so a new sentence mentioning the count can't
# silently bypass the check.
count_files = [
    SYS / "README.md", SYS / "ABOUT.md", SYS / "skills/README.md", SYS / "skills/MINDMAP.md",
    SYS / "skills/PORTABILITY.md",
]
COUNT_RE = re.compile(r"(?<![\d.,])(\d+)[\s-]+(?:individual\s+)?(?:domain\s+)?(?:Claude\s+Code\s+)?skills?")
n_docs = sum(1 for layer in ("meta", "macro", "meso", "micro") for _ in (SYS / layer).rglob("*.md"))
DOC_RE = re.compile(r"(?<![\d.,])(\d+)\s+(?:prose\s+|canonical\s+)?documents\b|(?<![\d.,])(\d+)\s+(?:prose|canonical)\s+files\b|\ball\s+(\d+)\s+(?:prose\s+|canonical\s+)?files")
for p in count_files:
    if not p.exists(): err(p, 1, "count file missing"); continue
    t = p.read_text(encoding="utf-8")
    for mm in COUNT_RE.finditer(t):
        n = int(mm.group(1))
        if n == n_skills or n < 5:  # small numbers are usually "3 sub-skills", not the total
            continue
        ln = t[:mm.start()].count(chr(10)) + 1
        err(p, ln, f"says {n} skills; {n_skills} on disk")
    for mm in DOC_RE.finditer(t):
        n = int(next(g for g in mm.groups() if g))
        if n == n_docs:
            continue
        ln = t[:mm.start()].count(chr(10)) + 1
        err(p, ln, f"says {n} documents; {n_docs} in meta/macro/meso/micro")

mind = (SYS / "skills/MINDMAP.md").read_text(encoding="utf-8")
for name in re.findall(r"^\s+[A-Z]+\[([a-z][a-z0-9-]+)(?:<br/>|\])", mind, re.M):
    if name not in skill_names and name != "eng-os-coding-standards":
        err(SYS / "skills/MINDMAP.md", 1, f"diagram names skill `{name}` which does not exist")
for name in skill_names:
    if name not in mind and not name.startswith("eng-os-coding-standards-"):
        err(SYS / "skills/MINDMAP.md", 1, f"skill `{name}` is not mentioned in MINDMAP")

# ---------- 5: relative links ----------
md_files = list(SYS.rglob("*.md"))
link_re = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
for p in md_files:
    if not p.exists(): continue
    t = p.read_text(encoding="utf-8")
    for i, ln in enumerate(t.split("\n"), 1):
        for target in link_re.findall(ln):
            if re.match(r"^[a-z]+:", target): continue
            tp = (p.parent / target).resolve()
            if not tp.exists(): err(p, i, f"broken link: {target}")

# ---------- 6: em dash joining clauses ----------
EM = re.compile(r"[A-Za-z0-9)\]`'\"] — [A-Za-z(`'\"]")
for p in md_files:
    if not p.exists(): continue
    if p.name in ("CHANGELOG.md",): continue  # historical record, kept verbatim
    t = p.read_text(encoding="utf-8")
    in_code = False; in_fm = False; allowed = False
    for i, ln in enumerate(t.split(chr(10)), 1):
        s = ln.strip()
        # a demonstration of the banned pattern is fenced by a begin/end pair, never a whole file
        if "<!-- lint-os: allow-em-dash-begin -->" in s: allowed = True; continue
        if "<!-- lint-os: allow-em-dash-end -->" in s: allowed = False; continue
        if allowed: continue
        if i == 1 and s == "---": in_fm = True; continue
        if in_fm:
            if s == "---": in_fm = False; continue
            # description: is prose an agent reads for routing; check it like any other
            # sentence. Other frontmatter lines (name/sources/globs/always_apply/
            # verified_platforms and their list items) are YAML structure, not prose.
            if not s.startswith("description:"): continue
        if s.startswith("```"): in_code = not in_code; continue
        if in_code or s.startswith("#"): continue
        if s.startswith("|"):
            # table cells: a `Label — definition` cell is allowed when the label is short
            for cell in s.strip("|").split("|"):
                mm = EM.search(cell)
                if mm and len(cell[:mm.start() + 1].split()) > 3:
                    err(p, i, "em dash joins two clauses in a table cell (prose-style hard ban)")
                    break
            continue
        if EM.search(ln):
            err(p, i, "em dash joins two clauses in flowing prose (prose-style hard ban)")

# ---------- 7: message code format ----------
NORMATIVE = ("skills", "meso", "micro", "meta", "macro")
for p in md_files:
    if not p.exists() or p.name == "CHANGELOG.md": continue
    if not any(part in NORMATIVE for part in p.relative_to(ROOT).parts): continue  # normative layers only
    t = p.read_text(encoding="utf-8")
    for i, ln in enumerate(t.split("\n"), 1):
        if "{AREA}{NNNN}" in ln or "CT0001" in ln:
            err(p, i, "stale message-code format; standard is 3 letters + 6 digits")


# ---------- 8: backticked file paths ----------
LAYER_RE = re.compile(r"`((?:meta|macro|meso|micro|skills)/[A-Za-z0-9_./\-]+\.(?:md|py|ps1|sh))`")
UP_RE = re.compile(r"`((?:\.\./)+[A-Za-z0-9_./\-]+\.md)`")
REF_RE = re.compile(r"`(references/[A-Za-z0-9_./\-]+\.md)`")
SKIP_PATH_FILES = ("CHANGELOG.md",)
for p in md_files:
    if not p.exists() or p.name in SKIP_PATH_FILES or "decisions" in p.parts: continue
    t = p.read_text(encoding="utf-8")
    in_skills = (SYS / "skills") in p.parents
    skill_dir = None
    if in_skills:
        skill_dir = next((a for a in [p.parent, *p.parents] if (a / "SKILL.md").exists()), None)
    for i, ln in enumerate(t.split("\n"), 1):
        for m in LAYER_RE.finditer(ln):
            if not (SYS / m.group(1)).exists():
                err(p, i, f"path does not resolve: {m.group(1)}")
        for m in UP_RE.finditer(ln):
            if not (p.parent / m.group(1)).resolve().exists():
                err(p, i, f"relative path does not resolve: {m.group(1)}")
        if skill_dir:
            for m in REF_RE.finditer(ln):
                if not (skill_dir / m.group(1)).exists():
                    err(p, i, f"references path does not resolve: {m.group(1)}")

# ---------- 9: references are reachable from SKILL.md ----------
for sk in skills:
    rdir = sk.parent / "references"
    if not rdir.is_dir(): continue
    body = sk.read_text(encoding="utf-8")
    for f in sorted(rdir.rglob("*.md")):
        if f.name not in body:
            err(f, 1, f"not named in {sk.relative_to(ROOT)}; an agent reading only the skill cannot find it")

# ---------- 10: copied canonical text must be sourced ----------
def _norm(s): return re.sub(r"\s+", " ", s).strip()
canon = {}
for layer in ("meta", "macro", "meso", "micro"):
    for cp in (SYS / layer).rglob("*.md"):
        canon[cp] = _norm(cp.read_text(encoding="utf-8"))
for f in sorted((SYS / "skills").rglob("*.md")):
    if f.name == "README.md" or f.name == "MINDMAP.md" or f.name == "PORTABILITY.md": continue
    owner = next((a for a in [f.parent, *f.parents] if a in skill_sources), None)
    if owner is None: continue
    raw = f.read_text(encoding="utf-8")
    if raw.startswith("---\n"):
        raw = raw[raw.index("\n---\n", 4) + 5:]
    allowed = {(SYS / s) for s in skill_sources[owner]}
    for blk in re.split(r"\n\s*\n", raw):
        q = _norm(blk)
        if len(q) < 220 or q.startswith("|"): continue
        hits = [cp for cp, ct in canon.items() if q in ct]
        if hits and not any(h in allowed for h in hits):
            where = raw[:raw.index(blk)].count("\n") + 1
            err(f, where, f"copies text from {hits[0].relative_to(SYS)}, which is not in this skill's sources:")

# ---------- 12: retired terms ----------
RETIRED = [
    (re.compile(r"JSDoc-style"), "`JSDoc-style` (docstrings are per language: JSDoc for TypeScript, Google style for Python)"),
    (re.compile(r"\bBACKOFF_MS\b|\bbackoffMs\b"), "a fixed backoff table (retry uses full jitter, common.md Standard 5)"),
    (re.compile(r"\[50, ?100, ?200, ?500"), "the fixed [50, 100, 200, 500] retry schedule"),
    (re.compile(r"\bMAX_ATTEMPTS\b"), "`MAX_ATTEMPTS` (the setting is `{AREA}_NUM_RETRIES`, retries after the first call)"),
    (re.compile(r"\bMAX_RETRIES\b"), "`MAX_RETRIES` as a constant (a retry count is config: `{AREA}_NUM_RETRIES`)"),
]
SEVERITY_FIELD = re.compile(r"severity")
for p in md_files:
    if not p.exists() or p.name == "CHANGELOG.md": continue
    parts = p.relative_to(SYS).parts
    if "decisions" in parts or "evidence" in parts: continue  # history keeps its own words
    t = p.read_text(encoding="utf-8")
    for i, ln in enumerate(t.split("\n"), 1):
        for rx, why in RETIRED:
            if rx.search(ln):
                err(p, i, f"retired term: {why}")
        if SEVERITY_FIELD.search(ln) and "trace_id" in ln:
            err(p, i, "retired term: `severity` as a log field (the field is `level`)")

# ---------- 13: numbered-standard citations ----------
common_text = (SYS / "micro/coding-standards/common.md").read_text(encoding="utf-8")
STD_TITLES = {m.group(1): m.group(2).strip() for m in re.finditer(r"^### (\d+[a-z]?)\. (.+)$", common_text, re.M)}
TITLE_WORDS = {n: title.split(":")[0].split(",")[0].split(" ")[0].lower() for n, title in STD_TITLES.items()}
STD_RE = re.compile(r"\bStandard (\d+[a-z]?)\b(?:[ ,(:]+\(?([A-Z][A-Za-z-]+))?")
for p in md_files:
    if not p.exists() or p.name == "CHANGELOG.md": continue
    if "decisions" in p.relative_to(SYS).parts: continue
    t = p.read_text(encoding="utf-8")
    for i, ln in enumerate(t.split("\n"), 1):
        for m in STD_RE.finditer(ln):
            n, word = m.group(1), m.group(2)
            if n not in STD_TITLES:
                err(p, i, f"cites Standard {n}, which common.md does not define")
                continue
            if word and word.lower() in TITLE_WORDS.values() and word.lower() != TITLE_WORDS[n]:
                err(p, i, f"cites Standard {n} as `{word}`; Standard {n} is `{STD_TITLES[n]}`")

# ---------- report ----------
if errors:
    for e in errors: print(e)
    print(f"\n{len(errors)} problem(s); {n_skills} skills on disk")
    sys.exit(1)
print(f"OK: {n_skills} skills, {len(md_files)} markdown files, no problems")
