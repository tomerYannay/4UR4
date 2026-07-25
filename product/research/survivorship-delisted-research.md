# 4UR4 — Survivorship-Bias-Free Constituents + Delisted History Research

> Research instrument for **R4** (point-in-time S&P 500 constituents), **R5**
> (delisted stock price history), and the **constituent/delisted portion of R7**
> (commercial redistribution/display rights). Feeds
> [`../data-provider-research.md`](../data-provider-research.md) and
> [HD-07](../human-decisions.md#hd-07--survivorship-bias-free-constituents--delisted-history--materiality-high).
> Advisory (GOV-016) role under the Architect. GitHub Issue #5.

---

## 1. Status banner

> **RESEARCH / CONTEXT ONLY under [GOV-015](../../governance/build-freeze.md).
> No dataset is acquired, licensed, or selected here; any acquisition/spend/license
> is HUMAN-GATED ([GOV-013](../../governance/approval-gate.md)).**

This document surveys **availability, licensing, and indicative cost** only. It
acquires nothing, licenses nothing, selects no provider, and writes no product
code. Provider names appear as *research candidates*, not recommendations. Every
specific claim carries a source URL; every price/term is **dated and marked
"confirm current"** because vendor terms change without notice. Where a specific
figure could not be verified from a primary source it is marked
**"unverified — confirm"** rather than stated as fact.

Terms and coverage figures below were reviewed **2026-07-25**.

---

## 2. Why this is correctness-critical

Two distinct biases corrupt any backtest that uses a naive "today's index members,
full history" universe:

- **Survivorship bias.** If the backtest universe is *today's* S&P 500 membership
  projected backward, it silently excludes every company that was in the index in
  the past but has since failed, been acquired, or been removed (SVB, Lehman,
  Enron, Bear Stearns, WorldCom, dozens of others). The surviving names are, by
  construction, the ones that did *not* blow up. Returns, breadth, and
  breakout-success statistics are all inflated because the losers were deleted
  from the sample. Studies of the CRSP data show that **omitting delisting returns
  alone biases results**, because a delisted-for-cause name (bankruptcy) often
  realizes a large negative final return that never enters a survivor-only sample
  ([Shumway 1997, "The Delisting Bias in CRSP Data"](https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf);
  [Alpha Architect, "Dealing with Delistings"](https://alphaarchitect.com/dealing-with-delistings-a-critical-aspect-for-stock-selection-research/)).

- **Look-ahead bias.** Using *current* membership to decide which stocks the
  scanner "would have" watched on a 2015 date embeds information (the eventual
  index composition) that was not knowable at that historical moment. The scanner
  must see the **actual index members as of each historical date** — point-in-time
  membership with dated add/remove events — to be honest.

Both are fixed by the same two inputs: **(a) point-in-time constituent membership
with add/remove dates (R4)** and **(b) OHLCV price history for delisted/merged/
bankrupt names (R5)**, mapped to each other so a backtest can reconstruct the true
tradeable universe on any past date.

This is load-bearing for the 4UR4 thesis of **correct, explainable signals.** A
Confidence-v1 lift validation (does the heuristic score rank-order breakout
outcomes better than chance?) run on a survivor-only universe would report
optimistic lift that will not reproduce live — precisely the mis-calibration
[HD-04](../human-decisions.md#hd-04--confidence-is-a-heuristic-not-a-probability--materiality-high)
and the Phase-4 backtest exist to prevent. The Product Owner has already ruled
this need **correctness-critical**
([HD-07](../human-decisions.md#hd-07--survivorship-bias-free-constituents--delisted-history--materiality-high),
APPROVED with condition; **purchase remains human-gated**).

---

## 3. R4 — Point-in-time S&P 500 constituents

Question: can 4UR4 obtain **as-of-date membership** plus **dated add/remove
events**, with enough history and a commercial-use license?

| Candidate | Point-in-time membership? | Add/remove events + dates? | History depth | Commercial licensing | Evidence |
|---|---|---|---|---|---|
| **CRSP** (Center for Research in Security Prices, via WRDS) | Yes — the `dsp500list` / S&P 500 index constituent tables track index entry/exit so returns can be computed on the members present on any date | Yes (entry/exit dated) | Deep (CRSP S&P history runs to the index's mid-20th-century origins) | Academic/institutional subscription via WRDS; **not a retail commercial-SaaS license** — redistribution to paying subscribers would need separate negotiation | [crsp.org](https://www.crsp.org/), [survivorship-bias reconstruction using `dsp500list`](https://riazarbi.github.io/quant/backtesting-sp500-constituent-history/) |
| **Norgate Data** | Yes — "know which stocks were in each index on any given day in history"; constituents used *as they were in the past* | Yes | **S&P 500 back to 1957 inception** | Subscription (Platinum tier carries delisted + index constituents); local Windows DB; commercial/redistribution rights need confirmation | [enlightenedstocktrading.com/norgate-data](https://enlightenedstocktrading.com/norgate-data/), [concretumgroup.com constituent workflow](https://concretumgroup.com/historical-constituents-of-an-equity-index-in-python-norgate-data/) |
| **Sharadar** (SF1/SEP/SP500, via Nasdaq Data Link / QuantRocket) | Yes — dedicated S&P 500 constituents product with historical additions/removals | Yes — "historical additions to and removals from the S&P 500 index **since 1957**" | Membership since 1957; price/fundamentals since 1998 | Requires an **institutional or distribution license to redistribute**; professional users must purchase via Nasdaq Data Link | [quantrocket.com/sharadar](https://www.quantrocket.com/sharadar/), [data.nasdaq.com/databases/SEP](https://data.nasdaq.com/databases/SEP) |
| **Index-fund holdings history (SPDR SPY / iShares) as a PROXY** | Approximate — a fund's *published daily holdings* track the index it replicates, so a holdings archive is a usable membership proxy | Only inferable by diffing successive holdings files; not an authoritative dated event log | Only as far back as retained holdings files go (often limited public history) | Fund-sponsor holdings files have their own site ToS; using them as an index-membership proxy does **not** grant S&P index-data rights (see R7) | Caveat: a fund can deviate from the index (sampling, timing), so this is a *proxy*, not ground truth |
| **Free/low-cost proxies — S&P DJI press announcements** | No standing snapshot, but each change is authoritatively announced | Yes — S&P Dow Jones Indices publishes each add/remove as a dated press release (the primary source for events) | Event-by-event; no bulk historical file | Press releases are readable; **the underlying index data/trademark is licensed** (R7) | [press.spglobal.com index announcements](https://press.spglobal.com/) |
| **Free/low-cost proxies — Wikipedia "List of S&P 500 companies"** | Current list only; a "Selected changes to the list of S&P 500 components" table gives *recent* dated changes | Partial — the changes table is not a complete, audited point-in-time reconstruction back to inception | Shallow/incomplete for historical reconstruction | Content is **CC-BY-SA** (reusable with attribution + share-alike), but **completeness/accuracy is not guaranteed** — unsuitable as the sole correctness-critical source | [en.wikipedia.org/wiki/List_of_S%26P_500_companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) |

**R4 reliability caveats.** The gold-standard point-in-time sources (CRSP, Norgate,
Sharadar) are paid/licensed. The free proxies (Wikipedia change log, diffed ETF
holdings, individual press releases) can *spot-check* or *illustrate* but are
**not** a substitute for an audited, gap-free membership series — Wikipedia's
change table is explicitly incomplete for full historical reconstruction, and an
ETF-holdings proxy can drift from the index. Using a free proxy as the backtest's
universe of record would leave residual survivorship/point-in-time error and must
be flagged.

---

## 4. R5 — Delisted stock price history

Question: is OHLCV available for **delisted / merged / bankrupt** tickers, retained
after delisting, adjustable, and mappable to the R4 membership series?

| Candidate | Delisted coverage | Survivorship handling | History depth | Adjustment handling | Licensing | Evidence |
|---|---|---|---|---|---|---|
| **CRSP** | Academic gold standard — retains delisted securities with **delisting dates, reasons, and delisting returns** | Explicitly survivorship-bias-free; the delisting-return field is the canonical fix for the CRSP delisting bias | Deep | Both raw and adjusted; corporate-action aware | Institutional/WRDS; redistribution needs separate terms | [Shumway 1997](https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf), [crsp.org](https://www.crsp.org/) |
| **Norgate Data** | Delisted stocks included (Platinum package) so no-longer-trading names remain testable | Purpose-built survivorship-bias-free backtesting | Aligned with constituent history (US to 1957) | Split/dividend-adjusted series available in local DB | Subscription; commercial/redistribution rights **unverified — confirm** | [enlightenedstocktrading.com](https://enlightenedstocktrading.com/norgate-data/), [alvarezquanttrading.com review](https://alvarezquanttrading.com/blog/norgate-data-review/) |
| **Sharadar SEP** | **21,000+ active and delisted tickers**; corporate actions incl. splits, dividends, spinoffs, acquisitions, delist reasons, ticker changes | "Nearly completely free from survivorship bias" | **Since 1998** | Corporate-action fields provided | Redistribution needs institutional/distribution license (R7) | [data.nasdaq.com/databases/SEP](https://data.nasdaq.com/databases/SEP), [quantrocket.com/sharadar](https://www.quantrocket.com/sharadar/) |
| **EOD Historical Data (EODHD)** | Dedicated delisted-companies dataset; names delisted **before 2018 have EOD (OHLCV) only**, later delistings may carry more data types | Delisted names retained and queryable | US tickers mostly from **Jan 2000**; 40+ yrs on some US series | EOD adjusted/raw prices via API | **Commercial license required** to display data to end users / build a product | [eodhd.com/financial-apis/delisted-stock-companies-data](https://eodhd.com/financial-apis/delisted-stock-companies-data), [eodhd.com/pricing](https://eodhd.com/pricing) |
| **Polygon.io** | Delisted tickers reachable via `active=false` on the stocks tickers endpoint; provides last-traded date | Retained but **data on delisted tickers is "spotty at best"** (missing names/dates); Ticker Events endpoint excludes delisted | Varies by ticker | Adjusted/raw aggregates | Commercial tiers; redistribution terms need confirmation | [polygon.io docs — all tickers](https://polygon.io/docs/rest/stocks/tickers/all-tickers), [community review](https://medium.com/@yolotrading/a-complete-review-of-the-polygon-io-api-everything-you-wanted-to-know-c79e992a74ff) |
| **Nasdaq Data Link (Sharadar host)** | Serves Sharadar SEP (above); professional access via Nasdaq Data Link account | Inherits Sharadar's handling | Since 1998 | Corporate actions in SEP | Institutional/distribution license for redistribution | [data.nasdaq.com/databases/SEP](https://data.nasdaq.com/databases/SEP) |

**R5 caveats.** Depth and quality diverge sharply: CRSP is the academic benchmark
(with the delisting-return field the literature says is essential); Norgate and
Sharadar are the practitioner-grade paid options with explicit delisted coverage;
API providers (EODHD, Polygon) carry delisted names but with **coverage gaps**
(EODHD: pre-2018 delistings EOD-only; Polygon: acknowledged spotty delisted
metadata) that must be spot-checked before relying on them. Mapping delisted price
series to the R4 membership series (ticker-change and symbol-reuse handling) is a
correctness step in its own right.

---

## 5. R7 — Redistribution / display rights (constituent & delisted portion)

**The key risk: "free to fetch" ≠ "free to resell/show".** 4UR4 is a SaaS that
would display signals to *paying subscribers*, so the operative question is not
"can we download this?" but "may we **redistribute/display** it commercially?"

| Source | Personal/research use | Commercial redistribution to paying subscribers | Quoted term (source + date) |
|---|---|---|---|
| **S&P Dow Jones Indices — index data + "S&P 500" trademark** | N/A | **Distinct commercial gate.** "Redistribution or reproduction in whole or in part are prohibited without written permission of S&P Dow Jones Indices LLC." "S&P 500" is a **registered trademark** licensed by S&P DJI; the firm licenses indices/real-time values to 550+ institutions and to media for display. | [spglobal.com/spdji legal disclaimers](https://www.spglobal.com/spdji/en/disclaimers/), [Data & Index Licensing](https://www.spglobal.com/spdji/en/about-us/data-index-licensing) — reviewed 2026-07-25, **confirm current** |
| **Sharadar (via Nasdaq Data Link)** | Single-user subscription | Requires stepping up to an **institutional or distribution license** to share/redistribute inside or outside your org; professional users must buy via Nasdaq Data Link. | "If you wish to share or redistribute any part or all of the Services … you agree to subscribe to the appropriate institutional or distribution license." — [quantrocket.com/sharadar](https://www.quantrocket.com/sharadar/), reviewed 2026-07-25, **confirm current** |
| **EOD Historical Data** | Free/low tiers for personal use | Commercial license needed to display data to end users or build a product; commercial plans state they include exchange redistribution rights. | "If you're building a product, displaying data to end users, or using data within a business application, you need a commercial license." — [eodhd.com/pricing](https://eodhd.com/pricing), reviewed 2026-07-25, **confirm current** |
| **CRSP / WRDS** | Academic/institutional | Redistribution to external paying users is **not** covered by a standard WRDS academic seat; commercial redistribution needs separate CRSP/S&P terms. | Institutional-license framing — [crsp.org](https://www.crsp.org/), reviewed 2026-07-25, **confirm current** (exact redistribution clause **unverified — confirm with CRSP**) |
| **Norgate Data** | Subscription for the subscriber's own use / local DB | Commercial redistribution/display terms **not confirmed** from a primary ToS excerpt in this pass. | **Unverified — confirm** against Norgate's licence agreement before any commercial-display reliance |
| **Polygon.io** | Paid API tiers | Redistribution/display terms per plan — **not confirmed** from a primary ToS excerpt in this pass. | **Unverified — confirm** against Polygon's terms |
| **Wikipedia change log** | Reusable | Reusable **with attribution + share-alike (CC-BY-SA)**, but does **not** confer any S&P index-data or trademark rights, and accuracy/completeness is not guaranteed. | [Wikipedia licensing (CC-BY-SA)](https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content), reviewed 2026-07-25 |

**Distinct S&P trademark/index gate.** Even a redistribution-safe *price* license
(e.g., a commercial EODHD plan) does **not** by itself grant the right to publish
**"S&P 500 membership"** as a labeled, branded dataset. The **index composition and
the "S&P 500" name are S&P DJI intellectual property**; presenting an "S&P 500
constituents" feature to paying users is a **separate commercial gate** from
licensing the underlying prices. This must be treated as its own human-gated
licensing question, not folded into the price-data decision.

---

## 6. Evidence — illustrative point-in-time examples

*Illustrative / public knowledge, from primary S&P Dow Jones Indices press releases
and major outlets. These few cited events show what **point-in-time membership**
captures that "today's list" does not. This is **not** a fabricated full membership
table — only real, individually cited add/remove events.*

- **Addition — Tesla (TSLA), effective 2020-12-21.** S&P DJI announced on
  **2020-12-11** that Tesla would join the S&P 500 effective before the open on
  **2020-12-21**, replacing **Apartment Investment & Management (AIV / Aimco)**. A
  backtest scanning "the S&P 500" on any date in, say, mid-2019 must **exclude**
  TSLA (not yet a member) and **include** AIV (then a member) — the opposite of
  what today's list implies.
  Sources: [S&P Global press release, 2020-12-11](https://press.spglobal.com/2020-12-11-Tesla-Set-to-Join-S-P-500-100-Apartment-Income-REIT-to-Join-S-P-MidCap-400);
  [CNBC, 2020-12-11](https://www.cnbc.com/2020/12/11/tesla-to-replace-apartment-investment-and-management-in-the-sp-500.html).

- **Removal for cause — SVB Financial Group (SIVB), effective 2023-03-15.** After
  the FDIC took SVB into receivership, S&P DJI announced on **2023-03-10** that
  **Insulet (PODD)** would replace **SVB Financial (SIVB)** in the S&P 500 before
  the open on **2023-03-15**. A survivor-only universe drops SIVB entirely and
  never sees its collapse — the exact deletion that inflates backtest returns and
  understates tail risk. A point-in-time + delisted-history dataset keeps SIVB in
  the sample through its removal, with its final price action intact.
  Sources: [S&P Global press release, 2023-03-10](https://press.spglobal.com/2023-03-10-Insulet-Set-to-Join-S-P-500);
  [MedTech Dive, 2023-03-10](https://www.medtechdive.com/news/insulet-PODD-SP500-SVB/644805/).

**What this demonstrates.** Between these dates the *true* index membership differed
from both the earlier and the current list. Only a dated, point-in-time series
(R4) plus retained price history for removed names like SIVB (R5) lets a Phase-4
backtest reconstruct the universe the scanner would actually have seen — the
precondition for an honest Confidence-v1 lift number.

---

## 7. Human-gated points

Each of the following is **HUMAN-GATED ([GOV-013](../../governance/approval-gate.md))**
and is *not* decided, initiated, or committed by this document:

- **HUMAN-GATED (GOV-013)** — Purchasing or licensing any **point-in-time S&P 500
  constituents** dataset (CRSP, Norgate, Sharadar, or other).
- **HUMAN-GATED (GOV-013)** — Purchasing or licensing any **delisted price-history**
  dataset or delisted add-on tier.
- **HUMAN-GATED (GOV-013)** — Any **commercial redistribution/display license** that
  permits showing constituent or delisted data to paying subscribers (institutional/
  distribution tier upgrades).
- **HUMAN-GATED (GOV-013)** — Any **S&P DJI index-data / "S&P 500" trademark**
  licensing for a user-facing "S&P 500 membership" feature (a gate distinct from the
  price-data license).
- **HUMAN-GATED (GOV-013)** — Selecting a specific provider or combination, and
  approving the associated recurring spend (feeds
  [HD-06](../human-decisions.md#hd-06--data-provider-selection--recurring-cost--materiality-high) /
  [HD-07](../human-decisions.md#hd-07--survivorship-bias-free-constituents--delisted-history--materiality-high)).

**Indicative cost note:** exact pricing is **unverified — confirm current** against
each vendor's own page before any decision. Public tiers exist (EODHD, Sharadar via
Nasdaq Data Link/QuantRocket, Norgate publish subscription pricing; CRSP is
institutional/WRDS), but **no dollar figures are asserted here** to avoid presenting
unverified specifics as fact, and none are needed to conclude that the correctness-
critical datasets are paid/licensed.

---

## 8. Explicit close

This research **recommends no acquisition and commits nothing.** It surveys
availability, licensing, and indicative cost so a human can later make an informed,
licensing-aware decision under
[GOV-013](../../governance/approval-gate.md) /
[HD-07](../human-decisions.md#hd-07--survivorship-bias-free-constituents--delisted-history--materiality-high).

**Without a survivorship-bias-free source (point-in-time constituents + delisted
history), any Phase-4 backtest must be flagged biased/provisional** and must not be
used to validate Confidence-v1 lift as if it were trustworthy. The build-freeze
([GOV-015](../../governance/build-freeze.md)) remains **ON**; no product code was
written and no provider was selected.

---

### Source index (all reviewed 2026-07-25; confirm current before reliance)

- CRSP / delisting bias: [crsp.org](https://www.crsp.org/) ·
  [Shumway 1997](https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf) ·
  [Alpha Architect](https://alphaarchitect.com/dealing-with-delistings-a-critical-aspect-for-stock-selection-research/) ·
  [`dsp500list` reconstruction](https://riazarbi.github.io/quant/backtesting-sp500-constituent-history/)
- Norgate Data: [enlightenedstocktrading.com](https://enlightenedstocktrading.com/norgate-data/) ·
  [Concretum constituents](https://concretumgroup.com/historical-constituents-of-an-equity-index-in-python-norgate-data/) ·
  [Alvarez review](https://alvarezquanttrading.com/blog/norgate-data-review/)
- Sharadar / Nasdaq Data Link: [quantrocket.com/sharadar](https://www.quantrocket.com/sharadar/) ·
  [data.nasdaq.com/databases/SEP](https://data.nasdaq.com/databases/SEP)
- EODHD: [delisted dataset](https://eodhd.com/financial-apis/delisted-stock-companies-data) ·
  [pricing/licensing](https://eodhd.com/pricing)
- Polygon.io: [all tickers docs](https://polygon.io/docs/rest/stocks/tickers/all-tickers)
- S&P DJI licensing/trademark: [legal disclaimers](https://www.spglobal.com/spdji/en/disclaimers/) ·
  [Data & Index Licensing](https://www.spglobal.com/spdji/en/about-us/data-index-licensing)
- Illustrative events: [Tesla/AIV S&P press, 2020-12-11](https://press.spglobal.com/2020-12-11-Tesla-Set-to-Join-S-P-500-100-Apartment-Income-REIT-to-Join-S-P-MidCap-400) ·
  [Insulet/SVB S&P press, 2023-03-10](https://press.spglobal.com/2023-03-10-Insulet-Set-to-Join-S-P-500)
- Wikipedia proxy: [List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) (CC-BY-SA)
