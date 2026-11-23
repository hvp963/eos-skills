---
name: eng-os-deployment-practices
description: "In a project governed by the Engineering OS, use when setting up CI/CD, environments, feature flags, or rollback/canary strategy."
sources: [meso/deployment.md]
globs: ["**/.github/workflows/**", "**/Dockerfile*", "**/docker-compose*", "**/.gitlab-ci.yml", "**/Jenkinsfile", "**/deploy/**"]
always_apply: false
verified_platforms: [claude-code]
---

# Deployment Practices

Apply these rules when designing or reviewing a deployment pipeline, environment setup, feature
flag, or rollback/canary strategy.

## Principles

- **Environments are explicit and isolated.** dev/stage/prod each have their own config, secrets, and infrastructure; nothing shared across boundaries.
- **Determinism within defined boundaries.** A build artifact is built once and promoted across environments unchanged.
- **Fail fast and loudly.** Every pipeline stage has a defined pass/fail gate; a failed stage stops promotion, no silent skips.
- **Rollback is a first-class operation.** The revert path is defined, tested, and executable without a code change.
- **Observability before promotion.** Each environment verifies readiness and a post-deploy smoke test, not just process liveness, before advancing.

## Core Patterns

### Environment Model
Three isolated environments (`dev`, `stage`, `prod`), each with its own config and secrets
namespace. Stage mirrors prod's configuration *structure*, not just values. No code path should
branch on `EXECUTION_MODE` for security decisions, and stage must never point at a prod database.
`EXECUTION_MODE` is set explicitly in every environment, test and CI included (an unset value fails
startup), and `.env` is never part of the build artifact.

### CI/CD Pipeline
One pipeline per repo, sequential stages, each with an explicit exit condition: `lint` → `test` →
`build` (immutable artifact tagged by git SHA) → `scan` (CVE + secret scan) → `migrate_stage` →
`deploy_stage` (health-gated) → `migrate_prod` → `promote_prod` (canary or blue-green,
health-gated). Migrations are their own gated stages, never a step inside a deploy. The artifact deployed to
stage is the *same* artifact promoted to prod, never rebuilt from source between environments.

### Feature Flags
Every flag has an explicit owner and expiry date. Flags are not a permanent branching mechanism;
clean them up after rollout, and removing a flag means removing the conditional code, not just
disabling it. Flag state changes are audit-logged.

### Rollback
Define the rollback path before deployment begins: identify last-known-good artifact, redeploy it,
verify health, alert on-call. Automatic triggers: error rate over threshold for 2+ minutes, failed
health check post-deploy, or manual on-call trigger. Irreversible DB migrations and external state
mutations (webhooks, emails) require a forward fix instead: design migrations additive-first.
Test the rollback path in stage on a schedule, not only during a real incident.

### Health Checks
Liveness (`/health/live`) only confirms the process is running. Readiness (`/health/ready`) reports
whether this instance can serve: configuration loaded and validated, its own connection pool
answering within a timeout, migrations at the version the artifact expects, warm-up done. It never
checks downstream services or non-critical dependencies: those sit behind breakers and degraded
paths (`eng-os-reliability-engineering`), and a readiness check on a shared dependency drains every
instance at once. Deployment gates use readiness, not liveness, plus a separate post-deploy smoke
test that exercises critical dependencies end to end. A check that always returns 200 gives false
confidence.

### Canary / Blue-Green
Shift traffic incrementally with success criteria agreed *before* the deployment starts (e.g.
error_rate and p99_latency thresholds at each stage), and roll back automatically on breach; never
rely on an engineer watching a dashboard in real time.

### Schema Migrations and Deploy Ordering
Schema change and dependent code never ship as one step. Expand (backward-compatible add, throttled idempotent backfill), deploy code that writes both shapes and reads the new one, contract (drop the old structure in a later release). Migrations run before the deploy that needs them as their own gated stage; each is reversible or marked forward-only with a documented compensating procedure; long-running migrations run online, never inside a deploy window that holds a lock. Schema-side rules: `eng-os-database-design`.
- Failure mode: a rename shipped with the code that reads it errors on every old instance during rollout and cannot roll back.

### Secret Rotation
Every secret has an owner, a rotation interval, and a procedure that needs no deploy: the manager holds two live versions, so rotation is add-new, cut over, retire-old. Exercised on schedule in stage; any secret seen in a log, ticket, or chat is rotated immediately.
- Failure mode: a leaked credential stays valid for days because rotating it needs a coordinated multi-service deploy.

## Failure Modes

- shared secrets across environments let a stage mistake become a prod credential leak
- rebuilding the artifact between environments introduces configuration/dependency drift
- feature flags without expiry or ownership accumulate as invisible conditional dead code
- rollback procedures that have never been tested fail under incident pressure
- liveness-only health checks pass deployments that cannot reach required dependencies
- a readiness check that tests a shared downstream service drains every instance when that service blips, turning a partial failure into a full outage
- canary promotion without automatic rollback criteria requires human vigilance on every deploy
- schema change and dependent code shipped as one step: errors on old instances mid-rollout, no rollback path
- secrets that cannot rotate without a deploy stay valid long after they leak

## Definition of Done

### Per change

- [ ] Every feature flag has an owner and an expiry date
- [ ] Readiness checks only this instance's own state (config, pool, migration version); a post-deploy smoke test covers critical dependencies
- [ ] Schema changes follow expand/contract, run as their own gated stage before the dependent deploy, and are reversible or documented forward-only

### Standing (release and audit)

- [ ] dev / stage / prod environments are fully isolated with no shared secrets
- [ ] The CI/CD pipeline has explicit pass/fail gates for lint, test, build, scan, migrate, and deploy
- [ ] The same build artifact is promoted from stage to prod without rebuild
- [ ] The rollback path is defined, documented, and has been tested in stage
- [ ] Canary or blue-green strategy has explicit success criteria and automatic rollback on threshold breach
- [ ] Every secret has an owner, a rotation interval, and a rotation procedure that needs no deploy

For a worked example, see `references/example.md`.
