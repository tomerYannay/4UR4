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
  **Pivots are SECONDARY / NON-AUTHORITATIVE for selection** (Product Owner decision
  2026-07-25, resolves SC-2): they serve only visualization, descriptive metadata, confidence
  features, and provably-lossless optimization — they never gate second-anchor candidacy.
- Second anchor `B* = (tB, HB)`: the **all-highs upper log-hull** selection (§6, §8, D-TL-04,
  D-TL-05) — the shallowest descending log line from `A` that dominates **all later bar
  highs** (not a pivot subset) within tolerance `eps`. Candidacy is over **every** later bar
  high; a non-pivot bar high can be the canonical anchor (see GX-19 / RM-01).
- Line geometry (§7):
  - slope `m = (yB - yA) / (tB - tA)`
  - intercept `b = yA - m * tA`
  - line value in log space `y_hat(t) = m*t + b`
  - line value in price space `line(t) = exp(y_hat(t))`
- Breakout / wick / retest / failure / expiry tests: §11, §13–§17, with the revised HD-03
  policy (breakout fires on the **first** qualifying daily close; `confirmed_bar ==
  breakout_bar`; persistence and volume are confidence-only, never validity gates).
- **Evaluation window: AS-OF-TIME (§21, HD-12, D-TL-11) — binding on every expected value.**
  Bar `t` is judged against `Λ_t`, the canonical line built from the available prefix
  `S_t = bars 0…t−1` only. A non-breakout bar's high then enters the candidate set and the
  recomputed line takes effect from `t+1` (§21.6); a confirmed breakout **freezes** `A`,
  `B*`, `m`, `b` and the tolerance version as `Λ^F`, which governs failure, retest and
  expiry (§21.5). No fixture may use a later bar to establish, revise or withdraw an
  earlier bar's classification (§21.8).
- **Formation (§21.3, D-TL-12):** a line first becomes `ACTIVE` at the least `t` satisfying
  `|S_t| ≥ min_formation_bars` **and** `tA ≤ (t−1) − min_ath_age_bars` **and** an
  envelope-valid `B*_t` exists. Both parameters are `k`-independent (HD-14).

Every `expected.json` carries a `geometry_check` block restating `yA`, `yB`, the slope /
intercept formulas, and the key inequality evaluations, plus a **`causal_record`** block
holding the machine-derived as-of-time evidence (formation-gate trace, candidate set,
active `B*` before each event bar, event margins, re-selections, frozen line, later
non-retroactive challengers, `eps_break` sweep, descriptive pivot context). An independent
verifier can confirm the arithmetic by hand from `geometry_check`, or mechanically with
`node tools/fixture-replay.mjs --all`. All rounding is to **6 significant figures**, and
the replay harness compares the 6-significant-figure rounding **exactly** rather than with
a fuzzy tolerance; where hand computation of `exp()` leaves ambiguity at the 6th figure,
the `geometry_check` inequalities (not the rounded display value) are the authority.

## 3. Fixture catalog

> **Every expected value below is AS-OF-TIME (§21 / HD-12 / D-TL-11).** Each bar is
> judged against the line built from bars strictly earlier than it; no expectation
> uses a full-series hull. `t_form` is the bar at which the line first becomes
> `ACTIVE` under the formation gates `min_formation_bars = 8` and
> `min_ath_age_bars = 3` (§21.3, D-TL-12). Every `expected.json` carries a
> **`causal_record`** block with the per-gate formation trace, the as-of-time
> candidate set, the active `B*` before each event bar, each event margin, every
> pre-breakout re-selection, the frozen event line `Λ^F`, the later non-retroactive
> challengers, an `ε_break` robustness sweep and a descriptive pivot context. The
> whole set is re-derived and re-checked by `node tools/fixture-replay.mjs --all`.

| ID | Category | Key expected outcome (as-of-time) | `t_form` | Governing `B*` | Final state | Spec section(s) |
|----|----------|-----------------------------------|---------:|----------------|-------------|-----------------|
| GX-01 | normal valid | Clean line, no re-selection, no breakout | 8 | (6, 93.00) | **ACTIVE** | §4–§8, §11, §21.3 |
| GX-02 | multiple competing second anchors | Envelope discrimination as a causal roll: `B*` (7,95.5) → (20,96) → **(45,92)**; the t=45 high pierces the (20,96) line beyond `eps=0.005`, exactly the spec §8 rejection | 8 | (45, 92.00) | **ACTIVE** | §8, §10.1, §17, §21.6 |
| GX-03 | wick-only crossing | Intrabar pierce, close rejects → `WICK_BREAK`, stays ACTIVE — and the same bar re-selects `B*` effective t=17 | 8 | (16, 86.00) | **ACTIVE** | §11, §14, §21.6 |
| GX-04 | clean retest | Breakout t=16, dip to the **frozen** line holds t=20 → `RETESTED` | 8 | (6, 93.00) | **RETESTED** | §13, §16, §21.5 |
| GX-05 | false breakout | Breakout t=16, decisive close below the frozen line t=20 → `FAILED_BREAKOUT`; the failing bar lies **entirely below** the line (high 76.50 < line 78.5133), so price never trades back at the broken level — a *physical* contrast with GX-17, since §15 fires first in both | 8 | (6, 93.00) | **FAILED_BREAKOUT** | §15, §21.5 |
| GX-06 | expiry & recalculation (new-ATH recompute) | New ATH t=10 → `RESET_NEW_ATH` (**not** a breakout — §21.2 rule 5); `ATH_TOO_RECENT` until the new anchor ages; new line ACTIVE at t=14 | 8, then 14 | (13, 103.00) | **ACTIVE** | §10.3, §17, §21.7 |
| GX-07 | expiry & recalculation | Breakout t=10, then `E_expiry` bars above the frozen line → `EXPIRED_POST_BREAKOUT` at t=110 → NONE | 8 | (6, 94.00) frozen | **NONE** (post-expiry) | §13, §17, §21.5 |
| GX-08 | monotonic decline — **HD-11 regression** | Strictly decreasing highs contain **zero** k=3 pivots, yet the all-highs hull binds at the **first** later bar | 8 | (1, 98.00) | **ACTIVE** | §6, §8, §18, D-TL-03/05 |
| GX-09 | normal valid variant (ATH on first bar) | IPO-peak decline; the t=10 high pierces and re-binds `B*` to (10,150) while its close stays below the line | 8 | (10, 150.00) | **ACTIVE** | §4, §6–§8, §21.6 |
| GX-10 | stock split edge case | Unadjusted ~2:1 jump → `SUSPECTED_UNADJUSTED_SPLIT`, no geometry at any prefix | n/a | — | **NONE** | §2, §18 |
| GX-11 | volume-as-confidence | Price identical to GX-16; **only volume differs** → same `BROKEN_OUT` at t=16 plus a `LOW_VOLUME` flag | 8 | (6, 93.00) frozen | **BROKEN_OUT** | §13.4, HD-03 |
| GX-12 | repeated ATH | Two equal ATHs → **earliest** anchor (D-TL-02). The equal high is out of *candidacy* but stays in the *domination* set, so formation waits to t=12 with `NO_VALID_SECOND_ANCHOR` | 12 | (15, 118.00) | **ACTIVE** | §4, §6, §8, D-TL-02/05 |
| GX-13 | intervening high invalidates a candidate | Lone spike at t=20 pierces by 3× `eps` and re-binds the hull; its close is 1.69% **below** the line, so no breakout | 8 | (20, 95.00) | **ACTIVE** | §8, §10.1, §17, D-TL-05 |
| GX-14 | envelope tie | The candidates at t=9 (83.00) and t=18 (68.89) give slopes equal **to the last bit** in IEEE754 → `ENVELOPE_TIE_LATER`, geometry unchanged. See the libm caveat in the fixture's `notes` | 8 | (18, 68.89) | **ACTIVE** | §8, §18, §20.3 |
| GX-15 | tolerance-boundary (**the dedicated one**) | Bar 28 sits just inside **both** boundaries at once; both sides documented numerically, with the exact flip values | 8 | (28, 87.90) | **ACTIVE** | §9, §13.1/§13.5, HD-13 |
| GX-16 | first-close breakout | First close above line+`eps_break` fires on that bar → `BROKEN_OUT`, `confirmed_bar == breakout_bar` | 8 | (6, 93.00) frozen | **BROKEN_OUT** | §13, HD-03, §21.5 |
| GX-17 | deep undercut not a valid retest | Bar 20 **straddles** the frozen line (high 80.00 above it, low far below) so price does trade back at the broken level, but the close fails and never reclaims within `h_hold` → `NOT_RETESTED` + `FAILED_BREAKOUT` | 8 | (6, 93.00) frozen | **FAILED_BREAKOUT** | §15, §16 |
| GX-18 | missing-data edge case | Missing high / non-positive price → `INVALID_INPUT` / `INVALID_PRICE`, no geometry | n/a | — | **NONE** | §1, §18 |
| GX-19 | non-pivot canonical anchor (**SC-2 proof**) | The hull rolls 7 times to a **non-pivot** bar (15,119) and bar 16 closes above it → causal breakout, then a retest | 8 | (15, 119.00) frozen | **RETESTED** | §5, §6, §8, D-TL-03/05 |
| GX-20 | no envelope-valid second anchor | **Duplicate ATH at t=5 — before `min_formation_bars`** — so at *every* evaluable prefix the shallowest candidate is pierced beyond `eps`: no line ever forms | never | — | **NONE** | §4, §6, §8, §10.4, §18 |
| GX-21 | formation-gate regression (minimum history) | F2 and F3 hold from early on; **F1 alone binds** → ACTIVE at exactly t=8 | 8 | (3, 95.00) | **ACTIVE** | §18, §21.3, D-TL-12 |
| GX-22 | formation-gate regression (anchor recency) | New ATH at t=12; F1 stays satisfied, **F2 alone binds** → `ATH_TOO_RECENT` at t=13–15, ACTIVE again at exactly t=16 | 8, then 16 | (15, 105.00) | **ACTIVE** | §18, §21.3, §21.7, D-TL-12 |
| GX-23 | formation-gate regression (pivot-independence) | **Zero** confirmed k=3 pivots in the formation prefix and a `B*` that could never be confirmed as one, yet the same `t_form = 8` as GX-21 | 8 | (7, 92.00) | **ACTIVE** | §5, §21.3, D-TL-03, D-TL-12 |

**Fixture count: 23** — **20 geometry** fixtures + **3 null-anchor by design** (GX-10,
GX-18, GX-20).

**Provenance of the current catalog.** GX-19 was added as the SC-2 proof (Product Owner
decision 2026-07-25). Under [Issue #16](https://github.com/tomerYannay/4UR4/issues/16),
GX-08 was corrected off the pivot precondition HD-11 removed and GX-20 was added; then the
**as-of-time audit** required by HD-12 re-derived the whole set, and GX-21/GX-22/GX-23 were
added as the D-TL-12 / HD-14 formation-gate regressions.

### What the as-of-time audit changed, and what it did not

| Outcome | Fixtures |
|---|---|
| **Expectation unchanged** — the causal result is identical to the previously recorded one | GX-08, GX-10, GX-12, GX-18 |
| **Expectation re-derived, input data unchanged** | GX-15 (the boundary fixture), GX-19 (its causal breakout at t=16 has a robust 0.0246129 margin and is **preserved**, per HD-13) |
| **Input data revised so the fixture still demonstrates its stated purpose causally** | GX-02, GX-06, GX-07, GX-09 |
| **Redesigned for tolerance robustness (HD-13)** | GX-01, GX-03, GX-04, GX-05, GX-11, GX-13, GX-14, GX-16, GX-17 |
| **Redesigned because the construction was defective under causal evaluation** | GX-20 |
| **New** | GX-21, GX-22, GX-23 |

**Why the redesigns were necessary, not cosmetic.** Seven fixtures (GX-01, GX-03, GX-04,
GX-05, GX-11, GX-16, GX-17) shared one fragile construction whose breakout margin was
**0.002660** log units, and GX-13's was **0.000245** — that one flipped its breakout bar
between 8 and 9 within ±20% of the documented `eps_break`. Under HD-03 `eps_break` is
deliberately **not locked**, so an expected classification may not depend on it (HD-13).
The seven shared fixtures were therefore redesigned **once**, as a single shared price
shape: **bars 0–15 are byte-identical across all seven**, so each fixture still differs
only in the one behaviour it exists to lock.

> **Read the count honestly.** Sharing a base *increases behavioural isolation* but
> *decreases geometric diversity*: seven of the twenty geometry fixtures now exercise one
> selection/formation path, and five of them (GX-04/05/11/16/17) additionally share the same
> frozen line `B*=(6,93)` and the same breakout margin at t=16. **"20 geometry fixtures" is
> not 20 independent geometric samples**, and a defect in that shared base would fail all
> seven together. The geometric diversity lives in GX-02, GX-06, GX-08, GX-09, GX-12, GX-13,
> GX-14, GX-15, GX-19, GX-20 and GX-21/22/23. GX-14's tie was likewise never actually
exercised — it used a rounded near-collinear high (89.44 against an exact 89.4427), so the
later candidate won outright rather than by tie-break. Its first replacement, an exact
decimal ladder (`100·0.9^(t/10)`), tied in real arithmetic but **not in IEEE754**, and its
selected anchor flipped between two bars depending on which algebraically-identical form of
§7 computed the slope — an expected value that is not reproducible is not evidence. The
current construction ties **bit-exactly** and was verified stable under three formulations —
subject to one honest caveat recorded in the fixture: the tie rests on `log(68.89)` equalling
`2·log(83) − log(100)` bit-for-bit in the libms tested, and IEEE 754 does not require `log()`
to be correctly rounded, so an engine on a different math library must re-check this fixture
specifically.

Category coverage: normal valid (GX-01, GX-09), monotonic decline / zero-pivot series
(GX-08), repeated ATH (GX-12), multiple competing second anchors (GX-02),
intervening-high invalidation (GX-13), envelope tie (GX-14), tolerance-boundary (GX-15),
wick-only crossing (GX-03), first-close breakout (GX-16), volume-as-confidence (GX-11),
false breakout (GX-05), clean retest (GX-04), deep-undercut-not-a-retest (GX-17), expiry &
recalculation (GX-07, GX-06), no envelope-valid second anchor / duplicate ATH (GX-20),
stock-split (GX-10), missing-data (GX-18), non-pivot canonical anchor / SC-2 proof (GX-19),
formation gates (GX-21, GX-22, GX-23).

## 4. Tolerance, formation parameters & versioning

Default parameters used (unless a fixture states otherwise):
`k=3, eps=0.02, eps_touch=0.01, eps_retest=0.01, eps_fail=0.01, F_fail=10, W_retest=20,
h_hold=3, E_expiry=100, min_formation_bars=8, min_ath_age_bars=3`.

**Formation parameters are first-class and `k`-independent (D-TL-12, HD-14).**
`min_formation_bars` (8) and `min_ath_age_bars` (3) replace the former pivot-derived
`2k+2` and `k`-recency formulations **at identical values**. They are named, versioned
with the detector's `spec_version`, backtestable, and carried explicitly in every
fixture's `params`. Changing the pivot window `k` may no longer move any event —
GX-21/GX-22/GX-23 lock the two gates individually and their independence from pivot
structure, and GX-08/GX-19/GX-23 lock that a non-pivot bar (or a series with no pivots at
all) selects the canonical anchor. `tools/fixture-replay.mjs --formation` re-checks the gates
and adds a positive control so they cannot pass vacuously. Note what the `k` sweep in that
check does **not** show: the reference model never reads `k`, so `k`-independence is
**structural** there and the sweep cannot fail — the binding evidence is the fixture data.

**`eps_break` is a versioned, backtestable tolerance with NO locked default (HD-03,
§13.5) — and no ordinary fixture's outcome may depend on it (HD-13).** Every fixture that
uses it sets `"eps_break": 0.01` **only as an illustrative value** and carries
`"eps_break_locked": false` plus an `eps_break_note` reaffirming this. The governing
`eps_break` value/definition (percentage/log-unit **or** ATR-based) is chosen later from
Phase-0 + Phase-4 evidence and pinned with the detector's `spec_version`. Every fixture except the two
whose bar-set is rejected by an input guard (GX-10, GX-18 — they never consult `eps_break`)
records a sweep in `causal_record.eps_break_robustness`. **HD-13 rule 1 is machine-enforced:**
`node tools/fixture-replay.mjs --all` **fails** if any ordinary fixture's classification moves
under ±20%, with GX-15 whitelisted as the fixture HD-13 exempts. Counted from the committed
sweeps: **22 of 23 invariant at ±20%** — all 22 ordinary fixtures comply, GX-15 being the
designed exception — and **21 of 23 across the wider 0.5×–2× sweep**. The two that are not
invariant across the wider sweep:
- **GX-15** — the *dedicated* tolerance-boundary fixture, whose sensitivity is the point. Bar
  28 clears the line by **0.008242654587** log units, so a breakout fires at t=28 for any
  `eps_break` strictly below that — including the 6-significant-figure display value
  `0.00824265` itself, and including the 0.8× sweep point. At the documented `0.01` it does
  not fire. The `eps` side flips at **0.018534340624**. Both boundaries are quoted at full
  precision deliberately: the 6 s.f. rounding falls *below* each of them (at exactly that value §13.1's
  strict inequality is not met and it stays `ACTIVE`).
- **GX-12** — **not** a second boundary fixture. It satisfies HD-13 (invariant at ±20%) and
  only leaves that band at 0.5×, where its t=15 wick becomes a breakout. Its input data is
  deliberately untouched, because the causal audit proved its expectation correct; the
  sensitivity is recorded in its `causal_record` rather than designed away. GX-02 uses `eps=0.005` to reproduce the spec §8 worked example exactly. Each
fixture's `params.tolerance_version` tags the tolerance set used so evidence is traceable.

## 5. Reason-code legend

| Reason code | Meaning | Fixtures |
|-------------|---------|----------|
| `LINE_ESTABLISHED` | A valid A->B* line became ACTIVE, **or a re-selected line took effect from this bar** (§21.6) — a fixture with N pre-breakout re-selections records N+1 of these | every geometry fixture |
| `ENVELOPE_TIE_LATER` | Envelope slope tie broken toward the later anchor (§18) | GX-14 |
| `WICK_BREAK` | Intrabar high pierced, close did not confirm; stays ACTIVE (§14) | GX-02, GX-03, GX-09, GX-12, GX-13 |
| `INVALID_PIERCE` | A bar high pierced the active line beyond `eps` without a breakout, superseding that line (§10.1); under all-highs candidacy the piercing bar itself becomes the new `B*` from `t+1` | GX-02, GX-03, GX-09, GX-12, GX-13 |
| `BREAKOUT_CONFIRMED` | First daily close above line+eps_break; alert fires (§13, HD-03) | GX-04, GX-05, GX-07, GX-11, GX-16, GX-17, GX-19 |
| `FAILED_BREAKOUT` | Post-breakout close below the **frozen** line-eps_fail within F_fail (§15) | GX-05, GX-17 |
| `RETEST_HELD` | Post-breakout dip to the **frozen** line that held as support (§16) | GX-04, GX-19 |
| `RESET_NEW_ATH` | New ATH retired the old line; new formation (§10.3, §21.7) | GX-06, GX-22 |
| `EXPIRED_POST_BREAKOUT` | >=E_expiry bars after the frozen breakout bar; retire + recompute (§17) | GX-07 |
| `ATH_TOO_RECENT` | Formation blocked because the anchor is within `min_ath_age_bars` of the last available bar (§18, §21.3 F2) | GX-06, GX-22 |
| `NO_VALID_SECOND_ANCHOR` | Eligible candidates exist (all later bar highs below the ATH) but **none survives the envelope test**; no line (§10.4, §18). **Never** emitted for an absence of pivot highs (HD-11) | GX-20 (permanent), GX-12 (transient, t=8–11) |
| `SUSPECTED_UNADJUSTED_SPLIT` | Impossible single-bar log jump > ln(1.5); do not fit (§18) | GX-10 |
| `INVALID_PRICE` | Non-positive price; reject bar-set (§1, §18) | GX-18 |
| `INVALID_INPUT` | Missing required field (high/close); reject bar-set (§1) | GX-18 |

Non-gating **flags** (confidence/quality only, never validity gates): `LOW_VOLUME` (GX-11),
`NOT_RETESTED` (GX-17).

A fixture with *N* pre-breakout re-selections records *N* + (one per formation episode)
`LINE_ESTABLISHED` transitions — usually *N*+1, but *N*+2 for GX-06 and GX-22, which form a
line twice across a new-ATH reset. The re-selection entry is stamped at the bar the
re-selected line takes **effect** (§21.6), and is emitted **before** that bar's own event, so
the transition list is always a valid walk of the §11 state machine (asserted by `--all`).

`INSUFFICIENT_BARS` is the standing reason for every bar before `t_form` in **every**
fixture. It is not recorded as an event transition — a series always starts short — but it
is visible bar by bar in `causal_record.formation.gate_trace`, which evaluates F1, F2 and
F3 **independently**, so a reader can always see exactly which gate binds at which bar and
never confuses a formation guard with `NO_VALID_SECOND_ANCHOR`.

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

## 6a. Fixture layers (synthetic vs real-market)

| Layer | Count | Status | Location |
|-------|-------|--------|----------|
| **Synthetic golden fixtures** | **23** (20 geometry + 3 null-anchor) | complete; the **entire set re-derived as-of-time (HD-12) and re-verified** by `tools/fixture-replay.mjs` — 23/23 reproduce exactly, with the §21.4 hull lemma checked against the §8 brute force at every evaluable prefix, prefix-truncation invariance, frozen-line invariants, formation-gate regressions and an `eps_break` robustness sweep (see `VERIFICATION.md`) | `golden/GX-01 … GX-23` |
| **Real-market fixtures** | **1 (RM-01)** | **verified from licensed OHLCV; SC-1 = MATCH; Product Owner approval `approved` (2026-07-25)** (`status: verified`) | `real/RM-01/` |

The two layers are complementary and must not be conflated: the **synthetic** set pins the
deterministic arithmetic (spec-derived expected values), while the **real-market** set is the
independent, non-circular ground truth (real charts + licensed OHLCV). **RM-01** is the
Product Owner's original SPCX chart — immutable chart image + immutable Alpha Vantage OHLCV
source, with geometry **independently recomputed** from real data: **SC-1 resolves as MATCH**
(2026-07-21 is the upper-log-hull canonical anchor; 0 envelope violations; no breakout through
2026-07-24). **SC-2** (the anchor is not a `k=3` pivot) is now **RESOLVED by the Product
Owner decision 2026-07-25**: the upper-log-hull over **all** highs is canonical and the pivot
prefilter is non-authoritative (spec §5/§6/§8, D-TL-05); the synthetic proofs are **GX-19**
(a non-pivot bar is the canonical anchor) and **GX-08** (a series with **no** pivots at all
still has a canonical anchor).
Product Owner approval of the RM-01 *result* (the separate review of the verified geometry) **was
granted on 2026-07-25**, in the same review that ruled HD-11 — see
[`real/RM-01/README.md`](real/RM-01/README.md) (status header and §5 visual-acceptance record),
[`VERIFICATION.md`](VERIFICATION.md) ("Product Owner approval: `approved` (2026-07-25)"),
[`real/RM-01/annotation.json`](real/RM-01/annotation.json)
(`product_owner_approval: approved`), and
[`../human-decisions.md`](../human-decisions.md) (HD-11, decided 2026-07-25).
The process is in [`real-market-plan.md`](real-market-plan.md). The synthetic catalog in §3
was last changed on 2026-07-25 by the Issue #16 as-of-time (HD-12) audit, which re-derived
every fixture causally, redesigned the tolerance-fragile constructions per HD-13, replaced
the defective GX-20 construction and added the D-TL-12 / HD-14 formation-gate regressions
GX-21/GX-22/GX-23: **23 fixtures, 20 geometry + 3 null-anchor**. RM-01 itself is untouched
by that audit — its approved anchor and its SC-1 = MATCH result are unaffected.

## 7. Files

- `README.md` — this document.
- `../../tools/fixture-replay.mjs` — the causal (as-of-time) **reference model and replay
  harness** that re-derives and re-checks every fixture. Phase-0 **evidence tooling**, not
  the product detector: it lives in `tools/` beside `validate.mjs`, creates no product-code
  directory, is wired into no product surface, and confers no Phase-2 credit. A future
  build-lifted engine must be written separately and must reproduce the **fixtures** —
  reproducing this script is not the contract.
- `schema/fixture.schema.json` — JSON Schema for every `expected.json`.
- `golden/<ID>/input.csv` — synthetic OHLCV (`timestamp,open,high,low,close,volume`);
  `timestamp` is an **ordinal index `t`** (see each fixture's `input_convention`).
- `golden/<ID>/expected.json` — the expected output for `<ID>`, schema-validated.
- `real-market-plan.md` — plan to add human-reviewed real-market fixtures as independent
  ground truth (acquires no data now).
- `schema/real-annotation.schema.json` — JSON Schema for real-market `annotation.json`
  (numeric market-data/geometry fields nullable until verified OHLCV exists).
- `real/RM-01/source-chart.png` — immutable chart-image evidence (do not edit/regenerate).
- `real/RM-01/alphavantage-source.json` — immutable licensed OHLCV source (Alpha Vantage, SPCX daily).
- `real/RM-01/input.csv` — chronologically-ascending `date,open,high,low,close,volume` derived from the source.
- `real/RM-01/annotation.json` — RM-01 annotation instance (`status: verified`, SC-1 = MATCH, approval `approved` (2026-07-25)).
- `real/RM-01/README.md` — human-readable RM-01 record (evidence, ATH verification, independent
  calculation, visual-acceptance checklist, spec-contradiction report SC-1/SC-2).

*Design artifact under GOV-015. It authorizes no build; implementation of a detector that
reproduces these fixtures follows only when a Ready ticket exists and the freeze is lifted
per-scope ([GOV-013](../../governance/approval-gate.md)).*
