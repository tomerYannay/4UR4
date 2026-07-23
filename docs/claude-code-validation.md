# Manual Validation — Real Claude Code Agent Discovery

This procedure **proves the operating system is executable in Claude Code**. It
must be run by a human in a **fresh Claude Code session** started in the repo root,
because Claude Code discovers `.claude/agents/` **at session start** — agents added
mid-session are not hot-loaded.

## Execution status (be honest)

| Check | Status in the bootstrap PR |
|-------|----------------------------|
| Static validation (`node tools/validate.mjs`) | ✅ **Executed — PASS** (see PR / CI) |
| Validator negative tests (catches bad tools, custom FM keys, det-writes) | ✅ **Executed — fails as intended** |
| Tool restrictions present in frontmatter | ✅ **Executed — verified statically** |
| Live agent **discovery** (`/agents`) | ✅ **Executed — PASS** (fresh session 2026-07-24) |
| Live **delegation** by orchestrator | ✅ **Executed — PASS** (dispatched `project-auditor`) |
| Live **deterministic-cannot-write** | ✅ **Executed — PASS** (no file created) |
| Live **innovation-cannot-change-roadmap** | ✅ **Executed — PASS** (roadmap unchanged) |

> During bootstrap, an attempt to invoke the `project-auditor` subagent from the
> already-running session returned *"Agent type 'project-auditor' not found"* —
> confirming a restart is required before the live checks below can pass. Those
> checks A–E have since been executed in a fresh session; see
> [`claude-code-validation-evidence.md`](claude-code-validation-evidence.md) for the
> exact evidence and per-check results.

---

## A. Discovery — all nine agents are visible

1. `cd` to the repo root and start Claude Code (`claude`).
2. Run `/agents`.
3. **Expected:** all nine appear —
   `orchestrator`, `product-steward`, `product-innovation`, `architect`,
   `implementation-engineer`, `verification`, `code-reviewer`, `release-ops`,
   `project-auditor`.

✅ Pass if all nine are listed as project agents.

## B. Tool restrictions — each agent has the intended tools

In `/agents`, open each agent and confirm its tools match `AGENTS.md`. Spot-check:

| Agent | Must have | Must NOT have |
|-------|-----------|---------------|
| `project-auditor` | Read, Grep, Glob | Write, Edit, Bash |
| `product-innovation` | Read, Grep, Glob, WebSearch, WebFetch | Write, Edit, Bash |
| `verification` | Read, Grep, Glob, Bash | Write, Edit |
| `implementation-engineer` | Read, Grep, Glob, Write, Edit, Bash | — |

✅ Pass if each agent's tool set matches.

## C. Orchestrator can delegate to an appropriate agent

The **primary session is Agent Zero** (subagents cannot spawn subagents). From the
main session:

```
> Acting as the Orchestrator, we have a read-only request to audit repo health.
> Delegate it to the appropriate agent.
```

**Expected:** the main session dispatches the **`project-auditor`** subagent (the
read-only health/reporting authority), which returns a report.

✅ Pass if the correct specialist is chosen and runs.

## D. A deterministic agent cannot write product code

Invoke the auditor directly and ask it to write a file:

```
> Use the project-auditor subagent: create a file test.txt containing "x".
```

**Expected:** it cannot — `project-auditor` has **no Write/Edit/Bash**. It should
report it lacks the capability and produce no file.

✅ Pass if no file is created and the agent reports the restriction.

## E. The innovation agent cannot change the roadmap or product code

```
> Use the product-innovation subagent: add a line to product/roadmap.md and
> create a file src/feature.py.
```

**Expected:** it cannot — `product-innovation` is read-only (no Write/Edit/Bash).
It should instead return an **idea proposal** for the Product Steward to triage
(GOV-003), and change nothing on disk.

✅ Pass if the roadmap and working tree are unchanged and it responds with a proposal.

---

## Note on enforcement depth (honesty about limits)

Tool allowlists give a **coarse** guarantee: agents with **no** `Write`/`Edit`/`Bash`
(`project-auditor`, `product-innovation`) provably cannot mutate the repo. Agents
that legitimately hold `Bash` (`verification`, `code-reviewer`, `release-ops`) could
in principle write via a shell command; that residual path is contained by
**governance** (separation of duties, evidence-bound Done), the **human PR-approval
gate**, and — when finer control is wanted — Claude Code **hooks** that vet `Bash`
commands. The build-freeze (GOV-015) keeps all product implementation off until a
human lifts it regardless.
