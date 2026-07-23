---
id: GOV-012
title: Skill Creation Threshold (reuse >= 2)
applies_to: [all]
class_scope: all
enforced_by: [product-steward]
---

# GOV-012 — Skill Creation Threshold

## Intent
Skills are leverage, but premature abstraction is bloat. Create shared skills only
when reuse is real (requirement 11), keeping **minimal process overhead**.

## Rule
1. A **skill** is a reusable, documented procedure/tool shared across work. It is
   created **only** when it is (or will provably be) **used by ≥ 2 tickets OR ≥ 2
   agents**.
2. A capability used once stays **inline** in that ticket — it is not promoted to a
   skill "in case."
3. Skill promotion is approved by the **Product Steward** and must record the ≥ 2
   consumers that justify it.
4. Skills live under `skills/`, each with: purpose, inputs/outputs, the consumers
   that justify it, and an owner.
5. Unused or single-consumer skills are **retired** by the Auditor's recommendation.

## Current state
**No skills exist**, by design — no procedure yet has ≥ 2 consumers. The `skills/`
directory documents this policy only.

## Enforcement
The Steward gates skill creation against the ≥ 2-consumer test; the Auditor flags
skills that drop below it.

## Escalation
Skill created below threshold → Auditor flag → Steward retires or documents the
second consumer.
