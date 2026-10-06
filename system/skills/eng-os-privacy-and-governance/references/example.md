# Privacy and Data Governance: Worked Example

## Data dictionary entry (`docs/data/customers.md`)

```
Dataset:         customers (Postgres, cell-scoped)
Owner:           commerce-platform team
Classification:  Confidential
Purpose:         account identity and order fulfillment
Fields:
  customer_id    UUIDv7        Internal      surrogate key
  email          text          Confidential  login + order notifications; pseudonymized in warehouse as email_hash
  full_name      text          Confidential  shipping label
  phone          text          Confidential  delivery contact; field-level encrypted (Restricted in EU markets)
  created_at     timestamptz   Internal
Retention:       account lifetime + 30 days; legal hold overrides
Deletion:        procedure docs/runbooks/erase-customer.md (see below)
Lineage:         source of customers_dim (warehouse, daily, run_id stamped), recs_features (pseudonymized)
Third parties:   email provider (email, full_name; DPA on file); none to AI models
```

Wrong version, for contrast: the warehouse table `customers_dim` was created by an analyst
from a full copy of `customers`, including phone numbers, with no classification and a default
retention of forever. It was found during the first lineage query.

## Erasure procedure (`docs/runbooks/erase-customer.md`, excerpt)

| Step | Store | Action | Verify |
|---|---|---|---|
| 1 | Postgres primary | delete `customers` row and cascade-scoped children; write audit event `PRV000012` | row absent on primary and replica |
| 2 | Redis cache | delete `customer:{id}` and `session:*` for the id | key count 0 |
| 3 | Warehouse | delete from `customers_dim` by `customer_id`; `recs_features` keeps pseudonymous rows (no direct identifier) | query returns 0 rows |
| 4 | Search index | delete document | 404 on fetch |
| 5 | Email provider | API deletion request | provider confirmation id recorded |
| 6 | Backups | logged for purge at backup expiry (35 days); erasure record retained | purge job report |

Stated completion time: 24 hours for steps 1 to 5; 35 days for step 6. Exercised quarterly with
a synthetic account; last run 2026-08-05, all steps verified.

## Access review (quarterly)

| Role | Level | Granted | Expires | Purpose | Reviewed |
|---|---|---|---|---|---|
| support-agent | Confidential (read) | 2026-01-10 | 2026-10-10 | customer support | 2026-07-01 |
| data-analyst | Confidential via pseudonymized views only | 2026-03-02 | 2026-09-02 | product analytics | 2026-07-01 |
| order-api service account | Confidential (read/write, own cell) | n/a | n/a | fulfillment | 2026-07-01 |

The July review found a former on-call engineer with standing Restricted read from a 2025
investigation; revoked the same day.
