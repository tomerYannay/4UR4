<!--
4UR4 PR template. Governed by GOV-005/006/007/011/013/015 and the
ChatGPT↔Claude Handoff Protocol (docs/operations/agent-handoff-protocol.md).
Keep every section current with the pushed HEAD (protocol §1.3). The PR is the
shared source of truth (protocol §2) — this template is the index into the evidence.
-->

## Objective
<!-- One or two sentences: what this PR is for. -->

## Scope
<!-- What IS included in this PR. -->

## Non-goals
<!-- What is deliberately NOT included; discovered scope becomes an idea, not an in-place change (GOV-007). -->

## Linked issues
<!-- e.g. Refs #NN  (use "Closes #NN" only when a human-approved merge should close it). -->

## Head SHA
<!-- The exact commit this description reflects (≥12 chars). MUST match the CHATGPT_REVIEW_REQUESTED comment. -->

## Evidence (source of truth — GOV-006)
<!-- Repository-verifiable proof mapped to what changed: commits, changed files, artifacts, links. The reviewer inspects these, not just the summary (protocol §2). -->
| Claim / acceptance | Evidence (file / commit SHA / test output / CI link) |
|--------------------|------------------------------------------------------|
|  |  |

## Validation
<!-- Exact commands run + pass/fail, e.g. node tools/validate.mjs; node .claude/hooks/bash-guard.test.mjs; fixture/independent verification. -->
- [ ] `node tools/validate.mjs` — PASS
- [ ] `node .claude/hooks/bash-guard.test.mjs` — PASS
- [ ] Change-specific verification — <!-- result -->
- [ ] CI on this head — <!-- check name + conclusion + link -->

## Governance
<!-- Explicit status. -->
- [ ] **GOV-015 build-freeze: ON** (no product-code dirs; no freeze marker changed)
- [ ] No governance rule or agent tool restriction weakened
- [ ] In scope (GOV-007); no speculative tickets created

## Human decisions (only the Product Owner may approve — protocol §5)
<!-- List any spending/paid-provider, roadmap, build-freeze, product-definition, security/privacy, or human-gated-merge decision. Flagged & recommended, NOT taken. "none" if none. -->

## ChatGPT review status
<!-- Updated each round. -->
- Latest request head SHA: <!-- SHA of the current CHATGPT_REVIEW_REQUESTED -->
- Latest ChatGPT state: <!-- CHATGPT_REVIEW_APPROVED | CHATGPT_CHANGES_REQUESTED | CHATGPT_HUMAN_DECISION_REQUIRED | CHATGPT_REVIEW_BLOCKED | (none yet) -->
- Reviewed head SHA: <!-- SHA ChatGPT reviewed; must equal current head for approval to count (protocol §4) -->
- Automated review round: <!-- N of max 2 (protocol §6) -->
- Eligible for Product Owner approval: <!-- yes/no -->

<!-- Merge is performed ONLY by Release & Ops, only with a passing Verification verdict AND an
approving Code Review AND a CHATGPT_REVIEW_APPROVED (or explicit PO approval) at the current head,
and never for a human-gated PR without the PO's recorded approval. Kept as draft until those hold. -->
