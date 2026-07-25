# 4UR4 — Golden-Fixture Verification Log (research evidence)

> Design/evidence artifact under [GOV-015](../../governance/build-freeze.md). Records an
> **independent** re-derivation of every fixture's geometry. Separation of duties: the
> fixtures were **authored by the Architect**; this verification was performed **independently
> by the primary session (Agent Zero)** — author ≠ verifier ([GOV-011](../../governance/separation-of-duties.md)).

> ## ⚠ CURRENCY — read this first
>
> **Machine-guarded surfaces.** The governing result table below and every `causal_record`
> block are **emitted and diffed by `node tools/fixture-replay.mjs --all`**, which CI runs,
> so neither can drift from the fixtures without failing the build. The surrounding prose is
> not machine-checked and is hand-verified at the head named in each section.
>
> **The current, governing verification pass is
> [§ As-of-time (HD-12) audit — 2026-07-25](#as-of-time-hd-12-audit--2026-07-25-governing) at
> the bottom of this file.** Every section above it is a **historical record retained under
> [GOV-006](../../governance/definition-of-done.md)** and describes the fixture set as it stood
> **before** the as-of-time audit. Those sections were derived with **full-series** hull
> calculations, which HD-12 rule 7 / §21.8 now outlaws as a derivation method; where they
> conflict with the audit section, **the audit governs**. Specific supersessions are flagged
> inline. The two open items they carry —
> the "FURTHER CAVEAT … UNRESOLVED" on GX-09/GX-15 and the "independent re-verification
> PENDING" on GX-08/GX-20 — are both **discharged** by the audit section.

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
- **FURTHER CAVEAT on the same check (raised 2026-07-25 during the #16 sweep — since
  RESOLVED by HD-12; see the governing audit section below).**
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

> **Status: SUPERSEDED — the re-derivation demanded here has since been performed; see the
> governing as-of-time audit section below.** GX-08's numbers were reproduced and are
> **confirmed unchanged**. GX-20's were reproduced and the construction was **found
> defective** under as-of-time evaluation (it forms a line at t=8 and breaks out at t=11,
> because its duplicate ATH sits at t=15 — after formation); it has been replaced. The
> GX-20 paragraph below is retained as the historical record of the defect, not as a
> description of the current fixture.

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

## As-of-time (HD-12) audit — 2026-07-25 (**GOVERNING**)

> **This section supersedes every verification claim above it.** It records the complete
> re-derivation of the fixture set under **as-of-time (rolling causal) evaluation**
> (§21, HD-12, D-TL-11), the redesigns required by **HD-13**, the formation-parameter
> decoupling of **D-TL-12 / HD-14**, and the mechanical checks that now guard all of it.

### Why a re-derivation was necessary

HD-12 rule 7 / §21.8 forbid using a later bar to establish an earlier bar's classification.
Every expected value above was derived from a **full-series** hull — the method HD-12
outlaws. A lemma proved during the §21 work (§21.4, non-normative corollary) makes the
consequence exact rather than speculative: *with the same anchor in force the causal line
lies at or below the full-series line*, so converting a full-series expectation to
as-of-time makes breakouts **appear or move earlier, never later**. A full-series
expectation is therefore valid evidence only where it is demonstrably identical to the
as-of-time result — and for most of the set it was not.

### Method (independent, mechanical, reproducible)

An independent **causal reference model**, `tools/fixture-replay.mjs`, was written directly
from the specification and replays every fixture bar by bar:

1. builds `Λ_t` from the available prefix `S_t = bars 0…t−1` **only**;
2. evaluates bar `t`'s new-ATH, breakout, wick, failure, retest and expiry tests against
   that pre-existing line, in the §21.2 order (rule 5 first);
3. freezes `Λ^F` on a confirmed breakout and suspends re-selection thereafter;
4. otherwise rolls `B*` forward, effective `t+1`.

`B*_t` is computed by **brute force from the §8 definition** — every candidate, dominated
against every bar high in the prefix — not by the §21.4 shortcut; the shortcut is then
checked *against* it. Geometry is compared at **exactly 6 significant figures** (equality
of the rounded value), not with a fuzzy tolerance, which is stricter than the ≤3×10⁻⁵ /
≤5×10⁻⁵ relative tolerances used in the passes above.

The model is **proposed as Phase-0 evidence tooling, not the product detector** — its status under the GOV-015 build-freeze is an open Product Owner question (**HD-15, PENDING**), and the following is the proposed disposition rather than a ruling: it lives in `tools/`
beside `validate.mjs`, creates no product-code directory, is wired into no product surface,
and confers no Phase-2 credit. A build-lifted engine must still be written separately and
must reproduce the **fixtures**.

**Cross-validation against a prior independent derivation.** Before being used to author
anything, the model was checked against the event-time margins derived independently during
the Issue #16 audit. It reproduces them exactly: GX-01 `0.0026602`, GX-02 `0.0059418`,
GX-07 `0.0100755`, GX-13 `0.00024511`, GX-19 `0.0246129`, and the defective GX-20's
`0.0032861` — six independent agreements to six significant figures.

**One correction to that prior audit.** Its table recorded GX-06 as a breakout at t=10 with
margin `0.205930`. That is wrong: bar 10's high (110) **exceeds** the prior ATH (100), so
§21.2 **rule 5** applies and takes precedence over the breakout test — a bar whose high
makes a new ATH is a `RESET_NEW_ATH`, never a breakout of the line it retires. The prior
model omitted rule 5. GX-06's correct causal result is reset at t=10, re-formation at t=14.

### Result — 23 / 23 fixtures reproduce exactly

| ID | bars | formation bar(s) | governing `B*` | `m` | final state | BO bar | breakout margin | re-sel | k=3 pivots | `B*` is a pivot? |
|----|-----:|---------:|----------------|-----|-------------|-------:|----------------:|-------:|-----------:|------------------|
| GX-01 | 19 | 8 | (6, 93) | -0.0120951 | ACTIVE | — | — | 0 | 1 | yes |
| GX-02 | 74 | 8 | (45, 92) | -0.00185292 | ACTIVE | — | — | 2 | 3 | yes |
| GX-03 | 19 | 8 | (16, 86) | -0.00942643 | ACTIVE | — | — | 1 | 1 | **no** |
| GX-04 | 23 | 8 | (6, 93) | -0.0120951 | RETESTED | 16 | 0.032699 | 0 | 2 | yes |
| GX-05 | 23 | 8 | (6, 93) | -0.0120951 | FAILED_BREAKOUT | 16 | 0.032699 | 0 | 2 | yes |
| GX-06 | 21 | 8, then 14 | (13, 103) | -0.0219171 | ACTIVE | — | — | 0 | 2 | **no** |
| GX-07 | 111 | 8 | (6, 94) | -0.0103126 | NONE | 10 | 0.0418324 | 0 | 2 | yes |
| GX-08 | 15 | 8 | (1, 98) | -0.0202027 | ACTIVE | — | — | 0 | 0 | **no** |
| GX-09 | 15 | 8 | (10, 150) | -0.0287682 | ACTIVE | — | — | 1 | 2 | yes |
| GX-10 | 10 | — | — | — | NONE | — | — | 0 | 0 | — |
| GX-11 | 19 | 8 | (6, 93) | -0.0120951 | BROKEN_OUT | 16 | 0.032699 | 0 | 1 | yes |
| GX-12 | 22 | 12 | (15, 118) | -0.00645666 | ACTIVE | — | — | 2 | 2 | yes |
| GX-13 | 40 | 8 | (20, 95) | -0.00256466 | ACTIVE | — | — | 1 | 3 | yes |
| GX-14 | 23 | 8 | (18, 68.89) | -0.0207033 | ACTIVE | — | — | 2 | 0 | **no** |
| GX-15 | 31 | 8 | (28, 87.9) | -0.00460609 | ACTIVE | — | — | 14 | 2 | **no** |
| GX-16 | 19 | 8 | (6, 93) | -0.0120951 | BROKEN_OUT | 16 | 0.032699 | 0 | 1 | yes |
| GX-17 | 24 | 8 | (6, 93) | -0.0120951 | FAILED_BREAKOUT | 16 | 0.032699 | 0 | 2 | yes |
| GX-18 | 8 | — | — | — | NONE | — | — | 0 | 0 | — |
| GX-19 | 21 | 8 | (15, 119) | -0.0346129 | RETESTED | 16 | 0.0246129 | 7 | 1 | **no** |
| GX-20 | 26 | — | — | — | NONE | — | — | 0 | 1 | — |
| GX-21 | 12 | 8 | (3, 95) | -0.0170978 | ACTIVE | — | — | 0 | 0 | **no** |
| GX-22 | 20 | 8, then 16 | (15, 105) | -0.0215128 | ACTIVE | — | — | 0 | 2 | **no** |
| GX-23 | 13 | 8 | (7, 92) | -0.0119117 | ACTIVE | — | — | 0 | 1 | **no** |

`B*` here is the **governing** line: the frozen event line `Λ^F` where a confirmed breakout
occurred (retained even after expiry — it is the line the market actually broke), otherwise
`Λ_n`, the line in force after the final bar. **9 of the 20 geometry fixtures now have a
non-pivot canonical `B*`** — under the superseded pivot prefilter, 9 fixtures would select a
different (wrong) anchor or none at all. That is the SC-2 / HD-11 defect, quantified.

### What changed, per fixture

| Outcome | Fixtures | Note |
|---|---|---|
| Expectation **unchanged** by the audit | GX-08, GX-10, GX-12, GX-18 | Only GX-08's and GX-12's *formation bar* moved (to 8 and 12), because §21.3 forbids an ACTIVE line before the gates are met. Geometry, state and events are identical. |
| Expectation re-derived; **input data untouched** | GX-15, GX-19 | GX-19's causal breakout at t=16 has a robust margin (`0.0246129`) and is **preserved**, per HD-13. GX-15 remains the dedicated boundary fixture. |
| Input data revised so the fixture still demonstrates its **stated purpose** causally | GX-02, GX-06, GX-07, GX-09 | Each kept its documented headline geometry where the causal reading supports it — GX-09 still ends at `B* = (10,150)` with `m = −0.0287682`; GX-07 still freezes `B* = (6,94)` with `m = −0.0103126`. |
| **Redesigned** for tolerance robustness (HD-13) | GX-01, GX-03, GX-04, GX-05, GX-11, GX-13, GX-14, GX-16, GX-17 | See below. |
| **Redesigned** because the construction was defective under causal evaluation | GX-20 | See below. |
| **New** — formation-gate regressions (D-TL-12 / HD-14) | GX-21, GX-22, GX-23 | |

**The HD-13 redesigns were necessary, not cosmetic.** Seven fixtures (GX-01, GX-03, GX-04,
GX-05, GX-11, GX-16, GX-17) were variants of a single construction whose causal breakout
margin was **0.0026602** log units; GX-13's was **0.00024511**, flipping its breakout bar
between 8 and 9 within ±20% of the documented `eps_break`. Since HD-03 deliberately leaves
`eps_break` unlocked, those expectations were indeterminate. The seven were redesigned
**once**, as one shared price shape — **bars 0–15 are byte-identical across all seven** — so
each still differs only in the behaviour it exists to lock. GX-14's tie was never actually
exercised: it used a rounded near-collinear high (89.44 against an exact 89.4427), so the
later candidate won outright rather than by tie-break. Its first replacement — the decimal
ladder `100·0.9^(t/10)` = 90.00 / 81.00 / 72.90 / 65.61 — was **also defective** and is
described in the round-2 corrections below; the committed construction ties at t=9 / t=18
and fires **once**.

**GX-20 as previously committed was defective.** Its double top was designed with
full-series reasoning ("no envelope-valid candidate over the whole series"), which HD-12
makes the wrong test. The tie sat at t=15, *after* formation, so a line legitimately formed
at t=8 from bars 0–7 and broke out at t=11 (margin `0.0032861`) — it was not a no-anchor
fixture at all. In the replacement the tie sits at **t=5, before `min_formation_bars = 8`**,
so **every** evaluable prefix already contains it. Proof, recorded per prefix in
`causal_record.no_anchor_proof`: at each prefix the shallowest descending candidate is
pierced by the ATH-tying bar by more than `eps`, and the shallowest candidate *minimises*
that pierce, so no candidate is envelope-valid at any prefix. The tightest case over the
whole series is the t=19 high (115), pierced by `0.0322638` = **1.61 × eps**. Because no
line ever exists, `eps_break` is never consulted — the result is invariant across the entire
0.5×–2× sweep by construction, not by margin.

### Mechanical checks — all green at this head

`node tools/fixture-replay.mjs --all` runs, for every fixture:

| Check | What it asserts | Result |
|---|---|---|
| Causal replay | expected anchors, slope, intercept, line values (exact at 6 s.f.), transitions, reason codes, final state and breakout bar all reproduce | **23 / 23** |
| Hull (`--hull`) | the §21.4 running-max lemma equals the §8 brute-force recomputation **at every evaluable prefix of every fixture** | **0 discrepancies** |
| No look-ahead (`--nolookahead`) | truncating the series at any bar leaves every classification at or before that bar unchanged (§21.8 streaming ≡ batch) | **0 violations** |
| Frozen line (`--frozen`) | the reported event line **is** `Λ_b` computed from `S_b`, and no post-breakout bar moves it (§21.5) | **0 violations** |
| Formation (`--formation`) | (a) no line ACTIVE before `min_formation_bars`; (b) none within `min_ath_age_bars` of its anchor; (c) formation is immediate once all three gates hold; (d) replaying at `k ∈ {1,2,3,4,5,8}` produces byte-identical output | **0 violations** |
| Transition-list continuity (`--all`) | each transition's `from` equals the previous `to`, and the last `to` equals the reported final state (§21.6 rule 3) — continuity, not edge legality | **0 violations** |
| OHLC coherence (`--ohlc`, `--all`) | every bar satisfies `low <= open, close <= high`; only bars with a MISSING field are skipped (GX-18's deliberate case) | **0 violations across 23 fixtures** |
| `eps_break` rule 1 (`--all`, gating) | HD-13 rule 1: every ORDINARY fixture's classification is invariant under ±20% of the documented `eps_break`. **This FAILS the run**, rather than printing a verdict — GX-15 is the single fixture HD-13 exempts by design and is whitelisted explicitly | **all 22 ordinary fixtures comply** |
| `eps_break` rule 2 (`--all`, gating) | HD-13 rule 2: **exactly one** fixture is retained as the boundary case. Asserted two ways, because a whitelist is otherwise unfalsifiable — (a) the whitelisted fixture MUST still be non-invariant, so a stale entry is caught; (b) the whitelist MUST name exactly one fixture and that fixture MUST exist, so a *deleted* boundary case is caught too | **1 entry (GX-15), present and still non-invariant** |
| `eps_break` sweep (`--robustness`, informational) | wider sensitivity picture | **22 / 23 invariant at ±20%** (exception: GX-15, by design) · **21 / 23 across 0.5×–2×** (exceptions: GX-15 and GX-12, the latter compliant with HD-13 and leaving the band only at 0.5×). Counted from the committed `causal_record.eps_break_robustness` sweeps, not asserted |

### Corrections from the independent review chain (2026-07-25)

The first head of this audit (`c27a2d6`) was routed through Verification, Code Review,
Project Audit and Strategic Review. The chain ran **seven successive heads** (`c27a2d6` → `c0ede4d` → `9d704e0` → `c10612c` →
`53b554a` → `4532492` → `a1e6a0f`) and six correction rounds. This table records what each
round found and how it was corrected; a cell annotated "corrected again" was fixed in a
later round than the one that first raised it. **Findings against the CHECKS themselves are
listed alongside findings against the fixtures** — a verification log that records only the
defects its own tooling caught would be measuring the wrong thing. They are recorded because a verification log that hides its
own misses is worth nothing.

| Finding | Correction |
|---|---|
| **GX-14's tie was not a tie in IEEE754.** The exact-decimal ladder `100·0.9^(t/10)` ties in real arithmetic but not in doubles: computed slopes differed by ~1e-17, one step won outright and another did not re-bind at all. Decisively, the selected anchor **flipped between (40, 65.61) and (30, 72.90)** depending on whether the slope was computed as `(ln H − ln HA)/Δt` or `ln(H/HA)/Δt` — algebraically identical readings of §7. An expected value that depends on floating-point associativity is not reproducible evidence (§0, §20.3). | Rebuilt on a **bit-exact** tie: `r = 0.83`, second candidate at exactly twice the bar distance. Verified identical under three formulations of §7. The harness's tie test now uses **exact equality with no tolerance**; its previous `1e-12` slack was what made a strictly-steeper candidate look like a tie. **Corrected again in round 3:** this cell originally justified the tie as *"`r² = 0.6889` exactly representable at 2dp"*, which is **false** — as a double, 68.89 is 68.8900000000000005684. The tie holds because `log(68.89)` equals `2·log(83) − log(100)` **bit-for-bit in the libms tested** (V8, CPython), and IEEE 754 does **not** require `log()` to be correctly rounded — so an engine on a different math library MUST re-check this fixture specifically. That caveat is recorded in GX-14's own `notes`. |
| **GX-17 bar 20 was physically impossible** — close 74.00 below its own low 78.00 — and the design as stated was unachievable, since `FAILED_BREAKOUT` needs a close below 77.73 while `low ≤ close`. | Low corrected to 73.50. The real contrast with GX-05 is that GX-17's bar **straddles** the frozen line while GX-05's lies entirely below it. No expected value changed (§15 fires first, and the low is read only by the §16 return leg). An **OHLC-coherence input guard** was added so the class cannot recur; all 23 fixtures now pass it. |
| **GX-12 bars 3–4 had `open` above `high`** (pre-existing, from before this branch). | Corrected; geometry never reads `open`, so no expectation changed. |
| **The `eps_break` robustness count was wrong**: "22 of 23 invariant across 0.5×–2×, single exception GX-15". | Corrected twice — the first correction ("23 of 23 at ±20%") was also wrong, because GX-15 flips at the 0.8× point. Counted from the committed sweeps: **22 of 23 at ±20%** (exception GX-15, which HD-13 exempts by design, so **all 22 ordinary fixtures comply**) and **21 of 23 across 0.5×–2×** (GX-15 and GX-12, the latter compliant and leaving the band only at 0.5×). Three successive wrong values for one statistic is why HD-13 rule 1 is now **enforced by the harness** rather than asserted in prose. |
| **GX-20's tightest pierce was mis-stated** as `0.0322635` in prose while the fixture recorded `0.0322638`. | Prose corrected; the fixture was right. |
| **GX-15's flip value was wrong** (`≤ 0.0082430`). | Corrected twice. The first correction (`< 0.00824265`) was still wrong *in the other direction*: 6-significant-figure rounding falls **below** the true boundary, so at exactly `0.00824265` the breakout does fire. The exact excesses are now quoted at full precision — `0.008242654587` (close/`eps_break`) and `0.018534340624` (high/`eps`) — and the false claim that the fixture stays `ACTIVE` at the rounded value is removed. |
| **The fixtures omitted the §21.6 re-selection reason codes.** §21.6, §21.9 and the §10 note all state that a pre-breakout re-selection emits `LINE_ESTABLISHED` for the line effective at `t+1`; no fixture recorded it, so an engine written faithfully from the spec would have **failed** exact reproduction. | The fixtures now comply with the approved spec: every re-selection records a `LINE_ESTABLISHED` transition at its effective bar. The spec text was **not** amended — following an approved rule is compliance, changing it would have been a product decision. |
| **`--formation` check (d) could not fail.** It replays at several `k`, but the model never reads `k`, so `k`-independence is *structural*, not empirical, and the sweep is not evidence. | The claim is downgraded to what it is, the binding evidence is re-attributed to the **fixtures** (GX-08, GX-19, GX-23 and the 9 non-pivot `B*` fixtures), and a **positive control** was added: perturbing either formation gate must change an outcome, so checks (a)–(d) cannot pass vacuously. |
| **Nothing in CI re-derived the fixtures.** Every claim here was an author-run, point-in-time assertion. | `node tools/fixture-replay.mjs --all` and `node tools/check-evidence.mjs` now run in `.github/workflows/governance-validation.yml`, so this evidence is continuously enforced rather than asserted once. |
| **GX-19's transition list was not a valid walk of the §11 state machine.** Its bar-16 `LINE_ESTABLISHED` was emitted *after* `BREAKOUT_CONFIRMED` and declared `from: ACTIVE` once the state had moved to `BROKEN_OUT`. Because the transition list is compared by exact equality, that was on its way into the contract. Found at `c0ede4d` by Verification, Code Review and Strategic Review independently. | The record now precedes the event, per §21.2 step 1. A **transition-continuity check** was added so an incoherent list fails the run rather than being silently baked in. |
| **The `checkOhlc` gate was vacuous** — its exemption skipped any fixture whose `inputGuards` result carried `INVALID_INPUT`, but the coherence clause of `inputGuards` *emits* that code, so the gate exempted precisely the class it exists to catch. Fed the historical GX-17 defect it returned `[]`. Found at `9d704e0`. | The blanket exemption was removed at `c10612c`; only bars with a missing field are skipped. Proven able to fire on that same defect. |
| **The HD-13 boundary whitelist fired falsely on scoped runs** — `checkBoundaryWhitelist` read the invocation's scoped fixture list rather than the set, so `--all GX-01` reported a repository-wide violation that was false. Found at `53b554a`. | It now reads the full set. A whitelist of size ≠ 1, or one naming a fixture that no longer exists, still fails. |
| **The governing table below was hand-maintained and unguarded**, and had gone stale on GX-14 after that fixture was rebuilt. Found at `c0ede4d`. | The table is now **emitted by `tools/fixture-replay.mjs --table` and diffed against this file by `--all`**, so a row that disagrees with the fixtures fails CI. |
| **The committed `causal_record` blocks were never re-derived.** The narrative evidence layer — where six of seven rounds found their defects — had no check at all. | `--all` now regenerates each block via `buildRecord()` and fails on any difference. |
| **The decision-register provenance for HD-12/13/14 was overstated**, and HD-13 cited an artifact that does not exist. | Corrected in `human-decisions.md`: all three now disclose that the ruling reached the repository as a direct Product Owner instruction to the session, with **no posted GitHub artifact**, and that ratification is outstanding. |

### Scope of the "23 / 23 reproduce exactly" claim

It covers: the ATH anchor, the second anchor, slope, intercept, line values (exact at 6
significant figures), state transitions, reason codes, final state and breakout bar. It does
**not** cover `flags` (authored per fixture, not compared), §12 touch counting, §13.4 volume,
or the §16 `h_hold` deferred-hold branch — all four are unimplemented in the reference model
and disclosed in its header. No committed fixture depends on the `h_hold` branch: every
retest in the set satisfies both legs on the same bar, which was checked explicitly.

### Discharge of the two open items carried above

- **"FURTHER CAVEAT … UNRESOLVED" (GX-09, GX-15 anchors).** Resolved by **HD-12**: selection
  is neither full-history-retroactive nor frozen-at-formation but **rolling and causal**.
  Both fixtures were re-derived accordingly; the `geometry_check.open_issue_2026_07_25`
  flags are removed. No end-window exclusion was reinstated, so RM-01 (whose approved `B*`
  sits 3 bars from the end of its series) remains consistent.
- **"AUTHOR-SUPPLIED RE-DERIVATION — independent re-verification PENDING" (GX-08, GX-20).**
  Discharged. GX-08 is re-verified and **confirmed unchanged** (`B* = (1,98)`,
  `m = −0.0202027`, `b = 4.60517`, ACTIVE); GX-20 is re-verified and **found defective**,
  then replaced by the causal construction above.

### Separation of duties

The reference model and the fixture set in this change were produced in the same session,
so this section is **author-adjacent evidence, not an independent verification verdict**
([GOV-011](../../governance/separation-of-duties.md)). Its value is that it is
**mechanically reproducible by anyone**: `node tools/fixture-replay.mjs --all` re-derives
every number here from `input.csv` and the specification alone. The independent verdict is
recorded by the Verification, Code Reviewer, Project Auditor and Strategic Product Reviewer
passes on the exact final head of [PR #18](https://github.com/tomerYannay/4UR4/pull/18).

---

*This log records verification only. It authorizes no build; a detector that reproduces these
fixtures is implemented only when a Ready ticket exists and the freeze is lifted per-scope.*
