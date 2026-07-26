# RM-01 — Product Owner's original chart (first real-market validation fixture)

> **Real-market EVIDENCE + ANNOTATION under [GOV-015](../../../../governance/build-freeze.md)
> build-freeze — DOCS/DATA only, no product code.** RM-01 is the first entry of the
> human-reviewed real-market ground-truth layer reserved in
> [`../../real-market-plan.md`](../../real-market-plan.md) §2, complementing the synthetic
> golden set in [`../../README.md`](../../README.md).
>
> **Status: `verified` (geometry independently recomputed from licensed OHLCV) · Product
> Owner approval: `approved` (2026-07-25).** SC-1 = MATCH; SC-2 resolved via HD-11.

> ## ⚠ Everything below is a **full-series** result — RM-01 also carries an as-of-time record
>
> This record predates **HD-12** (as-of-time evaluation, ratified 2026-07-25) and was
> never redone under it. Re-derived as-of-time from this directory's own `input.csv` by
> **five separate agent sessions** — Phase 2 planner, orchestrating session, Strategic
> Product Reviewer, Verification and Code Review — agreeing to six significant figures,
> **RM-01 confirms a breakout at bar 10 (2026-06-29)**: close `164.19` against a causal
> line at `150.593`, margin **0.0864461** log units (the raw clearance `ln(close) − ŷ`;
> the reference model's own `events[].margin` field reports `0.0764461`, the same
> quantity net of `ε_break`). Suppression would need `ε_break` at ≈8.6× its documented
> value, which HD-13 forbids in any case. *Stated precisely: three of the five — the
> Phase 2 planner, the orchestrating session and the Strategic Product Reviewer — are
> **correlated re-runs of the same arithmetic over the same committed CSV**, not
> independent instruments. **Two are not:** **Verification** and **Code Review** each
> wrote their **own replay from the specification text, with no reference to the
> repository's harness**, and agreed to six significant figures. It is those two, not
> the count of five, that establish the numbers are not an artifact of a single
> model.*
>
> **Both results are arithmetically correct about different objects.** The full-series
> line below (`B* = (25, 129.88)`) is genuinely never closed above, and §21.4's own
> corollary predicts an as-of-time breakout may exist where a full-series calculation
> reports none. **Nothing below is withdrawn**, and the Product Owner's approval is not
> reopened.
>
> In particular, §2's *"none through 2026-07-24"*, §4's *"no qualifying close breakout"*
> and §5's *"matches the PO's expectation"* are **full-series statements** and should be
> read as such.
>
> ### HD-20 is RESOLVED — by **SPR-D-01**, a delegated decision
>
> **Status: RESOLVED, 2026-07-26.** The divergence above was escalated as **HD-20**
> ([issue #26](https://github.com/tomerYannay/4UR4/issues/26)) and is closed by
> **SPR-D-01** — see the [register](../../../human-decisions.md), which is authoritative.
> **Approved under bounded Product Owner delegation; not direct Product Owner
> authorship**: decided by the **Strategic Product Reviewer** under the **HD-21**
> delegation ([#27](https://github.com/tomerYannay/4UR4/issues/27)), marked
> `DELEGATED_PRODUCT_DECISION_APPROVED`, and **CONFIRMED against all ten delegation
> conditions by the Project Auditor at `5b99ba6`**. *(Relayed, not independently authored
> — see the provenance note in
> [`../../../human-decisions.md`](../../../human-decisions.md) → SPR-D-01: role-level
> independence, not organizational, pending
> [#21](https://github.com/tomerYannay/4UR4/issues/21).)* It is **not** a Product Owner
> ruling and must not be read as one; the Product Owner may overturn it at any time
> without cause.
>
> **The resolution:** RM-01 carries **two records, neither superseding the other**.
> **Half A** — the full-series geometry below — is retained **verbatim** and is gated at
> **unit level** on an exported pure §8 selector, **not** on pipeline output. **Half B** —
> the as-of-time record above — is gated **within Phase-2-owned behaviour only**.
>
> **The scope limits, which travel with every use of this decision.** *Numbered 1, 1b, 2,
> 3, 4 to match the [register](../../../human-decisions.md), which is authoritative. The
> artifacts had renumbered them 1–4, which made "limit 3" and "limit 4" name different
> things in different files; all artifact copies —* `../../README.md`, `../../VERIFICATION.md`
> *and this one — now use the register's numbering.*
> 1. **Phase-2-only scope.** Half B asserts `line_at_stop`, **not** `Λ^F`, and asserts
>    **no** `BROKEN_OUT` state and **no** `BREAKOUT_CONFIRMED` reason code — those stay
>    Phase 3's.
> - **1b.** **The stop index must be engine-derived**, never supplied by the fixture or
>   the harness; otherwise the clause asserts nothing about the engine's own detection.
> 2. **Half B *narrows* RM-01's Phase-2 assertable surface** to bars 0–9 plus the stop
>    index. *"The gate is strengthened"* is **true of the gate as a whole** and **FALSE of
>    RM-01**. Neither sentence may travel without the other.
> 3. **Circularity — the condition HOLDS, so this is no longer conditional.** The Half B
>    expectation in [`expected-causal.json`](expected-causal.json) **is** generated by
>    `tools/fixture-replay.mjs`. It **is model-derived**, and it **is a regression guard
>    against today's model, not an independent correctness check** — it detects drift from
>    the current model and cannot detect that the current model is wrong. RM-01's non-circularity attaches to **Half A's
>    human-approved geometry and the real, undesigned prices** — not to Half B's
>    provenance.
> 4. **No [GOV-015](../../../../governance/build-freeze.md) clearance is granted.** The
>    build-freeze remains **ON** and `autonomous_implementation: DISABLED`.
>
> **Non-endorsement (required by SPR-D-01 to appear on the artifacts, not only in the
> register).** The B-clause is an **evidentiary conformance expectation, not an economic
> endorsement**. 4UR4 does **not** assert that the bar-10 signal is a good trade. It
> exemplifies a **short-history / post-IPO candidate false-positive class**, and whether
> that class should be suppressed is an **open Phase 4 backtest question**, deliberately
> not answered by SPR-D-01.
>
> Detail: [`../../README.md`](../../README.md) §6b.

The machine-validated record is [`annotation.json`](annotation.json), conforming to
[`../../schema/real-annotation.schema.json`](../../schema/real-annotation.schema.json). The
verified daily OHLCV is [`input.csv`](input.csv), derived from the immutable
[`alphavantage-source.json`](alphavantage-source.json).

---

## 1. Immutable source evidence

**Chart image (PO's original):**
- **Path:** `source-chart.png` · **SHA-256:** `d191300e3cde075aac86838185bfa5797a2c6d0e6dd6f1c2a8558a414ab05b15` · 137151 bytes · 1272 × 672 (PNG)

**Market-data source (Alpha Vantage):**
- **Path:** `alphavantage-source.json` · **SHA-256:** `69a67469e08af3f43f5a05c4730a3c4e2c2ff4c297b7237e2f41ecb3d550c377`
- **Source:** Alpha Vantage · **Symbol:** SPCX · **Interval:** daily · **Timezone:** US/Eastern
- **Last refreshed:** 2026-07-24 · **Output size:** compact · **Bars:** 29 (2026-06-12 → 2026-07-24)
- **Adjustment note:** Alpha Vantage `TIME_SERIES_DAILY` is raw **as-traded** (split-**un**adjusted). No split/corporate action is evident in this window, so it is consistent with **HD-01** (split-adjusted, dividend-unadjusted) over 2026-06-12 → 2026-07-24. A split in range would require adjustment before use.

**DO NOT edit or regenerate these files; they are immutable source evidence.** The checksums are recorded so any change is detectable. `input.csv` is a mechanical, chronologically-ascending re-encoding of the source; the source JSON remains the authority.

**Qualitative image description (no pixel prices transcribed):** a dark-themed TradingView chart labelled "SPCX · 1D · … Corporation Technologies Corp"; candles descend from a left peak (~top of a logarithmic axis) to the lower-right; a single **orange descending trendline** runs from the top-left peak wick toward the lower-right; the price axis uses **non-linear (logarithmic) spacing** (the "L" scale toggle is active). *No axis price value is read from pixels and recorded as market data.*

---

## 2. Recorded metadata (requirement 2)

- **Symbol:** SPCX (PO-stated) · **Exchange:** unknown
- **Chart timeframe:** 1D (PO-stated)
- **Chart scale:** logarithmic — **visually confirmed** (non-linear axis tick spacing; the log-scale toggle is active), consistent with the PO's stated log scale. Qualitative only; no pixel prices read.
- **Visible date range:** 2026-06-12 → 2026-07-24 (PO-stated; matches the source's bar range)
- **Data source shown in chart:** TradingView · **Timezone (chart display):** unknown (OHLCV source timezone is US/Eastern)
- **Visible ATH anchor:** 2026-06-16 @ **225.64** (PO-stated **and OHLCV-verified** — see §3)
- **Expected second-anchor region:** 2026-07-21 — high **now verified = 129.88** (was PO-stated unknown)
- **Expected breakout region:** **none through 2026-07-24** (verified — no qualifying close)
- **Expected retest region:** **none** (verified — no breakout occurred)

### Product Owner interpretation (verbatim, 6 bullets)
1. Orange descending line starts from the stock's all-time-high wick.
2. Intended second anchor is the later high wick on 2026-07-21.
3. Line should remain above intervening highs per the approved upper-log-hull rule.
4. A breakout is the first daily close above the line.
5. Persistence and volume are confidence features, not breakout validity gates.
6. A retest is a later contact/overlap with the line where the daily close holds above it.

### Drawn-line metadata (verbatim)
- The orange line is a **manually extended TradingView trendline** (two-point construction); **magnet mode** snapped endpoints to candle highs.
- Intended line connects the ATH high 2026-06-16 @ 225.64 to the later high on 2026-07-21.
- The exact second-anchor price was **not** inferred from pixels — it is now **verified from OHLCV** as 129.88.
- The drawn line was **not** treated as algorithmic ground truth until verified against actual OHLCV (now done).

### Unknown / unresolved metadata
- Exchange — unknown · Chart-display timezone — unknown.
- Lifetime-ATH assumption (see §3) — pending listing-history confirmation (HD-07).
- SC-2 pivot-eligibility question — **RESOLVED 2026-07-25 (HD-11)**; see §6. (No unresolved
  metadata remains on this item — the pivot prefilter is non-authoritative.)

---

## 3. ATH verification (requirement 5) — no unverified "lifetime ATH" claim

Independently computed as the **maximum bar high over ALL available bars in the source**:
**ATH = 225.64 on 2026-06-16** (bar index 2 of 29), a unique maximum (no tie). This matches the PO-stated ATH exactly.

**Listing-history assumption (documented, not asserted):** the source's earliest bar is **2026-06-12**. Alpha Vantage `compact` output returns up to the latest **100** bars; only **29** were returned, so the full available history is these 29 bars — consistent with SPCX having **listed on/around 2026-06-12**. Treating 225.64 as a **lifetime** ATH therefore depends on 2026-06-12 being the listing/IPO date. That is recorded as an **assumption to confirm** against a listing-history/reference source (HD-07); over the *available* history it is unambiguously the ATH.

---

## 4. Independent calculation (requirements 6–8, 10) — trading-bar indices

Computed from `input.csv` using **trading-bar ordinal indices** (not calendar-day gaps), on `y = ln(high)` (§3):

| Quantity | Value |
|----------|-------|
| Anchor **A** (ATH) | bar `t=2`, 2026-06-16, high **225.64** |
| Second anchor **B** (PO-intended) | bar `t=25`, 2026-07-21, high **129.88** |
| Bar-index delta (tB − tA) | **23** trading bars |
| `yA = ln(225.64)` | 5.41894 |
| `yB = ln(129.88)` | 4.86661 |
| **Log slope** `m = (yB−yA)/(tB−tA)` | **−0.0240143** per bar |
| **Intercept** `b = yA − m·tA` | **5.46697** |

**Envelope check (requirement 7).** Line value computed for **every** trading bar; every intervening high's distance from the line measured in % and log units. **Envelope violations: 0** — no intervening high pierces the line beyond ε = 0.02. **Maximum intervening approach: 2026-07-06** at **−0.740%** (log −0.00743) — the closest any high comes, and it is still **below** the line. (This matches the preliminary expectation, independently reproduced — not copied.)

**Canonical-anchor check (requirement 8).** Among **all** later highs, the slope from A to the **2026-07-21** high (−0.0240143) is the **shallowest** (closest to zero). By the upper-log-hull rule (§8), the shallowest descending line from the ATH that dominates all later highs is the canonical line, so **2026-07-21 is the upper-log-hull canonical second anchor** — and the A→B line dominates all later highs. The PO's two-point line and the canonical hull line **coincide**.

**Post-B evaluation (requirements 10–11).** Extending the line past B and evaluating 2026-07-22 → 2026-07-24: every high **and** close is **below** the line → **no wick-break, no qualifying close breakout, and therefore no retest** through 2026-07-24. (Independently reproduced.)

---

## 5. Visual-acceptance checklist (requirement 5) — now backed by OHLCV

| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1 | Line begins at the ATH wick 2026-06-16 @ 225.64 | ✅ pass | 225.64 verified as the ATH (max high) at 2026-06-16 |
| 2 | Line touches the later high wick 2026-07-21 | ✅ pass | Verified high 129.88; B lies on the line by construction |
| 3 | Line does not improperly cut through intervening highs | ✅ pass | 0 envelope violations; closest approach −0.740% |
| 4 | Projected line matches the PO's orange TradingView line | ✅ pass | Canonical hull line uses the same two endpoints as the PO line — geometrically identical |
| 5 | Breakout bar classification matches the PO's expectation | ✅ pass | No breakout through 2026-07-24 |
| 6 | Retest matches the approved rule | ✅ pass | No retest (no breakout occurred) |

All six pass on the calculated result — **approved by the Product Owner (2026-07-25)**.

---

## 6. Spec-contradiction report (requirement 11 & 13) — recorded, not silently changed

**SC-1 — RESOLVED = `MATCH`.** The independent calculation confirms the PO's intended two-point line (ATH 2026-06-16 → 2026-07-21) **coincides with the canonical upper-log-hull line**: 2026-07-21 is the shallowest-slope (hull) anchor over all later highs, **no intervening high pierces** the line (0 violations; closest −0.740% at 2026-07-06). This rules out `MISMATCH_INTERVENING_HIGH` and `MISMATCH_DIFFERENT_CANONICAL_ANCHOR`; the evidence is exact (not a tolerance judgement), so `MATCH` rather than `VISUAL_MATCH_WITHIN_TOLERANCE`, and there is enough data (29 bars) so not `INSUFFICIENT_DATA`.

**SC-2 — RESOLVED 2026-07-25 (Product Owner decision, [HD-11](../../../human-decisions.md)).** The surfaced question — 2026-07-21 is the upper-log-hull vertex over *all* later highs **but is not a `k=3` pivot high** (2026-07-17 @130.33 is higher within 3 bars; the only `k=3` pivot after the ATH, 2026-06-30, does not dominate) — has been ruled on: **the upper-log-hull envelope rule is canonical and must not depend on a fixed pivot-high prefilter.** Pivot detection is secondary/non-authoritative (visualization, descriptive metadata, confidence, provably-lossless optimization only) and **must never change the canonical anchor**. The trendline spec §5/§6/§8/D-TL-03/D-TL-05 were revised accordingly, and golden fixture **GX-19** was added to prove a non-pivot high can be the canonical anchor (with a strict `k=3` prefilter choosing the wrong result). RM-01 is cited as the motivating real-world case. **This resolves the last open contradiction on RM-01.**

---

*Design/evidence artifact under GOV-015. It authorizes no build. The geometry above is independently computed from licensed OHLCV as verification evidence; the Product Owner **approved** this result on 2026-07-25 (SC-1 = MATCH, SC-2 resolved via HD-11).*
