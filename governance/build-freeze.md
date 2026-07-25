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
   **context-only** research/design.
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

**Conditions attached to the permission:**

1. It confers **no Phase-2 credit**. Phase 2 is not partly done because this exists.
2. The Phase-2 engine MUST be authored **from the specification, by an agent that has not
   read this model**, so that "exact reproduction" tests conformance rather than
   transcription.
3. The **specification is authoritative**. Any divergence between the two is a spec-defect
   report or a model bug — never a silent model behaviour.
4. This ruling covers **this file, for this purpose**. It is not a precedent for committing
   executable product functionality under the freeze, and it is **not a freeze lift**:
   `build_freeze` stays `ON` and no product code is authorized.

## Freeze marker (machine-readable)

```yaml
build_freeze: ON
autonomous_implementation: DISABLED
lifted_by: null
lifted_at: null
scope: null
```

## Enforcement
The validator asserts `build_freeze: ON` and fails if product-code directories
appear while frozen. The Auditor cross-checks merges against freeze scope.

## Escalation
Any product code committed under freeze → validator/CI failure + Auditor violation
→ revert → human review.
