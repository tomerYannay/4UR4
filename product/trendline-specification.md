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

> **Reading order — §21 governs *when* every other rule is evaluated.**
> [§21](#21-as-of-time-rolling-causal-evaluation-semantics--approved-hd-12)
> (**HD-12**, Product Owner 2026-07-25) defines the **as-of-time (rolling causal)**
> evaluation semantics: which bars are visible when a rule is applied, when a line
> first becomes `ACTIVE`, and when the line is frozen. §4–§18 define **what** each
> rule tests; §21 defines **against which line and with which bars visible**. Where
> a section below says "the line", it means `Λ_t` — the line active at the **start**
> of the evaluation bar — as defined in §21.1. §21 is **normative** and overrides any
> reading of §4–§18 that would require future bars.

### Notation

| Symbol | Meaning |
|--------|---------|
| `bar[t]` | The OHLCV bar at integer index `t`, `t ∈ {0,1,…,N−1}`, ascending in time. |
| `H[t], L[t], O[t], C[t], V[t]` | High, low, open, close, volume of `bar[t]`. |
| `y[t]` | Log-price of the high: `y[t] = ln(H[t])` (see §3). |
| `A = (tA, HA)` | Anchor pivot = the all-time-high bar (§4). |
| `B = (tB, HB)` | Second anchor = the qualifying later **bar high** (pivot or not) selected by the all-highs envelope rule (§6, §8). |
| `m` | Slope of the trendline in log space, per bar (§7). |
| `b` | Intercept of the trendline in log space. |
| `ŷ(t) = m·t + b` | The trendline value in log space at index `t`. |
| `line(t) = exp(ŷ(t))` | The trendline value back in price space at index `t`. |
| `ε` | Tolerance, expressed in **log units** (§9). |
| `S_t` | The **available prefix** at evaluation bar `t`: bars `0 … t−1` (§21.1, HD-12). |
| `A_t`, `B*_t` | The as-of-time anchor and canonical second anchor computed **over `S_t`** (§21.1). |
| `Λ_t` | The **line active at the start of bar `t`** — `(A_t, B*_t, m_t, b_t, tolerance_version)`, or `⊥` when no line is eligible (§21.1, §21.3). Capital lambda is used deliberately: `L[t]` already denotes the bar **low**. |
| `Λ^F` | The **frozen event line** captured at a confirmed breakout (§21.5). |
| `t_form` | The **formation bar**: the earliest `t` at which `Λ_t ≠ ⊥` (§21.3). |

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
- **Source:** Real market data, the **4UR4 US Large-Cap 500** universe initially (HD-18;
  per thesis). Data
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

> **As-of-time reading (§21, HD-12).** "Full available delivered history" is
> evaluated **causally**: at evaluation bar `t` the available history is the prefix
> `S_t = bars[0 … t−1]`, so the anchor in force is
> `A_t = (tA, HA)` with `HA = max over S_t of H[·]` and `tA` the **earliest**
> bar of `S_t` attaining it (D-TL-02). The anchor is therefore **provisional**: it
> is the all-time high *of the bars seen so far*. A later bar whose high exceeds
> `HA` is a **new ATH** and triggers the reset of §10.3 / §17.1 / §21.7 — it does
> **not** retroactively re-anchor already-evaluated bars. A detector MUST NOT use
> any bar at index `≥ t` to determine the anchor in force at bar `t`.

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

## 5. Pivot-high rule (fractal / N-bar pivot) — **SECONDARY / NON-AUTHORITATIVE**

> **Product Owner decision 2026-07-25 — resolves SC-2 (upper-log-hull is canonical;
> pivot prefilter is non-authoritative).** The upper-log-hull envelope rule (§8) is
> **canonical** and **MUST NOT depend on a fixed pivot-high prefilter.**
> Specifically:
> 1. **Every valid later bar high may be a second-anchor candidate**, subject to:
>    it occurs after the ATH; its high is below the ATH; it produces a descending
>    log-space slope; and it satisfies the canonical envelope rule + tolerance (§8).
> 2. A bar does **NOT** need to qualify as a `k`-pivot high to become the canonical
>    upper-log-hull anchor.
> 3. **Pivot-high detection is SECONDARY and NON-AUTHORITATIVE.** It may be used
>    only for: **visualization**; **descriptive metadata**; **confidence
>    features**; and **performance optimization ONLY IF proven lossless** against
>    the all-highs canonical calculation.
> 4. A pivot filter **must NEVER change the selected canonical anchor.**
> 5. If a future optimized implementation uses pivot pruning, it **MUST fall back
>    to / verify against the full all-highs upper-hull result.**
> 6. **RM-01 demonstrates why a strict `k=3` precondition is invalid:** 2026-07-21
>    @ 129.88 is **NOT** a `k=3` pivot, yet it **is** the canonical shallowest
>    descending envelope anchor; excluding it would contradict the approved
>    upper-log-hull rule.
>
> **Motivating case: RM-01.** On the Product Owner's original SPCX chart the
> canonical second anchor is **2026-07-21 @ 129.88** — the shallowest descending
> line from the ATH that dominates all later highs (0 envelope violations). That
> bar is only a `k=1` local high (2026-07-17 @ 130.33 is higher within 3 bars), so
> it is **not** a `k=3` pivot. The only `k=3` pivot after the ATH (2026-06-30)
> yields a **steeper** line that does **not** dominate later highs, so a strict
> `k=3` prefilter would **wrongly exclude the correct canonical anchor**. The SC-2
> proof fixture is **GX-19** (`fixtures/golden/GX-19`).

Pivots below are retained **only** for the secondary, non-authoritative uses
listed above (visualization, descriptive metadata, confidence features, and
provably-lossless performance optimization). **Pivot status is not a precondition
for second-anchor candidacy or selection** (§6, §8).

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
> · **NON-AUTHORITATIVE FOR SELECTION (Product Owner 2026-07-25, resolves SC-2):**
> `k` governs only the secondary pivot uses in §5 (visualization / metadata /
> confidence / lossless optimization). It **does not gate second-anchor candidacy
> and must never change the canonical upper-log-hull anchor** (§6, §8). Changing
> `k` — including to any strict value — **cannot** exclude a bar high from
> canonical candidacy.

**Worked example.** Highs (index:value): `0:80 1:120 2:95 3:130 4:110 5:105 6:118
7:112`. With `k = 2`: `t=3` (130) is a pivot (`>` 120,95 left; `≥` 110,105
right). `t=6` (118) is a pivot (`>` 105,110 left; `≥` 112 right, and needs a
right neighbour at `t=8` which is absent → **not confirmable** if it is within
`k` of the end). With enough right bars, `t=6` is a valid pivot.

---

## 6. Second-anchor eligibility

> **Revised per Product Owner decision 2026-07-25 (resolves SC-2, see §5).** The
> pivot-high requirement is **REMOVED** from candidacy and selection. **Candidacy
> is over every later bar high**; pivots are **no longer a precondition**.

The line runs from `A` (the ATH) down to a **second anchor** `B = (tB, HB)`.
**Every later bar high is a candidate.** `B` is eligible iff **all** hold:

1. `tB > tA` — strictly later than the ATH.
2. `HB < HA` — strictly below the ATH (the line descends).
3. The implied slope `m = (yB − yA)/(tB − tA)` is `< 0` (guaranteed by 1 & 2,
   stated for completeness).
4. `B` survives the **envelope rule** (§8) — i.e. the line `A→B` keeps **all
   intervening bar highs** at/below it within tolerance `ε`.

There is **no `isPivotHigh(tB, k)` precondition**: a candidate need **not** be a
confirmed pivot high. The former requirement (previously listed here as
"`isPivotHigh(tB, k)` — `B` is a confirmed pivot high") is **superseded** by the
all-highs candidacy above; pivot detection is secondary and non-authoritative
(§5). A non-pivot bar high can be — and, per the RM-01 / GX-19 case, sometimes
**is** — the canonical anchor.

The **selected** `B*` among all eligible candidates is the canonical upper-log-hull
vertex chosen by the envelope rule in §8 (the shallowest descending line from `A`
that dominates **all later bar highs** within `ε`), **not** "the next pivot" and
**not** restricted to pivots.

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

> **Selection window is AS-OF-TIME (Product Owner 2026-07-25, HD-12 — resolves
> OQ-TL-7).** The algorithm below is evaluated over the **available prefix `S_t`**
> (bars `0 … t−1`), **never** over the full series retroactively. `B*_t` is the
> all-highs upper-log-hull vertex **of `S_t`**. While the line is `ACTIVE`, `B*`
> **rolls forward**: each non-breakout bar's high enters the candidate set and the
> resulting line becomes active from the **next** bar (§21.2 step 4, §21.6). At a
> confirmed breakout the anchors are **frozen** (§21.5). A later high MUST NOT
> re-select `B*` for an event that has already been classified (§21.8). See
> [§21](#21-as-of-time-rolling-causal-evaluation-semantics--approved-hd-12).

> **Candidates are ALL later bar highs (Product Owner 2026-07-25, resolves SC-2).**
> The candidate set is **every** bar high with `t > tA`, **not** a pivot-restricted
> subset. The canonical anchor is the **all-highs upper-log-hull vertex** — the
> shallowest descending line from `A` that dominates all later **bar** highs within
> `ε`. Pivot status is irrelevant to which candidate is selected; a non-pivot bar
> high can be the canonical anchor (see §5 motivating case RM-01, and GX-19).

This is equivalent to walking the **upper convex hull** (in log space) of the
**bar-high point set** (all later highs) to the right of the ATH:

### Algorithm (deterministic)

```
Given anchor A=(tA,yA) and the ordered set H of ALL bar highs with t>tA
  (as-of-time: restricted to the available prefix S_t = bars 0..t-1, §21.1):
1. Consider candidate second anchors B ∈ H with yB < yA (descending).   # ALL highs, not pivots
2. For each candidate B, define ŷ_B(t) = slope(A,B)·(t−tA)+yA.
3. B is ENVELOPE-VALID iff for EVERY bar high (not just pivots) with tA < t_i < tB
   AND for every bar high with t_i > tB:
        y[t_i] ≤ ŷ_B(t_i) + ε          # no bar high pierces the line above tol (D-TL-05)
4. Among ENVELOPE-VALID candidates choose B* = the canonical upper-hull vertex:
   the least-steep (highest / shallowest) descending line that still dominates
   ALL later bar highs — i.e. the FIRST hull vertex after A. Equivalently
   B* = argmax over valid B of slope(A,B) (slope closest to zero). See below.
```

> **Note (pivots are NOT a pre-filter).** A performance-optimized implementation
> MAY prune candidates using pivots **only if** it is proven lossless against this
> all-highs calculation and it **falls back to / verifies against** the full
> all-highs upper-hull result; it must **never** change the selected `B*` (§5).

**Selection rule (canonical).** The canonical line is the **upper convex hull
edge** emanating from `A`: choose `B*` such that **no bar high pierces
the line beyond `ε`** and the line is the **highest** such descending line
(smallest `|m|` that still dominates). Equivalently, `B*` is the **bar high** (any
later bar high, pivot or not) that maximizes the slope `m` (closest to zero, i.e.
shallowest) subject to the domination constraint — because any steeper line would
pass **below** some later high, violating "resistance stays above highs."

> Intuition: resistance must sit **above** the highs it caps. Of all descending
> lines from the ATH that stay above every intervening high, the **lowest**
> (steepest) ones are too aggressive (they cut through highs); the correct one is
> the **upper hull** — the shallowest line that still dominates everything. This
> is the first convex-hull vertex after `A` in log space.

**Worked example (hull selection).** Log-space **later bar highs** (all highs, not
a pivot subset) after `A=(0, y=4.605 [H=100])`:

| bar t | H | y=lnH |
|--------:|----:|--------:|
| 20 | 96 | 4.56435 |
| 45 | 92 | 4.52179 |
| 70 | 80 | 4.38203 |

- Candidate `B=(20,96)`: `m = (4.56435−4.60517)/20 = −0.0020410`. Line at t=45 =
  `4.60517 − 0.0020410·45 = 4.51333`; the bar-high y at 45 is `4.52179` >
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

> **Decision D-TL-05 — Domination set: every bar high** · **REVISED — Product
> Owner 2026-07-25 (resolves SC-2).** Enforce domination against **every bar high**
> for **both** line *selection* **and** line *validity monitoring* (§10). The prior
> default (domination against **pivot highs** for *selection*, every bar high for
> *monitoring*) is **SUPERSEDED**: selection domination is now over **ALL bar
> highs**, so the selected `B*` is the all-highs upper-log-hull vertex and pivots
> never restrict the selection set. · Rationale: the canonical object is the
> all-highs upper log-hull (§8); a pivot-restricted selection could pick a
> different, non-canonical anchor (exactly the SC-2 failure — see RM-01 / GX-19). ·
> Rejected alternative: pivots-only for selection (can exclude the true canonical
> anchor). · Materiality: **high** (defines the selected anchor). · Human-approval:
> yes — **granted 2026-07-25**.

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
4. **No envelope-valid second anchor:** no eligible `B` (§6) survives the envelope
   rule (§8) — e.g. a later bar high **ties the ATH** and pierces every descending
   candidate line beyond `ε` (double top, fixture GX-20), or the series is too
   short (§18) → **no line** (not an error; an explicit "no signal" state).
   **This is never triggered by an absence of pivot highs** — candidacy is over
   every later bar high (§6, D-TL-03, D-TL-05).

Every invalidation MUST emit a **named reason code** (e.g. `INVALID_PIERCE`,
`RESET_NEW_ATH`, `EXPIRED_POST_BREAKOUT`, `NO_VALID_SECOND_ANCHOR`) for
explainability and evidence.

> **As-of-time reconciliation (§21, HD-12).** Every test above is applied to the
> **line active at the start of the evaluation bar** (`Λ_t`, §21.1), using only the
> prefix `S_t`. The **classification** of bar `t` is final for bar `t`; the
> **replacement geometry** it triggers takes effect **from bar `t+1`** and is never
> applied retroactively to bar `t` itself (§21.2 step 4). Specifically:
>
> 1. **§10.1 structural pierce (pre-breakout).** Under all-highs candidacy a high
>    that pierces `Λ_t` beyond `ε` **is itself an envelope-valid candidate** (§21.4,
>    Lemma), so the mandated recomputation always resolves to a **shallower line
>    re-bound at that very bar**: `B*_{t+1} = (t, H[t])`. The bar therefore emits
>    `INVALID_PIERCE` **for the superseded line** and `LINE_ESTABLISHED` for the
>    re-selected line, which becomes active at **`t+1`**; the episode continues
>    (§21.6). The only cases in which recomputation does **not** yield a line are a
>    **new ATH** (§10.3 → `RESET_NEW_ATH`) and a high that **ties or is otherwise
>    incompatible with any descending candidate** (§10.4 → `NO_VALID_SECOND_ANCHOR`,
>    fixture GX-20). **No new reason code is introduced by §21.**
> 2. **§10.2 post-breakout expiry** is measured against the **frozen** line `Λ^F`
>    (§21.5), not against a re-selected one.
> 3. **§10.3 new ATH** is detected as-of-time against the provisional anchor `A_t`
>    (§4 as-of-time note) and starts a **new formation** subject to §21.3.
> 4. **§10.4** is evaluated on `S_t`; the guards of §18 (`INSUFFICIENT_BARS`,
>    `ATH_TOO_RECENT`) are likewise evaluated on `S_t` and are the **formation
>    eligibility** conditions of §21.3 — they keep a degenerate two-point line from
>    ever becoming `ACTIVE`.

---

## 11. Line states (state machine)

```
NONE ──(formation eligibility met on S_t, §21.3: |S_t| ≥ min_formation_bars, ATH not
        within min_ath_age_bars of the last available bar, and an envelope-valid B*
        exists)──▶ ACTIVE
ACTIVE ──(bar high pierces > ε, close below)──▶ ACTIVE, recorded as WICK_BREAK
        (WICK_BREAK is a REASON CODE, not a state: the machine never leaves ACTIVE.
         The fixture schema's `from`/`to` enum excludes it for that reason.)
ACTIVE ──(FIRST daily close above line + ε_break, §13)──▶ BROKEN_OUT (alert fires here;
        the line is FROZEN as Λ^F at the start-of-bar state, §21.5)
ACTIVE ──(new ATH)──▶ NONE (then recompute; new formation from t+1, §21.7)
ACTIVE ──(structural pierce, no breakout)──▶ ACTIVE with a re-selected B* effective t+1
        (§10 note, §21.6; → NONE only if §10.3 or §10.4 applies)
BROKEN_OUT ──(price returns & holds §16)──▶ RETESTED
BROKEN_OUT ──(price closes back below line − ε §15)──▶ FAILED_BREAKOUT
BROKEN_OUT / RETESTED ──(~100 bars elapsed §17)──▶ EXPIRED ──▶ NONE (recompute)
```

State transitions are deterministic functions of the bar stream; each emits a
reason code.

> **As-of-time reading (§21, HD-12).** Every transition out of `ACTIVE` is decided
> by comparing bar `t` against `Λ_t` — the line built from `S_t` only. Every
> transition is **final for that bar**: once emitted, a transition MUST NOT be
> revised, re-labelled, or withdrawn by any later bar (§21.8). Before `t_form`
> (§21.3) the state is `NONE` with reason `INSUFFICIENT_BARS` or `ATH_TOO_RECENT`
> (§18); while the state is `NONE` no breakout, wick-break, retest or failure event
> can be emitted, because there is no line to test against. While the state is
> `BROKEN_OUT` or `RETESTED`, **anchor re-selection is suspended** — the frozen line
> `Λ^F` governs (§21.5) — so the transitions still available (`RETEST_HELD`,
> `FAILED_BREAKOUT`, `EXPIRED_POST_BREAKOUT`, `RESET_NEW_ATH`) are **all** evaluated
> against `Λ^F`, never against a re-selected line.

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

> **As-of-time reading (§21, HD-12).** A touch at bar `t` is evaluated against `Λ_t`
> (§21.1) — the line active at the **start** of bar `t` — and is final for that bar
> (§21.8). Because `B*` may roll forward before a breakout (§21.6), the anchor pair
> counted as touches 1 and 2 is the pair of the line **in force at the time of the
> count**; at a confirmed breakout it is the frozen pair of `Λ^F` (§21.5). Touch
> counting is a confidence input only, so this never affects accept/reject logic.

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
ln(C[t]) > ŷ_t(t) + ε_break          # close (not the wick) exceeds the line by tolerance
                                     # ŷ_t = the line Λ_t ACTIVE AT THE START of bar t (§21.1)
```

The candidate is the first bar in the current `ACTIVE` episode to satisfy this.

> **As-of-time reading (§21, HD-12) — binding.** `ŷ_t(t)` is the value at index `t`
> of `Λ_t`, the line computed from the **available prefix `S_t` = bars `0 … t−1`**.
> Bar `t`'s own high MUST NOT enter the candidate set used to build the line against
> which bar `t`'s close is judged (§21.2 steps 1–2): **the evaluation bar may never
> redefine the line that judges it.** "First bar in the current `ACTIVE` episode"
> means the first bar whose close clears **the line that was active at the start of
> that bar** — the comparison line may legitimately differ from bar to bar as `B*`
> rolls forward (§21.6). On a confirmed breakout the line is **frozen** as `Λ^F`
> (§21.5) and every downstream test (§15 failure, §16 retest, §17 expiry) uses
> `Λ^F`.

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

> **As-of-time reading (§21, HD-12) — "stays ACTIVE" ≠ "geometry unchanged."** Both
> tests use `ŷ_t`, the line `Λ_t` active at the **start** of bar `t`. Because bar `t`
> produced no confirmed breakout, §21.2 step 4 applies: its high enters the candidate
> set and, since `y[t] > ŷ_t(t)` by construction of a wick-break, it **re-selects**
> `B*` — `B*_{t+1} = (t, H[t])` (§21.4 Lemma) — effective from bar `t+1`. The
> **state** remains `ACTIVE` (correct, per §11) while the **line geometry** legitimately
> shallows. A wick-break is therefore also a re-selection event and MUST be recorded
> as both (`WICK_BREAK` plus `LINE_ESTABLISHED` for the line effective at `t+1`, and
> `INVALID_PIERCE` for the superseded line when the pierce exceeded `ε` — §10 note).

---

## 15. Failed breakout definition

After a `BROKEN_OUT` state, a **failed breakout** occurs when price re-closes
decisively **below** the line:

```
ln(C[t]) < ŷ_F(t) − ε_fail     # default ε_fail = 0.01
                               # ŷ_F = the FROZEN event line Λ^F (§21.5), NOT a re-selected line
within F_fail bars of the breakout bar    # default F_fail = 10 bars
```

> **As-of-time reading (§21, HD-12).** After `BROKEN_OUT` the geometry is **frozen**:
> `ŷ_F(t) = m^F·t + b^F` from the `Λ^F` captured at the start of the breakout bar
> (§21.5). Anchor re-selection is suspended (§21.6), so a post-breakout high MUST NOT
> shift the line used by this test. The failure window `F_fail` is counted from the
> frozen `breakout_bar`.

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
toward the **broken line (now acting as support)** and holds.

> **As-of-time reading (§21, HD-12) — the retest line is the FROZEN line.** "The
> broken line" is `Λ^F` (§21.5): the exact `A`, `B*`, slope, intercept and tolerance
> version that were active at the **start of the breakout bar**. This is the line the
> market actually broke, which is precisely what retest semantics require. Every
> `ŷ(t)` below therefore means `ŷ_F(t)`. Post-breakout highs MUST NOT re-select `B*`
> (§21.6), and the retest window `W_retest` is counted from the frozen
> `breakout_bar`.

Conditions:

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
  `E_expiry = 100` bars, measured from the **frozen** `breakout_bar` (§21.5) and
  evaluated against the frozen line `Λ^F`. On expiry the line is retired (`→ NONE`)
  and the detector **recomputes** from scratch over the full **available** history
  (the prefix, §21.1) — never over bars the detector has not yet reached.
- **Recalculation triggers (any):**
  1. **New ATH** — a bar high exceeds the prior `HA`. Immediate reset: new anchor
     `A`, new envelope, new line. (Old line reason `RESET_NEW_ATH`.)
  2. **New bar high that changes the envelope hull** (§8) — e.g. a new lower high
     that becomes the binding `B*`. Pivot status is irrelevant to this trigger:
     **any** later bar high can re-bind the hull (§6, §8, D-TL-05). Recompute the
     canonical line.
  3. **Structural pierce without breakout** (§10.1) — recompute.
  4. **Post-breakout expiry** (above).
- **Determinism:** recomputation is a pure function of the **bars available at the
  time of recomputation** (the prefix `S_t`, §21.1) — never of bars at index `≥ t`;
  it never depends on prior mutable state, guaranteeing reproducibility. (Amended by
  HD-12: the earlier phrase "the current **full** history" is read as the **available**
  history as of the recomputation bar; recomputing from the complete series would be
  look-ahead and is prohibited by §21.8.)

> **As-of-time reading (§21, HD-12) — triggers 1–4 restated causally.**
>
> - **Trigger 1 (new ATH)** is detected against the provisional anchor `A_t` (§4
>   as-of-time note). Reset is immediate for classification purposes at bar `t`; the
>   **new** line becomes active no earlier than `t+1` and only when formation
>   eligibility (§21.3) is met again for the new anchor (§21.7).
> - **Trigger 2 (hull re-bind) is the OQ-TL-7 question and is now decided by HD-12.**
>   It fires **only while the line is `ACTIVE`**, only on bars that produced **no**
>   confirmed breakout, and the re-selected line is effective from **`t+1`**
>   (§21.2 step 4, §21.6). It is **suspended** while `BROKEN_OUT` / `RETESTED`
>   (§21.5). It MUST NOT be applied retroactively to any already-classified bar.
> - **Trigger 3 (structural pierce)** is the same event as trigger 2 whenever the
>   piercing bar produced no breakout — under all-highs candidacy the piercing bar is
>   itself the new binding `B*` (§10 note, §21.4 Lemma). The distinction is only in
>   the reason codes emitted, not in the resulting geometry.
> - **Trigger 4 (expiry)** is evaluated against the frozen line `Λ^F`; on expiry the
>   detector returns to `NONE` and recomputes from `S_{t+1}`, so the replacement line
>   is active from `t+1` at the earliest, subject to §21.3.
>
> **General rule:** *no line ever takes effect on the bar that caused it to be
> computed.*

> **Decision D-TL-10 — Expiry horizon** · Default: `E_expiry = 100` bars. ·
> Alternative: expiry keyed to volatility/ATR or to retest completion.
> · Materiality: med · Human-approval: no (matches thesis "~100 bars").

---

## 18. Edge cases (deterministic handling, each with a reason code)

| Case | Rule | Reason code |
|------|------|-------------|
| **Fewer than `min_formation_bars` bars available** | Minimum-history guard → no line. `min_formation_bars` is a **first-class, versioned, `k`-independent parameter** (default **8**, D-TL-12); it replaces the former pivot-derived `2k+2` formulation with **no change of value** at `k = 3`. **Evaluated as-of-time on the prefix `S_t`** (§21.1): the guard blocks formation while `t < min_formation_bars`, so the earliest possible formation bar is `t = min_formation_bars` (§21.3). | `INSUFFICIENT_BARS` |
| **ATH on the first bar** (`tA = 0`) | Valid anchor; `B` is any later eligible **bar high** (§6 — pivot status is not a precondition). Common for stocks in secular decline from IPO peak. Fixtures GX-09, GX-08. | — |
| **ATH within `min_ath_age_bars` of the last *available* bar** | No room for a descending second anchor yet → no line; wait for more bars. `min_ath_age_bars` is a **first-class, versioned, `k`-independent parameter** (default **3**, D-TL-12); it replaces the former pivot-derived `k`-recency window with **no change of value** at `k = 3`. **Evaluated as-of-time**: the last available bar at evaluation bar `t` is `t−1`, so the guard blocks formation while `tA > (t−1) − min_ath_age_bars`, i.e. until `t ≥ tA + min_ath_age_bars + 1` (§21.3). It constrains the **anchor `A`**, never the candidacy of any `B` — no bar high is excluded from selection for being near the end of the series (HD-11, HD-12 rule 6). | `ATH_TOO_RECENT` |
| **No envelope-valid second anchor** — e.g. a later bar high **ties the ATH** (double top) and so pierces every descending candidate line beyond `ε` | Eligible candidates exist (§6: all later bar highs with `HB < HA`) but **none** survives the envelope test of §8 → no line. Fixture **GX-20**. **A strictly monotonic decline can never emit this code**: its first later bar high is always eligible and the hull binds there (fixture **GX-08**, `B* = (1,98)`). The former "no qualifying pivot" trigger is **superseded** — the absence of pivot highs is never a reason for this code (§5, §6, D-TL-03, D-TL-05, HD-11). | `NO_VALID_SECOND_ANCHOR` |
| **Price gaps (overnight)** | Gaps are real bars; no interpolation. Gap-up through the line still requires **close** confirmation (§13). | — |
| **Trading halt** (missing calendar days) | Handled by ordinal indexing (§1); no synthetic bars. Halt does not alter `t` continuity. | — |
| **Unadjusted split slips through** | Detected as an impossible single-bar log jump `\|y[t]−y[t−1]\| > ln(1.5)` → flag `SUSPECTED_UNADJUSTED_SPLIT`, do not fit. | `SUSPECTED_UNADJUSTED_SPLIT` |
| **Equal ATHs** | Earliest wins (§4, D-TL-02). | — |
| **Ties in envelope (two candidate bar highs give identical dominating slope)** | Prefer the **later** `B` (longer confirmed structure). | `ENVELOPE_TIE_LATER` |
| **Non-positive price** | Invalid input, reject bar-set. | `INVALID_PRICE` |
| **Flat-top plateau at a pivot** | Earliest bar of plateau is the pivot (§5 `≥` rule). | — |

> **Note — the two formation guards are `k`-INDEPENDENT parameters (D-TL-12,
> approved 2026-07-25, HD-14; resolves OQ-TL-8).** Under HD-12 these guards became
> **outcome-determining**: they decide `t_form`, the first bar at which any event can
> be classified, and therefore which line the earliest evaluable bars are judged
> against. A parameter that determines events may not be a by-product of the pivot
> window `k`, which HD-11 declared **non-authoritative**. They are therefore restated
> as **first-class, named, versioned, backtestable parameters**:
>
> | Parameter | Default | Replaces | Constrains |
> |---|---|---|---|
> | `min_formation_bars` | **8** | the pivot-derived `2k+2` | minimum available history `\|S_t\|` |
> | `min_ath_age_bars` | **3** | the pivot-derived `k`-recency window | the age of the **anchor `A`** only |
>
> - **No value changed.** At the former `k = 3` the old formulation gave `2k+2 = 8`
>   and `k = 3`; the new parameters are numerically identical. The change is one of
>   *status*, not of behaviour: `k` may now be re-tuned freely — for pivot
>   visualization, descriptive metadata or confidence features — **without moving a
>   single event on a single fixture or backtest**. Regression fixtures **GX-21**,
>   **GX-22** and **GX-23** lock exactly that, and `tools/fixture-replay.mjs
>   --formation` asserts it mechanically by replaying every fixture at
>   `k ∈ {1,2,3,4,5,8}` and requiring byte-identical transitions, anchors and states.
> - **Why the guards exist at all** (their justification, restated free of pivots):
>   under all-highs candidacy the *geometric* minimum for a line is `A` plus one later
>   lower high — **two bars**. A two-point line over the opening bars has arbitrary
>   steepness, and under causal evaluation the next close clears it almost trivially,
>   manufacturing a spurious `BROKEN_OUT` at `t = 2`–`t = 3`. `min_formation_bars`
>   refuses to fit a canonical line on a window too short to exhibit structure;
>   `min_ath_age_bars` refuses to anchor on an all-time high that the market has not
>   yet had a chance to descend from. Both are conservatism, not pivot confirmability.
> - **`min_ath_age_bars` constrains the ANCHOR only.** It removes **no** candidate `B`
>   from the §6/§8 set and never changes `B*` for a formed line (HD-11, HD-12 rule 6).
>   The barred rule — "bars within `k` of the end are excluded from **selection**" —
>   would contradict RM-01, whose approved canonical **`B*` sits 3 bars from the end of
>   its series**; RM-01's **anchor** is not near the end, so this guard does not touch it.
> - Both codes stay **distinct** from `NO_VALID_SECOND_ANCHOR`, which concerns the §8
>   envelope test on a series that *is* long enough (fixture **GX-20**).
>
> > **Decision D-TL-12 — Formation parameters are first-class and `k`-independent** ·
> > **Status: APPROVED (Product Owner, 2026-07-25, HD-14) — resolves OQ-TL-8.** ·
> > Governing rule: formation eligibility is gated by the named parameters
> > `min_formation_bars` (default 8) and `min_ath_age_bars` (default 3), evaluated
> > as-of-time on `S_t` (§21.3). Neither is derived from the pivot window `k`;
> > changing `k` MUST NOT move any event. · Superseded formulation: `2k+2` minimum
> > history and a `k`-bar ATH-recency window, both justified by pivot confirmability. ·
> > Rejected alternatives: (a) keep the §18 guards expressed in `k` — leaves a
> > non-authoritative parameter determining events; (c) relax toward the two-bar
> > geometric minimum — reinstates the degenerate two-point line the guards exist to
> > prevent. · Materiality: **high** (decides `t_form`, hence which events can fire). ·
> > Human-approval: yes — **granted 2026-07-25 (HD-14)**. · Values are **versioned and
> > backtestable**: they are pinned with the detector's `spec_version` and carried
> > explicitly in every fixture's `params`.

---

## 19. Golden examples to produce in Phase 0 (fixtures a later ticket MUST build)

These are **deterministic fixtures** (synthetic OHLCV CSV + expected output
JSON) that Verification will check. No code is built now; this lists what the
build-lifted ticket must produce:

1. **GX-01 Clean single line:** ATH at `t=0`, a clean descending sequence, one clear
   envelope line that never re-binds, **no** breakout. Expected: `ACTIVE`, correct `A`,
   `B*`, `m`, `b`. **Revised 2026-07-25 (HD-12 audit):** the earlier wording ("three
   descending pivots", "touch list") described a pivot-framed design that the all-highs
   rule (HD-11) makes irrelevant — the redesigned fixture contains **one** confirmed `k=3`
   pivot and pivot count is not a property it asserts. Touch counting (§12) is a confidence
   input and is not asserted by any fixture.
2. **GX-02 Envelope discrimination:** a shallow candidate line pierced by a mid
   high (like §8 example) — asserts the hull picks `B*=(45,92)`, not `(20,96)`.
3. **GX-03 Wick-break (stays ACTIVE):** one bar wick-pierces beyond `ε` while its close
   fails to confirm → `WICK_BREAK`, state remains `ACTIVE`, and under §21.6 that same bar
   re-selects `B*` effective `t+1`. **Corrected 2026-07-25 (HD-12 audit):** this entry
   previously required GX-03 to end `BROKEN_OUT`, which the fixture has never done — the
   *first-close-breakout* behaviour it described is locked by **GX-16** (and, with volume,
   by GX-11). The HD-03 policy statement it carried is retained there. GX-03's job is the
   wick-vs-close distinction alone.
4. **GX-04 Retest hold:** post-breakout dip to line that holds → `RETESTED`.
5. **GX-05 Failed breakout:** post-breakout re-close below line within
   `F_fail` → `FAILED_BREAKOUT`.
6. **GX-06 New-ATH reset:** a new all-time high mid-series → `RESET_NEW_ATH`, new
   line recomputed.
7. **GX-07 Expiry:** 100+ bars after breakout → `EXPIRED_POST_BREAKOUT` → `NONE` → recompute.
8. **GX-08 Monotonic decline — the hull binds at the first later bar:** strictly
   decreasing highs (`100, 98, 96 … 72`) contain **zero** `k=3` pivots, yet
   all-highs candidacy still yields a canonical anchor `B* = (1, 98)` →
   `LINE_ESTABLISHED`, end state `ACTIVE`. A pivot-restricted prefilter would find
   **no** candidate and wrongly emit `NO_VALID_SECOND_ANCHOR`. **Revised
   2026-07-25 (HD-11 / SC-2):** the earlier expectation ("no valid second anchor →
   `NO_VALID_SECOND_ANCHOR`") rested on the pivot precondition that §6 removed and
   is **superseded**; GX-08 is now the **second HD-11 regression fixture** beside
   GX-19 (GX-19: a non-pivot bar is the canonical anchor; GX-08: a series with no
   pivots at all still has one).
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
13. **GX-20 Duplicate ATH (double top) → no envelope-valid second anchor:** a bar
    high **ties** the ATH **before `min_formation_bars`**, so at *every* evaluable
    prefix the shallowest descending candidate is already pierced by it beyond `ε` →
    `NO_VALID_SECOND_ANCHOR`, permanently. This is the **genuinely reachable** case
    for that reason code after HD-11 (§18); it is decided purely on the envelope
    test, never on pivot status. **Revised 2026-07-25 (HD-12 audit):** the first
    construction placed the tie *after* formation, so a line legitimately formed and
    broke out before the tie ever existed — a full-series design that §21.8 outlaws.
    The tie must precede formation for the property to hold causally.
14. **GX-21 / GX-22 / GX-23 Formation-gate regressions (D-TL-12, HD-14):** three
    fixtures that isolate the formation gates — `min_formation_bars` binding alone
    (GX-21), `min_ath_age_bars` binding alone after a new-ATH reset (GX-22), and
    eligibility holding with **zero** confirmed pivots in the formation prefix
    (GX-23). Together they lock: no formation before either gate; formation
    *immediately* once both are met and `B*` exists; and complete independence from
    the pivot window `k`.

*(The complete, superseding catalog — GX-01 … GX-23, including the SC-2 proof
GX-19 — is maintained in [`fixtures/README.md`](fixtures/README.md) §3.)*

Each fixture's expected JSON must include: selected anchors, `m`/`b`, state,
every reason code emitted, and (for numeric geometry) values to **6 significant
figures**, so Verification is exact and reproducible.

> **Binding on fixtures and backtests (HD-12 rule 7, §21.8).** Every expected value
> MUST be derived **as-of-time**: each bar's classification is computed against the
> line built from bars strictly before it (§21.2), and **no fixture may use a later
> bar to establish, revise, or withdraw an earlier bar's classification**. A single
> full-series hull computed over the complete fixture series is **not** a valid
> derivation of an expected event unless it is demonstrably identical to the
> as-of-time result.
>
> **Audit status — COMPLETE (2026-07-25).** Every fixture in the set has been
> re-derived as-of-time. Each `expected.json` now carries a **`causal_record`** block
> holding the per-gate formation trace, the as-of-time candidate set, the active `B*`
> and line value before every event bar, each event's margin, every pre-breakout
> re-selection, the frozen `Λ^F`, the later non-retroactive challengers, an
> `ε_break` robustness sweep and a descriptive pivot context. The whole set is
> re-checked mechanically by `tools/fixture-replay.mjs`, which additionally asserts
> the §21.4 hull lemma against the §8 brute-force recomputation **at every evaluable
> prefix**, prefix-truncation invariance (§21.8), the frozen-line invariants (§21.5)
> and the formation-gate regressions (§21.3, D-TL-12).

---

## 20. Determinism & reproducibility requirements (binding on implementation)

1. No randomness anywhere in geometry or state transitions.
2. All tolerances/constants (`k, ε, ε_touch, ε_break, ε_fail, ε_retest,
   W_retest, h_hold, F_fail, E_expiry, min_formation_bars, min_ath_age_bars`) are
   **named config**, versioned with the detector. **Per D-TL-12 (2026-07-25,
   HD-14):** `min_formation_bars` and `min_ath_age_bars` are **first-class formation
   parameters independent of `k`** — they are pinned with `spec_version`, are
   backtestable, and changing `k` MUST NOT move any event (asserted by
   `tools/fixture-replay.mjs --formation`). **Per HD-03 (2026-07-24):** `ε_break` is a **versioned, backtestable
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
5. **Causal (as-of-time) evaluation is a determinism requirement (HD-12, §21).**
   Every emitted event MUST be a pure function of the bars **available at or before
   the evaluation bar** (`S_t ∪ {bar[t]}`). Streaming the series bar-by-bar and
   batch-processing the whole series MUST produce **identical** output — this
   equivalence is the operational test for "no look-ahead" (§21.8) and SHOULD be
   asserted by Verification. A confirmed breakout additionally carries its **frozen**
   line `Λ^F` (`A`, `B*`, `m`, `b`, `tolerance_version`, §21.5) so that retest,
   failure and expiry evidence is reproducible from the event record alone.

---

## 21. As-of-time (rolling causal) evaluation semantics — **APPROVED: HD-12**

> **Product Owner approved 2026-07-25 (HD-12) — resolves OQ-TL-7.** **Anchor selection
> uses rolling, causal, as-of-time evaluation while the trendline is `ACTIVE`.** It
> is **neither** a final full-series calculation that may use future bars
> retroactively, **nor** a permanently frozen anchor from the first moment a valid
> line forms. This section states that ruling normatively and makes it computable.
> It is governing; §4–§18 are read through it.
>
> **Placement note.** This section is **appended** rather than inserted between §9
> and §10 deliberately: the 20 golden fixtures and `fixtures/README.md` cross-reference
> this document by **section number**, so renumbering would silently break evidence
> links. §21 is normative over the *timing* of §4–§18 regardless of its position;
> each affected section carries an explicit back-reference.

### 21.1 Definitions (precise and computable)

Let `k`, `ε`, `ε_break`, `ε_fail`, `ε_retest`, `W_retest`, `F_fail`, `E_expiry`,
`min_formation_bars` and `min_ath_age_bars` be the named config of §20.

- **Available prefix.** `S_t := bars[0 … t−1]` — every bar strictly before the
  evaluation bar `t`. `|S_t| = t`. `S_0 = ∅`.
- **As-of-time anchor.** `A_t := (tA, HA)` where `HA = max_{i ∈ S_t} H[i]` and `tA`
  is the **earliest** `i ∈ S_t` attaining it (§4, D-TL-02). Undefined for `S_t = ∅`.
- **As-of-time second anchor.** `B*_t :=` the canonical all-highs upper-log-hull
  vertex of §8 computed with the candidate set restricted to
  `{ i ∈ S_t : i > tA }`, with domination tested over **all bar highs in `S_t`**
  (D-TL-05) and ties broken by `ENVELOPE_TIE_LATER` (§18). `B*_t = ⊥` when no
  candidate is envelope-valid (§10.4).
- **Line active at the start of bar `t`.**
  ```
  Λ_t := ( A_t, B*_t, m_t, b_t, tolerance_version )      if FORMATION_ELIGIBLE(t)   (§21.3)
       := ⊥  (no line; state NONE)                        otherwise
  m_t = ( y[tB*_t] − y[tA] ) / ( tB*_t − tA )
  b_t = y[tA] − m_t · tA
  ŷ_t(u) = m_t · u + b_t
  ```
  `Λ_t` depends on **`S_t` only**. Bar `t` itself is **not** an input to `Λ_t`.
- **Formation bar.** `t_form :=` the least `t` with `Λ_t ≠ ⊥` for the current anchor
  episode. Re-computed afresh after every `RESET_NEW_ATH` and every
  `EXPIRED_POST_BREAKOUT` (§21.7).
- **Frozen event line.** `Λ^F :=` the value of `Λ_t` at the bar `t` on which a
  confirmed breakout fired, retained verbatim (§21.5).

### 21.2 Authoritative processing order for evaluation bar `t` (normative)

A conforming detector MUST process each bar in exactly this order.

1. **Build the line from the past only.** At the start of bar `t`, the active
   canonical line MUST be `Λ_t`, calculated **only from bars available through
   `t−1`**. Bars at index `≥ t` MUST NOT influence `Λ_t`.
2. **Evaluate bar `t` against that pre-existing line.** Bar `t`'s wick (§14), close
   (§13), breakout, touch (§12), failure (§15) and retest (§16) tests MUST be
   evaluated against `Λ_t` (or `Λ^F` where §21.5 applies) — never against a line
   that already includes `H[t]`.
3. **Freeze on confirmed breakout.** If bar `t` produces a confirmed breakout
   (§13.2), the detector MUST **freeze** the exact `A`, `B*`, slope `m`, intercept
   `b`, tolerance version and line that were active at the **start of bar `t`** as
   `Λ^F`, and MUST use `Λ^F` for breakout, retest, failure and expiry semantics.
   **Later highs MUST NOT retroactively replace `B*` for that event** (§21.5).
4. **Otherwise roll the anchor forward.** If bar `t` does **not** produce a
   confirmed breakout, the detector MUST incorporate `H[t]` into the candidate set,
   recompute the all-highs upper-log-hull canonical `B*` over `S_{t+1} = S_t ∪
   {bar[t]}`, and the resulting line MUST become active **beginning with bar `t+1`**
   — i.e. `Λ_{t+1}`. It MUST NOT be applied to bar `t` (§21.6).
5. **New ATH resets.** If `H[t] > HA` of `A_t`, the previous structure is
   invalidated (`RESET_NEW_ATH`, §10.3) and a **new formation** begins from the new
   anchor, subject to §21.3 (§21.7). **Ordering:** this test is evaluated on bar `t`
   **before** steps 3 and 4 and takes precedence over both — a bar that makes a new
   ATH resets the structure and MUST NOT be recorded as a breakout of the retired
   line, nor roll its `B*` forward.
6. **Pivot status and end-of-series proximity are non-authoritative for
   selection.** No candidate `B` may be excluded from §6/§8 candidacy because it is
   not a `k`-pivot (HD-11) **or** because it lies close to the end of the currently
   available series (HD-12 rule 6). The only end-of-series condition in this spec
   constrains the **anchor `A`** at **formation** time (`ATH_TOO_RECENT`, §18,
   §21.3), never the selection of `B*`.
7. **No look-ahead.** Backtests and fixtures MUST NOT use future bars to revise an
   earlier event classification (§21.8).

### 21.3 Formation eligibility — when a line FIRST becomes `ACTIVE`

**Normative rule.**

```
FORMATION_ELIGIBLE(t)  iff  all of:
  (F1)  |S_t| ≥ min_formation_bars        # §18 INSUFFICIENT_BARS, read as-of-time
  (F2)  tA ≤ (t − 1) − min_ath_age_bars   # §18 ATH_TOO_RECENT, read as-of-time
  (F3)  B*_t ≠ ⊥                          # §6 candidacy + §8 envelope test on S_t
                                          # (§10.4 NO_VALID_SECOND_ANCHOR otherwise)
```

Equivalently, the earliest bar at which a line can be `ACTIVE` is

```
t_form = min { t : t ≥ min_formation_bars
                 ∧ t ≥ tA + min_ath_age_bars + 1
                 ∧ B*_t ≠ ⊥ }
```

`min_formation_bars` (default **8**) and `min_ath_age_bars` (default **3**) are
**first-class, named, versioned, backtestable parameters — independent of the pivot
window `k`** (D-TL-12, HD-14). Neither may be derived from `k`, and changing `k` MUST
NOT move `t_form` or any event. The three gates are evaluated **independently**, so an
implementation and an auditor can always say which one binds; fixtures record that
per-gate trace in `causal_record.formation.gate_trace`.

and for every `t < t_form` the state is `NONE`, with reason code
`INSUFFICIENT_BARS`, `ATH_TOO_RECENT` or `NO_VALID_SECOND_ANCHOR` respectively (the
first unmet condition in the order F1, F2, F3).

**Emission form while `NONE` (normative — added 2026-07-25; an encoding, not a rule).**
The reason above is a **standing condition**, not a per-bar event, so a conforming detector
records it **once per contiguous `NONE` run**, at the first bar of that run — not once per
bar. Two consequences, both relied on by the fixtures: a run whose reason is merely
`INSUFFICIENT_BARS` at the head of a series is **not** recorded as an event at all (every
series begins short, so the record would carry no information); and a reason that *changes*
within a `NONE` run, or a new `NONE` run opened by a reset, starts a new record. Fixtures
GX-06 and GX-22 (`ATH_TOO_RECENT` after a new-ATH reset), GX-20 (`NO_VALID_SECOND_ANCHOR`
permanently) and GX-12 (the same, transiently) encode exactly this. While the state is `NONE` **no**
breakout, wick-break, retest or failure event may be emitted (§11) — there is no line
to test against, and a bar that cannot be evaluated MUST NOT be evaluated later.

**Derivation (this rule invents nothing; every element is already approved).**

1. **HD-12 rule 1** fixes the visible data: at evaluation bar `t` the active line is
   calculated **only from bars available through `t−1`**. Therefore "the available
   series", "the delivered history" and "the last bar" — the phrases §4, §10 and §18
   are written in — all denote `S_t` and its last element `t−1` when evaluated at bar
   `t`. Re-reading those existing predicates on `S_t` is a **mechanical consequence**
   of HD-12, not a new rule.
2. **§18, row 1** (approved; value unchanged, now named `min_formation_bars` per
   D-TL-12): fewer than `min_formation_bars` bars → **no line**,
   `INSUFFICIENT_BARS`. On `S_t` this is `|S_t| = t ≥ min_formation_bars` ⇒ **(F1)**.
3. **§18, row 3** (approved; value unchanged, now named `min_ath_age_bars` per
   D-TL-12): ATH on, or within `min_ath_age_bars` of, the **last bar** → no line,
   "wait for more bars", `ATH_TOO_RECENT`. This row is **already written in
   as-of-time language** ("wait for more bars" presupposes a rolling evaluation). On
   `S_t` the last bar is `t−1`, so the guard is `(t−1) − tA ≥ min_ath_age_bars`
   ⇒ **(F2)**.
4. **§6 + §8 + §10.4** (approved): a line exists only if some later bar high is
   eligible and survives the envelope test; otherwise `NO_VALID_SECOND_ANCHOR` and
   **no line** — an explicit "no signal" state, not an error. On `S_t` ⇒ **(F3)**.
5. **§11** (approved): the transition into `ACTIVE` is `NONE ──(valid A,B
   found)──▶ ACTIVE`; there is no other entry into `ACTIVE`. So `ACTIVE` at bar `t`
   ⟺ F1 ∧ F2 ∧ F3 on `S_t`. The conjunction is therefore forced, not chosen.
6. **HD-11 and HD-12 rule 6 are respected.** (F2) constrains only the **anchor
   `A`** — the phrasing §18 already uses ("ATH on … the last bar"). It removes **no**
   candidate `B` from the §6/§8 set, and once a line has formed it plays no further
   part. This is exactly the distinction HD-12's constraint bullet draws: the barred
   rule is "bars within `k` of the end are excluded from **selection**", which would
   contradict RM-01, whose approved canonical **`B*`** sits 3 bars from the end of its
   series. RM-01's **anchor** is not near the end, so (F2) does not touch it.
7. **Why the alternatives are excluded, not merely disfavoured.**
   - *Evaluate the guards once over the complete delivered series* (so a line may be
     `ACTIVE` from `t = 2` because the **whole** series happens to be long enough) —
     excluded by HD-12 rules 1 and 7: it uses the length of the unseen remainder to
     license an earlier line, which is look-ahead.
   - *Drop the guards as pivot-derived and let a line form as soon as `A` plus one
     later lower high exist* — excluded by D-TL-12, which **retains both values** and
     merely renames them free of `k`. It is also the degenerate case the guards exist
     to prevent: a two-point line over the first bars has arbitrary steepness, and
     under causal evaluation the next close clears it almost trivially, manufacturing
     a spurious `BROKEN_OUT` at `t = 2`–`t = 3`.
   - *Invent a new "enough structure" threshold* (e.g. require `n` dominated highs or
     `n` touches before forming) — excluded: no approved rule states one, and this
     spec introduces **no new threshold**.
8. **After a reset**, `S_t` keeps growing but the anchor changes, so (F1) is a
   condition on **total available history** and (F2) a condition on **history since
   the anchor**; both are the literal readings of §18 and they compose without
   ambiguity: a new ATH late in a long series satisfies (F1) immediately and must
   still wait out (F2). Fixture **GX-22** locks exactly this composition.

> **Numerically nothing changed; the parameters' STATUS did.** `min_formation_bars =
> 8` and `min_ath_age_bars = 3` are the former `2k+2` and `k` values at `k = 3`,
> unchanged (earliest formation at `t = 8` for an ATH at `t = 0`). What D-TL-12
> (HD-14) changed is that they are now **first-class, versioned, `k`-independent**
> parameters rather than by-products of a pivot window HD-11 declared
> non-authoritative — so re-tuning `k` can never move an event.
>
> **Regression evidence (binding).** The binding evidence is the **fixtures**; the replay
> harness is a convenience for re-checking them, never itself a source of the rule.
>
> | Property | Locked by (binding evidence) |
> |---|---|
> | No line is ever `ACTIVE` before `min_formation_bars` | **GX-21** — F2 and F3 are already satisfied from `t = 4` and `t = 2`, so F1 alone binds and the line forms at exactly `t = 8` |
> | No line is ever `ACTIVE` within `min_ath_age_bars` of its own anchor | **GX-22** — F1 stays satisfied across a new-ATH reset at `t = 12`, so F2 alone binds; `ATH_TOO_RECENT` at `t = 13…15` and `ACTIVE` at exactly `t = 16` |
> | Formation happens **immediately** once all three gates hold — not one bar later | every fixture's recorded `t_form`, each equal to the least `t` satisfying F1 ∧ F2 ∧ F3 |
> | Pivot status never affects eligibility **or selection** | **GX-08** (a series with zero pivots still has a canonical anchor), **GX-19** and **GX-23** (the canonical `B*` is a non-pivot bar), and 9 of the 20 geometry fixtures whose `B*` is not a confirmed pivot. **GX-23** additionally forms on the same bar as **GX-21** with a structurally different prefix |
>
> `tools/fixture-replay.mjs --formation` re-checks all of the above mechanically and adds a
> positive control (perturbing either gate must change an outcome, so the checks cannot pass
> vacuously). Note that `k`-independence of *this rule* is **structural, not empirical**: the
> formation predicate does not mention `k`, so a `k`-sweep cannot fail and is not offered as
> proof — the fixtures above are.

### 21.4 `Λ_t` in closed form — the running-max lemma (computability)

The normative definition of `B*_t` is the §8 recomputation over `S_t`. The following
**Lemma** makes it computable in `O(1)` per bar and — more importantly — makes the
semantics **reconstructible by an auditor**.

**Lemma (rolling hull = running maximum slope).** Let a line exist at bar `t` with
anchor `A_t` unchanged at `t+1` (bar `t` is neither a new ATH nor an ATH tie). Then

```
slope_t(i) := ( y[i] − y[tA] ) / ( i − tA )

B*_t  = argmax_{ i ∈ S_t, i > tA }  slope_t(i)      (later i wins ties — ENVELOPE_TIE_LATER)

B*_{t+1} = (t, H[t])   if  y[t] ≥ ŷ_t(t)            # bar t's high reached or exceeded the line
         = B*_t         otherwise
```

*Proof sketch.* (i) Adding a point to the candidate set only **adds** domination
constraints, so a candidate that was envelope-invalid cannot become valid. (ii) If
`y[t] ≤ ŷ_t(t)` then `Λ_t` still dominates every point of `S_{t+1}`, so `B*_t` remains
envelope-valid and remains the maximum-slope valid candidate ⇒ `B*_{t+1} = B*_t`.
(iii) If `y[t] > ŷ_t(t)` then `slope(A, (t,H[t])) > m_t`, and because the candidate
line through `(t, H[t])` is **shallower** than `Λ_t` it lies at or above `Λ_t` for all
`u > tA`; every earlier high satisfied `y[u] ≤ ŷ_t(u) + ε`, hence also
`y[u] ≤ ŷ_new(u) + ε` — so the new candidate is envelope-valid. No candidate with a
still-greater slope can exist (it would already have been selected at `t`), so the new
candidate is the maximum ⇒ `B*_{t+1} = (t, H[t])`. (iv) Equality `y[t] = ŷ_t(t)` gives
identical slopes and `ENVELOPE_TIE_LATER` selects the later bar; the geometry is
unchanged. ∎

**Consequences (all normative unless marked).**

- **`B*` re-binds exactly when a high reaches the active line** — `y[t] ≥ ŷ_t(t)` —
  and the new `B*` is **that bar**. Nothing else moves the anchor.
- `m_t` is **monotonically non-decreasing** in `t` within an episode: the causal line
  can only **shallow**, never steepen, while `A` is unchanged.
- *(Non-normative corollary — auditable invariant.)* With the same anchor in force,
  the running maximum over `S_t` is never greater than the maximum over the complete
  series, so for every `u > tA` the causal line `Λ_t` lies **at or below** the
  full-series line. Consequently a close that clears the full-series line also clears
  the causal line, and **the first as-of-time breakout of an episode occurs at or
  before the first full-series breakout — never after, and it may exist where the
  full-series calculation reports none.** An audit converting a full-series
  expectation to as-of-time MUST expect breakouts to **appear or move earlier**, and
  MUST treat "a first breakout moved later or disappeared" as a **defect in the
  conversion**, not as a finding. (Post-breakout geometry is not comparable this way:
  the frozen line `Λ^F` is by the same argument at or below the full-series line, so
  failure/retest tests are evaluated against a **lower** line than a full-series
  derivation would use.)
- The Lemma is an **optimization, not the definition**: like the pivot pruning of §5
  and §8, an implementation MAY use it **only if** it is lossless against the §8
  recomputation over `S_t`, and MUST fall back to the full recomputation whenever the
  anchor changes, a candidate ties the ATH, or `B*_t = ⊥` (§10.4).

> **The line a detector REPORTS for a series (normative — added 2026-07-25; an encoding,
> not a rule).** `Λ_t` and `Λ^F` define which line judges which bar. Separately, a detector
> asked "what is this name's line?" reports: **the frozen event line `Λ^F` if a confirmed
> breakout occurred anywhere in the series — retained even after `EXPIRED_POST_BREAKOUT`,
> because it is the line the market actually broke — and otherwise `Λ_n`**, the line in
> force after the last available bar. This is what every fixture's `expected_second_anchor`,
> `expected_log_slope` and `expected_intercept` denote. Note the deliberate consequence:
> GX-07 reports `B* = (6, 94)` while its `expected_final_state` is `NONE`, because the line
> expired but the event it carried is still the reportable one.

### 21.5 Freeze on confirmed breakout

When bar `t` produces a confirmed breakout (§13.2), the detector MUST capture the
frozen event line `Λ^F` **exactly as it stood at the start of bar `t`**:

| Frozen field | Meaning |
|--------------|---------|
| `A = (tA, HA)` | anchor in force at the start of bar `t` |
| `B* = (tB*, HB*)` | canonical second anchor in force at the start of bar `t` |
| `m` | log-space slope of `Λ_t` |
| `b` | log-space intercept of `Λ_t` |
| `tolerance_version` | the named tolerance set in force (`ε`, `ε_touch`, `ε_break`, `ε_fail`, `ε_retest`) — `ε_break` is versioned and unlocked (§13.5, HD-03) |
| `breakout_bar = confirmed_bar = t` | the alert bar (§13.2, HD-03) |

Binding consequences:

- **§15 failure**, **§16 retest** and **§17 expiry** MUST be evaluated against `Λ^F`
  (`ŷ_F(u) = m^F·u + b^F`), because that is the line the market actually broke.
- Anchor **re-selection is suspended** from bar `t` onward for that episode: while the
  state is `BROKEN_OUT` or `RETESTED`, §21.2 step 4 does **not** run and no later high
  may replace `B*`.
- `Λ^F` MUST be emitted with the event so that downstream evidence is reproducible
  from the event record alone (§20.5).
- The only exits are `RESET_NEW_ATH` (§21.7) and `EXPIRED_POST_BREAKOUT` (§17); both
  return the detector to `NONE`, after which a **new** formation is subject to §21.3
  and takes effect no earlier than the following bar.

### 21.6 Re-selection before breakout (the pre-breakout roll)

While the state is `ACTIVE` and bar `t` produced **no** confirmed breakout:

- The detector MUST incorporate `H[t]` and recompute `B*` over `S_{t+1}` (§21.2 step
  4). Per §21.4 this changes the anchor **iff** `y[t] ≥ ŷ_t(t)`.
- The re-selected line is `Λ_{t+1}` and is effective **from bar `t+1`**. **The
  evaluation bar MUST NEVER redefine the line against which its own event is judged**
  — this is the single most important invariant of §21 and the guarantee that no
  event is created or destroyed by its own bar.
- The state remains `ACTIVE` (§11): *"stays ACTIVE" does not mean "geometry
  unchanged."*
- Reason codes (existing codes only — §21 introduces none): `LINE_ESTABLISHED` for the
  line effective at `t+1`; additionally `INVALID_PIERCE` for the superseded line when
  `y[t] > ŷ_t(t) + ε` (§10.1); additionally `WICK_BREAK` when the close also failed to
  confirm (§14). A single bar may legitimately emit all three.
**Event-record form (normative — added 2026-07-25; decides no rule, fixes the encoding).**
§21.6 states *which* codes a re-selection emits but not where they are recorded, and the
golden fixtures cannot be a determinate contract without that. The following makes explicit
what §21.2 and §21.9 already imply; it changes no classification and no threshold.

1. **Bar attribution.** A re-selection is recorded at the bar the re-selected line takes
   **effect** (`t+1`), not at the bar that caused it. This is §21.9's own presentation —
   *"`LINE_ESTABLISHED`, **effective at bar 21**"* for a hull that re-bound during bar 20.
   The causing bar records its own event (`WICK_BREAK`, `INVALID_PIERCE`) at `t`.
2. **Within-bar ordering.** Records for a single bar are ordered by §21.2's processing
   order: the line effective at bar `t` is established in **step 1**, so `LINE_ESTABLISHED`
   (and `ENVELOPE_TIE_LATER`, where the slopes tie) precede any event that bar produces in
   steps 2–4. A conforming emitter MUST NOT record a line as established *after* the event
   it was used to judge.
3. **State-machine coherence.** The emitted transition sequence MUST be a valid walk of
   §11: each record's `from` state equals the previous record's `to`, and the final `to`
   equals the reported end state. A re-selection while `ACTIVE` is an `ACTIVE → ACTIVE`
   record.
   *One corner this ordering does settle, named explicitly rather than left implicit:*
   a bar that both takes a re-selection **and** makes a new ATH now records
   `LINE_ESTABLISHED` (the line effective at that bar) followed by `RESET_NEW_ATH` — a
   line established and retired within one bar. §21.2 rule 5 was silent on an incoming
   re-selection, so this was previously under-determined; no fixture depends on it.
4. **Transition records vs reason codes.** A record with a `from`/`to` pair is emitted for
   every event that the detector must be able to replay in order. `INVALID_PIERCE` is a
   *characterisation of the superseded line* rather than an event of its own, so it is
   carried in the emitted reason-code set alongside the `WICK_BREAK` record for that bar
   rather than duplicating it. This is why §21.6 says a single bar "may emit all three":
   three **codes**, across two records at two bars.

- If instead the recomputation yields `B*_{t+1} = ⊥` (§10.4 — e.g. a high that **ties**
  the ATH and pierces every descending candidate beyond `ε`, fixture GX-20), the state
  becomes `NONE` with `NO_VALID_SECOND_ANCHOR` from `t+1`, and §21.3 governs any later
  re-formation.

### 21.7 New-ATH reset (HD-12 rule 5)

If `H[t] > HA` of the anchor `A_t` in force:

- The previous structure is invalidated immediately for bar `t`'s classification, with
  `RESET_NEW_ATH` (§10.3, §17 trigger 1). This applies whether the state was `ACTIVE`,
  `BROKEN_OUT` or `RETESTED` — a new ATH overrides a frozen line.
- Bar `t` MUST NOT be classified as a breakout of the retired line by virtue of the same
  high: a close above a line whose high made a new ATH is a **reset**, not a breakout.
  (Rule 5 takes precedence over §21.2 step 3.)
- A **new formation** begins with anchor `A_{t+1}` (which is `(t, H[t])` unless an
  earlier equal high exists, D-TL-02) and is subject to §21.3 — in particular (F2)
  means the new line cannot become `ACTIVE` until at least `min_ath_age_bars` bars after
  the new anchor are available. (This gate is `k`-independent — D-TL-12, HD-14; it read
  `k` before that decision and is numerically unchanged at `k = 3`.)
- An `H[t]` that **equals** `HA` is **not** a new ATH (D-TL-02 keeps the earliest bar as
  the anchor); it is handled by §21.6 / §10.4 (the GX-20 double-top case).

### 21.8 No look-ahead — binding on backtests, fixtures and evidence

1. A detector, backtest or fixture MUST NOT use any bar at index `≥ t` to establish,
   revise, re-label or withdraw the classification of bar `t`.
2. A classification, once emitted, is **final for that bar**. A later bar may add a new
   event (a failure, a retest, an expiry) but may never rewrite an earlier one. A
   breakout that later fails is a `FAILED_BREAKOUT` (§15) — **not** a retroactively
   un-fired breakout (§13.3).
3. **Operational test (SHOULD be asserted by Verification):** streaming the series
   bar-by-bar and batch-processing the whole series MUST yield identical output
   (§20.5).
4. Any expected value derived from a **full-series** hull is valid evidence only if it
   is demonstrably identical to the as-of-time result (§19 note). Where it is not, the
   fixture MUST be re-derived under §21 by a dedicated audit.

### 21.9 Worked micro-example (three bars: a re-selection, then a breakout + freeze)

Setup: `min_formation_bars = 8` (so the earliest possible formation bar is `t = 8`),
`min_ath_age_bars = 3`, `k = 3` (descriptive only), `ε = 0.02`,
illustrative `ε_break = 0.01` (**not** a locked value — §13.5). Anchor `A = (0, 100)`,
`yA = ln 100 = 4.6051702`. Suppose that at the start of bar 20 the rolling hull has
selected `B*_20 = (18, 88)`, `y = ln 88 = 4.4773368`:

```
m_20 = (4.4773368 − 4.6051702) / 18 = −0.00710186
b_20 = 4.6051702
ŷ_20(20) = 4.6051702 − 0.00710186·20 = 4.4631331     → line(20) = 86.7589
```

**Bar 20 — evaluated against `Λ_20`, then re-selects (step 1 → 2 → 4).**
`H[20] = 88.00` (`y = 4.4773368`), `C[20] = 87.00` (`ln = 4.4659081`).

- Breakout test (§13.1): `4.4659081 > 4.4631331 + 0.01 = 4.4731331`? **No** → no
  breakout.
- Wick test (§14): `4.4773368 > 4.4631331 + 0.02 = 4.4831331`? **No** → not even a
  wick-break (the high is above the line but inside `ε`).
- Step 4 (§21.6): no breakout ⇒ incorporate `H[20]`. Since
  `y[20] = 4.4773368 ≥ ŷ_20(20) = 4.4631331`, the hull **re-binds**:
  `B*_21 = (20, 88)`, `m_21 = (4.4773368 − 4.6051702)/20 = −0.00639167`. Reason code
  `LINE_ESTABLISHED`, **effective at bar 21**. Bar 20's own classification is
  unaffected by this — the line that judged bar 20 was `Λ_20`.

**Bar 21 — breakout against `Λ_21`, freeze (step 1 → 2 → 3).**
`ŷ_21(21) = 4.6051702 − 0.00639167·21 = 4.4709451` → `line(21) = 87.4393`.
`C[21] = 88.50` (`ln = 4.4830025`).

- Breakout test: `4.4830025 > 4.4709451 + 0.01 = 4.4809451` ✓ (margin `0.0020574`)
  → **confirmed breakout**, `breakout_bar = confirmed_bar = 21`, `BREAKOUT_CONFIRMED`
  (§13.2, HD-03 — no persistence wait).
- **Freeze (§21.5):** `Λ^F = { A=(0,100), B*=(20,88), m=−0.00639167, b=4.6051702,
  tolerance_version }`.

**Bar 22 — the freeze binds; a later high MUST NOT re-select.**
`H[22] = 90` (`y = ln 90 = 4.4998097`).

- Under a **full-series** (rejected) reading, `(22, 90)` would be a shallower
  envelope-valid vertex: `m = (4.4998097 − 4.6051702)/22 = −0.00478911`, giving
  `ŷ(21) = 4.5045989` — and bar 21's close (`4.4830025`) would then sit **below** the
  line, so **the already-fired breakout would vanish retroactively**. That is exactly
  the look-ahead HD-12 prohibits.
- Under §21: re-selection is **suspended** (state `BROKEN_OUT`). Bar 22 is evaluated
  against the frozen line: `ŷ_F(22) = 4.6051702 − 0.00639167·22 = 4.4645535` →
  `line(22) = 86.8822`; §15/§16/§17 all use this value. `H[22]` does not exceed the
  prior `HA = 100`, so §21.7 does not fire.

> **Decision D-TL-11 — As-of-time (rolling causal) evaluation** · **Status: APPROVED
> (Product Owner, 2026-07-25, HD-12) — resolves OQ-TL-7.** · Governing rule: bar `t` is
> evaluated against `Λ_t`, the canonical all-highs upper-log-hull line built from bars
> `0 … t−1`; a non-breakout bar rolls `B*` forward effective `t+1`; a confirmed
> breakout **freezes** `A`, `B*`, `m`, `b`, tolerance version and line for
> breakout/retest/failure/expiry; a new ATH starts a new formation; formation
> eligibility is the §18 guards read as-of-time (§21.3). · Superseded/rejected
> alternatives: **full-series retroactive selection** (look-ahead; a later high could
> rewrite an earlier classification) and **permanently frozen at formation** (prevents
> a developing line from updating before any breakout). · Materiality: **high**
> (determines which events fire and when). · Human-approval: yes — **granted
> 2026-07-25 (HD-12).**

---

## Glossary additions proposed (for the Product Steward — do NOT self-edit)

The Architect proposes the Product Steward add these to
[`glossary.md`](glossary.md):

- **Anchor (A)** — the all-time-high bar that begins the descending trendline.
- **Second anchor (B / B\*)** — the qualifying later **bar high** (pivot or not)
  selected by the all-highs envelope rule to define the line (revised 2026-07-25,
  SC-2; pivot status is not a precondition).
- **Pivot high** — a bar high that is a local maximum over a symmetric `k`-bar
  window; **secondary / non-authoritative** for line selection (visualization,
  descriptive metadata, confidence features, and provably-lossless optimization
  only — §5, 2026-07-25 SC-2 decision).
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
- **As-of-time (rolling causal) evaluation** — evaluating each bar against a line
  built only from strictly earlier bars, so no classification can depend on future
  bars (§21, HD-12).
- **Available prefix (`S_t`)** — the bars `0 … t−1` visible when bar `t` is
  evaluated (§21.1).
- **Active line at bar `t` (`Λ_t`)** — the canonical line computed from `S_t` and in
  force for bar `t`'s tests (§21.1).
- **Formation eligibility / formation bar (`t_form`)** — the conditions under which a
  line first becomes `ACTIVE` (minimum available history, anchor not too recent, an
  envelope-valid `B*` exists) and the earliest bar satisfying them (§21.3).
- **Anchor re-selection (pre-breakout roll)** — a non-breakout bar whose high reaches
  the active line re-binds `B*` to that bar, effective from the **next** bar (§21.6).
- **Frozen event line (`Λ^F`)** — the `A`, `B*`, slope, intercept and tolerance
  version captured at the start of a confirmed-breakout bar, governing retest,
  failure and expiry (§21.5).

---

## Open questions (for Orchestrator/Steward/human triage)

> **Identifier namespace (added 2026-07-25 — resolves an identifier collision).**
> The open questions below are **local to this specification** and are numbered
> `OQ-TL-n`, mirroring this document's own `D-TL-nn` decision convention. They are
> **distinct** from the product-level open questions `OQ-n` in
> [`requirements.md`](requirements.md), which is **precedence 3** and governs. Before
> this change both registers used a bare `OQ-n`, so `OQ-7` denoted the
> anchor-selection-window question here and the external Fear & Greed
> source/redistribution question there — two different questions with one label.
> **Mapping:** every `OQ-n` previously cited *in this document* is now `OQ-TL-n`
> (same number, namespaced); every `OQ-n` in `requirements.md` is unchanged. Cite
> `OQ-TL-7` for the as-of-time selection window (resolved by HD-12) and `OQ-TL-8` for
> the formation-gate question (resolved by HD-14); `OQ-7`/`OQ-8` without the `TL`
> always mean the `requirements.md` entries.


1. **OQ-TL-1 (D-TL-01, high) — RESOLVED 2026-07-24 (HD-01):** price-adjustment basis
   **approved** split-adjusted, dividend-unadjusted ("as-traded").
2. **OQ-TL-2 (D-TL-04, high) — RESOLVED 2026-07-24 (HD-02):** the **upper-log-hull
   envelope** is **approved** as the canonical line-selection definition.
3. **OQ-TL-3 (D-TL-07, high) — RESOLVED (REVISED) 2026-07-24 (HD-03):** breakout
   confirmation fires on the **first daily close** above line + tolerance (no
   persistence wait); persistence and volume are confidence features; `ε_break` is
   a versioned, backtestable tolerance (%-based and ATR-based, evaluated Phase 0 +
   Phase 4). The prior "close + persistence 2 + soft volume" policy is superseded.
4. **OQ-TL-4 (D-TL-05, high) — RESOLVED 2026-07-25 (resolves SC-2):** selection
   domination uses **every bar high** (not pivots-only); the canonical anchor is
   the all-highs upper-log-hull vertex and **pivot detection is
   non-authoritative** (§5, §6, §8). Proof fixture: **GX-19**.
5. **OQ-TL-5 — PARTLY RESOLVED 2026-07-26 (HD-18):** the universe is the **4UR4 US
   Large-Cap 500**, 4UR4's own point-in-time set, **not licensed S&P 500 membership**
   (`docs/architecture/universe-methodology.md`). Data-vendor and split/dividend
   availability remain open under **HD-06** (still PENDING) — a data-layer ticket
   dependency, not this spec.
6. **OQ-TL-6:** Should very long (multi-decade) histories switch to weekly bars to
   tame pivot noise (D-TL-00)?
7. **OQ-TL-7 (high) — RESOLVED 2026-07-25 (HD-12):** anchor selection is **rolling,
   causal, as-of-time** while the line is `ACTIVE` — **neither** full-series
   retroactive **nor** permanently frozen at formation. Bar `t` is evaluated against
   the line built from bars `0 … t−1`; a non-breakout bar rolls `B*` forward
   effective `t+1`; a confirmed breakout **freezes** the line for
   breakout/retest/failure/expiry; a new ATH starts a new formation; formation
   eligibility is the §18 guards read as-of-time. Specified normatively in **§21**
   (D-TL-11). Both rejected alternatives are recorded there. **Evidence
   consequence — DISCHARGED 2026-07-25:** every fixture expectation derived by
   full-series calculation has been **re-derived as-of-time** by the dedicated audit
   (§19 note, §21.8). The causal result was identical for GX-08, GX-10, GX-12 and
   GX-18 and different for every other fixture; the in-place
   `geometry_check.open_issue_2026_07_25` flags on GX-03, GX-09 and GX-15 are resolved
   and removed, and every fixture now carries a full `causal_record`.
   *History (the question as raised, retained per the decision-history rule):* over
   **what window** is the §8 selection evaluated — the
   **full history** (so a later, shallower, envelope-valid bar high **re-selects**
   `B*` under §17 trigger 2, even while the current line is `ACTIVE` and unpierced)
   or **frozen at line formation** (later bars only *validate*)? Before HD-11 the
   pivot precondition answered this implicitly: a bar within `k` of the series end
   could not be a confirmed pivot and so could not be selected. HD-11 removed that
   exclusion **without stating a replacement**, and §6 imposes no end-window
   condition on `B`. This is **material**: it contests the stated anchors of
   fixtures **GX-09** (full-history vertex would be `t=14`, H=135) and **GX-15**
   (`t=28`, H=87.90), both flagged in place under
   `geometry_check.open_issue_2026_07_25` and in `fixtures/VERIFICATION.md`.
   **Constraint on any answer:** RM-01's Product-Owner-approved canonical anchor is
   itself only 3 bars from the end of its series, so "bars within `k` of the series
   end are excluded from **selection**" would contradict RM-01 and HD-11. Requires a
   Product Owner decision; **no fixture geometry has been changed pending it**.
8. **OQ-TL-8 (high) — RESOLVED 2026-07-25 (HD-14):** the formation gate is restated
   as **first-class, `k`-independent constants** — option (b). `min_formation_bars`
   (default **8**) and `min_ath_age_bars` (default **3**) replace the pivot-derived
   `2k+2` and `k`-recency formulations **at identical values**, are versioned with the
   detector's `spec_version`, are carried explicitly in every fixture's `params`, and
   are backtestable. Tuning the pivot window `k` can no longer move any event.
   Specified normatively in §18 and §21.3 (**D-TL-12**); locked by regression fixtures
   **GX-21**, **GX-22**, **GX-23** and by the `--formation` assertions of
   `tools/fixture-replay.mjs`, which replay every fixture at `k ∈ {1,2,3,4,5,8}` and
   require identical output.
   *History (the question as raised, retained per the decision-history rule):* HD-12
   made **formation eligibility** (§21.3) outcome-determining — `t_form` decides the
   first bar at which any event can fire and which line the earliest evaluable bars
   are judged against. §21.3 originally derived it from the **existing, numerically
   unchanged** §18 guards (`2k+2` minimum available history; ATH not within `k` of the
   last available bar), because those were the approved rules and no new threshold
   could be invented. But that made `k` — declared **non-authoritative for selection**
   (D-TL-03, HD-11) — authoritative for **formation timing**. The options put to the
   Product Owner were (a) keep the §18 guards as-is, (b) restate them as first-class
   `k`-independent constants, (c) relax them toward the geometric minimum. **(b) was
   approved.** Rejected: (a) leaves a non-authoritative parameter determining events;
   (c) reinstates the degenerate two-point line the guards exist to prevent.
