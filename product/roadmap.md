# 4UR4 Roadmap (governed) — **PROPOSED, pending human approval**

> **Authority:** Only the **Product Steward**, acting with explicit human
> approval, may add or reorder items here ([GOV-002](../governance/roadmap-authority.md)).
> The Product Innovation Agent may **never** write to this file
> ([GOV-003](../governance/roadmap-authority.md)). Any other agent editing this
> file is a governance violation the [Auditor](../.claude/agents/project-auditor.md) must flag.

> **STATUS: PROPOSED.** This is a **proposal** drafted for the product owner, not
> an approved commitment. The draft PR carrying this file is the approval request;
> until a human signs off ([GOV-013](../governance/approval-gate.md)) **no phase
> below is committed**. Phases 1+ involve product code and are **Blocked:
> build-freeze ([GOV-015](../governance/build-freeze.md))** — implementation
> begins only after a human lifts the freeze **per-scope**. Phase 0
> (specification, golden examples, research/design) is permitted context/design
> work under the freeze.

## Promotion path (how anything gets here)

```
Ideas Inbox  ──(human + Product Steward triage)──▶  Roadmap phases
             GOV-003 gate                            (this file)
```

An idea/phase becomes a **committed** roadmap item only after it has:
- a stated **user/business value** and a **success measure**,
- passed the [Product-Focus Guard](../governance/product-focus.md) (GOV-007),
- explicit **human sign-off** (GOV-013).

---

## Proposed MVP phases (0–9)

Each phase lists: **Goal**, **Entry criteria**, **Exit criteria**,
**Dependencies**, **Evidence required** ([GOV-006](../governance/definition-of-done.md)
style), and **Major risks**. Freeze status is marked per phase.

### Phase 0 — Specification & golden examples  ·  *Freeze: PERMITTED (design/research context)*

- **Goal:** Lock the deterministic contract of the product — trendline geometry,
  breakout/retest/expiry semantics, Confidence v1 decomposition — as specs plus
  **golden-example fixtures** (GX-01..12, CF-EV-01..07) that later implementation
  must satisfy. No product code.
- **Entry criteria:** Vision, trendline/confidence/sentiment specs, data-provider
  research, and MVP architecture drafted; this roadmap proposed.
- **Exit criteria:** Human-approved specs; complete golden-fixture set (synthetic
  OHLCV + expected-output JSON pinned to 6 sig figs) reviewed and committed as
  docs/fixtures; open questions OQ-1..OQ-4 resolved into HD decisions or explicitly
  deferred.
- **Dependencies:** None external. Human decisions HD-01..HD-04 inform fixtures.
- **Evidence required:** Committed spec docs; committed fixture files with expected
  outputs; a review record mapping each spec section to its fixture(s).
- **Major risks:** Envelope rule (R-2) or adjustment basis (R-1) mis-specified,
  baking an error into every downstream phase — mitigated by discrimination
  fixtures (GX-02) and human decisions.

### Phase 1 — Market-data foundation  ·  **Blocked: build-freeze (GOV-015)** (research sub-work permitted)

- **Goal:** A provider-agnostic `data/` layer delivering adjusted daily OHLCV and
  point-in-time S&P 500 constituents, with adjustment policy + provenance tagging.
  Preceded by human-gated provider selection.
- **Entry criteria:** Phase 0 approved; data-provider research (R1–R8) completed as
  context; human has selected/approved a provider and any recurring spend
  ([GOV-013](../governance/approval-gate.md)); freeze lifted for this scope.
- **Exit criteria:** `data/` interface implemented behind an internal contract;
  one concrete adapter passing data-quality checks; adjusted-vs-raw split
  spot-checks correct; provenance/snapshot recorded on every bar.
- **Dependencies:** Phase 0; **HD-01** (adjustment basis), **HD-06** (provider),
  **HD-07** (survivorship-free constituents + delisted history).
- **Evidence required:** Passing ingestion tests from a clean checkout; a worked
  split/symbol-change example; a stored provenance record; CI green.
- **Major risks:** Vendor cost/licensing overrun (R-5); survivorship bias if
  constituent/delisted data inadequate (R-3).

### Phase 2 — Trendline detection engine  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** The pure, deterministic `engine/` that fits the canonical ATH-anchored
  log descending line (envelope rule) and runs the ACTIVE-side state machine.
- **Entry criteria:** Phase 0 golden fixtures approved; **HD-02** (envelope rule)
  approved; freeze lifted for this scope.
- **Exit criteria:** Engine reproduces GX-01, GX-02, GX-06, GX-08, GX-09, GX-10,
  GX-12 exactly; every accept/reject emits a reason code; determinism guard passes.
- **Dependencies:** Phase 0 fixtures; **HD-01**, **HD-02**; (bars can be fixtures,
  so Phase 2 does not strictly require Phase 1).
- **Evidence required:** Passing fixture tests to 6 sig figs; determinism test
  (same input twice → identical output); reason-code coverage report; CI green.
- **Major risks:** Envelope mis-implementation (R-2); float/tie non-determinism.

### Phase 3 — Breakout & retest engine  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Extend the engine with confirmed-breakout, wick-break, retest,
  failed-breakout, and expiry/recompute logic.
- **Entry criteria:** Phase 2 exit met; **HD-03** (breakout confirmation policy)
  approved; freeze lifted for this scope.
- **Exit criteria:** Engine reproduces GX-03, GX-04, GX-05, GX-07, GX-11 exactly;
  full state machine + reason codes verified.
- **Dependencies:** Phase 2; **HD-03**.
- **Evidence required:** Passing breakout/retest/expiry fixture tests; state-machine
  transition coverage; CI green.
- **Major risks:** Confirmation policy too loose/tight (false positives/negatives);
  volume-qualifier data dependency on Phase 1.

### Phase 4 — Historical scanner & backtesting  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Replay historical bars survivorship-bias-free across the S&P 500 and
  produce a backtest/calibration report; the daily batch scaffold.
- **Entry criteria:** Phases 1–3 exit met; point-in-time constituents + delisted
  history available (**HD-07**); freeze lifted for this scope.
- **Exit criteria:** Backtest harness runs over historical universe; emits a
  rank-ordering/lift report shell (pre-Confidence, geometry/outcome stats);
  reproducible from a fixed data snapshot.
- **Dependencies:** Phases 1–3; **HD-07**.
- **Evidence required:** A reproducible backtest run (fixed snapshot → identical
  report); survivorship-bias-free universe evidence; CI green.
- **Major risks:** Survivorship bias (R-3); backtest non-reproducibility if
  snapshots not pinned.

### Phase 5 — Confidence v1  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** The deterministic, decomposable Confidence v1 heuristic (C1–C7) with
  full explainability output and the no-sentiment guard.
- **Entry criteria:** Phases 2–4 exit met; confidence spec + CF-EV fixtures
  approved; **HD-04** wording policy set; freeze lifted for this scope.
- **Exit criteria:** Reproduces CF-EV-01..07 exactly; `score_kind:"heuristic"`,
  disclaimers enforced, `Σ contributions == score`; no sentiment field present;
  rank-ordering lift measured on the historical set (**HD-05** label needed only
  for the win/loss validation).
- **Dependencies:** Phases 2–4; **HD-04**; **HD-05** (for lift validation labels).
- **Evidence required:** Passing confidence fixtures; no-sentiment assertion test
  (CF-EV-03); a lift report on historical breakouts; CI green.
- **Major risks:** Mis-presentation as probability (R-4); premature sentiment
  inclusion (R-6, GOV-014).

### Phase 6 — Internal dashboard & alerts  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Internal read-only dashboard rendering scans, lines, states, and the
  **decomposed** confidence score; internal alerting on new confirmed events.
- **Entry criteria:** Phases 4–5 exit met; thin read-model `api/` designed; freeze
  lifted for this scope.
- **Exit criteria:** Analyst can inspect any name's line, state, breakout, retest,
  and full score decomposition; internal alerts fire on new confirmed events.
- **Dependencies:** Phases 4–5; `api/` + `db/` read models.
- **Major risks:** Explainability regressions (decomposition not surfaced);
  scope creep into SaaS features prematurely (GOV-007).
- **Evidence required:** UI rendering tests against known fixtures; an alert-fired
  audit record; CI green.

### Phase 7 — SaaS MVP  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Turn the internal dashboard into a paid SaaS: auth, subscription-scoped
  queries, subscription **alert** delivery (email first), billing.
- **Entry criteria:** Phase 6 validated; **HD-10** SaaS PII/billing security review
  complete; **HD-08/HD-09** resolved for any user-facing sentiment display and its
  redistribution rights; freeze lifted for this scope.
- **Exit criteria:** A subscriber can register, subscribe, and receive alert cards
  with mandatory disclaimers; billing via a third-party processor; PII minimized.
- **Dependencies:** Phase 6; **HD-10**; **HD-08/HD-09** (only if sentiment is
  displayed); provider redistribution rights (data R7).
- **Evidence required:** Auth/billing integration tests; a delivered alert with
  disclaimer; a passing security/privacy review record; CI green.
- **Major risks:** PII/billing compliance exposure (R-7); data redistribution
  licensing (NFR-8).

### Phase 8 — Machine-learning confidence  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** A supervised Confidence v2 trained on captured features (confidence §5)
  with triple-barrier labels (confidence §6), backtested before shipping. This is
  where **sentiment may finally enter the score** — only if it improves calibration
  AND a human approves (GOV-014 §7).
- **Entry criteria:** Phases 4–5 produce a labeled historical dataset; **HD-05**
  label thresholds approved; **HD-08** (sentiment→score) evidence + approval **if**
  sentiment is a candidate feature; freeze lifted for this scope.
- **Exit criteria:** v2 model versioned and coexisting with v1; out-of-sample
  backtest meets calibration/reliability targets (confidence §7); if sentiment is
  included, the Sentiment-Before-Evidence rule (calibration lift + human approval)
  is satisfied with attached evidence.
- **Dependencies:** Phases 4–5; **HD-05**; **HD-08** (for any sentiment feature).
- **Evidence required:** Out-of-sample calibration/reliability report; model
  version registry entry; with-vs-without-sentiment comparison **if** applicable;
  a feature-flag/kill-switch demonstration; CI green.
- **Major risks:** Over-fitting / look-ahead bias; unproven sentiment inflating
  trust (R-6, GOV-014); mis-calibration presented as probability (R-4).

### Phase 9 — Scale & expansion  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Grow beyond the S&P 500 daily-batch MVP as measured demand justifies:
  broader universes, additional channels, and (only if a measured bottleneck
  exists) horizontal scaling / a service split along the existing module seams.
- **Entry criteria:** SaaS validated (Phase 7) with demand/scale evidence; specific
  expansion approved as its own roadmap item; freeze lifted per-scope.
- **Exit criteria:** Defined per approved expansion increment (each is its own
  bounded scope, not a blanket license).
- **Dependencies:** Phases 7–8; a measured, evidenced need (anti-gold-plating,
  GOV-007; architecture §7).
- **Evidence required:** Demand/scale metrics justifying the expansion; per-increment
  acceptance evidence; CI green.
- **Major risks:** Premature scaling (architecture §7); scope drift beyond the
  approved thesis (GOV-007).

---

## Change log

| Date | Change | Approved by |
|------|--------|-------------|
| 2026-07-23 | Roadmap created, empty, under build-freeze. | pending |
| 2026-07-24 | Proposed MVP roadmap (Phases 0–9) drafted for approval. | PENDING (human) |
