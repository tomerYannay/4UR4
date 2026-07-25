# 4UR4 — ChatGPT ↔ Claude Handoff Protocol (governed)

> **Status: operating-system / process governance under [GOV-015](../../governance/build-freeze.md)
> build-freeze — no product code.** This protocol is process + coordination only. It changes
> no product definition and grants no build authority. It does **not** weaken any existing
> governance rule or agent tool restriction; it adds a coordination layer on top of them.

## Purpose

Make **GitHub the shared communication and evidence layer** between **Claude Code** (which
does the work in the repository) and **ChatGPT** (which reviews it), so the **Product Owner
(PO)** does not manually copy summaries between the two tools. Claude pushes work and posts a
structured request; ChatGPT reviews against the repository; the PO reads a single source of
truth and makes only the decisions reserved to a human.

The two agents **coordinate and recommend**; they **never self-approve** the decisions
reserved to the PO (§5). All exchange happens as **PR comments, commits, issue comments, files,
and CI** — never as out-of-band chat the PO must relay.

---

## 1. Claude Code responsibilities (end of every meaningful work cycle)

A "meaningful work cycle" = any set of changes that reaches a coherent, validated checkpoint
(a feature slice, a fix, a research increment, a doc set). At the end of every such cycle,
Claude Code **MUST**:

1. **Push** all work to the task branch (never leave the reviewed state only local).
2. **Open or update a draft PR** for that branch (draft until the review + human gates clear).
3. **Ensure the PR description reflects the current head** — update the body so Objective,
   Scope, Linked issues, Head SHA, Evidence, Validation, Governance, Human decisions, and
   ChatGPT review status all match the pushed commit (use the [PR template](../../.github/PULL_REQUEST_TEMPLATE.md)).
4. **Run all required validation** (at minimum `node tools/validate.mjs`, the Bash-hook tests,
   any fixture/independent verification relevant to the change, and CI on the PR head).
5. **Post a top-level PR comment** whose **first line is exactly**:

   ```
   CHATGPT_REVIEW_REQUESTED
   ```

### Required contents of the `CHATGPT_REVIEW_REQUESTED` comment

The comment is an **index to the evidence**, not a replacement for it (§2). It MUST contain,
each clearly labeled:

- **Objective** — what this cycle set out to do.
- **Issue numbers** — the GitHub issues this work traces to.
- **Current head SHA** — the exact commit under review (full or ≥12-char SHA).
- **Files changed** — the paths (and a one-line what/why each), or a link to the diff.
- **Decisions made** — choices taken within already-approved scope.
- **Unresolved questions** — open items needing a reviewer or human answer.
- **Human-gated decisions** — anything in §5 that only the PO may approve (flagged, not taken).
- **Validation results** — exact commands + pass/fail (e.g. validator, hook tests, verifiers).
- **CI status** — the check name(s) and conclusion on the head SHA (link the run).
- **Governance status** — explicit confirmation, e.g. "GOV-015 build-freeze remains ON; no
  product-code dirs; no governance rule weakened."
- **Requested review scope** — precisely what ChatGPT should review (and what is out of scope
  for this round).

The comment MUST name the **same head SHA** that the PR description shows. If they differ, the
request is stale and MUST be reposted.

---

## 2. Evidence rule (source of truth)

**The PR, repository files, commits, issue comments, and CI are the source of truth.**

- ChatGPT **must not** be expected to rely only on Claude's summary. The
  `CHATGPT_REVIEW_REQUESTED` comment is an **index** into the evidence, **not a substitute**
  for it. ChatGPT is expected to open the diff, the changed files, the validation output, and
  the CI run at the stated head SHA.
- Claude **must not** assert an outcome the repository does not show. Every claim in the
  request comment must be independently checkable in the repo/PR/CI at the stated SHA
  ([GOV-006](../../governance/definition-of-done.md) evidence discipline extends here).
- If evidence and summary disagree, the **evidence wins** and the summary is corrected.

---

## 3. ChatGPT response states

Every ChatGPT review is posted as a PR comment whose **first line is exactly one** of:

```
CHATGPT_REVIEW_APPROVED
CHATGPT_CHANGES_REQUESTED
CHATGPT_HUMAN_DECISION_REQUIRED
CHATGPT_REVIEW_BLOCKED
```

Meaning:

| State | Meaning | Next actor |
|-------|---------|-----------|
| `CHATGPT_REVIEW_APPROVED` | Review passed at the stated head; no required changes. | PO (for gated PRs) or Release Ops (for non-gated, both internal gates green). |
| `CHATGPT_CHANGES_REQUESTED` | Specific required changes before approval. | Claude (implement approved scope only, §4). |
| `CHATGPT_HUMAN_DECISION_REQUIRED` | A decision reserved to the PO (§5) or an unresolved disagreement. | Product Owner. |
| `CHATGPT_REVIEW_BLOCKED` | Cannot review — evidence missing/stale, SHA mismatch, CI red, or scope unclear. | Claude (fix the request, repost). |

### Required contents of a ChatGPT review

- **Reviewed head SHA** — the exact commit reviewed (must match the request; if not → `BLOCKED`).
- **Files inspected** — what was actually opened (evidence the review is real, per §2).
- **Findings by severity** — `blocker` / `major` / `minor` / `nit`, each anchored to a file/line
  or artifact.
- **Required changes** — the closed list that must be addressed for approval.
- **Optional recommendations** — non-blocking suggestions (Claude may decline with a reason).
- **Whether another review is required** — yes/no after changes.
- **Whether the PR is eligible for Product Owner approval** — yes/no, and if human-gated (§5),
  say so explicitly.

---

## 4. Claude follow-up

Claude **must read the latest ChatGPT review before continuing.** Approval is **head-specific**:
Claude **must not treat an older review as approval for a newer head** (a new commit invalidates
a prior `CHATGPT_REVIEW_APPROVED`).

When the state is `CHATGPT_CHANGES_REQUESTED`, Claude MUST:

1. **Implement only the requested, approved scope** — no scope expansion, no gold-plating
   ([GOV-007](../../governance/product-focus.md)); discovered scope becomes an idea, not an
   in-place change.
2. **Push a new commit** to the task branch.
3. **Respond to each finding** — a point-by-point reply (addressed / declined-with-reason /
   deferred-as-idea), posted on the PR.
4. **Rerun validation** (§1.4) on the new head.
5. **Post a new `CHATGPT_REVIEW_REQUESTED` comment** — with the **new head SHA** and the updated
   index.

For `CHATGPT_REVIEW_BLOCKED`, Claude fixes the request (missing/stale evidence, SHA mismatch, red
CI) and reposts. For `CHATGPT_HUMAN_DECISION_REQUIRED`, Claude **stops** and waits for the PO; it
may prepare options but takes no gated action.

---

## 5. Human authority (only the Product Owner may approve)

Claude and ChatGPT may **recommend** but **never self-approve**:

- **Spending or paid providers** (data feeds, APIs, any recurring cost).
- **Roadmap changes** ([GOV-002](../../governance/roadmap-authority.md)).
- **Build-freeze changes** — lifting/altering [GOV-015](../../governance/build-freeze.md).
- **Product-definition changes** (requirements, thesis, scope).
- **Security / privacy gates** (e.g. SaaS PII, billing, credential handling).
- **Merges explicitly marked human-gated** (any PR labeled/marked as requiring PO sign-off).

For any of these, the correct agent output is a **recommendation + `CHATGPT_HUMAN_DECISION_REQUIRED`**
(or a flagged human-gated item in the request comment). The PO's approval is recorded on the PR
/ issue and, where relevant, in [`product/human-decisions.md`](../../product/human-decisions.md).
This protocol **does not** grant Release Ops, the Orchestrator, ChatGPT, or Claude any authority
they do not already hold; [GOV-013](../../governance/approval-gate.md) still governs.

---

## 6. Loop protection

To prevent endless agent-to-agent discussion:

1. **Maximum two automated review rounds per PR** (round = one `CHATGPT_REVIEW_REQUESTED` →
   `CHATGPT_*` response pair). Round count is tracked in the PR description's "ChatGPT review
   status" section.
2. **After two unsuccessful rounds**, the next comment MUST be
   `CHATGPT_HUMAN_DECISION_REQUIRED` — hand the disagreement to the Product Owner rather than
   continuing to argue.
3. **No repeated comments without new evidence** — a new `CHATGPT_REVIEW_REQUESTED` requires a
   **new commit or new evidence** (new head SHA). Re-posting the same request against the same
   head is forbidden.
4. **No autonomous scope expansion** — reviews and follow-ups stay within the PR's stated scope
   (GOV-007).
5. **No creation of speculative tickets during review** — review does not spawn new work items;
   genuine new scope goes to the [Ideas Inbox](../../ideas/inbox.md) for human + Steward triage
   ([GOV-003](../../governance/roadmap-authority.md)), not into new tickets
   ([GOV-008](../../governance/ticket-hygiene.md)).

---

## 7. PR template

Every PR uses [`.github/PULL_REQUEST_TEMPLATE.md`](../../.github/PULL_REQUEST_TEMPLATE.md), which
carries: Objective, Scope, Non-goals, Linked issues, Head SHA, Evidence, Validation, Governance,
Human decisions, and ChatGPT review status. Keeping these current (§1.3) is what lets ChatGPT
and the PO work from the PR alone.

## 8. Coordination Queue

The single permanent issue **"Agent Coordination Queue"** is an **index** of PRs currently
awaiting external review — PR number, branch, head SHA, current review state, round count. It
holds **no implementation details** and is never "worked" as a ticket (it is a meta index,
exempt from the Ready/WIP budgets of [GOV-008](../../governance/ticket-hygiene.md)). The
Orchestrator keeps it current when it initiates or closes a handoff.

## 9. Agent roles in the handoff

- **Orchestrator (Agent Zero)** — **initiates handoffs**: at the end of a cycle it ensures the
  push/PR/validation steps ran and posts (via `gh`) the `CHATGPT_REVIEW_REQUESTED` comment,
  updates the Coordination Queue, and enforces the §6 two-round cap (escalating to
  `CHATGPT_HUMAN_DECISION_REQUIRED`). It authors no files and approves nothing.
- **Project Auditor** — **verifies evidence completeness** (read-only): before/for a handoff it
  checks that every claim in the request comment maps to real repository evidence at the stated
  SHA (commits, changed files, validation output, CI, governance status). It returns a
  completeness verdict and flags any gap; it posts nothing and changes nothing.
- **Code Reviewer** — **responds to review findings**: it ingests ChatGPT's
  `CHATGPT_CHANGES_REQUESTED` findings, adjudicates each against the diff, plan, and ticket
  intent, and produces the point-by-point response + required-change list (in scope, GOV-007),
  handing rework to the Implementation Engineer. It merges nothing and never reviews its own code.
- **Release & Ops** — **does not merge without the required approval state**: in addition to its
  existing gates (a passing Verification verdict **and** an approving Code Review,
  [GOV-005](../../governance/definition-of-done.md)/[GOV-006](../../governance/definition-of-done.md)),
  it treats `CHATGPT_CHANGES_REQUESTED` / `CHATGPT_HUMAN_DECISION_REQUIRED` /
  `CHATGPT_REVIEW_BLOCKED` as **blocking**, requires a `CHATGPT_REVIEW_APPROVED` (or explicit PO
  approval) whose **reviewed head SHA matches the current head**, and refuses any human-gated
  merge without the PO's recorded approval ([GOV-013](../../governance/approval-gate.md)). These
  are **additional** gates — none of the existing gates is removed or weakened.

---

*Process/governance artifact under GOV-015. It authorizes no build and changes no product
definition. It composes with — and never overrides — the governance rules it references.*
