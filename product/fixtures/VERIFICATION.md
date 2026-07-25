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
agreement). Null-anchor fixtures (GX-08, GX-10, GX-18) were checked for the correct
no-geometry guard + reason codes.

## Result

- **18 / 18 fixtures verified** (15 with geometry; 3 null-anchor by design).
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
  removing the pivot precondition **moves no existing anchor** (existing fixtures unchanged).
- **GX-19** is the only fixture whose canonical `B*` is a **non-`k=3`-pivot** bar (`t=16`,
  H=120): the sole `k=3` pivot (`t=4`, H=160) yields a steeper line pierced at `t=5`, so a
  strict prefilter would pick the wrong anchor while the all-highs hull selects correctly —
  the SC-2 proof. Geometry verifier: **19 / 19** fixtures reproduce to 6 significant figures.

---

*This log records verification only. It authorizes no build; a detector that reproduces these
fixtures is implemented only when a Ready ticket exists and the freeze is lifted per-scope.*
