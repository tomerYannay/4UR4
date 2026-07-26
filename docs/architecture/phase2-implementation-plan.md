# 4UR4 — Phase 2 Implementation & Test Plan (deterministic trendline detection engine)

> **Status: DESIGN / SPECIFICATION ONLY under [GOV-015](../../governance/build-freeze.md).**
> The build-freeze is **ON**. This document writes no product code, no scaffolding
> and no configuration, and it does not begin implementation. It is the Architect's
> planning deliverable for [Issue #7](https://github.com/tomerYannay/4UR4/issues/7)
> (Phase 2, ticket (f)), produced as work the Product Owner named permitted in the
> 2026-07-26 batch ruling ([#23](https://github.com/tomerYannay/4UR4/issues/23),
> [#24](https://github.com/tomerYannay/4UR4/issues/24)) while separately forbidding
> the implementation itself. Nothing here is an authorization to build, and nothing
> here marks any ticket Done.

> **Author restriction observed — and this document inherits the quarantine.**
> **Scope of this attestation: the drafting of this document.** While it was written,
> `tools/fixture-replay.mjs` was **not opened at all** — not its body, not its header —
> and `product/fixtures/VERIFICATION.md` was likewise not opened.
>
> **Disclosure — later editing sessions did not inherit that quarantine.** This file has
> since been edited by commits that edited `product/fixtures/VERIFICATION.md` in the same
> atomic commit (`6af5261`, `9ef30b7`), and editing a file entails reading it. The
> attestation above is therefore **true of the drafting session and false as an
> open-ended claim about every session that has touched this file**; it is scoped rather
> than withdrawn. This matters because
> [#20](https://github.com/tomerYannay/4UR4/issues/20) is open precisely for the reason
> that HD-15 condition 2 has **no mechanical enforcement** — this attestation is
> currently the entire control, and a control that overstates itself is worse than one
> that states its limits. `tools/fixture-replay.mjs` remains unopened by every session
> that has edited this file; **that** is the claim that carries the quarantine, and it is
> the one E2-AUTHOR must eventually enforce mechanically rather than accept on trust.
>
> Every rule below is derived from
> [`trendline-specification.md`](../../product/trendline-specification.md),
> [`human-decisions.md`](../../product/human-decisions.md),
> [`roadmap.md`](../../product/roadmap.md) and the committed fixture **data**
> (`input.csv`, `expected.json`, `annotation.json`, `fixture.schema.json`,
> `fixtures/README.md`). That is the whole of it.
>
> **Why the restriction binds a *plan*.** HD-15 condition 2, as sharpened on
> 2026-07-26, requires the Phase-2 implementation to be independently authored and
> to *"not import, copy, execute or mechanically translate the reference model."* A
> plan detailed enough to implement from is close enough to authorship that it must
> be produced under the same discipline; otherwise it becomes a laundering channel —
> a clean-room implementer reading a model-contaminated plan is contaminated.
> This document is therefore written to be **safe to hand to a clean-room author**,
> and it is the only design artifact that is. Per
> [`phase2-independence-mechanism.md`](phase2-independence-mechanism.md) §3 Q4, that
> file itself is quarantined from the author; this one is not.
>
> **Independence is independence from the model's *source*, never from its outputs.**
> The fixtures' `causal_record` blocks publish the model's outputs and much of its
> intermediate state, and the Phase-2 exit criteria name those fields by name. The
> author **must** read them. §2–§6 below are written against that contract.

---

## 0. Precedence, and what this plan is bound by

| Rank | Source | Governs |
|------|--------|---------|
| 1 | [`trendline-specification.md`](../../product/trendline-specification.md) §4–§9, §11, §13–§18, **§21** | every rule, and (via §21) *when* each rule is evaluated |
| 2 | [`human-decisions.md`](../../product/human-decisions.md) HD-01/02/03/11/12/13/14/15 | ratified product decisions; not re-openable here |
| 3 | [`roadmap.md`](../../product/roadmap.md) Phase 2 | the exit gate, the E2-AUTHOR entry criterion, the Phase 2/3 boundary rule |
| 4 | [`fixtures/README.md`](../../product/fixtures/README.md), the 23 golden fixtures, RM-01 | the correctness contract in machine-checkable form |

Where this plan and any of the above disagree, **they govern and this plan is
defective**. Where the *specification* and a fixture disagree, the specification
governs and the disagreement is a defect report — never resolved by fitting the
engine to the fixture (HD-15 condition 1 posture, applied to fixtures as well as to
the model).

**Two prerequisites this plan cannot satisfy and does not pretend to.** Phase 2
implementation may not begin until (a) the per-scope freeze is lifted by a human,
and (b) E2-AUTHOR's five conditions hold — which requires
[#20](https://github.com/tomerYannay/4UR4/issues/20) closed and
[#21](https://github.com/tomerYannay/4UR4/issues/21) resolved or a recorded Product
Owner ruling on the §9 stopgap. This plan is written so that it is ready on the day
those clear, and so that it is useful evidence for closing #20 (it is the artifact
the author-facing brief points at).

---

## 1. Scope — the Phase 2 / Phase 3 boundary, and the one place the code straddles it

The boundary is a **behavioural rule**, ruled 2026-07-26, not a data partition:

- **Phase 2 owns** behaviour evaluated **while the structure remains `ACTIVE`** that
  performs **no `ACTIVE → BROKEN_OUT` transition**: the §18 input guards, ATH
  anchoring (§4), all-highs candidacy (§6), upper-log-hull selection (§8), log-space
  geometry (§3, §7), formation eligibility (§21.3), rolling as-of-time re-selection
  (§21.6), the structural-pierce edge (§10.1), and **wick-break** (§14).
- **Phase 3 owns** the `ACTIVE → BROKEN_OUT` transition itself and everything
  downstream on the frozen line `Λ^F`: `BREAKOUT_CONFIRMED`, retest (§16), failure
  (§15), expiry (§17), and the suspension of re-selection while frozen (§21.5).

### 1.1 The straddle, stated exactly

**A breakout *test* must exist inside Phase 2, or wick-break is not definable.**
§14 is `ln(H[t]) > ŷ_t(t) + ε` **and** `ln(C[t]) ≤ ŷ_t(t) + ε_break` — the second
conjunct *is* the negated §13.1 breakout predicate. Equally, §21.2 step 4 rolls the
anchor forward only "if bar `t` does **not** produce a confirmed breakout", so the
roll cannot be implemented without the predicate either.

The resolution that keeps Phase 3 from having to tear anything up:

| Phase 2 implements | Phase 2 does **not** implement |
|---|---|
| the pure predicate `breakout_signalled(bar, line, params) -> bool` — the §13.1 inequality and nothing else | the `BREAKOUT_CONFIRMED` reason code, the `ACTIVE → BROKEN_OUT` transition record, the `BROKEN_OUT` state |
| **halting** the episode at the first bar where the predicate is true, and returning the line that was active at the start of that bar as `line_at_stop` | labelling `line_at_stop` as `Λ^F`, freezing semantics, suspension of re-selection, `ŷ_F`-based tests |
| pure evaluation of a line at an arbitrary index (`ŷ(u) = m·u + b`), including indices after the stop bar | §15 failure, §16 retest, §17 expiry, `EXPIRED_POST_BREAKOUT`, `RESET_NEW_ATH` **from** a frozen state |

`line_at_stop` is not a Phase-3 object smuggled early: it is `Λ_t`, the line active
while the structure was still `ACTIVE`, which Phase 2 computes anyway. §21.5's
freeze is the *act of retaining it and suspending re-selection* — that act is
Phase 3's, and Phase 3 adds it as a new branch of one named function (§3.4), not as
a rewrite.

**Consequence for the gate, and it is a favourable one.** Because the reported line
for a series with a breakout is `Λ^F` (§21.4, "the line a detector REPORTS"), and
`Λ^F` *is* `line_at_stop`, Phase 2 can reproduce `expected_second_anchor`,
`expected_log_slope`, `expected_intercept` and every `expected_line_values` entry for
the breakout fixtures (GX-04, GX-05, GX-07, GX-11, GX-16, GX-17, GX-19) **without
performing the transition**. It reproduces `expected_state_transitions` only at bars
strictly before `confirmed_bar`, exactly as the roadmap's gate states, and it must
identify `confirmed_bar` itself correctly in order to know where "strictly before"
ends.

**Out of scope, explicitly:** touch counting and `ε_touch` (§12 — a confidence input,
asserted by no fixture); volume and the `LOW_VOLUME` flag (§13.4 — confidence, and
Phase 3 at the earliest); anything in `confidence-specification.md`; any I/O; any
provider adapter.

---

## 2. Module decomposition, interfaces, and the `data/` boundary

Language: **Python** (architecture §3.1; also
[`phase2-independence-mechanism.md`](phase2-independence-mechanism.md) §5 P6, which
makes language separation a stated requirement of the ticket rather than an
accident). Pure core: no network, no DB, no clock, no randomness, no credentials.

### 2.1 Modules

| Module | Responsibility | Depends on | Deliberately does **not** |
|---|---|---|---|
| `engine/params.py` | frozen `DetectorParams` carrying the whole §20 named set, `tolerance_version`, `spec_version`; construction from a fixture `params` block | — | apply defaults silently for a parameter a caller omitted that affects an outcome |
| `engine/bars.py` | immutable `Bar` and `BarSeries`; ordinal index `t` = position (§1); construction-time precondition checks | — | mutate, reorder, gap-fill, or interpolate |
| `engine/guards.py` | §1/§18 input guards as a **whole-bar-set pre-pass**: `INVALID_INPUT`, `INVALID_PRICE`, `SUSPECTED_UNADJUSTED_SPLIT` | `bars`, `logspace` | run inside the causal loop; invent new rejection classes (§9 OQ-F) |
| `engine/logspace.py` | the **only** site of `ln`, slope, intercept, line evaluation and 6-significant-figure rounding | — | expose any alternative algebraic form of the same quantity (§4.3) |
| `engine/anchor.py` | `anchor_of(prefix) -> (tA, HA)`: max high, earliest on ties (§4, D-TL-02) | `logspace` | consider any bar outside the prefix it was handed |
| `engine/envelope.py` | `select_second_anchor(prefix, tA, eps) -> Selection`: §8 brute force over all later bar highs, with per-candidate `slope`, `worst_gap`, `envelope_valid`, and the `ENVELOPE_TIE_LATER` outcome | `logspace` | import `engine/pivots.py` (enforced by a static test, §6.6) |
| `engine/formation.py` | F1, F2, F3 evaluated **independently** (§21.3); per-bar `GateTrace` entry with the first unmet gate | `anchor`, `envelope` | read `k`, or mention it (enforced statically) |
| `engine/state.py` | the closed `LineState` and `ReasonCode` sets (mirroring `fixture.schema.json`), transition records, and the "one record per contiguous `NONE` run" encoding (§21.3) | — | admit a code outside the schema's closed set |
| `engine/causal.py` | the fold: `seal(state, bar) -> state'` and `step(state, bar) -> (state', records)`; §21.2's processing order | all of the above | ever receive the full series (§3.2) |
| `engine/trace.py` | the structured evidence record: gate trace, as-of-time candidate set, active line before each event bar, event margins, re-selections, `line_at_stop` | — | emit prose formatted to match any other implementation's strings (§6.2) |
| `engine/detector.py` | the public API `detect(series, params, provenance) -> DetectionResult`; `reported_line(result)` per §21.4 | `causal`, `trace` | accept a series it has not run the guards over |
| `engine/pivots.py` | `isPivotHigh(p, k)` (§5) for **descriptive output only** | `bars` | be imported by `envelope`, `formation`, `causal` or `detector` |

### 2.2 The public interface (shape, not code)

```
detect(series: BarSeries, params: DetectorParams, provenance: Provenance)
    -> DetectionResult
```

`DetectionResult` carries: `spec_version`, `params`, `guard_verdict`,
`ath_anchor`, `reported_line` (`second_anchor`, `log_slope`, `intercept`),
`line_values` (a pure function of `reported_line`, evaluable at any index),
`state_transitions` (ordered), `reason_codes` (first-emission order),
`final_state`, `breakout_signalled_bar` (Phase 2's `confirmed_bar` equivalent),
`line_at_stop`, `evidence` (the `trace.py` record), and `provenance` passed through
untouched.

### 2.3 The `data/` boundary — what the engine assumes, and what it rejects

The engine receives plain bars and returns plain results; **every provider concern is
absorbed at the `data/` seam** ([`data-provider-findings.md`](../../product/data-provider-findings.md)
DI-01…DI-12 and its own §11 statement that none of DI-01…DI-12 changes `engine/`).
The engine's obligations at that seam:

| Assumption | Source | How the engine treats a violation |
|---|---|---|
| bars are **split-adjusted, dividend-unadjusted** and the basis is declared | HD-01, DI-01 | **precondition check** at `detect()` entry: a basis other than `SPLIT_ADJUSTED` raises, loudly. Not a reason code — the reason-code set is closed, and this is a caller defect |
| every read carried a mandatory **`as_of`**, already resolved by `data/` | DI-04, §21.8 | the engine **records** `as_of` in provenance and **never queries it in logic**. There is no clock in `engine/` (§5) |
| **wick semantics** are declared (`CONSOLIDATED_SIP` / `PRIMARY_LISTING` / `PARTIAL_VENUE` / `UNKNOWN`) plus `upstream_source` | DI-06 | recorded in provenance; `UNKNOWN` is admissible for research and must be surfaced as a non-gating diagnostic on the result. Geometry is anchored on **highs**, so this is the input attribute that can silently break the product |
| dividend-adjusted fields are **banned** at load time, not filtered here | DI-06b | the engine sees only what `data/` emitted; the ban is `data/`'s test |
| requested history was **not silently truncated** | DI-07 | the engine cannot verify this and must not pretend to. It surfaces `anchor_at_first_bar` as a **non-gating diagnostic** (an ATH at `t=0` is legitimate — GX-09 — but is also the signature of a truncated history) |
| provenance per bar: provider, adapter version, retrieval timestamp, snapshot id | DI-05 | passed through into `DetectionResult` so a signal is replayable against the series that produced it |
| bars are strictly ascending, de-duplicated, no synthetic gap-filling; `t` is ordinal position | §1 | **precondition violation → raise**, see §9 OQ-E |

**What the engine itself must reject, and with which code** (§18, and only these —
adding a rejection class is a product-definition change, §9 OQ-F):

| Condition | Code | Fixture |
|---|---|---|
| a bar missing `high` or `close` | `INVALID_INPUT` | GX-18 |
| any non-positive price | `INVALID_PRICE` | GX-18 |
| a single-bar log jump `\|y[t] − y[t−1]\| > ln(1.5)` | `SUSPECTED_UNADJUSTED_SPLIT` | GX-10 |

All three **reject the bar-set**, before any geometry is fitted, and produce no line
at any prefix — which is what GX-10 and GX-18 record (`"Input guards (§18) reject the
bar-set before any geometry is fitted, so no as-of-time line exists at any prefix"`),
and which is why neither fixture has a `gate_trace`. This is the plan's **one
deliberately non-causal element**; it is confined to a pre-pass, it can only produce
a whole-series rejection, and it interacts with the prefix-invariance property test
in a way that must be handled explicitly rather than assumed away (§6.4 P-2).

**What the engine must *not* reject.** A short series (that is `NONE` +
`INSUFFICIENT_BARS`, an explicit no-signal state, not an error); a series with no
pivot highs (GX-08); an ATH on the first bar (GX-09); a series with no envelope-valid
second anchor (that is `NONE` + `NO_VALID_SECOND_ANCHOR`, GX-20).

---

## 3. The as-of-time evaluation loop — the heart of it

§21 is normative over §4–§18. The single invariant, in the specification's own words
(§21.6): **"The evaluation bar MUST NEVER redefine the line against which its own
event is judged."**

### 3.1 The design rule

> A shape that **cannot** look ahead beats a shape that is **checked** for not
> looking ahead.

Every no-look-ahead defect this repository has already paid for came from a
full-series computation that was *later* audited for causality. The plan therefore
makes causality a property of the **types and the call graph**, and keeps the tests
as controls on the parts that remain checkable rather than as the primary defence.

### 3.2 Structural enforcement (four mechanisms, all cheap)

1. **The batch API *is* the streaming API.** `detect()` is a left fold over bars:
   `reduce(step, bars, initial_state)`. There is no separate batch path, so
   §21.8's "streaming equals batch" equivalence is true by construction. **This
   makes the §21.8.3 operational test vacuous, and the plan says so out loud** — a
   test that cannot fail is exactly the failure mode this repository keeps repeating.
   It is replaced by prefix-truncation invariance (§6.4 P-2), which *can* fail.
2. **No geometry function ever receives the full series.** `anchor_of`,
   `select_second_anchor` and `formation` take a `Prefix` — an immutable view of
   `bars[0 … n−1]` carrying its own length. The evaluation bar is passed to `step` as
   a *separate argument*, never appended to the prefix before evaluation. A geometry
   function has no reference through which a future bar is reachable.
3. **The line that judges bar `t` is sealed before bar `t` exists.** `Λ_t`, its
   formation-gate verdict, and any pending `LINE_ESTABLISHED` record are computed at
   the **end** of `step(t−1)` by `seal()`, from `S_t`. `step(t)` only *consumes*
   them. Bar `t` cannot influence its own judge because its judge was already
   finished when bar `t` was read.
4. **Length assertion at every geometry entry point.** `seal()` asserts
   `len(prefix) == t` before computing `Λ_t`. An off-by-one that leaks bar `t` into
   `Λ_t` is an assertion failure, not a subtly wrong number.

### 3.3 Normative per-bar order (§21.2, restated as the implementation's contract)

For evaluation bar `t`, given state sealed from `S_t`:

| # | Step | Spec | Notes |
|---|---|---|---|
| a | emit pending line records attributable to bar `t`: `LINE_ESTABLISHED` (formation or a re-selection **effective** at `t`), `ENVELOPE_TIE_LATER`, and the head-of-run `NONE` reason if the run's reason changed at `t` | §21.6 rule 2, §21.3 | line records precede the bar's own event records, always |
| b | **new-ATH test first**: `H[t] > HA` → `RESET_NEW_ATH`, close the episode, skip c–d | §21.2 rule 5, §21.7 | takes precedence over breakout and over the roll. `H[t] == HA` is **not** a new ATH (D-TL-02) |
| c | if `Λ_t = ⊥` (state `NONE`): no event test may run | §21.3 | "a bar that cannot be evaluated MUST NOT be evaluated later" |
| d | else evaluate bar `t` against `Λ_t`: breakout predicate (§13.1) → **stop**; otherwise pierce (§10.1) → `INVALID_PIERCE` in the bar's code set, and — since the close did not confirm — a `WICK_BREAK` record (`ACTIVE → ACTIVE`) | §13.1, §10.1, §14 | see the invariant in §3.5 |
| e | `seal()` for bar `t+1`: append `y[t]`; update the anchor; if not stopped and not reset, recompute `B*` over `S_{t+1}` and register any re-selection **effective at `t+1`**; if `NONE`, evaluate F1/F2/F3 on `S_{t+1}` and append the gate-trace entry | §21.2 step 4, §21.6, §21.3 | *no line ever takes effect on the bar that caused it to be computed* (§17) |

The corner §21.6 rule 3 names explicitly — a bar that takes an incoming re-selection
*and* makes a new ATH — falls out of this order without special-casing: step (a)
records `LINE_ESTABLISHED`, step (b) records `RESET_NEW_ATH`. A line established and
retired within one bar. No fixture depends on it; the order produces it anyway.

### 3.4 The Phase-3 extension seam

`seal()` dispatches its recompute branch on the episode state. Phase 2 ships two
branches (`NONE` → formation evaluation; `ACTIVE` → roll). Phase 3 adds a third
(`FROZEN` → **no** recompute, i.e. §21.5's suspension) and adds handlers for the
stop outcome. **No Phase-2 branch is edited.** Similarly, `step`'s (d) returns a
`BarOutcome` sum type (`NoEvent`, `WickBreak`, `Reset`, `BreakoutSignalled`); Phase 3
adds variants and a post-stop driver. This is the whole of the forward compatibility
claim, and it is deliberately small: anything larger would be designing Phase 3.

### 3.5 Two invariants worth asserting, because they are cheap and load-bearing

- **Pierce ⇒ wick-break, in Phase 2.** Reaching step (d)'s `else` means the close did
  not confirm; §14's second conjunct therefore holds, so any bar that pierces beyond
  `ε` is a wick-break. The fixtures agree exactly: `WICK_BREAK` and `INVALID_PIERCE`
  are recorded for the identical set {GX-02, GX-03, GX-09, GX-12, GX-13}. Assert set
  equality across the corpus; a divergence is a defect in one of the two.
- **Monotone shallowing.** Within an episode with an unchanged anchor, `m_t` is
  non-decreasing (§21.4). Assert it per bar. It is free and it catches an entire
  class of re-selection errors immediately.

---

## 4. §8 envelope selection, the §21.4 lemma, ties, and the numerical hazard

### 4.1 The definition the engine implements

The **normative** definition is the §8 brute force over the prefix, and that is what
the engine implements as its production path:

1. Candidates: every `i ∈ S_t` with `i > tA` **and** `H[i] < HA` (strict — §6 rule 2).
2. For each candidate, `slope(i) = (y[i] − y[tA]) / (i − tA)`.
3. `envelope_valid(i)` iff for **every bar high** `j ∈ S_t` with `j > tA`,
   `y[j] ≤ ŷ_i(j) + ε` (D-TL-05: **all** bar highs, never a pivot subset, and never
   only the candidates).
4. `B*_t = argmax slope` over the envelope-valid candidates, **later `i` wins exact
   ties** (`ENVELOPE_TIE_LATER`, §18).
5. `B*_t = ⊥` when no candidate is envelope-valid → `NO_VALID_SECOND_ANCHOR` (§10.4).

**The candidacy filter and the domination set are different sets, and conflating them
is the single easiest way to fail this gate.** A later high that *ties* the ATH is
excluded from candidacy (`H < HA` is strict) but **remains in the domination set**,
so it pierces every descending candidate and yields `NO_VALID_SECOND_ANCHOR`. That is
GX-20 (permanent, tie before `min_formation_bars`) and GX-12 (transient, `t=8…11`).
Both are named unit tests, not incidental coverage.

`worst_gap(i) = max over the domination set of (y[j] − ŷ_i(j))`, which is exactly `0`
at `j = i` and therefore never negative — matching the published `causal_record`
values (GX-01: `worst_gap 0` for the selected candidate, `0.0177383` for a valid but
steeper one, `envelope_valid` iff `worst_gap ≤ ε`). The engine emits `slope`,
`worst_gap` and `envelope_valid` per candidate because the gate compares them.

### 4.2 The §21.4 running-max lemma — a test oracle, not the production path

§21.4 states the lemma (`B*_{t+1} = (t, H[t])` iff `y[t] ≥ ŷ_t(t)`, else unchanged)
and then states its own status: *"The Lemma is an **optimization, not the
definition**"*, usable only if lossless against the §8 recomputation, with mandatory
fallback when the anchor changes, a candidate ties the ATH, or `B*_t = ⊥`.

**Decision: Phase 2 does not implement the lemma in the production path.** Reasons,
in order: correctness before speed is a stated design value; the fixture series are
19–130 bars and RM-01 is 29, so the brute force is trivially fast enough; and every
"lossless optimization" here has three fallback conditions that are themselves defect
sites. Instead the lemma is implemented **in the test suite** as an independently
written oracle and asserted equal to the brute force **at every evaluable prefix of
every fixture** — a genuine two-version check inside Phase 2, at zero product risk.

**Known scaling limit, recorded rather than solved.** Brute force is `O(t²)` per bar,
`O(n³)` per series: fine at `n ≈ 10²`, not fine at `n ≈ 10⁴` (a 50-year daily
history). Phase 4 may adopt the lemma as a validated optimization, gated on the
equivalence oracle above. Optimizing now would be gold-plating (GOV-007).

### 4.3 The numerical hazard — GX-14, and why the arithmetic form must be pinned

GX-14 exists because **two algebraically identical forms of §7 produced different
selected anchors in IEEE 754.** The fixture's own record is unambiguous: an earlier
construction's *"selected anchor FLIPPED between (40,65.61) and (30,72.90) depending
on whether the slope was computed as `(ln H − ln HA)/dt` or as `ln(H/HA)/dt`, two
algebraically identical readings of §7. An expected value that depends on the
associativity of a floating-point expression is not reproducible evidence."*

The engine must therefore fix the form, in one place, and pin it by test:

| Quantity | **Required** form | Forbidden |
|---|---|---|
| `y[t]` | `math.log(H[t])`, computed **once per bar** and cached in the fold state | recomputing `ln` at a second call site; `log1p`; `log` of a ratio |
| `slope(i)` | `(y[i] - y[tA]) / (i - tA)`, numerator a difference of the cached logs, denominator an exact integer difference | `math.log(H[i] / H[tA]) / (i - tA)`; any fused or reassociated variant |
| `b` | `y[tA] - m * tA` | any rearrangement |
| `ŷ(u)` | `m * u + b` | `y[tA] + m * (u - tA)` — equal in ℝ, not in IEEE 754 when `tA ≠ 0` |
| comparisons | form the right-hand side first: `lhs > y_hat + eps` | `lhs - y_hat > eps` |
| tie detection | exact `==` on the computed slope doubles, **no tolerance** | any epsilon-tolerant "near-tie" |

These live in `engine/logspace.py` and nowhere else, so there is exactly one place to
get them wrong and exactly one place to test them. `RM-01` (`tA = 2`), `GX-06`
(anchor moves to `t = 10`) and `GX-22` (anchor moves to `t = 12`) are the fixtures
with `tA ≠ 0`, and they are what pin the intercept/line-evaluation form.

**The GX-14 libm caveat is a gating preflight, not a skip.** The fixture's tie holds
because `log(68.89) == 2·log(83) − log(100)` bit-for-bit under the libms tested (V8
and CPython); IEEE 754 does not require `log()` to be correctly rounded, so a
different math library breaks the tie and selects `t=18` outright. The test suite
must assert that identity as a **preflight that fails loudly** on a platform where it
does not hold, naming the platform and the observed ulp difference. It must **not**
skip: a skipped assertion is an unfalsifiable gate, and this repository has already
shipped two of those.

---

## 5. Determinism requirements (binding, §20 + §21)

| # | Requirement | How it is made true | How it is checked |
|---|---|---|---|
| D-1 | 6-significant-figure geometry, compared **exactly** | one `sig6()` in `logspace.py`; decimal rounding of the exact binary value of the double, **ROUND_HALF_EVEN**, quantized to 6 significant digits | the conformance harness compares `sig6(computed)` to the fixture's stored decimal, as strings; plus the tie-proximity audit (§6.5 C-4) |
| D-2 | no dependence on floating-point associativity | single-site arithmetic forms (§4.3); no `sum()`/`fsum`/reductions in the geometry path; no NumPy in `engine/` | seeded mutation M-1/M-2 must be caught; static import ban test |
| D-3 | stable ordering everywhere | candidates iterated ascending by `t`; records ordered by `(bar, within-bar §21.6 rule-2 order)`; reason codes emitted in first-emission order; no iteration over a `set` on any output path | `PYTHONHASHSEED` variation test (§6.5 C-1) |
| D-4 | no wall-clock, no randomness | no `time`, `datetime.now`, `random`, `secrets`, `uuid`, `os.urandom` anywhere under `engine/`; time is passed in and never read | static import-ban test **and** a runtime test that monkeypatches those modules to raise, then runs the full corpus |
| D-5 | ties broken by stated rules only | D-TL-02 (earliest ATH), `ENVELOPE_TIE_LATER` (later `B`) | GX-12 and GX-14; mutations M-8 and M-14 |
| D-6 | same input twice → byte-identical output | serialization with fixed key order | the determinism guard, run over all 24 fixtures |
| D-7 | causal evaluation is itself a determinism requirement (§20.5) | the fold (§3.2) | prefix-truncation invariance (§6.4 P-2) |
| D-8 | every output carries `spec_version` and `tolerance_version` | stamped by `detector.py` from `params` | schema/round-trip test; see §9 OQ-J — `spec_version` has no defined value yet |

---

## 6. The test plan

This is the larger half of the deliverable. **Every test below carries a "passes
while the code is wrong when…" column.** That column is not decoration: this
repository's recurring failure is gates that could not fail — an OHLC check that
exempted the class it targeted, an unfalsifiable whitelist, a `k`-sweep structurally
incapable of failing. Each such note is discharged either by a stated mitigation or
by an entry in the seeded-mutation table (§6.7), which is the plan's primary
anti-vacuity device.

### 6.1 Layer 0 — the conformance gate (23 golden fixtures + RM-01)

The gate is **derived, not enumerated**: the harness walks
`product/fixtures/golden/*/` and `product/fixtures/real/*/` and fails if it finds a
directory it did not check. Adding a fixture tightens the gate automatically; that is
the roadmap's own design and it must not be re-broken by a hand-maintained list.

> **`real/*`'s comparison contract is now defined by SPR-D-01 — see §7.3.**
> *(Superseded, retained: this previously read "`real/*` has no comparison contract yet".)*
> The field table below is headed *per **golden** fixture* for a reason: RM-01 carries an
> `annotation.json` on a different schema, with **no `expected.json` and no
> `causal_record`**. As written, a `real/*` walk would therefore either fail permanently
> or pass vacuously — and a vacuous walk is worse, because it reports coverage it does
> not have. **SPR-D-01 supplies the *decision*, not the artifact:** it rules that RM-01
> **Half B** (§7.3) **shall be** carried in a separate `expected-causal.json` — the
> annotation schema is `additionalProperties: false`, so it cannot be extended in place,
> and `annotation.json`'s values are retained untouched. **That file does not exist yet.**
> As of this document's head, `product/fixtures/real/RM-01/` holds `annotation.json`,
> `input.csv`, `README.md`, `alphavantage-source.json` and `source-chart.png` and nothing
> else; authoring `expected-causal.json`, its additive schema and the `real/`-reading tool
> extension is **owed work**, not delivered work.
>
> Four constraints on this walk. (1) The **stop index must be engine-derived, not
> fixture-supplied**, or the clause asserts nothing about the engine's own detection.
> (2) The comparison is scoped to **Phase-2-owned behaviour**. (3) **Do not quietly narrow
> the walk to `golden/*` to make it pass** — a vacuous walk is worse than a failing one,
> because it reports coverage it does not have. (4) **The artifact must exist first:** a
> `real/*` walk that finds no `expected-causal.json` must **fail**, never skip. Absent
> this fourth constraint the first three are satisfiable by a walk that checks nothing —
> exactly the vacuity the paragraph above warns against.

Per golden fixture, the engine must reproduce:

| Field | Comparison |
|---|---|
| `expected_ath_anchor` | exact `(t, H)` |
| `expected_second_anchor` | exact `(t, H)`, or `null` with the recorded reason class |
| `expected_log_slope`, `expected_intercept` | `sig6` string equality |
| `expected_line_values` | `sig6` string equality on both `y_hat` and `line`, at **every** recorded index, including post-stop indices (pure arithmetic on the reported line) |
| `expected_state_transitions` | ordered list equality for every entry at a bar **strictly before** `confirmed_bar`; for `confirmed_bar == null` fixtures, the **whole** list |
| `expected_reason_codes` | set equality, restricted to Phase-2-owned codes for breakout fixtures; full set for `confirmed_bar == null` fixtures |
| `expected_final_state` | exact, for `confirmed_bar == null` fixtures only |
| `causal_record.formation.gate_trace` | **structural** comparison: parse the fixture's per-bar strings into `(t, f1, f2, f3, first_unmet)` with a documented parser and compare structurally (§6.2) |
| `causal_record.reselections` | ordered list equality on `(effective_bar, from, to, sig6(m), tie)` |
| `causal_record.as_of_time_candidate_set` | per-candidate `(t, H, sig6(slope), sig6(worst_gap), envelope_valid)` and the selected candidate |
| `causal_record.eps_break_robustness.sweep` | equality of `(scale, final_state, breakout_bar)` at every recorded scale (§6.5) |
| `causal_record.input_guard` | `(rejected, codes, detail)` for GX-10 and GX-18 |

**Passes while wrong when:** the engine emits a *superset* of transitions and the
comparison is "contains" rather than "equals"; or `expected_line_values` is compared
only at indices the engine chose to emit. *Mitigations:* list equality in both
directions, and an assertion that the engine emitted a value for every key present in
the fixture **and** that any extra key it emitted is declared. Also: seven of the
twenty geometry fixtures share bars 0–15 byte-identically, and five of those share
`B* = (6,93)` — so **"20 geometry fixtures" is not 20 independent samples**, and a
defect in the shared base fails seven at once while leaving the gate looking broad.
The genuinely diverse geometry lives in GX-02, GX-06, GX-08, GX-09, GX-12, GX-13,
GX-14, GX-15, GX-19, GX-20, GX-21, GX-22, GX-23 and RM-01; the per-section unit
coverage below is scoped against *those*, not against the count.

### 6.2 Why the `causal_record` comparison is structural, not textual

The gate names `causal_record` fields, and the engine must reproduce them. It must
**not** reproduce another implementation's *formatting*. Requiring string equality on
`gate_trace` would silently make "author an engine whose log strings match the
reference model" part of the contract — the precise circularity HD-15 condition 2
exists to prevent, and a way for an engine fitted to the fixtures to look more
conformant than it is. The engine emits a structured trace; the harness parses the
fixture's strings into the same structure. **The exact field list to be compared must
be agreed with Verification before implementation begins** (§9 OQ-H), because a gate
whose scope is settled after the results are known is not a gate.

### 6.3 Layer 1 — per-spec-section unit coverage

| Spec | Behaviour under test | Anchoring fixtures / cases | Passes while wrong when… |
|---|---|---|---|
| §1, §18 | the three input guards reject the **bar-set**; nothing else does | GX-10, GX-18; plus a constructed set with a jump of exactly `ln(1.5)` (must **not** trip — the guard is strict `>`) | the guard is tested only on series that also fail something else. *Mitigation:* the boundary case, and mutation M-9 |
| §3, §7 | `y = ln(H)`; slope/intercept/line forms | RM-01 (`tA = 2`), GX-06, GX-22; constructed adversarial pairs | both forms agree on the whole corpus. *Mitigation:* if a seeded mutation is **not** caught, that fact is recorded as a finding and a dedicated adversarial case is constructed — never left unrecorded |
| §4, D-TL-02 | ATH = max high, **earliest** on ties, computed on `S_t` only | GX-12; GX-09 (ATH at `t=0`); RM-01 (`tA=2`) | the fixture has a unique max, so "earliest" is untested. *Mitigation:* GX-12 plus a constructed triple-tie |
| §5, HD-11 | pivot status **never** affects selection or formation | GX-08 (zero pivots), GX-19 (non-pivot `B*`), GX-23 (non-confirmable `B*`) | the engine reads `k` but happens to agree. *Mitigation:* the static import test (§6.6), which can fail |
| §6, §8, D-TL-05 | all-highs candidacy; `H < HA` strict; domination over **all** later highs | GX-02 (discrimination), GX-12, GX-20, GX-14, RM-01 | domination is tested only against candidates, and no fixture distinguishes. *Mitigation:* GX-12/GX-20 (equal high dominates but is not a candidate); mutations M-6, M-7 |
| §9, §10.1 | pierce beyond `ε`; `INVALID_PIERCE` on the superseded line | GX-02, GX-03, GX-09, GX-12, GX-13 | `INVALID_PIERCE` is emitted for every re-selection rather than only for pierces beyond `ε`. *Mitigation:* GX-14 re-selects **without** piercing (`≥` not `>` + `ε`) and must emit no `INVALID_PIERCE`; GX-12 bar 14 likewise |
| §11, §21.3 | the closed state set; `WICK_BREAK` is **not** a state; one record per contiguous `NONE` run | GX-03, GX-06, GX-12, GX-20, GX-22 | the run-head encoding is tested only where the run is one bar long. *Mitigation:* GX-20 (`NONE` forever, one record), GX-12 (`t=8…11`, one record), GX-06/GX-22 (`ATH_TOO_RECENT` run after a reset); mutation M-13 |
| §13.1 | the breakout predicate — strictness and the comparison form | GX-15 at its documented boundary `0.008242654587`, both sides; GX-16 | the boundary is tested with a rounded value on the wrong side. *Mitigation:* full-precision boundary values, and the fixture's own statement that at exactly the boundary the strict inequality is **not** met |
| §14 | wick-break: high pierces, close does not confirm; stays `ACTIVE`; re-selects | GX-03, GX-12, GX-13 | the wick and the close are tested against different lines by accident. *Mitigation:* the assertion that both use `Λ_t`, plus the pierce⇒wick invariant (§3.5) |
| §18 / §21.3, D-TL-12 | F1, F2, F3 evaluated **independently**; `t_form` is the least `t` satisfying all three | GX-21 (F1 alone binds), GX-22 (F2 alone binds, post-reset), GX-23 (same `t_form`, structurally different prefix), GX-20 (F3 never satisfied) | the three gates are evaluated as a single conjunction, so "which one binds" is never wrong because it is never computed. *Mitigation:* the gate trace is compared per gate per bar; mutation M-10 |
| §21.6, §21.7 | re-selection effective at `t+1`; new ATH takes precedence and is not a breakout | GX-03, GX-09, GX-12, GX-14, GX-06, GX-22 | the effective bar is tested only where the re-selection changes nothing observable. *Mitigation:* GX-14's second re-selection has an identical slope and must still be recorded at `t=19`; mutations M-4, M-11 |
| §21.4 | monotone shallowing; the lemma agrees with the brute force at every prefix | all 20 geometry fixtures + RM-01 | the oracle is the same code as the implementation. *Mitigation:* the oracle is written from §21.4's closed form, the implementation from §8's brute force; they share only `logspace` |

### 6.4 Layer 2 — property-based tests

| ID | Property | Generation | Passes while wrong when… |
|---|---|---|---|
| **P-1** | **No look-ahead.** For any series and any bar `t`, mutating **any** bar at index `> t` leaves every record at bars `≤ t` unchanged | random series (positive, guard-passing) + a random mutation of a suffix bar | the generator never produces a series in which a suffix bar *could* have mattered (e.g. always monotone decline, where nothing re-binds). *Mitigation:* a **generator-quality assertion** — at least X% of generated series must contain a re-selection, a wick-break and a `NONE→ACTIVE` transition, asserted in the test run itself, and the suite fails if the corpus is degenerate |
| **P-2** | **Prefix-truncation invariance.** For a guard-passing series and any `k`, running on `bars[0…k]` yields exactly the record prefix of the full run through bar `k` | as P-1 | the property is asserted only for `k = n`. *Mitigation:* all `k` are exercised; and the **guard interaction is handled explicitly, not exempted** — for a series whose guard trips at bar `g`, truncation before `g` legitimately changes the result, so the test asserts the *converse* as a positive control: truncating GX-10 before its bar-4 split must produce a **non-rejected** run with real geometry. Without that control, "condition the property on guard status" is indistinguishable from "exempt the class the test targets" |
| **P-3** | **Frozen-line stability.** Once the breakout predicate fires at `t`, no later bar changes `line_at_stop`, and no record is emitted at a bar `> t` | as P-1, filtered to series that break out | Phase 2 halts at the stop bar, so there are no later bars to change anything — the property is **near-vacuous in Phase 2 by construction**. *Stated as such*; it is retained because it becomes load-bearing the moment Phase 3 continues past the stop, and it is asserted then against `Λ^F` |
| **P-4** | **Hull validity at every evaluable prefix.** For every prefix, the selected `B*` is envelope-valid and no envelope-valid candidate has a strictly greater slope; ties resolve later | all fixtures + random series | "no candidate has greater slope" is checked against the same candidate enumeration the selector used. *Mitigation:* the checker re-enumerates candidates independently, including ones the selector pruned |
| **P-5** | **Formation gates are independent of `k`.** Changing `k` moves no event | — | **This sweep is structurally incapable of failing** and is not offered as proof — HD-14's own correction says exactly this about the equivalent sweep on the reference model, and the plan does not repeat the error. *Replacement:* the static import test (§6.6), which fails the moment `engine/formation.py` or `engine/envelope.py` acquires a dependency on `engine/pivots.py` or reads `params.k`. The sweep is retained as a cheap redundant regression, **labelled** as unfalsifiable in the evidence log |
| **P-6** | **Monotone shallowing** within an episode with an unchanged anchor (§21.4) | all fixtures + random | series with no re-selection make it trivially true. *Mitigation:* generator-quality assertion as in P-1 |

### 6.5 Layer 3 — the HD-13 `eps_break` robustness sweep, as a **gating** check

HD-13 rule 1 (retained in full, 2026-07-26): every **ordinary** fixture's expected
classification must be invariant under **±20%** variation around the documented
`eps_break` default; GX-15 alone is the dedicated tolerance-boundary fixture.

The Phase-2 suite runs this **against the engine**, independently of any other
harness, and it **gates**:

| Check | Statement | Passes while wrong when… |
|---|---|---|
| **C-1** | every ordinary fixture's `(final_state, breakout_signalled_bar)` is invariant at `0.8×` and `1.2×` | — |
| **C-2** | the engine's sweep results **equal the recorded** `causal_record.eps_break_robustness.sweep` at every recorded scale, including `0.5×` and `2×` | C-1 alone is self-consistency: an engine that ignores `eps_break` entirely passes it trivially. C-2 compares against committed data and is the falsifiable half |
| **C-3** | **anti-vacuity on the whitelist**: GX-15 must still be **non-invariant** across the wider sweep (a stale exemption fails), the whitelist must name **exactly one** fixture, and that fixture must still exist | a whitelist is otherwise unfalsifiable — the exact defect class this repository has already shipped |
| **C-4** | **tie-proximity audit**: no expected value in any fixture sits within 1 ulp of a 6-significant-figure rounding tie | otherwise `sig6`'s rounding mode is an undeclared dependency and the gate is platform-luck. Any hit is escalated (§9 OQ-B), not silently absorbed |
| **C-5** | the sweep is **shown capable of failing**: mutation M-3 (`≥` for `>` in §13.1) and a mutation that ignores `eps_break` must both break it | a sweep that cannot fail is a decoration |

Additionally, and **non-gating**: an `ε` (envelope) sweep is recorded as a
diagnostic, with one gating assertion at GX-15's documented envelope boundary
`0.018534340624` — below which a `WICK_BREAK` appears at `t=28`, which is
**Phase-2-owned behaviour** under the behavioural boundary rule. HD-13 mandates only
the `eps_break` sweep; adding an `ε` sweep to the *test suite* changes no product
rule, and it is labelled as a diagnostic so it cannot be mistaken for one.

### 6.6 Layer 4 — architectural tests (these are the ones that can fail)

| ID | Assertion | Replaces |
|---|---|---|
| **A-1** | no module in the geometry/formation/causal path imports `engine/pivots.py`, and none reads `params.k` | the unfalsifiable `k`-sweep |
| **A-2** | no module under `engine/` imports `time`, `datetime`, `random`, `secrets`, `uuid`, `os.urandom`, `numpy`, or performs any I/O | a prose claim of purity |
| **A-3** | no module under `engine/` or its tests imports, executes, or references any path under `tools/` | E2-AUTHOR-A's executable senses (independence-mechanism D1), asserted from inside the engine's own suite as well as in CI |
| **A-4** | `ReasonCode` and `LineState` are exactly the schema's closed sets | drift between code and `fixture.schema.json` |
| **A-5** | the conformance harness derives its fixture list from the directory and fails on an unvisited directory | a hand-maintained fixture list — the defect class #19 already paid for |

### 6.7 Layer 5 — seeded mutations (the anti-vacuity backbone)

Each seeded defect must be caught by at least one **named** test. A mutation that
survives is a finding: either the corpus cannot distinguish it (record that, and add
an adversarial case) or a test is weaker than it looks.

| ID | Seeded defect | Must be caught by |
|---|---|---|
| M-1 | slope via `ln(H[i]/H[tA])` instead of the difference of cached logs | GX-14 tie test |
| M-2 | `ŷ(u)` as `y[tA] + m·(u − tA)` | RM-01 / GX-06 / GX-22 `sig6` comparison; **if uncaught, record and construct** |
| M-3 | `≥` for `>` in §13.1 | GX-15 boundary test; C-5 |
| M-4 | re-selection effective at `t` instead of `t+1` | GX-03, GX-09, GX-12, GX-14 transition bars |
| M-5 | `H[t]` incorporated before bar `t` is evaluated | P-1, P-2, and most breakout fixtures |
| M-6 | candidacy uses `H ≤ HA` instead of `<` | GX-12, GX-20 |
| M-7 | domination tested only over candidates (or only over pivots) | GX-12, GX-20; GX-08, GX-19 |
| M-8 | envelope tie broken toward the earlier anchor | GX-14 |
| M-9 | input guards applied per bar rather than to the bar-set | GX-10; P-2's positive control |
| M-10 | formation gates evaluated over the full series | GX-21, GX-22 |
| M-11 | a new-ATH bar recorded as a breakout of the retired line | GX-06 |
| M-12 | `H[t] == HA` treated as a new ATH | GX-12 |
| M-13 | `NONE`-run reason emitted per bar instead of once per run | GX-12, GX-20, GX-06, GX-22 |
| M-14 | ATH tie resolved to the latest bar | GX-12 |
| M-15 | `worst_gap` clamped, or computed over the wrong set | `as_of_time_candidate_set` comparison |

### 6.8 Determinism and evidence tests

- **Determinism guard:** same input twice → byte-identical serialized output, over all
  24 fixtures. *Passes while wrong when* the serializer sorts away a real ordering
  defect — *mitigation:* order is asserted separately (D-3), and the guard runs under
  varied `PYTHONHASHSEED`.
- **Reason-code coverage report:** every code in the closed set that Phase 2 owns is
  exercised by at least one fixture, and every code the engine can emit is in the
  closed set. *Passes while wrong when* coverage is measured by "the code appears in
  the source" — *mitigation:* it is measured by emission during the conformance run.
- **Clean-checkout run:** the whole suite passes from a fresh clone with no network.

---

## 7. RM-01 — why it is load-bearing, and a finding that must be resolved before implementation

### 7.1 Why the ruling put it in the Phase-2 gate

The synthetic set is **spec-derived**. It can prove an engine is self-consistent with
the written specification; it cannot prove the specification describes the object the
Product Owner drew. Worse, the independence mechanism's own §8.4 states the residual
risk plainly: *an engine derived entirely by fitting to `causal_record` — never
reading a line of the model, never opening the specification — would pass every
control in that document, and would by construction pass the synthetic gate.*

**RM-01 is what bites there.** It is real OHLCV with human-approved geometry: the
Product Owner's own SPCX chart, an immutable Alpha Vantage source, a
`product_owner_approval: approved` record, and a visual-acceptance checklist. An
engine fitted to the synthetic fixtures has no route to RM-01's answer except by
actually implementing §8 correctly over real, unrounded prices — 29 bars whose highs
were not designed to be convenient. That is the non-circularity the 2026-07-26 ruling
names, and it is why RM-01 belongs in the gate even though independence controls
already exist. Independence protects the N-version argument; RM-01 protects against
both versions being faithful to a specification that describes the wrong object.

### 7.2 The standing limit, recorded

**RM-01 contains no breakout under its approved record**, so §13–§17 have never met
real data. Every breakout, retest, failure and expiry expectation in this repository
is synthetic. That is a real limit on what the Phase-2 and Phase-3 gates can claim,
and it should be stated in the evidence log rather than discovered later.

> **Superseded in part — read §7.3.** This holds only of RM-01's *approved full-series
> record*. **HD-20 is RESOLVED (SPR-D-01, delegated, 2026-07-26; Auditor-confirmed):**
> RM-01 carries **both** layers, and its as-of-time record stops at bar 10. So the
> repository **does** now have a real-data stop — but the limit lifts only partly, and
> precisely: **Phase 2 asserts `line_at_stop`, not `Λ^F`**, and asserts no `BROKEN_OUT`
> state and no `BREAKOUT_CONFIRMED` reason code, because the Product Owner ruled Phase 3
> owns confirmed breakout, retest, failure and expiry. **§15–§17 have still never met real
> data**, and RM-01's Phase-2 assertable surface is *narrower* under Half B than under
> Half A — bars 0–9 plus the stop index.

### 7.3 **Finding — RM-01's approved record is full-series; as-of-time it appears to break out at `t = 10`**

> ## ⚠ SUPERSEDED BY **SPR-D-01** (2026-07-26) — retained as the finding, not as the position
>
> **Everything below states the question as it stood while HD-20 was open. It is retained
> verbatim because SPR-D-01 forbids deleting evidence, and it must not be read as the
> current position.** Read it as *how the divergence was found and proved*; read
> [`../../product/roadmap.md`](../../product/roadmap.md) Phase 2 exit criteria and the
> [register](../../product/human-decisions.md) → *Delegated product decisions (HD-21)*
> for *what was decided*.
>
> **What changed.** The divergence is **confirmed, not tentative** — "appears to" in the
> heading above is stale, and the heading is **retained unedited on purpose**, because
> section headings are cited by anchor elsewhere and rewriting one silently breaks those
> links. Read the heading as the question that was asked, not as the answer. HD-20 is
> **RESOLVED** — by **SPR-D-01**, a **delegated** decision of
> the Strategic Product Reviewer under HD-21, **not** a Product Owner ruling, and
> overturnable by the Product Owner at any time without cause. RM-01 carries **both**
> layers, neither superseding the other.
>
> **Two statements below are now positively wrong and are corrected here rather than in
> place:**
> - **Consequence 1 says a conforming engine "would report `Λ^F` … and
>   `confirmed_bar = 10`".** Under SPR-D-01 **Limit 1** the Phase-2 gate asserts
>   **`line_at_stop`, NOT `Λ^F`**, and asserts **no `BROKEN_OUT` state and no
>   `BREAKOUT_CONFIRMED` reason code** — those are Phase 3's. Consequence 1 describes a
>   gate shape that was rejected.
> - **"Half B (escalate)" and "the Product Owner asked to rule"** describe an escalation
>   that has since happened and been answered by delegation. Half B's expectation is no
>   longer "unrecorded" as a decision — though the *artifact* (`expected-causal.json`)
>   is still owed; see §6.1.
>
> The **four scope limits** (Phase-2-only; engine-derived stop index; Half B **narrows**
> RM-01's assertable surface to bars 0–9 plus the stop index; and the circularity limit
> under which a replay-generated Half B is a **regression guard against today's model,
> not independent verification**) travel with every use of SPR-D-01 and are stated in
> full in the roadmap and the register. **No GOV-015 clearance is granted.**

The RM-01 record was produced before HD-12, and the as-of-time audit of 2026-07-25
explicitly did **not** cover it (`fixtures/README.md` §6a: *"RM-01 itself is untouched
by that audit"*). Its approved values — `B* = (25, 2026-07-21, 129.88)`,
`m = −0.0240143`, `b = 5.46697`, zero envelope violations, no breakout — are the
**full-series** hull over all 29 bars.

§21.4's own corollary predicts the hazard: the causal line lies **at or below** the
full-series line, so *"the first as-of-time breakout of an episode occurs at or before
the first full-series breakout — never after, and **it may exist where the
full-series calculation reports none**."*

Re-deriving RM-01 as-of-time by hand from the committed `input.csv`, with the
documented defaults (`min_formation_bars = 8`, `min_ath_age_bars = 3`, `ε = 0.02`,
illustrative `ε_break = 0.01`):

| Bar | Date | Event | Arithmetic |
|---|---|---|---|
| — | — | anchor | `A = (2, 225.64)`, `yA ≈ 5.418941` |
| 8 | 2026-06-25 | `t_form = 8` (F1 binds; F2 satisfied from `t = 6`) | `B*_8 = (3, 213.7999)`, `m ≈ −0.0539003`, envelope-valid over `S_8` |
| 9 | 2026-06-26 | pierce beyond `ε` → `INVALID_PIERCE` + `WICK_BREAK`; re-selects | `y(158.40) ≈ 5.0651235 > ŷ_9(9) + 0.02 ≈ 5.0616389`; close `153.23` does not confirm |
| 10 | 2026-06-29 | **breakout predicate fires** | `Λ_10`: `B* = (9, 158.40)`, `m ≈ −0.0505453`, `ŷ_10(10) ≈ 5.014578`; `ln(164.19) ≈ 5.101024 > 5.014578`, **margin ≈ 0.086446 log units (≈ 9.0%) over the line** |

The margin is roughly thirty times any plausible hand-arithmetic error, and it
survives every sweep point HD-13 contemplates.

> **Corrected 2026-07-26.** An earlier revision of this section, and the commit message
> that landed it, said suppression would need `ε_break ≈ 0.076`, about `7.6×`. **That is
> wrong**, and the error is instructive: `0.0764` is the margin over `line + ε_break`,
> not over the line. Setting `ε_break = 0.076` therefore does **not** suppress the
> breakout — the predicate still fires, since `5.101024 > 5.014578 + 0.076`. Suppression
> requires `ε_break ≥ 0.086446`, i.e. **≈8.6× the documented `0.01`**. Caught by the
> Strategic Product Reviewer and confirmed by direct evaluation of the predicate at
> `0.076`, `0.0864` and `0.0865`. The figure is load-bearing — it is what forecloses
> "just tune the tolerance" as an answer — and HD-13 forbids resolving fixture outcomes
> by tolerance regardless.

If the re-selection at bar 9
were somehow wrong, the line judging bar 10 would be *steeper*, and the breakout would
be larger still. The same rally re-fires at bar 11 under a later formation.

**Consequences, if this stands after mechanical confirmation:** *(historical — stated
while HD-20 was open; consequence 1 was **not** the disposition adopted, see the banner)*

1. A **spec-conforming** engine cannot satisfy the Phase-2 RM-01 exit clause as
   written. It would report `Λ^F` — anchor `(2, 225.64)`, `B* = (9, 158.40)`,
   `m ≈ −0.0505`, `b ≈ 5.5200` — and `confirmed_bar = 10`, not `(25, 129.88)` /
   `−0.0240143` / `5.46697` / `confirmed_bar == null`.
   *(**Superseded by SPR-D-01 Limit 1.** The adopted gate asserts **`line_at_stop`, not
   `Λ^F`**, and asserts **no `confirmed_bar` and no `BREAKOUT_CONFIRMED`** — those are
   Phase 3's. The premise — that the clause **as then written** was unsatisfiable — was
   correct, and is what the A/B split resolves.)*
2. RM-01 would acquire the repository's **first real-data breakout**, changing the
   standing limit in §7.2 — and making §13's policy testable against real data for
   the first time.
3. It is a **Product-Owner-reserved** matter on two counts: RM-01's approved geometry
   is the Product Owner's own chart reading, and RM-01's place in the exit gate is a
   2026-07-26 ruling. An agent may not re-derive an approved record and quietly
   replace it.

**Proposed disposition — safest reversible split, for the Product Owner, not taken
here:**

- **Half A (uncontested, keep in the gate now).** `select_second_anchor()` applied to
  the full 29-bar prefix must reproduce `(25, 129.88)`, `−0.0240143`, `5.46697` and
  zero envelope violations to 6 significant figures. This is pure §8 geometry, it is
  exactly what the human approved and what the visual-acceptance checklist verified,
  and it is fully non-circular. It is also the strongest single test of the envelope
  selector in the whole corpus.
- **Half B (escalate).** The as-of-time state-machine expectation for RM-01 is
  currently **unrecorded**, and "no breakout in range" appears to be a full-series
  statement. Before Phase 2 implementation begins, RM-01 should be re-derived
  as-of-time by a party other than the Phase-2 author, the result recorded as an
  `expected.json`-shaped artifact with a `causal_record`, and the Product Owner asked
  to rule whether the Phase-2 exit clause means Half A, Half B, or both.
- **Do not** adjust the engine, the parameters, or RM-01's data to make the breakout
  disappear. That is fitting the object to the gate, and it is the failure mode the
  fixture exists to catch.

**Note the irony worth recording:** RM-01 has already bitten, before a line of engine
code exists. That is the ruling working exactly as intended.

---

## 8. Sequencing

Each step is independently verifiable **before** the next begins. No step's evidence
is "the next step passes".

| Step | Lands | Independently verifiable by | Gate to proceed |
|---|---|---|---|
| **S0** | *nothing built* — prerequisites | #20 closed; #21 resolved or the §9 stopgap ruled; per-scope freeze lift; RM-01 Half B ruled (§7.3) — **SATISFIED by SPR-D-01, 2026-07-26**, though its `expected-causal.json` artifact is still owed (§6.1); the `causal_record` field list agreed with Verification (§6.2); `spec_version` defined (§9 OQ-J) | **all six** recorded |
| **S1** | `params`, `bars`, `guards`, `logspace` (incl. `sig6`) | GX-10 and GX-18 **complete**; the arithmetic-form pinning tests (§4.3); the C-4 tie-proximity audit; the GX-14 libm preflight; A-2 | M-1, M-9 caught |
| **S2** | `anchor`, `envelope` | RM-01 **Half A** exactly; GX-08, GX-19, GX-23 (pivot-independence); GX-02's discrimination at its final prefix; GX-14's tie; GX-12/GX-20 candidacy-vs-domination; P-4 | M-6, M-7, M-8, M-14 caught |
| **S3** | `formation` | GX-21, GX-23 gate traces; every fixture's `t_form`; A-1 | M-10 caught |
| **S4** | `causal` fold, `ACTIVE` episode, re-selection, pierce, wick-break | GX-01, GX-02, GX-03, GX-08, GX-09, GX-12, GX-13, GX-14, GX-15, GX-20, GX-21, GX-23 **complete**; P-1, P-2, P-6; the §3.5 invariants | M-4, M-5, M-13, M-15 caught |
| **S5** | new-ATH reset, multi-episode | GX-06, GX-22 **complete** | M-11, M-12 caught |
| **S6** | breakout predicate, stop, `line_at_stop` | the pre-`confirmed_bar` portions of GX-04, GX-05, GX-07, GX-11, GX-16, GX-17, GX-19; each fixture's `confirmed_bar` **index** identified correctly; RM-01 Half B per the S0 ruling | M-3 caught; GX-15 boundary both sides |
| **S7** | `trace`, `detector`, conformance harness, sweeps, determinism, architectural tests | the full gate: 23 golden + RM-01, C-1…C-5, A-1…A-5, D-1…D-8, the full mutation table | Phase 2 exit criteria (§8.1) |

### 8.1 The Phase 2 exit criteria as they now stand

Reproduced from `roadmap.md` (Phase 2) so the plan is checkable against it, **not** as
a restatement that could drift — where the two differ, the roadmap governs:

1. Exact, as-of-time reproduction of the Phase-2-owned behaviour of **every** fixture
   directory under `product/fixtures/golden/` — no exemptions, no ID list.
2. Per fixture: `expected_ath_anchor`, `expected_second_anchor`, `expected_log_slope`,
   `expected_intercept`, `expected_line_values` to 6 significant figures, including
   **every** pre-breakout re-selection in `causal_record.reselections`.
3. The formation-gate trace with F1/F2/F3 evaluated **independently**, and the §18
   input guards.
4. Every `expected_state_transitions` entry with its `reason_code`, at a bar
   **strictly before** `confirmed_bar`; and for `confirmed_bar == null` fixtures,
   `expected_final_state` and the complete `expected_reason_codes` set as well.
5. **RM-01** (see §7.3 for the finding that touches this clause).
6. Every accept/reject emits a `reason_code` from the schema's closed set; the
   determinism guard passes.
7. Plus the E2-AUTHOR clean-room attestation, and CI green. **Explicitly not
   evidence:** agreeing with `tools/fixture-replay.mjs` (HD-15 condition 1).

---

## 9. Risks and open questions

### 9.1 What the specification settles (do not re-litigate)

Price basis (HD-01); the upper-log-hull as canonical (HD-02); first-close breakout
with no persistence wait (HD-03); all-highs candidacy and non-authoritative pivots
(HD-11); as-of-time evaluation and freeze-at-breakout (HD-12); `ε_break` unlocked
with ±20% fixture robustness (HD-13); `k`-independent formation gates at 8 and 3
(HD-14); the reference model's status (HD-15). None of these is an open question, and
this plan proposes no change to any of them.

### 9.2 Where the specification is genuinely silent — proposed safest reversible defaults

| ID | Question | Proposed default | Product-definition change? |
|---|---|---|---|
| **OQ-A** — ~~open~~ **CLOSED 2026-07-26** | RM-01's as-of-time expectation vs its approved full-series record (§7.3) | ~~escalate; do not choose~~ → **ANSWERED by SPR-D-01**: both halves are carried, neither superseding the other; Half A gated at unit level on an exported pure §8 selector, Half B within Phase-2-owned behaviour only. Its `expected-causal.json` artifact is **still owed** | **Resolved by DELEGATION, not by the Product Owner** — decided by the Strategic Product Reviewer under HD-21, Auditor-confirmed at `5b99ba6`, and **overturnable by the Product Owner at any time without cause** |
| **OQ-B** | 6-significant-figure rounding mode at an exact tie | `ROUND_HALF_EVEN` on the exact binary value; **plus** the C-4 audit asserting no fixture value is within 1 ulp of a tie. If C-4 ever hits, escalate rather than pick | No, unless C-4 hits |
| **OQ-C** | GX-14's tie depends on `log()` rounding, which IEEE 754 does not fix | gating preflight assertion that **fails loudly** on a platform where the identity does not hold; pin the CI platform and record it in the evidence log. **Never skip** | No |
| **OQ-D** | §18 guards reject the whole bar-set, which is not causal | keep as specified and as the fixtures record; confine to a pre-pass that can only produce a whole-series rejection; document it as the one non-causal element; carry P-2's positive control so the exemption cannot hide a defect | No |
| **OQ-E** | non-ascending or duplicate timestamps have **no** reason code (§1 assumes they cannot happen) | raise a precondition error (a caller defect), do **not** mint a code — the code set is closed by schema | **Yes** if a code is wanted — Product Owner |
| **OQ-F** | OHLC coherence: §1 states it as an *assumption*; §18 fixes only missing high/close and non-positive prices | **do not add a coherence rejection.** Both rejecting and evaluating an incoherent bar conform, so adding one is inventing a product rule under a freeze. Optionally assert coherence over *our own fixture inputs* in the test suite, clearly labelled as fixture data quality, not engine behaviour | **Yes** if a rejection is wanted — Product Owner |
| **OQ-G** | `expected_line_values` at post-`confirmed_bar` indices (GX-04 keys 20, 22) | Phase 2 computes them from the reported line as pure arithmetic; this performs no transition and is not Phase-3 behaviour | No |
| **OQ-H** | which `causal_record` fields are compared, and how | agree the field list with Verification **before** implementation; structural comparison, never string equality (§6.2) | No — but it must be settled *before*, not after |
| **OQ-I** | the engine and `as_of` (DI-04) | the engine records `as_of` in provenance and never reads it in logic; there is no clock in `engine/` | No |
| **OQ-J** | `spec_version` (§20.4) has no defined value — the specification declares no version number, and the fixtures carry only `tolerance_version: "tol-2026.07-illustrative"` | propose a content-addressed value (spec file commit SHA plus a human-readable tag) — but the specification is the **Product Steward's** file, so the value is theirs to define | Steward-owned |
| **OQ-K** | `O(n³)` brute force at 50-year daily histories | accept for the MVP; adopt the §21.4 lemma later, gated on the equivalence oracle (§4.2). Optimizing now is gold-plating | No |
| **OQ-L** | HD-13 mandates only an `ε_break` sweep, but GX-15's `ε` boundary also moves **Phase-2-owned** behaviour | add an `ε` sweep as a **non-gating diagnostic**, with one gating assertion at GX-15's documented `ε` boundary. A test-suite choice, not a product rule | No |

### 9.3 Risks

| Risk | Why it is live here | Mitigation in this plan |
|---|---|---|
| **Fitting to `causal_record` instead of deriving from the spec** | the fixtures publish the model's intermediate state, and the author must read them (independence-mechanism §8.4) | RM-01 (§7); structural rather than textual `causal_record` comparison (§6.2); the seeded-mutation table, which a fitted engine fails on the constructed cases |
| **A gate that cannot fail** | the repository's documented recurring failure: an exempting OHLC check, an unfalsifiable whitelist, a structurally-passing `k`-sweep | every test carries a "passes while wrong when…" note; §6.5 C-3/C-5; §6.6's architectural tests; §6.4 P-5 labelled unfalsifiable rather than counted; §6.4 P-2's positive control |
| **The corpus looks broader than it is** | seven of twenty geometry fixtures share bars 0–15; five share `B* = (6,93)` and one breakout margin | unit coverage scoped against the diverse subset (§6.1); RM-01 as real, undesigned data |
| **Float/tie non-determinism (R-2, GX-14)** | already demonstrated to flip a selected anchor | §4.3's pinned forms in one module; C-4; the libm preflight |
| **Envelope mis-implementation** | candidacy vs domination sets; pivot leakage | GX-12/GX-20/GX-08/GX-19; M-6/M-7; A-1 |
| **Silent Phase-3 scope creep** | the breakout predicate must exist in Phase 2 | §1.1's explicit split; no `BROKEN_OUT` state, no `BREAKOUT_CONFIRMED` code, no `Λ^F` naming in Phase 2; A-4 asserts the emitted code set |
| **Transcription of the reference model** | E2-AUTHOR-A | out of this plan's control; A-3 asserts the executable senses from inside the suite, and the attestation carries the rest |

---

## 10. What this plan does not do

It does not build, scaffold, or configure anything; it does not lift or narrow
[GOV-015](../../governance/build-freeze.md); it does not modify
[`roadmap.md`](../../product/roadmap.md),
[`human-decisions.md`](../../product/human-decisions.md),
[`trendline-specification.md`](../../product/trendline-specification.md) or any
governance file; it takes no Product Owner decision and marks no ticket Done. Four
items in §9.2 (OQ-A, OQ-E, OQ-F, OQ-J) are flagged to the Orchestrator for
escalation rather than absorbed (GOV-007). **OQ-A no longer blocks S0** — it was closed on
2026-07-26 by SPR-D-01 under the HD-21 delegation (§9.2). *(This sentence read "**OQ-A
blocks S0**" while the S0 row already recorded it as satisfied; one side had been updated
and not the other.)* **OQ-E, OQ-F and OQ-J remain open and still gate S0.**

---

**Related:** [`trendline-specification.md`](../../product/trendline-specification.md) ·
[`human-decisions.md`](../../product/human-decisions.md) ·
[`roadmap.md`](../../product/roadmap.md) ·
[`fixtures/README.md`](../../product/fixtures/README.md) ·
[`data-provider-findings.md`](../../product/data-provider-findings.md) ·
[`mvp-architecture.md`](mvp-architecture.md) ·
[`phase2-independence-mechanism.md`](phase2-independence-mechanism.md) *(quarantined
from the Phase-2 author — see its §3 Q4)* ·
[Issue #7](https://github.com/tomerYannay/4UR4/issues/7) ·
[Issue #20](https://github.com/tomerYannay/4UR4/issues/20) ·
[Issue #21](https://github.com/tomerYannay/4UR4/issues/21) ·
[Issue #23](https://github.com/tomerYannay/4UR4/issues/23)
