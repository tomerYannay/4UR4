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

*This log records verification only. It authorizes no build; a detector that reproduces these
fixtures is implemented only when a Ready ticket exists and the freeze is lifted per-scope.*
