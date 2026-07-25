# 4UR4 — Real-Market Fixture Plan (independent ground truth)

> **Status: PLAN ONLY under [GOV-015](../../governance/build-freeze.md). No market data is
> acquired, downloaded, licensed, or committed by this document.** This plans the addition
> of **manually reviewed real-market fixtures** as the independent, non-circular ground
> truth complementing the synthetic golden set in [`README.md`](README.md). Data acquisition
> depends on human-gated decisions **HD-06** (data provider) and **HD-07**
> (survivorship-free history) and on the freeze being lifted per-scope
> ([GOV-013](../../governance/approval-gate.md)).

## 1. Why real examples matter (avoid circular validation)

The synthetic golden fixtures derive their expected values **from the spec**. They prove an
engine is self-consistent with the written definitions, but they **cannot** prove the spec
matches the real-world object the Product Owner intends — validating spec-derived fixtures
against a spec-derived engine is **circular**.

Real, human-annotated charts provide **external truth**: a person marks the ATH, the second
anchor, the envelope line, the breakout, and the retest on an actual security, independently
of any engine. When the (future) engine reproduces those human annotations on real data, we
have non-circular evidence that the deterministic geometry captures the intended thesis
object. Real fixtures are therefore the **authoritative acceptance layer**; synthetic
fixtures pin the arithmetic beneath it.

## 2. The Product Owner's original chart (reserved fixture RM-01)

- **Reserved id: `RM-01`** — the **original chart supplied by the Product Owner** that
  motivated the thesis object.
- **Ticker / date-range / what it illustrates: TBD-from-PO.** These fields are intentionally
  left blank pending the Product Owner providing the chart, the ticker, the exact bar range,
  and a note on which behaviour it illustrates (e.g. ATH-anchored descending line and its
  breakout).
- RM-01 is the **canonical real anchor** for the whole real set: the first fixture the
  reviewed process below produces, and the reference the synthetic set is sanity-checked
  against.

## 3. Review process (human/analyst-gated, dual sign-off)

1. **PO supplies** the chart + ticker + date range + the behaviour it illustrates.
2. **Human/analyst annotates** on the chart, using the spec's definitions: the ATH bar (A),
   the selected second anchor (B*), the upper log-hull envelope line, the breakout bar
   (first confirming close), any wick-breaks, the retest (if any), any failure, and the
   reason codes — recorded in the same `expected.json` shape as the synthetic fixtures
   (schema `schema/fixture.schema.json`), with a `provenance` note naming the annotator and
   date.
3. **Cross-check against the selected data provider** — once **HD-06** resolves and a
   provider is human-approved — to confirm the split-adjusted, dividend-unadjusted
   ("as-traded", HD-01) OHLCV matches the annotated chart (especially wick highs, which
   anchor the geometry, and any splits in range).
4. **Dual-reviewer sign-off** — two independent reviewers must agree on the annotated
   anchors/line/events before the fixture is accepted; disagreements are escalated to the
   Product Owner. This mirrors separation-of-duties
   ([GOV-005](../../governance/separation-of-duties.md)).
5. **Commit as a reviewed real fixture** under `real/<RM-ID>/` with `input.csv` (real,
   adjusted OHLCV for the reviewed range) + `expected.json` (human-annotated expected
   output) + a provenance/licensing note. Redistribution rights must be confirmed (data
   research R7) before any real OHLCV is committed.

## 4. How many to target initially

A **small, curated set of ~5–10** reviewed real fixtures, spread across the core behaviours
so the real layer exercises each labeled outcome at least once:

- **normal valid line** (ACTIVE, no breakout),
- **first-close breakout** (BROKEN_OUT),
- **retest hold** (RETESTED),
- **false breakout** (FAILED_BREAKOUT),
- and RM-01 (the PO's chart) as the anchor case,
- with optional coverage of a **new-ATH reset** and an **expiry/recompute** on a long
  history.

Curated and manually reviewed beats volume: each real fixture is expensive (human
annotation + dual sign-off), so the set stays deliberately small and high-confidence.

## 5. Dependencies and gates (all human-gated)

- **HD-06 (data provider):** which provider supplies the adjusted daily OHLCV is
  human-gated ([`data-provider-research.md`](../data-provider-research.md) R1–R3, R8). No
  provider is chosen here; step 3 above is blocked until HD-06 resolves.
- **HD-07 (survivorship-free history):** point-in-time constituents + delisted history are
  a human-gated, likely-paid dataset (research R4/R5/R7). Needed only if a real fixture
  targets a delisted/removed name; not required for a currently-listed RM-01.
- **HD-01 (adjustment basis):** already approved — split-adjusted, dividend-unadjusted; real
  OHLCV must be pulled on that basis to match the geometry.
- **Build-freeze (GOV-015):** authoring the *plan* and the *expected.json annotation shape*
  is freeze-permitted design work; **pulling/committing real OHLCV is not** and waits on the
  provider decision + freeze lift per-scope.

## 6. Explicit no-acquisition statement

This plan **acquires no data now**. It introduces no provider, downloads no prices, commits
no real OHLCV, and makes no purchase or licensing commitment. It only reserves `RM-01`,
defines the review/sign-off process, and records the HD-06/HD-07 dependencies so that, once
a human lifts the relevant gates, the real-market ground-truth layer can be built on top of
the synthetic golden set.
