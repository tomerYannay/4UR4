---
id: GOV-008
title: Ticket Hygiene & Anti-Bloat
applies_to: [all]
class_scope: all
enforced_by: [orchestrator, project-auditor]
---

# GOV-008 — Ticket Hygiene & Anti-Bloat

## Intent
Autonomous agents tend to manufacture work. This rule rations tickets and ideas so
the system optimizes **throughput of value**, not paperwork (requirement 16).

## Rule
1. **WIP limit:** at most **3** tickets `In Progress` across the whole system at
   once. New work waits; the Orchestrator does not start a fourth.
2. **Ticket budget:** at most **5 open, unstarted** Ready tickets. Beyond that, no
   new tickets are created until the backlog drains — this caps excessive ticket
   creation.
3. **Idea budget:** the Product Innovation Agent may submit at most **3 new idea
   cards per cycle**; excess is deferred, not lost.
4. **One ticket = one verifiable outcome.** No umbrella/epic tickets used as
   perpetual open scope; split into bounded, Done-able units.
5. **No duplicate or near-duplicate tickets.** The Orchestrator dedupes before
   assignment; the Auditor flags duplicates.
6. **Stale tickets** (no evidence movement in a cycle) are surfaced by the Auditor
   for close/split, not left to accumulate.
7. **Meta-work cap:** process/tooling tickets may not exceed product tickets in an
   active cycle.

## Enforcement
The **Orchestrator** enforces WIP, ticket, and idea budgets at assignment time;
the **Auditor** reports counts, duplicates, and staleness each cycle.

## Escalation
Any budget breach → Orchestrator blocks new creation and escalates to human with
the Auditor's counts.
