# Agent Registry

The 4UR4 operating system runs on **9 permanent agents** — the hard ceiling
(requirement 2) — plus **temporary, ticket-scoped specialists** ([GOV-016](governance/temporary-specialists.md))
that do **not** count toward it.

Each permanent agent has **exactly one** authority so responsibilities never
overlap ([GOV-011 Separation of Duties](governance/separation-of-duties.md)).

## Executable in Claude Code

The canonical, executable agent definitions live under
[`.claude/agents/`](.claude/agents/) — Claude Code discovers them at session
start. Each file carries **real Claude Code frontmatter** (`name`, `description`,
`tools`, `disallowedTools`, `model`, `permissionMode`); governance metadata (`id`,
`class`, `authority`, `bindings`, …) lives in a machine-readable
`<!-- 4ur4:governance … -->` block in the body, so Claude Code never sees custom
frontmatter keys. **This is the single source of truth** — there is no second copy.

Prove discovery with [`docs/claude-code-validation.md`](docs/claude-code-validation.md).

## Agent classes ([GOV-001](governance/classification.md))

| Class | Behaviour | Creativity |
|-------|-----------|------------|
| **deterministic** | Same input → same output. Rule-checkers and gates. | None permitted |
| **bounded-creative** | Generates novel options *inside* explicit constraints. | Bounded |
| **mixed** | Deterministic where it decides, creative where it proposes. | Scoped per action |

## The nine permanent agents

| Agent (`name`) | Class | Sole authority | Tools | Cannot write? | File |
|----------------|-------|----------------|-------|---------------|------|
| `orchestrator` (Agent Zero) | mixed | Sequencing & prioritization | Read, Grep, Glob, Bash, TodoWrite | no file edits | [.claude/agents/orchestrator.md](.claude/agents/orchestrator.md) |
| `product-steward` | mixed | Roadmap & Definition of Ready | Read, Grep, Glob, Write, Edit | writes **docs** only | [.claude/agents/product-steward.md](.claude/agents/product-steward.md) |
| `product-innovation` | bounded-creative | Idea generation (proposals) | Read, Grep, Glob, WebSearch, WebFetch | **yes — read-only** | [.claude/agents/product-innovation.md](.claude/agents/product-innovation.md) |
| `architect` | mixed | Technical design of a ticket | Read, Grep, Glob, Write, Edit | writes **docs** only | [.claude/agents/architect.md](.claude/agents/architect.md) |
| `implementation-engineer` | mixed | Writing product code | Read, Grep, Glob, Write, Edit, Bash, NotebookEdit | **no — the code author** | [.claude/agents/implementation-engineer.md](.claude/agents/implementation-engineer.md) |
| `verification` | deterministic | Evidence-based Done verdict | Read, Grep, Glob, Bash | no file edits | [.claude/agents/verification.md](.claude/agents/verification.md) |
| `code-reviewer` | mixed | Judgement on diff quality | Read, Grep, Glob, Bash | no file edits | [.claude/agents/code-reviewer.md](.claude/agents/code-reviewer.md) |
| `release-ops` | deterministic | Merge, release, move to Done | Read, Grep, Glob, Bash | no file edits (git/gh only) | [.claude/agents/release-ops.md](.claude/agents/release-ops.md) |
| `project-auditor` | deterministic | Health, traceability, reports | Read, Grep, Glob | **yes — read-only** | [.claude/agents/project-auditor.md](.claude/agents/project-auditor.md) |

Distribution: **3 deterministic, 1 bounded-creative, 5 mixed**. `model: inherit`
and `permissionMode: default` on all nine (see "Model & permission choices" below).

## How each agent is invoked by Claude Code

- **Orchestrator = the primary Claude Code session (Agent Zero).** Because Claude
  Code removes the subagent-spawning tool from subagents, delegation happens at the
  primary-session layer: the main session reads state and dispatches specialists.
  When `orchestrator` is invoked *as* a subagent it returns a **routing decision**
  for the primary session to execute.
- **The other eight are delegatable subagents.** Invoke by intent (Claude auto-
  selects via each agent's `description`) or explicitly: *"use the `verification`
  subagent to …"*. Their `tools`/`disallowedTools` enforce the coarse boundary;
  governance enforces the fine-grained scope.

## Temporary specialists ([GOV-016](governance/temporary-specialists.md))

To cover quant, market-data, ML, backend, frontend, security, and DevOps depth
without growing the permanent roster:

- Created **per approved ticket**, justified by the **Orchestrator or Architect**,
  retired when the ticket is Done. **Do not count** toward the nine.
- Declare `status: temporary`, a `ticket`, and a `parent_authority` (the accountable
  permanent agent). Their output **returns to that parent**.
- **Advisory** specialists (quant-research, trendline-math, market-data,
  ml-evaluation, security) are **read-only**. **Implementation** specialists
  (backend, frontend, devops) may write code **only under the Implementation
  Engineer's authority**, within the ticket branch. None may create scope, edit the
  roadmap, mark Done, or merge.
- Scaffold: [`templates/specialist-agent.md`](templates/specialist-agent.md).

## Model & permission choices

`model: inherit` on every agent — no bootstrap agent has a justified reason to
override the session model; the field is set explicitly to record that decision.
`permissionMode: default` on every agent — under the build-freeze no agent
justifies a non-default mode. (When autonomy is enabled, the
`implementation-engineer` is the candidate for `acceptEdits`; that is a future,
human-approved change, not made here.)

## Authority matrix (who may do what)

| Capability | Owner | Everyone else |
|------------|-------|---------------|
| Add/change **roadmap** | `product-steward` (with human) | forbidden |
| Generate **ideas** | `product-innovation` | forbidden |
| Write **product code** | `implementation-engineer` (+ its temporary specialists) | forbidden |
| Issue **Done verdict** (evidence) | `verification` | forbidden |
| **Merge / release** | `release-ops` | forbidden |
| Mark ticket **Done** on board | `release-ops` | forbidden |
| **Prioritize / assign** work | `orchestrator` (primary session) | forbidden |
| **Audit / report** | `project-auditor` | forbidden |

## Lifecycle at a glance

```
Idea (product-innovation) ─▶ Inbox ─▶ [human + product-steward triage] ─▶ Roadmap
      │
      ▼
Ready ticket (product-steward) ─▶ orchestrator ─▶ architect (plan)
      │                                              (± temporary specialists)
      ▼
implementation-engineer (code + evidence) ─▶ verification (evidence gate)
      │
      ▼
code-reviewer ─▶ release-ops (merge + Done) ─▶ project-auditor (report)
```

See [`workflows/`](workflows/) for GitHub mechanics and
[GOV-010 Handoff Protocol](governance/handoffs.md) for the connective rules.
