# 4UR4 — Phase-2 independence attestation (E2-AUTHOR)

> **What this document is.** The §9 attestation artifact required by
> [`phase2-independence-mechanism.md`](phase2-independence-mechanism.md) before the Phase-2
> exit gate is assessed. Its field set is that document's §9 table, in that order.
>
> **What this document is NOT.** It is **not** a finding that E2-AUTHOR is satisfied. It is
> **not** a ruling on E2-AUTHOR criterion 5, which is an open Product Owner decision (§9
> below). Several required fields are recorded as **ABSENT**, and the mechanism doc's own
> rule governs those: *"A control that has not been observed refusing is treated as absent."*
> An attestation that overclaims is worse than one that is modest and kept
> ([mechanism §8](phase2-independence-mechanism.md)).

- **Attested at:** 2026-07-28
- **Attester role:** Product Steward
- **Attester eligibility:** the Product Steward did **not** author `engine/` and holds no
  `engine/` commits. This is the eligibility mechanism §9 requires ("recorded by a party
  **other than the author**", [GOV-011](../../governance/separation-of-duties.md) rule 2).
- **Roles that are NOT eligible to attest, and why:** the **Orchestrator** (it has read the
  reference model, and it authored executable lines in `engine/` — see §4), and whoever
  authored `product/fixtures/real/RM-01/expected-causal.json` (also model-exposed).

## 0. Transcription relationship — read this before any field below

**This attestation transcribes findings recorded by others. The Product Steward performed
none of the underlying checks and has no Bash, no shell and no ability to execute a test, a
probe or a git query.** Every positive statement below is therefore one of exactly two
kinds, and each field says which:

| Kind | Meaning | How to read it |
|---|---|---|
| **T** — transcribed | a finding recorded by another agent in a committed artifact, cited by that artifact | the cited artifact is the evidence; this document is an index to it |
| **R** — read off the tree | a property of a committed file the attester read directly at this SHA | re-checkable by anyone by opening the named file |

No field is marked **verified-by-attester**, because none is. Where a field's evidence does
not exist, it is marked **ABSENT** — not "weak", not "pending", not silently omitted.
Absence of a control is a disclosure, not a footnote (mechanism §5: *"Instruction is not a
control"*).

---

## 1. Base — `ABSENT / NOT APPLICABLE (no clean room existed)`

| Field | Value | Kind |
|---|---|---|
| Clean-room base commit SHA | **ABSENT** — no clean-room checkout was created, so there is no clean-room base SHA to record (see §2) | T |
| Head at which the A-check was recorded | `f0455f6` — the Project Auditor's condition-10 confirmation head, at which the A-check is recorded ([`human-decisions.md`](../../product/human-decisions.md), SPR-D-03 status line; [`maintenance-backlog.md`](../../product/maintenance-backlog.md) M-35) | T |
| Head carrying the E2-AUTHOR-B breach | `7ab8075` (PR #33 strategic-review head) — see §4 | T |
| Quarantine manifest version and hash | **NO P0 MANIFEST EXISTS.** There is no committed quarantine manifest, no content hashes, and no CI check asserting manifest-tree agreement. Mechanism AC-2 is **unmet** | R |

**What exists instead of P0, stated so the gap is not mistaken for the control.** The
quarantine is expressed as a **hard-coded list in a hook**, not as a hashed manifest:
[`.claude/hooks/bash-guard.mjs`](../../.claude/hooks/bash-guard.mjs) exports
`QUARANTINE['implementation-engineer'] = ['tools/fixture-replay.mjs',
'product/fixtures/VERIFICATION.md', 'docs/architecture/phase2-independence-mechanism.md']`
plus `WHOLLY_QUARANTINED_DIRS = new Set(['tools'])`. The `tools/` entry supplies a partial
default-deny over that directory. **It supplies no content hashes**, so mechanism threat
**T10 (quarantine decay)** — rated *high over time* — is uncountered: a rename, a split, or
a second model added outside `tools/` escapes silently. (Kind: R.)

## 2. Absence — `P1 WAS NOT USED`

**The primary control was not applied.** No clean-room repository was created; the engine was
authored inside this repository. There is consequently **no** P0-manifest-check transcript
run inside a clean room, **no** demonstration that the quarantined blobs were absent from a
tree, and **no** demonstration that they were absent from an object store. (Kind: R — the
absence of any such artifact anywhere under `docs/`, `product/` or `.claude/` is a property
of the tree at this SHA.)

Mechanism §10 ranks P1 **first**, as "the primary control", the one that "fails closed by
construction" and "does not rot". Its absence is the single largest gap in this attestation
and it is the reason threats **T3** (prior-session memory), **T4** (git-history retrieval)
and **T5** (network retrieval) rest entirely on defence-in-depth layers that the mechanism
doc itself labels "defence in depth only".

**This absence is not recoverable after the fact.** A clean room can be created for a future
phase; it cannot be retro-applied to `engine/` as it stands.

## 3. Liveness — `NO DENY-PROBE TRANSCRIPT EXISTS; P2 IS THEREFORE TREATED AS ABSENT`

Mechanism §5, control P2, states the rule this field must be judged by, verbatim:

> **a liveness probe, not a declaration**: before authoring begins, the author attempts a
> `Read` of a canary path in the manifest and of one network route, and records the refusal
> verbatim; the verifier repeats both probes independently. **A control that has not been
> observed refusing is treated as absent.**

| Control | Status | Kind |
|---|---|---|
| P2 author-run `Read` deny probe, verbatim transcript | **ABSENT.** No verbatim refusal transcript is recorded in any committed artifact | R |
| P2 independent verifier re-run of the same probes | **ABSENT** | R |
| P2 network-route probe (repository blob / raw URL / `gh api` contents) | **ABSENT**, and no network route is covered by any committed deny rule | R |
| P3 shell-layer QUARANTINE category | **EXISTS** — `quarantineBlock()` in `bash-guard.mjs`, with a hook test suite executed by CI (`.github/workflows/governance-validation.yml`, step *"Run Bash safety hook tests"*, `node .claude/hooks/bash-guard.test.mjs`) | R |
| The configuration that makes P2 a real control rather than an instruction | **EXISTS** — [`.claude/settings.json`](../../.claude/settings.json) registers a second `PreToolUse` matcher, `Read\|Grep\|Glob\|Edit\|Write\|MultiEdit\|NotebookEdit`, routed to the same hook, so the read-family tools are gated by configuration and not by prompt | R |

**The distinction that matters.** The *configuration* half of the read-deny exists and is
CI-tested against its own unit cases (delivered by PR #32). What does **not** exist is any
record of that configuration **refusing the actual authoring session** at the time it
authored. Under P2's own rule the control is therefore recorded as **absent** for the purpose
of this attestation, while the code and its tests are recorded as present. Both statements are
true and neither substitutes for the other.

**Known limitations of the layer that does exist**, carried rather than dropped:
[`maintenance-backlog.md`](../../product/maintenance-backlog.md) M-23 (a repo-root recursive
content search returns matching *lines* from the reference model — a **disclosed residual**,
not a closed hole), M-24/M-25 (bounded over-blocks), M-27 (the `settings.json` `$comment`
enumerates only `fixture-replay.mjs` among three denied paths), and M-22 (the parity check
does not cover GOV-016 temporary specialists).

## 4. Authorship — `engine/` HAS TWO AUTHORS, AND ONE B-RECORD IS ABSENT

**This section is the breach. It is carried on the face of the attestation, not appended to
it.**

| Field | Value | Kind |
|---|---|---|
| Authoring role | Implementation Engineer (primary author of `engine/`) | T |
| Configuration profile | the `implementation-engineer` role entry in `bash-guard.mjs`'s `QUARANTINE`, enforced through both `PreToolUse` matchers in `settings.json` (§3) | R |
| Second author | **the orchestrating session**, which authored **6 executable lines in `engine/`** | T |
| E2-AUTHOR-B record for commit `7ab8075` | **ABSENT — not weak, ABSENT.** The orchestrating session had **read the reference model**. It is not eligible to hold a B-record, and none exists | T |
| Commit range authored | **NOT RECORDED.** No committed artifact enumerates the `engine/` commit range per author. This is owed | R |
| Integrator (must not be the author) | **NOT RECORDED**, and under one shared identity not externally distinguishable in any case (§9) | R |

**The two-author disclosure, stated plainly.** `engine/` was not authored by a single
model-clean session. A second session — the orchestrating one, which had read
`tools/fixture-replay.mjs` — contributed 6 executable lines. For those lines the preventive
control E2-AUTHOR-B did not hold, and no record can make it hold retrospectively. The
sites of record are [`maintenance-backlog.md`](../../product/maintenance-backlog.md) **M-35**
(which states the B-record for `7ab8075` is ABSENT and why) and **M-32** (the Project
Auditor's independent observation of a style discontinuity in `engine/envelope.py` — "a faint
tell of second-hand authorship — which it is"); the narrative disclosure accompanies the
`project-state.md` update travelling with PR #35.

**What this does and does not mean for the gate.** Under the roadmap's own ordering,
**E2-AUTHOR-A governs where A and B diverge** ([`roadmap.md`](../../product/roadmap.md),
Phase 2): *"an unblemished read-history is not a defence for a transcribed artifact"* — and
symmetrically, a blemished read-history is not by itself an A-violation. The A-check result is
§5. But B is the control that exists to stop an A-violation from ever being written, and for
these 6 lines it did not operate. **That is a breach of a preventive control, disclosed, not
dissolved.**

## 5. A-checks — D1 PERFORMED; D2, D3, D4 NOT PERFORMED; D5 NOT APPLICABLE

### D1 — linkage · `PERFORMED AND PASSING`

D1 is the one detective control mechanism §6 rates **decisive**. It is satisfiable from the
tree and is executed on every pull request.

| Element | Where | Kind |
|---|---|---|
| The check | [`engine/tests/test_architecture.py`](../../engine/tests/test_architecture.py), class `A3NoReferenceModel` | R |
| **The forbidden set is derived, not named** | `sibling_directories()` returns every non-hidden top-level repository directory except `PERMITTED_SIBLINGS = {"engine", "product"}`, computed from `os.listdir(REPO_ROOT)`. A directory added later — "including a successor to the current evidence tooling" — is covered automatically, without an edit | R |
| **Anti-vacuity assertion** | the same class asserts `len(sibling_directories()) >= 3` and `"engine" not in sibling_directories()`, so a derivation that silently returned nothing fails the suite instead of passing it. `test_no_engine_source_references_a_forbidden_sibling_directory` additionally asserts the derived set is non-empty before using it | R |
| Execution-route coverage | `BANNED_CALLS = {"open", "input", "eval", "exec", "compile", "__import__"}` is asserted absent from every `engine/` module, closing the "execute" sense of the criterion alongside the "import" sense | R |
| Executed by CI | `.github/workflows/governance-validation.yml`, step *"Phase 2 engine — conformance against every fixture"*: `python3 -m engine.tests.run_all` | R |
| Result of record | The **Project Auditor performed and recorded the A-check**, at `f0455f6` (M-35) | T |

**What D1 settles and what it does not.** It settles the *executable* senses of "import,
copy, execute": there is no import, no dependency edge, and no invocation route from `engine/`
to `tools/`. It settles nothing about mechanical translation (mechanism §8.1).

### D2 / D3 / D4 — `NOT PERFORMED`

| Check | Status | Consequence |
|---|---|---|
| **D0** corpus baseline (a prerequisite, not a check) | **DOES NOT EXIST** | Without it D2 and D3 "report the shared vocabulary of the problem domain and are worthless" (mechanism §6). Their absence is therefore not merely a missing check but a missing precondition |
| **D2** verbatim k-gram overlap | **NOT PERFORMED** | Near-blind to the realistic threat in any case: Python-vs-JavaScript token overlap is low even for a literal translation (mechanism §6) |
| **D3** model-private lexicon (hashed) | **NOT PERFORMED** — no hashed lexicon file exists; mechanism AC-5 is unmet | The control against *honest* leakage (T1–T3, T8) is absent |
| **D4** structural comparison worksheet | **NOT PERFORMED** — no worksheet exists; mechanism AC-6 is unmet | Rated **weak** by the mechanism doc regardless: "substantial structural similarity is the expected outcome of genuine independence" |

(Kind: R for each — the absence of the artifact in the tree.)

### D5 — divergence fingerprint · `NOT APPLICABLE AT PHASE 2`

**Recorded as a named requirement, with the reason stated, per mechanism §9 and §7.**

D5 contributes **nothing** at the Phase-2 gate, and mechanism §7's judgement is that it
cannot be made to. The reason, in the mechanism doc's own terms: of the four divergences the
model discloses, **three lie in behaviour Phase 2 does not implement**, so an independent
Phase-2 engine and the model agree there **vacuously — both are silent**; and the fourth lies
inside Phase-2 scope but is **not determined by the specification**, so a spec-authored engine
may legitimately reinvent the same choice and agreement proves nothing. Turning it into a
pass/fail test "would fail honest engines and pass dishonest ones, which is worse than having
no test. It should not be built."

**Therefore: D5 is not applicable at Phase 2 — by design, not by omission.** It becomes a
real signal at the **Phase-3** gate in one specific form (sealed, spec-derived, verifier-held
differential probes), which mechanism AC-7 assigns to Verification. **No such probe is in
custody today**, and that is a Phase-3 entry gap recorded here so it is not discovered at the
Phase-3 gate. (Kind: T for the judgement; R for the absence of a custody declaration.)

## 6. Duties — NAMED, BUT NOT SEPARABLE FROM OUTSIDE THE REPOSITORY

| Duty | Role named | Identity as it appears in git and GitHub |
|---|---|---|
| Author | Implementation Engineer (plus the orchestrating session, §4) | `tomerYannay` |
| Verifier | Verification | `tomerYannay` |
| Reviewer | Code Review; Project Auditor for the A-check | `tomerYannay` |
| Attester | Product Steward (this document) | `tomerYannay` |

The **roles** are distinct and their outputs are distinguishable inside the repository by the
artifacts each produced. The **identities** are not distinguishable from outside it. See §9.

**T11 — the review-leakage rule.** Mechanism §4 states T11 as: the verifier, who may read the
model, feeds model-derived structure back to the author as review comments. Its own rating is
*"low, and invisible"*.

- **The rule was stated** to the reviewing roles: review findings must be justified by the
  specification or the fixtures, never by the reference model, and a comparison finding is
  raised as a **finding**, not as a suggested implementation (mechanism §5, P5).
- **The reviewing sessions report that it was observed**, and **no committed review record
  cites the reference model.** (Kind: R for the second clause; T for the first.)
- **This is self-report and is labelled as such.** T11 leakage is invisible by construction;
  no artifact in this repository can establish it did not occur. The statement mechanism §9
  requires — "a statement that the T11 review-leakage rule was observed" — is hereby recorded
  **as a self-report of the reviewing roles, not as a verified finding of the attester.**

## 7. Residual risk — WHAT WAS NOT ESTABLISHED

Recorded verbatim in substance from mechanism §8 and §10, because an attestation must not be
readable later as proving more than it does.

**The residual claim the Phase-2 gate can honestly make, and no more:** *the committed engine
does not link to, execute, or verbatim-copy the reference model; and no automated or human
check performed can exclude the possibility that it was mechanically translated by a party
determined to do so and to conceal it.*

**This attestation must claim less than that**, because the environment clause of it does not
hold here:

1. **"It was authored in an environment where the model was absent" is NOT available.** P1 was
   not used (§2). The model was present on disk throughout.
2. **Mechanical translation is not detectable with confidence.** D1 catches linkage; D2, D3
   and D4 catch copying, careless naming and arbitrary-choice mimicry — and D2, D3 and D4 were
   **not performed** (§5).
3. **Structural similarity has low evidential value for this problem.** The specification
   prescribes the algorithm closely, so genuinely independent authors converge; any control
   that treats similarity as suspicion **punishes fidelity**.
4. **B is unverifiable after the fact, permanently** — and here it is worse than unverifiable:
   for 6 executable lines it is **known not to have held** (§4).
5. **The permeable set is large and cannot shrink.** An engine derived entirely by fitting to
   `causal_record` — never reading the model, never opening the specification — would pass
   every control in the mechanism document and would also pass the exit gate. **RM-01 is the
   check that bites there**, which is why the Product Owner's 2026-07-26 ruling placing RM-01
   in the Phase-2 exit gate carries more weight than any control in this attestation.

**Disposition.** This residual risk is **irreducible by any mechanism available in this
repository**. The correct disposition is to **accept and document it as a recorded decision**,
which mechanism AC-10 assigns to the Product Steward and the Product Owner jointly. **That
acceptance has not been recorded.** It is owed and is not granted here: the Product Steward
may raise it, and only the Product Owner may accept it.

## 8. Human sign-off — `OWED. THIS BLOCK IS DELIBERATELY UNSIGNED.`

```
E2-AUTHOR independence attestation — human sign-off

  Name:            ______________________________   [ UNSIGNED — OWED ]
  Role:            Product Owner
  Date:            ______________________________   [ UNSIGNED — OWED ]
  Artifact:        ______________________________   [ UNSIGNED — OWED ]
  Head attested:   ______________________________   [ UNSIGNED — OWED ]

  By signing, the Product Owner records ONLY that this attestation has been read
  and its disclosures accepted as accurate. Signing does NOT rule that E2-AUTHOR
  criterion 5 is satisfied (§9), and does NOT accept the §7 residual risk — both
  are separate decisions requiring their own words.
```

**Nothing above is signed, and no agent may sign it.** The signature is a
[GOV-013](../../governance/approval-gate.md) human artifact. Any reading of this document as
"attested and signed" is a misreading of an explicitly unsigned block.

## 9. On its face — the single-identity disclosure, and criterion 5

**Stated here as a disclosure, not a footnote, because it is the fact that decides what this
document is worth.**

1. **All attribution collapses to one identity.** Author, verifier, reviewer and attester
   commit and comment as `tomerYannay`. The §6 role separation is real *inside* the repository
   and **unverifiable from outside it**.
2. **The artifact therefore rests on the human sign-off alone.** Mechanism §9 says this
   exactly of the committed-file stopgap: it "satisfies 'immutable and citable' but not
   attribution — inside this repository every agent commits under one identity, so the
   artifact's authorship rests on the human sign-off alone." The sign-off block is **unsigned**
   (§8). **At this moment the artifact rests on nothing but its own accuracy.**
3. **Whether this satisfies E2-AUTHOR criterion 5 is an OPEN PRODUCT OWNER DECISION.** It is
   mechanism **AC-8**, which offers two routes and no third: **either**
   [#21](https://github.com/tomerYannay/4UR4/issues/21) is resolved so a non-authoring role can
   record a citable, attributed artifact, **or** the Product Owner rules the §9 stopgap
   acceptable. Mechanism §9 is explicit that this "is not for the Architect to decide"; it is
   equally not for the Product Steward to decide. It is raised as **Part B of issue #36**.
4. **THIS DOCUMENT DOES NOT CLAIM THAT E2-AUTHOR CRITERION 5 IS SATISFIED.** It claims only
   that the **artifact half** of criterion 5 now exists. The **ruling half** does not.

### E2-AUTHOR's five criteria — status, so no reader has to infer it

| # | Criterion | Status | Basis |
|---|---|---|---|
| 1 | #20 has defined the enforceable independence mechanism | **UNMET** — #20 is open; the document half is on `main`, the configuration half landed with PR #32, and the issue has not closed | T |
| 2 | The **Ready** ticket carries E2-AUTHOR-A as a testable acceptance criterion and names the must-not-read set | **UNMET — and this is a real deviation, recorded rather than dissolved.** `engine/` was authored before its ticket ([#7](https://github.com/tomerYannay/4UR4/issues/7)) reached Ready; the ticket definition in [`ticket-set.md`](../../product/planning/ticket-set.md) carried neither element at the time. **#7 has NOT been backdated to Ready.** Fitting the record to the outcome is the failure this corpus exists to catch | R |
| 3 | The authoring agent is configuration-denied, not merely instructed | **PARTIALLY MET.** A real configuration deny exists over the read-family tools (§3) — this is a mechanism, not a prompt. But the **primary** control (P1 clean room) was not used (§2), and no probe was ever observed refusing (§3) | R |
| 4 | Authorship separated from verification | **MET IN ROLE, UNVERIFIABLE IN IDENTITY** (§6), and **breached in part**: a model-exposed session authored 6 executable lines (§4) | T |
| 5 | The claim is attested and citable, recorded by a party other than the author | **ARTIFACT HALF: satisfied by this file, subject to signature. RULING HALF: OPEN — Product Owner, AC-8, issue #36 Part B.** Not claimed satisfied | R |

## 10. What this document discharges — stated narrowly on purpose

[`maintenance-backlog.md`](../../product/maintenance-backlog.md) **M-35** records two things
at once: that *"the E2-AUTHOR-A attestation does not exist as a file in the tree"*, and that
roadmap criterion 5 is *"by its own words unsatisfiable while #21 is open"*.

- **This file discharges the first half, unilaterally.** The attestation now exists as a
  committed, citable artifact carrying the §9 field set including its absences.
- **It does not touch the second half.** That is a Product Owner ruling (§9.3).
- **Net effect on what is owed: "artifact + ruling" becomes "ruling only."** That is the whole
  of the claim. **It is not a Phase-2 gate pass, it is not a freeze lift, it authorizes
  nothing, and it does not make Phase 2 exit assessable** — §§1–5 record four absent controls
  and one absent commit range, and §7's acceptance is still owed.

---

**Related:** [`phase2-independence-mechanism.md`](phase2-independence-mechanism.md) (§9 field
set, §10 author brief, §11 acceptance criteria) ·
[`roadmap.md`](../../product/roadmap.md) (Phase 2, E2-AUTHOR-A/B and the five criteria) ·
[`human-decisions.md`](../../product/human-decisions.md) (HD-15 conditions 1–3, HD-22,
SPR-D-03) · [`build-freeze.md`](../../governance/build-freeze.md) (GOV-015, the `engine/`
scoped lift) · [`separation-of-duties.md`](../../governance/separation-of-duties.md)
(GOV-011 rule 2) · [`approval-gate.md`](../../governance/approval-gate.md) (GOV-013) ·
[`maintenance-backlog.md`](../../product/maintenance-backlog.md) (M-22…M-35) ·
[`project-state.md`](../../product/project-state.md) ·
[Issue #20](https://github.com/tomerYannay/4UR4/issues/20) ·
[Issue #21](https://github.com/tomerYannay/4UR4/issues/21) ·
[Issue #36](https://github.com/tomerYannay/4UR4/issues/36)
