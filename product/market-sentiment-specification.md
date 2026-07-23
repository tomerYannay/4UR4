# 4UR4 — Market-Sentiment Specification (design / context)

> **Status: RESEARCH/CONTEXT ONLY under [GOV-014](../governance/market-sentiment-context.md)
> and [GOV-015](../governance/build-freeze.md) — no sentiment feature may be
> implemented until a human approves it and it becomes a Ready ticket.**
>
> This document defines *what sentiment context means* and *how it would connect
> to the explainable confidence score*. It authorizes **nothing**. No pipeline,
> scorer, API integration, model, or UI described here may be built. Every item
> below is design/context that must trace back to making the confidence score
> more **explainable** or **correct** ([GOV-007](../governance/product-focus.md)).

## 1. Purpose and thesis link

4UR4's confidence score is a *decomposable* rating of breakout quality. Market
sentiment is one **named, inspectable contribution** to that decomposition — not
a black box. The entire reason to research sentiment is the product thesis:
a user should be able to see *why* a breakout is trusted, and part of "why" is
**the market environment the breakout happened in**. A breakout from an
ATH-anchored log descending trendline in a risk-on, broadening market is a
different animal from the same geometry in a fearful, narrowing market.

Sentiment therefore has exactly one job here: **make confidence more explainable
and, once proven, more correct.** It is not a standalone product, a trading
signal, or a research rabbit hole.

## 2. The external Fear & Greed input

### 2.1 What it is
"Fear & Greed" is a composite market-sentiment indicator, conventionally scaled
0–100, where low values denote fear (risk-off) and high values denote greed
(risk-on). Popular composites blend several sub-signals (e.g. price momentum vs.
a moving average, market breadth, put/call ratios, volatility levels, safe-haven
demand, junk-bond demand). 4UR4 treats it as an **exogenous context input**, not
something 4UR4 computes authoritatively at MVP.

### 2.2 Candidate sources (design only — NO source selected)
- A well-known published index value (single daily composite figure).
- A vendor/API that redistributes a sentiment composite.
- A **4UR4-reconstructed** approximation built from inputs 4UR4 already licenses
  for its own data (breadth, volatility, momentum), avoiding a third-party
  redistribution dependency.

> **HUMAN APPROVAL REQUIRED — source selection.** Choosing an external F&G source
> is a licensing/cost/redistribution decision, deferred to the data-provider
> research ([`data-provider-research.md`](data-provider-research.md)) and gated by
> [GOV-013](../governance/approval-gate.md). This spec does **not** pick one.

### 2.3 Cadence
- **Design assumption (safest default):** ingest **once per day**, aligned to the
  daily S&P 500 batch scan, storing a timestamped snapshot. Rationale: the MVP
  scanner is daily and end-of-day; sub-daily sentiment adds cost and complexity
  with no demonstrated confidence benefit yet (anti-gold-plating, GOV-007).
- **Recorded alternative:** intraday/hourly cadence — deferred until a backtest
  shows daily granularity is insufficient.

## 3. Licensing and data-source risk (READ BEFORE ANY BUILD)

Sentiment data is where 4UR4 is most exposed to legal/commercial risk, so it is
called out explicitly:

- **Redistribution rights.** Showing a third party's proprietary index to
  end users (especially paying SaaS subscribers) may require a **redistribution
  or display license** distinct from a data-access license. "We can fetch it" is
  not "we can show it to customers."
- **Terms of Service.** Many free/consumer sentiment feeds prohibit commercial
  use, scraping, caching, or resale. A consumer endpoint is **not** a commercial
  license.
- **Derived-data ambiguity.** Whether a *derived feature* (e.g. a percentile rank
  of someone else's index) is itself licensable is often unclear and must be
  treated conservatively.
- **Provenance for reproducibility.** Every sentiment value used in a score must
  be stored with its source, license reference, and snapshot timestamp so a score
  can be reproduced and defended (traceability + reproducibility values).

> **HUMAN APPROVAL REQUIRED — licensed / redistribution-safe source.** Any
> sentiment source that will be *displayed to users* or *fed into a shipped score*
> must be on a license that permits commercial display/redistribution. Selecting
> and paying for such a source is human-gated (GOV-013). **Safest default until
> then:** the 4UR4-reconstructed approximation (§2.2), built only from inputs
> 4UR4 already has redistribution-safe rights to.

## 4. Feature definitions (design only)

Each feature is a *named contribution* candidate for the confidence
decomposition. None is wired to a score until §7's rule is satisfied.

| Feature | Definition (conceptual) | Why it aids explainability/correctness |
|---------|-------------------------|----------------------------------------|
| **Level** | The current sentiment reading (e.g. F&G 0–100 or regime score today). | "This broke out while the market was in extreme fear (18/100)." Directly human-readable. |
| **Change (delta)** | Change in the reading over a defined lookback (e.g. Δ over 5 / 20 bars). | Distinguishes *improving* vs. *deteriorating* mood; a breakout into rising sentiment may be more durable. |
| **Percentile (historical rank)** | Where today's reading sits in its own history (e.g. 0–100th percentile over N years). | Normalizes across regimes; "greed today is only 60th-percentile greed historically" is more honest than a raw number. |
| **Regime-transition** | A flag/feature marking a crossing between regime states (e.g. fear→neutral→greed transitions). | Transitions often matter more than levels; lets the score explain "breakout coincided with a risk-on transition." |

**Design defaults (safest):** lookbacks and percentile windows are **parameters
defined per future ticket**, versioned with the confidence model (§ model
versioning in the architecture doc). This document deliberately does **not**
freeze numeric thresholds (consistent with the glossary rule that formulas are
per-ticket).

## 5. The proprietary 4UR4 market-regime score (conceptual)

### 5.1 Definition
A **proprietary, explainable measure of overall market state** (risk-on ↔
risk-off) that 4UR4 computes itself from market internals. Unlike an external
F&G index, 4UR4 owns this computation end-to-end, which improves both
**explainability** (we can decompose it) and **licensing posture** (fewer
redistribution constraints if built from licensed inputs).

### 5.2 Candidate inputs (design only — not selected/weighted here)
- **Breadth** — proportion of S&P 500 names above key moving averages / making
  new highs vs. new lows.
- **Trend** — index-level position relative to long-term moving averages, slope.
- **Volatility** — realized/implied volatility level and its own percentile.
- **Breakout breadth (see §6)** — how many 4UR4 names are breaking out at once.
- **Sector context (see §6)** — dispersion/leadership across sectors.

### 5.3 Design stance
The regime score must itself be **decomposable** into its named inputs (same
explainability bar as the top-level confidence score). Weights, formulas, and
normalization are **per-ticket, versioned, and backtest-justified** — not fixed
here. Safest default: begin as a **transparent, rules-based composite** (not a
learned/opaque model) so early explanations are trivially auditable; a learned
model is a recorded alternative deferred until data and calibration justify it.

## 6. Regime inputs derived from 4UR4's own scans

Two inputs are especially valuable because 4UR4 can compute them from data it
already needs for its core detector — no extra external dependency:

- **Breakout breadth.** The count/rate of confirmed breakouts occurring
  concurrently across the S&P 500. Many simultaneous breakouts may indicate a
  broad risk-on impulse (each individual signal potentially more reliable); an
  isolated breakout in a quiet tape is a different context. This is a
  **self-referential regime feature** — cheap, licensing-clean, and directly
  explainable ("42 names broke out this week vs. a median of 6").
- **Sector context.** Whether breakouts/strength are concentrated in a few
  sectors or broad-based, and which sectors lead. Adds explainability
  ("this breakout is part of a broad industrials move, not a lone name").

Both connect straight to the thesis: they help answer *why should I trust this
breakout* using the market's own structure.

## 7. Normative rule — sentiment may not touch confidence without evidence

Consistent with [GOV-014](../governance/market-sentiment-context.md), the
following is a **firm, normative rule**, not a preference:

> **RULE (Sentiment-Before-Evidence Prohibition).**
> 1. Sentiment features (F&G level/delta/percentile/transition, regime score,
>    breakout breadth, sector context) may be **displayed as context** next to a
>    signal at any time after a human approves a sentiment *display* ticket.
> 2. Sentiment features may enter the **confidence score itself** ONLY AFTER
>    **both** conditions hold:
>    - **(a) Backtest evidence** demonstrates the feature **improves calibration**
>      of the score (i.e. scores become measurably more predictive/better
>      calibrated with the feature than without it), using a pre-registered
>      metric and out-of-sample data; **and**
>    - **(b) explicit human approval** ([GOV-013](../governance/approval-gate.md))
>      to promote the feature into the scored model.
> 3. Until both hold, the confidence score is computed **without** sentiment
>    inputs; sentiment is context only. Any code path that lets sentiment move the
>    score before (a)+(b) is a governance violation (Auditor-flagged).

**Why this rule exists:** it protects **correctness** (no unproven input silently
inflating trust) and **explainability** (every scored contribution has evidence
behind it). It is the sentiment-specific expression of "signals must be right
before they are pretty."

## 8. Evidence plan (what a future sentiment ticket must prove)

When (and only when) sentiment is promoted to a Ready ticket, its Definition of
Done should require:
- A **provenance record** for every sentiment value used (source, license ref,
  snapshot timestamp) — reproducibility.
- A **calibration backtest** artifact: metric definition, in/out-of-sample split,
  and a with-vs-without-sentiment comparison (§7a).
- A **decomposition example**: a sample signal showing sentiment as a named,
  inspectable contribution — explainability.
- A **kill-switch / feature-flag** demonstration: sentiment can be removed from
  scoring without breaking the core signal (blast-radius control).

## 9. Decision protocol summary

| Decision | Disposition | Note |
|----------|-------------|------|
| Ingestion cadence | **Default: daily**, aligned to batch scan | Alternative (intraday) recorded, deferred |
| Regime score form | **Default: transparent rules-based composite** | Learned model recorded, deferred |
| External F&G source | **HUMAN-GATED** | Licensing/cost — see data-provider research |
| Redistribution-safe source for SaaS display | **HUMAN-GATED** | Default meanwhile: 4UR4-reconstructed approximation |
| Sentiment → confidence score | **BLOCKED until backtest + human approval** | §7 normative rule |

## 10. Out of scope (explicitly)
- Implementing any of the above (GOV-015 build-freeze is ON).
- Picking or paying a sentiment/data vendor (GOV-013).
- Freezing numeric thresholds, weights, or lookbacks (per-ticket, versioned).
- Trading, order-routing, or advice derived from sentiment.
