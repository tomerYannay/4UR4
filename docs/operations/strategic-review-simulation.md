# Strategic Product Reviewer — live-trial simulation (Phase 0 golden fixtures)

> **What this is:** the required live-trial (requirement 14) for the new
> [`strategic-product-reviewer`](../../.claude/agents/strategic-product-reviewer.md) agent.
> Because Claude Code discovers `.claude/agents/` **at session start**, the agent itself
> cannot be dispatched in the session that created it (same constraint as
> [`claude-code-validation.md`](../claude-code-validation.md)). This review was therefore
> produced by a **general-purpose agent applying the new agent's framework verbatim**
> (because the new **permanent** agent only becomes discoverable after a **new Claude Code
> session**) against the **merged** Phase 0 golden-fixture work at Phase-0 main commit
> `3c172e033770a08d9d856c5a3271dffab12bf767` (PR #9). It is **behavioral validation of the
> framework, NOT a live-agent discovery test**; a fresh-session `/agents` discovery run
> remains a separate check (see [`claude-code-validation.md`](../claude-code-validation.md) §A).
>
> **Recorded facts for this simulation:** executed via general-purpose agent (agent not yet
> session-discoverable when run) · reviewed Phase-0 main SHA `3c172e0…` · evidence inspected =
> the fixture/spec/decision files listed below (via `git show <sha>:<path>`) · **verdict =
> `STRATEGIC_HUMAN_DECISION_REQUIRED`** · the review is **head-specific** (bound to `3c172e0`;
> a new commit invalidates it) · **human-gated decision identified = HD-06** (data-provider
> selection + spend) · **next step = review PR #12** (Phase-1 research), freeze kept ON.

## What the trial demonstrates (requirement 14)
- **Evidence-first inspection** — it read the actual files at the reviewed SHA (`git show <sha>:<path>`), not summaries, and tied each claim to a file.
- **Head-specific approval** — it bound the assessment to one SHA and stated a new commit invalidates it.
- **PO-approval vs agent-approval** — it stated explicitly that a `STRATEGIC_*` verdict is **not** Product Owner approval and **not** a merge.
- **Human-gated decision identified** — it surfaced **HD-06** (provider selection/spend) with the full decision packet, and a second PO-only item (RM-01 result-approval reconciliation).
- **One concise next step** — a single smallest justified step (review PR #12 research), no phase-jumping, freeze kept ON.

## Real findings surfaced (accurate — verified against the repo)
The trial independently caught genuine **pre-existing** Phase 0 traceability defects (they live on `main`, **not** introduced by this PR, and are **out of scope** for this agent-creation PR — the framework forbids scope expansion):
1. **RM-01 result-approval record is inconsistent:** `product/fixtures/README.md` §6a says approval `pending` while `product/fixtures/real/RM-01/annotation.json` says `approved`; PR #9 carries **no** GitHub PO-approval comment/review.
2. **`product/fixtures/VERIFICATION.md`** reads "18 / 18 fixtures verified" in the Result header but "19 / 19" in the SC-2 regression section (GX-19 added).

**Recommended follow-up (separate PR, not this one):** the **Product Steward** reconciles the RM-01 approval record to a single value across the affected files and records the Product Owner's RM-01 approval as a **citable GitHub artifact**; and corrects the VERIFICATION.md count to 19/19. An agent must not silently choose which status is true (precedence: latest PO decision → `human-decisions.md` → …).

---

## Evidence report (pre-existing Phase 0 inconsistency)

### 1. Exact inconsistency
**(A) RM-01 Product-Owner result-approval recorded inconsistently.** The authoritative value is **`approved`** (the PO approved RM-01 on 2026-07-25), but the top-level fixtures index was not updated and still says `pending`.
- `product/fixtures/real/RM-01/annotation.json:205` → `"product_owner_approval": "approved"` ✅ authoritative
- `product/fixtures/real/RM-01/README.md:10` → "Owner approval: `approved` (2026-07-25)" ✅
- `product/fixtures/VERIFICATION.md` (RM-01 section) → "Product Owner approval: `approved` (2026-07-25)" ✅
- `product/fixtures/README.md:155` (§6a index), `:166`, `:184` → approval **`pending`** ❌ **stale outlier**
- **Expected:** one consistent value across all records for a human-gated approval, with a citable artifact.
- **Actual:** three RM-01-local records say `approved`; the fixtures index says `pending`; and **PR #9 carries no GitHub PO-approval comment/review** (`gh pr view 9` → `comments: 0, reviews: 0`), so precedence-1 evidence (a PO GitHub artifact) is absent.

**(B) Fixture-count mismatch in the evidence log.** `product/fixtures/VERIFICATION.md:27` reads "**18 / 18** fixtures verified" while `:106` (SC-2 regression) reads "**19 / 19**" after GX-19 was added. Expected: a single current count (**19/19**).

**(C) Annotation internal traceability (cosmetic).** `product/fixtures/real/RM-01/annotation.json:213` marks `spec_contradiction_report.status: "resolved-with-po"` and SC-2 `resolution: "resolved"`, yet `:210` `unresolved_metadata` still lists "SC-2 pivot-eligibility question (open)"; and SC-2's `verdict` (`:230`) reuses SC-1's enum value `"MATCH"`.

### 2. Classification
- (A) RM-01 approval record → **Governance / process** (a human-gated approval record).
- (B) count + (C) annotation internal → **Implementation / test-evidence** (traceability of the evidence docs).
- **None** is a *Product-definition* or *Technical-design* defect — no rule, formula, or geometry is in conflict.

### 3. Severity
- (A) RM-01 approval record → **Major** on the governance/traceability axis (a human-gated approval must be unambiguous and citable); **functional impact is documentation-only** (not Blocking — see §5).
- (B) count → **Minor**. (C) annotation internal → **Minor**.

### 4. Why it is genuinely pre-existing
- It exists on **merged `main`**: shown above via `git show main:<path>` (README lines 155/166/184 = `pending`; annotation:205 = `approved`; VERIFICATION 18/18 vs 19/19).
- It was **introduced by commit `3c172e0`** ("Phase 0 research: golden-fixture dataset … (#9)"), the PR #9 squash-merge — **before** this agent-creation PR existed.
- This PR (`governance/add-strategic-product-reviewer`) touches **no** `product/fixtures/` files: `git diff --name-only main...HEAD` lists only the agent, registry/validator, `project-state.md`, wiring, and this simulation doc. The inconsistency is therefore **not introduced here**.

### 5. Impact
- Changes the selected canonical line? **No.**
- Changes breakout/retest classification? **No.**
- Invalidates any golden fixture? **No** — all 19 verify to 6 sig figs; anchors unchanged; GX-19 is the sole non-pivot anchor.
- Changes an approved Product Owner decision? **No** — the PO's RM-01 approval and HD-11 stand; the correct value is `approved`; only a stale index line disagrees.
- Blocks future implementation? **No** — documentation only; Phase 1+ is freeze-blocked regardless (GOV-015).

### 6. Recommended resolution
- **Smallest safe correction:** update `product/fixtures/README.md` lines 155/166/184 `pending` → `approved` to match the authoritative RM-01 records; fix `VERIFICATION.md:27` "18/18" → "19/19"; remove the stale "SC-2 (open)" entry from `annotation.json:210` `unresolved_metadata` (optionally give SC-2 its own verdict token).
- **Files that would change:** `product/fixtures/README.md`, `product/fixtures/VERIFICATION.md`, `product/fixtures/real/RM-01/annotation.json`.
- **Product Owner decision required?** **No** for the correction (the approval already happened and is the authoritative value). *Optionally* the PO/Steward records a **citable GitHub PO-approval artifact** for RM-01 (a comment on PR #9 or the coordination queue) to close the precedence-1 gap — a traceability nicety, not a new decision.
- **Reopen #2 / #3?** Not recommended — both are evidence-backed **Done** (reopening churns closed tickets against GOV-005/006). Prefer a **new small Product-Steward doc-reconciliation follow-up** (its own issue or a fix-up PR). If the team prefers reopening, `#3` (owns the breakout/RM-01-adjacent fixtures) is the closer match; `#2` (pure geometry) is unaffected by the approval line.
- **Owner:** Product Steward (content), routed by the Orchestrator; re-reviewed by the Strategic Product Reviewer on the new head.

---

## Verbatim simulated review

```
STRATEGIC_HUMAN_DECISION_REQUIRED

Reviewed head SHA: 3c172e033770a08d9d856c5a3271dffab12bf767 (squash-merge of PR #9 on main,
merged 2026-07-25T12:32:01Z; gh confirms mergeCommit.oid == this SHA). This review is bound
to this exact head.

Objective reviewed: Phase 0 golden-fixture correctness contract — 19 synthetic fixtures
(GX-01…GX-19), one real-market fixture (RM-01), fixture/annotation JSON schemas, the RM-01
real-market plan, plus the HD-11 human-decision and trendline-spec revisions that make the
pivot prefilter non-authoritative. Data/docs only, under GOV-015.

Files inspected (at the reviewed SHA, via git show <sha>:<path>):
- product/fixtures/README.md, product/fixtures/VERIFICATION.md
- product/fixtures/golden/GX-19/expected.json (SC-2 proof) and the catalog/legend for
  GX-01/02/03/16/11/05/04/17/06/07/08/10/18
- product/fixtures/real/RM-01/README.md, .../annotation.json
- product/fixtures/real-market-plan.md (referenced), schema paths under product/fixtures/schema/
- product/trendline-specification.md §5 (pivot NON-AUTHORITATIVE), §6/§8 (all-highs
  upper-log-hull), D-TL-03/D-TL-05, HD-03/HD-11 language
- product/human-decisions.md (HD-01…HD-11 register + 2026-07-24 and 2026-07-25 decision logs)
- git show --stat 3c172e0 (50 files; confirmed no product-code directory — only .md/.json/.csv/.png)
- Attempted product/project-state.md — absent at this SHA and on main (present only on a later
  working branch).

Issues inspected: #4 (Phase 1 data-provider research, ready-eligible, human-gated), #5
(survivorship/delisted research, ready-eligible), #6/#7 (blocked: freeze), #10 (Agent
Coordination Queue). PR inspected: #12 (DRAFT, Refs #4/#5, head a62a1a61…, selects no
provider). PR #9: MERGED — gh pr view 9 shows reviews: [], comments: [].

CI and validation status: VERIFICATION.md records an independent re-derivation (author =
Architect, verifier = primary session; GOV-011 separation of duties): geometry reproduces to
6 significant figures; two exp() display digits (GX-06, GX-09) were corrected to the
independently computed values; SC-2 all-highs regression confirms 16/16 existing anchors are
already the all-highs hull vertex (no anchor moved) and GX-19 is the sole non-k=3-pivot
canonical anchor. I could not run CI (read-only, no Bash for git-blame of checks); I verified
arithmetic and claims against the files, not against a summary.

Governance status: GOV-015 build-freeze remains ON; the merged content authorizes no build
(data/docs only, banners present). HD-06 (provider selection + recurring spend) remains
PENDING/human-gated. HD-07 approves the need only, purchase human-gated. HD-11 is recorded
APPROVED (2026-07-25) resolving SC-2, refining HD-02.

Findings
- Blocking: none.
- Major — D. Governance/process (contradictory human-gated approval record): The RM-01 result
  approval status is inconsistent across merged files. product/fixtures/README.md §6a states
  RM-01 "Product Owner approval pending… (a separate review)"; whereas real/RM-01/README.md,
  annotation.json ("product_owner_approval": "approved"), and VERIFICATION.md state "approved
  2026-07-25." There is no GitHub PO approval comment or review on PR #9 (reviews: [],
  comments: []) — the framework expects the "latest Product Owner approval comment" as
  precedence-1 evidence, and it is absent. A human-gated acceptance recorded three ways as
  "approved" and once as "pending", with no independent GitHub artifact, cannot be certified.
  (Note: the HD-11/SC-2 rule decision is separately and consistently logged as APPROVED in
  human-decisions.md; this finding is about the RM-01 result acceptance, not the pivot rule.)
- Minor — D. traceability: product/project-state.md (required by this agent's §17/§20/§21) does
  not exist at the reviewed head or on main; it cannot be validated here.
- Minor — traceability: VERIFICATION.md "Result" header still reads "18 / 18 fixtures verified"
  while the catalog and the SC-2 regression section report 19/19 (GX-19 added). Stale count.
- Minor — traceability: annotation.json internal inconsistency — spec_contradiction_report
  marks SC-2 resolved, yet unresolved_metadata still lists "SC-2 pivot-eligibility question
  (open)"; and SC-2's verdict reuses the SC-1 enum value "MATCH".

Required changes (to clear the Major before Product Owner eligibility): Reconcile the RM-01
result-approval status to a single value across fixtures/README.md §6a, real/RM-01/README.md,
annotation.json, and VERIFICATION.md, and cite the authoritative Product Owner artifact (a
GitHub approval on PR #9 or the coordination queue) — an agent must not choose which status is
true. Then re-review on the new head.

Optional recommendations: update the VERIFICATION.md "Result" count to 19/19; remove the stale
"SC-2 open" line from annotation.json.unresolved_metadata; give SC-2 its own verdict vocabulary
distinct from SC-1's enum.

Human decisions required
(1) HD-06 — market-data provider selection + recurring spend (PENDING; gates Phase 1 and all
downstream).
- Exact decision: which market-data provider(s) to license for historical + EOD OHLCV and
  splits/corporate actions, and approval of the recurring cost.
- Recommended option: no agent recommendation — human-gated. Agents produce only the R1–R8
  evidence/comparison matrix (PR #12, no winner column); the Product Owner selects and
  authorizes spend.
- Alternatives: bundle (single vendor for OHLCV + constituents + delisted) vs. best-of-breed
  across vendors — a choice the matrix informs, not the agent.
- Evidence: human-decisions.md HD-06; issue #4; PR #12 (market-data-provider-comparison.md,
  ~90/108 cells evidence-backed, 11 "unverified — confirm", IEX N/A) — currently DRAFT, unreviewed.
- Cost: recurring subscription (provider/tier dependent; not yet quoted as a committed figure)
  — a commercial commitment only a human may make.
- Risk: selecting on incomplete/undated pricing, or licensing terms that forbid redistribution
  (ties to HD-07/HD-09).
- Cost of delaying: blocks Phase 1 data foundation and everything downstream; low near-term
  cost because Phase 0 is data/docs only and needs no live feed.
- Safe fallback: continue research-only; MVP cadence default EOD/daily; commit nothing until
  the Product Owner decides.
(2) RM-01 result acceptance — confirm the true approval status. Because files disagree and no
GitHub PO artifact exists, only the Product Owner can state whether the RM-01 result is approved
or pending, and that ruling must be recorded once, in one place, with a citable GitHub artifact.

Next governed step (single smallest justified step): With the freeze ON, the ready,
freeze-permitted step is the Phase 1 market-data research review — PR #12 against issues #4 and
#5 (research-only; selects no provider, commits no spend, feeds HD-06/HD-07). Why it's next: it
is the only ready-eligible freeze-permitted work with an open PR and produces exactly the
evidence the pending HD-06 human decision needs. Evidence it's ready: issues #4/#5 labeled
ready-eligible; PR #12 exists with an evidence matrix. What's blocked: Phase 1 implementation
(#6) and Phase 2 (#7) stay blocked: freeze; provider selection stays with the human. Freeze
status: GOV-015 remains ON. Owner of next action: Orchestrator marks PR #12 ready and hands it
to this strategic-product-reviewer for review; the RM-01 approval-status reconciliation and
HD-06 stay with the Product Owner. Completion criterion: PR #12 review returns a head-specific
verdict, R1–R5/R7/R8 evidence is complete with dated sources, and no provider is selected. Do
not lift the freeze, do not start Phase 1/2 implementation, do not promote any provider.

Another review required? Yes — a new review is required on any new head (the RM-01
approval-status fix, and PR #12 when it leaves DRAFT).

Eligible for Product Owner approval? Not yet — the Major RM-01 approval-record contradiction
must be reconciled first, and HD-06 is a Product-Owner-only decision. A STRATEGIC_* verdict is
not Product Owner approval and not a merge.

May GOV-015 remain ON? Yes — it must remain ON; nothing in the reviewed work justifies lifting
it, and no build is authorized.

Head-specific-approval statement: This assessment is bound solely to
3c172e033770a08d9d856c5a3271dffab12bf767. Any new commit invalidates it and requires a fresh
review; no approval may be inferred from silence.
```
