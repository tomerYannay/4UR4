# 4UR4 — Ticket Definitions (first three phases)

Status: planning artifact under [GOV-015](../../governance/build-freeze.md). These
began as **ticket DEFINITIONS** for the primary session to create as GitHub issues.
**They are now live issues** — (a)/(b) delivered by PR #18, (c) = [#4](https://github.com/tomerYannay/4UR4/issues/4),
(d) = [#5](https://github.com/tomerYannay/4UR4/issues/5), (e) = [#6](https://github.com/tomerYannay/4UR4/issues/6),
(f) = [#7](https://github.com/tomerYannay/4UR4/issues/7) — and the roadmap they
trace to is **approved** (HD-16, 2026-07-26). This file is therefore a historical
definition record; **the issues are authoritative** where the two disagree.

> **Hygiene ([GOV-008](../../governance/ticket-hygiene.md)):** at most 3 epics
> (labels only — no umbrella issues); at most 5 open **unstarted Ready** tickets;
> one ticket = one verifiable outcome; no speculative implementation backlog.
> Implementation tickets are `blocked: freeze` **unless their scope carries a lift** — as
> `engine/` now does twice over, **HD-22** for Phase 2 and **HD-24 §3** for Phase 3.
> **A lift removes `blocked: freeze`; it does not confer Ready.**
>
> **DoR ([GOV-004](../../governance/definition-of-ready.md)):** every ticket below
> "Becomes Ready upon human roadmap approval ([GOV-013](../../governance/approval-gate.md));
> freeze status set." Research/design tickets are freeze-permitted; implementation
> tickets are **blocked: freeze** until a human lifts the freeze per-scope — **and a lift
> for one phase's scope is not a lift for the next one's**
> ([GOV-015](../../governance/build-freeze.md) rule 4).
>
> **That approval was given on 2026-07-26** — the Phase 0–9 roadmap baseline is
> APPROVED under GOV-013
> ([artifact](https://github.com/tomerYannay/4UR4/issues/23); recorded as **HD-16**).
> Tickets (a)–(d) therefore satisfy their DoR condition and are **Ready**, not
> merely Ready-eligible; (a) and (b) are **delivered** (23 golden fixtures + RM-01,
> merged in PR #18). Approval of the baseline did **not** lift the freeze, so (e)
> and (f) are unchanged.

## Epic labels (3) — labels only, NOT issues

1. **`epic: product-quant-spec`** — "Product & Quant Specification" (Phase 0).
2. **`epic: market-data-foundation`** — "Market Data Foundation" (Phase 1).
3. **`epic: trendline-detection-engine`** — "Trendline Detection Engine" (Phase 2).

## Summary

| # | Ticket | Epic | Phase | Autonomy | Ready status |
|---|--------|------|-------|----------|--------------|
| a | Golden-example fixture set: trendline geometry & selection | product-quant-spec | 0 | design-only (freeze-permitted) | **Delivered** (PR #18) |
| b | Acceptance-example set: breakout / retest / expiry | product-quant-spec | 0 | design-only (freeze-permitted) | **Delivered** (PR #18) |
| c | Data-provider research & recommendation | market-data-foundation | 1 | research-only (freeze-permitted) | **Ready** ([#4](https://github.com/tomerYannay/4UR4/issues/4)) |
| d | Survivorship-free constituents + corporate-actions research | market-data-foundation | 1 | research-only (freeze-permitted) | **Ready** ([#5](https://github.com/tomerYannay/4UR4/issues/5)) |
| e | Market-data ingestion & storage service | market-data-foundation | 1 | blocked (build-freeze) | blocked: freeze |
| f | Deterministic trendline detection engine | trendline-detection-engine | 2 | implementation (HD-22 `engine/` lift) | **NOT Ready** — entry criteria; built anyway, see the deviation |
| g | Breakout, freeze, retest, failure & expiry engine | trendline-detection-engine | 3 | implementation (HD-24 §3 Phase-3 `engine/` lift) | **READY** ([#40](https://github.com/tomerYannay/4UR4/issues/40)) — 2026-07-28, all 8 DoR elements met; unstarted |
| h | Phase-2 engine hardening (M-28/29/30/32) | trendline-detection-engine | 2 | implementation (HD-22 `engine/` lift) | **Delivered and merged** ([PR #37](https://github.com/tomerYannay/4UR4/pull/37), `c66fd294`) — no longer In Progress |

**Totals (recounted 2026-07-28, after ticket (g) reached Ready and ticket (h) merged):** 8
tickets defined · **3 delivered** (a, b — Phase 0; h — engine hardening, merged at
`c66fd294`) · **2 Ready and in progress** (c, d — Phase 1 research) · **1 Ready and unstarted**
(g — Phase 3) · **1 blocked: freeze** (e) · **1 not Ready** (f). HD-06 remains **PENDING**: (c)
may recommend a provider and may not select one, commit spend, or accept licensing terms.
*(Superseded: "**3 Ready and in progress** (c, d, h) · **2 not Ready** (f, g)". **(h) is
delivered**, so it no longer consumes WIP; whether it is **Done** under
[GOV-005](../../governance/definition-of-done.md) is Verification's and Release & Ops' call,
not the Product Steward's, and is not asserted here.)*

**All three [GOV-008](../../governance/ticket-hygiene.md) budgets, stated — WIP was unstated
before this change (M-55) and the idea budget was still unstated in the first form of this
table — plus rule 4, whose row was mislabelled as rule 3.**

*Corrected 2026-07-28, with the wrong label quoted rather than replaced in silence.* This block
read *"All three GOV-008 budgets, stated — the third was previously unstated (M-55)"* over a
table whose last row was headed **"3 — epics"**. **The epic constraint is
[GOV-008](../../governance/ticket-hygiene.md) rule 4** — *"One ticket = one verifiable outcome.
No umbrella/epic tickets"* — and **rule 3 is the idea budget**, *"at most **3** new idea cards
per cycle"*. Rule 3 was therefore the budget still unstated, and the *"all three budgets"* claim
was **false at the moment it was made**: the table stated two budgets and one non-budget rule
under a third budget's number. Both are stated below. Found by Code Review.

| Rule | Limit | Count now | Verdict |
|---|---|---|---|
| 1 — WIP `In Progress` | ≤ 3 | **2** (c, d) — restated 2026-07-28; **(h) is delivered and merged** ([PR #37](https://github.com/tomerYannay/4UR4/pull/37), `c66fd294`) and no longer counts | **compliant, one slot FREE** |
| 2 — open **unstarted** Ready | ≤ 5 | **1** (g) | compliant |
| 3 — **idea budget**: new idea cards per cycle | ≤ 3 | **3** in the last cycle in which any were submitted — IDEA-0002/0003/0004, 2026-07-24, all still *awaiting triage* ([`../../ideas/inbox.md`](../../ideas/inbox.md)) — and **0** since | compliant, and saturated for that cycle |
| 4 — one ticket = one verifiable outcome; no umbrella/epic tickets | 3 epic **labels**, no umbrella issues | 3 | compliant |

**No budget is breached by this change, and the reason is worth stating rather than
asserting.** Making a ticket **Ready** consumes the rule-2 budget, not the rule-1 WIP limit;
only *starting* it consumes WIP. **(g) IS made Ready by this change**, so rule 2 moves from
**0 to 1** against a limit of 5 — comfortably compliant. **Rule 1 was at its limit and is no
longer:** WIP read **3 (c, d, h)** while (h) was in flight, and **(h) has since been delivered
and merged** ([PR #37](https://github.com/tomerYannay/4UR4/pull/37), `c66fd294` —
[`../project-state.md`](../project-state.md) records the merge), so it no longer counts as In
Progress and **WIP is 2 of 3**. **One slot is free, so (g) may be started** without breaching
rule 1. *(Superseded, quoted rather than deleted: "**But rule 1 is at its limit right now: WIP
is exactly 3.** Whenever (g) does become Ready, it cannot be started until a WIP slot frees."
True when written; the slot freed by (h) merging, not by any reinterpretation of the rule.)*
Recorded here because a totals line that checked two of GOV-008's rules read as a full check,
and one of the unstated rules was the one at its limit.

**Two corrections to the framing above, because it went stale rather than wrong-headed.**

1. **The freeze no longer blocks `engine/`.** The note above says *"Approval of the baseline
   did not lift the freeze, so (e) and (f) are unchanged"* — true when written, and
   **superseded by [HD-22](../human-decisions.md)** (Product Owner, 2026-07-26,
   [#31](https://github.com/tomerYannay/4UR4/issues/31)), which lifted GOV-015 for
   `engine/` and nothing else. **(e) is unchanged and still `blocked: freeze`. (f) is not
   blocked by the freeze any more** — it is held by Phase-2 **entry** criteria and by the
   DoR. ~~**(g) is `blocked: freeze`**: the lift is a Phase-2 lift, and
   [GOV-015](../../governance/build-freeze.md) rule 4 ties a lift to a specific approved,
   Ready ticket.~~ **Superseded 2026-07-28 by [HD-24](../human-decisions.md) §3
   ([#39](https://github.com/tomerYannay/4UR4/issues/39)), which lifts GOV-015 for **Phase 3**
   inside `engine/`. (g) is no longer `blocked: freeze`.** The struck sentence's second half
   nevertheless still bit, in the opposite direction from how HD-24 §3 read it: rule 4 ties
   a lift to a specific **approved, Ready** ticket, and **(g) was not Ready** — so the lift
   existed and rule 4 was still unsatisfied. **Closed 2026-07-28: (g) is now READY**, on a DoR
   re-assessed forward after the four escalations were ruled and Phase 2 exit was determined,
   so **rule 4 is satisfied by a ticket that meets it** rather than by assertion. See (g)'s
   DoR assessment.
2. **(g) is now a live issue; (h) is still a definition only.** (a)–(f) map to issues and
   *"the issues are authoritative where the two disagree"*.
   **(g) → [#40](https://github.com/tomerYannay/4UR4/issues/40)**, filed 2026-07-28 by the
   Orchestrator from the Product Steward's draft. **Filing it supplied *specific* — one of
   [GOV-015](../../governance/build-freeze.md) rule 4's three words — and supplied nothing
   toward *approved* or *Ready***; those came later the same day, from the rulings and the
   exit determination, not from the filing. The issue says so on its own face, leads with
   **"Status: NOT READY. Do not start."**, and instructs the filer not to apply a Ready label
   and not to apply `blocked: freeze` (HD-24 §3 lifted it).
   **⚠ [#40](https://github.com/tomerYannay/4UR4/issues/40)'s body is now STALE and an
   Orchestrator action is owed.** As of **2026-07-28** (g) **is Ready** — see its DoR
   assessment below — so the issue's leading line and its no-Ready-label instruction are both
   superseded. **The Product Steward does not edit GitHub issues**; the update is the
   Orchestrator's, and until it lands *"the issues are authoritative where the two disagree"*
   would point a reader at the **wrong** answer for this one field. **This file is the
   authority on (g)'s Ready status until #40 is updated**, and that exception is stated here
   rather than left to be discovered.
   **(h) has no issue number yet**;
   creating it remains an Orchestrator action. Neither adds roadmap scope:
   **(g)** is the already-approved **Phase 3** roadmap item and **(h)** is corrective work
   inside the already-approved **Phase 2** item, so neither requires a new
   [GOV-002](../../governance/roadmap-authority.md) roadmap placement or a
   [GOV-013](../../governance/approval-gate.md) clause-2 approval.

---

## Ticket (a) — Golden-example fixture set: trendline geometry & selection

- **Title:** Golden-example fixtures — trendline geometry, anchoring & envelope selection
- **Epic:** `epic: product-quant-spec`
- **Phase:** 0 — Specification & golden examples
- **Context:** The trendline spec ([`trendline-specification.md`](../trendline-specification.md)
  §4–§9, §18) defines the canonical ATH-anchored log descending line and its
  deterministic selection. Before any engine is built, we need the **correctness
  contract**: deterministic fixtures a later implementation MUST reproduce exactly.
  Design/doc artifacts only — no product code.
- **Scope (in-scope):** Author the geometry/selection golden fixtures GX-01, GX-02,
  GX-06, GX-08, GX-09, GX-10, GX-12 as (synthetic OHLCV CSV) + (expected-output
  JSON) pairs. Each expected output includes selected anchors `A`/`B*`, slope `m`,
  intercept `b`, touch list, line state, and every reason code, with numeric
  geometry pinned to **6 significant figures**.
- **Non-goals (out-of-scope):** Any detector/engine code; breakout/retest/expiry
  fixtures (ticket b); confidence fixtures; provider data.
- **Acceptance criteria (testable):**
  - [ ] GX-01, GX-02, GX-06, GX-08, GX-09, GX-10, GX-12 each exist as a CSV+JSON pair.
  - [ ] GX-02 encodes the §8 discrimination case and asserts `B*=(45,92)`, not `(20,96)`.
  - [ ] Every expected JSON lists anchors, `m`, `b`, state, touch list, and reason codes.
  - [ ] All numeric geometry is pinned to 6 significant figures.
  - [ ] A reviewer maps each fixture to the spec section(s) it locks.
- **Dependencies:** Human decisions **HD-01** (adjustment basis), **HD-02**
  (envelope rule) resolved or explicitly provisional; trendline spec §4–§9, §18.
- **Evidence plan ([GOV-006](../../governance/definition-of-done.md)):** Committed
  fixture files under a fixtures docs path; a review record mapping each GX to its
  spec section; no code — fixtures are the deliverable.
- **Autonomy level:** design-only (freeze-permitted).
- **Responsible agent type:** Architect, with a GOV-016 **trendline-math advisory**
  temporary specialist under the Architect.
- **DoR note:** Becomes Ready upon human roadmap approval (GOV-013); freeze status set.

## Ticket (b) — Acceptance-example set: breakout / retest / expiry

- **Title:** Golden-example fixtures — breakout, wick-break, retest, failure & expiry
- **Epic:** `epic: product-quant-spec`
- **Phase:** 0 — Specification & golden examples
- **Context:** The trendline spec (§11, §13–§18) defines the state machine and the
  breakout/wick-break/retest/failed-breakout/expiry semantics with reason codes.
  These need their own deterministic acceptance fixtures. Design/doc only.
- **Scope (in-scope):** Author fixtures GX-03 (wick-break vs breakout), GX-04
  (retest hold), GX-05 (failed breakout), GX-07 (expiry), GX-11 (volume-soft
  breakout) as CSV + expected-JSON pairs, each asserting the resulting state, the
  breakout/confirmed bars where relevant, and every reason code (incl. `LOW_VOLUME`).
- **Non-goals (out-of-scope):** Engine code; geometry-selection fixtures (ticket a);
  confidence fixtures; provider data.
- **Acceptance criteria (testable):**
  - [ ] GX-03, GX-04, GX-05, GX-07, GX-11 each exist as a CSV+JSON pair.
  - [ ] GX-03 shows a rejected `WICK_BREAK` (intrabar high only) then a `BROKEN_OUT` confirmed on the **first daily close** above the line — no multi-bar persistence wait (HD-03).
  - [ ] GX-11 asserts a first-close breakout flagged `LOW_VOLUME` — volume is a confidence feature, not a validity gate (not voided) (HD-03).
  - [ ] Each expected JSON records final state, relevant bars, and all reason codes.
  - [ ] Numeric values pinned to 6 significant figures; reviewer maps each to spec §.
- **Dependencies:** Human decision **HD-03** (breakout confirmation policy) resolved
  or provisional; trendline spec §11, §13–§18; ideally after ticket (a) for shared
  fixture conventions.
- **Evidence plan (GOV-006):** Committed fixture files; a review record mapping each
  GX to its spec section; no code.
- **Autonomy level:** design-only (freeze-permitted).
- **Responsible agent type:** Architect, with a GOV-016 **trendline-math advisory**
  temporary specialist under the Architect.
- **DoR note:** Becomes Ready upon human roadmap approval (GOV-013); freeze status set.

## Ticket (c) — Data-provider research & recommendation

- **Title:** Data-provider research & recommendation (research only, human-gated decision)
- **Epic:** `epic: market-data-foundation`
- **Phase:** 1 — Market-data foundation
- **Context:** The `data/` layer is provider-agnostic (architecture §3.2) and no
  provider is chosen by any agent — selection and spend are human-gated (HD-06,
  [GOV-013](../../governance/approval-gate.md)). This ticket executes the research
  instrument in [`data-provider-research.md`](../data-provider-research.md) (R1–R3,
  R8) and produces evidence for a human to decide.
- **Scope (in-scope):** Answer research areas R1 (historical daily OHLCV), R2
  (live/delayed), R3 (splits/corporate actions), R8 (expected cost); collect the
  specified evidence (sample pulls, adjusted-vs-raw split spot-check, EOD timing,
  cost summary); fill the comparison matrix **as evidence**, stopping short of a
  purchase recommendation.
- **Non-goals (out-of-scope):** Selecting or paying a provider (human-gated);
  building any adapter or `data/` code; constituents/delisted research (ticket d);
  sentiment source selection.
- **Acceptance criteria (testable):**
  - [ ] R1, R2, R3, R8 each have documented findings + the specified evidence artifacts.
  - [ ] Adjusted-vs-raw spot-check around a known split is recorded.
  - [ ] Comparison-matrix cells populated with evidence (not a scored decision).
  - [ ] Every human-gated point is explicitly flagged as **HUMAN-GATED (GOV-013)**.
  - [ ] Output states clearly it recommends no purchase and commits nothing.
- **Dependencies:** [`data-provider-research.md`](../data-provider-research.md);
  feeds **HD-06**. Independent of tickets a/b.
- **Evidence plan (GOV-006):** A committed research findings doc under `product/`
  with attached sample-pull artifacts and the evidence-populated matrix; labeled
  context-only.
- **Autonomy level:** research-only (freeze-permitted).
- **Responsible agent type:** Architect, with a GOV-016 **market-data advisory**
  temporary specialist under the Architect.
- **DoR note:** Becomes Ready upon human roadmap approval (GOV-013); freeze status set.

## Ticket (d) — Survivorship-bias-free constituents + corporate-actions research

- **Title:** Survivorship-bias-free universe constituents + delisted history research (research only)
  *(HD-18, 2026-07-26: redirected from licensed S&P 500 membership to the self-computed
  **4UR4 US Large-Cap 500**. The ticket's purpose — an unbiased point-in-time universe —
  is unchanged; the source of membership is not.)*
- **Epic:** `epic: market-data-foundation`
- **Phase:** 1 — Market-data foundation
- **Context:** Correct backtests require point-in-time universe membership and
  delisted price history (data research R4/R5); this is correctness-critical and
  commonly a paid, licensed dataset (HD-07). Research availability/licensing/cost
  only — no acquisition.
- **Scope (in-scope):** Answer R4 (point-in-time constituents), R5 (delisted
  history), and the constituent/delisted portions of R7 (redistribution rights);
  collect evidence (a historical membership snapshot vs. today; a delisted-name
  history pull; add/remove event coverage; licensing excerpts).
- **Non-goals (out-of-scope):** Purchasing/licensing any dataset (human-gated);
  building ingestion (ticket e); OHLCV/cost research (ticket c); sentiment sources.
- **Acceptance criteria (testable):**
  - [ ] R4 and R5 findings documented with the specified evidence artifacts.
  - [ ] A past-date membership snapshot is compared against today's members.
  - [ ] Delisted-coverage depth and add/remove event coverage are documented.
  - [ ] Redistribution/licensing terms for constituent data quoted with source+date.
  - [ ] Paid/licensed items flagged **HUMAN-GATED (GOV-013)**; commits nothing.
- **Dependencies:** [`data-provider-research.md`](../data-provider-research.md) R4/R5/R7;
  feeds **HD-07**. Independent of tickets a/b; complements ticket c.
- **Evidence plan (GOV-006):** A committed research findings doc with membership/
  delisted sample artifacts and licensing excerpts; labeled context-only.
- **Autonomy level:** research-only (freeze-permitted).
- **Responsible agent type:** Architect, with a GOV-016 **market-data advisory**
  temporary specialist under the Architect.
- **DoR note:** Becomes Ready upon human roadmap approval (GOV-013); freeze status set.

## Ticket (e) — Market-data ingestion & storage service  ·  **blocked: freeze**

- **Title:** Market-data ingestion & storage service (implementation)
- **Epic:** `epic: market-data-foundation`
- **Phase:** 1 — Market-data foundation
- **Context:** Implements the provider-agnostic `data/` layer (architecture §3.2):
  adjusted daily OHLCV + point-in-time 4UR4 US Large-Cap 500 membership behind an
  internal contract,
  owning adjustment policy and provenance tagging. **Product code — cannot start
  until a human selects a provider (HD-06/HD-07) and lifts the freeze per-scope
  ([GOV-015](../../governance/build-freeze.md)).**
- **Scope (in-scope):** The `data/` interface, one concrete adapter for the
  human-selected provider, normalization (adjustment policy per HD-01), provenance/
  snapshot tagging, and data-quality checks (gaps, split sanity, duplicate bars).
- **Non-goals (out-of-scope):** Choosing a provider; multi-provider failover;
  intraday/real-time feeds; the engine (ticket f); sentiment ingestion.
- **Acceptance criteria (testable):**
  - [ ] `data/` interface returns adjusted daily OHLCV and point-in-time 4UR4 US
        Large-Cap 500 membership.
  - [ ] One adapter implements the interface for the approved provider.
  - [ ] Adjustment policy matches HD-01; provenance/snapshot stored per bar.
  - [ ] Data-quality checks flag (not silently pass) gaps/split anomalies/duplicates.
  - [ ] Tests pass from a clean checkout; CI green.
- **Dependencies:** **Freeze lift (per-scope)**; **HD-01**, **HD-06**, **HD-07**;
  tickets (c) and (d) research complete; architecture §3.2, §5, §6.1.
- **Evidence plan (GOV-006):** Ticket branch + PR linked to the issue; passing
  ingestion tests + CI run link; a worked split/symbol-change example; a stored
  provenance record; Verification verdict + Code Review approval.
- **Autonomy level:** blocked (build-freeze).
- **Responsible agent type:** Implementation Engineer (inactive under freeze),
  supported by the Architect and a GOV-016 **market-data advisory** specialist.
- **DoR note:** Becomes Ready upon human roadmap approval (GOV-013); freeze status
  set — stays **blocked: freeze** until a human lifts the freeze for this scope.

## Ticket (f) — Deterministic trendline detection engine  ·  **NOT Ready** (freeze lifted for `engine/`; entry criteria open)

- **Title:** Deterministic trendline detection engine implementing the spec (implementation)
- **Epic:** `epic: trendline-detection-engine`
- **Phase:** 2 — Trendline detection engine
- **Context:** Implements the pure, deterministic `engine/` core (architecture
  §3.1) per the trendline spec: ATH anchoring, pivot detection, envelope selection,
  log-space line fit, and the ACTIVE-side state machine with reason codes.
  **Product code. The freeze for this scope IS lifted** — HD-22 /
  [#31](https://github.com/tomerYannay/4UR4/issues/31), `scope: ["engine/"]`
  ([GOV-015](../../governance/build-freeze.md)) — **and the ticket is still not Ready; see
  the DoR note and the deviation below.**
- **Scope (in-scope):** ATH anchoring (§4), pivot rule (§5), envelope/upper-log-hull
  selection (§6, §8), log-space slope/intercept/line (§3, §7), edge-case handling
  and reason codes (§10, §18), and the ACTIVE-side transitions to WICK_BREAK/NONE
  needed to reproduce the geometry fixtures. Named, versioned config (§20).
- **Non-goals (out-of-scope):** Breakout/retest/expiry engine (**ticket (g)**, Phase 3);
  confidence scoring; data ingestion (ticket e); any I/O in the engine
  (pure core); sentiment.
- **Acceptance criteria (testable):**
  - [ ] **The engine satisfies the Phase-2 exit criteria in [`roadmap.md`](../roadmap.md)
        as written there.** *No fixture list is restated in this ticket.* The gate is the
        roadmap's **derived** one — every fixture directory under
        `product/fixtures/golden/`, with "wholly Phase 2" selected by the predicate
        `confirmed_bar == null` evaluated against the committed `expected.json` files at
        gate time — **plus RM-01**. Adding a fixture therefore tightens this ticket
        automatically. *(This criterion previously named seven fixture IDs —
        `GX-01, 02, 06, 08, 09, 10, 12` — against what is now a **23**-fixture derived
        gate. Restating a list here is the drift class
        [#19](https://github.com/tomerYannay/4UR4/issues/19) was opened for;
        **deferring to the derived source is the #19 remedy**, and the list is removed
        rather than re-typed so it cannot drift again.)*
  - [ ] **E2-AUTHOR-A, as a testable property of the delivered artifact:** the committed
        `engine/` **does not import, copy, execute or mechanically translate**
        `tools/fixture-replay.mjs` or any successor reference model under `tools/`.
        Mechanically checked by an architecture test that **derives** the forbidden set
        rather than naming it and carries its own **anti-vacuity** assertion, executed by
        CI on every PR. Agreement with the reference model **earns no credit**
        (HD-15 condition 1).
  - [ ] Every accept/reject/transition emits the spec's named reason code, from the
        schema's **closed** set.
  - [ ] Determinism guard: same input scored twice → byte-identical output; and no
        look-ahead (prefix-truncation invariance).
  - [ ] All tolerances/constants are named, versioned config (no magic numbers).
  - [ ] Output carries `spec_version`; tests pass from a clean checkout; CI green.
  - [ ] **No fixture, `expected.json`, `annotation.json` or parameter is edited to make
        the engine pass** (HD-22 — a ticket acceptance criterion, not advice). A
        disagreement between the engine and a committed fixture is **escalated, never
        reconciled**.
- **Author-facing brief (E2-AUTHOR-B — the must-not-read set), from
  [`phase2-independence-mechanism.md`](../../docs/architecture/phase2-independence-mechanism.md)
  §10, which requires the ticket to carry it:** *Author `engine/` from
  `product/trendline-specification.md`, `product/fixtures/golden/**` and
  `product/fixtures/real/**` only (the `real/**` permission is SPR-D-03).
  `tools/fixture-replay.mjs`, any successor model under `tools/`,
  `product/fixtures/VERIFICATION.md` and
  `docs/architecture/phase2-independence-mechanism.md` are quarantined: you work in a
  checkout that does not contain them, you must not retrieve them from git history, the
  network or another agent, and if any of their content reaches you by any route —
  including from a human — stop and report it. This is not a trust question; reporting it
  costs nothing and concealing it voids the phase gate. The engine must not import, copy,
  execute or mechanically translate any of them. If the specification and any other
  artifact disagree, the specification governs and the disagreement is filed as a defect
  report.*
- **Dependencies:** ticket (a) fixtures approved; **HD-01**, **HD-02**; trendline spec
  §3–§10, §18, §20; **HD-22**'s `engine/` scope lift. (Uses fixture bars, so it does not
  strictly require ticket (e).) **Still open beneath this ticket:**
  [#20](https://github.com/tomerYannay/4UR4/issues/20) (Phase-2 entry), with
  [#21](https://github.com/tomerYannay/4UR4/issues/21) beneath it, and full branch
  protection on `main`.
- **Evidence plan (GOV-006):** Ticket branch + PR linked to the issue; passing
  fixture + determinism tests with CI run link; a reason-code coverage report;
  Verification verdict + Code Review approval.
- **Autonomy level:** implementation, inside the **HD-22 `engine/` scope lift**.
- **Responsible agent type:** Implementation Engineer, supported by the Architect and a
  GOV-016 **trendline-math advisory** specialist.
- **DoR note — CORRECTED.** This note previously read *"stays **blocked: freeze** until a
  human lifts the freeze for this scope."* **That is no longer true and was stale:**
  [HD-22](../human-decisions.md) (Product Owner, 2026-07-26,
  [#31](https://github.com/tomerYannay/4UR4/issues/31)) **lifted GOV-015 for `engine/`**,
  with `scope: ["engine/"]` in the machine-readable freeze marker. **The freeze is not what
  holds this ticket.** What holds it is the **Definition of Ready** (GOV-004) and Phase-2
  **entry**: [#20](https://github.com/tomerYannay/4UR4/issues/20) is open, with
  [#21](https://github.com/tomerYannay/4UR4/issues/21) beneath it, and full branch
  protection on `main` is a stated Product Owner precondition on merging Phase-2 product
  code. **The ticket is therefore NOT Ready — for a different reason than before, and the
  reason is now stated correctly.**
- **DEVIATION ON THE RECORD — the engine was built before this ticket reached Ready.**
  `engine/` exists and passes its suite; this ticket never reached **Ready**. That is a
  real process deviation, and **E2-AUTHOR criterion 2** — *"the Ready ticket carries both
  halves"* — is therefore **genuinely UNMET**, not met-late.
  - **#7 has NOT been backdated to Ready, and must not be.** Marking it Ready now would
    make the record fit the outcome, which is the precise failure the whole fixture and
    governance corpus exists to catch. The acceptance criteria and author brief added above
    are **the missing content, supplied late and disclosed as late** — they do not
    retroactively satisfy criterion 2, and nothing in this file should be read as claiming
    they do.
  - **Where the disclosure of record lives:**
    [`../../docs/architecture/phase2-independence-attestation.md`](../../docs/architecture/phase2-independence-attestation.md)
    §9 (criterion table, row 2) and §4 (the two-author disclosure for `engine/`, including
    the **ABSENT** E2-AUTHOR-B record for commit `7ab8075`), plus
    [`../maintenance-backlog.md`](../maintenance-backlog.md) **M-35**.
  - **Only a human may dispose of this deviation.** An agent may record it; none may waive
    it (GOV-013).

## Ticket (g) — Breakout, freeze, retest, failure & expiry engine  ·  **READY** (2026-07-28)

> **THE PHASE-3 FREEZE LIFT EXISTS AND THIS TICKET IS NOW READY — in that order, and the
> order is the whole point.**
>
> **Ready as of 2026-07-28, on a DoR re-assessed FORWARD.** Element 7 failed on two
> independent grounds and **both were closed on their merits before this line was written**:
> the four specification escalations are **ruled** — ESC-1, ESC-3 and ESC-5(a) by the Product
> Steward, **ESC-4 by the Product Owner as [HD-25](../human-decisions.md)** — together with
> normative dispositions for the six Steward-owned OQ-P3 rows, all recorded at
> [`../trendline-specification.md`](../trendline-specification.md) **§22**; and the **Phase 2
> exit determination** is made at [`../project-state.md`](../project-state.md)
> (`CLOSED_ON_AUTHORITY`, `clean_gate_pass: false`). **Nothing was backdated and nothing was
> flipped to make an external record read true** — which was the live risk here, named in the
> superseded banner below and still worth naming.
>
> **Superseded, retained: this banner previously read "THE PHASE-3 FREEZE LIFT NOW EXISTS, AND
> THIS TICKET IS STILL NOT READY."** True when written; superseded by the two closures above,
> not by a reassessment of the same evidence.
>
> **Superseded, and kept legible rather than deleted.** This banner previously read: *"THIS
> TICKET IS NOT A FREEZE LIFT AND MUST NOT BE READ AS ONE. It is `blocked: freeze` … and no
> Phase 3 lift exists."* **A Phase-3 lift now exists** — [HD-24](../human-decisions.md) §3,
> Product Owner, 2026-07-28, [#39](https://github.com/tomerYannay/4UR4/issues/39) — so
> `blocked: freeze` is removed **because HD-24 §3 lifts it**, and for no other reason.
>
> **What has NOT changed:** [GOV-015](../../governance/build-freeze.md) **rule 4** requires a
> lift to attach to *"a specific **approved, Ready** ticket — never a blanket 'autonomy on'"*.
> **HD-24 §3 asserted that attaching to this ticket satisfied rule 4. It did not** — at that
> head this ticket was `blocked: freeze` and expressly not Ready, so it met *specific* and
> failed *approved* and *Ready*. The repair is **forward**: the DoR below is re-assessed
> **dated 2026-07-28**, element by element, against the state that exists now.
>
> **This ticket was NOT BACKDATED to Ready.** The Phase-2 record carries the identical failure
> as a deviation — *"**#7 has NOT been backdated to Ready.** Fitting the record to the outcome
> is the failure this corpus exists to catch"* — and flipping this ticket to Ready would have
> made HD-24 §3 read true by editing the ticket instead of by finishing the work. **The work
> was finished instead**, in a change that touches no `engine/` file, and the assessment
> below is dated **2026-07-28 forward**. The Ready date is the date of the assessment, **not**
> the date of HD-24 §3, and rule 4 became true on the later date.

- **Title:** Deterministic trendline engine — confirmed breakout, line freezing (`Λ^F`),
  retest, failed breakout, expiry/recompute (implementation)
- **Epic:** `epic: trendline-detection-engine`
- **Phase:** 3 — Breakout & retest engine
- **Context:** Phase 2 stops the engine at the §13.1 predicate and deliberately names the
  stop a *stop*, not `Λ^F`. Phase 3 turns that stop into a transition and adds the four
  post-breakout behaviours the roadmap's **behavioural Phase 2 / Phase 3 boundary rule**
  assigns to it. The Architect has produced a full implementation plan for this ticket —
  **design only; it builds nothing and authorizes nothing** (GOV-015 rule 3: *the Architect
  may design but not build*). **The plan is committed:**
  [`../../docs/architecture/phase3-implementation-plan.md`](../../docs/architecture/phase3-implementation-plan.md).
  Its byte-exact copy and the sha256 that evidences it are recorded at
  [`../maintenance-backlog.md`](../maintenance-backlog.md) **M-51**. *Correction, recorded
  rather than overwritten: until the plan landed, this sentence read "**It is NOT YET in the
  repository**" and cited **M-48** — the first half went stale when the plan was committed,
  and the citation was wrong from the start, since M-48 is the bash-guard over-block row and
  has nothing to do with the plan.* Everything this ticket states about the plan's findings is
  restated here, so the ticket stands on its own if the plan is lost.
- **Scope (in-scope):** confirmed breakout (§13.2) · line freezing `Λ^F` (§21.5) · retest
  (§16) · failed breakout (§15) · expiry and recompute (§17) · the §15/§16/§17 parameters
  as named, versioned config. **`engine/` only.**
- **Non-goals (out-of-scope):** confidence/quality scoring and `flags` (`LOW_VOLUME`,
  `NOT_RETESTED` are confidence-layer surface — §13.3, §13.4) · §12 touch counting · data
  ingestion · any directory other than `engine/` · any new executable tool · **any fixture
  edit**.
- **Acceptance criteria (testable):**
  - [ ] **The engine satisfies the Phase-3 exit criteria in [`roadmap.md`](../roadmap.md)
        as written there.** *No fixture list is restated in this ticket* — the roadmap
        states the gate as "**every** fixture directory under `product/fixtures/golden/`
        **in full and exactly** … with no fixture named or exempted here", and that is the
        criterion. **Deferring to the derived source is the
        [#19](https://github.com/tomerYannay/4UR4/issues/19) remedy;** a restated list is
        the drift #19 was opened for.
  - [ ] **The conformance target is larger than the seven fixtures with a non-null
        `confirmed_bar`, and it too is stated by deferral, not by a list.**
        `causal_record.eps_break_robustness` records `final_state` at **every** sweep
        scale, and the Phase-2 harness compares it **only when that point's
        `breakout_bar` is null** — so every sweep point whose recorded `final_state` is a
        Phase-3 state is currently **unasserted**. The criterion is therefore: **remove
        that guard and compare `final_state` at every recorded sweep point of every
        fixture.** At the committed corpus that raises the count of asserted Phase-3
        outcomes from 7 to 10; **the number is derived from the robustness block, not
        pinned here**, so adding a fixture or a sweep scale tightens the gate
        automatically. *(For a reviewer: the three that the guard currently hides are
        GX-12 at 0.5× and GX-15 at 0.5× and 0.8×. Named as an aid to review only —
        **hard-coding them into this criterion would recreate the very drift it fixes.**)*
  - [ ] **E2-AUTHOR-A, as a testable property of the delivered artifact:** the committed
        `engine/` — including every module added by this ticket — **does not import, copy,
        execute or mechanically translate** `tools/fixture-replay.mjs` or any successor
        reference model under `tools/`. Checked by the architecture test that **derives**
        the forbidden sibling set and carries an **anti-vacuity** assertion, so a module
        added later is covered without an edit. Agreement with the reference model **earns
        no credit** (HD-15 condition 1).
  - [ ] **E2-AUTHOR-B — must-not-read, named:** `tools/fixture-replay.mjs` (the quarantined
        causal reference model) and any successor model under `tools/`, plus
        `product/fixtures/VERIFICATION.md` and
        `docs/architecture/phase2-independence-mechanism.md`. The ticket (f) author brief
        above applies verbatim to this ticket; **E2-AUTHOR continues to bind the authoring
        agent for the whole engine** (roadmap, Phase 3 entry criteria).
  - [ ] **No fixture, `expected.json`, `annotation.json` or parameter is edited** (HD-22).
        Every engine/fixture disagreement is **escalated, never reconciled** — see the
        escalations already lodged below.
  - [ ] Determinism and no-look-ahead guards extended to the new quantities: a mutation at
        any bar after the confirmed-breakout bar leaves the frozen line and the confirmed
        bar identical; the determinism digest covers the frozen line.
  - [ ] Full state machine and reason codes verified against the schema's **closed** code
        set; CI green.
  - [ ] **Explicitly-unasserted fixture keys are recorded against a declared allow-list —
        the OQ-P3-7 remedy.** The conformance harness MUST enumerate, for every fixture, each
        key present in the committed expectation that **no assertion reads**, and compare that
        set against an **allow-list declared alongside the harness**. **`flags`
        (`LOW_VOLUME`, `NOT_RETESTED`) is ON that list** — as an explicitly unasserted
        confidence-layer key (§13.3, §13.4), **not** as a key passed over in silence. A key
        that is unasserted and **not** on the allow-list **fails the run**. A key on the
        allow-list that has since become asserted, or that no longer appears in any fixture,
        **also fails**, so the list cannot rot into a blanket exemption. *Silence is the
        failure mode this criterion exists to remove: an unread key and a passing suite are
        indistinguishable without it.*
- **Escalations lodged by the Architect's plan — five (ESC-1…ESC-5) and eight open questions.
  ALL FIVE ARE NOW CLOSED, and the closing artifacts are named so a reader can check the
  claim rather than take it.** *(This heading previously read "**NONE is resolved by this
  ticket**", which remains true of *this ticket* — none was resolved **by** it; they were
  resolved **for** it, in a separate governed change, which is what HD-15 condition 3
  requires.)*

  | Escalation | Disposition | Closing artifact |
  |---|---|---|
  | **ESC-1** — §11 draws two expiry edges, GX-07 records one | **RULED** — one record, `EXPIRED_POST_BREAKOUT`; the `EXPIRED` enum member is reserved and unreachable | Product Steward, 2026-07-28 — [`../trendline-specification.md`](../trendline-specification.md) §11, §17, §22 |
  | **ESC-2** — the brief's parameter premise was wrong | **DISCHARGED, record-only** — corrected in this ticket's CORRECTION paragraph below | this file (pre-existing) |
  | **ESC-3** — the §15/§16 window right edges | **RULED** — half-open with inclusive right edges, and the reason no fixture can contradict is measured | Product Steward, 2026-07-28 — §15, §16, §22 |
  | **ESC-4** — is `FAILED_BREAKOUT` terminal against a new ATH | **RULED by the PRODUCT OWNER** — option C, both exits retained | **[HD-25](../human-decisions.md)**, 2026-07-28 — §11, §17, §21.5, §21.7, §22 |
  | **ESC-5(a)** — §16 needs `low`, §18 does not guard it | **RULED** — no fourth guard row; a missing `low` at a post-breakout predicate is a caller defect, not a reason code | Product Steward, 2026-07-28 — §18, §22 |
  | **ESC-5(b)** — *should* §18 gain that row | **DEFERRED**, and explicitly **NON-BLOCKING for DoR element 7** — it is not answerable from synthetic fixtures and belongs with the Phase-1 data layer | §18, §22 |
  | **OQ-P3-1 … OQ-P3-6** | **RULED** — normative dispositions, all six Steward-owned | Product Steward, 2026-07-28 — §16, §17, §21.4, §22 |
  | **OQ-P3-7** — `flags` produced by no engine layer | **Out of Phase-3 scope**; its remedy is an acceptance criterion of this ticket, above | this ticket |
  | **OQ-P3-8** — the `SPEC_VERSION` placeholder | **Consolidated into OQ-J** and **not blocking** — see the Dependencies below | §22.1 |

  The one with governance weight, retained in full because its disposition is the precedent:
  - **ESC-1 — a genuine specification/fixture divergence on expiry. This is a SPEC-DEFECT
    REPORT owed to the Product Steward, and it is recorded, not resolved.** Specification
    §11 draws expiry as **two** edges through a state named `EXPIRED`
    (`BROKEN_OUT`/`RETESTED` → `EXPIRED` → `NONE`); fixture **GX-07** records **one**
    transition (`bar 110: BROKEN_OUT → NONE / EXPIRED_POST_BREAKOUT`). **HD-22 forbids
    editing the fixture**, and the architecture test requires the engine's `LineState` set
    to **equal** the committed schema's closed set — so `LineState.EXPIRED` must **remain
    in the enum while being unreachable**, and that must be said in the code rather than
    left for a later reader to "fix" and break GX-07.
    **[HD-15](../human-decisions.md) condition 3 governs the disposition:** the
    **specification is authoritative**, and a divergence is *"a spec-defect report or a
    model bug — never resolved by copying the model"*. Therefore: **the specification is
    not amended in the same change as the engine**, and it is **not amended by this PR** —
    a spec amendment is a separate governed change. Two closes were available: amend §11 to
    draw **one** edge labelled `EXPIRED_POST_BREAKOUT`, **or** rule that `EXPIRED` is a
    transient state a conforming detector must record — in which case **GX-07 disagrees with
    the specification, and that disagreement is the escalation**, not something the engine may
    settle. **CLOSED 2026-07-28 on the FIRST**, by the Product Steward, in a change that
    touches no `engine/` file: §11 draws one edge, and `EXPIRED` stays in the schema's closed
    enum as a **reserved, unreachable** member that an implementation must name as such. The
    second was rejected because it would have put the specification in conflict with a fixture
    [HD-22](../human-decisions.md) forbids editing. **No behaviour change, so no Product Owner
    escalation was required** — the condition this ticket set for itself.
  - **ESC-2 … ESC-5 and OQ-P3-1 … OQ-P3-8** are carried in the plan with their owners
    (ESC-3 window right-edges, ESC-4 `FAILED_BREAKOUT` terminality against a new ATH,
    ESC-5 §16's `low` unguarded by §18 — Product Steward; ESC-2 a record-only correction).
    ~~**A Phase-3 lift should not be granted while ESC-1, ESC-3, ESC-4 and ESC-5 are
    open**~~ — **overtaken by events on 2026-07-28: the lift WAS granted, with all four still
    open** ([HD-24](../human-decisions.md) §3). This was an agent recommendation, not a
    condition anyone could impose on the Product Owner, and it is struck as a recommendation
    rather than restated as a breach. **Its reason survives the grant intact:** each of the
    four decides behaviour this ticket would otherwise choose by itself, so they blocked the
    ticket's **Definition of Ready** (element 7) instead of blocking the lift — and since rule
    4 wants a *Ready* ticket, the practical effect was the same. **All four are now ruled**
    (2026-07-28, table above), so the reason is discharged on its own terms rather than
    waived, and **implementation may begin.**
- **CORRECTION carried into this ticket rather than repeated as an error.** An earlier brief
  stated the six §15/§16/§17 parameters are *"not carried in any fixture's `params` block"*.
  **That was wrong** — it was generalised from a single fixture. Measured across the
  committed `expected.json` files: `eps_fail` and `F_fail` are carried by **GX-04, GX-05,
  GX-17**; `eps_retest`, `W_retest` and `h_hold` by **GX-04, GX-17**; `E_expiry` by
  **GX-07**. **Every carried value equals the specification default**, and the defaults
  reproduce all seven expected transition bars. **There is therefore NO parameter
  escalation, and none is recorded.** What the ticket requires instead is a **cross-check**:
  where a fixture carries one of the six, the engine reads it and asserts it equals the
  module default, so a future fixture carrying a non-default value fails loudly rather than
  being silently overridden.
- **Dependencies — restated 2026-07-28, one discharged and two still open.**
  - **A Phase-3 freeze lift — DISCHARGED.** [HD-24](../human-decisions.md) §3
    ([#39](https://github.com/tomerYannay/4UR4/issues/39)) grants it for `engine/`:
    `ACTIVE → BROKEN_OUT`, `Λ^F` freezing (§21.5), retest (§16), failed breakout (§15),
    expiry/recompute (§17). *(Previously read: "A Phase-3 freeze lift, which does not exist".)*
  - **Phase 2 exit met — DISCHARGED 2026-07-28.** The determination is made by the Product
    Steward at [`../project-state.md`](../project-state.md): **`phase_2_exit:
    CLOSED_ON_AUTHORITY`, `exit_criteria: MET`, `unmet_at_closure: [E2-AUTHOR-2]`,
    `met_by_ruling: [E2-AUTHOR-5]`, `clean_gate_pass: false`**, on the authority of
    [HD-24](../human-decisions.md) §4. **No agent other than the Product Steward may make it**
    — a [GOV-002](../../governance/roadmap-authority.md) call, on a gate assessment.
    *(Previously: "No agent has made the Phase-2 exit determination and none may; it is a
    GOV-002 call for the Product Steward" — which forbids to every agent what it then assigns
    to one of them. The Steward is an agent; the restriction is that no **other** agent may.)*
    **What is discharged is the determination, not the residue it discloses:** the phase closes
    **on authority, not on a clean gate pass**, E2-AUTHOR **criterion 2 is genuinely UNMET**
    (ticket (f)'s recorded deviation) and **criterion 5 is met by ruling** on an attestation
    that discloses its own gaps. **This entry must never be restated as "all criteria met."**
  - **The four specification escalations — DISCHARGED 2026-07-28.** ESC-1, ESC-3, ESC-4 and
    ESC-5, carried at [`../maintenance-backlog.md`](../maintenance-backlog.md) **M-50**, are
    ruled — see the table above and
    [`../trendline-specification.md`](../trendline-specification.md) §22. **ESC-5(b)** remains
    **deferred and is explicitly non-blocking for element 7.**
  - **D5 differential-probe custody — OPEN, owner VERIFICATION, and NOT Ready-blocking.** The
    Phase-2 independence attestation
    ([`../../docs/architecture/phase2-independence-attestation.md`](../../docs/architecture/phase2-independence-attestation.md)
    §5) records D5 as *"NOT APPLICABLE AT PHASE 2 — by design, not by omission"* and states
    that it **becomes a real signal at the Phase-3 gate**, in one specific form — **sealed,
    spec-derived, verifier-held differential probes** — which
    [`../../docs/architecture/phase2-independence-mechanism.md`](../../docs/architecture/phase2-independence-mechanism.md)
    **AC-7** assigns to **Verification**. **No such probe is in custody today**, and the
    attestation itself names that a **Phase-3 entry gap**, recorded there so it is not
    discovered at the gate. **Why it does not block element 7, ruled explicitly:** it is a
    **gate obligation on Verification**, not an open scope question the implementer would
    otherwise settle alone — the implementer builds nothing differently whether the probes
    exist or not, and cannot build them, since a probe held by the party it tests is not a
    probe. It is therefore an **addressed** dependency — named, owned, and dated to the gate —
    which is what element 7 asks, and it is **not discharged**. **Verification must hold the
    probes before the Phase-3 exit gate can pass**, and this ticket's Done evidence cannot be
    complete without them.
  - **OQ-J — the `SPEC_VERSION` value — OPEN, owner Product Steward, NOT blocking.**
    **OQ-P3-8** and [`../maintenance-backlog.md`](../maintenance-backlog.md) **M-34** are the
    same question in two other registers and are **consolidated into OQ-J**; they are
    cross-references, not separately owed decisions. **The versioning constraint is ruled**
    at [`../trendline-specification.md`](../trendline-specification.md) **§22.1**: the §22
    amendment is normative specification content, so it **must not land as a silent edit to an
    unversioned document** — which requires (i) the dated, enumerated amendment record §22 is,
    and (ii) a real `spec_version` minted **before any engine pins one**, in a change that can
    move the specification header, the engine's `SPEC_VERSION` and the value fixtures record
    **together**. A document-only change cannot mint it, which is why it is not minted here.
    **Not blocking:** no Phase-3 behaviour depends on the identifier, and the placeholder
    `"UNVERSIONED-PENDING-OQ-J"` is honest about being one.
  - **Unchanged and satisfied:** **HD-03**; **HD-12**; **[HD-25](../human-decisions.md)**;
    trendline spec §11, §13–§18, §21 **and the §22 amendment record**. Phase-2 **E2-AUTHOR**
    continues to bind for the whole engine.
- **Evidence plan (GOV-006):** Ticket branch + PR linked to the issue; the full-corpus
  conformance run with every fixture compared in full and in both directions; the sweep
  `final_state` comparison at every recorded scale; determinism and no-look-ahead runs;
  a reason-code coverage report counted **by emission, not by grepping source**; CI green;
  Verification verdict + Code Review approval.
- **Autonomy level:** implementation, inside the **HD-24 §3 Phase-3 `engine/` lift**. **No new
  or widened GOV-015 scope is requested or implied**, and the lift was never by itself
  permission to start — rule 4 wants a Ready ticket, and **as of 2026-07-28 it has one**.
  *(Previously: "blocked (build-freeze)", then "rule 4 still wants a Ready ticket".)*
- **Responsible agent type:** Implementation Engineer, supported by the Architect. *(The
  Engineer is no longer inactive for this scope; [GOV-015](../../governance/build-freeze.md)
  rule 3's inactivity attaches to frozen scopes, and this one is lifted.)*
- **DoR note — RE-ASSESSED FORWARD, 2026-07-28 (second assessment of that date). VERDICT:
  READY (8 of 8 elements met).** Assessed against
  [GOV-004](../../governance/definition-of-ready.md) element by element, against the state of
  the repository **after** the ten Phase-3 dispositions and the Phase 2 exit determination
  landed. **Nothing here is backdated**, and the earlier assessment — the one that returned
  **NOT READY** on the same date, before those two closures — is quoted below rather than
  overwritten. **Two assessments, two different states of the repository, in that order.**

  | # | [GOV-004](../../governance/definition-of-ready.md) element | Verdict | How it was checked |
  |---|---|---|---|
  | 1 | Traces to an approved roadmap item (GOV-002) | **MET** | [`roadmap.md`](../roadmap.md) **Phase 3 — Breakout & retest engine** is an existing phase of the Phase 0–9 baseline **approved** under GOV-013 as **HD-16** ([#23](https://github.com/tomerYannay/4UR4/issues/23)). This ticket adds no scope to it; the roadmap is not edited by this change |
  | 2 | States user/business value and a success measure | **MET** | **Value:** Phase 2 stops the engine at the §13.1 predicate and calls the stop a *stop*; this ticket turns it into a transition and adds the four post-breakout behaviours — i.e. it is what makes the product *fire and then follow* rather than only draw. **Success measure:** the derived Phase-3 exit gate, plus the sweep comparison that raises asserted Phase-3 outcomes from **7** to **10** at the committed corpus. Both are counted from artifacts, not asserted |
  | 3 | Explicit, testable acceptance criteria | **MET** | **Eight** criteria above — seven, plus the **OQ-P3-7 remedy** added 2026-07-28 *(the cell read "Seven" before that criterion existed; recounted, not restated)* — each either mechanically checked or stated by **deferral to a derived source** rather than by a restated list, the [#19](https://github.com/tomerYannay/4UR4/issues/19) remedy. E2-AUTHOR-A carries its own anti-vacuity assertion, and the OQ-P3-7 criterion carries its own: an allow-list that has gone stale in either direction fails the run |
  | 4 | Bounded — completable and verifiable in one flow | **MET, with the reservation stated and now heavier** | The Architect's plan bounds the delta at **one new module (`engine/frozen.py`, ~120 lines) plus edits to twelve existing files** — counted from the plan's own delta table ([`../../docs/architecture/phase3-implementation-plan.md`](../../docs/architecture/phase3-implementation-plan.md) §0), whose **ten** `edit` rows name **twelve** files because one row carries three test modules. *(This cell previously read **"plus edits to five existing ones"** — not the plan's number, and understated the very quantity this element assesses. Corrected 2026-07-28; found by Code Review.)* It is still **one verifiable outcome** — the Phase-3 exit gate — and splitting it would split that gate, which is the thing GOV-008 rule 4 exists to keep whole. **The reservation, restated against the true number:** five behaviours across thirteen files is the largest unit this file has ever called bounded, and if the flow does not complete in one pass the Steward splits it rather than letting it expand |
  | 5 | Uses defined glossary terms; new terms added | **MET** | Checked term by term against [`../glossary.md`](../glossary.md): *Confirmed breakout*, *Breakout bar / confirmed bar*, *Failed breakout*, *Retest hold*, *Line expiry / reset*, *Line state machine*, *Frozen event line (`Λ^F`)*, *As-of-time (rolling causal) evaluation*, *Available prefix (`S_t`)*, *Active line at bar `t`*. **All present. No new term is introduced by this ticket**, so none needs adding |
  | 6 | Names required evidence for Done (GOV-006) | **MET** | The evidence plan above names the full-corpus conformance run compared in both directions, the sweep `final_state` comparison at every recorded scale, determinism and no-look-ahead runs, a reason-code report counted **by emission rather than by grepping source**, CI green, and both gate verdicts |
  | 7 | **No unaddressed dependency or open scope question** | **MET — both grounds closed 2026-07-28, and this is the element that changed** | **(a) The four specification escalations are RULED**, in a separate governed change touching no `engine/` file (**HD-15** condition 3): **ESC-1** and **ESC-3** and **ESC-5(a)** by the Product Steward, **ESC-4** by the Product Owner as **[HD-25](../human-decisions.md)**, plus normative dispositions for the six Steward-owned **OQ-P3** rows — [`../trendline-specification.md`](../trendline-specification.md) **§22**. **(b) The Phase 2 exit determination is MADE** — [`../project-state.md`](../project-state.md), `CLOSED_ON_AUTHORITY`, `clean_gate_pass: false` — which satisfies the roadmap's Phase 3 entry criterion. **Three items remain open and each is ruled non-blocking on its own stated ground, not by omission:** **ESC-5(b)** (deferred; not answerable from synthetic fixtures, and (a) is complete without it) · **D5 probe custody** (a gate obligation on **Verification**, addressed and dated, not a scope question the implementer would settle) · **OQ-J** (the `SPEC_VERSION` value; no Phase-3 behaviour depends on it and a document-only change cannot mint it). See Dependencies |
  | 8 | Respects the build-freeze (GOV-015) | **MET — newly, and this is the element HD-24 §3 changed** | `blocked: freeze` is removed **because [HD-24](../human-decisions.md) §3 lifts GOV-015 for Phase 3 inside `engine/`**, and for no other reason. The freeze marker's `scope` stays `["engine/"]` because the directory is unchanged; the phase distinction lives in `build-freeze.md`'s prose and **not** in the machine check |

  **What had to happen before this ticket could become Ready — both done, 2026-07-28, and the
  path is recorded as it was actually walked:** **(i)** the Product Steward ruled **ESC-1,
  ESC-3 and ESC-5(a)** and gave the six Steward-owned **OQ-P3** rows normative dispositions,
  **escalating ESC-4 to the Product Owner because its close IS a behaviour change** — ruled as
  **[HD-25](../human-decisions.md)** — all **as a separate governed change**, since HD-15
  condition 3 forbids amending the specification in the same change as the engine; and
  **(ii)** the Product Steward made the **Phase 2 exit determination** under GOV-002.
  **Neither was done quickly to unblock something**: ESC-1 and ESC-5(a) were closed on the
  reading that moves no committed expectation, ESC-3 and the OQ-P3 rows on measurements that
  show the corpus cannot distinguish the readings, ESC-4 by the only party who may change
  behaviour, and the exit determination with `clean_gate_pass: false` on its face.

  **What Ready does NOT mean here, stated because this ticket's history invites the
  misreading:** it does not mean Phase 2 was clean (it closed **on authority**), it does not
  mean the escalation residue is empty (ESC-5(b), D5 custody and OQ-J are open and each is
  ruled non-blocking for a stated reason), and it does not mean the work has started —
  [GOV-008](../../governance/ticket-hygiene.md) rule 1 governs that, and the WIP table at the
  top of this file is where it is assessed.

  **Superseded note, retained verbatim.** *"**NOT Ready. `blocked: freeze`, and deliberately
  so.** [GOV-015](../../governance/build-freeze.md) **rule 4** requires a lift to be
  per-scope, tied to a specific approved, Ready ticket — never a blanket 'autonomy on'. **No
  Phase-3 lift exists**; the freeze marker's `scope` is `["engine/"]` granted for **Phase 2**
  (HD-22 enumerates what is authorized inside `engine/` and the Phase-3 behaviours are not
  among them). This ticket exists so that a Phase-3 lift **has a specific ticket to attach
  to** rather than being granted as a directory-wide blank cheque — that is **Part A of
  [#36](https://github.com/tomerYannay/4UR4/issues/36)**. It also does not yet meet GOV-004 on
  its own terms: four open escalations are unaddressed scope questions."* **The first half was
  superseded by HD-24 §3 on 2026-07-28; the last sentence was superseded later the same day,
  by the four escalations being ruled — see the escalation table above. #36 Part A is
  answered — the lift was granted.**

## Ticket (h) — Phase-2 engine hardening: close the measured vacuous-test gap  ·  **Delivered and merged**

- **Title:** Engine hardening — unify the domination range, restore the pinned comparison,
  close the M-28 coverage gap (implementation)
- **Epic:** `epic: trendline-detection-engine`
- **Phase:** 2 — Trendline detection engine (**inside the existing HD-22 `engine/` lift**;
  no new or widened scope)
- **Context:** The Phase-2 engine is committed and green, and two gate reviews found defects
  in it that are **not** cosmetic. This ticket is the one that fixes them. It is **in
  flight** on branch `fix/m28-envelope-domination-coverage`.
- **Scope (in-scope):** [`../maintenance-backlog.md`](../maintenance-backlog.md) **M-28**,
  **M-29**, **M-30**, **M-32**, all inside `engine/`:
  - **M-28 — a MEASURED vacuous-test gap, and the reason this ticket is Ready rather than
    backlogged.** `engine/envelope.py` holds **three** copies of the domination range (the
    `domination` tuple, the loop in `_is_envelope_valid`, and the loop in
    `envelope_violations`), and Code Review **measured** that the corpus does not pin its
    endpoint **at all**: mutating the range endpoint produces **0 test failures**, while
    passing a wrong anchor produces **10**. A test suite that cannot fail on a real mutation
    is not evidence, and *"causes tests to pass vacuously"* is on the fix-immediately list.
  - **M-29** — `_is_envelope_valid` inlines the pinned comparison instead of calling
    `logspace.exceeds()`, whose docstring claims to be the only site of that form: **the
    same defect class `envelope.py` just fixed**, and explicitly **not** to be triaged as
    cosmetic.
  - **M-30** — `_alternative_select` in `engine/tests/test_mutations.py` still uses the
    forbidden `if worst > eps: continue` form, and the adversarial test compares its output
    directly against the engine's now-pinned predicate. Last surviving instance in
    `engine/`.
  - **M-32** — `prefix` is the sole unannotated parameter in an otherwise fully annotated
    module.
- **Non-goals (out-of-scope):** any Phase-3 behaviour (ticket g) · any fixture change ·
  anything outside `engine/` · new features of any kind.
- **Acceptance criteria (testable):**
  - [ ] The domination range has **one** definition in `engine/envelope.py`; the two loops
        consume it rather than restating it.
  - [ ] **The M-28 gap is closed by a test that fails on the mutation that currently passes**
        — mutating the domination-range endpoint produces **> 0** failures, demonstrated by
        running the mutation, not asserted. *This is the ticket's success measure.*
  - [ ] `_is_envelope_valid` and `envelope_violations` call the pinned `logspace` form; no
        inlined copy of it remains in `engine/`.
  - [ ] The forbidden comparison form no longer appears anywhere in `engine/`, tests
        included.
  - [ ] `engine/envelope.py` is fully annotated.
  - [ ] **All 23 golden fixtures and RM-01 still pass, byte-identically** — this is
        behaviour-neutral refactoring plus new tests; a changed expectation means the
        refactor changed behaviour and must be escalated, not accepted.
  - [ ] **No fixture, `expected.json`, `annotation.json` or parameter is edited** (HD-22).
        Note for the author: a change under `product/fixtures/` travelling in the same PR as
        an `engine/` change trips the CI fixture-immutability guard — land any such change
        separately.
  - [ ] CI green from a clean checkout.
- **Dependencies:** none open. The freeze is already lifted for this scope (**HD-22**);
  the roadmap item is approved (**HD-16**); the defects are recorded and measured.
- **Evidence plan (GOV-006):** Ticket branch + PR linked to the issue; the mutation
  transcript showing the endpoint mutation failing tests **after** the fix and the recorded
  0-failure baseline **before** it; the unchanged 23+RM-01 conformance run; CI run link;
  Verification verdict + Code Review approval.
- **Autonomy level:** implementation, inside the existing HD-22 `engine/` lift. **No new or
  widened GOV-015 scope is requested or implied.**
- **Responsible agent type:** Implementation Engineer, supported by Code Review.
- **DoR note — Ready, and here is the checklist ([GOV-004](../../governance/definition-of-ready.md)):**
  traces to an approved roadmap item (Phase 2, HD-16) ✓ · states value and a success measure
  (the M-28 mutation must fail a test) ✓ · explicit testable acceptance criteria ✓ ·
  bounded — one module plus its tests ✓ · uses defined glossary terms ✓ · names its Done
  evidence ✓ · **no unaddressed dependency or open scope question** ✓ · respects
  GOV-015 — the scope is already lifted, so nothing here is `blocked: freeze` ✓.
  **Superseded by delivery, 2026-07-28:** this read *"It is Ready and in progress, so it
  consumes none of the GOV-008 'open unstarted Ready' budget."* **It is now delivered and
  merged** — [PR #37](https://github.com/tomerYannay/4UR4/pull/37) at `c66fd294`, 4 files, all
  `engine/`, 141 tests ([`../project-state.md`](../project-state.md)) — so it consumes
  **neither** budget: not rule 2 (never unstarted-Ready) and **no longer rule 1**, which is
  what frees the slot ticket (g) needs. **Whether it is DONE under
  [GOV-005](../../governance/definition-of-done.md) is not stated here**: that is Verification's
  and Release & Ops' determination, and the Product Steward does not make it.

---

*The build-freeze ([GOV-015](../../governance/build-freeze.md)) **remains ON**, with **two**
scopes lifted, both inside `engine/` — **Phase 2** (HD-22, 2026-07-26) and **Phase 3**
([HD-24](../human-decisions.md) §3, 2026-07-28). The marker's `scope` is `["engine/"]` for
both, because the directory is the same one; **the validator cannot tell the two apart**, and
`build-freeze.md` says so rather than leaving it to be discovered. Implementation ticket
**(e)** stays `blocked: freeze` — no lift covers ingestion. **(g)** is **no longer
freeze-blocked and, as of 2026-07-28, is READY**: DoR element 7's two grounds are closed —
ESC-1/3/4/5 ruled (ESC-4 by the Product Owner as [HD-25](../human-decisions.md)) and the
Phase-2 exit determination made — so **rule 4 is satisfied and Phase-3 implementation may
begin**, WIP permitting. **(f)** is not freeze-blocked and is not Ready either: its
Phase-2 entry criteria are open, and the deviation recorded under it — the engine was built
before the ticket reached Ready — stands unresolved and has **not** been backdated away.
**(h)** was Ready inside the Phase-2 lift, asked for no new scope, and is **delivered and
merged**. **(g) was not made Ready to make an external record read true** — the two grounds
were closed first, on their merits, in a change that touches no `engine/` file; **and (f) has
not been made Ready at all.***
