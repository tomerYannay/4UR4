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
a **named list** of product-code directories, not a heuristic: `src`, `lib`, `app`, `server`,
`client`, `packages`, `engine`, `api`, `services`, `scanner`, `worker`, `dashboard`, `web`,
`backend`, `frontend`, `db`, `alerts`, `billing`, `providers`. A directory outside that list is
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

<!-- DO NOT RENAME the heading below, relabel its fence, or insert anything between them:
     tools/validate.mjs parses the `## Freeze marker` heading plus the ```yaml fence
     immediately following it, and errors if it cannot find EXACTLY ONE such block.
     Any of those edits fails the build closed rather than silently. -->

## Freeze marker (machine-readable)

```yaml
build_freeze: ON
autonomous_implementation: ENABLED_FOR_SCOPE
lifted_by: "Product Owner — issue #31, 2026-07-26"
lifted_at: "2026-07-26"
scope: ["engine/"]
```

## Enforcement
The validator asserts `build_freeze: ON` and fails if a product-code directory appears that
is **not** named in `scope`. `engine/` is guarded like every other product directory and is
permitted **only** because the marker above names it — delete the `scope` entry and the
validator fails on `engine/` immediately. That is what makes the lift's boundary mechanical
rather than declaratory. The Auditor cross-checks merges against freeze scope.

## Escalation
Any product code committed under freeze → validator/CI failure + Auditor violation
→ revert → human review.
