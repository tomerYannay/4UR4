# 4UR4 — Phase-2 Independence Mechanism (design)

> **Status: DESIGN / SPECIFICATION ONLY under [GOV-015](../../governance/build-freeze.md).**
> The build-freeze is **ON**. Nothing here is built, scaffolded, configured or merged
> by this document. It specifies controls; creating them is a separate, assigned
> action by the roles named in §11. This document is the Architect's deliverable for
> [Issue #20](https://github.com/tomerYannay/4UR4/issues/20) and satisfies no other
> part of it on its own.

**Author restriction observed.** While writing this, `tools/fixture-replay.mjs` was
read **only to line 60 — its header comment block**, which is the file's own
disclosure of its status and its four divergences and is already quoted in
[`build-freeze.md`](../../governance/build-freeze.md) and
[`fixtures/README.md`](../../product/fixtures/README.md). No part of its
implementation was read. Designing a quarantine is not a licence to breach it.

**This document is itself inside the quarantine (see §4, Q4).** It names the four
regions in which the model is known to diverge from the specification. That is
negative information about the model, and it degrades the one detective control that
has real discriminating power (§7). The Phase-2 author is therefore given the
**author-facing brief** (§10) — the rules, with no model-derived content — and not
this file. Nothing in this document discloses model internals; it must stay that way.

---

## 1. What independence is actually for

The Phase-2 exit gate is *"the engine reproduces every fixture exactly."* Its
evidential value is an **N-version argument**: two implementations, written
separately from the same specification, agreeing to six significant figures is
strong evidence that both read the specification the same way and that neither
carries an isolated arithmetic error. That argument has exactly one premise —
**the two implementations are independent derivations**. If the engine is a
transcription of `tools/fixture-replay.mjs`, N collapses from 2 to 1: the gate
still passes, and it now proves only that the transcription was accurate.

Two consequences shape everything below.

1. **Independence is about the code path, not the numbers.** Every expected value
   in `product/fixtures/golden/**` was produced by the model, and the fixtures'
   `causal_record` blocks publish its intermediate state — candidate lists, gate
   traces, per-bar line values. The author **must** read those; they are the
   contract the roadmap's exit criteria name field by field. So "independent of the
   model" can never mean "independent of the model's outputs". It means: the engine
   was **derived from the specification**, and the model's *source* played no part.
2. **Independence is not the only defence against circularity, and not the last
   one.** The synthetic set is spec-derived, so it can only prove self-consistency
   with the written spec ([`fixtures/README.md`](../../product/fixtures/README.md) §6).
   The non-circular anchor is **RM-01** — real OHLCV, human-approved geometry — which
   the Product Owner ruled into the Phase-2 exit gate on 2026-07-26. Independence
   protects the N-version argument; RM-01 protects against both implementations
   being faithful to a specification that describes the wrong object. Neither
   substitutes for the other, and the residual risk in §9 is smaller because RM-01
   exists.

## 2. The ruled criterion, restated

| Half | Statement | Nature | Verifiable when |
|------|-----------|--------|-----------------|
| **A — artifact property** (governing) | The committed engine must not **import, copy, execute or mechanically translate** the reference model or any successor model under `tools/` | property of the code that exists | any time, indefinitely, by anyone |
| **B — read restriction** (preventive) | The engine is authored by an agent that has **not read** the reference model | claim about a session's history | only while the session exists; otherwise self-report |

Where they diverge, **A governs**: an engine that transcribes the model fails even
if no agent ever opened it, and a clean read-history is not a defence for a
transcribed artifact ([`roadmap.md`](../../product/roadmap.md), E2-AUTHOR-A/B).
This document designs **B** as a set of preventive controls (§5) and **A** as a set
of detective controls (§6–§7).

## 3. The quarantine set, and what cannot be quarantined

The single most important design fact is that the quarantine is **partial by
necessity**, and pretending otherwise would produce a control that is either
useless or blocks the work.

| ID | Surface | What it leaks | Disposition |
|----|---------|---------------|-------------|
| Q1 | `tools/fixture-replay.mjs` | the model's source: decomposition, naming, control flow, every arbitrary choice | **QUARANTINE** — the whole file, header included |
| Q2 | `product/fixtures/VERIFICATION.md` | the model's method restated in prose: prefix construction, evaluation order, brute-force selection, freezing, roll-forward | **QUARANTINE** — it is an evidence log, not the contract; the author loses nothing they need |
| Q3 | any successor or variant reference model under `tools/` | same as Q1 | **QUARANTINE** by rule, not by filename (see §5, P0) |
| Q4 | this document | names the four divergence regions | **QUARANTINE** — the author gets the §10 brief instead |
| Q5 | the verifier's sealed probe set (§7) | the one signal with discriminating power | **QUARANTINE** — never committed before the gate |
| R1 | `product/trendline-specification.md` | the algorithm, prescriptively | **PERMEABLE** — it is the source of truth the engine must be derived from |
| R2 | `product/fixtures/golden/**` including every `causal_record` | the model's outputs and much of its intermediate state | **PERMEABLE by necessity** — this is the contract; the exit gate names these fields |
| R2b | `product/fixtures/real/**` — RM-01's `input.csv`, `annotation.json`, `README.md`, `expected-causal.json`, and `schema/real-causal.schema.json` | Half A: real prices and human-approved geometry. Half B: the model's as-of-time output | **PERMEABLE by necessity** — [SPR-D-03](../../product/human-decisions.md), condition-10 CONFIRMED. The Product Owner placed RM-01 in the Phase 2 exit gate (HD-22 requirement 3); an author who may not read the target cannot satisfy it. **No-credit rider travels with this row:** reproducing `expected-causal.json` earns conformance credit only — no independence credit (HD-15 condition 1) and no non-circularity credit (SPR-D-01 limit 3, which attaches non-circularity to Half A alone) |
| R3 | `product/fixtures/README.md`, `product/glossary.md`, `product/roadmap.md` | fixture-level detail, vocabulary, gate definitions | **PERMEABLE** — required context |
| R4 | `.github/workflows/governance-validation.yml` | that the model is invoked, not how | **PERMEABLE** — one command line, no logic |

*(`Q*` identifiers are quarantined surfaces and `R*` readable ones; `P*` and `D*`
below are preventive and detective **controls**, a separate numbering.)*

**The consequence of R2 is the load-bearing one for §6.** The vocabulary of the
problem — `B*`, `worst_gap`, `envelope_valid`, `t_form`, F1/F2/F3, `y_hat`,
`reselections`, `frozen_event_line`, the reason-code set — is published in the
specification and in every `expected.json`. An engine that uses those names has
demonstrated nothing except that it read its own contract. **Shared vocabulary is
not evidence of copying**, and any detective control that ignores this will produce
a stream of false positives, be overridden once, and then be ignored. The corpus
baseline in §6 (D0) exists precisely to remove it.

## 4. Threat model

Ordered by likelihood, not by severity. The likeliest failure is not deception.

| ID | Failure | Likelihood | Why it happens | Countered by |
|----|---------|-----------:|----------------|--------------|
| T1 | The authoring agent reads the model innocently, for context | **high** | it is the most relevant file in the repository for the task; every agent heuristic points at it; a `Grep` for a spec symbol surfaces it unprompted | P1, P2, P3 |
| T2 | A human pastes the model, or an excerpt, into the authoring session | **medium** | helpfulness under time pressure; "here is how the reference does it" | P4, P6, D1–D3, and finally attestation |
| T3 | The agent read it in a **prior** session and carries the content forward | **medium** | resumed sessions, `--continue`, memory files, a summary written by an earlier session into a scratch or planning file | P4 |
| T4 | The file is retrieved from **git history** in an otherwise-clean checkout | **medium** | `git show <sha>:tools/fixture-replay.mjs`, `git log -p`, `git cat-file`, `git grep`, `git archive`, `git worktree add` — all are read-only git and are currently **allowed for every role** by `bash-guard.mjs` | P1 (absence of the objects), P3 |
| T5 | The file is retrieved **over the network** | **medium** | it is public on GitHub: `WebFetch` of the blob URL, `gh api repos/.../contents/tools/...`, a raw.githubusercontent fetch, or a web search that surfaces it | P2, P3 |
| T6 | The author reads `VERIFICATION.md`'s worked derivations | **medium** | it is linked from the fixtures README and reads like documentation, but its "Method" section restates the model's own decomposition in prose | Q2 quarantine, P1, P2 |
| T7 | The author reads `causal_record` and mirrors its structure into the engine | **certain, and permitted** | it is the contract | not counterable; neutralised instead by D0's corpus baseline |
| T8 | Indirect read through a delegated subagent, a tool, or a skill that is not itself restricted | **medium** | `Task` to an unrestricted agent, a file-summarising tool, an MCP server, a shell one-liner that prints the file | P2 (deny applies to the delegating and delegated session), P3, P5 |
| T9 | Deliberate mechanical translation by an author that has the model | **low** | there is no incentive here beyond speed | D1–D4 partially; ultimately **not detectable with confidence** (§8) |
| T10 | **Quarantine decay** — the model is renamed, moved, split, or a second model is added, and the deny list still names the old path | **high over time** | this is how every denylist dies | P0 (content-hash manifest plus a default-deny rule over `tools/`), and the CI manifest check |
| T11 | Leakage **through review**: the verifier, who may read the model, feeds model-derived structure back to the author as review comments ("factor out a helper that does X") | **low, and invisible** | reviewers naturally compare against the reference they hold | P5 (rule stated in the reviewer's brief), and recorded in the attestation |
| T12 | The author attests to their own independence | **medium** | it is the path of least resistance while #21 blocks anyone else from posting | §8, GOV-011 rule 2 |

Note that T1, T3, T4, T5, T6 and T10 are all **honest** failures. A mechanism that
only defeats T9 addresses the least likely branch.

## 5. Preventive controls

Design rule: **prefer absence of the bytes over denial of the path.** A denylist
must enumerate every retrieval route (T4, T5, T8) and must be maintained forever
(T10); an empty directory needs neither.

| ID | Control | Mechanism (specification) | Failure mode | How it is proven in force |
|----|---------|---------------------------|--------------|---------------------------|
| **P0** | Quarantine manifest | A committed manifest listing quarantined paths **and their SHA-256 content hashes**, plus a **default-deny rule**: every executable file under `tools/` is quarantined unless explicitly allow-listed (today: `validate.mjs`, `check-evidence.mjs`). Renaming or adding a model therefore fails closed rather than silently escaping | manifest and tree drift apart | a CI check that every hashed path exists with the recorded hash, and that no unlisted, non-allow-listed executable exists under `tools/` |
| **P1** | **Clean-room checkout (primary control)** | The engine is authored in a **separate repository**, not a branch or worktree of this one: a snapshot of the base commit's tree with the quarantine set removed, initialised as a fresh git repo with **no remote and no inherited history**. The quarantined blobs are not merely hidden — they are **absent from the object store**, so no git command, no history walk and no reflog can produce them. Work returns as a patch series applied by an integrator who is **not the author**, preserving authorship metadata | the author works in the main checkout by mistake or convenience | the attestation records the clean-room root, its base SHA, and the output of the P0 manifest check run **inside** the clean room, which must report every quarantined path absent; the imported commits' trees are checked to contain no quarantined path |
| **P2** | Tool-permission deny | A clean-room settings profile whose `permissions.deny` covers the quarantine manifest for **every content-reading tool** — `Read`, `Grep`, `Glob`, `Edit`, `WebFetch`, `WebSearch` where applicable — and denies the network routes in T5 (repository blob and raw URLs, `gh api` contents endpoints). Deny must take precedence over any `allow` entry in any settings layer, including an untracked `settings.local.json` | the semantics of a deny rule differ from what was assumed; a settings layer loosens it | **a liveness probe, not a declaration**: before authoring begins, the author attempts a `Read` of a canary path in the manifest and of one network route, and records the refusal verbatim; the verifier repeats both probes independently. A control that has not been *observed* refusing is treated as absent |
| **P3** | Shell-layer deny | A `QUARANTINE` category in [`bash-guard.mjs`](../../.claude/hooks/bash-guard.mjs), blocked for the authoring role, covering: any command whose text references a manifest path; git object-retrieval commands (`show`, `cat-file`, `log -p`, `grep`, `archive`, `worktree add`, `restore`, `checkout <ref> -- <path>`) naming one; and `gh api`/`curl` against the repository's contents or raw endpoints. Extend `settings.json` so the hook also sees `Read`-family tools, and reject unknown roles into the most restrictive policy rather than `default` | it is a denylist over a shell, not a parser — `cat tools/fix*.mjs`, base64 indirection and `node -e` all evade it | the hook's existing test harness gains cases for the new category; the attestation cites the CI run of `bash-guard.test.mjs`. **This is defence in depth only** — if P1 holds, there is nothing on disk for these commands to find |
| **P4** | Session hygiene | The authoring session is **fresh**: not resumed or continued, no carried transcript, no memory or scratch file that quotes the model, and the clean-room profile is the session's only agent configuration. The session's file-read log is exported and attached to the attestation | prior-session memory is not observable from outside the session (T3) | the read log shows no quarantined path; the clean-room base SHA and session start time are recorded. This is **weak evidence** and is labelled as such — it constrains T3 rather than refuting it |
| **P5** | Separation of duties | Author is not verifier is not attester (GOV-011 rule 2). The **verifier may read the model; the author may not**. The reviewer's brief states T11 explicitly: review comments must be justified by the specification or the fixtures, never by the reference model, and any comparison finding is raised as a **finding**, not as a suggested implementation | a reviewer helpfully describes the model's structure in review | the attestation names the distinct roles and the commit range each touched, and asserts the T11 rule was observed |
| **P6** | Language separation | The engine is Python ([`mvp-architecture.md`](mvp-architecture.md) §3.1); the model is JavaScript. Stated as a **requirement** of the Phase-2 ticket rather than left as an accident | none; it is free | it is visible in the artifact. It does not stop translation, but it removes copy-paste as a cheap failure mode and makes any surviving verbatim overlap glaring |

**Instruction is not a control.** A prompt saying "do not read this file" satisfies
none of the rows above and is not counted as any part of the mechanism.

**What P1 costs.** The author loses the repository's git history, main-branch
tooling and the ability to run the full CI locally (CI invokes the model). For a
greenfield `engine/` these are small; the fixtures, the schema, the specification
and the glossary are all present in the clean room. The integration step is one
patch export and one patch application, performed by a different role. This is the
cheapest control here that **fails closed by construction**, and the only one that
does not rot: it requires no enumeration of retrieval routes and no maintenance
when the model is renamed.

## 6. Detective controls

These check property **A** against the committed artifact. Each is stated with what
it establishes and what it cannot.

**D0 — the corpus baseline (a prerequisite, not a check).** Build the set of
identifiers, symbols and phrases that appear in the **permeable** corpus (R1–R3 of
§3: specification, fixtures, fixture README, glossary). Every similarity finding is
computed **after** subtracting this set. Without it, D2 and D3 report the shared
vocabulary of the problem domain and are worthless. With it, a hit means the engine
contains something present in the model and **absent from everything the author was
entitled to read**.

| ID | Check | Automatable | Evidence class | False positives | False negatives |
|----|-------|-------------|----------------|-----------------|-----------------|
| **D1** | **Linkage** — no import, require, dynamic import, subprocess or shell invocation of a quarantined path anywhere in the engine tree or its tests; and no dependency edge of any kind from the engine to `tools/` | yes, trivially; belongs in CI | **decisive** — a violation is proof, and passing genuinely settles "import, copy, execute" for the executable senses of those words | essentially none | deliberate obfuscation of a string path; but the engine must survive code review, where an obfuscated path is itself the finding |
| **D2** | **Verbatim copy** — normalised token k-gram (shingle) overlap between engine sources and the model, minus D0. Report the longest common normalised token run and every shared shingle of length ≥ 12 tokens not derivable from the permeable corpus | yes, but must be run by a role permitted to read the model | **strong for same-language copying** | comments quoting the specification verbatim (spec text is in D0, so these subtract out) | cross-language: Python-vs-JavaScript token overlap is low even for a literal translation, so D2 is near-blind to the realistic threat |
| **D3** | **Model-private lexicon** — the verifier extracts every identifier and literal string in the model that is **absent** from the D0 corpus, publishes them as **SHA-256 hashes of the lowercased token**, and CI tests every engine identifier for membership. Any hit is a finding requiring written explanation | yes, in CI, **without disclosing model internals** — which is what makes it compatible with the quarantine | **strong** — a private name reaching the engine has no innocent route | a coincidental common name (mitigated by requiring an explanation, not by auto-failing); minimum token length to avoid noise | an adversary who renames everything; and the published hashes are dictionary-attackable, so this is a control against **honest** leakage (T1–T3, T8), not against T9. Stated openly rather than hidden |
| **D4** | **Structural comparison worksheet** — the verifier records, per axis, a written verdict: helper decomposition and boundaries, call-graph shape, branch ordering where the specification does not fix it, choice and naming of intermediates, error and message strings, constant derivation, and handling of cases the specification leaves open | evidence gathering, yes; the verdict, no | **weak** — see §8 | high, structurally: the specification is prescriptive and the problem is small, so **substantial structural similarity is the expected outcome of genuine independence** | anything a competent translator restructures |
| **D5** | **Divergence fingerprint** — see §7 | partially | **situational**; zero at the Phase-2 gate | see §7 | see §7 |
| **D6** | **Provenance forensics** — clean-room base SHA, the imported patch series, commit shape and cadence, whether the engine appeared incrementally or arrived complete, and the author's session read log | yes, cheap | **weak, corroborative** | a legitimately fast author; squashed history | trivially forgeable |

**Cost discipline (GOV-007).** D1 and D3 are two small CI checks and stay green
without attention. D2 and D4 are gate-time, verifier-run, once per phase. Nothing
here needs to be maintained between gates except the P0 manifest, which is checked
by CI and so cannot silently drift.

## 7. The divergence signal — assessment and judgement

The model's header discloses four deliberate divergences from the specification.
The proposition to test is: *an engine written from the specification should differ
from the model in exactly those four places; one that reproduces them did not come
from the specification.* The logic is sound. Its applicability is not.

| # | Disclosed divergence | Spec clause | Phase that owns the behaviour | Does the spec determine the correct behaviour? | Usable as a positive test? |
|---|----------------------|-------------|-------------------------------|-----------------------------------------------|----------------------------|
| 1 | Deferred retest hold not implemented; both legs required on the same bar (stricter than spec) | §16, `h_hold = 3` | **Phase 3** (retest is downstream of `ACTIVE → BROKEN_OUT`) | **yes** — `h_hold = 3` is stated with a worked example | **yes, at the Phase-3 gate** |
| 2 | Touch counting and `eps_touch` not implemented | §12 | a later confidence phase | yes | not at Phase 2 or Phase 3 |
| 3 | Volume and the `LOW_VOLUME` flag not implemented; `flags` are authored per fixture and not compared | §13.4 | **Phase 3** | yes | weakly, at Phase 3 — no fixture asserts flags today, so there is nothing to differ *on* until one does |
| 4 | OHLC coherence enforced as an input guard although the spec only assumes it | §1, §18 | **Phase 2** (the §18 input guards are named in the Phase-2 goal) | **no** — §1 states coherence as an assumption; §18 fixes only missing `high`/`close` and non-positive prices. Both rejecting and evaluating an incoherent bar conform | **no** |

**Judgement: at the Phase-2 gate this signal yields no positive test, and I do not
think it can be made to yield one.** The arrangement is exactly unhelpful. Three of
the four divergences lie in behaviour Phase 2 does not implement, so an independent
Phase-2 engine and the model agree there vacuously — both are silent. The one
divergence inside Phase-2 scope is the one the specification does not determine, so
a spec-authored engine may legitimately add the same guard (an input guard is an
ordinary defensive instinct, and this one is *more* likely than not to be
reinvented), and agreement proves nothing. Turning row 4 into a pass/fail test
would fail honest engines and pass dishonest ones, which is worse than having no
test. It should not be built.

**At the Phase-3 gate the signal becomes real, and only in one specific form.** For
rows 1 and 3 the specification *does* fix the answer, so the discriminating
construction is a **sealed spec-derived differential probe**:

- **Content.** Small OHLCV inputs that exercise §16's deferred hold (a return bar
  whose close does not hold, followed within `h_hold` by one that does) and §13.4's
  low-volume breakout, with expected outputs derived **from the specification, by
  the verifier, by hand** — the model cannot produce them, which is precisely what
  makes them clean.
- **Custody.** Authored **before** authoring begins, held by the verifier, **never
  committed** and never described in any author-readable artifact. Their existence
  is declared in the ticket; their content is not.
- **Verdict rule.** The engine matching the **specification** is the expected
  outcome and yields no independence conclusion. The engine matching the **model's**
  divergent behaviour is a **finding that requires explanation** — and, separately
  and independently, a specification-conformance failure.

Even so, be clear about what the probe does and does not achieve.

- Its power is **asymmetric and Bayesian, never proof**. Passing establishes nothing
  about provenance. Failing is **over-determined**: an engine can omit `h_hold`
  because it copied the model, or because it simply missed a clause. The probe
  cannot separate the two; it can only say "this artifact carries the model's
  specific spec-defect fingerprint", and the strength of that inference rises with
  the *number* of divergences matched and falls to near-nothing when only one is.
- It **catches carelessness, not intent**. The divergence list is disclosed in the
  model's own header, is quoted in governance, and is restated in this document
  (the note at the top of this file explains why that was unavoidable, and why this
  file is therefore quarantined as Q4). Anyone who has read the model knows which
  four places to get right. A deliberate translator will therefore pass the probe by
  construction — implementing `h_hold` correctly and thereby also conforming to the
  specification, which is the outcome we wanted anyway.
- It is a **conformance test wearing an independence badge**. That is not a defect,
  but it should be recorded honestly in the evidence log rather than counted twice.

**Recommendation:** build the sealed probes for Phase 3 (rows 1 and 3), specify them
now while the reasoning is fresh, and record explicitly in the Phase-2 evidence log
that **D5 contributes nothing at the Phase-2 gate**. Do not manufacture a Phase-2
divergence test out of row 4.

## 8. What no automated check can establish

Stated plainly, because a mechanism that overclaims is worse than one that is
modest and kept.

1. **Mechanical translation is not detectable with confidence.** A competent
   translation into another language, with renamed identifiers and resequenced
   helpers, is — by every measure available here — indistinguishable from an
   independent implementation. D1 catches linkage; D2 catches copying; D3 catches
   careless naming; none of them catch a careful translation.
2. **Structural similarity has low evidential value for *this* problem.** The
   specification prescribes the algorithm closely: the §21.2 evaluation order, the
   F1/F2/F3 formation gates, the brute-force hull over all later highs, six-figure
   comparison. The space of reasonable implementations is small. Two genuinely
   independent authors working from this specification would produce similar
   structures, and the more faithful each is, the more similar they get. Any
   detective control that treats similarity as suspicion **punishes fidelity**.
   Only *arbitrary* choices carry signal, and there are fewer of them here than the
   thousand-line size of the model suggests.
3. **B is unverifiable after the fact, permanently.** No artifact can prove what a
   finished session did or did not read. P4's read log is a record produced by the
   same session it purports to constrain.
4. **The permeable set is large and cannot shrink.** The fixtures publish the
   model's outputs and much of its intermediate state (T7). An engine derived
   entirely by fitting to `causal_record` — never reading a line of the model, never
   opening the specification — would pass every control in this document. It would
   also, by construction, pass the exit gate. **RM-01 is the check that bites there**,
   which is a further reason the Product Owner's 2026-07-26 ruling putting RM-01
   into the Phase-2 gate matters more than any control here.

**Therefore: independence cannot be fully enforced.** It can be made the default
outcome (P1), the honest failure modes can be made hard (P1–P3), the executable
senses of "import, copy, execute" can be settled decisively (D1), careless
transcription can be caught (D2, D3), and everything remaining is residual risk that
must be **accepted and documented** rather than papered over. §9 states it.

## 9. Attestation, and the #21 dependency

**Required artifact.** Before the Phase-2 exit gate is assessed, an **independence
attestation** exists, recorded by a party **other than the author** (GOV-011 rule 2,
GOV-006), containing at minimum:

| Field | Content |
|-------|---------|
| Base | Clean-room base commit SHA; quarantine manifest version and hash |
| Absence | Output of the P0 manifest check run inside the clean room, showing every quarantined path absent from the tree **and from the object store** |
| Liveness | Verbatim transcripts of the P2 deny probes, run by the author and re-run independently by the verifier |
| Authorship | Authoring role and configuration profile; the imported commit range; the integrator, who is not the author |
| A-checks | D1, D2, D3 results against the committed engine, with the corpus baseline version used; D4 worksheet with a written verdict per axis; D5 recorded as **not applicable at Phase 2**, with the reason |
| Duties | Named distinct author, verifier, reviewer and attester; a statement that the T11 review-leakage rule was observed |
| Residual | An explicit statement of what was **not** established (§8), so the attestation cannot later be read as proving more than it does |
| Sign-off | Named human sign-off |

**This is currently unsatisfiable, and I am not designing around it.**
`bash-guard.mjs`'s `ROLE_POLICY` blocks the `GH` category for `verification`,
`code-reviewer` and `project-auditor`, so **no reviewing role can post anything to
GitHub**; and review attribution collapses to a single account, so "recorded by
someone other than the author" is not externally checkable even when a comment does
appear. That is [Issue #21](https://github.com/tomerYannay/4UR4/issues/21), and it
is a hard dependency of this mechanism, not a nuisance.

What #20 needs from #21, stated as an interface so #21 can be scoped against it:

1. A **non-authoring role** must be able to create a **citable, immutable artifact**
   (a posted verdict or an equivalent) without acquiring general GitHub mutation
   rights.
2. That artifact must carry **attribution distinguishable from the author's**, so
   the author-is-not-attester property is verifiable from outside the repository.
3. The artifact must be **linkable from the ticket** and survive as evidence under
   GOV-006.

**Interim stopgap, and why it is one.** A committed attestation file, written by the
verifier into the ticket branch and signed off by a named human, satisfies
"immutable and citable" but not attribution — inside this repository every agent
commits under one identity, so the artifact's authorship rests on the human
sign-off alone. That may be acceptable **if the Product Owner rules it so**; it is
not for the Architect to decide, and it is escalated in §11.

## 10. Recommended mechanism

Minimum set that fails closed, ordered by the weight it carries.

1. **P1 clean-room repository** — the primary control. One creation step, one patch
   import. Removes T1, T3 (for the authoring session), T4, T5, T6 and T8 by removing
   the bytes rather than by forbidding routes, and does not decay when the model is
   renamed.
2. **P0 manifest with default-deny over `tools/`** — the thing that makes P1
   maintainable and stops T10.
3. **P2 deny rules plus mandatory liveness probes**, and **P3 bash-guard
   QUARANTINE** — defence in depth for the case where someone works in the main
   checkout anyway. Both are declared useless unless *observed* refusing.
4. **P5 separation of duties, P6 language separation, P4 session hygiene** — free or
   near-free.
5. **D1 and D3 in CI**; **D2 and D4 at the gate**, verifier-run.
6. **Sealed divergence probes for Phase 3 only** (§7), specified now, held by the
   verifier.
7. **Attestation** per §9, blocked on #21.

**Author-facing brief** (the text the Phase-2 ticket carries; contains no
model-derived content): *Author `engine/` from `product/trendline-specification.md`,
`product/fixtures/golden/**` and `product/fixtures/real/**` only. (The `real/**`
permission is SPR-D-03; this brief previously said `golden/**` **only**, which
excluded the very fixture HD-22 requirement 3 puts in the exit gate.) **Reproducing
`real/RM-01/expected-causal.json` earns CONFORMANCE CREDIT ONLY — no independence credit
(HD-15 condition 1) and no non-circularity credit (SPR-D-01 limit 3, which attaches
non-circularity to Half A alone). It is replay-generated, and it is a regression guard against
today's reference model, not independent verification.** SPR-D-03 clause 3 requires this rider
to travel with the classification, and this brief is precisely where an author would otherwise
form the opposite belief. `tools/fixture-replay.mjs`, any successor
model under `tools/`, `product/fixtures/VERIFICATION.md` and
`docs/architecture/phase2-independence-mechanism.md` are quarantined: you work in a
checkout that does not contain them, you must not retrieve them from git history,
the network or another agent, and if any of their content reaches you by any route —
including from a human — stop and report it. This is not a trust question; reporting
it costs nothing and concealing it voids the phase gate. The engine must not import,
copy, execute or mechanically translate any of them. If the specification and any
other artifact disagree, the specification governs and the disagreement is filed as a
defect report.*

**What it costs.** One clean-room setup and one patch import per authoring cycle; a
manifest and two small CI checks to build once; a verifier-run comparison at each
phase gate; the author's loss of git history and local full-CI during authoring.

**What it cannot catch.** Deliberate mechanical translation (§8.1); an engine fitted
to `causal_record` rather than derived from the specification (§8.4); content
carried in an author's memory from a prior session (§8.3); anything a human pastes
that the author does not report.

**Residual risk, stated plainly.** After all of the above, the residual claim the
Phase-2 gate can honestly make is: *the committed engine does not link to, execute,
or verbatim-copy the reference model; it was authored in an environment where the
model was absent; and no automated or human check performed can exclude the
possibility that it was mechanically translated by a party determined to do so and
to conceal it.* That risk is **irreducible** by any mechanism available in this
repository, and the correct disposition is to **accept and document it**, with the
non-circular RM-01 fixture and human review of the specification carrying the weight
that independence cannot. I recommend the Product Owner be asked to accept that
residual risk explicitly, as a recorded decision, rather than leaving it implied by
the closure of #20.

## 11. Acceptance criteria for closing Issue #20

All of these are satisfiable **before** Phase-2 implementation begins, which is the
Product Owner's stated precondition.

| AC | Criterion | Owner | Evidence |
|----|-----------|-------|----------|
| AC-1 | The mechanism is **defined**: this document is reviewed and approved through the normal chain | Architect, review chain | approved PR linked to #20 |
| AC-2 | The **quarantine manifest** exists, with content hashes and the default-deny rule over `tools/`, and a CI check enforces manifest-tree agreement | Implementation Engineer under an assigned ticket | green CI run |
| AC-3 | The **clean-room procedure** exists as a documented, repeatable operation with a named owner for creation and for patch import, and has been **exercised once on a throwaway branch**, producing a transcript showing every quarantined path absent from tree and object store | Orchestrator plus Release & Ops | recorded transcript |
| AC-4 | **P2 deny rules and P3 bash-guard QUARANTINE exist**, with the settings matcher extended to the read-family tools, unknown roles failing to the most restrictive policy, and new hook test cases green in CI | Implementation Engineer | green `bash-guard.test.mjs`, deny-probe transcript |
| AC-5 | **D1 and D3 exist as CI checks**, with the D0 corpus baseline defined and the hashed lexicon produced by a role permitted to read the model — not by the author | Verification plus Implementation Engineer | green CI run; the lexicon file, hashes only |
| AC-6 | **D2 and D4 are specified** as gate-time verifier procedures with a written-verdict template | Verification | committed procedure |
| AC-7 | The **sealed Phase-3 divergence probes** exist and are in verifier custody; their existence, not content, is declared on the Phase-3 ticket. The Phase-2 evidence log records that D5 is not applicable at Phase 2 | Verification | custody declaration on the ticket |
| AC-8 | The **attestation template** (§9 fields) exists, and **either** #21 is resolved so a non-authoring role can record a citable, attributed artifact, **or** the Product Owner has ruled the §9 stopgap acceptable | Orchestrator escalation; Product Owner | #21 closed, or a recorded ruling |
| AC-9 | The **Phase-2 ticket's Definition of Ready** carries both halves: E2-AUTHOR-A as a testable acceptance criterion on the artifact, and the §10 author-facing brief naming the quarantine set | Orchestrator, Product Steward | the ticket |
| AC-10 | The **residual risk statement** (§10) is recorded where decisions live, and the Product Owner has been asked to accept it explicitly | Product Steward, Product Owner | recorded decision |

**Escalations to the Orchestrator (GOV-007 — flagged, not absorbed).**

1. **Is the independence checker permitted tooling under GOV-015?** AC-2, AC-4 and
   AC-5 require executable files. They are governance and evidence tooling, of the
   same kind as `validate.mjs` and `check-evidence.mjs` — but HD-15 condition 4
   states its permission is **not a precedent**. A Product Owner confirmation is
   cheaper than an audit finding later.
2. **May #20 close while #21 is open?** AC-8 offers two routes; choosing between
   them is a Product Owner call, not an Architect one.
3. **Who owns clean-room creation and patch import?** It must not be the author
   (P5). Release & Ops is the natural holder, but its current policy blocks file
   mutation; this needs an explicit assignment.
4. **Custody of the sealed probes** across sessions and agents, given that the
   verifier is not a persistent identity.
5. **No new permanent agent is proposed.** The clean room is a *profile* applied to
   the existing Implementation Engineer, not an eleventh agent — the roster ceiling
   and GOV-011 rule 4 make that a human decision, and this design does not need one.

**Considered and rejected.**

- **Retiring the model from the repository after Phase 0** — would make the
  quarantine the default state. Rejected: CI's per-commit re-derivation of every
  fixture is the control Issue #16 exists to provide, and hosting the model outside
  the repository trades a solved problem for a fragile one.
- **Held-out fixtures as an independence test** — good evidence of *conformance*,
  none of *provenance*: a transcription of the model passes held-out fixtures
  exactly as an independent engine does, because their expectations are model-derived
  too.
- **Prompt-level instruction alone** — not a mechanism; explicitly excluded by the
  roadmap's E2-AUTHOR criterion 3.
- **Auto-failing CI on structural similarity** — punishes fidelity to a prescriptive
  specification (§8.2) and would be overridden the first time it fired, after which
  it would be ignored.

---

**Related:** [`build-freeze.md`](../../governance/build-freeze.md) (GOV-015, HD-15
conditions) · [`roadmap.md`](../../product/roadmap.md) (Phase 2, E2-AUTHOR) ·
[`human-decisions.md`](../../product/human-decisions.md) (HD-15) ·
[`separation-of-duties.md`](../../governance/separation-of-duties.md) (GOV-011) ·
[`definition-of-done.md`](../../governance/definition-of-done.md) (GOV-005/006) ·
[`temporary-specialists.md`](../../governance/temporary-specialists.md) (GOV-016) ·
[`mvp-architecture.md`](mvp-architecture.md) ·
[`fixtures/README.md`](../../product/fixtures/README.md) ·
[Issue #20](https://github.com/tomerYannay/4UR4/issues/20) ·
[Issue #21](https://github.com/tomerYannay/4UR4/issues/21) ·
[Issue #23](https://github.com/tomerYannay/4UR4/issues/23)
