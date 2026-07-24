# 4UR4 Glossary (shared vocabulary)

A single, authoritative vocabulary keeps tickets, plans, and evidence
consistent (supports **traceability** and **reproducibility**). Terms are
descriptive context; thresholds and formulas are **defined per ticket**, never
here.

| Term | Meaning in 4UR4 |
|------|-----------------|
| **ATH** | All-time high; the anchor point for a descending trendline. |
| **Log descending trendline** | A downward trendline fitted in logarithmic price space from the ATH along subsequent lower highs. |
| **Breakout** | Price action that crosses above the descending trendline under defined confirmation criteria. |
| **Confirmed breakout** | A breakout that satisfies the confirmation rules for a ticket (e.g. close-based, volume, persistence) — rules TBD per ticket. |
| **Retest** | Price returning toward the broken trendline and holding it as support. |
| **Confidence score** | A transparent, decomposed 0–1 (or 0–100) rating of signal quality. |
| **Explainability** | The property that a score can be broken into named, inspectable contributions. |
| **Fear & Greed (F&G)** | A market-sentiment indicator used as *context* to modulate confidence. |
| **Market-regime score** | A proprietary measure of overall market state (e.g. risk-on/risk-off) used as context. |
| **Sentiment context** | Collective term for F&G + regime inputs. Research-only for now ([GOV-014](../governance/market-sentiment-context.md)). |
| **Ticket** | A GitHub Issue representing one unit of governed work. |
| **Evidence** | Repository-verifiable proof a ticket is Done (commits, tests, CI, links). |
| **Ready** | A ticket that meets the [Definition of Ready](../governance/definition-of-ready.md). |
| **Done** | A ticket that meets the [Definition of Done](../governance/definition-of-done.md) with evidence. |

## Geometry & detection terms (from the trendline specification)

| Term | Meaning in 4UR4 |
|------|-----------------|
| **Anchor (A)** | The all-time-high **bar high (wick)** that begins the descending trendline; the earliest bar achieving the maximum high. |
| **Second anchor (B / B\*)** | The qualifying later pivot high selected by the envelope rule to define the line; `B*` is the chosen canonical one. |
| **Pivot high** | A bar high that is a local maximum over a symmetric `k`-bar lookback/lookforward window (fractal). |
| **Envelope rule / upper log-hull** | The selection rule choosing the **shallowest** descending log-space line from the ATH that stays at/above every intervening high within tolerance `ε` — the upper convex hull from `A` in log space. |
| **Log-hull** | Shorthand for the upper convex hull of pivot highs in log-price space used by the envelope rule. |
| **Tolerance ε** | Permitted deviation in **log units** for envelope domination, touch, and breakout tests (e.g. `ε≈0.02`, `ε_touch≈0.01`). |
| **Touch** | A bar whose high satisfies the `ε_touch` test while the line is ACTIVE; anchors `A` and `B` count as the first two touches. |
| **Touch count & spacing** | Number and temporal distribution of touches; feeds Confidence, not accept/reject logic. |
| **Wick-break** | An intrabar high crosses the line while the **close does not confirm**; not a signal — recorded as a rejection with reason `WICK_BREAK`, line stays ACTIVE. |
| **Confirmed breakout (confirmation policy)** | A close-based cross above the line qualified by persistence (`p_break` bars) and a soft volume check; low volume flags `LOW_VOLUME` rather than voiding the signal. |
| **Breakout bar / confirmed bar** | The first bar that crossed (breakout bar) vs. the bar that completes the persistence requirement (confirmed bar). |
| **Failed breakout** | A post-breakout re-close **below** the line by `ε_fail` within the failure window `F_fail`. |
| **Retest hold** | A post-breakout return to the broken line (now support) that dips to it and **holds** (close reclaims it) within the retest window. |
| **Line expiry / reset** | Retirement and recomputation of the line — ~`E_expiry` (~100) bars after breakout, on a new ATH, or on structural change. |
| **Reason code** | The named, machine-readable justification emitted with every accept, reject, or state transition (e.g. `INVALID_PIERCE`, `RESET_NEW_ATH`, `NO_VALID_SECOND_ANCHOR`). |
| **Line state machine** | The deterministic states ACTIVE → WICK_BREAK / BROKEN_OUT / RETESTED / FAILED_BREAKOUT / EXPIRED, each transition a pure function of the bar stream. |

## Confidence terms (from the confidence specification)

| Term | Meaning in 4UR4 |
|------|-----------------|
| **Confidence v1 (heuristic score)** | A deterministic, decomposable **0–100 quality heuristic** for a confirmed breakout; explicitly **not** a probability. |
| **Score component** | A named, bounded `[0,1]` sub-score with a points weight and a reason string (components C1–C7). |
| **Score decomposition** | The full list of components with their sub-scores, weights, contributions, and reasons; `Σ contributions (clamped) == score`. |
| **Contribution** | `weight × sub-score` — the points a component adds to the total. |
| **score_kind** | Output field fixed to `"heuristic"` in v1 to prevent probability mis-presentation. |
| **Success label (win/loss)** | The forward-outcome label used to train/validate future ML; default triple-barrier. |
| **Triple-barrier label** | Win if forward return reaches `+R_win` before a `−R_stop` stop within horizon `H_label` bars, else loss (default `+15% / −7% / 60 bars`, first touch). |
| **Calibration / rank-ordering lift** | The property that higher scores track higher realized win-rates (v1 validated by rank-ordering, not probability calibration). |
| **Market-regime score** | A proprietary, decomposable measure of overall market state (risk-on ↔ risk-off) computed from market internals; **research context only** ([GOV-014](../governance/market-sentiment-context.md)), never in Confidence v1. |
| **Breakout breadth** | A self-referential regime feature: the count/rate of concurrent confirmed breakouts across the universe; sentiment context only. |

> If a term is missing or ambiguous, the **Product Steward** adds it here as part
> of making a ticket Ready — not the agent that happens to trip over it.
