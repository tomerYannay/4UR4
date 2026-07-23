# 4UR4 — ATH-Anchored Logarithmic Descending Trendline Specification

Status: design/context under GOV-015 build-freeze — not an implementation order.

> **Authority:** Technical design (Architect). This document defines the
> deterministic geometry, detection rules, and evidence plan for the core
> trendline detector. It does **not** authorize building anything. Implementation
> follows only when a Ready ticket exists and the build-freeze is lifted
> ([GOV-013](../governance/approval-gate.md), [GOV-015](../governance/build-freeze.md)).
> Terms are proposed for the glossary at the end — the **Product Steward**, not
> this document, edits [`glossary.md`](glossary.md).

---

## 0. Scope and intent

This spec makes the 4UR4 thesis object precise enough to implement
deterministically: an **ATH-anchored logarithmic descending resistance
trendline**, its **breakout**, **wick-break**, **retest**, **failure**, and
**expiry** semantics. Everything here is scoped to that single object per
[GOV-007](../governance/product-focus.md). Confidence scoring is deferred to
[`confidence-specification.md`](confidence-specification.md). Sentiment is out of
scope entirely here ([GOV-014](../governance/market-sentiment-context.md)).

**Design values honoured:** Correctness before speed; Reproducibility (identical
inputs → identical lines); Explainability (every accept/reject decision has a
named reason). Determinism is a hard requirement: no randomness, no
floating-point-order-dependent tie resolution — ties are broken by explicit,
stated rules.

### Notation

| Symbol | Meaning |
|--------|---------|
| `bar[t]` | The OHLCV bar at integer index `t`, `t ∈ {0,1,…,N−1}`, ascending in time. |
| `H[t], L[t], O[t], C[t], V[t]` | High, low, open, close, volume of `bar[t]`. |
| `y[t]` | Log-price of the high: `y[t] = ln(H[t])` (see §3). |
| `A = (tA, HA)` | Anchor pivot = the all-time-high bar (§4). |
| `B = (tB, HB)` | Second anchor = the qualifying later pivot high (§6). |
| `m` | Slope of the trendline in log space, per bar (§7). |
| `b` | Intercept of the trendline in log space. |
| `ŷ(t) = m·t + b` | The trendline value in log space at index `t`. |
| `line(t) = exp(ŷ(t))` | The trendline value back in price space at index `t`. |
| `ε` | Tolerance, expressed in **log units** (§9). |

---

## 1. OHLCV input assumptions

- **Granularity:** Daily bars (`1D`) for MVP. The math is granularity-agnostic;
  "~100 bars" (§16) means ~100 daily bars. Intraday is out of scope for MVP.
- **Ordering:** Bars are strictly ascending by timestamp, de-duplicated, with no
  synthetic gap-filling (calendar gaps for weekends/holidays are expected and do
  **not** create bars). Index `t` is the ordinal position in the delivered
  series, **not** a calendar day count.
- **Required fields:** `timestamp, open, high, low, close, volume`. A bar missing
  `high` or `close` is invalid input (see §17 edge cases).
- **Positivity:** All prices must be `> 0` for `ln` to be defined. A non-positive
  price is invalid input and rejected before geometry runs.
- **Source:** Real market data, S&P 500 universe initially (per thesis). Data
  provenance/vendor is a data-layer ticket concern, not this spec.

> **Decision D-TL-00 — Bar granularity** · Default: daily (`1D`). ·
> Alternative: weekly for very long histories to reduce pivot noise. ·
> Materiality: med · Human-approval: no (daily is the safe, conventional default;
> revisit if ATH histories are decades long).

---

## 2. Adjusted vs unadjusted prices — **APPROVED: split-adjusted, dividend-unadjusted ("as-traded")**

> **Product Owner approved 2026-07-24 (HD-01).** The price basis is **confirmed
> split-adjusted, dividend-unadjusted ("as-traded")**. This is now the governing
> rule, not a pending recommendation. The same field is used consistently for ATH
> selection, pivot detection, line fitting, and breakout tests. The alternative
> (fully adjusted / total-return close) is **rejected** for this detector, and raw
> unadjusted is rejected (splits inject false ATHs).

Trendline geometry is a **multi-decade log-space** construction anchored at an
all-time high. Price-affecting corporate actions must be handled consistently or
the ATH and the line become meaningless.

- **Splits:** MUST be adjusted. An unadjusted 2:1 split injects a 50% artificial
  gap that would create a false ATH and a false breakout. **Use split-adjusted
  prices.**
- **Dividends:** SHOULD **not** be back-adjusted for this detector.
  Dividend-adjustment retroactively lowers historical prices, which can silently
  move the *all-time high* and distort the log slope. Because 4UR4 reasons about
  **price resistance a trader actually sees on a chart**, the chart-native series
  (split-adjusted, dividend-unadjusted, i.e. "as-traded" adjusted close) is the
  correct geometric substrate.

**Why log + split-adjusted + dividend-unadjusted is the safe default:** it
matches what a chartist sees, keeps the ATH stable, and avoids negative
adjusted prices (deep dividend back-adjustment on long histories can approach or
cross zero, breaking `ln`).

> **Decision D-TL-01 — Price adjustment basis** · **Status: APPROVED (Product
> Owner, 2026-07-24, HD-01) — no longer pending.** · Governing rule:
> split-adjusted, dividend-**un**adjusted ("as-traded"). · Superseded/rejected
> alternative: fully adjusted (total-return) close. · Materiality: **high**
> (changes which bar is the ATH and therefore every downstream signal). ·
> Human-approval: yes — **granted 2026-07-24 (HD-01).**

**Consistency rule:** whichever basis is chosen, the **same** field is used for
ATH selection, pivot detection, line fitting, and breakout tests. Mixing bases is
a correctness violation.

---

## 3. Logarithmic transformation

Descending resistance in 4UR4 is a **straight line in log-price space** (constant
*percentage* decay), not linear price space. Define:

```
y[t] = ln( price_field[t] )
```

- **Which field feeds `y`?** For the *line geometry* (anchors, slope, envelope),
  the field is the **bar high** `H[t]`, because the object is a *resistance* line
  connecting **highs**. So `y[t] = ln(H[t])`.
- For **breakout tests** the relevant field is the **close** `C[t]` compared
  against `line(t)` (§13); the comparison is done in log space:
  `ln(C[t]) vs ŷ(t)`.
- **Base:** natural log. Base is irrelevant to geometry (scales slope by a
  constant) but MUST be fixed to `ln` for reproducible numeric outputs.

**Worked example (log vs linear).** Highs `H1 = 100` at `t=0`, `H2 = 50` at
`t=100`.
`y1 = ln 100 = 4.60517`, `y2 = ln 50 = 3.91202`.
Log slope `m = (3.91202 − 4.60517) / (100 − 0) = −0.0069315` per bar
(a constant −0.693%/bar decay). At `t=50` the line sits at
`exp(4.60517 + (−0.0069315·50)) = exp(4.25859) = 70.71`, i.e. the geometric
mean of 100 and 50 — correct for constant-percentage resistance. A linear fit
would put `t=50` at 75, over-stating resistance at the midpoint.

---

## 4. All-time-high (ATH) selection — the anchor

- **Window:** the **full available delivered history** (no rolling window). The
  ATH is `HA = max over t of H[t]`.
- **Wick semantics:** the ATH is the **bar high** (the wick), not the close. This
  matches resistance being tested by intrabar extremes.
- **Anchor point:** `A = (tA, HA)` where `tA = argmax_t H[t]`.

**Worked example.** Highs `[80, 120, 95, 130, 110]`. `HA = 130`, `tA = 3`.
Anchor `A = (3, 130)`, `yA = ln 130 = 4.86753`.

### Repeated / equal all-time highs (tie on `HA`)

If multiple bars share the exact maximum high:

> **Decision D-TL-02 — Duplicate-ATH anchoring** · Default: anchor at the
> **earliest** bar achieving `HA` (smallest `tA`). · Rationale: the resistance
> line should span the **longest** descent, and the earliest touch is the first
> establishment of the all-time high. · Alternative: latest occurrence (shorter,
> steeper line). · Materiality: med · Human-approval: no.

**Worked example.** Highs `[130, 100, 130, 90]` → both `t=0` and `t=2` equal 130.
Default picks `tA = 0`.

---

## 5. Pivot-high rule (fractal / N-bar pivot)

A **pivot high** at index `p` is a local maximum of the high series over a
symmetric lookback/lookforward window of `k` bars:

```
isPivotHigh(p, k)  iff  H[p] > H[p−i]  for all i in 1..k
                    and  H[p] ≥ H[p+j]  for all j in 1..k
```

- **Asymmetry note:** strict `>` on the left, `≥` on the right. This makes the
  **earliest** bar of a flat-topped plateau the pivot (deterministic tie
  handling), consistent with D-TL-02.
- **Window `k`:** default `k = 3` (a 3-bar fractal: a high greater than the 3
  bars before and ≥ the 3 bars after). Larger `k` → fewer, more significant
  pivots.
- **Edge bars:** a bar within `k` of either series end cannot be a confirmed
  pivot (insufficient neighbours). The ATH bar `A` is treated as an anchor
  regardless of pivot confirmation (it is the global max by construction).

> **Decision D-TL-03 — Pivot lookback `k`** · Default: `k = 3` bars. ·
> Alternative: `k = 5` (fewer, stronger pivots) or ATR-scaled. · Materiality: med
> (affects candidate density and line stability). · Human-approval: no (tunable
> default; changing it does not change signal *semantics*, only sensitivity).

**Worked example.** Highs (index:value): `0:80 1:120 2:95 3:130 4:110 5:105 6:118
7:112`. With `k = 2`: `t=3` (130) is a pivot (`>` 120,95 left; `≥` 110,105
right). `t=6` (118) is a pivot (`>` 105,110 left; `≥` 112 right, and needs a
right neighbour at `t=8` which is absent → **not confirmable** if it is within
`k` of the end). With enough right bars, `t=6` is a valid pivot.

---

## 6. Second-anchor eligibility

The line runs from `A` (the ATH) down to a **second anchor** `B = (tB, HB)`.
`B` is eligible iff **all** hold:

1. `tB > tA` — strictly later than the ATH.
2. `isPivotHigh(tB, k)` — `B` is a confirmed pivot high (§5).
3. `HB < HA` — strictly below the ATH (the line descends).
4. The implied slope `m = (yB − yA)/(tB − tA)` is `< 0` (guaranteed by 1 & 3,
   stated for completeness).
5. `B` survives the **envelope rule** (§8) — i.e. the line `A→B` keeps all
   intervening highs at/below it within tolerance.

The **selected** `B` among all eligible candidates is chosen by the envelope
rule in §8 (not simply "the next pivot").

---

## 7. Slope in log space

```
m = ( yB − yA ) / ( tB − tA )        # per-bar log slope, m < 0
b = yA − m·tA                         # intercept so that ŷ(tA) = yA
ŷ(t) = m·t + b
line(t) = exp( ŷ(t) )                 # trendline in price space
```

**Worked example.** `A = (3, 130)`, `B = (60, 90)`.
`yA = ln130 = 4.867534`, `yB = ln90 = 4.499810`.
`m = (4.499810 − 4.867534)/(60 − 3) = −0.367724/57 = −0.00645130` per bar.
`b = 4.867534 − (−0.00645130·3) = 4.886888`.
Line at `t=30`: `ŷ = −0.00645130·30 + 4.886888 = 4.693349` →
`line(30) = exp(4.693349) = 109.22`.

---

## 8. The envelope rule — selecting **THE** valid descending line

> **Product Owner approved 2026-07-24 (HD-02).** The canonical trendline-selection
> rule is **confirmed the upper log-hull from the ATH** — the shallowest
> descending log-space line that dominates all intervening highs within tolerance
> `ε`, anchored at `A`. This is now the governing, canonical definition of the
> product's core object (not a pending recommendation). The naive "steepest line
> through two most significant pivots" alternative is **rejected** (it cuts through
> intervening highs).

Among all eligible `B` candidates, 4UR4 selects a **single canonical** descending
resistance line. The governing principle: the line is the **upper log-envelope**
of the price highs from the ATH forward — the tightest descending straight line
in log space that stays **at or above every intervening high** (within tolerance
`ε`), anchored at `A`.

This is equivalent to walking the **upper convex hull** (in log space) of the
pivot-high point set to the right of the ATH:

### Algorithm (deterministic)

```
Given anchor A=(tA,yA) and the ordered set P of pivot highs with t>tA:
1. Consider candidate second anchors B ∈ P with yB < yA (descending).
2. For each candidate B, define ŷ_B(t) = slope(A,B)·(t−tA)+yA.
3. B is ENVELOPE-VALID iff for every pivot high P_i with tA < t_i < tB:
        y[t_i] ≤ ŷ_B(t_i) + ε          # no intervening high pierces above tol
   AND for every bar high (not just pivots) in (tA, tB):
        H-check optional per D-TL-05.
4. Among ENVELOPE-VALID candidates choose B* = the one giving the LINE THAT
   BINDS: the least-steep (highest) line that still dominates all highs — i.e.
   the FIRST hull vertex. Concretely: B* = argmin over valid B of slope
   magnitude? NO — see selection rule below.
```

**Selection rule (canonical).** The canonical line is the **upper convex hull
edge** emanating from `A`: choose `B*` such that **no intervening high pierces
the line beyond `ε`** and the line is the **highest** such descending line
(smallest `|m|` that still dominates). Equivalently, `B*` is the pivot high that
maximizes the slope `m` (closest to zero, i.e. shallowest) subject to the
domination constraint — because any steeper line would pass **below** some
intervening high, violating "resistance stays above highs."

> Intuition: resistance must sit **above** the highs it caps. Of all descending
> lines from the ATH that stay above every intervening high, the **lowest**
> (steepest) ones are too aggressive (they cut through highs); the correct one is
> the **upper hull** — the shallowest line that still dominates everything. This
> is the first convex-hull vertex after `A` in log space.

**Worked example (hull selection).** Log-space pivot highs after `A=(0, y=4.605
[H=100])`:

| pivot t | H | y=lnH |
|--------:|----:|--------:|
| 20 | 96 | 4.56435 |
| 45 | 92 | 4.52179 |
| 70 | 80 | 4.38203 |

- Candidate `B=(20,96)`: `m = (4.56435−4.60517)/20 = −0.0020410`. Line at t=45 =
  `4.60517 − 0.0020410·45 = 4.51333`; pivot y at 45 is `4.52179` >
  `4.51333 + ε`? If `ε=0.005`, `4.51333+0.005 = 4.51833 < 4.52179` → **pierces →
  invalid** (the t=45 high pokes above this shallow line).
- Candidate `B=(45,92)`: `m = (4.52179−4.60517)/45 = −0.0018529`. Line at t=20 =
  `4.60517 − 0.0018529·20 = 4.56811 ≥ 4.56435` (t=20 high sits below) ✓. Line at
  t=70 = `4.60517 − 0.0018529·70 = 4.47547 ≥ 4.38203` ✓. All intervening highs
  dominated → **envelope-valid**.
- Candidate `B=(70,80)`: `m = (4.38203−4.60517)/70 = −0.0031877` (steeper). Line
  at t=45 = `4.60517 − 0.0031877·45 = 4.46173 < 4.52179` → the t=45 high pierces
  far above → **invalid**.

Selected `B* = (45, 92)` — the shallowest line that still dominates all highs.
This is the correct canonical resistance.

> **Decision D-TL-04 — Envelope selection principle** · **Status: APPROVED /
> CANONICAL (Product Owner, 2026-07-24, HD-02).** · Governing rule: **upper convex
> hull in log space from the ATH** (shallowest descending line dominating all
> intervening highs within `ε`). · Superseded/rejected alternative: "steepest line
> touching two most significant pivots" (naive two-point). · Materiality: **high**
> (defines the core object). · Human-approval: yes — **granted 2026-07-24 (HD-02)**;
> this is the load-bearing geometric definition of the product.

> **Decision D-TL-05 — Domination set: pivots-only vs every bar high** · Default:
> enforce domination against **pivot highs** for line *selection*, and against
> **every bar high** for line *validity monitoring* (§10). · Rationale: hull over
> pivots is stable and noise-tolerant; per-bar check catches a single spike that
> should invalidate. · Alternative: pivots-only everywhere (ignores lone spikes).
> · Materiality: med · Human-approval: no.

---

## 9. Tolerance `ε`

`ε` is expressed in **log units** (dimensionless, ≈ fractional price deviation
for small values, since `ln(1+x) ≈ x`).

- Default `ε = 0.02` log units ≈ **2%** price tolerance for envelope domination
  and touch detection.
- A high at index `t` **pierces** the line if `y[t] > ŷ(t) + ε`.
- A high **touches** the line if `|y[t] − ŷ(t)| ≤ ε_touch` (touch uses a tighter
  `ε_touch`, default `0.01` ≈ 1%). Touches feed structure-quality scoring later.

**Worked example.** `ŷ(t) = 4.4755` (`line = 87.85`). A high `H = 89.0`,
`y = 4.48864`. Deviation `= 4.48864 − 4.4755 = 0.01314`. With `ε = 0.02`: within
tolerance (does **not** pierce). With `ε_touch = 0.01`: `0.01314 > 0.01` → not a
clean touch, it is a mild overshoot within envelope tolerance.

> **Decision D-TL-06 — Tolerance basis and magnitude** · Default: log-unit
> tolerance, `ε = 0.02` (envelope), `ε_touch = 0.01` (touch). · Alternative:
> ATR-scaled tolerance (volatility-adaptive). · Materiality: med · Human-approval:
> no (tunable; ATR variant is a documented future enhancement).

---

## 10. Invalidation conditions (line becomes stale/dead)

A currently-tracked line is invalidated when **any** of:

1. **Structural break (intervening pierce):** a **bar high** after `A` and before
   the current bar pierces the line beyond `ε` **without** a confirmed breakout
   (§13). This means the descent structure was violated — the line must be
   **recomputed** (§16).
2. **Confirmed breakout occurred and expiry window elapsed** (§16): line resets
   ~100 bars after breakout.
3. **New ATH** forms (a later bar high exceeds `HA`): the old line is retired and
   a new anchor/line is computed from the new ATH.
4. **Insufficient pivots:** fewer than one eligible `B` exists (§17 monotonic
   decline / too-few-bars) → **no line** (not an error; an explicit "no signal"
   state).

Every invalidation MUST emit a **named reason code** (e.g. `INVALID_PIERCE`,
`RESET_NEW_ATH`, `EXPIRED_POST_BREAKOUT`, `NO_VALID_SECOND_ANCHOR`) for
explainability and evidence.

---

## 11. Line states (state machine)

```
NONE ──(valid A,B found)──▶ ACTIVE
ACTIVE ──(bar high pierces > ε, close below)──▶ WICK_BREAK (transient, stays ACTIVE)
ACTIVE ──(FIRST daily close above line + ε_break, §13)──▶ BROKEN_OUT (alert fires here)
ACTIVE ──(new ATH)──▶ NONE (then recompute)
ACTIVE ──(structural pierce, no breakout)──▶ NONE (recompute)
BROKEN_OUT ──(price returns & holds §16)──▶ RETESTED
BROKEN_OUT ──(price closes back below line − ε §15)──▶ FAILED_BREAKOUT
BROKEN_OUT / RETESTED ──(~100 bars elapsed §17)──▶ EXPIRED ──▶ NONE (recompute)
```

State transitions are deterministic functions of the bar stream; each emits a
reason code.

> **Revised per HD-03 (Product Owner, 2026-07-24).** `ACTIVE → BROKEN_OUT` fires on
> the **first** qualifying daily close above the line (§13), so
> `confirmed_bar == breakout_bar`. There is **no 2-bar persistence gate** on this
> transition. Persistence above the line and volume are tracked as post-breakout
> **quality/confidence** signals only; they never gate this transition nor delay
> the alert. The `WICK_BREAK` vs `BROKEN_OUT` distinction is unchanged: `WICK_BREAK`
> is an intrabar-only pierce whose close does **not** clear the line (stays
> `ACTIVE`), whereas `BROKEN_OUT` requires that first **close** above line + ε_break.

---

## 12. (reserved — numbering aligns states/§ for cross-reference)

Touch counting: a **touch** is any bar whose high satisfies the `ε_touch` test
(§9) while the line is `ACTIVE`. The anchors `A` and `B` count as touches 1 and
2. Touch count and spacing feed Confidence (see confidence spec), not this
detector's accept/reject logic.

---

## 13. Confirmed breakout definition

> **Product Owner revised 2026-07-24 (HD-03).** This section is **rewritten**. The
> earlier formulation — "close-based cross **+ 2-bar persistence** + soft volume,"
> where the alert waited for `p_break = 2` consecutive closes and volume was a soft
> qualifier — is **SUPERSEDED**. The governing policy below fires the confirmed
> breakout **ALERT on the first qualifying daily close**, with no mandatory
> multi-bar wait; persistence and volume are moved to the **confidence/quality**
> layer and never gate breakout validity.

### 13.1 Breakout candidate

A **breakout candidate** at bar `t` is the **first daily close above the line +
tolerance**:

```
ln(C[t]) > ŷ(t) + ε_break            # close (not the wick) exceeds the line by tolerance
```

The candidate is the first bar in the current `ACTIVE` episode to satisfy this.

### 13.2 Confirmed breakout ALERT (no multi-bar wait)

A **confirmed breakout** — the state that fires the **ALERT** — is the **first
daily close above the trendline** (i.e. the breakout candidate of §13.1).

- There is **NO mandatory 2-bar (or multi-bar) persistence requirement** on the
  alert/confirmation path. The 2-bar wait is **removed**. The alert fires on that
  **first qualifying daily close**.
- The **breakout bar** and the **confirmed bar** are therefore the **same bar**
  (`confirmed_bar == breakout_bar`) in the revised policy.
- Transition `ACTIVE → BROKEN_OUT` occurs on that first qualifying close (§11).

### 13.3 Persistence — a SEPARATE post-breakout QUALITY feature (does NOT gate)

Whether the close **persists** above the line for subsequent bars is tracked as a
**post-breakout quality signal only**. It feeds the confidence/quality score
(see [`confidence-specification.md`](confidence-specification.md)) as an
explainable component. It **does not gate breakout validity and does not delay
the alert**. A breakout that later fails to persist is still a valid, already-fired
breakout (it may separately become a `FAILED_BREAKOUT` per §15, which is a
distinct labeled outcome, not a retroactive un-firing).

### 13.4 Volume — a CONFIDENCE feature, not a validity gate

Breakout volume is a **confidence input only**. Low volume lowers the confidence
score via a flag/component (e.g. `LOW_VOLUME`) but **never voids a breakout**.
There is **no hard volume gate**. Volume expansion is measured against a reference
(e.g. 20-bar average volume) purely to compute the volume-confirmation confidence
component; validity is independent of it.

### 13.5 Tolerance `ε_break` — versioned & backtestable, NOT a locked 1%

The breakout tolerance is a **versioned, backtestable parameter**, **not** a
permanently locked `ε_break = 0.01`. No fixed value is committed by this spec.
Two candidate tolerance definitions are carried side by side and **evaluated
before any value is locked**:

- a **percentage/log-unit** candidate (deviation above the line as a fraction /
  log units), and
- an **ATR-based** candidate (tolerance scaled by recent Average True Range, i.e.
  volatility-adaptive).

Both are to be **evaluated in Phase 0 (golden fixtures) and Phase 4 (backtest)**;
the governing value/definition is chosen from that evidence and pinned with the
detector's `spec_version`. Until then `ε_break` is an explicit, named,
overridable config parameter with no locked default.

> **Decision D-TL-07 — Breakout confirmation policy** · **Status: REVISED (Product
> Owner, 2026-07-24, HD-03).** · Governing rule: a **breakout candidate** is the
> **first daily close above line + tolerance**; the **confirmed breakout ALERT
> fires on that first qualifying daily close** (`confirmed_bar == breakout_bar`),
> with **no mandatory persistence wait**. **Persistence** above the line and
> **volume** are **confidence/quality features only** — neither gates validity nor
> delays the alert. `ε_break` is a **versioned, backtestable tolerance**
> (percentage-based AND ATR-based candidates, evaluated Phase 0 + Phase 4), **not
> a locked 1%**. · **Superseded formulation:** close + `p_break = 2` persistence +
> soft volume, with a fixed `ε_break = 0.01`. · Rejected alternatives: hard volume
> gate (voids valid breaks); persistence as a validity gate (delays the alert). ·
> Materiality: **high** (defines when the product fires). · Human-approval: yes —
> **revised & granted 2026-07-24 (HD-03).**

**Worked example (revised, single-close confirms).** Line at `t=81`:
`ŷ(81) = 4.3000` (`line ≈ 73.70`), with a candidate tolerance `ε_break = 0.01`
(illustrative only — not a locked value; the governing tolerance is chosen from
Phase 0/Phase 4 evidence and may be ATR-based). `C[80] = 74.2` →
`ln = 4.30680`; `4.30680 > 4.3000 + 0.01 = 4.3100`? No → not yet a candidate.
`C[81] = 76.0` → `ln = 4.33073 > 4.3100` ✓ → this **first qualifying daily close
IS the confirmed breakout**: the **alert fires at `t=81`**, and
`confirmed_bar == breakout_bar == 81`. No second bar is required. Whether
`C[82]`, `C[83]`, … hold above the line only adjusts the **confidence/quality**
score afterward; it does not change that the breakout already fired at `t=81`.

---

## 14. Wick-break definition (and how it differs from breakout)

A **wick-break** at bar `t`: the **intrabar high** crosses the line but the
**close** does not confirm:

```
ln(H[t]) > ŷ(t) + ε      AND      ln(C[t]) ≤ ŷ(t) + ε_break
```

The line **stays ACTIVE**. A wick-break is *not* a signal; it is recorded as a
**rejection with reason `WICK_BREAK`** and contributes (negatively or as
context) to later confidence, and to the touch/pressure history. The essential
difference: **breakout = close-confirmed** (§13); **wick-break = intrabar-only,
close rejected**.

**Worked example.** `ŷ(t) = 4.3000`, `ε = 0.02`. `H[t] = 76 → ln = 4.33073 >
4.3000+0.02 = 4.3200` ✓ wick pierces. `C[t] = 73 → ln = 4.29046 ≤ 4.3100` →
close does not confirm → **WICK_BREAK**, line remains ACTIVE.

---

## 15. Failed breakout definition

After a `BROKEN_OUT` state, a **failed breakout** occurs when price re-closes
decisively **below** the line:

```
ln(C[t]) < ŷ(t) − ε_fail       # default ε_fail = 0.01
within F_fail bars of the breakout bar    # default F_fail = 10 bars
```

Transition `BROKEN_OUT → FAILED_BREAKOUT`, reason `FAILED_BREAKOUT`. A failed
breakout is a first-class labeled outcome (feeds later ML success labels — see
confidence spec §labels).

> **Decision D-TL-08 — Failed-breakout window/threshold** · Default: close back
> below line by `ε_fail = 0.01` within `F_fail = 10` bars. · Alternative: any
> close below line at any time before expiry. · Materiality: med · Human-approval:
> no.

---

## 16. Retest definition

A **retest** strengthens a confirmed breakout: after `BROKEN_OUT`, price returns
toward the **broken line (now acting as support)** and holds:

1. **Return:** within `W_retest` bars of the breakout bar (default `W_retest =
   20`), a bar low approaches the line from above:
   `ln(L[t]) ≤ ŷ(t) + ε_retest` (default `ε_retest = 0.01`) — i.e. price dips to
   the line.
2. **Hold as support:** the **close** of that bar (or within `h_hold = 3` bars)
   is back **at/above** the line: `ln(C) ≥ ŷ(t) − ε_retest`. Price touched and
   held.
3. **No structural failure** (§15) during the window.

Transition `BROKEN_OUT → RETESTED`, reason `RETEST_HELD`. A retest is a positive
confidence contributor.

> **Decision D-TL-09 — Retest window/tolerances** · Default: `W_retest = 20`
> bars, `ε_retest = 0.01`, hold within `h_hold = 3` bars. · Alternative:
> volume-declining retest requirement. · Materiality: med · Human-approval: no.

**Worked example.** Breakout bar `t=81`, line `ŷ(90) = 4.2900` (`line = 72.97`).
`L[90] = 73.1 → ln = 4.29184`; `4.29184 ≤ 4.2900+0.01 = 4.3000` ✓ (dipped to
line). `C[90] = 74.0 → ln = 4.30407 ≥ 4.2900−0.01 = 4.2800` ✓ (held). Within 20
bars of t=81 ✓ → **RETEST_HELD**.

---

## 17. Line expiry & recalculation (~100 bars after breakout)

- **Expiry trigger:** `EXPIRED` when `t − breakoutBar ≥ E_expiry`, default
  `E_expiry = 100` bars. On expiry the line is retired (`→ NONE`) and the
  detector **recomputes** from scratch over the full updated history.
- **Recalculation triggers (any):**
  1. **New ATH** — a bar high exceeds the prior `HA`. Immediate reset: new anchor
     `A`, new envelope, new line. (Old line reason `RESET_NEW_ATH`.)
  2. **New qualifying pivot** that changes the envelope hull (§8) — e.g. a new
     lower-high pivot that becomes the binding `B*`. Recompute the canonical line.
  3. **Structural pierce without breakout** (§10.1) — recompute.
  4. **Post-breakout expiry** (above).
- **Determinism:** recomputation is a pure function of the current full history;
  it never depends on prior mutable state, guaranteeing reproducibility.

> **Decision D-TL-10 — Expiry horizon** · Default: `E_expiry = 100` bars. ·
> Alternative: expiry keyed to volatility/ATR or to retest completion.
> · Materiality: med · Human-approval: no (matches thesis "~100 bars").

---

## 18. Edge cases (deterministic handling, each with a reason code)

| Case | Rule | Reason code |
|------|------|-------------|
| **Fewer than `2k+2` bars** | Cannot confirm any pivot → no line. | `INSUFFICIENT_BARS` |
| **ATH on the first bar** (`tA = 0`) | Valid anchor; `B` is any later eligible pivot. Common for stocks in secular decline from IPO peak. | — |
| **ATH on (or within `k` of) the last bar** | No room for a descending second anchor yet → no line; wait for more bars. | `ATH_TOO_RECENT` |
| **Monotonic decline, no qualifying pivot** | No confirmed pivot below ATH that survives envelope → no line. | `NO_VALID_SECOND_ANCHOR` |
| **Price gaps (overnight)** | Gaps are real bars; no interpolation. Gap-up through the line still requires **close** confirmation (§13). | — |
| **Trading halt** (missing calendar days) | Handled by ordinal indexing (§1); no synthetic bars. Halt does not alter `t` continuity. | — |
| **Unadjusted split slips through** | Detected as an impossible single-bar log jump `|y[t]−y[t−1]| > ln(1.5)` → flag `SUSPECTED_UNADJUSTED_SPLIT`, do not fit. | `SUSPECTED_UNADJUSTED_SPLIT` |
| **Equal ATHs** | Earliest wins (§4, D-TL-02). | — |
| **Ties in envelope (two pivots give identical dominating slope)** | Prefer the **later** `B` (longer confirmed structure). | `ENVELOPE_TIE_LATER` |
| **Non-positive price** | Invalid input, reject bar-set. | `INVALID_PRICE` |
| **Flat-top plateau at a pivot** | Earliest bar of plateau is the pivot (§5 `≥` rule). | — |

---

## 19. Golden examples to produce in Phase 0 (fixtures a later ticket MUST build)

These are **deterministic fixtures** (synthetic OHLCV CSV + expected output
JSON) that Verification will check. No code is built now; this lists what the
build-lifted ticket must produce:

1. **GX-01 Clean single line:** ATH at `t=0`, three descending pivots, one clear
   envelope line, **no** breakout. Expected: `ACTIVE`, correct `A`, `B*`, `m`,
   `b`, touch list.
2. **GX-02 Envelope discrimination:** a shallow candidate line pierced by a mid
   high (like §8 example) — asserts the hull picks `B*=(45,92)`, not `(20,96)`.
3. **GX-03 Wick-break vs breakout:** one bar wick-pierces (rejected
   `WICK_BREAK`), a later bar's **first daily close** above line + `ε_break`
   confirms (`BROKEN_OUT`). **Revised per HD-03 (2026-07-24):** this fixture must
   **no longer require a 2-bar persistence confirmation**. The expected output
   must assert the breakout fires on the **first qualifying close** with
   `confirmed_bar == breakout_bar` (the alert bar is the crossing bar itself).
   Any subsequent above-line closes are expected to appear as **persistence
   *quality* data** feeding confidence, **not** as a precondition of `BROKEN_OUT`.
   The prior expected fixture (breakout confirmed one bar *after* the cross, at
   `t = crossbar + 1`) is **superseded** and must be regenerated to the
   single-close-confirms policy. (Describe/regenerate the fixture when the build
   is lifted — do not build it now.)
4. **GX-04 Retest hold:** post-breakout dip to line that holds → `RETESTED`.
5. **GX-05 Failed breakout:** post-breakout re-close below line within
   `F_fail` → `FAILED_BREAKOUT`.
6. **GX-06 New-ATH reset:** a new all-time high mid-series → `RESET_NEW_ATH`, new
   line recomputed.
7. **GX-07 Expiry:** 100+ bars after breakout → `EXPIRED` → recompute.
8. **GX-08 Monotonic decline:** no valid second anchor → `NO_VALID_SECOND_ANCHOR`.
9. **GX-09 ATH on first bar:** IPO-peak decline; valid line from `t=0`.
10. **GX-10 Split artifact:** an unadjusted 2:1 jump → `SUSPECTED_UNADJUSTED_SPLIT`.
11. **GX-11 Low-volume breakout (volume is confidence-only):** a **first-close**
    breakout on low volume → `BROKEN_OUT` fires normally, with a `LOW_VOLUME`
    flag. **Revised per HD-03 (2026-07-24):** the fixture must assert the breakout
    is **valid and fired** (volume does **not** gate validity); `LOW_VOLUME` is a
    **confidence** signal only, lowering the score, never voiding the signal. The
    fixture must **not** depend on any 2-bar persistence wait. The earlier
    "volume-soft breakout" framing (where volume was a soft *qualifier* on the
    validity path) is **superseded** by "volume is a confidence feature, not a
    validity gate"; regenerate expected output accordingly when the build is lifted.
12. **GX-12 Equal-ATH tie:** duplicate highs → earliest anchors (D-TL-02).

Each fixture's expected JSON must include: selected anchors, `m`/`b`, state,
every reason code emitted, and (for numeric geometry) values to **6 significant
figures**, so Verification is exact and reproducible.

---

## 20. Determinism & reproducibility requirements (binding on implementation)

1. No randomness anywhere in geometry or state transitions.
2. All tolerances/constants (`k, ε, ε_touch, ε_break, ε_fail, ε_retest,
   W_retest, h_hold, F_fail, E_expiry`) are **named config**, versioned with the
   detector. **Per HD-03 (2026-07-24):** `ε_break` is a **versioned, backtestable
   tolerance with NO locked default** (percentage-based **and** ATR-based
   candidates evaluated in Phase 0 + Phase 4 before any value is pinned). The former
   persistence gate `p_break` and volume gate `f_vol` are **removed from the
   validity path**; persistence and volume are now **confidence/quality** inputs
   (see the confidence spec) — any persistence-window or volume-reference constants
   they use live with the confidence scorer, not the validity config.
3. Floating-point comparisons use the stated `ε` buffers; no bare equality on
   prices. Tie rules (D-TL-02, ENVELOPE_TIE_LATER) make outcomes order-stable.
4. Output carries a `spec_version` matching this document's version so evidence
   is traceable.

---

## Glossary additions proposed (for the Product Steward — do NOT self-edit)

The Architect proposes the Product Steward add these to
[`glossary.md`](glossary.md):

- **Anchor (A)** — the all-time-high bar that begins the descending trendline.
- **Second anchor (B / B\*)** — the qualifying later pivot high selected by the
  envelope rule to define the line.
- **Pivot high** — a bar high that is a local maximum over a symmetric `k`-bar
  window.
- **Envelope rule / upper log-hull** — the selection rule choosing the shallowest
  descending log-space line from the ATH that stays above all intervening highs
  within tolerance `ε`.
- **Tolerance ε** — permitted log-unit deviation for domination/touch/breakout.
- **Wick-break** — intrabar high crosses the line while the close does not
  confirm; not a signal.
- **Breakout candidate** — the first daily close above the line + tolerance
  (`ε_break`).
- **Confirmed breakout** — the **first daily close above the line + tolerance**;
  fires the alert on that bar with **no mandatory persistence wait** (revised
  HD-03, 2026-07-24). Persistence above the line and volume are **confidence /
  quality** features, not validity gates.
- **Retest** — post-breakout return to the broken line that holds as support.
- **Failed breakout** — post-breakout re-close below the line within the failure
  window.
- **Line expiry / reset** — retirement/recomputation of the line (~100 bars
  post-breakout, on new ATH, or on structural change).
- **Reason code** — the named machine-readable justification emitted with every
  accept/reject/state transition.

---

## Open questions (for Orchestrator/Steward/human triage)

1. **OQ-1 (D-TL-01, high) — RESOLVED 2026-07-24 (HD-01):** price-adjustment basis
   **approved** split-adjusted, dividend-unadjusted ("as-traded").
2. **OQ-2 (D-TL-04, high) — RESOLVED 2026-07-24 (HD-02):** the **upper-log-hull
   envelope** is **approved** as the canonical line-selection definition.
3. **OQ-3 (D-TL-07, high) — RESOLVED (REVISED) 2026-07-24 (HD-03):** breakout
   confirmation fires on the **first daily close** above line + tolerance (no
   persistence wait); persistence and volume are confidence features; `ε_break` is
   a versioned, backtestable tolerance (%-based and ATR-based, evaluated Phase 0 +
   Phase 4). The prior "close + persistence 2 + soft volume" policy is superseded.
4. **OQ-4:** Should the touch/domination check use pivot highs only or every bar
   high (D-TL-05)? Default hybrid proposed.
5. **OQ-5:** Universe/data-vendor and split/dividend data availability for S&P 500
   (data-layer ticket dependency, not this spec).
6. **OQ-6:** Should very long (multi-decade) histories switch to weekly bars to
   tame pivot noise (D-TL-00)?
