---
id: GOV-004
title: Definition of Ready
applies_to: [all]
class_scope: all
enforced_by: [product-steward]
---

# GOV-004 — Definition of Ready (DoR)

## Intent
Work should not start until it is unambiguous and bounded. A ticket that is not
Ready wastes downstream agents and invites scope drift.

## Rule
A ticket is **Ready** only when **all** hold:

- [ ] **Traces to an approved roadmap item** ([GOV-002](roadmap-authority.md)).
- [ ] States a clear **user/business value** and a **success measure**.
- [ ] Has **explicit, testable acceptance criteria**.
- [ ] Is **bounded** — small enough to complete and verify in one flow; oversized
      tickets are split by the Steward, not silently expanded.
- [ ] Uses defined [glossary](../product/glossary.md) terms; any new term is added.
- [ ] Names required **evidence** for Done ([GOV-006](definition-of-done.md)).
- [ ] Carries no unaddressed dependency or open scope question.
- [ ] Respects the [build-freeze](build-freeze.md) — implementation tickets stay
      `Blocked: freeze` until a human lifts it.

## Enforcement
The **Product Steward** owns the DoR and attaches the checklist to each ticket.
The **Orchestrator** refuses to assign a ticket that is not Ready.

## Escalation
Not-Ready work pulled into progress → Orchestrator returns it → Auditor notes the
process breach.
