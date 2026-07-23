# 4UR4 — Product Vision (context only)

> This document exists so agents share a single, accurate understanding of the
> product. It is **context, not a build order**. Nothing here may be implemented
> until it becomes a Ready ticket on an approved roadmap and the build-freeze is
> lifted ([GOV-013](../governance/approval-gate.md), [GOV-015](../governance/build-freeze.md)).

## One-liner

4UR4 helps traders spot high-quality **breakouts from long, logarithmic
descending trendlines** that begin at a stock's **all-time high (ATH)**, and
tells them *how much to trust each signal* with an **explainable confidence
score** informed by **market sentiment**.

## Core concepts

1. **ATH-anchored log descending trendline** — a downward trendline drawn in
   logarithmic price space, anchored at the security's all-time high, tracking
   the sequence of lower highs that followed.
2. **Confirmed breakout** — price closing decisively above that trendline under
   defined confirmation criteria (to be specified per ticket, not here).
3. **Retest** — price returning to the broken trendline and holding it as
   support, strengthening the signal.
4. **Explainable confidence score** — a transparent, decomposable score so a
   user can see *why* a signal is rated as it is (structure quality, volume,
   retest, sentiment, regime). Explainability is a first-class requirement, not
   a nice-to-have.
5. **Market sentiment context** — **Fear & Greed** and a **proprietary
   market-regime score** modulate confidence. See
   [GOV-014](../governance/market-sentiment-context.md): this is **research
   context now**, not a feature to implement yet.

## Product values (inherited by every agent)

| Value | What it means for the build |
|-------|-----------------------------|
| **Correctness** | Signals and scores must be right before they are fast or pretty. |
| **Explainability** | Every score must be decomposable and defensible to a user. |
| **Traceability** | Every shipped behaviour traces to a ticket, a plan, and evidence. |
| **Reproducibility** | Given the same inputs, the system yields the same signals. |
| **Business value** | Effort is justified by user/trading value, not novelty. |

## Explicitly out of scope for the bootstrap

- Any detector, scorer, data pipeline, model, API, or UI code.
- Any Fear & Greed / regime **feature** (research context only — GOV-014).
- Any brokerage, order-routing, or financial-advice functionality.

See the [glossary](glossary.md) for precise term definitions used across tickets.
