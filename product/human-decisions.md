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
| HD-12 | high | Anchor selection is rolling/causal (as-of-time), frozen at confirmed breakout | APPROVED |
| HD-13 | high | `eps_break` stays unlocked; ordinary fixtures must be tolerance-robust | APPROVED |
| HD-14 | high | Formation gates are first-class `k`-independent parameters | APPROVED |

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
- **Status:** PENDING (unchanged).
- **Ruling:** No selection or spend yet. Complete the R1–R8 provider research and
  comparison matrix **before** any provider selection or commitment.
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
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-25.** Resolves **OQ-TL-7**
  (surfaced by [Issue #16](https://github.com/tomerYannay/4UR4/issues/16) /
  [PR #18](https://github.com/tomerYannay/4UR4/pull/18), the stale-pivot sweep, which
  explicitly did **not** decide it). Builds on
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
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-25.** Surfaced by the
  causal fixture audit on [Issue #16](https://github.com/tomerYannay/4UR4/issues/16)
  as "Decision 1" and answered there; implemented in
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
     produces a breakout with a robust margin (**GX-19**, margin 0.024613 log units),
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
- **Cost of delaying:** n/a — resolved 2026-07-25.
- **Safe default:** the documented illustrative `ε_break = 0.01` with
  `eps_break_locked: false` in every fixture, plus a recorded robustness sweep.
- **Evidence:** every fixture carries `causal_record.eps_break_robustness`;
  `tools/fixture-replay.mjs --robustness` re-runs the sweep. 22 of 23 fixtures are
  invariant across a **0.5×–2×** sweep (wider than required); GX-15 is the intended
  boundary case.
- **Cross-references:** [HD-03](#hd-03--breakout-confirmation-policy--materiality-high)
  (unamended), [HD-12](#hd-12--anchor-selection-is-rolling-and-causal-as-of-time-frozen-at-confirmed-breakout--materiality-high),
  `trendline-specification.md` §13.5.

## HD-14 — Formation gates are first-class, `k`-independent parameters · materiality: **high**
- **Status:** APPROVED — **Decided by: Product Owner, 2026-07-25.** Surfaced as
  "Decision 2" / **OQ-TL-8** by the §21 specification work on
  [Issue #16](https://github.com/tomerYannay/4UR4/issues/16); implemented in
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
  (anchor recency binds alone, after a new-ATH reset) and **GX-23** (eligibility with
  zero confirmed pivots in the formation prefix); `tools/fixture-replay.mjs
  --formation` asserts all four properties across the whole set, including replaying
  every fixture at `k ∈ {1,2,3,4,5,8}` and requiring identical output.
- **Cross-references:** `trendline-specification.md` §18, §21.3 and **D-TL-12**;
  resolves **OQ-TL-8**.

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
- **2026-07-25 — [HD-13](#hd-13--eps_break-stays-unlocked-ordinary-fixtures-must-be-tolerance-robust--materiality-high)
  approved:** `ε_break` **stays unlocked** (HD-03 unamended); instead, every **ordinary**
  fixture's expected classification must be invariant under **±20%** variation around the
  documented default, **GX-15** alone is retained as the dedicated tolerance-boundary
  fixture with both sides documented, ordinary fixtures must not become boundary tests,
  and a robust causal breakout (**GX-19**, margin 0.024613) is **preserved rather than
  reverted**.
- **2026-07-25 — [HD-14](#hd-14--formation-gates-are-first-class-k-independent-parameters--materiality-high)
  approved (resolves OQ-TL-8):** the formation gate is restated as **first-class,
  `k`-independent** parameters `min_formation_bars = 8` and `min_ath_age_bars = 3` —
  **numerically identical** to the superseded `2k+2` / `k` formulation at `k = 3`, but
  versioned with `spec_version`, backtestable, and carried in every fixture's `params`.
  Changing the pivot window `k` may no longer move any event. Locked by **GX-21**,
  **GX-22**, **GX-23** and by `tools/fixture-replay.mjs --formation`.
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

*This register records the Product Owner's rulings of 2026-07-24 and 2026-07-25. Ruled
items are governing; HD-06 remains a proposal pending human decision
([GOV-013](../governance/approval-gate.md)). The build-freeze
([GOV-015](../governance/build-freeze.md)) remains ON.*
