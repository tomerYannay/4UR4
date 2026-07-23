---
id: GOV-001
title: Agent Classification & Non-Determinism Governance
applies_to: [all]
class_scope: all
enforced_by: [validator, orchestrator]
---

# GOV-001 — Agent Classification & Non-Determinism Governance

## Intent
Novelty is powerful and dangerous. This rule makes every agent declare *how much*
creativity it is allowed, so non-determinism is contained and auditable.

## Rule
1. Every agent declares exactly one `class`: **deterministic**,
   **bounded-creative**, or **mixed**.
2. **Deterministic agents** must be reproducible: identical inputs must yield
   identical outputs. They may **not** introduce novelty. Facing an ambiguous
   decision, they **escalate**, never improvise. *(Verification, Release & Ops,
   Project Auditor.)*
3. **Bounded-creative agents** may generate novelty **only** into a designated
   sink (the Ideas Inbox) and **only** within declared constraints (value/effort/
   risk tags and budgets). They hold **no commit authority**. *(Product Innovation.)*
4. **Mixed agents** must, per action, act either as a deterministic gate (rule-
   bound) or as a bounded proposer (escalatable) — never blur the two.
   *(Orchestrator, Product Steward, Architect, Implementation Engineer, Code
   Reviewer.)*
5. Non-deterministic output that would change committed state (roadmap, code,
   Done) must pass through a deterministic gate or a human.

## Enforcement
The [validator](../tools/validate.mjs) checks that each agent has a valid class.
The Orchestrator refuses handoffs that would let a creative action bypass its gate.

## Escalation
Any detected class violation → Auditor logs it → Orchestrator halts the flow →
human decides.
