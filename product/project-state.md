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
- **Last reviewed commit SHA (main):** `5ff743115cbf99194a9e76683ae7548de410591a` — the merge
  commit of [PR #43](https://github.com/tomerYannay/4UR4/pull/43), the **Phase 3 engine**. CI is
  **green on `main` at this SHA**, and three gate verdicts were taken at the exact head. 16
  files, **all `engine/`**; every top-level tree except `engine` is object-identical to base.
  **The HD-22 fixture-immutability guard engaged and passed on the merits** — `engine/` files
  changed and the MDT set under `product/fixtures/` was empty, so the short-circuit branch was
  not taken.

  *The Product Steward has no shell.* The test count (**202**, base 141), the CI status, the
  tree-identity comparison and the guard's engagement are **relayed from the gates and the
  Orchestrator**, not measured here. Everything this file states about the **contents of the
  repository** was read from the tree at this SHA.

  **The governing merge authority remains [HD-24](human-decisions.md)**
  ([#39](https://github.com/tomerYannay/4UR4/issues/39), Product Owner, 2026-07-28): §2's
  gate-relay provision (a relay makes a verdict **citable, not independently attributable**),
  §3's Phase-3 `engine/` freeze lift, §4's affirmative ruling on
  [#36](https://github.com/tomerYannay/4UR4/issues/36) Part B.
  [#21](https://github.com/tomerYannay/4UR4/issues/21) and
  [#34](https://github.com/tomerYannay/4UR4/issues/34) **remain open** and HD-24 closes neither.
  The standing [GOV-005](../governance/definition-of-done.md) *"merged by Release & Ops only"*
  deviation lives in [`human-decisions.md`](human-decisions.md), not here.

  **The gate runs five checks:** `tools/validate.mjs` · `.claude/hooks/bash-guard.test.mjs` ·
  `tools/fixture-replay.mjs --all` (23/23 golden + 1/1 real) · `tools/check-evidence.mjs` ·
  **`python3 -m engine.tests.run_all`** — plus the **fixture-immutability guard** that hard-fails
  any PR touching `engine/` that also carries a non-`*.md` change (including a typechange) under
  `product/fixtures/`. *Per-check counts move with every commit and are deliberately not pinned
  here; the figures that were pinned at `c66fd294` are superseded by this refresh.*
- **Build-freeze status:** **ON, with TWO scopes lifted — both inside `engine/`**
  ([GOV-015](../governance/build-freeze.md)).
  - **Phase 2 `engine/`** — Product Owner, 2026-07-26,
    [#31](https://github.com/tomerYannay/4UR4/issues/31), **HD-22**: the deterministic engine,
    fixture and RM-01 conformance tests, engine-local test infrastructure, minimal shared types.
  - **Phase 3 `engine/`** — Product Owner, 2026-07-28,
    [#39](https://github.com/tomerYannay/4UR4/issues/39) §3, **HD-24**: the **`ACTIVE →
    BROKEN_OUT` transition**, **line freezing** (`Λ^F`, §21.5), **retest** (§16), **failed
    breakout** (§15), **expiry and recompute** (§17).

  **Both lifts' enumerated behaviour is now DELIVERED.** Neither lift is spent as an
  authorization — engine-local test infrastructure and conformance tests remain inside the
  HD-22 grant — but no *unbuilt* behaviour remains inside either scope.

  **Still frozen everywhere else**, per HD-24 §3's own list: provider integration, live
  ingestion, `api`, `db`, `scanner`, `worker`, `dashboard`, `alerts`, `billing`, `providers`,
  SaaS surfaces, spend, licensing, privacy/billing, external deployment. **E2-AUTHOR binds the
  whole engine across both phases**, and the fixture-immutability condition carries over.

  **⚠ The machine check does NOT distinguish the two lifts.** The freeze marker's `scope` is a
  list of **directory names** and is still `["engine/"]` because the directory did not change.
  `tools/validate.mjs` cannot tell Phase-2 work from Phase-3 work inside `engine/`, and never
  could. What remains mechanical is the outer boundary: `engine/` passes **only** because the
  marker names it. The **inner** boundary — the roadmap's behavioural Phase 2 / Phase 3 rule —
  is enforced by review and the Auditor, **not by CI**. See
  [`../governance/build-freeze.md`](../governance/build-freeze.md).

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
  endorsed by or equivalent to S&P Dow Jones Indices. The cost travels with the benefit:
  **4UR4 backtest results are not comparable to published S&P 500 strategy results**, which
  the Phase 4 **UNIV-DISC** gate requires to accompany every reported number. Design:
  [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
  (design, not implementation).

## Current phase

**Phases 2 and 3 are BUILT, MERGED and DETERMINED. Phase 1 is at its research stage and its
implementation is freeze-blocked. Phases 4–9 are freeze-blocked and, additionally,
gated on HD-06.** Those are four separate statements and this file keeps them apart.

**Phase 0 exit is clean.** The defect that once qualified it — **GX-08 as committed** encoding a
precondition **HD-11 forbids** — was corrected by PR #18: GX-08 expects the all-highs
upper-log-hull result `B* = (1, 98)`, GX-20 covers the still-reachable
`NO_VALID_SECOND_ANCHOR` case, and the pivot-conditioned text was swept. **HD-12, HD-13 and
HD-14 are APPROVED — RATIFIED; HD-15 is APPROVED**, in one ruling recorded as a citable
artifact ([2026-07-25](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012),
against head `2651cd0`).

### Phase 2 exit determination — Product Steward, 2026-07-28

```
phase_2_exit: CLOSED_ON_AUTHORITY
exit_criteria: MET
unmet_at_closure: [E2-AUTHOR-2]
met_by_ruling: [E2-AUTHOR-5]
authority: HD-24 §4 (issue #39, Product Owner, 2026-07-28)
clean_gate_pass: false
```

**Phase 2 is CLOSED ON AUTHORITY, not on a clean gate pass.** `clean_gate_pass` is `false` and
is stated first. Phase 2 closes because a Product Owner ruling authorized it to close on its
acceptance criteria — **not** because every criterion was independently satisfied. **This must
not be restated anywhere as "all criteria met."**

| # | E2-AUTHOR criterion | Status at Phase-2 closure |
|---|---|---|
| **E2-AUTHOR-1** | #20 has defined the enforceable independence mechanism | **MET on measurement** — [#20](https://github.com/tomerYannay/4UR4/issues/20) CLOSED `2026-07-26T23:17:13Z`, `stateReason: COMPLETED`, by PR #32; the attestation's own §9 row still reads UNMET and is a dated record, not edited |
| **E2-AUTHOR-2** | The **Ready** ticket carries E2-AUTHOR-A and names the must-not-read set | **UNMET** — `engine/` was authored before [#7](https://github.com/tomerYannay/4UR4/issues/7) reached Ready, and **#7 has not been backdated** |
| **E2-AUTHOR-3** | The authoring agent is configuration-denied, not merely instructed | **PARTIALLY MET** — a real tool-level deny exists; the primary P1 clean room was not used and no probe was observed refusing |
| **E2-AUTHOR-4** | Authorship separated from verification | **MET IN ROLE, BREACHED IN PART** — unverifiable in identity, and a model-exposed session authored 6 executable lines |
| **E2-AUTHOR-5** | The claim is attested and citable, recorded by a party other than the author | **MET BY RULING** — [HD-24](human-decisions.md) §4, on an attestation whose B-record is ABSENT, whose commit range is not recorded, and whose sign-off is deliberately unsigned |

**[HD-24](human-decisions.md) §4 names only criterion 2; the attestation's own §9 table shows
more than criterion 2 outstanding.** The determination is written to the wider of them. **The
ruling governs; the residue is disclosed, not discharged.** It closes Phase 2 and thereby
satisfies the roadmap's Phase 3 **entry** criterion. It marks no ticket Done
([GOV-005](../governance/definition-of-done.md)), closes no issue, and **edits no byte of**
[`roadmap.md`](roadmap.md) ([GOV-002](../governance/roadmap-authority.md),
[GOV-013](../governance/approval-gate.md)).

### Phase 3 exit determination — Product Steward, 2026-07-28

```
phase_3_exit: CLOSED_ON_CRITERIA
exit_criteria: MET
clean_gate_pass: true
unmet_at_closure: []
met_by_ruling: []
not_assessable_by_steward: [V-2 (as a posted report), V-3]
relayed_not_measured: [V-1 run figures, V-3]
authority: HD-28 (Product Owner, 2026-07-29) — a phase whose criteria are met as written closes on the Steward's determination; no further approval
evidence_base: SYNTHETIC_ONLY
independence_probe_D5: UNDISCHARGED
corpus_blind_regions: MEASURED
```

**Phase 3 closes on a clean gate pass over a gate that is narrower than it sounds.** Both
halves are load-bearing and neither may travel without the other. Unlike Phase 2, no Product
Owner ruling was needed: the criteria as the roadmap writes them were independently satisfied,
first run, with nothing reconciled. And the criteria as the roadmap writes them reach **only
`product/fixtures/golden/`** — 23 constructed fixtures — so a clean pass over them is **not** a
statement about real-market behaviour.

| # | Phase 3 criterion (roadmap) | Verdict | Evidence |
|---|---|---|---|
| **E-1** | Entry — Phase 2 exit met | **MET (inherited)** | The Phase-2 determination above — `CLOSED_ON_AUTHORITY`, `clean_gate_pass: false`. Phase 3 inherits that qualification and does not launder it |
| **E-2** | Entry — **HD-03** (breakout confirmation policy) approved | **MET** | HD-03 ratified; `confirmed_bar == breakout_bar`, no persistence gate. Asserted per fixture in `engine/tests/conformance.py` as `breakout_bar == confirmed_bar (HD-03)` |
| **E-3** | Entry — freeze lifted for this scope | **MET** | [HD-24](human-decisions.md) §3, [`../governance/build-freeze.md`](../governance/build-freeze.md); ticket **(g)** READY 2026-07-28 **before** implementation began, so GOV-015 rule 4 was satisfied by a ticket that met it |
| **E-4** | Entry — E2-AUTHOR continues to bind the authoring agent for the whole engine | **MET** | Measured by the Product Steward at this head with an exact-match search over `engine/`: **zero** occurrences of `fixture-replay`, `fixture_replay`, `VERIFICATION.md` or `independence-mechanism`. `engine/tests/test_architecture.py` A-3 forbids any reference to a sibling top-level directory and carries its own anti-vacuity assertion. The implementer hit a guard refusal and did **not** work around it |
| **X-1** | Every golden fixture reproduced in full: the complete `expected_state_transitions` list | **MET** | `compare_golden` compares the transition list with `_compare_ordered` — element by element, **length asserted, both directions**. The Phase-2 branch that narrowed the comparison for a non-null `confirmed_bar` is removed and the removal is stated in the module docstring |
| **X-2** | The complete `expected_reason_codes` set of each | **MET** | Compared **as a set and in first-emission order**, plus a closed-set membership check on every emitted code |
| **X-3** | The `expected_final_state` of each | **MET** | Compared for every fixture, and additionally at **every** recorded `eps_break` sweep point — the Phase-2 harness compared sweep `final_state` only where `breakout_bar` was null |
| **X-4** | No fixture named or exempted; the gate is derived | **MET** | `golden_fixture_ids()` walks the directory; `GateCoverage` asserts set equality between generated tests and directories and fails on an unvisited one. Counted on disk at this SHA: **23** directories, `GX-01`…`GX-23`, each with `input.csv` + `expected.json` |
| **X-5** | The Phase-2 gate **plus all post-`confirmed_bar` behaviour on `Λ^F`**: failure, retest, expiry, recompute | **MET, with recompute-after-expiry unfixtured** | `Λ^F` compared field by field against `causal_record.frozen_event_line`, including object identity with `line_at_stop`; every event type compared in both directions; suspension proven **positively** via `non_retroactive_challengers`. Final states counted on disk: `BROKEN_OUT` GX-11/GX-16 · `RETESTED` GX-04/GX-19 · `FAILED_BREAKOUT` GX-05/GX-17 · expiry GX-07 (`EXPIRED_POST_BREAKOUT` → `NONE`). **Recompute is covered only after `RESET_NEW_ATH`** (GX-06, GX-22, both from `ACTIVE`); **no fixture recomputes after an expiry** |
| **X-6** | The two gates cover the committed set exactly once | **MET** | Phase 3 compares all 23 in full, subsuming the Phase-2 partition. `Phase3OutcomeCensus` **derives** the post-breakout outcome count from the committed robustness blocks rather than pinning it, and asserts the derived set is actually compared |
| **X-7** | Full state machine + reason codes verified against the schema's **closed** code set | **MET, and stronger than the text asks** | `test_architecture.py` A-4 asserts `ReasonCode` and `LineState` **equal** the enums in `product/fixtures/schema/fixture.schema.json`. `_assert_valid_walk` adds continuity **and edge legality** against a transcription of §11 — which nothing in `engine/` checked before Phase 3 — and asserts `LineState.EXPIRED` never appears in a record (ESC-1) |
| **V-1** | Evidence — passing breakout/retest/expiry fixture tests | **MET in the tree; run figures RELAYED** | `test_conformance_golden.py`, `test_post_breakout.py`, `test_rm01.py` are committed and are inside the required CI check. The **202** count, the green result and *"first run, nothing reconciled"* are relayed from the gates; the Steward has no shell and measured none of them |
| **V-2** | Evidence — state-machine transition coverage | **MET as a mechanical check; NOT ASSESSABLE as a posted report** | The legality check is in the tree and citable. **No committed artifact enumerates which §11 edges the corpus exercises and which it does not** — the nearest is prose in `engine/tests/conformance.py`. Ticket (g)'s evidence plan asks for a report *"counted by emission, not by grepping source"*; whether one was posted on PR #43 is not determinable from the tree |
| **V-3** | Evidence — CI green | **NOT ASSESSABLE by the Steward; relayed green at the exact head** | No shell. Three gate verdicts at `5ff74311` are the cited basis |
| **V-4** | Evidence exclusion — agreement with `tools/fixture-replay.mjs` earns no credit (HD-15 condition 1) | **MET, measured** | Zero references under `engine/` (E-4 above). `conformance.py`'s docstring states that nothing there runs, imports or compares against any reference model; the contract is the fixtures and the specification |

**Reason-code corpus coverage, measured on disk at this SHA:** the closed set holds **15**
codes; **14** appear in at least one committed golden `expected_reason_codes` list.
**`INSUFFICIENT_BARS` appears in none** — it is emitted only inside formation gate traces, not
as a transition reason, anywhere in the committed corpus.

**Three records that must not be softened. All three came from the gates and from the tree, not
from any agent's summary.**

**(a) RM-01 contributes ZERO Phase-3 evidence, and the roadmap's Phase-3 gate never asked it
to.** [`fixtures/real/RM-01/expected-causal.json`](fixtures/real/RM-01/expected-causal.json)
declares `not_asserted.fields` = `frozen_line`, `final_state`, `BROKEN_OUT`,
`BREAKOUT_CONFIRMED`, `bars_after_stop_index`, on **SPR-D-01 limits 1–2**. Under Phase 2 that
cost nothing: the engine halted at bar 10. **Phase 3 now evaluates bars 11–28 — eighteen bars
of the only real-market series in the repository — and no committed expectation covers the
result.** `RM01NotAssertedScope` makes that structural: it asserts the RM-01 test module reads
**none** of those five fields out of the record. What the module does assert about that window
is engine-internal consistency written by the implementer (`frozen_line.line is line_at_stop`,
one episode, the first post-breakout emission at the engine-derived stop) — legitimate, and
**not** fixture evidence. **Phase-3 conformance evidence is therefore SYNTHETIC-ONLY**: 23
constructed golden fixtures, plus a real series whose Phase-3 surface is unasserted by ruling.
*"All 23 golden + RM-01 reproduce"* is **true and materially narrower than it sounds**, and it
must never be absorbed into *"RM-01 reproduces."* The roadmap's Phase-3 exit criteria name only
`product/fixtures/golden/` — RM-01 sits in the **Phase-2** gate — so this is a **gap in the
criterion**, not a criterion failure, which is why the verdict above is MET.

**(b) D5 is UNDISCHARGED.** Eleven sealed differential probes exist (declared at
[#40 comment](https://github.com/tomerYannay/4UR4/issues/40#issuecomment-5106088344)) and carry
**no evidentiary weight**: **unsealed** (Verification holds no `Write` tool, so the content
passed through the Orchestrator — an interested party), **authored during implementation rather
than before**, which is a permanent unrepairable property of this instance, and **un-runnable**
until the harness accepts verifier-supplied uncommitted inputs. **The Strategic Product Reviewer
ruled explicitly that Phase 3 must not close counting probe *existence* as probe *coverage*, and
this determination does not.** Additionally, the Orchestrator disclosed a **partial leak**: two
clarifications sent to the implementer identified **two of the seven** corpus-blind regions,
reducing the reset-edge probes' diagnostic value. **The declaration is not a repository
artifact** — it lives as an issue comment, and
[`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md)
§5 still reads *"No such probe is in custody today."* Tracked as
[`maintenance-backlog.md`](maintenance-backlog.md) **M-62**; owner **Verification**.

**(c) The corpus cannot constrain several ruled behaviours, and this is MEASURED, not
asserted.** Both mechanical gates independently ran the `h_hold` mutant against **only** the
fixture tests and got **zero failures** — proving **an engine with `h_hold = 0` passes all 24
committed fixtures**, because every `RETEST_HELD` in the corpus has its hold leg on the same bar
as its return leg. `engine/tests/test_post_breakout.py`'s module docstring records exactly that,
and adds that **no fixture reaches the right edge of `F_fail` or `W_retest`** — the largest event
gap anywhere in the corpus is 4 bars against windows of 10 and 20. The **§11 post-breakout reset
edge** is likewise unfixtured: [`trendline-specification.md`](trendline-specification.md) §11's
own 2026-07-28 completeness note records *"Unexercised by the corpus — GX-06 and GX-22 both reset
from `ACTIVE`."* The `FAILED_BREAKOUT → NONE` exits (HD-25) are unfixtured for the same reason.
**These behaviours are covered ONLY by constructed unit tests.** That is legitimate evidence and
it is **weaker than fixture evidence** — a constructed test is authored by the same party as the
engine and pins the author's reading of the specification; a committed fixture predates the
engine and was approved independently. Both are in the record and this determination says which
is which.

**Is Phase 3's independence posture materially better than Phase 2's? Yes, on two criteria,
and no on the rest.** **E2-AUTHOR criterion 2's breach is bounded to Phase 2**: ticket (g)
carried **E2-AUTHOR-A as a testable acceptance criterion and named the must-not-read set
prospectively**, and (g) was **READY before implementation began**, so Phase 3 re-armed a control
Phase 2 never had. **Criterion 3 also improves**: Phase 2's attestation recorded that *no probe
was observed refusing*; on Phase 3 the implementer **hit a guard refusal and did not work around
it**, which is direct evidence the deny is a configuration rather than an instruction.
**Criterion 4 is unchanged** — separation is unverifiable in identity while
[#21](https://github.com/tomerYannay/4UR4/issues/21) is open. **And Phase 3 has no independence
attestation of its own**: only
[`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md)
exists. That is a **disclosed gap, not an unmet criterion** — the roadmap's Phase-3 entry text
carries E2-AUTHOR forward as a binding on the artifact and the author, not as a re-run of the
five-item Phase-2 entry checklist.

**What this determination does and does not do.** It closes Phase 3 and thereby satisfies part
of the Phase 4 entry criterion *"Phases 1–3 exit met"* — **only part**: Phase 1 exit is not met
and UNIV-METH is not met. It marks **no ticket Done**
([GOV-005](../governance/definition-of-done.md) — not the Steward's call), closes neither
[#40](https://github.com/tomerYannay/4UR4/issues/40) nor
[#36](https://github.com/tomerYannay/4UR4/issues/36), lifts no freeze, selects no
provider, and **edits no byte of** [`roadmap.md`](roadmap.md)
([GOV-002](../governance/roadmap-authority.md), [GOV-013](../governance/approval-gate.md)).

*Also true, and it limits what the 23 prove:* seven of the twenty geometry fixtures share bars
0–15 byte-identically and five share `B* = (6,93)`. **Twenty fixtures are not twenty independent
samples.** Two Phase-2 mutations (M-1, M-2) survive the committed corpus and were recorded as
findings with constructed adversarial cases rather than absorbed — no fixture was added, edited
or reinterpreted to accommodate them, and the same discipline held through Phase 3.

## Completed milestones
- Agent Operating System bootstrapped + executable in Claude Code (PR #1).
- Proposed MVP roadmap, PRD, specs, human-decision register (PR #8).
- **Phase 0 golden fixtures** (**23 synthetic** — 20 geometry + 3 null-anchor) + **RM-01**
  real-market case, PO-approved; **SC-1 = MATCH**, **SC-2 resolved (HD-11)** (PR #9; corrected
  under #16 by PR #18, which also landed spec §21, D-TL-11/12, GX-20, GX-21/22/23 and
  `tools/fixture-replay.mjs` under HD-15).
- Roadmap **APPROVED as a baseline** under GOV-013
  ([#23](https://github.com/tomerYannay/4UR4/issues/23)) — a baseline only: it lifts no freeze,
  authorizes no implementation, selects no provider and approves no spend.
- **HD-18 universe definition** and
  [`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md),
  the HD-06 due-diligence pack, the **HD-21** delegation record and **SPR-D-01** (PR #25, `d1a1c41`).
- **RM-01 under mechanical causal replay** — `expected-causal.json`, `real-causal.schema.json`,
  the `real/`-reading tool extensions (PR #30, `54b16ee`). The expectation is
  **replay-generated**: a regression guard against today's reference model, not independent
  verification.
- **The E2-AUTHOR tool-deny quarantine** — `bash-guard.mjs`, closing #20's configuration half
  (PR #32, `758c0a0`), merged **before** the engine PR deliberately.
- **The Phase 2 trendline engine** (PR #33, `ed92bbb`) and its hardening (PR #37, `c66fd294`).
- **The Phase 3 engine** — [PR #43](https://github.com/tomerYannay/4UR4/pull/43), `5ff74311`:
  confirmed breakout, line freezing `Λ^F`, retest, failed breakout, expiry and recompute, plus
  the widened conformance harness (full-corpus comparison in both directions, sweep
  `final_state` at every recorded scale, the §11 valid-walk check, the OQ-P3-7 unasserted-key
  census). 16 files, **all `engine/`**; no fixture, schema, tool or governance file touched.
- ChatGPT↔Claude **handoff protocol** + PR template + Agent Coordination Queue (PR #11);
  **Strategic Product Reviewer** added as the 10th permanent agent (PR #13); the
  **Historical Product Owner Decision Record — RM-01** in
  [`human-decisions.md`](human-decisions.md) (PR #15).

## Active work
- **PR #12** — Phase 1 market-data research (Issues **#4**, **#5**): provider comparison +
  survivorship/delisted research. **Draft; CI green; 0 reviews; awaiting strategic review.**
  This is the path to **HD-06**, and it is now the **only** open path to any further phase.
- **Issue [#21](https://github.com/tomerYannay/4UR4/issues/21)** — review verdicts cannot become
  citable artifacts, and review attribution collapses to a single account. **Required before
  HD-06**; a stated dependency of E2-AUTHOR **criterion 5**; the reason HD-22 part 3 cannot be
  closed; and the reason the D5 declaration had to be relayed by an interested party.
  **[#34](https://github.com/tomerYannay/4UR4/issues/34)** is the same root cause.
  It **was also recorded as required before *any* freeze lift, and the [#31](https://github.com/tomerYannay/4UR4/issues/31)
  lift proceeded without it** — the Product Owner's prerogative, restated here because the
  clause's own words were *"recorded here because the earlier condition should not silently
  disappear"*, and this refresh had dropped it. Found by the Strategic Product Reviewer.
- **Issue [#22](https://github.com/tomerYannay/4UR4/issues/22)** — evidence-tooling follow-ups.
- **D5 probe custody** ([`maintenance-backlog.md`](maintenance-backlog.md) **M-62**) — owner
  **Verification**. Undischarged; see the Phase-3 determination record (b).
- **Traceability debt from [#16](https://github.com/tomerYannay/4UR4/issues/16)** (the issue is
  CLOSED). #16 was never re-scoped to what PR #18 delivered, so the ticket→PR link is
  incomplete. A documentation debt, not an open ticket; reopening is an Orchestrator decision.

## Next milestone

**There is no further product implementation permitted today that does not require HD-06.**
Ranked below is what remains permitted, and it is **all evidence-hardening inside the delivered
`engine/` scope** — no new product capability.

1. **Close the D5 harness gap** — make the Phase-3 conformance harness accept a
   **verifier-supplied, uncommitted** probe input directory. It is the item that keeps eleven
   existing probes un-runnable, and it is **engine-local test infrastructure**, squarely inside
   the HD-22 lift. Needs a Ready ticket (GOV-015 rule 4) and one WIP slot. Highest value
   because it converts an owed gate obligation into a discharged one, and it is the only listed
   item that changes what a *future* phase gate can prove.
2. **Fix the two logged engine defects, L-2 first.** **L-2** — `P1NoLookAhead`'s direction
   assertion on a mutation that opens a later episode is false in general (a mutation may
   equally *remove* a later episode and legitimately lower the reported `confirmed_bar`); the
   gate reports 139 measured counterexamples and reports that it cannot fire today because the
   property corpus generates no multi-episode series. That makes it a **false-failure risk**
   that will surface as a mystery. **L-1** — `earliest_open_window`'s `min` is pinned by
   nothing; flipping it to `max` passes all 202 tests. Both are engine-local test
   infrastructure. **Neither figure was measured by the Steward**, who has no shell; both are
   relayed and both should be re-measured by whoever takes the ticket.
3. **Fixture the corpus-blind regions** — `h_hold` as a window, the §11 post-breakout reset
   edge, the `FAILED_BREAKOUT` exits, `F_fail`/`W_retest` right edges, recompute after expiry.
   A **new** golden fixture is a Phase-0 design artifact and is freeze-permitted; it does not
   touch a committed expectation, so HD-22 is not engaged. Third rather than first because it
   is the largest unit of work here and it is genuinely optional: constructed unit tests
   already cover the behaviour, and this converts weaker evidence into stronger evidence rather
   than closing an absence.
4. **RM-01's unasserted Phase-3 surface — DO NOT open it as engine work.** Narrowing
   `not_asserted` changes the scope of **SPR-D-01**, a delegated product decision. It is
   therefore an **HD-21 delegated question for the Strategic Product Reviewer**, and a Product
   Owner matter only if the SPR declines it — **not** an Implementation Engineer task. There is
   a harder problem beneath the governance one: the expectation for bars 11–28 has to come from
   somewhere. The reference model can produce it, and then it is circular under SPR-D-01
   limit 3 **and known to be stricter than the specification** — `tools/fixture-replay.mjs`
   discloses `h_hold` as NOT IMPLEMENTED. Hand-derivation from the specification by a party
   that has not read the engine is the only route that yields real evidence, and it is
   expensive. **Ranked last, and recommended as a decision to take rather than work to start.**

**What is NOT available, stated plainly because the temptation is to invent work.** **Phase 4
is not startable in any part.** Its entry criteria require Phases 1–3 exit **and UNIV-METH**,
and its exit criteria require a backtest **over the historical 4UR4 US Large-Cap 500 at each
date's point-in-time membership**. A backtest over 23 synthetic fixtures and one 29-bar real
series is not that, and calling it a Phase-4 increment would be scope drift
([GOV-007](../governance/product-focus.md)). **Phases 5–9 are each gated on the phase before
them.** **HD-06 gates Phase 1 implementation, and transitively Phases 4–9 wherever real market
data is needed** — which is everywhere they report a number. HD-06 requires money and licensing
and is **Product-Owner-only**; no agent may take it, and no agent may work around it.

**So: after the four items above, the honest answer is that all permitted product work is
complete and everything remaining is gated on HD-06.** The critical path is not engineering. It
is **(i)** completing the PR #12 research review and **(ii)** closing
[#21](https://github.com/tomerYannay/4UR4/issues/21), which is required before any financial
authorization — and then **HD-06 itself**, which only the Product Owner may take.

## Owed work — debts carried forward
Stated as **owed**, not done.

- **The RM-01 annotation schema was never updated.**
  [`fixtures/schema/real-annotation.schema.json`](fixtures/schema/real-annotation.schema.json)
  is **untouched**: it carries **no `causal_artifact` pointer** to the Half B record, and
  `confirmed_bar` is still described as *"HD-03: equals breakout_bar. NULL until data."* — a
  full-series description saying nothing about the as-of-time layer. *Verified on disk at this
  SHA.* A reader arriving at Half A alone is not told Half B exists.
- **No Phase-3 independence attestation exists.** Only the Phase-2 one is committed. See the
  determination above; disclosed gap, not an unmet criterion.
- **The D5 declaration is not a repository artifact**, and
  [`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md)
  §5 still says no probe is in custody. Amending it is the attester's, not the Orchestrator's
  (GOV-011).
- **Deferred provenance-tense correction — two sites remain.**
  [`human-decisions.md`](human-decisions.md)'s SPR-D-01 *Rationale* still reads *"**if**
  `expected-causal.json` is replay-generated…"*, and the [`roadmap.md`](roadmap.md) SPR-D-01
  ledger row keeps the conditional form deliberately, as a **dated record marked rather than
  rewritten**.
- **Low-severity prose-precision findings are tracked** in
  [`maintenance-backlog.md`](maintenance-backlog.md), not here. Nothing there blocks a milestone.
- **`main` IS branch-protected — 6 of HD-22's 7 parts**, with the seventh open and blocked on
  [#21](https://github.com/tomerYannay/4UR4/issues/21). Measured: `enforce_admins: true` ·
  PR-only merges · required check `Validate agent OS & governance` with `strict: true` · no
  force pushes · no deletions · direct push **empirically rejected**. **The one gap:
  `required_approving_review_count: 0`**, so "required exact-head reviews" is **unimplemented,
  not partially met**. It cannot be fixed by raising the number: GitHub forbids a PR author from
  approving their own PR, and under one shared identity every PR is authored by that identity.
  **The constraint is #21, not the setting.** *"Full branch protection is in place" is not an
  available statement.* **RESOLVED by the Product Owner 2026-07-26: not blocking, deviation
  recorded** — [`human-decisions.md`](human-decisions.md) → HD-22 part 3.

## Blocked work
- **#6** Market-data ingestion service (Phase 1 impl) — `blocked: freeze`, and additionally
  blocked on **HD-06**. Outside both `engine/` lifts.
- **#7** Trendline detection engine (Phase 2 impl) — **built and merged**; the exit
  determination is made above. It never passed a formal Definition of Ready, and that is
  recorded rather than smoothed: **E2-AUTHOR criterion 2 is genuinely UNMET** and #7 has **not**
  been backdated. **That determines the phase; it does not mark the ticket Done**
  ([GOV-005](../governance/definition-of-done.md)).
- **#40 / ticket (g)** Phase-3 engine — **delivered and merged** at `5ff74311`; the exit
  determination is made above. **Done is not asserted here**: ticket (g)'s own Done evidence
  requires the D5 probes to be held and run by a verifier who did not author the engine, and
  they are not. That is a [GOV-005](../governance/definition-of-done.md) call for Verification
  and Release & Ops, and the Product Steward does not make it.
- **Phases 4–9** — behind the build-freeze **and** their entry criteria **and**, from Phase 4
  onward, **HD-06**. Phase 4 additionally requires **UNIV-METH** (Phase 1 exit), which no
  committed code addresses.
- **Every Phase 2/3 surface outside `engine/`** — API, database, scanner, worker, dashboard,
  alerts, SaaS — remains frozen.

## Pending Product Owner decisions
- **HD-06** — data-provider selection + recurring spend (**human-gated**). **PENDING, and now
  the single gate on the entire remaining roadmap.** Research is delivered
  ([`data-provider-findings.md`](data-provider-findings.md),
  [`hd06-due-diligence.md`](hd06-due-diligence.md)); **Intrinio Startup is recorded as the
  leading candidate at ≈\$5,994 year 1 and is explicitly not selected.** Eight evidence
  prerequisites remain, **two marked blocking** — **C-1**, the only condition the Product Owner
  has accepted, and **C-2**, agent-*proposed* (as are C-3, C-4 and C-5; an agent may recommend a
  blocking condition, not impose one). C-2 is the sharpest: the candidate's history-depth claim
  is contradicted by its own upstream, and depth is the only ground on which it leads.
  [#21](https://github.com/tomerYannay/4UR4/issues/21)'s out-of-band confirmation is required
  before any financial authorization. **Neither `engine/` lift touches HD-06.**

**HD-06 is the only pending *HD-numbered* Product Owner decision — and that is not the same as
the only open question.**
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md)
§11.2 still escalates **OQ-U1…OQ-U7** to the Product Owner **with stated defaults**. Those are
open Product Owner questions, not HD entries. Both claims must travel together; only the first
is true on its own.

*Resolved and no longer pending:* **HD-12**, **HD-13**, **HD-14** (ratified) and **HD-15**
(approved), 2026-07-25 · **HD-16**, **HD-17** (superseded and widened by **HD-21**), **HD-18**,
**HD-19**, **HD-21**, 2026-07-26, plus **HD-20** — resolved not by the Product Owner but by the
delegated decision **SPR-D-01** · **HD-22**, 2026-07-26 · **[HD-24](human-decisions.md)** and
**[HD-25](human-decisions.md)**, 2026-07-28. **None of these selects a provider or authorizes
spend or licensing.** **Two HD-24 overreaches stay on the register rather than smoothed:** §3's
claim that ticket (g) satisfied GOV-015 rule 4 was **false when written** (closed forward, not
backdated), and §4's ruling rests on an attestation whose E2-AUTHOR-B record is **ABSENT**,
whose commit range is **not recorded**, and whose sign-off block is **deliberately unsigned**.
**[HD-23](human-decisions.md) remains PENDING PRODUCT OWNER CONFIRMATION.**

## Delegated product decisions (HD-21) — a second decision channel

- **HD-21 — APPROVED (Product Owner, 2026-07-26,
  [#27](https://github.com/tomerYannay/4UR4/issues/27)).** The permanent **Strategic Product
  Reviewer** may decide **reversible product-definition questions** autonomously under **ten
  conjunctive conditions**, with a mandatory record format and the decision marked
  `DELEGATED_PRODUCT_DECISION_APPROVED`. It **supersedes and widens HD-17**. **Condition 10
  differs in kind:** the **Project Auditor** — read-only, and not the producer of the work —
  must independently confirm the conditions were met, so every delegated decision carries
  **two** records. **Never delegated:** HD-06 purchase or spend, licensing, lifting or widening
  GOV-015, roadmap phase-order changes, core-thesis or target-customer changes,
  security/privacy/billing/PII, irreversible external actions, and **deletion of any important
  evidence or historical decision record**.
- **SPR-D-01 — RM-01 carries both analytical layers · resolves HD-20.** **Approved under
  bounded Product Owner delegation; not direct Product Owner authorship**, and **overturnable by
  the Product Owner at any time without cause.** **CONFIRMED against all ten conditions by the
  Project Auditor at `5b99ba6`** *(relayed, not independently authored — role-level
  independence, not organizational, pending
  [#21](https://github.com/tomerYannay/4UR4/issues/21))*. RM-01 carries **two records, neither
  superseding the other**: **Half A**, the full-series geometry, gated at **unit level** on an
  exported pure §8 function and explicitly **not** on pipeline output; and **Half B**, the
  as-of-time record (engine-derived stop at **bar 10**, `line_at_stop` `B* = (9, 158.40)`,
  `m = -0.0505453`, line `150.593`, close `164.19`, margin `0.0864461` *(raw clearance
  `ln(close) − ŷ`; the reference model's `events[].margin` field carries `0.0764461`, the same
  quantity net of `ε_break`)*), gated **within Phase-2-owned behaviour only**. **Half B narrows
  RM-01's Phase-2 assertable surface** to bars **0–9** plus the stop index. **RM-01's
  non-circularity attaches to Half A's human-approved geometry and the real prices, not to Half
  B's provenance.** **Its `not_asserted` list is what leaves RM-01 contributing zero Phase-3
  evidence** — see the Phase-3 determination record (a). Gate wording:
  [`roadmap.md`](roadmap.md) Phase 2 exit criteria; evidence:
  [`fixtures/README.md`](fixtures/README.md) §6b.
- **Sequencing rule, binding on SPR-D-02 onward:** a delegated decision's status line reads
  `RESOLVED — pending condition-10 audit` until the Project Auditor confirms it.
- **SPR-D-03 — STANDS. M-09 is CLOSED.** `product/fixtures/real/**` is classified **R2b
  PERMEABLE by necessity**, with a mandatory no-credit rider. **Condition-10 CONFIRMED.**
  **Scope: M-09 only.**
- **SPR-D-02 — DOES NOT STAND.** Returned **NOT CONFIRMED** under condition 10: the decision was
  never written to [`human-decisions.md`](human-decisions.md) while a
  [`maintenance-backlog.md`](maintenance-backlog.md) row already cited it forward — the
  sequencing rule, broken on its first use. Retained because the reversal must stay visible.

## Open issues / PRs (governed index)
- **The GitHub issue list is authoritative; this index is a snapshot and is stale by
  construction.** It was **not re-queried on 2026-07-28** — the Product Steward has no shell —
  so **no count is stated here.** Known open: **#4**, **#5** (Phase 1 research) · **#6** (Phase 1
  impl, `blocked: freeze`) · **#7** (Phase 2 engine — built, merged, determined; not marked
  Done) · **#10** (Agent Coordination Queue, permanent index) ·
  **[#21](https://github.com/tomerYannay/4UR4/issues/21)** (review verdicts cannot become
  artifacts + single-account attribution — **required before HD-06**) ·
  **[#22](https://github.com/tomerYannay/4UR4/issues/22)** (evidence-tooling follow-ups) ·
  **[#23](https://github.com/tomerYannay/4UR4/issues/23)** (roadmap baseline, HD-16 — ruling
  artifact) · **[#24](https://github.com/tomerYannay/4UR4/issues/24)** (universe, HD-18 — ruling
  artifact) · **[#27](https://github.com/tomerYannay/4UR4/issues/27)** (HD-21 delegation) ·
  **[#28](https://github.com/tomerYannay/4UR4/issues/28)** ·
  **[#31](https://github.com/tomerYannay/4UR4/issues/31)** (HD-22, the Phase-2 `engine/` lift) ·
  **[#34](https://github.com/tomerYannay/4UR4/issues/34)** (GOV-013's Enforcement clause asserts
  a structural guarantee this repository does not provide; same root cause as #21) ·
  **[#36](https://github.com/tomerYannay/4UR4/issues/36)** — **still OPEN**, both parts answered
  by HD-24 (Part A: the Phase-3 lift granted, §3; Part B: E2-AUTHOR criterion 5 ruled
  affirmatively, §4, on an attestation carrying less than roadmap criterion 5 asks for). Being
  answered is not being closed, and closing it is an Orchestrator action ·
  **[#39](https://github.com/tomerYannay/4UR4/issues/39)** (HD-24 itself) ·
  **[#40](https://github.com/tomerYannay/4UR4/issues/40)** — **still OPEN**: ticket (g)'s live
  issue. **⚠ Its body remains STALE** — it leads with *"Status: NOT READY. Do not start."* while
  (g) became READY on 2026-07-28 and has since been **delivered and merged**. Updating or
  closing it is an **Orchestrator** action the Product Steward may not take. Until it lands,
  [`planning/ticket-set.md`](planning/ticket-set.md) is the authority on (g), which is a
  **stated exception** to *"the issues are authoritative."*
- **CLOSED, retained only because they are cited above:**
  **[#16](https://github.com/tomerYannay/4UR4/issues/16)** (Phase 0 evidence correction) ·
  **[#19](https://github.com/tomerYannay/4UR4/issues/19)** (roadmap exit-criteria gap; the
  derived fixture-coverage gate is on `main`) ·
  **[#20](https://github.com/tomerYannay/4UR4/issues/20)** (CLOSED `2026-07-26T23:17:13Z`,
  `stateReason: COMPLETED`, by PR #32) ·
  **[#26](https://github.com/tomerYannay/4UR4/issues/26)** (RM-01 as-of-time divergence;
  resolved by SPR-D-01).
- **Open PRs — a snapshot, not a claim of completeness.** At this refresh: **#12** (Phase 1
  research, draft, CI green, 0 reviews, awaiting strategic review). Coordination queue:
  [#10](https://github.com/tomerYannay/4UR4/issues/10).
- **[PR #43](https://github.com/tomerYannay/4UR4/pull/43) MERGED** at `5ff74311` — the **Phase 3
  engine**. 16 files, **all `engine/`**; every other top-level tree object-identical to base.
  **The HD-22 fixture-immutability guard engaged and passed on the merits.** Three gate verdicts
  at the exact head. Relayed: 202 tests (base 141); all 23 golden reproduce in full, **and RM-01
  reproduces only its Phase-2 assertable surface** — record (a) above forbids that phrase from
  travelling without this rider, and an earlier form of this very line dropped it.
  Both directions, **first run, nothing reconciled**.
- **Recently merged:** **[#37](https://github.com/tomerYannay/4UR4/pull/37)** at `c66fd294`
  (ticket (h) engine hardening, M-28/29/30/32; the first PR on which the fixture-immutability
  guard did real work) · **[#38](https://github.com/tomerYannay/4UR4/pull/38)** at `0b564a41`
  (the E2-AUTHOR independence attestation, the HD-23 record, ticket (g)'s first statement, the
  Phase-3 implementation plan — documentation only) ·
  **[#33](https://github.com/tomerYannay/4UR4/pull/33)** at `ed92bbb` (the Phase 2 engine) ·
  **[#32](https://github.com/tomerYannay/4UR4/pull/32)** at `758c0a0` (the E2-AUTHOR tool-deny
  quarantine) · **[#30](https://github.com/tomerYannay/4UR4/pull/30)** at `54b16ee` (RM-01
  causal replay) · **[#25](https://github.com/tomerYannay/4UR4/pull/25)** at `d1a1c41` (universe
  definition, Phase 2 plan, HD-06 due diligence, HD-21, SPR-D-01) ·
  **[#18](https://github.com/tomerYannay/4UR4/pull/18)** at `e56ed8e` (Phase 0 evidence
  correction + as-of-time fixture audit).

## Sources
[`roadmap.md`](roadmap.md) · [`requirements.md`](requirements.md) · [`human-decisions.md`](human-decisions.md) ·
[`trendline-specification.md`](trendline-specification.md) · [`confidence-specification.md`](confidence-specification.md) ·
[`fixtures/README.md`](fixtures/README.md) · [`fixtures/VERIFICATION.md`](fixtures/VERIFICATION.md) ·
[`maintenance-backlog.md`](maintenance-backlog.md) · [`planning/ticket-set.md`](planning/ticket-set.md) ·
[`glossary.md`](glossary.md) ·
[`../governance/build-freeze.md`](../governance/build-freeze.md) ·
[`../governance/definition-of-ready.md`](../governance/definition-of-ready.md) ·
[`../governance/definition-of-done.md`](../governance/definition-of-done.md) ·
[`../governance/ticket-hygiene.md`](../governance/ticket-hygiene.md) ·
[`../governance/product-focus.md`](../governance/product-focus.md) ·
[`../docs/architecture/mvp-architecture.md`](../docs/architecture/mvp-architecture.md) ·
[`../docs/architecture/phase3-implementation-plan.md`](../docs/architecture/phase3-implementation-plan.md) ·
[`../docs/architecture/phase2-independence-attestation.md`](../docs/architecture/phase2-independence-attestation.md) ·
[`../docs/architecture/universe-methodology.md`](../docs/architecture/universe-methodology.md) ·
[`../docs/architecture/phase2-implementation-plan.md`](../docs/architecture/phase2-implementation-plan.md) ·
[`../docs/architecture/phase2-independence-mechanism.md`](../docs/architecture/phase2-independence-mechanism.md) ·
[`../docs/operations/agent-handoff-protocol.md`](../docs/operations/agent-handoff-protocol.md) ·
[`../GOVERNANCE.md`](../GOVERNANCE.md)
