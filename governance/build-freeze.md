---
id: GOV-015
title: Build-Freeze (no product implementation yet)
applies_to: [all]
class_scope: all
enforced_by: [human, validator]
---

# GOV-015 — Build-Freeze

## Intent
This repository is bootstrapping the **operating system**, not the product. Until a
human approves the system, **no product functionality may be implemented**
(requirements 13 & 14).

## Rule
1. The build-freeze is **ON** until a human explicitly lifts it via
   [GOV-013](approval-gate.md).
2. While frozen, **no product code** may be written or merged. Permitted work is
   limited to: this operating system, governance, workflows, templates, and
   **context-only** research/design. *(One ruled exception — see the HD-15 scope
   ruling below, which permits a specific Phase-0 evidence-tooling file.)*
3. The **Implementation Engineer is inactive** while frozen; the Architect may
   *design* but not build.
4. Lifting the freeze is **per-scope**, tied to a specific approved, Ready ticket —
   never a blanket "autonomy on."
5. The freeze state is machine-readable so the [validator](../tools/validate.mjs)
   can assert it and gate CI.

## Scope ruling — Phase-0 evidence tooling (HD-15, Product Owner, 2026-07-25)

> **Ruled by the Product Owner on 2026-07-25**
> ([artifact](https://github.com/tomerYannay/4UR4/issues/16#issuecomment-5080542012),
> against head `2651cd0efffb7d48ec6e9929aed8fa3c4f22afcd`): *"permit the reference model
> under GOV-015."* Recorded as **HD-15** in
> [`human-decisions.md`](../product/human-decisions.md).

**`tools/fixture-replay.mjs` — a causal reference model that re-derives every golden
fixture from `input.csv` and the specification — is PERMITTED under this freeze as
Phase-0 evidence tooling.**

Why the question arose, and why it needed a human: rule 2's permitted list is closed, and
an executing implementation of the detection algorithm is not obviously "context-only
research/design"; rule 3 says the Architect may *design* but not *build*. The validator's
freeze check is **directory-name-based** (`PRODUCT_CODE_DIRS`) and never reads file
contents, so a file passing it is **not** thereby cleared — that is a gap in enforcement,
not a ruling. Against that: the alternative is hand arithmetic, which drifted repeatedly
and shipped a defective fixture, and a correctness contract nobody can mechanically
re-derive is the larger hazard.

**Conditions attached to the permission.** Condition 4 is the ruling's own scope, stated in
the artifact. Conditions 1–3 originated as the **review chain's recommended terms**, adopted
as the detail of the permission rather than separately quoted Product Owner words; the
artifact recorded that distinction and invited them to be struck if a bare permission was
intended. **They were not struck.** On **2026-07-26** the Product Owner ruled
([artifact](https://github.com/tomerYannay/4UR4/issues/23)): *"Retain HD-15 conditions 1–3.
The fixture reference model remains verification-only and is not product implementation."*
All four conditions are now directly ruled, and condition 2 was **sharpened** — see below.

1. It confers **no Phase-2 credit**. Phase 2 is not partly done because this exists.
2. The Phase-2 implementation MUST be **independently authored**, and **must not import,
   copy, execute or mechanically translate this model** (Product Owner, 2026-07-26), so that
   "exact reproduction" tests conformance rather than transcription. The original wording —
   *authored by an agent that has not read this model* — is retained as the **preventive
   control**, but the ruled criterion is now a **property of the artifact** rather than a
   claim about a session's history, and is therefore checkable after the fact.
   **[Issue #20](https://github.com/tomerYannay/4UR4/issues/20) must define an enforceable
   independence mechanism before Phase 2 implementation begins.**
3. The **specification is authoritative**. Any divergence between the two is a spec-defect
   report or a model bug — never a silent model behaviour.
4. This ruling covers **this file, for this purpose**. It is not a precedent for committing
   executable product functionality under the freeze, and it is **not a freeze lift**:
   `build_freeze` stays `ON` and no product code is authorized.

## Scoped lift — Phase 2 `engine/` only (Product Owner, 2026-07-26, [#31](https://github.com/tomerYannay/4UR4/issues/31))

**The freeze remains ON.** One scope is lifted, and it is enumerated rather than described,
because a scope stated only in prose is not a scope — it is an intention.

**Authorized inside `engine/`:** the deterministic trendline-engine implementation · fixture
and RM-01 conformance tests · engine-local test infrastructure · minimal shared types
strictly required by the engine.

**NOT authorized, and still frozen:** provider integration · live market-data ingestion ·
API, database, scanner, worker, dashboard, alerts or SaaS work · spend, licensing, privacy,
billing or external deployment.

**How far the machine check actually reaches, stated precisely.** `tools/validate.mjs` guards
a **named list** of product-code directories, not a heuristic.
<!-- GUARDED-DIRS-LIST — tools/validate.mjs parses the backticked names between these
     markers and fails the build if they disagree with PRODUCT_CODE_DIRS. Do not remove. -->
`src`, `lib`, `app`, `server`, `client`, `packages`, `engine`, `api`, `services`, `scanner`,
`worker`, `dashboard`, `web`, `backend`, `frontend`, `db`, `alerts`, `billing`, `providers`.
<!-- /GUARDED-DIRS-LIST -->
A directory outside that list is
**unguarded no matter what this section says** — the prose forbids it, the validator does not.

**Still unguarded, named here so the gap is not rediscovered as a surprise:** any directory
this list does not name. Before the 2026-07-26 lift the list held **six** names and did not
include `engine/` — the directory the lift was about — so the scope would have been prose
over an already-open door. **Add the name here and to `PRODUCT_CODE_DIRS` together, or the
ban is decorative.**

**Binding requirements on the engine**, quoted from the ruling:
1. **independently authored** from the fixture reference model;
2. **must not import, execute or mechanically translate** that model;
3. passes **all 23 golden fixtures and RM-01 causal replay**;
4. preserves **HD-11 through HD-20**;
5. **deterministic and free of look-ahead bias**.

Requirements 1 and 2 are governed by **E2-AUTHOR** ([#20](https://github.com/tomerYannay/4UR4/issues/20)):
**E2-AUTHOR-A** — the committed `engine/` must not import, copy, execute or mechanically
translate `tools/fixture-replay.mjs` or any successor model under `tools/` — is the property
assessed at the gate, and it governs where it and the read-restriction diverge. **Agreement
with the reference model earns no credit** (HD-15 condition 1): the engine is proven against
the **fixtures**, never against the model.

**Fixture immutability — adopted as detail of the permission, not a sixth ruled requirement.**
**No fixture, `expected.json`, `annotation.json` or parameter may be edited to make the engine
pass.** A disagreement between the engine and a committed fixture is **escalated, never
reconciled**. This was proposed by the requesting session rather than ruled, on the same
footing as HD-15 conditions 1–3 — see [`../product/human-decisions.md`](../product/human-decisions.md)
HD-22 — and it may be struck by the Product Owner. It is the one control that cannot be
recovered after the fact: a fixture edited to accommodate an engine looks identical to a
fixture that was always right.

**This lift does not touch HD-06.** No provider is selected and no spend is authorized.

## Scoped lift — Phase 3 `engine/` only (Product Owner, 2026-07-28, [#39](https://github.com/tomerYannay/4UR4/issues/39) §3)

**The freeze remains ON.** A **second** scope is lifted, alongside — not replacing — the
Phase-2 lift above. Enumerated for the same reason: a scope stated only in prose is an
intention, not a scope.

**Authorized inside `engine/`, quoting §3's grant:** the **`ACTIVE → BROKEN_OUT` transition**
· **line freezing** (`Λ^F`, §21.5) · **retest** (§16) · **failed breakout** (§15) ·
**expiry and recompute** (§17). Read with the roadmap's behavioural **Phase 2 / Phase 3
boundary rule**: Phase 3 owns the transition itself and everything downstream of it on the
frozen line.

**NOT authorized, and still frozen, quoting §3's list:** provider integration · live
ingestion · `api` · `db` · `scanner` · `worker` · `dashboard` · `alerts` · `billing` ·
`providers` · SaaS surfaces · spend · licensing · privacy/billing · external deployment.

**E2-AUTHOR continues to bind the whole engine.** The Phase-2 conditions are not spent by the
phase changing: **E2-AUTHOR-A** — the committed `engine/`, *including every module a Phase-3
ticket adds*, must not import, copy, execute or mechanically translate
`tools/fixture-replay.mjs` or any successor model under `tools/` — is the property assessed at
the gate, and **agreement with the reference model earns no credit** (HD-15 condition 1). The
**fixture-immutability** condition carries over unchanged: no fixture, `expected.json`,
`annotation.json` or parameter may be edited to make the engine pass, and a disagreement is
**escalated, never reconciled**.

**Rule 4 is NOT satisfied by this lift, and that is stated here rather than left to be
discovered.** §3 attaches the lift to **ticket (g)** in
[`../product/planning/ticket-set.md`](../product/planning/ticket-set.md) and asserts that this
*"satisfi[es] GOV-015 rule 4"*. **It did not, at the head the assertion was made against:**
(g) was `blocked: freeze`, expressly **not Ready**, with no live issue. It satisfied
*specific*; it failed *approved* and *Ready*. The Product Owner's authority to lift is not in
question — a Product Owner decision outranks this file — but §3 did not **waive** rule 4, it
**asserted** it. **(g)'s `blocked: freeze` is removed by this lift**, and its Definition of
Ready was re-assessed forward and dated, **not backdated**; on that assessment it is **still
not Ready**, because four open specification escalations (ESC-1, ESC-3, ESC-4, ESC-5) are
unaddressed scope questions and the Phase-2 exit determination is owed. **Until (g) is Ready,
rule 4 remains unsatisfied and Phase-3 implementation does not begin.** See
[`../product/human-decisions.md`](../product/human-decisions.md) HD-24 §3.

**The marker's `scope` is UNCHANGED, and the reason is a limit rather than a reassurance.**
Phase 3 work is inside `engine/`, the directory the Phase-2 lift already names, so
`scope: ["engine/"]` is correct and **must not change**: the marker is a list of directory
names checked against the validator's guarded list, and this lift widens **authorized
behaviour within** a directory, not the directory list. The consequence must be stated:
**`tools/validate.mjs` CANNOT DISTINGUISH Phase-2 work from Phase-3 work inside `engine/`.**
It never could — the Phase-2 lift was equally prose over a directory-name check — and it
could not have distinguished them before this lift either. **The prose grants Phase 3; the
machine check is blind to the difference.** That gap is named here on exactly the footing this
file already uses for its other unguarded gaps: *the prose forbids it, the validator does
not*. Anyone relying on CI to catch Phase-3 behaviour committed under a Phase-2-only
authorization will not be caught by CI.

**HD-24's closing directive asked for a widened `scope`, and that half of it was DECLINED.**
Quoted so the departure is legible rather than invisible:

> "To be recorded in `product/human-decisions.md` as **HD-24**, and in
> `governance/build-freeze.md`'s machine-readable marker as **a widened `scope`**."

The record was filed as HD-24. **The marker's `scope` was not widened**, for the reason the
section above already states: `scope` is a **list of directory names**, `engine/` is **already
in it**, and this lift widens authorized *behaviour inside* that directory. **No widening
available in this field expresses this grant** — adding a name could only un-guard a *different*
directory, and there are **18** such candidates (the 19 guarded names above, minus `engine`).
They split in two, and **both halves point the same way**:

- **Eight are on §3's own still-frozen list** — `api`, `db`, `scanner`, `worker`, `dashboard`,
  `alerts`, `billing`, `providers`. Adding any of them would un-guard a directory §3 expressly
  froze: **the literal opposite of what §3 ruled.**
- **Ten appear on no list at all** — `src`, `lib`, `app`, `server`, `client`, `packages`,
  `services`, `web`, `backend`, `frontend`. §3 neither authorized nor froze them. Adding any of
  them would un-guard a directory **no decision addresses**, which is not what §3 ruled either.

*Corrected 2026-07-28, and the correction matters more than the sentence.* This passage first
read *"every candidate (`api`, `db`, … `providers`) is on §3's own still-frozen list"* — **false
for ten of the eighteen**, measured. That is the **same conflation of the guarded list with §3's
NOT-authorized list** that [`../tools/validate.mjs`](../tools/validate.mjs)'s own INVARIANT
comment exists to record: *"685b65a's prose said the list 'was extended to cover the surfaces the
NOT-authorized list above names' while `alerts`, `billing` and provider integration were named as
forbidden and left unguarded."* The two lists are **not** the same list and never were. It
recurred here in the one sentence carrying the entire evidentiary weight of an agent declining a
Product Owner instruction — which is exactly where an over-claim must not sit. Found by Code
Review. **A Product Owner instruction declined on
engineering grounds is written down, not absorbed:** see
[`../product/human-decisions.md`](../product/human-decisions.md) HD-24, *"HD-24's closing
recording directive."* **Reversible by the Product Owner alone** — if a *directory* was
intended, name it, and it is added here **and** to `PRODUCT_CODE_DIRS` together, per the
pairing rule above. **No agent may widen `scope` on its own reading of that directive.**

**This lift does not touch HD-06.** No provider is selected and no spend is authorized. It
does not widen the lift beyond `engine/`, and it changes no roadmap phase order.

<!-- DO NOT RENAME the heading below, relabel its fence, or insert anything between them:
     tools/validate.mjs parses the `## Freeze marker` heading plus the ```yaml fence
     immediately following it, and errors if it cannot find EXACTLY ONE such block.
     Any of those edits fails the build closed rather than silently. -->

## Freeze marker (machine-readable)

```yaml
build_freeze: ON
autonomous_implementation: ENABLED_FOR_SCOPE
lifted_by: "Product Owner — issue #31 (HD-22, Phase 2), 2026-07-26; extended by issue #39 (HD-24 §3, Phase 3), 2026-07-28"
lifted_at: "2026-07-28"
# `scope` is a list of DIRECTORY names, matched against the validator's guarded list.
# It is UNCHANGED because the directory is unchanged: both lifts are inside `engine/`.
# The validator therefore cannot tell Phase-2 work from Phase-3 work here — see the
# Phase 3 section above, which states that gap rather than leaving it to be discovered.
scope: ["engine/"]
```

## Enforcement
The validator asserts `build_freeze: ON` and fails if a product-code directory appears that
is **not** named in `scope`. `engine/` is guarded like every other product directory and is
permitted **only** because the marker above names it — delete the `scope` entry and the
validator fails on `engine/` immediately. That is what makes the lift's boundary mechanical
rather than declaratory. The Auditor cross-checks merges against freeze scope.

**What the marker does NOT reach.** `scope` names **directories**, so it draws the boundary
*between* directories and never *inside* one. Two lifts now sit inside `engine/` — Phase 2
(HD-22) and Phase 3 (HD-24 §3) — and **the validator cannot tell their work apart.** The
boundary between them is the roadmap's behavioural Phase 2 / Phase 3 rule, enforced by review
and by the Auditor, **not by CI**. Stated so it is not rediscovered as a surprise.

## Escalation
Any product code committed under freeze → validator/CI failure + Auditor violation
→ revert → human review.
