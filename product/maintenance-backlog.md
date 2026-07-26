# 4UR4 — Maintenance Backlog

> **Purpose.** Non-blocking items, logged so work does not stop for them. Created under the
> Product Owner's **Product Execution Mode** directive (2026-07-26), which instructs that
> product work must not halt for wording, historical attribution, minor documentation
> inconsistencies, agent-count mismatches, link cleanup, table formatting, or non-blocking
> governance refinement.
>
> **Nothing here blocks a milestone.** An item is promoted out of this file — and *does*
> block — only if it changes product behaviour, invalidates fixture or real-market evidence,
> creates look-ahead bias, weakens security or branch safety, requires money/licensing/
> privacy/billing/legal approval, or prevents the current milestone from being tested or
> merged.
>
> **Owner:** Orchestrator maintains the list; each item names the agent that would fix it.

## Open

| # | Item | Site | Class | Owner |
|---|------|------|-------|-------|
| M-01 | Stale count: "the four limits" over a five-item list (`1, 1b, 2, 3, 4`) | `fixtures/README.md` §6b status line | wording | Product Steward |
| M-02 | Dated ledger row says "Four scope limits travel with it" and enumerates four, silently dropping limit 4 (no GOV-015 clearance). Row is a dated record, so it is marked rather than rewritten | `roadmap.md` SPR-D-01 change-log row | wording | Product Steward |
| M-03 | Paraphrase drift: cites the rule as *"never rewriting"* a record where the register says *"never **removing**"*. Different rules; the cited one is stronger than the source | `phase2-implementation-plan.md` §7.3 banner | wording | Architect |
| M-04 | HD-06 blocking-condition status disagrees: the register says C-2/C-3/C-5 are agent-proposed; the due-diligence pack marks C-2 **through C-5**. C-4's status is inconsistent | `human-decisions.md` vs `hd06-due-diligence.md` | doc inconsistency | Product Steward |
| M-05 | Six pre-existing broken same-file `#anchor` links, and `check-evidence.mjs` structurally skips `#`-prefixed links. The header limit is now stated honestly rather than overclaimed | `survivorship-bias-findings.md` ×5, `data-provider-findings.md` ×1 | link cleanup | tracked on [#22](https://github.com/tomerYannay/4UR4/issues/22) |
| M-06 | `- **1b.**` renders as a bullet interrupting an ordered list; some renderers restart numbering at "1." for the following item. Text is unambiguous and the numbering intent is stated inline | `fixtures/README.md`, `real/RM-01/README.md` | formatting | Product Steward |
| M-07 | [#16](https://github.com/tomerYannay/4UR4/issues/16) was closed without being re-scoped to what PR #18 actually delivered (HD-12/13/14, spec §21, D-TL-11/12, three fixtures, the reference model), so the ticket→PR traceability link is incomplete (GOV-007) | GitHub #16 | traceability | Orchestrator |
| M-08 | `check-evidence.mjs`'s golden census filter is `/^GX-\d\d$/`, so a stray `golden/RM-02` or `GX-024` directory is invisible to the census rather than reported as unexpected. The same applies to `/^RM-\d\d$/` in both tools — `RM-1`, `RM-001`, `rm-02` are ignored rather than reported | `check-evidence.mjs`, `fixture-replay.mjs` | tooling hardening | — |

## From the PR #30 review (RM-01 causal replay)

Three findings from that review were **not** logged here — they were fixed before merge,
because a gate you can silently disable is not a wording issue: the deletable
`input_binding` byte-binding, the `real/` walk that failed only when *every* directory
lacked an expectation, and a `TypeError` where a diff should have been reported.

*The third took two attempts, and the first attempt is worth recording. It made
`buildRealRecord` return an `unreachable` marker instead of throwing — but `compareReal`'s
guard tested `stop_index === null`, and the new shape carries a stop index, so execution
fell straight through — past the provenance checks, three `eq()` calls and both
`not_asserted` loops — and threw about sixteen lines later at `got.formation.t_form`. **The throw was relocated, not removed**,
while the comment and this paragraph both claimed it was fixed. Both reviewers caught it
independently. The guard now keys on `unreachable`.*

The rest:

| # | Item | Class | Why it can wait |
|---|------|-------|-----------------|
| M-09 | **The quarantine table does not classify `real/**`.** `phase2-independence-mechanism.md` classifies `golden/**` — *including every `causal_record`* — as **R2, permeable by necessity, "this is the contract"**, and says nothing about `real/**`. `expected-causal.json` is the same class (it *is* the B-clause conformance target), so quarantining it from the engine author is a **de facto quarantine item no decision record ratifies**, hard-coded into a schema description | ratification gap | Runs in the **restrictive** direction, so E2-AUTHOR is not weakened. **But it decides whether the Phase 2 engine author may read the B-clause target, so it must be ruled before the clean-room cut — i.e. before the Phase 2 ticket can meet its Definition of Ready (E2-AUTHOR / #20 AC-9).** *(A ruling was made in the PR #30 strategic review — `real/**` as R2 permeable with a no-credit rider, proposed as **SPR-D-02** — but the Project Auditor returned **NOT CONFIRMED** under HD-21 condition 10, because the decision was never written to `human-decisions.md` while this row cited it forward. **SPR-D-02 therefore does not stand.** **RESOLVED by [SPR-D-03](human-decisions.md), condition-10 CONFIRMED by the Project Auditor:** `real/**` is classified **R2b PERMEABLE by necessity**, with a mandatory no-credit rider (conformance credit only — no independence credit per HD-15 condition 1, no non-circularity credit per SPR-D-01 limit 3). SPR-D-03 is not a re-run of SPR-D-02: it leads with the argument below, which the audit established *after* SPR-D-02 was declined, and SPR-D-02 failed on a **procedural** ground rather than on the merits. Propagated to the §3 table (row R2b), the §10 author brief, the schema description (superseded, not deleted) and the `bash-guard.mjs` comment. The audit did establish the strongest argument for it, which the ruling did not lead with: the roadmap's **E2-AUTHOR-B is Product-Owner-approved text** naming only `tools/fixture-replay.mjs` and successors under `tools/`, so the *"nor this file"* clause widened a PO-approved criterion without a ruling — removing it would restore the PO's text rather than reduce the PO's control.)* |
| M-13 | `params` is fixture-supplied and unpinned — `eps = 0.05` still passes, because RM-01's geometry is ε-insensitive in that range. A silent retune away from the ratified D-TL-12 set is caught by nothing | tooling hardening | Not live: a retune that *does* move geometry breaks the comparison. `const`-pinning the ratified values would close it |
| M-14 | The `robustness` block is **recorded but never compared** — `compareReal` runs its own sweep and ignores it. Hand-recorded numbers inside an artifact whose purpose is mechanical verification; its `eps_break = 0.05` row also sits outside the checked 0.5×–2× range | evidence hygiene | The sweep that gates HD-13 robustness *is* mechanical; only the recorded copy is decorative |
| M-15 | A real fixture with **no breakout cannot be expressed** — `compareReal` hard-fails it. Correct and deliberate for RM-01 (it is what makes the check non-vacuous), but "stop index" has no meaning for a series that never breaks out | design limit | Blocks nothing until a second real fixture arrives; needs a decision then |
| M-18 | `--real` is undocumented in the USAGE block, and a bare `node tools/fixture-replay.mjs` prints "23/23" without touching RM-01 | docs | CI runs `--all`, so the gate is closed; only the bare run's summary is incomplete |
| M-19 | `line_at_stop.stop_index` is asserted explicitly and again inside the `Object.keys` loop — the identical diff prints twice on failure | cosmetic | — |
| M-20 | That loop iterates the *derived* keys, so a key present only in the expectation is invisible to the harness | none — caught by the schema's `additionalProperties: false` | Worth a one-line comment saying so |

## From the PR #32 review (E2-AUTHOR tool-deny)

The tool-deny took four revisions. Three of its findings were fixed before merge because
they were ordinary-use bypasses or a functional regression; the rest are **disclosed
limitations**, recorded here because the Product Owner ruled the hook is
**defence-in-depth, not a security proof** ([#31](https://github.com/tomerYannay/4UR4/issues/31)),
and **E2-AUTHOR-A is the authoritative independence criterion**.

| # | Item | Class | Why it can wait |
|---|------|-------|-----------------|
| M-22 | **The parity check does not cover TEMPORARY specialists** (GOV-016). It filters `status === 'permanent'`. There are none today, but an unregistered temporary agent would be silently quarantined by AC-4 — the exact failure the check exists to prevent, one category over | tooling gap | Stated in the code rather than implied. No temporary specialists exist; promote the moment one is created |
| M-23 | **Repo-root recursive content search** — `grep -rn <pattern> .` or `Grep {pattern, output_mode:"content"}` with no `path` — returns matching *lines* from the reference model | disclosed residual | Incidental, not targeted. Closing it means blocking repo-root search, an over-block that breaks the ticket. P1 clean-room checkout removes the blobs entirely and is the primary control |
| M-24 | The bare word `tools` in an engineer Bash command blocks, so `node engine/tools.mjs` and a commit message containing "tools" are denied | over-block, bounded | Friction the author can reword around; blocks no file the ticket requires |
| M-25 | `Object.values()` path scanning treats `content`/`new_string` as candidate paths, so writing prose containing `tools/` or a quarantined filename blocks | over-block, bounded | Code Review ruled it does not break the ticket: the attestation is recorded by a party other than the author (GOV-011 rule 2), so the engineer never needs to type the model's path |
| M-27 | The `settings.json` `$comment` enumerates only `fixture-replay.mjs` as denied, omitting `VERIFICATION.md` and the mechanism doc. Incomplete rather than false — it correctly states the Bash layer is not airtight and that E2-AUTHOR-A governs. The PR body likewise never mentions the SPR registration or the parity check | wording, understates | Understating the diff is the harmless direction |
| M-26 | Pre-existing, outside this diff: `fileMutation`'s `/>>?/` fires on `=>`, blocking read-only roles from `node -e` with arrow functions | pre-existing | Tripped several review harnesses this session; unrelated to the quarantine |

## Promoted out (was here, turned out to block)

*None yet.*

## Closed

| # | Item | Closed by |
|---|------|-----------|
| M-00 | RM-01 had **no mechanical guard of any kind** — `fixture-replay.mjs` read only `golden/` and `check-evidence.mjs` only schema-validated the annotation. This was **not** a maintenance item; it invalidated the real-market layer's claim to be checked at all, and is logged here only to record that it was closed | `expected-causal.json` + `real-causal.schema.json` + the `real/`-reading tool extension (branch `feat/rm01-causal-replay`) |
