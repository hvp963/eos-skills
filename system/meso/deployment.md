# Deployment

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A guide for designing and operating a deployment system that is reproducible, observable, and safe to roll back.

### What This Is Not
- not a specific CI/CD tool tutorial (GitHub Actions, CircleCI, etc.)
- not a container orchestration guide
- not a cloud provider reference

## Scope
- Level: Meso
- Applies To: All services, pipelines, and AI workloads deployed to any environment
- See Also: `meso/observability.md`; signals required to verify deployment health

---

## Applied Principles

### Environments Are Explicit and Isolated
Each environment (dev / stage / prod) has its own configuration, secrets, and infrastructure. Nothing is shared across environment boundaries.

### Determinism Within Defined Boundaries
A build artifact is built once and promoted across environments. The artifact does not change between stage and prod.

### Fail Fast and Loudly
Every pipeline stage has a defined pass/fail gate. A failed stage stops promotion immediately; no silent skips.

### Rollback is a First-Class Operation
The ability to revert a deployment must be defined, tested, and executable without a code change.

### Observability Before Promotion
Each environment must verify real health (not just process liveness) before advancing.

---

## Core Patterns

### 1. Environment Model

Three environments (`dev`, `stage`, `prod`), each fully isolated.

```
environments:
    dev:
        purpose: local development and rapid iteration
        config:  .env (never committed)
        secrets: developer-local or dev-only secrets manager namespace
        scale:   minimal

    stage:
        purpose: pre-production verification; mirrors prod config structure
        config:  environment variables via CI secrets / secrets manager
        secrets: stage namespace — no overlap with prod
        scale:   representative (not necessarily full prod size)

    prod:
        purpose: live traffic
        config:  environment variables via secrets manager
        secrets: prod namespace — restricted access; audit-logged
        scale:   full
```

Rules:
- no shared secrets between environments
- no code path that reads `EXECUTION_MODE` and branches on it for security decisions
- stage must mirror prod's configuration structure, not only its values
- database connections in stage must never point to prod

#### Failure Mode
Using the same database connection string across environments turns a stage data migration into a prod incident.

---

### 2. CI/CD Pipeline

One pipeline per repository. Stages are sequential. Each stage has a defined exit condition.

```
pipeline:
    on: [push to main, pull request]

    stages:
        lint:
            run: lint_check()
            pass: zero warnings or errors
            fail: stop; block merge

        test:
            run: unit_tests() + integration_tests()
            pass: all tests green; coverage >= threshold
            fail: stop; block merge

        build:
            run: build_artifact(tag=git_sha)
            output: immutable artifact (container image, binary, package)
            fail: stop

        scan:
            run: cve_scan(artifact) + secret_scan(source)
            pass: no critical CVEs; no secrets detected in source
            fail: stop; notify security channel

        deploy_stage:
            run: deploy(artifact, env=stage)
            health_check: wait_for_healthy(env=stage, timeout=5m)
            pass: health check passes
            fail: rollback stage; stop

        promote_prod:
            run: deploy(artifact, env=prod)
            strategy: canary or blue-green (see patterns below)
            health_check: wait_for_healthy(env=prod, timeout=10m)
            fail: rollback prod; alert on-call
```

The artifact deployed to stage is the same artifact deployed to prod: built once, promoted by reference.

#### Failure Mode
Rebuilding from source between stage and prod allows environmental differences to introduce bugs that were never tested.

---

### 3. Feature Flags

Named runtime flags that decouple deployment from feature activation.

```
flag:
    name: "new_checkout_flow"
    owner: "payments-team"
    expires: "2027-03-01"
    rollout: 10%          // percentage of traffic; or: user_ids, regions, etc.

// usage in code
if featureFlag("new_checkout_flow").enabled(user=currentUser):
    runNewCheckoutFlow()
else:
    runLegacyCheckoutFlow()
```

Requirements:
- every flag has an explicit owner and expiry date
- flags are not a permanent branching mechanism; they must be cleaned up after rollout
- flag state changes are logged as audit events
- removing a flag requires removing the conditional code, not just disabling the flag

#### Failure Mode
Feature flags without expiry dates accumulate indefinitely, creating invisible conditional logic and dead code paths that nobody remembers.

---

### 4. Rollback

The rollback path must be defined before deployment begins and executable without a code change.

```
// artifact promotion — rollback = re-deploy previous artifact
rollback_procedure:
    identify:  last_known_good_artifact = artifact_store.get_previous_stable(service)
    execute:   deploy(last_known_good_artifact, env=target_env)
    verify:    wait_for_healthy(env=target_env, timeout=5m)
    alert:     notify_on_call("rollback completed", service=service, artifact=last_known_good_artifact)

// triggers — rollback initiates automatically when:
triggers:
    - error_rate exceeds threshold for 2 consecutive minutes
    - health check fails after deploy
    - on-call engineer initiates manual rollback

// exclusions — the following require a forward fix, not rollback:
exclusions:
    - irreversible database migrations (must be designed as additive first)
    - external state mutations (webhooks sent, emails delivered)
```

Test rollback in stage on a defined schedule, not just when a real incident forces it.

#### Failure Mode
A rollback procedure that has never been tested will fail under the pressure of a real production incident.

---

### 5. Health Checks

Health checks must verify that the service can do its actual work, not just that the process is alive.

```
// liveness — is the process running?
GET /health/live
response: 200 { "status": "alive" }

// readiness — can the service handle traffic?
GET /health/ready
    check: database connection pool responds within timeout
    check: required downstream services reachable
    check: configuration loaded and validated
    response (passing): 200 { "status": "ready", "checks": { "db": "ok", "cache": "ok" } }
    response (failing): 503 { "status": "not_ready", "checks": { "db": "timeout" } }
```

Deployment gates use `/ready`, not `/live`: a liveness-only gate will pass a service that is alive but cannot reach its database.

#### Failure Mode
A health check that always returns 200 provides false confidence and allows unhealthy deployments to pass promotion gates silently.

---

### 6. Canary / Blue-Green Deployment

Shift traffic incrementally. Define success criteria before shifting. Roll back automatically on threshold breach.

```
// canary — shift traffic in stages
canary_deployment:
    artifact: new_version
    stages:
        - shift:    5%
          wait:     5 minutes
          criteria: error_rate < 0.5% AND p99_latency < 300ms
        - shift:    25%
          wait:     10 minutes
          criteria: error_rate < 0.5% AND p99_latency < 300ms
        - shift:    100%
          criteria: error_rate < 0.5% AND p99_latency < 300ms

    on_criteria_breach:
        action: rollback to previous version
        notify: on-call engineer

// blue-green — run two full environments; switch routing
blue_green:
    blue:  current stable version (live)
    green: new version (deployed; not yet live)
    switch:
        pre_condition: green health check passes
        action: route 100% of traffic to green
        fallback: re-route to blue if green health degrades within 10 minutes
```

Success criteria must be agreed before deployment begins, not evaluated after the fact.

#### Failure Mode
Canary deployments without automatic rollback on error thresholds require an engineer to be watching dashboards in real time, which is an unreliable gate.

---

### 7. Schema Migrations and Deploy Ordering

A schema change and the code that depends on it never ship as one step. Use expand/contract:

1. **Expand**: add the new column, table, or index in a backward-compatible migration. Old code
   keeps running. Backfill in batches, throttled, idempotent.
2. **Deploy** code that writes both old and new shapes and reads the new one.
3. **Contract**: after every instance runs the new code and the backfill is verified, remove the
   old column or table in a separate migration.

Migrations run before the deploy that needs them, as their own pipeline stage with their own
health gate, and every migration is either reversible or explicitly marked forward-only with
the compensating procedure documented. Long-running migrations (large-table index builds,
backfills) run online, never inside a deploy window that holds a lock.

- Failure mode: a single deploy that renames a column and ships the code reading it produces
  errors on every old instance still running during the rollout, and cannot roll back because
  the old code no longer matches the schema.

### 8. Secret Rotation

Every secret has an owner, a rotation interval, and a rotation procedure that does not require
a deploy: services read secrets from a manager that supports two live versions, so rotation is
add-new, cut over, retire-old. Rotation is exercised on schedule in stage, and any secret that
has ever appeared in a log, a ticket, or a chat is rotated immediately.

- Failure mode: a leaked credential cannot be rotated without a coordinated multi-service
  deploy, so it stays valid for days after the leak is known.

## Failure Modes

- shared secrets across environments allow a stage mistake to become a prod credential leak
- rebuilding the artifact between environments introduces configuration and dependency drift
- feature flags without expiry or ownership accumulate as invisible conditional dead code
- rollback procedures that have never been tested will fail under incident pressure
- liveness-only health checks pass deployments that cannot reach required dependencies
- canary promotion without automatic rollback criteria requires human vigilance on every deploy
- schema change and dependent code shipped as one step: errors on old instances during rollout, and no rollback path
- secrets that cannot be rotated without a deploy stay valid long after they leak

---

## Definition of Done

Deployment design is complete when:
- dev / stage / prod environments are fully isolated with no shared secrets
- the CI/CD pipeline has explicit pass/fail gates for lint, test, build, scan, and deploy
- the same build artifact is promoted from stage to prod without rebuild
- every feature flag has an owner and an expiry date
- the rollback path is defined, documented, and has been tested in stage
- health checks verify real dependencies, not just process liveness
- canary or blue-green strategy has explicit success criteria and automatic rollback on threshold breach
- schema changes follow expand/contract, run as their own gated pipeline stage before the dependent deploy, and are reversible or documented forward-only
- every secret has an owner, a rotation interval, and a rotation procedure that does not require a deploy
