# 4UR4 — Project State (canonical, current-state only)

> **Current state only — not a history log.** *The post-merge refresh deferred until PR #18
> merged, and the roadmap fixture-coverage reconciliation it queued, are **both done** — see
> the 2026-07-26 entries in [`roadmap.md`](roadmap.md).* **Content owner: Product Steward.** The
> **Orchestrator** ensures this file is updated after: a phase completes · a Product Owner
> decision is recorded · a roadmap phase changes · a major PR merges · a build-freeze scope
> changes. The **Strategic Product Reviewer** reads and validates this file but **may not
> edit** it. If it is stale or contradicts stronger evidence, that is flagged, not silently
> fixed. Precedence when sources disagree: latest PO decision on GitHub →
> [`human-decisions.md`](human-decisions.md) → [`requirements.md`](requirements.md) + specs →
> [`roadmap.md`](roadmap.md) → merged fixture evidence → open PR proposals → agent summaries.

- **Last updated:** 2026-07-26
- **Last reviewed commit SHA (main):** `e56ed8eec79a800d759e17bd7b2dba81d449904b` — the merge
  commit of [PR #18](https://github.com/tomerYannay/4UR4/pull/18).
- **Unmerged work this file already reflects:** branch
  `feat/universe-definition-and-phase2-planning` at its **current head** — the HD-18
  universe definition, the Phase 2 implementation plan, the HD-20 → **SPR-D-01**
  resolution propagated here, and the 2026-07-26 review-round corrections. **None of it is
  on `main` yet**, so where this file and `main` disagree, the branch is the newer
  statement and the merge is still owed. *(This line named a specific commit and fell one
  commit behind itself — a file whose job is to say what is and is not on `main` must not
  do that. It now names the branch head rather than a SHA that goes stale on every
  commit.)*
- **Build-freeze status:** **ON** ([GOV-015](../governance/build-freeze.md)) — no product
  implementation until a human lifts it per-scope. `build_freeze: ON`,
  `autonomous_implementation: DISABLED`. **Nothing has been lifted**; the HD-15 ruling is a
  scope clarification covering one Phase-0 evidence-tooling file, not a partial lift.

## Product objective
- **Final:** a reliable commercial SaaS that detects ATH-anchored logarithmic descending
  resistance lines, identifies breakouts and retests, produces explainable confidence
  scores, adds market context, and eventually delivers subscription alerts.
- **Current MVP:** prove the detector can **reproducibly** identify the intended canonical
  trendline and breakout state on **historical market data** before building dashboard,
  alerts, billing, or ML.
- **Universe (HD-18, 2026-07-26,
  [#24](https://github.com/tomerYannay/4UR4/issues/24)):** 4UR4 computes its **own
  point-in-time universe**, the **4UR4 US Large-Cap 500**, under transparent versioned
  rules. It **is not the S&P 500**, is not licensed constituent membership, and is not
  endorsed by or equivalent to S&P Dow Jones Indices. The cost is stated with the benefit:
  **4UR4 backtest results are not comparable to published S&P 500 strategy results**, which
  the Phase 4 **UNIV-DISC** gate requires to travel with every reported number. Design:
  [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
  (design, not implementation).

## Current phase
**Phase 0 → Phase 1 boundary.** Phase 0 (specification & golden examples) is substantially
complete and Phase 1 (market-data foundation) is in its **research** stage; Phase 1
implementation and beyond remain **freeze-blocked**.

**Phase 2 entry is separately blocked**, independently of the freeze, by
[#19](https://github.com/tomerYannay/4UR4/issues/19) and
[#20](https://github.com/tomerYannay/4UR4/issues/20) — see Active work. Both are now named as
Phase 2 criteria in [`roadmap.md`](roadmap.md).

**Phase 0 completeness qualifier — RETIRED (2026-07-25), and the correction is now MERGED.**
The qualifier recorded here (that Phase 0 exit was not clean because **GX-08 as committed**
encoded a precondition **HD-11 forbids**) is **removed by the
[#16](https://github.com/tomerYannay/4UR4/issues/16) evidence
correction, merged as `e56ed8e`**: GX-08 now expects the all-highs upper-log-hull result
`B* = (1, 98)`, GX-20
covers the still-reachable `NO_VALID_SECOND_ANCHOR` case, and the stale pivot-conditioned text
has been swept. The narrower question that sweep raised — whether §8 selection is evaluated
over the **full history** or freezes at line formation — has since been **decided by the
Product Owner as HD-12** (originally a *relayed* ruling; since ratified — see below):
selection is **rolling, causal, as-of-time**, frozen at a confirmed
breakout. Two consequential decisions followed on 2026-07-25: **HD-13** (`eps_break` stays
unlocked; ordinary fixtures must be tolerance-robust, with GX-15 alone retained as the
boundary fixture) and **HD-14** (formation gates restated as first-class, `k`-independent
parameters `min_formation_bars = 8` / `min_ath_age_bars = 3`). The entire fixture set has been
re-derived as-of-time and re-verified mechanically; the in-place
`geometry_check.open_issue_2026_07_25` flags are resolved and removed.

**HD-12, HD-13 and HD-14 are APPROVED — RATIFIED; HD-15 is APPROVED.** The first three
originally reached the repository as Product Owner instructions with no posted artifact; that
gap is closed by the
[ratification of 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012)
(Product Owner, given against head `2651cd0`), with HD-13 ratified *as recorded* — including
the four clauses
its entry enumerates as going beyond the escalated options. **HD-15** was approved in the same
ruling: the causal reference model is permitted under GOV-015 as Phase-0 evidence tooling,
**conferring no Phase-2 credit**, and requiring that the Phase-2 engine be authored by an agent
that has not read it. **GOV-015 itself remains ON** — the HD-15 ruling clarifies the scope of
one file and lifts nothing.

## Completed milestones
- Agent Operating System bootstrapped + executable in Claude Code (PR #1).
- Proposed MVP roadmap, PRD, specs, human-decision register (PR #8).
- **Phase 0 golden fixtures** (**23 synthetic** — 20 geometry + 3 null-anchor, after the #16
  correction and the HD-12 as-of-time audit added GX-20 and the formation-gate regressions
  GX-21/GX-22/GX-23, and moved GX-08 into the geometry set) + **RM-01** real-market case,
  PO-approved; **SC-1 = MATCH**, **SC-2 resolved (HD-11)** (PR #9; fixtures corrected under #16).
  *Counted from disk on 2026-07-26: `product/fixtures/golden/` holds exactly 23 fixture
  directories, `GX-01`…`GX-23`, each with `input.csv` + `expected.json`, plus `real/RM-01/`.*
- **[PR #18](https://github.com/tomerYannay/4UR4/pull/18) MERGED** as `e56ed8e` — the Phase 0
  evidence correction and the HD-12 as-of-time fixture audit. The **23 golden fixtures
  (GX-01…GX-23)** reproduce **exactly** under as-of-time replay in CI. *(Corrected
  2026-07-26: this previously read "23 golden + RM-01". **RM-01 is not replayed** —
  `fixture-replay.mjs` reads only `golden/`, and `check-evidence.mjs` only schema-validates
  RM-01's annotation. No mechanical guard has ever covered RM-01's geometry, which is why
  the divergence escalated as HD-20 — since resolved by **SPR-D-01** — survived that audit.
  SPR-D-01's B-clause is the first mechanical guard proposed over RM-01, and if its
  expectation **is** replay-generated, so it **is** a **regression guard against today's
  model**, not independent verification.)* Landed with
  it: spec §21, D-TL-11, D-TL-12, GX-20, the HD-14 formation-gate regressions
  GX-21/GX-22/GX-23, and `tools/fixture-replay.mjs` (permitted under HD-15).
- **Roadmap fixture-coverage reconciliation** (Refs #19, #20): Phase 2/3 exit gates now cover
  the **whole** committed fixture set via a derived partition instead of a typed fixture list,
  and HD-15 condition 2 has a Phase-2 **entry** mechanism (E2-AUTHOR). See
  [`roadmap.md`](roadmap.md).
- ChatGPT↔Claude **handoff protocol** + PR template + Agent Coordination Queue (#10) (PR #11).
- **Strategic Product Reviewer** added as the 10th permanent agent (PR #13).
- **Six-record documentation reconciliation** to merged evidence, docs-only (Refs #14); also
  committed the **Historical Product Owner Decision Record — RM-01** in
  [`human-decisions.md`](human-decisions.md), supplying the citable approval artifact PR #9
  lacked (PR #15).

## Active work
- **Branch `feat/universe-definition-and-phase2-planning` (unmerged).** Carries the HD-18
  universe definition and
  [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
  (design only — §11.2 escalates **OQ-U1…OQ-U7** to the Product Owner and they are still
  open), the Phase 2 implementation plan, and the **SPR-D-01** propagation into
  [`roadmap.md`](roadmap.md), [`fixtures/README.md`](fixtures/README.md) §6b and this file.
  **Documents only; no product code, and no freeze lift.**
- **PR #12** — Phase 1 market-data research (Issues **#4**, **#5**): provider comparison +
  survivorship/delisted research. **Draft; CI green; 0 reviews; awaiting ChatGPT/strategic
  review** (round 1 of 2). This is the path to **HD-06**.
- **Issue [#19](https://github.com/tomerYannay/4UR4/issues/19)** — roadmap exit-criteria gap.
  **Addressed in [`roadmap.md`](roadmap.md) on the current unmerged branch** (not on `main`,
  which was last reviewed at `e56ed8e`, before #19 existed) and awaiting review: the Phase
  2/3 gates named 12 of the 23
  golden fixtures, so an engine could have satisfied the Phase 2 exit gate while contradicting
  the ratified HD-11/SC-2, HD-13 and HD-14 rulings. **Blocks Phase 2 entry until closed.**
- **Issue [#20](https://github.com/tomerYannay/4UR4/issues/20)** — HD-15 condition 2 had no
  enforcement mechanism. **Partly addressed on the same unmerged branch:**
  [`roadmap.md`](roadmap.md) now
  carries **E2-AUTHOR**, a four-part Phase 2 *entry* criterion requiring clean-room authorship
  of the engine w.r.t. `tools/fixture-replay.mjs`. The *document* half is done; the
  *configuration* half (a real tool-deny on the authoring agent) is owed by the Orchestrator
  and is **not** a Product Steward action. **Blocks Phase 2 entry until closed.**
- **Issue [#21](https://github.com/tomerYannay/4UR4/issues/21)** — review verdicts cannot
  become citable artifacts, and review attribution collapses to a single account. **Required
  before HD-06 or any freeze lift**, and now also a stated dependency of E2-AUTHOR criterion 4
  (the clean-room attestation has nowhere to live until #21 is fixed).
- **Issue [#22](https://github.com/tomerYannay/4UR4/issues/22)** — evidence-tooling follow-ups.
- **Traceability debt from [#16](https://github.com/tomerYannay/4UR4/issues/16)
  (the issue itself is CLOSED).** Phase 0 evidence correction, **delivered by PR #18, now
  merged** (see Completed milestones). #16 was closed without ever being re-scoped to cover
  what PR #18 actually delivered (HD-12/13/14, spec §21, D-TL-11/12, three new fixtures, the
  reference model), so the ticket→PR traceability link remains incomplete (Project Auditor,
  GOV-007). **This survives as a documentation debt, not as an open ticket** — reopening #16
  to record it is an Orchestrator decision, not a Product Owner one.

## Next milestone
Two tracks. (1) **Unblock Phase 2 entry:** close **#19** (addressed on the current unmerged
branch, pending review) and **#20** (document half likewise; the authoring-agent deny
configuration still owed), both of which gate Phase 2 entry, with **#21** required beneath
them. **HD-20 is no longer on this list** — SPR-D-01 resolved it, and the RM-01 gate values
are now stated rather than suspended. (2) **Complete the
PR #12 Phase 1 research review**, the path to the **Product Owner decision on HD-06**
(data-provider selection + recurring spend) — which **#21** also gates. Phase 1 and Phase 2
*implementation* cannot start until a human lifts the freeze per-scope; nothing here lifts it.

## Blocked work
- **#6** Market-data ingestion service (Phase 1 impl) — `blocked: freeze`.
- **#7** Trendline detection engine (Phase 2 impl) — `blocked: freeze`, **and additionally
  blocked on #19 + #20** (Phase 2 entry criteria), with **#21** beneath them. *(The RM-01
  gate-value block is **cleared** by SPR-D-01; the Phase 2 plan's S0 dependency on HD-20 is
  satisfied. Nothing else about #7 moved — the freeze and the entry criteria stand.)*
- All of Phases 2–9 — behind the build-freeze and their entry criteria.

## Pending Product Owner decisions
- **HD-06** — data-provider selection + recurring spend (**human-gated**). Research is
  delivered ([`data-provider-findings.md`](data-provider-findings.md),
  [`hd06-due-diligence.md`](hd06-due-diligence.md)); **Intrinio Startup is recorded as the
  leading candidate at ≈\$5,994 year 1 and is explicitly not selected.** Eight evidence
  prerequisites remain, two of them blocking — most sharply that the candidate's
  history-depth claim is contradicted by its own upstream, and depth is the only ground on
  which it leads. [#21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band
  confirmation is required before any financial authorization.

**HD-06 is the only pending *HD-numbered* Product Owner decision — and that is not the same
as the only open question.** [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
§11.2 still escalates **OQ-U1…OQ-U7** to the Product Owner (ADRs/non-US listings; exactly
500 vs a buffer band; REITs; whether R9 point-in-time shares outstanding is opened and
whether spend attaches; backtest window depth; first-class universe disclosure on
user-facing surfaces; and the provisional 4UR4-minted `security_uid`). Those are open
Product Owner questions with stated defaults, not HD entries.

*(Correction history, kept because this exact sentence has been wrong twice on this branch:
the section once asserted HD-06 was "the only pending Product Owner decision" while HD-20
was open; it was then corrected to name HD-20 as pending. HD-20 is now **resolved** (below),
so HD-06 is again the only pending HD-numbered decision — but the OQ-U1…OQ-U7 escalations
above mean "only pending HD" and "only open question" are different claims, and only the
first is true. HD-16/17/18/19 and HD-21 were ruled on 2026-07-26 — see
[`human-decisions.md`](human-decisions.md).)*

*Resolved 2026-07-25 and no longer pending:* **HD-12**, **HD-13** and **HD-14** ratified, and
**HD-15** approved (the causal reference model is permitted under GOV-015 as Phase-0 evidence
tooling, conferring no Phase-2 credit) — one ruling, recorded as a citable artifact
[on #16](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012) against head
`2651cd0`. **GOV-015 itself remains ON.**

*Resolved 2026-07-26 and no longer pending:* **HD-16** (roadmap baseline approved),
**HD-17** (bounded delegation for reversible ambiguity — **superseded and widened by
HD-21**), **HD-18** (the self-computed **4UR4 US Large-Cap 500** universe), **HD-19**
(independence checker permitted as verification tooling), **HD-21** (bounded delegation —
below), and
**HD-20**, which was **not** resolved by the Product Owner but by the delegated decision
**SPR-D-01** under HD-21 — see the next section. **None of these lifts GOV-015, selects a
provider, or authorizes spend or licensing.**

## Delegated product decisions (HD-21) — a second decision channel

- **HD-21 — APPROVED (Product Owner, 2026-07-26,
  [#27](https://github.com/tomerYannay/4UR4/issues/27)).** The permanent **Strategic Product
  Reviewer** may decide **reversible product-definition questions** autonomously under **ten
  conjunctive conditions**, with a mandatory record format and the decision marked
  `DELEGATED_PRODUCT_DECISION_APPROVED`. It **supersedes and widens HD-17**. **Condition 10
  differs in kind:** the **Project Auditor** — read-only, and not the producer of the work —
  must independently confirm the delegation conditions were met, so every delegated decision
  carries **two** records: the decision, and an independent confirmation of authority.
  **Never delegated:** HD-06 purchase or spend, licensing, lifting or widening GOV-015,
  roadmap phase-order changes, core-thesis or target-customer changes,
  security/privacy/billing/PII, irreversible external actions, and **deletion of any
  important evidence or historical decision record** — nothing delegated permits removing a
  record, only adding to or superseding one. **HD-21 lifts nothing and makes HD-06 no more
  decidable than before.**
- **SPR-D-01 — RM-01 carries both analytical layers · resolves HD-20.**
  **Approved under bounded Product Owner delegation; not direct Product Owner authorship.**
  Decided by the Strategic Product Reviewer under HD-21 on the evidence of
  [#26](https://github.com/tomerYannay/4UR4/issues/26), and **CONFIRMED against all ten
  conditions by the Project Auditor at `5b99ba6`** *(Relayed, not independently
  authored — see the provenance note in [`human-decisions.md`](human-decisions.md) →
  SPR-D-01: role-level independence, not organizational, pending
  [#21](https://github.com/tomerYannay/4UR4/issues/21).)* (the first audit returned **NOT
  CONFIRMED** at `0b23f91`, because the decision existed only in a session transcript while
  the register still read `PENDING`). RM-01 now carries **two records, neither superseding
  the other**: **Half A**, the full-series geometry, retained **verbatim** and gated at
  **unit level** on an exported pure §8 function — explicitly **not** on pipeline output;
  and **Half B**, the as-of-time record (engine-derived stop at **bar 10**, `line_at_stop`
  `B* = (9, 158.40)`, `m = -0.0505453`, line `150.593`, close `164.19`, margin `0.0864461` *(raw clearance `ln(close) − ŷ`; the reference model's `events[].margin` field carries `0.0764461`, the same quantity net of `ε_break`)*),
  gated **within Phase-2-owned behaviour only** — asserting `line_at_stop`, **not** `Λ^F`,
  and **no** `BROKEN_OUT` state and **no** `BREAKOUT_CONFIRMED` reason code, which remain
  Phase 3's. **Half B narrows RM-01's Phase-2 assertable surface** to bars **0–9** plus the
  stop index, so *"the gate is strengthened"* is true of the gate as a whole and **false of
  RM-01**. Half B **is** replay-generated and therefore **model-derived**, so RM-01's non-circularity
  attaches to **Half A's human-approved geometry and the real prices**, not to Half B's
  provenance. The 2026-07-25 Product Owner approval, SC-1, SC-2/HD-11, `annotation.json`'s
  values and the **golden fixtures** are all unchanged; parameters stay at their ratified
  HD-14/D-TL-12 values. **No GOV-015 clearance is granted by it.** Gate wording:
  [`roadmap.md`](roadmap.md) Phase 2 exit criteria; evidence:
  [`fixtures/README.md`](fixtures/README.md) §6b.
- **Sequencing rule learned from SPR-D-01, binding on SPR-D-02 onward:** a delegated
  decision's status line reads `RESOLVED — pending condition-10 audit` until the Project
  Auditor confirms it, and only then is promoted.

## Open issues / PRs (governed index)
- **OPEN issues:** **#4**, **#5** (Phase 1 research) · **#6**, **#7** (impl, `blocked: freeze`) · **#10** (Agent Coordination Queue, permanent index) · **[#19](https://github.com/tomerYannay/4UR4/issues/19)** (roadmap exit-criteria gap — **blocks Phase 2 entry**; addressed on the current unmerged branch, pending review) · **[#20](https://github.com/tomerYannay/4UR4/issues/20)** (HD-15 condition 2 has no enforcement mechanism — **blocks Phase 2 entry**; document half addressed on the current unmerged branch, agent deny-configuration still owed) · **[#21](https://github.com/tomerYannay/4UR4/issues/21)** (review verdicts cannot become artifacts + single-account attribution — **required before HD-06 or any freeze lift**) · **[#22](https://github.com/tomerYannay/4UR4/issues/22)** (evidence-tooling follow-ups) · **[#23](https://github.com/tomerYannay/4UR4/issues/23)** (roadmap baseline approval, HD-16 — ruling artifact) · **[#24](https://github.com/tomerYannay/4UR4/issues/24)** (universe decision, HD-18 — ruling artifact) · **[#27](https://github.com/tomerYannay/4UR4/issues/27)** (HD-21 bounded delegation — the authority under which SPR-D-01 was taken).
- **CLOSED, retained here only because they are cited above:** **[#16](https://github.com/tomerYannay/4UR4/issues/16)** (Phase 0 evidence correction — delivered by the merged PR #18; **closed**, leaving the traceability debt recorded under Active work, not an open ticket) · **[#26](https://github.com/tomerYannay/4UR4/issues/26)** (RM-01 as-of-time divergence — the HD-20 evidence and options; **closed, resolved by SPR-D-01**). *(Both were previously listed as open in this index. The canonical current-state document must not assert open tickets that are closed.)*
- Open PRs: **#12** (Phase 1 research, draft, CI green, 0 reviews, awaiting strategic review). Coordination queue: [#10](https://github.com/tomerYannay/4UR4/issues/10).
- Recently merged: **[#18](https://github.com/tomerYannay/4UR4/pull/18)** — **MERGED as `e56ed8e`** (Phase 0 evidence correction + as-of-time fixture audit; the full review chain was re-run against every head, findings recorded in [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md); HD-12/13/14 ratified and HD-15 approved 2026-07-25). Issues **#19**–**#22** were opened after this merge.

## Sources
[`roadmap.md`](roadmap.md) · [`requirements.md`](requirements.md) · [`human-decisions.md`](human-decisions.md) ·
[`trendline-specification.md`](trendline-specification.md) · [`confidence-specification.md`](confidence-specification.md) ·
[`fixtures/README.md`](fixtures/README.md) · [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md) ·
[`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) ·
[`../docs/operations/agent-handoff-protocol.md`](../docs/operations/agent-handoff-protocol.md) ·
[`../GOVERNANCE.md`](../GOVERNANCE.md)
