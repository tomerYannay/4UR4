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
| **Executable agents** | The 9 permanent agents as Claude Code subagents (single source of truth) | [`.claude/agents/`](.claude/agents/) |
| Agents (registry) | Missions, tools, boundaries, invocation, temporary specialists | [`AGENTS.md`](AGENTS.md) |
| Governance | The rules every agent obeys (`GOV-001`…`GOV-016`) | [`GOVERNANCE.md`](GOVERNANCE.md) |
| Workflows | Issues, Project, PRs, Ideas Inbox, experiments, audit, status | [`workflows/`](workflows/) |
| Product | Vision, glossary, governed roadmap | [`product/`](product/) |
| Ideas | The Ideas Inbox (proposals, not commitments) | [`ideas/inbox.md`](ideas/inbox.md) |
| Templates | Issue / PR / idea / experiment / report + temporary-specialist scaffold | [`templates/`](templates/) |
| Skills | Created only when reused by ≥2 tickets or agents ([GOV-012](governance/skills-policy.md)) | `skills/` *(none yet, by design)* |
| Validation (static) | Structural + governance + executability checks | [`tools/validate.mjs`](tools/validate.mjs) |
| Validation (live) | Manual Claude Code discovery/restriction procedure | [`docs/claude-code-validation.md`](docs/claude-code-validation.md) |
| CI | Runs the validator on every PR and push to main | [`.github/workflows/governance-validation.yml`](.github/workflows/governance-validation.yml) |

## Operating principle

> **Verified progress beats task volume.** ([GOV-009](governance/prioritization.md))
> A ticket is not `Done` until the repository *proves* it is
> ([GOV-006](governance/definition-of-done.md#gov-006--evidence-bound-done)).

## Run the validation checks

```bash
node tools/validate.mjs
```

The validator enforces: canonical agents under `.claude/agents/` (single source
of truth), valid Claude Code frontmatter and **real tool identifiers**, required
governance metadata, agent-class rules, the ≤9 permanent-agent ceiling,
separation of duties, handoff integrity, governance cross-references, that
deterministic and innovation agents **cannot write**, temporary-specialist
governance, the build-freeze state, and the presence of the CI workflow. It exits
non-zero on any failure so it gates CI ([`governance-validation.yml`](.github/workflows/governance-validation.yml),
run on `pull_request` and `push` to `main`).

For **live** proof that Claude Code discovers the agents and honours their tool
restrictions, follow [`docs/claude-code-validation.md`](docs/claude-code-validation.md)
in a fresh session.

## Human control points

1. **Approve this operating system** (this pull request).
2. **Triage the Ideas Inbox** — only a human + the Product Steward may promote an
   idea to the roadmap ([GOV-003](governance/roadmap-authority.md)).
3. **Lift the build-freeze** to enable autonomous implementation
   ([GOV-015](governance/build-freeze.md)).

Nothing in categories 2–3 happens automatically.
