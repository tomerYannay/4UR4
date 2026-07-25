# 4UR4 — Golden-Fixture Verification Log (research evidence)

> Design/evidence artifact under [GOV-015](../../governance/build-freeze.md). Records an
> **independent** re-derivation of every fixture's geometry. Separation of duties: the
> fixtures were **authored by the Architect**; this verification was performed **independently
> by the primary session (Agent Zero)** — author ≠ verifier ([GOV-011](../../governance/separation-of-duties.md)).

## Method

An independent calculator re-derived, for each fixture, straight from the spec formulas and
the fixture's own `input.csv` — **without** using the fixture's stated geometry as input:

- ATH anchor = earliest bar at the global-max high (§4, D-TL-02) → cross-checked against
  `expected_ath_anchor` and against the CSV.
- Second-anchor high cross-checked against the CSV bar.
- `yA = ln(HA)`, `yB = ln(HB)`, `m = (yB − yA)/(tB − tA)`, `b = yA − m·tA` (§3, §7) →
  compared to `expected_log_slope` / `expected_intercept`.
- Every entry in `expected_line_values`: recomputed `ŷ(t) = m·t + b` and
  `line(t) = exp(ŷ(t))` → compared to the stated values.

Tolerance: relative ≤ 3×10⁻⁵ on slope/intercept, ≤ 5×10⁻⁵ on line values (6-significant-figure
agreement). Null-anchor fixtures (**as of this pass**: GX-08, GX-10, GX-18) were checked for the
correct no-geometry guard + reason codes. **GX-08 has since been corrected — see "Issue #16
correction" below: the current null-anchor set is GX-10, GX-18, GX-20.**

## Result (verification pass of 2026-07-25, pre-#16)

- **19 / 19 fixtures verified** (16 with geometry; 3 null-anchor **as committed at the time** —
  GX-08, GX-10, GX-18).
- All anchors, slopes, intercepts, and `y_hat` values reproduced independently.
- **Two `line` (price) display values** were off in the 5th–6th significant figure due to
  manual `exp()` rounding and were **corrected to the independently computed values**:
  - `GX-06` line@t=11: `108.983 → 108.976`
  - `GX-09` line@t=14: `133.685 → 133.695`
  (`y_hat`, slope, intercept, anchors, and all inequality outcomes were already correct in
  both; only the displayed `exp()` digit changed.)

Re-running the verifier after the corrections reports: **all geometry, anchors, and line
values reproduce independently within 6-significant-figure tolerance.**

## Scope notes carried forward (not defects)

- `GX-07`: only the expiry **timing/transition** is pinned; the post-expiry recomputed line
  geometry is intentionally not pinned (a later increment may pin it).
- `GX-06`: the single anchor fields report the **current post-reset** line; the retired first
  line is documented in `geometry_check` and the transition list.
- Reason codes `LINE_ESTABLISHED` / `BREAKOUT_CONFIRMED` are introduced by the fixture set for
  the `NONE→ACTIVE` and breakout transitions; they are self-consistent and documented in the
  README legend. A follow-up may formally enumerate them in the trendline spec's reason-code
  list.

---

## RM-01 — real-market verification (Alpha Vantage SPCX)

Independent verification of the first real-market fixture, computed by the primary session
(verifier) from `real/RM-01/input.csv` (derived from immutable `alphavantage-source.json`,
sha256 `69a67469…50c377`) using **trading-bar ordinal indices**, not calendar-day gaps. The
preliminary conclusions supplied with the task were **recomputed, not copied**.

**Inputs.** 29 daily bars, 2026-06-12 → 2026-07-24. A = ATH = bar `t=2` 2026-06-16 high
**225.64** (max over all available bars; unique). B = bar `t=25` 2026-07-21 high **129.88**.

**Computed geometry.** `yA=ln225.64=5.41894`, `yB=ln129.88=4.86661`,
slope `m=(yB−yA)/(25−2)=−0.0240143`/bar, intercept `b=5.46697`.

**Results (exact, independently reproduced):**

| Check | Result |
|-------|--------|
| Envelope violations (intervening high pierces line, ε=0.02) | **0** |
| Max intervening approach | **2026-07-06**, −0.740% (log −0.00743), below the line |
| Shallowest slope from ATH over all later highs | **2026-07-21** (−0.0240143) → upper-log-hull vertex |
| A→B line dominates all later highs within ε | **yes** |
| Breakout through 2026-07-24 (first daily close above line) | **none** |
| Wick-break through 2026-07-24 | **none** |
| Retest | **none** (no breakout occurred) |

Every preliminary expectation is **confirmed**: 2026-07-21 canonical anchor; no intervening
high exceeds the line; closest approach near 2026-07-06; no breakout / wick-break / retest.

**SC-1 → `MATCH`** (of the 5 options MATCH / VISUAL_MATCH_WITHIN_TOLERANCE /
MISMATCH_INTERVENING_HIGH / MISMATCH_DIFFERENT_CANONICAL_ANCHOR / INSUFFICIENT_DATA): the PO's
two-point line coincides with the canonical upper-log-hull line; exact evidence, adequate data.

**SC-2 → RESOLVED 2026-07-25 (HD-11).** The recorded disagreement (2026-07-21 is the hull
vertex but not a `k=3` pivot — 2026-07-17 @130.33 is higher within 3 bars; the only `k=3`
pivot after the ATH, 2026-06-30, does not dominate) was ruled on by the Product Owner: the
**upper-log-hull is canonical; the pivot prefilter is non-authoritative** and must never change
the canonical anchor. The trendline spec (§5/§6/§8/D-TL-03/D-TL-05) was revised and golden
fixture **GX-19** added as the deterministic proof.

`annotation.json` is machine-validated against `schema/real-annotation.schema.json`.
**Product Owner approval: `approved` (2026-07-25).**

## SC-2 regression check — all-highs upper-log-hull across the golden set

After the pivot prefilter was made non-authoritative, an independent **all-highs hull check**
recomputed, for every geometry fixture, the shallowest descending line from `A` over **all**
later bar highs in the formation window (no pivot restriction) and confirmed it equals the
stated second anchor and dominates all intervening highs:

- **16 / 16 geometry fixtures**: stated `B*` **is** the all-highs upper-log-hull vertex — so
  removing the pivot precondition **moved no anchor that already existed**.
  **CORRECTED 2026-07-25 (Issue #16):** this check was run only over the fixtures that *had* a
  stated anchor, so it missed the one fixture that had **none**. **GX-08** expected
  `NO_VALID_SECOND_ANCHOR` on the pivot precondition HD-11 removed; under all-highs candidacy it
  **gains** an anchor, `B* = (1, 98)`. The correct statement is therefore: removing the pivot
  precondition moves no *existing* anchor **but creates one** (GX-08). The geometry set is now
  **17** (GX-08 joined it) and the null-anchor set is **GX-10, GX-18, GX-20**.
- **FURTHER CAVEAT on the same check (raised 2026-07-25 during the #16 sweep, UNRESOLVED).**
  The check searched the shallowest line "over all later bar highs **in the formation window**",
  i.e. up to the stated `B*`. Re-run over the **full** history, two fixtures do **not** satisfy
  the claim: **GX-09** (the `t=11` high 146 sits above the stated `A→(10,150)` line; the
  full-history argmax-slope valid candidate is `t=14`, H=135, `m=−0.0280745`, 0 violations at
  `ε=0`) and **GX-15** (the `t=28` high 87.90 is a valid candidate with `m=−0.00460611`,
  shallower than the stated `−0.00526803`, 0 violations at `ε=0`). Both fixtures previously
  relied on the pivot precondition — a bar within `k` of the series end could not be a confirmed
  pivot and so could not be selected — which **HD-11 removed without stating a replacement**.
  Resolving this (full-history selection vs. formation-freeze) is a **product-definition
  decision** and is therefore **out of scope for Issue #16, which changes no rule**; it is
  **escalated** and recorded in each fixture under `geometry_check.open_issue_2026_07_25`. Note
  that RM-01's PO-approved canonical anchor is itself only 3 bars from the end of its series, so
  a "bars near the series end cannot be selected" answer would contradict RM-01/HD-11.
- **GX-19** was the only fixture whose canonical `B*` is a **non-`k=3`-pivot** bar (`t=16`,
  H=120): the sole `k=3` pivot (`t=4`, H=160) yields a steeper line pierced at `t=5`, so a
  strict prefilter would pick the wrong anchor while the all-highs hull selects correctly —
  the SC-2 proof. **CORRECTED 2026-07-25 (Issue #16):** the corrected **GX-08** is a second
  such fixture — a stronger one, since its series contains **zero** `k=3` pivots yet still has
  the canonical anchor `B* = (1, 98)`. Geometry verifier at that pass: **19 / 19** fixtures
  reproduced to 6 significant figures.

---

## Issue #16 correction (2026-07-25) — GX-08 re-derived, GX-20 added

> **Status: AUTHOR-SUPPLIED RE-DERIVATION — independent re-verification PENDING.** These two
> entries were **authored**, not verified, in this change; under
> [GOV-011](../../governance/separation-of-duties.md) the author is not the verifier, so the
> numbers below must be reproduced by an independent verifier before this log claims them as
> verified. Nothing above this section is re-verified by this change.

- **GX-08 — corrected from `NO_VALID_SECOND_ANCHOR` to an `ACTIVE` line.** Highs
  `100, 98, 96 … 72` (15 bars), `A = (0,100)`. Candidacy is over all later bar highs (§6), so
  there are **14 candidates** despite **zero** `k=3` pivots. Slopes are
  `m(t) = ln(1 − 0.02t)/t`, strictly decreasing in `t`, so the hull vertex is the **first**
  later bar: `B* = (1, 98)`, `m = −0.0202027`, `b = ln 100 = 4.60517`. Domination holds with
  **0 violations even at `ε = 0`** (worst gap `−4.1658×10⁻⁴` at `t = 2`); at `ε = 0.02` all
  **14/14** candidates are envelope-valid and at `ε = 0` exactly **one** is (`B*` itself).
  No close exceeds `line + ε_break` anywhere (`line(t) = 100·0.98ᵗ ≥ 100 − 2t = C[t]`), so the
  end state is **ACTIVE**, `breakout_bar = confirmed_bar = null`. `INSUFFICIENT_BARS`
  (`n = 15 ≥ 2k+2 = 8`) and `ATH_TOO_RECENT` (`tA = 0` of 15) do not fire.
- **GX-20 — new fixture for the genuinely reachable `NO_VALID_SECOND_ANCHOR`.** A **double top
  at the ATH**: `130` at both `t = 0` and `t = 15` of 26 bars. `A = (0,130)` (D-TL-02, earliest
  wins). The tying high is excluded from **candidacy** by §6 (`HB < HA` strictly) but stays in
  the **domination set** of §8 step 3 (every bar high), so for any candidate slope `m` the gap
  at `t = 15` is exactly `−15m`. The shallowest of the **24** candidates (`t = 16, H = 116`,
  `m = −0.00712152`) gives `0.106823` = **5.34 × ε** → **0 of 24** valid →
  `NO_VALID_SECOND_ANCHOR`, `NONE`. Still none at `ε = 0.05` and `ε = 0.08`. Guards silent:
  max single-bar `|log jump| = 0.113944 ≤ ln 1.5 = 0.405465`; `n = 26 ≥ 2k+2 = 8`; `tA = 0`
  with 25 later bars; all prices positive. No `RESET_NEW_ATH` (§10.3 needs a high that
  **exceeds** `HA`); the ε-treatment of the equal high follows the precedent already set by
  **GX-12**.
- **Rule impact: none.** This is a Phase 0 **evidence** correction. `human-decisions.md`,
  HD-11 and the canonical algorithm are untouched; the fixtures are being aligned to rules
  approved on 2026-07-25.
- Catalog after the correction: **20 fixtures — 17 geometry + 3 null-anchor (GX-10, GX-18,
  GX-20)** — consistent with [`README.md`](README.md) §3 and §6a.

---

*This log records verification only. It authorizes no build; a detector that reproduces these
fixtures is implemented only when a Ready ticket exists and the freeze is lifted per-scope.*
