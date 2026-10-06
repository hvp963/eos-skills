<#
.SYNOPSIS
  Registers every Engineering OS skill with Claude Code by creating one directory junction per
  skill under the user's skills folder (and optionally a project's .claude\skills folder).

.DESCRIPTION
  Claude Code discovers skills at %USERPROFILE%\.claude\skills\<name>\SKILL.md and
  <project>\.claude\skills\<name>\SKILL.md. It does not follow Windows .lnk shortcuts.
  This script reads each SKILL.md frontmatter `name` and creates a junction with that name
  pointing at the skill's folder, so nested skills (eng-os-coding-standards\common) register as
  eng-os-coding-standards-common. Junctions need no administrator rights. Re-run after adding a skill.

.PARAMETER Project
  Optional path to a project; the same junctions are created under <Project>\.claude\skills.

.PARAMETER Remove
  Remove the junctions this script would create, instead of creating them.
#>
param(
  [string]$Project = "",
  [switch]$Remove
)

$ErrorActionPreference = "Stop"
$repoRoot  = Split-Path -Parent $PSScriptRoot
$skillsSrc = Join-Path $repoRoot "system\skills"

function Get-SkillName([string]$skillFile) {
  $head = Get-Content $skillFile -TotalCount 40
  foreach ($line in $head) {
    if ($line -match '^name:\s*(.+?)\s*$') { return $Matches[1] }
  }
  throw "no name: in frontmatter of $skillFile"
}

function Install-Into([string]$targetRoot) {
  if (-not (Test-Path $targetRoot)) { New-Item -ItemType Directory -Force $targetRoot | Out-Null }
  $created = 0; $removed = 0
  Get-ChildItem -Path $skillsSrc -Recurse -Filter SKILL.md | ForEach-Object {
    $name = Get-SkillName $_.FullName
    $link = Join-Path $targetRoot $name
    if ($Remove) {
      if (Test-Path $link) { (Get-Item $link).Delete(); $removed++ }
    } else {
      if (Test-Path $link) { (Get-Item $link).Delete() }
      New-Item -ItemType Junction -Path $link -Target $_.DirectoryName | Out-Null
      $created++
    }
  }
  if ($Remove) { "removed $removed skill links from $targetRoot" } else { "linked $created skills into $targetRoot" }
}

Install-Into (Join-Path $env:USERPROFILE ".claude\skills")
if ($Project -ne "") { Install-Into (Join-Path $Project ".claude\skills") }
if (-not $Remove) { "Start a new Claude Code session and confirm the eng-os-* skills appear in its skill list." }
