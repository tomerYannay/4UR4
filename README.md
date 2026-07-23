# 4UR4 — Agent Operating System

> **Status: `AWAITING HUMAN APPROVAL` — autonomous implementation is DISABLED.**
> This repository currently contains **only** the agent operating system
> (agents, governance, workflows, templates). **No product functionality is
> implemented, and none may be built until a human approves this system and
> lifts the build-freeze** (see [GOV-015](governance/build-freeze.md) and
> [GOV-013](governance/approval-gate.md)).

## What this is

4UR4 is an AI-managed SaaS that identifies **logarithmic descending trendlines**
originating at a stock's **all-time high**, detects **confirmed breakouts and
retests**, assigns **explainable confidence scores**, and incorporates
**market sentiment** — including **Fear & Greed** and a **proprietary
market-regime score**.

This repo bootstraps the *operating system that will build that product*: a
small, focused, non-overlapping team of agents governed by explicit rules that
optimize for **correctness, focus, traceability, reproducibility, controlled
creativity, business value, and minimal process overhead**.

The product itself is described in [`product/vision.md`](product/vision.md).
This bootstrap deliberately **does not** implement any of it (requirement 13).

## Map of the system

| Area | Purpose | Entry point |
|------|---------|-------------|
| Agents | The ≤9 permanent agents, their missions and boundaries | [`AGENTS.md`](AGENTS.md) |
| Governance | The rules every agent obeys (`GOV-###`) | [`GOVERNANCE.md`](GOVERNANCE.md) |
| Workflows | Issues, Project, PRs, Ideas Inbox, experiments, audit, status | [`workflows/`](workflows/) |
| Product | Vision, glossary, governed roadmap | [`product/`](product/) |
| Ideas | The Ideas Inbox (proposals, not commitments) | [`ideas/inbox.md`](ideas/inbox.md) |
| Templates | Canonical issue / PR / idea / experiment / report shapes | [`templates/`](templates/) |
| Skills | Created only when reused by ≥2 tickets or agents ([GOV-012](governance/skills-policy.md)) | `skills/` *(none yet, by design)* |
| Validation | Structural + governance checks | [`tools/validate.mjs`](tools/validate.mjs) |

## Operating principle

> **Verified progress beats task volume.** ([GOV-009](governance/prioritization.md))
> A ticket is not `Done` until the repository *proves* it is
> ([GOV-006](governance/definition-of-done.md#gov-006--evidence-bound-done)).

## Run the validation checks

```bash
node tools/validate.mjs
```

The validator enforces agent-count limits, required fields, valid agent
classes, handoff integrity, governance cross-references, and the build-freeze
state. It exits non-zero on any failure so it can gate CI.

## Human control points

1. **Approve this operating system** (this pull request).
2. **Triage the Ideas Inbox** — only a human + the Product Steward may promote an
   idea to the roadmap ([GOV-003](governance/roadmap-authority.md)).
3. **Lift the build-freeze** to enable autonomous implementation
   ([GOV-015](governance/build-freeze.md)).

Nothing in categories 2–3 happens automatically.
