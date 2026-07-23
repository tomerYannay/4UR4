---
id: GOV-014
title: Market-Sentiment Research Boundary
applies_to: [product-innovation, product-steward, all]
class_scope: all
enforced_by: [product-steward]
---

# GOV-014 — Market-Sentiment Research Boundary

## Intent
Fear & Greed and the proprietary market-regime score are core to 4UR4's
**explainable confidence** thesis — but they are **research context now, not a
feature to build yet** (requirement 19). This rule keeps the thinking alive
without prematurely committing engineering.

## Rule
1. Agents **may research** market sentiment — Fear & Greed, market-regime signals,
   how sentiment should modulate confidence — and record findings as **context**:
   [research briefs](../workflows/experimentation.md), glossary entries, idea cards.
2. Agents **may not implement** any sentiment feature: no data pipeline, scorer,
   API integration, model, or UI for F&G or regime, until a human approves it via
   [GOV-013](approval-gate.md) and it becomes a Ready ticket on the roadmap.
3. Research outputs are **clearly labeled "context only"** and live in
   [`ideas/`](../ideas/inbox.md) or `product/`, never as executable product code.
4. Sentiment context must connect back to the product thesis (how it makes a
   confidence score more **explainable** or **correct**), not become an open-ended
   research rabbit hole ([GOV-007](product-focus.md), [GOV-008](ticket-hygiene.md)).

## Enforcement
The Product Steward ensures sentiment work stays in context artifacts; the Auditor
flags any executable sentiment code appearing before approval + build-freeze lift.

## Escalation
Sentiment feature code found pre-approval → Auditor violation → revert →
human review.
