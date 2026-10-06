# Evidence

**Status:** Current
**Owner:** Haresh V. Parekh

`ledger.md` records why each evidence-based rule in the Engineering OS exists: the failure or
comparison that justified it, where it was observed, and when. It is the queryable form of the
rationale that `skills/MINDMAP.md` cites by row id.

Rules:
- add a row in the same change as any new rule, pattern, or gate
- cite rows by id from `MINDMAP.md` and from ADRs
- a rule whose evidence has not recurred in two releases is reviewed for retirement
- company-specific detail stays out; name a downstream app or project generically ("a downstream project"), never by its real name
