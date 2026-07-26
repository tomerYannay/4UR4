# 4UR4 Roadmap (governed) — **APPROVED baseline** · *not an authorization to build*

> **Authority:** Only the **Product Steward**, acting with explicit human
> approval, may add or reorder items here ([GOV-002](../governance/roadmap-authority.md)).
> The Product Innovation Agent may **never** write to this file
> ([GOV-003](../governance/roadmap-authority.md)). Any other agent editing this
> file is a governance violation the [Auditor](../.claude/agents/project-auditor.md) must flag.

> **STATUS: APPROVED (baseline).** The Phase 0–9 roadmap below is **approved as a
> baseline** by the Product Owner under
> [GOV-013](../governance/approval-gate.md) —
> [issue #23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26. It is no
> longer a proposal, and **no general human approval is pending** for the phase
> structure, ordering, or gate criteria recorded here.

> ### ⚠ Approved as a baseline, and nothing more
>
> **This approval does NOT:**
>
> 1. **lift [GOV-015](../governance/build-freeze.md).** The build-freeze remains
>    **ON**, with `autonomous_implementation: DISABLED`. Nothing about the freeze
>    moved on 2026-07-26.
> 2. **authorize product implementation.** Phases 1–9 remain **Blocked:
>    build-freeze**. Implementation begins only when a human lifts the freeze
>    **per-scope**, tied to a specific approved, Ready ticket — never as a blanket
>    "autonomy on" (GOV-015 rule 4).
> 3. **select a provider.** **HD-06 remains PENDING** and is still the only open
>    Product Owner decision. No agent may select a data provider.
> 4. **authorize spend or licensing.** No recurring cost, purchase, or licence
>    term is approved by this ruling, and no agent may commit one.
>
> These four exclusions are the Product Owner's own, stated in
> [#23](https://github.com/tomerYannay/4UR4/issues/23) and reproduced here as the
> operative limits of the approval. **A reader arriving at
> an "APPROVED" roadmap must not conclude that building may begin.** An approved
> baseline fixes *what* is planned and *in what order*; [GOV-015](../governance/build-freeze.md)
> governs *whether any of it may yet be built*, and it has not moved. Phase 0
> (specification, golden examples, research/design) remains permitted
> context/design work under the freeze, as does explicitly research-only Phase 1
> sub-work (see Phase 1).

> **Decisions retained in full by this ruling.** **HD-13** is retained **in full** —
> no clause struck, including the **±20%** invariance threshold, **GX-15** as the
> sole dedicated tolerance-boundary fixture, the bar on turning ordinary fixtures
> into boundary tests, and the preservation (not reversion) of the robust **GX-19**
> causal breakout. **HD-15 conditions 1–3** are likewise retained in full, with
> condition 2 *sharpened* (see **E2-AUTHOR** under Phase 2). Nothing in this
> roadmap treats any of those clauses as provisional, conditional, or pending.

> ### The universe: **4UR4 US Large-Cap 500** — ruled 2026-07-26 (HD-18, [#24](https://github.com/tomerYannay/4UR4/issues/24))
>
> **4UR4's universe is a self-computed, point-in-time universe of the 500
> largest eligible US-listed operating companies**, built by 4UR4 under its own
> transparent, versioned rules. Working product name: **4UR4 US Large-Cap 500**.
> It **is not the S&P 500**, is **not** licensed S&P 500 constituent membership,
> and is **not endorsed by, affiliated with, sponsored by, or equivalent to
> S&P Dow Jones Indices**. Where the name "S&P 500" still appears in this
> roadmap it is **only** as the thing being deliberately *not* used, or as an
> external market reference, and the reason is stated in place.
>
> **Why the universe is built rather than bought.**
> [`survivorship-bias-findings.md`](survivorship-bias-findings.md) established
> two facts that together made licensed membership an unacceptable dependency.
> First, **index membership is licensed separately from prices and far more
> restrictively**: an executed S&P *Master Index License Agreement* on SEC EDGAR
> contracts "index constituents" under a **separate MSA with separate fees**
> (§4.1), and **SPDJI withdrew constituent names from Compustat in 2020** in
> order to license them directly (§2.3) — the direction of travel is more
> restriction, not less. Second, the two most complete survivorship-free
> datasets found — **Norgate and CRSP** — are both **licence-barred from
> commercial use** (§4.2). Licensed membership was therefore an **unpriced,
> unbounded exposure on a dependency a third party can withdraw or reprice
> unilaterally**. A self-computed universe removes that dependency entirely.
>
> **What the change costs — stated here so that no gate below can imply
> otherwise.** A mechanical top-500 rule **cannot reproduce S&P 500 membership**.
> The index committee applies discretion — profitability screens, public float,
> sector balance, judgement — that no published mechanical rule replicates. The
> consequence is load-bearing, and it is gated below as **UNIV-DISC**:
> **4UR4 backtest results will not be comparable to published S&P 500 strategy
> results.** That is a licensing advantage and an interpretation liability at
> the same time, and **both halves must travel with every number 4UR4 reports.**
>
> **What this ruling did *not* change.** [GOV-015](../governance/build-freeze.md)
> remains **ON**, with `autonomous_implementation: DISABLED`. **HD-06 remains
> PENDING.** *(Corrected 2026-07-26: this previously said HD-06 was "the only open
> Product Owner decision". **HD-20** — RM-01's as-of-time divergence
> ([#26](https://github.com/tomerYannay/4UR4/issues/26)) — is now open too, and
> `universe-methodology.md` §11.2 escalates OQ-U1…OQ-U7.)* This ruling is
> **not a freeze lift** and **not a provider selection**; it authorizes no spend
> and accepts no licence terms. It changes *which universe is being described*,
> not whether any of it may yet be built or bought.
>
> **What may move without a further ruling, and what may not.** The exact
> inclusion, liquidity, security-type, domicile and rebalance rules are
> **independently versioned and backtestable**, and the **Strategic Product
> Reviewer may choose the safest reversible initial research defaults** for them
> under [HD-17](human-decisions.md)'s six conjunctive conditions. **A material
> change to the intended market segment remains Product Owner-gated** and is a
> product-definition change, which HD-17 expressly excludes.

## Promotion path (how anything gets here)

```
Ideas Inbox  ──(human + Product Steward triage)──▶  Roadmap phases
             GOV-003 gate                            (this file)
```

An idea/phase becomes a **committed** roadmap item only after it has:
- a stated **user/business value** and a **success measure**,
- passed the [Product-Focus Guard](../governance/product-focus.md) (GOV-007),
- explicit **human sign-off** (GOV-013).

The Phase 0–9 baseline below has **cleared this gate**
([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26). Clearing it
commits the *plan*; it does not authorize the *build* — see the four exclusions
above.

---

## Approved MVP phases (0–9)

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
  research, and MVP architecture drafted; this roadmap **approved as a baseline**
  ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26).
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
  **point-in-time 4UR4 US Large-Cap 500 membership computed by 4UR4** (HD-18,
  [#24](https://github.com/tomerYannay/4UR4/issues/24)) — not licensed index
  membership — with adjustment policy + provenance tagging. Preceded by
  human-gated provider selection.
- **Entry criteria:** Phase 0 approved; data-provider research (R1–R8) completed as
  context; human has selected/approved a provider and any recurring spend
  ([GOV-013](../governance/approval-gate.md)); freeze lifted for this scope.

- **Ready now — research sub-work only ([#23](https://github.com/tomerYannay/4UR4/issues/23),
  2026-07-26).** The baseline approval makes **Phase 1 research** proceed-able.
  Issues [#4](https://github.com/tomerYannay/4UR4/issues/4) (data-provider research
  and comparison matrix) and [#5](https://github.com/tomerYannay/4UR4/issues/5)
  (survivorship-bias-free constituents + delisted history research) are now
  **Ready** — tickets (c) and (d) of
  [`planning/ticket-set.md`](planning/ticket-set.md), whose DoR note *"becomes Ready
  upon human roadmap approval (GOV-013)"* is hereby satisfied. **What Ready means
  here, precisely:**
  - **Both are `research-only (freeze-permitted)`.** That is the autonomy level, and
    it is the whole of it. Ready authorizes the *research*; it authorizes **no**
    `data/` interface, **no** adapter, and **no** ingestion code. This is **not** a
    freeze lift — [GOV-015](../governance/build-freeze.md) is untouched and the
    Phase 1 *implementation* ticket (e) stays **blocked: freeze**.
  - **#4's provider *selection* remains human-gated.** Its research may proceed and
    must terminate in an **evidence-populated comparison matrix, not a scored
    decision**. **HD-06** — still the **only PENDING** Product Owner decision — is
    the sole instrument that may select a provider or commit spend or licensing,
    and only a human may take it. Producing the evidence that informs HD-06 is in
    scope; making, pre-empting, or recommending-as-settled the selection is not.
  - **#5 likewise commits nothing.** **HD-07** approved the *need* for
    point-in-time membership and delisted history; **purchase remains
    human-gated**, so #5 researches availability, licensing and cost only.
  - **HD-18 redirects what #5 researches; it does not change its status.** With
    the universe self-computed, #5's object is the **inputs** a 4UR4-computed
    universe needs — listing status, shares outstanding / market capitalisation,
    liquidity, security type, domicile, delisted price history and corporate
    actions — rather than a licensed constituent list. Both tickets remain
    **Ready** at **`research-only (freeze-permitted)`**; **HD-06 stays PENDING**;
    no freeze moved.
- **Exit criteria:** `data/` interface implemented behind an internal contract;
  one concrete adapter passing data-quality checks; adjusted-vs-raw split
  spot-checks correct; provenance/snapshot recorded on every bar.
- **Exit criteria (UNIV-METH — the universe is built here, so the methodology is
  gated here) — ruled [#24](https://github.com/tomerYannay/4UR4/issues/24),
  2026-07-26.** Under HD-18 the universe is no longer a purchased artifact whose
  correctness is the vendor's problem; it is a 4UR4 deliverable, and Phase 1 does
  not exit until **all six** hold:
  1. **Eligibility and ranking rules are transparent and versioned.** The rules
     that decide *which* companies are eligible and *how* the top 500 are ranked
     are written down, carry a version identifier, and are complete enough that a
     third party can reproduce the membership list for any date from the rules
     plus the input data.
  2. **Membership is point-in-time.** Membership on date `d` is derived **only**
     from information that existed on `d`. This is the **same causal discipline
     HD-12 already ratified for anchor selection, applied one layer down** (§21,
     D-TL-11): the universe that judges bar `t` may not be built from anything
     after it. A present-day membership list is never used for a historical date.
  3. **Delisted securities are preserved.** A company that stops trading stays in
     the history with its terminal record; nothing is dropped because it no
     longer exists today.
  4. **Additions and removals carry effective dates and evidence.** Every
     membership change records the date it took effect and the artifact that
     justifies it, so any single change can be audited on its own.
  5. **Survivorship bias is absent by construction, and demonstrated.** Criteria
     2–4 are the construction; the demonstration is a reproducible check that a
     membership list rebuilt as-of a past date contains names absent from today's
     list. Absence of bias is **shown**, not asserted.
  6. **The rule set is independently versioned and backtestable.** Inclusion,
     liquidity, security-type, domicile and **rebalance** rules version
     **separately** from one another, and every backtest records the rule-set
     versions it ran under — so a change of rules is visible as a change in
     results rather than hiding inside one.

  The **design** lands in
  [`docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
  (**being authored now — it is design, not implementation, and is
  freeze-permitted as such**). That document *specifies* criteria 1–6; it
  **satisfies none of them by itself**. UNIV-METH is met by the implemented
  `data/` layer conforming to it, under a per-scope freeze lift.
  [GOV-015](../governance/build-freeze.md) is untouched by this criterion.
- **Dependencies:** Phase 0; **HD-01** (adjustment basis), **HD-06** (provider —
  **still PENDING**, and unaffected by the 2026-07-26 baseline approval or by
  HD-18), **HD-07** (survivorship-free membership + delisted history; need
  approved, purchase human-gated), **HD-18** (the universe is the **4UR4 US
  Large-Cap 500**, self-computed).
- **Evidence required:** Passing ingestion tests from a clean checkout; a worked
  split/symbol-change example; a stored provenance record; **a reproducible
  as-of-date membership rebuild demonstrating UNIV-METH criteria 2–5, including
  at least one name present historically and absent today**; CI green.
- **Major risks:** Vendor cost/licensing overrun (R-5); survivorship bias if
  input/delisted data inadequate (R-3); **a self-computed universe that silently
  diverges from any published index in ways nobody measures — mitigated by
  UNIV-METH item 6 (versioned rules) and by UNIV-DISC (Phase 4), never by
  implying comparability**.

### Phase 2 — Trendline detection engine  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** The pure, deterministic `engine/` that fits the canonical ATH-anchored
  log descending line (envelope rule) as-of-time and runs the **pre-breakout**
  state machine — formation gates, input guards, rolling re-selection (§21.6) and
  the `ACTIVE → ACTIVE` wick-break edge (§14), which is not a state.
- **Entry criteria:** Phase 0 golden fixtures approved; **HD-02** (envelope rule)
  approved; freeze lifted for this scope; **and the clean-room authorship
  criterion below (E2-AUTHOR) is satisfied.**

- **Entry criterion E2-AUTHOR — independent authorship (HD-15 condition 2,
  [#20](https://github.com/tomerYannay/4UR4/issues/20)).**
  `tools/fixture-replay.mjs` is a causal reference model permitted under GOV-015
  **only** as Phase-0 evidence tooling, conferring **no Phase-2 credit**
  ([HD-15](human-decisions.md); [`build-freeze.md`](../governance/build-freeze.md)).
  With no mechanism, HD-15 condition 2 is unenforceable and HD-15 degrades from a
  scope ruling into a de facto partial freeze lift.

  **HD-15 condition 2 as sharpened by the Product Owner**
  ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26): the Phase-2
  implementation *"must remain independently authored and must not import, copy,
  execute or mechanically translate the reference model"*, and *"Issue #20 must
  define an enforceable independence mechanism before Phase 2 implementation
  begins."*

  **E2-AUTHOR-A — the testable criterion is a property of the artifact.** The
  committed `engine/` **must not import, copy, execute or mechanically translate**
  `tools/fixture-replay.mjs`, or any successor reference model under `tools/`.
  This is the criterion that is **assessed at the gate**, because it is a property
  of the code that exists: imports and invocations are statically detectable, and
  copying or mechanical translation is assessable by comparing structure, control
  flow, naming and constant-derivation against the model. It is checkable by
  anyone, at any time, indefinitely after the fact.

  **E2-AUTHOR-B — the read-restriction is the preventive control, not the test.**
  *"Authored by an agent that has not read this model"* is a claim about a
  **session's history**: it is unverifiable once the session has ended, and it
  degrades to self-report. It is **retained in full** — it is the cheapest way to
  stop an A-violation from ever being written — but it is retained as a
  **control**, not as the evidence. **Where the two diverge, A governs:** an
  `engine/` that imports or transcribes the model **fails** E2-AUTHOR even if no
  agent ever read it, and an unblemished read-history is **not** a defence for a
  transcribed artifact.

  Phase-2 **implementation may not begin**, and Phase 2 may not be entered, until
  **all five** hold:
  1. **#20 has defined the enforceable independence mechanism.** This is the
     Product Owner's **named precondition**: the mechanism must be *defined
     before* Phase 2 implementation begins, not improvised during it. Items 2–5
     are this roadmap's current statement of what that mechanism must cover;
     [#20](https://github.com/tomerYannay/4UR4/issues/20) is where it is settled,
     and until it closes this criterion is unmet.
  2. **The Ready ticket carries both halves.** The Phase-2 implementation ticket's
     Definition of Ready states **E2-AUTHOR-A as a testable acceptance criterion**
     on the delivered artifact, *and* names `tools/fixture-replay.mjs` — and any
     successor reference model under `tools/` — as **must-not-read** for the
     authoring agent (E2-AUTHOR-B).
  3. **The authoring agent is configuration-denied, not merely instructed.** The
     agent that writes `engine/` cannot read the reference model because its
     tool/permission configuration forbids that path. A prompt-level instruction
     is not a mechanism and does not satisfy this criterion.
  4. **Authorship is separated from verification.** The agent that runs the
     reference model against the engine is **not** the agent that wrote the
     engine. The verifier may read the model; the author may not.
  5. **The claim is attested and citable.** Before the Phase-2 exit gate is
     assessed, an **independence attestation** exists as an artifact, recorded by
     a party other than the authoring agent, carrying **both**: the
     **E2-AUTHOR-A** check performed against the committed `engine/` (no import,
     copy, execution or mechanical translation), and the **E2-AUTHOR-B** record of
     the authoring agent, its deny configuration, and the commit range it authored.

  Criterion 5 is not satisfiable until
  [#21](https://github.com/tomerYannay/4UR4/issues/21) (review verdicts must be
  able to become artifacts; single-account attribution) is resolved, so **Phase 2
  entry is blocked on #20 and #21 in addition to the per-scope freeze lift.**
  Nothing in this criterion weakens [GOV-015](../governance/build-freeze.md), and
  **HD-15 conditions 1–3 are retained in full** — condition 2 is sharpened here,
  not narrowed or relaxed.

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
  `expected_reason_codes` set must also match. **Which fixtures are wholly
  Phase-2 is derived, not listed:** a fixture is Phase-2-complete iff
  `confirmed_bar == null`, evaluated against the committed `expected.json` files
  at gate time. Adding a fixture therefore tightens this gate automatically. That
  predicate is the **mechanical selector over fixture data**; it is *not* the
  criterion that assigns behaviour to phases — the behavioural **Phase 2 / Phase 3
  boundary rule** below is, and it governs wherever the two could diverge.
  Additionally: RM-01 (see below); every accept/reject emits a `reason_code` from
  the schema's closed set; the determinism guard passes.
- **Exit criteria (RM-01, the non-circular ground truth) — ruled
  [#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26.**
  ⚠ **Numeric acceptance values: `UNDER REVIEW — pending HD-20` (2026-07-26).**
  Product Owner ruling, verbatim: *"RM-01 is part of the Phase 2 exit gate as the
  committed real-market, non-circular conformance fixture."* **That ruling stands
  and is untouched here: RM-01 remains part of the Phase 2 exit gate.** The engine
  therefore also reproduces the RM-01 geometry from the committed
  [`fixtures/real/RM-01/input.csv`](fixtures/real/RM-01/input.csv), which needs no
  data provider and so creates **no Phase 1 dependency**: the OHLCV is committed.
  The synthetic set proves the engine is self-consistent with the written spec;
  RM-01 is the only committed evidence that the spec captures the object the
  Product Owner actually drew — which is precisely the **non-circularity** the
  ruling names, since every synthetic fixture was derived from the same
  specification the engine is being tested against.

  **`UNDER REVIEW — pending HD-20` — the acceptance values only.** The values this
  gate has required — anchor, canonical second anchor, slope and intercept to 6
  significant figures, zero envelope violations, and **no breakout in range
  (`confirmed_bar == null`)** — are **suspended**, and are restated here only so the
  pending review has a subject. **Why:** RM-01's approved record is a **full-series**
  hull (`B* = (25, 129.88)`, slope `-0.0240143`) under which no close ever exceeds
  the line, but replayed **as-of-time** — the evaluation that §21 / HD-12 / D-TL-11
  and this gate's own first clause both require — the same committed OHLCV yields a
  **confirmed breakout at bar 10 (2026-06-29) with a margin of `0.0864461` log
  units**; so `confirmed_bar == null` is **provably unsatisfiable by a
  spec-conforming engine**, and a gate demanding it would fail a *correct*
  implementation. Both records are arithmetically correct about different objects,
  exactly as §21.4's non-normative corollary predicts. Full disclosure, including the
  bar-by-bar derivation and the robustness argument (suppression would need
  `eps_break` ≈ 8.6× the documented value, which HD-13 forbids in any case):
  [`fixtures/README.md`](fixtures/README.md) §6b.

  **Until HD-20 is ruled, the RM-01 acceptance values are pending and this gate is
  not assessable on them.** Nothing is unblocked by that: Phase 2 is
  **Blocked: build-freeze** ([GOV-015](../governance/build-freeze.md)) and its entry
  additionally awaits [#20](https://github.com/tomerYannay/4UR4/issues/20) and
  [#21](https://github.com/tomerYannay/4UR4/issues/21). **This roadmap decides
  nothing here.** The suspension reaches only the acceptance values, which are
  **Steward drafting**; the ruled text — RM-01's membership in the gate — is not
  Steward-suspendable and has not been suspended.

  **What a split would cost — one side of a contested assessment — recorded because it bears on HD-20 (Strategic Product
  Reviewer finding under its [HD-17](human-decisions.md) bounded delegation).** One
  resolution under consideration would replace the end-to-end RM-01 check with a §8
  **unit-level** assertion on the full-series hull (the *"Half A"* proposal). That
  assertion is **weaker than this gate's current wording implies**: a §21-conforming
  detector **never computes `(25, 129.88)` at all**, because the bar-10 breakout
  **freezes** the line (§21.5) long before bar 25 is reached — so the unit check
  would test a quantity the engine does not produce in normal operation. And because
  §8 is the **most fixture-covered rule in the corpus**, a unit test on it **bites
  less** than the end-to-end real-data check that the synthetic-vs-real independence
  design ([`fixtures/README.md`](fixtures/README.md) §6) relies on RM-01 to provide.
  **The contrary assessment, recorded alongside it so this is disclosure and not
  advocacy:** [`../docs/architecture/phase2-implementation-plan.md`](../docs/architecture/phase2-implementation-plan.md)
  §7.3 calls that same §8 check *"the strongest single test of the envelope selector in
  the whole corpus"*, and its actual proposal is **not** a replacement — it is Half A
  **retained now** *plus* Half B **escalated**, asking the Product Owner to rule
  "Half A, Half B, **or both**". Two documents in this PR reach opposite judgements on
  the same check; both are before whoever rules HD-20.
  Recording this **decides nothing**; it exists so the cost — and the disagreement about
  it — is in front of whoever rules HD-20 rather than lost.
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

- **The Phase 2 / Phase 3 boundary — a behavioural rule (ruled
  [#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26).** The boundary
  is **stated as a rule, not inferred** from what the current fixtures happen to
  contain:
  - **Phase 2 owns** behaviour that is evaluated **while the structure remains
    `ACTIVE`** and that itself performs **no `ACTIVE → BROKEN_OUT` state
    transition** — formation gates, the §18 input guards, rolling as-of-time
    re-selection (§21.6), and the **wick-break** edge (§14).
  - **Phase 3 owns** **confirmed breakout, retest, failure and expiry** behaviour —
    the `ACTIVE → BROKEN_OUT` transition itself and everything downstream of it on
    the frozen line `Λ^F` (§21.5).

  **Wick-break is in Phase 2 because of what it does.** Product Owner ruling,
  verbatim: *"Wick-break belongs in Phase 2 because it is evaluated while the
  structure remains ACTIVE and does not itself perform an ACTIVE → BROKEN_OUT state
  transition. Phase 3 remains responsible for confirmed breakout, retest, failure
  and expiry behavior."* §14 is evaluated against the **live** line while the
  structure is still `ACTIVE`, and it is an `ACTIVE → ACTIVE` edge; the fixture
  schema's closed `expected_final_state` set confirms `WICK_BREAK` is not a state
  at all. This is a boundary clarification, not new scope.

  ***Corroboration only — and deliberately demoted.*** The committed fixtures
  currently agree: the five fixtures carrying a `WICK_BREAK` reason code —
  **GX-02, GX-03, GX-09, GX-12, GX-13** — all presently have `confirmed_bar:
  null`, and so fall in the Phase-2 partition. **That is evidence, not the
  criterion.** An earlier revision of this roadmap justified wick-break's
  placement by that partition; the justification is now the behavioural rule
  above, because the partition observation is a **mechanical consequence of
  current fixture data** and would evaporate if the data changed — whereas the
  behavioural rule would not.

  This is not a hypothetical worry. Both tolerances are deliberately **unlocked**
  (`ε_break` per HD-03 unamended, retained by **HD-13**), and per
  [`fixtures/README.md`](fixtures/README.md) and `GX-15/expected.json`:
  - **GX-12**, one of the five, has its `t=15` wick **become a breakout** at the
    0.5× sweep point — moving it out of the `confirmed_bar == null` partition
    entirely, while complying with HD-13 at ±20%.
  - **GX-15** shows the converse instability. At the documented tolerances it
    carries neither a `WICK_BREAK` nor a breakout, but a `WICK_BREAK` appears at
    `t=28` for any envelope `ε` strictly below `0.018534340624`, and a breakout
    fires at `t=28` for any `ε_break` strictly below `0.008242654587`. Both its
    wick-break status *and* its partition membership are tolerance-contingent.

  So the `confirmed_bar` partition assigns wick-break to Phase 2 only under
  parameter values the specification expressly declines to fix. **Under the
  behavioural rule the wick-break edge is Phase-2 in every one of those
  configurations**, with only the resulting confirmed breakout moving to Phase 3.
  A criterion that survives a change in fixture data is worth more than one
  derived from it.

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
  from the confirming bar onward. Per the ruling of
  [#23](https://github.com/tomerYannay/4UR4/issues/23), **Phase 3 remains
  responsible for confirmed breakout, retest, failure and expiry behaviour** —
  that is this phase's half of the behavioural **Phase 2 / Phase 3 boundary rule**
  stated under Phase 2, and it is the explicit complement of Phase 2's half.
  (Wick-break sits in Phase 2 under that rule: §14 is evaluated while the structure
  remains `ACTIVE` and performs no `ACTIVE → BROKEN_OUT` transition. A boundary
  clarification, not new scope.)
- **Entry criteria:** Phase 2 exit met; **HD-03** (breakout confirmation policy)
  approved; freeze lifted for this scope. E2-AUTHOR (Phase 2) continues to bind
  the authoring agent for the whole engine.
- **Exit criteria:** The engine reproduces **every** fixture directory under
  [`product/fixtures/golden/`](fixtures/golden/) **in full and exactly** — the
  complete `expected_state_transitions` list, the complete `expected_reason_codes`
  set and `expected_final_state` of each — with no fixture named or exempted here.
  This is the Phase-2 gate plus all post-`confirmed_bar` behaviour on the **frozen**
  line `Λ^F` (§21.5): failure, retest, expiry and recompute. Together the two gates
  cover the committed set exactly once; which fixtures fall wholly to Phase 2 is
  selected by the derived `confirmed_bar` predicate stated there, while **which
  behaviour belongs to which phase** is fixed by the behavioural boundary rule
  under Phase 2. Full state machine + reason codes verified against the schema's
  closed code set.
- **Dependencies:** Phase 2; **HD-03**, **HD-12** (as-of-time freezing).
- **Evidence required:** Passing breakout/retest/expiry fixture tests; state-machine
  transition coverage; CI green. The Phase-2 exclusion carries over: agreement with
  `tools/fixture-replay.mjs` is **not** evidence and earns no credit (HD-15
  condition 1).
- **Major risks:** Confirmation policy too loose/tight (false positives/negatives);
  volume-qualifier data dependency on Phase 1.

### Phase 4 — Historical scanner & backtesting  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Replay historical bars survivorship-bias-free across the **4UR4 US
  Large-Cap 500** (HD-18) and produce a backtest/calibration report; the daily
  batch scaffold.
- **Entry criteria:** Phases 1–3 exit met; **UNIV-METH met** (Phase 1) so
  point-in-time membership + delisted history exist for the 4UR4-computed
  universe (**HD-07**, **HD-18**); freeze lifted for this scope.
- **Exit criteria:** Backtest harness runs over the historical **4UR4 US
  Large-Cap 500** universe at each date's point-in-time membership; emits a
  rank-ordering/lift report shell (pre-Confidence, geometry/outcome stats);
  reproducible from a fixed data snapshot; **and UNIV-DISC below is satisfied.**
- **Exit criteria (UNIV-DISC — the disclosure that travels with every reported
  number) — ruled [#24](https://github.com/tomerYannay/4UR4/issues/24),
  2026-07-26.** **Every artifact that reports backtest results** — the report
  shell emitted here, any file, table, chart, alert, export or API field derived
  from it, and any later phase's re-use of it — carries **in the artifact
  itself**, not only in a note or a README:
  1. that the universe is **4UR4's own methodology, the 4UR4 US Large-Cap 500**,
     together with the **rule-set version(s)** the run used (UNIV-METH item 6);
  2. that it **is not the S&P 500** and is **not endorsed by, affiliated with,
     sponsored by, or equivalent to S&P Dow Jones Indices**; and
  3. that **results are therefore not comparable to published S&P 500 strategy
     results** — a mechanical top-500 rule cannot reproduce a committee's
     discretionary membership (profitability screens, float, sector balance,
     judgement), so a difference in results is not evidence of a difference in
     strategy.

  **This is enforced, not documented.** The harness **fails** rather than emits
  an undisclosed report, in exactly the shape the Confidence-v1 disclaimer
  enforcement takes in Phase 5 — a machine-checkable property of the output, with
  a test that an undisclosed report cannot be produced. **UNIV-DISC binds Phases
  4, 5, 6, 7 and 8** wherever a backtest, lift, or calibration number is
  reported, and a later phase may not re-emit a Phase-4 number stripped of it.
- **Dependencies:** Phases 1–3; **HD-07**; **HD-18** (universe definition);
  Phase 1 **UNIV-METH**.
- **Evidence required:** A reproducible backtest run (fixed snapshot → identical
  report); survivorship-bias-free universe evidence; **an emitted report carrying
  the UNIV-DISC disclosure, plus a passing test that a report without it cannot
  be produced**; CI green.
- **Major risks:** Survivorship bias (R-3); backtest non-reproducibility if
  snapshots not pinned; **results read as S&P 500 results by a reader who never
  saw the methodology — the single failure mode UNIV-DISC exists to prevent, and
  the reason it is enforced in the artifact rather than promised in prose**.

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
  for the win/loss validation) **and reported under UNIV-DISC (Phase 4)** — the
  lift figure is a backtest result on the 4UR4 US Large-Cap 500 and carries the
  universe/non-comparability disclosure in the artifact, enforced by the same
  mechanism as the `score_kind` disclaimers.
- **Dependencies:** Phases 2–4; **HD-04**; **HD-05** (for lift validation labels);
  **HD-18** + Phase 4 **UNIV-DISC** (for any reported lift figure).
- **Evidence required:** Passing confidence fixtures; no-sentiment assertion test
  (CF-EV-03); a lift report on historical breakouts **carrying the UNIV-DISC
  disclosure**; CI green.
- **Major risks:** Mis-presentation as probability (R-4); premature sentiment
  inclusion (R-6, GOV-014).

### Phase 6 — Internal dashboard & alerts  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Internal read-only dashboard rendering scans, lines, states, and the
  **decomposed** confidence score; internal alerting on new confirmed events.
- **Entry criteria:** Phases 4–5 exit met; thin read-model `api/` designed; freeze
  lifted for this scope.
- **Exit criteria:** Analyst can inspect any name's line, state, breakout, retest,
  and full score decomposition; internal alerts fire on new confirmed events;
  **any backtest, lift or calibration figure the dashboard surfaces carries the
  UNIV-DISC disclosure (Phase 4)**, and the universe is labelled **4UR4 US
  Large-Cap 500** wherever it is named — never as the S&P 500.
- **Dependencies:** Phases 4–5; `api/` + `db/` read models; **HD-18** +
  **UNIV-DISC** for any surfaced backtest figure.
- **Major risks:** Explainability regressions (decomposition not surfaced);
  scope creep into SaaS features prematurely (GOV-007); **a UI that re-renders a
  Phase-4 number with its disclosure stripped**.
- **Evidence required:** UI rendering tests against known fixtures; an alert-fired
  audit record; **a rendering test that a surfaced backtest figure carries its
  UNIV-DISC disclosure**; CI green.

### Phase 7 — SaaS MVP  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Turn the internal dashboard into a paid SaaS: auth, subscription-scoped
  queries, subscription **alert** delivery (email first), billing.
- **Entry criteria:** Phase 6 validated; **HD-10** SaaS PII/billing security review
  complete; **HD-08/HD-09** resolved for any user-facing sentiment display and its
  redistribution rights; freeze lifted for this scope.
- **Exit criteria:** A subscriber can register, subscribe, and receive alert cards
  with mandatory disclaimers; billing via a third-party processor; PII minimized.
  **User-facing surfaces name the universe as the 4UR4 US Large-Cap 500 and never
  as, or as equivalent to, the S&P 500**; any performance or backtest claim shown
  or marketed carries the **UNIV-DISC** disclosure (Phase 4).
- **Dependencies:** Phase 6; **HD-10**; **HD-08/HD-09** (only if sentiment is
  displayed); provider redistribution rights (data R7); **HD-18** (universe
  naming) + **UNIV-DISC**.
- **Evidence required:** Auth/billing integration tests; a delivered alert with
  disclaimer; **a review record confirming no user-facing or marketing surface
  names the product as an S&P 500 product or implies S&P Dow Jones Indices
  endorsement or equivalence**; a passing security/privacy review record; CI green.
- **Major risks:** PII/billing compliance exposure (R-7); data redistribution
  licensing (NFR-8); **index-mark and constituent-data exposure if any surface
  reverts to S&P 500 branding — the exposure HD-18 was taken to remove
  ([`survivorship-bias-findings.md`](survivorship-bias-findings.md) §4.1)**.

### Phase 8 — Machine-learning confidence  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** A supervised Confidence v2 trained on captured features (confidence §5)
  with triple-barrier labels (confidence §6), backtested before shipping. This is
  where **sentiment may finally enter the score** — only if it improves calibration
  AND a human approves (GOV-014 §7).
- **Entry criteria:** Phases 4–5 produce a labeled historical dataset; **HD-05**
  label thresholds approved; **HD-08** (sentiment→score) evidence + approval **if**
  sentiment is a candidate feature; freeze lifted for this scope.
- **Exit criteria:** v2 model versioned and coexisting with v1; out-of-sample
  backtest meets calibration/reliability targets (confidence §7) **and is reported
  under UNIV-DISC (Phase 4)**, recording the universe rule-set version(s) the
  training and out-of-sample windows ran under; if sentiment is included, the
  Sentiment-Before-Evidence rule (calibration lift + human approval) is satisfied
  with attached evidence.
- **Dependencies:** Phases 4–5; **HD-05**; **HD-08** (for any sentiment feature);
  **HD-18** + **UNIV-DISC** (reported calibration figures).
- **Evidence required:** Out-of-sample calibration/reliability report; model
  version registry entry; with-vs-without-sentiment comparison **if** applicable;
  a feature-flag/kill-switch demonstration; CI green.
- **Major risks:** Over-fitting / look-ahead bias; unproven sentiment inflating
  trust (R-6, GOV-014); mis-calibration presented as probability (R-4).

### Phase 9 — Scale & expansion  ·  **Blocked: build-freeze (GOV-015)**

- **Goal:** Grow beyond the **4UR4 US Large-Cap 500** daily-batch MVP as measured
  demand justifies: broader universes, additional channels, and (only if a
  measured bottleneck exists) horizontal scaling / a service split along the
  existing module seams.
- **Entry criteria:** SaaS validated (Phase 7) with demand/scale evidence; specific
  expansion approved as its own roadmap item; freeze lifted per-scope. **A change
  to the intended market segment — a different universe size, asset class, or
  listing venue — is a product-definition change and remains Product Owner-gated
  under HD-18**; it is outside HD-17's bounded delegation, and no agent may take
  it. Extending the *rule set* (a new versioned rebalance or liquidity rule inside
  the same segment) is the reversible case; changing the segment is not.
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
| 2026-07-23 | Roadmap created, empty, under build-freeze. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-24 | MVP roadmap (Phases 0–9) drafted. **Approved as a baseline** under [GOV-013](../governance/approval-gate.md): *"The current Phase 0–9 roadmap baseline is APPROVED under GOV-013."* Baseline only — it does **not** lift GOV-015, authorize product implementation, select a provider, or authorize spend or licensing. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-26 | **Fixture-coverage reconciliation ([#19](https://github.com/tomerYannay/4UR4/issues/19)).** Phase 0/2/3/5 exit criteria no longer enumerate fixture IDs. Phase 2 and Phase 3 now gate on *every* committed fixture, split by the derived predicate `confirmed_bar == null`; Phase 5 defers to `confidence-specification.md` §11. The old enumeration covered 12 of the committed golden fixtures and omitted the HD-11/SC-2, HD-13 and HD-14 evidence. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) — part of the approved baseline |
| 2026-07-26 | **E2-AUTHOR added as a Phase 2 *entry* criterion ([#20](https://github.com/tomerYannay/4UR4/issues/20)).** Gives HD-15 condition 2 (clean-room authorship w.r.t. `tools/fixture-replay.mjs`) a mechanism, and makes Phase 2 entry depend on [#21](https://github.com/tomerYannay/4UR4/issues/21). No freeze lift; [GOV-015](../governance/build-freeze.md) unchanged and still ON. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) — part of the approved baseline; superseded in detail by the E2-AUTHOR-A/B restatement below |
| 2026-07-26 | **Two further stale enumerations of the same defect class, found while doing the above and fixed here.** Phase 0's goal said the fixture set was "GX-01..12, CF-EV-01..07"; Phase 5's goal said the Confidence v1 component set was "C1–C7". Both had drifted: 23 golden fixtures are committed, `confidence-specification.md` §11 defines CF-EV-01..09, and HD-03/HD-05 revised the component set to C1–C8. All three now defer to their source instead of restating it. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) — part of the approved baseline |
| 2026-07-26 | **RM-01 added to the Phase 2 exit gate** (Steward judgement call beyond the literal text of #19, now ruled). It was in no phase gate at all; its OHLCV is committed, so this adds no Phase 1 dependency. **Ruled rationale (adopted verbatim):** *"RM-01 is part of the Phase 2 exit gate as the committed real-market, non-circular conformance fixture."* | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-26 | **Wick-break (§14) reassigned from the Phase 3 goal to Phase 2** (Steward judgement call beyond the literal text of #19, now ruled). **Ruled rationale (adopted verbatim), which replaces the one originally recorded:** *"Wick-break belongs in Phase 2 because it is evaluated while the structure remains ACTIVE and does not itself perform an ACTIVE → BROKEN_OUT state transition. Phase 3 remains responsible for confirmed breakout, retest, failure and expiry behavior."* | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-26 | **Baseline approval recorded, with its four exclusions stated up front** ([#23](https://github.com/tomerYannay/4UR4/issues/23)). Title, STATUS block, phases heading and Phase 0 entry criteria no longer say PROPOSED/pending. A prominent block states that approval does **not** lift [GOV-015](../governance/build-freeze.md), authorize product implementation, select a provider, or authorize spend or licensing; `build_freeze: ON` and `autonomous_implementation: DISABLED` are unchanged. **HD-13 retained in full** (no clause struck) and **HD-15 conditions 1–3 retained in full**. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-26 | **Phase 1 research is Ready; the build is not** ([#23](https://github.com/tomerYannay/4UR4/issues/23)). Issues [#4](https://github.com/tomerYannay/4UR4/issues/4) and [#5](https://github.com/tomerYannay/4UR4/issues/5) (tickets c and d) recorded as **Ready** at autonomy level **`research-only (freeze-permitted)`**, satisfying their DoR note. **#4's provider *selection* stays human-gated**: research may proceed, but **HD-06 remains PENDING** and is the only instrument that may select a provider or commit spend or licensing. No freeze lift; ticket (e) stays blocked. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-26 | **E2-AUTHOR restated around HD-15 condition 2 as sharpened** ([#23](https://github.com/tomerYannay/4UR4/issues/23); [#20](https://github.com/tomerYannay/4UR4/issues/20)). The testable criterion is now **E2-AUTHOR-A**, a property of the **artifact** — `engine/` must not *import, copy, execute or mechanically translate* the reference model, checkable against the code that exists. The read-restriction becomes **E2-AUTHOR-B**, retained as the **preventive control** rather than the evidence, since a session's read-history is unverifiable after the fact; **where they diverge, A governs**. The mechanism grows from four parts to five, with **#20 named as an explicit precondition for Phase 2 implementation beginning**. No freeze lift; GOV-015 unchanged and still ON. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-26 | **Universe redefined as the self-computed 4UR4 US Large-Cap 500** ([#24](https://github.com/tomerYannay/4UR4/issues/24), HD-18). Every use of "S&P 500" as 4UR4's universe is replaced (Phase 1 goal, Phase 4 goal, Phase 9 goal); the name survives only where the index is deliberately *not* used or is an external reference, with the reason stated in place. Two new named gates: **UNIV-METH** (Phase 1 exit — versioned eligibility/ranking rules, point-in-time membership, delisted names preserved, adds/removes with effective dates and evidence, bias absence demonstrated, rule set independently versioned and backtestable; design in `docs/architecture/universe-methodology.md`, which is design, not implementation) and **UNIV-DISC** (Phase 4 exit, binding Phases 4–8 — every reported backtest number carries, in the artifact, the 4UR4 methodology + rule-set version, the non-endorsement statement, and the fact that **results are not comparable to published S&P 500 strategy results**, enforced by a failing harness rather than by prose). Rationale: index membership is licensed separately and more restrictively than prices (separate MSA, separate fees; SPDJI withdrew constituents from Compustat in 2020), and the two best survivorship-free datasets (Norgate, CRSP) are licence-barred from commercial use. **No freeze lift; GOV-015 remains ON; HD-06 remains PENDING; no provider selected and no spend or licensing authorized.** | Product Owner ([#24](https://github.com/tomerYannay/4UR4/issues/24), 2026-07-26) |
| 2026-07-26 | **Phase 2 / Phase 3 boundary stated as a behavioural rule** ([#23](https://github.com/tomerYannay/4UR4/issues/23)). Phase 2 owns behaviour evaluated while the structure remains `ACTIVE` that performs no `ACTIVE → BROKEN_OUT` transition; Phase 3 owns confirmed breakout, retest, failure and expiry. The `confirmed_bar == null` partition is **demoted to corroboration** and retained only as the mechanical selector over fixture data. Rationale: the partition is contingent on tolerances the spec declines to fix — GX-12 (one of the five `WICK_BREAK` fixtures) leaves the `confirmed_bar == null` partition at the 0.5× sweep point, and GX-15 gains both a wick-break and a breakout below its documented boundaries — whereas the behavioural rule does not. | APPROVED ([#23](https://github.com/tomerYannay/4UR4/issues/23), 2026-07-26) |
| 2026-07-26 | **RM-01's Phase 2 numeric acceptance values marked `UNDER REVIEW — pending HD-20`. Suspension and disclosure only — nothing is resolved.** Replayed **as-of-time** (§21 / HD-12 / D-TL-11) from the committed OHLCV, RM-01 yields a **confirmed breakout at bar 10 (2026-06-29)**, margin `0.0864461` log units, while its approved record — a **full-series** hull, `B* = (25, 129.88)`, slope `-0.0240143` — reports none. Both are arithmetically correct about different objects, exactly as §21.4's non-normative corollary predicts, so the gate's `confirmed_bar == null` target is **provably unsatisfiable by a spec-conforming engine**. Derived independently three times to 6 significant figures; not suppressible by tolerance (`eps_break` would need ≈ 8.6× the documented value, and HD-13 forbids resolving fixture outcomes by tolerance regardless). Structural cause, recorded as a gap rather than an incident: **no mechanical guard has ever covered RM-01** — `check-evidence.mjs` only schema-validates its annotation and `fixture-replay.mjs` does not replay it at all. **The Product Owner ruling that RM-01 is part of the Phase 2 exit gate stands and is untouched**; only the Steward-drafted acceptance values are suspended. Disclosure: [`fixtures/README.md`](fixtures/README.md) §6b. | **NOT APPROVED — pending Product Owner ruling (proposed HD-20).** Recorded by the Product Steward at the direction of the Strategic Product Reviewer under its [HD-17](human-decisions.md) bounded delegation; disclosure and suspension only, no decision taken |
