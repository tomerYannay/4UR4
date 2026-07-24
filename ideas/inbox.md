# Ideas Inbox

Proposals only — **not** commitments. Nothing here is roadmap or work until a
**human + the Product Steward** promote it ([GOV-003](../governance/roadmap-authority.md),
[GOV-013](../governance/approval-gate.md)). Added **only** by the Product Innovation
Agent, within the idea budget ([GOV-008](../governance/ticket-hygiene.md)).

See [`workflows/ideas-inbox.md`](../workflows/ideas-inbox.md) for the process and
[`templates/idea.md`](../templates/idea.md) for the card shape.

---

## Parked (seed context — not scheduled)

### IDEA-0001 — Market-sentiment context for confidence (Fear & Greed + regime)
- **Status:** Parked — **research/context only** ([GOV-014](../governance/market-sentiment-context.md))
- **Value:** Could make the explainable confidence score more trustworthy by
  modulating it with market sentiment.
- **Effort:** Unknown — needs an experiment first.
- **Risk:** Data sourcing, over-fitting sentiment, explainability of the modulation.
- **Note:** Seeded to record the product thesis. **Do not implement.** Any work is a
  bounded [experiment](../workflows/experimentation.md) producing context, until a
  human approves a feature and lifts the [build-freeze](../governance/build-freeze.md).

---

## Active proposals

> Proposed by the **Product Innovation Agent** during the MVP planning cycle
> (2026-07-24), recorded here on its behalf (the agent is read-only, GOV-003).
> **Proposals only** — none is scheduled or approved; each awaits human + Product
> Steward triage ([GOV-003](../governance/roadmap-authority.md),
> [GOV-013](../governance/approval-gate.md)). Within the ≤3/cycle idea budget
> ([GOV-008](../governance/ticket-hygiene.md)).

### IDEA-0002 — Volume-confirmation term in the confidence score
- **Status:** New
- **Value:** Targets **breakout detection quality** and **explainability**. A breakout closing above the ATH-anchored log trendline on expanding volume is historically more durable than one on thin volume; a transparent, decomposable "volume confirmation" component makes the confidence score more *correct* and more *defensible* — the core thesis promise.
- **Effort:** Medium
- **Risk:** Volume normalization across tickers/liquidity regimes; threshold overfitting; must stay explainable (one legible term, not a black box).
- **Confidence:** Medium
- **Success measure (if promoted):** On a labeled historical set, high-volume-term breakouts show a measurably higher confirmed-continuation rate than low-volume ones, with the term contributing legibly to the score decomposition.
- **Minimum experiment:** Offline backtest — take past confirmed trendline breakouts on S&P 500 names, split by relative-volume-at-breakout, measure follow-through vs. failure. No product code; an analysis producing an evidence table.
- **Context only?** No
- **Not roadmap-ready because:** unvalidated scoring hypothesis; needs backtest evidence + Product Steward/human triage before any scoring change is committed.

### IDEA-0003 — "Why this score" explainability breakdown
- **Status:** New
- **Value:** Targets **explainability** (a first-class thesis requirement) and **retention**. Presenting each confidence score as a decomposed, human-readable breakdown differentiates 4UR4 from opaque scanners and gives traders a reason to trust — and keep paying for — the signal.
- **Effort:** Low (as a spec/mock, not a build)
- **Risk:** Over-explaining implies false precision; the decomposition must reflect the *actual* scoring logic (no post-hoc rationalization) or it erodes trust.
- **Confidence:** Medium
- **Success measure (if promoted):** In user testing, a majority of target traders correctly state *why* a signal is rated high/low from the breakdown alone, and self-report higher trust vs. a bare numeric score.
- **Minimum experiment:** Paper prototype — 3–5 example signal cards with mocked score decompositions, run a lightweight comprehension/trust test with a few trader users. Qualitative evidence only; no implementation.
- **Context only?** No
- **Not roadmap-ready because:** the presentation format is unvalidated and must couple to the real (not-yet-built) scorer; needs human + Product Steward triage.

### IDEA-0004 — Retest-hold as a distinct confidence tier
- **Status:** New
- **Value:** Targets **breakout detection quality** and **monetization**. Formalizing "broke then retested and held as support" as a distinct, higher-confidence tier lets the product surface fewer, higher-quality alerts — a natural premium/paid differentiator ("confirmed + retested") while reducing false-breakout noise.
- **Effort:** Medium
- **Risk:** Defining "held the retest" precisely (tolerance band, time window) is non-trivial; waiting for a retest adds latency, so some winning moves are missed — the tradeoff must be measured, not assumed.
- **Confidence:** Medium
- **Success measure (if promoted):** Historically the retest-held tier shows a materially higher continuation/success rate than raw breakouts, at an alert volume still high enough to justify a subscription tier.
- **Minimum experiment:** Offline backtest — replay historical breakouts, algorithmically label which retested-and-held, compare success rate and alert frequency of the retest-held subset vs. all breakouts. Evidence table only; no product code.
- **Context only?** No
- **Not roadmap-ready because:** the retest definition and monetization framing are hypotheses requiring backtest evidence + human + Product Steward triage before any detector or tiering is committed.

## Triage log
| Date | Idea | Outcome | Decided by |
|------|------|---------|-----------|
| 2026-07-23 | IDEA-0001 | Parked (context only) | bootstrap |
| 2026-07-24 | IDEA-0002 | Proposed — awaiting triage | product-innovation (pending human + steward) |
| 2026-07-24 | IDEA-0003 | Proposed — awaiting triage | product-innovation (pending human + steward) |
| 2026-07-24 | IDEA-0004 | Proposed — awaiting triage | product-innovation (pending human + steward) |
