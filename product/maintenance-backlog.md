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
| M-08 | `check-evidence.mjs`'s golden census filter is `/^GX-\d\d$/`, so a stray `golden/RM-02` or `GX-024` directory is invisible to the census rather than reported as unexpected | `check-evidence.mjs` | tooling hardening | — |

## Promoted out (was here, turned out to block)

*None yet.*

## Closed

| # | Item | Closed by |
|---|------|-----------|
| M-00 | RM-01 had **no mechanical guard of any kind** — `fixture-replay.mjs` read only `golden/` and `check-evidence.mjs` only schema-validated the annotation. This was **not** a maintenance item; it invalidated the real-market layer's claim to be checked at all, and is logged here only to record that it was closed | `expected-causal.json` + `real-causal.schema.json` + the `real/`-reading tool extension (branch `feat/rm01-causal-replay`) |
