# 4UR4 — Data-Provider Research (research ticket set / context)

> **No paid provider is selected here; any paid-service decision is HUMAN-GATED
> ([GOV-013](../governance/approval-gate.md)).**
>
> **Status: RESEARCH / CONTEXT ONLY under [GOV-015](../governance/build-freeze.md).**
> This is a *research instrument*, not a purchase, an integration, or a decision.
> It defines **what to investigate** so a human can later make an informed,
> licensing-aware provider choice. It feeds the `data/` provider-agnostic
> abstraction described in
> [`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md).

## How to use this document

Each research area below is a **mini research-ticket** with the same shape:
- **Question / scope** — what we are trying to answer.
- **What to evaluate** — concrete attributes to inspect.
- **Evidence to collect** — the artifacts that make findings verifiable
  (traceability), attached to the eventual research ticket.
- **Human-gated note** — where a paid choice is implied and must stop for
  approval (GOV-013).

Findings are recorded as **context**; they do **not** authorize integration.
Provider names are intentionally omitted to avoid steering the human decision.

---

## R1 — Historical daily OHLCV

- **Question / scope:** Where can 4UR4 obtain accurate, **split/dividend-adjusted**
  daily open/high/low/close/volume for all S&P 500 constituents with enough
  history to reach each name's **all-time high** (the trendline anchor)?
- **What to evaluate:** history depth (years), adjustment methodology (and access
  to *both* raw and adjusted), coverage completeness, correction/restatement
  policy, bar timestamp conventions, wick (high/low) fidelity — critical since
  trendlines anchor on **wicks**.
- **Evidence to collect:** sample pulls for a few representative symbols
  (long-lived, recently added, and a split-heavy name); a spot-check of adjusted
  vs. raw around a known split; documented history start dates.
- **Human-gated note:** if adequate depth/quality requires a paid tier →
  **HUMAN-GATED (GOV-013)**.

## R2 — Live / delayed market data

- **Question / scope:** For the daily batch MVP, is **end-of-day** data
  sufficient, and what would **delayed vs. real-time** cost if needed later?
- **What to evaluate:** EOD availability timing, delayed-feed licensing, real-time
  entitlement requirements (often exchange-fee-bearing), update latency.
- **Evidence to collect:** documented EOD delivery time; a delayed-vs-real-time
  entitlement/cost summary.
- **Human-gated note:** real-time/exchange-entitled feeds carry recurring exchange
  fees → **HUMAN-GATED (GOV-013)**. **Default MVP assumption:** EOD only.

## R3 — Stock splits & corporate actions

- **Question / scope:** How are splits, dividends, spin-offs, mergers, and symbol
  changes represented, and can 4UR4 adjust history correctly and reproducibly?
- **What to evaluate:** corporate-actions coverage, whether adjustment is
  provider-applied or self-applied, historical restatement behavior, symbol-change
  mapping.
- **Evidence to collect:** a worked example through a known split and a known
  symbol change; confirmation that an **all-time high** computed post-adjustment
  matches expectations.
- **Human-gated note:** premium corporate-actions data may be paid →
  **HUMAN-GATED (GOV-013)**.

## R4 — Historical S&P 500 constituents (survivorship-bias-free)

- **Question / scope:** Can we obtain **point-in-time** S&P 500 membership so the
  scanner and any backtest see the *actual* index members on each historical
  date, not today's members projected backward?
- **What to evaluate:** point-in-time constituent history, add/remove dates,
  history depth, licensing for index-membership data.
- **Evidence to collect:** a sample historical membership snapshot for a past date
  vs. today's; documentation of add/remove event coverage.
- **Human-gated note:** survivorship-bias-free constituent data is frequently a
  **paid, licensed dataset** → **HUMAN-GATED (GOV-013)**. This is a
  **correctness-critical** item: without it, backtests are biased.

## R5 — Delisted stocks

- **Question / scope:** Is price history for **delisted / removed** names available
  (needed so backtests and regime/breadth stats aren't survivorship-biased)?
- **What to evaluate:** delisted-symbol coverage, history retention after delisting,
  final-bar handling, mapping to the constituent history from R4.
- **Evidence to collect:** a sample history pull for a known delisted name; a note
  on how far back delisted coverage extends.
- **Human-gated note:** delisted history is commonly a **paid** add-on →
  **HUMAN-GATED (GOV-013)**.

## R6 — Fear & Greed / equivalent sentiment sources

- **Question / scope:** What sources provide a Fear & Greed composite (or
  equivalent), and could 4UR4 **reconstruct** an approximation from data it
  already licenses (breadth/volatility/momentum)?
- **What to evaluate:** composite methodology, history depth (for percentile
  features), update cadence, **and — critically — commercial/display licensing**
  (see R7). Cross-reference
  [`market-sentiment-specification.md`](market-sentiment-specification.md).
- **Evidence to collect:** methodology docs; history-depth confirmation; a
  licensing-terms excerpt; a feasibility note on 4UR4-reconstruction.
- **Human-gated note:** selecting/paying for an external sentiment source →
  **HUMAN-GATED (GOV-013)**. Recall sentiment cannot enter the **score** until the
  backtest+approval rule (spec §7) is met — this ticket is about *availability and
  licensing only*.

## R7 — Commercial redistribution rights

- **Question / scope:** For each candidate source (R1–R6), does the license permit
  **commercial use and redistribution/display** to end users — including paying
  SaaS subscribers — or only internal/personal use?
- **What to evaluate:** ToS commercial-use clauses, redistribution/display rights,
  caching/storage permissions, derived-data rights, attribution requirements,
  per-seat vs. per-app licensing.
- **Evidence to collect:** the specific license/ToS clauses (quoted, with source
  and date) for each candidate; a red/amber/green redistribution assessment per
  source.
- **Human-gated note:** **This is the highest-risk area.** Any source destined for
  **user-facing display or a shipped score** must be on a redistribution-safe
  commercial license → **HUMAN-GATED (GOV-013)**. "Free to fetch" ≠ "free to
  resell/show."

## R8 — Expected cost

- **Question / scope:** What is the total expected recurring cost to cover
  R1–R7 at MVP scope (S&P 500, daily), and how does it scale toward SaaS?
- **What to evaluate:** pricing tiers, rate limits vs. our batch volume, overage
  costs, contract/commitment terms, cost of the *combination* of datasets (OHLCV +
  constituents + delisted + corporate actions + sentiment often span tiers/vendors).
- **Evidence to collect:** a cost summary per candidate mapped to the criteria
  matrix; a "bundle vs. best-of-breed" cost comparison.
- **Human-gated note:** **all recurring spend is HUMAN-GATED (GOV-013).** This
  ticket produces numbers for a human to decide on; it commits nothing.

---

## Comparison-criteria matrix (TEMPLATE — intentionally unfilled)

> This is a **research instrument**, not a scorecard to be completed into a
> decision by an agent. Cells are left blank on purpose. A human, reviewing the
> evidence from R1–R8, populates and weighs it. Filling this in toward a paid
> selection is **HUMAN-GATED (GOV-013)**.

| Candidate | Coverage | Adjustments | History depth | Survivorship bias | Licensing / redistribution | Latency | Cost | API quality |
|-----------|----------|-------------|---------------|-------------------|----------------------------|---------|------|-------------|
| _Candidate A_ |  |  |  |  |  |  |  |  |
| _Candidate B_ |  |  |  |  |  |  |  |  |
| _Candidate C_ |  |  |  |  |  |  |  |  |

Column meanings:
- **Coverage** — symbols/universe completeness (incl. delisted).
- **Adjustments** — split/dividend/corporate-action handling; raw+adjusted access.
- **History depth** — years available (must reach each name's ATH).
- **Survivorship bias** — point-in-time constituents available? (R4/R5)
- **Licensing / redistribution** — commercial display/redistribution rights (R7).
- **Latency** — EOD/delayed/real-time timing (R2).
- **Cost** — recurring cost at MVP and SaaS scale (R8).
- **API quality** — reliability, docs, rate limits, stability, support.

## Decision protocol summary

| Item | Disposition |
|------|-------------|
| Any provider selection | **HUMAN-GATED (GOV-013)** — not made here |
| MVP data cadence | **Default: EOD/daily** (recorded; real-time deferred) |
| Survivorship-bias-free constituents | **Required for correct backtests** — flagged as likely paid |
| Sentiment source | Availability/licensing researched here; **score use blocked** until spec §7 |
| Matrix completion toward a purchase | **HUMAN-GATED (GOV-013)** |

## Out of scope
- Integrating any provider (GOV-015 build-freeze ON).
- Recommending or committing to a specific vendor or spend.
- Building the `data/` adapters (design only until freeze lifted per-scope).
