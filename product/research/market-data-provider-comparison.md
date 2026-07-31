# 4UR4 — Market-Data Provider Comparison (evidence survey)

> **RESEARCH / CONTEXT ONLY under [GOV-015](../../governance/build-freeze.md). No
> provider is selected; any selection, spend, or license is HUMAN-GATED
> ([GOV-013](../../governance/approval-gate.md)).**

Executes research areas **R1 (historical daily OHLCV)**, **R2 (live/delayed market
data)**, **R3 (stock splits & corporate actions)** and **R8 (expected cost)** from the
research instrument [`../data-provider-research.md`](../data-provider-research.md), and
populates the comparison matrix **with evidence**. It is a *survey*, not a scored
decision: **no ranking picks a winner, and no purchase is recommended.** It feeds the
provider-agnostic `data/` abstraction in
[`../../docs/architecture/mvp-architecture.md`](../../docs/architecture/mvp-architecture.md).

GitHub Issue #4. Branch `research/market-data-research`.

---

## 1. Scope & method

- **What this is:** desk research (vendor pricing/docs pages + secondary reviews, each
  cited) plus the **one real sample pull 4UR4 already holds** — the Alpha Vantage SPCX
  daily OHLCV fixture **RM-01**
  ([`../fixtures/real/RM-01/`](../fixtures/real/RM-01/)).
- **Verified vs. indicative — read this carefully:**
  - **Verified (first-hand):** only the Alpha Vantage `TIME_SERIES_DAILY` behaviour we
    directly observed in RM-01 — a **raw, as-traded (split-unadjusted)** daily OHLCV
    series for SPCX, US/Eastern, 29 bars 2026-06-12 → 2026-07-24, last refreshed
    2026-07-24. See RM-01 §1 and `alphavantage-source.json`.
  - **Indicative (desk research):** every other cell below. Pricing, history depth,
    licensing and entitlements are **as published by vendors/reviewers on the dates
    cited** and can change. **All pricing must be re-confirmed at purchase time.**
  - Where a specific fact could not be established from a citable source, the cell reads
    **"unverified — confirm"** rather than guessing.
- **Pricing dates:** every dollar/euro figure carries the source's context date and is
  tagged **"confirm current pricing at purchase."** Prices captured **2026-07-24/25**.
- **No first-hand trial was run** against any provider other than the pre-existing
  RM-01 Alpha Vantage pull. No account was created, no key issued, nothing purchased.

---

## 2. Candidate providers (survey — no down-select)

Retail / developer API tier:

- **Alpha Vantage** — US equities incl. S&P 500. `TIME_SERIES_DAILY` returns **raw
  as-traded** daily OHLCV (verified via RM-01); `TIME_SERIES_DAILY_ADJUSTED` provides a
  split/dividend-adjusted series and adjustment factors. Premium API tiers **$49.99 →
  $249.99/mo** (annual ≈ 10× monthly). Realtime/15-min-delayed US data and realtime
  options are **separate entitlements** via the Alpha X Terminal, not bundled into the
  base API tier. Commercial/redistribution use is **not covered by a personal premium
  plan** and must be arranged directly with the vendor.
  [Premium pricing](https://www.alphavantage.co/premium/) ·
  [pricing/compliance review, 2026](https://blocksentient.com/review/alpha-vantage/) ·
  RM-01 evidence.
- **Polygon.io (now "Massive", rebranded late 2025)** — Polygon.io rebranded to
  **Massive.com**; existing polygon.io URLs/keys continue to work.
  [Polygon is now Massive](https://massive.com/blog/polygon-is-now-massive). Stocks
  tiers (Massive pricing page, 2026): **Basic $0** (2 yrs history, EOD, 5 calls/min),
  **Starter $29/mo** (5 yrs, 15-min delayed, unlimited calls), **Developer $79/mo** (10
  yrs, 15-min delayed), **Advanced $199/mo** (20+ yrs, real-time). Pricing page labels
  tiers **"Individual use only"** and **"Non-pros only"**; explicit
  redistribution/commercial-display terms are **not stated on the pricing page** — must
  confirm in ToS/with sales. [Massive pricing](https://massive.com/pricing).
- **Tiingo** — US stocks/ETFs/mutual funds/ADRs + some international. EOD price history
  **30+ years**. **Power $30/mo** and free **Starter** are licensed **"Internal Use
  Only"** (no display/redistribution); a separate **Commercial plan ~$50/mo (~$499/yr)**
  adds a commercial-use license. [Tiingo pricing](https://www.tiingo.com/pricing) ·
  [EOD product](https://www.tiingo.com/products/end-of-day-stock-price-data) ·
  [review, 2026](https://www.findmymoat.com/tools/tiingo).
- **EOD Historical Data (EODHD)** — 51,000+ US tickers, **40+ yrs** US price history.
  **All-In-One €99.99/mo** (≈ €999.90/yr). Standard plans are **personal use only**;
  **commercial use requires the custom-priced Startups & Enterprise plan.**
  [EODHD pricing](https://eodhd.com/pricing) ·
  [review, 2026](https://tradingdatacompare.com/providers/eod-historical-data/).
- **Nasdaq Data Link — Sharadar (SEP / SFP)** — **21,000+ active *and delisted*
  tickers**; EOD prices; updated **17:30 and 23:30 ET** each business day. History start
  is cited inconsistently across sources (**1998** on the product page vs **Jan 2014**
  in a secondary source) — **unverified — confirm.** **Sharing/redistribution requires
  the appropriate institutional/distribution license** per the terms; a personal license
  does not grant redistribution. Personal-license dollar price is **not publicly listed
  (login-gated)** — **unverified — confirm.**
  [SEP database](https://data.nasdaq.com/databases/SEP) ·
  [QuantRocket Sharadar overview](https://www.quantrocket.com/sharadar/).
- **Databento** — usage-based (pay-as-you-go) **or ~$825/mo** flat unlimited. Notable:
  its **US Equities Bundle carries zero exchange license fees and explicitly permits
  distribution and display to end users** — but that bundle covers **4 venues only
  (NYSE Chicago, NYSE National, IEX, MIAX)**, is **historical from ~April 2023**, and is
  **T+1** — so it is *not* full-consolidated-tape and *not* deep enough to reach older
  all-time highs. [Databento pricing](https://databento.com/pricing) ·
  [zero-license-fee bundle PR](https://www.prnewswire.com/news-releases/databento-launches-the-industrys-first-us-equities-bundle-with-zero-license-fees-301960067.html)
  · [equities](https://databento.com/equities).
- **Norgate Data** — desktop-oriented, **survivorship-bias-free** US data back to
  **1950**, incl. delisted stocks and **historically accurate index constituents**
  (Platinum). US Stocks **Gold $360/yr**, **Platinum $630/yr** (6-/12-month terms; no
  monthly). Aimed at systematic-trading end users; commercial-redistribution rights
  **unverified — confirm.** [Stock market packages](https://norgatedata.com/stockmarketpackages.php)
  · [review](https://alvarezquanttrading.com/blog/norgate-data-review/).
- **IEX Cloud** — **DISCONTINUED. Verified:** IEX Group announced closure in March 2024
  and **fully shut down the IEX Cloud API on 2024-08-31**; all endpoints off, accounts
  inactive. Not a viable candidate; listed only to record its removal.
  [IEX Cloud closure notice](https://iexcloud.org/) ·
  [shutdown/migration analysis](https://www.alphavantage.co/iexcloud_shutdown_analysis_and_migration/).

Premium / institutional tier (enterprise-licensed, sales-negotiated):

- **CRSP** (Center for Research in Security Prices, via **WRDS**) — the academic gold
  standard: **36,000+ active and inactive securities**, daily & monthly data + corporate
  actions, **survivorship-bias-free**, deep history (NYSE from 1925-era). Delivered to
  **academic/government/practitioner licensees**; pricing is institutional and
  negotiated — **unverified — confirm.** [CRSP US Stock Databases](https://www.crsp.org/research/crsp-us-stock-databases/)
  · [CRSP on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/center-for-research-in-security-prices-crsp/).
- **S&P Global — Compustat** — fundamentals + pricing, active & inactive companies;
  often paired with CRSP (CRSP/Compustat Merged). Enterprise-licensed — **pricing
  unverified — confirm.** [CRSP/Compustat Merged](https://www.crsp.org/research/crsp-compustat-merged-database/).
- **Bloomberg** — Terminal **~$31,980/yr per seat (2026)** single-terminal (≈
  $28,320/seat multi-terminal); automated data via **B-PIPE add-on ≈ $2,000–$3,000/mo**.
  Redistribution/enterprise data licensing is separate and negotiated.
  [Bloomberg Terminal cost, 2026](https://godeldiscount.com/blog/bloomberg-terminal-cost-2026).
- **LSEG / Refinitiv (Workspace, Datastream)** and **FactSet** — enterprise market-data
  platforms; named-user licenses, data entitlements, usage-based feeds; **pricing and
  redistribution terms are negotiated per contract — unverified — confirm.**
  [LSEG Workspace service description](https://www.lseg.com/content/dam/data-analytics/en_us/documents/support/workspace/service-description.pdf)
  · [LSEG pricing marketplace](https://www.vendr.com/marketplace/refinitiv).

---

## 3. Comparison matrix (evidence + source; no winner/score column)

Columns: coverage · history depth · adjustments (split/div/raw) · corporate-actions ·
live/delayed · redistribution license · latency (EOD timing) · indicative cost · API
quality. Cells give **evidence + a link**, or **"unverified — confirm"**.

| Provider | Coverage (US eq / S&P 500) | History depth | Adjustments (split / div / raw) | Corporate actions | Live vs delayed | Redistribution / display license | Latency / EOD timing | Indicative cost (2026-07, confirm current at purchase) | API quality |
|---|---|---|---|---|---|---|---|---|---|
| **Alpha Vantage** | US equities incl. S&P 500 ([review](https://blocksentient.com/review/alpha-vantage/)) | 20+ yrs daily (indicative; [guide](https://alphalog.ai/blog/alphavantage-api-complete-guide)) — unverified exact start, confirm | **Raw as-traded verified** via RM-01 (`TIME_SERIES_DAILY`); split+div **adjusted** via `TIME_SERIES_DAILY_ADJUSTED` ([RM-01 §1](../fixtures/real/RM-01/README.md)) | Split/div adjustment factors in adjusted endpoint; depth of spin-off/merger handling **unverified — confirm** | 15-min delayed & realtime = **separate entitlements** (Alpha X Terminal), not in base tier ([premium](https://www.alphavantage.co/premium/)) | **Not covered by personal premium plan**; commercial/redistribution arranged w/ vendor ([review](https://blocksentient.com/review/alpha-vantage/)) | Daily EOD; exact publish time **unverified — confirm** | **$49.99–$249.99/mo** by rate limit; annual ≈10× ([premium](https://www.alphavantage.co/premium/)) | Widely used REST/JSON; free tier 25 req/day, 5/min ([review](https://tradingtoolshub.com/review/alpha-vantage/)) |
| **Polygon.io / Massive** | US equities incl. S&P 500 ([massive](https://massive.com/)) | Basic 2y / Starter 5y / Developer 10y / **Advanced 20+y** ([pricing](https://massive.com/pricing)) | Adjusted + unadjusted both offered by API (split/div params) — **confirm per-endpoint detail** | Splits & dividends endpoints published ([docs](https://massive.com/docs/rest/stocks/overview)) — **confirm depth** | Delayed (15-min) on Starter/Developer; **real-time on Advanced** ([pricing](https://massive.com/pricing)) | Pricing page: **"Individual use only," "Non-pros only"**; explicit redistribution terms **not on pricing page — confirm ToS** ([pricing](https://massive.com/pricing)) | EOD on free tier; intraday on paid; exact EOD time **unverified — confirm** | **$0 / $29 / $79 / $199 per mo** ([pricing](https://massive.com/pricing)) | Modern REST + WebSocket; "unlimited calls" on paid ([pricing](https://massive.com/pricing)) |
| **Tiingo** | US stocks/ETFs/mutual funds/ADRs (+intl) ([EOD product](https://www.tiingo.com/products/end-of-day-stock-price-data)) | **30+ yrs** price history ([pricing](https://www.tiingo.com/pricing)) | Adjusted + raw supported; proprietary error-checking ([EOD product](https://www.tiingo.com/products/end-of-day-stock-price-data)) — confirm raw/adj flag detail | Splits/dividends handled in EOD API ([docs](https://www.tiingo.com/documentation/end-of-day)) — confirm depth | EOD focus; IEX-based delayed intraday available — **confirm entitlements** | **Starter/Power = "Internal Use Only"**; **Commercial plan** adds commercial license ([pricing](https://www.tiingo.com/pricing)) | Daily EOD; exact time **unverified — confirm** | **Power $30/mo** (non-commercial); **Commercial ~$50/mo (~$499/yr)** ([review](https://www.findmymoat.com/tools/tiingo)) | REST/JSON, generous limits on Power (10k/hr) ([pricing](https://www.tiingo.com/pricing)) |
| **EODHD** | 51,000+ US tickers incl. S&P 500 ([pricing](https://eodhd.com/pricing)) | **40+ yrs** US price history ([review](https://tradingdatacompare.com/providers/eod-historical-data/)) | Adjusted + raw EOD available — **confirm split/div flag semantics** | Splits/dividends + calendar data in All-In-One ([pricing](https://eodhd.com/pricing)) — confirm depth | EOD + delayed; realtime add-ons — **confirm entitlements** | **Standard = personal use only; commercial = custom Enterprise plan** ([review](https://tradingdatacompare.com/providers/eod-historical-data/)) | Daily EOD; time **unverified — confirm** | **All-In-One €99.99/mo** (≈€999.90/yr); commercial = custom quote ([pricing](https://eodhd.com/pricing)) | REST/JSON; 100k calls/day, 1,000/min on paid ([review](https://tradingdatacompare.com/providers/eod-historical-data/)) |
| **Nasdaq Data Link — Sharadar (SEP)** | **21,000+ active + delisted** US tickers ([SEP](https://data.nasdaq.com/databases/SEP)) | Start **1998 vs 2014** cited inconsistently — **unverified — confirm** | Adjusted + unadjusted equity prices published — **confirm flag detail** ([SEP](https://data.nasdaq.com/databases/SEP)) | Sister datasets (SF1 fundamentals, S&P 500 constituents, actions) — **confirm CA depth** | EOD only | **Redistribution needs institutional/distribution license**; personal ≠ redistribution ([terms per search](https://data.nasdaq.com/databases/SEP)) | Updated **17:30 & 23:30 ET** business days ([SEP](https://data.nasdaq.com/databases/SEP)) | Personal price **login-gated — unverified — confirm** ([SEP](https://data.nasdaq.com/databases/SEP)) | Nasdaq Data Link REST + client libs; established platform |
| **Databento** | US equities; **zero-fee bundle = 4 venues only** (NYSE Chicago, NYSE National, IEX, MIAX), not consolidated tape ([bundle PR](https://www.prnewswire.com/news-releases/databento-launches-the-industrys-first-us-equities-bundle-with-zero-license-fees-301960067.html)) | Zero-fee bundle historical from **~Apr 2023** — **too shallow for older ATHs** ([equities](https://databento.com/equities)) | Schemas incl. OHLCV aggregates; raw ticks; **adjustment policy — confirm** | Corporate-actions handling **unverified — confirm** | Real-time + historical, **T+1** for bundle ([equities](https://databento.com/equities)) | **Explicitly permits distribution + display to end users, zero exchange license fee** (bundle) ([bundle PR](https://www.prnewswire.com/news-releases/databento-launches-the-industrys-first-us-equities-bundle-with-zero-license-fees-301960067.html)) | Real-time / T+1; not a fixed EOD batch | Usage-based **or ~$825/mo** unlimited ([pricing](https://databento.com/pricing)) | Modern low-latency API, strong docs; schema-oriented |
| **Norgate Data** | US stocks **survivorship-bias-free** incl. delisted + historical constituents ([packages](https://norgatedata.com/stockmarketpackages.php)) | Back to **1950** (US) ([review](https://alvarezquanttrading.com/blog/norgate-data-review/)) | Split/div adjusted + unadjusted for backtesting ([review](https://alvarezquanttrading.com/blog/norgate-data-review/)) — confirm flags | **Delisted + historically accurate index constituents** (Platinum) ([packages](https://norgatedata.com/stockmarketpackages.php)) | EOD only (desktop updater) | Aimed at end-user systematic trading; **commercial-redistribution rights unverified — confirm** | Daily EOD via updater; time **unverified — confirm** | US Stocks **Gold $360/yr, Platinum $630/yr** ([packages](https://norgatedata.com/stockmarketpackages.php)) | Desktop-integration model (AmiBroker/etc.), Python SDK; not a cloud REST API |
| **IEX Cloud** | — **DISCONTINUED** — | — | — | — | — | — | — | **N/A — shut down 2024-08-31** ([closure](https://iexcloud.org/)) | Retired |
| **CRSP** (via WRDS) | **36,000+ active + inactive** US securities ([CRSP](https://www.crsp.org/research/crsp-us-stock-databases/)) | Deep (NYSE ~1925-era) ([CRSP](https://www.crsp.org/research/crsp-us-stock-databases/)) | Adjusted + raw + returns; research-grade CA methodology ([CRSP](https://www.crsp.org/research/crsp-us-stock-databases/)) | **Research-grade corporate actions**, survivorship-bias-free ([CRSP](https://www.crsp.org/research/crsp-us-stock-databases/)) | EOD / research files (not live) | **Academic/institutional license**; redistribution restricted — **confirm terms** ([CRSP on WRDS](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/center-for-research-in-security-prices-crsp/)) | Not real-time; periodic research delivery | Institutional/negotiated — **unverified — confirm** | WRDS query/download + SAS/Python; research tooling, not a product API |
| **S&P Global — Compustat** | US (+global) fundamentals + pricing, active & inactive ([merged](https://www.crsp.org/research/crsp-compustat-merged-database/)) | Deep fundamentals history — **confirm** | Fundamentals-centric; pricing adj via merged CRSP — **confirm** | Corporate actions in fundamentals context — **confirm** | EOD / research | Enterprise license; redistribution negotiated — **confirm** | Not real-time | Institutional/negotiated — **unverified — confirm** | WRDS / enterprise delivery |
| **Bloomberg** | Global incl. all US equities | Deep | Full adj/raw + CA (enterprise) — **confirm specifics** | Comprehensive corporate actions (enterprise) — **confirm** | Real-time (exchange-entitled) | Redistribution via separate enterprise data license; **exchange fees apply** — confirm | Real-time | **Terminal ≈ $31,980/yr/seat (2026)**; B-PIPE ≈ $2–3k/mo ([cost 2026](https://godeldiscount.com/blog/bloomberg-terminal-cost-2026)) | Terminal + B-PIPE / API; institutional-grade |
| **LSEG/Refinitiv & FactSet** | Global incl. US equities ([LSEG svc](https://www.lseg.com/content/dam/data-analytics/en_us/documents/support/workspace/service-description.pdf)) | Deep | Full adj/raw + CA (enterprise) — **confirm** | Comprehensive (enterprise) — **confirm** | Real-time + historical | Named-user + entitlement + feed licensing; redistribution negotiated — **confirm** ([pricing](https://www.vendr.com/marketplace/refinitiv)) | Real-time / batch | Enterprise/negotiated — **unverified — confirm** | Workspace/Datastream/feeds; enterprise APIs |

---

## 4. Adjusted-vs-raw split spot-check (R3)

**Method (reproducible when a provider trial is later human-approved):**

1. Pick a symbol with a **known split inside the requested range** (a large, unambiguous
   ratio makes the effect obvious).
2. From the provider, pull **two series over the same range**: the **raw / as-traded**
   series and the provider's **split-adjusted** series.
3. Compare the **high (wick)** on and around the split date across the two bases. On the
   raw series the pre-split highs sit at the pre-split price level; on the adjusted
   series every pre-split value is divided by the split ratio, so the pre-split highs
   drop to the post-split scale and the series is continuous across the split date.
4. **Confirm which basis matches a TradingView-style chart per [HD-01].** HD-01 mandates
   **split-adjusted, dividend-UNadjusted** prices; a default TradingView continuous chart
   is split-adjusted, so the provider's **split-adjusted (but dividend-unadjusted)** basis
   is the one that should line up. Because 4UR4 anchors trendlines on **wicks**, verify
   the **adjusted high** — not just the close — is continuous and correct across the split.

**Illustrative example — AAPL 4-for-1 split on 2020-08-31**
*(illustrative / public knowledge, NOT a provider-specific verified pull):*

- On a **raw as-traded** series, AAPL highs immediately **before** 2020-08-31 sit around
  the **~$500** level (pre-split share price); immediately **after** the split they sit
  around **~$125** — a ~4× discontinuity purely from the split, not a real move.
- On a **split-adjusted** series, every pre-split bar is divided by 4, so the pre-split
  highs restate to the **~$125** scale and the series is **continuous** across
  2020-08-31 — matching how a default TradingView chart renders it, which is the HD-01
  basis.
- (TSLA's 3-for-1 on 2022-08-25 behaves identically at a 3× ratio and is an equally
  valid public illustration.)

**Why no live provider-specific split check is included here:** the only real pull 4UR4
holds is the **Alpha Vantage SPCX RM-01** sample, and **RM-01 contains no split in its
range** (2026-06-12 → 2026-07-24; RM-01 §1 explicitly notes this). A live,
provider-specific adjusted-vs-raw comparison therefore **awaits a split-bearing symbol
and a human-approved provider trial** — it is deliberately not fabricated here.

[HD-01]: ../human-decisions.md

---

## 5. Human-gated points

Each of the following is **HUMAN-GATED (GOV-013)** — prepared here, decided by a human:

- **Provider selection** — choosing any provider (or combination) to fill the `data/`
  adapter. Nothing above selects one. **HUMAN-GATED (GOV-013).**
- **Recurring spend** — any subscription (e.g. a $30–$100/mo retail API, an ~$825/mo
  Databento plan, a Norgate annual term, or a five-figure institutional CRSP/Bloomberg
  license). **HUMAN-GATED (GOV-013).**
- **Redistribution / commercial-display license** — any license needed to **show data to
  paying users**. Several retail tiers here are **personal/internal use only** (Tiingo
  Power, EODHD standard, Massive "individual use", Alpha Vantage personal premium);
  showing their data to SaaS subscribers needs a commercial/redistribution license.
  **HUMAN-GATED (GOV-013).**
- **Real-time / exchange-entitled feeds** — carry recurring exchange fees; deferred by
  default (MVP is EOD). Enabling them is **HUMAN-GATED (GOV-013).**
- **Lifting the GOV-015 build-freeze per-scope** before any adapter is built.
  **HUMAN-GATED (GOV-013).**

---

## 6. Close

**This document recommends NO purchase and commits nothing; MVP default cadence is
EOD/daily; selection and spend are the Product Owner's.** It records evidence as
*context* to inform a later, licensing-aware human decision under GOV-013 — it does not
make that decision, and it authorizes no build under GOV-015.
