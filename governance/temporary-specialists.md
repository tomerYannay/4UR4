---
id: GOV-016
title: Temporary Ticket-Scoped Specialist Subagents
applies_to: [all]
class_scope: all
enforced_by: [orchestrator, architect, validator, project-auditor]
---

# GOV-016 — Temporary Ticket-Scoped Specialists

## Intent
The nine permanent agents must stay minimal (GOV-011), but one generic
Implementation Engineer cannot be the sole expertise for quant, market-data, ML,
backend, frontend, security, and DevOps work. This rule allows **temporary,
ticket-scoped specialist subagents** without growing the permanent roster or
breaking separation of duties.

## Rule

### Existence & counting
1. A specialist is **temporary** and **ticket-scoped**: it exists only for one
   approved ticket and is retired when that ticket is Done.
2. Specialists have `status: temporary` and **do not count** toward the
   nine-permanent-agent ceiling. Only `status: permanent` agents count.
3. **Minimum-necessary rule:** no more specialists are active than the ticket
   strictly requires. The Orchestrator caps concurrent specialists.

### Authority & scope
4. A specialist **inherits the ticket's scope and cannot create scope**, edit the
   roadmap, mark Done, or merge. Discovered scope becomes an idea (GOV-007).
5. Every specialist declares a **`parent_authority`** — the permanent agent
   accountable for its output — and a **`ticket`** id. Its work **returns to that
   parent**, who owns the resulting artifact/PR.
6. Creation must be **justified** by the **Orchestrator or Architect** (recorded on
   the ticket): why permanent agents are insufficient, and the expected output.

### Resolving the code-authorship conflict (GOV-011)
Two kinds of specialist, with explicit bounded permissions:

- **Advisory specialists** — e.g. `quant-research`, `trendline-math`,
  `market-data`, `ml-evaluation`, `security`. **Read-only** (no `Write`, `Edit`,
  or `Bash` that mutates). They produce analysis/design that returns to the
  **Architect** or **Implementation Engineer**. They never write product code.

- **Implementation specialists** — e.g. `backend`, `frontend`, `devops`. They may
  **write code, but only under the Implementation Engineer's `parent_authority`**,
  strictly within the ticket branch and scope. The Implementation Engineer remains
  the accountable code author (GOV-011), owns the PR, and hands off to
  Verification/Review. The specialist **cannot** open a competing authority line,
  merge, or mark Done. This is a **delegation of bounded write permission**, not a
  second permanent code-owner.

### Separation of duties still holds
7. Specialists **never** verify, review, approve, or merge their own output, and
   never assume a permanent agent's single-owner authority. Author ≠ verifier ≠
   reviewer ≠ merger applies to specialists too.

## Machine-readable requirements (validator-enforced)
A temporary specialist agent file under `.claude/agents/` must carry, in its
governance block: `status: temporary`, a `ticket:` id, a `parent_authority:` that
matches a permanent agent, `class`, and `bindings` including `GOV-016`. It must
**not** claim `merge-and-release` or `evidence-verdict` authority. Advisory
specialists must not list `Write`/`Edit` tools.

Use [`templates/specialist-agent.md`](../templates/specialist-agent.md) to create one.

## Enforcement
The Orchestrator/Architect justify and cap specialists; the validator checks the
required metadata and that permanent count stays ≤ 9; the Auditor flags orphaned or
expired specialists and any that outlive their ticket.

## Escalation
Specialist without a parent/ticket, or one that writes outside scope or claims a
permanent authority → validator failure or Auditor violation → retired → human review.
