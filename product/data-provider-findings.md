# 4UR4 — Data-Provider Findings (R1, R2, R3, R6, R7, R8)

> **Status: RESEARCH FINDINGS under [GOV-015](../governance/build-freeze.md) (build-freeze ON)
> and [GOV-013](../governance/approval-gate.md).**
> This document answers the research questions defined in
> [`data-provider-research.md`](data-provider-research.md). It is **evidence and a
> recommendation**. It is **not** a selection, not a purchase, not an acceptance of
> any licence, and not a financial authorization.
>
> **[HD-06](human-decisions.md) remains PENDING and is not changed by this document.**
> Nothing here may be read as the Product Owner's approval of a provider or of spend.
> No account was created, no API key was issued, no terms were clicked through, and no
> provider data was fetched, cached, or redistributed in producing this research.
>
> **Scope note:** this document covers **R1, R2, R3, R6, R7, R8**. **R4 (point-in-time
> S&P 500 constituents) and R5 (delisted history)** were assigned to a parallel research
> effort and are deliberately *not* answered here; where a constituent/delisted question
> surfaced it is recorded in [§10 Open gaps](#10-open-gaps-and-things-i-could-not-verify)
> and routed to R4/R5 rather than answered.

**All research retrieved 2026-07-26** unless a different date is stated on the claim.

---

## 0. Method, and what "verified" means in this document

This repository's dominant defect class is *a restatement of a fact, stored apart from
the fact, and never re-derived*. Pricing, rate limits and licence text are exactly that
kind of fact: they change, and a claim without a source and a date decays into a defect.
So every factual claim below carries **(source URL, retrieval date)**, and every claim is
tagged:

| Tag | Meaning |
|-----|---------|
| **VERIFIED** | I fetched the named page on the stated date and the quoted text was in the page I read. |
| **PARTIAL** | I reached a source, but it did not contain the specific attribute; what is stated is the most the source supports. |
| **UNVERIFIED** | Reported by a search-result summary or a secondary site; the primary page was not successfully read. Treat as a lead, not a fact. |
| **GAP** | I could not determine this at all. Recorded deliberately — see §10. |

**Two structural evidence limits, stated up front rather than papered over:**

1. **R1/R3 ask for sample pulls** ("a spot-check of adjusted vs. raw around a known
   split"). Those require an API key, and issuing an API key requires accepting terms —
   which the 2026-07-26 authority boundary forbids, and which GOV-015 forbids
   independently (no client libraries, no ingestion scripts). **No sample pull was
   performed.** Every adjustment/wick claim below is therefore from *provider
   documentation*, not from observed data. This is a real, deliberate evidence gap, and
   §11 specifies it as the first acceptance test after HD-06 is taken and the freeze is
   lifted per-scope.
2. **Some primary pages could not be read.** `site.financialmodelingprep.com` returned
   HTTP 403; `twelvedata.com/enterprise` returned HTTP 404; Nasdaq Data Link's Sharadar
   pricing sits behind a login. Those are recorded as GAPs, not filled from memory.

**One naming fact that invalidates recalled knowledge.** Polygon.io **rebranded to
Massive**, effective 2025-10-30; `polygon.io/pricing` now issues an HTTP 301 to
`massive.com/pricing` (observed 2026-07-26). Prices and tier *names* on that vendor have
changed from the widely-cited pre-rebrand figures. This is precisely why nothing in this
document is quoted from memory.
(Sources: <https://massive.com/blog/polygon-is-now-massive>, observed redirect from
<https://polygon.io/pricing>, retrieved 2026-07-26.) **VERIFIED**

---

## 1. Candidate set

Candidates were selected to span the plausible price/quality range for a **US-equity,
daily-EOD, ATH-depth, redistribution-bearing** requirement — not to be exhaustive.

| # | Candidate | Why it is in the set |
|---|-----------|----------------------|
| A | **Intrinio** | 50+ year EOD history with a **published** display/commercial licence tier — the combination nothing else offers |
| B | **Massive** (formerly Polygon.io) | Consolidated-tape aggregates, documented split-only adjustment, explicit business/redistribution tier |
| C | **EODHD** | Cheap deep-history EOD vendor; publishes a commercial price list |
| D | **Norgate Data** | The only vendor found with a first-class split-only-adjusted series and history to 1950 |
| E | **Finnhub** | 40+ year daily OHLC with a documented split-only adjustment flag |
| F | **Twelve Data** | Cheap, with an unusually clear published derived-data definition |
| G | **Alpaca** | Explicit `adjustment=split` parameter and documented consolidated-tape high/low conditions |
| H | **Tiingo** | Very cheap, 30+ year claim; included to test its licence, which turns out to be the deciding attribute |
| I | **Financial Modeling Prep** | Frequently-cited low-cost option with a 30+ year claim |
| J | **Marketstack** | Very cheap tiered API; included to test whether cheap tiers ever carry display rights |
| K | **Alpha Vantage** | Ubiquitous free tier; included to establish whether it is licensable at all |
| L | **Databento** | Institutional-grade, transparent exchange-fee treatment; included as the quality ceiling |
| M | **Nasdaq Data Link / Sharadar** | The conventional survivorship-bias-free answer (mostly R4/R5 territory) |

Providers examined by the parallel effort for R4/R5, and sentiment providers, are treated
in [§6](#6-r6--fear--greed--equivalent-sentiment-sources) and §10 respectively.

> **A note on how some pages were read.** Several vendors (Financial Modeling Prep,
> Finnhub, Marketstack, parts of FRED and AAII) return **HTTP 403** to a plain automated
> fetch. Where noted, those pages were read through a **public rendering proxy**
> (`r.jina.ai`) — a renderer for publicly-accessible pages, **not** a login, paywall or
> access-control bypass. No credentials were used anywhere in this research. Claims read
> that way are tagged **VERIFIED (proxy)** so the reader can weigh them accordingly.

---

## 2. R1 — Historical daily OHLCV

**Question:** accurate, split/dividend-handled daily OHLCV for all S&P 500 constituents,
with enough history to reach **each name's all-time high** — the trendline anchor.

### 2.1 The finding that dominates R1: history depth is a *correctness* constraint, not a nice-to-have

4UR4 anchors every trendline at the ATH **wick** over the full delivered history
([`trendline-specification.md`](trendline-specification.md) §4). If a provider's history
begins *after* a name's true all-time high, the detector does not degrade gracefully — it
silently anchors on the wrong bar and every downstream signal for that name is wrong.
Worse, the affected names are exactly the ones this product cares about: a name whose ATH
is decades old is, by definition, a name in a long descent, which is the population that
generates ATH-anchored descending trendlines at all.

This makes **history start date the first-order selection criterion**, ahead of price.

| Provider | Stated daily-history start / depth | Tag | Source (retrieved 2026-07-26) |
|---|---|---|---|
| **Intrinio** | "**Over 50 years of history**, making it one of the deepest EOD stock price datasets available via API" | **VERIFIED** | <https://intrinio.com/financial-market-data/stock-prices-eod> |
| **Norgate Data** | Plan-gated by history: Silver 10 yrs, Gold 20 yrs, Platinum **back to 1990**, Diamond **back to 1950** | **VERIFIED** | <https://norgatedata.com/stockmarketpackages.php> |
| **Finnhub** | Daily OHLC: Basic 10 yrs, Standard 25 yrs, Professional **40+ yrs** | **VERIFIED (proxy)** | <https://finnhub.io/pricing-stock-api-market-data> |
| Massive | "We offer historical tick-level data for stocks dating back to **2004**." Plan-gated: Basic 2 yrs, Starter 5 yrs, Developer 10 yrs, Advanced/Business "20+ Years Historical Data" | **VERIFIED** | <https://massive.com/knowledge-base/article/how-much-historical-stock-data-does-polygon-have>, <https://massive.com/pricing>, <https://massive.com/business> |
| EODHD | Pricing page: "**30+ years** for US companies". EODHD's own academy article instead says coverage is "11,000+ US tickers from **January 2000**" | **VERIFIED (both), CONTRADICTORY** | <https://eodhd.com/pricing>; <https://eodhd.com/financial-academy/financial-faq/historical-stock-prices-for-delisted-companies> |
| Financial Modeling Prep | Starter 5 yrs, Premium **30 yrs**, Professional **30+ yrs** | **VERIFIED (proxy)** | <https://site.financialmodelingprep.com/pricing-plans> |
| Tiingo | Pricing page: "Historical data: **30+ years**" (all tiers, incl. free) | **VERIFIED** | <https://www.tiingo.com/pricing> |
| Marketstack | Pricing table: Basic 10 yrs, Professional/Business "**15+ years**". Marketstack's own FAQ instead says "up to 30 years" on premium plans | **VERIFIED (proxy), CONTRADICTORY** | <https://marketstack.com/pricing>, <https://marketstack.com/faq> |
| Alpaca | Historical bars "**7+ years**" | **VERIFIED** | <https://alpaca.markets/data> |
| Twelve Data | Not stated on the pricing page | **GAP** | <https://twelvedata.com/pricing> |
| Alpha Vantage | Not stated on the premium page | **GAP** | <https://www.alphavantage.co/premium/> |
| Databento | US equities "Since **2018**"; XNAS.ITCH from **May 2018**; DBEQ.BASIC from **April 2023** | VERIFIED (2018) / **UNVERIFIED** (specific dataset dates, search-sourced) | <https://databento.com/equities> |
| Nasdaq Data Link / Sharadar | Via a reseller listing: "End-of-Day US Stock Prices (**1998**-present)" | **UNVERIFIED** (third-party page, not Nasdaq's own) | <https://www.quantrocket.com/pricing/data/sharadar/> |

**Worked consequence, stated concretely.** Intel (INTC) — a long-lived large-cap — set its
all-time high in **August 2000** at roughly $75.81 (split-adjusted), during the dot-com
peak (**UNVERIFIED**, secondary sources: <https://pro.macrotrends.net/stocks/charts/INTC/intel/stock-price-history>,
<https://www.bitget.com/wiki/intel-stock-price-history>, retrieved 2026-07-26). A provider
whose daily history begins in **2004** cannot see that bar. Fed such a series, 4UR4 would
select a *post-2004* high as `HA`, anchor there, and emit a trendline that is not the
product's defined object at all. The same class of failure applies to any name whose ATH
predates the provider's history start.

**Therefore: Massive's 2004 start is its single serious weakness, and it is a weakness in
exactly the dimension 4UR4 is most sensitive to** — while **Intrinio (50+ yrs), Norgate
(to 1950) and Finnhub (40+ yrs)** clear the bar comfortably. This one attribute is what
reorders the recommendation in §13, because **depth is the only constraint on this list
that cannot be closed by asking a vendor a question or by writing more code.** Every other
gap in this document is closable; a bar that the provider does not hold is not.

> **Not resolved here:** *how many* current S&P 500 names have a pre-2004 ATH. Answering
> that requires point-in-time constituents (R4) plus a long price series — i.e. it is
> partly the parallel effort's question. It is logged in §10 as the highest-value
> follow-up, because it converts "Massive's depth is a risk" into a number.

### 2.2 Adjustment methodology — and whether both raw and adjusted are available

[HD-01](human-decisions.md) fixes the basis: **split-adjusted, dividend-UNadjusted
("as-traded")**, used identically for ATH selection, pivots, fitting and breakout tests.
A provider that offers only *fully adjusted* (split **and** dividend) closes cannot
satisfy HD-01, and a provider that offers only *raw* can satisfy it only if it also
publishes a complete split history (see R3).

| Provider | Adjustment behaviour | Satisfies HD-01? | Tag | Source |
|---|---|---|---|---|
| **Norgate Data** | Four explicit modes: `NONE` (raw), **`CAPITAL` (splits, reverse splits, bonus and rights issues only — no ordinary dividends)**, `CAPITALSPECIAL`, `TOTALRETURN` (default) | **Yes — as a first-class, named series.** The only exact published match found | **VERIFIED** | <https://norgatedata.com/data-content-tables.php> |
| **Massive** | Aggregates take an `adjusted` parameter: "Whether or not the results are adjusted for splits. By default, results are adjusted. Set this to false to get results that are NOT adjusted for splits." No dividend adjustment is applied to bars. | **Yes — directly.** Default output *is* the HD-01 basis; `adjusted=false` gives raw for cross-checking | **VERIFIED** | <https://massive.com/docs/rest/stocks/aggregates/custom-bars> |
| **Alpaca** | `adjustment` parameter takes four values: `raw` (default), **`split`**, `dividend`, `all` | **Yes — directly**, via `adjustment=split` | **VERIFIED** | <https://docs.alpaca.markets/us/docs/about-market-data-api> |
| **Finnhub** | `adjusted` defaults to `false` (raw); `adjusted=true` on daily candles adjusts **for splits but not dividends** | **Yes — apparently directly.** But see the reliability caveat below | **UNVERIFIED** (docs + corroborating issue reports, not a clean primary render) | <https://github.com/finnhubio/Finnhub-API/issues/336> |
| **EODHD** | EOD API returns OHLC "raw — adjusted for neither splits nor dividends"; `adjusted_close` is "adjusted for both splits and dividends"; volume "adjusted for splits". Docs: "If you need OHLC adjusted for splits only, use the Technical API with `function=splitadjusted`." | **Yes — via a second endpoint**, or by self-applying splits to raw OHLC | **VERIFIED** | <https://eodhd.com/financial-apis/api-for-historical-data-and-volumes> |
| **Intrinio** | Raw `open/high/low/close` plus `adj_*` fields defined as "adjusted for **splits and dividends**" — so `adj_*` is **not** the HD-01 basis. But a separate price-adjustments dataset exposes `factor`, `dividend` and **`split_ratio`** independently | **Yes — by self-applying `split_ratio` to raw OHLC.** Not a first-class series; see below | **VERIFIED** | <https://docs.intrinio.com/documentation/web_api/get_security_stock_prices_v2>, <https://docs.intrinio.com/documentation/web_api/get_stock_exchange_price_adjustments_v2> |
| Marketstack | Returns raw OHLCV plus `adj_open/adj_high/adj_low/adj_close/adj_volume`, `split_factor`, `dividend` — but **Marketstack's own FAQ states the `adj_*` methodology is not documented** | **Cannot determine** | **GAP (vendor-acknowledged)** | <https://marketstack.com/faq> |
| Financial Modeling Prep | Search snippets indicate both split-only and split+dividend series exist; primary docs returned HTTP 403 even through the proxy | **Cannot determine** | **GAP** | — |
| Twelve Data | Not documented on any page reached | **Cannot determine** | **GAP** | — |
| Tiingo | Not established (superseded by the licence finding in R7) | **Cannot determine** | **GAP** | — |
| Alpha Vantage | Not established from the pages reached | **Cannot determine** | **GAP** | — |
| Databento | Raw trade/venue data; adjustment is the consumer's problem | Would require self-applied adjustment | PARTIAL | <https://databento.com/equities> |

**Two findings here are worth separating out.**

**(a) Norgate is the exact fit — and it is unusable.** Norgate's `CAPITAL` mode is HD-01
stated in a vendor's own vocabulary: capital reconstructions adjusted, ordinary dividends
not. With history to 1950 for **$787.50/year**, it is on paper the best technical match in
this entire survey. Its EULA disqualifies it outright — see §7.2. This is recorded because
it is genuinely instructive: **the best technical fit and the best commercial fit are
different vendors, and licence, not data, is the binding constraint.**

**(b) Intrinio's `adj_*` fields are a trap, and the trap has a clean workaround.**
`adj_high` is documented as "The highest price over the span of the period, adjusted for
splits **and dividends**" — feeding that to the engine would violate HD-01 and silently
move the ATH, which is exactly the failure HD-01 exists to prevent. But Intrinio also
publishes raw OHLC **and** a separate adjustments dataset carrying `split_ratio` distinctly
from `dividend`. So the HD-01 basis is obtained by **self-applying `split_ratio` only to
raw OHLC** — which is not a workaround at all but the *preferred* posture under §4 and
DI-02/DI-03, because a self-applied adjustment is re-derivable and auditable while a
vendor-applied one must be taken on trust. **The `adj_*` fields must be explicitly banned
in the adapter**, and that ban is an acceptance test (§11).

> **Flagged per the brief — providers whose adjustment methodology I could not determine:**
> **Marketstack** (its own FAQ concedes this), **Financial Modeling Prep** (pages
> unreachable), **Twelve Data**, **Tiingo** and **Alpha Vantage**. Under HD-01 that is
> disqualifying until resolved — not because the data is necessarily wrong, but because
> HD-01 requires a *known, reproducible* basis, and an undetermined basis cannot honestly
> be stamped into `bars.adjustment_policy` (architecture §4).
>
> **Reliability caveat on Finnhub and Alpaca:** for both, public issue reports describe the
> adjustment flag at some point returning identical data regardless of its value
> (finnhubio/Finnhub-API #336; a comparable Alpaca report). Neither could be confirmed
> fixed as of 2026-07-26. **This is precisely why DI-02 requires both series and §11 test 2
> re-derives the adjustment rather than trusting the flag** — a documented parameter that
> silently no-ops is indistinguishable from a correct one until you check.

### 2.3 Wick fidelity — the attribute that quietly decides this

Trendlines anchor on **highs**, not closes ([`trendline-specification.md`](trendline-specification.md)
§3: `y[t] = ln(H[t])`; §4: "the ATH is the **bar high** (the wick), not the close"). A
provider that is accurate on closes but sloppy on highs is unusable here — and daily-high
construction genuinely differs between vendors, because it depends on *which trades are
eligible to update the high*.

**Only two candidates publish a per-trade-condition rule; a third states consolidated-tape
sourcing; the rest are silent.**

**Massive — VERIFIED** (<https://massive.com/knowledge-base/article/how-does-polygon-create-the-open-high-low-close-volume-aggregate-bars>,
retrieved 2026-07-26). Massive determines eligibility from the **Sale Conditions** attached
to each trade, and exposes the rule per condition — each condition carries
`updates_high_low`, `updates_open_close`, `updates_volume` flags. Example given in the
article: condition 2 ("Average Price Trade") is `updates_high_low: false,
updates_open_close: false, updates_volume: true`. Massive states it follows the
**Securities Information Processors' consolidated processing guidelines** rather than
market-centre rules, because it provides "aggregates for the consolidated feed (meaning
trades from all exchanges)", and notes that the SIP/OPRA guidelines "apply primarily to
daily bars" — with a documented deviation for *minute* bars only, where "trades in
extended-hours markets can update OHLC for minute bars".

For 4UR4 that reads: **daily highs are consolidated-tape, condition-eligible intraday
extremes, with a published eligibility rule and no extended-hours deviation at the daily
granularity.** That is exactly the wick semantics §3/§4 require, and it is the strongest
single piece of evidence in this document.

**Alpaca — VERIFIED** (<https://docs.alpaca.markets/us/docs/market-data-faq>, retrieved
2026-07-26). Alpaca distinguishes the **SIP** feed (CTA/UTP consolidated tape, ~100% of
market volume) from the **IEX** feed (~2.5% of volume), and documents condition-level
behaviour — e.g. condition `P` ("Prior Reference Price") and condition `G` ("Bunched Sold
Trade") update high/low on **daily** bars but explicitly not on minute bars. **A notable
sub-finding:** Alpaca's docs state that for historical queries where `end` is at least 15
minutes old, SIP (consolidated) data is available **without a paid subscription** — so
consolidated-tape *daily* bars are reachable on the free tier. That makes Alpaca an
attractive **independent cross-check source** for the §11 wick-fidelity test, even though
its 7-year history rules it out as the primary.

| Provider | Wick (high/low) construction | Tag |
|---|---|---|
| **Massive** | Consolidated (all exchanges), per-condition `updates_high_low` rule published | **VERIFIED** |
| **Alpaca** | SIP consolidated tape (~100% of volume) vs IEX (~2.5%); condition-level daily-bar high/low rules published | **VERIFIED** |
| **Norgate Data** | "Price & Volume reflects consolidated tape trading from all trading venues and ECNs… The Close is the price determined by the closing auction on the listing exchange" — but this wording was read in the **Canadian**-market section; US-specific wording not directly confirmed | **PARTIAL** |
| **Intrinio** | Documents access to CTA Tape A/B and UTP Tape C SIP feeds and `UpdateHighLowConsolidated` vs `UpdateHighLowMarketCenter` condition handling in its real-time SDK — but **the EOD price endpoint docs say nothing about high/low construction**, and which tier carries consolidated daily high/low is unconfirmed | **PARTIAL — the blocking question for the recommended provider** |
| **Finnhub** | Sourcing named ("directly from the exchanges, ActivFinancial, EDI, QuoteMedia") but no statement that daily high/low are consolidated extremes | **PARTIAL** |
| **Marketstack** | US data is "licensed and sourced from **Tiingo, Inc.**"; whether Tiingo's historical daily high/low is consolidated or IEX-derived is undetermined | **GAP — with an inherited-risk lead** |
| EODHD | Not documented on any page reached | **GAP** |
| Twelve Data | Not documented on any page reached | **GAP** |
| Tiingo | Not documented on any page reached | **GAP** |
| Financial Modeling Prep | Pages unreachable (HTTP 403) | **GAP** |
| Alpha Vantage | Not documented on any page reached | **GAP** |
| Databento | Venue-level feeds; DBEQ.BASIC is a *partial-venue* blend, so its extremes are not consolidated-tape extremes by construction | PARTIAL — <https://databento.com/equities> |

**The Marketstack finding generalises into a rule worth carrying forward:** Marketstack
resells Tiingo. A vendor's wick fidelity is only ever as good as its *upstream's*, and
several cheap APIs are resellers. **`data/` must record the upstream, not just the
vendor** — otherwise two "independent" sources in a cross-check can silently be the same
data, and the check proves nothing. This is added to DI-06.

**The Databento sub-finding is worth stating plainly** because it generalises: a feed built
from a *subset* of venues cannot reproduce the consolidated high if the true extreme
printed on an excluded venue. Any "cheap real-time" feed that is a venue blend rather than
a SIP-derived consolidation carries this defect, and it is invisible in close-price
comparisons — which is precisely how a wick-sensitive product gets silently broken.

### 2.4 Correction / restatement policy

**Massive — VERIFIED-adjacent** (<https://massive.com/blog/aggregate-bar-delays>,
<https://polygon.io/knowledge-base/article/why-am-i-receiving-a-late-aggregate-bar-through-polygons-websockets>,
retrieved 2026-07-26): daily bars are continuously recalculated as late trades arrive;
trades arriving after a 15-minute buffer are incorporated at end of day; corrected bars are
rebroadcast rather than dropped. (Tagged **UNVERIFIED** on exact wording — retrieved via
search summary of these pages rather than a clean render.)

**This is an architectural requirement, not a footnote.** If daily bars are restated, then
"the bar as of the scan that produced the signal" and "the bar today" can differ, and
[HD-12](human-decisions.md)'s causal/as-of-time guarantee is only meaningful if the data
layer records the **vintage** it read. §8 turns this into an interface requirement.

Other candidates: **GAP** — no published correction policy was found.

---

## 3. R2 — Live / delayed market data

**Question:** is EOD sufficient for the daily-batch MVP, and what would delayed vs
real-time cost later?

### 3.1 The single most important cost fact in this document

> "Exchanges require a license for any intraday or delayed data. Anything **T+1** (24 hours
> and earlier) doesn't require a license."
> — Databento, *Part 2: Understanding exchange license fees*,
> <https://databento.com/blog/understanding-exchange-fees>, retrieved 2026-07-26. **VERIFIED**

The documented default MVP cadence is **daily, end-of-day aligned** (architecture §3.3;
research instrument's decision protocol). If 4UR4 consumes bars at **T+1** — i.e. runs the
batch on yesterday's completed session rather than reaching for today's 15-minute-delayed
tape — then **US exchange entitlement fees do not attach at all**. Every recurring
per-subscriber display fee, non-display fee and admin fee in §7.3 is avoided by a cadence
decision that has already been made for unrelated (correctness) reasons.

Corroborating primary evidence: Massive attaches "**Additional exchange fees apply to these
products**" specifically to its real-time and delayed *feed expansions* (Full Market,
Nasdaq Basic, Cboe EDGX, Full Market Delayed, IEX), and **not** to the base Stocks Business
plan (<https://massive.com/business>, retrieved 2026-07-26, **VERIFIED**).

**Conclusion for R2: EOD is sufficient, and it is also the configuration that removes the
category of cost that usually dominates market-data budgets.** The MVP cadence should be
stated as *T+1 completed-session bars*, not merely "daily", because the T+1 boundary is
what carries the licensing consequence.

### 3.2 EOD availability timing

| Provider | Documented EOD timing | Tag | Source |
|---|---|---|---|
| **Intrinio** | Unconfirmed EOD prices begin ~**4:45 pm ET**, finish loading ~**5:00 pm ET**; **confirmed/official EOD prices arrive 8:00–9:00 pm ET** | **VERIFIED (proxy)** | <https://help.intrinio.com/eod-market-data-faqs> |
| EODHD | "Major US exchanges, NYSE and NASDAQ, are updated **within 15 minutes after the market closes**." Mutual funds, PINK, OTCBB and indices "update only the next morning, starting at 3-4 am EST and usually ending at 5-6 am EST." | **VERIFIED** | <https://eodhd.com/financial-apis/api-for-historical-data-and-volumes> |
| Massive | Daily bar is continuously updated; late trades after the 15-minute buffer are folded in at end of day | **UNVERIFIED** (search summary of the cited KB/blog pages) | <https://massive.com/blog/aggregate-bar-delays> |
| Norgate, Finnhub, Alpaca, Marketstack, FMP, Twelve Data, Tiingo, Alpha Vantage | Not established on any page reached | **GAP** | — |

**Intrinio's distinction between "unconfirmed" and "confirmed" EOD prices is the single most
operationally useful timing fact found**, and it should drive the batch schedule directly: a
scan that runs before ~8 pm ET is reading provisional bars. Combined with §2.4's restatement
finding, this is the concrete reason DI-04 (`as_of`) exists — "the bar" is not a single
value until the confirmed load lands.

**Practical reading:** a batch scheduled comfortably after the session (e.g. next morning)
gets a settled bar from either vendor and stays on the fee-free side of the T+1 line. A
batch that runs at 16:05 ET is reaching for a bar that is still being restated — which
costs correctness *and* potentially crosses into licensed-intraday territory.

### 3.3 What intraday would cost later — see §7.3

Cost scenarios for delayed and real-time are in [§7.3](#73-scenario-c--if-intraday-is-ever-wanted-not-mvp),
because they are inseparable from the exchange-entitlement structure.

---

## 4. R3 — Stock splits & corporate actions

**Question:** can 4UR4 adjust history correctly and *reproducibly*?

Under HD-01 the basis is split-adjusted / dividend-unadjusted. There are two viable
mechanisms, and 4UR4 should prefer the one that is **re-derivable**:

- **Provider-applied:** consume the vendor's split-adjusted series directly.
- **Self-applied:** consume raw OHLC plus a complete split history and apply the
  adjustment in `data/`.

Self-application is more work but is the only mechanism that makes the adjustment
*auditable* — 4UR4 can re-derive the adjusted series from (raw bars + split events) and
prove it. Given this repository's stated defect class, **the recommended posture is:
consume the provider's split-adjusted series as primary, and hold raw + split events so
the adjustment can be independently re-derived and diffed.** Both recommended providers
support that.

| Attribute | Massive | EODHD |
|---|---|---|
| Splits endpoint | `GET /stocks/v1/splits` — returns `execution_date` ("Date when the stock split takes effect. The adjustment is applied overnight."), `split_from`, `split_to`, `ticker` | Splits & dividends API returns split events with dates and ratios |
| Split history depth | "Records date back to **October 25, 1978**"; full history on Starter/Developer/Advanced/Business, 2 years on Basic | "over 30 years of comprehensive data" for paid users; free tier limited to ~1 year of dividend history |
| Dividends | Separate corporate-actions dataset; **never** applied to bars | Ex-date and value for nearly all symbols; declaration/record/payment date, value, **unadjusted value**, currency for major US/EU names |
| Symbol changes | Ticker Events endpoint — "a timeline of key events associated with a given ticker, CUSIP, or Composite FIGI", highlighting "ticker changes, such as symbol renaming or rebranding"; "Currently `ticker_change` is the only supported `event_type`" | Not established from pages reached — **GAP** |
| Spin-offs / mergers | Not established as discrete event types — **GAP** | Not established — **GAP** |
| Tag | **VERIFIED** — <https://massive.com/docs/rest/stocks/corporate-actions/splits>, <https://massive.com/docs/rest/stocks/corporate-actions/ticker-events> | **VERIFIED** — <https://eodhd.com/financial-apis/api-splits-dividends> |

**A notable asymmetry.** Massive's **split history reaches back to 1978** even though its
**price bars start in 2004**. That is useful: it means the corporate-actions spine is deep
enough to adjust a *longer* price series obtained elsewhere — which is what makes the
composed-provider design in §9 mechanically feasible rather than hypothetical.

**Spin-offs and mergers are a GAP for both.** Neither provider's documentation, as read,
enumerates spin-off or merger event types with adjustment factors. For an ATH-anchored
detector a mishandled spin-off is a *price-affecting* event that behaves like an
unadjusted split — it can inject a false ATH. This must be an explicit question to any
provider before HD-06 is taken, and an explicit data-quality check in `data/` regardless
(architecture §6.1 already names "split-adjustment sanity" as a check; **spin-off sanity
should be added to it**).

**Evidence the instrument asks for that I could not produce:** the worked example through a
known split and a known symbol change, and the confirmation that a post-adjustment ATH
matches expectations, both require live pulls — blocked, see §0. Specified as an acceptance
test in §11 instead.

---

## 5. (R4 / R5 — not in scope here)

Point-in-time S&P 500 constituents and delisted price history are being researched in
parallel and are **not** answered in this document. Two observations surfaced incidentally
and are handed over rather than developed:

- EODHD publishes delisted-symbol documentation and states that delisted tickers' EOD
  prices, fundamentals, dividends and splits remain retrievable, with availability
  depending on when the company was delisted
  (<https://eodhd.com/financial-apis/delisted-stock-companies-data-2>,
  <https://eodhd.com/financial-academy/financial-faq/historical-stock-prices-for-delisted-companies>,
  retrieved 2026-07-26). **UNVERIFIED** in detail — flagged to R5.
- A third-party reseller listing describes Sharadar's bundle as including "S&P 500
  Constituents (1957-present)" (<https://www.quantrocket.com/pricing/data/sharadar/>,
  retrieved 2026-07-26). **UNVERIFIED** — flagged to R4.

Both bear on [HD-07](human-decisions.md), which approved the *need* (not the spend).

---

## 6. R6 — Fear & Greed / equivalent sentiment sources

**Question:** what sources provide a Fear & Greed composite, and could 4UR4 *reconstruct*
an approximation from data it already licenses?

Context: [HD-08](human-decisions.md) keeps sentiment **out of the confidence score** until
a backtest plus human approval; [HD-09](human-decisions.md) forbids displaying or
redistributing any third-party F&G index until rights are verified, and **prefers a
proprietary 4UR4 score where practical**. This section therefore answers *availability and
licensing only*.

### 6.1 The headline composite is not licensable as found

**CNN Business Fear & Greed Index.** There is **no official public API**. Every
third-party library either scrapes CNN's page or calls an **undocumented internal
endpoint** (`production.dataviz.cnn.io/index/fearandgreed/graphdata/`) discovered by
inspecting CNN's own chart widget — not published by CNN as a developer product; the most
prominent repository self-labels as "**Unofficial** CNN Fear and Greed Index". That
endpoint's own history reportedly begins around 2020-09-18; earlier history exists only as
third-party archival reconstruction. **UNVERIFIED** on the endpoint history date;
**VERIFIED** that no official API or licensing route was found.

CNN's commercial terms, **VERIFIED** at <https://commercial.cnn.com/terms-of-use/>
(retrieved 2026-07-26):

> "Such material may not be modified, copied, reproduced, republished, uploaded, posted,
> transmitted, or distributed in any way, including by e-mail or other electronic means."

> "use of the materials for any purpose other than personal, non-commercial use is a
> violation of the copyrights, trademarks, and other proprietary rights, and is prohibited."

CNN's main `www.cnn.com` terms pages returned **HTTP 451 (Unavailable For Legal Reasons)**
to direct fetch, so CNN's primary consumer ToU text could not be read — recorded as a
**GAP**, not filled from memory.

**Assessment: RED.** Displaying CNN's number, or a derivative labelled as CNN-sourced, to
paying subscribers has no documented licence, depends on an undocumented endpoint, and runs
against CNN's own published commercial terms. This is consistent with HD-09 and, in the
absence of any licensing contact for the index, effectively closes the option.

**Methodology (published, and reproducible):** seven equally-weighted sub-indicators on a
0–100 scale — market momentum (S&P 500 vs its 125-day MA), stock price strength (NYSE
52-week highs vs lows), stock price breadth (advancing vs declining volume), put/call ratio,
junk-bond demand (high-yield vs investment-grade spread), market volatility (VIX vs its
50-day MA), safe-haven demand (20-day stock vs Treasury returns). **UNVERIFIED** in the
sense that this was corroborated across secondary sources rather than read from a single
CNN methodology page.

### 6.2 The reconstruction path, input by input — this is where the licensing bites

HD-09 prefers a 4UR4-reconstructed score. That is achievable **only if each input is itself
redistribution-clear**, and the research shows that is not automatic:

| Input | Candidate source | Licence posture | Tag |
|---|---|---|---|
| Market momentum (index vs 125-day MA) | Computable from 4UR4's own licensed equity bars | Clean, if the OHLCV licence permits derived display (see R7) | Derived from §7 |
| Breadth (advance/decline, % above MA) | **Computable from 4UR4's own S&P 500 universe bars** | Clean — no new vendor needed | Analysis |
| Volatility (VIX) | Cboe | Cboe's terms bar display and derivative-index creation without prior written consent — see quote below | **VERIFIED** |
| Put/call ratio | Cboe free CSVs (`cdn.cboe.com/resources/options/volume_and_call_put_ratios/…`) | Free to download, "provided for informational purposes only", explicitly "subject to the Terms and Conditions of Cboe Websites" — i.e. the same restriction | **VERIFIED** |
| Junk-bond demand (credit spreads) | FRED (e.g. ICE BofA HY OAS) | FRED disclaims authority over third-party-owned series — see quote below | **VERIFIED** |
| Safe-haven demand (stocks vs Treasuries) | Computable from equity bars + a Treasury series | Depends on the Treasury series' own licence | Analysis |

**Cboe**, <https://www.cboe.com/terms/>, retrieved 2026-07-26 — **VERIFIED**:

> "[You may not] copy, reproduce, alter, store either in hard copy or in an electronic
> retrieval system, license, transmit, **display**, broadcast, **create a derivative work
> (for example, a financial product, service or index) from**, use to verify or correct
> other data or information, publish, rent, sublicense, distribute, or otherwise use in
> whole or in part in any other manner the Materials without Cboe's prior written consent…"

This clause reaches *both* verbs 4UR4 cares about — **display** and **derivative index** —
so a VIX-derived sentiment feature shown to subscribers needs a Cboe licence. Cboe's
licensing route is a quote request (`marketdata@cboe.com`), with no public self-serve price
(<https://www.cboe.com/us/indices/accessing-index-data>, retrieved 2026-07-26,
**VERIFIED**). Historical daily VIX CSVs back to 1990 are freely downloadable but carry an
informational-use disclaimer, not a commercial-display grant
(<https://www.cboe.com/tradable_products/vix/vix_historical_data/>, **VERIFIED**).

**FRED**, <https://fred.stlouisfed.org/docs/api/terms_of_use.html>, retrieved 2026-07-26 —
**VERIFIED** (via a rendered fetch; direct fetch returned 403):

> "Data series available through the FRED® API[,] may be owned by third parties and subject
> to copyright restrictions."

> "You are solely responsible for complying with any requirements or restrictions imposed
> on usage of the data series by their respective owners… contact the data owner to obtain
> permission. The Federal Reserve Bank of St. Louis cannot give you such permission."

Required attribution if the API is used: "This product uses the FRED® API but is not
endorsed or certified by the Federal Reserve Bank of St. Louis."

**The non-obvious trap, stated explicitly:** pulling a junk-bond-spread series *via FRED*
does **not** clear it for commercial display, because the ICE BofA-branded series are
third-party-owned and FRED says so in terms. Government-produced series are a different
case. **The specific ICE Data Indices redistribution terms were not verified** — recorded
as a **GAP** in §10.

### 6.3 Other sources examined

| Source | Finding | Tag |
|---|---|---|
| **SentimenTrader** | Sells proprietary "Fear & Greed Model" / "Panic-Euphoria Model" indicators. Subscriptions $59–$99/mo; separate **Indicator API from ~$300/year for 10 indicators, +$30/year per additional**; Enterprise API custom, min. 5 seats. **Its resale/end-customer-display clause is not published** — needs a sales conversation | **VERIFIED** (pricing) / **GAP** (redistribution terms) — <https://sentimentrader.com/pricing>, <https://sentimentrader.com/indicator-api> |
| **Alternative.me** crypto F&G | "**Commercial use is allowed as long as the attribution is given right next to the display of the data.**" — the cleanest display grant found anywhere in this research. **But it is a crypto index**, not an S&P 500 composite, and is not a valid equity-sentiment substitute | **VERIFIED** — <https://alternative.me/crypto/fear-and-greed-index/> |
| **AAII Investor Sentiment Survey** | No public API found. Site ToS: "No part of the contents of the website or newsletter may be copied or forwarded to anyone else…". No licence grant of any kind located | **VERIFIED** (ToS quote) / **GAP** (survey-specific terms) — <https://www.aaii.com/privacy/tos> |
| **FearGreedChart.com** | Free no-auth JSON/CSV API with its own 5-component composite; "Attribution appreciated… but not required"; "as-is with no uptime guarantee" | **VERIFIED** — <https://feargreedchart.com/api-docs> |

### 6.4 R6 conclusion

**HD-09's preference for a 4UR4-reconstructed score is the correct call, and the research
strengthens it — but with one correction to the naive version of that plan.** The
reconstruction is only licence-clean if it is built from inputs 4UR4 *already licenses*.
Two of the seven CNN sub-indicators (**volatility/VIX** and **put/call ratio**) come from
Cboe and are **not** free for commercial display despite being free to download. Two more
(momentum, breadth) and arguably a third (safe-haven demand, given a Treasury series) are
computable **entirely from 4UR4's own S&P 500 universe bars**, with no new vendor and no new
licence.

**Recommended R6 posture:** build the v1 sentiment context from the **breadth / momentum /
dispersion family computable from 4UR4's own licensed equity bars only**, and treat VIX,
put/call and credit spreads as *deferred inputs* requiring their own licence decisions.
This keeps sentiment on the redistribution-safe side of R7 without any additional recurring
spend, and it is fully consistent with HD-08 (sentiment stays out of the score until
backtested and approved) and HD-09.

---

## 7. R7 — Commercial redistribution rights **(highest risk; treated first-class)**

**Question:** does the licence permit commercial use and redistribution/display to end
users — including paying SaaS subscribers — or only internal/personal use?

### 7.1 The distinction that decides everything: three different things, priced differently

Vendors do not price "data". They price **use**. Three uses must be separated, because a
provider that is cheap for one is often unavailable for another:

| Use | What it means for 4UR4 | Typical vendor term |
|---|---|---|
| **1. Internal / non-display** | 4UR4 pulls bars, computes trendlines, nobody outside the company sees any vendor value | "internal use", "non-display use" |
| **2. Derived-signal display** | 4UR4 shows *its own* output — "confirmed breakout, confidence 72, line slope −0.4%/bar" — with no vendor price series visible | "derived data" — sometimes free, sometimes needs written approval, sometimes prohibited |
| **3. Raw-data display / redistribution** | 4UR4 renders a **price chart with the trendline overlaid** — which shows the vendor's highs, lows and closes to a paying subscriber | "external display", "redistribution", "Edge Users" |

**The load-bearing product judgement:** 4UR4's core value is *explainability* — the user
sees **why** a breakout is trusted (vision; architecture §3.5). An explainable breakout
product that cannot draw the chart is a materially different, weaker product. So the honest
planning assumption is that **4UR4 needs category 3, not merely category 2**. Every cheap
tier surveyed below is category-1-only, and that — not price — is what removes it.

A second judgement worth recording: **category 2 is not automatically safe either.** Two
vendors reached opposite conclusions about derived data, and one of them requires *written
approval before a derived value may even be created*.

### 7.2 Per-provider licence findings, quoted

All quotes retrieved **2026-07-26**.

#### A0. Intrinio — **GREEN for category 3, and the only vendor that prices it openly at the low end**

*Pricing page* — <https://intrinio.com/pricing> — **VERIFIED**. Intrinio states the licence
class **as a tier attribute on the price list itself**, which no other candidate does:

| Tier | Price | Seats | Licence attribute, quoted |
|---|---|---|---|
| Individual | $150/mo | "1 seat license" | "**No redistribution or external display**" |
| Startup | $333/mo to start, billed quarterly — "6 mo at $333, 6 mo at $666, $999 thereafter" | "Business-wide license" | "**Display & Commercial Use**" |
| Enterprise | $1,250/mo minimum, custom terms | Business-wide | Inherits Display & Commercial Use; adds custom datasets, SLA, onboarding |

*Terms* — <https://docs.intrinio.com/terms> and <https://intrinio.com/guides/starter-plan>
— **VERIFIED (proxy)**. The default (individual/starter) grant is internal-use-only and
explicit about it:

> "you may access and use the Services and Intrinio Data **solely for your own internal
> purposes**"

> "you may not… use any Intrinio Data for any commercial purpose, including in connection
> with any commercial product, service, application, website, software platform, **SaaS
> offering**"

> "you shall not… **Display, publish, distribute, transmit, or otherwise make any Intrinio
> Data available to any third party**, including through any website, application,
> dashboard, API, portal, report."

> Starter Plan: "can be licensed for Individual, Non-Business, **Non-Display**, and
> **Non-Redistribution** Use, only."

And a derived-data clause that is unusually modern and unusually relevant:

> "If an AI system can reproduce, approximate, or reveal Intrinio data in a way that a user
> could infer or reconstruct the original data, it is treated as **original data
> redistribution, not purely derived output**."

**Read together, this is coherent and favourable:** the restrictive quotes govern the
Individual/Starter tiers; the **Startup tier explicitly buys out of them** with a
business-wide "Display & Commercial Use" licence. The derived-data clause draws the same
reconstruction line as Twelve Data's, and 4UR4 sits on the safe side of it — a confidence
score and a breakout flag do not let a user reconstruct the underlying bars. The *chart*
does show bars, which is why the display right in the Startup tier is the operative
permission rather than the derived-data clause.

**Gap:** rate limits (calls/min or /day) are **not published** on the pricing page
(**GAP**), and third-party aggregators quote tier names and prices that do not match
Intrinio's own page — those were disregarded rather than reported as fact.

#### A. Massive (formerly Polygon.io) — **GREEN for category 3**, with one clause to clarify

*Individuals ToS* — <https://massive.com/legal/individuals-terms-of-service> — **VERIFIED**:

> §2: "non-exclusive, non-transferable, non-assignable, worldwide, limited right to access
> and use the Services… **solely for your own personal, non-commercial, and non-business
> purposes**"

> "**If you are using the Services for business or commercial purposes, you may not use any
> of the Services labeled for individual or personal use.**"

The pricing page reinforces this: all individual tiers are marked "**Individual use only**"
(<https://massive.com/pricing>, **VERIFIED**). Knowledge base: "**Any user who wishes to
redistribute Massive's market data must sign up for one of our business products.**"
(<https://massive.com/knowledge-base/article/how-can-i-redistribute-massives-market-data>,
**VERIFIED**.)

*Businesses ToS* — <https://massive.com/legal/businesses-terms-of-service> — **VERIFIED**.
The prohibition is on making Information available:

> "…to anyone other than **Customer, its Authorized Users, or its Edge Users**"

and **Edge Users** are defined as:

> "individuals or entities that are **users of Customer's products and services**"

with the grant covering use of the Information "solely for its use in **websites or
software applications owned or licensed by Customer**".

**This is the finding that makes Massive viable.** The business licence is written for
exactly 4UR4's shape: a SaaS whose subscribers see vendor data inside 4UR4's own
application. No other candidate's *published* terms name this case affirmatively.

**But one clause must be clarified before HD-06 is taken.** The same ToS prohibits:

> "use the Information to **create derivative works** (including, without limitation, any
> index, indicative value, net asset value, investment product, financial contract,
> (including, without limitation, contracts for difference or spread betting), settlement
> value or investment strategy) based on the Information **unless licensed to do so**"

The enumerated examples are all *tradeable/valuation* constructs — an index, an NAV, a
settlement value, an investment strategy. A **confidence score describing the quality of a
chart pattern** is plausibly outside that list. But 4UR4's own vision positions the score
as decision-support, and "investment strategy" is a broad phrase. **This is the single
open legal question on the recommended provider, and it should be put to Massive in
writing before any commitment.** It is not a reason to reject Massive; it is a reason not
to treat this document as the end of diligence.

#### B. EODHD — **AMBER**: cheapest legitimate internal path; display tier not explicitly documented

*Terms* — <https://eodhd.com/financial-apis/terms-conditions> — **VERIFIED**:

> Non-Professional User: "An individual who views or uses EOD Historical Data Information
> **solely in a personal capacity for their own personal investment activities**."

> Non-Professional Users are prohibited from: "**Selling, reselling, retransmitting,
> redistributing, displaying, or granting access to** the Information or Services."

> Professional Users may "**request prior written approval** from EOD Historical Data
> representatives to sell, resell, retransmit, redistribute, display, or grant access to
> EOD Historical Data Information."

> Storage: "EOD Historical Data Information may be stored on the subscriber's premises
> during the active subscription period. Upon termination or expiration of the
> subscription, the subscriber is required to **delete all copies of the data** in their
> possession within one (1) month."

*Commercial pricing* — <https://eodhd.com/commercial-pricing> — **VERIFIED**. The
**Internal Use** plan ($399/mo) states plainly:

> "the data is restricted to being used **solely within your company**. **Displaying the
> data or sharing it with individuals outside your company is not permissible.**"

The **Enterprise** plan ($2,499/mo) adds unlimited calls, bulk retrieval and a "**Data
Services Agreement**" — but **the page does not state that Enterprise grants external
display**. Combined with the ToS requiring *prior written approval* for redistribution,
the fair reading is: **external display at EODHD is a negotiated term inside the Data
Services Agreement, not a published entitlement.** Recorded as a **GAP** to be closed with
EODHD sales before EODHD could be ranked first.

EODHD's own documentation is unusually candid on the general point, which is worth quoting
because it states 4UR4's risk better than most vendor pages do:
"if you're building a product, displaying data to end users, or using data within a
business application, you need a commercial license" and "API access does not equal
redistribution rights" (<https://eodhd.com/financial-apis/commercial-vs-personal-license-use>,
<https://eodhd.com/financial-academy/financial-faq/best-market-data-apis-for-product-teams-in-2026-a-practical-buyers-guide>,
**UNVERIFIED** on exact wording — retrieved via search summary of EODHD pages).

#### C. Twelve Data — **AMBER**: the clearest *derived-data* grant found; external display is an add-on

*Terms* — <https://twelvedata.com/terms> — **VERIFIED**:

> "**Redistribute or provide external display of Data only if and as expressly authorized
> by a Redistribution Rights Add-On or separate written agreement**"

> "**Non-Display Use** means any use of Data that does not involve displaying the Data to
> natural persons."

> "**Internal Use** means use solely for Customer's internal business purposes and not for
> redistribution or external commercial purposes."

> "**Derived Data** means data created by Customer from the Data, **provided such data
> cannot be reverse-engineered to arrive at the underlying Data**." — and the customer
> retains rights to compliant derived data.

> Prohibited: "Store or cache Data beyond permitted timeframes specified in the
> Documentation"; "**Use Free Tier data for commercial purposes**". Deletion within 30 days
> of termination.

**This is the most useful licence text in the whole survey**, because it is the only one
that draws 4UR4's own category-2/category-3 line explicitly. Under it, a **confidence score
and a breakout flag are clean derived data** (they cannot be reverse-engineered back to the
bars), while **drawing the price chart is external display** and needs the add-on. The
add-on's price is **not published** (`twelvedata.com/enterprise` returned HTTP 404 on
2026-07-26) — **GAP**.

Pricing (<https://twelvedata.com/pricing>, **VERIFIED**): Basic free "8 API (800 a day)",
"Internal non-display usage"; **Grow $29/mo** ("Internal display data access"); **Pro
$99/mo**; **Ultra $329/mo** with a 99.95% SLA. The page frames plans as for "personal,
internal, and non-commercial purposes".

Twelve Data is blocked from a higher ranking not by its licence but by §2.2 and §2.3: its
**adjustment methodology and wick construction are undocumented**, which HD-01 cannot
accept.

#### D. Tiingo — **RED for this product**, on the derived-data clause specifically

*Terms* — <https://app.tiingo.com/tos/> — **VERIFIED**:

> "**All data via the API is for internal consumption only.**"

> "Redistribution is only available upon special request and permission, and comes with
> additional fees."

> "**Data independently created by you through the transformation, analysis, or processing
> of Tiingo Data… may be created or retained only if Company has expressly approved such
> creation and retention in writing.**"

> "Tiingo Data may be stored locally on systems owned or controlled by you **only while
> your applicable subscription remains active**."

> "you shall not license, sell, rent, lease, transfer, assign, reproduce, distribute, host
> or otherwise commercially exploit Company Properties."

> "if you are representing an organization or business, you must sign up for a **Commercial
> plan**."

Attribution required on any permitted redistribution: "Data sourced by Tiingo" with a link.

**Why this is disqualifying rather than merely restrictive.** 4UR4 *is* a
transformation-and-analysis product: trendlines, breakouts and confidence scores are
nothing but derived data. Tiingo's clause makes the **creation and retention** of derived
data contingent on prior **written** approval — not just its display. A licence under which
computing the product's core artefact is itself gated is the wrong foundation, regardless
of the $30/mo price. Tiingo's pricing page reinforces the point: both listed tiers are
"Internal Use Only" — "you may only use the data for your own personal use and you may not
display or share the data with another person or organization"
(<https://www.tiingo.com/pricing>, **VERIFIED**).

A search summary suggested Tiingo offers "Display Redistribution" plans around $250–$500/mo;
**this could not be confirmed on any Tiingo page I read and is recorded as UNVERIFIED — do
not rely on it.**

#### E. Alpha Vantage — **RED**: personal, non-commercial licence by default

*Terms of Service* (PDF), <https://www.alphavantage.co/terms_of_service/> — **VERIFIED**
(text extracted from the PDF):

> §2(a): Alpha Vantage grants the right to install, use, access, display and run the
> software "…for **personal, non-commercial use**, unless you and Alpha Vantage have agreed
> otherwise **in writing**…"

> Usage falls under "Professional" if, among other criteria: "You plan to use or provide
> information accessed through the Alpha Vantage Platform as part of **any type of
> commercial activity that allows individuals or entities other than User to access
> information directly or indirectly**, even if the scope of such activity falls outside of
> the securities industry."

> "If you are interested in using the Alpha Vantage Platform for commercial purposes,
> please contact us at: premium@alphavantage.co"

The premium tiers ($49.99–$249.99/mo, <https://www.alphavantage.co/premium/>, **VERIFIED**)
are described in terms of **rate limits only** — the pages reached contain **no statement
that a premium subscription conveys commercial or redistribution rights**. On the text
available, a commercial licence is a separate written agreement of unpublished price.
Combined with the §2.2 adjustment GAP, Alpha Vantage is not a candidate.

#### E2. Norgate Data — **RED**: the perfect data, on a licence that forbids the product

*EULA* — <https://norgatedata.com/subscribe/eula.php> — **VERIFIED**:

> Clause 8: "The Licensee will not… use the Data for **any other commercial purpose**."

> Clause 8: "The Licensee will not **redistribute the Data in any way or form** except where
> express permission has been sought and obtained to publish limited extracts from it."

> "The Licensee may use the Data for a **personal purpose** such as investment or trading."

> "'**Derived Data**' means data that is wholly or partially derived from Data but cannot be
> transformed back to the original form."

> Clause 21: "If a Licensee's subscription lapses, the Licensee must **delete all copies of
> the Data, including Derived Data**, related to that subscription."

> Clause 2: "The Licensee may make a copy of the Database for backup purposes."

**This is the sharpest lesson in the survey.** Norgate has the only first-class
split-only-adjusted series found anywhere (`CAPITAL`), consolidated-tape sourcing, an
explicit corrections policy, and history to 1950 — for **$787.50 per year**, roughly 3% of
the recommended provider's cost. And it is **unusable**: the EULA grants personal use,
forbids other commercial purposes, forbids redistribution, and — via clause 21 — requires
deletion of **derived data** on lapse, which would extend to 4UR4's own computed trendlines
and scores. No published path to an external-display licence exists.

**Norgate is therefore excluded, and the exclusion is on licence alone.** It is recorded in
full because it is the clearest possible demonstration of R7's thesis: *"free to fetch" —
or even "cheap to buy" — is not "free to show", and the cheapest technically-correct
option can be the one you may not use.*

#### E3. Finnhub — **RED by default**; commercial licensing is bespoke

*Terms of Service* — <https://finnhub.io/terms-of-service> — **VERIFIED (proxy)**:

> "**All plan listed on Finnhub website is strictly for personal use unless explicitly
> stated otherwise.**"

> "You hereby agree to **not redistribute or share access to data or derived results from
> the data** obtained from Finnhub with anyone or any 3rd party without written approval
> from Finnhub."

> "All data must be deleted should your subscription to that data ends."

> "**Personal plan can't be used by any business even internally without a written
> approval.**"

Finnhub is attractive on the two hardest technical attributes — **40+ years of daily OHLC**
at $199.99/mo and a documented **split-only** adjustment flag — but its published terms bar
even *internal business use* without written approval, and explicitly extend the
redistribution ban to "**derived results from the data**". That phrase reaches 4UR4's
scores, not merely its charts. Commercial licensing is handled bespoke via sales; no price
is published (**GAP**).

Also noted: Finnhub publishes two pricing pages whose free-tier OHLC entitlements do not
reconcile (<https://finnhub.io/pricing> vs
<https://finnhub.io/pricing-stock-api-market-data>). Flagged rather than resolved.

#### E4. Alpaca — licensing not verifiable at the primary document

Alpaca's market-data terms are PDFs that incorporate third-party exchange agreements by
reference (the **NASDAQ OMX Global Subscriber Agreement** / **Agreement for Market Data
Display Services**). Those documents were **not read directly**, so no verbatim licence
quote is offered. **UNVERIFIED — GAP.** Alpaca is in any case ruled out as the primary by
its 7-year history (§2.1); it is retained in §11 only as a free, consolidated-tape
**cross-check** source, a use that is itself subject to the same unverified terms and must
be cleared before use.

#### E5. Marketstack — cheapest published *hint* of display rights, weakest verification

Marketstack's legal pages redirect to its parent (APILayer / Idera). A search-snippet
summary of those terms states that a customer "**is permitted to receive, process, and
display Marketstack API data and services to individual end-users of your application(s)**",
provided end users do not store or redistribute it. **However, when the actual agreement
pages were fetched, the fetched document body did not contain that clause.**

**UNVERIFIED — and flagged as the weakest licensing finding in this document.** It is
recorded because a cheap tier with genuine display rights would be commercially
significant if true; it must not be relied on without reading the executed agreement. Note
also that Marketstack resells Tiingo (§2.3), whose own terms are among the most restrictive
surveyed — an inherited-rights question that would need answering regardless.

#### E6. Financial Modeling Prep — could not be verified at all

Every FMP legal page (terms of service, acceptable data use policy) returned **HTTP 403**,
including through the rendering proxy. Search snippets indicate that display to third
parties requires a separate "**Data Display and Licensing Agreement**", and that the
default grant is "a limited, revocable, non-transferable, non-sublicensable, non-exclusive
license to access the Services and view content". **UNVERIFIED** — recorded as a lead only.
Pricing was readable via the proxy ($19 / $49 / $99 per month billed annually, with 5 / 30 /
30+ years of history and 300 / 750 / 3,000 calls per minute), and FMP has a documented
history of frequent repricing, so even that is a point-in-time snapshot.

#### F. Databento — favourable licensing, disqualified on history

<https://databento.com/pricing> and <https://databento.com/equities>, **VERIFIED**:

> "Most of our datasets can be **redistributed internally or externally after 24 hours**."

> (on US Equities Mini) "Databento has a **derived use license** in place with these venues
> specifically for its redistribution and in turn our end users are allowed to use and
> redistribute the feed **without further licensing or exchange fee requirements**."

This is genuinely attractive licensing and it corroborates the T+1 principle in §3.1 from a
second angle. **But Databento's US equities history begins in 2018**, which fails §2.1 by a
wide margin for an all-time-high-anchored product. Not a candidate for R1; potentially
interesting much later if 4UR4 ever wants real-time.

### 7.3 Red / amber / green summary

| Provider | Cat. 1 internal | Cat. 2 derived-signal display | Cat. 3 raw-data display to subscribers | Overall for 4UR4 |
|---|---|---|---|---|
| **Intrinio** | Green (Startup tier, business-wide) | Green — reconstruction-based derived-data clause, 4UR4 on the safe side | **Green — "Display & Commercial Use" stated on the price list from $333/mo** | **GREEN** |
| **Massive** | Green (Business tier) | Green, subject to the derivative-works clause being clarified | **Green — "Edge Users" defined as users of Customer's products and services** | **GREEN (with one written question)** |
| **Norgate Data** | Red — personal use only | Red — derived data must be deleted on lapse | Red — redistribution forbidden | **RED — best technical fit, unusable licence** |
| **Finnhub** | Red — "can't be used by any business even internally without a written approval" | Red — ban extends to "derived results from the data" | Red | **RED by default; bespoke commercial licence unpriced** |
| **Marketstack** | Amber | Amber | Amber — display to end users reported but **not confirmed in the document body** | **AMBER — weakest verification in this document** |
| **Financial Modeling Prep** | Amber | Amber | Amber — separate "Data Display and Licensing Agreement" reported | **UNVERIFIED — pages unreachable** |
| **Alpaca** | Amber | Amber | Amber — governed by incorporated NASDAQ OMX agreements not read | **UNVERIFIED** |
| **EODHD** | Green — Internal Use $399/mo, explicit | Amber — not addressed in published terms | Amber — requires prior written approval; not published as an Enterprise entitlement | **AMBER** |
| **Twelve Data** | Green | **Green — explicit derived-data definition, customer retains rights** | Amber — requires an unpublished Redistribution Rights Add-On | **AMBER** |
| **Tiingo** | Amber — business use requires a Commercial plan | **Red — derived data needs prior written approval to even create/retain** | Red — internal use only; redistribution by special request | **RED** |
| **Alpha Vantage** | Amber | Red — personal, non-commercial by default | Red | **RED** |
| **Databento** | Green | Green | Green after 24h on most datasets | Green licence, **RED on history depth** |
| **Cboe (VIX, put/call)** | Amber | Red without consent — clause names derivative index creation | Red without consent | **RED without a Cboe licence** |
| **CNN F&G** | n/a | Red | Red | **RED — no licence route found** |

---

## 8. R8 — Expected cost

All prices retrieved **2026-07-26** from the vendor's own pricing page unless noted.
**None of these is a quote, a commitment, or an authorization.**

### 8.1 Published price list

| Provider | Tier | Price | Limits / inclusions | Tag |
|---|---|---|---|---|
| **Intrinio** | Individual | **$150/mo** | 1 seat; "No redistribution or external display" | **VERIFIED** |
| **Intrinio** | **Startup** | **$333/mo** to start, billed quarterly | "6 mo at $333, 6 mo at $666, $999 thereafter"; **business-wide licence, "Display & Commercial Use"**; rate limits not published | **VERIFIED** |
| **Intrinio** | Enterprise | **$1,250/mo** minimum | Custom terms, custom datasets, SLA, onboarding | **VERIFIED** |
| **Norgate Data** | Silver / Gold / Platinum / Diamond (US Stocks) | **$270 / $360 / $630 / $787.50 per YEAR** (12-mo) | History 10 yr / 20 yr / to 1990 / to 1950; US OTC add-on $90/yr. Local database + updater, not a REST API | **VERIFIED** |
| **Finnhub** | Basic / Standard / Professional (market data) | **$49.99 / $129.99 / $199.99 per mo** | 150 / 300 / 900 calls per min; daily OHLC 10 / 25 / 40+ years | **VERIFIED (proxy)** |
| **Financial Modeling Prep** | Free / Starter / Premium / Professional | **$0 / $19 / $49 / $99 per mo** (billed annually) | 250 calls/day / 300 / 750 / 3,000 calls per min; 5 / 30 / 30+ years history | **VERIFIED (proxy)** |
| **Alpaca** | Basic / Algo Trader Plus | **$0 / $99 per mo** | 200 calls/min free, unlimited paid; SIP consolidated available free for data >15 min old; 7+ years history | **VERIFIED** |
| **Marketstack** | Free / Basic / Professional / Business | **$0 / $9.99 / $49.99 / $149.99 per mo** | 100 / 10,000 / 100,000 / 500,000 requests per month; 1 / 10 / 15+ / 15+ years | **VERIFIED (proxy)** |
| Massive | Basic | **$0** | "5 API Calls / Minute", end-of-day, 2 years history, individual use only | **VERIFIED** |
| Massive | Starter | **$29/mo** | Unlimited calls, 15-min delayed, 5 years, individual use only | **VERIFIED** |
| Massive | Developer | **$79/mo** | Unlimited calls, 15-min delayed + trades, 10 years, individual use only | **VERIFIED** |
| Massive | Advanced | **$199/mo** | Unlimited calls, real-time, trades/quotes/financials, "20+ Years Historical Data", individual use only | **VERIFIED** |
| Massive | **Stocks Business** | **$1,999/mo** | Unlimited calls, 20+ yrs history, reference data, corporate actions, streaming, historical trades/quotes, financials & ratios | **VERIFIED** |
| Massive | Full Market Delayed (add-on) | $499/mo | 15-min delayed trades/quotes, every US exchange — "Additional exchange fees apply" | **VERIFIED** |
| Massive | Full Market real-time (add-on) | $1,999/mo | Real-time trades/quotes, every US exchange — "Additional exchange fees apply" | **VERIFIED** |
| Massive | IEX / NYSE Imbalances (add-ons) | $499 / $399 per mo | Single-venue feeds — "Additional exchange fees apply" | **VERIFIED** |
| Massive | Startup discount | up to **50% off first year** | Via sales@massive.com, qualification required | **VERIFIED** |
| EODHD | Free | **$0** | 20 API calls/day | **VERIFIED** |
| EODHD | EOD Historical Data (personal) | **$19.99/mo** / $199/yr | 100k calls/day, 1,000/min; personal use only | **VERIFIED** |
| EODHD | ALL-IN-ONE (personal) | **$99.99/mo** / $999.90/yr | EOD + intraday + fundamentals + calendar + bonds; personal use only | **VERIFIED** |
| EODHD | **Commercial — Internal Use** | **$399/mo** / $3,990/yr | 1,000 req/min, 100k calls/day; **no display outside the company** | **VERIFIED** |
| EODHD | **Commercial — Enterprise** | **$2,499/mo** / $24,990/yr | Unlimited calls, +500k onboarding calls, bulk retrieval, Data Services Agreement | **VERIFIED** |
| Twelve Data | Basic / Grow / Pro / Ultra | **$0 / $29 / $99 / $329 per mo** | 800 calls-a-day free; Ultra adds a 99.95% SLA | **VERIFIED** |
| Twelve Data | Redistribution Rights Add-On | **not published** | Required for external display | **GAP** |
| Tiingo | Starter / Power | **$0 / $30 per mo** | Free: 500 unique symbols/mo, 50 req/hr, 1,000/day, 1 GB/mo. Power: 10,000 req/hr, 100,000/day, 40 GB/mo | **VERIFIED** |
| Tiingo | Commercial / redistribution | **not published** | By request, "additional fees" | **GAP** |
| Alpha Vantage | Free | **$0** | 25 requests/day, 5/min | **UNVERIFIED** (search-sourced) |
| Alpha Vantage | Premium | **$49.99 → $249.99/mo** | 75 / 150 / 300 / 600 / 1,200 requests per minute; "No daily limits" | **VERIFIED** |
| Databento | Historical pay-as-you-go | **from $0.40/GB** | Billed on uncompressed binary size | **VERIFIED** |
| Databento | Standard / Plus / Unlimited | **$199 / $1,750 / $4,500 per mo** | Subscription tiers | **VERIFIED** |
| Nasdaq Data Link / Sharadar | SEP / bundles | **not published** — login required | Reseller notes professional users must buy from Nasdaq Data Link | **GAP** |

### 8.2 Free-tier and trial feasibility — explicitly, because the ruling names it

MVP batch volume: **~500 symbols, once per trading day** (~500 requests/day incremental),
plus a one-time backfill of ~500 symbols × full history.

| Provider free tier | Daily 500-symbol scan feasible? | History adequate? | Licence adequate? | Verdict |
|---|---|---|---|---|
| **Alpaca Basic ($0)** | **Yes** — 200 calls/min | **No — 7+ years** | Unverified (NASDAQ OMX agreements) | Not viable as primary — **but the best free cross-check**, since SIP consolidated bars are free for data >15 min old |
| Massive Basic ($0) | Technically yes — 500 calls at 5/min ≈ 100 min | **No — 2 years** | No — individual use only | **Not viable** (history and licence) |
| EODHD Free ($0) | **No — 20 API calls/day** | n/a | No | **Not viable** |
| Tiingo Starter ($0) | Marginal — 500 unique symbols/mo is exactly the cap; 50 req/hr means a 500-symbol pass takes ~10 h | 30+ yrs claimed | No — internal use only, derived data needs written approval | **Not viable** (licence) |
| Twelve Data Basic ($0) | Yes — 800 calls/day, 8/min ≈ 63 min | Unknown | No — "internal non-display", free tier barred from commercial use | **Not viable** (licence) |
| Financial Modeling Prep Free ($0) | **No — 250 calls/day** | n/a (EOD only) | Unverified | **Not viable** |
| Marketstack Free ($0) | **No — 100 requests/month** | **No — 1 year** | Unverified | **Not viable** |
| Finnhub Free ($0) | Yes — 60 calls/min | Contested between Finnhub's own two pricing pages | No — personal use only, no business use without written approval | **Not viable** (licence) |
| Alpha Vantage Free ($0) | **No — 25 requests/day** | Unknown | No | **Not viable** |

**Conclusion on free tiers:** *no free tier is viable as the MVP's production source* —
every one fails on licence, and most also fail on history depth or throughput. **But one
free tier is genuinely valuable for a specific purpose: Alpaca's Basic tier serves
consolidated-tape (SIP) daily bars at no cost for data older than 15 minutes**, which makes
it a legitimate **independent cross-check** for the §11 wick-fidelity test — the single
most important pre-purchase quality check for this product.

That evaluation still requires an API key, and issuing a key is accepting terms, which is
outside this agent's authority (and Alpaca's terms are themselves unverified, §7.2 E4).
**It is recommended as a Product-Owner action, not performed here.**

On trials: none of the candidates published a time-limited paid trial on the pages read
(**GAP**). Massive's "up to 50% discount on the first year" for qualifying startups is the
nearest published concession (**VERIFIED**).

### 8.3 Cost scenarios

Scenarios, not a single number — because the number depends entirely on *which of the three
uses* in §7.1 is in force.

#### Scenario A — MVP as documented: daily T+1 batch, internal dashboard only, no external users

| Option | Monthly | Annual | Notes |
|---|---|---|---|
| Intrinio Individual | **$150** | $1,800 | 1 seat, no display — adequate for a genuinely internal MVP, but does **not** carry forward to SaaS |
| **Intrinio Startup** | **$333 → $666 → $999** | **≈$5,994 yr 1**, $11,988 steady state | Business-wide, display + commercial use from day one — carries forward to SaaS unchanged |
| EODHD Commercial — Internal Use | **$399** | $4,788 | Explicitly permits company-internal use; explicitly forbids external display |
| Massive Stocks Business | **$1,999** | $23,988 | ~$999/mo in year 1 if the startup discount applies |
| Finnhub Professional | **$199.99** | $2,400 | 40+ yr history, but personal-use-only terms bar business use without written approval |
| Twelve Data Grow / Pro | **$29 / $99** | $348 / $1,188 | Cheapest, but adjustment + wick GAPs make it non-compliant with HD-01 today |
| Exchange entitlement fees | **$0** | $0 | T+1 consumption — no exchange licence required (§3.1) |

**Cheapest licence-clean, depth-adequate internal MVP: $150/month (Intrinio Individual).**
**Recommended internal MVP: $333/month (Intrinio Startup)** — because it is the only option
that is *simultaneously* deep enough (§2.1), licence-clean for SaaS (§7), and does not
require a provider migration between the internal dashboard and the paid product.

#### Scenario B — SaaS: derived signals **and price charts** shown to paying subscribers

| Option | Monthly | Annual | Redistribution basis |
|---|---|---|---|
| **Intrinio Startup** | **$333 → $666 → $999** | **≈$5,994 yr 1**, $11,988 steady state | **Published on the price list** — "Display & Commercial Use", business-wide licence |
| **Massive Stocks Business** | **$1,999** | $23,988 (≈$11,994 yr 1 with 50% startup discount) | **Published** — "Edge Users" = users of Customer's products and services |
| EODHD Enterprise | **$2,499** | $29,988 | Data Services Agreement — external display **not published as an entitlement**; must be negotiated |
| Intrinio Enterprise | $1,250+ | $15,000+ | Same display rights, plus SLA and custom datasets |
| Twelve Data Pro + Redistribution Add-On | $99 + **unknown** | — | Add-on price not published |
| Tiingo / Finnhub / Norgate commercial | **unknown / none** | — | Derived-data creation or business use itself gated — not recommended |
| Exchange entitlement fees | **$0** | $0 | Still T+1 (§3.1) |

**Recommended SaaS configuration: ≈$6k in year 1, ≈$12k/year steady state, one vendor, no
exchange fees.** The structurally important point is that **Scenario B costs exactly the
same as Scenario A** on both leading providers — the business/startup tier already carries
the display right. Buying it at MVP therefore acquires the SaaS licence at **zero
incremental cost** and removes a provider migration from the moment the product can least
afford one. Intrinio's ramp ($333 for six months) means the *early* MVP is cheaper still,
which is the right shape for a product whose Phase 1 is a data foundation rather than
revenue.

#### Scenario C — if intraday is ever wanted (not MVP)

This is where costs change *category*, not degree.

| Element | Cost | Source |
|---|---|---|
| Massive Full Market Delayed (15-min) add-on | $499/mo + "Additional exchange fees apply" | <https://massive.com/business> |
| Massive Full Market real-time add-on | $1,999/mo + "Additional exchange fees apply" | <https://massive.com/business> |
| Exchange entitlement, illustrative (Nasdaq, professional) | "the **lowest** fee for professional users is roughly **$2,051/month**" — TotalView internal distribution $1,500/mo + admin $100/mo + $76 per subscriber per month non-display | <https://databento.com/blog/understanding-exchange-fees> |
| Per-subscriber display fees | Scale **with user count** — the fee model changes from flat to per-seat | ibid. |

**The hidden cost, named explicitly as the brief requires:** exchange entitlement fees are
*not* charged by the API vendor and do not appear on the vendor's pricing page; they are
levied by NYSE/Nasdaq/Cboe and passed through, and the per-subscriber component means a
successful SaaS gets *more* expensive per user. Moving from T+1 to delayed or real-time
therefore does not add ~$500–$2,000/month — it adds ~$2,000+/month **plus a per-subscriber
line item that grows with the business**.

**This makes the documented EOD/daily default a genuine commercial asset, not just a
simplicity choice, and it should be defended on those grounds.**

#### Bundle vs. best-of-breed

| Approach | Illustrative annual cost | Assessment |
|---|---|---|
| **Bundle** — one vendor for OHLCV + corporate actions + (later) constituents | **≈$5,994 yr 1 / $11,988 steady (Intrinio Startup)**; $23,988 (Massive Business) | Simplest: one licence to reason about, one provenance chain, one seam. **Recommended for MVP** |
| **Best-of-breed** — primary vendor for bars/actions + a specialist for point-in-time constituents/delisted (R4/R5) + reconstructed sentiment (§6.4) | Primary + R4/R5 dataset (unpriced) + **$0 sentiment** | Likely necessary eventually, because R4/R5 survivorship needs may not be met by one vendor. The `data/` design in §9 must assume it |
| **Composed depth** — a shallow-but-authoritative vendor for recent bars + a deep vendor for the pre-history | $23,988 + a second licence | Only required if the primary fails §2.1. Choosing a deep primary (Intrinio, 50+ yrs) **avoids this entire cost and complexity class**, which is a substantial and easily-overlooked saving |

**Sentiment adds $0** under the §6.4 recommendation, because the reconstruction uses bars
4UR4 already licenses. That is a meaningful and slightly non-obvious cost finding.

---

## 9. Technical interface requirements for `data/`

**Purpose:** make HD-06 **decidable and reversible**. The architecture (§3.2) already
requires `data/` to be provider-agnostic and to own normalisation and provenance. The
findings above turn that principle into a specific, testable contract. Each requirement
below exists because a *specific* finding in this document would otherwise leak into the
engine.

| # | Requirement | Driven by |
|---|---|---|
| **DI-01** | **Explicit adjustment basis on every bar.** Bars carry an `adjustment_basis` ∈ {`RAW`, `SPLIT_ADJUSTED`, `SPLIT_AND_DIVIDEND_ADJUSTED`}. The layer **rejects** anything other than `SPLIT_ADJUSTED` at the engine boundary. An adapter that cannot state its basis cannot be admitted. | HD-01; §2.2 — three candidates have undetermined methodology |
| **DI-02** | **Both series obtainable.** Every adapter must expose the same symbol/range as raw **and** split-adjusted, so the adjustment can be independently re-derived and diffed rather than trusted. | HD-01; §4 — re-derivability is the antidote to this repo's defect class |
| **DI-03** | **Corporate actions are a first-class call**, not a side effect: `corporate_actions(symbol, range)` returning splits (with `execution_date`, ratio), dividends, and symbol-change events, so `data/` can self-apply and verify adjustment. | §4 |
| **DI-04** | **Mandatory `as_of` on every read.** `get_bars(symbol, start, end, as_of)` — `as_of` is required, not optional. A backtest must be unable to see a restatement that post-dates the bar it is evaluating. | HD-12 §21.8 no-look-ahead; §2.4 — Massive restates daily bars for late trades |
| **DI-05** | **Vintage/snapshot provenance per bar**: provider id, adapter version, retrieval timestamp, snapshot id — persisted with the bar, so any historical signal is replayable against the series that produced it. | Architecture §4/§5; §2.4 |
| **DI-06** | **Wick semantics declared as a capability**, not assumed: `wick_semantics` ∈ {`CONSOLIDATED_SIP`, `PRIMARY_LISTING`, `PARTIAL_VENUE`, `UNKNOWN`}, plus `includes_extended_hours`, **plus `upstream_source`** — because several cheap vendors are resellers (Marketstack resells Tiingo), and two "independent" adapters sharing an upstream make a cross-check meaningless. `UNKNOWN` is admissible for research but **not** for a shipped signal. | §2.3 — the attribute that silently breaks an ATH-anchored detector |
| **DI-06b** | **Adapters may declare fields as forbidden.** Intrinio's `adj_*` fields are split **and** dividend adjusted; feeding them to the engine would violate HD-01 while looking entirely normal. The adapter must be able to mark a provider field as banned so the violation is a load-time error, not a silent wrong answer. | §2.2(b) |
| **DI-07** | **`history_start_date` is a declared, enforced capability.** If a requested range predates it, the layer must **fail loudly**, never silently truncate — because a truncated history produces a *plausible but wrong* ATH anchor. | §2.1 — the Intel-class failure |
| **DI-08** | **Composable adapters.** A `CompositeProvider` must be able to stitch a deep-history source for `t < seam` with the primary for `t ≥ seam`, with an explicit seam date, per-bar provenance, and a mandatory **overlap-reconciliation test** across the seam. This is not speculative: §2.1 shows the best-licensed provider is also the shallowest. | §2.1, §8.3 best-of-breed |
| **DI-09** | **Licence class travels with the data.** Each adapter declares `redistribution_class` ∈ {`INTERNAL_ONLY`, `EXTERNAL_DISPLAY`, `REDISTRIBUTION`}, and the api/web layer can assert it at render time. A chart must be unable to render vendor bars whose adapter is `INTERNAL_ONLY`. | R7 §7.1 — and directly addresses "a restatement of a fact, stored apart from the fact" by keeping the licence fact attached to the data it governs |
| **DI-10** | **Bulk/whole-market reads where the provider offers them.** Massive's Daily Market Summary returns OHLCV for all US stocks for one date in a single call, and honours the `adjusted` parameter — so a 30-year backfill is ~7,500 calls, not ~500 × 30 years of per-symbol pagination. The interface must expose `bulk_daily(date)` as an optional capability with a per-symbol fallback. | <https://massive.com/docs/rest/stocks/aggregates/daily-market-summary>, **VERIFIED** |
| **DI-11** | **Partial-universe results flag the scan run** rather than silently producing a smaller scan. | Architecture §6.1 |
| **DI-12** | **A provider conformance suite.** One fixed set of symbols and date ranges that *every* adapter must pass, with tolerance-bounded agreement on O/H/L/C and exact agreement on split-adjustment factors. This suite is what makes HD-06 reversible: swapping providers becomes a test run, not a rewrite. | The brief's explicit requirement that HD-06 be decidable *or reversible* |

**Consequence for the engine:** none of DI-01…DI-12 changes `engine/`. The engine keeps
receiving plain bars and returning plain results (architecture §2). Every provider-specific
concern above is absorbed at the `data/` seam — which is the test of whether the seam is in
the right place. It is.

---

## 10. Open gaps and things I could not verify

Recorded as findings. Each is a question for the Product Owner or a follow-up ticket — none
is filled from memory.

| # | Gap | Why it matters | Suggested owner |
|---|---|---|---|
| G-01 | **No sample pulls were performed** (no API key — that would be accepting terms; and GOV-015 forbids ingestion scripts). Every adjustment/wick claim is documentation-based | R1/R3 evidence requirements are not fully satisfied; §11 converts them into acceptance tests | Product Owner (a key issuance is a terms acceptance) |
| G-02 | **EODHD history depth is self-contradictory**: "30+ years" on the pricing page vs "from January 2000" in its own academy article | Decides whether EODHD actually solves the §2.1 depth problem — the whole reason to consider it over Massive | To EODHD sales, in writing |
| G-03 | **How many current S&P 500 names have a pre-2004 all-time high?** | Converts "Massive's 2004 start is a risk" into a number, and determines whether DI-08 composition is required or merely prudent | Needs R4 constituents + a long price series — joint with the R4/R5 effort |
| G-03b | **Intrinio's daily high/low construction** — consolidated tape or single market centre, and at which tier? Its EOD price docs are silent; its real-time SDK references CTA/UTP SIP feeds and `UpdateHighLowConsolidated` conditions | **The blocking question on the recommended provider.** Wick fidelity is the one attribute this product cannot compromise (§2.3) | To Intrinio, in writing, before HD-06 — condition **C-1** |
| G-03c | **Intrinio's published rate limits** (calls/min, calls/day) are absent from the pricing page | Determines whether a 500-symbol daily batch and a 50-year backfill are throughput-feasible | To Intrinio sales |
| G-03d | **Whether Intrinio exposes a split-only series directly**, or whether 4UR4 must self-apply `split_ratio` to raw OHLC | Affects adapter complexity only, not viability — the self-applied path is preferred anyway (§4, DI-02) | To Intrinio; low risk |
| G-04 | **Massive's derivative-works clause** — does a confidence score count as a prohibited "investment strategy"/"index"? | The open legal question on the runner-up | To Massive, in writing, if Massive is selected |
| G-05 | **EODHD Enterprise external-display rights** are not published; ToS requires prior written approval | Determines whether EODHD is a real runner-up for SaaS or internal-only | To EODHD sales |
| G-06 | **Twelve Data Redistribution Rights Add-On price** — `twelvedata.com/enterprise` returned HTTP 404 | Would make a ~$99/mo + add-on configuration comparable if the adjustment/wick GAPs also closed | To Twelve Data sales |
| G-07 | **Twelve Data / Tiingo / Alpha Vantage adjustment methodology and wick construction** undetermined | HD-01 cannot be satisfied by an unknown basis | Vendor documentation request |
| G-08 | **Spin-off and merger event coverage** not enumerated by either recommended provider | A mishandled spin-off injects a false ATH, exactly like an unadjusted split | To both vendors; also add a spin-off sanity check to architecture §6.1 |
| G-09 | **Sharadar / Nasdaq Data Link pricing** is behind a login | The conventional survivorship-bias-free answer is unpriced, so HD-07's cost is still unknown | R4/R5 effort |
| G-10 | **Financial Modeling Prep** legal pages returned HTTP 403 to every attempt, including via the rendering proxy; pricing was readable but FMP reprices frequently | A commonly-cited candidate's licensing is entirely unverified | Follow-up |
| G-15 | **Marketstack's display-rights clause** could not be found in the fetched agreement body, only in a search snippet; Marketstack also resells Tiingo, raising an inherited-rights question | The weakest-verified licensing finding here; a cheap tier with real display rights would matter commercially if true | Read the executed agreement before relying on it |
| G-16 | **Alpaca's market-data terms** incorporate NASDAQ OMX agreements that were not read | Alpaca is proposed only as a free cross-check source (§11), but even that use is governed by these terms | Clear before using Alpaca even for evaluation |
| G-17 | **Finnhub publishes two pricing pages** whose free-tier OHLC entitlements do not reconcile; and issue #336 reports its adjusted/unadjusted flag returning identical data | Finnhub is excluded on licence anyway, but the adjustment-flag class of bug applies to any vendor — hence §11 test 2 | Recorded; no action unless Finnhub is reconsidered |
| G-18 | **Norgate's consolidated-tape wording** was read in its Canadian-market section; the US-specific statement was not directly confirmed | Moot while Norgate is licence-excluded; would matter if Norgate ever offered a commercial licence | Only if Norgate is revisited |
| G-11 | **ICE Data Indices redistribution terms** for credit-spread series pulled via FRED | FRED explicitly disclaims authority over third-party-owned series; assuming FRED access implies display rights is a real trap | Only if credit spreads enter the sentiment reconstruction |
| G-12 | **SentimenTrader's end-customer display/resale terms** not published | The only vendor found with a genuinely commercial equity-sentiment licensing route | Only if §6.4's reconstruction is rejected |
| G-13 | **CNN's primary consumer Terms of Use** returned HTTP 451 to direct fetch | The commercial ToU that *was* read points the same way, so the conclusion is unlikely to change — but it is not fully verified | Low priority — HD-09 already forbids the use |
| G-14 | **No published time-limited trials** were found for any candidate | Affects how a data-quality evaluation could be run before spend | Product Owner |

---

## 11. What would prove this right — acceptance tests for after HD-06 and a per-scope freeze lift

These exist because §0's evidence limit is real and should be closed rather than forgotten.
Each is a test, not a task.

1. **Wick fidelity, cross-vendor.** For ~10 symbols spanning long-lived, recently-added and
   split-heavy names, pull daily bars from **two vendors with different upstreams** over the
   same range and assert agreement on **high** and **low** within a stated tolerance.
   Disagreement on highs — not closes — is the failure this product must detect. Alpaca's
   free consolidated-tape tier is the recommended second source (§8.2). The
   *different-upstream* requirement is not pedantry: Marketstack resells Tiingo (§2.3), and
   two adapters sharing an upstream would agree perfectly while both being wrong.
2. **Adjustment re-derivation (HD-01).** Pull raw OHLC + split events; re-derive the
   split-adjusted series in `data/`; assert bit-comparable agreement with the vendor's
   split-adjusted series across at least one known split per symbol. This is DI-02 in test
   form, and it is also the check that catches a **silently no-op adjustment flag** — a
   failure mode with open public issue reports against at least two candidates (§2.2).
3. **Forbidden-field assertion.** Assert that the adapter refuses to emit a bar built from
   a dividend-adjusted field (e.g. Intrinio's `adj_high`). Under HD-01 this must fail at
   load time, loudly — not produce a plausible, wrong ATH. This is DI-06b in test form.
4. **ATH stability across the seam.** For any composed provider (DI-08), assert that the
   selected `HA`/`tA` is invariant to which side of the seam supplies the overlapping bars.
5. **Depth sufficiency.** For every symbol in the universe, assert
   `provider.history_start_date` precedes the bar selected as `HA`. Any symbol failing this
   is quarantined, not silently scanned — this is DI-07 in test form and it is the direct
   answer to the Intel-class failure.
6. **Restatement/as-of correctness (HD-12).** Read the same date twice with different
   `as_of` values across a known restatement; assert the earlier `as_of` does not observe
   the later correction.
7. **Licence-class enforcement.** Assert that a render path cannot emit vendor bars sourced
   from an `INTERNAL_ONLY` adapter (DI-09).

---

## 12. Comparison matrix

One row per candidate, across the attributes R1/R2/R3/R7/R8 name. All cells reflect the
evidence above; "?" means GAP, not "adequate".

| Candidate | Coverage | Adjustments (HD-01) | History depth | Wick fidelity | Corporate actions | Latency / EOD | Redistribution (R7) | Cost at MVP | Cost at SaaS | API quality |
|---|---|---|---|---|---|---|---|---|---|---|
| **Intrinio** | US equities + options + fundamentals | Raw OHLC + `split_ratio` published separately → **HD-01 self-derivable**; `adj_*` is splits+dividends and must be banned | **50+ years** — best of any licensable candidate | **PARTIAL** — CTA/UTP SIP feeds and consolidated conditions referenced, but EOD high/low construction undocumented | Splits, dividends, adjustment factors, provider-applied; spin-off/merger/symbol-change ? | Unconfirmed EOD ~4:45–5:00pm ET; **confirmed EOD 8:00–9:00pm ET** | **Green — "Display & Commercial Use", business-wide, stated on the price list** | **$333/mo** (Startup) | **$333 → $666 → $999/mo** — same tier | Good docs; **rate limits not published** |
| **Massive** (ex-Polygon.io) | Full US equities, consolidated tape | **Split-only by default; `adjusted=false` gives raw — exactly HD-01** | **2004** — weakest attribute | **Best in survey** — consolidated SIP, per-condition `updates_high_low` rule published | Splits back to 1978; ticker-change events; spin-off/merger ? | EOD bar continuously restated; late trades folded in at close | **Green — "Edge Users" = users of Customer's products/services** | $1,999/mo (≈$999 yr 1 w/ startup discount) | $1,999/mo — same tier | Strong docs; bulk whole-market daily endpoint; documented corrections |
| **EODHD** | US + global, incl. delisted | Raw OHLC + `adjusted_close`; split-only via `function=splitadjusted` | "30+ yrs" vs "from 2000" — **contradictory** | ? | Splits + dividends (incl. unadjusted value); symbol changes ? | **NYSE/NASDAQ within 15 min of close** | Amber — internal $399/mo explicit; external display needs written approval | $399/mo internal | $2,499/mo Enterprise (display not published) | Good docs; explicit personal/commercial split |
| **Norgate Data** | US stocks (+OTC add-on) | **`CAPITAL` mode = exactly HD-01, first-class** | **To 1950** (Diamond) | Consolidated tape (US wording unconfirmed) | Explicit corrections policy incl. mergers, listing-status, dividends | ? | **Red — personal use only; derived data deleted on lapse** | **$787.50/YEAR** | **Not licensable** | Local DB + updater, not a REST API |
| **Finnhub** | Global equities | `adjusted=true` = split-only (bug report open) | **40+ years** (Professional) | Named upstreams (EDI, QuoteMedia, ActivFinancial); consolidation unstated | Multi-source | ? | **Red — personal use only; ban extends to "derived results"** | $199.99/mo | Bespoke, unpriced | Two irreconcilable pricing pages |
| **Twelve Data** | 84 markets | ? | ? | ? | ? | ? | Amber — **best derived-data clause found**; external display needs unpublished add-on | $29–$99/mo | $99/mo + unpublished add-on | Clear ToS; 99.95% SLA at Ultra |
| **Alpaca** | US equities, SIP + IEX | **`adjustment=split` — exactly HD-01** | **7+ years — disqualifying as primary** | **Verified consolidated SIP**, condition-level daily rules published | Corporate Actions API from April 2020 | ? | Unverified (NASDAQ OMX agreements) | $0 / $99/mo | Unverified | Good docs; **best free cross-check source** |
| **Tiingo** | 108,993 global securities | ? | 30+ yrs claimed | ? | ? | ? | **Red — derived data requires prior written approval to create/retain** | $30/mo (internal only) | Unpublished | Simple; attribution required |
| **Financial Modeling Prep** | Global at Professional | ? — docs unreachable | 30+ yrs claimed | ? | ? | ? | Unverified — separate Data Display and Licensing Agreement reported | $19–$99/mo | Unverified | Legal pages 403; reprices frequently |
| **Marketstack** | Global; **resells Tiingo** for US | ? — **vendor concedes it is undocumented** | "15+ yrs" vs "up to 30" — contradictory | ? — inherits Tiingo's | split_factor + dividend fields only | ? | Amber — display reported, **not found in the document body** | $9.99–$149.99/mo | Unverified | Cheapest tiers; weakest verification |
| **Alpha Vantage** | Broad | ? | ? | ? | ? | ? | **Red — personal, non-commercial unless agreed in writing** | $49.99–$249.99/mo | Unpublished written agreement | Rate-limit-only tiering |
| **Databento** | US equities, venue-level | Self-applied | **2018 — disqualifying** | Partial-venue blends are **not** consolidated extremes | ? | T+1 redistributable | Green — "redistributed internally or externally after 24 hours" | from $0.40/GB; $199–$4,500/mo | Green licence | Excellent licensing transparency |
| **Nasdaq Data Link / Sharadar** | US equities + constituents | ? | EOD prices from 1998 (third-party listing) | ? | ? | ? | ? | **Unpriced — login required** | ? | Mostly an R4/R5 candidate |

---

## 13. Recommendation memo

> **This is a recommendation to the Product Owner. It is not a decision, not a purchase,
> and not an acceptance of any licence.**
> **[HD-06](human-decisions.md) remains PENDING.** Nothing in this document — including
> this section — constitutes the Product Owner's financial authorization, and no agent may
> represent it as such (authority boundary, 2026-07-26, issue #23, boundary 5).

### 13.0 The reasoning, before the answer

Thirteen candidates reduce to a small number once three filters are applied in order of how
hard each is to fix:

1. **History depth (§2.1).** Unfixable by negotiation or engineering — a provider either
   holds the bar that is the ATH or it does not. This removes **Massive (2004)**,
   **Databento (2018)** and **Alpaca (7 yrs)** as *primary* sources, and puts EODHD and
   Marketstack in doubt on their own contradictory documentation.
2. **Redistribution licence (§7).** Fixable only by the vendor having a product for it.
   This removes **Norgate**, **Finnhub**, **Tiingo** and **Alpha Vantage** outright, and
   leaves **Twelve Data**, **Marketstack**, **FMP** and **Alpaca** unverified.
3. **HD-01 adjustment basis and wick fidelity (§2.2, §2.3).** Fixable by asking, or by
   self-applying adjustments in `data/`. This is a *question*, not a wall.

Applying filters 1 and 2 together leaves exactly **two** candidates that clear both:
**Intrinio** and **EODHD** — and EODHD's depth rests on documentation that contradicts
itself. Massive clears filter 2 superbly and fails filter 1.

The judgement, stated plainly: **an all-time-high-anchored detector cannot be built on a
provider that structurally cannot see the all-time high.** Massive has the best-documented
wick semantics in the survey, and that matters enormously — but a perfectly-constructed high
on the wrong anchor bar is still the wrong trendline. Depth therefore outranks documentation
quality, because depth cannot be recovered and documentation can be requested.

### 13.1 Recommended: **Intrinio — Startup tier**, $333/mo ramping to $999/mo

Ranked first on four grounds, in order of weight:

1. **It is the only candidate with a published external-display licence that also has the
   history depth this product structurally requires.** "Over 50 years" of EOD history
   (**VERIFIED**) comfortably reaches the ATH of any current S&P 500 constituent, including
   the dot-com-peak cohort that defeats a 2004-start provider. This is the constraint that
   cannot be engineered around, and Intrinio is the only candidate that clears it *and*
   filter 2.
2. **Its licence class is stated on the price list, not left to negotiation.** Individual =
   "No redistribution or external display"; **Startup = "Display & Commercial Use",
   business-wide**. Combined with a derived-data clause drawn on reconstruction ("if a user
   could infer or reconstruct the original data…"), 4UR4's position is unambiguous on both
   sides of the §7.1 line: its scores are safely derived, and its charts are covered by the
   display right it is buying.
3. **HD-01 is satisfiable in the *auditable* way.** Intrinio publishes raw OHLC and exposes
   `split_ratio` **separately** from `dividend`, so `data/` derives the split-adjusted,
   dividend-unadjusted series itself and can re-derive and diff it at any time (DI-02,
   DI-03). §4 already argues this is the preferred posture over trusting a vendor-applied
   series. The `adj_*` fields are splits **and** dividends and must be banned outright
   (DI-06b) — a real hazard, but a load-time-checkable one.
4. **It is roughly half the cost of the runner-up, and cheapest exactly when cash matters
   most.** ≈$5,994 in year 1 (six months at $333, six at $666) against Massive's $23,988,
   settling at $11,988/year. No exchange entitlement fees at T+1 (§3.1). And because the
   Startup tier already carries display rights, **the MVP and the SaaS cost the same** — no
   migration, no re-platforming, no second licence.

**One condition attaches, and it is blocking:**

- **C-1 (correctness, blocking): obtain Intrinio's written confirmation that its daily EOD
  high and low are consolidated-tape extremes** (CTA/UTP), and at which tier (G-03b).
  Intrinio's real-time SDK references SIP feeds and `UpdateHighLowConsolidated` conditions,
  which is encouraging, but **its EOD price documentation is silent**, and §2.3 establishes
  that wick construction is the attribute that silently breaks this product. **If the answer
  is "primary listing only" or "single market centre", this recommendation is withdrawn in
  favour of §13.2.**

Two non-blocking follow-ups: published rate limits (G-03c) and whether a split-only series
exists directly (G-03d, low risk — the self-applied path is preferred anyway).

**Independent verification is available and cheap.** Alpaca's free tier serves
consolidated-tape daily bars for data older than 15 minutes, which makes the §11 wick test a
genuine cross-vendor check at no cost — subject to clearing Alpaca's own unverified terms
(G-16).

### 13.2 Runner-up: **Massive** (formerly Polygon.io) — **Stocks Business, $1,999/month**

Massive is the **correctness benchmark of this survey** and would be ranked first on data
quality alone:

- It is the only candidate that publishes a **per-sale-condition** rule for which trades
  update the high and low, and states that its daily bars follow the SIP **consolidated**
  processing guidelines across all exchanges. For a product whose anchor is a wick, that is
  the requirement, not a nicety.
- Its **default output is exactly the HD-01 basis** — `adjusted` defaults to split-only,
  dividends are never applied, `adjusted=false` returns raw. No derivation needed.
- Its business licence names 4UR4's exact case: **"Edge Users" = "users of Customer's
  products and services"**, with the grant covering use "in websites or software
  applications owned or licensed by Customer".
- Operationally it fits the batch design better than anything else: the Daily Market Summary
  endpoint returns OHLCV for **all** US stocks for a date in one call and honours `adjusted`
  (DI-10), and its correction/restatement behaviour is documented — which is what makes
  DI-04/DI-05 implementable rather than aspirational.

**It is ranked second for exactly one reason: its stock history begins in 2004** (§2.1). For
a detector anchored at the all-time high, that is a correctness defect on precisely the
population the product targets — names in long descents from old highs.

Massive also carries an open legal question: its derivative-works clause prohibits creating
"any index, indicative value, … settlement value or investment strategy" from the
Information "unless licensed to do so" (G-04). The enumerated examples are tradeable and
valuation constructs, so a chart-pattern confidence score is plausibly outside them — but
this would need a written answer before selecting Massive.

**Massive becomes the recommendation if C-1 fails** — i.e. if Intrinio's wicks are not
consolidated — because at that point the ranking inverts: an unusable wick is fatal
immediately, whereas a 2004 depth limit can be mitigated by composition (DI-08) at the cost
of a second licence and a seam.

### 13.3 Third: **EODHD** — Internal Use $399/month, Enterprise $2,499/month

EODHD is the natural fallback if both leaders fail. It exposes raw OHLC plus a split-only
adjusted series (satisfying HD-01 by a third route), publishes a precise EOD delivery time
(within 15 minutes of the NYSE/NASDAQ close — the most specific timing commitment found),
documents delisted coverage (relevant to R5/HD-07), and its **$399/month Internal Use** tier
is a cheap, licence-clean way to run a purely internal MVP.

It ranks third because its own documentation contradicts itself on history depth (G-02) —
the very attribute it would be chosen for — its **wick construction is undocumented**
(§2.3), and its external-display right is a negotiated term rather than a published
entitlement (G-05). Three open questions on the three attributes that matter most is too
many to rank higher on today's evidence.

### 13.4 Not recommended, and why

- **Norgate Data** — the best *technical* fit in the survey (`CAPITAL` = HD-01 exactly,
  history to 1950, consolidated tape, explicit corrections policy) at **$787.50/year**, and
  **unusable**: its EULA grants personal use only, forbids commercial purposes and
  redistribution, and requires deletion of **derived data** on lapse. A textbook case of
  licence, not data, being the binding constraint.
- **Finnhub** — 40+ years and a documented split-only flag at $199.99/month, defeated by
  terms that bar business use even internally without written approval and extend the
  redistribution ban to "derived results from the data".
- **Tiingo** — $30/month and a 30+ year claim, defeated by a clause making the **creation
  and retention** of derived data contingent on prior written approval. 4UR4 is a
  derived-data product; that is the wrong foundation at any price.
- **Alpha Vantage** — personal and non-commercial unless separately agreed in writing;
  premium tiers are described purely as rate limits with no stated commercial grant;
  adjustment and wick methodology are GAPs.
- **Alpaca** — `adjustment=split` and verified consolidated SIP make it technically apt, but
  **7 years of history** rules it out as primary. **Retained as the recommended free
  cross-check source** for the §11 wick test.
- **Databento** — excellent licensing and the most transparent exchange-fee treatment found
  anywhere, but US equities history begins in **2018**. Revisit only if 4UR4 ever pursues
  real-time.
- **Twelve Data / Marketstack / Financial Modeling Prep** — not rejected, **not
  assessable**. Adjustment methodology, wick construction, or licence text could not be
  verified for each (Marketstack's own FAQ concedes the first; FMP's legal pages are
  unreachable). They cannot be ranked on evidence that does not exist.
- **CNN Fear & Greed** — no official API, no licensing route found, and CNN's commercial
  terms prohibit redistribution and non-personal use. Consistent with HD-09; unavailable.

### 13.5 What would change the ranking

| If this proves true | Then |
|---|---|
| **Intrinio's EOD high/low are not consolidated-tape** (C-1 / G-03b) | **Recommendation withdrawn.** Massive becomes first, with a deep-history composition (DI-08) to cover pre-2004 anchors |
| Intrinio's rate limits cannot support a 500-symbol daily batch or a 50-year backfill (G-03c) | Re-open; likely a negotiation rather than a disqualification |
| A negligible number of current S&P 500 names have a **pre-2004** ATH (G-03) | Massive's only weakness largely evaporates and it becomes first on documentation quality — at roughly double the cost |
| EODHD confirms genuine 1990s daily history **and** consolidated wicks **and** written display rights (G-02, G-05) | EODHD becomes a strong first — matching on correctness, beating on depth, competitive on price |
| Massive confirms the confidence score is a prohibited derivative work (G-04) | Massive is removed from contention entirely, not merely demoted |
| Twelve Data documents split-only adjustment + consolidated wicks and prices the add-on sensibly (G-06, G-07) | Twelve Data becomes a serious cost challenger at roughly 1/10th the price |
| 4UR4 decides it will **never** display price bars — only derived signal text | The whole category-3 requirement drops away and the cheap internal-use tiers become viable. **This is a product decision, not a data decision, and should be taken deliberately rather than by default** — §7.1 argues against it, since explainability is the product |
| Intraday is ever adopted | Exchange entitlement fees attach (~$2,000+/month **plus per-subscriber display fees that grow with the business**, §8.3 Scenario C). A business-model decision, not a technical upgrade |

### 13.6 Statement of authority

This document was produced under GOV-015 (build-freeze ON) and the HD-06 authority boundary
of 2026-07-26. No provider was selected. No spend was committed. No licensing terms were
accepted, viewed under login, or clicked through. No account was created and no API key was
requested. No provider data was fetched, cached, stored or redistributed. **HD-06 remains
PENDING**, and only the Product Owner may decide it — via the out-of-band confirmation step
that [#21](https://github.com/tomerYannay/4UR4/issues/21) requires as a precondition.

---

## 14. Source log

Every URL relied on above, with the date it was retrieved. Where a page could not be read,
that is recorded here too — an unreachable source is part of the evidence.

| Source | Used for | Retrieved | Result |
|---|---|---|---|
| <https://intrinio.com/pricing> | Intrinio tiers, "No redistribution or external display" vs "Display & Commercial Use" | 2026-07-26 | Read |
| <https://intrinio.com/financial-market-data/stock-prices-eod> | "Over 50 years of history"; adjusted + unadjusted + split ratios | 2026-07-26 | Read |
| <https://docs.intrinio.com/documentation/web_api/get_security_stock_prices_v2> | `adj_*` defined as splits **and** dividends | 2026-07-26 | Read |
| <https://docs.intrinio.com/documentation/web_api/get_stock_exchange_price_adjustments_v2> | `factor`, `dividend`, `split_ratio` exposed separately | 2026-07-26 | Read |
| <https://docs.intrinio.com/terms>, <https://intrinio.com/guides/starter-plan> | Internal-use default, non-display starter, AI/derived-data clause | 2026-07-26 | Read (proxy) |
| <https://help.intrinio.com/eod-market-data-faqs> | Unconfirmed vs confirmed EOD timing | 2026-07-26 | Read (proxy) |
| <https://norgatedata.com/stockmarketpackages.php> | Package prices and history depth (to 1950) | 2026-07-26 | Read |
| <https://norgatedata.com/data-content-tables.php> | `CAPITAL` adjustment mode; consolidated-tape wording | 2026-07-26 | Read |
| <https://norgatedata.com/subscribe/eula.php> | Commercial-use ban, redistribution ban, derived-data deletion | 2026-07-26 | Read |
| <https://norgatedata.com/ndu-faq.php> | Corrections policy | 2026-07-26 | Read |
| <https://finnhub.io/terms-of-service> | Personal-use-only, derived-results redistribution ban | 2026-07-26 | Read (proxy) |
| <https://finnhub.io/pricing-stock-api-market-data>, <https://finnhub.io/pricing> | Market-data tiers, 40+ yr history; the two pages disagree | 2026-07-26 | Read (proxy) |
| <https://github.com/finnhubio/Finnhub-API/issues/336> | Adjustment-flag no-op report | 2026-07-26 | Search-sourced — **UNVERIFIED** |
| <https://alpaca.markets/data> | Free/paid tiers, 7+ yr history, SIP vs IEX | 2026-07-26 | Read |
| <https://docs.alpaca.markets/us/docs/about-market-data-api> | `adjustment` = raw/split/dividend/all | 2026-07-26 | Read |
| <https://docs.alpaca.markets/us/docs/market-data-faq> | SIP ~100% vs IEX ~2.5%; condition-level daily high/low rules | 2026-07-26 | Read |
| <https://marketstack.com/pricing>, <https://marketstack.com/faq> | Tiers; Tiingo as upstream; adjustment methodology undocumented | 2026-07-26 | Read (proxy) |
| <https://marketstack.com/agreement> | Display-rights clause | 2026-07-26 | Read — **clause not found in body; UNVERIFIED** |
| <https://site.financialmodelingprep.com/pricing-plans> | FMP tiers, history, rate limits | 2026-07-26 | Read (proxy) |
| FMP terms-of-service / acceptable-data-use-policy | FMP licensing | 2026-07-26 | **HTTP 403 — including via proxy** |
| <https://massive.com/pricing> | Massive individual tiers, limits, "Individual use only" | 2026-07-26 | Read |
| <https://massive.com/business> | Stocks Business $1,999/mo, add-ons, exchange-fee note, startup discount | 2026-07-26 | Read |
| <https://massive.com/blog/polygon-is-now-massive> | Rebrand | 2026-07-26 | Read (via search) |
| <https://polygon.io/pricing> | Rebrand corroboration | 2026-07-26 | **HTTP 301 → massive.com/pricing** |
| <https://massive.com/legal/individuals-terms-of-service> | Personal/non-commercial restriction | 2026-07-26 | Read |
| <https://massive.com/legal/businesses-terms-of-service> | Edge Users, derivative-works clause | 2026-07-26 | Read |
| <https://massive.com/legal/market-data-terms-of-service> | Display-use-only, derivative works | 2026-07-26 | Read (partial) |
| <https://massive.com/knowledge-base/article/how-can-i-redistribute-massives-market-data> | Business product required to redistribute | 2026-07-26 | Read |
| <https://massive.com/knowledge-base/article/how-much-historical-stock-data-does-polygon-have> | History from 2004 | 2026-07-26 | Read |
| <https://massive.com/knowledge-base/article/how-does-polygon-create-the-open-high-low-close-volume-aggregate-bars> | Wick construction, sale conditions, SIP consolidated | 2026-07-26 | Read |
| <https://massive.com/docs/rest/stocks/aggregates/custom-bars> | `adjusted` parameter semantics | 2026-07-26 | Read |
| <https://massive.com/docs/rest/stocks/aggregates/daily-market-summary> | Whole-market daily endpoint | 2026-07-26 | Read |
| <https://massive.com/docs/rest/stocks/corporate-actions/splits> | Splits fields, history to 1978 | 2026-07-26 | Read |
| <https://massive.com/docs/rest/stocks/corporate-actions/ticker-events> | Symbol-change events | 2026-07-26 | Read |
| <https://massive.com/blog/aggregate-bar-delays> | Restatement/late-trade policy | 2026-07-26 | Search summary only |
| <https://eodhd.com/pricing> | Personal tiers, "30+ years", commercial-use pointer | 2026-07-26 | Read |
| <https://eodhd.com/commercial-pricing> | Internal Use $399, Enterprise $2,499, display restriction | 2026-07-26 | Read |
| <https://eodhd.com/financial-apis/terms-conditions> | Professional/Non-Professional, redistribution, storage | 2026-07-26 | Read |
| <https://eodhd.com/financial-apis/commercial-vs-personal-license-use> | Commercial definition, onboarding | 2026-07-26 | Read |
| <https://eodhd.com/financial-apis/api-for-historical-data-and-volumes> | Raw OHLC vs adjusted_close, `splitadjusted`, EOD timing | 2026-07-26 | Read |
| <https://eodhd.com/financial-apis/api-splits-dividends> | Splits/dividends coverage | 2026-07-26 | Read |
| <https://eodhd.com/financial-academy/financial-faq/historical-stock-prices-for-delisted-companies> | "from January 2000" contradiction; delisted | 2026-07-26 | Search summary |
| <https://eodhd.com/lp/b2b-solution> | Commercial-use definition | 2026-07-26 | Read |
| <https://www.tiingo.com/pricing> | Tiers, limits, "Internal Use Only" | 2026-07-26 | Read |
| <https://app.tiingo.com/tos/> | Internal consumption, derived data, storage, attribution | 2026-07-26 | Read |
| <https://twelvedata.com/pricing> | Tiers, credits, internal display/non-display wording | 2026-07-26 | Read |
| <https://twelvedata.com/terms> | External display, non-display, derived data, caching | 2026-07-26 | Read |
| <https://twelvedata.com/enterprise> | Redistribution add-on price | 2026-07-26 | **HTTP 404** |
| <https://www.alphavantage.co/premium/> | Premium tiers and rate limits | 2026-07-26 | Read |
| <https://www.alphavantage.co/terms_of_service/> | Personal/non-commercial licence, Professional criteria | 2026-07-26 | Read (PDF, text extracted) |
| <https://databento.com/pricing> | Pay-as-you-go, subscription tiers, 24h redistribution | 2026-07-26 | Read |
| <https://databento.com/equities> | History "Since 2018", derived-use licence | 2026-07-26 | Read |
| <https://databento.com/blog/understanding-exchange-fees> | **T+1 exemption**; Nasdaq fee example | 2026-07-26 | Read |
| <https://databento.com/docs/faqs/licensing> | Full licensing FAQ | 2026-07-26 | Truncated — not usable |
| <https://www.quantrocket.com/pricing/data/sharadar/> | Sharadar bundle contents, 1998/1957 dates | 2026-07-26 | Read (third-party) |
| <https://data.nasdaq.com/databases/SEP> | Sharadar SEP specs and price | 2026-07-26 | **Not readable — content behind login** |
| <https://site.financialmodelingprep.com/pricing-plans> | FMP pricing | 2026-07-26 | **HTTP 403** |
| <https://commercial.cnn.com/terms-of-use/> | CNN commercial terms | 2026-07-26 | Read |
| <https://www.cnn.com/terms> | CNN consumer ToU | 2026-07-26 | **HTTP 451** |
| <https://www.cboe.com/terms/> | Display + derivative-work prohibition | 2026-07-26 | Read |
| <https://www.cboe.com/us/indices/accessing-index-data> | Licensing route (quote only) | 2026-07-26 | Read |
| <https://www.cboe.com/tradable_products/vix/vix_historical_data/> | Free VIX history, informational-use disclaimer | 2026-07-26 | Read |
| <https://fred.stlouisfed.org/docs/api/terms_of_use.html> | Third-party-owned series disclaimer, attribution | 2026-07-26 | Read (rendered; direct fetch 403) |
| <https://alternative.me/crypto/fear-and-greed-index/> | Commercial use with attribution (crypto only) | 2026-07-26 | Read |
| <https://sentimentrader.com/pricing>, <https://sentimentrader.com/indicator-api> | Sentiment vendor pricing | 2026-07-26 | Read |
| <https://www.aaii.com/privacy/tos> | AAII ToS | 2026-07-26 | Read (rendered; direct fetch 403) |
| <https://feargreedchart.com/api-docs> | Free F&G alternative | 2026-07-26 | Read |
| <https://pro.macrotrends.net/stocks/charts/INTC/intel/stock-price-history> | Intel 2000 ATH illustration | 2026-07-26 | Secondary — **UNVERIFIED** |

---

## 15. Cross-references

- Research instrument: [`data-provider-research.md`](data-provider-research.md) (R1–R8)
- Price-adjustment basis: [`human-decisions.md`](human-decisions.md) — HD-01
- Provider selection + spend (**PENDING**): [`human-decisions.md`](human-decisions.md) — HD-06
- Constituents/delisted need: [`human-decisions.md`](human-decisions.md) — HD-07
- Sentiment gating: [`human-decisions.md`](human-decisions.md) — HD-08, HD-09
- As-of-time causality: [`human-decisions.md`](human-decisions.md) — HD-12;
  [`trendline-specification.md`](trendline-specification.md) §21
- Wick semantics: [`trendline-specification.md`](trendline-specification.md) §3, §4
- `data/` seam: [`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) §3.2, §9
- Sentiment design: [`market-sentiment-specification.md`](market-sentiment-specification.md) §2, §3
- Approval gate: [`../governance/approval-gate.md`](../governance/approval-gate.md) (GOV-013)
- Build freeze: [`../governance/build-freeze.md`](../governance/build-freeze.md) (GOV-015)
</content>
</invoke>
