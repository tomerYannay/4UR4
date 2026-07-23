---
id: GOV-007
title: Product-Focus Guard (anti scope-drift)
applies_to: [all]
class_scope: all
enforced_by: [product-steward, project-auditor]
---

# GOV-007 — Product-Focus Guard

## Intent
Protect **focus** and **business value** by keeping every unit of work tied to the
approved product thesis and refusing quiet scope expansion (requirement 16).

## Rule
1. Every ticket must trace to an approved roadmap item that advances the 4UR4
   thesis: **ATH-anchored log descending trendlines → confirmed breakout & retest
   → explainable confidence, modulated by sentiment context.**
2. Work that does not serve a user/business value on the roadmap is **out of
   scope** and must be routed to the [Ideas Inbox](../ideas/inbox.md), not built.
3. Agents may **not** widen a ticket mid-flight. New scope discovered during work
   becomes a **new idea** for triage, never an in-place expansion.
4. "Nice to have," "while we're here," and gold-plating are explicit anti-patterns.
5. **Explainability** and **correctness** outrank feature breadth: deepening a
   committed capability beats adding a shallow new one.

## Enforcement
The **Product Steward** screens tickets at DoR; the **Auditor** computes a
scope-drift signal (tickets/PRs touching areas with no roadmap trace) each cycle.

## Escalation
Drift detected → Auditor alert → Steward reclassifies as idea or splits →
Orchestrator halts out-of-scope work.
