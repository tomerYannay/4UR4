# 4UR4 — Project State (canonical, current-state only)

> **Current state only — not a history log.** **Content owner: Product Steward.** The
> **Orchestrator** ensures this file is updated after: a phase completes · a Product Owner
> decision is recorded · a roadmap phase changes · a major PR merges · a build-freeze scope
> changes. The **Strategic Product Reviewer** reads and validates this file but **may not
> edit** it. If it is stale or contradicts stronger evidence, that is flagged, not silently
> fixed. Precedence when sources disagree: latest PO decision on GitHub →
> [`human-decisions.md`](human-decisions.md) → [`requirements.md`](requirements.md) + specs →
> [`roadmap.md`](roadmap.md) → merged fixture evidence → open PR proposals → agent summaries.

- **Last updated:** 2026-07-27
- **Last reviewed commit SHA (main):** `ed92bbb` — the merge commit of
  [PR #33](https://github.com/tomerYannay/4UR4/pull/33). [PR #32](https://github.com/tomerYannay/4UR4/pull/32)
  merged immediately before it at `758c0a0`, in that order deliberately: #32's commits are
  ancestors of #33's, so merging #33 first would have landed the quarantine control on `main`
  under the engine PR's number. CI is **green on `main` at `ed92bbb`**.

  **Both were merged by the Product Owner personally, through the GitHub UI**, and that is
  the substance of the authorization rather than a procedural detail — see
  [#34](https://github.com/tomerYannay/4UR4/issues/34). No agent can produce an approval
  artifact distinguishable from one it wrote itself, so **the act of merging is the approval**.
  **Deviation to record for the Auditor:** [GOV-005](../governance/definition-of-done.md) says
  "merged by Release & Ops only", with no agent qualifier in the clause itself. **This file
  does not reinterpret it.** An earlier draft said the clause "scopes *agents*" — that was an
  interpretation presented as a statement of meaning, with no decision record, three screens
  from a section quoting the Strategic Reviewer approvingly: *"a precondition that is quietly
  reinterpreted is not a precondition."* The same standard applies here. **Recorded as a
  deviation, for the Auditor and the Product Owner to dispose of.** What stands on its own:
  the Release & Ops gate refused both merges precisely because no authorization channel
  existed, and its refusals were correct each time.

  **Provenance of "merged by the Product Owner personally":** the API confirms
  `mergedBy.login = tomerYannay` for both, which is all it can confirm. Per
  [#34](https://github.com/tomerYannay/4UR4/issues/34), no artifact under this single identity
  distinguishes a Product Owner act from an agent act. This rests on the Product Owner's own
  statement, and is recorded as such rather than as independently verified.

  **The gate now runs five checks**, not four: `tools/validate.mjs` ·
  `.claude/hooks/bash-guard.test.mjs` (329 assertions) · `tools/fixture-replay.mjs --all` ·
  `tools/check-evidence.mjs` · **`python3 -m engine.tests.run_all` (136 tests)** — plus a
  **fixture-immutability guard** that fails any PR touching `engine/` that also modifies or
  deletes committed fixture data.
- **Build-freeze status:** **ON everywhere except Phase 2 `engine/` work**
  ([GOV-015](../governance/build-freeze.md)). A **Product Owner ruling on
  [#31](https://github.com/tomerYannay/4UR4/issues/31) (2026-07-26)** **LIFTS the freeze for
  Phase 2 `engine/` work only**: the deterministic engine, fixture and RM-01 conformance
  tests, engine-local test infrastructure, and minimal shared types. **Not authorized:**
  provider integration, live data, API, database, scanner, worker, dashboard, alerts, SaaS
  surfaces, and anything touching spend, licensing, privacy, billing or deployment. **For
  everything else the freeze stays ON.** Conditions on the lifted scope: the engine is
  **independently authored** from the reference model and must not import, execute or
  mechanically translate it (HD-15 condition 2 / E2-AUTHOR); it must pass **23/23 golden +
  RM-01**; it must preserve **HD-11…HD-20**; and it must be deterministic and free of
  look-ahead bias. **Propagation is complete and is on `main`** (it landed with PR #31's ruling
  record, not with the PR currently open — a deictic that outlived its PR, same class as M-01/M-02)**:** the ruling is recorded
  as **HD-22** in [`human-decisions.md`](human-decisions.md), and
  [`../governance/build-freeze.md`](../governance/build-freeze.md) carries the scoped-lift
  section with `scope: ["engine/"]`, `autonomous_implementation: ENABLED_FOR_SCOPE` and a
  named `lifted_by`. The scope is **machine-enforced**: `tools/validate.mjs` guards `engine`
  alongside every other listed product-code directory and permits one **only** when the
  marker names it, so deleting the scope entry re-freezes `engine/` on the next CI run.
  **Full branch protection on `main` is required before any Phase 2 product code merges**
  — *and 6 of its 7 parts are in force while part 3 (required exact-head reviews) is UNMET and
  ruled a recorded deviation; Phase 2 product code merged at `ed92bbb` under that ruling. Read
  with [`human-decisions.md`](human-decisions.md) → HD-22 part 3. The matching passage in the
  register got this cross-reference; this one did not, in the same commit.*
  (same ruling).

## Product objective
- **Final:** a reliable commercial SaaS that detects ATH-anchored logarithmic descending
  resistance lines, identifies breakouts and retests, produces explainable confidence
  scores, adds market context, and eventually delivers subscription alerts.
- **Current MVP:** prove the detector can **reproducibly** identify the intended canonical
  trendline and breakout state on **historical market data** before building dashboard,
  alerts, billing, or ML.
- **Universe (HD-18, 2026-07-26,
  [#24](https://github.com/tomerYannay/4UR4/issues/24)):** 4UR4 computes its **own
  point-in-time universe**, the **4UR4 US Large-Cap 500**, under transparent versioned
  rules. It **is not the S&P 500**, is not licensed constituent membership, and is not
  endorsed by or equivalent to S&P Dow Jones Indices. The cost is stated with the benefit:
  **4UR4 backtest results are not comparable to published S&P 500 strategy results**, which
  the Phase 4 **UNIV-DISC** gate requires to travel with every reported number. Design:
  [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
  (design, not implementation).

## Current phase
**Phase 0 → Phase 1 boundary.** Phase 0 (specification & golden examples) is substantially
complete and Phase 1 (market-data foundation) is in its **research** stage; Phase 1
implementation remains **freeze-blocked**.

**Phase 2 — the engine is BUILT and on `main`; the exit determination is OWED.** These are
two different statements and this file keeps them apart deliberately.

*What is delivered and mechanically enforced* (`engine/`, 27 files, merged at `ed92bbb`):
the deterministic pre-breakout engine reproduces **all 23 golden fixtures and RM-01** —
anchors, `sig6` slope/intercept, line values at every recorded index, formation traces with
F1/F2/F3 evaluated independently, §18 input guards, every pre-breakout re-selection, and
both RM-01 clauses with the stop index **derived by the engine, never read from the fixture**.
136 tests — **2,525 field comparisons across the 23 golden fixtures and 142 more on RM-01** (instrumented by Code Review; the bare figure `2,525` previously appeared with no artifact emitting it and was uncitable under GOV-006) — inside the **required** CI check. Determinism is asserted
across varied `PYTHONHASHSEED` in a child process. Look-ahead is structurally prevented: the
`Prefix` value object is exactly `t` bars long and geometry never receives the series.

*What is NOT thereby true.* **No agent has declared Phase 2 exit met, and none may** — that
is a [GOV-002](../governance/roadmap-authority.md) roadmap determination owned by the Product
Steward, on a gate assessment, not an inference from a green suite. **E2-AUTHOR criterion 1
is MET** — [#20](https://github.com/tomerYannay/4UR4/issues/20) **CLOSED** at
`2026-07-26T23:17:13Z`, `stateReason: COMPLETED`, by PR #32's merge, and the roadmap's own
wording is *"until it closes this criterion is unmet"*. **Criterion 5 — the independence
attestation — remains unmet**, and the roadmap states it is unsatisfiable while
[#21](https://github.com/tomerYannay/4UR4/issues/21) is open; it is recorded as **disclosed
rather than satisfied**. *(An earlier draft of this paragraph said "two … remain formally
unmet" and named criterion 1 among them. False — it re-asserted the very stale reading this
refresh exists to correct, two paragraphs before correcting it. Caught by Code Review.)*
**At least one further criterion is not cleanly met and is not counted above:** criterion 2
requires the Ready ticket to carry both halves, and #7 never reached Ready. The Product Owner ruled that
E2-AUTHOR-A governs and must not block Phase 2 indefinitely; **that unblocked the work, it
did not retroactively satisfy the criteria.**

*Also true, and it limits what the 23 prove:* seven of the twenty geometry fixtures share
bars 0–15 byte-identically and five share `B* = (6,93)`. **Twenty fixtures are not twenty
independent samples.** Two mutations (M-1, M-2) were found to **survive the committed
corpus** and were recorded as findings with constructed adversarial cases rather than
absorbed — no fixture was added, edited or reinterpreted to accommodate them. RM-01 is the
only committed evidence that the specification captures the object the Product Owner actually
drew, and **only its Half A is non-circular**; Half B is replay-generated and earns
conformance credit only (SPR-D-03's mandatory rider).

**M-09 is CLOSED** by [SPR-D-03](human-decisions.md), condition-10 CONFIRMED.
[#19](https://github.com/tomerYannay/4UR4/issues/19) is **CLOSED** and no longer blocks.
[#20](https://github.com/tomerYannay/4UR4/issues/20)'s configuration half is on `main`;
[#21](https://github.com/tomerYannay/4UR4/issues/21) and
[#34](https://github.com/tomerYannay/4UR4/issues/34) remain open and are the same root cause.

**Phase 0 exit is clean.** The defect that once qualified it — **GX-08 as committed**
encoding a precondition **HD-11 forbids** — was corrected by PR #18: GX-08 expects the
all-highs upper-log-hull result `B* = (1, 98)`, GX-20 covers the still-reachable
`NO_VALID_SECOND_ANCHOR` case, and the pivot-conditioned text was swept. **HD-12, HD-13 and
HD-14 are APPROVED — RATIFIED; HD-15 is APPROVED**, in one ruling recorded as a citable
artifact
([2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012), given
against head `2651cd0`), with HD-13 ratified *as recorded* including the four clauses its
entry enumerates as going beyond the escalated options:
- **HD-12** — anchor selection is **rolling, causal, as-of-time**, frozen at a confirmed
  breakout. The whole fixture set was re-derived as-of-time and re-verified mechanically.
- **HD-13** — `eps_break` stays unlocked; ordinary fixtures must be tolerance-robust, with
  GX-15 alone retained as the boundary fixture.
- **HD-14** — formation gates are first-class, `k`-independent parameters
  `min_formation_bars = 8` / `min_ath_age_bars = 3`.
- **HD-15** — the causal reference model is permitted under GOV-015 as **Phase-0 evidence
  tooling**, conferring **no Phase-2 credit**, and requiring that the Phase-2 engine be
  authored by an agent that has not read it. HD-15 clarifies the scope of one file and
  **lifts nothing**; its condition-2 independence requirement is carried forward intact
  by the #31 ruling.

## Completed milestones
- Agent Operating System bootstrapped + executable in Claude Code (PR #1).
- Proposed MVP roadmap, PRD, specs, human-decision register (PR #8).
- **Phase 0 golden fixtures** (**23 synthetic** — 20 geometry + 3 null-anchor, after the #16
  correction and the HD-12 as-of-time audit added GX-20 and the formation-gate regressions
  GX-21/GX-22/GX-23, and moved GX-08 into the geometry set) + **RM-01** real-market case,
  PO-approved; **SC-1 = MATCH**, **SC-2 resolved (HD-11)** (PR #9; fixtures corrected under #16).
  *Counted from disk on 2026-07-26: `product/fixtures/golden/` holds exactly 23 fixture
  directories, `GX-01`…`GX-23`, each with `input.csv` + `expected.json`, plus `real/RM-01/`.*
- **[PR #18](https://github.com/tomerYannay/4UR4/pull/18) MERGED** as `e56ed8e` — the Phase 0
  evidence correction and the HD-12 as-of-time fixture audit. The **23 golden fixtures
  (GX-01…GX-23)** reproduce **exactly** under as-of-time replay in CI. Landed with it: spec
  §21, D-TL-11, D-TL-12, GX-20, the HD-14 formation-gate regressions GX-21/GX-22/GX-23, and
  `tools/fixture-replay.mjs` (permitted under HD-15).
- **Roadmap fixture-coverage reconciliation** (Refs #19, #20), on `main` at `83b0fcc`: Phase
  2/3 exit gates cover the **whole** committed fixture set via a derived partition instead of
  a typed fixture list, and HD-15 condition 2 has a Phase-2 **entry** mechanism (E2-AUTHOR).
  See [`roadmap.md`](roadmap.md). Roadmap **APPROVED as a baseline** under GOV-013
  ([#23](https://github.com/tomerYannay/4UR4/issues/23)) — a baseline only: it lifts no
  freeze, authorizes no implementation, selects no provider and approves no spend.
- **[PR #25](https://github.com/tomerYannay/4UR4/pull/25) MERGED** as `d1a1c41` — the **HD-18
  universe definition** and
  [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md),
  the **Phase 2 implementation plan**, the **HD-06 due-diligence pack**, the **HD-21**
  delegation record and the **SPR-D-01** propagation into
  [`roadmap.md`](roadmap.md), [`fixtures/README.md`](fixtures/README.md) §6b and the RM-01
  artifacts. **Documents only; no product code, no freeze lift.** Landed after **four
  correction rounds** (`9ef30b7` → `c5606e6` → `5522694` → `34df259`), each closing a full
  Verification / Code Review / Strategic Product Review pass. *(The #19 derived
  fixture-coverage gate and the #20 E2-AUTHOR entry criterion reached `main` earlier, at
  `83b0fcc` — the merge's first parent — not via this PR. Both are on `main` either way.)*
- **[PR #30](https://github.com/tomerYannay/4UR4/pull/30) MERGED** as `54b16ee` — **RM-01 is
  now under mechanical causal replay**, for the first time. It delivered
  [`fixtures/real/RM-01/expected-causal.json`](fixtures/real/RM-01/expected-causal.json),
  a **new, separate** [`fixtures/schema/real-causal.schema.json`](fixtures/schema/real-causal.schema.json)
  (deliberately not an edit to `real-annotation.schema.json`, and not a relaxation of the
  golden `fixture.schema.json`), the `real/`-reading extensions to
  `tools/fixture-replay.mjs` and `tools/check-evidence.mjs`, and
  [`maintenance-backlog.md`](maintenance-backlog.md). `fixture-replay.mjs --all` now reports
  **23/23 golden + 1/1 real** in CI, and a `real/` fixture directory carrying no expectation
  **fails** rather than being skipped. **The expectation is replay-generated:** it is a
  **regression guard against today's reference model, not independent verification**, and it
  cannot detect that the model itself is wrong — RM-01's non-circularity attaches to Half A's
  human-approved geometry and the real prices, never to Half B's provenance. Whoever authored
  it has read the reference model and is **disqualified** from authoring the Phase 2 engine.
- ChatGPT↔Claude **handoff protocol** + PR template + Agent Coordination Queue (#10) (PR #11).
- **Strategic Product Reviewer** added as the 10th permanent agent (PR #13).
- **Six-record documentation reconciliation** to merged evidence, docs-only (Refs #14); also
  committed the **Historical Product Owner Decision Record — RM-01** in
  [`human-decisions.md`](human-decisions.md), supplying the citable approval artifact PR #9
  lacked (PR #15).

## Active work
- **PR #12** — Phase 1 market-data research (Issues **#4**, **#5**): provider comparison +
  survivorship/delisted research. **Draft; CI green; 0 reviews; awaiting ChatGPT/strategic
  review** (round 1 of 2). This is the path to **HD-06**.
- **Issue [#20](https://github.com/tomerYannay/4UR4/issues/20)** — HD-15 condition 2 had no
  enforcement mechanism. **The document half is on `main`**: [`roadmap.md`](roadmap.md)
  carries **E2-AUTHOR** (A/B form, five conditions) as a Phase 2 *entry* criterion, with the
  design in
  [`../docs/architecture/phase2-independence-mechanism.md`](../docs/architecture/phase2-independence-mechanism.md).
  **The configuration half is now ON `main`** ([PR #32](https://github.com/tomerYannay/4UR4/pull/32),
  merged at `758c0a0`): `.claude/hooks/bash-guard.mjs` denies the `implementation-engineer`
  role the reference model, `product/fixtures/VERIFICATION.md` and the mechanism document, at
  tool level rather than by instruction, covered in both directions by the quarantine and
  evasion sections of the **329-assertion** `bash-guard.test.mjs` suite. *(329 is the suite
  TOTAL — it also covers the DANGER set, five role postures, `resolveRole` and permanent-agent
  registration — not the read-deny's own count. An earlier draft attributed the whole figure
  to the quarantine.)*

  **It no longer blocks Phase 2, and the reason is a Product Owner ruling, not the hook
  landing:** *"E2-AUTHOR-A is the authoritative Phase 2 independence criterion… The read-deny
  hook is preventive defense-in-depth only. It is not the proof of clean-room authorship and
  must not block Phase 2 indefinitely."* **E2-AUTHOR-A was assessed on the committed artifact
  by the Project Auditor at `f0455f6` and found SATISFIED** — no import, no execution, and
  structure, control flow, naming and constant derivation that diverge from the reference model
  at every point where they could have converged.

  **What is still owed, stated honestly:** criterion 5's independence *attestation* does not
  exist as a file, and the roadmap says in its own words that it is unsatisfiable while #21 is
  open. It is **disclosed, not treated as satisfied** — see M-35. And the E2-AUTHOR-B record
  for commit `7ab8075` is **ABSENT, not weak**: the orchestrating session authored 6 executable
  lines in `engine/` having read the reference model. The Auditor examined exactly those lines
  and found they move *further* from the model than the code they replaced.
- **Issue [#21](https://github.com/tomerYannay/4UR4/issues/21)** — review verdicts cannot
  become citable artifacts, and review attribution collapses to a single account. **Required
  before HD-06**, and a stated dependency of E2-AUTHOR **criterion 5** (the clean-room
  attestation has nowhere to live until #21 is fixed; criterion 4 is authorship/verification
  separation, and this line named it wrongly). It was also recorded as required
  before *any* freeze lift; **the #31 lift proceeded without it** — the Product Owner's
  prerogative, recorded here because the earlier condition should not silently disappear.
- **Issue [#22](https://github.com/tomerYannay/4UR4/issues/22)** — evidence-tooling follow-ups.
- **Traceability debt from [#16](https://github.com/tomerYannay/4UR4/issues/16)
  (the issue itself is CLOSED).** #16 was closed without ever being re-scoped to cover what
  PR #18 actually delivered (HD-12/13/14, spec §21, D-TL-11/12, three new fixtures, the
  reference model), so the ticket→PR traceability link remains incomplete (Project Auditor,
  GOV-007). **This survives as a documentation debt, not as an open ticket** — reopening #16
  is an Orchestrator decision, not a Product Owner one.

## Next milestone
**Determine Phase 2 exit, and resolve the attribution defect.** The engine is built, merged
at `ed92bbb` and enforced by the required CI check, so the previous milestone — *"unblock
Phase 2 entry and get the ticket to Ready"* — is spent. What actually remains:
**(a)** the Product Steward's **Phase 2 exit determination** under GOV-002, on a gate
assessment, which no agent may make; **(b)** [#21](https://github.com/tomerYannay/4UR4/issues/21)
and [#34](https://github.com/tomerYannay/4UR4/issues/34) — the single-identity attribution
defect, which now blocks *every* merge and is the stated blocker on E2-AUTHOR criterion 5;
**(c)** closing the HD-22 part 3 deviation, which requires a **second identity**.
*(Superseded and recorded: this paragraph previously asked to close #20 — CLOSED — rule M-09
— CLOSED by SPR-D-03 — and get full branch protection in place — ruled, with the deviation
recorded.)* In parallel, **complete the PR #12
Phase 1 research review**, the path to the **Product Owner decision on HD-06** — which
**#21** also gates. Phase 1 *implementation* and everything outside the `engine/` scope
remain freeze-blocked.

## Owed work — debts carried forward
Stated as **owed**, not done.

- **The RM-01 annotation schema was never updated.**
  [`fixtures/schema/real-annotation.schema.json`](fixtures/schema/real-annotation.schema.json)
  is **untouched**: it carries **no `causal_artifact` pointer** to the Half B record, and
  `confirmed_bar` is still described as *"HD-03: equals breakout_bar. NULL until data."* —
  a full-series description that says nothing about the as-of-time layer. *Verified on disk
  at this SHA.* A reader arriving at Half A alone is not told Half B exists. The rest of
  this debt is **discharged** by PR #30.
- **Deferred provenance-tense correction — two sites remain**, not the ~8 originally
  recorded. The circularity limit is resolved to its **true** value nearly everywhere (the
  Half B expectation **is** replay-generated and **is** model-derived). Residue:
  [`human-decisions.md`](human-decisions.md)'s SPR-D-01 *Rationale* still reads *"**if**
  `expected-causal.json` is replay-generated…"*, and the [`roadmap.md`](roadmap.md) SPR-D-01
  ledger row keeps the conditional form deliberately, as a **dated record marked rather
  than rewritten**.
- **Low-severity prose-precision findings are now tracked**, not carried here: see
  [`maintenance-backlog.md`](maintenance-backlog.md) (M-01…M-08 plus the PR #30 review set).
  **M-09 is CLOSED** by [SPR-D-03](human-decisions.md), condition-10 CONFIRMED; nothing in
  that file now blocks a milestone.
- **`main` IS branch-protected — 6 of HD-22's 7 parts, with the seventh open and blocked
  on [#21](https://github.com/tomerYannay/4UR4/issues/21).** Measured, not asserted:
  `enforce_admins: true` · PR-only merges · required check `Validate agent OS & governance`
  with `strict: true` · no force pushes · no deletions · direct push **empirically rejected**
  (`protected branch hook declined`). **The one gap: `required_approving_review_count: 0`**,
  so "required exact-head reviews" is **unimplemented, not partially met** — at count 0,
  `dismiss_stale_reviews: true` is inert because there is no review to dismiss. It cannot be
  fixed by raising the number: GitHub forbids a PR author from approving their own PR, and
  under one shared identity every PR is authored by that identity, so a count of 1 would make
  `main` permanently unmergeable and the predictable response would be to disable
  `enforce_admins` — trading a real protection for a theatrical one. **The constraint is #21,
  not the setting.** *"Full branch protection is in place" is not an available statement.*
  **The two gates reached opposite verdicts on the same question from different premises** —
  the Project Auditor said not blocking (the load-bearing protections are in place; the defect
  is #21 and is already ticketed), the Strategic Product Reviewer said blocking (HD-22 states
  it as a precondition on Phase 2 product code merging). **RESOLVED by the Product Owner on
  2026-07-26: not blocking, deviation recorded** — see
  [`human-decisions.md`](human-decisions.md) → HD-22 part 3.

  Historical, retained: `mergeStateStatus: CLEAN` on PR #25 and PR #30
  reflected the **absence of required checks, not their satisfaction** — agent discipline
  was the entire merge gate. **The Product Owner now requires full branch protection before
  any Phase 2 product code merges** ([#31](https://github.com/tomerYannay/4UR4/issues/31)),
  which converts this from a recommendation into a **precondition on the newly lifted
  scope**. Related to [#21](https://github.com/tomerYannay/4UR4/issues/21).
- **[#21](https://github.com/tomerYannay/4UR4/issues/21) remains required before HD-06.**
  Every gate on PR #25 and PR #30 — **including the GOV-013 merge authorization** — was a
  single-account relay, and the E2-AUTHOR clean-room attestation still has nowhere citable
  to live.

## Blocked work
- **#6** Market-data ingestion service (Phase 1 impl) — `blocked: freeze`. Outside the #31
  lift, which excludes provider integration and live data.
- **#7** Trendline detection engine (Phase 2 impl) — **the engine is BUILT and MERGED**
  (`ed92bbb`), passing all 23 golden fixtures and RM-01 under the required CI check. It never
  passed through a formal Definition of Ready, and that is recorded rather than smoothed over:
  the work proceeded on the Product Owner's #31 scope lift and the ruling that E2-AUTHOR-A
  governs. **What remains on this ticket is the exit determination, not the build** — a
  GOV-002 call for the Product Steward. #20 is CLOSED, M-09 is CLOSED (SPR-D-03), and branch
  protection is ruled with a recorded deviation; **#21/#34 remain** and gate E2-AUTHOR
  criterion 5. The RM-01 gate-value block is cleared by SPR-D-01 and the Phase 2 plan's S0
  dependency on HD-20 is satisfied.
- All of Phases 3–9, and every Phase 2 surface outside `engine/` (API, database, scanner,
  worker, dashboard, alerts, SaaS) — behind the build-freeze and their entry criteria.

## Pending Product Owner decisions
- **HD-06** — data-provider selection + recurring spend (**human-gated**). Research is
  delivered ([`data-provider-findings.md`](data-provider-findings.md),
  [`hd06-due-diligence.md`](hd06-due-diligence.md)); **Intrinio Startup is recorded as the
  leading candidate at ≈\$5,994 year 1 and is explicitly not selected.** Eight evidence
  prerequisites remain, **two marked blocking** — **C-1**, the only condition the Product
  Owner has accepted, and **C-2**, agent-*proposed* (as are C-3, C-4 and C-5; an agent may
  recommend a blocking condition, not impose one). C-2 is the sharpest: the candidate's
  history-depth claim is contradicted by its own upstream, and depth is the only ground on
  which it leads. [#21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band
  confirmation is required before any financial authorization. **HD-06 is untouched by the
  #31 lift**, which authorizes no provider integration, no live data and no spend — verified
  against the register, where HD-06 is still marked `PENDING`.

**HD-06 is the only pending *HD-numbered* Product Owner decision — and that is not the same
as the only open question.**
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
§11.2 still escalates **OQ-U1…OQ-U7** to the Product Owner **with stated defaults**
(ADRs/non-US listings; exactly 500 vs a buffer band; REITs; whether R9 point-in-time shares
outstanding is opened and whether spend attaches; backtest window depth; first-class universe
disclosure on user-facing surfaces; and the provisional 4UR4-minted `security_uid`). Those
are open Product Owner questions, not HD entries. Both claims must travel together; only the
first is true on its own.

*Resolved 2026-07-25 and no longer pending:* **HD-12**, **HD-13** and **HD-14** ratified, and
**HD-15** approved — one ruling, recorded as a citable artifact
[on #16](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012) against head
`2651cd0`. **That ruling lifted no part of GOV-015** — the only lift on record is the #31
Phase-2-`engine/` lift above.

*Resolved 2026-07-26 and no longer pending:* **HD-16** (roadmap baseline approved),
**HD-17** (bounded delegation for reversible ambiguity — **superseded and widened by
HD-21**), **HD-18** (the self-computed **4UR4 US Large-Cap 500** universe), **HD-19**
(independence checker permitted as verification tooling), **HD-21** (bounded delegation —
below), and **HD-20**, which was **not** resolved by the Product Owner but by the delegated
decision **SPR-D-01** under HD-21 — see the next section. **None of these lifts GOV-015,
selects a provider, or authorizes spend or licensing.**

## Delegated product decisions (HD-21) — a second decision channel

- **HD-21 — APPROVED (Product Owner, 2026-07-26,
  [#27](https://github.com/tomerYannay/4UR4/issues/27)).** The permanent **Strategic Product
  Reviewer** may decide **reversible product-definition questions** autonomously under **ten
  conjunctive conditions**, with a mandatory record format and the decision marked
  `DELEGATED_PRODUCT_DECISION_APPROVED`. It **supersedes and widens HD-17**. **Condition 10
  differs in kind:** the **Project Auditor** — read-only, and not the producer of the work —
  must independently confirm the delegation conditions were met, so every delegated decision
  carries **two** records: the decision, and an independent confirmation of authority.
  **Never delegated:** HD-06 purchase or spend, licensing, lifting or widening GOV-015,
  roadmap phase-order changes, core-thesis or target-customer changes,
  security/privacy/billing/PII, irreversible external actions, and **deletion of any
  important evidence or historical decision record** — nothing delegated permits removing a
  record, only adding to or superseding one. **HD-21 lifts nothing and makes HD-06 no more
  decidable than before.**
- **SPR-D-01 — RM-01 carries both analytical layers · resolves HD-20.**
  **Approved under bounded Product Owner delegation; not direct Product Owner authorship** —
  **not** a Product Owner ruling, and **overturnable by the Product Owner at any time without
  cause.** Decided by the Strategic Product Reviewer under HD-21 on the evidence of
  [#26](https://github.com/tomerYannay/4UR4/issues/26), and **CONFIRMED against all ten
  conditions by the Project Auditor at `5b99ba6`** *(Relayed, not independently authored —
  see the provenance note in [`human-decisions.md`](human-decisions.md) → SPR-D-01:
  role-level independence, not organizational, pending
  [#21](https://github.com/tomerYannay/4UR4/issues/21).)* RM-01 now carries **two records,
  neither superseding the other**: **Half A**, the full-series geometry, retained
  **verbatim** and gated at **unit level** on an exported pure §8 function — explicitly
  **not** on pipeline output; and **Half B**, the as-of-time record (engine-derived stop at
  **bar 10**, `line_at_stop` `B* = (9, 158.40)`, `m = -0.0505453`, line `150.593`, close
  `164.19`, margin `0.0864461` *(raw clearance `ln(close) − ŷ`; the reference model's
  `events[].margin` field carries `0.0764461`, the same quantity net of `ε_break`)*), gated
  **within Phase-2-owned behaviour only** — asserting `line_at_stop`, **not** `Λ^F`, and
  **no** `BROKEN_OUT` state and **no** `BREAKOUT_CONFIRMED` reason code, which remain
  Phase 3's. **Half B narrows RM-01's Phase-2 assertable surface** to bars **0–9** plus the
  stop index, so *"the gate is strengthened"* is true of the gate as a whole and **false of
  RM-01**. RM-01's non-circularity attaches to **Half A's human-approved geometry and the
  real prices**, not to Half B's provenance. **The Half B artifact now exists** and is
  asserted by `fixture-replay.mjs --all` (PR #30). The 2026-07-25 Product Owner approval, SC-1, SC-2/HD-11, `annotation.json`'s
  values and the **golden fixtures** are all unchanged; parameters stay at their ratified
  HD-14/D-TL-12 values. **No GOV-015 clearance is granted by it.** Gate wording:
  [`roadmap.md`](roadmap.md) Phase 2 exit criteria; evidence:
  [`fixtures/README.md`](fixtures/README.md) §6b.
- **Sequencing rule, binding on SPR-D-02 onward:** a delegated decision's status line reads
  `RESOLVED — pending condition-10 audit` until the Project Auditor confirms it, and only
  then is promoted.
- **SPR-D-03 — STANDS. M-09 is CLOSED.** `product/fixtures/real/**` is classified **R2b
  PERMEABLE by necessity**, with a mandatory no-credit rider. **Condition-10 CONFIRMED by the
  Project Auditor against all ten HD-21 conditions**, and — a first for this register — the
  decision was written to [`human-decisions.md`](human-decisions.md) **before anything cited
  it forward**, which is the sequencing rule SPR-D-01 broke and SPR-D-02 died on. The audit
  also recorded three corrections to the record itself (F-1 under-claim, F-2 the §10 author
  brief's `golden/** only`, F-3 a prescription written as fact); all three are applied.
  **Scope: M-09 only. It does not clear Phase 2 entry.**

  Superseded, retained because the reversal must stay visible:

- **SPR-D-02 — DOES NOT STAND.** A ruling on whether `real/**` is R2 *permeable* in the
  independence quarantine table was proposed in the PR #30 strategic review, but the
  **Project Auditor returned NOT CONFIRMED** under **HD-21 condition 10**: the decision was
  **never written to [`human-decisions.md`](human-decisions.md)** while a
  [`maintenance-backlog.md`](maintenance-backlog.md) row already cited it forward — the
  sequencing rule above, broken on its first use. *Verified on disk: the register carries no
  SPR-D-02 entry.* **M-09 therefore remains open**: `phase2-independence-mechanism.md`
  classifies `golden/**` and says nothing about `real/**`, so quarantining
  `expected-causal.json` — the B-clause conformance target — from the engine author is a
  **de facto quarantine no decision record ratifies**. It runs in the restrictive direction,
  so E2-AUTHOR is not weakened, but it decides what the engine author may read and **must be
  ruled before the Phase 2 ticket meets its Definition of Ready** (E2-AUTHOR / #20 AC-9).

## Open issues / PRs (governed index)
- **OPEN issues (13)** — verified against `gh issue list` at this refresh:
  `[4, 5, 6, 7, 10, 21, 22, 23, 24, 27, 28, 31, 34]`. **#4**, **#5** (Phase 1 research) ·
  **#6** (Phase 1 impl, `blocked: freeze`), **#7** (Phase 2 engine — freeze lifted for
  `engine/` by #31; the engine is built and merged, and what remains of the ticket is the
  exit determination, not the build) · **#10** (Agent Coordination Queue, permanent index) ·
  **[#34](https://github.com/tomerYannay/4UR4/issues/34)** (GOV-013's Enforcement clause
  asserts a structural guarantee this repository does not provide — no channel exists in
  which a human approval is distinguishable from an agent's; the same root cause as #21) ·

  *(Correction: this index previously listed **#20** as OPEN and **"blocks Phase 2 entry"**.
  #20 is **CLOSED**, `2026-07-26T23:17:13Z`, by PR #32's merge — and it omitted **#34**
  entirely. The count read 13 only because the two errors cancelled, which is worse than
  being off by one. Both caught by the Verification gate.)*
  **[#21](https://github.com/tomerYannay/4UR4/issues/21)** (review verdicts cannot become
  artifacts + single-account attribution — **required before HD-06**; the #31 lift went
  ahead without it) ·
  **[#22](https://github.com/tomerYannay/4UR4/issues/22)** (evidence-tooling follow-ups) ·
  **[#23](https://github.com/tomerYannay/4UR4/issues/23)** (roadmap baseline approval, HD-16
  — ruling artifact) · **[#24](https://github.com/tomerYannay/4UR4/issues/24)** (universe
  decision, HD-18 — ruling artifact) · **[#27](https://github.com/tomerYannay/4UR4/issues/27)**
  (HD-21 bounded delegation — the authority under which SPR-D-01 was taken) ·
  **[#28](https://github.com/tomerYannay/4UR4/issues/28)** ·
  **[#31](https://github.com/tomerYannay/4UR4/issues/31)** (the Product Owner ruling that
  lifts GOV-015 for Phase 2 `engine/` work and requires branch protection — see Build-freeze
  status). *#28's subject is not determinable from the working tree; GitHub is authoritative.*
- **CLOSED, retained here only because they are cited above:**
  **[#16](https://github.com/tomerYannay/4UR4/issues/16)** (Phase 0 evidence correction —
  delivered by the merged PR #18; the traceability debt it leaves is recorded under Active
  work, not as an open ticket) · **[#19](https://github.com/tomerYannay/4UR4/issues/19)**
  (roadmap exit-criteria gap — the derived fixture-coverage gate is on `main`; closed
  2026-07-26, no longer a Phase 2 entry blocker) ·
  **[#26](https://github.com/tomerYannay/4UR4/issues/26)**
  (RM-01 as-of-time divergence — the HD-20 evidence and options; **resolved by SPR-D-01**).
- **Open PRs — a snapshot, not a claim of completeness; the GitHub PR list is authoritative
  and this line is stale the moment a PR is opened.** At this refresh: **#12** (Phase 1
  research, draft, CI green, 0 reviews, awaiting strategic review) and
  **[#35](https://github.com/tomerYannay/4UR4/pull/35)** (this refresh, the HD-22 part 3
  deviation record, and the fixture-immutability guard hardening). **#29 is MERGED** and was
  listed here as open — corrected.
  Coordination queue: [#10](https://github.com/tomerYannay/4UR4/issues/10).
- **Recently merged:** **[#33](https://github.com/tomerYannay/4UR4/pull/33)** as `ed92bbb`
  (**the Phase 2 trendline engine** — `engine/`, 27 files, 136 tests, all 23 golden fixtures
  and RM-01 causal replay, the engine conformance step added to the required CI check, the
  fixture-immutability guard, and the SPR-D-03 record and propagation) ·
  **[#32](https://github.com/tomerYannay/4UR4/pull/32)** as `758c0a0` (the E2-AUTHOR tool-deny
  quarantine — `bash-guard.mjs`, 329 assertions — closing #20's configuration half; merged
  **first**, deliberately, so the control enforcing the quarantine entered `main` under its own
  reviewed PR rather than as a side effect of the engine PR) ·
  **[#30](https://github.com/tomerYannay/4UR4/pull/30)** as `54b16ee`
  (RM-01 causal replay: `expected-causal.json`, `real-causal.schema.json`, the `real/`-reading
  tool extensions, `maintenance-backlog.md`) ·
  **[#25](https://github.com/tomerYannay/4UR4/pull/25)** as `d1a1c41`
  (universe definition, Phase 2 plan, HD-06 due diligence, HD-21, SPR-D-01 propagation) ·
  **[#18](https://github.com/tomerYannay/4UR4/pull/18)** as `e56ed8e` (Phase 0 evidence
  correction + as-of-time fixture audit; review-chain findings in
  [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md)).

## Sources
[`roadmap.md`](roadmap.md) · [`requirements.md`](requirements.md) · [`human-decisions.md`](human-decisions.md) ·
[`trendline-specification.md`](trendline-specification.md) · [`confidence-specification.md`](confidence-specification.md) ·
[`fixtures/README.md`](fixtures/README.md) · [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md) ·
[`maintenance-backlog.md`](maintenance-backlog.md) · [`../governance/build-freeze.md`](../governance/build-freeze.md) ·
[`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) ·
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md) ·
[`../docs/architecture/phase2-implementation-plan.md`](../docs/architecture/phase2-implementation-plan.md) ·
[`../docs/architecture/phase2-independence-mechanism.md`](../docs/architecture/phase2-independence-mechanism.md) ·
[`../docs/operations/agent-handoff-protocol.md`](../docs/operations/agent-handoff-protocol.md) ·
[`../GOVERNANCE.md`](../GOVERNANCE.md)
