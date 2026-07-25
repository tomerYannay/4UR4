# 4UR4 — Survivorship-Bias Findings (R4 / R5 / R7-constituents)

> **Status: RESEARCH / CONTEXT ONLY.** Produced under the
> [GOV-015](../governance/build-freeze.md) build-freeze as **freeze-permitted
> research**. This document **selects nothing, buys nothing, and commits
> nothing**.
>
> **Authority boundary (Product Owner, 2026-07-26, issue #23):** the author of
> this document was **not** authorized to select or acquire a dataset, commit
> spend, accept licensing terms, create accounts or API keys (including free
> ones), or redistribute restricted data. **No account was created, no terms
> were accepted, and no market data was downloaded.** Every figure below comes
> from a publicly readable page, cited with a retrieval date.
>
> **[HD-06](human-decisions.md) remains PENDING.**
> **[HD-07](human-decisions.md#hd-07--survivorship-bias-free-constituents--delisted-history--materiality-high)
> approved the *need*, not the spend** — acquisition remains
> **HUMAN-GATED ([GOV-013](../governance/approval-gate.md))**.
>
> **Scope:** answers [`data-provider-research.md`](data-provider-research.md)
> **R4** (point-in-time constituents), **R5** (delisted history), and the
> **constituent/delisted portion of R7** (redistribution). R1/R2/R3/R6/R8
> (OHLCV, corporate actions, sentiment, general redistribution, total cost) are
> **out of scope here** and researched separately.

---

## 0. How to read this document

**All retrieval dates in this document are 2026-07-25 / 2026-07-26** unless a
row says otherwise. Vendor pricing, coverage and terms change; every claim is
therefore anchored to a URL plus the date it was read, and **nothing is
asserted from prior knowledge**. Where a fact could not be reached from a
public page, it is recorded in [§8 — Verification gaps](#8-verification-gaps-what-could-not-be-confirmed)
rather than estimated.

Two methodological cautions apply to the evidence below and are stated up front
because they bear on how much weight the Product Owner should give it:

1. **Model-mediated extraction is not a verified read.** Several artifacts here
   were extracted from HTML tables by an automated reader. On one occasion
   during this research the reader **transposed the Added/Removed columns** of a
   third-party change log, which would have produced a confident but false
   finding. It was caught by re-reading the same page with an explicit
   column-labelling instruction. Any row below marked *unverified* has **not**
   been through that second read.
2. **A reconstructed membership list is not the same artifact as a licensed
   point-in-time one.** This distinction is the whole subject of §2 and is where
   survivorship bias re-enters after you think you have removed it.

---

## 1. Why this matters, and what the bias is worth in annualised return

4UR4 backtests a trendline-breakout strategy on "the S&P 500". If the backtest
universe is *today's* members, the index's failures have already been deleted
from the sample and its successes retained. The strategy is then measured on a
universe that was selected, in part, **by knowing the future**.

### 1.1 Published magnitude estimates

| Source | Population studied | Reported magnitude | Retrieved |
|---|---|---|---|
| Daniel, Sornette & Wöhrmann, *Look-Ahead Benchmark Bias in Portfolio Performance Evaluation*, arXiv:0810.1922 (submitted 2008-10-10) — [abs](https://arxiv.org/abs/0810.1922) | **S&P 500**, CRSP data 1926–2006, running top-500 US capitalisations | **"up to 8% annum for the S&P500 taken as the benchmark"**; also "a gross overestimation of performance metrics such as the Sharpe ratio as well as an underestimation of risk, as measured for instance by peak-to-valley drawdowns" | 2026-07-26 |
| Ranse, *Survivorship Bias in Emerging Market Small-Cap Indices: Evidence from India's NIFTY Smallcap 250*, arXiv:2603.19380 (submitted 2026-03-19) — [abs](https://arxiv.org/abs/2603.19380) | NIFTY Smallcap 250, 1,437 stocks, 2016–2025 | **"survivor-only backtesting overstates annual returns by 4.94 percentage points (23.3%) and Sharpe ratios by 0.097 (9.1%)"**; 82.5% turnover, of which delisted 16.1% | 2026-07-26 |
| Elton, Gruber & Blake, *Survivor Bias and Mutual Fund Performance*, Review of Financial Studies 9(4):1097–1120 (1996) — [publisher](https://academic.oup.com/rfs/article-abstract/9/4/1097/1580100) | US mutual funds | Frequently cited as ~0.9%–1.4%/yr overstatement; **the exact figure was not confirmed from the paper itself** (paywalled) — see [§8](#8-verification-gaps-what-could-not-be-confirmed) | 2026-07-26 |

**The decision-relevant number is the first row.** It is (a) about the S&P 500
specifically, (b) about exactly 4UR4's failure mode — using end-of-period
constituents rather than the constituents as of each historical date — and (c)
built on CRSP, the reference dataset for this question. Its headline is **up to
8 percentage points of annualised return**, which is larger than almost any
edge a breakout strategy could plausibly claim.

**Honest framing for the Product Owner:** "up to 8%" is an upper amplitude over
a long window and a particular construction, not a point estimate for a 4UR4
backtest. The defensible statement is: *the bias is of the same order as, or
larger than, the entire effect 4UR4 is trying to measure.* A backtest run
without point-in-time membership cannot distinguish "this strategy works" from
"this universe was chosen with hindsight."

### 1.2 A second-order point that is easy to miss

Delisted-name removal and index-membership drift are **two different biases**
and both must be fixed:

- Fixing **R4 only** (correct historical membership, but no price series for
  names that no longer trade) leaves the backtest unable to *hold* the members
  it correctly selected — positions in soon-to-fail names silently vanish.
- Fixing **R5 only** (delisted prices, but today's member list) still tests a
  hindsight-selected universe.

They are a package. HD-07 is correctly scoped as one decision covering both.

---

## 2. R4 — Point-in-time S&P 500 constituents

### 2.1 The artifact distinction that decides everything

There are three genuinely different things sold or given away under the label
"historical constituents":

| Artifact type | What it actually is | Fitness for an unbiased backtest |
|---|---|---|
| **Licensed point-in-time membership** | A vendor-maintained, dated membership state for every trading day, sourced under contract from the index provider | Fit for purpose |
| **Change-event log** | A list of add/remove events with effective dates, from which membership is *derived* by replaying backwards from today | Fit **only if the event log is complete**; silently biased if not |
| **Reconstructed snapshot history** | Membership inferred from public traces (wiki revisions, ETF holdings, filings) | Provisional; error rate grows with age |

The gap between rows 1 and 3 is precisely where survivorship bias re-enters
after you believe you have removed it. A change-event log that is missing 5% of
removals reintroduces a smaller version of the same bias, and — critically —
**the missing entries are not random**: the events most likely to be poorly
documented are the messy ones (bankruptcies, receiverships, distressed
takeunders), which are exactly the negative-return events whose absence causes
the bias.

### 2.2 Free / public sources

| Source | Granularity | Earliest coverage | What it costs | Reliability caveat |
|---|---|---|---|---|
| [Wikipedia, *List of S&P 500 companies*](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) — current table | Snapshot, today only | n/a | Free (CC BY-SA text) | States the index "comprises 503 common stocks which are issued by 500 large-cap companies" (retrieved 2026-07-26); no as-of date printed on the page |
| Same page, **"Selected changes"** table | Change events | **In the revision read on 2026-07-26 the detailed rows span 2024-04-01 → 2026-06-30 only**, plus a summary line "Between January 1, 1963, and December 31, 2014, 1,186 index components were replaced by other components." | Free | It is a **rolling, explicitly *selected*** table. Reconstructing 10+ years from it is not possible from the table alone |
| Same page, **MediaWiki revision history** | Dated snapshots | Practically usable to the mid-2000s; CIK column only added 2014 | Free | The method that actually works — see [§5.1](#51-e1--past-date-membership-snapshot-vs-today-worked-comparison) |
| [`fja05680/sp500`](https://github.com/fja05680/sp500) (MIT) | Dated snapshots + changes | 1996 | Free | README states only 487 symbols in the 1996 row and suggests dropping "the first ~5 years"; 1996–2019 base data inherited from a third-party book, unverified by the maintainer |
| [`bkestelman/sp500_historical_components`](https://github.com/bkestelman/sp500_historical_components) (MIT) | Dated snapshots via revision history | Not stated | Free | README: "The Wikipedia lists sometimes have errors and are not always up to date. Check the data for anomalies and use at your own risk." |
| [`hanshof/sp500_constituents`](https://github.com/hanshof/sp500_constituents) | Dated snapshots | 1996-01-02 | Free | Not independently assessed in this ticket |
| [Tickericons S&P 500 changes](https://tickericons.com/changes) | Change events | Earliest row 1976-07-01; page states **"402 changes since 1976, with 383 companies added and 379 removed"** | Free, "© 2026 Tickericons. All rights reserved."; no data licence stated | **402 events over 50 years is implausibly few** — Wikipedia alone attributes 1,186 replacements to 1963–2014, and 2025 alone had ~20. Treat as materially incomplete |
| SEC EDGAR — SPY / index-ETF holdings (N-PORT, CIK 0000884394) | Portfolio snapshots | N-PORT era | Free | **Quarterly, not monthly.** The SEC's move to public monthly N-PORT was **delayed to 2027-11-17** (fund groups ≥ $1bn) and **2028-05-18** (< $1bn) — [Federal Register, 2025-04-22](https://www.federalregister.gov/documents/2025/04/22/2025-06861/form-n-port-and-form-n-cen-reporting-guidance-on-open-end-fund-liquidity-risk-management-programs). ETF holdings ≈ index membership but are **not** the index |
| [S&P DJI press releases](https://press.spglobal.com/) | Authoritative per-event announcements | Long history | Free to read | The **authoritative** free source for a *specific* event, but there is no bulk export; verifying ~25 events/yr by hand is the cost |

**Blogged reconstruction methods and their own accuracy statements:**

- Robot Wealth, [*How To Get Historical S&P 500 Constituents Data For Free*](https://robotwealth.com/how-to-get-historical-spx-constituents-data-for-free/) (retrieved 2026-07-26): scrapes the current table and walks backwards through the "Selected changes" table to 1990. The author's own verdict: **"I've checked this against our data set and it's relatively accurate and complete up to about the year 2000. It gets less complete and accurate before then"**, and advises being **"increasingly wary about its accuracy the further back we go in time."**
- Riaz Arbi, [*Survivorship-bias free S&P 500 constituent lists*](https://riazarbi.github.io/quant/backtesting-sp500-constituent-history/) (retrieved 2026-07-26): combines iShares ETF holdings (back to 2007) with Wikipedia revision history, and — importantly for 4UR4 — matches securities by **CIK rather than ticker**, because "the symbol for META didn't exist" in 2019: "Back then, it was FB. The CIK, however, hasn't changed." Limitation reported: "the CIK column was only added in 2014, so you can't go further back than that."

**Finding (R4, free path):** a *usable* reconstruction back to roughly **2000**
is achievable at zero cost from Wikipedia revision history plus MIT-licensed
GitHub datasets. Before ~2000 the free path degrades, and no free source is
authoritative. **The free path is a research aid, not a product input.**

### 2.3 Paid / licensed sources

| Provider | Constituent history depth | Granularity | Price found (retrieved 2026-07-26) | Commercial/redistribution posture |
|---|---|---|---|---|
| **Norgate Data** — [packages](https://norgatedata.com/stockmarketpackages.php), [content tables](https://norgatedata.com/data-content-tables.php) | **S&P 500 constituents from Mar 1957**; DJIA from Jan 1950; 27 indices total | Per-bar membership ("was this stock in the index on that day") | US **Platinum USD 630 / 12 months**; US **Diamond USD 787.50 / 12 months** (6-month options USD 346.50 / 433.13) | **BLOCKING — see [§4.2](#42-vendor-terms-constituentdelisted-relevant)**. EULA is personal-use-only |
| **Siblis Research** — [historical component changes](https://siblisresearch.com/data/historical-component-changes/) | "Full historical component lists — including point-in-time summaries for historical dates"; depth **not stated on the page** | Point-in-time lists + add/remove events + official announcement dates + historical weightings for major indices | **USD 48/mo billed annually (USD 576/yr)**, or **USD 97/mo** monthly | Licence terms **not published on the page**; must be requested |
| **Sharadar** via Nasdaq Data Link (`SHARADAR/SP500`) — [QuantRocket listing](https://www.quantrocket.com/pricing/data/sharadar/) | **"S&P 500 Constituents (1957 - present)"** | Add/remove events + constituent state | **Login-gated** — "Log in or create account to see pricing", "Select license to see pricing", with **Professional / Non-Professional** licence types | Professional licence exists as a purchasable category — the most promising commercial-tier candidate found. **No account was created, so no price was obtained** |
| **EODHD** (Unicorn Bay S&P Global feed) — [product page](https://eodhd.com/lp/spglobal), [blog](https://eodhd.com/financial-apis-blog/sp-500-historical-constituents-data) | **Conflicting**: product page says **"12 years of historical events"** for S&P indices (2 years for Dow Jones); the blog says "from January 2000" | Change events with dates; historical snapshots stated to be S&P 500 only | **USD 29.99/mo** add-on ("$50 for the first 3 months") | Product page states **"We have a direct contract with S&P Global"** — the only vendor found making that claim explicitly. Personal-tier plans are marked personal use; commercial is quote-only |
| **Financial Modeling Prep** — [Historical S&P 500 API](https://site.financialmodelingprep.com/developer/docs/stable/historical-sp-500) | **Not stated anywhere on the docs page** — "additions and removals ... along with the reasons"; endpoint `/stable/historical-sp500-constituent` | Change events with reasons | Individual plans **USD 22 / 59 / 149 per month billed annually**; "Usage: Individual" on all four tiers | Personal plans explicitly forbid display; commercial requires a separate agreement — see [§4.2](#42-vendor-terms-constituentdelisted-relevant) |
| **CRSP** via WRDS — [SMU library note](https://library.smu.edu.sg/topics-insights/notes-and-thoughts-retrieving-historical-members-sp-500-wrds) | Daily SPX membership via `crsp_a_indexes.dsp500list_v2` / `dsp500list`; CRSP data begins 1925-12-31 | Daily membership | Institutional subscription, not publicly priced | [WRDS Terms of Use](https://wrds-www.wharton.upenn.edu/users/tou/): the service "is for academic and non-commercial research purposes only." **Not available to a commercial SaaS** |
| **S&P DJI direct** — [Data & index licensing](https://www.spglobal.com/spdji/en/about-us/data-index-licensing) | Authoritative | Packages offered at index level, **constituent data**, and/or corporate actions | Quote only | The source of truth; see [§4.1](#41-does-a-constituent-list-trigger-an-index-licence) |

**A structural datapoint worth the Product Owner's attention.** Index
constituent data is moving *behind* direct licensing, not away from it. From
the SMU Libraries note (retrieved 2026-07-26):

> "In July 2020 however the S&P Dow Jones Indices (SPDJI) constituent names data
> was removed from Compustat, due to SPDJI direct licensing. With the move, the
> constituents of S&P 500, along with other S&P indices, such as the S&P 1500
> Super Composite to name few, are no longer available via Compustat."

That is an index provider withdrawing membership data from a major redistributor
in order to license it directly. The likely direction of travel is **more**
restriction and **more** cost over time, not less.

### 2.4 Add/remove event coverage — earliest date by source

| Source | Earliest add/remove event coverage | Completeness claim | Basis |
|---|---|---|---|
| Norgate Data (Platinum/Diamond) | **Mar 1957** (S&P 500) | Vendor-asserted historically accurate constituents | Content tables page |
| Sharadar `SHARADAR/SP500` | **1957** | "historical additions to and removals from the S&P 500 index since 1957" | QuantRocket listing |
| CRSP via WRDS | 1925-12-31 (database); S&P 500 as such from 1957 | Daily membership tables | SMU library note |
| Siblis Research | **Not published** | "Full historical component lists" | Product page |
| EODHD S&P feed | **12 years** (page) / **2000** (blog) — unresolved | ~200+ changes, 90,000+ rows (blog) | Product page + blog |
| FMP | **Not published** | Adds/removes with reasons | API docs |
| Tickericons (free) | 1976-07-01 | 402 changes since 1976 — **implausibly low, treat as incomplete** | Page text |
| Wikipedia "Selected changes" (free) | 2024-04-01 in the revision read | Explicitly *selected*, not complete | Direct read, 2026-07-26 |
| Wikipedia revision history (free) | ~2000 usable; degrades before that | No completeness claim | Third-party validations above |

---

## 3. R5 — Delisted price history

### 3.1 Coverage by candidate

| Provider | Delisted names included? | Depth | Delisting **date** supplied? | Delisting **reason** supplied? | Adjusted series? |
|---|---|---|---|---|---|
| **Norgate Data** (Platinum/Diamond) | **Yes** — "Access to delisted securities and historical index constituents" | Content tables state **"25222 delisted securities from the start of 1950 to Sep 2022"**; price history to **1990** (Platinum) / **1950** (Diamond) | Yes — year and month of delisting are appended to the delisted symbol | **Not confirmed** from public pages | Not confirmed from public pages |
| **CRSP** | **Yes** — the reference implementation | From 1925 | Yes | **Yes — `DLSTCD`, a 3-digit delisting code**; "All coded delistings are categorized by the first digit"; performance-related delistings occupy codes 500 and 520–584 ([CRSP data-definitions guide](https://terpconnect.umd.edu/~wermers/ftpsite/fnce7200/data_defs_061899.pdf)) | Yes, incl. delisting returns — but see §3.3 |
| **Sharadar** (SEP / bundle) | **Yes** — "No survivorship bias: includes active and delisted tickers", "over 20,000 US companies" | **Prices from 1998** | Via `SHARADAR/TICKERS` / `ACTIONS` (not verified in this ticket) | Not verified | Not verified |
| **EODHD** | **Yes** — `exchange-symbol-list/US?...&delisted=1` returns "delisted (inactive) tickers **only**" | Not stated | **No.** Documented response fields are Code, Name, Country, Exchange, Currency, Type, Isin — **no delisting date field** | **No** | Not stated |
| **Massive** (formerly Polygon.io) | **Yes** — All Tickers endpoint, `active=false` | Tier-dependent: 2 / 5 / 10 / **"20+ Years Historical Data"** | **Yes** — `delisted_utc`, "The last date that the asset was traded" | **No** — no reason field exists in the response schema | Adjusted/unadjusted handled at the aggregates endpoint (out of scope here) |
| **Alpha Vantage** | **Yes** — `LISTING_STATUS` with `state=delisted` | `date` parameter supported for **any date later than 2010-01-01** | Yes (delisting date) | Not documented | n/a — this is a listing register, not prices |
| **FMP** | **Yes** — "Delisted Companies" and "Symbol Changes List" endpoints appear in the plan comparison | Not stated | Not verified | Not verified | Not verified |
| **Yahoo Finance / `yfinance`** | **NO — drops delisted names** | n/a | n/a | n/a | n/a |
| **Free "current constituents" scrapes generally** | **NO** | n/a | n/a | n/a | n/a |

### 3.2 The silent failure, named explicitly

**The single most common way this goes wrong is a provider that returns HTTP 200
and an empty or truncated series for a name that no longer trades.** Yahoo
Finance / `yfinance` — the default free source almost every retail project
starts on — is in this category. A [coverage study of ~2,000 tickers,
2000–2025](https://github.com/Neyt/yahoo-finance-coverage-study) found 63
tickers (3.2%) with **zero** Yahoo coverage, "primarily warrants, delisted
stocks, and special securities" (retrieved 2026-07-26).

There is no error. There is no warning. The backtest just quietly runs on the
survivors.

**Providers on the candidate list that must be assumed to drop delisted names
unless proven otherwise:** Yahoo Finance / `yfinance`, and any pipeline whose
universe is defined by "today's ticker list."

**Providers that explicitly retain delisted names:** Norgate (Platinum/Diamond
only — Silver and Gold do **not** include them), CRSP, Sharadar, EODHD,
Massive, Alpha Vantage (listing register), FMP.

**Note the tier trap:** Norgate Silver and Gold are described as
"currently-listed ... equities, indices & **current** index constituents". A
Norgate subscription is therefore *not* survivorship-bias-free by default — only
Platinum and Diamond are.

### 3.3 Two correctness traps in delisted price data

1. **Ticker reuse and remapping.** Delisted tickers get reassigned, and delisted
   companies get renamed. Both free reconstructions cited in §2.2 independently
   converged on the same fix: **join on CIK, not ticker.** 4UR4's data layer
   should carry a stable non-ticker identifier from day one. This is a design
   consequence of this research and belongs in the `data/` abstraction whenever
   the freeze lifts.
2. **The delisting return is often missing, and it is the one that matters.**
   Shumway, *The Delisting Bias in CRSP Data* (1997)
   ([PDF](https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf),
   retrieved 2026-07-26) documents that **"correct delisting returns are not
   available for most of the stocks that have been delisted for negative reasons
   since 1962"** and that "the omitted delisting returns are large." Even the
   gold-standard academic database has a residual bias here. A vendor that gives
   you a price series ending on the last trading day, with no terminal return,
   is understating the loss — for a strategy that *holds through* the failure,
   that error is systematically favourable.

   4UR4 does not currently specify how a position in a name that is delisted
   mid-trade is closed in a backtest. **That is an open specification gap this
   research surfaces**, and it is logged in [§9](#9-open-items-this-research-surfaces).

---

## 4. R7 (constituent / delisted portion) — redistribution and licensing

### 4.1 Does a constituent list trigger an index licence?

**Yes, on the evidence found — index membership is licensed separately from,
and more restrictively than, price data.**

The clearest primary source located is a real executed **Master Index License
Agreement** between S&P Opco, LLC (a subsidiary of S&P Dow Jones Indices LLC)
and Mutual of America Capital Management LLC, **effective 2019-07-01**, filed as
Exhibit 99.8(c) on SEC EDGAR
([source](https://www.sec.gov/Archives/edgar/data/1776030/000119312521050328/d83606dex998c.htm),
retrieved 2026-07-26). Its Exhibit A, clause 2 reads, verbatim:

> "**Index Data.** Licensee agrees and acknowledges that the provision of Index
> related data (e.g. index levels, index constituents, constituent weights,
> etc.) to Licensee will be contracted under and governed by the relevant S&P
> data license agreement (the "MSA"), which is separate from this Agreement and
> Order Schedule, and separate fees may be payable by Licensee to S&P or its
> affiliates under the MSA."

Read plainly: **an index licence and an index-*data* licence are two different
contracts with two different fees, and "index constituents" is named explicitly
as index data.**

S&P DJI's standard disclaimer states:

> "Redistribution or reproduction in whole or in part are prohibited without
> written permission of S&P Dow Jones Indices LLC."

This text appears on S&P DJI's own [Legal Disclaimers
page](https://www.spglobal.com/spdji/en/disclaimers/) and throughout its
methodology and brochure PDFs. **`spglobal.com` returned HTTP 403 to every
automated fetch attempted during this research**, so the sentence was verified
verbatim from a third-party reproduction of the S&P DJI disclaimer
([Calcalist](https://www.calcalistech.com/ctechnews/article/bjgc5hyyjg),
retrieved 2026-07-26) and corroborated across multiple S&P DJI-hosted documents
via search. This is a **partially verified** quote — see [§8](#8-verification-gaps-what-could-not-be-confirmed).

S&P DJI's own licensing page describes packages "offered at three levels: index,
constituent data, and/or corporate action information" — i.e. **constituent data
is a priced product line in its own right**.

**What this means for 4UR4 concretely.** Three distinct exposures, in increasing
order of risk:

| Use | Index-licence exposure | Assessment |
|---|---|---|
| Backtesting internally against historical S&P 500 membership, results never shown | Lowest — but still governed by whatever vendor licence supplied the membership | **Amber** — vendor terms decide, not S&P directly |
| Displaying a 4UR4 signal for a company that happens to be an index member, without naming the index | Low | **Green**, provided the *price* data licence permits display |
| Marketing or labelling the product as "S&P 500 scanner", showing "S&P 500 members", or displaying an index-derived breadth/regime statistic | Highest — uses both the **mark** and the **constituent data** | **Red** — assume a licence and fees are required |

The third row is not hypothetical for 4UR4: the vision is an S&P 500 scanner and
the sentiment/regime work contemplates breadth statistics computed over index
members. **A product decision to define the universe *without* reference to the
S&P 500 — e.g. "the 500 largest US listings by market capitalisation, computed
by 4UR4" — would materially reduce this exposure.** Note that the
Daniel/Sornette/Wöhrmann paper itself works with "the running top 500 US
capitalizations" rather than licensed membership, which is a live demonstration
that rigorous work is possible on a self-defined universe. This is offered as an
**option for the Product Owner**, not a recommendation to change the product.

### 4.2 Vendor terms (constituent/delisted-relevant), quoted

All retrieved 2026-07-26.

**Norgate Data** — [EULA](https://norgatedata.com/subscribe/eula.php). **This is
a blocking finding.** Clause 8, verbatim:

> "The Licensee may use the Data for a personal purpose such as investment or
> trading.
> The Licensee will not:
> (i) redistribute the Data in any way or form except where express permission
> has been sought and obtained to publish limited extracts from it.
> (ii) use the Data to establish, maintain or provide a market for trading in
> securities, or as the basis for a financial instrument, or as the basis for
> settlement of a contract.
> (iii) **use the Data for any other commercial purpose.**
> (iv) use the Data in any manner that may be directly or indirectly competitive
> with the operations of Norgate or its associates."

Clause 2(i) limits installation to "two computers that are normally accessed by
the Licensee **for personal use**". Clause 21 requires deletion of "all copies
of the Data, **including Derived Data**" when a subscription lapses — which
would reach 4UR4's computed trendlines and scores. Clause 13 states
"Reproduction of any information obtained from any S&P/ASX Index in any form is
prohibited except with the written permission of S&P Dow Jones Indices." **The
EULA read on 2026-07-26 contains no commercial or business licence option.**

> **Conclusion: Norgate has the best constituent history found (S&P 500 to Mar
> 1957) at the lowest verified price (USD 630–787.50/yr), and its licence
> appears to forbid the use 4UR4 needs.** If the Product Owner wants Norgate,
> the path is to *ask Norgate for a commercial licence*, not to subscribe.

**EODHD** — [Terms and Conditions](https://eodhd.com/financial-apis/terms-conditions),
[Commercial vs Personal](https://eodhd.com/financial-apis/commercial-vs-personal-license-use).
Non-Professional Users are prohibited from "Selling, reselling, retransmitting,
redistributing, **displaying**, or granting access to the Information or
Services." Professional Users **may request written approval** to "sell, resell,
retransmit, redistribute, display, or grant access to EOD Historical Data
Information or Services in a repackaged form." Definitions: Professional User =
"any regulated individual, institution, or business"; Non-Professional =
"any non-regulated user e.g. a retail user." The pricing page marks every listed
plan **"Personal use"**, and the ALL-IN-ONE tier states "For commercial use,
choose Startups & Enterprise Data Solution Plan." Commercial onboarding is a
quote process ("in as little as 3 business days") and EODHD states it is
"required to report all commercial users of exchange data to the relevant
exchanges."

**Storage clause worth flagging to the Product Owner:** under "Data Storage and
Deletion", subscribers may retain data "during the active subscription period"
and on termination must "delete all copies of the data in their possession
within one (1) month." **A 4UR4 historical archive built on EODHD is not
ownable — it evaporates with the subscription.** The same is true of Norgate
(clause 21). This is a strategic, not merely legal, consideration: it makes the
data a rental, and it makes provider switching a re-ingestion project.

**Financial Modeling Prep** — [Terms of Service](https://site.financialmodelingprep.com/terms-of-service),
last updated 2023-08-01. Clause 2.2.1 (Personal Use), verbatim:

> "This license may only be used by a Customer who is an individual, and strictly
> for their own personal, non-business and non-commercial purposes. In no event
> may the Customer use this licence on behalf of a company, partnership,
> organization, group, entity or any other third party. This license is personal
> to the Customer, and the Customer may not share FMP Services or Data, resell,
> permit other users access to our Services through the Customer's account,
> integrate the Data or Services into any tools or applications accessible by
> any third parties, or use the Services to host, share, display, or provide
> content for others."

Clause 2.2.2 (Data Display), verbatim:

> "Without a specific agreement with FMP, customers are prohibited from
> showcasing FMP Services or Data on platforms including but not limited to
> websites, blogs, software products, or applications designed for utilization
> by multiple individuals, irrespective of whether such usage is complimentary
> or paid..."

Clause 2.6.1 prohibits "resell, sublicense, distribute or otherwise provide
access to The Services, **or data or information contained in or derived from
The Services**, to any third party". FMP's own pricing page states:
**"Displaying or redistributing data sourced from FMP requires a specific Data
Display and Licensing Agreement with FMP."** Its
[Enterprise page](https://site.financialmodelingprep.com/enterprise) lists
"Display and Redistribution" as an enterprise feature, priced by contact form.

**Massive (formerly Polygon.io)** — [pricing](https://massive.com/pricing).
Every listed Stocks tier, including paid ones, carries **"Individual use only"**
and the page footnotes **"Non-pros only"**. Commercial use routes to
[Business pricing](https://massive.com/business), which does not publish terms
or rates. Massive does **not** appear to offer index constituent data at all —
its Indices product is index *levels*, and no constituent endpoint was found.

**WRDS / CRSP** — [Terms of Use](https://wrds-www.wharton.upenn.edu/users/tou/):
the service "is for academic and non-commercial research purposes only."
**Structurally unavailable to 4UR4 as a commercial product.** Worth stating
plainly because CRSP is the dataset every academic estimate of this bias is
built on, and it is the one 4UR4 cannot have.

**Free reconstructions** — MIT-licensed GitHub datasets
(`fja05680/sp500`, `bkestelman/sp500_historical_components`) are freely
redistributable *as code and data artifacts*. Wikipedia text is CC BY-SA.
**Neither licence, however, can grant rights S&P DJI may hold in the underlying
membership facts**, and neither carries any accuracy warranty — both READMEs
disclaim it. Legal counsel, not this document, should assess whether a
reconstructed membership list is a derivative of S&P's licensed data.

### 4.3 Red / amber / green summary (constituent + delisted only)

| Source | Backtest-only internal use | User-facing display / SaaS redistribution |
|---|---|---|
| Norgate Data | **Red** — EULA clause 8(iii) bars "any other commercial purpose" | **Red** |
| CRSP / WRDS | **Red** — academic & non-commercial only | **Red** |
| FMP (individual plans) | **Red** — 2.2.1 bars business use | **Red** without a Data Display and Licensing Agreement |
| FMP Enterprise | Not verified | **Amber** — "Display and Redistribution" advertised; terms by quote |
| EODHD (personal plans) | **Red** — plans marked personal use | **Red** — display explicitly prohibited for Non-Professionals |
| EODHD commercial/B2B | Not verified | **Amber** — repackaged redistribution possible with prior written approval |
| Massive (individual) | **Red** — "Individual use only" | **Red** |
| Massive Business | Not verified | **Amber** — no constituent data anyway |
| Sharadar via Nasdaq Data Link | **Amber** — a Professional licence category exists | **Amber** — terms not readable without an account |
| Siblis Research | **Amber** — terms not published | **Amber** |
| S&P DJI direct | **Green** by construction | **Green** by construction — at S&P DJI's price |
| Wikipedia / MIT GitHub reconstructions | **Green** for internal research | **Amber** — no warranty; underlying-rights question unresolved |

---

## 5. Evidence artifacts

### 5.1 E1 — Past-date membership snapshot vs today (worked comparison)

**Method.** Two dated snapshots of the same public artifact were retrieved and
compared. No account, no API key, no paid data.

| Snapshot | Artifact | Retrieved |
|---|---|---|
| **A (past)** | Wikipedia *List of S&P 500 companies*, **revision id 697200065**, timestamp **2015-12-28T23:11:35Z** ([permalink](https://en.wikipedia.org/w/index.php?title=List_of_S%26P_500_companies&oldid=697200065)) — states "the index contains 505 stocks" | 2026-07-26 |
| **B (today)** | Same page, current revision ([link](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)) — states the index "comprises 503 common stocks which are issued by 500 large-cap companies" | 2026-07-26 |

The revision id was resolved via the MediaWiki API
(`rvstart=2016-01-01T00:00:00Z&rvdir=older`), which is the mechanism that makes
a *dated* free snapshot possible at all.

**Scope of the comparison.** A full 505-vs-503 diff was **not** attempted,
because the extraction method (§0, caution 1) is not reliable enough at that
volume to publish as evidence. Instead the comparison is restricted to the
**"A" alphabetical block** of the table — a bounded, checkable slice — and every
apparent difference is then adjudicated individually.

**Snapshot A, "A" block (2015-12-28), 56 entries:**
`MMM, ABT, ABBV, ACN, ACE, ATVI, ADBE, ADT, AAP, AES, AET, AFL, AMG, A, GAS,
APD, ARG, AKAM, AA, AGN, ALXN, ALLE, ADS, ALL, GOOGL, GOOG, MO, AMZN, AEE, AAL,
AEP, AXP, AIG, AMT, AMP, ABC, AME, AMGN, APH, APC, ADI, AON, APA, AIV, AAPL,
AMAT, ADM, AIZ, T, ADSK, ADP, AN, AZO, AVGO, AVB, AVY`

**Snapshot B, "A" block (2026-07-26), 56 entries:**
`MMM, AOS, ABT, ABBV, ACN, ADBE, AMD, AES, AFL, A, APD, ABNB, AKAM, ALB, ARE,
ALGN, ALLE, LNT, ALL, GOOGL, GOOG, MO, AMZN, AMCR, AEE, AEP, AXP, AIG, AMT,
AWK, AMP, AME, AMGN, APH, ADI, AON, APA, APO, AAPL, AMAT, APP, APTV, ACGL, ADM,
ARES, ANET, AJG, AIZ, T, ATO, ADSK, ADP, AZO, AVB, AVY, AXON`

**Raw set difference (in A, not in B) — 18 tickers:**
`ACE, ATVI, ADT, AAP, AET, AMG, GAS, ARG, AA, AGN, ALXN, ADS, ABC, APC, AIV, AN,
AAL, AVGO`

**Adjudication.** Each is checked against snapshot B's *full* table and against
an independent source. This is where the reconstruction problem becomes visible.

| Ticker (2015) | Actually removed? | Date / event | Source | Verification status |
|---|---|---|---|---|
| `AVGO` Avago Technologies | **NO — false positive** | Renamed Broadcom; still an index member, just re-sorted out of the "A" name-block | Snapshot B full table lists "Broadcom" (AVGO), Information Technology | **Verified** |
| `ABC` AmerisourceBergen | **NO — false positive** | Renamed Cencora (COR); still an index member | Snapshot B full table lists "Cencora" (COR) | **Verified** |
| `ALXN` Alexion Pharmaceuticals | Yes | Removed effective **2021-07-21**, replaced by Moderna (MRNA) after AstraZeneca's acquisition | S&P DJI announcement PDF `20210715-1419561` | **Verified** |
| `AGN` Allergan | Yes | Removed **2020-05-12**, replaced by DexCom (DXCM); "Allergan acquired by AbbVie" | Tickericons change log | Single free source |
| `AAP` Advance Auto Parts | Yes — absent from snapshot B | Removed **2023-08-25**, Kenvue (KVUE) added | Tickericons change log | Single free source |
| `AA` Alcoa Inc | Yes | **2016-11-01**, Arconic (ARNC) added; "AA spins off ARNC" | Tickericons change log | Single free source |
| `ACE` ACE Limited | Yes | **2016-01-19**; "EXR replaces ACE as ACE Ltd acquires Chubb and retains the CB ticker, giving up ACE" | Tickericons change log | Single free source |
| `AAL` American Airlines Group | Yes — absent from snapshot B | Removal date **not independently verified** | — | **UNVERIFIED** |
| `ATVI` Activision Blizzard | Yes — absent from snapshot B | Microsoft acquisition; date **not independently verified** | — | **UNVERIFIED** |
| `ADT`, `AET`, `AMG`, `GAS`, `ARG`, `ADS`, `APC`, `AIV`, `AN` | Yes — absent from snapshot B | Dates and reasons **not independently verified in this ticket** | — | **UNVERIFIED** |

**What E1 demonstrates — this is the finding, not the table.**

1. **The index really does churn this hard.** In one alphabetical block, over ten
   and a half years, **16 of 56 names (29%)** genuinely left. Extrapolated, the
   membership of the S&P 500 today is materially different from 2015's. A
   backtest run on snapshot B and applied to 2016 data is testing a universe
   that did not exist.
2. **Reconstruction produces false positives, and they look exactly like true
   ones.** Two of the 18 apparent removals — `AVGO` and `ABC` — are **renames of
   companies that never left the index**. A naive diff would have deleted
   Broadcom and Cencora from the historical universe. That is not a small error:
   Broadcom is one of the largest constituents by weight in snapshot B.
3. **Verification does not scale by hand.** Of 18 candidate diffs in one
   alphabetical block, **2 were resolved as false positives and 5 dated to a
   source within this research session; 11 remain unverified.** Extrapolating
   that ratio across the full index and a multi-year backtest window is the
   honest argument for a licensed dataset: the free path's true cost is not $0,
   it is *analyst-hours per event, forever, with a residual error rate nobody
   measures.*

### 5.2 E2 — Add/remove event coverage, fully enumerated (2026 YTD)

To show what *complete* event coverage looks like at short horizons, here is the
**entire** set of S&P 500 membership changes with effective dates in 2026 up to
the retrieval date, from Wikipedia's "Selected changes" table (retrieved
2026-07-26). **13 events in under seven months** — the churn rate a backtest
must model.

| Effective date | Added | Removed | Stated reason |
|---|---|---|---|
| 2026-06-30 | — | CAG (Conagra Brands) | Market capitalization change |
| 2026-06-29 | HONA (Honeywell Aerospace) | — | Honeywell spun off Honeywell Aerospace |
| 2026-06-22 | MRVL (Marvell Technology) | POOL (Pool Corporation) | Market capitalization change |
| 2026-06-22 | FLEX (Flex Ltd.) | CPB (Campbell's) | Market capitalization change |
| 2026-06-02 | — | EPAM (EPAM Systems) | Market capitalization change |
| 2026-06-01 | FDXF (FedEx Freight) | — | FedEx Corp. spun off FedEx Freight Holding |
| 2026-05-07 | VEEV (Veeva Systems) | CTRA (Coterra Energy) | Devon Energy acquired Coterra Energy |
| 2026-04-09 | CASY (Casey's) | HOLX (Hologic) | Blackstone and TPG acquired Hologic |
| 2026-03-23 | VRT (Vertiv) | MTCH (Match Group) | Market capitalization change |
| 2026-03-23 | LITE (Lumentum) | MOH (Molina Healthcare) | Market capitalization change |
| 2026-03-23 | COHR (Coherent Corp.) | LW (Lamb Weston) | Market capitalization change |
| 2026-03-23 | SATS (EchoStar) | PAYC (Paycom) | Market capitalization change |
| 2026-02-09 | CIEN (Ciena) | DAY (Dayforce) | Thoma Bravo acquired Dayforce |

Two structural observations for the engine, both visible in this table alone:

- **Unpaired events exist.** Four of the 13 rows have an add with no removal or a
  removal with no add (spin-offs and one-sided market-cap moves). A membership
  model that assumes add/remove pairs will drift out of 500 within a year.
- **Corporate actions and membership are entangled.** Spin-offs (HONA, FDXF)
  create *new* members from *existing* members. This is the seam between R3
  (corporate actions, out of scope here) and R4, and 4UR4's data layer will have
  to reconcile them.

For contrast: the 2026-03-23 rebalance events above are corroborated by the S&P
DJI press release [*Vertiv Holdings, Lumentum Holdings, Coherent, and EchoStar
Set to Join S&P 500*](https://press.spglobal.com/2026-03-06-Vertiv-Holdings,-Lumentum-Holdings,-Coherent,-and-EchoStar-Set-to-Join-S-P-500-Others-to-Join-S-P-100,-S-P-MidCap-400,-and-S-P-SmallCap-600),
dated 2026-03-06 — the authoritative artifact, one event at a time.

### 5.3 E3 — Documented delisted-name history example: First Republic Bank

A name that entered the index, was held by any index-following strategy, and
then ceased to exist — the exact case a survivorship-biased universe erases.

| Event | Date | Detail | Source |
|---|---|---|---|
| **Added to S&P 500** | Announced **2018-12-27**, effective **2019-01-02** | First Republic Bank (NYSE: FRC) replaced SCANA Corporation, which Dominion Energy was acquiring | [S&P DJI press release](https://press.spglobal.com/2018-12-27-First-Republic-Bank-Set-to-Join-S-P-500) |
| **Closed / seized** | **2023-05-01** | "the FDIC announced that First Republic had been closed and sold to JPMorgan Chase" | [Wikipedia, *First Republic Bank*](https://en.wikipedia.org/wiki/First_Republic_Bank) |
| **NYSE delisting announced, trading suspended** | **2023-05-02** | NYSE announced it would delist FRC; trading suspended immediately | Reported 2023-05-02; **exact SEC Form 25 date not verified** |
| **Removed from S&P 500** | Announced **2023-05-01**, effective **prior to the open on 2023-05-04** | Axon Enterprise (AXON) replaced FRC. Verbatim reason: "The Federal Deposit Insurance Corp. (FDIC) announced that it has taken First Republic Bank into FDIC Receivership and therefore First Republic Bank is no longer eligible for inclusion." | [S&P DJI press release](https://press.spglobal.com/2023-05-01-Axon-Enterprise-Set-to-Join-S-P-500-STAG-Industrial-to-Join-S-P-MidCap-400) |
| **Post-delisting trading** | 2023 → present | Now quoted OTC / Expert Market under a **different ticker, `FRCB`**; 52-week range shown as 0.0001–0.3006 | [stockanalysis.com/stocks/frc/](https://stockanalysis.com/stocks/frc/), retrieved 2026-07-26 |

**Why this one example carries most of the R5 argument:**

- **FRC was in the index for 4 years and 4 months.** Any backtest over 2019–2023
  on today's member list never sees it — not the entry, not the run-up, not the
  collapse.
- **The ticker changed at delisting** (`FRC` → `FRCB`). A pipeline keyed on
  ticker either finds nothing or, worse, finds the *wrong* instrument. This is
  the concrete case for the CIK-based identity discussed in §3.3.
- **The equity went to approximately zero, not to a merger price.** The terminal
  return is the entire economic content of the event, and it is exactly the
  number §3.3 warns is most often missing.
- **Both S&P DJI press releases — the add and the remove — are free and
  authoritative.** Constructing this record cost nothing but time. Doing it for
  every removal since 1990 is the labour a paid dataset replaces.

**Not verified:** whether any specific candidate provider returns a complete,
adjustment-correct `FRC`/`FRCB` daily series through 2023-05-01 including a
terminal value. **Confirming this would have required creating accounts and
pulling data, which was outside the authority granted for this ticket.** It is
the single highest-value item for a trial-based evaluation once the Product
Owner authorises one — see [§9](#9-open-items-this-research-surfaces).

---

## 6. Ranked options and cost scenarios

**All prices below are as retrieved on 2026-07-26 and are list prices for
personal/individual tiers unless stated.** Commercial-tier pricing for every
vendor examined is quote-only; **no quote was requested, because requesting one
would begin a commercial engagement this ticket has no authority to begin.**

| # | Option | Constituent history | Delisted history | Verified cost / yr | Redistribution-safe for SaaS? |
|---|---|---|---|---|---|
| 1 | **Sharadar bundle** (Nasdaq Data Link) | **1957–present** | Prices **1998–present**, active + delisted | **Unknown — login-gated** | **Possibly** — a Professional licence category exists |
| 2 | **Siblis Research** constituents + a separate delisted price source | Depth not published | Not offered — needs pairing | **USD 576** (annual billing) + price source | Unknown — terms not published |
| 3 | **EODHD** commercial tier (EOD + Fundamentals + S&P add-on) | 12 yrs (page) / 2000 (blog) | Yes, but **no delisting date or reason field** | Personal-tier equivalent ≈ **USD 1,159**; commercial by quote | **Possibly**, with prior written approval |
| 4 | **FMP Enterprise** | Depth not published | Endpoints exist | Individual tiers **USD 264 / 708 / 1,788**; enterprise by quote | **Possibly** — "Display and Redistribution" advertised |
| 5 | **S&P DJI direct** constituent-data licence + a price vendor | Authoritative, full | Via price vendor | Quote only; expect institutional pricing | **Yes, by construction** |
| 6 | **Norgate Platinum / Diamond** | **1957–present**, best found | **25,222 names, 1950–Sep 2022** | **USD 630 / 787.50** — cheapest by far | **NO** — EULA clause 8(iii) |
| 7 | **CRSP / WRDS** | 1925–present, reference quality | Reference quality, with `DLSTCD` reasons | Institutional | **NO** — academic & non-commercial only |
| 8 | **Free reconstruction** (Wikipedia revisions + MIT datasets + SEC/S&P press releases) | ~2000 usable, degrading | **None** — must pair with a delisted-capable price source | **USD 0** | Ambiguous; no warranty |

### 6.1 Three scenarios a decision can actually be made against

**Scenario A — "Honest internal backtest, nothing shipped." ≈ USD 0–800/yr.**
Free reconstruction for membership (2000-onwards only), paired with a
delisted-capable price source. Every backtest output labelled
**biased/provisional** per HD-07's safe default. Buys correctness of *direction*,
not of *magnitude*. Appropriate while Phase 4 is exploratory.

**Scenario B — "Trustworthy backtest, still nothing shipped." ≈ USD 600–1,800/yr,
plus an unknown commercial uplift.** Option 1 or 2 above. This is the smallest
spend that makes a Confidence-v1 lift claim defensible. **The blocker is not
money, it is that the two cheapest good datasets (Norgate, CRSP) are both
licence-barred from commercial use, and the ones that are not are price-opaque.**

**Scenario C — "Shippable, user-facing, index-referencing SaaS." Unknown, likely
four to five figures per year.** Requires a commercial data licence *and*, if
the product names or displays the index, an S&P DJI index/constituent-data
licence with separate fees (§4.1). **No figure should be assumed until quotes
exist.**

### 6.2 Recommendation

Offered as a **recommendation only**. It selects nothing and authorises nothing.

1. **Do not subscribe to Norgate**, despite it being the cheapest and deepest
   option found, unless a commercial licence is first negotiated. Subscribing on
   the published EULA and using the data in 4UR4 would be a licence breach on
   the plain text of clause 8(iii).
2. **Request quotes from Sharadar/Nasdaq Data Link and Siblis Research** — the
   two candidates whose data shape fits and whose commercial posture is not
   already disqualifying. **This requires Product Owner action**; an agent
   cannot open a commercial conversation.
3. **Treat the S&P 500 branding decision as a product decision, not a data
   decision** (§4.1). Defining 4UR4's universe as a self-computed top-500 US
   listing set would sidestep the index-licence question entirely and cost
   nothing but a naming change. This is the highest-leverage, lowest-cost
   mitigation identified in this research and deserves an explicit ruling.
4. **In the interim, mark every Phase 4 backtest run without point-in-time
   membership as biased/provisional**, exactly as HD-07's safe default already
   requires.
5. **Add a stable non-ticker identity (CIK) to the `data/` abstraction's design**
   before any ingestion is built. This is free to decide now and expensive to
   retrofit.

> **HD-07 acquisition remains HUMAN-GATED (GOV-013).** Nothing in this section is
> an authorisation, a purchase, or an acceptance of terms. **HD-06 remains
> PENDING.**

---

## 7. Answers to the ticket's acceptance criteria

| Acceptance criterion | Where answered |
|---|---|
| R4 and R5 findings documented with the specified evidence artifacts | §2, §3, §5 |
| A past-date membership snapshot is compared against today's members | §5.1 — 2015-12-28 revision 697200065 vs 2026-07-26, worked and adjudicated |
| Delisted-coverage depth and add/remove event coverage are documented | §3.1, §2.4, §5.2 |
| Redistribution/licensing terms for constituent data quoted with source+date | §4.1, §4.2 — all quotes carry a URL and retrieval date |
| Paid/licensed items flagged HUMAN-GATED (GOV-013); commits nothing | Header, §6.2 |

---

## 8. Verification gaps — what could not be confirmed

Recorded as findings. A documented gap is more useful than a confident guess.

| # | Gap | Why it could not be closed |
|---|---|---|
| G1 | **Sharadar / Nasdaq Data Link pricing** | Behind a login: "Log in or create account to see pricing." Account creation was outside the granted authority |
| G2 | **Siblis Research licensing terms, history depth, and index list** | Not published; the page says "contact us to confirm the indices relevant to your research are included" |
| G3 | **FMP historical-constituent history depth** | Stated nowhere in the API documentation |
| G4 | **EODHD S&P 500 constituent depth: 12 years or back to 2000?** | The product page and the vendor's own blog disagree. **Unresolved** |
| G5 | **S&P DJI's own terms of use and licensing pages** | `spglobal.com` returned HTTP 403 to every automated request. The redistribution sentence in §4.1 is quoted from a third-party reproduction and corroborated by search, **not** read on S&P DJI's own site |
| G6 | **Whether any specific vendor returns a complete `FRC`/`FRCB` series with a terminal value** | Would require an account and a data pull. Explicitly outside authority |
| G7 | **Elton/Gruber/Blake exact bias figure (0.9% vs 1.4%)** | Paper is paywalled; secondary sources disagree. The S&P-500-specific figure in §1.1 row 1 does not depend on it |
| G8 | **Delisting reason/date fields for Norgate, Sharadar, FMP** | Not documented on public pages |
| G9 | **11 of the 18 candidate removals in §5.1** | Would require per-name research against S&P DJI announcements; the cost of doing so *is* the finding |
| G10 | **Whether a reconstructed membership list is legally a derivative of S&P's data** | A legal question, not a research question. Requires counsel |
| G11 | **Norgate's US index-constituent data source and licence** | EULA clause 13 names S&P Dow Jones Indices only in the context of **S&P/ASX** indices; the US S&P 500 constituent licence chain is not disclosed |

---

## 9. Open items this research surfaces

Raised as context for the Product Steward and Product Owner. **No ticket is
created, no roadmap is modified, and nothing here is marked Done.**

1. **Backtest semantics for a mid-position delisting are unspecified.** §3.3.
   When a held name is delisted, what does 4UR4 book — last close, terminal
   value, zero? This changes backtest results and is not currently defined.
2. **Membership as-of semantics must match HD-12.** HD-12 made anchor selection
   causal/as-of-time. Index membership must be evaluated the same way: a name is
   tradeable on date *d* iff it was a member on *d*, using only information
   available at *d*. Point-in-time membership is the data-layer counterpart of a
   decision already ratified in the engine layer.
3. **Stable identity (CIK) in the `data/` abstraction.** §3.3, §6.2 item 5.
4. **The "S&P 500" naming/licensing question deserves an explicit human ruling.**
   §4.1, §6.2 item 3. It is a product decision with legal consequences and is
   currently implicit.
5. **Data rented, not owned.** Both Norgate and EODHD require deletion of all
   copies — Norgate explicitly including *derived* data — on subscription lapse.
   This affects archive strategy and provider lock-in, and is not currently
   reflected in the architecture.

---

## 10. Source index

All retrieved 2026-07-25 / 2026-07-26.

**Bias quantification:** [arXiv:0810.1922](https://arxiv.org/abs/0810.1922) ·
[arXiv:2603.19380](https://arxiv.org/abs/2603.19380) ·
[Shumway 1997 (PDF)](https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf) ·
[Elton/Gruber/Blake 1996](https://academic.oup.com/rfs/article-abstract/9/4/1097/1580100)

**Constituents — free:** [Wikipedia list](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) ·
[revision 697200065](https://en.wikipedia.org/w/index.php?title=List_of_S%26P_500_companies&oldid=697200065) ·
[fja05680/sp500](https://github.com/fja05680/sp500) ·
[bkestelman/sp500_historical_components](https://github.com/bkestelman/sp500_historical_components) ·
[hanshof/sp500_constituents](https://github.com/hanshof/sp500_constituents) ·
[Tickericons changes](https://tickericons.com/changes) ·
[Robot Wealth method](https://robotwealth.com/how-to-get-historical-spx-constituents-data-for-free/) ·
[Riaz Arbi method](https://riazarbi.github.io/quant/backtesting-sp500-constituent-history/)

**Constituents — paid:** [Norgate packages](https://norgatedata.com/stockmarketpackages.php) ·
[Norgate content tables](https://norgatedata.com/data-content-tables.php) ·
[Siblis](https://siblisresearch.com/data/historical-component-changes/) ·
[Sharadar via QuantRocket](https://www.quantrocket.com/pricing/data/sharadar/) ·
[Sharadar SEP](https://data.nasdaq.com/databases/SEP) ·
[EODHD S&P feed](https://eodhd.com/lp/spglobal) ·
[EODHD blog](https://eodhd.com/financial-apis-blog/sp-500-historical-constituents-data) ·
[FMP historical S&P 500](https://site.financialmodelingprep.com/developer/docs/stable/historical-sp-500) ·
[CRSP via WRDS (SMU note)](https://library.smu.edu.sg/topics-insights/notes-and-thoughts-retrieving-historical-members-sp-500-wrds) ·
[S&P DJI data & index licensing](https://www.spglobal.com/spdji/en/about-us/data-index-licensing)

**Delisted:** [Massive All Tickers](https://massive.com/docs/rest/stocks/tickers/all-tickers) ·
[EODHD delisted symbols](https://eodhd.com/financial-academy/financial-faq/survivorship-bias-free-financial-analysis) ·
[EODHD exchange symbol list](https://eodhd.com/financial-apis/exchanges-api-list-of-tickers-and-trading-hours) ·
[Alpha Vantage docs](https://www.alphavantage.co/documentation/) ·
[CRSP data definitions (DLSTCD)](https://terpconnect.umd.edu/~wermers/ftpsite/fnce7200/data_defs_061899.pdf) ·
[Yahoo coverage study](https://github.com/Neyt/yahoo-finance-coverage-study)

**Licensing:** [S&P Master Index License Agreement, SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1776030/000119312521050328/d83606dex998c.htm) ·
[S&P DJI legal disclaimers](https://www.spglobal.com/spdji/en/disclaimers/) ·
[Norgate EULA](https://norgatedata.com/subscribe/eula.php) ·
[EODHD T&Cs](https://eodhd.com/financial-apis/terms-conditions) ·
[EODHD commercial vs personal](https://eodhd.com/financial-apis/commercial-vs-personal-license-use) ·
[FMP Terms of Service](https://site.financialmodelingprep.com/terms-of-service) ·
[FMP pricing](https://site.financialmodelingprep.com/developer/docs/pricing) ·
[FMP enterprise](https://site.financialmodelingprep.com/enterprise) ·
[Massive pricing](https://massive.com/pricing) ·
[Massive business](https://massive.com/business) ·
[WRDS Terms of Use](https://wrds-www.wharton.upenn.edu/users/tou/)

**Events:** [Axon replaces First Republic](https://press.spglobal.com/2023-05-01-Axon-Enterprise-Set-to-Join-S-P-500-STAG-Industrial-to-Join-S-P-MidCap-400) ·
[First Republic joins S&P 500](https://press.spglobal.com/2018-12-27-First-Republic-Bank-Set-to-Join-S-P-500) ·
[March 2026 rebalance](https://press.spglobal.com/2026-03-06-Vertiv-Holdings,-Lumentum-Holdings,-Coherent,-and-EchoStar-Set-to-Join-S-P-500-Others-to-Join-S-P-100,-S-P-MidCap-400,-and-S-P-SmallCap-600) ·
[N-PORT delay, Federal Register](https://www.federalregister.gov/documents/2025/04/22/2025-06861/form-n-port-and-form-n-cen-reporting-guidance-on-open-end-fund-liquidity-risk-management-programs) ·
[First Republic Bank (Wikipedia)](https://en.wikipedia.org/wiki/First_Republic_Bank) ·
[FRC/FRCB on stockanalysis.com](https://stockanalysis.com/stocks/frc/)
