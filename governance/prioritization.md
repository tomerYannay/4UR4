---
id: GOV-009
title: Verified-Progress-Over-Volume
applies_to: [orchestrator, all]
class_scope: all
enforced_by: [orchestrator, project-auditor]
---

# GOV-009 — Verified-Progress-Over-Volume

## Intent
Make the Orchestrator optimize the *right* thing: **verified, shipped value**, not
the number of tickets touched (requirement 18).

## Rule
1. The Orchestrator's primary metric is **verified progress** — tickets reaching
   evidence-backed **Done** ([GOV-006](definition-of-done.md)) — **not** task
   volume, tickets opened, or lines changed.
2. **Finish before start:** driving an in-flight ticket to Done takes priority
   over starting a new one, subject to the WIP limit ([GOV-008](ticket-hygiene.md)).
3. When prioritizing, order by **(business value × confidence) ÷ effort**, then by
   unblocking-power; ties break toward the smallest Done-able increment.
4. Activity that does not move a ticket toward verified Done is **overhead** and is
   minimized, not rewarded.
5. A cycle with many opened tickets but little verified Done is a **red flag** the
   Auditor reports and the Orchestrator must correct.

## Enforcement
The **Auditor** reports a *verified-throughput* figure (Done-with-evidence per
cycle) beside opened-ticket counts; a widening gap triggers correction.

## Escalation
Volume-over-progress pattern → Auditor flag → Orchestrator rebalances to finishing
work → persistent gap escalated to human.
