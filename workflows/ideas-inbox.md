# Workflow — Ideas Inbox

The [Ideas Inbox](../ideas/inbox.md) is where creativity is captured **without**
committing the product. It is a proposal queue, not a backlog.

## Flow

```
Product Innovation Agent ─(idea card, ≤3/cycle)─▶ Ideas Inbox
        │
        ▼
Human + Product Steward triage  ── reject / park / promote
        │ (promote requires value + success measure + focus check + human sign-off)
        ▼
Roadmap (Product Steward writes)  ─▶ later becomes a Ready ticket
```

## Rules

- **Only the Product Innovation Agent** adds idea cards, **only** to the Inbox,
  **only** within the idea budget ([GOV-008](../governance/ticket-hygiene.md)).
- An idea is **not** work. It has **no** roadmap or ticket status until promoted.
- **Promotion is human-gated** ([GOV-003](../governance/roadmap-authority.md),
  [GOV-013](../governance/approval-gate.md)) and must pass the
  [Product-Focus Guard](../governance/product-focus.md).
- Each idea uses [`templates/idea.md`](../templates/idea.md) with **value / effort /
  risk** tags and an optional experiment to de-risk it.
- The Auditor may **signal gaps** to Innovation, but does not author ideas
  ([GOV-011](../governance/separation-of-duties.md)).

## Triage outcomes

| Outcome | Meaning |
|---------|---------|
| **Promote** | Human-approved → Steward adds to roadmap. |
| **Park** | Keep in Inbox for a future cycle. |
| **Experiment** | Run a bounded [experiment](experimentation.md) before deciding. |
| **Reject** | Out of scope / low value; archived with a reason. |
