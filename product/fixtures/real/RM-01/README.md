# RM-01 — Product Owner's original chart (first real-market validation fixture)

> **Real-market EVIDENCE + ANNOTATION under [GOV-015](../../../../governance/build-freeze.md)
> build-freeze — DOCS/DATA only, no product code.** RM-01 is the first entry of the
> human-reviewed real-market ground-truth layer reserved in
> [`../../real-market-plan.md`](../../real-market-plan.md) §2, complementing the synthetic
> golden set in [`../../README.md`](../../README.md).
>
> **Status: `awaiting-market-data` · Product Owner approval: `pending`.**
> No licensed/verified OHLCV exists for this fixture yet, so every
> `verified_market_data` field is `null` and no geometry has been computed.

The machine-validated record is [`annotation.json`](annotation.json), conforming to
[`../../schema/real-annotation.schema.json`](../../schema/real-annotation.schema.json).

---

## 1. Immutable source evidence

- **Image path:** `product/fixtures/real/RM-01/source-chart.png`
- **SHA-256:** `d191300e3cde075aac86838185bfa5797a2c6d0e6dd6f1c2a8558a414ab05b15`
- **Size:** 137151 bytes
- **Dimensions:** 1272 × 672 (PNG)

**DO NOT edit or regenerate this image; it is immutable source evidence.** The checksum
above is recorded so any future change is detectable. The image is the externally supplied
artifact that motivated the thesis object; it is preserved exactly as delivered.

**Qualitative description (no pixel prices transcribed):** a dark-themed TradingView chart
labelled "SPCX · 1D · … Corporation Technologies Corp". A candlestick sequence descends
from a peak on the left to lower prices on the right. A single **orange descending
trendline** is drawn from the top-left peak wick down toward the lower-right. The right-hand
price axis uses **non-linear (logarithmic) spacing**. In the mid-section the orange line
runs close to — and appears to graze — some intervening candle highs (see §6). A current
price marker and post-market marker appear at the lower right. *No axis price value is read
from pixels and recorded as market data.*

---

## 2. Recorded metadata (requirement 2)

All values below are **Product-Owner-stated** (PO-asserted, verbatim) or explicitly
**unknown** — none are pixel-derived.

- **Symbol:** SPCX (PO-stated)
- **Exchange:** unknown
- **Chart timeframe:** 1D (PO-stated)
- **Chart scale:** logarithmic. *Log-scale confirmation:* the chart's right-hand price axis
  is **visually confirmed to be logarithmic** (non-linear tick spacing — successive gridline
  gaps compress toward higher prices), consistent with the PO's stated log scale. This is a
  **qualitative** confirmation of the scale toggle/axis only; no pixel prices are read.
- **Visible date range:** 2026-06-12 → 2026-07-24 (PO-stated)
- **Data source shown in chart:** TradingView · **Timezone:** unknown
- **Visible ATH anchor:** 2026-06-16 @ **225.64** (PO-stated ATH high/anchor; not
  pixel-derived; awaits OHLCV verification)
- **Expected second-anchor region:** 2026-07-21, price **unknown** (PO-stated date only; the
  second-anchor high price is intentionally not inferred from pixels)
- **Expected breakout region:** unknown (awaits verified OHLCV + first-daily-close test §13)
- **Expected retest region:** unknown (awaits verified OHLCV §16)

### Product Owner interpretation (verbatim, 6 bullets)

1. Orange descending line starts from the stock's all-time-high wick.
2. Intended second anchor is the later high wick on 2026-07-21.
3. Line should remain above intervening highs per the approved upper-log-hull rule.
4. A breakout is the first daily close above the line.
5. Persistence and volume are confidence features, not breakout validity gates.
6. A retest is a later contact/overlap with the line where the daily close holds above it.

### Drawn-line metadata (verbatim)

- The orange line is a **manually extended TradingView trendline** (two-point construction);
  **magnet mode** snapped endpoints to candle highs.
- Intended line connects the ATH high 2026-06-16 @ 225.64 to the later high on 2026-07-21.
- The exact second-anchor price is **not** inferred from screenshot pixels.
- The drawn line is **not** treated as algorithmic ground truth until verified against actual
  OHLCV.

### Unknown / unresolved metadata

- Exchange — unknown
- Timezone — unknown
- Second-anchor high price on 2026-07-21 — unknown (null until verified OHLCV)
- Breakout date — unknown
- Retest date — unknown
- All verified OHLCV bars and the recomputed line geometry (slope/intercept/line values,
  actual anchors, breakout/retest bars) — unavailable; awaits a licensed data provider
  (HD-06) and a per-scope freeze lift.

---

## 3. Data-integrity note (requirement 3)

**No exact price, date, or OHLCV value has been inferred from screenshot pixels and recorded
as factual market data.** The only numeric values present anywhere in RM-01 are
**Product-Owner-stated**: the ATH high **225.64** and the calendar dates (visible range
2026-06-12 → 2026-07-24, ATH 2026-06-16, second anchor 2026-07-21). Every other numeric
market-data / geometry field — the second-anchor price, the log slope and intercept, the
line values, the actual anchor bars, and the breakout/retest bars — is **`null`** in
[`annotation.json`](annotation.json) and stays null until **licensed/verified OHLCV** exists.
Reading axis prices or candle positions from the image and presenting them as data is
explicitly forbidden here.

---

## 4. Visual-acceptance checklist (requirement 5)

To be checked against verified OHLCV once available. **All items are currently unchecked /
pending verification.**

- [ ] (1) Line begins at the intended ATH wick on 2026-06-16 at 225.64.
- [ ] (2) Line touches the intended later high wick on 2026-07-21.
- [ ] (3) Line does not improperly cut through intervening highs.
- [ ] (4) Projected line visually matches the PO's orange TradingView line.
- [ ] (5) Breakout bar classification matches the PO's expectation.
- [ ] (6) Retest, if present, matches the approved rule.

---

## 5. Product Owner approval (requirement 6)

**Field: `product_owner_approval`** — possible values: `pending | approved | rejected |
needs-adjustment`.

**Current value: `pending`.**

Approval follows the reviewed process in [`../../real-market-plan.md`](../../real-market-plan.md)
§3 (analyst annotation against verified OHLCV, cross-check, dual sign-off) and cannot advance
while `status` is `awaiting-market-data`.

---

## 6. Spec-contradiction report (requirement 11 — CRITICAL: recorded, NOT resolved)

**Open verification question (SC-1).** The PO's orange line is a **two-point** construction
(ATH 2026-06-16 → later high 2026-07-21) drawn in TradingView. The **approved canonical rule
is the upper-log-hull** ([`../../../trendline-specification.md`](../../../trendline-specification.md)
§8, D-TL-04): it selects the **shallowest descending log line from the ATH that stays above
ALL intervening highs** within tolerance. A two-point line and the hull line **coincide only
if** no intervening high pierces the two-point line and no shallower dominating line exists.

**Visually (qualitative, unverified) the drawn two-point line appears to run close to — and
possibly through — some intervening candle highs in the mid-section.** Therefore it is
**UNRESOLVED** whether the PO's intended second anchor (2026-07-21) equals the hull-canonical
second anchor.

Stated plainly: **this must be checked against real OHLCV once available.** If intervening
highs pierce the two-point line, the hull rule (§8) would select a **different** second
anchor than 2026-07-21 — and that discrepancy **must be surfaced to the Product Owner, NOT
resolved by silently editing the spec or this annotation.** This is recorded as a
**contradiction / risk** (`spec_contradiction_report.status = "open"`,
`SC-1.resolution = "unresolved-awaiting-ohlcv"`), **not a decision**. Resolving it is out of
scope under the build-freeze and requires verified OHLCV and/or a Product Owner ruling
([GOV-007](../../../../governance/product-focus.md) — hidden scope is flagged, not absorbed).

---

*Design/evidence artifact under GOV-015. It authorizes no build and acquires no market data.
Verified OHLCV is loaded only when a Ready ticket exists, the data-provider gate (HD-06)
resolves, and the freeze is lifted per-scope
([GOV-013](../../../../governance/approval-gate.md)).*
