---
id: GOV-013
title: Human Approval Gate
applies_to: [all]
class_scope: all
enforced_by: [human]
---

# GOV-013 — Human Approval Gate

## Intent
Keep a human in control of the irreversible and the strategic (requirement 14).
Agents may prepare anything; humans authorize the commitments.

## Rule
A **human** must approve, in writing (PR review, roadmap change-log sign-off, or
issue approval), before any of the following:

1. **Enabling autonomous implementation** / lifting the [build-freeze](build-freeze.md).
2. **Adding or reordering roadmap items** ([GOV-002](roadmap-authority.md)).
3. **Promoting an idea** from Inbox to roadmap ([GOV-003](roadmap-authority.md)).
4. **Merging to the default branch** and any release/deploy.
5. **Adding, removing, or re-scoping a permanent agent**, or changing a governance
   rule.
6. **Starting the Fear & Greed / sentiment feature** ([GOV-014](market-sentiment-context.md)).

Agents facing any of the above **stop and request approval**; they never assume it.

## Enforcement
These actions are structurally impossible without a recorded human artifact; the
Auditor verifies each committed action carries its approval.

## Escalation
Action taken without the required approval → Auditor violation → revert →
human review of how the gate was bypassed.
