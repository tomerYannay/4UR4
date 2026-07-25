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
  **golden-example fixtures** that later implementation must satisfy. The fixture
  set is **whatever is committed**, not a list restated here: every fixture
  directory under [`fixtures/golden/`](fixtures/golden/), the real-market
  fixture(s) under [`fixtures/real/`](fixtures/real/), and every `CF-EV-*`
  case enumerated in [`confidence-specification.md`](confidence-specification.md)
  §11. No product code.
- **Entry criteria:** Vision, trendline/confidence/sentiment specs, data-provider
  research, and MVP architecture drafted; this roadmap proposed.
- **Exit criteria:** Human-approved specs; complete golden-fixture set (synthetic
  OHLCV + expected-output JSON pinned to 6 sig figs) reviewed and committed as
  docs/fixtures; open questions OQ-1..OQ-4 resolved into HD decisions or explicitly
  deferred. Machine-checkable form: every `expected.json` under
  `product/fixtures/golden/` schema-validates and every documentation link and
  markdown table resolves under `node tools/check-evidence.mjs`, which **derives**
  its fixture list from the directory rather than from any written list.
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
  log descending line (envelope rule) as-of-time and runs the **pre-breakout**
  state machine — formation gates, input guards, rolling re-selection (§21.6) and
  the `ACTIVE → ACTIVE` wick-break edge (§14), which is not a state.
- **Entry criteria:** Phase 0 golden fixtures approved; **HD-02** (envelope rule)
  approved; freeze lifted for this scope; **and the clean-room authorship
  criterion below (E2-AUTHOR) is satisfied.**

- **Entry criterion E2-AUTHOR — clean-room authorship (HD-15 condition 2,
  [#20](https://github.com/tomerYannay/4UR4/issues/20)).**
  `tools/fixture-replay.mjs` is a causal reference model permitted under GOV-015
  **only** as Phase-0 evidence tooling, on the stated conditions that it confers
  **no Phase-2 credit** and that the Phase-2 engine is *"authored from the
  specification by an agent that has not read this model"*
  ([HD-15](human-decisions.md); [`build-freeze.md`](../governance/build-freeze.md)).
  With no mechanism, that clause is unenforceable and HD-15 degrades from a scope
  ruling into a de facto partial freeze lift. Phase 2 may therefore not be entered
  until **all four** hold:
  1. **The Ready ticket names the constraint.** The Phase-2 implementation
     ticket's Definition of Ready carries an explicit clean-room clause naming
     `tools/fixture-replay.mjs` — and any successor reference model under
     `tools/` — as **must-not-read** for the authoring agent.
  2. **The authoring agent is configuration-denied, not merely instructed.** The
     agent that writes `engine/` cannot read the reference model because its
     tool/permission configuration forbids that path. A prompt-level instruction
     is not a mechanism and does not satisfy this criterion.
  3. **Authorship is separated from verification.** The agent that runs the
     reference model against the engine is **not** the agent that wrote the
     engine. The verifier may read the model; the author may not.
  4. **The claim is attested and citable.** Before the Phase-2 exit gate is
     assessed, a clean-room attestation exists as an artifact — naming the
     authoring agent, its deny configuration, and the commit range it authored —
     recorded by a party other than the authoring agent.

  Criterion 4 is not satisfiable until
  [#21](https://github.com/tomerYannay/4UR4/issues/21) (review verdicts must be
  able to become artifacts; single-account attribution) is resolved, so **Phase 2
  entry is blocked on #21 in addition to the per-scope freeze lift.** Nothing in
  this criterion weakens [GOV-015](../governance/build-freeze.md).

- **Exit criteria:** The engine reproduces, **exactly and as-of-time**
  (§21 / HD-12 / D-TL-11), the Phase-2-owned behaviour of **every** fixture
  directory under [`product/fixtures/golden/`](fixtures/golden/) — no fixture is
  exempt, and no list of fixture IDs is maintained here. For each fixture the
  engine must reproduce:
  - `expected_ath_anchor`, `expected_second_anchor`, `expected_log_slope`,
    `expected_intercept` and `expected_line_values` to 6 significant figures,
    including **every** pre-breakout re-selection recorded in
    `causal_record.reselections`;
  - the formation-gate trace (`causal_record.formation`, with F1/F2/F3 evaluated
    independently) and the §18 input guards;
  - every entry of `expected_state_transitions`, with its `reason_code`, at a bar
    **strictly before** that fixture's top-level `confirmed_bar`.

  For every fixture whose top-level `confirmed_bar` is `null`, the above is the
  **whole** fixture: `expected_final_state` and the complete
  `expected_reason_codes` set must also match. **The Phase-2/Phase-3 split is a
  derived partition, not a list:** a fixture is Phase-2-complete iff
  `confirmed_bar == null`, evaluated against the committed `expected.json` files
  at gate time. Adding a fixture therefore tightens this gate automatically.
  Additionally: RM-01 (see below); every accept/reject emits a `reason_code` from
  the schema's closed set; the determinism guard passes.
- **Exit criteria (RM-01, the non-circular ground truth):** The engine also
  reproduces the **approved** RM-01 geometry from the committed
  [`fixtures/real/RM-01/input.csv`](fixtures/real/RM-01/input.csv) — anchor, canonical
  second anchor, slope and intercept to 6 significant figures, zero envelope
  violations, and no breakout in range (`confirmed_bar == null`). This needs no
  data provider and so creates **no Phase 1 dependency**: the OHLCV is committed.
  The synthetic set proves the engine is self-consistent with the written spec;
  RM-01 is the only committed evidence that the spec captures the object the
  Product Owner actually drew.
- **Why this gate is stated as a derived set, not an enumeration.** The previous
  form named seven fixture IDs here and five under Phase 3 — a hand-maintained
  restatement of a fact the repository already holds on disk, stored apart from
  it and never re-derived. It had already drifted: it silently omitted the
  HD-11/SC-2 non-pivot-`B*` proof, the sole HD-13 tolerance-boundary fixture, the
  `NO_VALID_SECOND_ANCHOR` reachability case and all three HD-14 formation-gate
  regressions, so **an engine could have passed this exit gate while contradicting
  three ratified Product Owner rulings**
  ([#19](https://github.com/tomerYannay/4UR4/issues/19)). That defect class —
  a human restatement of a machine-derivable fact — is the one this project has
  already paid for in Phase 0, and it is not repeated here. Fixture-level detail
  belongs in [`fixtures/README.md`](fixtures/README.md) §3, which is its home.
- **Dependencies:** Phase 0 fixtures; **HD-01**, **HD-02**, **HD-11**, **HD-12**,
  **HD-13**, **HD-14**, **HD-15**; Issue **#20** (E2-AUTHOR mechanism) and Issue
  **#21** (attestation artifacts); (bars can be fixtures, so Phase 2 does not
  strictly require Phase 1).
- **Evidence required:** Passing fixture tests to 6 sig figs; determinism test
  (same input twice → identical output); reason-code coverage report; the
  E2-AUTHOR clean-room attestation; CI green. **Explicitly not evidence:**
  reproducing, resembling, or agreeing with `tools/fixture-replay.mjs` earns
  **no** Phase-2 credit (HD-15 condition 1). The contract is the committed
  fixtures and the specification; where the model and the spec disagree the
  **spec governs**, and the divergence is filed as a spec-defect report or a
  model bug — never resolved by copying the model.
- **Major risks:** Envelope mis-implementation (R-2); float/tie non-determinism
  (see the GX-14 libm caveat in [`fixtures/README.md`](fixtures/README.md));
  **transcription of the reference model in place of conformance to the spec**, if
  E2-AUTHOR is asserted rather than mechanically enforced.

### Phase 3 — Breakout & retest engine  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Extend the engine with confirmed-breakout, line freezing (`Λ^F`,
  §21.5), retest, failed-breakout, and expiry/recompute logic — i.e. everything
  from the confirming bar onward. (Wick-break moved to Phase 2: §14 is an
  `ACTIVE → ACTIVE` edge on the *live* line, not a post-breakout behaviour, and
  the fixture schema's closed `expected_final_state` set confirms `WICK_BREAK` is
  not a state. This is a boundary clarification, not new scope.)
- **Entry criteria:** Phase 2 exit met; **HD-03** (breakout confirmation policy)
  approved; freeze lifted for this scope. E2-AUTHOR (Phase 2) continues to bind
  the authoring agent for the whole engine.
- **Exit criteria:** The engine reproduces **every** fixture directory under
  [`product/fixtures/golden/`](fixtures/golden/) **in full and exactly** — the
  complete `expected_state_transitions` list, the complete `expected_reason_codes`
  set and `expected_final_state` of each — with no fixture named or exempted here.
  This is the Phase-2 gate plus all post-`confirmed_bar` behaviour on the **frozen**
  line `Λ^F` (§21.5): failure, retest, expiry and recompute. Together the two gates
  cover the committed set exactly once; the split between them is the derived
  `confirmed_bar` partition stated under Phase 2, not a list. Full state machine +
  reason codes verified against the schema's closed code set.
- **Dependencies:** Phase 2; **HD-03**, **HD-12** (as-of-time freezing).
- **Evidence required:** Passing breakout/retest/expiry fixture tests; state-machine
  transition coverage; CI green. The Phase-2 exclusion carries over: agreement with
  `tools/fixture-replay.mjs` is **not** evidence and earns no credit (HD-15
  condition 1).
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

- **Goal:** The deterministic, decomposable Confidence v1 heuristic — the component
  set defined in [`confidence-specification.md`](confidence-specification.md), which
  HD-03/HD-05 revised to **C1–C8** (this line previously said "C1–C7") — with full
  explainability output and the no-sentiment guard.
- **Entry criteria:** Phases 2–4 exit met; confidence spec + CF-EV fixtures
  approved; **HD-04** wording policy set; freeze lifted for this scope.
- **Exit criteria:** Reproduces **every** `CF-EV-*` case enumerated in
  [`confidence-specification.md`](confidence-specification.md) §11 exactly — the
  spec section is the single source and is not restated here (the previous form,
  "CF-EV-01..07", had already fallen behind CF-EV-08/09); `score_kind:"heuristic"`,
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
| 2026-07-26 | **Fixture-coverage reconciliation ([#19](https://github.com/tomerYannay/4UR4/issues/19)).** Phase 0/2/3/5 exit criteria no longer enumerate fixture IDs. Phase 2 and Phase 3 now gate on *every* committed fixture, split by the derived predicate `confirmed_bar == null`; Phase 5 defers to `confidence-specification.md` §11. The old enumeration covered 12 of the committed golden fixtures and omitted the HD-11/SC-2, HD-13 and HD-14 evidence. | PENDING (human) |
| 2026-07-26 | **E2-AUTHOR added as a Phase 2 *entry* criterion ([#20](https://github.com/tomerYannay/4UR4/issues/20)).** Gives HD-15 condition 2 (clean-room authorship w.r.t. `tools/fixture-replay.mjs`) a four-part mechanism, and makes Phase 2 entry depend on [#21](https://github.com/tomerYannay/4UR4/issues/21). No freeze lift; [GOV-015](../governance/build-freeze.md) unchanged and still ON. | PENDING (human) |
| 2026-07-26 | **Two further stale enumerations of the same defect class, found while doing the above and fixed here.** Phase 0's goal said the fixture set was "GX-01..12, CF-EV-01..07"; Phase 5's goal said the Confidence v1 component set was "C1–C7". Both had drifted: 23 golden fixtures are committed, `confidence-specification.md` §11 defines CF-EV-01..09, and HD-03/HD-05 revised the component set to C1–C8. All three now defer to their source instead of restating it. | PENDING (human) |
| 2026-07-26 | **Two Steward judgement calls needing human confirmation, beyond the literal text of #19.** (a) **RM-01 added to the Phase 2 exit gate** — it is the only committed non-circular ground truth and was in no phase gate at all; its OHLCV is committed, so this adds no Phase 1 dependency. (b) **Wick-break (§14) reassigned from the Phase 3 goal to Phase 2**, since `WICK_BREAK` is an `ACTIVE → ACTIVE` edge on the live line and falls in the `confirmed_bar == null` partition. Both are coherence fixes, not new scope; flag them if either is unwanted. | PENDING (human) |
