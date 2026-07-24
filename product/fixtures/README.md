# 4UR4 — Golden-Example Fixture Set (trendline geometry, selection & state machine)

> **This is TEST DATA / RESEARCH EVIDENCE, not product implementation.** Under the
> [GOV-015](../../governance/build-freeze.md) build-freeze these fixtures author only
> Markdown / CSV / JSON data + docs. No engine, runner, or product source directory is
> created here. The fixtures exist to be the **correctness contract**: the deterministic
> inputs and expected outputs a future, build-lifted detector MUST reproduce exactly.

## 1. Purpose

Prove that a future trendline-detection engine matches the **approved** definitions in
[`product/trendline-specification.md`](../trendline-specification.md) (HD-01/HD-02/HD-03
incorporated) and the confidence context in
[`product/confidence-specification.md`](../confidence-specification.md). Each fixture is a
`(input.csv, expected.json)` pair whose expected values are derived **by hand from the
spec**, with every number pinned to **6 significant figures** and every accept/reject
decision carrying a **named reason code** and a **numeric rejection rationale**.

These expand and supersede the spec's own GX-01..GX-12 catalog (§19) and cover every
required Phase-0 category (tickets (a) geometry/selection and (b) breakout/retest/expiry).

## 2. Methodology — how expected values are derived from the spec

All geometry is computed in **log-price space on the bar high**, exactly as the spec
mandates:

- Price basis: **split-adjusted, dividend-unadjusted ("as-traded")** (HD-01, §2). Fixture
  inputs are treated as already split-adjusted (except GX-10, which deliberately presents
  unadjusted data to exercise the split guard).
- Transform: `y[t] = ln(H[t])` (§3).
- Anchor `A = (tA, HA)`: earliest bar at the global-max high (§4, D-TL-02).
- Pivot highs: strict `>` on the left, `>=` on the right over `k` bars (§5), default `k=3`.
- Second anchor `B* = (tB, HB)`: the **upper log-hull** selection (§8, D-TL-04) — the
  shallowest descending log line from `A` that dominates all intervening pivot highs within
  tolerance `eps`.
- Line geometry (§7):
  - slope `m = (yB - yA) / (tB - tA)`
  - intercept `b = yA - m * tA`
  - line value in log space `y_hat(t) = m*t + b`
  - line value in price space `line(t) = exp(y_hat(t))`
- Breakout / wick / retest / failure / expiry tests: §11, §13–§17, with the revised HD-03
  policy (breakout fires on the **first** qualifying daily close; `confirmed_bar ==
  breakout_bar`; persistence and volume are confidence-only, never validity gates).

Every `expected.json` carries a `geometry_check` block restating `yA`, `yB`, the slope /
intercept formulas, and the key inequality evaluations, so an independent verifier can
confirm the arithmetic without running any code. All rounding is to **6 significant
figures**; where hand computation of `exp()` leaves ambiguity at the 6th figure, the
`geometry_check` inequalities (not the rounded display value) are the authority.

## 3. Fixture catalog

| ID | Category | Purpose (key expected outcome) | Spec section(s) |
|----|----------|--------------------------------|-----------------|
| GX-01 | normal valid | Clean line, no breakout -> **ACTIVE**; B*=(12,88) | §4–§8, §11 |
| GX-09 | normal valid variant (ATH on first bar) | IPO-peak decline, valid line from t=0; B*=(10,150) | §4, §6–§8, §18 |
| GX-12 | repeated ATH | Two equal ATHs -> **earliest** anchor (t=0); B*=(15,118) | §4, D-TL-02 |
| GX-02 | multiple competing second anchors | Envelope discrimination -> **B*=(45,92)**, rejects (20,96)/(70,80) (spec §8 worked example, eps=0.005) | §8, D-TL-04/05 |
| GX-13 | intervening high invalidates a candidate | Lone spike rejects steeper candidates; B*=(20,95) | §8, §10.1, D-TL-05 |
| GX-14 | nearly equal slopes / envelope tie | Collinear pivots -> **ENVELOPE_TIE_LATER**; B*=(40,80) | §8, §18 |
| GX-15 | tolerance-boundary cases | eps and eps_break boundaries shown on **both sides** numerically | §9, §13.1/§13.5, D-TL-05/06 |
| GX-03 | wick-only crossing | Intrabar pierce, close rejects -> **WICK_BREAK**, stays ACTIVE | §11, §14 |
| GX-16 | first-close breakout | First close above line+eps_break -> **BROKEN_OUT**, confirmed_bar==breakout_bar | §13, HD-03 |
| GX-11 | volume-as-confidence | Low-volume first-close breakout -> **BROKEN_OUT** + LOW_VOLUME flag (volume does NOT gate) | §13.4, HD-03 |
| GX-05 | false breakout | Breakout then close below line-eps_fail within F_fail -> **FAILED_BREAKOUT** | §15 |
| GX-04 | clean retest | Breakout then dip to line that holds -> **RETESTED** | §16 |
| GX-17 | deep undercut not a valid retest | Return reaches line but close fails to hold -> **NOT RETESTED** + FAILED_BREAKOUT | §15, §16 |
| GX-07 | expiry & recalculation | >=100 bars after breakout -> **EXPIRED_POST_BREAKOUT** -> recompute | §17 |
| GX-06 | expiry & recalculation (recompute) | New ATH mid-series -> **RESET_NEW_ATH**, new line recomputed | §10.3, §17 |
| GX-08 | invalidation | Monotonic decline -> **NO_VALID_SECOND_ANCHOR** (no line) | §5, §6, §18 |
| GX-10 | stock split edge case | Unadjusted ~2:1 jump -> **SUSPECTED_UNADJUSTED_SPLIT**, do not fit | §2, §18 |
| GX-18 | missing-data edge case | Missing high / non-positive price -> **INVALID_INPUT / INVALID_PRICE**, no geometry | §1, §18 |

**Fixture count: 18.** Category coverage: normal valid (GX-01, GX-09), repeated ATH
(GX-12), multiple competing second anchors (GX-02), intervening-high invalidation (GX-13),
nearly-equal slopes / envelope tie (GX-14), tolerance-boundary (GX-15), wick-only crossing
(GX-03), first-close breakout (GX-16), volume-as-confidence (GX-11), false breakout
(GX-05), clean retest (GX-04), deep-undercut-not-a-retest (GX-17), expiry & recalculation
(GX-07, GX-06), invalidation / no-second-anchor (GX-08), stock-split (GX-10), missing-data
(GX-18).

Several breakout-family fixtures deliberately **share the same base line** `A=(0,100),
B*=(12,88)` (GX-01, GX-03, GX-16, GX-11, GX-05, GX-04, GX-17) so the differences are
isolated to the single behaviour under test (wick vs close, volume, failure, retest,
undercut).

## 4. Tolerance & versioning note (eps_break is NOT locked)

Default parameters used (unless a fixture states otherwise):
`k=3, eps=0.02, eps_touch=0.01, eps_retest=0.01, eps_fail=0.01, F_fail=10, W_retest=20,
h_hold=3, E_expiry=100`.

**`eps_break` is a versioned, backtestable tolerance with NO locked default (HD-03,
§13.5).** Every fixture that uses it sets `"eps_break": 0.01` **only as an illustrative
value** and carries `"eps_break_locked": false` plus an `eps_break_note` reaffirming this.
The governing `eps_break` value/definition (percentage/log-unit **or** ATR-based) is chosen
later from Phase-0 + Phase-4 evidence and pinned with the detector's `spec_version`. Each
fixture's `params.tolerance_version` tags the tolerance set used so evidence is traceable.
GX-15 explicitly probes the `eps_break` boundary from both sides to demonstrate it is a
knob, not a constant. GX-02 uses `eps=0.005` to reproduce the spec §8 worked example
exactly.

## 5. Reason-code legend

| Reason code | Meaning | Fixtures |
|-------------|---------|----------|
| `LINE_ESTABLISHED` | A valid A->B* line became ACTIVE | most |
| `ENVELOPE_TIE_LATER` | Envelope slope tie broken toward the later anchor (§18) | GX-14 |
| `WICK_BREAK` | Intrabar high pierced, close did not confirm; stays ACTIVE (§14) | GX-03 |
| `BREAKOUT_CONFIRMED` | First daily close above line+eps_break; alert fires (§13, HD-03) | GX-16, GX-11, GX-05, GX-04, GX-17, GX-07 |
| `FAILED_BREAKOUT` | Post-breakout close below line-eps_fail within F_fail (§15) | GX-05, GX-17 |
| `RETEST_HELD` | Post-breakout dip to line that held as support (§16) | GX-04 |
| `RESET_NEW_ATH` | New ATH retired the old line; recompute (§10.3, §17) | GX-06 |
| `EXPIRED_POST_BREAKOUT` | >=E_expiry bars after breakout; retire + recompute (§17) | GX-07 |
| `NO_VALID_SECOND_ANCHOR` | No eligible pivot below the ATH; no line (§10.4, §18) | GX-08 |
| `SUSPECTED_UNADJUSTED_SPLIT` | Impossible single-bar log jump > ln(1.5); do not fit (§18) | GX-10 |
| `INVALID_PRICE` | Non-positive price; reject bar-set (§1, §18) | GX-18 |
| `INVALID_INPUT` | Missing required field (high/close); reject bar-set (§1) | GX-18 |

Non-gating **flags** (confidence/quality only, never validity gates): `LOW_VOLUME` (GX-11),
`NOT_RETESTED` (GX-17). Reason codes reserved by the spec but not exercised by a dedicated
fixture here (documented for completeness): `INVALID_PIERCE`, `INSUFFICIENT_BARS`,
`ATH_TOO_RECENT`.

## 6. Synthetic-vs-real principle (avoiding circular validation)

These golden fixtures are **synthetic**: hand-designed from the spec to be small,
unambiguous, and exactly hand-verifiable. Their expected values are **spec-derived**, so on
their own they only prove an engine is *self-consistent with the written spec* — they cannot
prove the spec matches the market reality the Product Owner has in mind.

To break that circularity, an **independent, non-circular ground truth** is required:
**manually reviewed real-market fixtures** (see
[`real-market-plan.md`](real-market-plan.md)), including the **original chart supplied by
the Product Owner**. Real charts are annotated by humans/analysts and cross-checked against
the selected data provider, providing external truth that the synthetic set cannot. The two
layers are complementary: synthetic fixtures pin the deterministic arithmetic; real fixtures
validate that the arithmetic captures the intended real-world object. **No market data is
acquired now** (build-freeze + human-gated provider selection, HD-06/HD-07).

## 7. Files

- `README.md` — this document.
- `schema/fixture.schema.json` — JSON Schema for every `expected.json`.
- `golden/<ID>/input.csv` — synthetic OHLCV (`timestamp,open,high,low,close,volume`);
  `timestamp` is an **ordinal index `t`** (see each fixture's `input_convention`).
- `golden/<ID>/expected.json` — the expected output for `<ID>`, schema-validated.
- `real-market-plan.md` — plan to add human-reviewed real-market fixtures as independent
  ground truth (acquires no data now).

*Design artifact under GOV-015. It authorizes no build; implementation of a detector that
reproduces these fixtures follows only when a Ready ticket exists and the freeze is lifted
per-scope ([GOV-013](../../governance/approval-gate.md)).*
