# Workflow — GitHub Issues (Tickets)

A GitHub **Issue** is the atomic unit of governed work (a "ticket"). This defines
its lifecycle; authority for each transition comes from [AGENTS.md](../AGENTS.md).

## States (labels)

| Label | Meaning | Enters via |
|-------|---------|-----------|
| `inbox` | Idea, not yet a ticket | Innovation → Inbox (not an Issue yet) |
| `ready` | Meets [DoR](../governance/definition-of-ready.md) | Product Steward |
| `blocked: freeze` | Ready but under [build-freeze](../governance/build-freeze.md) | Steward |
| `in-progress` | Being planned/built | Orchestrator (assign) |
| `in-verification` | Awaiting evidence gate | Engineer → Verification |
| `in-review` | Awaiting judgement | Verification → Reviewer |
| `done` | Merged + evidenced | Release & Ops only |
| `blocked` | Stalled on dependency | Orchestrator |

## Required fields (enforced at DoR)

- Linked roadmap item, user/business value, success measure.
- Testable acceptance criteria.
- Declared **evidence for Done** ([GOV-006](../governance/definition-of-done.md)).
- Glossary terms used.

Use [`templates/issue.md`](../templates/issue.md).

## Rules

- **Creation is rationed** by [GOV-008](../governance/ticket-hygiene.md): ≤ 5 open
  unstarted Ready tickets, ≤ 3 `in-progress`.
- One Issue = **one verifiable outcome**. No perpetual epics.
- Only **Release & Ops** applies `done`, and only with linked evidence.
- Every state change is a recorded **handoff** ([GOV-010](../governance/handoffs.md)).
- The Auditor reconciles Issue state against evidence each cycle.
