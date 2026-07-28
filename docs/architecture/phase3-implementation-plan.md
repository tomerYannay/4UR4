# Phase 3 — Breakout, freeze, retest, failure, expiry: implementation plan

> **Authority:** Technical design (Architect). This document plans work; it builds
> nothing and authorizes nothing. It is scoped to `engine/` only.
> No new top-level directory, no new executable tool, nothing under `api/`, `db/`,
> `scanner/`, `worker/`, `dashboard/`, `alerts/`, `providers/`.
>
> **Which lift applies — corrected, and dated (M-52).** As first written, this
> block cited the [GOV-015](../../governance/build-freeze.md) lift as
> `scope: ["engine/"]` **with no phase qualifier**, which reads as a
> directory-scoped lift. The lift it named is narrower: `build-freeze.md` heads it
> **"Scoped lift — Phase 2 `engine/` only"** and **HD-22** rules it for *"Phase 2
> work under `engine/` and nothing else"*. A Phase-3 implementer reading the
> uncorrected line would have concluded they were already lifted; they were not.
> **The position as of this correction:** a **Phase 3** lift now exists —
> **HD-24 §3**, Product Owner, 2026-07-28,
> [#39](https://github.com/tomerYannay/4UR4/issues/39) — granting the
> `ACTIVE → BROKEN_OUT` transition, `Λ^F` freezing (§21.5), retest (§16), failed
> breakout (§15) and expiry/recompute (§17) inside `engine/`. The freeze marker's
> `scope` is still `["engine/"]` **because the directory did not change**, so the
> machine check does not distinguish the two lifts; the prose in `build-freeze.md`
> does. **The lift is not by itself permission to start:** GOV-015 rule 4 ties a
> lift to a specific approved, **Ready** ticket, and ticket (g) is **not Ready** —
> see [`../../product/planning/ticket-set.md`](../../product/planning/ticket-set.md).
> *(**Superseded later the same day**, and quoted rather than replaced because this
> block is a dated correction record: **ticket (g) became READY on 2026-07-28**, once
> the four specification escalations were ruled and the Phase 2 exit determination
> was made. GOV-015 rule 4 is now satisfied. See the ticket, and the correction block
> immediately below.)*
>
> **E2-AUTHOR-B declared read-abstention, declared on the artifact (M-53).** *Not a
> clean room, and the earlier heading's word "clean-room" is withdrawn rather than
> reinterpreted.* **P1 was not used** — the attestation records **"P1 WAS NOT
> USED"** and that *"the model was present on disk throughout"* — so no separate
> repository excluded the quarantined blobs from the object store. What follows is
> a **read-abstention self-report**, which is the mechanism document's own category
> under ***"Instruction is not a control."*** It is worth having and it is not a
> control. This plan was derived from
> `product/trendline-specification.md`, `product/roadmap.md`,
> `product/human-decisions.md`, `product/fixtures/schema/fixture.schema.json`, the
> committed golden `input.csv` / `expected.json` files, and the committed
> `engine/` source. **`tools/fixture-replay.mjs`, `product/fixtures/VERIFICATION.md`
> and `product/fixtures/real/RM-01/expected-causal.json` were not opened, read,
> grepped or quoted.** Every numeric derivation below is re-derived here from the
> specification and the fixtures' own recorded inputs and expectations, and is
> shown with its arithmetic so a reviewer can re-check it without the model.
> Agreement with the reference model earns no credit (HD-15 condition 1); the
> contract is the fixtures.

---

> ## Correction block — 2026-07-28: two clauses contradicted by the OQ-P3-5 ruling
>
> **Recorded on the M-52 / M-53 pattern: dated, in place, with the superseded text
> quoted rather than deleted.** The plan's own §11 escalated **OQ-P3-5** and resolved
> it *provisionally* as *"the **first**"* breakout episode supplying the reported
> `Λ^F` and `confirmed_bar`. **The Product Steward has ruled it the LATEST**
> ([`../../product/trendline-specification.md`](../../product/trendline-specification.md)
> §21.4 and §22, 2026-07-28), and two clauses written on the `first` reading are
> therefore **wrong and must not be implemented as written**. Both are the
> Architect's to restate; they are named here so no implementer meets them silently.
>
> 1. **§8.3, milestone M4 — `stop_bar` as an alias for `confirmed_bar`.** The alias
>    holds **only while a series has exactly one breakout episode**. Under the
>    LATEST ruling the reported `confirmed_bar` moves to each new episode's freeze,
>    while a series' engine-derived **stop bar** does not follow it. RM-01 is
>    unaffected — it has one episode — so **no committed expectation changes**; what
>    changes is that the alias may not be relied on in general, and an engine that
>    encodes it will be wrong on the first two-episode series it meets.
> 2. **§6 / EV-P3-10 — the prefix-truncation clause.** As written it asserts that
>    *"for every `k ≥ confirmed_bar`, `frozen_line` is field-identical to the full
>    run's"*. **False the moment a later episode exists:** truncating between the
>    first and second breakouts reports the **earlier** `Λ^F`, so the two runs differ
>    by construction. The invariant is sound only for **`k ≥` the LATEST episode's
>    `confirmed_bar`**, and must be stated that way — otherwise a property test
>    asserting it will either fail honestly on a two-episode generator or, worse,
>    pass vacuously on a corpus that has none.
>
> **Neither correction moves a committed expectation.** Measured 2026-07-28: **zero
> golden fixtures carry more than one `BREAKOUT_CONFIRMED`**, so nothing in the
> corpus distinguishes the two readings — which is precisely why the ruling had to
> be made by a decision-maker rather than discovered by a test.
>
> **No integrity evidence depends on this edit.** The plan's pinned digest was
> already **superseded and re-recorded** at
> [`../../product/maintenance-backlog.md`](../../product/maintenance-backlog.md)
> **M-51** when M-52 and M-53 were fixed in place, on the ruling that *"'we cannot
> fix the error because we hashed the error' must not become precedent."* The same
> disposition applies here: this block changes the file, and **M-51's digest is stale
> by design again**. Whoever next computes it should re-record it there; the Product
> Steward has no shell and computes none.

---

## 0. Summary

Phase 2 stopped the engine at the §13.1 predicate and named the stop a *stop*,
deliberately not `Λ^F`. Phase 3 turns that stop into a transition and adds the
four post-breakout behaviours the roadmap's behavioural boundary rule assigns to
it: **confirmed breakout** (§13.2), **freeze** (§21.5), **retest** (§16),
**failed breakout** (§15), **expiry/recompute** (§17).

The delta is small and the seams are already cut. Concretely:

| Change | Kind |
|---|---|
| `engine/frozen.py` (new, ~120 lines) — `FrozenLine` and the three post-breakout predicates | new module |
| `engine/causal.py` — turn the `break` at the §13.1 predicate into a transition; add the post-breakout branch; suspend re-selection; always append the tail seal; track per-bar state-at-start | edit |
| `engine/params.py` — add the six §15/§16/§17 parameters with the D-TL-08/09/10 defaults | edit |
| `engine/logspace.py` — three pinned comparison forms (`falls_below`, `at_or_below`, `at_or_above`) | edit |
| `engine/state.py` — grow the docstring; the closed sets do **not** change | edit (comments) |
| `engine/trace.py` — `active_line_at` must return the **governing** line and the real state-at-start | edit |
| `engine/detector.py` — expose `confirmed_bar`, `frozen_line`; keep `stop_bar` and `line_at_stop` as-is | edit |
| `engine/tests/conformance.py` — assert the 7 breakout fixtures **in full**; extend the event, sweep and gate-trace comparisons | edit |
| `engine/tests/test_rm01.py` — re-scope the B-clause's negative assertions (see §8) | edit |
| `engine/tests/test_architecture.py`, `test_determinism.py`, `test_properties.py` | edit |
| `engine/tests/test_units.py` — new boundary unit tests for the windows the corpus does not exercise (§9.3) | edit |

**No fixture, `expected.json`, `annotation.json` or parameter is edited.** Every
disagreement found below is recorded as an escalation in §11, not reconciled.

---

## 1. The conformance target, re-derived from the fixtures

The brief's summary of the 7 fixtures with a non-null `confirmed_bar` is
**correct as stated**, and I verified each against its `expected.json` and
`input.csv`. Below is the derivation, because the plan must show the spec
defaults actually produce these bars.

All seven share `eps = 0.02`, `eps_break = 0.01`, `min_formation_bars = 8`,
`min_ath_age_bars = 3`, `tolerance_version = "tol-2026.07-illustrative"`.
Notation: `ŷ_F(u) = m^F·u + b^F` on the frozen line.

### 1.1 The five that share the `A=(0,100), B*=(6,93)` construction

`m^F = (ln 93 − ln 100)/6 = −0.012095115472472587`, `b^F = ln 100 = 4.605170185988092`
(exactly the values `causal_record.events[0].line` records at full double precision).
`ŷ_F(16) = 4.411648338`, `ŷ_F(17) = 4.399553223`, `ŷ_F(18) = 4.387458107`,
`ŷ_F(19) = 4.375362992`, `ŷ_F(20) = 4.363267877`, `ŷ_F(21) = 4.351172761`,
`ŷ_F(22) = 4.339077646`, `ŷ_F(23) = 4.326982530`.

**Breakout, all five:** `ln C[16] = ln 86 = 4.454347296 > 4.411648338 + 0.01`
→ margin `0.032698958` → `sig6 = 0.032699`, matching each fixture's
`events[].margin` (which is therefore **net of `ε_break`**, not the raw
clearance — the same distinction the roadmap draws for RM-01).

| Fixture | bars | post-breakout data | derivation at the default parameters | expected |
|---|---|---|---|---|
| **GX-04** | 23 | L/C: 17→85/87, 18→86/88, 19→84/85, 20→**78/82**, 21→81.5/84, 22→83/85 | §15 never fires (every close is far above `ŷ_F − 0.01`). §16 return leg `ln L ≤ ŷ_F + 0.01` fails at 17 (4.442651 > 4.409553), 18 (4.454347 > 4.397458), 19 (4.430817 > 4.385363); **holds at 20**: `ln 78 = 4.356709 ≤ 4.373268` (room `0.0165590`). Hold leg same bar: `ln 82 = 4.406719 ≥ 4.353268` (room `0.0534514`). | `RETEST_HELD` @20 → `RETESTED` ✓ (fixture records exactly `return_margin 0.016559`, `hold_margin 0.0534514`) |
| **GX-05** | 23 | C: 17→85, 18→83.5, 19→82.5, 20→**74** | §15: no close is below `ŷ_F − 0.01` at 17–19. At 20: `ln 74 = 4.304065 < 4.353268` → fires, `20 − 16 = 4 ≤ F_fail = 10`. Margin `(ŷ_F(20) − 0.01) − ln 74 = 0.049202784` → `sig6 0.0492028`. | `FAILED_BREAKOUT` @20 ✓ (fixture records `margin 0.0492028`) |
| **GX-11** | 19 | L/C: 17→85/87, 18→86/88 | §15 no; §16 return leg fails at 17 and 18 (as GX-04); `18 − 16 = 2 < E_expiry`. | terminal `BROKEN_OUT` ✓ |
| **GX-16** | 19 | identical bars to GX-11 (only volume differs) | same | terminal `BROKEN_OUT` ✓ |
| **GX-17** | 24 | L/C: 17→84/85, 18→83/83.5, 19→82/82.5, 20→**73.5/74**, 21→72/73, 22→71/72, 23→70/71 | §15 at 20: `ln 74 = 4.304065 < 4.353268` → fires. §16 return leg *also* holds at 20 (`ln 73.5 = 4.297285 ≤ 4.373268`) but the hold leg fails at 20, 21, 22, 23 (`4.304065 < 4.353268`; `4.290459 < 4.341173`; `4.276666 < 4.329078`; `4.262680 < 4.316983`) — never reclaims within `h_hold = 3`. | `FAILED_BREAKOUT` @20, `flags: ["NOT_RETESTED"]` ✓ |

### 1.2 GX-07 — expiry

`B* = (6, 94)`, `m^F = (ln 94 − ln 100)/6 = −0.010312567286347996`,
`b^F = 4.605170185988092`. Breakout at 10: `ln 95 = 4.553877 > ŷ_F(10) = 4.502044 + 0.01`
→ margin `0.041832` → `sig6 0.0418324` ✓.

Bars 11–110 are all `H=95, L=92, C=94`.

- **§15 never fires:** `ln 94 = 4.543295 < ŷ_F(t) − 0.01` requires
  `0.010312567·t < 0.051875` i.e. `t < 5.03` — impossible for `t ≥ 11`.
- **§16 never returns:** `ln 92 = 4.521789 ≤ ŷ_F(t) + 0.01` requires
  `0.010312567·t ≤ 0.093382` i.e. `t ≤ 9.05` — impossible for `t ≥ 11`.
  (`W_retest = 20` would in any case close the window at bar 30.)
- **§17 fires at exactly `t = 110`:** `110 − 10 = 100 ≥ E_expiry = 100`, and
  `109 − 10 = 99 < 100`. `ŷ_F(110) = 3.470787784` → `sig6 3.47079` and
  `exp(·) = 32.1621`, matching `expected_line_values["110"]`.
- No new ATH: post-breakout highs never exceed `HA = 100`.

→ `EXPIRED_POST_BREAKOUT` @110, `BROKEN_OUT → NONE`, `expected_final_state: "NONE"`,
and `expected_second_anchor` still reports `(6, 94)` — the §21.4 reporting rule
("`Λ^F` … retained even after `EXPIRED_POST_BREAKOUT`"). ✓
**This is the only fixture whose window boundary is exercised exactly.**

### 1.3 GX-19 — the SC-2 fixture

`A = (0, 200)`. `B*_16` over `S_16` is the max-slope envelope-valid candidate:
`slope(A,(15,119)) = (ln 119 − ln 200)/15 = −0.03461292489576711` beats
`(14,120.5) = −0.036190`, `(13,126) = −0.035541`, `(12,130) = −0.035899`.
`b^F = ln 200 = 5.298317366548036`.

**Breakout at 16.** `m^F·16 = −0.553806798`, so `ŷ_F(16) = 4.744510569` →
`sig6 4.74451`, matching `expected_line_values["16"]`. `C[16] = 119`, so
`ln C[16] = 4.779123493 > 4.744510569 + 0.01` ✓ and the recorded margin is
`ln C[16] − ŷ_F(16) − ε_break = 0.024612924` → `sig6 0.0246129` ✓ — the same
figure HD-13 rule 4 names as the robust causal margin that must be preserved
rather than reverted to the full-series `ACTIVE` expectation.

Retest at 17: `ŷ_F(17) = 4.709897643` → `sig6 4.7099` ✓.
Return: `ln L[17] = ln 111 = 4.709530201 ≤ 4.719897643` (room `0.0103674` ✓).
Hold: `ln C[17] = ln 112.5 = 4.722953221 ≥ 4.699897643` (room `0.0230556` ✓).
§15 does not fire at 17 (`4.722953 > 4.699898`). Bars 18–20: state `RETESTED`,
no further edge available (see §5.4), no new ATH, `20 − 16 = 4 < 100`.
→ `RETEST_HELD` @17 → final `RETESTED` ✓.

### 1.4 Three more Phase-3 conformance targets nobody listed

**The 7 fixtures are not the whole target.** `causal_record.eps_break_robustness`
records `final_state` at **every** sweep point, and at three off-baseline points
the recorded state is a Phase-3 state on a fixture whose baseline
`confirmed_bar` is `null`. The Phase-2 harness compares `final_state` in the
sweep **only when `breakout_bar` is null**, so these are currently unasserted.
Phase 3 must assert them (§7.4), and they must be derived here because they are
the corpus's only discriminating evidence for two design decisions:

| Fixture | sweep point | recorded | derivation |
|---|---|---|---|
| **GX-12** | `eps_break = 0.005` (0.5×) | `breakout_bar 15`, `final_state FAILED_BREAKOUT` | `Λ_15 = A(0,130), B*(13,117)`, `m = −0.008104655050602`, `b = ln 130 = 4.867534450`. `ŷ(15) = 4.745964625`; `ln 116 = 4.753590191 > 4.750964625` ✓ breakout @15 (and *not* at `ε_break = 0.008`: `4.753590 < 4.753965`, matching the fixture's recorded `close_margin −0.00237443` at 0.01). Frozen. Bar 16: `ŷ_F(16) = 4.737859969`; §15: `ln 113 = 4.727387819 < 4.727859969` ✓ **fires, by 4.72e-4 log units**. `16 − 15 = 1 ≤ 10`. Bars 17–21: nothing (see below). → `FAILED_BREAKOUT` ✓ |
| **GX-15** | `eps_break = 0.005` and `0.008` | `breakout_bar 28`, `final_state RETESTED` | `Λ_28 = A(0,100), B*(20,90)` (the roll's last re-selection before 28 is effective at bar 21), `m = −0.0052680258`, `b = 4.605170186`. `ŷ(28) = 4.457665464`; `ln 87 = 4.465908119` clears at `ε_break < 0.008242655` — exactly the flip value HD-13's evidence names — so it breaks out at 0.005 and 0.008 and not at 0.01 ✓. Bar 29: `ŷ_F(29) = 4.452397438`; §15 no (`ln 85.3 = 4.446174 > 4.442397`); §16 return `ln 84.3 = 4.434382 ≤ 4.462397` ✓, hold `4.446174 ≥ 4.442397` ✓ → `RETEST_HELD` @29 → `RETESTED` ✓ |

**What GX-12 @0.5× proves, and nothing else in the corpus does.** At bar 16 the
§16 return leg *also* holds (`ln 112 = 4.718499 ≤ 4.747860`), and its hold leg
would be satisfied **two bars later** at bar 18 (`ln 112 = 4.718499 ≥
ŷ_F(18) − 0.01 = 4.711651`). An engine that deferred the failure decision to see
whether the hold arrived within `h_hold` would produce `RETESTED`; the fixture
says `FAILED_BREAKOUT`. So the §15-before-§16 precedence of §5.3 is
**fixture-forced, not chosen** — and §21.8 rule 2 independently forbids the
deferral, because bar 16's classification must be final at bar 16.

**What GX-05 / GX-17 / GX-12 @0.5× jointly prove:** `FAILED_BREAKOUT` is
**terminal**. All three have bars after the failure (2, 3 and 5 respectively) and
all three end `FAILED_BREAKOUT` with no further transition record. If the engine
returned to `NONE` and recomputed, the formation gates would be satisfied
immediately on the next bar (`|S_t| ≥ 8`, `tA` old, `B*` exists) and the final
state would be `ACTIVE` with extra `LINE_ESTABLISHED` records. It is not.

### 1.5 A derived rule the fixtures force: the post-breakout windows are open at the left

§15 and §16 say "within `F_fail` / `W_retest` bars of the breakout bar" without
saying whether the breakout bar itself is in the window. **The fixtures decide
it: the breakout bar is excluded.** On GX-04 at bar 16 the §16 return leg holds
(`ln L[16] = ln 82.5 = 4.412798 ≤ ŷ_F(16) + 0.01 = 4.421648`) and the hold leg
holds trivially (the close is above the line by construction — that is what a
breakout is), so an engine that evaluated §16 on the breakout bar would emit
`RETEST_HELD` at bar 16. The fixture records it at bar 20. The same holds for
GX-05, GX-11, GX-16, GX-17 and GX-12 @0.5×.

**Governing form, therefore:**

```
§15 failure window   :  breakout_bar <  t  ≤  breakout_bar + F_fail
§16 return window    :  breakout_bar <  t  ≤  breakout_bar + W_retest
§16 hold window      :  r            ≤  t  ≤  r + h_hold        (r = the return bar)
§17 expiry           :  t − breakout_bar ≥ E_expiry
```

Note the asymmetry, which is not an inconsistency: §17 is written as an explicit
`≥` inequality on the elapsed count and GX-07 pins it at exactly 100, whereas
§15/§16 are written in prose ("within … bars of the breakout bar") and the
fixtures pin the left edge. This is recorded as **ESC-3** in §11 because the
right edges (`+F_fail`, `+W_retest`, `+h_hold`) are **not** exercised by any
fixture and the reading above is the Architect's, not a fixture's.

---

## 2. Parameters — where they live, and what the fixtures actually say

### 2.1 Correction to the brief's premise

The brief states the six Phase-3 parameters are "**not** carried in any fixture's
`params` block". **That is factually wrong**, and the correction matters, because
it converts most of the parameter risk from "escalate" to "cross-check". Measured
across `product/fixtures/golden/*/expected.json`:

| Parameter | Carried by | Value carried | Spec default |
|---|---|---|---|
| `eps_fail` | GX-04, GX-05, GX-17 | `0.01` | `0.01` (D-TL-08) |
| `F_fail` | GX-04, GX-05, GX-17 | `10` | `10` (D-TL-08) |
| `eps_retest` | GX-04, GX-17 | `0.01` | `0.01` (D-TL-09) |
| `W_retest` | GX-04, GX-17 | `20` | `20` (D-TL-09) |
| `h_hold` | GX-04, GX-17 | `3` | `3` (D-TL-09) |
| `E_expiry` | GX-07 | `100` | `100` (D-TL-10) |

`GX-11`, `GX-16`, `GX-19`, `GX-12` and `GX-15` carry **none** of them. The
schema (`fixture.schema.json` `params`) declares all six as optional properties
with `additionalProperties: true`.

**Every carried value equals the specification default.** So:

- **No escalation on parameter values is required.** §1's derivations reproduce
  every expected transition bar at the D-TL-08/09/10 defaults, on both the
  fixtures that carry them and the fixtures that do not. No fixture needs a
  non-default value.
- **The defaults must live in `engine/params.py`**, because five of the ten
  fixtures with Phase-3 behaviour supply nothing. They cannot come from the
  fixtures.
- **Where a fixture *does* carry a value, the engine must read it and it must
  agree with the default.** That agreement is asserted, not assumed — see
  `EV-P3-2` in §10. A future fixture carrying a non-default value would then
  fail loudly rather than being silently overridden by a default.

### 2.2 `engine/params.py` — the change

Add six fields to `DetectorParams` **with defaults**, beside the existing
ratified set:

```python
    #: §15, D-TL-08 — Human-approval: no.  Carried by GX-04, GX-05, GX-17 at
    #: exactly these values; defaulted for the fixtures that omit them.
    eps_fail: float = 0.01
    F_fail: int = 10
    #: §16, D-TL-09 — Human-approval: no.
    eps_retest: float = 0.01
    W_retest: int = 20
    h_hold: int = 3
    #: §17, D-TL-10 — Human-approval: no.
    E_expiry: int = 100
```

Rules that must hold, and why each is not arbitrary:

1. **These six get defaults; `eps_break` still does not.** `eps_break` is
   *unlocked by ruling* (HD-03 / §13.5 — "no locked default"), so
   `DetectorParams` must keep refusing to invent one. The six above are
   `Human-approval: no` decisions **with stated defaults**, so defaulting them is
   the specification's own instruction, not an engine choice. The docstring must
   say exactly this, because the two cases look alike and are not.
2. **They are *not* added to `REQUIRED_FIXTURE_PARAMS`.** That tuple names
   parameters that "may never be defaulted silently when a caller supplies a
   parameter block" — and five fixtures legitimately omit these. Adding them
   would fail GX-11/16/19/12/15 on a fixture-immutability-protected file. Instead:
3. **`from_fixture_params` reads each of the six when present, and defaults it
   when absent** — and a dedicated test (`EV-P3-2`) asserts that for every
   fixture that carries one, the carried value equals the module default. That
   test is the mechanism that keeps an unnoticed fixture/engine parameter
   disagreement from being papered over by a default.
4. `__post_init__` validates: `eps_fail ≥ 0`, `eps_retest ≥ 0`, `F_fail ≥ 0`,
   `W_retest ≥ 0`, `h_hold ≥ 0`, `E_expiry ≥ 1`.
5. `replace()` and `with_eps_break()` must carry all six through. (Both build a
   full kwarg dict today; forgetting a field there silently resets it to the
   default in every sweep. A unit test asserts `params.replace() == params` and
   `params.with_eps_break(x).eps_fail == params.eps_fail` for all six.)

### 2.3 `tolerance_version` covers all of them

§21.5's frozen-field table defines `tolerance_version` as "the named tolerance
set in force (`ε`, `ε_touch`, `ε_break`, `ε_fail`, `ε_retest`)". `DetectorParams`
already carries `tolerance_version`, threaded from the fixture's `params`. Phase 3
adds no second version tag: the six new values ride the existing string, and
`Λ^F` records that string verbatim (§4.1).

---

## 3. `engine/logspace.py` — three new pinned comparison forms

`logspace.py` is the *only* site of log arithmetic and comparison, and its
pinned-form table is load-bearing (GX-14 already demonstrated an anchor flipping
on an algebraically equivalent rearrangement). Phase 3 needs three predicates and
three margins, and each must be pinned there, RHS formed first, never inlined:

```python
def falls_below(lhs, y_hat_value, tolerance):     # §15
    """``lhs < y_hat - tolerance`` — strict."""
    return lhs < y_hat_value - tolerance

def at_or_below(lhs, y_hat_value, tolerance):     # §16 return leg
    """``lhs <= y_hat + tolerance`` — non-strict (§16.1 writes ≤)."""
    return lhs <= y_hat_value + tolerance

def at_or_above(lhs, y_hat_value, tolerance):     # §16 hold leg
    """``lhs >= y_hat - tolerance`` — non-strict (§16.2 writes ≥)."""
    return lhs >= y_hat_value - tolerance
```

Strictness is taken **verbatim from the specification's own inequality glyphs**:
§15 writes `<`, §16.1 writes `≤`, §16.2 writes `≥`. §13.1's `>` and §10.1's `>`
are already pinned in `exceeds`. Nothing in the corpus sits on any of these
boundaries (the tightest margins are GX-12 @0.5×'s `4.72e-4` and GX-15 @0.8×'s
`2.43e-4`, both ~1e12 ulps clear), so no fixture depends on the strictness — but
the strictness must still match the spec, and must be unit-tested at the exact
boundary (`EV-P3-9`).

The three margin quantities the fixtures record must be pinned in the same
algebraic form the comparison uses:

```
failure margin      =  (ŷ_F(t) - eps_fail)   - ln C[t]      # GX-05/17: 0.0492028
retest return room  =  (ŷ_F(t) + eps_retest) - ln L[t]      # GX-04: 0.016559
retest hold room    =  ln C[t] - (ŷ_F(t) - eps_retest)      # GX-04: 0.0534514
breakout margin     =  ln C[t] - (ŷ_F(t) + eps_break)       # already: StopRecord.clearance_net_of_eps_break
```

The `C-4` tie-proximity audit in `test_determinism.py` must be extended to cover
these four values on every fixture that records them. If any lands within one ulp
of a 6-s.f. rounding tie, that is **escalated**, per the audit's existing
instruction — the form is not adjusted to make the gate pass.

---

## 4. `Λ^F` — where it is captured and how it is represented

### 4.1 Representation

New in `engine/frozen.py`:

```python
@dataclass(frozen=True)
class FrozenLine:
    """``Λ^F`` — §21.5's frozen-field table, one field per row, nothing more."""
    line: Line                 # A=(tA,HA), B*=(tB*,HB*), m, b  — the §21.5 rows 1–4
    tolerance_version: str     # §21.5 row 5
    breakout_bar: int          # §21.5 row 6; == confirmed_bar (HD-03)

    @property
    def confirmed_bar(self) -> int:
        return self.breakout_bar          # HD-03: the same bar, named twice

    def y_hat_at(self, u: int) -> float:  return self.line.y_hat_at(u)
    def price_at(self, u: int) -> float:  return self.line.price_at(u)
```

`Line` already carries exactly `t_anchor, high_anchor, y_anchor, t_b, high_b, m, b`
— §21.5 rows 1–4 with nothing extra. `FrozenLine` therefore adds only the two
rows `Line` lacks. It is `frozen=True`, so "retained verbatim" is a type-level
fact and not a convention.

**Deliberately absent:** any window state (`F_fail` counters, pending retest
legs). Those are the fold's local variables, not part of the frozen line. §21.5's
table has six rows; `FrozenLine` has six fields.

### 4.2 Where it is captured — and why it must be *the same object* Phase 2 computed

Phase 2 already computes the exact quantity, at the exact moment, and refuses to
name it:

```python
# engine/causal.py, StopRecord
#     ``line`` is ``Λ_stop`` — the line active while the structure was still
#     ``ACTIVE`` … deliberately **not** named ``Λ^F``: freezing is §21.5's act
#     and Phase 3's.
```

Phase 3 respects that seam by **wrapping, not replacing**. In the fold, at the
bar where `exceeds(ln_close, y_hat_value, params.eps_break)` holds:

1. build the `StopRecord` exactly as today (same fields, same values);
2. `frozen = FrozenLine(line=stop.line, tolerance_version=params.tolerance_version,
   breakout_bar=t)` — **`stop.line`, not a recomputation**;
3. `emit(t, LineState.BROKEN_OUT, ReasonCode.BREAKOUT_CONFIRMED)`;
4. append a `BarEvent(t, BREAKOUT_CONFIRMED, {...})` carrying the fields the
   fixtures record: `line.tA`, `line.tB`, `line.m`, `line.b`, `y_hat`,
   `line_value`, `close`, `ln_close`, `margin`;
5. **do not `break`** — continue the fold in the post-breakout branch;
6. assert `frozen.line is stop.line` (object identity) as an `EngineDefect`
   invariant.

Step 6 is the whole point. RM-01's B-clause asserts `line_at_stop` field by
field; `Λ^F` is asserted against `frozen_event_line` by the golden fixtures. If
the two were computed independently they could drift and both gates could still
pass on different numbers. Identity makes drift impossible, and it makes the
Phase-2/Phase-3 relationship a checkable property: **`Λ^F` is `Λ_stop` plus a
tolerance version and a bar index, and nothing else.**

`StopRecord`'s docstring is amended to say that Phase 3 now freezes it — the
comment must not be left claiming freezing has not happened.

### 4.3 What the fixtures let us assert about `Λ^F`

`causal_record.frozen_event_line` carries `A{t,H}`, `B_star{t,H}`, `m` (6 s.f.),
`b` (6 s.f.), `breakout_bar`, `confirmed_bar`, `tolerance_version`. All seven
breakout fixtures carry it; the five non-breakout ones carry
`"frozen_event_line": null`. The harness compares all of it, **including
`tolerance_version`** and including the `null` case in both directions
(`EV-P3-3`).

Additionally, `causal_record.events[].line` records `m` and `b` at **full double
precision** (e.g. `-0.012095115472472587`). That is a stronger comparison than
6 s.f. and it is available, so the harness asserts exact equality there as well
as the 6-s.f. comparison — the same both-ways pattern `input_guard.detail.log_jump`
already uses.

---

## 5. The fold — §21.2's order extended

`engine/causal.py`'s per-bar order (a)–(e) is retained verbatim and extended. The
new element is a **post-breakout branch** and an explicit **suspension** of steps
(a) and (e)'s re-selection while the frozen line governs.

### 5.1 Per-bar order, complete

For evaluation bar `t`, with `state` = the effective state at the **start** of
bar `t`:

```
(a)  seal Λ_t from S_t                                        — ALWAYS (pure, §21.1)
     emit line records for bar t                              — ONLY if state ∈ {NONE, ACTIVE}
(b)  §21.7 new-ATH test: H[t] > HA(A_t)                       — BEFORE (d), (e), (f)
     retires a line-bearing state → RESET_NEW_ATH → NONE
(c)  if state is NONE and Λ_t = ⊥ : no event test may run     — §21.3
(d)  if state is ACTIVE : judge bar t against Λ_t
        §13.1 predicate → BREAKOUT_CONFIRMED, freeze Λ^F, → BROKEN_OUT
        else §10.1 pierce → WICK_BREAK record + INVALID_PIERCE code
(e)  if state ∈ {BROKEN_OUT, RETESTED} : judge bar t against Λ^F, in this order
        e1  §15 failure         (BROKEN_OUT only)  → FAILED_BREAKOUT   [terminal]
        e2  §16 retest          (BROKEN_OUT only)  → RETESTED
        e3  §17 expiry          (BROKEN_OUT, RETESTED) → EXPIRED_POST_BREAKOUT → NONE
     if state is FAILED_BREAKOUT : no test runs                — terminal, §5.4
(f)  seal for t+1: extend the prefix                          — ALWAYS
     register a Reselection                                   — ONLY if state was ACTIVE
                                                                and remains ACTIVE
```

Two structural notes:

- **(a) and (f) always run**, even while frozen and even after a terminal state.
  The prefix must keep growing so that §17's post-expiry "recomputes … over the
  full available history" is possible, and so that `causal_record.formation.gate_trace_full`
  can be compared at **every** bar. GX-04's own
  `gate_trace_full_caveat` states this precisely: an `ELIGIBLE` entry after the
  breakout bar "describes gate arithmetic only, not an active line". The sealed
  record is arithmetic; the *effective state* is separate. Phase 3 makes that
  separation explicit rather than implicit (§5.5).
- The tail seal at `t = n` is now appended **unconditionally** (Phase 2 appended
  it only when there was no stop), because `gate_trace_full` runs to
  `t = bar_count`. It never overrides `reported_line` when a breakout occurred
  (§5.6).

### 5.2 Re-selection suspension (§21.5, §21.6 step 4 must not run)

Two independent mechanisms, so that a single oversight cannot re-open it:

1. **The emit guard.** Step (a)'s `LINE_ESTABLISHED` / `ENVELOPE_TIE_LATER`
   emission and step (f)'s `Reselection` registration are both gated on
   `state ∈ {NONE, ACTIVE}` / `state is ACTIVE`. While `BROKEN_OUT` or
   `RETESTED`, §21.2 step 4 provably does not run: nothing is emitted and nothing
   is registered.
2. **The line-selection guard.** Every §15/§16/§17 test in step (e) takes its
   `ŷ` from `frozen.y_hat_at(t)`. `frozen` is a `FrozenLine`, a distinct type
   from `Line`, and the post-breakout predicates in `engine/frozen.py` accept
   **only** `FrozenLine`. A future edit that accidentally passed `sealed.line`
   into a failure test is a type error, not a wrong number.

The mechanically checkable evidence that suspension worked is already in the
fixtures: `causal_record.non_retroactive_challengers.bars` lists every bar
`u ≥ breakout_bar` whose `slope(A^F, (u, H[u])) > m^F` — the highs that *would*
have re-bound `B*` under a full-series hull. Counts verified against the
committed data: GX-04 → 7 bars (16–22), GX-11 → 3 (16–18), GX-19 → 5 (16–20),
GX-07 → 101 (10–110), each matching the prose count in its own
`rejection_rationale`. The engine computes this list and the harness compares it
element by element (`EV-P3-5`). GX-12 and GX-15 (baseline, no breakout) carry
`bars: []` with the note "No later high has a shallower slope", so the empty case
is asserted too.

### 5.3 Within-bar precedence (§21.2, §21.7, §21.6 rules 1–4)

**Order: new-ATH → failure → retest → expiry.** Grounding, clause by clause:

- **New-ATH first, and it overrides a frozen line.** §21.2 rule 5: "this test is
  evaluated on bar `t` **before** steps 3 and 4 and takes precedence over both".
  §21.7: "This applies whether the state was `ACTIVE`, `BROKEN_OUT` or
  `RETESTED` — a new ATH overrides a frozen line", and "Bar `t` MUST NOT be
  classified as a breakout of the retired line by virtue of the same high". So
  `_LINE_BEARING` in `causal.py` grows from `(ACTIVE,)` to
  `(ACTIVE, BROKEN_OUT, RETESTED)` — exactly as its own comment already
  anticipates ("Phase 3 adds `BROKEN_OUT` and `RETESTED` to this tuple").
  `FAILED_BREAKOUT` is **not** added: §21.7 enumerates three states and
  `FAILED_BREAKOUT` is not among them, and §11 gives it no outgoing edge. That is
  the literal reading of two ratified texts; it is unexercised by the corpus and
  is escalated as **ESC-4**.
- **Failure before retest.** §16 condition 3: "No structural failure (§15) during
  the window." Fixture-forced by GX-12 @0.5× (§1.4). §21.8 rule 2 independently
  forbids the alternative, which would require holding bar 16's classification
  open until bar 18.
- **Expiry last, and the order is formally rather than materially load-bearing at
  the defaults.** With `F_fail = 10`, `W_retest = 20`, `E_expiry = 100`, the
  expiry window and the other two are disjoint (`t − breakout ≥ 100` cannot
  coincide with `t − breakout ≤ 20`), so no committed configuration reaches a
  tie. The order is stated anyway, because the parameters are backtestable and a
  future configuration with `E_expiry ≤ W_retest` would reach it.
- **Failure and the retest *hold* leg are mutually exclusive on a single bar
  whenever `eps_fail ≤ eps_retest`** — failure needs `ln C < ŷ_F − eps_fail`,
  hold needs `ln C ≥ ŷ_F − eps_retest`. At the documented defaults both are
  `0.01`, so they can never both hold at the same bar. This is why the ordering
  is *only* load-bearing across bars (GX-12 @0.5×). If a future parameter set had
  `eps_fail > eps_retest` a genuine same-bar conflict would exist, resolved by
  the stated order. Recorded so it is not rediscovered as a surprise.

**§21.6 rules 1–4, applied to the new records.**

1. *Bar attribution.* `BREAKOUT_CONFIRMED`, `FAILED_BREAKOUT`, `RETEST_HELD`,
   `EXPIRED_POST_BREAKOUT` are recorded at the bar whose data satisfies them —
   they are events of their own bar, not lines taking effect later, so rule 1's
   `t+1` attribution does not apply to them. It continues to apply, unchanged, to
   the pre-breakout roll. A `RETEST_HELD` whose return leg fired on an earlier
   bar is recorded at the **hold** bar, because that is the bar at which the state
   changes (unexercised by the corpus — **OQ-P3-2**).
2. *Within-bar ordering.* Line records precede event records, because the line is
   established in step (a) and the event judged in steps (d)/(e). **GX-19 is the
   fixture that pins this across the new boundary**: at bar 16 it records
   `ACTIVE → ACTIVE / LINE_ESTABLISHED` (the roll effective at 16) *then*
   `ACTIVE → BROKEN_OUT / BREAKOUT_CONFIRMED`. The Phase-2 harness already
   compares the first of those; Phase 3 compares both, in order.
3. *State-machine coherence.* Every record's `from` equals the previous record's
   `to`, and the last `to` equals `expected_final_state`. Phase 3 adds an
   explicit assertion of this walk over the engine's own output for every fixture
   (`EV-P3-6`) — the schema describes it but nothing in `engine/` checks it today.
   `causal.py`'s existing `EngineDefect` for "state changed without a record"
   is retained and extended to the new states.
4. *Transition records vs reason codes.* Unchanged, and no new code joins
   `INVALID_PIERCE` in the code-set-only category. All four Phase-3 codes are
   genuine transition records.

### 5.4 Terminal and quiescent states

| State | Outgoing edges Phase 3 implements | Grounding |
|---|---|---|
| `BROKEN_OUT` | `FAILED_BREAKOUT`, `RETESTED`, `NONE` (expiry), `NONE` (new ATH) | §11, §21.5 ("The only exits are `RESET_NEW_ATH` and `EXPIRED_POST_BREAKOUT`" — plus §11's two edges to failure/retest) |
| `RETESTED` | `NONE` (expiry), `NONE` (new ATH) | §11 draws only `BROKEN_OUT / RETESTED → EXPIRED`; §15 says "After a `BROKEN_OUT` state"; §21.7 names `RETESTED` |
| `FAILED_BREAKOUT` | **none — terminal** | §11 gives it no outgoing edge; proven by GX-05, GX-17, GX-12 @0.5× (§1.4) |
| `EXPIRED` | **never entered** | see below |

**`LineState.EXPIRED` is never assigned.** §11 draws
`BROKEN_OUT / RETESTED ──▶ EXPIRED ──▶ NONE`, two edges; GX-07 records **one**
transition, `bar 110: BROKEN_OUT → NONE / EXPIRED_POST_BREAKOUT`, and its
`expected_reason_codes` has exactly three entries. Under HD-22 the fixture is not
edited, so the engine must implement the single-record reading. `EXPIRED` stays a
member of `LineState` because architectural test A-4 requires the engine's set to
**equal** the schema's closed set — but it is unreachable, and `state.py`'s
docstring must say so explicitly, or a later reader will "fix" the gap by
inserting an `EXPIRED` record and break GX-07. Escalated as **ESC-1**: §11 and
GX-07 describe the same behaviour with a different number of records.

`RETEST_HELD` fires at most once per breakout episode (§11 has no
`RETESTED → RETESTED` edge). Unexercised — **OQ-P3-3**.

### 5.5 The effective-state track

Phase 2 read the running state off `SealedBar.state`, which is a pure function of
the prefix and therefore says `ACTIVE` on every post-breakout bar whose gates
happen to pass. Phase 3 must not conflate the two. `CausalResult` gains:

```python
    #: The state at the START of each evaluated bar, before that bar's own
    #: transitions — the quantity ``causal_record.active_line_before_event_bars
    #: [].state_at_start`` records.  DISTINCT from ``SealedBar.state``, which is
    #: gate arithmetic over ``S_t`` and is ``ACTIVE`` on bars the frozen line
    #: governs (GX-04's own ``gate_trace_full_caveat`` says so).
    state_at_start: Tuple[LineState, ...]
    frozen: Optional[FrozenLine]
    challengers: Tuple[Challenger, ...]
```

Verified against the fixtures: GX-04 records `state_at_start` `ACTIVE` @8,
`ACTIVE` @16 (the breakout bar — *before* its own transition), `BROKEN_OUT` @20,
`RETESTED` @22. GX-17 records `FAILED_BREAKOUT` @23. GX-07 records `BROKEN_OUT`
@110 (before the expiry fires on that bar). The definition "state at the start of
the bar, before this bar's transitions" reproduces all of them.

### 5.6 What the detector *reports* (§21.4)

Unchanged rule, newly reachable cases:

```
reported_line = Λ^F   if a confirmed breakout occurred anywhere in the series
              = Λ_n   otherwise
```

Verified: GX-04 `expected_second_anchor (6,93)` = `Λ^F`; GX-19 `(15,119)` = `Λ^F`;
**GX-07 `(6,94)` with `expected_final_state "NONE"`** — the deliberate
consequence §21.4 itself names, and the case that will break any implementation
that reports "the current line". GX-12/GX-15 baselines report `Λ_n` (unchanged
from Phase 2).

`final_state` becomes always populated (Phase 2 returned `None` at a stop). This
is the single most consequential API change for RM-01 — see §8.

Two under-determined cases, both unexercised, both recorded rather than decided:
`reported_line` after `RESET_NEW_ATH` retires a frozen line (§21.4's literal
"anywhere in the series" says `Λ^F` survives — **OQ-P3-4**), and which `Λ^F` is
reported when a series contains two confirmed breakouts in two episodes
(**OQ-P3-5**). The plan's design is: `confirmed_bar` and `reported_line` name the
**first** confirmed breakout of the series, preserving the single-valued
`confirmed_bar` the schema declares and the engine-derived-stop semantics RM-01's
B-clause depends on; each later episode's breakout still gets its own
`BREAKOUT_CONFIRMED` record and event. No fixture distinguishes this.

---

## 6. Determinism and no-look-ahead

Phase 2's four structural mechanisms survive unchanged and are extended:

1. **The batch API *is* the streaming API.** `run` is still a single left fold;
   there is no second path. §21.8 rule 3's "streaming equals batch" operational
   test is therefore **still vacuous by construction**, and Phase 3 does **not**
   introduce a second incremental driver to make it non-vacuous. Adding one would
   create exactly the divergence the test exists to detect. `causal.py`'s
   docstring already says this out loud and must keep saying it; §20.5's
   requirement is discharged by the fold's structure plus the falsifiable
   substitute below.
2. **Prefix-truncation invariance is the falsifiable replacement, and Phase 3
   makes it much stronger.** `P2PrefixTruncationInvariance` currently asserts
   that running on `bars[0..k]` reproduces the record prefix at bars `≤ k`. In
   Phase 2 that was nearly vacuous past the stop, because the engine halted.
   Phase 3 must extend it to assert, for every `k ≥ confirmed_bar`:
   `truncated.confirmed_bar == full.confirmed_bar`, and
   `truncated.frozen_line == full.frozen_line` **field for field** — the exact
   property §21.5 and §21.9's bar-22 walkthrough are about. This test can now
   genuinely fail, which is the point.
3. **No geometry function ever receives the series.** Unchanged: `_seal` receives
   a `Prefix` of length exactly `t`, whose constructor asserts its own length.
   The post-breakout predicates receive a `FrozenLine` and the single bar under
   test — never the series, never a prefix.
4. **§21.8 rule 2 — no later bar may revise an earlier classification.**
   Enforced by construction: `transitions` is append-only, `TransitionRecord` and
   `FrozenLine` are `frozen=True` dataclasses, and `frozen` is assigned exactly
   once per episode (an `EngineDefect` fires on a second assignment while a
   frozen line is live). `P1NoLookAhead`'s suffix-mutation property gains a
   Phase-3 clause: mutating any bar at index `> confirmed_bar` must leave
   `confirmed_bar` and `frozen_line` byte-identical. The generator-quality
   assertion is extended to require the random corpus to contain post-breakout
   bars in the failure and retest windows, so the new clause cannot pass
   vacuously.
5. **Determinism digest.** `serialize()` in `test_determinism.py` must gain
   `frozen_line` (all six §21.5 fields, `repr()` on the floats) and
   `state_at_start`. Without that, D-3/D-6 would certify a corpus in which every
   new Phase-3 quantity was unobserved.
6. **`P3StopStability`** — described in Phase 2 as "near-vacuous by construction
   … kept because it becomes load-bearing the moment Phase 3 continues past the
   stop". That moment is now. It must be rewritten to assert, on the random
   corpus, that `frozen_line` at the end of the run equals the `FrozenLine` built
   at the breakout bar, and that no record before `confirmed_bar` changed.
7. **Purity.** No new import. `engine/frozen.py` imports only from `.causal`,
   `.logspace`, `.params`, `.state` — architectural tests A-1, A-2, A-3 apply to
   it automatically because they enumerate `engine/*.py` from the directory.

---

## 7. `engine/tests/conformance.py` — closing the gap

The current harness gates on `phase2_complete = (confirmed_bar is None)` and,
when false, asserts only bars strictly before `confirmed_bar` plus the Phase-2
records *at* the stop bar. Phase 3 **deletes that branch**: every fixture is
compared in full, and `_PHASE2_CODE_NAMES` filtering disappears from the
comparison path. The changes, one by one.

### 7.1 The branch that must go

| Site | Today | Phase 3 |
|---|---|---|
| `expected_state_transitions` | split into "strictly before `confirmed_bar`" + "Phase-2 records at the stop bar" | one `_compare_ordered` over the **whole** list, both directions, for every fixture |
| `expected_reason_codes` | set-equality only on the Phase-2 subset when `confirmed_bar` is non-null | set-equality **and** first-emission-order equality for every fixture |
| `report.check(all(code in _PHASE2_CODE_NAMES ...))` | asserts the engine emits no Phase-3 code | **replaced** by: the engine's code set equals the fixture's, and every emitted code is a member of the schema's closed set (`EV-P3-8`) |
| `expected_final_state` | compared only when `confirmed_bar` is null | compared for every fixture |
| `stop index vs confirmed_bar` | `result.stop_bar == confirmed_bar` | unchanged (`stop_bar` is retained as an alias — §8.3) |

**What must keep asserting exactly what it asserts today** (no regression of the
16 `confirmed_bar == null` fixtures): `input_guard`, `expected_ath_anchor`,
`expected_second_anchor`, `expected_log_slope`, `expected_intercept`,
`expected_line_values` at every recorded index, `causal_record.formation.t_form`
and gate traces, `causal_record.reselections`,
`causal_record.as_of_time_candidate_set`, the `WICK_BREAK` / `RESET_NEW_ATH`
event comparisons, and the both-directions "no Phase-2 event the fixture does not
record" check. All of these are Phase-2-owned and none of their code paths
changes. The 16 fixtures with `confirmed_bar == null` take
**`phase2_complete == True` today and the same comparisons tomorrow**; the only
difference is that the `else` branch no longer exists for them because they never
entered it.

### 7.2 `causal_record.frozen_event_line` — new comparison

For each fixture: if the key is `null`, assert `result.frozen_line is None`; else
compare `A.t`, `A.H` (exact price), `B_star.t`, `B_star.H` (exact price), `m`
(6 s.f.), `b` (6 s.f.), `breakout_bar`, `confirmed_bar` and
`tolerance_version` (string equality against `result.params.tolerance_version`).
Both directions.

### 7.3 `causal_record.events` — extend past the two Phase-2 names

The `if name not in ("WICK_BREAK", "RESET_NEW_ATH"): continue` filter is removed.
Field maps per event type, taken from the committed records:

| Event | Fields compared |
|---|---|
| `BREAKOUT_CONFIRMED` | `line.tA`, `line.tB` (int), `line.m`, `line.b` (**exact double** *and* 6 s.f.), `y_hat`, `line_value`, `margin` (6 s.f.), `close`, `ln_close` (`ln_close` 6 s.f., `close` exact price) |
| `FAILED_BREAKOUT` | `y_hat_frozen`, `line_value`, `margin` (6 s.f.), `close` (exact price) |
| `RETEST_HELD` | `y_hat_frozen`, `line_value`, `return_margin`, `hold_margin` (6 s.f.), `low`, `close` (exact price) |
| `EXPIRED_POST_BREAKOUT` | `bars_since_breakout` (int) |

The both-directions set check is widened from
`{WICK_BREAK, RESET_NEW_ATH}` to the whole recorded event set, so a Phase-3 event
the engine invents — or omits — fails.

### 7.4 `causal_record.eps_break_robustness` — compare `final_state` at every point

`_compare_eps_break_sweep` currently compares `final_state` only when
`point["breakout_bar"] is None`. That guard is removed; `final_state` is compared
at every recorded scale. This is the change that brings GX-12 @0.5× →
`FAILED_BREAKOUT` and GX-15 @0.5×/0.8× → `RETESTED` into the gate (§1.4), and it
tightens all seven breakout fixtures' sweeps as well (all record an invariant
Phase-3 `final_state` across 0.5×–2×; verified). `HD13EpsBreakSweep.test_c2` in
`test_determinism.py` gets the same removal.

### 7.5 `causal_record.formation.gate_trace_full` — compare every entry

The harness currently skips trace entries "beyond the engine's reach (bars at or
after the stop, which Phase 2 does not evaluate)". Phase 3 evaluates every bar
and seals every prefix including `t = n`, so **every entry is compared** and the
`compared == reachable` guard becomes `compared == len(recorded)`. GX-04's
`gate_trace_full` runs to `t = 23` on a 23-bar series and GX-07's runs the full
length; these become asserted for the first time.

### 7.6 `active_line_before_event_bars` — the governing line

Two changes in `engine/trace.py`:

- `active_line_at` must return the **governing** line, selected by the
  state at the start of the bar: `Λ^F` when that state is `BROKEN_OUT`,
  `RETESTED` or `FAILED_BREAKOUT`; `Λ_bar` when it is `ACTIVE`; `None` when it is
  `NONE`. Verified against GX-04 (bars 8/16 → `Λ_t`; 20 → `Λ^F` labelled
  `"frozen event line Λ^F (§21.5)"`; 22 → `Λ^F` while `RETESTED`), GX-17 (bar 23
  → `Λ^F` while `FAILED_BREAKOUT`) and GX-07 (bar 110 → `Λ^F`).
  Today the function returns `sealed.line` for any bar it considers "evaluated";
  once Phase 3 evaluates post-breakout bars, that would silently return the
  rolled hull and every one of those four records would fail. **This is the
  subtlest single edit in the harness and it must not be missed.**
- `state_at_start` must come from `CausalResult.state_at_start`, not from
  `sealed.state`, and the harness's
  `if confirmed_bar is None or bar <= confirmed_bar` guard around the
  `state_at_start` comparison is **removed** so it is compared at every recorded
  bar.

### 7.7 New: `causal_record.non_retroactive_challengers`

Compared for the first time (`EV-P3-5`): for each fixture, the engine's
challenger list — every bar `u` with `breakout_bar ≤ u ≤ n−1` and
`slope(A^F, (u, H[u])) > m^F`, carrying `bar`, `H` (exact price) and
`slope_if_selected` (6 s.f.) — compared element by element against the recorded
`bars` array, including the empty-list case on the fixtures with no breakout.
This is the direct, positive, mechanical proof that re-selection was suspended:
the engine both *knows* which highs would have re-bound `B*` and *did not use
them*.

---

## 8. RM-01 must not regress — the subtlest interaction

### 8.1 What breaks, stated exactly

`engine/tests/test_rm01.py::RM01HalfB::test_not_asserted_fields_are_genuinely_absent`
asserts four things that become **false** the moment Phase 3 exists, because
RM-01's engine-derived stop is bar 10 and the series has 29 bars:

```python
self.assertIsNone(self.result.final_state, "Phase 2 claims no final state at a stop")
self.assertNotIn(ReasonCode.BREAKOUT_CONFIRMED, self.result.reason_codes)
for record in self.result.transitions:
    self.assertNotIn(record.to, (LineState.BROKEN_OUT, LineState.RETESTED))
    self.assertNotIn(record.frm, (LineState.BROKEN_OUT, LineState.RETESTED))
for record in self.result.transitions:
    self.assertLessEqual(record.bar, self.result.stop_bar)
```

Also `RM01HalfA::test_half_a_is_not_reachable_through_the_pipeline` asserts
`result.reported_line.t_b != 25`, which stays true (`reported_line` becomes `Λ^F`
with `B* = (9, 158.40)`), and `test_robustness_sweeps` compares
`result.stop_bar` at every sweep point, which stays true only if `stop_bar`
survives as a name.

### 8.2 Why the fix is a re-scoping, not a weakening

SPR-D-01 limit 1 says the B-clause is asserted "**within Phase-2-owned behaviour
only**", that it "therefore asserts **`line_at_stop`, not `Λ^F`**", and that "no
`BROKEN_OUT` state and no `BREAKOUT_CONFIRMED` reason code" are "Phase 3's to
gate and are **not** claimed here". That is a statement about **the scope of the
claim**, not a prediction that the engine cannot produce those things. RM-01's
record names those fields in a `not_asserted` list — *not asserted*, not
*forbidden*.

Phase 2 implemented "not asserted" as "must not occur". That was a legitimate
strengthening while the engine was incapable of it, and it is an **over-reading**
now. The re-scoping restores the ruled meaning and, done as below, is **stronger
than the current test in the one respect that matters**: it pins the *first*
Phase-3 emission to the engine-derived stop, rather than merely asserting that no
Phase-3 emission exists anywhere.

### 8.3 The five concrete measures

**M1 — `line_at_stop` keeps asserting the identical numbers, and identity makes
that structural.** `StopRecord` is not modified: same fields, same values,
computed at the same bar by the same code. `test_line_at_stop` is **unchanged**,
including the margin-identity check (raw clearance minus net clearance equals
`eps_break`). `Λ^F` is built by *wrapping* `stop.line`, and the fold asserts
`frozen.line is stop.line`. A **new** RM-01 test asserts the bridge explicitly:

```
frozen_line.line == line_at_stop        (field for field)
frozen_line.breakout_bar == stop_bar == 10   (engine-derived)
frozen_line.tolerance_version == params.tolerance_version
```

This converts the Phase-2/Phase-3 boundary from a risk into an assertion: the
line Phase 3 freezes *is* the line Phase 2 named, and the two records can never
disagree.

**M2 — the negative assertions are re-scoped to the Phase-2-owned window, not
deleted.** Replace the four assertions above with:

```
# no Phase-3 state or code anywhere STRICTLY BEFORE the engine-derived stop
for record in transitions:
    if record.bar < stop_bar:
        assert record.to not in PHASE3_STATES and record.frm not in PHASE3_STATES
        assert record.reason not in PHASE3_REASON_CODES
# and the FIRST Phase-3 emission is at exactly the engine-derived stop
first_phase3_bar = min(r.bar for r in transitions if r.reason in PHASE3_REASON_CODES)
assert first_phase3_bar == stop_bar
```

The second clause is new and is the stronger form: the engine must not merely
avoid Phase-3 behaviour early, it must place the boundary at precisely the bar it
derived for itself. `PHASE3_REASON_CODES` in `state.py` — already committed —
is the vocabulary this uses, which is why that set is retained rather than
deleted (its docstring changes from "this engine must never emit one of these" to
"the codes the frozen-line layer owns; nothing before `confirmed_bar` may emit
one").

**M3 — RM-01's post-stop behaviour is deliberately not asserted, and the test
asserts *that it is not asserted*.** RM-01's record carries no post-stop
expectation (its `not_asserted` list names `frozen_line` and
`BREAKOUT_CONFIRMED`). Under HD-22 no expectation may be added to it to
accommodate the engine, and under SPR-D-01 limit 3 the Half-B artifact is
model-derived and earns no independence credit anyway. So Phase 3 asserts nothing
about RM-01's final state, its retest, its failure or its expiry. The
`test_not_asserted_fields_are_genuinely_absent` method is renamed
`test_the_not_asserted_scope_is_honoured` and asserts the *scope*: every key the
RM-01 test module reads from the record is disjoint from
`not_asserted["fields"]`, computed from the record itself rather than
hand-listed. That makes limit 1 a checkable property of the test suite instead of
a comment.

**M4 — `stop_bar` and `line_at_stop` survive as names.** `DetectionResult` gains
`confirmed_bar` and `frozen_line`; `stop_bar` becomes a property returning
`confirmed_bar`, and `line_at_stop` is unchanged. Rationale: `test_robustness_sweeps`
compares `stop_bar` across three sweeps (`eps_break`, `eps`,
`min_formation_bars`), `serialize()` in `test_determinism.py` records it, the
golden harness compares it against `confirmed_bar`, and `HD13EpsBreakSweep`
uses it in four places. Renaming buys nothing and risks a silent behaviour change
inside a test whose whole purpose is to be a regression guard. Keeping the alias
means **RM-01's sweep assertions are literally unchanged**.

**M5 — the A-clause is untouched.** `prefix_of`, `second_anchor_over`,
`anchor_of` and `envelope_violations` are not modified. The A-clause is a unit
assertion on the pure §8 selector over the full 29-bar prefix and does not go
through the fold at all, so Phase 3 cannot reach it.
`test_half_a_is_not_reachable_through_the_pipeline` keeps passing and gets one
added line — `assertEqual(result.frozen_line.line.t_b, 9)` — which makes the
"§21 freezes the line long before bar 25" claim positive rather than merely
negative.

### 8.4 What the reviewer should check in one place

Four properties, all mechanical:

1. `RM01HalfB::test_line_at_stop` diff is **empty**.
2. `frozen_line.line == line_at_stop` for RM-01 and for all seven breakout
   fixtures.
3. The first bar at which any `PHASE3_REASON_CODES` member is emitted equals
   `confirmed_bar`, on RM-01 and on every golden fixture.
4. No test in `engine/tests/` compares an RM-01 quantity named in that record's
   `not_asserted.fields`.

---

## 9. Task breakdown

Ordered so each task leaves the suite green. `T-1`…`T-4` are pure additions that
cannot change Phase-2 output; the behaviour change lands in `T-5`.

| # | Task | Files | Done when |
|---|---|---|---|
| **T-1** | Add the six §15/§16/§17 parameters with D-TL-08/09/10 defaults; thread them through `replace`, `with_eps_break`, `from_fixture_params`; validate ranges | `engine/params.py` | all 24 fixtures still pass unchanged; new unit test asserts `replace()`/`with_eps_break()` round-trip all six; new test asserts every fixture-carried value equals the module default |
| **T-2** | Add `falls_below`, `at_or_below`, `at_or_above` and the four pinned margin forms | `engine/logspace.py` | boundary unit tests at exact equality for each; `C-4` audit extended |
| **T-3** | `engine/frozen.py`: `FrozenLine`, `Challenger`, and the three pure predicates `failed_breakout_at`, `retest_at`, `expired_at`, each taking `(FrozenLine, bar_data, t, params)` and returning an optional detail dict | `engine/frozen.py` (new) | unit-tested in isolation against §1's hand arithmetic for GX-04/05/07/17/19 and GX-12@0.5×/GX-15@0.5× |
| **T-4** | Effective-state track and unconditional tail seal, with no behaviour change yet | `engine/causal.py` | `state_at_start` populated; `sealed` includes `t = n` in both branches; all 24 fixtures unchanged |
| **T-5** | The fold: turn the stop into `BREAKOUT_CONFIRMED`, freeze, add the post-breakout branch in the order of §5.1/§5.3, suspend re-selection, grow `_LINE_BEARING`, compute `challengers`, assert `frozen.line is stop.line` | `engine/causal.py`, `engine/detector.py` | the 7 breakout fixtures reach their recorded `expected_final_state`; the 16 others byte-identical |
| **T-6** | `active_line_at` returns the governing line and the real `state_at_start` | `engine/trace.py` | GX-04 @20/@22, GX-17 @23, GX-07 @110 records compare |
| **T-7** | Harness: remove the `phase2_complete` branch; add `frozen_event_line`, the four event types, `non_retroactive_challengers`, full `gate_trace_full`, sweep `final_state`, and the §21.6 rule 3 walk assertion | `engine/tests/conformance.py` | every fixture compared in full, both directions, on every recorded key |
| **T-8** | RM-01 re-scoping, measures M1–M5 | `engine/tests/test_rm01.py` | §8.4's four properties hold; `test_line_at_stop` unchanged |
| **T-9** | Determinism, properties, architecture, coverage; new boundary unit tests for the unexercised windows (§9.3) | `engine/tests/test_determinism.py`, `test_properties.py`, `test_architecture.py`, `test_units.py` | §10's evidence table complete |

### 9.1 Not in scope

Confidence/quality output (`LOW_VOLUME` and the §13.3 persistence feature are
`flags` in the fixtures and belong to the confidence spec — GX-11 records
`flags: ["LOW_VOLUME"]` and GX-17 `["NOT_RETESTED"]`; **the engine does not
produce `flags` today and Phase 3 does not start**); §12 touch counting; anything
outside `engine/`; any new executable tool; any fixture edit.

### 9.2 Architectural tests that must change, and how

`ScopeDiscipline.test_no_phase_3_reason_code_is_ever_emitted` and
`test_no_phase_3_state_is_ever_assigned` currently forbid the four Phase-3 tokens
in every module except `state.py`. They must be **replaced, not deleted**, by a
containment check: those tokens may appear only in `state.py`, `frozen.py` and
`causal.py`. A grep-based scope test that is simply removed leaves nothing behind;
one that is narrowed keeps detecting the real risk — a Phase-3 code emitted from
the guards, the envelope selector or the formation gates, where it would mean the
layering had collapsed.

### 9.3 Coverage gaps the corpus cannot close, and the unit tests that must

Measured from §1: **every `RETEST_HELD` in the entire corpus has its hold leg on
the same bar as its return leg** (GX-04 @20, GX-19 @17, GX-15@0.5× @29). So an
engine that implemented `h_hold = 0` would pass every committed fixture. Likewise
no fixture exercises the right edge of `F_fail` (the largest gap used is 4 bars)
or of `W_retest` (largest 4 bars), and `E_expiry`'s edge is exercised exactly once
(GX-07, bar 110). GX-12 @0.5× is the *only* datum touching the multi-bar hold
window, and it touches it negatively (the hold that would have arrived at +2 is
pre-empted by the failure).

Four constructed engine-local unit tests are therefore **required evidence**, not
optional polish — built from the specification with `make_series`, with **no
fixture added, edited or reinterpreted** (the pattern `test_mutations.py` already
established for the two mutations the 6-s.f. comparison cannot catch):

- `h_hold` boundary: a return at `r` whose hold arrives at `r + h_hold` fires;
  at `r + h_hold + 1` it does not.
- `F_fail` boundary: a qualifying close at `breakout + F_fail` fails; at
  `breakout + F_fail + 1` it does not.
- `W_retest` boundary: a return at `breakout + W_retest` can complete; at
  `breakout + W_retest + 1` it cannot.
- Left edges: the breakout bar itself triggers neither §15 nor §16 (§1.5), on a
  constructed series where both legs would otherwise hold.

---

## 10. Acceptance / evidence plan

Every row names a **mechanically checkable artifact**. "Passes" means the named
test fails if the property is violated.

| ID | Acceptance criterion | Proof artifact |
|---|---|---|
| **EV-P3-1** | The 7 `confirmed_bar != null` fixtures are reproduced **in full**: complete `expected_state_transitions`, complete `expected_reason_codes` (set **and** first-emission order), and `expected_final_state` | `test_conformance_golden` via `compare_golden` with the `phase2_complete` branch removed; the A-5 derived-gate test proves no directory is skipped |
| **EV-P3-2** | No regression of the 16 `confirmed_bar == null` fixtures | same suite, same comparisons; plus a git-diff-level check that no comparison in the Phase-2-owned list of §7.1 was weakened. Additionally: for every fixture carrying `eps_fail`/`F_fail`/`eps_retest`/`W_retest`/`h_hold`/`E_expiry`, the carried value equals `DetectorParams`' default — a disagreement is a **failure and an escalation**, never a default override |
| **EV-P3-3** | `Λ^F` is captured per §21.5's table, including `tolerance_version` | `causal_record.frozen_event_line` compared on all 24 fixtures (7 present, 17 `null`), both directions; `causal_record.events[].line.m`/`.b` compared at **exact double precision** |
| **EV-P3-4** | Re-selection is suspended while `BROKEN_OUT`/`RETESTED` | (a) zero `LINE_ESTABLISHED` records and zero `reselections` at bars in `(confirmed_bar, exit_bar]` — asserted directly against `causal_record.reselections` and `expected_state_transitions`; (b) the post-breakout predicates accept only `FrozenLine`, so passing `Λ_t` is a type error |
| **EV-P3-5** | Suspension is proven *positively*, not only by absence | `causal_record.non_retroactive_challengers.bars` compared element by element: 7 bars on GX-04, 3 on GX-11/GX-16, 5 on GX-19, 101 on GX-07, `[]` on GX-12/GX-15 — the engine names the highs that would have re-bound `B*` and demonstrably did not use them |
| **EV-P3-6** | `RESET_NEW_ATH` still overrides a frozen line (§21.7) | `_LINE_BEARING == (ACTIVE, BROKEN_OUT, RETESTED)` asserted directly; a constructed unit series with a new ATH while `BROKEN_OUT` emits `BROKEN_OUT → NONE / RESET_NEW_ATH` and **no** `BREAKOUT_CONFIRMED` on that bar (§21.7's "a close above a line whose high made a new ATH is a reset, not a breakout"). Unexercised by the corpus, so the unit test is the evidence |
| **EV-P3-7** | Within-bar order and §21.6 rules 1–4 | GX-19 bar 16 (`LINE_ESTABLISHED` then `BREAKOUT_CONFIRMED`, in order) compared as an ordered list; a new engine-wide assertion that the emitted transition sequence is a valid walk (each `from` == previous `to`, last `to` == reported final state) on all 24 fixtures; GX-12 @0.5× fixes failure-before-retest; the existing `EngineDefect` for an unrecorded state change is retained |
| **EV-P3-8** | **Reason-code coverage:** every accept/reject emits a code from the schema's closed set, and the closed set is exercised | A-4 (engine sets **equal** the schema's, both directions) unchanged. `ReasonCodeCoverage` extended: emission over the whole corpus yields **14 of the 15** codes — the four Phase-3 codes now among them — with `INSUFFICIENT_BARS` reachable in the gate trace and deliberately unrecorded at the head of a series (§21.3), asserted by its own existing test. `LineState.EXPIRED` is asserted **unreachable** (see ESC-1). No code is counted by grepping source; only by emission |
| **EV-P3-9** | Determinism guard | `D-6` byte-identical over 24 fixtures with `frozen_line` and `state_at_start` in the digest; `D-3` identical under two `PYTHONHASHSEED` values in a child process; `C-4` tie-proximity audit extended to the four new margin quantities; `C-2` sweep equality with `final_state` compared at **every** scale (which is what brings GX-12@0.5× and GX-15@0.5×/0.8× into the gate); `C-5` anti-vacuity retained |
| **EV-P3-10** | No look-ahead (§21.8 rules 1–2) | `P1NoLookAhead` extended: a mutation at any bar `> confirmed_bar` leaves `confirmed_bar` and `frozen_line` identical; `P2PrefixTruncationInvariance` extended: for every `k ≥ confirmed_bar`, `frozen_line` is field-identical to the full run's; `P3StopStability` rewritten from "near-vacuous" to the live post-breakout property; generator-quality assertions extended so the random corpus contains post-breakout bars inside the failure and retest windows |
| **EV-P3-11** | Streaming ≡ batch (§21.8 rule 3, §20.5) | Discharged structurally: `run` is a single fold, so the two cannot differ. **Stated as vacuous, not as passing evidence** — the docstring says so — with `EV-P3-10`'s prefix-truncation invariance as the falsifiable substitute. No second incremental code path is introduced |
| **EV-P3-12** | Window boundaries the corpus cannot reach | The four constructed unit tests of §9.3, plus the `h_hold`/`F_fail`/`W_retest`/left-edge cases. Recorded in the plan as a **coverage gap closed by unit test**, so the gap is disclosed rather than hidden by a green suite |
| **EV-P3-13** | RM-01 non-regression | §8.4's four properties: `test_line_at_stop` diff empty; `frozen_line.line == line_at_stop` on RM-01 and all 7 breakout fixtures; first Phase-3 emission bar == `confirmed_bar` on RM-01 and every fixture; no test reads an RM-01 key named in `not_asserted.fields`. A-clause untouched |
| **EV-P3-14** | Scope | `ScopeDiscipline.test_engine_is_the_only_product_directory` unchanged; A-3 (no engine source references any sibling top-level directory, derived not enumerated) unchanged — which is also the E2-AUTHOR-A executable check, and it covers `engine/frozen.py` automatically because A-3 enumerates `engine/*.py` from the directory; `git status` shows changes confined to `engine/` and this plan |

**Anti-vacuity, stated once.** Four of the properties above are capable of
passing while asserting nothing, and each carries its own control:
`EV-P3-4`(a) is an absence claim, so `EV-P3-5` supplies the positive form;
`EV-P3-9`'s sweep would pass on an engine ignoring `eps_break`, so `C-5` shows
it can fail; `EV-P3-10` would hold vacuously on a corpus with no post-breakout
events, so the generator-quality assertion requires them; `EV-P3-11` cannot
fail at all, and says so on its face rather than being counted.

---

## 11. Open questions and escalations

Escalations are disagreements or gaps a **decision-maker** must close. Open
questions are under-determinations the plan resolves provisionally and flags.
Neither is closed by the Architect.

> **STATUS, 2026-07-28 — ALL FIVE ESCALATIONS AND THE SIX STEWARD-OWNED OPEN QUESTIONS
> ARE NOW CLOSED BY A DECISION-MAKER.** The text below is retained **as raised**,
> because the record of what was escalated is evidence (GOV-006); it is **no longer
> the current disposition**. The rulings are at
> [`../../product/trendline-specification.md`](../../product/trendline-specification.md)
> **§22** (the amendment record, with the section each ruling amended):
> **ESC-1**, **ESC-3**, **ESC-5(a)** and **OQ-P3-1 … OQ-P3-6** ruled by the **Product
> Steward**; **ESC-4** ruled by the **Product Owner** as
> **[HD-25](../../product/human-decisions.md)** — option **C**, `FAILED_BREAKOUT`
> retains **both** exits, which resolves this plan's own §7.6-vs-§11 contradiction in
> favour of **§7.6**. **ESC-2** was discharged as a record-only correction.
> **ESC-5(b)** — whether §18 gains a fourth guard row — is **deferred** and explicitly
> non-blocking. **OQ-P3-7**'s remedy is an acceptance criterion of ticket (g).
> **OQ-P3-8** is consolidated into **OQ-J** and is not blocking.
> **Where a ruling differs from the provisional resolution below, the ruling
> governs** — that is the case for **OQ-P3-5** (**latest**, not first), and the two
> clauses it invalidates are named in the dated correction block at the head of this
> file.

### Escalations

**ESC-1 — §11 and GX-07 describe expiry with a different number of records.
Decider: Product Steward (spec clarification); Product Owner if it is a
behaviour change.**
§11 draws `BROKEN_OUT / RETESTED ──▶ EXPIRED ──▶ NONE` — two edges through a
state named `EXPIRED`. GX-07 records **one** transition,
`bar 110: BROKEN_OUT → NONE / EXPIRED_POST_BREAKOUT`, with a three-entry
`expected_reason_codes`. The schema's closed `from`/`to` enum contains `EXPIRED`,
and architectural test A-4 requires `LineState` to **equal** that set, so the
member must exist. Under HD-22 the fixture is not edited, so the plan implements
the fixture's single-record reading and leaves `LineState.EXPIRED` **unreachable**.
Requested: either amend §11 to draw one edge labelled `EXPIRED_POST_BREAKOUT`, or
rule that `EXPIRED` is a transient state a conforming detector must record — in
which case GX-07 disagrees with the specification and that disagreement is the
escalation, not something the engine may resolve.

**ESC-2 — the brief's parameter premise is wrong, and the correction should be
recorded. Decider: Orchestrator / Product Steward (record only).**
The ticket states the six Phase-3 parameters are "not carried in any fixture's
`params` block". They are: GX-04 and GX-17 carry all five §15/§16 parameters,
GX-05 carries `eps_fail` and `F_fail`, GX-07 carries `E_expiry`. Every carried
value equals the D-TL-08/09/10 default. Consequently **no parameter escalation on
values is required** and no fixture needs a non-default value — but the ticket's
risk framing should be corrected so a later reader does not conclude the
parameters were chosen by the engine rather than read from the specification and
corroborated by the fixtures.

**ESC-3 — the left edge of the §15/§16 windows is fixture-forced; the right edges
are not evidenced at all. Decider: Product Steward.**
§15/§16 say "within `F_fail` / `W_retest` bars of the breakout bar" without
bounding the interval. The fixtures force the **left** edge open
(`breakout_bar < t`): on GX-04 both retest legs hold at the breakout bar itself,
and the fixture puts `RETEST_HELD` at bar 20. The **right** edges (`≤ breakout +
F_fail`, `≤ breakout + W_retest`, `≤ r + h_hold`) are unexercised by any fixture
— the largest gap the corpus uses is 4 bars against windows of 10 and 20, and
every corpus hold leg is on the return bar itself. The plan adopts the inclusive
reading `breakout_bar < t ≤ breakout_bar + F_fail` (and likewise for the others)
and covers it by unit test (§9.3), but a ruling would make the reading normative
rather than the Architect's.

**ESC-4 — is `FAILED_BREAKOUT` terminal even against a new ATH?
Decider: Product Steward.**
§11 gives `FAILED_BREAKOUT` no outgoing edge and §21.7 enumerates exactly
`ACTIVE`, `BROKEN_OUT` and `RETESTED` as the states a new ATH invalidates. The
plan takes that literal reading, so a new all-time high while `FAILED_BREAKOUT`
records nothing and the state stays terminal. That is behaviourally surprising —
a new ATH plausibly ought to reset everything — and it is **unexercised**: no
committed expectation changes under either reading. Flagged rather than silently
taken, because the terminality of `FAILED_BREAKOUT` *is* fixture-forced (GX-05,
GX-17, GX-12@0.5×) while its immunity to a new ATH is not.

**ESC-5 — §16's `low` is required data but §18 does not guard it.
Decider: Product Steward.**
§1 lists `low` among the required fields, but §18's table names only a missing
`high` or `close` as `INVALID_INPUT`, and `engine/guards.py` implements exactly
those three rows with the standing note that adding a fourth is a
product-definition change. §16's return leg reads `ln(L[t])`. A bar with
`low: None` therefore reaches a Phase-3 predicate with nothing to test. The plan
raises `PreconditionError` (a caller defect, consistent with the existing
non-positive-basis and ordering handling) rather than minting a reason code,
because the code set is closed by schema. A ruling is needed on whether §18 gains
a fourth row for a missing `low` when the state is post-breakout — which would be
a guard change and therefore a product-definition change, not an engine one.

### Open questions (resolved provisionally; each unexercised by the corpus)

| ID | Question | Provisional resolution | Owner |
|---|---|---|---|
| **OQ-P3-1** | In §16's hold leg, is `ŷ` evaluated at the **return** bar or at the **hold** bar? §16 writes `ln(C) ≥ ŷ(t) − ε_retest` with `t` ambiguous | At the **hold** bar's own index, because §21.2 step 2 evaluates each bar against the line *at that bar*. The two readings differ on GX-12 @0.5× (`ŷ_F(18)` gives a hold, `ŷ_F(16)` does not) but the failure pre-empts both, so no fixture distinguishes them | Product Steward |
| **OQ-P3-2** | Is `RETEST_HELD` recorded at the return bar or the hold bar when they differ? | At the **hold** bar — that is where the state changes, and §21.6 rule 1 attributes a record to where its effect lands. Every corpus retest has them on one bar | Product Steward |
| **OQ-P3-3** | May a second `RETEST_HELD` fire while `RETESTED`? May a new return leg open after a failed hold, within `W_retest`? | No second `RETEST_HELD` (§11 has no `RETESTED → RETESTED` edge). Yes to a new return leg: any bar in the return window may open a fresh hold window. GX-17 exercises the negative (return at 20, no hold through 23) but its state is decided by the failure | Product Steward |
| **OQ-P3-4** | Does `reported_line` stay `Λ^F` after `RESET_NEW_ATH` retires a frozen line? | Yes — §21.4's rule is "if a confirmed breakout occurred **anywhere** in the series", and it explicitly survives `EXPIRED_POST_BREAKOUT`. Unexercised | Product Steward |
| **OQ-P3-5** | Which `Λ^F` and which `confirmed_bar` are reported when a series contains two breakouts in two episodes? | The **first**, preserving the schema's single-valued `confirmed_bar` and RM-01's engine-derived-stop semantics; each later episode still emits its own `BREAKOUT_CONFIRMED` record and event. Unexercised | Product Steward |
| **OQ-P3-6** | After `EXPIRED_POST_BREAKOUT` returns to `NONE`, does the new formation re-derive `B*` over the whole grown prefix — including the post-breakout highs that suspension refused to roll? | Yes: §21.1 makes `B*_t` a pure function of `S_t`, and §17 says the detector "recomputes from scratch over the full **available** history". On GX-07 this would bind `B*_{111} = (110, 95)` — but the series ends at 110, so it is unexercised | Product Steward |
| **OQ-P3-7** | `flags` (`LOW_VOLUME`, `NOT_RETESTED`) are recorded by GX-11 and GX-17 and produced by no engine layer | Out of Phase-3 scope: §13.4 and §13.3 place volume and persistence in the confidence layer, and the roadmap's Phase-3 exit criteria name transitions, reason codes and final state — not `flags`. The harness must therefore **not** silently ignore the key; it should record it as an explicitly unasserted fixture field, so the omission is visible | Orchestrator (scope) |
| **OQ-P3-8** | `SPEC_VERSION` is still the placeholder `"UNVERSIONED-PENDING-OQ-J"` | Unchanged by Phase 3; carried forward as Phase 2 left it. §20.4 requires a real `spec_version`; the value is the Product Steward's | Product Steward (OQ-J, pre-existing) |
