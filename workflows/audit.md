# Workflow — Project Audit

The **Project Auditor** runs an independent audit each cycle. The audit is
**observational**: it changes nothing, it reports (requirement 10).

## Cadence

- Once per cycle, and on demand from the Orchestrator or a human.

## Checklist

1. **Traceability** — every merged change traces roadmap → ticket → plan → PR →
   evidence. List any break.
2. **Evidence integrity** — sample `done` tickets; re-check evidence reproduces.
   Void any Done lacking reproducible evidence ([GOV-006](../governance/definition-of-done.md)).
3. **Scope-drift** — tickets/PRs touching areas with no roadmap trace
   ([GOV-007](../governance/product-focus.md)).
4. **Bloat** — WIP, ticket, and idea budgets; duplicates; stale tickets; meta-work
   ratio ([GOV-008](../governance/ticket-hygiene.md)).
5. **Verified throughput** — Done-with-evidence per cycle vs opened tickets
   ([GOV-009](../governance/prioritization.md)).
6. **Separation of duties** — any self-check or role absorption
   ([GOV-011](../governance/separation-of-duties.md)).
7. **Approval gates** — every gated action carries its human sign-off
   ([GOV-013](../governance/approval-gate.md)).
8. **Freeze compliance** — no product/sentiment code under freeze
   ([GOV-015](../governance/build-freeze.md), [GOV-014](../governance/market-sentiment-context.md)).

## Output

An [audit report](../templates/audit-report.md) with a **traceability matrix**, a
**violation list** (rule id + evidence), and prioritized recommendations handed to
the Orchestrator (flow) and Product Steward (scope). The Auditor is **read-only**,
so it **reads the latest CI result** of [`tools/validate.mjs`](../tools/validate.mjs)
(run by [`governance-validation.yml`](../.github/workflows/governance-validation.yml))
and attaches it, rather than running it itself.
