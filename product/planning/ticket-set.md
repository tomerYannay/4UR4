# 4UR4 — Ticket Definitions (first three phases)

Status: planning artifact under [GOV-015](../../governance/build-freeze.md); these
are **ticket DEFINITIONS for the human/primary session to create as GitHub
issues**, not tickets yet, and not approved.

> **Hygiene ([GOV-008](../../governance/ticket-hygiene.md)):** at most 3 epics
> (labels only — no umbrella issues); at most 5 open **unstarted Ready** tickets;
> one ticket = one verifiable outcome; no speculative implementation backlog.
> Implementation tickets are `blocked: freeze`.
>
> **DoR ([GOV-004](../../governance/definition-of-ready.md)):** every ticket below
> "Becomes Ready upon human roadmap approval ([GOV-013](../../governance/approval-gate.md));
> freeze status set." Research/design tickets are **Ready-eligible-now** (permitted
> under freeze); implementation tickets are **blocked: freeze** until a human lifts
> the freeze per-scope.

## Epic labels (3) — labels only, NOT issues

1. **`epic: product-quant-spec`** — "Product & Quant Specification" (Phase 0).
2. **`epic: market-data-foundation`** — "Market Data Foundation" (Phase 1).
3. **`epic: trendline-detection-engine`** — "Trendline Detection Engine" (Phase 2).

## Summary

| # | Ticket | Epic | Phase | Autonomy | Ready status |
|---|--------|------|-------|----------|--------------|
| a | Golden-example fixture set: trendline geometry & selection | product-quant-spec | 0 | design-only (freeze-permitted) | Ready-eligible-now |
| b | Acceptance-example set: breakout / retest / expiry | product-quant-spec | 0 | design-only (freeze-permitted) | Ready-eligible-now |
| c | Data-provider research & recommendation | market-data-foundation | 1 | research-only (freeze-permitted) | Ready-eligible-now |
| d | Survivorship-free constituents + corporate-actions research | market-data-foundation | 1 | research-only (freeze-permitted) | Ready-eligible-now |
| e | Market-data ingestion & storage service | market-data-foundation | 1 | blocked (build-freeze) | blocked: freeze |
| f | Deterministic trendline detection engine | trendline-detection-engine | 2 | blocked (build-freeze) | blocked: freeze |

**Totals:** 6 tickets defined · **4 Ready-eligible-now** (a, b, c, d) ·
**2 blocked: freeze** (e, f). Ready-eligible count (4) ≤ 5 budget ✓; total (6) ✓;
3 epics ✓; no umbrella issues ✓.

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

- **Title:** Survivorship-bias-free S&P 500 constituents + delisted history research (research only)
- **Epic:** `epic: market-data-foundation`
- **Phase:** 1 — Market-data foundation
- **Context:** Correct backtests require point-in-time S&P 500 membership and
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
  adjusted daily OHLCV + point-in-time constituents behind an internal contract,
  owning adjustment policy and provenance tagging. **Product code — cannot start
  until a human selects a provider (HD-06/HD-07) and lifts the freeze per-scope
  ([GOV-015](../../governance/build-freeze.md)).**
- **Scope (in-scope):** The `data/` interface, one concrete adapter for the
  human-selected provider, normalization (adjustment policy per HD-01), provenance/
  snapshot tagging, and data-quality checks (gaps, split sanity, duplicate bars).
- **Non-goals (out-of-scope):** Choosing a provider; multi-provider failover;
  intraday/real-time feeds; the engine (ticket f); sentiment ingestion.
- **Acceptance criteria (testable):**
  - [ ] `data/` interface returns adjusted daily OHLCV and point-in-time constituents.
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

## Ticket (f) — Deterministic trendline detection engine  ·  **blocked: freeze**

- **Title:** Deterministic trendline detection engine implementing the spec (implementation)
- **Epic:** `epic: trendline-detection-engine`
- **Phase:** 2 — Trendline detection engine
- **Context:** Implements the pure, deterministic `engine/` core (architecture
  §3.1) per the trendline spec: ATH anchoring, pivot detection, envelope selection,
  log-space line fit, and the ACTIVE-side state machine with reason codes.
  **Product code — cannot start until the freeze is lifted per-scope
  ([GOV-015](../../governance/build-freeze.md)).**
- **Scope (in-scope):** ATH anchoring (§4), pivot rule (§5), envelope/upper-log-hull
  selection (§6, §8), log-space slope/intercept/line (§3, §7), edge-case handling
  and reason codes (§10, §18), and the ACTIVE-side transitions to WICK_BREAK/NONE
  needed to reproduce the geometry fixtures. Named, versioned config (§20).
- **Non-goals (out-of-scope):** Breakout/retest/expiry engine (a separate Phase 3
  ticket); confidence scoring; data ingestion (ticket e); any I/O in the engine
  (pure core); sentiment.
- **Acceptance criteria (testable):**
  - [ ] Engine reproduces GX-01, GX-02, GX-06, GX-08, GX-09, GX-10, GX-12 exactly
        (to 6 sig figs) from ticket (a)'s fixtures.
  - [ ] Every accept/reject/transition emits the spec's named reason code.
  - [ ] Determinism guard: same input scored twice → byte-identical output.
  - [ ] All tolerances/constants are named, versioned config (no magic numbers).
  - [ ] Output carries `spec_version`; tests pass from a clean checkout; CI green.
- **Dependencies:** **Freeze lift (per-scope)**; ticket (a) fixtures approved;
  **HD-01**, **HD-02**; trendline spec §3–§10, §18, §20. (Uses fixture bars, so it
  does not strictly require ticket (e).)
- **Evidence plan (GOV-006):** Ticket branch + PR linked to the issue; passing
  fixture + determinism tests with CI run link; a reason-code coverage report;
  Verification verdict + Code Review approval.
- **Autonomy level:** blocked (build-freeze).
- **Responsible agent type:** Implementation Engineer (inactive under freeze),
  supported by the Architect and a GOV-016 **trendline-math advisory** specialist.
- **DoR note:** Becomes Ready upon human roadmap approval (GOV-013); freeze status
  set — stays **blocked: freeze** until a human lifts the freeze for this scope.

---

*These definitions are proposals pending human approval ([GOV-013](../../governance/approval-gate.md));
the build-freeze ([GOV-015](../../governance/build-freeze.md)) remains ON. Implementation
tickets (e, f) do not become Ready-to-start until a human lifts the freeze per-scope.*
