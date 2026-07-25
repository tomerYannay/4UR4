# 4UR4 — Project State (canonical, current-state only)

> **Current state only — not a history log.** *A fuller post-merge refresh of this file — and
> the queued roadmap-status reconciliation — are deliberately deferred until PR #18 merges; the
> edits made on that branch are confined to statements the branch's own diff would otherwise
> falsify.* **Content owner: Product Steward.** The
> **Orchestrator** ensures this file is updated after: a phase completes · a Product Owner
> decision is recorded · a roadmap phase changes · a major PR merges · a build-freeze scope
> changes. The **Strategic Product Reviewer** reads and validates this file but **may not
> edit** it. If it is stale or contradicts stronger evidence, that is flagged, not silently
> fixed. Precedence when sources disagree: latest PO decision on GitHub →
> [`human-decisions.md`](human-decisions.md) → [`requirements.md`](requirements.md) + specs →
> [`roadmap.md`](roadmap.md) → merged fixture evidence → open PR proposals → agent summaries.

- **Last updated:** 2026-07-25
- **Last reviewed commit SHA (main):** `bd5ab575d0461d033c7c54741d25d632ed74a10c`
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

**Phase 0 completeness qualifier — RETIRED (2026-07-25).** The qualifier recorded here (that
Phase 0 exit was not clean because **GX-08 as committed** encoded a precondition **HD-11
forbids**) is **removed by the [#16](https://github.com/tomerYannay/4UR4/issues/16) evidence
correction**: GX-08 now expects the all-highs upper-log-hull result `B* = (1, 98)`, GX-20
covers the still-reachable `NO_VALID_SECOND_ANCHOR` case, and the stale pivot-conditioned text
has been swept. The narrower question that sweep raised — whether §8 selection is evaluated
over the **full history** or freezes at line formation — has since been **decided by the
Product Owner as HD-12** (a *relayed* ruling — see the caveat below): selection is **rolling, causal, as-of-time**, frozen at a confirmed
breakout. Two consequential decisions followed on 2026-07-25: **HD-13** (`eps_break` stays
unlocked; ordinary fixtures must be tolerance-robust, with GX-15 alone retained as the
boundary fixture) and **HD-14** (formation gates restated as first-class, `k`-independent
parameters `min_formation_bars = 8` / `min_ath_age_bars = 3`). The entire fixture set has been
re-derived as-of-time and re-verified mechanically; the in-place
`geometry_check.open_issue_2026_07_25` flags are resolved and removed.

**⚠ All three rulings are RELAYED, not ratified.** HD-12, HD-13 and HD-14 reached the
repository as Product Owner instructions issued directly to the autonomous session; nothing
was posted to GitHub, so no citable decision artifact exists and each register entry is
marked *"relayed — ratification outstanding"*. Everything downstream — the 23-fixture
correctness contract, spec §18/§21, D-TL-11 and D-TL-12 — inherits that status until a
ruling is posted naming the exact head.

## Completed milestones
- Agent Operating System bootstrapped + executable in Claude Code (PR #1).
- Proposed MVP roadmap, PRD, specs, human-decision register (PR #8).
- **Phase 0 golden fixtures** (**23 synthetic** — 20 geometry + 3 null-anchor, after the #16
  correction and the HD-12 as-of-time audit added GX-20 and the formation-gate regressions
  GX-21/GX-22/GX-23, and moved GX-08 into the geometry set) + **RM-01** real-market case,
  PO-approved; **SC-1 = MATCH**, **SC-2 resolved (HD-11)** (PR #9; fixtures corrected under #16).
- ChatGPT↔Claude **handoff protocol** + PR template + Agent Coordination Queue (#10) (PR #11).
- **Strategic Product Reviewer** added as the 10th permanent agent (PR #13).
- **Six-record documentation reconciliation** to merged evidence, docs-only (Refs #14); also
  committed the **Historical Product Owner Decision Record — RM-01** in
  [`human-decisions.md`](human-decisions.md), supplying the citable approval artifact PR #9
  lacked (PR #15).

## Active work
- **PR #12** — Phase 1 market-data research (Issues **#4**, **#5**): provider comparison +
  survivorship/delisted research. **Draft; CI green; 0 reviews; awaiting ChatGPT/strategic
  review** (round 1 of 2).
- **Issue [#16](https://github.com/tomerYannay/4UR4/issues/16)** — Phase 0 **evidence
  correction** (freeze-permitted; created per **Product Owner ruling 2026-07-25**, recorded in
  the [rulings comment on #14](https://github.com/tomerYannay/4UR4/issues/14#issuecomment-5078902902)
  and restated in the body of #16). **GX-08**'s
  expected output asserts `NO_VALID_SECOND_ANCHOR` on a justification **HD-11 removed** (the
  pivot-high precondition). The correction re-derives GX-08 to the all-highs upper-log-hull
  result (**`B* = (1, 98)`**), sweeps the remaining stale pivot-conditioned no-anchor text in
  [`trendline-specification.md`](trendline-specification.md),
  [`fixtures/README.md`](fixtures/README.md) and
  [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md) (its null-anchor list, its
  `19 / 19 … 3 null-anchor by design` result line, and its SC-2 claim that removing the pivot
  precondition **moves no existing anchor**), and adds a new fixture **GX-20** for the
  genuinely reachable `NO_VALID_SECOND_ANCHOR` case (duplicate ATH / double top). It
  **changes no rule** — **HD-11** and the canonical algorithm are untouched; this is a **stale
  Phase 0 evidence defect, not a new product-definition decision** (Product Owner ruling).
  Labels: `documentation`, `epic: product-quant-spec`, `ready-eligible`. **Authored on branch
  `fix/gx08-hd11-pivot-sweep`; awaiting verification/review and merge.** The sweep additionally
  surfaced the full-history-vs-formation-window selection question, which the Product Owner
  decided as **HD-12** (as-of-time selection), followed by **HD-13** and **HD-14**. The branch
  now also carries the complete as-of-time re-derivation of the fixture set, the
  `k`-independent formation parameters and their regression fixtures. **Two Product-Owner-only
  items block merge:** ratification of the relayed rulings HD-12/13/14, and a GOV-015 scope
  ruling on the committed causal reference model `tools/fixture-replay.mjs`.

## Next milestone
Two tracks: (1) complete the **[#16](https://github.com/tomerYannay/4UR4/issues/16) Phase 0
evidence correction** (GX-08 re-derivation + stale-text sweep + GX-20); (2) complete the
**PR #12 Phase 1 research review**, which is the path to the **Product Owner decision on
HD-06** (data-provider selection + recurring spend). Phase 1 *implementation* cannot start
until the freeze is lifted per-scope.

## Blocked work
- **#6** Market-data ingestion service (Phase 1 impl) — `blocked: freeze`.
- **#7** Trendline detection engine (Phase 2 impl) — `blocked: freeze`.
- All of Phases 2–9 — behind the build-freeze and their entry criteria.

## Pending Product Owner decisions
- **HD-06** — data-provider selection + recurring spend (**human-gated**; research in PR #12).

## Open issues / PRs (governed index)
- Issues: **#4**, **#5** (Phase 1 research, open), **#6**, **#7** (impl, `blocked: freeze`), **#10** (Agent Coordination Queue, permanent index), **[#16](https://github.com/tomerYannay/4UR4/issues/16)** (GX-08 + stale pivot-conditioned `NO_VALID_SECOND_ANCHOR` sweep, open, Phase 0 evidence correction).
- Open PRs: **#12** (Phase 1 research, draft, CI green, 0 reviews, awaiting strategic review) · **[#18](https://github.com/tomerYannay/4UR4/pull/18)** (Phase 0 evidence correction + as-of-time fixture audit, draft, CI green, **two rounds of the full review chain recorded**, blocked on two Product-Owner-only items — ratification of HD-12/13/14 and a GOV-015 scope ruling). Coordination queue: [#10](https://github.com/tomerYannay/4UR4/issues/10).

## Sources
[`roadmap.md`](roadmap.md) · [`requirements.md`](requirements.md) · [`human-decisions.md`](human-decisions.md) ·
[`trendline-specification.md`](trendline-specification.md) · [`confidence-specification.md`](confidence-specification.md) ·
[`fixtures/README.md`](fixtures/README.md) · [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md) ·
[`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) ·
[`../docs/operations/agent-handoff-protocol.md`](../docs/operations/agent-handoff-protocol.md) ·
[`../GOVERNANCE.md`](../GOVERNANCE.md)
