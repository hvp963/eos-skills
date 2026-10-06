# Worked Example — Small Next.js + SQLite App

Source: illustrates `../SKILL.md` CI/CD Pipeline, Health Checks, and Rollback sections applied to
one real, small deployment.

## Pipeline Stages

```yaml
# .github/workflows/deploy.yml (illustrative)
stages:
  - lint:            eslint + tsc --noEmit; fails the build on any error
  - test:             vitest run (unit + integration against an ephemeral SQLite file)
  - build:            next build; artifact tagged with the git SHA (app-${GIT_SHA}.tar.gz)
  - deploy_stage:      unpack tagged artifact to the stage host; run DB migrations; restart process
  - health_check:      poll stage's /health/ready for up to 60s before proceeding
  - promote_prod:      copy the *same* SHA-tagged artifact to prod (never rebuilt); run migrations; restart
  - health_check_prod: poll prod's /health/ready for up to 60s; on failure, trigger rollback
```
Each stage gates the next: a lint failure never reaches `build`, a failed stage health check
never reaches `promote_prod`.

## Concrete Health Check

`GET /health/ready` for this app actually verifies, in order:
1. the SQLite file at `DATABASE_PATH` is present and a `SELECT 1` query succeeds against it
2. the most recent migration in the `migrations` table matches the migration bundled in this
   build's artifact (catches a deploy that shipped code expecting a schema that wasn't migrated)
3. the Next.js server can render a lightweight internal route (`/api/internal/ping`) end-to-end,
   not just respond to a raw TCP connection

It returns `503` if any check fails, `200` only if all three pass. This is distinct from
`/health/live`, which only checks that the Node process is running and accepting connections:
`/health/live` returning `200` while the SQLite file is locked or missing is exactly the false
confidence this two-tier split is meant to prevent.

## Concrete Rollback Trigger

Automatic rollback fires when: **the `/health/ready` check fails on 3 consecutive polls
(15 seconds apart) within the first 2 minutes after `promote_prod` completes.** On trigger:
1. redeploy the last-known-good SHA-tagged artifact still present on the prod host
2. re-run `/health/ready` against the restored artifact
3. page on-call with the failing SHA, the last-known-good SHA, and the health check output

If the deploy included a destructive DB migration (column drop, type change), automatic rollback
is skipped (that case requires a forward fix per the additive-first migration rule), and on-call
is paged immediately instead of a silent auto-rollback attempt.
