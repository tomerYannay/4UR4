# Workflow — GitHub Project (Board)

One GitHub **Project** board is the single operational view of flow. It mirrors
Issue state; the Issue is the source of truth, the board is the lens.

## Columns

```
Inbox ▶ Ready ▶ In Progress ▶ In Verification ▶ In Review ▶ Done
                     │
                  Blocked (swimlane)
```

| Column | WIP cap | Moved by |
|--------|---------|----------|
| Inbox | — (idea budget: 3/cycle) | Product Innovation → Steward |
| Ready | **5** unstarted | Product Steward |
| In Progress | **3** total | Orchestrator |
| In Verification | — | Engineer → Verification |
| In Review | — | Verification → Reviewer |
| Done | — | **Release & Ops only** |

WIP caps come from [GOV-008](../governance/ticket-hygiene.md); they are the
system's primary anti-bloat control.

## Rules

- The **Orchestrator** owns column movement up to Verification; **Release & Ops**
  owns the final move to **Done** ([GOV-011](../governance/separation-of-duties.md)).
- A card cannot enter **Done** without linked evidence
  ([GOV-006](../governance/definition-of-done.md)).
- **Verified throughput** (Done-with-evidence per cycle) is the headline metric,
  shown beside opened-card counts ([GOV-009](../governance/prioritization.md)).
- The board is read-only context for the **Auditor**; it never edits cards.
