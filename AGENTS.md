# Agent Registry

The 4UR4 operating system runs on **9 permanent agents** — the hard ceiling
(requirement 2). New permanent agents require a human decision; temporary
experimental agents are governed by [GOV-008](governance/ticket-hygiene.md).

Each agent has **exactly one** primary authority so responsibilities never
overlap ([GOV-011 Separation of Duties](governance/separation-of-duties.md)).

## Agent classes ([GOV-001](governance/classification.md))

| Class | Behaviour | Creativity |
|-------|-----------|------------|
| **deterministic** | Same input → same output. Rule-checkers and gates. | None permitted |
| **bounded-creative** | Generates novel options *inside* explicit constraints. | Bounded |
| **mixed** | Deterministic where it decides, creative where it proposes. | Scoped per action |

## The nine agents

| # | Agent | Codename | Class | Sole authority | File |
|---|-------|----------|-------|----------------|------|
| 0 | Orchestrator | Agent Zero | mixed | Sequencing & prioritization | [agents/00-orchestrator.md](agents/00-orchestrator.md) |
| 1 | Product Steward | — | mixed | The roadmap & Definition of Ready | [agents/01-product-steward.md](agents/01-product-steward.md) |
| 2 | Product Innovation Agent | — | bounded-creative | Idea generation (Inbox only) | [agents/02-product-innovation.md](agents/02-product-innovation.md) |
| 3 | Architect | — | mixed | Technical design of a ticket | [agents/03-architect.md](agents/03-architect.md) |
| 4 | Implementation Engineer | — | mixed | Writing product code | [agents/04-implementation-engineer.md](agents/04-implementation-engineer.md) |
| 5 | Verification Agent | — | deterministic | Evidence-based Done verdict | [agents/05-verification.md](agents/05-verification.md) |
| 6 | Code Reviewer | — | mixed | Judgement on diff quality | [agents/06-code-reviewer.md](agents/06-code-reviewer.md) |
| 7 | Release & Ops Agent | — | deterministic | Merge, release, move to Done | [agents/07-release-ops.md](agents/07-release-ops.md) |
| 8 | Project Auditor | — | deterministic | Health, traceability, reports | [agents/08-project-auditor.md](agents/08-project-auditor.md) |

## Authority matrix (who may do what)

| Capability | Owner | Everyone else |
|------------|-------|---------------|
| Add/change **roadmap** | Product Steward (with human) | forbidden |
| Generate **ideas** | Product Innovation Agent | forbidden |
| Write **product code** | Implementation Engineer | forbidden |
| Issue **Done verdict** (evidence) | Verification Agent | forbidden |
| **Merge / release** | Release & Ops Agent | forbidden |
| Mark ticket **Done** on board | Release & Ops Agent | forbidden |
| **Prioritize / assign** work | Orchestrator | forbidden |
| **Audit / report** | Project Auditor | forbidden |

## Lifecycle at a glance

```
Idea (Innovation) ─▶ Inbox ─▶ [human + Steward triage] ─▶ Roadmap (Steward)
      │
      ▼
Ready ticket (Steward) ─▶ Orchestrator (prioritize) ─▶ Architect (plan)
      │
      ▼
Implementation Engineer (code + evidence) ─▶ Verification (evidence gate)
      │
      ▼
Code Reviewer (judgement) ─▶ Release & Ops (merge + Done) ─▶ Project Auditor (report)
```

See [`workflows/`](workflows/) for the concrete GitHub mechanics and
[GOV-010 Handoff Protocol](governance/handoffs.md) for the rules that connect them.
