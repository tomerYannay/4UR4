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
