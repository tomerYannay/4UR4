---
id: GOV-002
title: Single Roadmap Authority (with GOV-003 Innovation Governance)
applies_to: [product-steward, product-innovation, all]
class_scope: non-deterministic
enforced_by: [product-steward, human, project-auditor]
also_defines: [GOV-003]
---

# GOV-002 — Single Roadmap Authority

## Intent
A product dies of a thousand good ideas. Exactly one authority, gated by a human,
protects **focus** and **business value**.

## Rule
1. The [`product/roadmap.md`](../product/roadmap.md) is the **only** commitment
   surface. Ideas, briefs, and experiments are **not** commitments.
2. **Only the Product Steward may write the roadmap**, and only with explicit
   **human approval** ([GOV-013](approval-gate.md)).
3. Any other agent editing the roadmap is a violation the Auditor must flag and
   the Orchestrator must halt.

## Enforcement
Steward is the sole holder of `roadmap_write`; the Auditor diffs roadmap history
against approvals.

---

# GOV-003 — Innovation Governance (propose, never commit)

## Intent
Preserve **controlled creativity**: let a dedicated agent think big without
letting it steer the product unilaterally (requirement 17).

## Rule
1. The **Product Innovation Agent may propose** ideas and experiments **only into
   the [Ideas Inbox](../ideas/inbox.md)**.
2. It **may not** add anything to the roadmap, create tickets, or trigger builds.
3. An idea reaches the roadmap **only** via **human + Product Steward** triage,
   after passing the [Product-Focus Guard](product-focus.md) and stating value +
   a success measure.
4. No idea may cite "the Innovation Agent proposed it" as sufficient justification.

## Enforcement
Innovation holds only `ideas_write_inbox`. Promotion events require a human
sign-off recorded in the roadmap change log.

## Escalation
Unapproved roadmap change → Auditor violation entry → revert → human review.
