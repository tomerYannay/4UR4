# 4UR4 — Universe Methodology and Point-in-Time Reconstruction (design)

> **Status: DESIGN / SPECIFICATION ONLY under [GOV-015](../../governance/build-freeze.md).**
> The build-freeze is **ON**. Nothing in this document is built, scaffolded, ingested,
> fetched or merged. It specifies rules, contracts and an evidence plan; producing any
> of the artifacts it describes is a separate, assigned action after a human lifts the
> freeze per-scope ([GOV-013](../../governance/approval-gate.md)).
>
> **Authority.** This document is the Architect's design deliverable for
> [HD-18](../../product/human-decisions.md#hd-18--4ur4-computes-its-own-point-in-time-universe--materiality-high)
> (Product Owner, 2026-07-26, [issue #24](https://github.com/tomerYannay/4UR4/issues/24)).
> Under HD-18's delegation clause it **chooses safest reversible initial research
> defaults**. It does **not** decide anything that changes the intended market segment —
> every such item is routed to the Product Owner in [§11](#11-open-questions--decided-defaults-vs-product-owner-gated).
> It selects no provider, commits no spend, and does not modify
> [`roadmap.md`](../../product/roadmap.md), [`human-decisions.md`](../../product/human-decisions.md)
> or [`glossary.md`](../../product/glossary.md).

---

## 0. How to read this document

### 0.1 The naming rule, first, because it is binding

The universe specified here is **4UR4 US Large-Cap 500** (internal id `U4-500`). Under
HD-18 it **must not** be called the S&P 500, and nothing about it may imply endorsement
by or equivalence to S&P Dow Jones Indices. Throughout this document the S&P 500 is
referred to as **"the licensed index"** and appears only as *the thing deliberately not
used* — because its constituent data is licensed separately from, and far more
restrictively than, price data. The primary evidence for that is an executed **S&P
Master Index License Agreement** filed on SEC EDGAR, Exhibit A clause 2: *"the provision
of Index related data (e.g. index levels, index constituents, constituent weights, etc.)
… will be contracted under and governed by the relevant S&P data license agreement (the
'MSA'), which is separate from this Agreement and Order Schedule, and separate fees may
be payable"*
([SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1776030/000119312521050328/d83606dex998c.htm),
retrieved 2026-07-26, via
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md#41-does-a-constituent-list-trigger-an-index-licence)).

### 0.2 Evidence status — and a limit stated up front rather than papered over

This repository's stated defect class is *a restatement of a fact, stored apart from the
fact, and never re-derived*. Every external factual claim below therefore carries one of
three tags:

| Tag | Meaning |
|---|---|
| **VERIFIED (inherited)** | The claim was retrieved, quoted and dated by [`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) or [`data-provider-findings.md`](../../product/data-provider-findings.md). The URL and retrieval date travel with it here. |
| **UNVERIFIED-LEAD** | A design predicate that is probably true and is load-bearing enough to name, but was **not retrieved in this session**. The exact page that would confirm it is given. It may not be relied on until read. |
| **GAP** | Could not be determined at all. Recorded in [§12](#12-gaps-this-design-opens-or-inherits). |

**The limit:** this design session had **no web-retrieval tool** (Read/Write/Edit/Grep/Glob
only). No external page was fetched, no SEC endpoint was touched, no account exists and
no terms were accepted — which is also what GOV-015 and the 2026-07-26 authority boundary
require. Consequently **every claim about SEC EDGAR, XBRL tagging, CUSIP/FIGI licensing
and the licensed index's own published methodology is an UNVERIFIED-LEAD**, and §12 lists
the exact URLs a later, authorised session must read. Nothing here is asserted from prior
knowledge as though it were checked.

The design is deliberately written so that it **survives verification failure**: the
reconstruction is specified against an abstract *share-count observation* with three
dates, not against a particular SEC field name. If the field name is different, the
adapter changes and the methodology does not.

### 0.3 The five principles everything below is derived from

> **P1 — As-of causality.** Membership on date `d` is a function of the information set
> available at `d`, and of nothing else. **Never derive an earlier membership from later
> information.** This is
> [HD-12](../../product/human-decisions.md#hd-12--anchor-selection-is-rolling-and-causal-as-of-time-frozen-at-confirmed-breakout--materiality-high)
> and [`trendline-specification.md`](../../product/trendline-specification.md) §21.8 —
> "a detector, backtest or fixture MUST NOT use any bar at index `≥ t` to establish,
> revise, re-label or withdraw the classification of bar `t`" — restated one layer down.
> HD-12 governs *which bar may judge a bar*. P1 governs *which filing may judge a
> membership*. They are the same rule, and if the engine obeys HD-12 on a universe built
> in violation of P1, the look-ahead is still there, just moved.

> **P2 — Preservation.** Nothing is ever deleted. Delisted securities, removed members,
> superseded share-count observations and superseded price vintages all persist. A
> removal writes an `effective_to`; it never removes a row.

> **P3 — No data-availability rule may correlate with outcome.** A rule of the form
> "drop names whose data is missing/stale/awkward" preferentially deletes distressed
> names, because distress causes delinquent filing, messy corporate actions and thin
> documentation. That is survivorship bias re-entering through the back door — precisely
> the failure
> [`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) §2.1
> names: *"the missing entries are not random"*.

> **P4 — Rules are product surface.** Under HD-18 each eligibility rule is independently
> named, versioned, evidenced and re-derivable. A rule that exists only as code, or only
> in someone's head, is a defect regardless of whether its output is correct.

> **P5 — Corroboration is not the target.** Agreement with the licensed index is
> *evidence that the rules were applied sanely*, never the objective. The objective is
> that the stated rules are correctly and causally applied. See [§7.5](#75-ue-05--comparison-against-the-51-reconstructed-membership-evidence).

---

## 1. The object being specified

### 1.1 Three layers, deliberately separated

Most reconstruction defects come from collapsing these three into one row keyed by
ticker.

| Layer | What it is | Stable key | Changes when |
|---|---|---|---|
| **Issuer** | The company | `issuer_uid` (4UR4-minted); SEC CIK is an *attribute* | Reincorporation, holdco formation, post-bankruptcy succession |
| **Security** | One share class of one issuer | `security_uid` (4UR4-minted); CUSIP/FIGI are *attributes* | Never — a security's identity outlives every identifier it carries |
| **Listing** | A tradeable line: venue + ticker | none — a listing is an interval, not an entity | Ticker change, venue change, delisting, OTC continuation |

**Ranking happens at the issuer layer. Membership is recorded at the security layer.
Prices arrive at the listing layer.** Keeping these apart is what makes dual-class
handling ([§2.3](#23-ur-sec--security-type-and-share-class-the-biggest-silent-fork)) and
the `FRC → FRCB` case ([§5.3](#53-worked-identity-case--first-republic-bank)) expressible
at all.

### 1.2 The rule bundle

HD-18 requires inclusion, liquidity, security-type, domicile and rebalance rules to be
**independently versioned and backtestable**. The methodology is therefore not one
version number but a **manifest of independently versioned rule modules**:

| Rule id | Governs | Initial version | Section |
|---|---|---|---|
| `UR-OPCO` | Operating-company test | `0.1.0` | [§2.1](#21-ur-opco--operating-company) |
| `UR-LIST` | US-listed test; domicile vs listing | `0.1.0` | [§2.2](#22-ur-list--us-listed-the-domicile-vs-listing-decision) |
| `UR-SEC` | Security type and share-class handling | `0.1.0` | [§2.3](#23-ur-sec--security-type-and-share-class-the-biggest-silent-fork) |
| `UR-LIQ` | Liquidity and seasoning screens | `0.1.0` | [§2.4](#24-ur-liq--liquidity-and-seasoning-screens) |
| `UR-RANK` | Ranking basis | `0.1.0` | [§2.5](#25-ur-rank--ranking-basis-and-the-float-question) |
| `UR-REBAL` | Rebalance frequency, dates, buffer | `0.1.0` | [§3](#3-ur-rebal--rebalance-rules) |
| `UR-PIT` | Point-in-time reconstruction and as-of discipline | `0.1.0` | [§4](#4-ur-pit--point-in-time-reconstruction) |
| `UR-ID` | Identity model | `0.1.0` | [§5.1](#51-ur-id--the-identity-model) |
| `UR-CA` | Corporate-action handling | `0.1.0` | [§5.2](#52-ur-ca--corporate-action-handling) |

The bundle id is `universe_methodology_version`, e.g. `u500-0.1.0`. It pins the exact
version of every module plus every named parameter ([§8](#8-versioning-and-backtestability)).

---

## 2. Eligibility rules

### 2.1 `UR-OPCO` — operating company

**Rule (v0.1.0).** An issuer is an **operating company** on date `d` iff, using only
evidence with `filed_at ≤ d`:

1. it is an SEC registrant with a CIK that files periodic reports on **Forms 10-K/10-Q**
   (domestic) or **20-F/40-F** (foreign private issuer); **and**
2. it does **not** file on the registered-investment-company forms (**N-CSR, N-PORT,
   N-1A, N-2, N-CEN**) — this is the test that removes ETFs, closed-end funds, mutual
   funds and unit trusts, and it removes them by *what the entity legally is*, not by a
   name pattern; **and**
3. its self-reported SIC code is not in the **excluded set** `{6726 investment offices,
   6770 blank checks, 6792 oil royalty traders}`; **and**
4. it does not appear in the **exclusion register** ([§2.1.2](#212-the-exclusion-register))
   with an active exclusion on `d`.

**Evidence that determines it:** EDGAR submissions metadata (form types filed, SIC code,
entity classification) plus the filing record itself. **UNVERIFIED-LEAD** — the exact
EDGAR submissions endpoint, its field names, and the SEC fair-access/User-Agent policy
were not retrieved in this session; see [§12](#12-gaps-this-design-opens-or-inherits) G-U2.

**Why form type is the primary test rather than SIC code.** SIC codes are
self-selected by the registrant and are frequently stale or wrong. The *form* an entity
files is a legal consequence of what it is: a registered investment company cannot file
a 10-K instead of an N-CSR. The form test is therefore both more reliable and more
re-derivable, and the SIC test is a secondary net, not the primary one.

#### 2.1.1 The four named exclusions, and how each is actually decided

| Excluded thing | Primary test | Failure mode of the naive test | Residual risk |
|---|---|---|---|
| **ETFs / closed-end funds** | Files N-CSR/N-PORT/N-1A/N-2, not 10-K | Name matching ("Trust", "Fund") both over- and under-fires | Low — the form test is close to dispositive |
| **SPACs / blank-cheque shells** | SIC 6770 **or** an active exclusion-register entry evidenced by the trust-account language in the registration statement | A de-SPAC'd company is a genuine operating company *from the closing date* — a static list is wrong on both sides of that date | Medium — the exclusion must be **dated**, not permanent |
| **Royalty / statutory trusts** | SIC 6792, **or** register entry evidenced by a 10-K filed by a corporate trustee with no operations and no employees | Regex on "Royalty Trust" misses the ones not named that way | Medium — needs human adjudication, see below |
| **Blank-cheque shells (non-SPAC)** | Register entry, evidenced | No mechanical test exists | Medium |

**Practical note that matters more than it looks.** At the top-500 boundary these
exclusions almost never bind: a SPAC or royalty trust is essentially never among the 500
largest US companies by market capitalisation. The exclusions do their work **in the
candidate pool**, where a mis-classified entity distorts *ranks* and can therefore push a
real company across the boundary. So the exclusion rules are cheap to get slightly wrong
and expensive to get badly wrong, which is the right risk profile for a v0.1.0 rule with
a human-reviewable register.

#### 2.1.2 The exclusion register

Exclusions that cannot be decided by form type or SIC code are recorded as **dated,
evidenced rows** — never as a regex and never as a hard-coded list in code (P4):

`(issuer_uid, exclusion_reason, effective_from, effective_to, evidence_url, evidence_retrieved_at, adjudicated_by)`

`effective_to` is what makes a de-SPAC expressible: the entity is excluded until the
business combination closes and eligible after it. The register is itself point-in-time
and is replayed under P1 like everything else.

**REIT treatment (sub-decision, default INCLUDE).** Equity and mortgage REITs file 10-Ks,
are not registered investment companies, and are operating businesses. They are **in** at
v0.1.0. This is flagged for Product Owner *awareness* in
[§11](#11-open-questions--decided-defaults-vs-product-owner-gated) because excluding a
whole sector is a segment change; including them is the status quo of any broad US
large-cap universe and is the lower-surprise default.

---

### 2.2 `UR-LIST` — "US-listed": the domicile-vs-listing decision

Both answers are defensible. HD-18 requires that it be **decided, versioned and
re-derivable**, which is the actual requirement.

**Decision (v0.1.0): listing-based, restricted to primary listings. Domicile of
incorporation is recorded but is not dispositive.**

A security is US-listed on `d` iff on `d`:

1. it trades on a **US national securities exchange** (NYSE, NYSE American, Nasdaq,
   Cboe BZX) — OTC, Pink, Expert Market and grey-market quotation do **not** qualify;
   **and**
2. it is **common stock or ordinary shares** (see [§2.3](#23-ur-sec--security-type-and-share-class-the-biggest-silent-fork)); **and**
3. the US listing is the security's **primary** listing — i.e. the security is **not** a
   depositary receipt (ADR/ADS/GDR) and **not** a secondary or cross-listing of a
   security whose principal market is a non-US exchange.

**Consequence, stated plainly.** Foreign-*domiciled* companies whose ordinary shares are
primarily listed in the US are **IN** (the Ireland-, Switzerland- and Bermuda-domiciled
large caps that trade as ordinary shares on NYSE/Nasdaq). Depositary receipts of
companies whose principal market is Taipei, Amsterdam, London, Tokyo or Hong Kong are
**OUT**. *(These characterisations describe the rule's shape; the classification of any
individual security must be derived from data, never from a list in a design document.)*

**Why this default, in order of weight:**

1. **It is product-specific, not borrowed.** 4UR4's core object is an ATH-anchored
   descending trendline fitted to `ln(H[t])` — the **bar high**
   ([`trendline-specification.md`](../../product/trendline-specification.md) §3–§4). An
   ADR's USD price series is the underlying equity's local-currency price *multiplied by
   an FX rate*. A multi-year descending line on an ADR can therefore be an FX artefact
   rather than an equity structure, and the product cannot tell the difference. That is
   not a philosophical objection; it is a wrong-object risk of exactly the kind
   [`data-provider-findings.md`](../../product/data-provider-findings.md) §2.1 describes
   for truncated history.
2. **ADR ratio changes behave like unadjusted splits.** They are a corporate-action class
   that the surveyed providers do not document (**G-08** in
   [`data-provider-findings.md`](../../product/data-provider-findings.md#10-open-gaps-and-things-i-could-not-verify)
   already records that spin-off and merger events are undocumented for both recommended
   providers). Admitting ADRs imports an un-evidenced adjustment dependency.
3. **It is mechanically derivable.** Listing venue and security type come from an
   exchange-published listed-securities file. "Principal place of business", which a
   domicile-based rule would require, is a judgement call — exactly the kind of
   discretion this methodology exists to avoid.
4. **It is reversible.** Admitting ADRs is `UR-LIST` v0.2.0 plus a re-run, not a rewrite.

**Rejected alternative — domicile-based** (include only US-incorporated issuers): would
exclude several of the largest US-listed operating companies on a technicality of where
a holding company is registered, produces a universe that does not match what a US user
can actually trade, and requires the judgement call in point 3.

**⚠ Near the Product-Owner line.** Excluding ADRs *narrows* the set of companies the
product will ever show a user. That is arguably a change to the intended market segment,
which HD-18 reserves to the Product Owner. It is taken here as a **reversible research
default** and is escalated explicitly as **OQ-U1** in [§11](#11-open-questions--decided-defaults-vs-product-owner-gated).

---

### 2.3 `UR-SEC` — security type and share class (the biggest silent fork)

**Admissible security types (v0.1.0):** common stock / ordinary shares only.
**Excluded:** preferred stock, warrants, rights, units, when-issued lines, convertible
instruments, and **tracking stocks** (a tracking stock's economics do not correspond to
the issuer's consolidated equity, which breaks the proxy assumption in step 3 below).

The dual-class question has **two axes**, and conflating them is the classic error.

#### Axis 1 — ranking: aggregate the classes, or rank them separately?

**Decision: rank at the issuer level, summing the market capitalisation of *all* share
classes — listed and unlisted.**

Why. A company's size is not partitioned by its capital structure. Ranking classes
separately systematically under-ranks every dual-class company by the size of its
smaller class. For a company split, say, 60/40 across two classes and sitting near rank
500, separate ranking pushes both lines out of the universe while an aggregating rule
keeps the company in — a large, silent, and entirely capital-structure-driven distortion.
**This single choice moves names in and out of a top-500 ranking more than any other rule
in this document.**

Counting *unlisted* classes matters and is achievable: the cover page of a periodic
report states the outstanding count **for each class separately**
(**UNVERIFIED-LEAD**, [§12](#12-gaps-this-design-opens-or-inherits) G-U3). Where a class
has no market price, the price of the designated primary class is used as a proxy.
**Stated assumption and its error direction:** super-voting classes are normally
economically equivalent to the listed class, so the proxy error is small; where a class
is *not* economically equivalent — the tracking-stock case — the assumption fails, which
is why tracking stocks are excluded outright rather than proxied.

#### Axis 2 — membership: all classes tradeable, or one line per company?

**Decision: one line per issuer — the *designated primary class*.**

The designated primary class is the listed common class with the greatest trailing
`MDDV_63` ([§2.4](#24-ur-liq--liquidity-and-seasoning-screens)) as of the reference date.
Deterministic tie-break: greater shares outstanding, then lower CIK, then lexicographic
ticker. Every other listed class is retained in the security register with
`class_role = SECONDARY` — retained, not discarded, so a future `UR-SEC` v0.2.0 can admit
all classes without re-deriving anything.

Why one line: 4UR4 emits one signal per company. Two near-identical descending-trendline
signals on two classes of one company are not two pieces of evidence — they are one
piece, double-counted. That double-count would propagate directly into the breadth and
regime statistics contemplated by
[`market-sentiment-specification.md`](../../product/market-sentiment-specification.md)
and into the glossary's *breakout breadth* feature, where "count of concurrent confirmed
breakouts across the universe" would be inflated by exactly the number of dual-class
members.

**Intended, disclosed divergence.** This makes 4UR4 US Large-Cap 500 exactly **500
companies and 500 securities**. The licensed index deliberately carries more stocks than
companies — its own public description says it *"comprises 503 common stocks which are
issued by 500 large-cap companies"* (Wikipedia, retrieved 2026-07-26, **VERIFIED
(inherited)**). Ours is a different construction and must not be presented as the same
one.

---

### 2.4 `UR-LIQ` — liquidity and seasoning screens

**Rule (v0.1.0).** A security is liquidity-eligible at reference date `r` iff, computed
from bars with `as_of ≤ r`:

| Screen | Parameter | Value at v0.1.0 | Measured how |
|---|---|---|---|
| Dollar liquidity | `mddv_min_usd` | 25,000,000 | **Median** of `close × volume` over the trailing `liquidity_window_bars` |
| Window | `liquidity_window_bars` | 63 trading days (≈ one quarter) | Trading days, not calendar days |
| Data completeness | `min_bar_coverage` | 0.90 | Fraction of scheduled session days in the window that have a bar |
| Seasoning | `seasoning_bars` | 63 trading days | Bars since first regular-way trade on a qualifying venue |

**Median, not mean** — a mean is dominated by one rebalance-day or earnings-day volume
spike. **Dollar volume, not share volume** — share counts are not comparable across price
levels.

**Why the threshold is deliberately low.** At the top-500 boundary this screen is almost
never binding: a company among the 500 largest in the US trades far more than $25m/day in
normal conditions. That is the point. **A liquidity screen that binds frequently is doing
hidden selection work**, i.e. it has become a second, undeclared ranking rule. Its real
job here is defensive: to catch a name whose *rank* is still high but which has become
untradeable — halted, in receivership, or moved off-exchange. That is the First Republic
class of event, and it is the case the screen exists for.

**⚠ P3 interaction, and the resulting design constraint.** A liquidity screen removes
distressed names, and distress correlates with the outcome being measured. The screen is
therefore permitted to trigger **removal** only in combination with a *structural*
event (halt, delisting, venue loss) or a sustained breach, and every liquidity-driven
removal is recorded with reason code `INELIGIBLE_LIQUIDITY` and is separately reportable,
so the count of such removals can be audited for outcome correlation
(see [§7.6](#76-the-remaining-checks) UE-14).

**Split-consistency of dollar volume.** `close × volume` is invariant to a split only if
price and volume are adjusted on the same basis. This is a real hazard: EODHD returns raw
OHLC but split-adjusted volume (**VERIFIED (inherited)**,
[`data-provider-findings.md`](../../product/data-provider-findings.md) §2.2), so a naive
`close × volume` on that feed is wrong by the cumulative split factor. Hence **UD-05**
([§9](#9-interface-requirements-for-data-extending-di-01di-12)).

**Seasoning, and why it costs 4UR4 nothing.** A new listing waits 63 trading days. This
is usually framed as an index-stability rule; here it has a stronger, product-specific
justification: **the ATH-anchored trendline is undefined for a security with no
meaningful price history.** The engine's formation gates cannot produce a line for a
three-month-old security anyway. Seasoning therefore removes names the engine could not
have scanned — a rare case of an eligibility rule with no cost.

**Consequence for spin-offs, stated:** newly spun entities such as the 2026 spin-offs
recorded in
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) §5.2
(**VERIFIED (inherited)**) will not enter the universe for at least one quarter, and in
practice until the next scheduled rebalance after seasoning. This is intended, and for
this product it is free, per the previous paragraph.

---

### 2.5 `UR-RANK` — ranking basis, and the float question

**Decision (v0.1.0): full (total) market capitalisation, summed across all share classes
of the issuer. Not float-adjusted.**

```
market_cap(issuer i, date d, as_of a)
  = Σ over classes c of i:  raw_close(primary_listing(c), d, as_of=a)
                            × shares_outstanding(i, c, as_of=a)
```

Four properties of that formula are load-bearing.

**(a) It uses the RAW, unadjusted close — not the split-adjusted series.** A
split-adjusted price series restates pre-split prices onto a later share basis.
Multiplying such a price by the *contemporaneous* (pre-split) share count mixes bases and
misstates market capitalisation by the cumulative split factor. The universe layer
therefore needs the raw series, while the engine needs the split-adjusted series
([HD-01](../../product/human-decisions.md)). This is a **new and concrete use of DI-02**
("both series obtainable"), which existed for adjustment auditing and turns out to be a
correctness requirement for the universe as well.

**(b) The cumulative adjustment factor is itself a point-in-time object.** A split that
occurs after `as_of` must not be applied. `as_of` therefore propagates into the
adjustment factor, not merely into the bar.

**(c) It requires point-in-time shares outstanding.** That is [§4](#4-ur-pit--point-in-time-reconstruction),
and it is the hard part.

**(d) It is checkable.** `raw_close × raw_shares` must equal `adjusted_close ×
adjusted_shares` to tolerance — an invariant that catches the double-counted split
directly (UE-11, [§7.6](#76-the-remaining-checks)).

#### Why not float-adjusted, and what that costs

Float adjustment weights by the shares actually available to public investors. It is the
better *weighting* basis. It is rejected at v0.1.0 for one decisive reason and two
supporting ones:

1. **Decisive: float is a further dataset dependency, and a harder one than shares
   outstanding.** There is no filing that states "free float as of date `d`". Float must
   be *estimated* by subtracting affiliate, insider, strategic and government holdings —
   reconstructed from Forms 3/4/5, Schedules 13D/13G and proxy beneficial-ownership
   tables, each with its own filing lag, its own thresholds, and no clean point-in-time
   series. **Float would multiply the reconstruction problem of §4 rather than add to
   it.** (**UNVERIFIED-LEAD** on the specific forms; the structural point — that no
   single filed field gives float as of a date — is the design predicate, G-U4.)
2. 4UR4 uses the universe as a **scan set, not as index weights**. Float changes how much
   of a company you could buy; it does not change whether the company is one of the 500
   largest. For a membership decision it only shifts the boundary.
3. Full market cap keeps the entire methodology derivable from two inputs — price and
   shares outstanding — both of which are obtainable.

**The honest cost, stated rather than buried.** Full-cap ranking systematically favours
companies with small public float: controlled companies, founder-supermajority dual-class
names, recent IPOs with small floats, and companies with large strategic or state
holdings. A float-adjusted ranking would place several of them lower. **This is a named,
intended divergence** from float-adjusted practice, and **its magnitude is unquantified**
— recorded as **G-U5**, measurable once any float estimate exists, and not guessed at
here.

---

## 3. `UR-REBAL` — rebalance rules

### 3.1 Scheduled rebalances

| Parameter | Value at v0.1.0 | Meaning |
|---|---|---|
| `rebalance_frequency` | quarterly | Reference dates in March, June, September, December |
| `reference_date r` | last trading day of the quarter | The information cut-off: only data with `as_of ≤ r` may be used |
| `rebalance_lag_days` | 6 trading days | Membership changes take effect at the **open** of the 6th trading day after `r` |
| `effective_date e` | `r + 6` trading days | `effective_from` is inclusive at the open; `effective_to` is exclusive |

**Why a nonzero lag exists.** Not for data latency — the reconstruction already uses only
information filed by `r`, so no waiting is needed for correctness. The lag exists so that
(i) the decision is *recorded and auditable before it binds*, mirroring the real-world
announce-then-effect pattern visible in the per-event announcements cited in
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md#51-e1--past-date-membership-snapshot-vs-today-worked-comparison)
(**VERIFIED (inherited)**), and (ii) **no bar can ever be classified under a membership
decision that consumed that same bar's data.** Six is a stated, named, versioned
parameter — not a magic constant. This is the posture
[HD-13](../../product/human-decisions.md) established for `eps_break`: named, versioned,
backtestable, unlocked.

### 3.2 The buffer

**Decision: buffered candidacy with reconciliation to exactly 500.**

| Parameter | Value at v0.1.0 | Rule |
|---|---|---|
| `buffer_in_rank` | 450 | A non-member is **added** only if its issuer rank at `r` is ≤ 450 |
| `buffer_out_rank` | 550 | An incumbent is **removed** only if its issuer rank at `r` is > 550 |
| reconciliation | exact 500 | After the buffer, if the set exceeds 500 remove worst-ranked incumbents; if short, add best-ranked eligible non-members until 500 |
| tie-break | deterministic | Greater `MDDV_63`, then lower CIK |

**Why a buffer at all.** Near rank 500 the market capitalisations of adjacent companies
differ by a fraction of a percent, while daily price moves of one to two percent are
ordinary. A hard rank-500 cutoff therefore reorders the boundary **from noise alone**,
generating additions and removals that carry no information and that a backtest would
faithfully trade. *(The size of the boundary gap is asserted here as an expectation, not
a measurement — UE-06 in [§7.6](#76-the-remaining-checks) exists precisely
to replace this expectation with a number, and G-U6 records it as open until then.)*

**What the buffer costs, stated because it is easy to miss.** A buffer introduces **path
dependence**: membership at `r` now depends on membership at `r − 1 quarter`. The universe
stops being a pure function of date-`r` data and becomes a **forward replay from a seed
state**. Three consequences follow, and all three must be honoured:

1. **Reconstruction must be a forward replay.** Membership on any date is obtained by
   replaying every rebalance from the seed forward. Evaluating a single historical date
   in isolation is **not** a valid shortcut and will give a different answer.
2. **The seed is itself a methodology choice.** The first rebalance in the reconstruction
   window has no prior state, so it uses a **hard rank-500 cutoff with no buffer**,
   recorded with reason code `SEED`.
3. **The seed leaves an artefact.** Membership near the start of the window is biased by
   the arbitrary seed. The first **four** rebalances are flagged `SEED_INFLUENCED` in the
   artifact, and any backtest whose window overlaps them must say so (UE-12).

### 3.3 Intra-quarter (event-driven) changes

**Mandatory removals — effective immediately, no waiting for a rebalance:**

| Trigger | Effective at | Reason code |
|---|---|---|
| Delisting from a qualifying exchange | Close of the last regular-way trading day | `DELISTED` |
| Merger/acquisition completion (security ceases to exist) | Close of the last regular-way trading day | `MERGED` |
| Receivership, conservatorship or seizure by a regulator | Close of the last regular-way trading day | `RECEIVERSHIP` |
| Ceases to satisfy `UR-OPCO` (e.g. converts to a fund) | Effective date of the change | `INELIGIBLE_OPCO` |
| Ceases to satisfy `UR-LIST` (venue loss, moves to OTC) | Effective date of the change | `INELIGIBLE_LISTING` |
| Sustained liquidity breach with a structural cause | Effective date, evidenced | `INELIGIBLE_LIQUIDITY` |

**Mandatory additions: none.** When a member is removed intra-quarter the universe **runs
at 499** until the next scheduled rebalance.

Why running short beats back-filling: back-filling requires computing a fresh full
ranking on an arbitrary mid-quarter date, which adds an off-cycle ranking surface, extra
state, and extra opportunity for as-of violations — in exchange for a name that would
have entered at the next quarterly rebalance anyway. 4UR4 is a **scanner, not a
fully-invested portfolio**, so the exact cardinality between rebalances is not
economically load-bearing. Running short is also *observable*: the count is in the
artifact and a dashboard can show it.

**Spin-offs are additions, and they are also declined.** The 2026 spin-off events in
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) §5.2 show
that spin-offs create new large members from existing ones and that **membership events
are not add/remove pairs** — four of thirteen 2026 events were unpaired (**VERIFIED
(inherited)**). A model that assumes pairs drifts away from 500 within a year, so this
design never assumes pairs. Spun entities are handled by the ordinary seasoning rule
([§2.4](#24-ur-liq--liquidity-and-seasoning-screens)) and, as argued there, their absence
costs this product nothing because the engine cannot fit an ATH-anchored line to them yet.

### 3.4 The membership record

Every membership row carries, at minimum:

`(security_uid, issuer_uid, effective_from, effective_to, decided_at, reference_date, rank_at_reference, reason_code, universe_methodology_version, evidence_ref)`

`decided_at` is the **information vintage** of the decision and is distinct from
`effective_from`. Their separation is what makes P1 auditable rather than merely asserted.
Reason codes are a closed enumeration — the same discipline
[`trendline-specification.md`](../../product/trendline-specification.md) applies to
detector events.

---

## 4. `UR-PIT` — point-in-time reconstruction

**This is the hard part, and the rest of the methodology is downstream of it.**

### 4.1 The dependency chain, and where it breaks

```
point-in-time membership
   ← point-in-time rank
      ← point-in-time market cap
         ← point-in-time RAW price        (available: R1 research)
         ← point-in-time SHARES OUTSTANDING  (NOT EVALUATED — no provider assessed)
```

**Stated without softening:**
[`data-provider-research.md`](../../product/data-provider-research.md) poses R1–R8 and
[`data-provider-findings.md`](../../product/data-provider-findings.md) answers R1, R2, R3,
R6, R7, R8, with R4/R5 answered in
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md). **None of
them evaluates shares outstanding, fundamentals, or market capitalisation, because the
question did not exist when that research ran** — the universe ruling (HD-18) is dated
2026-07-26 and the research questions predate it. There is therefore **no evaluated
provider for the single input the whole universe depends on.** That is a gap, and the
correct response is to open it as a research question — proposed as **R9** for the
Product Steward — not to quietly assume a vendor.

### 4.2 What data is needed

Per issuer, per share class, an ordered set of **share-count observations**:

| Field | Meaning | Why it is separate |
|---|---|---|
| `value` | Shares outstanding of that class | — |
| `value_as_of` | The date the count is **true** | Cover-page counts are as of a date near filing |
| `filed_at` | Acceptance timestamp — when the fact became **knowable** | This, not `value_as_of`, is what P1 gates on |
| `period_end` | The fiscal period the report covers | **Not** the same as `value_as_of` — see below |
| `class_id` | Which share class | Dual-class ranking is unresolvable without it |
| `source_ref` | Accession number / URL | Evidence, per HD-18 requirement 4 |
| `is_amendment` | Whether it supersedes an earlier observation | Amendments create new observations, never rewrites |

> **A defect that will otherwise be silent.** `period_end` and `value_as_of` are
> different dates. The **cover page** count is as of a date shortly before filing; the
> **financial statements'** count is as of the period end. They are different numbers.
> Mixing them produces market caps that are wrong by a quarter's worth of buybacks and
> issuance, consistently, and with no error to observe. Any adapter must state which of
> the two it returns.

**Frequency required:** quarterly per issuer is sufficient, because membership is only
evaluated at rebalance reference dates and at mandatory event dates — not daily.

**Volume, as a scoping fact:** the candidate pool is the full set of US-listed operating
companies at each date, not just the eventual members. For scale, the surveyed vendors
describe "over 20,000 US companies" active and delisted (Sharadar) and "11,000+ US
tickers" (EODHD), and Norgate alone lists **25,222 delisted securities from 1950 to
Sep 2022** (all **VERIFIED (inherited)**,
[`data-provider-findings.md`](../../product/data-provider-findings.md) and
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) §3.1). The
reconstruction is therefore thousands of issuers × four filings per year × the window
length.

**No causal prefilter at v0.1.0.** It is tempting to compute caps only for issuers that
"could plausibly" be top-500. Every such prefilter is a silent selection rule and several
plausible ones are non-causal. If throughput later forces one, it becomes a versioned
rule with its own evidence, not an optimisation.

### 4.3 Where the data comes from

| Rank | Source | Coverage | Cost | Status |
|---|---|---|---|---|
| 1 | **SEC EDGAR primary filings** (10-K/10-Q cover page, per class) | All SEC registrants, permanently retained | Free | **UNVERIFIED-LEAD** — G-U3 |
| 2 | **SEC XBRL structured data** — company-concept / frames APIs and the quarterly Financial Statement Data Sets | Registrants from the XBRL phase-in onward | Free | **UNVERIFIED-LEAD** — G-U3 |
| 3 | Vendor fundamentals (Sharadar, EODHD, FMP and others) | Vendor-dependent | Priced; HUMAN-GATED under HD-06/HD-07 | **GAP** — none evaluated |
| 4 | Fund holdings (N-PORT) as **corroboration only** | Quarterly | Free | Public monthly N-PORT delayed to **2027-11-17** / **2028-05-18** — **VERIFIED (inherited)** |

**The decisive advantage of the SEC path, and it is not cost.** EDGAR retains the filings
of companies that failed. A reconstruction built on the primary filing record is
**survivorship-complete by construction** — the share counts of a company that went to
zero in 2023 are still there, filed, dated and unamended. Every vendor fundamentals
dataset must be *proven* to retain delinquent and delisted issuers; EDGAR does not need
to be. This is the same structural argument
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) §3.2 makes
about price feeds that silently drop delisted names, applied to the share-count input.

**The bound nobody should discover late.** XBRL tagging phased in over several years and
does not extend back indefinitely; before the phase-in, cover-page counts exist only as
text in a filing document and require extraction. **This bounds how far back a rigorous
free reconstruction reaches.** The exact phase-in dates are **UNVERIFIED-LEAD** (G-U3),
but the shape of the constraint is certain and it is decision-relevant: *if the Product
Owner wants a backtest window reaching the 1990s, the free path does not reach it*, and
the choice becomes a text-extraction project or a paid dataset (HD-06/HD-07 territory,
human-gated). Escalated as **OQ-U5** in [§11](#11-open-questions--decided-defaults-vs-product-owner-gated).

**The restated-fundamentals trap.** Many fundamentals datasets are *restated*: they show
today's best value for a historical period rather than the value knowable at the time.
Such a dataset silently violates P1 no matter how carefully the rest of the pipeline is
written. Any R9 evaluation must therefore ask, in writing, whether the dataset is
**as-reported with filing timestamps** or **restated**, and must reject a vendor that
cannot answer. This is exactly the *artifact distinction* that
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) §2.1 shows
decides everything for constituent data — the same distinction, applied to fundamentals.

### 4.4 The lag rule — the governing invariant

> **UR-PIT rule 1 (binding).** For reference date `r`, the share-count observation used
> for issuer `i`, class `c` is the observation with the **greatest `value_as_of` among
> those with `filed_at ≤ r`**. If no such observation exists, the issuer is ineligible on
> `r` with reason code `NO_SHARE_DATA`. It is **never** back-filled from a later filing.

> **UR-PIT rule 2 (binding).** Between observations, the last filed value is **carried
> forward as a step function**. **Interpolation is a banned technique** — interpolating
> between a known past value and a future value is look-ahead by construction, and it is
> the single most natural mistake in this entire design. Causal extrapolation is likewise
> not a default.

> **UR-PIT rule 3 (binding).** An amendment (e.g. a 10-K/A) creates a **new observation
> with its own `filed_at`**. It changes membership only from its own `filed_at` forward.
> Membership already recorded stands. This is the DI-05 vintage discipline applied to
> filings.

> **UR-PIT rule 4 (binding).** Prices are read with `as_of = r`, never `as_of = today`.
> Daily bars are restated as late trades arrive (**VERIFIED (inherited)**,
> [`data-provider-findings.md`](../../product/data-provider-findings.md) §2.4), so a
> market cap computed from today's vintage of a 2019 bar is not the market cap that was
> knowable in 2019. DI-04 already makes `as_of` mandatory; the universe is one of its
> most sensitive consumers.

**Staleness, and the P3 trap it hides.** If the newest observation with `filed_at ≤ r`
has a `value_as_of` older than `max_staleness_days` (v0.1.0: **270 days**, i.e. roughly
two missed reporting periods), the issuer is flagged `STALE_SHARE_DATA` and is
**retained, not removed**.

This is deliberate and it is P3 in action. **Delinquent filing correlates with distress.**
A rule that drops names with stale data would preferentially delete the companies that
were about to fail — which is the exact non-random deletion that produces the bias this
entire methodology exists to remove. The flag exists so the condition is *visible and
auditable*; it must never become a filter.

### 4.5 How large is the lag error, honestly

The filing lag means a market cap can be computed from a share count up to roughly a
quarter old. Two properties matter, and they point in different directions:

- **In the ordinary case the error is bounded and symmetric.** Buybacks and
  share-based-compensation issuance move share counts by low single-digit percentages a
  year for large caps. It does not systematically favour winners or losers. Against a
  rank-boundary gap of well under one percent, however, it is **not negligible at the
  boundary** — it can flip individual members. The buffer ([§3.2](#32-the-buffer))
  absorbs some of this, which is a second, independent argument for having one.
- **Around stock-financed M&A and large secondary offerings the error is directional.**
  An acquirer that issues shares to fund a purchase has a materially larger count that is
  not filed until its next periodic report. The reconstruction therefore **understates**
  that acquirer's market cap for up to a quarter, and it does so precisely for companies
  that just got bigger. **This is the largest single systematic error of the
  filing-lag approach** and it is named here rather than discovered later. Mitigation
  deferred to `UR-PIT` v0.2.0: an event-driven share-count override sourced from the
  merger 8-K. At v0.1.0 the condition is flagged `SHARE_COUNT_STALE_MA`, not corrected.

**This is measurable, and measuring it is cheap.** UE-07
([§7.6](#76-the-remaining-checks)) recomputes membership at `r` using
information available at `r` versus information available at `r + 120` days and reports
the count of boundary flips attributable to the lag. That converts an assertion into a
number using only data the reconstruction already holds.

---

## 5. `UR-ID` and `UR-CA` — identity and corporate actions

### 5.1 `UR-ID` — the identity model

**Decision: the canonical key is a 4UR4-minted, immutable `security_uid` (and
`issuer_uid`). Every external identifier — ticker, CIK, CUSIP, FIGI, exchange symbol —
is an *attribute with a validity interval*, never a key.**

`(security_uid, identifier_type, value, valid_from, valid_to, source_ref)`

Resolution is always dated: `resolve(identifier_type, value, on_date) -> security_uid`.
**A bare ticker map with no date is a defect**, not a convenience.

| Identifier | Role | Why it cannot be the key |
|---|---|---|
| **Ticker** | Attribute, interval-scoped | Changes (`FB → META`, `FRC → FRCB`) **and is reused** by unrelated companies after a delisting |
| **CIK** | Strong issuer attribute | Two independent free reconstructions converged on CIK over ticker (**VERIFIED (inherited)**), but a new holdco or post-bankruptcy successor gets a **new CIK**, and non-registrants have none |
| **CUSIP** | Security attribute | Changes on reincorporation and ratio changes; **and its redistribution is licensed** — an unresearched exposure for a redistribution-bearing product (**G-U7**) |
| **FIGI** | Security attribute | Openly licensed and referenced by at least one surveyed provider's ticker-events endpoint (**VERIFIED (inherited)**); licence terms not read here (**G-U7**) |

Issuer continuity across a CIK change is recorded as an evidenced, dated edge
`SUCCEEDED_BY(issuer_uid_old, issuer_uid_new, effective_date, evidence_ref)` — a fact with
a citation, not an inference.

**Why this matters more than it sounds.** The repository's own worked comparison found
that **two of eighteen apparent removals were renames of companies that never left** —
`AVGO` (Avago → Broadcom) and `ABC` (AmerisourceBergen → Cencora) — and that a naive diff
"would have deleted Broadcom and Cencora from the historical universe" (**VERIFIED
(inherited)**,
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md#51-e1--past-date-membership-snapshot-vs-today-worked-comparison)).
Broadcom is one of the largest companies in the set. A universe keyed on ticker gets this
wrong, confidently, at the top of the ranking.

### 5.2 `UR-CA` — corporate-action handling

The universe layer and the engine layer need **different treatments of the same event**.
That is not duplication; it is why the two layers are separate.

| Event | Price series | Shares outstanding | Identity | Membership | Evidence |
|---|---|---|---|---|---|
| **Forward / reverse split** | Adjust engine series; universe uses raw × contemporaneous count | New count filed at next report; the split ratio is known at the execution date | Unchanged `security_uid`; ticker may change on a reverse split | No effect | Splits endpoint; one surveyed provider records splits back to **1978-10-25** (**VERIFIED (inherited)**) |
| **Spin-off** | **Unadjusted price drop in the parent** — the engine must treat it or a false ATH structure appears; the universe needs no adjustment because the parent's cap genuinely fell | Parent's count usually unchanged; child has a new count | New `security_uid` for the child; `SPUN_FROM` edge | Parent unaffected; child waits for seasoning ([§3.3](#33-intra-quarter-event-driven-changes)) | **GAP** for both recommended providers (**G-08**, inherited) |
| **Merger / acquisition** | Target series terminates | **Acquirer's count jumps and is not filed for up to a quarter** ([§4.5](#45-how-large-is-the-lag-error-honestly)) | Target `security_uid` closes; acquirer unchanged | Target removed `MERGED` at last regular-way close | Provider corporate-action feeds; **GAP** on event coverage |
| **Ticker change** | Continuous | Unchanged | **Same `security_uid`**, new ticker interval | No effect | One surveyed provider exposes a `ticker_change` event type (**VERIFIED (inherited)**); another's coverage is a **GAP** |
| **Delisting** | Series ends on the exchange; may continue OTC | Continues to be filed if the registrant keeps reporting | Same `security_uid`; new listing interval on the new venue | Removed `DELISTED`; **row retained forever** (P2) | Exchange notice / Form 25 |
| **Relisting / OTC continuation** | New listing interval, different venue | Unchanged | **Same `security_uid`** | Not a member (fails `UR-LIST`), but the price series is retained | Quotation records |
| **Redomiciliation** | Continuous | Unchanged | Same security; **CUSIP and CIK may both change** | No effect under `UR-LIST` v0.1.0 (listing-based) | Filing record |
| **Share-class collapse** | One class's series ends | Counts merge into the surviving class | Secondary `security_uid` closes | Primary-class designation re-evaluated | Filing record |

**Delisting returns — flagged, not decided here.** Shumway (1997) documented that
*"correct delisting returns are not available for most of the stocks that have been
delisted for negative reasons"* and that *"the omitted delisting returns are large"*
(**VERIFIED (inherited)**,
[PDF](https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf), retrieved
2026-07-26). What a backtest books for a position held through a delisting is an open
specification gap the repository has **already logged**
([`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md#9-open-items-this-research-surfaces),
item 1). This document deliberately does **not** decide it. The universe layer's
obligation is narrower and is discharged here: record the removal, its date, its reason
code, and a `terminal_disposition` field for the engine to consume — leaving the semantics
of that field to the owner of the backtest specification.

### 5.3 Worked identity case — First Republic Bank

The case that makes the abstraction concrete. All rows **VERIFIED (inherited)** from
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md#53-e3--documented-delisted-name-history-example-first-republic-bank)
(retrieved 2026-07-26) unless marked.

| Date | Event | 4UR4 representation |
|---|---|---|
| 2019-01-02 | Entered the licensed index (announced 2018-12-27) | Not a 4UR4 event — 4UR4 membership is determined by its own rules, at its own reference dates |
| 2023-05-01 | FDIC receivership; closed and sold to JPMorgan Chase | `RECEIVERSHIP` — mandatory removal trigger |
| 2023-05-02 | NYSE announced delisting; trading suspended (exact Form 25 date **not verified** in the source) | Listing interval `(NYSE, FRC)` closes |
| 2023-05-04 | Removed from the licensed index prior to the open | Corroboration only, not a 4UR4 trigger |
| 2023 → present | Quoted OTC under a **different ticker, `FRCB`** | **Same `security_uid`**; new listing interval `(OTC, FRCB)`; not a member (fails `UR-LIST`); price series retained under P2 |

**What this case proves about the design:**

1. **The join key is not stable, and that is the whole difficulty.** A ticker-keyed
   pipeline querying `FRC` after 2023 finds nothing — or, worse, finds a reassigned
   instrument. Only `security_uid` with dated identifier intervals survives this.
2. **The company was a genuine large-cap for years and then went to approximately zero.**
   A universe reconstructed from today's listings never sees it: not the entry, not the
   run-up, not the collapse. It is the archetype of what P2 preserves.
3. **The evidence is free and authoritative but per-event.** Constructing this record cost
   nothing but time; doing it for every removal across a multi-year window is the labour
   that a paid dataset replaces — which is a cost argument, not a correctness argument,
   and belongs to HD-06/HD-07, not here.

---

## 6. What this is **not** — stated plainly

### 6.1 It is not, and cannot be, the licensed index

4UR4 US Large-Cap 500 is a **self-computed, mechanical, versioned universe**. It is not
the S&P 500; it is not derived from S&P Dow Jones Indices constituent data; it is neither
endorsed by nor equivalent to any S&P Dow Jones Indices index.

HD-18 states the reason directly: *"A mechanical rule cannot reproduce S&P 500 membership:
the index committee applies discretion — profitability screens, float, sector balance,
judgement."* This document does not attempt to reproduce it and **should not**: the
independence is the point of HD-18, not a shortfall against it.

**Sourcing discipline on this claim.** The repository has *not* read the licensed index's
published methodology — `spglobal.com` returned HTTP 403 to every automated fetch during
the survivorship research (**G5**, inherited), and no page was fetched in this session at
all. What *is* verified from the repository's own evidence is narrower and sufficient:
membership changes are **announced per-event by the index provider**, with stated reasons
such as "Market capitalization change" and acquisition-driven replacements, at dates the
provider chooses (**VERIFIED (inherited)**, thirteen enumerated 2026 events plus the
corroborating provider press release). That is the signature of a **discretionary,
announced process**, not of a published mechanical rule a third party could replay. Any
further characterisation of the committee's criteria is **UNVERIFIED-LEAD** and is not
asserted here.

### 6.2 The named, intended divergences

Each is a *choice*, not an error, and each is traceable to a rule version.

| Divergence | Rule | Direction of effect |
|---|---|---|
| One security per company (500 securities, not ~503) | `UR-SEC` | Removes duplicate signals; changes breadth statistics |
| Full market cap, not float-adjusted | `UR-RANK` | Favours controlled and small-float companies |
| ADRs and non-US-primary listings excluded | `UR-LIST` | Narrows the segment; removes FX-confounded series |
| No profitability screen | (none — deliberately absent) | Admits large loss-making companies the committee might not |
| No sector-balance judgement | (none — deliberately absent) | Sector weights float freely with market cap |
| 63-day seasoning; no intra-quarter additions | `UR-LIQ`, `UR-REBAL` | New listings and spin-offs enter late |
| Quarterly rebalance with a rank buffer | `UR-REBAL` | Lower turnover; path-dependent membership |
| Share counts lag by up to a quarter | `UR-PIT` | Understates recent acquirers ([§4.5](#45-how-large-is-the-lag-error-honestly)) |

### 6.3 Backtest results are not comparable — and where that must be disclosed

**Binding consequence.** A backtest run on 4UR4 US Large-Cap 500 measures a strategy on a
different universe from any published S&P 500 strategy result. The two are **not
comparable**, and a reader who assumes they are will draw a false conclusion.

Disclosure is required at **five** surfaces. Note that four of them are *artifacts*, not
prose — this repository's dominant defect class is a fact restated apart from the fact, so
the disclosure is attached to the data, not to a document about the data.

| # | Surface | Mechanism |
|---|---|---|
| D-1 | Every backtest / calibration report artifact | Required field `universe_methodology_version` **and** the verbatim statement below. Missing ⇒ CI failure (UE-13) |
| D-2 | Every evidence artifact carrying universe-derived results | Same required fields |
| D-3 | Every scan-run record | `universe_methodology_version` + `universe_snapshot_id` alongside `spec_version` |
| D-4 | The internal dashboard, wherever a universe-level statistic is shown (breadth, regime, counts) | Rendered label naming the universe and its version |
| D-5 | Any external, marketing or user-facing surface | The verbatim statement; and never the name "S&P 500" as a label for this universe |

**Draft disclosure text (verbatim, versioned with the bundle):**

> 4UR4 US Large-Cap 500 is a self-computed universe of the 500 largest eligible US-listed
> operating companies, constructed under methodology version `{universe_methodology_version}`.
> It is **not** the S&P 500, is not derived from S&P Dow Jones Indices constituent data,
> and is neither endorsed by nor equivalent to any S&P Dow Jones Indices index. Results
> computed on this universe are **not comparable** to published S&P 500 strategy results.

**An enforceable control, not just a convention.** A repository check should fail if the
string "S&P 500" appears as a *label* for 4UR4's universe in any result artifact, UI
string or report template. Referring to the licensed index as the thing deliberately not
used — as this document does — is permitted and is distinguishable, because those
references appear in prose with the licensing reason attached.

### 6.4 Expected divergence — not quantified, recorded as a gap

The brief asks for published evidence on mechanical-versus-committee index overlap.
**None was retrieved, because this session had no retrieval tool** ([§0.2](#02-evidence-status--and-a-limit-stated-up-front-rather-than-papered-over)).
No figure is guessed. Recorded as **G-U1**.

Two things are worth stating rather than nothing:

- **A precedent exists for the mechanical construction itself.** The paper that supplies
  this project's headline bias estimate — *"up to 8% per annum for the S&P500 taken as the
  benchmark"* — works with **"the running top 500 US capitalizations"** rather than
  licensed membership ([arXiv:0810.1922](https://arxiv.org/abs/0810.1922), retrieved
  2026-07-26, **VERIFIED (inherited)**). Rigorous work on a self-defined top-500 universe
  is established practice, not an improvisation. Whether that paper publishes an overlap
  figure against the licensed index is **not known** and is part of G-U1.
- **The overlap is measurable in-house, with free data, using a method the repository has
  already demonstrated.** See UE-05 below. The right way to close G-U1 is to measure it,
  not to find someone else's number.

---

## 7. Validation and the evidence plan

This is the acceptance proof a Verification role would check. Each item states the check,
the artifact, and the pass criterion. **None of them can be run under GOV-015**; they are
the specification of what would prove the reconstruction correct once a per-scope freeze
lift and a data source exist.

### 7.1 What these checks can and cannot establish

They establish that **the stated rules were applied correctly, completely and causally**.
They cannot establish that the rules describe the right object — that is a judgement, and
the only non-circular anchor for it is human adjudication of a real sample. This is
exactly the argument
[`phase2-independence-mechanism.md`](phase2-independence-mechanism.md) §1 makes about
spec-derived fixtures versus RM-01, and it has the same answer: **an `RU-01`-style
artifact** — one reference date, the full 500 with ranks and market caps, human-approved
and stored as evidence — should anchor the universe the way RM-01 anchors the detector.

### 7.2 `UE-01` — determinism and re-derivability

Re-running the reconstruction from the same inputs and the same
`universe_methodology_version` produces a **byte-identical** membership history.
**Artifact:** `universe_snapshot_id` = hash of the ordered membership table.
**Pass:** hashes equal.

### 7.3 `UE-02` — prefix-replay equivalence (the as-of test)

Streaming the reconstruction — feeding filings and bars in `filed_at` / bar order and
emitting membership as it goes — must produce the **same** membership history as any
batch computation. This is the direct analogue of
[`trendline-specification.md`](../../product/trendline-specification.md) §21.8 rule 3
("streaming the series bar-by-bar and batch-processing the whole series MUST yield
identical output"), and it is the operational definition of P1.
**Pass:** identical membership history, including `decided_at`.

### 7.4 `UE-03` — the no-future-information negative control

The strongest item here, and the one most likely to be skipped.

1. Reconstruct membership through reference date `r`.
2. Inject a share-count observation with `filed_at > r` that, if used, would change the
   rank ordering at `r`.
3. Re-run. **Membership at `r` must be unchanged.**
4. **Then prove the test has power:** run the same injection against a deliberately
   look-ahead-broken variant (one that selects by `value_as_of` instead of `filed_at`).
   That variant **must fail**. A control that passes for both is not a control.

This mirrors the repository's existing discipline — `check-evidence.mjs` carries a
negative control for its schema validator and positive/negative controls for its table
scanner precisely because *"a validator that silently regressed to a no-op would print
PASS forever"*.

### 7.5 `UE-05` — comparison against the §5.1 reconstructed-membership evidence

**Method.** Use the repository's own worked comparison
([`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md#51-e1--past-date-membership-snapshot-vs-today-worked-comparison)):
the dated 2015-12-28 public snapshot (revision `697200065`) versus today's, restricted
initially to the bounded "A" alphabetical block. Compare 4UR4's reconstructed universe at
the same two dates.

**The known false positives are a control on the comparison harness, not on the
universe.** The source research established that `AVGO` (Avago → Broadcom) and `ABC`
(AmerisourceBergen → Cencora) look like removals and are not — they are renames of
companies that never left. Therefore:

> **Harness pass criterion:** the comparison tool, resolving identity through
> `security_uid`, must report `AVGO` and `ABC` as **continuations, not removals**. If it
> reports them as removals, **the harness is wrong**, and no conclusion may be drawn about
> the universe from that run.

**Universe reporting criterion — and this is where P5 bites.** Agreement with the licensed
index is corroboration, never the target. A low overlap is **not** a failure. The metric
is therefore not the overlap percentage but the **attribution of the symmetric
difference**:

| Attribution bucket | Meaning | Target |
|---|---|---|
| Share-class aggregation | Explained by `UR-SEC` | Reported, expected non-zero |
| ADR / listing exclusion | Explained by `UR-LIST` | Reported, expected non-zero |
| Float adjustment | Explained by `UR-RANK` | Reported, expected non-zero |
| Seasoning / rebalance timing | Explained by `UR-LIQ`, `UR-REBAL` | Reported, expected non-zero |
| Committee discretion | Not reproducible by construction ([§6.1](#61-it-is-not-and-cannot-be-the-licensed-index)) | Reported, expected non-zero |
| **Unexplained** | Not attributable to any named rule | **Must be driven to zero** |

The count of *unexplained* differences is the only number in this table with a pass
threshold. It is also the number that would catch a genuine reconstruction bug, which is
the point.

**Two limits on this evidence, inherited and restated.** The comparison baseline is itself
a *reconstructed snapshot history*, the weakest of the three artifact types the source
research distinguishes; and its own adjudication left **11 of 18 candidate diffs
unverified** in a single alphabetical block. UE-05 is therefore corroborating evidence of
bounded strength, and treating a disagreement with it as authoritative would be an error.

### 7.6 The remaining checks

| # | Check | Pass criterion |
|---|---|---|
| **UE-04** | **Survivorship completeness.** The reconstructed history over any multi-year window must contain securities that no longer trade | If a window covering 2019–2023 yields **zero** currently-delisted members, the reconstruction is broken. First Republic is the canonical name to look for |
| **UE-06** | **Boundary stability / churn.** Report the market-cap gap distribution at ranks 490–510 and quarterly turnover with and without the buffer | Reported, with the buffer parameters justified by the measurement — replaces the assertion in [§3.2](#32-the-buffer) with data (closes G-U6) |
| **UE-07** | **Lag sensitivity.** Membership at `r` from information at `r` versus at `r + 120` days | Reported as a count of boundary flips; quantifies [§4.5](#45-how-large-is-the-lag-error-honestly) |
| **UE-08** | **Share-class invariants.** Σ class caps = issuer cap; exactly one `PRIMARY` class per issuer per date; no issuer appears twice in a snapshot | Exact |
| **UE-09** | **Identity invariants.** No ticker resolves to two `security_uid`s on one date; every membership interval resolves to a security with price coverage; ticker reuse across time is detected and recorded | Exact |
| **UE-10** | **Cardinality and continuity.** Exactly 500 at each effective date; between rebalances the count only decreases; membership intervals are half-open and non-overlapping per security | Exact |
| **UE-11** | **Market-cap basis invariant.** `raw_close × raw_shares` = `adjusted_close × adjusted_shares` to tolerance | Catches the double-counted split of [§2.5](#25-ur-rank--ranking-basis-and-the-float-question)(a) |
| **UE-12** | **Seed-artefact disclosure.** The first four rebalances after the seed carry `SEED_INFLUENCED` | Present in the artifact; any backtest overlapping them reports it |
| **UE-13** | **Disclosure presence.** Every result artifact carries `universe_methodology_version` and the [§6.3](#63-backtest-results-are-not-comparable--and-where-that-must-be-disclosed) statement | CI failure if absent |
| **UE-14** | **Exclusion-register and P3 audit.** Every `UR-OPCO` exclusion has a citation and a date; a random sample is re-adjudicated by a human; liquidity- and staleness-driven removals are reported as counts and reviewed for outcome correlation | Sample agreement; no undisclosed availability-driven removals |

---

## 8. Versioning and backtestability

The mechanism deliberately mirrors `spec_version` and `tolerance_version`, which already
work in this repository.

### 8.1 The manifest

`universe_methodology_version` (e.g. `u500-0.1.0`) pins:

- the version of each of the nine rule modules in [§1.2](#12-the-rule-bundle);
- every named parameter and its value — `mddv_min_usd`, `liquidity_window_bars`,
  `min_bar_coverage`, `seasoning_bars`, `rebalance_frequency`, `rebalance_lag_days`,
  `buffer_in_rank`, `buffer_out_rank`, `max_staleness_days`;
- the hash of the exclusion register;
- and produces a `universe_snapshot_id` — the hash of the membership history it yields.

**These parameters are first-class, versioned, backtestable objects, not magic constants.**
That is the posture [HD-13](../../product/human-decisions.md) and
[HD-14](../../product/human-decisions.md) established for `eps_break` and the formation
gates, applied to the universe.

### 8.2 Pinning a backtest run

A result is interpretable **iff** its run record carries all of:

| Field | Pins |
|---|---|
| `universe_methodology_version` | Which rules produced the universe |
| `universe_snapshot_id` | Which membership history, exactly |
| `data_snapshot_id` (prices) | Which bar vintage, per DI-05 |
| `filings_snapshot_id` | Which share-count vintage |
| `spec_version` | Which detector |
| `tolerance_version` | Which tolerance set |
| `confidence_version` | Which score |

A run missing any of these is **not** a defensible result, and the check is mechanical
(UE-13). This extends the existing rule that a signal is reproducible from
`(algo_version, confidence_version, data snapshot_id, input bars)`
([`mvp-architecture.md`](mvp-architecture.md) §5) by the two universe fields that rule
does not yet name.

### 8.3 Change semantics — and how HD-18's gate is enforced by the version scheme

| Bump | Meaning | Mechanical test | Gate |
|---|---|---|---|
| **PATCH** | Clarification only; membership must be unchanged | Re-run must yield an **identical** `universe_snapshot_id`. A PATCH that changes it is a **CI failure** | Architect |
| **MINOR** | Membership changes; the intended market segment does not | Diff report of added/removed members with attribution | Architect, with evidence |
| **MAJOR** | The **intended market segment** changes | Diff report plus explicit rationale | **Product Owner-gated under HD-18** |

This maps HD-18's delegation boundary directly onto the version scheme: *"material
changes to the intended market segment remain Product Owner-gated."* A MAJOR bump is by
definition that change, and the PATCH test makes the claim "this changed nothing"
falsifiable instead of merely asserted.

**Rule changes never mutate history.** A new bundle version produces a **new** membership
history under a new `universe_snapshot_id`; the previous one is retained (P2). Comparing
versions is an explicit diff artifact, never a silent overwrite. This is what keeps an
older backtest interpretable after the rules move.

---

## 9. Interface requirements for `data/` (extending DI-01…DI-12)

These extend, and do not replace, the twelve requirements in
[`data-provider-findings.md`](../../product/data-provider-findings.md#9-technical-interface-requirements-for-data).
Each exists because a specific finding above would otherwise leak into `engine/` or into
`worker/`.

| # | Requirement | Driven by |
|---|---|---|
| **UD-01** | **Share counts are a first-class call**: `shares_outstanding(issuer, range, as_of)` returning observations with `value`, `value_as_of`, `filed_at`, `period_end`, `class_id`, `source_ref`, `is_amendment`. All seven fields mandatory; an adapter that cannot supply `filed_at` **cannot be admitted**, because P1 is unenforceable without it | [§4.2](#42-what-data-is-needed), [§4.4](#44-the-lag-rule--the-governing-invariant) |
| **UD-02** | **A filings adapter distinct from the bars adapter**, with its own `redistribution_class` per DI-09. Do **not** assume filing content is freely redistributable — the licensing of filing text and of derived identifiers is unresearched (**G-U7**) | DI-09; [§5.1](#51-ur-id--the-identity-model) |
| **UD-03** | **Universe reads take two dates**: `members(on_date, as_of)`. `on_date` is the membership date; `as_of` is the information vintage. Conflating them **is** the look-ahead bug, so the interface must make them un-conflatable | P1; DI-04 |
| **UD-04** | **Dated identity resolution only**: `resolve(identifier_type, value, on_date)`. No bare ticker map may exist anywhere in `data/` | [§5.1](#51-ur-id--the-identity-model); `FRC → FRCB` |
| **UD-05** | **Volume adjustment basis declared**, and the invariant `adj_close × adj_volume ≈ raw_close × raw_volume` asserted per bar, so dollar volume is well-defined across splits | [§2.4](#24-ur-liq--liquidity-and-seasoning-screens); the raw-OHLC/split-adjusted-volume mismatch |
| **UD-06** | **Raw (unadjusted) close obtainable for every bar the universe ranks on** — a new, load-bearing consumer of DI-02 | [§2.5](#25-ur-rank--ranking-basis-and-the-float-question)(a) |
| **UD-07** | **The universe is a stored artifact, not a function call.** Every membership row is persisted with `decided_at`, provenance and reason code; recomputation must reproduce it exactly (UE-01) | HD-18 requirement 4 |
| **UD-08** | **Delisted securities and removed members are retained forever.** A removal writes `effective_to`; it never deletes a row. `data/` must have no operation that can drop a security | P2 |
| **UD-09** | **Candidate-pool completeness is declared and recorded.** Ranking runs against a declared pool with a recorded row count; a pool that silently shrinks **flags the run** rather than producing a smaller ranking | P3; mirrors DI-11 |
| **UD-10** | **Interpolation of share counts is a banned operation**, enforced as a derivation-time assertion rather than a convention — mirroring DI-06b, which makes a forbidden provider field a load-time error | [§4.4](#44-the-lag-rule--the-governing-invariant) rule 2 |
| **UD-11** | **Restated-versus-as-reported is a declared adapter capability.** `fundamentals_basis ∈ {AS_REPORTED, RESTATED, UNKNOWN}`. `RESTATED` and `UNKNOWN` are admissible for research and **inadmissible** for a shipped or evidence-bearing universe | [§4.3](#43-where-the-data-comes-from) |

**Consequence for the engine: none.** `engine/` keeps receiving plain bars and returning
plain results. Everything above is absorbed at the `data/` seam, exactly as DI-01…DI-12
were — which remains the test of whether the seam is in the right place.

---

## 10. Task breakdown (design-only sequencing; nothing here is authorised to be built)

Ordered so that each step's output is checkable before the next depends on it. Every step
below the line requires a **per-scope GOV-015 lift** ([GOV-013](../../governance/approval-gate.md)).

| # | Task | Depends on | Output | Freeze status |
|---|---|---|---|---|
| T1 | Product Owner rules on OQ-U1…OQ-U6 ([§11](#11-open-questions--decided-defaults-vs-product-owner-gated)) | this document | Ruling recorded as an HD entry by the Product Steward | **Permitted now** — a decision, not a build |
| T2 | Open **R9 — point-in-time shares outstanding / market cap** as a research question | T1 | Research question added by the Product Steward | **Permitted now** |
| T3 | Verify the UNVERIFIED-LEADs in [§12](#12-gaps-this-design-opens-or-inherits) against primary pages | T2 | Findings document with URLs and retrieval dates | **Freeze-permitted research**, no accounts, no downloads |
| T4 | Freeze the rule bundle at `u500-0.1.0` with rulings and verified predicates folded in | T1, T3 | Amended version of this document | **Permitted now** |
| T5 | Specify `RU-01` — the human-adjudicated reference-date universe artifact | T4 | Evidence specification | **Permitted now** |
| T6 | Implement the identity register and filings adapter (UD-01…UD-04) | T4, provider decision | Code | **Blocked** — GOV-015 + HD-06 |
| T7 | Implement the reconstruction and run UE-01…UE-04 | T6 | Membership history + control results | **Blocked** |
| T8 | Run UE-05…UE-14; produce `RU-01`; close G-U1, G-U5, G-U6 | T7 | Evidence pack | **Blocked** |

---

## 11. Open questions — decided defaults vs Product-Owner-gated

### 11.1 Decided here as safe reversible research defaults (HD-18 delegation)

Each is reversible by a rule-version bump plus a re-run — no rewrite, no data
re-acquisition.

| Default | Rule | Reversal cost |
|---|---|---|
| Form-type-primary operating-company test; dated exclusion register | `UR-OPCO` | Register edit + re-run |
| REITs included | `UR-OPCO` | Version bump + re-run *(flagged for PO awareness)* |
| Issuer-level aggregation of share classes | `UR-SEC` | Version bump + re-run |
| One line per issuer (designated primary class) | `UR-SEC` | Version bump; secondary classes are already retained |
| `MDDV_63 ≥ $25m`, 90% coverage, 63-day seasoning | `UR-LIQ` | Parameter bump + re-run |
| Full market cap, not float-adjusted | `UR-RANK` | Requires a float dataset first — reversible but not free |
| Quarterly rebalance, 6-trading-day effective lag | `UR-REBAL` | Parameter bump + re-run |
| Buffer 450/550 with reconciliation to exactly 500 | `UR-REBAL` | Parameter bump + re-run |
| No intra-quarter additions; universe may run below 500 | `UR-REBAL` | Version bump + re-run |
| Carry-forward step function; interpolation banned | `UR-PIT` | Not reversible in spirit — P1 forbids the alternative |
| Stale share data is flagged, never filtered | `UR-PIT` | Not reversible in spirit — P3 forbids the alternative |
| 4UR4-minted `security_uid` as the canonical key | `UR-ID` | Not reversible cheaply; chosen deliberately as the low-regret option |

### 11.2 Escalated to the Product Owner

Each of these either changes the intended market segment or implies spend, and HD-18
reserves both.

| # | Question | Why it is gated | Default if the Product Owner does not rule |
|---|---|---|---|
| **OQ-U1** | **Are ADRs and non-US-primary listings in or out?** [§2.2](#22-ur-list--us-listed-the-domicile-vs-listing-decision) | Changes which companies the product will ever show — arguably a market-segment change | Excluded, as designed; flagged in every artifact as a v0.1.0 default awaiting ruling |
| **OQ-U2** | **Exactly 500, or a variable count within the buffer band?** [§3.2](#32-the-buffer) | The product name says 500; a 512-name "500" is a product-surface question | Exactly 500 with reconciliation |
| **OQ-U3** | **Are REITs in?** [§2.1.2](#212-the-exclusion-register) | Excluding a sector is a segment change; including is the lower-surprise default | Included |
| **OQ-U4** | **Is R9 (point-in-time shares outstanding) opened, and does any spend attach?** [§4.1](#41-the-dependency-chain-and-where-it-breaks) | HD-06 and HD-07 make provider selection and spend human-gated | R9 opened as **free-path-only** research; no vendor contact |
| **OQ-U5** | **How far back must the backtest window reach?** [§4.3](#43-where-the-data-comes-from) | The free SEC/XBRL path has a hard historical bound; reaching further is a spend or a text-extraction project | Window starts where the free structured path starts, and the start date is disclosed |
| **OQ-U6** | **Is a *first-class* universe-methodology disclosure required on user-facing surfaces at MVP, or only internally?** [§6.3](#63-backtest-results-are-not-comparable--and-where-that-must-be-disclosed) | It is a product and legal-posture question, not a technical one | All five surfaces, D-1…D-5 |

**Nothing in this section is a decision on the Product Owner's behalf.** Where a default
is stated, it is stated so that work is not blocked and so that the cost of the default is
visible.

---

## 12. Gaps this design opens or inherits

Recorded as gaps. A documented gap is more useful than a confident guess.

| # | Gap | Why it matters | How to close it |
|---|---|---|---|
| **G-U1** | **No published evidence on mechanical-vs-committee index overlap was retrieved** | Prevents quantifying [§6.2](#62-the-named-intended-divergences) | Literature search **and** the in-house UE-05 measurement; the latter is the better answer |
| **G-U2** | **EDGAR submissions metadata**: endpoint, field names, entity/form classification, fair-access and User-Agent policy | `UR-OPCO` depends on the form-type test | Read <https://www.sec.gov/search-filings/edgar-application-programming-interfaces> and <https://www.sec.gov/os/webmaster-faq#developers> |
| **G-U3** | **Cover-page share counts**: the exact XBRL tag, per-class axis mechanics, bulk-file layout, and the XBRL phase-in dates that bound the reconstruction window | The single input the whole universe depends on, and the bound on how far back it reaches | Read the SEC's XBRL frames/company-concept API docs and the Financial Statement Data Sets documentation |
| **G-U4** | **Float estimation** from ownership filings: which forms, which thresholds, what lag | Determines whether `UR-RANK` v0.2.0 is feasible at all | Research question, only if float is wanted |
| **G-U5** | **Magnitude of the full-cap versus float-adjusted divergence** | Named in [§2.5](#25-ur-rank--ranking-basis-and-the-float-question) but unquantified | Measurable once any float estimate exists |
| **G-U6** | **Rank-boundary gap distribution and turnover with/without buffer** | The buffer's justification is currently an expectation, not a measurement | UE-06 |
| **G-U7** | **CUSIP and FIGI licensing** for a redistribution-bearing product | An identifier licence is exactly the class of unpriced exposure HD-18 was taken to avoid — repeating it with identifiers would be ironic | Read CUSIP Global Services and OpenFIGI terms; route to counsel like **G10** was |
| **G-U8** | **No provider evaluated for point-in-time shares outstanding**, and no vendor's as-reported-vs-restated posture is known | [§4.1](#41-the-dependency-chain-and-where-it-breaks) | R9 (OQ-U4) |
| **G-U9** | **Backtest semantics for a mid-position delisting remain unspecified** (inherited) | Deliberately not decided here; the universe supplies the event, not the accounting | Owner of the backtest specification |
| **G-U10** | **Spin-off and merger corporate-action coverage** is undocumented for both recommended providers (inherited **G-08**) | `UR-CA` depends on it, and a mishandled spin-off injects a false ATH | Vendor questions before HD-06 |
| **G-U11** | **The licensed index's published methodology has not been read** (inherited **G5** — `spglobal.com` returns HTTP 403 to automated fetch) | Bounds what [§6.1](#61-it-is-not-and-cannot-be-the-licensed-index) may assert | Low priority **by design**: 4UR4 is not trying to replicate it, and reading it to replicate would raise its own question |

---

## 13. Source index

All external claims below were retrieved and dated by the cited repository research
documents; **no page was fetched in this session** ([§0.2](#02-evidence-status--and-a-limit-stated-up-front-rather-than-papered-over)).

**Repository sources:**
[`survivorship-bias-findings.md`](../../product/survivorship-bias-findings.md) ·
[`data-provider-findings.md`](../../product/data-provider-findings.md) ·
[`data-provider-research.md`](../../product/data-provider-research.md) ·
[`human-decisions.md`](../../product/human-decisions.md) ·
[`trendline-specification.md`](../../product/trendline-specification.md) ·
[`mvp-architecture.md`](mvp-architecture.md) ·
[`phase2-independence-mechanism.md`](phase2-independence-mechanism.md) ·
[`build-freeze.md`](../../governance/build-freeze.md) ·
[`approval-gate.md`](../../governance/approval-gate.md)

**External, all retrieved 2026-07-26 by the cited research (VERIFIED (inherited)):**
[S&P Master Index License Agreement, SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1776030/000119312521050328/d83606dex998c.htm) ·
[Daniel, Sornette & Wöhrmann, arXiv:0810.1922](https://arxiv.org/abs/0810.1922) ·
[Shumway, *The Delisting Bias in CRSP Data* (1997)](https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf) ·
[Wikipedia, *List of S&P 500 companies*, revision 697200065 (2015-12-28)](https://en.wikipedia.org/w/index.php?title=List_of_S%26P_500_companies&oldid=697200065) ·
[First Republic Bank / FRCB on stockanalysis.com](https://stockanalysis.com/stocks/frc/) ·
[N-PORT public-reporting delay, Federal Register](https://www.federalregister.gov/documents/2025/04/22/2025-06861/form-n-port-and-form-n-cen-reporting-guidance-on-open-end-fund-liquidity-risk-management-programs)

**Named but NOT retrieved — UNVERIFIED-LEAD, see [§12](#12-gaps-this-design-opens-or-inherits):**
<https://www.sec.gov/search-filings/edgar-application-programming-interfaces> ·
<https://www.sec.gov/os/webmaster-faq#developers> ·
SEC XBRL frames / company-concept API documentation ·
SEC Financial Statement Data Sets documentation ·
CUSIP Global Services licensing terms ·
OpenFIGI licensing terms

---

> **Reminder.** Under **GOV-015 none of this is built.** This document defines rules,
> contracts and the evidence that would prove them — it is the map, not the territory.
