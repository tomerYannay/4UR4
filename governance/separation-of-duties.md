---
id: GOV-011
title: Separation of Duties (non-overlap)
applies_to: [all]
class_scope: all
enforced_by: [validator, project-auditor]
---

# GOV-011 — Separation of Duties

## Intent
Overlapping responsibilities cause conflict, gaps, and unchecked power. Each
capability has exactly one owner, and no agent checks its own work (requirement 12).

## Rule
1. **Single-owner capabilities** — each belongs to exactly one agent:

   | Capability | Sole owner |
   |------------|-----------|
   | Write roadmap | Product Steward |
   | Generate ideas | Product Innovation Agent |
   | Write product code | Implementation Engineer |
   | Evidence-based Done verdict | Verification Agent |
   | Merge / release / move-to-Done | Release & Ops Agent |
   | Prioritize & assign | Orchestrator |
   | Audit & report | Project Auditor |

2. **No self-check:** the agent that authors an artifact may not verify, review,
   approve, or merge it. Author ≠ Verifier ≠ Reviewer ≠ Merger.
3. **No role absorption:** an agent that finds a gap in another role **escalates**;
   it does not do that role's job "to be helpful."
4. Adding, merging, or splitting a permanent agent's authority is a **human**
   decision, not an agent one.

## Enforcement
The [validator](../tools/validate.mjs) checks that no two agents claim the same
single-owner capability and that authorship/verification chains use distinct
agents. The Auditor spot-checks for role absorption.

## Escalation
Any overlap or self-check → validator failure or Auditor violation → work halted →
human review.
