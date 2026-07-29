# 4UR4 — Human Decision Register

Status: planning artifact under [GOV-015](../governance/build-freeze.md); these are
**proposals for the product owner, not decisions taken**.

> These are the material decisions that genuinely require the product owner
> ([GOV-013](../governance/approval-gate.md)). Each lists a recommended option, the
> reason, alternatives, the cost of delaying, and a safe default to hold until the
> owner decides. Agents must not self-approve these. Trivial/tunable choices
> (e.g. pivot `k`, tolerances, default weights) are intentionally **excluded** —
> they are per-ticket, versioned, and revisable within their workstream.

| ID | Materiality | Decision (short) | Status |
|----|-------------|------------------|--------|
| HD-01 | high | Price-adjustment basis | APPROVED |
| HD-02 | high | Envelope selection rule (upper log-hull) | APPROVED |
| HD-03 | high | Breakout confirmation policy | REVISED |
| HD-04 | high | Confidence presented as heuristic, not probability | APPROVED |
| HD-05 | high | ML success-label thresholds (triple-barrier) | REVISED |
| HD-06 | high | Data-provider selection + recurring cost | PENDING |
| HD-07 | high | Survivorship-bias-free constituents + delisted history | APPROVED (conditional) |
| HD-08 | high | Promoting sentiment into the confidence score | APPROVED |
| HD-09 | med  | External Fear & Greed source + redistribution/display rights | APPROVED |
| HD-10 | high | SaaS billing/PII security review | APPROVED |
| HD-11 | high | Pivot-high prefilter is non-authoritative (upper-log-hull is canonical) | APPROVED |
| HD-12 | high | Anchor selection is rolling/causal (as-of-time), frozen at confirmed breakout | **APPROVED — RATIFIED** |
| HD-13 | high | `eps_break` stays unlocked; ordinary fixtures must be tolerance-robust | **APPROVED — RATIFIED** |
| HD-14 | high | Formation gates are first-class `k`-independent parameters | **APPROVED — RATIFIED** |
| HD-15 | high | GOV-015 scope: a committed causal reference model is permitted evidence tooling | **APPROVED** |
| HD-16 | high | Roadmap baseline approved under GOV-013 | **APPROVED** |
| HD-17 | high | Bounded delegation to the Strategic Product Reviewer for reversible ambiguity | **APPROVED** |
| HD-18 | high | 4UR4 computes its own point-in-time universe (4UR4 US Large-Cap 500) | **APPROVED** |
| HD-19 | med  | Independence checker permitted as verification tooling | **APPROVED** |
| HD-20 | high | RM-01: as-of-time result diverges from the approved full-series record | **RESOLVED — SPR-D-01 (delegated)** |
| HD-21 | high | Bounded autonomous product-decision authority delegated to the Strategic Product Reviewer | **APPROVED** |
| HD-22 | high | GOV-015 scope lift — Phase 2 `engine/` only | **APPROVED** |
| HD-23 | high | Autonomous-execution directive: finish the permitted work; product delivery outranks governance polish | **PENDING PRODUCT OWNER CONFIRMATION** |
| HD-24 | high | Merge authorization for PR #38/#37, a **Phase-3** GOV-015 scope lift, and a ruling on #36 Part B | **APPROVED (relayed) — two overreaches recorded** |
| HD-25 | high | `FAILED_BREAKOUT` retains **both** exits — new-ATH reset and expiry (resolves ESC-4) | **APPROVED (relayed, no citable artifact)** |
| HD-28 | high | A phase whose exit criteria are met **as written** closes on the Product Steward's determination; no further approval | **APPROVED (relayed)** |

> **HD-26 and HD-27 are not missing.** They are recorded on the branch of [PR #44](https://github.com/tomerYannay/4UR4/pull/44) (the exploratory Alpha Vantage pilot and the HD-27 split-guard correction) and land in this register when that PR merges. The gap is a branch-ordering artifact, not a lost decision — noted because a reader of this file alone would otherwise have to guess.

---

## HD-01 — Price-adjustment basis · materiality: **high**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling:** Use **split-adjusted, dividend-UNadjusted** prices, consistently
  across all stages. The recommended option is accepted as the governing basis.
- **Decision:** Which price series feeds ATH selection, pivots, line fitting, and
  breakout tests?
- **Recommended option:** **Split-adjusted, dividend-UNadjusted ("as-traded")**,
  used consistently across all stages (trendline spec §2, D-TL-01).
- **Reason:** Matches the chart a trader actually sees, keeps the ATH stable, and
  avoids negative adjusted prices on long histories that would break `ln`.
- **Alternatives:** Fully adjusted (total-return) close; raw unadjusted (rejected —
  splits inject false ATHs/breakouts).
- **Cost of delaying:** Blocks Phase 1 (data) and Phase 2 (engine) — the adjustment
  basis changes *which bar is the ATH* and therefore every downstream signal.
- **Safe default:** Hold on split-adjusted/dividend-unadjusted; build fixtures
  against it. Reversible before Phase 1 implementation.

## HD-02 — Envelope selection rule · materiality: **high**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling:** The **upper log-hull from the ATH** is the canonical trendline
  selection rule. The recommended option is accepted as the governing definition.
- **Decision:** The canonical rule that selects the single second anchor `B*` and
  thus THE line.
- **Recommended option:** **Upper convex hull in log space from the ATH** — the
  shallowest descending log line that dominates all intervening highs within
  tolerance `ε` (trendline spec §8, D-TL-04).
- **Reason:** This is the load-bearing geometric *definition of the product*;
  resistance must sit above the highs it caps. The hull is deterministic and
  noise-tolerant.
- **Alternatives:** Naive "steepest line through two most significant pivots"
  (rejected — cuts through intervening highs).
- **Cost of delaying:** Blocks Phase 2 entirely; the engine cannot be built or
  fixture-tested without the confirmed definition.
- **Safe default:** Hold on upper-log-hull; encode discrimination fixture GX-02
  (must pick `B*=(45,92)`, not `(20,96)`).
- **Refinement (see [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high)):**
  the upper-log-hull rule stated here is canonical and does **not** depend on a
  fixed pivot-high prefilter. Pivot-high detection is secondary/non-authoritative
  and must never change the selected canonical anchor. HD-11 refines (does not
  supersede) this rule following real-market evidence from RM-01.

## HD-03 — Breakout confirmation policy · materiality: **high**
- **Status:** REVISED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling (governing definition):**
  - A **breakout candidate** is the **first daily close above the trendline**.
  - A confirmed breakout **alert MUST NOT require waiting for two daily bars**.
  - **Persistence** above the line is a **separate post-breakout quality feature**
    that feeds confidence, **not validity**.
  - **Volume** is a **confidence feature, not a hard validity gate**.
  - Do **not** permanently lock a fixed 1% threshold yet.
  - **Tolerance is versioned and backtestable**, with **percentage-based and
    ATR-based candidates evaluated in Phase 0/4**.
- **Superseded:** The prior recommended "close + 2-bar persistence + soft-volume"
  policy is **superseded** by the ruling above.
- **Decision:** What counts as a *confirmed* breakout.
- **Recommended option (superseded):** ~~**Close-based cross** (`ε_break=0.01`) **+
  persistence** (`p_break=2` bars) **+ soft volume** (`f_vol=1.0×` 20-bar avg; low
  volume flags `LOW_VOLUME`, does not void) (trendline spec §13, D-TL-07).~~
- **Reason:** Defines *when the product fires*; balances signal count against false
  positives while keeping correctness/explainability separate (volume softens
  score, not validity).
- **Alternatives:** Single-close breakout (more signals, more false positives);
  hard volume gate (fewer signals, discards borderline valid breaks).
- **Cost of delaying:** Blocks Phase 3 (breakout/retest engine).
- **Safe default:** Fire on the **first daily close above the line**; treat
  persistence and volume as confidence features; keep tolerance a versioned,
  backtestable parameter (%/ATR candidates) rather than a locked 1%.

## HD-04 — Confidence is a heuristic, not a probability · materiality: **high**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling:** Confidence v1 is a **0–100 heuristic quality score, never a
  probability**. The recommended option is accepted as governing.
- **Decision:** How the confidence score is *presented* in UI/API/copy.
- **Recommended option:** Present Confidence v1 as a **0–100 heuristic quality
  score**, `score_kind:"heuristic"`, with mandatory disclaimers; **never** labeled
  a probability, odds, or expected return (confidence spec §1, §8, D-CF-01).
- **Reason:** Mis-presenting a heuristic as a probability is a user-trust and
  compliance risk. Explainability integrity depends on honest framing.
- **Alternatives:** 0–1 scale or star tiers (cosmetic, allowed); presenting as
  "% chance" (rejected — prohibited).
- **Cost of delaying:** Blocks Phase 5 UI wording and Phase 6 dashboard copy;
  low cost to hold since the data-layer default is already `"heuristic"`.
- **Safe default:** Enforce `score_kind:"heuristic"` + disclaimers at the data
  layer regardless; owner confirms user-facing wording.

## HD-05 — ML success-label thresholds · materiality: **high**
- **Status:** REVISED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling (governing definition):**
  - Do **not** adopt +15%/−7%/60 bars as the **only** success definition.
  - Store **multiple** labels per breakout: forward horizons **5, 10, 20, 60 bars**;
    triple-barriers **+5%/−3%, +10%/−5%, +15%/−7%**; plus **MFE, MAE,
    failed-breakout, successful-retest**.
  - Keep **+15%/−7%/60 bars as an initial research label, not final product truth.**
- **Superseded:** The single-label recommendation below is replaced by the
  multi-label evaluation set above.
- **Decision:** How each historical breakout is labeled win/loss for future ML (v2)
  and for Confidence v1 rank-ordering validation.
- **Recommended option (superseded):** ~~**Triple-barrier, first-touch**: win if
  forward return reaches **+15%** before a **−7%** stop within **60 bars**, else
  loss (confidence spec §6, D-CF-04).~~
- **Reason:** Defines what "confidence" is eventually calibrated against; a wrong
  label yields a misleading future model. Path/drawdown-aware.
- **Alternatives:** Fixed-horizon return sign (simpler; ignores path/drawdown).
- **Cost of delaying:** Blocks Confidence-v1 lift validation (Phase 5) and Phase 8
  ML labels; delaying leaves the calibration target undefined.
- **Safe default:** Compute the **full multi-label set** for research/backtest only
  (never shown live); +15%/−7%/60 bars is the initial research label, not product
  truth.

## HD-06 — Data-provider selection + recurring cost · materiality: **high**
- **Status:** **PENDING** (unchanged) — with an **explicit authority boundary added
  2026-07-26**, see below.
- **Ruling:** No selection or spend yet. Complete the R1–R8 provider research and
  comparison matrix **before** any provider selection or commitment.

### Authority boundary — Product Owner, 2026-07-26

Ruled in the batch ruling of 2026-07-26
([artifact](https://github.com/tomerYannay/4UR4/issues/23), against head `45dfb91`).
**Agents are NOT authorized to:**

1. select a paid provider;
2. commit recurring or one-time spend;
3. accept commercial licensing terms;
4. publish or redistribute restricted provider data;
5. **represent an agent-composed decision as the Product Owner's financial
   authorization.**

**Permitted, and expected to continue:** evidence verification; provider comparison;
licensing and redistribution analysis; free-tier and trial feasibility; technical
interface requirements; point-in-time constituents research; delisted-history
research; shortlist criteria; a recommendation memo with ranked options; cost
scenarios; implementation planning; acceptance criteria.

**Agents may recommend one provider clearly** — but must not purchase, subscribe,
accept terms, or record HD-06 as approved.

### Leading candidate and evidence prerequisites — Product Owner, 2026-07-26

Ruled in the second batch of 2026-07-26
([artifact](https://github.com/tomerYannay/4UR4/issues/24)):

> **Intrinio Startup may be recorded as the current evidence-based leading candidate at
> approximately \$5,994 for year 1, but it is not selected or approved for purchase.**

**Recorded as a candidate, not a selection.** Research: [`data-provider-findings.md`](data-provider-findings.md)
§13. It is the only surveyed candidate clearing both hard filters — 50+ years of history
*and* a published display licence. Runner-up **Massive Stocks Business**; §13.5 states
what flips the ranking.

**Eight prerequisites must be obtained or prepared before the final HD-06 decision:**

| # | Prerequisite | Status at 2026-07-26 |
|---|---|---|
| 1 | Written confirmation that daily high/low are **consolidated-tape** | **BLOCKING (C-1)** — the one condition the Product Owner has already accepted; now a one-sentence question, see below |
| 2 | Exact historical-depth coverage | **BLOCKING — C-2 \[proposed\]** — the leading candidate's claim is contradicted by its own upstream |
| 3 | **Split-only** adjustment availability (HD-01) | raw OHLC + `split_ratio` exposed; `adj_*` bundles dividends and must be banned |
| 4 | Delisted-history coverage | partial — capped at 2007 for the leading candidate; see proposed **C-3** |
| 5 | Redistribution / display rights | published display licence; terms to be confirmed |
| 6 | **Point-in-time universe implications** | **new work** — created by HD-18; not evaluated by the original research |
| 7 | Complete first-year and recurring cost | ≈\$5,994 year 1; recurring to confirm |
| 8 | **Cancellation and data-retention constraints** | **new work** — Norgate and EODHD require deleting *derived* data on lapse, making an archive a rental; must now be asked of every candidate |

Prerequisites 6 and 8 are work the original research **did not do**: 6 exists only
because of [HD-18](#hd-18--4ur4-computes-its-own-point-in-time-universe--materiality-high),
and 8 was surfaced by a finding about other vendors that must now be put to the leading
one. Preparation: [`hd06-due-diligence.md`](hd06-due-diligence.md).

> **C-2, C-3 and C-5 are agent-*proposed*, not established.** Only **C-1** pre-existed.
> An agent may recommend a blocking condition; it may not impose one. The Product Owner
> may accept, modify or reject each. Recorded here so this register cannot be read as
> asserting gates nobody ruled.

**The due-diligence pass materially weakened the leading candidate.** Four findings from
[`hd06-due-diligence.md`](hd06-due-diligence.md), all from vendor documentation read
directly:

1. **The depth claim is contradicted by its own upstream.** Intrinio states history
   *"back to the 1960s"*; its documentation also states that raw historical EOD prices
   are **sourced from its data partner EDI**, and **EDI's own FAQ says its EOD prices
   begin 1 January 2007.** **Depth is the *only* ground on which Intrinio outranks
   Massive.** If EDI's date governs, the ranking does not merely narrow — it inverts.
   Proposed blocking condition **C-2** (agent-proposed; the Product Owner may accept, modify or reject it); one question (first-bar dates for ten named symbols)
   settles it.
2. **Delisted history likewise starts 2007**, which caps the survivorship-bias-free
   backtest window regardless of the ATH question. Proposed blocking condition **C-3** (agent-proposed).
3. **The consolidated-tape question (C-1) was aimed at the wrong party.** EDI sells both
   a per-exchange file and a **US Composite (CTA)** file. C-1 collapses to: *which file
   does Intrinio buy?*
4. **Retention: the runner-up requires deletion; the leader is silent.** Massive's ToS
   §11.4 requires deleting all information on termination. Both Intrinio terms pages
   were read in full and contain **no post-termination data clause at all** — and
   **silence is weaker than a written grant**, not stronger. Proposed blocking condition
   **C-5** (agent-proposed; express Order Form term).

Also recorded: on **point-in-time shares outstanding** — the input HD-18 newly requires —
Intrinio serves the SEC cover-page count with **no filing-date field or as-of parameter
documented**, and Massive keys on **period-of-report rather than acceptance date**, which
reads as a **look-ahead leak** of exactly the kind FR-22 forbids.

**Standing prohibition, restated:** do not purchase, subscribe, accept licensing terms,
or commit spend. **[#21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band
confirmation remains mandatory before financial authorization.**

> **Boundary 5 binds the relay channel itself.** Every artifact in this repository —
> including the rulings that authorize agent work — is authored by a single account,
> and this ruling arrived that way too, disclosed as a relay. Boundary 5 is
> [#21](https://github.com/tomerYannay/4UR4/issues/21)'s defect restated as a rule:
> an agent-composed comment on the owner's account must never stand as a financial
> commitment. #21 remains a **precondition for taking HD-06 at all**, and requires an
> out-of-band confirmation step before this decision can be made.
- **Decision:** Which market-data provider(s) to license, and approval of the
  recurring spend.
- **Recommended option:** **No recommendation — human-gated.** Agents produce the
  R1–R8 research and comparison matrix; the human selects and approves spend
  (data-provider research; architecture §9, [GOV-013](../governance/approval-gate.md)).
- **Reason:** Recurring cost and licensing are commercial commitments only a human
  may make; provider names are deliberately omitted to avoid steering.
- **Alternatives:** Bundle vs. best-of-breed across vendors (a decision the matrix
  informs).
- **Cost of delaying:** Blocks Phase 1 (data foundation) and everything downstream.
- **Safe default:** Continue research-only; **default MVP cadence is EOD/daily**.
  Commit nothing until the owner decides.

## HD-07 — Survivorship-bias-free constituents + delisted history · materiality: **high**
- **Status:** APPROVED (with condition) — **Decided by: Product Owner, 2026-07-24.**
- **Ruling:** Point-in-time constituents and delisted-history support are
  **correctness-critical** for trustworthy backtesting. The **need** is approved.
  **Purchase remains human-gated** — this approves the *need*, not any spend; the
  actual acquisition still requires a human's commercial approval.
- **Decision:** Whether to license point-in-time S&P 500 membership and delisted
  price history (frequently a paid dataset).
- **Recommended option:** **Acquire it (human-gated)** — treated as
  **correctness-critical**; without it, backtests are survivorship-biased (data
  research R4/R5).
- **Reason:** Backtests and regime/breadth stats are misleading without the actual
  historical members and delisted names.
- **Alternatives:** Use today's members projected backward (rejected — biased);
  defer accurate backtesting (limits trust in Confidence v1 lift).
- **Cost of delaying:** Blocks trustworthy Phase 4 backtesting and Phase 5/8
  calibration.
- **Safe default:** Research availability/cost now; hold the purchase for the owner;
  flag any Phase 4 backtest run without it as **biased/provisional**.

## HD-08 — Promoting sentiment into the confidence score · materiality: **high**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling:** Sentiment **stays out of the confidence score** until an out-of-sample
  backtest demonstrates improvement **AND** a human approves it. The recommended
  Sentiment-Before-Evidence block is accepted as governing.
- **Decision:** Whether/when Fear & Greed or the regime score may enter the
  **scored** confidence model.
- **Recommended option:** **Blocked** until BOTH (a) a backtest shows the feature
  improves calibration on out-of-sample data, AND (b) explicit human approval — the
  Sentiment-Before-Evidence rule (sentiment spec §7, [GOV-014](../governance/market-sentiment-context.md)).
- **Reason:** Protects correctness (no unproven input inflating trust) and
  explainability (every scored contribution must have evidence).
- **Alternatives:** Display sentiment as *context only* next to a signal (allowed
  after a human approves a display ticket + HD-09); wiring it into the score early
  (rejected — governance violation).
- **Cost of delaying:** None to the MVP — Confidence v1 is defined to exclude
  sentiment; this decision only gates Phase 8+.
- **Safe default:** Keep sentiment out of the score (enforced by the C1–C7 set and
  CF-EV-03 test); research only.

## HD-09 — External Fear & Greed source + redistribution/display rights · materiality: **med**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling:** **No third-party Fear & Greed index may be displayed or redistributed
  commercially until rights are verified.** **Prefer a proprietary 4UR4 sentiment
  score where practical.**
- **Decision:** Which sentiment source (if any) to use, and confirmation it permits
  commercial **display/redistribution** to end users.
- **Recommended option:** **Human-gated selection**; safest interim default is the
  **4UR4-reconstructed approximation** built only from inputs 4UR4 already has
  redistribution-safe rights to (sentiment spec §2.2/§3, data research R6/R7).
- **Reason:** Showing a third party's proprietary index to paying subscribers may
  need a display/redistribution license distinct from data access; "free to fetch"
  ≠ "free to resell/show." Highest legal-risk area.
- **Alternatives:** A licensed published composite (paid, redistribution-checked);
  a vendor API (licensing must be verified).
- **Cost of delaying:** None to MVP core; gates any user-facing sentiment display in
  Phase 7.
- **Safe default:** Research licensing (R6/R7) only; hold selection for the owner;
  do not display any third-party index until rights are confirmed.

## HD-10 — SaaS billing/PII security review · materiality: **high**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-24.**
- **Ruling:** Require a **formal security/privacy review before SaaS billing or
  customer PII**; use a **third-party payment processor** and **never store card
  details**. The recommended posture is accepted as governing.
- **Decision:** Approve the privacy/security posture before any customer or billing
  data is collected.
- **Recommended option:** **Require a formal privacy/security review** before Phase
  7 SaaS work: PII minimization, isolated billing behind a **third-party
  processor** (no card data held), least-privilege module access (architecture
  §6.2, §9).
- **Reason:** Collecting customer/billing data creates a compliance surface that
  must be reviewed by a human before exposure.
- **Alternatives:** Hold card data directly (rejected — unnecessary risk); defer
  review until after launch (rejected — exposure precedes review).
- **Cost of delaying:** None to Phases 0–6 (internal only); a hard gate on Phase 7.
- **Safe default:** Keep the MVP internal-only (no customer PII) until the review
  is done.

## HD-11 — Pivot-high prefilter is non-authoritative (upper-log-hull is canonical) · materiality: **high**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-25.** Resolves **SC-2**
  (raised by RM-01 real-market verification). Refines [HD-02](#hd-02--envelope-selection-rule--materiality-high).
- **Decision:** Whether the canonical upper-log-hull envelope anchor selection may
  depend on a fixed pivot-high (e.g. k=3) prefilter.
- **Ruling (governing rule):**
  1. Every valid later bar high may be a **second-anchor candidate** — after the ATH;
     high below the ATH; descending log-space slope; satisfies the canonical envelope
     rule plus tolerance.
  2. A bar **need not be a k-pivot high** to become the canonical upper-log-hull anchor.
  3. **Pivot-high detection is secondary and non-authoritative** — used only for
     visualization, descriptive metadata, confidence features, and lossless
     performance optimization.
  4. A pivot filter **must never change the selected canonical anchor**.
  5. Optimized implementations using pivot pruning **must fall back to / verify
     against the full all-highs upper-hull result**.
  6. RM-01 demonstrates why a strict k=3 precondition is invalid: **2026-07-21 @129.88**
     is not a k=3 pivot yet is the canonical shallowest descending envelope anchor;
     excluding it would contradict the approved upper-log-hull rule ([HD-02](#hd-02--envelope-selection-rule--materiality-high)).
- **Reason:** RM-01 real-world evidence shows the canonical anchor was a **non-pivot
  high**. A strict k=3 prefilter would wrongly exclude the shallowest descending
  envelope anchor and select a different (incorrect) line, contradicting the
  load-bearing product definition in HD-02. The all-highs upper-log-hull is the
  authority; pivots are a descriptive/optimization convenience only.
- **Alternatives:** Keep the strict pivot prefilter as a precondition for anchor
  candidacy (**REJECTED** — would contradict the approved upper-log-hull rule and the
  real RM-01 data by excluding a valid canonical anchor).
- **Cost of delaying:** n/a — resolved 2026-07-25.
- **Safe default:** All-highs upper-log-hull is canonical; treat any pivot filter as
  a non-authoritative optimization that must reproduce the full-hull result.
- **Cross-references:** refines [HD-02](#hd-02--envelope-selection-rule--materiality-high)
  (the envelope rule); real-market evidence in `product/fixtures/real/RM-01/`.

## HD-12 — Anchor selection is rolling and causal (as-of-time), frozen at confirmed breakout · materiality: **high**
- **Status:** **APPROVED and RATIFIED** — **Decided by: Product Owner, 2026-07-25**, and [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012) against head `2651cd0efffb7d48ec6e9929aed8fa3c4f22afcd`. Resolves **OQ-TL-7**
  (surfaced by [Issue #16](https://github.com/tomerYannay/4UR4/issues/16) /
  [PR #18](https://github.com/tomerYannay/4UR4/pull/18), the stale-pivot sweep, which
  explicitly did **not** decide it).
- **⚠ Provenance.** As with HD-13 and HD-14, this ruling originally reached the repository as a
  Product Owner instruction to the autonomous session rather than as a posted GitHub
  artifact, and until the ratification below the issue thread carried the escalation with no
  answer. **Ratification: DONE** — [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012). It mattered more
  here than anywhere else, because the entire 23-fixture correctness contract derives from
  this rule. Builds on
  [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high).
- **Decision:** Over what window is the canonical §8 anchor selection evaluated —
  full history (later bars may retroactively re-select `B*`), frozen at line
  formation, or rolling/as-of-time?
- **Ruling (governing rule):** **Anchor selection uses rolling, causal, as-of-time
  evaluation while the trendline is `ACTIVE`.** It is **neither** a final full-series
  calculation that may use future bars retroactively, **nor** a permanently frozen
  anchor from the first moment a valid line forms. Authoritative processing order for
  evaluation bar `t`:
  1. At the start of bar `t`, the active canonical line is calculated **only from bars
     available through `t−1`**.
  2. Evaluate bar `t`'s wick, close, breakout and related events **against that
     pre-existing line**.
  3. If bar `t` produces a **confirmed breakout**: **freeze** the exact `A`, `B*`,
     slope, intercept, tolerance version and line that were active at the **start of
     bar `t`**; use that frozen event line for breakout, retest, failure and expiry
     semantics; **later highs must not retroactively replace `B*` for that event**.
  4. If bar `t` does **not** produce a breakout: incorporate bar `t`'s high into the
     candidate set; recompute the all-highs upper-log-hull canonical `B*`; the
     resulting line becomes active **beginning with bar `t+1`**.
  5. A **new ATH** invalidates the previous structure and starts a new formation.
  6. **Pivot status and distance from the end of the currently available series remain
     non-authoritative.**
  7. **Backtests and fixtures must never use future bars to revise an earlier event
     classification.**
- **Reason:** Preserves causality and prevents look-ahead bias; allows a developing
  resistance line to update before breakout; freezes the actual line the market broke
  so subsequent retest semantics refer to the line that existed at the event; remains
  consistent with **RM-01** and
  [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high);
  and avoids reinstating a pivot-derived end-window exclusion.
- **Alternatives:**
  - **Full-series retroactive selection** — compute `B*` once over the complete
    history so a later, shallower, envelope-valid high re-selects the anchor of an
    already-evaluated event (**REJECTED** — introduces look-ahead bias and would let
    future bars rewrite an earlier breakout/retest classification).
  - **Permanently frozen at formation** — fix `B*` at the first moment a valid line
    forms, with later bars only validating (**REJECTED** — prevents a developing
    resistance line from legitimately updating before any breakout occurs).
- **Constraint that made the obvious alternative unavailable:** a "bars within `k` of
  the end of the series are excluded from **selection**" rule is **not** available:
  **RM-01's Product-Owner-approved canonical anchor is itself only 3 bars from the end
  of its series**, so reinstating such an end-window exclusion would contradict
  **RM-01** and
  [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high).
- **Cost of delaying:** n/a — resolved 2026-07-25. (While open it contested the stated
  anchors of fixtures **GX-09** and **GX-15** and blocked closure of the Phase 0
  evidence correction.)
- **Safe default:** Evaluate each bar against the line built from strictly prior bars;
  freeze the line at a confirmed breakout for all downstream event semantics; never
  revise an earlier classification with later bars.
- **Cross-references:** resolves **OQ-TL-7** in
  [`trendline-specification.md`](trendline-specification.md) (Open questions, §8/§17);
  surfaced by [Issue #16](https://github.com/tomerYannay/4UR4/issues/16) /
  [PR #18](https://github.com/tomerYannay/4UR4/pull/18); consistent with
  [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high)
  and the RM-01 real-market evidence in `product/fixtures/real/RM-01/`.

---

## Decision log — 2026-07-24 (Product Owner)

- **Approved as recommended:** HD-01 (split-adjusted, dividend-unadjusted prices),
  HD-02 (upper log-hull from the ATH), HD-04 (Confidence v1 heuristic 0–100, never a
  probability), HD-08 (sentiment out of the score until backtest + human approval),
  HD-09 (no third-party F&G display/redistribution until rights verified; prefer a
  proprietary 4UR4 sentiment score), HD-10 (formal security/privacy review before
  SaaS billing/PII; third-party processor, never store card data).
- **Approved with condition:** HD-07 — point-in-time constituents + delisted history
  are correctness-critical (the *need* is approved); **purchase remains human-gated**
  (no spend authorized).
- **Revised:** HD-03 — breakout candidate = **first daily close above the trendline**;
  **no 2-bar wait**; persistence and volume are **confidence features, not validity
  gates**; **no locked 1% threshold**; tolerance is **versioned/backtestable** with
  %/ATR candidates evaluated in Phase 0/4. Prior close+2-bar+soft-volume recommendation
  is superseded. HD-05 — adopt a **multi-label evaluation set** (horizons 5/10/20/60;
  barriers +5/−3, +10/−5, +15/−7; MFE/MAE/failed-breakout/successful-retest) instead
  of a single label; +15/−7/60 kept as the initial research label only.
- **Left pending:** HD-06 — data-provider selection + recurring spend; complete R1–R8
  research before any selection or commitment.

## HD-13 — `eps_break` stays unlocked; ordinary fixtures must be tolerance-robust · materiality: **high**
- **Status:** **APPROVED and RATIFIED** — **Decided by: Product Owner, 2026-07-25**, and [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012) against head `2651cd0efffb7d48ec6e9929aed8fa3c4f22afcd`.
- **⚠ Provenance — read before relying on this entry.** Surfaced as "Decision 1" by the
  causal fixture audit on [Issue #16](https://github.com/tomerYannay/4UR4/issues/16), whose
  escalation comment explicitly declined to choose. **The ruling was then issued by the
  Product Owner directly to the autonomous session as continuation instructions and was NOT
  posted to GitHub at the time, so for the whole of that period no citable decision artifact
  existed on the issue or the PR.** (One does now — see *Ratification* below.) This
  entry is the relay record, written by the agent that received and implemented the
  instruction. An earlier revision claimed the decision was "answered there" on Issue #16;
  that citation was **false** and is corrected here (found independently by the Project
  Auditor and the Strategic Product Reviewer, 2026-07-25). This is the same disclosure
  pattern as the *Historical Product Owner Decision Record — RM-01* below, and it falls short
  of the standard the Product Owner set on
  [#14](https://github.com/tomerYannay/4UR4/issues/14#issuecomment-5078902902) (*"the record
  must be a committed, citable artifact"*). **Ratification: DONE** — [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012), naming head
  `2651cd0efffb7d48ec6e9929aed8fa3c4f22afcd`. The gap this block discloses is closed; the
  block is retained because the record of how a decision reached the repository is itself
  evidence (GOV-006), and because the false "answered there" citation it retracts must stay
  retracted. Implemented in
  [PR #18](https://github.com/tomerYannay/4UR4/pull/18).
- **Decision:** Under [HD-12](#hd-12--anchor-selection-is-rolling-and-causal-as-of-time-frozen-at-confirmed-breakout--materiality-high)
  `ε_break` became **outcome-determining**: at least one fixture's expected
  classification flipped between `ACTIVE` and `BROKEN_OUT` depending on the value
  chosen, yet [HD-03](#hd-03--breakout-confirmation-policy--materiality-high)
  deliberately leaves `ε_break` **unlocked** (versioned and backtestable, no locked
  default). A fixture's expected outcome may not depend on a tolerance the
  specification declines to fix.
- **Ruling (governing rule):** **Keep `ε_break` unlocked (HD-03 stands, unamended) and
  remove the dependency from the evidence instead.**
  1. Every **ordinary** fixture's expected classification MUST be invariant under at
     least **±20% variation around the documented `ε_break` default**. Fixtures that
     were not are **redesigned**, not re-labelled.
  2. **Exactly one** fixture — **GX-15** — is retained as the dedicated
     **tolerance-boundary** fixture. Its classification is deliberately
     tolerance-sensitive and both sides of the boundary are documented numerically,
     including the exact value at which it flips.
  3. Ordinary fixtures MUST NOT be turned into tolerance-boundary tests as a
     side-effect of a redesign.
  4. A robust causal event is **preserved, not reverted**: where the as-of-time audit
     produces a breakout with a robust margin (**GX-19**, margin 0.0246129 log units),
     the fixture keeps that breakout rather than being restored to its full-series
     `ACTIVE` expectation.
- **Reason:** Locking `ε_break` now would pre-empt the Phase 0/Phase 4 evidence that
  HD-03 exists to gather, and would pin a validity threshold before the backtest that
  is meant to choose it. Accepting indeterminacy in the correctness contract is the
  other unacceptable option. Making the evidence robust removes the conflict without
  deciding the tolerance.
- **Alternatives:** (a) **Lock `ε_break`** at a specific value, amending HD-03 —
  **REJECTED** (pre-empts Phase 0/4 evidence). (c) Keep it unlocked and treat
  `ε_break`-boundary fixtures as **provisional**, excluded from the Phase 2
  exact-reproduction exit criteria — **REJECTED** (weakens the correctness contract
  exactly where it is load-bearing).
- **⚠ Where this ruling goes beyond the options as escalated.** Option (b) is the one
  approved, but the ruling as received **added specifics that appeared in no option**, and
  those specifics are load-bearing. They are listed rather than presented as a clean
  selection from the menu:
  1. the **±20%** invariance threshold — no numeric threshold appeared in any option;
  2. **GX-15** as the dedicated boundary fixture — option (b) had named **GX-01**;
  3. rule 3 (ordinary fixtures must not become boundary tests) and rule 4 (a robust causal
     event is preserved, not reverted) — neither appeared in any option.
  **Ratified as recorded, then retained in full.** [Ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012) *as recorded* — which includes these four clauses — with an invitation to correct any that was meant to be excepted. That invitation was **answered on 2026-07-26** ([artifact](https://github.com/tomerYannay/4UR4/issues/23)): *"Retain HD-13 in full … Do not strike any of these clauses."* **None was struck; the question is closed.**
- **Cost of delaying:** n/a — resolved 2026-07-25.
- **Safe default:** the documented illustrative `ε_break = 0.01` with
  `eps_break_locked: false` in every fixture, plus a recorded robustness sweep.
- **Evidence:** every fixture that ever forms a line carries
  `causal_record.eps_break_robustness` (the two input-guard-rejected fixtures, GX-10 and
  GX-18, never consult `eps_break` at all). Rule 1 is **machine-enforced**:
  `tools/fixture-replay.mjs --all` fails the run if any ordinary fixture's classification
  moves under ±20%, with GX-15 whitelisted as the fixture this decision exempts. Counted
  from the committed sweeps: **22 of 23 invariant at ±20%** — i.e. **all 22 ordinary
  fixtures comply**, GX-15 being the designed exception — and **21 of 23 across the wider
  0.5×–2× sweep**, the second exception being GX-12, which complies with this decision and
  leaves the band only at 0.5×.
  *(Correction, 2026-07-25: this clause previously read "22 of 23 … across a 0.5×–2× sweep;
  GX-15 is the intended boundary case", and a first correction over-stated it as 23 of 23 at
  ±20%. Both were wrong. The figures above are counted from the artifacts on disk. Three
  successive wrong values for one statistic is why the rule is now enforced by the harness
  rather than asserted in prose.)*
- **Cross-references:** [HD-03](#hd-03--breakout-confirmation-policy--materiality-high)
  (unamended), [HD-12](#hd-12--anchor-selection-is-rolling-and-causal-as-of-time-frozen-at-confirmed-breakout--materiality-high),
  `trendline-specification.md` §13.5.

## HD-14 — Formation gates are first-class, `k`-independent parameters · materiality: **high**
- **Status:** **APPROVED and RATIFIED** — **Decided by: Product Owner, 2026-07-25**, and [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012) against head `2651cd0efffb7d48ec6e9929aed8fa3c4f22afcd`.
- **⚠ Provenance — same limitation as HD-13 above.** Surfaced as "Decision 2" / **OQ-TL-8**
  by the §21 specification work on
  [Issue #16](https://github.com/tomerYannay/4UR4/issues/16). **The ruling was issued by the
  Product Owner directly to the autonomous session as continuation instructions and was not
  posted to GitHub at the time, so no citable decision artifact existed until the
  ratification below.** This entry is the relay record.
  Unlike HD-13, the substance here matches option (b) exactly as escalated — only the
  parameter names differ (`min_bars`/`min_bars_after_anchor` → `min_formation_bars`/
  `min_ath_age_bars`) and no threshold value changed. **Ratification: DONE** — [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012). Implemented in
  [PR #18](https://github.com/tomerYannay/4UR4/pull/18).
- **Decision:** Under HD-12 the §18 formation guards became **outcome-determining** —
  they fix `t_form`, the first bar at which any event can fire, and therefore which
  line the earliest evaluable bars are judged against. Both were expressed in the
  pivot window `k` (`2k+2` minimum history; ATH not within `k` of the last available
  bar), so `k` — declared **non-authoritative for selection** by
  [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high)
  — had become authoritative for formation **timing**.
- **Ruling (governing rule):** **Restate the formation gate as first-class,
  `k`-independent constants** (option (b)):
  - `min_formation_bars` — default **8** — minimum available history `|S_t|`;
  - `min_ath_age_bars` — default **3** — minimum age of the **anchor `A`** relative to
    the last available bar.
  Both are **named, versioned with the detector's `spec_version`, and backtestable**,
  are carried explicitly in every fixture's `params`, and are **numerically identical**
  to the superseded `2k+2` / `k` formulation at `k = 3` — **no threshold value
  changes**. Changing `k` MUST NOT move any event. `min_ath_age_bars` constrains the
  **anchor only**; it removes no candidate `B` from §6/§8 candidacy (HD-11, HD-12
  rule 6), so it does not reinstate the end-window exclusion that would contradict
  RM-01.
- **Reason:** A parameter that determines which events fire must not be a by-product of
  a parameter the same register declared non-authoritative. Naming the gates makes the
  formation timing explicitly tunable, versionable and backtestable, and lets the pivot
  window be re-tuned for visualization or confidence features without moving a single
  event.
- **Alternatives:** (a) keep the §18 guards expressed in `k` — **REJECTED** (leaves a
  non-authoritative parameter determining events); (c) relax the gates toward the
  two-bar geometric minimum — **REJECTED** (reinstates the degenerate two-point line
  the guards exist to prevent, which under causal evaluation manufactures a spurious
  `BROKEN_OUT` within a bar or two of the series start).
- **Cost of delaying:** n/a — resolved 2026-07-25.
- **Safe default:** `min_formation_bars = 8`, `min_ath_age_bars = 3` (the pre-existing
  values at `k = 3`).
- **Evidence:** regression fixtures **GX-21** (minimum history binds alone), **GX-22**
  (anchor recency binds alone, after a new-ATH reset) and **GX-23** (eligibility with zero
  confirmed pivots in the formation prefix), together with **GX-08** (a series containing no
  pivots at all still has a canonical anchor) and **GX-19** (the canonical `B*` is a
  non-pivot bar) — 9 of the 20 geometry fixtures have a non-pivot `B*`.
  `tools/fixture-replay.mjs --formation` re-checks the gates mechanically and adds a
  **positive control** so the checks cannot pass vacuously.
  *(Correction, 2026-07-25: this clause previously offered a `k ∈ {1,2,3,4,5,8}` replay
  sweep as proof. It is not proof — the reference model never reads `k`, so
  `k`-independence is **structural** there and the sweep is incapable of failing. The
  binding evidence is the fixture data above.)*
- **Cross-references:** `trendline-specification.md` §18, §21.3 and **D-TL-12**;
  resolves **OQ-TL-8**.

## HD-15 — GOV-015 scope: is `tools/fixture-replay.mjs` permitted under the build-freeze? · materiality: **high**
- **Status:** **APPROVED** — **Decided by: Product Owner, 2026-07-25** ([ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012), against head
  `2651cd0efffb7d48ec6e9929aed8fa3c4f22afcd`). Raised by the Project Auditor and the Strategic
  Product Reviewer, independently, during the review of
  [PR #18](https://github.com/tomerYannay/4UR4/pull/18).
- **Ruling:** `tools/fixture-replay.mjs` is **permitted under GOV-015 as Phase-0 evidence
  tooling** — the recommended option below. Recorded in
  [`governance/build-freeze.md`](../governance/build-freeze.md) so the ruling lives in the
  governance file rather than only in the artifact it licenses. **GOV-015 itself remains ON:**
  this is a scope clarification about one file, not a freeze lift, and it authorizes no
  product code.
- **Conditions carried with the permission** (the recommended option's own terms, implemented
  as the detail of the ruling rather than separately quoted): it confers **no Phase-2 credit**;
  the Phase-2 engine MUST be authored from the specification by an agent that has **not read
  this model**, so that "exact reproduction" tests conformance rather than transcription; and
  the **specification governs** wherever the two disagree, with any divergence handled as a
  spec-defect report or a model bug, never as silent model behaviour.
- **Decision:** [PR #18](https://github.com/tomerYannay/4UR4/pull/18) commits
  `tools/fixture-replay.mjs`, a roughly thousand-line executable causal reference model implementing
  §3, §4, §6, §7, §8, §9, §10, §11, §13, §14, §15, §16, §17, §18 and §21 of the trendline
  specification, and CI now depends on it. Is that **permitted evidence tooling** under
  [GOV-015](../governance/build-freeze.md), or is it **product functionality** implemented
  under a freeze?
- **Why it is genuinely contested, stated from both sides:**
  - *For permitting:* the alternative is hand arithmetic, which **demonstrably drifted, repeatedly**
    — the whole pre-#16 fixture set was derived with full-series hulls, and the replacement
    GX-20 was designed with full-series reasoning and shipped defective. A correctness
    contract nobody can mechanically re-derive is the larger Phase-2 hazard. The file creates
    none of the `PRODUCT_CODE_DIRS` the validator guards, is wired to no product surface, and
    the freeze validator passes.
  - *Against:* GOV-015 rule 2's permitted list is **closed** ("this operating system,
    governance, workflows, templates, and **context-only** research/design") and an executing
    implementation of the detection algorithm is not obviously on it; rule 3 says the
    Architect "may **design** but not build". The validator's check is **directory-name-based**
    and does not reach file contents, so passing it is not clearance — it is a gap in the
    enforcement, not a ruling.
- **Recommended option:** **permit as Phase-0 evidence tooling**, recording the conditions
  explicitly in `governance/build-freeze.md`: it confers no Phase-2 credit; the Phase-2 engine
  MUST be authored from the specification by an agent that has not read it, so that "exact
  reproduction" tests conformance rather than transcription; and the specification remains
  authoritative wherever the two disagree.
- **Alternatives:** (a) permit but bar CI from depending on it — keeps the freeze tighter, but
  removes the continuous enforcement the review chain specifically demanded; (b) require its
  removal before merge — returns Phase 0 to the hand derivation that failed repeatedly.
- **Cost of delaying:** n/a — resolved 2026-07-25.
- **Safe default (superseded by the ruling):** the freeze stays **ON** — which remains true;
  the ruling is a scope clarification about one file, not a freeze lift.
- **Note on the disclaimers in the tree (history).** `tools/fixture-replay.mjs`,
  `fixtures/README.md` §7 and `fixtures/VERIFICATION.md` each state that the file is evidence
  tooling and confers no Phase-2 credit. Before this ruling those statements were the
  **proposed** disposition and were labelled as proposals in each file, because an artifact
  may not settle a question reserved to the Product Owner in its own header — the Project
  Auditor's finding. They are now labelled as **ruled**, citing this decision.

## Decision log — 2026-07-25 (Product Owner)

- **2026-07-25 — HD-11 approved (resolves SC-2 from RM-01):** upper-log-hull canonical,
  pivot prefilter non-authoritative.
- **2026-07-25 — [HD-12](#hd-12--anchor-selection-is-rolling-and-causal-as-of-time-frozen-at-confirmed-breakout--materiality-high)
  approved (resolves OQ-TL-7, surfaced by [Issue #16](https://github.com/tomerYannay/4UR4/issues/16) /
  [PR #18](https://github.com/tomerYannay/4UR4/pull/18)):** anchor selection is **rolling,
  causal, as-of-time** while the line is `ACTIVE` — bar `t` is evaluated against the line
  built from bars through `t−1`; a confirmed breakout **freezes** that line (`A`, `B*`,
  slope, intercept, tolerance version) for breakout/retest/failure/expiry semantics; with
  no breakout, bar `t`'s high joins the candidate set and the recomputed line becomes
  active from `t+1`; a new ATH starts a new formation. Neither full-series retroactive
  selection nor permanent freeze-at-formation. Pivot status and distance from the end of
  the series remain non-authoritative, and no end-window (`within k of the end`) exclusion
  is reinstated — **RM-01's approved anchor is only 3 bars from the end of its series**, so
  such an exclusion would contradict RM-01 and
  [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high).
  Backtests and fixtures must never use future bars to revise an earlier event
  classification. See [`trendline-specification.md`](trendline-specification.md).
  **Relayed, then ratified:** this ruling reached the repository as a direct Product Owner
  instruction; it now also carries a posted artifact — [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012).

- **2026-07-25 — [HD-13](#hd-13--eps_break-stays-unlocked-ordinary-fixtures-must-be-tolerance-robust--materiality-high)
  approved:** `ε_break` **stays unlocked** (HD-03 unamended); instead, every **ordinary**
  fixture's expected classification must be invariant under **±20%** variation around the
  documented default, **GX-15** alone is retained as the dedicated tolerance-boundary
  fixture with both sides documented, ordinary fixtures must not become boundary tests,
  and a robust causal breakout (**GX-19**, margin 0.0246129) is **preserved rather than
  reverted**.
  **Relayed, then ratified:** this ruling reached the repository as a direct Product Owner
  instruction; it now also carries a posted artifact — [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012).

- **2026-07-25 — [HD-14](#hd-14--formation-gates-are-first-class-k-independent-parameters--materiality-high)
  approved (resolves OQ-TL-8):** the formation gate is restated as **first-class,
  `k`-independent** parameters `min_formation_bars = 8` and `min_ath_age_bars = 3` —
  **numerically identical** to the superseded `2k+2` / `k` formulation at `k = 3`, but
  versioned with `spec_version`, backtestable, and carried in every fixture's `params`.
  Changing the pivot window `k` may no longer move any event. Locked by **GX-21**,
  **GX-22**, **GX-23** and by `tools/fixture-replay.mjs --formation`.
  **Relayed, then ratified:** this ruling reached the repository as a direct Product Owner
  instruction; it now also carries a posted artifact — [ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012).

- **2026-07-25 — HD-12, HD-13 and HD-14 RATIFIED, and HD-15 approved** ([ratified 2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012), against head
  `2651cd0efffb7d48ec6e9929aed8fa3c4f22afcd`): *"Ratify HD-12, HD-13 and HD-14; permit the
  reference model under GOV-015."* The three relayed rulings now carry the citable artifact
  their entries disclosed as missing, HD-13 ratified **as recorded** including the four clauses
  its entry enumerates as going beyond the escalated options. `tools/fixture-replay.mjs` is
  permitted under GOV-015 as Phase-0 evidence tooling, conferring no Phase-2 credit;
  **GOV-015 remains ON.**
- **2026-07-25 — Historical Product Owner Decision Record — RM-01** (*recorded here, not
  newly decided*): PR #9 merged the RM-01 verification without a citable GitHub decision
  artifact (0 comments, 0 reviews), so this bullet supplies the missing precedence-1
  (Product-Owner-decision) record. Decision content: **RM-01 approved**; **SC-1 resolved as
  `MATCH`**; **SC-2 resolved by
  [HD-11](#hd-11--pivot-high-prefilter-is-non-authoritative-upper-log-hull-is-canonical--materiality-high)**;
  the **canonical upper-log-hull rule is retained**; the **pivot prefilter is
  non-authoritative**. Decision made by the Product Owner on 2026-07-25. This record only
  documents the existing decision and does not create or self-approve a new Product Owner
  decision. The same decision is already carried by
  [`fixtures/real/RM-01/annotation.json`](fixtures/real/RM-01/annotation.json)
  (`product_owner_approval: approved`),
  [`fixtures/real/RM-01/README.md`](fixtures/real/RM-01/README.md) and
  [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md).

## HD-16 — Roadmap baseline approved under GOV-013 · materiality: **high**

- **Status:** **APPROVED** — **Decided by: Product Owner, 2026-07-26**
  ([artifact](https://github.com/tomerYannay/4UR4/issues/23), against head `45dfb91`).
- **Decision:** The current Phase 0–9 roadmap baseline in
  [`roadmap.md`](roadmap.md) is approved. It is no longer PROPOSED.
- **Consequence:** [#4](https://github.com/tomerYannay/4UR4/issues/4) and
  [#5](https://github.com/tomerYannay/4UR4/issues/5) may become **Ready**, and Phase 1
  **research** may proceed.
- **What this approval explicitly does NOT do** (the Product Owner's own four
  exclusions): it does **not** lift GOV-015; does **not** authorize product
  implementation; does **not** select a provider; does **not** authorize spend or
  licensing.
- **Reason it needed a human:** GOV-013 reserves roadmap approval to the Product
  Owner, and until now `roadmap.md` opened with *"PROPOSED, pending human approval"*,
  which made every Phase 1 ticket un-Ready by its own Definition of Ready.
- **Standing risk:** an approved roadmap invites the reading that building may begin.
  It may not. `build_freeze: ON`, `autonomous_implementation: DISABLED` *(as of HD-16; the
  marker now reads `ENABLED_FOR_SCOPE` with `scope: ["engine/"]` under HD-22 — the freeze
  stays ON everywhere else)*, and Phase 2
  entry additionally requires [#19](https://github.com/tomerYannay/4UR4/issues/19),
  [#20](https://github.com/tomerYannay/4UR4/issues/20) and a per-scope freeze lift.

## HD-17 — Bounded delegation for reversible ambiguity · materiality: **high**

- **Status:** **APPROVED** — **Decided by: Product Owner, 2026-07-26**
  ([artifact](https://github.com/tomerYannay/4UR4/issues/23)).
- **Decision:** For a *new ambiguity*, the **Strategic Product Reviewer** may select
  the safest reversible option — but only when **all six** conditions hold: no spend
  or licensing commitment; no product-definition change; no roadmap phase-order
  change; GOV-015 remains ON; no privacy, security, billing or PII impact; and the
  decision is documented with rationale and is reversible.
- **Hard limit:** it **must not claim Product Owner authority** when exercising this
  delegation. Every exercise is recorded as a *delegated* call with its rationale, so
  this register keeps delegated choices distinguishable from ruled ones. A delegated
  call is reversible by construction and creates no precedent.
- **Reason:** the alternative was stopping the session on questions that cost nothing
  to get wrong and can be undone. The six conditions are conjunctive precisely so the
  delegation cannot creep into the classes that are expensive or irreversible.

## Decision log — 2026-07-26 (Product Owner)

- **2026-07-26 — Batch ruling** ([artifact](https://github.com/tomerYannay/4UR4/issues/23),
  against head `45dfb91`). Six parts: the roadmap baseline approved under GOV-013
  (**HD-16**); the two phase-gate questions ruled; **HD-13 retained in full** with none
  of its four clauses struck; **HD-15 conditions 1–3 retained**; an explicit **authority
  boundary** added to the still-**PENDING** HD-06; and a **bounded delegation** to the
  Strategic Product Reviewer (**HD-17**). **GOV-015 remains ON throughout** — the ruling
  says so three separate times.

- **2026-07-26 — Phase-gate placements ruled.** **RM-01 is part of the Phase 2 exit
  gate** as the committed real-market, non-circular conformance fixture. **Wick-break
  belongs to Phase 2** *"because it is evaluated while the structure remains ACTIVE and
  does not itself perform an `ACTIVE → BROKEN_OUT` state transition"*; **Phase 3 remains
  responsible for confirmed breakout, retest, failure and expiry.** This resolves both
  `PENDING (human)` rows recorded in `45dfb91` — and supplies a **better rationale than
  the one proposed**: the roadmap had justified wick-break's placement by the
  `confirmed_bar` partition, a mechanical property of current fixture data that would
  evaporate if a future fixture gave GX-03 a breakout. The ruling's behavioural reason
  survives that change; the roadmap now leads with it.

- **2026-07-26 — HD-13 retained in full.** `eps_break` stays unlocked, versioned and
  backtestable; ordinary fixtures must be robust under **±20%** around the documented
  default; **GX-15** is the dedicated tolerance-boundary fixture; non-boundary fixtures
  must not depend on threshold coincidence. *"Do not strike any of these clauses."*
  This closes the invitation HD-13's own entry recorded — that its four beyond-the-menu
  clauses could be struck if a bare ratification had been intended. It was not.

- **2026-07-26 — HD-15 conditions 1–3 retained, and condition 2 sharpened into
  something testable.** The reference model *"remains verification-only and is not
  product implementation."* The Phase 2 implementation *"must remain independently
  authored and must not import, copy, execute or mechanically translate the reference
  model,"* and **#20 must define an enforceable independence mechanism before Phase 2
  implementation begins.** This is a material improvement on the original wording:
  *"authored by an agent that has not read this model"* is a claim about a session's
  history and therefore unverifiable after the fact, whereas *"must not import, copy,
  execute or mechanically translate"* is **a property of the artifact**, checkable
  against the code that exists. Both are kept — the artifact property as the testable
  criterion, the read-restriction as the preventive control.

- **2026-07-26 — HD-06 remains PENDING, with an explicit authority boundary.** See the
  [HD-06](#hd-06--data-provider-selection--recurring-cost--materiality-high) entry.
  Phase 1 research continues in full; provider *selection*, spend, licensing acceptance
  and redistribution do not. Agents may **recommend one provider clearly** and must not
  purchase, subscribe, accept terms, or record HD-06 as approved.

## HD-18 — 4UR4 computes its own point-in-time universe · materiality: **high**

- **Status:** **APPROVED** — **Decided by: Product Owner, 2026-07-26**
  ([artifact](https://github.com/tomerYannay/4UR4/issues/24), against head `83b0fcc`).
- **Decision:** 4UR4 uses a **self-computed, point-in-time universe of the 500 largest
  eligible US-listed operating companies** rather than licensed S&P 500 constituent
  membership. Working product name: **4UR4 US Large-Cap 500**.
- **Binding requirements:**
  1. **Do not call it the S&P 500**, and **do not imply endorsement by or equivalence
     to S&P Dow Jones Indices.**
  2. Transparent, **versioned** eligibility and ranking rules.
  3. **Point-in-time membership history preserved**; **delisted securities preserved**;
     survivorship bias avoided.
  4. Additions and removals recorded with **effective dates and evidence**.
  5. Inclusion, liquidity, security-type, domicile and rebalance rules **independently
     versioned and backtestable**.
- **Delegation:** the Strategic Product Reviewer may choose the safest reversible
  **initial research defaults**; **material changes to the intended market segment
  remain Product Owner-gated** (see [HD-17](#hd-17--bounded-delegation-for-reversible-ambiguity--materiality-high)).
- **Reason:** licensed index membership was an **unpriced, unbounded exposure**.
  [`survivorship-bias-findings.md`](survivorship-bias-findings.md) established that
  membership is licensed **separately from prices and far more restrictively** — an
  executed S&P Master Index License Agreement on SEC EDGAR contracts constituent data
  under a separate MSA with separate fees — and that SPDJI **withdrew constituent names
  from Compustat in 2020** to license directly. The two best survivorship-free datasets,
  Norgate and CRSP, are both **licence-barred** from commercial use. A self-computed
  universe converts a dependency that could be withdrawn or repriced unilaterally into a
  methodology the project owns.
- **Cost of the decision, stated rather than discovered later.** A mechanical rule
  **cannot reproduce S&P 500 membership**: the index committee applies discretion —
  profitability screens, float, sector balance, judgement. Three consequences follow:
  1. **Backtest results will not be comparable to published S&P 500 strategy results.**
     A licensing feature and an interpretation liability at once; it must be disclosed
     wherever results are reported.
  2. **Eligibility rules become product surface.** "Operating company" (excluding ETFs,
     closed-end funds, SPACs, trusts, shells), the domicile-vs-listing question, and
     **share-class handling for dual-class names** each materially change a top-500
     ranking. Each is a rule someone must own, version and re-derive.
  3. **Reconstruction is the hard part.** Point-in-time membership needs point-in-time
     market cap, which needs point-in-time **shares outstanding** — a harder dataset to
     source than prices, and one the provider research **did not evaluate, because the
     question did not exist when it ran**.
- **Design:** [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md).
- **What this did NOT do:** it did not lift GOV-015, select a provider, or authorize
  spend.

## HD-19 — Independence checker permitted as verification tooling · materiality: **med**

- **Status:** **APPROVED** — **Decided by: Product Owner, 2026-07-26**
  ([artifact](https://github.com/tomerYannay/4UR4/issues/24)).
- **Decision:** the independence checker proposed under
  [#20](https://github.com/tomerYannay/4UR4/issues/20) is **permitted under GOV-015 as
  verification/governance tooling**, on the same footing as
  [HD-15](#hd-15--gov-015-scope-is-toolsfixture-replaymjs-permitted-under-the-build-freeze--materiality-high),
  subject to six boundaries:
  1. **not product implementation**;
  2. **not imported or executed by production/runtime code**;
  3. **no provider or market-data acquisition**;
  4. **deterministic and auditable**;
  5. it **validates process independence rather than pretending to prove what an agent
     privately read**;
  6. it **must fail honestly when independence cannot be established.**
- **Why 5 and 6 are the substantive ones.** Boundary 5 ratifies the design's own
  conclusion in [`../docs/architecture/phase2-independence-mechanism.md`](../docs/architecture/phase2-independence-mechanism.md):
  what an agent read is not provable after the fact, and a checker claiming otherwise
  would be theatre. Boundary 6 forbids this repository's most persistent failure mode —
  a gate that cannot fail and therefore certifies nothing. Both were reached
  independently by the design and the ruling.
- **Delegation:** for the **remaining #20 escalations**, the Strategic Product Reviewer
  may choose the safest reversible option where it does **not** change product
  behaviour, lift GOV-015, incur spend, accept licensing, or weaken separation of
  duties.
- **Not a freeze lift.** `build_freeze` stays `ON`. Like HD-15, this covers specific
  tooling for a specific purpose and is **not a precedent** for committing executable
  product functionality under the freeze.

## HD-20 — RM-01: as-of-time result diverges from the approved full-series record · materiality: **high**

- **Status:** **RESOLVED — by delegated decision [SPR-D-01](#spr-d-01--rm-01-carries-both-analytical-layers--delegated_product_decision_approved)**, not by
  direct Product Owner authorship. Decided by the **Strategic Product Reviewer** under the
  [HD-21](#hd-21--bounded-autonomous-product-decision-authority--materiality-high)
  delegation, 2026-07-26.
  **Artifacts:** [issue #26](https://github.com/tomerYannay/4UR4/issues/26) (evidence and
  options), [issue #27](https://github.com/tomerYannay/4UR4/issues/27) (the delegation).
  Raised 2026-07-26 at head `d22f434`.
- **Decision required:** on RM-01, the approved **full-series** record and the ratified
  **as-of-time** rule ([HD-12](#hd-12--anchor-selection-is-rolling-and-causal-as-of-time-frozen-at-confirmed-breakout--materiality-high) / §21)
  disagree about whether a breakout occurred. **Both are arithmetically correct about
  different objects.** Which is the product's answer, and what does RM-01 assert in the
  Phase 2 exit gate?
- **The facts, not in dispute.** The approved line (`B* = (25, 129.88)`, slope
  `−0.0240143`) is never closed above — true. Under §21, the line judging bar 10 is built
  only from bars 0–9, binds `B* = (9, 158.40)` after bar 9's wick-break re-selection, and
  sits at **150.593**; the close of **164.19** clears it by **0.0864461** log units (≈9%).
  Re-derived by **five separate agent sessions** — Phase 2 planner, orchestrating session,
  Strategic Product Reviewer, Verification and Code Review — agreeing to six significant
  figures. *Stated precisely, because the stronger verb would be false: three of the
  five — the Phase 2 planner, the orchestrating session and the Strategic Product
  Reviewer — are **correlated re-runs of the same arithmetic over the same committed
  CSV**, not independent instruments. **Two are not:** **Verification** and **Code
  Review** each wrote their **own replay from the specification text, with no reference
  to the repository's harness**, and agreed to six significant figures. It is those
  two, not the count of five, that establish the numbers are not an artifact of a
  single model.*
  *(`0.0864461` is the raw clearance `ln(close) − ŷ`. The reference model's own
  `events[].margin` field carries `0.0764461`, the same quantity net of `ε_break`; both
  are correct about different things, and an unqualified "margin" has two readings.)*
- **Tolerance cannot suppress it — but one documented parameter can.** Suppression by
  tolerance would require `ε_break ≥ 0.0864461`, **≈8.6×** the documented `0.01`, and
  HD-13 forbids resolving fixture outcomes by tolerance in any case. `ε` is irrelevant.
  **However — `min_formation_bars ≥ 12` removes the breakout entirely** (8–10 → bar 10,
  margin `0.0864461`; 11 → bar 11, margin `0.0660743`; **12–20 → none**). That parameter
  is already first-class, named, versioned and backtestable under D-TL-12 / HD-14, so
  **option (3) below is a *parameter* change, not a new rule** — materially cheaper than
  first presented. It remains a setting fitted to a single 29-bar sample, which is the
  argument against it. *(An earlier revision of this entry said "delaying formation
  enlarges the margin" — false; it inverted §21.4, since shallower means higher and the
  margin therefore shrinks. The Product Owner was corrected on the artifact.)*
- **Why it was escalated rather than treated as a documentation fix.** *(Historical — the
  framing as it stood while HD-20 was open. It was resolved under **delegation** by
  SPR-D-01, not by direct Product Owner ruling; the underlying product question this
  bullet identifies remains genuinely Product-Owner-owned and is deliberately left open
  as a Phase 4 backtest question.)* The causal line at
  bar 10 sits **below the entire recent trading range** — a steep two-point fit over a
  6-bar window after an IPO spike. §21.3's own derivation names that as precisely the
  failure the formation gates exist to prevent. **On the only real data in the
  repository, the gates did not prevent it; they moved it from bar 3 to bar 10.** So this
  is first real-data evidence that the ratified rule, at ratified gate values, emits a
  signal the Product Owner did not call a breakout when looking at the same chart.
  Whether that is a true positive to ship or a false positive to suppress is a
  product-definition question (GOV-013).
- **Options:** (1) both, split — keep the §8 geometry assertion *and* gate on the
  as-of-time expectation; (2) geometry only for now, as-of-time recorded but non-gating;
  (3) call bar 10 a false positive and change the rule, re-deriving RM-01 and all 23
  golden fixtures; (4) declare RM-01 out of scope for as-of-time evaluation. Costs for
  each are stated on the artifact. The review chain **recommends option 1** — a
  recommendation, not a decision.
- **Scope of the ruling:** it must resolve **both** the roadmap's gate clause **and**
  what RM-01's committed `annotation.json` carries. The suspension applied so far is
  honest only because those are separable; the ruling should not be read as touching only
  the roadmap.
- **Applied pending the ruling — disclosure and suspension only, deciding nothing:**
  [`fixtures/README.md`](fixtures/README.md) §6b, `fixtures/VERIFICATION.md`'s RM-01
  header notice, `fixtures/real/RM-01/README.md`'s header notice, and the roadmap's RM-01
  **numeric acceptance values** marked `UNDER REVIEW`. **RM-01 remains in the Phase 2 exit
  gate**; the Product Owner's ruling placing it there is untouched.
- **Cost of delaying:** Phase 2 implementation cannot start — its own plan blocks on this
  at S0, correctly.
- **Systemic finding recorded alongside it:** **no mechanical guard has ever covered
  RM-01.** `check-evidence.mjs` only schema-validates its annotation and
  `fixture-replay.mjs` never reads `real/`. That is why this survived the 2026-07-25
  causal audit — a gap in the evidence system, not a one-off.
  *(**As recorded on 2026-07-26, and since closed.** `expected-causal.json`,
  `real-causal.schema.json` and the `real/`-reading extension to both evidence tools now
  place RM-01 under mechanical causal replay in CI. Marked rather than rewritten: this is
  the finding as it stood, and it is what the closure answers.)*

## HD-22 — GOV-015 scope lift, Phase 2 `engine/` only · materiality: **high**

- **Status:** **APPROVED** — Product Owner, 2026-07-26,
  [#31](https://github.com/tomerYannay/4UR4/issues/31).
- **Decision:** [GOV-015](../governance/build-freeze.md) is lifted **for Phase 2 work under
  `engine/` and nothing else**. The freeze remains **ON** everywhere else.

**Authorized:** the deterministic trendline-engine implementation · fixture and RM-01
conformance tests · engine-local test infrastructure · minimal shared types strictly
required by the engine.

**Not authorized, and still frozen:** provider integration · live market-data ingestion ·
API, database, scanner, worker, dashboard, alerts or SaaS work · spend, licensing, privacy,
billing or external deployment.

**Binding requirements on the engine**, as ruled: (1) **independently authored** from the
fixture reference model; (2) **must not import, execute or mechanically translate** that
model; (3) passes **all 23 golden fixtures and RM-01 causal replay**; (4) preserves
**HD-11 through HD-20**; (5) **deterministic and free of look-ahead bias**.

**The scope is machine-enforced, not declaratory.** `governance/build-freeze.md`'s marker
carries `scope: ["engine/"]`, `tools/validate.mjs` guards `engine` alongside every other
product-code directory, and a guarded directory passes **only** when the marker names it.
Removing the scope entry re-freezes `engine/` on the next CI run. Verified in a sandbox
across all three cases: `engine/` in scope passes; `src/` fails; `engine/` with the scope
removed fails.

**Requirements 1 and 2 are governed by E2-AUTHOR** ([#20](https://github.com/tomerYannay/4UR4/issues/20)).
**E2-AUTHOR-A governs at the gate** — the committed `engine/` must not import, copy, execute
or mechanically translate `tools/fixture-replay.mjs` or any successor model under `tools/`.
**Agreement with the reference model earns no credit** (HD-15 condition 1): the engine is
proven against the **fixtures**, never against the model.

**Fixture-immutability condition — provenance stated precisely, on the HD-15 pattern.** The
Product Owner's ruling enumerates **five** binding requirements and this is **not** among
them. It was **proposed by the requesting session** in the #31 request as a self-binding
condition, and the ruling granted the request that contained it — so it is adopted as **detail
of the permission**, not as separately quoted Product Owner words. It **narrows** agent
authority rather than expanding it. **If a bare five-condition permission was intended, strike
this and say so.** Until then it binds:
**No fixture, `expected.json`, `annotation.json`, or parameter may be edited to make
the engine pass.** If the engine and a committed fixture disagree, that is **escalated, never
reconciled**. This is the strongest single control on the Phase 2 work: fitting the object to
the gate is precisely the failure the whole fixture corpus exists to catch, and it is the one
control that cannot be recovered after the fact — a fixture edited to accommodate an engine
looks identical to a fixture that was always right. It is a **Phase-2 ticket acceptance
criterion**, not advice.

**What this does not do.** It does not touch **HD-06** — no provider is selected and no spend
is authorized. It does not resolve **M-09** (the `real/**` quarantine classification), which
*(as recorded on 2026-07-26, and since closed)* remained open and had to be ruled before the
Phase 2 ticket met its Definition of Ready — **M-09 is now CLOSED by
[SPR-D-03](#spr-d-03--productfixturesreal-is-r2b-permeable-by-necessity--delegated_product_decision_approved),
condition-10 CONFIRMED.** Marked rather than rewritten, per this register's convention. It
grants no Phase-2 credit for existing evidence tooling.

**Related condition, recorded because events overtook it.**
[#21](https://github.com/tomerYannay/4UR4/issues/21) states that an out-of-band confirmation
is *"required before HD-06 or any GOV-015 freeze lift"*. **This lift proceeded without that
mechanism existing**, on a Product Owner ruling relayed under the same single-account channel
#21 describes. That is disclosed rather than treated as satisfied: the condition stands for
**HD-06**, which remains PENDING, and #21 remains open.

**Also required by the same ruling:** full branch protection on `main` — PR-only merges,
required CI, required exact-head reviews, no direct pushes, no force pushes, no branch
deletion, no routine administrative bypass — **before Phase 2 product code merges**.
**Read this together with the part 3 deviation immediately below: one of the seven is UNMET,
and stopping at this paragraph gives an unqualified precondition that is not the current state.**

### HD-22 part 3 — DEVIATION RECORDED, ruled by the Product Owner 2026-07-26

**Six of the seven parts are in force. The seventh — "required exact-head reviews" — is
UNMET, and it is unmet by structural impossibility rather than by omission.**

*"Full branch protection is in place" is not an available statement about this repository.*

| # | Part | State | Evidence |
|---|------|-------|----------|
| 1 | PR-only merges | **MET** | proven directly by the **empirical push rejection** in part 4. *(This row previously cited the `required_pull_request_reviews` block alone. That block IS "require a pull request before merging" and does enforce part 1's subject; what it does not enforce at count 0 is any **review**, so it is not evidence about reviews. An earlier correction here overshot and called it evidence that "enforces nothing" — false in the direction that matters for this row.)* |
| 2 | required CI | **MET** | context `Validate agent OS & governance`, `strict: true` — the single job that runs the validator, the hook suite, the fixture re-derivation, the evidence checker and the 136-test engine conformance suite |
| 3 | **required exact-head reviews** | **UNMET** | `required_approving_review_count: 0` |
| 4 | no direct pushes | **MET** | proven empirically: a direct push was rejected, `protected branch hook declined` |
| 5 | no force pushes | **MET** | `allow_force_pushes: false` |
| 6 | no branch deletion | **MET** | `allow_deletions: false` |
| 7 | no routine admin bypass | **MET** | `enforce_admins: true` |

**Measured** against `gh api repos/tomerYannay/4UR4/branches/main/protection` on **2026-07-26**,
with `main` at `ed92bbb`, and independently re-verified row-by-row by the Verification and Code
Review gates at that head. None of these values is re-derivable from the working tree, so the
measurement point is recorded with them.

**Why part 3 cannot be satisfied by raising the number.** GitHub forbids a pull-request
author from approving their own pull request. This repository has **one identity** — the
Product Owner and every agent share `tomerYannay` — so every PR is authored by that identity
and **no approving review can ever exist**. Setting the count to `1` would not tighten the
gate; it would make `main` **permanently unmergeable**, and the predictable response is to
switch `enforce_admins` off, trading a real protection for a theatrical one. **The constraint
is [#21](https://github.com/tomerYannay/4UR4/issues/21) and
[#34](https://github.com/tomerYannay/4UR4/issues/34), not the setting.** At count `0`,
`dismiss_stale_reviews: true` is **inert** — there is no review to dismiss — so part 3 is
**unimplemented, not partially met**. Do not read the two settings together as partial
compliance.

**The two gates split on this, and both were right about what they were looking at.** The
Project Auditor ruled it non-blocking: the load-bearing protections for engine code are in
place, and the defect is already ticketed. The Strategic Product Reviewer ruled it blocking:
HD-22 states it as a precondition on Phase 2 product code merging, and a precondition that
is quietly reinterpreted is not a precondition. **The Product Owner resolved it on
2026-07-26: NOT BLOCKING, deviation to be recorded rather than closed.**

**What the compensating controls do and do not cover.** Parts 1, 2, 4–7 mean no change
reaches `main` without a PR whose required check ran the full gate at that head — **subject to
one limit that must be stated in a section whose whole subject is that one identity holds every
role.** `enforce_admins: true` prevents *bypassing* protection; it does **not** prevent
*reconfiguring* it. The single identity that authors, reviews and merges is also the repository
admin, so the settings can be relaxed, a merge taken, and the settings restored — leaving **no
in-repo artifact and no gate**. Part 7's "no routine administrative bypass" carries some of this
weight but not that. Recorded on the Project Auditor's finding.

What they do **not** cover is the residual part 3 exists for: *that a party independent of the author
looked at the exact head that merges.* Today that residual is carried by the agent review
chain, whose verdicts are same-account relays with no citable artifact. **That is genuinely
weaker, and it is not described here as equivalent.** It is why #21 stays open.

**Closing this deviation requires a second identity** — a GitHub App or machine account —
after which `required_approving_review_count: 1` becomes **settable**. It does **not** thereby
become *meaningful*: a machine account operated by the same principal restores the **artifact**,
not the **independence**, and that is precisely the theatrical control this section refuses
above for `enforce_admins`. An earlier draft said "settable and meaningful", which
over-promised and, worse, set the bar for closing this deviation too low. **The honest closure
condition is a second identity under separate control, or an equivalent that makes the approving
party genuinely distinct from the authoring one.** Until then this row stands as the honest
state.

*(Placement note: this paragraph belongs to **HD-22 part 3** — "this row" is part 3's table
row. An earlier edit inserted the GOV-005 heading immediately above it, which silently
reparented it under GOV-005 and left both of its back-references dangling across a section
boundary: part 3 lost its stated closure condition and GOV-005 acquired one that is not about
it. Caught by the Verification gate. Restored here.)*

### Related deviation — GOV-005 "merged by Release & Ops only" (recorded 2026-07-26)

Recorded **here** rather than only in [`project-state.md`](project-state.md), whose own header
says *"current state only — not a history log"* — a routine refresh can sweep it, and a
deviation that evaporates is not recorded. Flagged by the Project Auditor.

PRs [#32](https://github.com/tomerYannay/4UR4/pull/32) (`758c0a0`) and
[#33](https://github.com/tomerYannay/4UR4/pull/33) (`ed92bbb`) were **merged by the Product
Owner personally through the GitHub UI**, not by Release & Ops.
[GOV-005](../governance/definition-of-done.md) says *"Merged by **Release & Ops** only"*, with
no agent qualifier in the clause itself. **This register does not reinterpret it as scoping only
agents** — that reading was drafted and withdrawn, because it is exactly the "quietly
reinterpreted precondition" this section objects to elsewhere. It is a **deviation**, recorded
for the Auditor and for the Product Owner to dispose of.

Why it happened: the Release & Ops gate **refused both merges**, and its refusals were correct
each time — no channel existed in which a human authorization could be expressed
([#34](https://github.com/tomerYannay/4UR4/issues/34)). Under a single shared identity the
Product Owner performing the merge is the *only* act that carries attribution, because it is not
a claim about a human, it is a human. **Provenance:** the API confirms
`mergedBy.login = tomerYannay` for both, which is all it can confirm; that this was the Product
Owner rather than an agent rests on the Product Owner's own statement.

## HD-21 — Bounded autonomous product-decision authority · materiality: **high**

- **Status:** **APPROVED** — **Decided by: Product Owner, 2026-07-26**
  ([artifact](https://github.com/tomerYannay/4UR4/issues/27), against head `6af5261`).
- **Decision:** the permanent **Strategic Product Reviewer** may decide **reversible
  product-definition questions** autonomously, so the project is not blocked on the
  Product Owner for ambiguities that cost nothing to get wrong and can be undone.
- **Supersedes and widens [HD-17](#hd-17--bounded-delegation-for-reversible-ambiguity--materiality-high).**
  HD-17 permitted the safest reversible option on a *new ambiguity* under six conditions.
  This grants authority to **decide product-definition questions** under ten, with a
  mandatory record format and an independent audit. Where the two differ, **this governs**.
- **All ten conditions must hold:** (1) no purchase, subscription, recurring spend or
  financial commitment; (2) no acceptance of licensing, redistribution, trademark or
  commercial terms; (3) **GOV-015 remains ON** and no implementation permission is
  expanded; (4) no privacy, security, billing, PII, authentication or legal exposure;
  (5) reversible through a later specification revision; (6) no material change to the
  target customer, core product thesis or roadmap phase order; (7) at least one option
  clearly has lower look-ahead bias, lower false-evidence risk, stronger causal
  correctness or better testability; (8) justifiable from approved product goals,
  existing human decisions, real-market evidence and reproducible analysis; (9) the
  decision **and its alternatives** recorded transparently; (10) **the Project Auditor
  confirms the delegation conditions were satisfied.**
- **Condition 10 is what makes the other nine safe, and it differs in kind.** Conditions
  1–9 are self-assessed by the deciding agent. Condition 10 requires the **Project
  Auditor** — read-only, and not the producer of the work — to confirm the decision was
  the decider's to make. Without it an agent would certify its own eligibility to decide,
  which is the failure mode this repository has spent its whole history removing. Every
  delegated decision therefore carries **two** records: the decision, and an independent
  confirmation of authority.
- **Required record:** decision · rationale · rejected alternatives · evidence ·
  reversibility · risks · affected fixtures/specifications · what would trigger
  reconsideration. Assigned a decision ID, marked
  `DELEGATED_PRODUCT_DECISION_APPROVED`, and stating explicitly *"Approved under bounded
  Product Owner delegation; not direct Product Owner authorship."*
- **Tie-break order** when options remain defensible: (1) no look-ahead bias; (2) causal
  real-time correctness; (3) mechanically verifiable evidence; (4) reversible
  implementation; (5) lower false-confidence risk; (6) **preserve information rather than
  discard it**; (7) **defer economic interpretation to backtesting rather than fit a rule
  to one example.**
  > **Tie-breaks 6 and 7 are the substantive ones**, and they were written knowing what
  > they would bite. 7 forbids the cheapest wrong answer to HD-20 — raising
  > `min_formation_bars` to 12 so one 29-bar sample behaves, which the corrected evidence
  > shows would work. 6 forbids resolving an ambiguity by dropping a valid analytical
  > layer. Tie-break 1 outranks all of them, and matters because the HD-20 options are
  > not symmetric: the as-of-time result is the causal one and the full-series record is,
  > by construction, look-ahead.
- **Never delegated — Product-Owner-only:** HD-06 provider purchase or spend; licensing
  acceptance or redistribution rights; paid data contracts; lifting or widening GOV-015;
  roadmap phase-order changes; changing the core product thesis or target customer;
  security/privacy/billing/PII; irreversible external actions; public claims carrying
  legal or financial exposure; and **deletion of important evidence or historical
  decision records** — nothing delegated permits removing a record, only adding to or
  superseding one.
- **HD-20 specifically** is delegated, to be decided from the evidence on
  [#26](https://github.com/tomerYannay/4UR4/issues/26), and returns to the Product Owner
  only if the chosen resolution would introduce a new commercial threshold, change the
  core product thesis, require spend or licensing, or lift GOV-015.
- **What this does not do:** it does not lift GOV-015 (condition 3 restates it), authorize
  spend, or make **HD-06** decidable. HD-06 remains **PENDING** and Product-Owner-only,
  with [#21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band confirmation
  still mandatory before any financial authorization.

## Decision log — 2026-07-26 (Product Owner, second batch)

- **2026-07-26 — [HD-18](#hd-18--4ur4-computes-its-own-point-in-time-universe--materiality-high)
  approved** ([artifact](https://github.com/tomerYannay/4UR4/issues/24)): 4UR4 computes
  its own point-in-time **4UR4 US Large-Cap 500** universe instead of licensing S&P 500
  membership. This is a **product-definition change** and the largest single decision on
  this branch — it removes an unbounded licensing exposure at the cost of comparability
  with published S&P 500 results, and it makes the eligibility rules product surface.
  Requirements, roadmap, glossary, research documents, acceptance criteria and issue
  wording updated consistently.

- **2026-07-26 — HD-06 unchanged in status, advanced in evidence.** **Intrinio Startup
  is recorded as the current evidence-based leading candidate at approximately \$5,994
  for year 1** — *"but it is not selected or approved for purchase."* Eight
  prerequisites must be obtained or prepared before the final decision; see the
  [HD-06](#hd-06--data-provider-selection--recurring-cost--materiality-high) entry.
  **[#21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band confirmation
  remains mandatory before financial authorization** — this ruling names a number and
  simultaneously refuses to be the authority for spending it, which is the correct
  posture on a single-account relay channel.

- **2026-07-26 — [HD-19](#hd-19--independence-checker-permitted-as-verification-tooling--materiality-med)
  approved:** the #20 independence checker is permitted as verification/governance
  tooling under six boundaries, and the remaining #20 escalations fall to the Strategic
  Product Reviewer's bounded delegation.

*This register records the Product Owner's rulings of 2026-07-24, 2026-07-25 and
2026-07-26 (two batches). Ruled items are governing; **HD-06 remains a proposal pending
human decision** ([GOV-013](../governance/approval-gate.md)), now with an explicit
authority boundary, eight evidence prerequisites, and
[#21](https://github.com/tomerYannay/4UR4/issues/21) as a precondition. The build-freeze
([GOV-015](../governance/build-freeze.md)) **remains ON**; neither the roadmap baseline
approval (HD-16), the universe decision (HD-18), nor the tooling permission (HD-19)
changes that.*

## HD-23 — Autonomous-execution directive · materiality: **high**

- **Status:** **PENDING PRODUCT OWNER CONFIRMATION.** Recorded as **relayed**, not as ruled.
- **Relayed:** 2026-07-28, by the Product Owner **to the Orchestrator**, which relayed it
  onward to the working agents.
- **Artifact:** **NONE.** There is **no citable external artifact** — no issue comment, no PR
  review, no commit trailer. This entry is the only record, and it is a record of a relay
  through the Orchestrator under the **single shared identity**
  [#21](https://github.com/tomerYannay/4UR4/issues/21) /
  [#34](https://github.com/tomerYannay/4UR4/issues/34) describe. **It is not dressed as a
  ruling with an artifact link it does not have.**
- **Scope of that last claim, corrected against the file.** An earlier form of this entry said
  *"every other HD in this register above HD-23 cites an artifact"*. **That is false, and was
  measured false at this head:** **HD-01–HD-05 and HD-07–HD-11 — ten entries — cite no
  artifact and do not use the word.** They predate the practice, and no blanket ratification
  reaches them: the [#16](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012)
  ratification covers **HD-12/13/14/15 only**. The register concedes the pattern in its own
  2026-07-25 decision log — *"this ruling reached the repository as a direct Product Owner
  instruction; it now also carries a posted artifact"*. **What is true is narrower, and is
  enough:** every HD from **HD-12 onward** carries a citable artifact in its own text, and
  **HD-23 is the only one of those that does not**; where HD-12/13/14 recorded the lack as
  *pending* and the #16 ratification then supplied it, HD-23 has no ratification in prospect,
  because the relay ran through the single shared identity. **The disposition below does not
  rest on the discarded wording** — it rests on the absence itself, which is why the wording
  is corrected rather than defended.

**Operative terms, as relayed.**

1. **Finish the remaining permitted work autonomously** — do not stop to ask about matters
   already inside an approved scope.
2. **Product delivery outranks governance polish** where the two compete for the same session.
3. **Log non-blocking defects and continue.** The [maintenance
   backlog](maintenance-backlog.md) is the destination.
4. **Fix immediately — do not defer — when a defect** changes product behaviour · invalidates
   evidence · creates look-ahead bias · weakens security or merge integrity · **causes tests to
   pass vacuously** · or blocks the current milestone.
5. **Human-only stops, unchanged:** spend · licensing · privacy, security, billing or PII
   approval · irreversible external action · material change to the core thesis or the target
   customer · roadmap phase-order change · **a new or widened [GOV-015](../governance/build-freeze.md)
   scope.**
6. It stated that **"GOV-015 is lifted only for the already approved Phase 2 engine scope"**
   and that **"HD-06 remains PENDING"**. Both are **consistent with this register** — HD-22's
   lift is `scope: ["engine/"]` and HD-06 is PENDING — so neither sentence changes anything;
   they are recorded because a directive that restates existing limits is evidence about its
   own intended breadth.

**Its delegation language is broader in SHAPE than HD-21's, and the difference is recorded
rather than smoothed.** HD-21 delegates **reversible product-definition questions** under ten
conditions with a mandatory record format and an independent Project Auditor confirmation.
HD-23 additionally directs the resolution of **"technical ambiguities"** — a category
[HD-21](#hd-21--bounded-autonomous-product-decision-authority--materiality-high) **does not
name**, and one whose natural reading reaches engineering judgement rather than product
definition. Three observations, none of which resolve it:

- Read narrowly, "technical ambiguities" adds nothing: engineering judgement inside an
  approved ticket was never Product-Owner-gated.
- Read broadly, it would let an agent settle questions that are product-definitional in
  substance and merely technical in appearance — the class HD-21 deliberately fenced with its
  ten conditions and condition-10 audit.
- **Nothing in this session relied on the broad reading**, so the ambiguity did not have to be
  resolved and was not. It is recorded here so that a later session cannot cite HD-23 as a
  widening of HD-21 without a human first saying which reading was meant.

**Two places this directive was read too broadly, and corrected. Both corrections stand.**

- **(a) It did NOT authorize an agent merge.** *"Merge through the strongest currently
  available safe path"* was read by the Orchestrator as authorizing an **agent** merge of PR
  [#35](https://github.com/tomerYannay/4UR4/pull/35). **Release & Ops refused, under
  [GOV-013](../governance/approval-gate.md) clause 4, and was right.** The strongest currently
  available safe path **is the Product Owner's own merge** — the path actually used for PR #32
  and PR #33 — and **a weaker path is not the strongest.** The sentence is a *ranking
  instruction*; reading it as a *permission* inverts it. GOV-013 clause 4 is unaffected by
  HD-23 and continues to require a human approval naming the PR and its head.
- **(b) It did NOT rule on E2-AUTHOR criterion 5.** *"Shared GitHub identity must not block
  product progress"* was considered as a possible disposition of E2-AUTHOR criterion 5 and
  found **insufficient**: a general instruction about a class of obstacle is **not a
  disposition of the specific artifact** that #20 **AC-8** names. AC-8 offers exactly two
  routes — resolve #21, or rule the §9 stopgap acceptable — and a sentence that does neither
  selects neither. Criterion 5 therefore **remains open**; see
  [`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md)
  §9 and [#36](https://github.com/tomerYannay/4UR4/issues/36) Part B.

**Dependency check — deliberate.** **No determination made this session depends on HD-23.**
The attestation, the HD-23 record itself, the ticket-set repairs and the maintenance rows are
all document work inside already-permitted scope, and each would stand unchanged if the
Product Owner declined to confirm this directive. If HD-23 is **not** confirmed, nothing
recorded on this branch is invalidated; only the *autonomy* the working sessions exercised
would lose its stated basis, and that basis was never load-bearing for any product or
governance conclusion.

**What this does not do.** It does not lift or widen GOV-015 (its own term 5 forbids that).
It does not make **HD-06** decidable. It does not supersede HD-21 or HD-17. It does not create
an artifact where #21 says none can exist. It is **not** a merge authorization
(GOV-013 clause 4).

## HD-24 — PR #38/#37 merge authorization · Phase-3 GOV-015 scope lift · #36 Part B · materiality: **high**

- **Status:** **APPROVED** as a Product Owner decision — **relayed**, with **two places where
  the decision asserts more than its own evidence supports, recorded below rather than
  smoothed.**
- **Decided by:** Product Owner, **2026-07-28**.
- **Artifact:** [issue #39](https://github.com/tomerYannay/4UR4/issues/39). Unlike
  [HD-23](#hd-23--autonomous-execution-directive--materiality-high), this decision **has** a
  citable artifact; HD-24's own closing line directs that it be recorded here as **HD-24**,
  which is what this entry does. **That closing line has a second half — a directive to widen
  the freeze marker's `scope` — which is NOT executed**, and is quoted with its reasons under
  *"HD-24's closing recording directive"* below.
- **⚠ Provenance, as HD-24 discloses it about itself.** It was **relayed in session under the
  single shared identity**, and **written up by the Orchestrator, which is an interested
  party** in the merges §2 authorizes. It is therefore **citable but not independently
  attributable**: no artifact under one identity distinguishes a relayed Product Owner
  decision from one the relaying agent composed.
  [#21](https://github.com/tomerYannay/4UR4/issues/21) and
  [#34](https://github.com/tomerYannay/4UR4/issues/34) **remain open**, and HD-24 does not
  close either.
- **⚠ Provenance of *this record*, on the HD-13 pattern.** This entry was written by the
  Product Steward from the decision as **relayed to the recording session**, corroborated
  against the three gate relays and the PR #38 body, each of which quotes HD-24 §2 by
  section. **The recording agent did not read the issue body itself.** Where this entry and
  [#39](https://github.com/tomerYannay/4UR4/issues/39) disagree, **the issue governs.**
- **⚠ What this entry transcribes — narrowed and corrected 2026-07-28, because the first form
  of the claim was too wide.** It said: *"Only **§2, §3 and §4** — the parts this record
  propagates — are transcribed here; the remaining sections are not."* That reads as **§2, §3
  and §4 entire**, and they were not: **§2's #35 and #37 rows**, **§3's ruling on HD-22
  requirement 3**, **§4's Phase-2-exit authorization**, and **the freeze-marker half of #39's
  closing recording line** were all absent. A disclaimer covering §1, §5 and §6 licenses
  nothing about the three sections this entry says it *does* transcribe. All four omissions
  are repaired below, and the claim is now stated by part rather than by section number.
  **Transcribed here:** §2's three-row authorization table and its gate-relay provision · §3's
  enumerated grant, its still-frozen list, its rule-4 assertion and its HD-22-requirement-3
  ruling · §4's #36 Part B ruling and its Phase-2-exit authorization · **#39's closing
  recording line**, which sits outside all three sections and is transcribed with the half of
  it that was **declined**. **Not transcribed:** §1, §5, §6, and anything within §2/§3/§4 not
  named in that list — their absence is **not** a statement about their content.
- **⚠ Provenance of the newly transcribed passages.** They were **relayed verbatim by the Code
  Review gate**, which read [#39](https://github.com/tomerYannay/4UR4/issues/39) and confirmed
  each against the issue body and against the working tree. **The recording agent still has not
  read #39's body**, so these quotations inherit the same relay weakness as the rest of this
  entry: they are citable, not independently attributable. Where they and the issue disagree,
  **the issue governs.**

### §2 — merge authorization and the gate-relay provision

**Recorded as it operated, not as it was first written.** §2's authorization table has
**three** rows, each carrying **its own** condition and its own authorized head. All three are
transcribed here, because collapsing them loses exactly the distinction the last row was
written to make:

| PR | Head authorized, in §2's own wording | Condition, verbatim |
|---|---|---|
| [#35](https://github.com/tomerYannay/4UR4/pull/35) | `6482a5db7f66dc1a8c0bd44d4ade39718f0a8ef0` | *"Both gates already green at this head"* |
| [#38](https://github.com/tomerYannay/4UR4/pull/38) | `207e91a4c315ffa01475a9b79ccb69dd18657502` | *"Merge **after** #35; gates required first"* |
| [#37](https://github.com/tomerYannay/4UR4/pull/37) | *"**new SHA after R1**"* — no fixed SHA is named | *"Only **after** the R1 correction and a **re-run of both gates at the new head**"* |

**Corrected 2026-07-28, with the superseded sentence quoted.** This paragraph read: *"§2
authorizes PR #38 and PR #37 by number, on the condition 'Merge after #35; gates required
first.'"* That condition is **#38's row alone**. **#37's row carries a different condition** —
the one the re-anchoring immediately below actually relies on — and **#35's row was omitted
entirely**, which is how a three-row authorization came to be narrated as a one-condition one.
Found by Code Review.

§2 states that **the gates themselves are NOT waived**; what it
waives is the requirement that the Product Owner personally approve or perform each merge. It
also permits the **Orchestrator to relay** a gate verdict where `ROLE_POLICY` blocks the `GH`
category for the gate role, requiring each relay to state on its face that it is one — which
*"does not repair the attribution weakness; it makes the verdict citable"*, a strictly weaker
property.

**The head it named is void, and the authorization was re-anchored.** §2's table named
`207e91a`. PR #38's head then moved four times under §2's own condition — merge-forward onto
`main`, then three rounds of gate-driven correction — and the authorization was re-anchored to
`586a34e091591b69b35b596b01c4e848cc68e846`
([artifact](https://github.com/tomerYannay/4UR4/issues/39#issuecomment-5101982897)), on the
ground that §2's own #37 row already contemplates a new SHA produced by a gate correction. All
three gates were re-run and posted at that exact head, every prior head-specific verdict
explicitly discarded. **The re-anchoring comment is itself Orchestrator-authored and inherits
HD-24's attribution weakness rather than curing it** — it says so on its face. PR #38 merged
at `586a34e` as `0b564a41dc77c07ade797632cf78bb5183e91825`, post-merge CI green.

### §3 — the Phase-3 GOV-015 scope lift

**Granted, and enumerated.** §3 lifts [GOV-015](../governance/build-freeze.md) for **Phase 3
work inside `engine/`**: the **`ACTIVE → BROKEN_OUT` transition**, **line freezing** (`Λ^F`,
§21.5), **retest** (§16), **failed breakout** (§15), and **expiry/recompute** (§17). Still
frozen, per §3's own list: **provider integration · live ingestion · `api` · `db` · `scanner`
· `worker` · `dashboard` · `alerts` · `billing` · `providers` · SaaS surfaces · spend ·
licensing · privacy/billing · external deployment.** **E2-AUTHOR continues to bind the whole
engine.** Propagated to [`../governance/build-freeze.md`](../governance/build-freeze.md).

**§3 also RULES on HD-22 requirement 3, and the first form of this entry omitted the ruling
entirely.** Verbatim, as relayed by Code Review:

> **"HD-22 requirement 3 is hereby read as reading (i)** — it was **Phase-2-scoped** and is
> satisfied by the engine merged at `ed92bbb`. **No governance finding against `ed92bbb`
> arises.** Phase 3's own gate is the roadmap's Phase 3 exit criteria: every fixture
> reproduced in full."

**What it decides, and why leaving it out mattered.** [HD-22](#hd-22--gov-015-scope-lift-phase-2-engine-only--materiality-high)'s
binding requirement 3 on the engine is *"passes **all 23 golden fixtures and RM-01 causal
replay**"*. Read as a demand that the committed engine reproduce every fixture **in full**, the
Phase-2 engine does not meet it and never could: it stops at the §13.1 predicate and implements
no Phase-3 behaviour by design. That reading would put the engine **already merged at
`ed92bbb`** in breach of the very lift that authorized it. **§3 forecloses that**: requirement 3
was Phase-2-scoped, it is satisfied, and **no governance finding against `ed92bbb` arises** —
while the full-reproduction reading is relocated to where it belongs, the roadmap's **Phase 3
exit criteria**. This is a ruling **about a commit already on `main`**, which is why its
omission was the most consequential of the four: an entry that records the lift but not the
ruling leaves a live, unanswered breach question against `main`.

**It answers [#36](https://github.com/tomerYannay/4UR4/issues/36) Part A's second question.**
Part A asked the Product Owner to *"state which you intended"* between two labelled readings of
requirement 3; §3 answers **reading (i)**. **The labels are #36's, not this register's**, and
**the recording agent has not read #36's body either** — so this entry does not restate #36's
wording of the two readings beyond §3's own gloss (*"Phase-2-scoped"*, against *"every fixture
reproduced in full"*). Elsewhere this file and
[`project-state.md`](project-state.md) describe #36 Part A as the Phase-3 lift request; that is
Part A's **first** question, and it remains accurate — Part A carried both.

**What this ruling does NOT do.** It does **not** make the **Phase 2 exit determination** —
that is a separate [GOV-002](../governance/roadmap-authority.md) call, still owed, and **not
made here** (see §4). It does not convert `ed92bbb` into a Phase-2 gate pass; it rules that no
**finding** arises against it under requirement 3, which is a narrower thing and is recorded as
the narrower thing.

**⚠ OVERREACH 1 — §3's claim that ticket (g) satisfies GOV-015 rule 4 was FALSE when
written, and this PR repairs it FORWARD, not retroactively.** Rule 4 requires a lift to be
*per-scope, tied to a specific **approved, Ready** ticket*. At head `586a34e` — the state §3
was asserted against — ticket (g) in
[`planning/ticket-set.md`](planning/ticket-set.md) read **`blocked: freeze`**, **"NOT Ready …
and deliberately so"**, with **no live GitHub issue**. It satisfied **specific**. It failed
**approved** and failed **Ready**. **Rule 4 was not satisfied at the moment HD-24 asserted it,
and nothing in this register should be read as saying it was.** Found by the Strategic Product
Reviewer in the PR #38 review, stated there without hedge.

**The Product Owner's authority to lift is not in question** — a Product Owner decision
outranks GOV-015, and §3 could simply have *waived* rule 4. It did not waive it; it
**asserted** it, and the asserted mechanism did not exist. The repair is therefore **forward**:
ticket (g)'s `blocked: freeze` is removed under this lift, its DoR is re-assessed **dated now**
against [GOV-004](../governance/definition-of-ready.md), and a live issue is opened for it —
**[#40](https://github.com/tomerYannay/4UR4/issues/40)**, filed 2026-07-28, leading with
*"Status: NOT READY. Do not start."*, which supplies **specific** and supplies nothing toward
**approved** or **Ready**.
**The repair is begun and is NOT complete.** On that re-assessment ticket (g) is **still not
Ready** — [GOV-004](../governance/definition-of-ready.md)'s *"carries no unaddressed dependency
or open scope question"* is genuinely unmet while **ESC-1, ESC-3, ESC-4 and ESC-5**
([`maintenance-backlog.md`](maintenance-backlog.md) M-50) are open and while the **Phase 2 exit
determination** the roadmap makes a Phase 3 entry criterion is still owed. **Rule 4 is
therefore still unsatisfied at this head, now for a stated and closable reason rather than an
unnoticed one, and Phase-3 implementation may not begin.**

> **The trap, named so it is not walked into.** The Phase-2 attestation records that `engine/`
> was authored before its ticket reached Ready and that ***"#7 has NOT been backdated to
> Ready. Fitting the record to the outcome is the failure this corpus exists to catch."***
> The identical defect was available here prospectively: flipping (g) to Ready would make §3
> read true. **It was not done, and must not be.**

### §4 — E2-AUTHOR criterion 5 and #36 Part B

**§4 resolves [#36](https://github.com/tomerYannay/4UR4/issues/36) Part B affirmatively, on the
Phase-2 independence attestation** committed by PR #38
([`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md)).
**That ruling stands as a Product Owner decision.**

**§4 also AUTHORIZES the Phase 2 exit to close, and the first form of this entry omitted that
as well.** Verbatim, as relayed by Code Review:

> "Phase 2 exit is authorized to close on its acceptance criteria **without further Product
> Owner approval**."

**What it changes, stated precisely, because two things were being carried as one.** *(a)* **Who
may determine Phase 2 exit** is **unchanged**: a [GOV-002](../governance/roadmap-authority.md)
determination owned by the **Product Steward**, on a gate assessment, and no other agent may
make it. *(b)* **Whether that determination then needs a further Product Owner approval before
the phase can close** is what §4 answers: **it does not.** The approval requirement is
**already removed**. **The determination itself is still owed, is NOT made by §4, and is NOT
made in this change** — it lands separately, on its own evidence.

**Why the omission was load-bearing.** [`project-state.md`](project-state.md),
[`planning/ticket-set.md`](planning/ticket-set.md) and this entry all carried the Phase-2 exit
as *owed* with **no indication that the Product Owner had already removed the approval step**.
A reader planning the path to Ready would have budgeted for a Product Owner round that §4 had
deleted — and, worse, could have read the silence as the approval still being outstanding. All
three files now say which half is outstanding.

**§4 supersedes a live roadmap sentence — in authority, not in the file, and the distinction is
the whole point.** §4 supersedes the roadmap's *"Criterion 5 is not satisfiable until
[#21](https://github.com/tomerYannay/4UR4/issues/21) … is resolved, so **Phase 2 entry is
blocked on #20 and #21 in addition to the per-scope freeze lift**"* — in HD-24's own terms,
*"in writing, rather than leaving it reinterpreted."* **The sentence is still in
[`roadmap.md`](roadmap.md), and this change edits no byte of that file**: roadmap edits are
[GOV-002](../governance/roadmap-authority.md) / [GOV-013](../governance/approval-gate.md)
territory, and the Product Steward does not restate a Product Owner scope decision there even
to make it current — the same disposition already taken for **M-56**. So **the sentence is live
in the file and no longer governs**, and those two facts must not be collapsed into either one
of them. **#21 remains open**; what §4 removes is that sentence's blocking effect on criterion
5, not the attribution defect #21 records.

**⚠ OVERREACH 2 — the artifact §4 relies on does not carry what the roadmap criterion asks
for, and both facts are true at once.** [`roadmap.md`](roadmap.md) criterion 5 requires the
attestation to carry **both** the A-check **and** the E2-AUTHOR-B record **plus the commit
range**. The attestation itself records the B-record for `7ab8075` as **"ABSENT — not weak,
ABSENT"** and the commit range as **"NOT RECORDED … This is owed."** #36 Part B's question was
conditioned on an attestation *"carrying your named sign-off"*, and attestation §8 is
**"OWED. THIS BLOCK IS DELIBERATELY UNSIGNED."** Attestation §10 states its own ceiling: *"it
is not a Phase-2 gate pass, it is not a freeze lift, it authorizes nothing."*

**The artifact pre-emptively refused the claim now made of it.** What §4's *descriptive* clause
says is accurate — the attester is the Product Steward, disclosed as a non-author of `engine/`;
the artifact is committed and citable; §9.1 discloses the single-identity collapse on its face.
What §4's *ruling* does is answer a question while dropping the precondition it was conditioned
on. **Both are recorded. The ruling governs; the gap is not thereby closed**, and
[`project-state.md`](project-state.md) continues to carry criterion 5's residue as owed.

### HD-24's closing recording directive — half executed, half DECLINED on engineering grounds

**The directive, verbatim, as relayed by Code Review:**

> "To be recorded in `product/human-decisions.md` as **HD-24**, and in
> `governance/build-freeze.md`'s machine-readable marker as **a widened `scope`**."

**First half — EXECUTED.** This entry is that record, filed as **HD-24**.

**Second half — NOT EXECUTED, and recorded as declined rather than quietly dropped.** The
freeze marker's `scope` is **not** widened, and it must not be. **`scope` is a list of
directory names**, matched by [`../tools/validate.mjs`](../tools/validate.mjs) against its
guarded-directory list; it is not a list of behaviours, phases or permissions. `engine/` — the
only directory §3's grant reaches — **is already in it**. There is therefore **no widening
available that expresses this lift**: the sole mechanical effect of adding a name would be to
un-guard **some other** directory. There are **18** such candidates (the guarded list minus
`engine`), and they split in two: **eight** — `api`, `db`, `scanner`, `worker`, `dashboard`,
`alerts`, `billing`, `providers` — are on **§3's own still-frozen list**, so adding one would
un-guard what §3 expressly froze; the other **ten** — `src`, `lib`, `app`, `server`, `client`,
`packages`, `services`, `web`, `backend`, `frontend` — appear on **no list at all**, so adding
one would un-guard a directory **no decision addresses**. **Executing the directive literally
would authorize the opposite of what §3 ruled, or something §3 never considered.**
*(Corrected 2026-07-28: this read "every candidate … is on §3's own still-frozen list", **false
for ten of eighteen**. It is the same conflation of the guarded list with §3's NOT-authorized
list that `tools/validate.mjs`'s INVARIANT comment records against commit `685b65a` — and it
recurred in the one sentence carrying the whole evidentiary weight of declining a Product Owner
instruction. Found by Code Review; the conclusion survives, the reasoning is now measured.)* What was
done instead: `lifted_by` records the Phase-3 extension in prose, the marker's own comment says
why `scope` did not move, and
[`../governance/build-freeze.md`](../governance/build-freeze.md) states in terms that the
validator **cannot** tell Phase-2 work from Phase-3 work inside `engine/` — a gap named rather
than closed, because a directory-name check cannot close it.

**This is a Product Owner instruction declined by an agent, which is exactly the thing this
register exists to make visible.** It is recorded here, quoted, with its reason, and it is
**reversible by the Product Owner alone**: if a *directory* was intended, naming that directory
is all that is required, and it would then be added to `scope` **and** to
`PRODUCT_CODE_DIRS`/the guarded list together — the pairing `build-freeze.md` already warns is
mandatory, *"or the ban is decorative."* No agent may widen `scope` on its own reading of this
directive, and none has.

### What this decision does not do

It does **not** touch **HD-06** — no provider is selected and no spend is authorized. It
changes **no byte of [`roadmap.md`](roadmap.md) and no phase order**
([GOV-002](../governance/roadmap-authority.md), [GOV-013](../governance/approval-gate.md)) —
**it does not leave every roadmap sentence authoritative**, and the earlier form of this
line implied it did. It read: *"It does **not** change the roadmap or its phase order."*
**§4 expressly supersedes the roadmap sentence** *"Criterion 5 is not satisfiable until #21 …
is resolved"* — in writing, rather than by reinterpretation. The **file** is untouched; that
**sentence's authority** is not. This register keeps the two apart from here on. Found by Code
Review.
It does **not** widen the lift beyond `engine/`.
It does **not** close [#21](https://github.com/tomerYannay/4UR4/issues/21) or
[#34](https://github.com/tomerYannay/4UR4/issues/34), and it creates no independent
attribution. It does **not** confirm [HD-23](#hd-23--autonomous-execution-directive--materiality-high),
which remains **PENDING**. It does **not** make ticket (g) Ready — only a
[GOV-004](../governance/definition-of-ready.md) assessment can, and the current one says no.

## Decision log — 2026-07-28 (relayed, unconfirmed)

- **2026-07-28 — HD-23 relayed, not ruled.** An autonomous-execution directive reached the
  working agents through the Orchestrator with **no citable artifact**. It is recorded above as
  **PENDING PRODUCT OWNER CONFIRMATION**, with its two over-broad readings and their
  corrections, and with the note that no determination made that day depends on it. **It is
  the first entry since HD-12 — the point from which every entry carries a citable artifact —
  to name none**, and the first anywhere in the register to carry an explicit
  **`Artifact: NONE`** field rather than leave the gap to be counted. *(An earlier form of
  this line said "the first entry in this register that names no artifact". The ten earliest
  entries — HD-01–HD-05, HD-07–HD-11 — name none either; they predate the practice and no
  ratification covers them.)* The absence is itself the disclosure
  [#21](https://github.com/tomerYannay/4UR4/issues/21) exists to fix.

## Decision log — 2026-07-28 (Product Owner, HD-24)

*Kept under its own heading rather than folded into the log above: HD-23 is relayed and
**unconfirmed with no artifact**, HD-24 is relayed and **carries one**
([#39](https://github.com/tomerYannay/4UR4/issues/39)). Merging the two headings would level a
distinction this register exists to keep.*

- **2026-07-28 — [HD-24](#hd-24--pr-3837-merge-authorization--phase-3-gov-015-scope-lift--36-part-b--materiality-high)
  ruled, and recorded with its two overreaches.** §2 authorizes **PR #35, PR #38 and PR #37** —
  three rows, each with its own head and **its own condition** — without waiving their gates,
  and permits Orchestrator **relay** of gate verdicts; #38's named head was voided by four
  gate-driven corrections and the authorization was **re-anchored** to
  `586a34e`. §3 **lifts GOV-015 for Phase 3 inside `engine/`** — the `ACTIVE → BROKEN_OUT`
  transition, `Λ^F` freezing, retest, failed breakout, expiry/recompute — everything else
  still frozen, E2-AUTHOR still binding — and **rules HD-22 requirement 3 to have been
  Phase-2-scoped**, satisfied by the engine merged at `ed92bbb`, so **no governance finding
  arises against that commit**. §4 resolves
  [#36](https://github.com/tomerYannay/4UR4/issues/36) Part B affirmatively **and authorizes
  Phase 2 exit to close on its acceptance criteria without further Product Owner approval** —
  the determination itself is still owed, is the Product Steward's under GOV-002, and is **not
  made here** — which **supersedes the roadmap's "criterion 5 is not satisfiable until #21"
  sentence in authority while editing no roadmap byte**. **HD-24's closing directive to record
  the lift as a widened marker `scope` is DECLINED, and recorded as declined:** `scope` is a
  directory-name list, `engine/` is already in it, and the only widening available would
  un-guard a directory §3 itself lists as still frozen.
  **Two overreaches are recorded rather than smoothed:** §3's claim that ticket (g) satisfied
  **GOV-015 rule 4 was false when written** — (g) was `blocked: freeze` and expressly not
  Ready — and §4's ruling rests on an attestation that records its own E2-AUTHOR-B entry as
  **ABSENT**, its commit range as **not recorded**, and its sign-off block as **deliberately
  unsigned**. The rulings stand; the gaps stand with them.

## HD-25 — `FAILED_BREAKOUT` retains BOTH exits (resolves ESC-4) · materiality: **high**

- **Status:** **APPROVED** — **Decided by: Product Owner, 2026-07-28.** Resolves **ESC-4**,
  the fourth of the specification escalations lodged by
  [`../docs/architecture/phase3-implementation-plan.md`](../docs/architecture/phase3-implementation-plan.md)
  §11 and carried at [`maintenance-backlog.md`](maintenance-backlog.md) **M-50**.
- **⚠ Provenance — the same disclosure form as
  [HD-23](#hd-23--autonomous-execution-directive--materiality-high) and
  [HD-24](#hd-24--pr-3837-merge-authorization--phase-3-gov-015-scope-lift--36-part-b--materiality-high),
  stated plainly rather than by reference.** This ruling was **relayed in session**, under the
  **single shared identity**, and there is **no citable external artifact** for it — no issue,
  no comment, no commit by a second party. It is therefore **citable within this register and
  not independently attributable**: nothing here distinguishes a relayed Product Owner decision
  from one the recording agent composed. This entry was written by the **Product Steward**,
  which is the party that raised ESC-4's options, so it is **not** a disinterested record.
  [#21](https://github.com/tomerYannay/4UR4/issues/21) and
  [#34](https://github.com/tomerYannay/4UR4/issues/34) remain open and HD-25 closes neither.
- **Decision:** §11 gave `FAILED_BREAKOUT` **no outgoing edge**, and §21.7 enumerated exactly
  `ACTIVE`, `BROKEN_OUT` and `RETESTED` as the states a new all-time high invalidates. Read
  literally, `FAILED_BREAKOUT` was **terminal for the whole series**. Is it?
- **Ruling — option C: `FAILED_BREAKOUT` retains BOTH exits.**
  1. **A new ATH resets it** — §10.3 / §17 trigger 1, which is **unqualified by state**.
  2. **Expiry retires it** at `t − breakout_bar ≥ E_expiry`, emitting
     `EXPIRED_POST_BREAKOUT → NONE` and a recompute (§17, §21.5).
  3. Both exits return the detector to `NONE`, after which a new formation is subject to
     §21.3 and takes effect no earlier than the following bar.
- **The decisive product reason, recorded because it is the ratio.** Under the rejected
  readings, **the first failed breakout in a name's history silences that name permanently**.
  §18 names **secular decline from an IPO peak** as a supported case — fixtures **GX-08** and
  **GX-09** are exactly that — and such a name **may never make another all-time high**. 4UR4
  is a **recurring daily scanner**; a rule that can retire a name forever on one failed break
  makes it a one-shot one. Only option C keeps it a scanner.
- **What this resolves that was previously a self-contradiction.** The Phase-3 plan contained
  both readings: §7.6 applied the **frozen regime** to `FAILED_BREAKOUT`, while §11's ESC-4
  took the literal three-state reading. **This ruling resolves it in favour of §7.6** — the
  frozen regime **does** extend to `FAILED_BREAKOUT`, which fixture **GX-17 bar 23** already
  records (`state_at_start: FAILED_BREAKOUT`, `line_source: frozen event line Λ^F (§21.5)`).
- **§21.7's three-state enumeration is therefore NOT exhaustive for the reset**, and is
  amended to include `FAILED_BREAKOUT`. That amendment is a **behaviour change**, which is why
  it is the Product Owner's and not the Product Steward's.
- **The Product Steward's settled part stands, unchanged.** **Within an episode**, once
  `FAILED_BREAKOUT` is recorded, **§15 and §16 are not re-evaluated for that episode** — no
  second failure, no later retest of the same broken line. That part is **fixture-forced** by
  **GX-12 at the 0.5× sweep scale**. Option C adds **episode-ending** exits; it does **not**
  reopen §15/§16 within the episode. `FAILED_BREAKOUT` is **episode-terminal, not
  name-terminal**, and the two must not be collapsed.
- **Alternatives, both REJECTED.** **(A)** `FAILED_BREAKOUT` is fully terminal — rejected for
  the reason above. **(B)** A new ATH resets it but expiry does not — rejected as arbitrary:
  it leaves a state that can be held open indefinitely by a name that never makes another
  high, which is the same defect in slower form.
- **Nothing moves on the corpus.** **No fixture has a post-failure new ATH**, and **none has a
  tail reaching `E_expiry`** from a failed breakout. Both exits are therefore **unexercised by
  committed evidence** and owe **constructed unit tests**, not fixtures. This framing is
  confirmed rather than assumed: the Product Steward has no shell and measured nothing here.
- **Cost of delaying:** n/a — ruled 2026-07-28. While open it was one of the four escalations
  holding ticket **(g)** below [GOV-004](../governance/definition-of-ready.md) element 7.
- **Safe default (now superseded by the ruling):** implement neither exit and escalate on
  first contact — which is what the Phase-3 plan proposed, and what this ruling replaces.
- **Cross-references:** [`trendline-specification.md`](trendline-specification.md) §11, §17,
  §21.5, §21.7 and the amendment record §22 · ESC-4 in
  [`../docs/architecture/phase3-implementation-plan.md`](../docs/architecture/phase3-implementation-plan.md)
  §11 · [`maintenance-backlog.md`](maintenance-backlog.md) M-50 ·
  [`planning/ticket-set.md`](planning/ticket-set.md) ticket (g).

## Decision log — 2026-07-28 (Product Owner, HD-25)

*Under its own heading, on the HD-24 precedent: HD-24 carries an artifact
([#39](https://github.com/tomerYannay/4UR4/issues/39)) and **HD-25 carries none**. Folding
them together would level exactly the distinction these headings exist to keep.*

- **2026-07-28 — [HD-25](#hd-25--failed_breakout-retains-both-exits-resolves-esc-4--materiality-high)
  ruled (resolves ESC-4):** `FAILED_BREAKOUT` retains **both** exits — a new ATH resets it
  (§10.3 / §17 trigger 1, unqualified) and expiry retires it at
  `t − breakout_bar ≥ E_expiry` with `EXPIRED_POST_BREAKOUT → NONE` and recompute. It is
  **episode-terminal, not name-terminal**: §15/§16 are still not re-evaluated within the
  episode (fixture-forced by GX-12 @0.5×). §21.7's three-state enumeration is amended to
  include it, and the Phase-3 plan's §7.6-vs-§11 contradiction is resolved **in favour of
  §7.6**. **Relayed in session under the single shared identity, with no citable external
  artifact** — the same disclosure form as HD-23/HD-24. **Nothing moves on the corpus.**

---

## HD-28 — A phase closes on its criteria; no further approval · materiality: **high**

**Ruled by the Product Owner, 2026-07-29.** Escalated by the Strategic Product Reviewer as
`STRATEGIC_HUMAN_DECISION_REQUIRED` on PR #45, and ruled in the **general** form rather than the
Phase-3-only form, which retires the question for Phases 4–9 at the same cost.

**Ruling.** **A phase-exit determination whose acceptance criteria are met as written closes on the
Product Steward's determination alone. No further Product Owner approval is required.**

**What made this a live question, stated so the ruling is not read as a formality.** [HD-24](#hd-24--pr-3837-merge-authorization--phase-3-gov-015-scope-lift--36-part-b--materiality-high)
§4 said Phase 2 was *"authorized to close on its acceptance criteria **without further Product Owner
approval**"*, and §4(b) glossed that as *"The approval requirement is **already removed**."* An
approval step that is *removed* is a step that **existed** — so the corpus could not treat
"criteria met ⇒ closes" as self-evident, and §4's removal was scoped to **Phase 2 by name**. Nothing
granted the Phase-3 equivalent. PR #45 nonetheless recorded `authority: the criteria themselves —
no ruling was required`, which asserted an authority that had not been granted. The Reviewer's
finding was correct and this ruling supplies what was missing, generally.

**Who still makes the determination is UNCHANGED.** [HD-24](#hd-24--pr-3837-merge-authorization--phase-3-gov-015-scope-lift--36-part-b--materiality-high) §4(a): it is a GOV-002
determination **owned by the Product Steward, and no other agent may make it.** This ruling removes
an approval step; it does not move the determination or widen who may make it.

**What this ruling does NOT do, because the Reviewer named the risk precisely and it is accepted
rather than waved away.** Phase 4's exit criteria carry backtest numbers and, transitively,
**[HD-06](#hd-06--data-provider-selection--recurring-cost--materiality-high) money**. This ruling
therefore lands on Phase 4 as well — deliberately. It is survivable **only** because the spend gate
is independent of the exit gate:

- **HD-06 remains PENDING and is untouched.** No phase-exit determination authorizes spend,
  licensing, provider selection, or external data. A phase whose criteria require purchased data
  cannot have those criteria met until HD-06 is separately ruled, so this ruling cannot be used to
  reach money.
- **GOV-015 is untouched.** Closing a phase lifts no freeze. Phase entry has its own conditions.
- **The ruling binds only where criteria are met AS WRITTEN.** A determination that a criterion is
  met *by ruling*, or that closes over an unmet criterion — Phase 2's actual situation — is a
  different act and is **not** covered here. Phase 2 needed a Product Owner ruling because a
  criterion was unmet, and that requirement stands for any future phase in the same position.

**Recorded consequence.** `phase_3_exit` at
[`project-state.md`](project-state.md) cites this ruling in its `authority:` field instead of
claiming none was required.

# Delegated product decisions (HD-21)

> **Sequencing rule, learned from SPR-D-01:** a delegated decision's status line is written
> **`RESOLVED — pending condition-10 audit`** and promoted only once the Project Auditor
> confirms. SPR-D-01 asserted `RESOLVED` while the audit was outstanding; it was disclosed
> rather than concealed, and is true as of `5b99ba6` — but SPR-D-02 onward must not repeat
> the ordering.

Decisions taken by the **Strategic Product Reviewer** under the bounded delegation of
[HD-21](#hd-21--bounded-autonomous-product-decision-authority--materiality-high). Each is
**approved under bounded Product Owner delegation; not direct Product Owner authorship**,
and each requires an independent **Project Auditor** confirmation of the ten delegation
conditions (condition 10) before it stands.

## SPR-D-01 — RM-01 carries both analytical layers · `DELEGATED_PRODUCT_DECISION_APPROVED`

> **Approved under bounded Product Owner delegation; not direct Product Owner authorship.**

- **Decision ID:** SPR-D-01 · **Resolves:** [HD-20](#hd-20--rm-01-as-of-time-result-diverges-from-the-approved-full-series-record--materiality-high)
  · **Authority:** [HD-21](https://github.com/tomerYannay/4UR4/issues/27)
  · **Evidence:** [issue #26](https://github.com/tomerYannay/4UR4/issues/26)
  · **Condition-10 audit: CONFIRMED by the Project Auditor at `5b99ba6`.** First audit
  returned **NOT CONFIRMED** at `0b23f91` — correctly: the decision existed only in a
  session transcript while this register still read `PENDING`, which is the substitution
  condition 10 exists to prevent. The decision stands from `5b99ba6`.

  > **Provenance of the condition-10 confirmation — disclosed to the same standard this
  > register applies to HD-12/13/14.** The confirmation reached this register as a
  > **session relay**. **No artifact authored by the auditor exists.** The verdict text is
  > posted in exactly **one** place — [#26](https://github.com/tomerYannay/4UR4/issues/26)
  > (2026-07-26), which states *"CONFIRMED by the Project Auditor at `5b99ba6`"* — and that
  > posting is a **same-account relay written by the deciding session**, not by the auditor.
  > It is **not** on [#27](https://github.com/tomerYannay/4UR4/issues/27), which has no
  > comments, and **not** on [PR #25](https://github.com/tomerYannay/4UR4/pull/25), which
  > describes *that* a disclosure was made but states neither the verdict nor the SHA — a
  > reader of PR #25 alone cannot learn what was confirmed. No audit report is committed.
  > That gap is **because [#21](https://github.com/tomerYannay/4UR4/issues/21) is
  > unresolved**; it is precisely the defect #21 records.
  > *(This note has now been wrong in both directions and the corrections are kept rather
  > than overwritten. It first said the confirmation was "not on #26" — **understating**
  > disclosure. It was then corrected to "it is on both" — **overstating** it, in the one
  > note whose whole subject is provenance honesty. The statement above is the checked one:
  > #26 only, relayed, not independently authored.)* The
  > auditor ran **inside the
  > same autonomous session and under the same single GitHub account** as the decision it
  > audited, so its independence is **role-level (a different, read-only agent that did
  > not produce the work), not organizational**. The verdict is not weakened by saying
  > so — but a register that penalised a transcript-only *decision* must not quietly rest
  > on a transcript-only *confirmation*. Closing #21 is what upgrades this record.

### Decision

RM-01 carries **two records, explicitly scoped, neither superseding the other.**

**Half A — full-series geometry, retained verbatim, gated at unit level.**
`A = (2, 2026-06-16, 225.64)`, `B* = (25, 2026-07-21, 129.88)`, `m = −0.0240143`,
`b = 5.46697`, 0 envelope violations. The Product Owner's 2026-07-25 approval, SC-1 =
`MATCH`, SC-2 / HD-11 and the six visual-acceptance items stand **untouched and
unreopened**.

**Half B — as-of-time / causal, newly recorded, gated within Phase-2-owned behaviour.**
Stop at bar 10 (2026-06-29). Line at stop: `A = (2, 225.64)`, `B* = (9, 2026-06-26,
158.40)`, `m = −0.0505453`, `b = 5.52003`; line value `150.593`; close `164.19`; margin
`0.0864461` log units — **the raw clearance `ln(close) − ŷ`**. *Naming the convention is
load-bearing for the gate: `tools/fixture-replay.mjs` assigns its own `events[].margin`
field the value `0.0764461`, the same quantity **net of `ε_break`**. An engine asserting
`margin == 0.0864461` against that field fails by exactly `0.01`. The §6.2 `causal_record`
field-list agreement is still owed, so this ambiguity is live, not historical.*
Pre-stop trace: `t_form = 8` with `B* = (3, 213.7999)`,
`m = −0.0539003`; bar 9 `INVALID_PIERCE` + `WICK_BREAK` re-selecting `B* → (9, 158.40)`
effective bar 10 (§21.6).

**Mandatory non-endorsement clause — must appear on the artifacts, not only here.**
Half B is an **evidentiary conformance expectation, not an economic endorsement**. 4UR4
does **not** assert the bar-10 signal is a good trade. It exemplifies a **short-history /
post-IPO candidate false-positive class**, and whether that class should be suppressed is
an **open Phase 4 backtest question**, deliberately not answered here.

**Parameters unchanged:** `min_formation_bars = 8`, `min_ath_age_bars = 3`, `ε = 0.02` stay
at their ratified HD-14 / D-TL-12 values; `ε_break` stays unlocked per HD-13. **The 23
golden fixtures are unchanged** — no re-derivation, a direct consequence of rejecting
option 3.

### Scope limits, recorded because each is easy to over-claim

1. **"Gated end-to-end" means within Phase-2-owned behaviour only.** The Product Owner
   ruled on 2026-07-26 that *"Phase 3 remains responsible for confirmed breakout, retest,
   failure and expiry."* The Phase 2 clause therefore asserts **`line_at_stop`, not
   `Λ^F`**, and asserts no `BROKEN_OUT` state and no `BREAKOUT_CONFIRMED` reason code.
1b. **The stop index must be engine-derived, not fixture-supplied.** Identifying it
   requires computing the first close above the line — the *trigger* of a Phase-3-owned
   transition, though not the transition itself. If the harness were allowed to hand the
   engine the stop index, the B-clause would assert nothing about the engine's own
   detection. The Phase 2 plan clause must say so explicitly; left ambiguous, this is
   where "gated end-to-end" would quietly re-expand.
2. **Half B *narrows* what RM-01 asserts at the Phase 2 exit.** Under Half A
   (`confirmed_bar == null`) the complete final state and reason-code set were
   Phase-2-assertable. Under Half B, transitions are assertable only at **bars 0–9**, plus
   correct identification of the stop index. "The gate is strengthened" is true of the
   gate as a whole and **false** of RM-01's Phase-2 assertable surface.
3. **Circularity limit — RESOLVED to its true value, 2026-07-26: the condition HOLDS.**
   Half B's expectation **is** generated by `fixture-replay.mjs`, so it
   is **model-derived**. RM-01's non-circularity then attaches to **Half A's
   human-approved geometry and to the real, undesigned prices — not to Half B's
   provenance**. HD-15 conditions 1 and 2 remain the only controls on that.
4. **No GOV-015 clearance is granted by this decision.** Extending `check-evidence.mjs`
   and `fixture-replay.mjs` to read `real/` rests on narrow grounds — `check-evidence.mjs`
   **already reads** `real/RM-01/annotation.json`, and pointing the existing permitted
   model at `real/RM-01/input.csv` is *the same file, for the same purpose*, needing no
   specification section it does not already implement; its scope constant is a **path,
   not a capability**. *(An earlier draft justified this by "the HD-15/HD-19 precedent".
   That reasoning is **struck**: both instruments expressly say they are **not** a
   precedent, so it relied on the one thing they refuse to be. The Project Auditor caught
   it.)* **A new executable tool file, detection logic beyond what the model already
   implements, or a product-code directory is a fresh GOV-015 question and
   Product-Owner-only.**

### Rationale

Applied in the HD-21 tie-break order; all seven point the same way. **(1) No look-ahead
bias** — the full-series record is by construction look-ahead, since it uses bar 25 to
describe the line judging bar 10; only this option puts the causal expectation in the gate.
**(2) Causal correctness** — §21.4's corollary predicts this direction and §21.8 rule 4
commands the re-derivation. **(3) Mechanically verifiable evidence** — the sole option
supplying `real/*` a comparison contract, and the only one that puts RM-01 under any
mechanical guard at all. **Stated precisely, because the stronger verb would be false:** if
`expected-causal.json` is replay-generated it is a **regression guard against today's
model**, not an independent correctness check — so it closes the *absence* of a guard, not
the absence of independent verification. `expected-causal.json` **must state its own
provenance on its face.** **(4) Reversibility** — all four reversible; option 3 the most
expensive. **(5) Lower false-confidence risk** — this option's risk is visible; option 3's
is worse in kind, a corpus that agrees with the human because it was tuned to.
**(6) Preserve information** — both analytical layers retained. **(7) Defer economics to
backtesting** — with the non-endorsement clause.

The status quo is not merely weaker but **broken**: `confirmed_bar == null` is
unsatisfiable by a spec-conforming engine at the documented gate values, so the gate as
written would fail a *correct* implementation.

### Rejected alternatives

**Option 2 — geometry only, as-of-time non-gating.** The only real contender. Rejected on
tie-breaks 1 and 3: its gate asserts only the look-ahead-derived quantity, and it leaves
`real/*` without a comparison contract, so the Layer 0 walk stays vacuous or absent —
reporting coverage the corpus does not have.

**Option 3 — `min_formation_bars → 12`.** Rejected. Cheap, and **it works**: the causal
walk at `mfb = 12` is `(11, 172.4) → (12, 171.74) → (14, 167.895) → (25, 129.88)`,
converging on **exactly the approved full-series anchor**, slope `−0.0240143`, with no
close ever clearing. *Recorded precisely because that makes it seductive, not because it
recommends it:* at `mfb = 12` the causal record and the human's chart reading agree
exactly, so it **reads as validation**. It is not. `12` has no principle behind it — it is
the threshold at which *this one 29-bar series'* causal line shallows enough to reach *its
own* full-series answer, a fact about an IPO spike followed by a bounce. **HD-21 tie-break
7 forecloses it**, naming this exact move. *(Reproduction detail: the final step
`(14) → (25)` is **not** a wick-break — bar 25's high is above the line but inside `ε`
(`4.866611 < 4.872370`), so it re-selects under the §21.4 running-max rule with **no
`INVALID_PIERCE`**. Anyone tracking pierces alone will fail to reproduce the walk.)*
The substantive argument for rejecting it: option 1 **keeps the 8-vs-12 question decidable
later on population evidence**, since `min_formation_bars` remains first-class, named,
versioned and backtestable under HD-14 / D-TL-12 — option 3 decides it **now, on n = 1**.

**Option 4 — declare RM-01 out of scope; minimum-history-to-serve.** Rejected on
tie-breaks 6 and 3: it leaves **zero** non-circular real-market end-to-end evidence. Also
fitted to n = 1, and a minimum-history-to-serve rule defines *which names the product will
serve*, which brushes the never-delegated "new commercial threshold" line — declined
rather than tested.

### Evidence

Re-derived from `product/fixtures/real/RM-01/input.csv` by the decider, and by **five**
parties agreeing to six significant figures: Phase 2 planner, orchestrating session,
Strategic Product Reviewer, Verification and Code Review. *Stated precisely, because
the stronger verb would be false: three of the five — the Phase 2 planner, the
orchestrating session and the Strategic Product Reviewer — are **correlated re-runs of
the same arithmetic over the same committed CSV**, not independent instruments. **Two
are not:** **Verification** and **Code Review** each wrote their **own replay from the
specification text, with no reference to the repository's harness**, and agreed to six
significant figures. It is those two, not the count of five, that establish the numbers
are not an artifact of a single model.* *(The **Project
Auditor** also re-derived it, at `5b99ba6`, as **post-hoc verification of this record** —
deliberately **not** counted among the corroborating derivations. An auditor named as
evidence for the decision it audits is an auditor with something to defend.)*
Repository evidence: §21.3, §21.4 (lemma + corollary), §21.5, §21.6, §21.8 rule 4, D-TL-12;
HD-11, HD-12, HD-13, HD-14; `fixtures/real/RM-01/{input.csv, annotation.json}`;
`fixtures/schema/real-annotation.schema.json`; `docs/architecture/phase2-implementation-plan.md`
§6.1, §7.1–§7.3, §8; `roadmap.md` Phase 2 exit criteria.

### Reversibility

Fully reversible by later specification revision. Half B is a **fixture expectation, not
shipped behaviour** — no code exists and none may be written under GOV-015. Reversal means
re-deriving one artifact and one gate clause. Half A is untouched throughout, so the
Product Owner's approved record survives any reversal of Half B. Reversal is by
**superseding** the record, never deleting it.

### Risks accepted

1. **The gate asserts a signal the Product Owner did not see on their own chart.** The
   substantive cost, accepted knowingly, mitigated by the non-endorsement clause.
2. **Phases 3, 5 and 6 inherit RM-01's stop** as their first real-data input. One sample;
   not a validated pattern.
3. **The short-history false-positive class remains open.** If Phase 4 shows it is
   systematic, the fix is a *principled* minimum-history rule derived from many names —
   not `12` chosen from this one.
4. `ε_break` is illustrative at `0.01`; the margin is `8.6×` it, so the result is robust
   across HD-13's sweep, but the value is not yet ratified for production.
5. **RM-01's lifetime-ATH assumption is still unconfirmed** (HD-07, listing history). It
   affects both halves equally, so it does not discriminate between options.

### Affected fixtures and specifications

`fixtures/real/RM-01/expected-causal.json` (**new**, `causal_record`-bearing, authored by a
party other than the prospective Phase 2 engine author) · `fixtures/schema/real-annotation.schema.json`
(**superseded — see below**; the planned additive edit to this schema was **not** the route
taken. `expected-causal.json` is validated by a **new, separate**
`fixtures/schema/real-causal.schema.json` instead, because `real-annotation.schema.json` is
`additionalProperties: false` and admitting Half B into it would have meant loosening a
gate rather than adding one. `annotation.json` and its schema are **unchanged**.) · `fixtures/real/RM-01/annotation.json`
(**values unchanged**) ·
`fixtures/real/RM-01/README.md` · `fixtures/README.md` §6b · `roadmap.md` Phase 2 exit gate
(`UNDER REVIEW` lifted; A-clause and B-clause stated) ·
`docs/architecture/phase2-implementation-plan.md` §6.1, §7.2, §7.3, §8 S0 ·
`tools/check-evidence.mjs` and `tools/fixture-replay.mjs` extended to cover `real/`
(**DONE**; `fixture-replay.mjs` now discovers `real/RM-*` carrying `expected-causal.json`
and asserts the Half B surface under `--all`, and `check-evidence.mjs` schema-validates it
and **fails** on a real fixture directory that carries no expectation) · **the 23 golden fixtures unchanged** · `project-state.md` (Product Steward).

*This list is a **change surface**. As of 2026-07-26 **nothing on it is owed**:
`expected-causal.json` exists, the schema question was resolved by adding a separate
`real-causal.schema.json` rather than editing `real-annotation.schema.json`, and both
evidence tools now cover `real/`. RM-01 is under mechanical causal replay in CI.*

**Four records are RETAINED, not deleted** — HD-21 permits adding to or superseding a
record, never removing one, and each of these is the kind a well-meaning tidy-up would
take: (1) `annotation.json`'s `expected_regions.breakout.note` — *"No confirmed breakout
through 2026-07-24"* — qualify additively elsewhere, do not rewrite; (2) the visual
checklist item *"Breakout bar classification matches the PO's expectation → pass"*, which
is the Product Owner's own reading; (3) `product_owner_approval: "approved"`; and (4)
**`roadmap.md`'s Steward contrary assessment** — the most deletable artifact in the tree
once the question is settled, and the record of the strongest argument against the adopted
structure.

### What would trigger reconsideration

1. **Phase 4 backtesting shows short-history / post-IPO signals are a *systematic* false
   positive class across many names** — then a principled minimum-history rule derived
   from the population supersedes this. **This is the intended route for option 3's
   substance**, and it is why the 8-vs-12 question is left open rather than closed.
2. A second or third real-market fixture reproduces the pattern — that is the evidence base
   `min_formation_bars` should be tuned on, not RM-01.
3. RM-01's lifetime-ATH assumption is falsified by listing history (HD-07).
4. `ε_break` is ratified at a production value materially different from `0.01`.
5. **Any Product Owner instruction** — this is a delegated decision and may be overturned
   at any time without cause.
6. **The Project Auditor finds any HD-21 condition unmet** — then this decision does not
   stand.

---

## SPR-D-03 — `product/fixtures/real/**` is R2b, permeable by necessity · `DELEGATED_PRODUCT_DECISION_APPROVED`

> **Approved under bounded Product Owner delegation; not direct Product Owner authorship.**

- **Decision ID:** SPR-D-03 · **Resolves:** M-09 (`maintenance-backlog.md`)
  · **Authority:** [HD-21](https://github.com/tomerYannay/4UR4/issues/27)
  · **Ruled at head:** `7ab8075` (PR [#33](https://github.com/tomerYannay/4UR4/pull/33) strategic review)
  · **Status:** **RESOLVED — condition-10 CONFIRMED by the Project Auditor at `f0455f6`,
  all ten HD-21 conditions met.** Propagated at `70362fa`+ (§3 table row R2b, §10 author
  brief, schema `author_independence`, M-09, `project-state.md`, the `bash-guard.mjs`
  comment).

> **Correction, Project Auditor F-3.** When first written, clause 1 below said
> `real/**` "**is** classified R2 … in §3". It was not — the §3 table had no `real/**`
> row at all. A prescription written as a statement of fact, the same class as M-01/M-02.
> It is now true because the propagation pass made it true, and it was not true when the
> sentence was written. Recorded rather than quietly fixed by the passage of time.

**Written here before it is cited anywhere else**, per the sequencing rule above. This is
the first delegated decision to follow that rule from the start; SPR-D-01 did not, and
SPR-D-02 was withheld and then vacated without ever being written.

### History that must travel with this record

**SPR-D-02 proposed the same ruling and was VACATED.** It was proposed, withheld, then
declined outright, and was **never written to this register**. SPR-D-03 is not a re-run of
it: the Strategic Product Reviewer records that SPR-D-02 did not lead with the argument
that now decides the question — that the quarantine clause being corrected was **agent-invented
scope**, not Product Owner scope. That argument was established by the Project Auditor
during the PR #30 audit, after SPR-D-02 was declined. The record is retained rather than
overwritten so the reversal is visible as a reversal.

### The decision

`product/fixtures/real/**` is classified **R2 — PERMEABLE by necessity** in §3 of
[`../docs/architecture/phase2-independence-mechanism.md`](../docs/architecture/phase2-independence-mechanism.md),
on the same footing as `product/fixtures/golden/**`, for the Phase-2 engine author and
successor-phase engine authors.

1. `real/RM-01/input.csv`, `annotation.json` and `README.md` are **permeable**. Half A is the
   human-approved, non-circular anchor and **is** the contract.
2. `real/RM-01/expected-causal.json` and `schema/real-causal.schema.json` are **permeable**.
   Half B is the B-clause conformance target the Product Owner placed in the Phase 2 exit gate.
3. **Mandatory no-credit rider — it must travel with the classification.** Reproducing
   `expected-causal.json` earns **conformance credit only**. It earns **no independence
   credit** (HD-15 condition 1 — agreement with the reference model earns none, and Half B is
   replay-generated) and **no non-circularity credit** (SPR-D-01 limit 3 — RM-01's
   non-circularity attaches to Half A's human-approved geometry and the real prices, never to
   Half B's provenance).
4. **The quarantine set is unchanged in substance.** It remains the causal reference model and
   its successors under `tools/`, `product/fixtures/VERIFICATION.md`, and the mechanism
   document. **Nothing is added to or removed from the `QUARANTINE` configuration** — `real/**`
   was never in it. Adopting the restrictive reading would have meant *adding* a control, not
   preserving one.
5. The `author_independence` description in
   [`fixtures/schema/real-causal.schema.json`](fixtures/schema/real-causal.schema.json) is
   **superseded, not deleted**. Its clause requiring the Phase-2 author to have *"read neither
   this file nor the reference model"* widened Product-Owner-approved text by agent authorship.
   The corrected text must **retain** the statement that that file's own author read the model
   and is disqualified, and must record that the widening clause was superseded by SPR-D-03.

### Why this is inside the delegation, boundary by boundary

Checked individually rather than concluded in aggregate. No provider purchase or spend · no
licensing acceptance · no security/privacy/billing/PII (the artifact is committed public
fixture data already in the repository) · no irreversible external action · no core
product-thesis change · no roadmap phase-order change. It is **not a GOV-015 lift or
widening**: it expands no implementation permission, and HD-22 already governs what may be
built.

### The argument that decides it

**E2-AUTHOR-B is Product-Owner-approved text, and it names only the reference model under
`tools/`.** The *"nor this file"* clause in the schema widened a PO-approved criterion without
any ruling. Correcting it **restores the Product Owner's own text**; it does not reduce the
Product Owner's control. A delegated decision that narrows agent-invented scope back to
PO-authored scope is the safest available use of this delegation.

Supporting, on the HD-21 tie-break order: **mechanical verifiability (tie-break 3) is
decisive.** Permeable is the only option under which the Product-Owner-ruled RM-01 B-clause is
assertable inside the engine's own suite, in CI, at every commit. Look-ahead bias (1) and
causal correctness (2) are neutral — this is a read-permission question, not an
evaluation-window one.

### The argument the record under-claimed (Project Auditor F-1)

**Half B's numbers were already permeable, so the "split" alternative was never a real
control.** The §3 table classifies `product/roadmap.md` as **R3 PERMEABLE**, and the
roadmap's own Phase-2 exit criteria already publish every Half B value: stop bar 10,
`A = (2, 225.64)`, `B* = (9, 158.40)`, `m = −0.0505453`, `b = 5.52003`, line `150.593`,
close `164.19`, margin `0.0864461`, `t_form = 8`, `(3, 213.7999)`, `m = −0.0539003` — and
the margin-convention trap besides. A compliant author reading only permeable sources
already had all of them.

This is what actually makes the split option unavailable: it would have been a control over
the **interface** and not over the **information**. It also converts "risks accepted" item 3
(*"the §8.4 fitting risk grows by one artifact — unchanged in kind"*) from an assertion into
a demonstration. The original record argued the split down on proportionality; that was the
weaker version of a decisive argument.

### Rejected alternatives

- **Quarantine `real/**` entirely.** Rejected: it makes the Product Owner's own Phase 2 exit
  gate **unsatisfiable by the ticket**. An author who may not read the target cannot know the
  field set, the margin convention (raw clearance vs. net of `ε_break` — the ambiguity SPR-D-01
  flagged as live), the `not_asserted` exclusion set, or the `input_binding` hash. The
  restrictive direction is usually the safe one; here it is the unsatisfiable one.
- **Split: Half A permeable, Half B quarantined.** The only real contender, and its argument is
  genuine — Half B is replay-generated, so reading it is reading model output. Rejected on
  proportionality: the 23 golden `causal_record` blocks are **already R2 and are model outputs
  of identical provenance**, and §8.4 of the mechanism document already concedes that an engine
  fitted entirely to `causal_record` would pass every control in that document. Excluding one
  further model-derived expectation buys almost nothing against that threat and costs the
  corpus's only real-market gate. The residual is carried by the rider in (3) and by Half A.

### Risks accepted, recorded rather than mitigated away

1. The engine's RM-01 B-clause agreement is a **regression guard against today's reference
   model**, not independent verification.
2. **The ruling is partly retrospective** — PR #33's engine already reads
   `expected-causal.json`. Disclosed rather than laundered: no configured control was
   circumvented (`real/**` was never in `QUARANTINE`), and the ruling would be identical for a
   Phase-3 author who has not yet begun.
3. The §8.4 fitting risk grows by one artifact. Unchanged in kind.

### Reversibility

Full, by later mechanism or specification revision. Reversal costs one table row, one schema
description, and — for a future phase — a clean-room profile that excludes `real/**`. **No code
depends on the classification.** Reversal is by **superseding** this record, never deleting it.

### What would trigger reconsideration

1. A real fixture whose expectation is **not** replay-generated.
2. Issue [#20](https://github.com/tomerYannay/4UR4/issues/20)'s P1 clean-room procedure being
   exercised for real, forcing an explicit include/exclude list.
3. **Any Product Owner instruction** — delegated, overturnable at any time without cause.
4. **The Project Auditor finding any HD-21 condition unmet** — then SPR-D-03 does not stand and
   M-09 reopens unchanged.
