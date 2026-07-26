# 4UR4 — HD-06 Due-Diligence Pack

> **Status: RESEARCH AND DRAFTING ONLY**, under [GOV-015](../governance/build-freeze.md)
> (build-freeze ON) and [GOV-013](../governance/approval-gate.md).
>
> **[HD-06](human-decisions.md) remains PENDING.** This document is **preparation, not
> authorization**. It selects nothing, buys nothing, and commits nothing. Nothing in it —
> including the cost figures — may be represented as the Product Owner's financial
> authorization (HD-06 authority boundary, 2026-07-26, boundary 5).
>
> **Nothing here was sent to any vendor.** The questions in Part A are *drafted*, not asked.
> In producing this document **no account was created, no trial was requested, no API key was
> issued, no contact or sales form was submitted, and no licensing terms were accepted or
> clicked through.** Every source below is a publicly readable page, fetched without
> credentials, with its retrieval date recorded.
>
> **[Issue #21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band confirmation
> remains mandatory before any financial authorization.** The single-account relay channel
> that carries rulings into this repository is **not adequate authority for spending money**.

**Ruling this document serves:** Product Owner, 2026-07-26
([artifact](https://github.com/tomerYannay/4UR4/issues/24)) — *"Intrinio Startup may be
recorded as the current evidence-based leading candidate at approximately $5,994 for year 1,
but it is not selected or approved for purchase."* The same ruling lists eight prerequisites
to obtain or prepare before returning for the final HD-06 decision. Those eight are the spine
of this document.

**All retrievals in this document are dated 2026-07-26** unless a claim states otherwise.

---

## 0. Method, scope, and what was assumed

### 0.1 The eight prerequisites, indexed

| # | Prerequisite (ruling wording) | Part A section | Prior research coverage |
|---|---|---|---|
| **P-1** | Written confirmation that daily high/low are based on consolidated-tape data | [A.1](#a1--p-1-consolidated-tape-highlow) | [`data-provider-findings.md`](data-provider-findings.md) §2.3, G-03b, condition C-1 |
| **P-2** | Exact historical-depth coverage | [A.2](#a2--p-2-exact-historical-depth-coverage) | §2.1, G-02 |
| **P-3** | Split-only adjustment availability | [A.3](#a3--p-3-split-only-adjustment-availability) | §2.2, §4, G-03d |
| **P-4** | Delisted-history coverage | [A.4](#a4--p-4-delisted-history-coverage) | [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3 — **but never for Intrinio** |
| **P-5** | Redistribution / display rights | [A.5](#a5--p-5-redistribution--display-rights) | §7, G-04, G-05 |
| **P-6** | Point-in-time universe implications | [A.6](#a6--p-6-point-in-time-universe-implications-new-work) | **None — new work, see 0.3** |
| **P-7** | Complete first-year and recurring cost | [A.7](#a7--p-7-complete-first-year-and-recurring-cost) | §8, G-03c |
| **P-8** | Cancellation and data-retention constraints | [A.8](#a8--p-8-cancellation-and-data-retention-constraints-new-work) | Partial — Norgate/EODHD only, see 0.3 |

### 0.2 Evidence tags

The tags are inherited unchanged from [`data-provider-findings.md`](data-provider-findings.md) §0
so the two documents can be read together.

| Tag | Meaning |
|---|---|
| **VERIFIED** | The named page was fetched on the stated date and the quoted text was in the page read. |
| **PARTIAL** | A source was reached, but it does not contain the specific attribute; what is stated is the most the source supports. |
| **UNVERIFIED** | Reported by a search-result summary or a secondary site; the primary page was not read cleanly. A lead, not a fact. |
| **GAP** | Could not be determined at all. Recorded deliberately. |

**A documented gap is a finding; a confident guess is a defect.** Where this document could
close a gap from public documentation without contacting anyone, it did — and those closures
are marked VERIFIED with their source. Where it could not, the gap is recorded as a gap.

### 0.3 What is new here, and what is deliberately not re-derived

**Not re-derived.** The provider survey, the licence quotations, the price list, the wick
analysis and the ranking rationale all live in
[`data-provider-findings.md`](data-provider-findings.md); the constituent/delisted analysis
lives in [`survivorship-bias-findings.md`](survivorship-bias-findings.md). Part B **cites**
them rather than restating them.

**New work in this document, in order of decision weight:**

1. **P-1 is re-aimed at the right party.** Intrinio's own documentation names its upstream:
   *"Raw historical end of day prices are sourced from our data partner EDI"*
   (<https://intrinio.com/docs/market-data/us-historical-end-of-day-prices>, retrieved
   2026-07-26, **VERIFIED**). EDI publishes that it sells **both** per-exchange files **and**
   a **US Composite (CTA)** file, and recommends the composite. So the consolidated-tape
   question is not "does Intrinio use the SIP?" but **"which EDI file does Intrinio buy?"** —
   a far more falsifiable question. See [A.1](#a1--p-1-consolidated-tape-highlow).
2. **A contradiction on the leading candidate's single ranking ground.** Intrinio claims
   history "back to the 1960s"; its named upstream EDI states its end-of-day prices begin
   **1 Jan 2007**. Depth is the *only* reason Intrinio outranks Massive
   ([`data-provider-findings.md`](data-provider-findings.md) §13.0). See
   [A.2](#a2--p-2-exact-historical-depth-coverage) and
   [C.4](#c4--blocking-conditions-proposed).
3. **The leading candidate's delisted coverage, previously unassessed, has a stated start
   date — 2007.** [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3.1 does
   not contain an Intrinio row; the ruling now requires one. See
   [A.4](#a4--p-4-delisted-history-coverage).
4. **P-6 (point-in-time universe) is entirely new**, because the question did not exist when
   the provider research ran. It exists only because of the 2026-07-26 universe ruling.
5. **P-8 (cancellation and retention) is extended from two vendors to every candidate**, and
   the leading candidate's position turns out to be *silence*, not permission. See
   [A.8](#a8--p-8-cancellation-and-data-retention-constraints-new-work).

### 0.4 Reconciliation with the universe methodology

**Sequencing, stated honestly.** `docs/architecture/universe-methodology.md` **did not exist
when Part A.6 was drafted** — the `docs/architecture/` directory then held only
`mvp-architecture.md` and `phase2-independence-mechanism.md`. A.6 was therefore built from the
2026-07-26 ruling text and five stated assumptions. **The methodology landed while this
document was being written**, and A.6 has been reconciled against it. The assumptions are kept
below with their outcome, because a superseded assumption is evidence about how the questions
were derived.

| # | Assumption taken in its absence | Outcome against `universe-methodology.md` |
|---|---|---|
| **U-1** | Ranking is by market capitalisation = point-in-time price × point-in-time shares outstanding | **Confirmed and sharpened.** §2.5 `UR-RANK` v0.1.0: **full (total) market capitalisation**, summed across share classes, **not float-adjusted**, computed from the **RAW (unadjusted) close × contemporaneous raw share count**. My draft Q-6.6 assumed a split-adjusted basis and **has been corrected** |
| **U-2** | Membership is recomputed on a periodic rebalance, not daily | **Confirmed.** §3.1 quarterly scheduled rebalances plus event-driven intra-quarter changes; §4.2 states "quarterly per issuer is sufficient". But the candidate pool is **all** US-listed operating companies (thousands, not 500), which makes bulk retrieval *more* important, not less — Q-6.9 stands |
| **U-3** | Eligibility excludes ETFs, closed-end funds, SPACs, non-US-primary listings | **Broadly confirmed, with two live escalations.** §2.1–§2.3 define `UR-OPCO`, `UR-LIST`, `UR-SEC`; **REITs are included** by default (OQ-U3) and **ADR/non-US-primary treatment is escalated to the Product Owner** (OQ-U1). Point-in-time classification (Q-6.10) is required either way |
| **U-4** | The universe must be reconstructable across the full backtest window | **Confirmed, and it is now an escalated question.** OQ-U5 asks how far back the window must reach, and §4.3 records that the free SEC/XBRL path has a hard historical bound. [A.2](#a2--p-2-exact-historical-depth-coverage) and [A.4](#a4--p-4-delisted-history-coverage) supply the *price-side* bound on the same question |
| **U-5** | Membership is subject to HD-12 as-of-time causality | **Confirmed and made binding.** §4.4 `UR-PIT` rule 1 gates on **`filed_at` — the SEC acceptance timestamp** — not on `value_as_of` and not on `period_end`. Interpolation is banned (rule 2); amendments create new observations (rule 3); prices are read at `as_of = r` (rule 4) |

**The one thing the methodology adds that the questions did not anticipate, and it matters.**
§4.2 records that the **cover-page** share count and the **financial-statement** share count
are *different numbers as of different dates*, and that mixing them "produces market caps that
are wrong by a quarter's worth of buybacks and issuance, consistently, and with no error to
observe." Intrinio's shares-outstanding endpoint is documented as returning **the cover-page
figure specifically** ([B.6](#b6--p-6-point-in-time-universe-implications)). **Q-6.15 has been
added** to make every vendor state which of the two it returns.

**Where this pack sits relative to the methodology's own gaps.** §12 records **G-U8** — *"No
provider evaluated for point-in-time shares outstanding, and no vendor's
as-reported-vs-restated posture is known"* — and §4.3 ranks vendor fundamentals **third**,
behind SEC EDGAR primary filings and SEC XBRL structured data, precisely because EDGAR is
survivorship-complete by construction. **[A.6](#a6--p-6-point-in-time-universe-implications-new-work)
is the vendor-facing half of G-U8**: it does not propose buying a fundamentals dataset, and it
does not pre-empt OQ-U4 (whether R9 opens with any spend attached). It establishes what the
candidates *can* supply, so that the choice between the free EDGAR path and a paid path is
made on evidence rather than on the absence of it.

---

# Part A — The vendor question set

**How to use this part.** Each prerequisite gives the *exact question to put to the vendor*,
what an acceptable answer looks like, and what answer disqualifies. Questions are numbered
`Q-<prereq>.<n>` so an answer can be filed against the question that produced it.

Questions are addressed to **the leading candidate (Intrinio)** unless marked otherwise.
Questions marked **[ALL]** must be put to **every** candidate still in contention — Intrinio,
Massive and EODHD — because a differential answer is what reorders the ranking.

**These questions have not been asked.** Sending them is a Product Owner action; see
[Part D](#part-d--what-cannot-be-answered-without-spending-or-contacting).

---

## A.1 — P-1: Consolidated-tape high/low

**Why it is blocking.** 4UR4 anchors every trendline on the **bar high — the wick** — not the
close ([`trendline-specification.md`](trendline-specification.md) §3, §4). A high built from a
single market centre is a *different number* from the consolidated extreme, and the difference
is invisible in any close-price comparison. This is condition **C-1** in
[`data-provider-findings.md`](data-provider-findings.md) §13.1 and gap **G-03b**.

**What changed today.** The question is no longer only about Intrinio. Intrinio's own product
page states the upstream:

> "Raw historical end of day prices are sourced from our data partner EDI."
> — <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices>, retrieved
> 2026-07-26. **VERIFIED**

And EDI's own FAQ makes the composite-vs-exchange distinction explicitly, in 4UR4's exact
terms:

> "The individual exchanges like NYSE, Nasdaq, NYSE Arca and NYSE Amex only report trading
> that occurs on those individual exchanges. They do not report trading that occurs via the US
> consolidated tape that link trading with all the exchanges that are part of the Consolidated
> Tape Association (CTA)."

> "By taking only the exchange by exchange file you are missing a potential large portion of
> activity in stocks if you only take the files from the primary listing market."

> "The US Composite end of day price file represents trading that occurs on all the exchanges
> that are part of the CTA and we feel that this is what you should use instead of the
> individual exchanges."
> — <https://www.exchange-data.com/faqs-end-of-day-prices/>, retrieved 2026-07-26. **VERIFIED**

**This makes C-1 sharply falsifiable.** EDI sells two products; one of them is right for 4UR4
and one is wrong for it; the vendor knows which one it buys. This also means Intrinio's answer
is only as good as EDI's, and a vendor that answers about *its own* processing without naming
its upstream has not answered the question — the same reseller trap that
[`data-provider-findings.md`](data-provider-findings.md) §2.3 found with Marketstack/Tiingo,
and the reason DI-06 requires `upstream_source`.

### Questions

| # | Exact question to put to the vendor |
|---|---|
| **Q-1.1** | For your **historical daily end-of-day** US equity bars (not real-time, not minute bars): are the **high** and **low** fields the extremes of trades reported to the **consolidated tape** (CTA Tape A/B and UTP Tape C, all US market centres), or the extremes of trades on a **single market centre** such as the primary listing exchange? Answer for the daily EOD product specifically. |
| **Q-1.2** | You state that raw historical end-of-day prices are sourced from your data partner **EDI**. EDI publishes both an **exchange-by-exchange** end-of-day file and a **US Composite (CTA)** end-of-day file. **Which of the two does Intrinio license and serve** through the EOD prices endpoint? If both, which one is returned by default and how does a caller select the other? |
| **Q-1.3** | If the high/low are consolidated: **which sale conditions are excluded** from updating the high and the low? Please provide the condition-code list or the processing rule you follow (for example, whether you follow the SIP/UTP consolidated processing guidelines, and whether average-price trades, prior-reference-price trades and bunched sold trades update daily high/low). |
| **Q-1.4** | Do **extended-hours** (pre-market and post-market) trades update the **daily** bar's high and low? Answer yes or no for the daily granularity specifically. |
| **Q-1.5** | Is the answer to Q-1.1 **the same on every subscription tier**, including the Startup tier, or does consolidated-tape high/low require a higher tier or an add-on? |
| **Q-1.6** | Are historical daily bars ever **restated** after first publication (late trades, corrections, cancellations)? If yes: within what window, and can a caller request the bar **as it stood on a given prior date** (an as-of or vintage parameter)? |
| **Q-1.7** | **[ALL]** Name every **upstream source** for your US daily EOD OHLCV, and state for each whether it is a consolidated (SIP/CTA) feed or a venue feed. We need this to guarantee that a cross-vendor comparison is not two resellers of the same upstream. |

### Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-1.1 / Q-1.2 | "Consolidated — we license EDI's **US Composite (CTA)** end-of-day file; high and low are the extremes across all CTA/UTP market centres," in writing | "Primary listing exchange only", "the exchange-by-exchange file", "we don't disclose our source", or any answer that does not distinguish the two EDI products |
| Q-1.3 | A condition list or a named public rule (e.g. "we follow the SIP consolidated processing guidelines"), specific enough to be re-derived against an independent consolidated source | "We don't publish that" — **not automatically fatal**, but it downgrades P-1 to PARTIAL and makes the [Part D](#part-d--what-cannot-be-answered-without-spending-or-contacting) cross-vendor spot-check mandatory before spend, not after |
| Q-1.4 | "No — extended-hours trades do not update the daily high/low" | "Yes" **without a flag to exclude them**. Extended-hours prints in the wick change which bar is the ATH, and HD-01/HD-12 need a stable anchor. A documented, switchable flag is acceptable; silent inclusion is not |
| Q-1.5 | "Same on all tiers, including Startup" | "Consolidated high/low requires Enterprise" — this converts the $5,994 year-1 figure into a wrong number and re-opens P-7 entirely |
| Q-1.6 | Either "bars are never restated after T+1 close" **or** "restated, and an as-of/vintage parameter is available" | "Restated, and no as-of parameter exists" — this breaks **HD-12** causality and **DI-04** at the data layer, and no amount of application code can recover it |
| Q-1.7 | A named upstream per dataset | Refusal. An undisclosed upstream makes DI-06's `upstream_source` unfillable and makes every cross-check unfalsifiable |

**Standing rule for this prerequisite:** the ruling asks for *written* confirmation. A sales
call, a chat transcript summary, or an agent's recollection is not written confirmation. The
acceptable artifact is an email or an Order Form clause from the vendor, retained in the
repository as evidence.

---

## A.2 — P-2: Exact historical-depth coverage

**Why it matters.** Depth is the *only* attribute on this list that cannot be fixed by asking
a better question or writing more code: a provider either holds the bar that is a name's
all-time high, or it does not. If the history starts after the true ATH, the detector does not
degrade — it silently anchors on the wrong bar and every downstream signal for that name is
wrong ([`data-provider-findings.md`](data-provider-findings.md) §2.1). Depth is also the
**sole ground** on which the leading candidate outranks the runner-up (§13.0).

**The contradiction found today, stated plainly.**

| Claim | Source | Tag |
|---|---|---|
| "Over 50 years of history, making it one of the deepest EOD stock price datasets available via API" | <https://intrinio.com/financial-market-data/stock-prices-eod>, retrieved 2026-07-26 | **VERIFIED** (recorded in prior research) |
| "History is available back to the 1960s for actively trading securities (where applicable) and 2007 for delisted securities." | <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices>, retrieved 2026-07-26 | **VERIFIED** |
| "Raw historical end of day prices are sourced from our data partner EDI." | <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices>, retrieved 2026-07-26 | **VERIFIED** |
| "End of Day prices goes back to 1 Jan 2007 unless the exchange started traded on later day then we will have it from that day." | <https://www.exchange-data.com/faqs-end-of-day-prices/>, retrieved 2026-07-26 | **VERIFIED** |

**The reconciliation is not obvious and must not be guessed.** Either (a) Intrinio sources
pre-2007 US history from a second, undisclosed partner or an EDI archive product distinct from
the end-of-day feed; or (b) the "back to the 1960s" claim is narrower than it reads — for
example, applying to a subset of names, or to a dataset other than the raw OHLC bars. EDI does
publish a separate **US Equities Historical Reference Services** line (with Financial
Information Inc.) covering obsolete securities, but **its price-history depth is not stated on
any page reached** — **GAP** (<https://www.exchange-data.com/product/us-equities-historical-reference-services/>,
retrieved 2026-07-26, **UNVERIFIED** — reached via search summary only).

Note also the qualifier **"(where applicable)"** in Intrinio's own sentence. A depth claim
qualified by "where applicable" is not a coverage guarantee for any *particular* symbol, and
4UR4's requirement is per-symbol, not aggregate.

### Questions

| # | Exact question to put to the vendor |
|---|---|
| **Q-2.1** | For **US common stocks**, what is the **earliest date on which a daily OHLCV bar exists**, and what fraction of today's US common-stock universe has bars on that date? Please answer with a date and a count, not "50+ years". |
| **Q-2.2** | Your product page states history "back to the 1960s for actively trading securities (where applicable)". **What does "where applicable" exclude?** Please state the rule that determines whether a given security has pre-2007 history. |
| **Q-2.3** | Your documentation names **EDI** as the source of raw historical end-of-day prices, and EDI's published FAQ states its end-of-day prices begin **1 January 2007**. **From which source is your pre-2007 US daily OHLC obtained**, and is that source's construction of daily high/low the same as EDI's (see Q-1.1)? |
| **Q-2.4** | Please provide the **exact first available bar date** for these specific symbols: `AAPL`, `INTC`, `IBM`, `GE`, `T`, `XOM`, `KO`, `MMM`, `JNJ`, `PG`. These are long-lived large-caps whose all-time highs may predate 2007. A CSV of symbol and first-bar date is sufficient. |
| **Q-2.5** | Is the answer to Q-2.1 **tier-dependent**? Specifically, does the **Startup** tier deliver the full available history, or is history depth gated by plan as it is at some vendors? |
| **Q-2.6** | Is there a **separate one-time charge**, a bulk-download fee, or a call-volume surcharge for the **initial backfill** of full history across ~10,000 US symbols? (See also Q-7.4.) |
| **Q-2.7** | **[ALL]** Do you provide a machine-readable **per-symbol `first_bar_date`** (or equivalent coverage manifest), so that a consumer can assert depth sufficiency programmatically rather than discovering a truncated series at runtime? |

### Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-2.1 | A specific date in the 1960s–1980s with a stated coverage fraction | Any answer establishing a **first bar after ~1995**. A 2007 start is materially worse than the runner-up's 2004 start, and would invert the ranking immediately |
| Q-2.3 | A named pre-2007 source **plus** a statement of its high/low construction | "We don't disclose"; or "our pre-2007 history is back-filled from close-only data" — a close-only backfill has **no wicks**, which is fatal for an ATH-wick-anchored product and would not be visible in any close comparison |
| Q-2.4 | A per-symbol first-bar date list showing `INTC` with bars in **2000** or earlier | `INTC` first bar in 2007 — the Intel case in §2.1 is then live on the *recommended* provider, not merely on the runner-up |
| Q-2.5 | "Full history on Startup" | "Full depth requires Enterprise" — re-opens P-7 and probably the ranking |
| Q-2.7 | A coverage endpoint or file | Absence is not disqualifying, but it makes **DI-07** (`history_start_date` declared and enforced) an adapter-side inference rather than a provider-declared fact, and raises the cost of the depth-sufficiency acceptance test |

**Note for the Product Owner:** Q-2.4 is the single highest-value question in this document.
Ten symbols and ten dates settle, in one reply, the attribute that decides the ranking — and
it costs the vendor nothing to answer.

---

## A.3 — P-3: Split-only adjustment availability

**Why it matters.** [HD-01](human-decisions.md) fixes the basis: **split-adjusted,
dividend-UNadjusted ("as-traded")**, used identically for ATH selection, pivots, fitting and
breakout tests. A provider offering only fully-adjusted closes cannot satisfy HD-01. A
provider offering raw plus a complete split history can — and that is the *preferred* posture,
because a self-applied adjustment is re-derivable and auditable while a vendor-applied one must
be taken on trust ([`data-provider-findings.md`](data-provider-findings.md) §4).

**Already established** (§2.2, **VERIFIED**): Intrinio publishes raw OHLC **and** a separate
price-adjustments dataset exposing `factor`, `dividend` and `split_ratio` independently, so the
HD-01 basis is derivable. Its `adj_*` fields are **splits *and* dividends** and must be banned
outright in the adapter (DI-06b). What remains open is **G-03d** — whether a split-only series
is also available directly — plus the correctness of the split spine itself.

### Questions

| # | Exact question to put to the vendor |
|---|---|
| **Q-3.1** | Do you offer a **split-adjusted, dividend-UNadjusted** daily OHLC series **directly**, as a documented parameter or endpoint? If yes, name the parameter and its exact semantics. If no, confirm that the intended path is: raw OHLC from the prices endpoint, adjusted by the consumer using `split_ratio` from the price-adjustments dataset. |
| **Q-3.2** | Confirm in writing that the fields `adj_open`, `adj_high`, `adj_low`, `adj_close` are adjusted for **both splits and dividends**, and that no field in the prices response is adjusted for splits only. |
| **Q-3.3** | In the price-adjustments dataset, is `split_ratio` populated **independently** of `dividend` for every adjustment event — i.e. can a consumer reconstruct a splits-only cumulative factor without any dividend contamination? Are reverse splits, stock dividends, bonus issues and rights issues represented in `split_ratio`, in `dividend`, or in `factor` only? |
| **Q-3.4** | How far back does the **split/corporate-action history** extend, independently of the price history? (A vendor may hold a deeper action spine than price spine; that is useful.) |
| **Q-3.5** | Are **spin-offs** and **mergers** represented as distinct, dated event types with adjustment factors? If not, how is the price discontinuity from a spin-off reflected in the adjusted series? |
| **Q-3.6** | Are **symbol changes** exposed as dated events, and is a **stable non-ticker identifier** (CIK, FIGI or your own security ID) preserved across a symbol change and across a delisting? |
| **Q-3.7** | **[ALL]** When a corporate action is discovered late or corrected, is the **historical adjusted series revised retroactively**? If so, is the revision observable (a version, a vintage, or a change feed), or is it applied in place? |

### Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-3.1 | Either a documented split-only parameter, **or** confirmation of the raw + `split_ratio` path | "Only fully-adjusted closes are available" — cannot satisfy HD-01 at all |
| Q-3.2 | Explicit written confirmation | Ambiguity. If the vendor will not state which fields carry dividend adjustment, DI-06b cannot be configured and a dividend-adjusted high can silently become the ATH |
| Q-3.3 | "Yes, independently populated", with a statement of where each capital event lands | "`factor` is a single blended number and the components are not separable" — this makes HD-01 non-derivable and is disqualifying on its own |
| Q-3.5 | Distinct spin-off/merger event types **or** an explicit statement that the price series is adjusted for them and how | "Not covered" — **not automatically disqualifying** (it applies to every candidate; §4 records it as G-08), but it forces a spin-off sanity check in `data/` and lowers confidence in every ATH near a known spin-off |
| Q-3.6 | CIK or FIGI preserved across ticker change and delisting | Ticker-only identity — the `FRC` → `FRCB` case in [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §5.3 shows this silently returns the wrong instrument or nothing at all |
| Q-3.7 | Retroactive revisions are observable | Silent in-place revision with no vintage — breaks **HD-12** and **DI-05** the same way Q-1.6 does |

**Residual risk that survives any answer here.** A documented adjustment flag that silently
no-ops is indistinguishable from a correct one until you re-derive it. Public issue reports
describe exactly that failure at two surveyed vendors
([`data-provider-findings.md`](data-provider-findings.md) §2.2, G-17). **No vendor answer can
close this** — only acceptance test §11.2 can, and that needs an API key. See
[Part D](#part-d--what-cannot-be-answered-without-spending-or-contacting).

---

## A.4 — P-4: Delisted-history coverage

**Why it matters more under the new universe ruling, not less.** Before 2026-07-26, delisted
history mattered for backtest honesty ([HD-07](human-decisions.md)). Now it also determines
whether the **self-computed universe can be reconstructed at all**: a point-in-time top-500 by
market cap on a 2010 date must be ranked over the companies that were large in 2010 —
including the ones that have since failed. If those names are absent, the *universe itself* is
survivorship-biased before a single backtest runs, and the bias is the one
[`survivorship-bias-findings.md`](survivorship-bias-findings.md) §1.1 measures at up to 8
percentage points of annualised return.

**New finding: the leading candidate's delisted coverage was never assessed, and it has a
stated start date.** [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3.1
contains rows for Norgate, CRSP, Sharadar, EODHD, Massive, Alpha Vantage, FMP and Yahoo —
**there is no Intrinio row.** Intrinio's own documentation supplies one:

> "History is available back to the 1960s for actively trading securities (where applicable)
> and **2007 for delisted securities**."
> — <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices>, retrieved
> 2026-07-26. **VERIFIED**

A secondary reading of Intrinio's own pages also reports "10,000+ active and delisted
securities" (**UNVERIFIED** — search-summary of Intrinio pages, retrieved 2026-07-26; not
confirmed on a page read directly).

**The consequence, stated concretely:** on today's evidence the leading candidate supports a
survivorship-bias-free universe reconstruction **no earlier than 2007**. That is a
*product-scope* fact, not a footnote — it caps the honest backtest window.

### Questions

| # | Exact question to put to the vendor |
|---|---|
| **Q-4.1** | Confirm that daily OHLCV bars for **delisted** US securities remain retrievable indefinitely after the delisting, and that they are **not** removed from the API when a security ceases trading. |
| **Q-4.2** | Your documentation states delisted-security history is available from **2007**. Is 2007 (a) the earliest **delisting date** for which a name is retained, or (b) the earliest **bar date** available for retained delisted names? These are materially different: under (a) a company delisted in 2009 may still carry bars from the 1990s; under (b) it cannot. |
| **Q-4.3** | For a delisted name, do you supply the **delisting date** and the **delisting reason** as structured fields? If yes, name the fields and enumerate the reason codes. |
| **Q-4.4** | Does the final bar of a delisted series represent the **last trade**, or is a **terminal value** supplied (e.g. cash-merger consideration, or a zero/near-zero value on a receivership)? A price series that simply stops understates the loss to any strategy that held the name. |
| **Q-4.5** | When a delisted company continues to trade OTC under a **different ticker**, are the two series linked by a stable identifier? Concretely: for **First Republic Bank**, which traded as `FRC` on NYSE until 2023-05-01 and subsequently OTC as `FRCB`, does your API return a continuous, identifier-linked history, and does it include the terminal collapse? |
| **Q-4.6** | Are **ticker symbols ever reused** across different companies in your data, and if so, what identifier distinguishes them? |
| **Q-4.7** | **[ALL]** Are **fundamentals and shares-outstanding records** (see [A.6](#a6--p-6-point-in-time-universe-implications-new-work)) retained for delisted names on the same terms as prices, or are they dropped? |

### Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-4.1 | "Yes, retained indefinitely" | Removal on delisting — this is the silent-failure class named in [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3.2 (HTTP 200, empty series, no warning) and it is disqualifying for any survivorship-free claim |
| Q-4.2 | Answer **(a)** — 2007 is the earliest *delisting* date retained, with bars extending as far back as the name traded | Answer **(b)** — the universe and every backtest are then capped at 2007, and that cap must be written into the product's honest claims and into HD-07's provisional-labelling rule |
| Q-4.3 | Structured date **and** reason | Neither — reconstructing reasons by hand is the analyst-hours cost that [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §5.1 quantifies as the real price of the "free" path |
| Q-4.4 | Terminal value supplied, or an explicit statement that it is not | An unstated answer is the worst case: a series that stops looks identical to a series that ended at its last traded price, and the difference is the entire economic content of a failure |
| Q-4.5 | Identifier-linked, continuous | Ticker-keyed only — see Q-3.6 |
| Q-4.7 | Retained | Dropped — the point-in-time universe then cannot rank a name in the period before it failed, which reintroduces the bias at the universe layer even if prices are complete |

---

## A.5 — P-5: Redistribution / display rights

**Why it matters.** 4UR4's core value is explainability: the user sees the chart with the
trendline overlaid, which shows the vendor's highs, lows and closes to a paying subscriber.
That is **category 3 — raw-data display/redistribution** in
[`data-provider-findings.md`](data-provider-findings.md) §7.1, not merely category 2
(derived-signal display). Almost every cheap tier surveyed is category-1-only, and that, not
price, is what removes it.

**Already established for the leading candidate** (§7.2 A0, **VERIFIED** at
<https://intrinio.com/pricing>): the licence class is stated as a **tier attribute on the
price list** — Individual = "No redistribution or external display"; **Startup =
"Display & Commercial Use", business-wide licence**. No other candidate publishes this.
The questions below exist to convert a price-list phrase into a contract term.

### Questions

| # | Exact question to put to the vendor |
|---|---|
| **Q-5.1** | Confirm that the **Startup** tier's "Display & Commercial Use" licence permits us to **render your price bars (open, high, low, close) inside charts shown to our own paying subscribers**, in a web and mobile application we own and operate. State the clause of the agreement that grants this. |
| **Q-5.2** | Is that grant **limited by the number of end users** who view the data, by revenue, or by any other metric? If we grow from 10 subscribers to 10,000, does the licence or the price change, and at what thresholds? |
| **Q-5.3** | Does the grant cover **derived values** we compute from your data — a trendline, a breakout flag, a 0–100 heuristic confidence score — displayed **without** the underlying bars? Confirm these are permitted derived data and not "redistribution of the original data". |
| **Q-5.4** | Your terms state that if an AI system can reproduce, approximate, or reveal Intrinio data such that a user could infer or reconstruct the original data, that is treated as **original data redistribution, not purely derived output**. Confirm that a **chart-pattern confidence score and a breakout flag** fall on the *derived* side of that line, and describe what would put a derived product on the *redistribution* side. |
| **Q-5.5** | May we allow subscribers to **export** what they see — a CSV of a chart, a screenshot, a shared link? If not, we must build export restrictions, and we need to know that before we design the product. |
| **Q-5.6** | Does the licence permit **US exchange-fee-free** consumption at **T+1** (bars for completed prior sessions only, never intraday or 15-minute-delayed)? Confirm that **no exchange entitlement, display or per-subscriber fee attaches** at that cadence, and that no such fee is passed through on the Startup tier. |
| **Q-5.7** | Are we required to **report our end users** to you or to any exchange, and if so at what granularity and frequency? |
| **Q-5.8** | What **attribution** must appear, in what wording, and where? |
| **Q-5.9** | **[ALL]** May we retain and display **derived results** (backtest statistics, calibration tables, historical signal records) **after** a subscription ends? (This is the hinge between P-5 and [P-8](#a8--p-8-cancellation-and-data-retention-constraints-new-work) and must be answered as one question, not two.) |
| **Q-5.10** | **[Massive only]** Your business terms prohibit using the Information to "create derivative works (including, without limitation, any index, indicative value, net asset value, investment product, financial contract, settlement value or investment strategy) … unless licensed to do so." Is a **0–100 heuristic quality score describing a chart pattern**, presented explicitly as decision support and never as a probability or an expected return, a prohibited derivative work under that clause? Answer specifically for that construct. |
| **Q-5.11** | **[EODHD only]** Does the **Enterprise** plan's Data Services Agreement grant **external display to our end users** as a standard entitlement, or is that a separately negotiated and separately priced term? |

### Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-5.1 | A named clause granting external display to the customer's end users | A pointer back to the marketing page. The price list says "Display & Commercial Use"; the **contract** must say it, or the price list is not the licence |
| Q-5.2 | Either unlimited end users, or stated thresholds with stated prices | Undisclosed thresholds. A per-user step that appears at scale converts a fixed cost into a variable one and invalidates the year-1 and recurring figures in [C.1](#c1--the-leading-candidate) |
| Q-5.3 / Q-5.4 | Confirmation that scores and flags are derived data | Any answer treating a derived score as redistribution — 4UR4 **is** a derived-data product, and a licence that gates the creation of its core artefact is the wrong foundation at any price (the Tiingo finding, §7.2 D) |
| Q-5.6 | "No exchange fees at T+1" | Exchange fees attaching at T+1 — this would add ~$2,000+/month **plus per-subscriber display fees that grow with the business** (§8.3 Scenario C) and change the cost category, not the cost |
| Q-5.9 | Derived results may be retained | "All derived material must be deleted on termination" — see [A.8](#a8--p-8-cancellation-and-data-retention-constraints-new-work). This is the Norgate clause, and it reaches 4UR4's own computed trendlines and scores |
| Q-5.10 | "A chart-pattern confidence score is not a prohibited derivative work" | Confirmation that it **is** — this removes Massive from contention entirely rather than demoting it (§13.5), and would leave the ranking with no runner-up at the same quality level |

---

## A.6 — P-6: Point-in-time universe implications (**new work**)

> **This prerequisite exists only because of the 2026-07-26 universe ruling.** 4UR4 will
> compute its own point-in-time universe of the **500 largest eligible US-listed operating
> companies** (working name **4UR4 US Large-Cap 500**) rather than license S&P 500 membership.
> No prior *provider* research covers it, because the question did not exist when that
> research ran.
>
> **This section is the vendor-facing half of gap G-U8** in
> [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
> §12. That design ranks **SEC EDGAR primary filings and SEC XBRL structured data ahead of any
> vendor** for this input (§4.3), because EDGAR is survivorship-complete by construction.
> **Nothing here proposes buying a fundamentals dataset**, and nothing here pre-empts **OQ-U4**
> (whether R9 opens, and whether any spend attaches to it). The questions establish what the
> candidates *can* supply, so that the free-path-versus-paid-path choice is made on evidence.

### A.6.1 The chain the ruling creates, and where it breaks

The ruling replaces a *licensing* problem with a *data* problem, and the new problem has a
longer dependency chain — set out in
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
§4.1 and reproduced here in the form the vendor questions attack:

**500 largest eligible US-listed operating companies, as of date *d*** requires
**point-in-time market capitalisation**, which requires a **point-in-time RAW close** *and*
**point-in-time shares outstanding**, which requires **an as-of-time-correct
shares-outstanding history — including for names that have since delisted** — plus a
**point-in-time eligibility classification** (security type, domicile, listing venue,
operating-company status).

Only the first link is covered by existing provider research. That is the gap this section
fills with questions.

**Two hazards, both named in the methodology and both invisible in the data.**

**(1) The filing-lag look-ahead.** Shares outstanding is reported in SEC filings, and a filing
for a period ending 2010-03-31 is not *public* until it is accepted, typically weeks later. A
dataset keyed on **period end** silently lets a backtest on 2010-04-15 use a number that was
not knowable until 2010-05-10. `UR-PIT` rule 1 makes this binding: the observation used for
reference date *r* is the one with the greatest `value_as_of` **among those with
`filed_at ≤ r`** — the SEC **acceptance timestamp**, not the period end. Under
[HD-12](human-decisions.md) and
[`survivorship-bias-findings.md`](survivorship-bias-findings.md) §9 item 2, this is exactly
the class of defect 4UR4 has already ruled against in the engine layer. It would be perverse
to close it in the engine and reopen it in the universe.

**(2) The two-share-counts trap.** A filing contains **two different share counts**: the
**cover-page** figure, true as of a date shortly before filing, and the **financial-statement**
figure, true as of the period end. They are different numbers. Mixing them, per
`universe-methodology.md` §4.2, "produces market caps that are wrong by a quarter's worth of
buybacks and issuance, consistently, and with no error to observe." Intrinio's endpoint is
documented as returning **the cover-page figure**. Q-6.15 exists so that every vendor states
which one it serves rather than leaving it to be discovered.

**(3) The restated-fundamentals trap.** Many fundamentals datasets show *today's best value*
for a historical period rather than the value knowable at the time. Such a dataset violates
the causality rule no matter how carefully the rest of the pipeline is written, and it does so
invisibly. `universe-methodology.md` §4.3 requires that any evaluation ask, **in writing**,
whether the dataset is as-reported with filing timestamps or restated, and **reject a vendor
that cannot answer**. Q-6.3 and Q-6.4 are that question.

**What the documentation says today, and why it is not yet reassuring.**

| Provider | Documented behaviour | Source (retrieved 2026-07-26) | Tag |
|---|---|---|---|
| **Intrinio** — Shares Outstanding by Company | "Returns the shares outstanding reported on the front cover of the SEC 10-K and 10-Q filings." Response fields include `shares_outstanding`, `adj_shares_outstanding` ("The shares outstanding adjusted for stock splits"), `end_date` ("End date of the filing period"), `xbrl_axis`, `xbrl_member`, `title_of_security`, `trading_symbol`. Filters offered are `end_date_greater_than` / `end_date_less_than` | <https://docs.intrinio.com/documentation/web_api/shares_outstanding_by_company_v2> | **VERIFIED** |
| **Intrinio** — same endpoint, **filing-date semantics** | **No filing-date or acceptance-date field, and no as-of parameter, is documented on the page read.** Only period-end filters | ibid. | **GAP — the decisive one for U-5** |
| **Intrinio** — historical data by tag | Historical time series per company for a data tag, with `frequency`, `type` (FY/QTR/TTM), `start_date`, `end_date`, `sort_order`; `marketcap` is a documented tag | <https://docs.intrinio.com/documentation/web_api/get_company_historical_data_v2>, <https://data.intrinio.com/data-tag/marketcap> | **PARTIAL** — the endpoint exists; **whether its values are as-reported-at-the-time or as-restated-today is not documented on the page read** |
| **Massive** — Ticker Overview | "Retrieve comprehensive details for a single ticker supported by Massive that is active as-of a given date." `date` parameter: "Specify a point in time to get information about the ticker available on that date. **When retrieving information from SEC filings, we compare this date with the period of report date on the SEC filing.**" Fields: `share_class_shares_outstanding`, `weighted_shares_outstanding`, `market_cap` ("The most recent close price of the ticker multiplied by weighted outstanding shares"), `delisted_utc`, `active`, `cik` | <https://massive.com/docs/rest/stocks/tickers/ticker-overview> | **VERIFIED** |
| **EODHD** — Fundamentals | `SharesStats.SharesOutstanding`, `SharesStats.SharesFloat`; `outstandingShares.annual` and `.quarterly`, each entry carrying `date`, `dateFormatted`, `sharesMln`, `shares`. Fundamentals coverage: "Major US companies are covered from 1985 (40+ years)… Minor companies have the last 6 years and 20 quarters." `General.IsDelisted` exists | <https://eodhd.com/financial-apis/stock-etfs-fundamental-data-feeds> | **VERIFIED** (fields and general depth); **GAP** on `outstandingShares` depth specifically |

**Two readings of that table deserve to be stated rather than left implicit.**

1. **Massive has the point-in-time mechanism and the wrong key.** A `date` parameter is
   exactly the right shape — and the documentation says it compares that date against the
   **period of report date**, not the filing or acceptance date. On the plain text, an as-of
   query for 2010-04-15 can therefore surface a figure from a report whose period ended
   2010-03-31 but which was not filed until weeks later. Q-6.3 exists to test that reading; it
   may be wrong, and the vendor is the only party who can say so.
2. **Intrinio has the right source and no documented as-of key at all.** The SEC cover-page
   figure is the correct primitive, and `adj_shares_outstanding` conveniently matches HD-01's
   split-adjusted basis — but with only period-end filters documented, the consumer cannot ask
   "what did we know on date *d*?" without also holding filing dates from somewhere else.

### A.6.2 Questions

| # | Exact question to put to the vendor |
|---|---|
| **Q-6.1** | Do you provide a **historical time series of shares outstanding** for US common stocks — not merely the current value? State the endpoint, the frequency (per filing, quarterly, or daily), and the earliest date covered. |
| **Q-6.2** | For each shares-outstanding record, which dates are supplied: the **period end date**, the **date the count is true as of**, the **SEC filing date**, and/or the **SEC acceptance datetime**? We require the date on which the figure **first became publicly knowable** — the acceptance timestamp — as a distinct field, not only the period it describes. |
| **Q-6.3** | Can we query shares outstanding, or market capitalisation, **as it was known on a given historical date** — i.e. using only records whose filing date is on or before that date? If your API has an as-of or point-in-time parameter, state **which date field it compares against**: period-of-report, filing date, or acceptance date. |
| **Q-6.4** | When a company **restates** or amends a shares-outstanding figure (10-K/A, corrections), is the original record **preserved alongside** the restatement, or **overwritten in place**? If preserved, how does a caller retrieve the original ("as first reported") value? |
| **Q-6.5** | Is `shares_outstanding` reported **per share class**, and do you supply a **total across classes** (or a weighted equivalent)? For dual-class companies, which figure should be used to compute total market capitalisation, and is that figure available historically? |
| **Q-6.6** | Are shares-outstanding figures **adjusted for splits**? If both raw and split-adjusted are available (e.g. `shares_outstanding` and `adj_shares_outstanding`), state the adjustment basis of each explicitly. We need **both**: our universe ranking multiplies the **raw, unadjusted close** by the **contemporaneous raw share count**, and we cross-check it against adjusted price × adjusted shares. A mismatch of bases misstates market capitalisation by the cumulative split factor and silently reorders the universe, with no error to observe. |
| **Q-6.15** | A 10-K or 10-Q contains **two different share counts**: the **cover-page** figure (true as of a date shortly before filing) and the **financial-statement** figure (true as of the period end). **Which of the two does your API return?** If both, how does a caller select between them, and is each stamped with its own as-of date? |
| **Q-6.7** | Do you supply shares-outstanding history for **delisted** companies, on the same terms and to the same depth as for active ones? State the earliest date. (This is the universe-layer version of Q-4.7, and without it a historical top-500 ranking cannot include companies that later failed.) |
| **Q-6.8** | Do you publish a **historical market capitalisation** series directly? If so: is it computed as price × shares outstanding **as known at each historical date**, or as price × **today's** shares outstanding applied backwards? Your ticker documentation defines `market_cap` as "the most recent close price of the ticker multiplied by weighted outstanding shares" — please state whether an as-of query recomputes both terms as of that date. |
| **Q-6.9** | To rank a whole market on a historical date we need shares outstanding for **every** US-listed name as of that date. Do you offer a **bulk or whole-market** endpoint that returns shares outstanding (or market cap) for all tickers on a given date in one call, or must we paginate ~10,000 symbols per rebalance date? |
| **Q-6.10** | Do you supply **point-in-time classification** fields needed for eligibility — security type (common stock vs ETF vs closed-end fund vs trust vs unit), country of domicile, primary listing venue, and an industry/sector code? Critically: are these **as they were on a historical date**, or only current state? A company's security type, domicile and listing venue can all change. |
| **Q-6.11** | Do you flag **ADRs, foreign private issuers, SPACs and shell companies** distinctly enough that they can be excluded from an "operating company" universe by rule rather than by hand? |
| **Q-6.12** | Is a **free-float share count** available historically, or only total shares outstanding? (**Not needed at v0.1.0** — `UR-RANK` ranks on full market capitalisation and explicitly rejects float adjustment. Ask only if a float basis is ever revisited; it is recorded as gap G-U4/G-U5 in the methodology.) |
| **Q-6.13** | Is a **stable non-ticker identifier** (CIK, FIGI, or your security ID) present on **every** record in the shares-outstanding, classification and price datasets, so that the three can be joined across ticker changes and delistings? |
| **Q-6.14** | Is shares-outstanding / fundamentals data included in the **Startup** tier, or is it a separately priced dataset? (Feeds directly into P-7 — the year-1 figure assumes prices only.) |

### A.6.3 Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-6.1 | A named endpoint with per-filing granularity and a stated earliest date | Current-value-only. Backwards-projecting today's share count is the *same* class of error as backwards-projecting today's index membership — it is survivorship bias wearing a different hat |
| Q-6.2 / Q-6.3 | **Filing date or acceptance date supplied**, and an as-of query that compares against it | An as-of parameter keyed only on **period of report** — usable, but only if filing dates are obtained separately (SEC EDGAR supplies them free), and the adapter must then enforce the lag itself. **Answering "we don't hold filing dates and there is no as-of query" is disqualifying for U-5**, because the universe would be non-causal by construction |
| Q-6.4 | Originals preserved and retrievable | Overwrite-in-place. A universe recomputed today would then differ from the universe as it stood, and no backtest built on it is reproducible — this is **DI-05**'s vintage requirement at the universe layer |
| Q-6.6 | Both bases available and explicitly labelled | A single unlabelled share count. A split-adjusted price multiplied by a raw share count is wrong by the cumulative split factor, and the error is largest for exactly the long-lived, split-heavy mega-caps that dominate a top-500 ranking |
| Q-6.15 | An explicit answer, ideally both figures with separate as-of dates | "We don't distinguish them." The two counts differ by a quarter of buybacks and issuance, systematically and invisibly — a vendor that cannot say which one it serves cannot be used for ranking |
| Q-6.7 | Delisted names covered, with a stated earliest date | Not covered — the universe is then survivorship-biased at the ranking step regardless of how complete the price history is. This is the single most important question in A.6 |
| Q-6.9 | A bulk endpoint | Per-symbol only — **not disqualifying**, but it turns each rebalance into ~10,000 calls and makes Q-7.5 (rate limits) load-bearing |
| Q-6.10 | Point-in-time classification | Current-state-only classification — eligibility would be evaluated with hindsight, a subtler survivorship bias that is easy to miss and hard to detect afterwards |
| Q-6.13 | CIK or FIGI everywhere | Ticker joins — see Q-3.6 and Q-4.5 |

**The alternative is the design's first choice, not a fallback.**
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
§4.3 ranks **SEC EDGAR primary filings** and **SEC XBRL structured data** *above* vendor
fundamentals, for a reason that is structural rather than financial: **EDGAR retains the
filings of companies that failed**, so a reconstruction built on the primary record is
survivorship-complete by construction, whereas every vendor dataset must be *proven* to retain
delinquent and delisted issuers (Q-6.7). Its cost is a text/XBRL extraction project and a hard
historical bound at the XBRL phase-in (gap G-U3, escalated as OQ-U5).

**So the vendor answers here are not deciding whether to buy — they are pricing an
alternative.** If the leading candidate answers Q-6.2, Q-6.3, Q-6.7 and Q-6.15 well, the
universe layer can ride on the price licence at no extra seam. If it does not, the universe
layer is sourced separately, and the two candidates worth a quote request in that event are
**Sharadar** via Nasdaq Data Link (its bundle advertises point-in-time fundamentals and
constituents from 1957 with prices from 1998 — <https://www.quantrocket.com/pricing/data/sharadar/>,
retrieved 2026-07-26, **UNVERIFIED**, third-party listing; pricing is **login-gated**, gaps
G-09/G1) and **EDGAR itself at zero licence cost**. Neither is recommended here. Both are
named so the fallback is a priced option rather than an absence.

---

## A.7 — P-7: Complete first-year and recurring cost

**The figure in the ruling and what it rests on.** ≈**$5,994 in year 1** is the Startup tier's
published ramp — "6 mo at $333, 6 mo at $666, $999 thereafter", billed quarterly — with
steady-state ≈**$11,988/year** (<https://intrinio.com/pricing>, retrieved 2026-07-26,
**VERIFIED**, recorded in [`data-provider-findings.md`](data-provider-findings.md) §8.1). It
assumes **no exchange entitlement fees**, which follows from T+1 consumption (§3.1,
**VERIFIED**).

**What that figure does not yet include, and each is a real category of spend:** a one-time
historical backfill charge; the fundamentals/shares-outstanding dataset needed for
[A.6](#a6--p-6-point-in-time-universe-implications-new-work); overage charges against
**unpublished** rate limits (gap G-03c); the cost of the *second* provider if depth or
point-in-time data must be composed; and the price after the Startup tier's qualification
lapses.

### Questions

| # | Exact question to put to the vendor |
|---|---|
| **Q-7.1** | Confirm the Startup tier's published ramp — six months at $333/mo, six months at $666/mo, $999/mo thereafter, billed quarterly — and confirm that the **total payable in the first 12 months is $5,994**. State the currency and whether sales tax or VAT is added. |
| **Q-7.2** | Is the ramp **contractual** for the full 12 months, or promotional and revocable? What is the **notice period and permitted uplift at renewal**, and is there a cap on the annual increase? |
| **Q-7.3** | What are the **qualification criteria** for the Startup tier (company age, revenue, funding, headcount)? What happens — and at what price — when we **no longer qualify**? Specifically, does the account move to the Enterprise minimum of $1,250/mo, and with how much notice? |
| **Q-7.4** | Is the **initial historical backfill** (full available history for ~10,000 US symbols) included in the subscription at no extra charge, or is there a one-time bulk-history fee or a call-volume surcharge? |
| **Q-7.5** | What are the **published rate limits** — calls per minute, per day, and any concurrency cap — on the Startup tier? Are limits **hard** (rejected calls) or **soft** (billed overage)? If overage is billed, at what rate? |
| **Q-7.6** | Which **datasets are included** in the Startup price: EOD prices, price adjustments/corporate actions, **shares outstanding and fundamentals**, security reference and classification, delisted securities? Please mark each as included or separately priced, with the separate price. |
| **Q-7.7** | Are there **seat limits** on a "business-wide licence", and does an additional seat or environment (staging, CI) cost anything? |
| **Q-7.8** | Are there **onboarding, setup, integration or minimum-term** fees of any kind not shown on the pricing page? |
| **Q-7.9** | Confirm that **no exchange entitlement, display, or per-subscriber fee** applies to T+1 end-of-day US equity data on this tier, and that none is passed through. If any does apply, itemise it. |
| **Q-7.10** | **[ALL]** Provide a written quote covering: year-1 total, year-2 total, all included datasets, all one-time fees, and the price at 100 / 1,000 / 10,000 end users. A single all-in annual figure per scenario. |

### Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-7.1 / Q-7.2 | $5,994 confirmed in writing, ramp contractual, renewal uplift capped or stated | Ramp revocable at will — the year-1 figure in the ruling is then not a number, and a mid-ramp reprice would land exactly when the product has least revenue |
| Q-7.3 | Clear criteria, and a stated glide path when they lapse | An undisclosed cliff to $1,250+/mo. The Startup tier ranks first partly on price; a cliff makes the true multi-year cost closer to the runner-up's and narrows the ranking gap |
| Q-7.4 | Backfill included | A four- or five-figure one-time backfill charge — not disqualifying, but it must appear in the year-1 total before the Product Owner sees a number |
| Q-7.5 | Limits sufficient for ~500 symbols/day incremental plus a full backfill | Limits that cannot support the backfill without a higher tier — §13.5 already flags this as "re-open; likely a negotiation rather than a disqualification" |
| Q-7.6 | Prices **and** shares outstanding **and** reference data included | Shares outstanding priced separately — the year-1 figure rises by that amount, and the ruling's ≈$5,994 becomes a partial cost rather than a complete one, which is precisely what P-7 exists to prevent |
| Q-7.9 | Written confirmation of $0 exchange fees at T+1 | Any pass-through — the per-subscriber component grows with the business (§8.3 Scenario C) and changes the cost model's shape |

---

## A.8 — P-8: Cancellation and data-retention constraints (**new work**)

**Why this is now asked of every candidate, including the leading one.**
[`survivorship-bias-findings.md`](survivorship-bias-findings.md) §4.2 and §9 item 5 found that
**Norgate** requires deletion of "all copies of the Data, **including Derived Data**" on lapse,
and **EODHD** requires deletion of all copies within one month of termination. The conclusion
recorded there is the right one and it generalises: *a 4UR4 historical archive built on such
terms is **not ownable — it evaporates with the subscription***. That makes the archive a
**rental, not an asset**, and it makes provider switching a re-ingestion project rather than a
configuration change.

**Two findings today extend that from a two-vendor observation to a shortlist-wide one.**

**(1) The runner-up requires deletion too — and this had not been recorded.**

> **§11.4:** "Upon expiration or termination of this Agreement for any reason, all rights and
> licenses granted by Massive hereunder to Customer will immediately cease including the right
> to use the Information, **Customer must delete all Information in its possession**"
> — <https://massive.com/legal/businesses-terms-of-service>, retrieved 2026-07-26. **VERIFIED**

The clause is silent on **derived** works. That silence is not comfort: it is the ambiguity
Q-8.3 exists to resolve. (§5.4 of the same agreement permits retention of Confidential
Information "contained in electronic archives and backups made in the ordinary course of
business" and where required by law — a **backup** carve-out, not a licence to keep using the
data.)

**(2) The leading candidate's published terms are SILENT on post-termination deletion — and
silence is not permission.** Two Intrinio terms pages were read directly on 2026-07-26
(<https://docs.intrinio.com/terms> and <https://about.intrinio.com/terms>). Both contain
termination and survival machinery:

> "Either party may terminate these Terms upon written notice if the other party materially
> breaches any provision of these Terms … and fails to cure such breach within thirty (30)
> days after receiving written notice thereof."

> "Any sections or terms which by their nature should survive or are otherwise necessary to
> enforce the purpose of these Terms, will survive the termination of these Terms and
> termination of the Services."

> "You may cancel or suspend your Paid Services by contacting Intrinio at
> support@intrinio.com."

> "…the Services are billed in advance on an annual, quarterly, or monthly basis (as specified
> in the applicable Order Form) and are **non-refundable**."

**Neither page contains a clause stating whether Intrinio Data already received must be
deleted, may be retained, or may be retained in derived form after termination.** Recorded as
a **GAP**, not filled from memory. (A search summary reports Intrinio "reserves the right to
delete all of your Content, data, and other information stored on Intrinio's servers" —
**UNVERIFIED**, and in any case that concerns *Intrinio's* servers, not the customer's copies.
It does not answer this question.)

**Why the gap is more dangerous than a bad answer would be.** A written deletion requirement
is a known constraint that can be designed around. Silence, combined with a survival clause
covering "any terms which by their nature should survive", means the position is decided later
— by an Order Form, or by a dispute. **The right time to convert this from silence into a
written term is before signature, and only the Product Owner can do that.**

### Questions

| # | Exact question to put to the vendor — **all are [ALL]** |
|---|---|
| **Q-8.1** | On cancellation, expiry or termination for any reason, **may we retain the raw bars and corporate-action records already delivered to us during the paid term**? Answer yes or no, and cite the clause. |
| **Q-8.2** | If retention is not permitted: what is the **deletion deadline**, does it extend to **backups and disaster-recovery copies**, and is a **certificate of destruction** required? |
| **Q-8.3** | May we retain **derived data** computed from your data during the term — trendline geometry, breakout events, 0–100 confidence scores — where the derived values **cannot be reverse-engineered back to your original bars**? Answer separately from Q-8.1. |
| **Q-8.4** | May we retain **backtest results, calibration tables and performance statistics** computed from your data, given these are aggregate statistics from which no original bar can be reconstructed? Answer separately from Q-8.3. |
| **Q-8.5** | May we retain **historical signal records already shown to our subscribers** — a dated record that 4UR4 emitted a given signal — after termination? These are part of our audit trail and our users' history. |
| **Q-8.6** | Is a **perpetual licence to historical data already delivered** available, as a separate purchase or an Order Form term? If so, at what price? |
| **Q-8.7** | Is there a **wind-down or transition period** after termination during which we may continue to serve existing subscribers while migrating? |
| **Q-8.8** | If we cancel and later **re-subscribe**, do we re-acquire rights to data delivered under the earlier subscription, or must the entire history be re-ingested (and re-billed, see Q-7.4)? |
| **Q-8.9** | May the retention position in Q-8.1 and Q-8.3–Q-8.5 be **written into the Order Form** as an express term? We will not rely on silence. |
| **Q-8.10** | What is the **minimum commitment** and the **notice period** to cancel? For a quarterly-billed plan, is the effective minimum one quarter? Are prepaid amounts refundable on cancellation? |

### Acceptable vs disqualifying answers

| Question | Acceptable answer | Disqualifying answer |
|---|---|---|
| Q-8.1 | "Yes, delivered historical data may be retained" — best case, and rare | "All copies must be deleted" — **not disqualifying on its own** (it is the market norm; Norgate, EODHD, Twelve Data, Tiingo and Finnhub all impose some version), but it must be recorded as a **strategic** constraint: the archive is a rental, switching cost is a re-ingestion project, and business continuity depends on continued payment |
| Q-8.3 | "Yes, non-reversible derived data may be retained" | "Derived data must also be deleted" — this is the **Norgate clause**, and it reaches 4UR4's own trendlines and scores. On a leading candidate this would be close to disqualifying: it would mean the product's own output is destroyed if the subscription lapses, which is a single-point-of-failure on the company's core asset |
| Q-8.4 | "Yes, aggregate backtest results may be retained" | "No" — Confidence-v1 calibration and every lift claim would then be **unreproducible and undisplayable** after termination, which affects what the product may honestly claim to users |
| Q-8.6 | A perpetual option exists and is priced | No such option — acceptable, but then the retention answer above is the whole story |
| Q-8.9 | "Yes, we will write it into the Order Form" | Refusal to reduce it to writing. Given that the published terms are **silent**, a refusal to make it express leaves 4UR4 relying on an unwritten understanding about its own archive |
| Q-8.10 | Stated minimum and notice period | An undisclosed multi-year minimum — which would also invalidate the "$5,994 for year 1" framing by making year 2 non-optional |

**Design consequence, whatever the answers.** `data/` should treat vendor bars as **replaceable
input, never as the system of record for anything 4UR4 must keep**. Derived artefacts that
must survive a provider change — signal records, calibration tables, backtest outputs — should
be stored so that they carry **no reconstructable vendor bars**, which is both the licence-safe
posture and the architecture-honest one. That is DI-05 and DI-09 read through P-8.

---

# Part B — What is already answered, and how firmly

One table per prerequisite. **Current best answer, source, retrieval date, confidence.** Rows
sourced from prior research cite it rather than re-deriving it; rows marked **[new]** were
closed by this document from public documentation, without contacting anyone.

## B.1 — P-1: Consolidated-tape high/low

| Candidate | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio** | EOD price docs are **silent** on high/low construction; the real-time SDK references CTA/UTP SIP feeds and `UpdateHighLowConsolidated` vs `UpdateHighLowMarketCenter` conditions; tier not stated | [`data-provider-findings.md`](data-provider-findings.md) §2.3, G-03b | 2026-07-26 | **GAP** — this is blocking condition **C-1** |
| **Intrinio** **[new]** | Upstream named: "Raw historical end of day prices are sourced from our data partner EDI." | <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices> | 2026-07-26 | **VERIFIED** |
| **EDI (upstream)** **[new]** | EDI sells both per-exchange and **US Composite (CTA)** EOD files and recommends the composite: "The US Composite end of day price file represents trading that occurs on all the exchanges that are part of the CTA and we feel that this is what you should use instead of the individual exchanges." | <https://www.exchange-data.com/faqs-end-of-day-prices/> | 2026-07-26 | **VERIFIED** — but **which file Intrinio buys is a GAP** |
| **EDI (upstream)** **[new]** | Data elements: "open, high, low, close, traded volume & value and number of transactions" | <https://www.exchange-data.com/product/end-day-pricing-data/> | 2026-07-26 | **VERIFIED** |
| **Massive** | Consolidated across all exchanges; per-sale-condition `updates_high_low` rule published; follows SIP consolidated processing guidelines; no extended-hours deviation at daily granularity | [`data-provider-findings.md`](data-provider-findings.md) §2.3 | 2026-07-26 | **VERIFIED** — best in survey |
| **EODHD** | Not documented on any page reached | [`data-provider-findings.md`](data-provider-findings.md) §2.3 | 2026-07-26 | **GAP** |
| **Alpaca** (cross-check only) | SIP consolidated (~100% of volume) vs IEX (~2.5%); condition-level daily-bar high/low rules published; SIP daily bars free for data >15 min old | [`data-provider-findings.md`](data-provider-findings.md) §2.3, §8.2 | 2026-07-26 | **VERIFIED** |

**Net position on P-1:** **not closed.** It has, however, been converted from an unanswerable
question ("how does Intrinio build highs?") into a binary one ("which EDI file?"), which a
vendor can answer in one sentence.

## B.2 — P-2: Exact historical-depth coverage

| Candidate | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio** | "Over 50 years of history, making it one of the deepest EOD stock price datasets available via API" | <https://intrinio.com/financial-market-data/stock-prices-eod> | 2026-07-26 | **VERIFIED** (marketing page) |
| **Intrinio** **[new]** | "History is available back to the 1960s for actively trading securities (where applicable) and 2007 for delisted securities." | <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices> | 2026-07-26 | **VERIFIED** |
| **Intrinio / EDI** **[new]** | Upstream EDI states: "End of Day prices goes back to 1 Jan 2007 unless the exchange started traded on later day then we will have it from that day." | <https://www.exchange-data.com/faqs-end-of-day-prices/> | 2026-07-26 | **VERIFIED** — **contradicts the 1960s claim unless a second source exists** |
| **EDI historical archive** **[new]** | A separate "US Equities Historical Reference Services" line exists (with Financial Information Inc.), covering obsolete securities; **price-history depth not stated** | <https://www.exchange-data.com/product/us-equities-historical-reference-services/> | 2026-07-26 | **UNVERIFIED** — search summary only |
| **Massive** | Bars from **2004**; split history from 1978; plan-gated ("20+ Years" on Advanced/Business) | [`data-provider-findings.md`](data-provider-findings.md) §2.1 | 2026-07-26 | **VERIFIED** |
| **EODHD** | Pricing page "30+ years for US companies" vs its own academy article "from January 2000" | [`data-provider-findings.md`](data-provider-findings.md) §2.1, G-02 | 2026-07-26 | **VERIFIED (both) — CONTRADICTORY** |
| **Norgate** (licence-excluded) | Diamond back to 1950; Platinum to 1990 | [`data-provider-findings.md`](data-provider-findings.md) §2.1 | 2026-07-26 | **VERIFIED** |
| **Per-symbol first-bar dates, any vendor** | Not obtainable without an API key | [`data-provider-findings.md`](data-provider-findings.md) §0, G-01 | 2026-07-26 | **GAP** — see [Part D](#part-d--what-cannot-be-answered-without-spending-or-contacting) |

**Net position on P-2:** **materially weakened since the recommendation was written.** Depth
was the sole ground for ranking Intrinio first; the upstream's own FAQ puts that ground in
question. This is proposed as a **new blocking condition** (C-2, [Part C](#c4--blocking-conditions-proposed)).

## B.3 — P-3: Split-only adjustment availability

| Candidate | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio** | Raw OHLC published, plus a price-adjustments dataset exposing `factor`, `dividend` and `split_ratio` **independently** — HD-01 basis is self-derivable | [`data-provider-findings.md`](data-provider-findings.md) §2.2 | 2026-07-26 | **VERIFIED** |
| **Intrinio** | `adj_*` fields are adjusted for splits **and dividends** — must be banned in the adapter (DI-06b) | <https://docs.intrinio.com/documentation/web_api/get_security_stock_prices_v2> | 2026-07-26 | **VERIFIED** |
| **Intrinio** **[new]** | EOD product page lists "Split ratio and date" and "Ex-dividend amount and date" as supplied fields, i.e. the split spine is a first-class deliverable | <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices> | 2026-07-26 | **VERIFIED** |
| **Intrinio** | Whether a split-only *series* is offered directly | [`data-provider-findings.md`](data-provider-findings.md) G-03d | 2026-07-26 | **GAP** — low risk; the self-applied path is preferred anyway |
| **Massive** | `adjusted` defaults to split-only, dividends never applied to bars, `adjusted=false` returns raw — exactly HD-01 | [`data-provider-findings.md`](data-provider-findings.md) §2.2 | 2026-07-26 | **VERIFIED** |
| **EODHD** | Raw OHLC; `adjusted_close` is splits+dividends; split-only via the Technical API `function=splitadjusted` | [`data-provider-findings.md`](data-provider-findings.md) §2.2 | 2026-07-26 | **VERIFIED** |
| **All candidates** | Spin-off and merger event coverage | [`data-provider-findings.md`](data-provider-findings.md) §4, G-08 | 2026-07-26 | **GAP** |
| **All candidates** | Whether the adjustment flag actually adjusts (no-op reports at two vendors) | [`data-provider-findings.md`](data-provider-findings.md) §2.2, G-17 | 2026-07-26 | **GAP — closable only by a sample pull** |

**Net position on P-3:** **substantially answered** for all three shortlisted candidates. The
residue is spin-off/merger coverage and the no-op risk, neither of which a vendor answer can
fully close.

## B.4 — P-4: Delisted-history coverage

| Candidate | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio** **[new]** | "…and **2007 for delisted securities**" — the first delisted-coverage statement recorded for the leading candidate | <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices> | 2026-07-26 | **VERIFIED** |
| **Intrinio** **[new]** | "10,000+ active and delisted securities" reported for EOD prices | Search summary of Intrinio pages | 2026-07-26 | **UNVERIFIED** — not confirmed on a directly-read page |
| **Intrinio** | Whether 2007 is the earliest delisting date or the earliest bar date; delisting reason codes; terminal values | — | 2026-07-26 | **GAP** — Q-4.2, Q-4.3, Q-4.4 |
| **Massive** | All Tickers with `active=false`; `delisted_utc` = "The last date that the asset was traded"; **no delisting-reason field** | [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3.1; <https://massive.com/docs/rest/stocks/tickers/ticker-overview> | 2026-07-26 | **VERIFIED** |
| **EODHD** | Delisted tickers retrievable; **no delisting-date field** in the documented response; reason not supplied | [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3.1 | 2026-07-26 | **VERIFIED** |
| **Norgate** (licence-excluded) | "25222 delisted securities from the start of 1950 to Sep 2022"; Platinum/Diamond only | [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3.1 | 2026-07-26 | **VERIFIED** |
| **Any candidate** | Whether a complete `FRC`/`FRCB` series with a terminal value is returned | [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §5.3, G6 | 2026-07-26 | **GAP — requires an account and a pull** |
| **General** | Delisting returns are systematically missing for negative-reason delistings even in CRSP | Shumway 1997, via [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3.3 | 2026-07-26 | **VERIFIED** — an industry-wide residual risk, not a vendor defect |

**Net position on P-4:** **partially closed, and the answer is worse than assumed.** A 2007
delisted-history floor on the leading candidate caps the survivorship-bias-free universe and
backtest window. Q-4.2 decides how severe that cap is.

## B.5 — P-5: Redistribution / display rights

| Candidate | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio Startup** | Licence class stated on the price list: Startup = "**Display & Commercial Use**", business-wide | <https://intrinio.com/pricing> | 2026-07-26 | **VERIFIED** |
| **Intrinio Individual/Starter** | "No redistribution or external display"; Starter is "Individual, Non-Business, Non-Display, and Non-Redistribution Use, only" | <https://docs.intrinio.com/terms>, <https://intrinio.com/guides/starter-plan> | 2026-07-26 | **VERIFIED** |
| **Intrinio derived-data clause** | "If an AI system can reproduce, approximate, or reveal Intrinio data in a way that a user could infer or reconstruct the original data, it is treated as original data redistribution, not purely derived output." | <https://docs.intrinio.com/terms> | 2026-07-26 | **VERIFIED** — 4UR4's scores sit on the safe side; the **chart** is covered by the display right |
| **Massive Business** | Grant extends to "Edge Users" = "individuals or entities that are users of Customer's products and services" | <https://massive.com/legal/businesses-terms-of-service> | 2026-07-26 | **VERIFIED** |
| **Massive derivative-works clause** | Prohibits creating "any index, indicative value, net asset value, investment product, financial contract, settlement value or investment strategy" from the Information "unless licensed to do so" | <https://massive.com/legal/businesses-terms-of-service> | 2026-07-26 | **VERIFIED — open legal question (G-04), see Q-5.10** |
| **EODHD** | Internal Use $399/mo explicitly forbids external display; Enterprise adds a Data Services Agreement but **external display is not published as an entitlement** | <https://eodhd.com/commercial-pricing>, <https://eodhd.com/financial-apis/terms-conditions> | 2026-07-26 | **VERIFIED (text) / GAP (entitlement)** — G-05, see Q-5.11 |
| **Exchange fees at T+1** | "Exchanges require a license for any intraday or delayed data. Anything T+1 (24 hours and earlier) doesn't require a license." | <https://databento.com/blog/understanding-exchange-fees> | 2026-07-26 | **VERIFIED** — third-party but authoritative and specific |
| **Index-licence exposure** | Constituent data is licensed separately from index use, with separate fees | S&P Master Index License Agreement, SEC EDGAR, via [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §4.1 | 2026-07-26 | **VERIFIED** — **largely removed by the 2026-07-26 universe ruling**; see [C.5](#c5--residual-risks-that-survive-a-positive-answer) |

**Net position on P-5:** **the best-answered of the eight prerequisites**, and the only one
where the leading candidate's advantage is documented on the vendor's own price list. What
remains is contract confirmation (Q-5.1) and scale terms (Q-5.2), not discovery.

## B.6 — P-6: Point-in-time universe implications

| Item | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio shares-outstanding endpoint exists** **[new]** | "Returns the shares outstanding reported on the front cover of the SEC 10-K and 10-Q filings." | <https://docs.intrinio.com/documentation/web_api/shares_outstanding_by_company_v2> | 2026-07-26 | **VERIFIED** |
| **Intrinio fields** **[new]** | `shares_outstanding`, `adj_shares_outstanding` ("adjusted for stock splits"), `end_date` ("End date of the filing period"), `xbrl_axis`, `xbrl_member`, `title_of_security`, `trading_symbol`; filters `end_date_greater_than` / `end_date_less_than` | ibid. | 2026-07-26 | **VERIFIED** |
| **Intrinio filing-date / as-of semantics** **[new]** | **No filing-date field and no as-of parameter documented** on the page read | ibid. | 2026-07-26 | **GAP — the decisive one for HD-12 causality (U-5)** |
| **Intrinio historical market cap** **[new]** | Historical-data-by-tag endpoint exists with `frequency`, `type`, `start_date`, `end_date`; `marketcap` is a documented tag; as-reported vs as-restated **not documented** | <https://docs.intrinio.com/documentation/web_api/get_company_historical_data_v2>, <https://data.intrinio.com/data-tag/marketcap> | 2026-07-26 | **PARTIAL** |
| **Intrinio shares outstanding for delisted names** | Not stated anywhere reached | — | 2026-07-26 | **GAP** — Q-6.7 |
| **Massive point-in-time mechanism** **[new]** | `date` parameter: "Specify a point in time to get information about the ticker available on that date. When retrieving information from SEC filings, we compare this date with **the period of report date** on the SEC filing." | <https://massive.com/docs/rest/stocks/tickers/ticker-overview> | 2026-07-26 | **VERIFIED** — the mechanism exists; **the key it compares against is the look-ahead concern** |
| **Massive fields** **[new]** | `share_class_shares_outstanding`, `weighted_shares_outstanding`, `market_cap` ("The most recent close price of the ticker multiplied by weighted outstanding shares"), `delisted_utc`, `active`, `cik` | ibid. | 2026-07-26 | **VERIFIED** |
| **EODHD** **[new]** | `SharesStats.SharesOutstanding`, `SharesStats.SharesFloat`; `outstandingShares.annual` / `.quarterly` with `date`, `dateFormatted`, `sharesMln`, `shares`; `General.IsDelisted` | <https://eodhd.com/financial-apis/stock-etfs-fundamental-data-feeds> | 2026-07-26 | **VERIFIED** |
| **EODHD fundamentals depth** **[new]** | "Major US companies are covered from 1985 (40+ years); non-US symbols from 2000 … Minor companies have the last 6 years and 20 quarters." | ibid. | 2026-07-26 | **VERIFIED** for fundamentals generally; **GAP** for `outstandingShares` specifically |
| **Point-in-time eligibility classification, any vendor** | Whether security type, domicile and listing venue are available **as-of a historical date** rather than current-state | — | 2026-07-26 | **GAP** — Q-6.10, and unaddressed by any prior research |
| **Free-float history, any vendor** | EODHD exposes a current `SharesFloat`; historical float not established for any candidate | ibid. | 2026-07-26 | **GAP** — matters only under assumption U-1 |
| **Fallback specialist source** | Sharadar bundle advertises point-in-time fundamentals, prices from 1998, constituents from 1957 | <https://www.quantrocket.com/pricing/data/sharadar/> | 2026-07-26 | **UNVERIFIED** — third-party listing; **pricing login-gated (G-09/G1)** |

**Net position on P-6:** **the least-answered prerequisite, and the one with no prior provider
research to lean on** — it is gap **G-U8** in
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
§12, seen from the vendor side. Three findings stand out. The **mechanisms** exist at two of
three candidates, but their **as-of semantics** are either undocumented (Intrinio) or
documented in a way that reads as a look-ahead leak against period-of-report rather than
acceptance date (Massive). **No candidate documents a shares-outstanding history for delisted
names** — which is the requirement that decides whether the universe itself is
survivorship-biased. And **no candidate states which of the two share counts it serves**
(cover page vs financial statements), a distinction the methodology shows is worth a quarter
of buybacks and issuance, consistently and invisibly. Against that, the design's own first
choice — SEC EDGAR — is free, survivorship-complete by construction, and bounded only by the
XBRL phase-in.

## B.7 — P-7: Complete first-year and recurring cost

| Item | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio Startup price** | "$333/mo to start, billed quarterly — 6 mo at $333, 6 mo at $666, $999 thereafter"; business-wide licence | <https://intrinio.com/pricing> | 2026-07-26 | **VERIFIED** |
| **Year-1 total** | ≈**$5,994** (6 × $333 + 6 × $666); steady state ≈**$11,988/yr** | Arithmetic on the verified ramp; [`data-provider-findings.md`](data-provider-findings.md) §8.3 | 2026-07-26 | **VERIFIED** (derivation) / **GAP** (whether the ramp is contractual — Q-7.2) |
| **Billing terms** **[new]** | "…billed in advance on an annual, quarterly, or monthly basis (as specified in the applicable Order Form) and are **non-refundable**." | <https://about.intrinio.com/terms> | 2026-07-26 | **VERIFIED** — implies a practical minimum of one quarter |
| **Cancellation mechanism** **[new]** | "You may cancel or suspend your Paid Services by contacting Intrinio at support@intrinio.com." | <https://docs.intrinio.com/terms> | 2026-07-26 | **VERIFIED** — cancellation is a support request, not self-serve |
| **Intrinio rate limits** | Not published on the pricing page | [`data-provider-findings.md`](data-provider-findings.md) G-03c | 2026-07-26 | **GAP** — Q-7.5 |
| **Backfill / one-time fees** | Not published by any candidate | — | 2026-07-26 | **GAP** — Q-7.4, and **not previously asked by any research** |
| **Startup-tier qualification criteria** | Not published | — | 2026-07-26 | **GAP** — Q-7.3 |
| **Whether shares outstanding / fundamentals are included in Startup** | Not established | — | 2026-07-26 | **GAP** — Q-7.6; **this can move the year-1 figure** |
| **Exchange entitlement fees at T+1** | $0 — no exchange licence required for T+1 consumption | <https://databento.com/blog/understanding-exchange-fees>; [`data-provider-findings.md`](data-provider-findings.md) §3.1 | 2026-07-26 | **VERIFIED** |
| **Massive Stocks Business** | $1,999/mo = $23,988/yr; "up to 50% off first year" startup discount via sales, qualification required | <https://massive.com/business> | 2026-07-26 | **VERIFIED** |
| **EODHD commercial** | Internal Use $399/mo ($3,990/yr); Enterprise $2,499/mo ($24,990/yr) | <https://eodhd.com/commercial-pricing> | 2026-07-26 | **VERIFIED** |

**Net position on P-7:** **the published price is verified; the *complete* cost is not.** Four
separate cost categories (backfill, fundamentals, overage, qualification lapse) are unpriced,
and the ruling asked specifically for the **complete** first-year cost.

## B.8 — P-8: Cancellation and data-retention constraints

| Candidate | Current best answer | Source | Retrieved | Confidence |
|---|---|---|---|---|
| **Intrinio** **[new]** | **Silent.** Neither terms page contains a post-termination data-deletion or retention clause; termination, survival, cancellation and non-refundability clauses are present | <https://docs.intrinio.com/terms>, <https://about.intrinio.com/terms> | 2026-07-26 | **GAP by silence** — must be made express in the Order Form (Q-8.9) |
| **Intrinio** **[new]** | Search summary claims Intrinio "reserves the right to delete all of your Content, data, and other information stored on Intrinio's servers" | Search summary | 2026-07-26 | **UNVERIFIED** — and concerns Intrinio's servers, not the customer's copies |
| **Massive** **[new]** | §11.4: "Upon expiration or termination … all rights and licenses granted by Massive hereunder to Customer will immediately cease including the right to use the Information, **Customer must delete all Information in its possession**" | <https://massive.com/legal/businesses-terms-of-service> | 2026-07-26 | **VERIFIED** |
| **Massive** **[new]** | §5.4 permits retention of Confidential Information "contained in electronic archives and backups made in the ordinary course of business" and where required by law | ibid. | 2026-07-26 | **VERIFIED** — a **backup** carve-out, not a use grant |
| **Massive** **[new]** | Derived works are **not** mentioned in the §11.4 deletion obligation | ibid. | 2026-07-26 | **GAP — ambiguity, see Q-8.3** |
| **EODHD** | "Upon termination or expiration of the subscription, the subscriber is required to delete all copies of the data in their possession within one (1) month." | <https://eodhd.com/financial-apis/terms-conditions> | 2026-07-26 | **VERIFIED** |
| **Norgate** (licence-excluded) | Clause 21: "If a Licensee's subscription lapses, the Licensee must delete all copies of the Data, **including Derived Data**" | <https://norgatedata.com/subscribe/eula.php> | 2026-07-26 | **VERIFIED** — the sharpest form of the constraint |
| **Twelve Data** | "Store or cache Data beyond permitted timeframes" prohibited; deletion within 30 days of termination | <https://twelvedata.com/terms> | 2026-07-26 | **VERIFIED** |
| **Tiingo** | "Tiingo Data may be stored locally … **only while your applicable subscription remains active**"; derived data may be created or retained only with express written approval | <https://app.tiingo.com/tos/> | 2026-07-26 | **VERIFIED** |
| **Finnhub** | "All data must be deleted should your subscription to that data ends." | <https://finnhub.io/terms-of-service> | 2026-07-26 | **VERIFIED (proxy)** |
| **Every candidate** | Whether **backtest results** may be retained | — | 2026-07-26 | **GAP** — Q-8.4; no vendor addresses it |

**Net position on P-8:** **closed enough to be decision-relevant, and the finding is
uncomfortable.** Every candidate whose terms are explicit requires deletion. The leading
candidate is the only shortlisted vendor that does not — **because it says nothing**, which is
weaker than a written grant and must be converted into an express Order Form term before
signature. The general conclusion in
[`survivorship-bias-findings.md`](survivorship-bias-findings.md) §9 item 5 holds and now
applies to the shortlist as a whole: **the archive is a rental, not an asset.**

---

# Part C — Decision memo skeleton

> **HD-06 remains PENDING.** This section is **preparation, not authorization**. It records a
> leading candidate and explicitly withholds approval, exactly as the 2026-07-26 ruling
> requires. No provider is selected. No spend is committed. No terms are accepted.
>
> **[Issue #21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band confirmation is
> mandatory before any financial authorization.** Every artifact in this repository, including
> the rulings that authorize agent work, is authored by a single account. **That channel is
> not adequate authority for spending money**, and no comment on it — however worded — may
> stand as a financial commitment (HD-06 authority boundary, boundary 5).

## C.1 — The leading candidate

**Intrinio, Startup tier.**

| Item | Figure | Basis | Confidence |
|---|---|---|---|
| Year 1 | **≈$5,994** | 6 months at $333/mo + 6 months at $666/mo, billed quarterly | **VERIFIED** price list; **GAP** on whether the ramp is contractual (Q-7.2) |
| Recurring (year 2+) | **≈$11,988/yr** | $999/mo thereafter | **VERIFIED** price list; subject to renewal uplift (Q-7.2) and tier-qualification lapse (Q-7.3) |
| US exchange entitlement fees | **$0** | T+1 consumption requires no exchange licence | **VERIFIED** |
| Not yet in either figure | Backfill charge, fundamentals/shares-outstanding dataset, rate-limit overage, any second provider for depth or point-in-time data | — | **GAP** — Q-7.4, Q-7.6, Q-7.5 |

**Why it leads** (unchanged from [`data-provider-findings.md`](data-provider-findings.md)
§13.1): it is the only candidate with a **published external-display licence** that also has
the **history depth** the product structurally requires; the licence class is on the price
list rather than left to negotiation; HD-01 is satisfiable in the *auditable* way (raw OHLC
plus independently-published `split_ratio`); and the MVP and the SaaS cost the same, so buying
it at MVP acquires the SaaS licence at zero incremental cost.

**What this pack changes about that case.** The second of those four grounds — depth — is the
one now in question ([B.2](#b2--p-2-exact-historical-depth-coverage)). The other three are
undisturbed and remain well-evidenced.

## C.2 — The runners-up, and precisely what would flip the ranking

**Runner-up: Massive (formerly Polygon.io), Stocks Business — $1,999/mo, $23,988/yr**
(≈$11,994 in year 1 if the published "up to 50% off first year" startup discount applies).
It is the **correctness benchmark** of the survey: the only candidate publishing a
per-sale-condition `updates_high_low` rule, with default output already on the HD-01 basis, a
business licence naming 4UR4's exact case ("Edge Users"), a whole-market bulk daily endpoint,
and documented restatement behaviour. **It is second for exactly one reason: bars begin in
2004.**

**Third: EODHD — Internal Use $399/mo, Enterprise $2,499/mo.** The natural fallback if both
leaders fail. Cheapest licence-clean internal path; the most precise EOD delivery-time
commitment found; documented delisted coverage. Third because its own documentation
contradicts itself on depth, its wick construction is undocumented, and external display is a
negotiated rather than published entitlement.

**Ranking flippers.** The first six rows are
[`data-provider-findings.md`](data-provider-findings.md) §13.5, carried forward unchanged. The
last four are **new to this pack**.

| If this proves true | Then |
|---|---|
| Intrinio's EOD high/low are **not** consolidated-tape (C-1) | **Recommendation withdrawn.** Massive becomes first, with deep-history composition (DI-08) covering pre-2004 anchors |
| Intrinio's rate limits cannot support a 500-symbol daily batch or a full backfill | Re-open; likely a negotiation rather than a disqualification |
| A negligible number of eligible names have a pre-2004 ATH | Massive's only weakness largely evaporates and it becomes first on documentation quality, at roughly double the cost |
| EODHD confirms genuine 1990s daily history **and** consolidated wicks **and** written display rights | EODHD becomes a strong first — matching on correctness, beating on depth, competitive on price |
| Massive confirms the confidence score is a prohibited derivative work (Q-5.10) | Massive is removed from contention entirely, not merely demoted |
| 4UR4 decides it will **never** display price bars | The whole category-3 requirement drops away and cheap internal-use tiers become viable — a **product** decision, to be taken deliberately rather than by default |
| **[new]** Intrinio's pre-2007 daily OHLC does not exist, or exists only as close-only backfill (Q-2.3, Q-2.4) | **The ranking inverts immediately.** Depth is the sole ground on which Intrinio outranks Massive; a 2007 floor is *worse* than Massive's 2004 floor, and a wick-less pre-2007 backfill is worse still for an ATH-wick-anchored product |
| **[new]** Intrinio's delisted floor of 2007 is the earliest **bar** date rather than the earliest **delisting** date (Q-4.2) | The self-computed universe and every survivorship-bias-free backtest are capped at 2007. Not necessarily disqualifying — but it must be written into HD-07's provisional-labelling rule and into what the product may honestly claim |
| **[new]** No candidate supplies shares-outstanding history keyed on **acceptance date** for **delisted** names (Q-6.2, Q-6.7, Q-6.15) | The universe layer is sourced separately from the price layer — most likely from **SEC EDGAR at zero licence cost**, which `universe-methodology.md` §4.3 already ranks first. That is not a cost increase; it is a **seam**, and it bounds the backtest window at the XBRL phase-in (OQ-U5) rather than at the price vendor's history start |
| **[new]** The leading candidate will not put retention of **derived data and backtest results** in writing (Q-8.3, Q-8.4, Q-8.9) | Every candidate is then equivalent on the archive question, and the ranking reverts to correctness and cost. But the **product** must be designed on the assumption that the vendor archive is a rental — which is an architecture decision that should be taken now, not at renewal |

## C.3 — The one-line statement of position

**Intrinio Startup is the current evidence-based leading candidate at approximately $5,994 for
year 1 and approximately $11,988 recurring. It is not selected, not approved, and not
purchased. HD-06 remains PENDING.**

## C.4 — Blocking conditions (**proposed**)

C-1 is the existing blocking condition from
[`data-provider-findings.md`](data-provider-findings.md) §13.1. C-2 to C-5 are **proposed**
here for the Product Owner to accept, modify or reject — an agent may recommend conditions but
may not impose them.

| # | Condition | Status | Test that closes it |
|---|---|---|---|
| **C-1** | Written confirmation that daily EOD high/low are consolidated-tape (CTA/UTP) extremes, on the Startup tier | **Existing, open** | Q-1.1, Q-1.2, Q-1.5 answered in writing. "Primary listing only" or "the exchange-by-exchange EDI file" **withdraws the recommendation** |
| **C-2** | **[proposed]** Written resolution of the pre-2007 depth contradiction: the source of pre-2007 US daily OHLC, and confirmation it carries true intraday highs and lows | **Proposed, open** | Q-2.3 plus a per-symbol first-bar-date list (Q-2.4) showing `INTC` with bars at or before 2000 |
| **C-3** | **[proposed]** Written clarification of whether the delisted floor of 2007 is a delisting-date floor or a bar-date floor | **Proposed, open** | Q-4.2. Answer (b) caps the honest backtest window and must be recorded against HD-07 |
| **C-4** | **[proposed]** A point-in-time shares-outstanding path that is causal under HD-12 — filing-date keyed, covering delisted names | **Proposed, open** | Q-6.2, Q-6.3, Q-6.7. If unmet by the price vendor, the universe layer needs its own source and its own budget line |
| **C-5** | **[proposed]** An express Order Form term on post-cancellation retention of raw bars, derived signals and backtest results | **Proposed, open** | Q-8.1, Q-8.3, Q-8.4, Q-8.9. Silence is not an acceptable answer here — it is the current state, and it is what C-5 exists to fix |

**C-1 and C-2 are of the same kind and should be sent together**, because both are questions
about the same upstream (EDI) and a single reply can settle both.

## C.5 — Residual risks that survive a positive answer

Even if every question in Part A comes back favourably, these remain. They are not reasons to
delay; they are reasons the decision should be made with them written down.

| # | Residual risk | Why a favourable answer does not remove it |
|---|---|---|
| **R-1** | **No sample pull has been performed.** Every adjustment and wick claim in this pack and in prior research is *documentation-based* | A vendor's description of its data is not its data. Only acceptance tests §11.1–§11.3 close this, and they need an API key — which is a terms acceptance |
| **R-2** | **A documented adjustment flag can silently no-op** | Two surveyed vendors have public reports of exactly this. Indistinguishable from correct behaviour until re-derived |
| **R-3** | **Restatement and vintage** | If daily bars are restated and no as-of parameter exists, HD-12 causality is unenforceable at the data layer no matter how good the bars are |
| **R-4** | **Shared upstream defeats cross-checking** | Intrinio sources from EDI. Any second source that also resells EDI would agree perfectly while both are wrong. Alpaca's SIP feed is a genuinely independent upstream and is the right cross-check for that reason |
| **R-5** | **Prices and terms change** | Polygon.io rebranded to Massive and repriced; FMP reprices frequently. Every figure here is a point-in-time snapshot with a retrieval date, and must be re-verified at signature |
| **R-6** | **Startup-tier qualification can lapse** | A tier that ranks first partly on price may step to the Enterprise minimum with little notice |
| **R-7** | **The archive is a rental** | On every candidate with explicit terms, cancellation destroys the archive. Provider switching is a re-ingestion project, and continuity depends on continued payment |
| **R-8** | **Spin-off and merger coverage is a gap at every candidate** | A mishandled spin-off injects a false ATH exactly as an unadjusted split does. Requires a `data/` sanity check regardless of the vendor answer |
| **R-9** | **Delisting returns are systematically missing industry-wide** | Documented even in CRSP (Shumway 1997). A vendor answering "yes we have delisted history" does not mean the terminal loss is in it |
| **R-10** | **The universe ruling trades one risk for another** | Self-computing the universe removes S&P index-licence exposure (a real and quantified saving) and replaces it with **4UR4 owning its own methodology risk**: eligibility rules, rebalance timing and point-in-time correctness become 4UR4's defect surface, not a vendor's |
| **R-11** | **Ticker reuse and identity** | Solved only if CIK/FIGI is present on **every** dataset — prices, shares outstanding, classification. A partial answer leaves a silent join failure |

## C.6 — What the Product Owner is being asked to do next

Nothing in this list is a purchase, and none of it can be done by an agent.

1. **Decide whether to send the Part A questions**, and to whom. Q-2.4 and Q-1.2 are the two
   highest-value questions; a single email to Intrinio carrying C-1 and C-2 together would
   move HD-06 further than any additional agent research.
2. **Decide whether the free-tier checks in [Part D](#d3--what-the-product-owner-can-settle-in-minutes-with-a-free-tier-account)
   are worth minutes of your time.** Several would close GAPs that no amount of documentation
   reading can.
3. **Confirm or amend the proposed blocking conditions C-2 to C-5.**
4. **Note that HD-06 cannot be taken at all** until [#21](https://github.com/tomerYannay/4UR4/issues/21)'s
   out-of-band confirmation exists.

---

# Part D — What cannot be answered without spending or contacting

Stated explicitly, because the ruling asks for it and because the boundary between "research"
and "engagement" is exactly where an agent must stop.

**The structural constraint, restated.** Several questions — sample pulls, actual wick
fidelity, real coverage depth per symbol — can only be answered by **calling the API**. Calling
the API requires an **API key**. Issuing an API key requires **accepting terms**. Accepting
terms is forbidden to agents by the HD-06 authority boundary (boundary 3) and independently by
GOV-015. **This is not a limitation that more agent effort can overcome.**

## D.1 — Vendor-contact-only (a human must send an email; no spend, no account)

These need a reply from a person at the vendor. None requires payment. All are drafted in
Part A.

| Question | Prereq | Why documentation cannot settle it |
|---|---|---|
| Which EDI file Intrinio licenses; consolidated vs single market centre; sale-condition rule | P-1 | Intrinio's EOD docs are silent; only the vendor knows which upstream product it buys |
| Source and wick-fidelity of pre-2007 US history | P-2 | The vendor's marketing page and its named upstream's FAQ disagree; only the vendor can reconcile them |
| Delisted floor: delisting-date or bar-date | P-4 | The published sentence is genuinely ambiguous |
| Delisting reason codes and terminal values | P-4 | Not documented by any candidate |
| Spin-off and merger event coverage | P-3 | Not enumerated by any candidate |
| Display grant as a **contract clause**, end-user scaling thresholds, export rights | P-5 | The price list is not the licence |
| Whether a confidence score is a prohibited derivative work | P-5 | An interpretive question about a specific clause — only the counterparty's written position resolves it |
| EODHD Enterprise external-display entitlement | P-5 | Explicitly a negotiated term, not published |
| Filing-date vs period-end as-of semantics for shares outstanding | P-6 | The docs describe the parameter but not which date field it compares |
| Shares-outstanding coverage for delisted names | P-6 | Not documented by any candidate |
| Point-in-time security-type / domicile / venue classification | P-6 | Not documented by any candidate |
| Rate limits, backfill fees, dataset inclusion, qualification criteria, renewal uplift | P-7 | Unpublished for the leading candidate |
| Retention of raw bars, derived signals and backtest results after cancellation | P-8 | Intrinio's published terms are **silent**; only an Order Form term can fix that |
| Sharadar / Nasdaq Data Link and Siblis Research pricing and licence terms | P-6 fallback | Login-gated and unpublished respectively (G-09, G1, G2) |

**Caution the Product Owner should have before sending.** Asking a vendor a question is not
neutral — it opens a commercial conversation and puts you on a sales cadence. That is a normal
cost of buying software and is noted only so it is a decision rather than a side effect.
**Nothing in this repository has begun such a conversation.**

## D.2 — Requires an API key or a paid trial (issuing a key is accepting terms)

No candidate publishes a time-limited paid trial (**GAP**, G-14). The nearest published
concession is Massive's "up to 50% off first year" for qualifying startups, which is a
discount, not a trial. Each item below is already specified as an acceptance test in
[`data-provider-findings.md`](data-provider-findings.md) §11 — they are listed here so the
Product Owner can see which questions are *deferred by construction* rather than unanswered by
oversight.

| Item | Prereq | Corresponding acceptance test |
|---|---|---|
| **Wick fidelity, cross-vendor.** Pull daily bars for ~10 symbols from two vendors with **different upstreams** and assert agreement on **high** and **low** | P-1 | §11.1 — the single most important pre-purchase quality check |
| **Adjustment re-derivation.** Raw OHLC + split events, re-derive the split-adjusted series, assert agreement across a known split | P-3 | §11.2 — also the only check that catches a silently no-op adjustment flag |
| **Forbidden-field assertion.** Confirm the adapter refuses a dividend-adjusted field | P-3 | §11.3 |
| **Per-symbol depth.** Actual first-bar date for every universe symbol; assert it precedes the selected ATH | P-2 | §11.5 — Q-2.4 is the documentation-only substitute, and a much weaker one |
| **Delisted completeness.** Whether a complete, adjustment-correct `FRC`/`FRCB` series with a terminal value is returned | P-4 | [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §5.3, G6 — "the single highest-value item for a trial-based evaluation" |
| **Shares-outstanding as-of behaviour.** Query the same historical date twice and confirm no post-dated filing leaks in | P-6 | New — the universe-layer analogue of §11.6 |
| **Restatement / as-of correctness.** Read the same date with two `as_of` values across a known restatement | P-1, P-3 | §11.6 |
| **Throughput.** Whether the published or unpublished rate limits actually sustain a full backfill | P-7 | New |

**The honest summary of D.2:** the eight items above are the difference between *believing* the
data is right and *knowing* it is. They cost one API key and a day of work — and the API key is
the part an agent cannot supply.

## D.3 — What the Product Owner can settle in minutes with a free-tier account

**Only the Product Owner may create these accounts**, because creating one accepts terms.
Each of these is minutes of work and closes a gap that no amount of documentation reading can.

| Check | Free tier needed | Gap it closes | Estimated effort |
|---|---|---|---|
| **First-bar date for `INTC`, `GE`, `IBM`, `T`, `XOM`** on the leading candidate | Intrinio free/self-signup tier (if its history entitlement permits — the free tier's depth is itself unverified) | **C-2** — settles the pre-2007 contradiction empirically, without waiting for a sales reply | Minutes |
| **Consolidated-tape daily bars for the same symbols** as an independent comparison | **Alpaca Basic ($0)** — SIP consolidated bars are free for data older than 15 minutes, and Alpaca is a genuinely different upstream from EDI | **C-1** and R-4 — the only free, independent wick cross-check identified anywhere in this research | Under an hour |
| **Sharadar / Nasdaq Data Link pricing and licence type** | A Nasdaq Data Link account (free to create; pricing is behind the login, not behind a purchase) | **G-09 / G1** — the universe-layer fallback in [A.6](#a6--p-6-point-in-time-universe-implications-new-work) is currently unpriced | Minutes |
| **EODHD depth contradiction** (30+ years vs from-2000) for one symbol | EODHD free tier — 20 calls/day is enough for a handful of probes | **G-02** — decides whether EODHD is a real third option | Minutes |
| **Massive `date`-parameter behaviour** on Ticker Overview against a known filing | Massive Basic ($0) | **Q-6.3** — settles empirically whether the as-of query leaks post-dated filings | Under an hour |

**A caution that must travel with this list.** Alpaca's market-data terms incorporate NASDAQ
OMX agreements that **were not read** ([`data-provider-findings.md`](data-provider-findings.md)
G-16), and Intrinio's free/starter tier is explicitly "Individual, Non-Business, Non-Display,
and Non-Redistribution Use, only". **A free tier used for evaluation is still governed by
terms**, and evaluation on a non-business tier may itself be outside those terms for a company
account. That is a judgement for the Product Owner, made knowingly — it is precisely the kind
of decision boundary 3 reserves to a human.

## D.4 — What no one can answer, at any price

| Item | Why |
|---|---|
| Whether a **reconstructed** membership list is legally a derivative of S&P's licensed data | A legal question requiring counsel, not research ([`survivorship-bias-findings.md`](survivorship-bias-findings.md) G10). **Largely moot under the 2026-07-26 universe ruling** — 4UR4 no longer reconstructs S&P membership — but it returns if any comparison to the index is ever displayed |
| Whether **delisting returns** are complete for negative-reason delistings | Documented as systematically missing even in CRSP, the academic reference dataset (Shumway 1997). A residual bias 4UR4 must disclose, not solve |
| Whether the vendor's answers **remain true** after signature | Only a contractual term with a remedy makes an answer durable. This is the argument for Q-8.9 and for putting C-1's answer in the Order Form rather than in an email thread |

---

## Source log — sources newly retrieved for this document

Prior sources are logged in [`data-provider-findings.md`](data-provider-findings.md) §14 and
[`survivorship-bias-findings.md`](survivorship-bias-findings.md) §10 and are not repeated. All
rows below were retrieved **2026-07-26** without credentials, without an account, and without
submitting any form.

| Source | Used for | Result |
|---|---|---|
| <https://intrinio.com/docs/market-data/us-historical-end-of-day-prices> | "back to the 1960s… and 2007 for delisted securities"; "sourced from our data partner EDI"; fields supplied | Read — **VERIFIED** |
| <https://www.exchange-data.com/faqs-end-of-day-prices/> | US Composite (CTA) vs exchange-by-exchange files; "End of Day prices goes back to 1 Jan 2007" | Read — **VERIFIED** |
| <https://www.exchange-data.com/product/end-day-pricing-data/> | EDI data elements ("open, high, low, close, traded volume & value and number of transactions") | Read — **VERIFIED**; composite/CTA statement and depth **not** on this page |
| <https://www.exchange-data.com/product/us-equities-historical-reference-services/> | EDI/FII obsolete-securities archive; depth not stated | Search summary — **UNVERIFIED** |
| <https://docs.intrinio.com/terms> | Termination, 30-day cure, survival, cancellation by support request; **no post-termination deletion clause** | Read — **VERIFIED** (including the verified absence) |
| <https://about.intrinio.com/terms> | Billing in advance, non-refundable; **no post-termination deletion clause** | Read — **VERIFIED** (including the verified absence) |
| <https://docs.intrinio.com/documentation/web_api/shares_outstanding_by_company_v2> | SEC 10-K/10-Q cover-page source; `shares_outstanding`, `adj_shares_outstanding`, `end_date`; period-end filters only | Read — **VERIFIED** |
| <https://docs.intrinio.com/documentation/web_api/get_company_historical_data_v2> | Historical-data-by-tag endpoint; `frequency`, `type`, `start_date`, `end_date`; `marketcap` example | Read — **VERIFIED** (endpoint) / **PARTIAL** (as-of semantics) |
| <https://data.intrinio.com/data-tag/marketcap> | `marketcap` as a documented data tag | Read — **PARTIAL**; full tag directory not enumerable from the page reached |
| <https://massive.com/docs/rest/stocks/tickers/ticker-overview> | `date` point-in-time parameter and its period-of-report comparison; `share_class_shares_outstanding`, `weighted_shares_outstanding`, `market_cap`, `delisted_utc`, `active`, `cik` | Read — **VERIFIED** |
| <https://massive.com/legal/businesses-terms-of-service> | §11.4 deletion on termination; §5.4 backup carve-out; §11.1/§11.2 termination; §11.5 survival | Read — **VERIFIED** |
| <https://eodhd.com/financial-apis/stock-etfs-fundamental-data-feeds> | `SharesStats`, `outstandingShares` annual/quarterly, `General.IsDelisted`; fundamentals depth from 1985 | Read — **VERIFIED** |
| <https://www.quantrocket.com/sharadar/> | Sharadar point-in-time semantics, DAILY table, dimensions | Read — **did not contain** the requested detail; recorded as a **GAP** |
| <https://www.quantrocket.com/pricing/data/sharadar/> | Sharadar bundle contents (prices 1998, constituents 1957) | Third-party listing — **UNVERIFIED** |
| <https://massive.com/docs/rest/stocks/tickers/ticker-details> | Attempted first; wrong path | **HTTP 404** — superseded by `ticker-overview` |
| <https://eodhd.com/financial-apis/market-capitalization> | Attempted: a dedicated historical market-cap endpoint | **HTTP 404** — no such page; whether such an endpoint exists is a **GAP** |
| <http://help.intrinio.com/en/articles/2020475-delisted-securities> | Intrinio delisted-securities help article | Fetched but returned only navigation content — **not usable**; recorded rather than filled from the search snippet |

---

## Cross-references

- Provider evidence and ranking: [`data-provider-findings.md`](data-provider-findings.md)
  §2 (depth, adjustment, wicks), §7 (licensing), §8 (cost), §9 (DI-01…DI-12), §11 (acceptance
  tests), §13 (recommendation), §13.5 (what would change the ranking)
- Survivorship, delisted and constituent evidence:
  [`survivorship-bias-findings.md`](survivorship-bias-findings.md) §3 (delisted), §4.1 (index
  licensing), §4.2 (vendor terms), §5.3 (First Republic), §9 (open items)
- Price-adjustment basis: [`human-decisions.md`](human-decisions.md) — **HD-01**
- Provider selection and spend (**PENDING**): [`human-decisions.md`](human-decisions.md) —
  **HD-06**, including the 2026-07-26 authority boundary
- Constituents / delisted need (approved, purchase human-gated):
  [`human-decisions.md`](human-decisions.md) — **HD-07**
- As-of-time causality: [`human-decisions.md`](human-decisions.md) — **HD-12**
- Wick semantics: [`trendline-specification.md`](trendline-specification.md) §3, §4
- `data/` seam: [`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) §3.2, §9
- Universe methodology:
  [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
  — §2.5 `UR-RANK` (raw close × contemporaneous shares, full cap, not float-adjusted),
  §4.1 the dependency chain, §4.2 the two-share-counts trap, §4.3 source ranking (EDGAR first),
  §4.4 `UR-PIT` rules 1–4 (`filed_at` gating), §11.2 OQ-U4/OQ-U5, §12 G-U8/G-U10. It landed
  **while this document was being written**; the reconciliation, including one corrected
  question and one added question, is in
  [§0.4](#04-reconciliation-with-the-universe-methodology)
- Approval gate: [`../governance/approval-gate.md`](../governance/approval-gate.md) (GOV-013)
- Build freeze: [`../governance/build-freeze.md`](../governance/build-freeze.md) (GOV-015)
- Rulings: [#23](https://github.com/tomerYannay/4UR4/issues/23) (authority boundary),
  [#24](https://github.com/tomerYannay/4UR4/issues/24) (universe definition, HD-06
  prerequisites), [#21](https://github.com/tomerYannay/4UR4/issues/21) (out-of-band
  confirmation — **mandatory before any financial authorization**)
