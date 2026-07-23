# Workflow — Pull Requests

Every code change reaches the default branch through **one PR linked to one
Issue**. The PR is where evidence, verification, and review converge.

## Lifecycle

```
Engineer opens PR (draft) ─▶ tests pass ─▶ mark ready
   ─▶ Verification: evidence gate (pass/fail + evidence log)
   ─▶ Code Review: judgement (approve / request-changes)
   ─▶ Release & Ops: merge (both gates green) ─▶ Done
```

## Requirements to merge (all mandatory)

- [ ] PR **linked to its Issue** (`Closes #<n>`).
- [ ] On a **ticket branch**, scoped to that ticket only.
- [ ] **Tests pass**, reproducible from a clean checkout.
- [ ] **Verification pass verdict** + evidence log ([GOV-006](../governance/definition-of-done.md)).
- [ ] **Code Review approval**, author ≠ reviewer ([GOV-011](../governance/separation-of-duties.md)).
- [ ] **Human approval** of the merge ([GOV-013](../governance/approval-gate.md)).
- [ ] Change stays in scope ([GOV-007](../governance/product-focus.md)).

Use [`templates/pull-request.md`](../templates/pull-request.md).

## Rules

- The **author never merges their own PR**, and **only Release & Ops merges**.
- Failing checks are **never overridden**; the PR returns to the Engineer.
- A merged PR without reproducible evidence is **voided and reverted** by Auditor
  recommendation.
- **Under the [build-freeze](../governance/build-freeze.md), no product-code PR may
  be opened or merged** — only operating-system / context PRs (like this one).
