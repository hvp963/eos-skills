# Worked Example — Naming, Terminology Lock, and Deprecation Timeline

Source: illustrates `../SKILL.md` Naming Conventions and Terminology Lock sections with concrete,
realistic names.

## Naming — RIGHT vs. WRONG

| Construct | RIGHT | WRONG | Why wrong |
|---|---|---|---|
| Variable (Python) | `retry_delay_secs` | `t` | generic single-letter, no unit, requires a comment |
| Function | `load_checkpoint(path)` | `doStuff(path)` | vague verb, mixed camelCase in a snake_case file |
| Constant | `RETRY_BASE_MS = 100` | `max = 100` | not upper-snake, name shadows builtin, no unit or domain context |
| Class | `CheckpointManager` | `checkpoint_manager_class` | wrong casing for a class, redundant `_class` suffix |
| File (Python) | `checkpoint_manager.py` | `CheckpointManager.py` | PascalCase file name in a snake_case-file project |
| File (TS) | `checkpoint-manager.ts` | `checkpointManager.ts` | camelCase file name in a kebab-case-file project |
| Env var | `IMAGE_API_KEY` | `API_KEY` | collides the moment a second external API is added |
| Boolean | `is_valid`, `has_checkpoint` | `valid`, `checkpoint_flag` | no `is_`/`has_` prefix — ambiguous at call sites |

```python
# WRONG — generic name, mixed casing, no boolean prefix
def doStuff(data):
    flag = data.get("valid")
    temp = data["value"] * 2
    return temp

# RIGHT — self-describing, consistent casing, prefixed boolean
def double_validated_amount(order_payload):
    is_valid = order_payload.get("is_valid")
    if not is_valid:
        raise InvalidOrderError(order_payload["order_id"])
    validated_amount = order_payload["amount"] * 2
    return validated_amount
```

## Terminology Lock — Worked Example

Hypothetical domain concept: the record representing a customer's request to cancel a
subscription mid-cycle.

| Decided term | Rejected alternatives | Locked at |
|---|---|---|
| `cancellation_request` | `termination`, `unsubscribe_event`, `churn_record` | Phase 4 (Terminology Lock), design review 2026-04-02 |
| `effective_date` (date the cancellation takes effect) | `end_date`, `cancel_date` | same |
| "Cancel Subscription" (UI button/section title) | "End Plan", "Stop Billing" | same |

Once locked, `cancellation_request` is the only term used in code identifiers, DB columns, API
fields, UI copy, and docs. `termination` and `churn_record` do not appear anywhere in the
implementation, even as aliases.

## Versioned-Deprecation Rename of a Public API Field: Mini Timeline

Renaming `cancellation_request` to `subscription_cancellation` after a later design review
determined the original term was ambiguous with hard account termination. Partner systems read
the field from the public API, so the alias window applies to the API field only; inside the
system the rename is one complete change:

```
2026-05-01  ADR-014 approved: rename cancellation_request -> subscription_cancellation.
            Reason: term collided with unrelated "account termination" flow, causing
            confusion in support tooling. New name declared final.

2026-05-03  One complete change inside the system: classes, routes, columns, UI text,
            docs, and tests use subscription_cancellation only. At the API boundary,
            responses carry both fields; cancellation_request is a deprecated alias with
            Deprecation and Sunset headers naming 2026-06-15.

2026-05-03..2026-06-15   Transition window, for API consumers only:
              - partners move to subscription_cancellation
              - nothing inside the system uses the old name

2026-06-15  The API alias is removed. Grep for the old term returns zero results outside
            of the ADR and changelog history.
```

This is the allowed pattern: one complete rename inside the system, plus an alias window only
on the public contract, with a declared end date. An internal-only term gets no alias window at
all. Unplanned drift, where two terms coexist indefinitely with no one able to say which is
current, is what the rule prevents.
