---
id: GOV-005
title: Definition of Done (with GOV-006 Evidence-Bound Done)
applies_to: [all]
class_scope: all
enforced_by: [verification, release-ops]
also_defines: [GOV-006]
---

# GOV-005 — Definition of Done (DoD)

## Intent
"Done" must mean the same thing every time, and it must be provable — the
foundation of **traceability** and **reproducibility**.

## Rule
A ticket is **Done** only when **all** hold:

- [ ] All acceptance criteria from the ticket are met.
- [ ] Code lives on a **ticket branch** in a **PR linked to the issue**.
- [ ] Declared **tests pass** and are reproducible from a clean checkout.
- [ ] A **Verification pass verdict** exists ([GOV-006](#gov-006--evidence-bound-done)).
- [ ] A **Code Review approval** exists (author ≠ reviewer, [GOV-011](separation-of-duties.md)).
- [ ] Merged by **Release & Ops** only; the board is moved to Done **by them**.
- [ ] Evidence links are recorded on the ticket.

Only the **Release & Ops Agent** may move a ticket to Done, and only after both
gates are green.

---

# GOV-006 — Evidence-Bound Done

## Intent
Prevent the single most common failure of autonomous agents: **declaring victory
without proof** (requirement 7).

## Rule
1. **No agent may mark, request, or treat a ticket as Done without repository
   evidence.** Assertions ("it works", "looks good") are **not** evidence.
2. Acceptable evidence is **repository-verifiable**: commit SHAs on the linked PR,
   captured test output / CI run links, produced artifacts, and the mapping from
   each acceptance criterion to one of these.
3. The **Verification Agent** (deterministic) is the sole issuer of the Done-
   eligible verdict, and must attach an **evidence log**.
4. A Done claim whose evidence cannot be reproduced is **automatically void** and
   reopened by the Auditor.

## Enforcement
Verification gate + Release & Ops refusal to merge without it; Auditor re-checks a
sample of Done tickets and voids any lacking reproducible evidence.

## Escalation
Done-without-evidence → ticket reopened → Auditor violation entry → Orchestrator
reprioritizes → human notified.
