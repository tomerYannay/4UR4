---
id: GOV-010
title: Handoff Protocol
applies_to: [all]
class_scope: all
enforced_by: [orchestrator]
---

# GOV-010 — Handoff Protocol

## Intent
Clean handoffs preserve **traceability** and prevent work from silently changing
owner, scope, or state (requirement 4).

## Rule
1. Every handoff is **explicit** and recorded on the ticket: *from agent → to
   agent*, with the artifact passed and its state.
2. An agent may hand off **only** to a target listed in its `handoff_to`, and
   accept **only** from a source in its `handoff_from`. The validator checks these
   references resolve to real agents.
3. **Required artifacts per handoff** (nothing advances without them):

   | From → To | Required artifact |
   |-----------|-------------------|
   | Innovation → Steward | Idea card (Inbox) |
   | Steward → Orchestrator | Ready ticket + DoR checklist |
   | Orchestrator → Architect | Assigned Ready ticket |
   | Architect → Engineer | Technical plan + evidence plan |
   | Engineer → Verification | Linked PR + tests + evidence |
   | Verification → Reviewer | Pass verdict + evidence log |
   | Reviewer → Release & Ops | Review approval |
   | Release & Ops → Auditor | Merge + Done record |

4. A handoff missing its required artifact is **rejected** back to the sender; the
   receiver never "fills the gap" for another role ([GOV-011](separation-of-duties.md)).
5. The **Orchestrator** owns the handoff ledger and resolves stalls, loops, and
   ping-pong.

## Enforcement
Validator checks `handoff_to`/`handoff_from` integrity; Orchestrator enforces the
artifact table at runtime.

## Escalation
Malformed or artifact-less handoff → Orchestrator returns it → repeated failures
escalate to human.
