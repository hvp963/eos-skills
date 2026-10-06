# Platform Infrastructure: Worked Example

The same `order-api` from the reliability example, on a managed cloud, two cells in one region
with a warm standby region.

## Repository layout

```
infra/
  modules/
    cell/            one complete stack: compute, database, cache, queue, per-cell alerts
    control-plane/   routing, identity, config store, observability backend
    region/          composes N cells + one control plane
  envs/
    dev.tfvars       cells = 1, instance_size = small, db_size = small
    stage.tfvars     cells = 1, instance_size = medium, db_size = medium   (25% of prod capacity model)
    prod.tfvars      cells = 2, instance_size = large,  db_size = large, standby_region = "eu-west-2"
  README.md          lists every dev/stage/prod difference in one table
```

Every `.tfvars` file differs only in the variables above plus secret references. The pipeline
applies `infra/` with the same tag as the application release that needs it.

Wrong version, for contrast: prod had a manually created read replica and a hand-edited
security group that stage did not, so a release that depended on the replica passed stage and
failed in prod.

## Cell routing

Tenants map to cells by a stable hash recorded in the control plane's routing table. A new cell
is added by raising `cells` in `prod.tfvars`; tenant migration between cells is a documented
procedure, not an automatic rebalance.

## Backup and restore

| Store | RPO target | Backup | Off-domain copy | Last drill | Measured RTO |
|---|---|---|---|---|---|
| Postgres (per cell) | 15 min | continuous WAL + daily snapshot | replicated to standby region, immutable 35 days | 2026-07-22 | 41 min (target 60) |
| Object storage | 1 h | versioning on | cross-region replication | 2026-07-22 | 12 min |
| Redis cache | none (rebuildable) | none | none | n/a | n/a |

The July drill found that the restore runbook assumed a database user that no longer existed;
the runbook was fixed the same day and the drill re-run.

## Cost attribution

Tags: `service=order-api`, `cell=a|b`, `env=prod`. Reported monthly: cost per 1,000 requests
(target under 0.04 units). In June it rose 30% while requests rose 5%; the cause was a
per-request log line at debug level in prod, which Standard 1 forbids. Fixed, and the cost
metric is now on the reliability dashboard next to the SLOs.
