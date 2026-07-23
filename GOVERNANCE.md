# Governance Registry

Every rule has a stable `GOV-###` id. Agents cite these ids in their
**Governance Bindings** section; the [validator](tools/validate.mjs) checks that
every binding resolves to a rule here and that every rule is enforced somewhere.

Rules are **normative**: an agent that cannot satisfy a bound rule must **stop
and escalate**, never proceed.

| Rule | Title | Scope | Enforced by | File |
|------|-------|-------|-------------|------|
| **GOV-001** | Agent Classification & Non-Determinism Governance | all | validator + Orchestrator | [classification.md](governance/classification.md) |
| **GOV-002** | Single Roadmap Authority | non-deterministic | Product Steward | [roadmap-authority.md](governance/roadmap-authority.md) |
| **GOV-003** | Innovation Governance (propose, never commit) | bounded-creative | Product Steward + human | [roadmap-authority.md](governance/roadmap-authority.md) |
| **GOV-004** | Definition of Ready | all | Product Steward | [definition-of-ready.md](governance/definition-of-ready.md) |
| **GOV-005** | Definition of Done | all | Verification + Release & Ops | [definition-of-done.md](governance/definition-of-done.md) |
| **GOV-006** | Evidence-Bound Done (no Done without repo evidence) | all | Verification Agent | [definition-of-done.md](governance/definition-of-done.md) |
| **GOV-007** | Product-Focus Guard (anti scope-drift) | all | Product Steward + Auditor | [product-focus.md](governance/product-focus.md) |
| **GOV-008** | Ticket Hygiene & Anti-Bloat | all | Orchestrator + Auditor | [ticket-hygiene.md](governance/ticket-hygiene.md) |
| **GOV-009** | Verified-Progress-Over-Volume | all | Orchestrator | [prioritization.md](governance/prioritization.md) |
| **GOV-010** | Handoff Protocol | all | Orchestrator | [handoffs.md](governance/handoffs.md) |
| **GOV-011** | Separation of Duties (non-overlap) | all | validator + Auditor | [separation-of-duties.md](governance/separation-of-duties.md) |
| **GOV-012** | Skill Creation Threshold (reuse ≥2) | all | Product Steward | [skills-policy.md](governance/skills-policy.md) |
| **GOV-013** | Human Approval Gate | all | human | [approval-gate.md](governance/approval-gate.md) |
| **GOV-014** | Market-Sentiment Research Boundary | all | Product Steward | [market-sentiment-context.md](governance/market-sentiment-context.md) |
| **GOV-015** | Build-Freeze (no product implementation yet) | all | human + validator | [build-freeze.md](governance/build-freeze.md) |

## Rule anatomy

Each rule file states:

- **Intent** — the risk it controls.
- **Rule** — the normative statement(s).
- **Applies to** — agents / classes in scope.
- **Enforcement** — who checks it and how (human, agent, or validator).
- **Escalation** — what happens on violation.

## Governance by agent class ([GOV-001](governance/classification.md))

- **Deterministic agents** (Verification, Release & Ops, Project Auditor) may
  never introduce novelty. Their outputs must be reproducible from inputs; if a
  decision requires judgement they **escalate** rather than improvise.
- **Bounded-creative agents** (Product Innovation) may generate novelty **only**
  into designated sinks (the Ideas Inbox) and **only** within tagged constraints
  (value/effort/risk, budgets). They hold **no commit authority**.
- **Mixed agents** (Orchestrator, Product Steward, Architect, Implementation
  Engineer, Code Reviewer) declare, per action, whether they are acting
  deterministically (gated by rules) or creatively (bounded and escalatable).
