# 4UR4 — Project State (canonical, current-state only)

> **Current state only — not a history log.** **Content owner: Product Steward.** The
> **Orchestrator** ensures this file is updated after: a phase completes · a Product Owner
> decision is recorded · a roadmap phase changes · a major PR merges · a build-freeze scope
> changes. The **Strategic Product Reviewer** reads and validates this file but **may not
> edit** it. If it is stale or contradicts stronger evidence, that is flagged, not silently
> fixed. Precedence when sources disagree: latest PO decision on GitHub →
> [`human-decisions.md`](human-decisions.md) → [`requirements.md`](requirements.md) + specs →
> [`roadmap.md`](roadmap.md) → merged fixture evidence → open PR proposals → agent summaries.

- **Last updated:** 2026-07-25
- **Last reviewed commit SHA (main):** `c0f66ea15a1a5c9c7af631c8fcfccbd7cc8e1527`
- **Build-freeze status:** **ON** ([GOV-015](../governance/build-freeze.md)) — no product implementation until a human lifts it per-scope.

## Product objective
- **Final:** a reliable commercial SaaS that detects ATH-anchored logarithmic descending
  resistance lines, identifies breakouts and retests, produces explainable confidence
  scores, adds market context, and eventually delivers subscription alerts.
- **Current MVP:** prove the detector can **reproducibly** identify the intended canonical
  trendline and breakout state on **historical market data** before building dashboard,
  alerts, billing, or ML.

## Current phase
**Phase 0 → Phase 1 boundary.** Phase 0 (specification & golden examples) is substantially
complete and Phase 1 (market-data foundation) is in its **research** stage; Phase 1
implementation and beyond remain **freeze-blocked**.

## Completed milestones
- Agent Operating System bootstrapped + executable in Claude Code (PR #1).
- Proposed MVP roadmap, PRD, specs, human-decision register (PR #8).
- **Phase 0 golden fixtures** (19 synthetic) + **RM-01** real-market case, PO-approved;
  **SC-1 = MATCH**, **SC-2 resolved (HD-11)** (PR #9).
- ChatGPT↔Claude **handoff protocol** + PR template + Agent Coordination Queue (#10) (PR #11).
- **Strategic Product Reviewer** added as the 10th permanent agent (PR #13).

## Active work
- **PR #12** — Phase 1 market-data research (Issues **#4**, **#5**): provider comparison +
  survivorship/delisted research. **Draft; CI green; 0 reviews; awaiting ChatGPT/strategic
  review** (round 1 of 2).
- **Issue #14** — documentation reconciliation (freeze-permitted, **docs only**): refresh this
  file's reviewed-SHA/PR-#13 currency, the RM-01 Product-Owner-approval references in
  [`fixtures/README.md`](fixtures/README.md), the stale fixture count in
  [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md), SC-2 hygiene in
  `fixtures/real/RM-01/annotation.json`, and a currency note on
  [`../docs/live-validation-evidence.md`](../docs/live-validation-evidence.md). Open PR on
  branch `docs/reconcile-project-state-phase0-traceability`. Changes **no** product
  definition, spec rule, fixture data, or roadmap entry.

## Next milestone
Complete the Phase 1 research review, then obtain the **Product Owner decision on HD-06**
(data-provider selection + recurring spend). Phase 1 *implementation* cannot start until the
freeze is lifted per-scope.

## Blocked work
- **#6** Market-data ingestion service (Phase 1 impl) — `blocked: freeze`.
- **#7** Trendline detection engine (Phase 2 impl) — `blocked: freeze`.
- All of Phases 2–9 — behind the build-freeze and their entry criteria.

## Pending Product Owner decisions
- **HD-06** — data-provider selection + recurring spend (**human-gated**; research in PR #12).

## Open issues / PRs (governed index)
- Issues: **#4**, **#5** (Phase 1 research, open), **#6**, **#7** (impl, `blocked: freeze`), **#10** (Agent Coordination Queue, permanent index), **[#14](https://github.com/tomerYannay/4UR4/issues/14)** (documentation reconciliation, open, docs-only).
- Open PRs: **#12** (Phase 1 research, draft, CI green, 0 reviews, awaiting strategic review) · the **documentation-reconciliation PR for Issue #14** (docs-only, branch `docs/reconcile-project-state-phase0-traceability`; its PR number is recorded here once the PR is opened). Coordination queue: [#10](https://github.com/tomerYannay/4UR4/issues/10).

## Sources
[`roadmap.md`](roadmap.md) · [`requirements.md`](requirements.md) · [`human-decisions.md`](human-decisions.md) ·
[`trendline-specification.md`](trendline-specification.md) · [`confidence-specification.md`](confidence-specification.md) ·
[`fixtures/README.md`](fixtures/README.md) · [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md) ·
[`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) ·
[`../docs/operations/agent-handoff-protocol.md`](../docs/operations/agent-handoff-protocol.md) ·
[`../GOVERNANCE.md`](../GOVERNANCE.md)
