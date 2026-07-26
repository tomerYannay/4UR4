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
| **Confirmed breakout** | A breakout that satisfies the confirmation rules for a ticket (e.g. close-based, volume). For the trendline detector, the governing rule (HD-03) is the **first qualifying daily close** above the line + `ε_break`, with **no persistence wait** — see the geometry-section entry below and [`trendline-specification.md` §13](trendline-specification.md#13-confirmed-breakout-definition). |
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

## Universe & membership terms (HD-18, [#24](https://github.com/tomerYannay/4UR4/issues/24), 2026-07-26)

> **The spine of this section.** Membership on a date `d` must never be derived
> from information that did not exist on `d`. That is the **same causal
> discipline HD-12 ratified for anchor selection** — see **As-of-time (rolling
> causal) evaluation**, **Available prefix (`S_t`)** and **Active line at bar `t`**
> in the geometry table below — applied **one layer down**, to *which securities
> exist in the scan at all* rather than to *which bars build the line*. A causal
> engine run over a hindsight-selected universe is not causal; the two disciplines
> are one idea at two levels, and either alone is insufficient.

| Term | Meaning in 4UR4 |
|------|-----------------|
| **4UR4 US Large-Cap 500** | 4UR4's universe and its working product name: a **self-computed, point-in-time universe of the 500 largest eligible US-listed operating companies**, built by 4UR4 from transparent, versioned eligibility and ranking rules (HD-18). **What it is not:** it is **not the S&P 500**, not licensed S&P 500 constituent membership, and **not endorsed by, affiliated with, sponsored by, or equivalent to S&P Dow Jones Indices**. **Why it exists:** index *membership* is licensed separately from prices and far more restrictively — a separate MSA with separate fees, and SPDJI withdrew constituent names from Compustat in 2020 to license directly — while the two most complete survivorship-free datasets (Norgate, CRSP) are licence-barred from commercial use ([`survivorship-bias-findings.md`](survivorship-bias-findings.md) §2.3, §4.1, §4.2). Building the universe removes an unpriced dependency a third party could withdraw or reprice. **Its cost:** a mechanical top-500 rule cannot reproduce a committee's discretionary membership, so **4UR4 results are not comparable to published S&P 500 strategy results** — see **UNIV-DISC**. |
| **Universe** | The set of securities 4UR4 scans **on a given date** — always the 4UR4 US Large-Cap 500 as of that date, never a present-day list applied to the past. |
| **S&P 500** | An external index published by S&P Dow Jones Indices. In 4UR4 documents it appears **only** as an external market reference or as the thing deliberately *not* used as 4UR4's universe; every such use states which. It is never 4UR4's universe and 4UR4 claims no relationship to it. |
| **Eligibility rules** | The versioned criteria deciding which securities may be members at all — security type, domicile, listing venue, liquidity, operating-company status. Published, transparent, and **independently versioned** so each can change and be backtested on its own. Their initial research defaults may be set as safest-reversible under HD-17; a **material change to the intended market segment is Product Owner-gated**. |
| **Ranking rule** | The versioned rule ordering the eligible set to select the 500 members (e.g. by market capitalisation), stated precisely enough that a third party reproduces the same list from the same inputs. |
| **Point-in-time membership** | Membership as it actually stood on date `d`, derived **only** from information available on `d`. The universe that judges bar `t` may not be built from anything after it. This is **as-of-time discipline applied to the universe** (HD-12's causal rule, one layer down) and is the property that makes a backtest honest about *which names could have been traded*. |
| **As-of-date membership rebuild** | The reproducible reconstruction of the membership list for a past date from the rules plus the inputs; the demonstration (not assertion) that survivorship bias is absent — a rebuilt past list must contain names absent from today's. |
| **Survivorship bias** | Measuring a strategy on a universe selected with hindsight: today's members carry the survivors and have already deleted the failures. Two distinct biases must both be fixed — wrong *membership* (a hindsight-chosen list) and missing *prices* for names that no longer trade; fixing one alone leaves the other. Published estimates for exactly this failure mode reach **up to 8 percentage points of annualised return** — the same order as, or larger than, the entire effect 4UR4 is trying to measure ([`survivorship-bias-findings.md`](survivorship-bias-findings.md) §1). |
| **Delisted security** | A security that has ceased trading (failure, acquisition, receivership, going private). It is **preserved** in 4UR4's history with its terminal record and its membership span — never dropped because it does not exist today. The common silent failure is a provider returning success with an empty series for such a name. |
| **Membership change record (add / remove event)** | The record of a security entering or leaving the universe, carrying the **effective date** and the **evidence** that justifies it, so any single change can be audited alone. Events are **not** reliably paired — spin-offs and one-sided moves produce adds without removes and vice versa. |
| **Rebalance** | The scheduled, versioned recomputation of membership under the current rule set, producing membership change records with effective dates. The rebalance rule (cadence, buffer, effective-date convention) versions **independently** of the eligibility and ranking rules. |
| **Universe rule-set version** | The identifier naming which versions of the inclusion, liquidity, security-type, domicile and rebalance rules produced a given membership series. Every backtest records it, so a change of rules shows up as a change in results rather than hiding inside one. |
| **Stable security identity** | A non-ticker identifier (e.g. CIK) carried through the data layer, because tickers are reused and reassigned and change at rename or delisting. Membership history keyed on ticker silently misidentifies names — a rename can look exactly like a removal. |
| **UNIV-METH** | The Phase 1 exit gate on the universe *methodology* — versioned eligibility/ranking rules, point-in-time membership, delisted names preserved, adds/removes with effective dates and evidence, bias absence demonstrated, rule set independently versioned and backtestable ([`roadmap.md`](roadmap.md), Phase 1). |
| **UNIV-DISC** | The disclosure that must travel **inside** any artifact reporting backtest results, binding Phases 4–8: the universe is 4UR4's own methodology (with rule-set version), it is not the S&P 500 and implies no S&P Dow Jones Indices endorsement or equivalence, and **results are not comparable to published S&P 500 strategy results**. Enforced by a failing harness, not by a promise ([`roadmap.md`](roadmap.md), Phase 4). |

## Geometry & detection terms (from the trendline specification)

| Term | Meaning in 4UR4 |
|------|-----------------|
| **Anchor (A)** | The all-time-high **bar high (wick)** that begins the descending trendline; the earliest bar achieving the maximum high. |
| **Second anchor (B / B\*)** | The qualifying later **bar high** (pivot or not) selected by the all-highs envelope rule to define the line; `B*` is the chosen canonical one. Pivot status is **not** a precondition for candidacy or selection (HD-11, 2026-07-25). |
| **Pivot high** | A bar high that is a local maximum over a symmetric `k`-bar lookback/lookforward window (fractal). **Secondary / non-authoritative** for line selection — retained only for visualization, descriptive metadata, confidence features, and provably-lossless performance optimization (§5, D-TL-03, HD-11). |
| **Envelope rule / upper log-hull** | The selection rule choosing the **shallowest** descending log-space line from the ATH that stays at/above every intervening high within tolerance `ε` — the upper convex hull from `A` in log space. |
| **Log-hull** | Shorthand for the upper convex hull of **all later bar highs** (pivot or not) in log-price space used by the envelope rule; domination and selection are never restricted to pivot highs (D-TL-05). |
| **Tolerance ε** | Permitted deviation in **log units** for envelope domination, touch, and breakout tests (e.g. `ε≈0.02`, `ε_touch≈0.01`). |
| **Touch** | A bar whose high satisfies the `ε_touch` test while the line is ACTIVE; anchors `A` and `B` count as the first two touches. |
| **Touch count & spacing** | Number and temporal distribution of touches; feeds Confidence, not accept/reject logic. |
| **Wick-break** | An intrabar high crosses the line while the **close does not confirm**; not a signal — recorded as a rejection with reason `WICK_BREAK`, line stays ACTIVE. |
| **Confirmed breakout (confirmation policy)** | The **first daily close** above the line + tolerance (`ε_break`) fires the alert on that bar, with **no mandatory persistence wait** (revised HD-03, 2026-07-24). Persistence above the line and volume are post-breakout **confidence/quality** features only — low volume flags `LOW_VOLUME` but never voids the signal, and neither gates validity nor delays the alert. |
| **Breakout bar / confirmed bar** | The first bar whose close crosses the line + tolerance. Under the revised confirmation policy (HD-03), `confirmed_bar == breakout_bar` — there is no separate persistence-completion bar. |
| **Failed breakout** | A post-breakout re-close **below** the line by `ε_fail` within the failure window `F_fail`. |
| **Retest hold** | A post-breakout return to the broken line (now support) that dips to it and **holds** (close reclaims it) within the retest window. |
| **Line expiry / reset** | Retirement and recomputation of the line — ~`E_expiry` (~100) bars after breakout, on a new ATH, or on structural change. |
| **Reason code** | The named, machine-readable justification emitted with every accept, reject, or state transition (e.g. `INVALID_PIERCE`, `RESET_NEW_ATH`, `NO_VALID_SECOND_ANCHOR`). |
| **Line state machine** | The deterministic states ACTIVE → WICK_BREAK / BROKEN_OUT / RETESTED / FAILED_BREAKOUT / EXPIRED, each transition a pure function of the bar stream. |
| **As-of-time (rolling causal) evaluation** | Evaluating each bar against a line built only from strictly earlier bars, so no classification can ever depend on future bars; a confirmed breakout freezes the line for all downstream tests (§21, D-TL-11, HD-12). **The same discipline governs the universe one layer down** — see **Point-in-time membership** above: a causal engine run over a hindsight-selected universe is not causal. |
| **Available prefix (`S_t`)** | The bars `0 … t−1` visible when evaluation bar `t` is processed; the active line `Λ_t` is built from `S_t` only (§21.1). |
| **Active line at bar `t` (`Λ_t`)** | The canonical line — anchor, second anchor, slope, intercept, tolerance version — computed from `S_t` and in force for bar `t`'s wick/close/breakout/touch/failure/retest tests (§21.1). |
| **Formation eligibility / formation bar (`t_form`)** | The three as-of-time gates (minimum available history, anchor not too recent, an envelope-valid `B*` exists) that must all hold before a line first becomes `ACTIVE`; `t_form` is the earliest bar satisfying them (§21.3). |
| **Anchor re-selection (pre-breakout roll)** | On a non-breakout bar whose high reaches the active line, `B*` re-binds to that bar, effective from the **next** bar only; the evaluation bar never redefines the line that judges it (§21.6). |
| **Frozen event line (`Λ^F`)** | The `A`, `B*`, slope, intercept, and tolerance version captured exactly as they stood at the start of a confirmed-breakout bar; retest, failure, and expiry are evaluated against `Λ^F`, never a re-selected line (§21.5). |
| **`min_formation_bars` / `min_ath_age_bars`** | First-class, versioned, `k`-**independent** formation parameters (defaults **8** and **3**) gating when a line may first become `ACTIVE`; they replace the former pivot-derived `2k+2` and `k`-recency formulations at identical values, so re-tuning the pivot window `k` can never move an event (D-TL-12, HD-14). |

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
| **Breakout breadth** | A self-referential regime feature: the count/rate of concurrent confirmed breakouts across the **4UR4 US Large-Cap 500** universe (never an index-derived breadth statistic); sentiment context only. |

> If a term is missing or ambiguous, the **Product Steward** adds it here as part
> of making a ticket Ready — not the agent that happens to trip over it.
