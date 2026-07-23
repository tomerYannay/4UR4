# 4UR4 — Product Requirements Document (PRD)

Status: proposed planning artifact under [GOV-015](../governance/build-freeze.md) build-freeze.

> **Authority:** Product (Product Steward). This PRD describes **what** 4UR4 must do
> and **why**, tracing to the [vision](vision.md), [trendline spec](trendline-specification.md),
> [confidence spec](confidence-specification.md), [market-sentiment spec](market-sentiment-specification.md),
> [data-provider research](data-provider-research.md), and [MVP architecture](../docs/architecture/mvp-architecture.md).
> It authorizes **no build**. Implementation begins only when a Ready ticket exists
> on an approved roadmap and a human lifts the freeze per-scope
> ([GOV-013](../governance/approval-gate.md), [GOV-015](../governance/build-freeze.md)).
> Scope is held to the approved thesis ([GOV-007](../governance/product-focus.md)).

---

## 1. Target user

- **Primary (MVP): the internal 4UR4 analyst / operator.** A technically literate
  trader-analyst who reviews a **daily end-of-day scan** of the S&P 500 for
  high-quality breakouts from ATH-anchored logarithmic descending resistance
  trendlines, and needs to understand *why* each signal is rated as it is.
- **Secondary (later, Phase 7): the SaaS subscriber.** A self-directed retail or
  semi-professional trader who subscribes to receive **alerts** on confirmed
  breakouts (and retests) with an **explainable confidence score** attached.

Non-user (hard boundary): 4UR4 serves no one seeking order execution, brokerage,
portfolio management, or financial advice (see §5, inherited from the vision).

## 2. User problem

Traders can *see* long descending resistance lines from an all-time high on a
chart, but doing this **consistently, objectively, and at S&P 500 scale** is hard:

- Drawing the "right" line is subjective; two analysts draw two different lines.
- Deciding when a breakout is *real* (close-confirmed, persistent, volume-backed)
  vs. a fake wick-break is inconsistent and emotional.
- There is no transparent, defensible measure of *how much to trust* a given
  breakout — most tools give a signal with no decomposable reasoning.
- Backtesting these ideas free of survivorship bias requires data most retail
  tools do not expose.

4UR4 exists to make this **deterministic, explainable, and reproducible**.

## 3. Core value proposition

**A deterministic scanner that finds ONE canonical ATH-anchored logarithmic
descending resistance line per S&P 500 name, detects confirmed breakouts and
retests, and attaches an explainable, decomposable confidence score** — so a user
can trust the signal *and see exactly why*. Correctness and explainability are the
product, not speed or breadth.

## 4. MVP scope

In scope for the MVP (traces to the trendline + confidence specs):

- **One canonical trendline per name**: ATH (wick) anchor → later qualifying pivot
  high, in **log price space**, selected by the **envelope / upper-log-hull rule**
  (trendline spec §4–§9).
- **Deterministic state machine** (trendline spec §11): ACTIVE, WICK_BREAK,
  BROKEN_OUT, RETESTED, FAILED_BREAKOUT, EXPIRED — each transition emits a **named
  reason code**.
- **Confirmed breakout** detection: close-based + persistence + soft-volume policy
  (trendline spec §13).
- **Retest** detection and **failed-breakout** detection (trendline spec §15–§16).
- **Line expiry / recomputation** ~100 bars after breakout, on new ATH, or on
  structural change (trendline spec §17).
- **Confidence v1**: a 0–100 **heuristic** (NOT a probability), decomposed into
  named contributions C1–C7 with reason strings (confidence spec §1–§4).
- **Daily end-of-day batch scan** of the S&P 500 over **real market data**, with
  provenance/versioning stamped on every result (architecture §5).
- **Historical scanner + backtest harness** for rank-ordering validation of
  Confidence v1 (confidence spec §7).
- **Internal dashboard** to inspect scans, lines, breakouts, retests, and the
  **decomposed** score.
- **Golden-example fixtures** (trendline GX-01..GX-12; confidence CF-EV-01..07) as
  the correctness contract.

## 5. Explicit non-goals (out of scope for the MVP)

- **Sentiment in the score.** Fear & Greed and the market-regime score do **not**
  feed Confidence v1. They are **research context only** until a backtest proves
  calibration lift AND a human approves ([GOV-014](../governance/market-sentiment-context.md),
  sentiment spec §7). Sentiment *display* is also deferred.
- **Machine-learning confidence (v2).** Feature/label capture is design context;
  no model is trained or shipped in the MVP core.
- **Intraday / real-time scanning or streaming.** Daily EOD batch only
  (architecture §7).
- **Brokerage, order-routing, trade execution, or financial advice.** Hard
  boundary — the architecture has no module that could place a trade.
- **Multi-provider live failover, horizontal scaling, caching layers,
  microservices.** Deferred as premature (architecture §7).
- **Picking or paying a data/sentiment vendor.** Human-gated
  ([GOV-013](../governance/approval-gate.md)); research only for now.
- **Intraday granularity, weekly-bar mode, ATR-scaled tolerances.** Recorded
  alternatives, deferred.

## 6. User journeys

**Journey A — Internal analyst reviews the daily scan (MVP).**
It is end-of-day. The overnight/EOD batch has pulled adjusted daily OHLCV for the
S&P 500, run the deterministic engine per name, and persisted results. The analyst
opens the internal dashboard and sees a list of names with new state changes:
three new `BROKEN_OUT`, one `RETESTED`, two `FAILED_BREAKOUT`. She clicks a
breakout on symbol AAAA: the chart shows the ATH anchor `A`, the selected second
anchor `B*`, the log line, the breakout bar, and a **confidence of 76** decomposed
into C1 line-fit 18.8, C2 touches 12.0, C5 retest 15.0, etc., each with a reason
string. She can defend the rating to a colleague because every point is traceable.

**Journey B — Analyst investigates a rejected wick-break.**
A name flagged `WICK_BREAK` catches her eye. The dashboard shows the intrabar high
pierced the line but the close was rejected, with reason code `WICK_BREAK`; the
line remains ACTIVE. She trusts that the system did **not** fire a false signal,
because the confirmation policy (close + persistence + soft volume) is explicit and
the reason code explains the rejection.

**Journey C — SaaS subscriber receives an alert (Phase 7, later).**
A subscriber has opted into alerts for confirmed breakouts scoring ≥ 70. The daily
batch confirms a breakout on symbol BBBB at score 82; the alert pipeline emails the
subscriber a signal card: symbol, breakout date, score, top decomposed reasons, and
a mandatory disclaimer ("heuristic quality score, not a probability or trading
advice; excludes market sentiment"). The subscriber clicks through to a read-only
signal page.

## 7. Functional requirements

Traceability: each FR cites the governing spec.

- **FR-1** The engine MUST select the ATH anchor `A` as the earliest bar achieving
  the maximum **high** over the full delivered history (trendline §4, D-TL-02).
- **FR-2** The engine MUST detect pivot highs by a symmetric `k`-bar fractal rule
  with deterministic tie handling (trendline §5).
- **FR-3** The engine MUST select **one** canonical second anchor `B*` via the
  **upper-log-hull envelope rule** — the shallowest descending log line from `A`
  that dominates all intervening highs within tolerance `ε` (trendline §6, §8,
  D-TL-04).
- **FR-4** The engine MUST compute the line in **log price space** (`y = ln(H)`)
  and expose slope `m`, intercept `b`, and `line(t) = exp(ŷ(t))` (trendline §3, §7).
- **FR-5** The engine MUST implement the line **state machine** (ACTIVE,
  WICK_BREAK, BROKEN_OUT, RETESTED, FAILED_BREAKOUT, EXPIRED) and emit a **named
  reason code** on every transition and rejection (trendline §10–§11).
- **FR-6** The engine MUST detect a **confirmed breakout** by the close-based +
  persistence (`p_break`) + soft-volume (`f_vol`) policy, recording the breakout bar
  and confirmation bar, and flag `LOW_VOLUME` rather than voiding low-volume
  breakouts (trendline §13, D-TL-07).
- **FR-7** The engine MUST distinguish a **wick-break** (intrabar pierce, close
  rejected) from a breakout and keep the line ACTIVE (trendline §14).
- **FR-8** The engine MUST detect **retest hold** and **failed breakout** within
  their windows, each with reason codes (trendline §15–§16).
- **FR-9** The engine MUST **expire** a line ~`E_expiry` bars after breakout and
  **recompute** on new ATH, envelope-changing pivot, or structural pierce
  (trendline §17).
- **FR-10** The engine MUST handle all enumerated **edge cases** deterministically
  with reason codes, including `INSUFFICIENT_BARS`, `ATH_TOO_RECENT`,
  `NO_VALID_SECOND_ANCHOR`, `SUSPECTED_UNADJUSTED_SPLIT`, `INVALID_PRICE`
  (trendline §18).
- **FR-11** The engine MUST compute **Confidence v1** as `clamp(Σ w_i·s_i, 0, 100)`
  over components C1–C7, emitting each `(id, subscore, weight, contribution, reason)`
  (confidence §2–§3).
- **FR-12** Confidence output MUST set `score_kind = "heuristic"`, carry non-empty
  `disclaimers`, and satisfy `Σ contributions (clamped) == score` (confidence §3–§4).
- **FR-13** Confidence v1 MUST contain **no** sentiment-derived component; component
  ids are exactly `{C1..C7}` (confidence §10, [GOV-014](../governance/market-sentiment-context.md)).
- **FR-14** Every result (line, breakout, score) MUST carry a `spec_version` /
  algo version and data `snapshot_id` for reproducibility (architecture §5;
  trendline §20; confidence §3).
- **FR-15** The **data layer** MUST expose a provider-agnostic interface for
  adjusted daily OHLCV and point-in-time S&P 500 constituents, and own
  split/dividend **adjustment policy** and **provenance tagging** (architecture
  §3.2; data research R1, R3, R4).
- **FR-16** The **worker** MUST run a **daily EOD batch** over the S&P 500, persist
  results, write an auditable `scan_run` record, and enqueue alerts for new
  confirmed events (architecture §3.3).
- **FR-17** The **historical scanner / backtest harness** MUST replay historical
  bars survivorship-bias-free and emit a **rank-ordering / lift** report for
  Confidence v1 (confidence §7; architecture §3.1; data research R4/R5).
- **FR-18** The **internal dashboard** MUST render the line, states, and the
  **decomposed** confidence score with reasons (architecture §3.5).
- **FR-19** (Later, Phase 7) The **alert pipeline** MUST fan out confirmed-event
  alerts to channels (email first) with mandatory disclaimers (architecture §3.6).
- **FR-20** All engine tolerances/constants MUST be **named, versioned config**
  with the spec defaults, never hard-coded magic numbers (trendline §20).

## 8. Non-functional requirements

- **NFR-1 — Correctness (primary).** Signals and scores MUST be right before they
  are fast or pretty. Golden fixtures (GX-01..12, CF-EV-01..07) are the acceptance
  contract; a failing fixture blocks Done.
- **NFR-2 — Explainability.** Every score MUST be decomposable into named,
  inspectable contributions with reason strings; every accept/reject/transition
  MUST emit a reason code. No hidden terms.
- **NFR-3 — Reproducibility.** Given identical inputs + versions, the system MUST
  produce byte-identical signals and scores. Every result is replayable from
  (algo_version, confidence_version, snapshot_id, input bars).
- **NFR-4 — Determinism.** No randomness; no float-order-dependent tie resolution.
  All ties resolved by explicit stated rules (trendline §20).
- **NFR-5 — Performance (daily S&P 500 scan).** The full ~500-name EOD batch MUST
  complete within the overnight window with margin (target budget set at
  build-lift time; correctness never traded for speed). Engine is a pure library
  with no I/O in the hot path (architecture §3.1).
- **NFR-6 — Security.** No secrets in code/repo; provider keys and DB creds via a
  secrets manager. Least privilege between modules (engine holds no credentials).
  For eventual SaaS: PII minimization, isolated billing behind a third-party
  processor, no card data held (architecture §6.2). Formal privacy/security review
  is human-gated before any customer data is collected.
- **NFR-7 — Auditability / observability.** Every batch writes a `scan_run` audit
  record; data-quality checks (gaps, split sanity, duplicate bars, constituent
  drift) flag a run rather than silently emitting wrong signals (architecture §6.1).
- **NFR-8 — Data licensing correctness.** No user-facing display or shipped score
  may use data whose license does not permit commercial display/redistribution
  (data research R7; sentiment spec §3) — human-gated.

## 9. Risks

- **R-1 (high) — Wrong price-adjustment basis moves the ATH.** Choosing the wrong
  split/dividend basis silently changes the anchor and every downstream signal
  (trendline §2, D-TL-01). Mitigation: HD-01 decision + consistency rule + fixtures.
- **R-2 (high) — Envelope rule mis-defined.** The upper-log-hull selection is the
  load-bearing geometric definition; getting it wrong makes the whole product
  wrong (trendline §8, D-TL-04). Mitigation: HD-02 + GX-02 discrimination fixture.
- **R-3 (high) — Survivorship bias in backtests.** Without point-in-time
  constituents + delisted history, calibration is biased and misleading (data R4/R5).
  Mitigation: HD-06/HD-07 (likely paid, human-gated) before trusting backtests.
- **R-4 (high) — Confidence mis-presented as probability.** Regulatory/trust risk
  if a heuristic is read as odds (confidence §8, D-CF-01). Mitigation:
  `score_kind:"heuristic"`, mandatory disclaimers, HD-04.
- **R-5 (med) — Data-vendor cost/licensing overrun.** Bundled datasets (OHLCV +
  constituents + delisted + corporate actions + sentiment) may span tiers/vendors
  at material recurring cost (data R8). Mitigation: research-only + human gate.
- **R-6 (med) — Sentiment scope creep.** Pressure to wire sentiment into the score
  before evidence (GOV-014). Mitigation: normative rule + Auditor guard + HD-08.
- **R-7 (med) — SaaS PII/billing exposure.** Collecting customer/billing data
  introduces compliance surface. Mitigation: HD-10 security review, defer to Phase 7.

## 10. Open questions

- **OQ-1 (high, D-TL-01):** Confirm price-adjustment basis (split-adjusted,
  dividend-unadjusted). → HD-01.
- **OQ-2 (high, D-TL-04):** Confirm upper-log-hull envelope as the canonical
  selection rule. → HD-02.
- **OQ-3 (high, D-TL-07):** Confirm breakout confirmation policy (close +
  persistence 2 + soft volume). → HD-03.
- **OQ-4 (high, D-CF-04):** Confirm ML success-label thresholds (triple-barrier
  +15% / −7% / 60 bars). → HD-05.
- **OQ-5 (high):** Data-provider selection and recurring cost. → HD-06.
- **OQ-6 (high):** Survivorship-bias-free constituents + delisted history (paid). → HD-07.
- **OQ-7 (high, GOV-014):** External F&G source + redistribution/display rights,
  and whether/when sentiment enters the score. → HD-08, HD-09.
- **OQ-8 (med, D-CF-01):** UI wording policy that v1 is heuristic, never a
  probability. → HD-04.
- **OQ-9 (med):** SaaS billing/PII security-review scope and timing. → HD-10.
- **OQ-10 (low):** Retest-absent C5 value — strictly 0 vs. 0.5 clean-hold
  (confidence OQ-CF-3). Tunable within the confidence workstream.

## 11. Success metrics

**Leading (product):**
- Daily EOD S&P 500 batch completes within the overnight window (green
  `scan_run`), ≥ N consecutive days.
- 100% of GX-01..12 and CF-EV-01..07 fixtures pass on every engine build.
- 100% of emitted signals carry a full, reproducible decomposition + reason codes.

**Lagging (product):**
- Internal analyst can, in a review session, defend every displayed signal from
  its decomposition (qualitative acceptance).
- (Phase 7) SaaS: subscriber activation and alert open-through rate (targets set
  at Phase 7 planning).

**Signal-quality:**
- **Rank-ordering lift (Confidence v1):** on the historical set, higher-scored
  breakouts show a monotonically higher realized win-rate by decile (Spearman ≥
  target set at backtest time; confidence §7, D-CF-05).
- **Reproducibility:** a re-run of any historical scan reproduces byte-identical
  signals/scores (determinism guard).
- **False-signal discipline:** wick-breaks correctly rejected vs. confirmed
  breakouts, measured against golden fixtures and historical spot-checks.

---

*This PRD is a proposal pending human approval ([GOV-013](../governance/approval-gate.md)).
Nothing here is a build order; the build-freeze ([GOV-015](../governance/build-freeze.md))
remains ON.*
