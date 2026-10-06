# Platform Infrastructure

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
The design guide for what a system runs on: how environments are defined and kept identical,
how regions and cells are laid out, how state is backed up and restored, and how all of that is
expressed as versioned code rather than configured by hand.

### What This Is Not
- not the deployment pipeline (see `meso/deployment.md`; this guide owns what the pipeline deploys onto)
- not a cloud-provider tutorial; patterns here are provider-neutral
- not the reliability guide (that covers runtime behavior; this covers the substrate)

## Scope
- Level: Meso
- Applies To: every system with more than one environment or more than one instance
- See Also: `meso/deployment.md`, `meso/reliability.md`, `meso/system-design.md`, `meso/security.md`

---

## Applied Principles

### Determinism Within Defined Boundaries
An environment is the output of applying versioned code to a provider; two applications of the
same code produce the same environment.

### Explicitness Over Implicitness
Nothing exists in production that is not declared in the infrastructure repository.

### Fault Isolation Over Global Stability
Regions and cells are the physical form of blast-radius limits.

---

## 1. Infrastructure as Code

Every resource (compute, network, storage, queues, DNS, identity policies, alert rules) is
declared in code, reviewed like application code, and applied by a pipeline, never by a console.
The infrastructure repository is versioned and tagged alongside the application releases it
supports. A manual change made during an incident is captured in code before the incident is
closed, or reverted.

- Failure mode: "stage mirrors prod" is a sentence until both are the same code with different
  variables; every hand-made console change is drift that surfaces as "works in stage."

## 2. Environment Parity

`dev`, `stage`, and `prod` are the same infrastructure code with a variables file each.
Differences are limited to scale (instance counts, sizes), secrets, and external endpoints, and
every difference is listed in one place. Stage runs at a declared fraction of prod's capacity
model so load tests (`meso/testing-strategy.md` Layer 6) extrapolate.

- Failure mode: a stage that differs from prod in topology, not just size, validates nothing
  about how the release will behave.

## 3. Regions and Cells

The blast-radius architecture chosen in `meso/system-design.md` (single region, active-passive,
active-active, cell-based) is realized here:

- each region is a full, independent application of the infrastructure code
- each cell is a full stack with its own data store, addressed through a routing layer that
  maps tenants or users to cells
- the control plane (routing, identity, configuration, observability backend) is deployed with
  higher redundancy than any cell and never shares a failure domain with one
- capacity is provisioned per cell from the capacity model; adding capacity means adding cells

- Failure mode: a "multi-region" system whose identity provider, configuration store, or
  metrics backend lives in one region is single-region with extra steps.

## 4. Backup, Restore, and Disaster Recovery

Every stateful store has a backup schedule sized to the RPO in the Scale Targets, a restore
procedure, and a restore drill on a schedule (quarterly at minimum) that measures the actual
time to recover against the RTO. Backups live in a different failure domain (region, account)
from the data they protect and are immutable for their retention period. A backup that has never
been restored is a hope.

- Failure mode: the restore is attempted for the first time during the incident, takes six times
  longer than the RTO, and the backup turns out to be missing one schema.

## 5. Cost as a Design Signal

Every environment carries cost attribution tags (service, team, tenant cohort where relevant),
and monthly cost per unit of the Scale Targets (per thousand requests, per tenant, per gigabyte)
is a reported metric. A cost that grows faster than the driving unit is a scaling defect to
investigate, not a budget line to approve.

- Failure mode: infrastructure spend that doubles while traffic grows by half, discovered a
  quarter late.

---

## Failure Modes

- resources created by hand that exist nowhere in code
- stage and prod that differ in topology, so stage validates nothing
- a shared control-plane dependency that makes every region fail together
- backups never restored, or restorable only into the same failure domain
- no cost attribution, so scaling defects surface as finance questions

## Definition of Done

Infrastructure is complete when:
- every production resource is declared in a versioned infrastructure repository applied by pipeline
- environments are one code base with a variables file each, and every difference is listed
- the region and cell layout matches the system design, and the control plane has no shared failure domain with a cell
- every stateful store has a backup meeting the RPO, an immutable off-domain copy, and a scheduled restore drill measured against the RTO
- cost is attributed by tag and reported per Scale Target unit
