# 4UR4 — Project State (canonical, current-state only)

> **Current state only — not a history log.** **Content owner: Product Steward.** The
> **Orchestrator** ensures this file is updated after: a phase completes · a Product Owner
> decision is recorded · a roadmap phase changes · a major PR merges · a build-freeze scope
> changes. The **Strategic Product Reviewer** reads and validates this file but **may not
> edit** it. If it is stale or contradicts stronger evidence, that is flagged, not silently
> fixed. Precedence when sources disagree: latest PO decision on GitHub →
> [`human-decisions.md`](human-decisions.md) → [`requirements.md`](requirements.md) + specs →
> [`roadmap.md`](roadmap.md) → merged fixture evidence → open PR proposals → agent summaries.

- **Last updated:** 2026-07-28
- **Last reviewed commit SHA (main):** `c66fd2947dfa98573f6d43bf53079aa7bb6304de` — the merge
  commit of [PR #37](https://github.com/tomerYannay/4UR4/pull/37). CI is **green on `main` at
  this SHA** (post-merge job `90238891750`), and was green on the reviewed head `4630564`
  itself rather than on an ancestor. The merged tree is byte-identical to the reviewed head's
  tree.

  **[PR #38](https://github.com/tomerYannay/4UR4/pull/38) merged immediately before it** at
  `0b564a41dc77c07ade797632cf78bb5183e91825` (post-merge job `90228331147`; reviewed head
  `586a34e`, job `90223085692`). **Both were merged by Release & Ops**, each on three gate
  verdicts taken at the exact head and posted as citable artifacts. **Release & Ops refused #38
  once, correctly**, because no gate verdict existed on the PR as a repository artifact — GOV-006
  rule 1 is that assertions are not evidence — and it merged only after the verdicts, a
  head-current strategic review, and the HD-24 §2 re-anchor were all posted.

  *An earlier draft of this line said PR #37's merge status was "NOT stated here, because it is
  not determinable from the working tree". That was the correct disposition when written — the
  Product Steward had no shell and refused to guess. It has since been determined and is stated
  above.*

  **The governing decision is now [HD-24](human-decisions.md)**
  ([#39](https://github.com/tomerYannay/4UR4/issues/39), Product Owner, 2026-07-28). §2
  authorizes PR #38 and PR #37 **by number without waiving their gates**, and permits the
  Orchestrator to **relay** a gate verdict where `ROLE_POLICY` blocks the gate role from
  posting — each relay stating on its face that it is one, which makes a verdict **citable,
  not independently attributable**. §2's original head `207e91a` was voided by four
  gate-driven corrections and the authorization was **re-anchored** to `586a34e`.
  **HD-24 is relayed under the single shared identity and written up by the Orchestrator, an
  interested party**; [#21](https://github.com/tomerYannay/4UR4/issues/21) and
  [#34](https://github.com/tomerYannay/4UR4/issues/34) **remain open** and HD-24 closes
  neither. The standing [GOV-005](../governance/definition-of-done.md) *"merged by Release &
  Ops only"* deviation is **not** re-narrated here — it lives in
  [`human-decisions.md`](human-decisions.md) precisely so a refresh of this file cannot sweep
  it.

  **The gate runs five checks** — *every figure below is as measured at `c66fd294`, this
  file's declared reference SHA, and is **not** restated as current: the `check-evidence`
  census moves with every documentation commit, including this one*: `tools/validate.mjs` ·
  `.claude/hooks/bash-guard.test.mjs`
  (329 assertions) · `tools/fixture-replay.mjs --all` (23/23 golden + 1/1 real) ·
  `tools/check-evidence.mjs` (74 markdown files, 0 broken cross-file links, 1651 body rows in
  214 tables) · **`python3 -m engine.tests.run_all` (141 tests)** — plus a
  **fixture-immutability guard** that hard-fails any PR touching `engine/` that also carries a
  non-`*.md` change under `product/fixtures/`, **plus typechange** (broader than earlier prose
  said — M-46). *(**Corrected 2026-07-28:** the engine count read **"136 tests"** here while
  the PR #37 entry under **Open issues / PRs** below said **"141 tests (was 136)"** — one file,
  two counts. **141** is the count at `c66fd294`; **136** was carried over from the `586a34e`
  measurement, taken before PR #37's engine hardening merged. The other four figures in this
  sentence were exact at `c66fd294`. Found by Code Review.)* **What the gate did NOT do on PR #38, recorded because a green result hides
  it:** no automated step provided substantive assurance for a documentation PR. The
  fixture-immutability guard early-returned and contributed **nothing**; four gate steps were
  unchanged-by-construction; only `check-evidence.mjs` read the changed files, and it validates
  link and table *structure*, not factual content. The review chain found **five false
  statements** across four rounds; **no automated step found any of them**.
- **Build-freeze status:** **ON, with TWO scopes lifted — both inside `engine/`**
  ([GOV-015](../governance/build-freeze.md)).
  - **Phase 2 `engine/`** — Product Owner, 2026-07-26,
    [#31](https://github.com/tomerYannay/4UR4/issues/31), recorded as **HD-22**: the
    deterministic engine, fixture and RM-01 conformance tests, engine-local test
    infrastructure, minimal shared types.
  - **Phase 3 `engine/`** — Product Owner, **2026-07-28**,
    [#39](https://github.com/tomerYannay/4UR4/issues/39) §3, recorded as **HD-24**: the
    **`ACTIVE → BROKEN_OUT` transition**, **line freezing** (`Λ^F`, §21.5), **retest** (§16),
    **failed breakout** (§15), **expiry and recompute** (§17).

  **Still frozen everywhere else**, per HD-24 §3's own list: provider integration, live
  ingestion, `api`, `db`, `scanner`, `worker`, `dashboard`, `alerts`, `billing`, `providers`,
  SaaS surfaces, spend, licensing, privacy/billing, external deployment. **E2-AUTHOR binds the
  whole engine across both phases**, and the fixture-immutability condition carries over
  unchanged.

  **⚠ The machine check does NOT distinguish the two lifts, and that gap is stated rather than
  hidden.** The freeze marker's `scope` is a list of **directory names**; it is still
  `["engine/"]` **because the directory did not change**, and a lift that widens authorized
  *behaviour inside* a directory is invisible to a directory-name check. So `tools/validate.mjs`
  cannot tell Phase-2 work from Phase-3 work in `engine/`, and never could. What remains
  mechanical is the outer boundary: `engine/` passes **only** because the marker names it, and
  deleting the entry re-freezes it on the next CI run. The **inner** boundary — the roadmap's
  behavioural Phase 2 / Phase 3 rule — is enforced by review and the Auditor, **not by CI**.
  See [`../governance/build-freeze.md`](../governance/build-freeze.md).

  **⚠ A lift is not permission to start — and as of 2026-07-28 the permission now exists.**
  [GOV-015](../governance/build-freeze.md) rule 4 ties a lift to a *specific **approved,
  Ready*** ticket. **HD-24 §3 asserted that attaching to ticket (g) satisfied rule 4; it did
  not** — at that head (g) was `blocked: freeze` and expressly not Ready. The repair was made
  **forward, not backdated**: `blocked: freeze` was removed under HD-24 §3, and (g)'s DoR has
  now been re-assessed a **second** time, dated **2026-07-28**, after the two grounds that
  failed element 7 were closed — the nine Steward rulings and
  [HD-25](human-decisions.md) in
  [`trendline-specification.md`](trendline-specification.md) §22, and the **Phase 2 exit
  determination** below. **(g) is now READY**, so rule 4 is satisfied by a ticket that
  genuinely meets it rather than by assertion. See
  [`planning/ticket-set.md`](planning/ticket-set.md) ticket (g). **Ready is still not
  "started"**: [GOV-008](../governance/ticket-hygiene.md) rule 1 governs that, and is assessed
  there.

  **Full branch protection on `main` remains a stated Product Owner precondition on Phase 2
  product-code merges**, with **6 of its 7 parts in force**; part 3 (required exact-head
  reviews) is **UNMET** and ruled a **recorded deviation** — read with
  [`human-decisions.md`](human-decisions.md) → **HD-22 part 3**.

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

**Phase 2 — the engine is BUILT and on `main`, and the exit determination is now MADE.** These
are two different statements and this file keeps them apart deliberately. **What was owed was
the determination, not a Product Owner approval of it:** [HD-24](human-decisions.md) §4 rules
that *"Phase 2 exit is authorized to close on its acceptance criteria without further Product
Owner approval."* The approval requirement was **already removed**; the
[GOV-002](../governance/roadmap-authority.md) determination against the acceptance criteria is
what had not been made. **It is made below, dated 2026-07-28, by the Product Steward — the only
agent who may make it.**

### Phase 2 exit determination — Product Steward, 2026-07-28

```
phase_2_exit: CLOSED_ON_AUTHORITY
exit_criteria: MET
unmet_at_closure: [E2-AUTHOR-2]
met_by_ruling: [E2-AUTHOR-5]
authority: HD-24 §4 (issue #39, Product Owner, 2026-07-28)
clean_gate_pass: false
```

**Register form: Phase 2 is CLOSED ON AUTHORITY, not on a clean gate pass.** `clean_gate_pass`
is `false` and is stated first, because a determination that buried it would be the failure
this record exists to catch. Phase 2 closes because a Product Owner ruling authorized it to
close on its acceptance criteria — **not** because every criterion was independently satisfied.
**This must not be restated anywhere as "all criteria met."**

**E2-AUTHOR — the fuller status, so no reader has to infer it:**

| # | Criterion | Status at closure |
|---|---|---|
| **E2-AUTHOR-1** | #20 has defined the enforceable independence mechanism | **UNMET** on the attestation's own §9 table — *and contradicted at this head*, see the note below |
| **E2-AUTHOR-2** | The **Ready** ticket carries E2-AUTHOR-A and names the must-not-read set | **UNMET** — `engine/` was authored before [#7](https://github.com/tomerYannay/4UR4/issues/7) reached Ready, and **#7 has not been backdated** |
| **E2-AUTHOR-3** | The authoring agent is configuration-denied, not merely instructed | **PARTIALLY MET** — a real tool-level deny exists; the primary P1 clean room was not used and no probe was observed refusing |
| **E2-AUTHOR-4** | Authorship separated from verification | **MET IN ROLE, BREACHED IN PART** — unverifiable in identity, and a model-exposed session authored 6 executable lines |
| **E2-AUTHOR-5** | The claim is attested and citable, recorded by a party other than the author | **MET BY RULING** — [HD-24](human-decisions.md) §4, on an attestation whose B-record is ABSENT, whose commit range is not recorded, and whose sign-off is deliberately unsigned |

**[HD-24](human-decisions.md) §4 names only criterion 2, and the attestation's own §9 table
shows more than criterion 2 outstanding.** Both facts are recorded, and the determination is
written to the wider of them: `unmet_at_closure` lists **E2-AUTHOR-2** because that is the
criterion the authorizing ruling addresses, while the table above carries **criteria 1, 3 and 4
as well** — none of which the ruling reaches. **The ruling governs; the residue is disclosed,
not discharged.**

**One correction inside that table, stated rather than silently resolved.** The attestation's
§9 row for **criterion 1** reads *"UNMET — #20 is open … the issue has not closed."* That is
**contradicted at this head** by the measurement recorded earlier in this file:
[#20](https://github.com/tomerYannay/4UR4/issues/20) is **CLOSED**, `2026-07-26T23:17:13Z`,
`stateReason: COMPLETED`, by PR #32's merge — and the roadmap's own wording is *"until it
closes this criterion is unmet."* On that measurement **criterion 1 is MET**. The table above
reports the attestation's face value because the attestation is the artifact the ruling rests
on and **is not edited by the session it attests**; the contradiction is recorded here instead.
The Product Steward has no shell and re-measured neither state. **The determination does not
turn on it**: criterion 1 being MET would make the disclosure narrower, never wider.

**What this determination does and does not do.** It closes Phase 2 and thereby satisfies the
roadmap's Phase 3 **entry** criterion *"Phase 2 exit met"*. It does **not** mark any ticket
Done — that is [GOV-005](../governance/definition-of-done.md) and not the Steward's call — it
does not close [#7](https://github.com/tomerYannay/4UR4/issues/7), it does not close
[#21](https://github.com/tomerYannay/4UR4/issues/21) or
[#34](https://github.com/tomerYannay/4UR4/issues/34), and it **edits no byte of**
[`roadmap.md`](roadmap.md) ([GOV-002](../governance/roadmap-authority.md),
[GOV-013](../governance/approval-gate.md)).

**Phase 3 — the freeze is LIFTED, the design is committed, the ticket is READY, and nothing
has been built yet.** Four different statements, and keeping them apart is the point.
[HD-24](human-decisions.md) §3 lifted GOV-015 for Phase 3 inside `engine/` on 2026-07-28; the
Architect's plan is committed as design-only at
[`../docs/architecture/phase3-implementation-plan.md`](../docs/architecture/phase3-implementation-plan.md)
(now carrying a dated correction block for the two clauses the OQ-P3-5 ruling invalidates); and
ticket **(g)** became **READY on 2026-07-28**, so GOV-015 rule 4 is satisfied and
implementation **may** start. **The lift was granted while the ticket was not Ready — exactly
the gap HD-24 §3 asserted away** — and it was closed by doing the work, not by assertion:
the four escalations were ruled and Phase 2 exit was determined **first**, and the DoR
re-assessment followed. *(Superseded: "and ticket **(g)** is **not Ready**, so GOV-015 rule 4
is unsatisfied and no implementation has started.")*

*What is delivered and mechanically enforced* (`engine/`, 27 files, merged at `ed92bbb`):
the deterministic pre-breakout engine reproduces **all 23 golden fixtures and RM-01** —
anchors, `sig6` slope/intercept, line values at every recorded index, formation traces with
F1/F2/F3 evaluated independently, §18 input guards, every pre-breakout re-selection, and
both RM-01 clauses with the stop index **derived by the engine, never read from the fixture**.
136 tests — **2,525 field comparisons across the 23 golden fixtures and 142 more on RM-01** (instrumented by Code Review; the bare figure `2,525` previously appeared with no artifact emitting it and was uncitable under GOV-006) — inside the **required** CI check. Determinism is asserted
across varied `PYTHONHASHSEED` in a child process. Look-ahead is structurally prevented: the
`Prefix` value object is exactly `t` bars long and geometry never receives the series.

*What is NOT thereby true.* **Phase 2 exit is declared by the Product Steward above, on the
authority of [HD-24](human-decisions.md) §4 and with `clean_gate_pass: false` — it is NOT an
inference from a green suite**, and **no agent other than the Product Steward may make it**:
it is a [GOV-002](../governance/roadmap-authority.md) roadmap determination owned by the
Steward. *(Previously "No agent has declared Phase 2 exit met, and no agent other than the
Product Steward may" — accurate until 2026-07-28, and superseded by the determination itself
rather than deleted. Before that it read "and none may", in the same sentence that assigns it
to the Steward, who is an agent; the restriction is on every **other** agent.)* **E2-AUTHOR
criterion 1
is MET** — [#20](https://github.com/tomerYannay/4UR4/issues/20) **CLOSED** at
`2026-07-26T23:17:13Z`, `stateReason: COMPLETED`, by PR #32's merge, and the roadmap's own
wording is *"until it closes this criterion is unmet"*. **Criterion 5 — the independence
attestation — has changed state twice and neither change makes it cleanly met.** *(As of
2026-07-27 this read simply "remains unmet".)* **(1) The artifact now exists**, committed by
PR #38 at
[`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md);
the earlier statement that it *"does not exist as a file"* is false at this head. **(2)
[HD-24](human-decisions.md) §4 ruled [#36](https://github.com/tomerYannay/4UR4/issues/36)
Part B affirmatively**, and that ruling governs. **What the artifact does not carry**, on its
own face: roadmap criterion 5 asks for **both** the A-check **and** the E2-AUTHOR-B record
**plus the commit range**, and the attestation records the B-record for `7ab8075` as
**"ABSENT — not weak, ABSENT"**, the commit range as **"NOT RECORDED … This is owed"**, and
its own sign-off block (§8) as **"OWED. THIS BLOCK IS DELIBERATELY UNSIGNED."** §10 states its
ceiling: *"it is not a Phase-2 gate pass, it is not a freeze lift, it authorizes nothing."*
**The roadmap's own sentence — file versus authority, and they now differ.** The **file** is
untouched: [`roadmap.md`](roadmap.md) still reads *"Criterion 5 is not satisfiable until
#21 … is resolved, so **Phase 2 entry is blocked on #20 and #21 in addition to the per-scope
freeze lift**"*, and **no byte of it is edited by this change** — a roadmap edit is
[GOV-002](../governance/roadmap-authority.md) / [GOV-013](../governance/approval-gate.md)
territory and the Product Steward does not restate a Product Owner scope decision there. The
**authority** of that sentence is another matter: **[HD-24](human-decisions.md) §4 supersedes
it in writing**, *"rather than leaving it reinterpreted"*, and a superseding Product Owner
decision outranks the sentence it supersedes. So: **the sentence is live in the file, and it no
longer governs.** #21 **is still open** and is still the attribution defect it always was —
what HD-24 §4 removes is the sentence's *blocking effect on criterion 5*, not the defect.
*(An earlier form of this passage said the roadmap statement "is untouched, and #21 is open"
with no further qualification. True of the file, **false of the sentence's authority**, and the
two were being read as one. Found by Code Review.)*
**Both are recorded: the ruling stands, and the residue is not thereby discharged.**
*(An earlier draft of this paragraph said "two … remain formally
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

  **What is still owed, stated honestly — and updated 2026-07-28.** *(This paragraph
  previously opened "criterion 5's independence *attestation* does not exist as a file". **That
  is false at this head** and is corrected rather than quietly dropped: PR #38 committed it at
  [`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md),
  discharging one half of M-35.)* The **ruling** half is now answered too —
  [HD-24](human-decisions.md) §4 resolved [#36](https://github.com/tomerYannay/4UR4/issues/36)
  Part B affirmatively. **What remains owed is what the artifact itself says it lacks:** the
  **E2-AUTHOR-B record for commit `7ab8075` is ABSENT, not weak** — the orchestrating session
  authored 6 executable lines in `engine/` having read the reference model (the Auditor
  examined exactly those lines and found they move *further* from the model than the code they
  replaced) — the **commit range is NOT RECORDED**, and the **sign-off block is deliberately
  unsigned**. #36 Part B's question was conditioned on an attestation *"carrying your named
  sign-off"*, so §4 answered it while dropping that precondition. **The roadmap's file still says
  criterion 5 is unsatisfiable while #21 is open; that sentence no longer governs** —
  [HD-24](human-decisions.md) §4 supersedes it in writing, and **no roadmap byte is edited**
  (GOV-002/GOV-013). *(Corrected 2026-07-28: this read "The roadmap still says criterion 5 is
  unsatisfiable while #21 is open" with nothing distinguishing the file's text from its
  authority.)* **The ruling governs; the residue is disclosed, not treated as satisfied.**
- **Issue [#21](https://github.com/tomerYannay/4UR4/issues/21)** — review verdicts cannot
  become citable artifacts, and review attribution collapses to a single account. **Required
  before HD-06**, and a stated dependency of E2-AUTHOR **criterion 5** (*corrected 2026-07-28:
  this read "the clean-room attestation has nowhere to live until #21 is fixed" — the
  attestation now exists as a committed file, so what #21 withholds is **attribution**, not a
  place to put it; a same-identity artifact is citable and not independently attributable*;
  criterion 4 is authorship/verification separation, and this line named it wrongly). It was also recorded as required
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
**Start Phase 3 — ticket (g) is READY as of 2026-07-28 — and resolve the attribution defect.**
Both grounds that held (g) below [GOV-004](../governance/definition-of-ready.md) element 7 are
now closed, in this change and as a **separate governed change** from any engine work (HD-15
condition 3):
**(a)** the Product Steward has **ruled ESC-1, ESC-3 and ESC-5(a)** and given the six
Steward-owned **OQ-P3** rows normative dispositions, and the Product Owner has ruled **ESC-4**
as [HD-25](human-decisions.md) — all ten recorded at
[`trendline-specification.md`](trendline-specification.md) **§22**, with **ESC-2** already
discharged as record-only and **ESC-5(b)** deferred and explicitly non-blocking;
**(b)** the **Phase 2 exit determination** is made above — `CLOSED_ON_AUTHORITY`,
`clean_gate_pass: false` — which is also the roadmap's Phase 3 **entry** criterion, so (a) and
(b) together make (g) Ready and [GOV-015](../governance/build-freeze.md) rule 4 true.
What remains: **(c)** [#21](https://github.com/tomerYannay/4UR4/issues/21)
and [#34](https://github.com/tomerYannay/4UR4/issues/34) — the single-identity attribution
defect, which blocks *every* merge and is the stated residue on E2-AUTHOR criterion 5;
**(d)** closing the HD-22 part 3 deviation, which requires a **second identity**.
**[GOV-008](../governance/ticket-hygiene.md) rule 1 no longer blocks the start:** ticket (h)
was **delivered and merged** by [PR #37](https://github.com/tomerYannay/4UR4/pull/37) at
`c66fd294`, so it no longer counts as In Progress and **WIP is 2 of 3** (c, d) — one slot is
free. *(Whether (h) is **Done** under [GOV-005](../governance/definition-of-done.md) is not the
Product Steward's call and is not made here; what is assessed here is only whether it still
consumes WIP, and a merged deliverable does not.)*
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
  single-account relay. *(Corrected 2026-07-28: this continued "and the E2-AUTHOR clean-room
  attestation still has nowhere citable to live." It exists and is committed. **What #21
  withholds is attribution, not a location** — and PR #38's own gate verdicts were relayed by
  the Orchestrator under HD-24 §2, which makes them citable and, as those relays say on their
  face, no more attributable than before.)*

## Blocked work
- **#6** Market-data ingestion service (Phase 1 impl) — `blocked: freeze`. Outside the #31
  lift, which excludes provider integration and live data.
- **#7** Trendline detection engine (Phase 2 impl) — **the engine is BUILT and MERGED**
  (`ed92bbb`), passing all 23 golden fixtures and RM-01 under the required CI check. It never
  passed through a formal Definition of Ready, and that is recorded rather than smoothed over:
  the work proceeded on the Product Owner's #31 scope lift and the ruling that E2-AUTHOR-A
  governs. **The exit determination is now MADE** — `CLOSED_ON_AUTHORITY`,
  `clean_gate_pass: false`, dated 2026-07-28, above. **That determines the phase; it does not
  mark this ticket Done** ([GOV-005](../governance/definition-of-done.md)), and the Product
  Steward does not do so. #20 is CLOSED, M-09 is CLOSED (SPR-D-03), and branch
  protection is ruled with a recorded deviation; **#21/#34 remain** and gate E2-AUTHOR
  criterion 5. The RM-01 gate-value block is cleared by SPR-D-01 and the Phase 2 plan's S0
  dependency on HD-20 is satisfied.
- **Phase 3 — NO LONGER BLOCKED.** *(This bullet is retained under "Blocked work" for one
  refresh so the transition is legible, and moves out at the next.)* [HD-24](human-decisions.md)
  §3 lifted GOV-015 for Phase 3 inside `engine/`, and on **2026-07-28** both remaining grounds
  closed: [GOV-004](../governance/definition-of-ready.md) element 7's **four specification
  escalations** ([`maintenance-backlog.md`](maintenance-backlog.md) **M-50**) are ruled —
  ESC-1, ESC-3 and ESC-5(a) by the Product Steward, **ESC-4 by the Product Owner as
  [HD-25](human-decisions.md)**, with the six Steward-owned OQ-P3 rows given normative
  dispositions, all at [`trendline-specification.md`](trendline-specification.md) §22 — and the
  roadmap's Phase 3 entry criterion **"Phase 2 exit met"** is **determined** above. Ticket
  **(g)** in [`planning/ticket-set.md`](planning/ticket-set.md) is therefore **READY**, on a
  DoR re-assessed **forward and dated 2026-07-28**. **It was not backdated and not cosmetically
  flipped** — the two grounds were closed on their merits first, and the assessment followed.
  **GOV-008 rule 1:** WIP is **2 of 3** (c, d) now that (h) is delivered and merged
  ([PR #37](https://github.com/tomerYannay/4UR4/pull/37), `c66fd294`), so a slot is free and
  (g) may be started.
- All of Phases 4–9, and every Phase 2/3 surface outside `engine/` (API, database, scanner,
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

*Ruled 2026-07-28 and no longer pending:* **[HD-24](human-decisions.md)**
([#39](https://github.com/tomerYannay/4UR4/issues/39)) — the PR #38/#37 merge authorization
with its gate-relay provision, the **Phase-3 `engine/` freeze lift**, and an affirmative ruling
on [#36](https://github.com/tomerYannay/4UR4/issues/36) Part B. **It selects no provider and
authorizes no spend; HD-06 is untouched.** **Two overreaches are recorded on the register entry
rather than smoothed:** §3's claim that ticket (g) satisfied GOV-015 rule 4 was **false when
written**, and §4's ruling rests on an attestation whose E2-AUTHOR-B record is **ABSENT**,
whose commit range is **not recorded**, and whose sign-off block is **deliberately unsigned**.
The rulings govern; the gaps are not thereby closed. **[HD-23](human-decisions.md) remains
PENDING PRODUCT OWNER CONFIRMATION** and is unaffected.

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
- **OPEN issues — the list below is CARRIED FORWARD from the 2026-07-27 refresh and was NOT
  re-queried on 2026-07-28.** It read **13** — `[4, 5, 6, 7, 10, 21, 22, 23, 24, 27, 28, 31,
  34]` — verified against `gh issue list` **at that refresh**, and the count is not restated as
  current here because the Product Steward has no shell and did not measure it. **Known to
  exist and absent from that list:** [#36](https://github.com/tomerYannay/4UR4/issues/36)
  (Part A — the Phase-3 lift request, **answered**: HD-24 §3 granted it; Part B —
  E2-AUTHOR criterion 5, **ruled** by HD-24 §4, on an attestation that carries less than
  roadmap criterion 5 asks for),
  [#39](https://github.com/tomerYannay/4UR4/issues/39) (**HD-24** itself), and
  **[#40](https://github.com/tomerYannay/4UR4/issues/40)** — **ticket (g)'s live issue**, filed
  2026-07-28 by the Orchestrator from the Product Steward's draft, leading with *"Status: NOT
  READY. Do not start."* **⚠ That leading line is now STALE**: (g) became **READY** later the
  same day, and updating the issue is an **Orchestrator** action the Product Steward may not
  take. Until it lands, [`planning/ticket-set.md`](planning/ticket-set.md) is the authority on
  (g)'s Ready status, which is a **stated exception** to *"the issues are authoritative"*. *(**Corrected 2026-07-28, and the superseded sentence is quoted rather
  than deleted, because this PR's standard is to quote what it supersedes:** this bullet read
  **"A live issue for ticket (g) does not exist yet; opening one is an Orchestrator action and
  no number is invented here."** That was **false at this head** — #40 exists, and
  [`planning/ticket-set.md`](planning/ticket-set.md) records **`(g) → #40`** in this same
  commit. One commit asserted both. The enumeration above also omitted #40 — the one issue this
  change created — while naming #36 and #39. Found by Code Review.)* The GitHub issue list is
  authoritative and this bullet is stale by construction. **#4**, **#5** (Phase 1 research) ·
  **#6** (Phase 1 impl, `blocked: freeze`), **#7** (Phase 2 engine — freeze lifted for
  `engine/` by #31; the engine is built and merged, and the exit determination is now made —
  see above) · **#10** (Agent Coordination Queue, permanent index) ·
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
  research, draft, CI green, 0 reviews, awaiting strategic review). **#35 is MERGED** at
  `8cdaffc` and was listed here as open — corrected.
  Coordination queue: [#10](https://github.com/tomerYannay/4UR4/issues/10).
- **[PR #38](https://github.com/tomerYannay/4UR4/pull/38) MERGED** as
  `0b564a41dc77c07ade797632cf78bb5183e91825` — five documentation artifacts, **no `engine/`,
  fixture, tooling, `.github/` or `.claude/` change** (`git diff --name-only` over those paths
  is empty). It delivered the **E2-AUTHOR independence attestation**
  ([`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md)),
  the **HD-23** record, the ticket-set repairs including the first statement of ticket **(g)**,
  seven maintenance rows plus **ESC-1**, and the **Phase-3 implementation plan**
  ([`../docs/architecture/phase3-implementation-plan.md`](../docs/architecture/phase3-implementation-plan.md),
  design only). Authorized by **HD-24 §2**, re-anchored to head `586a34e` after the head moved
  four times under §2's own condition.
- **[PR #37](https://github.com/tomerYannay/4UR4/pull/37) — MERGED** at
  `c66fd2947dfa98573f6d43bf53079aa7bb6304de`, delivering ticket (h)'s engine hardening
  (M-28/M-29/M-30/M-32). Head `4630564`; 4 files, all `engine/`; **141 tests** (was 136).
  Authorized by **HD-24 §2**, whose row named no fixed SHA — *"new SHA after R1"* — so the two
  subsequent head moves fell **inside** its wording rather than beside it. Both moves were
  compelled, not discretionary: `0a3c33d`→`5a2cec0` by branch protection (`strict: true`, the
  branch was 16 behind `main`), and `5a2cec0`→`4630564` by a Code Review verdict.

  **This is the first PR on which the HD-22 fixture-immutability guard did real work.** It
  *engaged* (4 `engine/` files changed) and passed **on the merits** — the MDT set under
  `product/fixtures/` was empty and the short-circuit branch was not taken, confirmed in the CI
  job log, not only by local reproduction. On #38 the same step was **inert**. HD-22 calls this
  the one control that cannot be recovered after the fact.

  **Behaviour-neutrality was established by inspection, not only by sampling.** The gates argued
  it empirically (145,904 base-vs-head comparisons across eight ε values including 0, plus a
  byte-identical serialized corpus). Release & Ops went further and proved it structurally:
  `domination_set(t, L)` returns `tuple(range(t + 1, length))`, exactly what the base expressed
  inline at all three sites, and `logspace.exceeds(lhs, y_hat, tol)` is `lhs > y_hat + tol` with
  the right-hand side formed first — identical **including floating-point association order**.
  Worth recording precisely because the PR is *not* a no-op against `main`: `domination_set` is
  newly extracted there.
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
[`maintenance-backlog.md`](maintenance-backlog.md) · [`planning/ticket-set.md`](planning/ticket-set.md) ·
[`../governance/build-freeze.md`](../governance/build-freeze.md) ·
[`../governance/definition-of-ready.md`](../governance/definition-of-ready.md) ·
[`../governance/ticket-hygiene.md`](../governance/ticket-hygiene.md) ·
[`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) ·
[`../docs/architecture/phase3-implementation-plan.md`](../docs/architecture/phase3-implementation-plan.md) ·
[`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md) ·
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md) ·
[`../docs/architecture/phase2-implementation-plan.md`](../docs/architecture/phase2-implementation-plan.md) ·
[`../docs/architecture/phase2-independence-mechanism.md`](../docs/architecture/phase2-independence-mechanism.md) ·
[`../docs/operations/agent-handoff-protocol.md`](../docs/operations/agent-handoff-protocol.md) ·
[`../GOVERNANCE.md`](../GOVERNANCE.md)
