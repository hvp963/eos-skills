# Security Policy

This repository is a body of written standards plus three small tools. It runs no service and stores no user data, so the realistic security reports are about:

- `tools/install.sh` and `tools/install.ps1`, which create symlinks or junctions under `~/.claude/skills` or a project's `.claude/skills`
- `tools/lint-os.py`, which reads files in this repository
- `.github/workflows/lint.yml`
- guidance in `system/` that would lead a reader to write insecure code (for example in `meso/security.md` or `eng-os-security-practices`)

## Reporting

Please report privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Do not open a public issue for something exploitable.

Include the file, what you did, what happened, and what you expected. For guidance that is wrong or unsafe, quote the passage and say what a safer statement would be.

Reports are reviewed on a best-effort basis by one maintainer. There is no fixed response time.

## Supported versions

Only the latest tagged release is maintained. Fixes ship in the next release and are listed in `system/CHANGELOG.md`.
