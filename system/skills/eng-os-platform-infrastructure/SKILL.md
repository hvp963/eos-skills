---
name: eng-os-platform-infrastructure
description: "Use when creating or changing an infrastructure resource, defining environments, laying out regions or cells, or setting up backup, restore, or disaster recovery. Owns what the deployment pipeline deploys onto; `eng-os-deployment-practices` owns the pipeline itself."
sources:
  - meso/infrastructure.md
globs: ["**/*.tf", "**/*.tfvars", "**/pulumi*/**", "**/cdk*/**", "**/infra/**", "**/infrastructure/**", "**/k8s/**", "**/helm/**"]
always_apply: false
verified_platforms: [claude-code]
---

# Platform Infrastructure

Apply these rules to anything that provisions or configures the substrate a system runs on.
Patterns are provider-neutral.

## Principles

- **Determinism within defined boundaries.** An environment is the output of applying versioned code; two applications produce the same environment.
- **Explicitness over implicitness.** Nothing exists in production that is not declared in the infrastructure repository.
- **Fault isolation over global stability.** Regions and cells are the physical form of blast-radius limits.

## Infrastructure as Code

Every resource (compute, network, storage, queues, DNS, identity policies, alert rules) is
declared in code, reviewed like application code, applied by a pipeline, never by a console. The
infrastructure repository is tagged alongside the application releases it supports. A manual
change made during an incident is captured in code before the incident closes, or reverted.
- Failure mode: "stage mirrors prod" is a sentence until both are the same code with different variables.

## Environment Parity

`dev`, `stage`, and `prod` are one code base with a variables file each. Differences are limited
to scale, secrets, and external endpoints, listed in one place. Stage runs at a declared fraction
of prod's capacity model so load tests extrapolate.
- Failure mode: a stage that differs in topology validates nothing about the release.

## Regions and Cells

Realize the blast-radius architecture chosen in `eng-os-system-design`: each region a full independent
application of the code; each cell a full stack with its own data store behind a routing layer
mapping tenants or users to cells; the control plane (routing, identity, configuration,
observability backend) deployed with higher redundancy than any cell and sharing no failure
domain with one. Capacity grows by adding cells.
- Failure mode: a "multi-region" system whose identity provider lives in one region is single-region with extra steps.

## Backup, Restore, Disaster Recovery

Every stateful store has a backup schedule sized to the RPO in the Scale Targets, an immutable
copy in a different failure domain, a restore procedure, and a scheduled restore drill
(quarterly minimum) measured against the RTO.
- Failure mode: the first restore is attempted during the incident and takes six times the RTO.

## Cost as a Design Signal

Every environment carries cost attribution tags; cost per Scale Target unit (per thousand
requests, per tenant, per gigabyte) is a reported metric. Cost growing faster than its driving
unit is a scaling defect to investigate.
- Failure mode: spend doubles while traffic grows by half, discovered a quarter late.

See `references/example.md` for a minimal infrastructure repository layout, a variables split,
and a restore-drill record.

## Failure Modes

- resources created by hand that exist nowhere in code
- stage and prod that differ in topology
- a shared control-plane dependency that makes every region fail together
- backups never restored, or restorable only into the same failure domain
- no cost attribution

## Definition of Done

- [ ] Every production resource is declared in a versioned infrastructure repository applied by pipeline
- [ ] Environments are one code base with a variables file each, and every difference is listed
- [ ] Region and cell layout matches the system design; the control plane shares no failure domain with a cell
- [ ] Every stateful store has a backup meeting the RPO, an immutable off-domain copy, and a scheduled restore drill measured against the RTO
- [ ] Cost is attributed by tag and reported per Scale Target unit
