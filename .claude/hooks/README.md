# Bash Safety Hook

A single project-scoped `PreToolUse` hook ([`../settings.json`](../settings.json))
gates **every** `Bash` command — from the primary session and from subagents —
through [`bash-guard.mjs`](bash-guard.mjs). It is deterministic and dependency-free
(Node only), and it reinforces the governance boundaries
([GOV-011](../../governance/separation-of-duties.md),
[GOV-015](../../governance/build-freeze.md),
[GOV-016](../../governance/temporary-specialists.md)) at the tool layer.

## How the role is determined

Claude Code passes `agent_type` on the PreToolUse payload when a subagent runs
(omitted for the main session). The guard maps that to a policy; explicit
`--role <name>` or `CLAUDE_AGENT_ROLE` override it (used by temporary specialists).

## Policy (what each role may run)

| Role | DANGER | File mutation | Git state | GitHub state |
|------|:------:|:-------------:|:---------:|:------------:|
| `implementation-engineer` | ❌ blocked | ✅ allowed (in-repo) | ✅ allowed | ✅ allowed |
| `release-ops` | ❌ blocked | ❌ blocked | ✅ allowed (release) | ✅ allowed (release) |
| `verification`, `code-reviewer` | ❌ | ❌ | ❌ | ❌ |
| `product-innovation`, `project-auditor` | ❌ | ❌ | ❌ | ❌ |
| `product-steward`, `architect` | ❌ | ❌ | ❌ | ❌ |
| main session / `default` | ❌ | ✅ | ✅ | ✅ |

"❌ blocked" = commands in that category are denied for that role. Everything else
— tests, builds, linters, type-checks, formatters in check mode, `git diff/status/
log/show`, `gh … view/list/diff` — runs normally.

## DANGER (fail closed for every role)

Force pushes; rewriting `main`/`master` history (`reset --hard main`, `rebase`,
`filter-branch`, `commit --amend` on main); deleting the repo/`.git`; recursive
deletes of `/`, `~`, parent, or system dirs; `sudo`/`su`; global/system git config;
`curl … | sh`; reading or exfiltrating secrets (`.env`, `~/.ssh`, credentials).

## Role-specific rules (requirement mapping)

- **Read-only** (`product-innovation`, `project-auditor`) — block any mutation of
  files, git, GitHub, or system config.
- **Verification / Review** — may run tests, linters, type-checks, and
  `git diff/status/log/show`; may **not** edit/delete files, change git state
  (commit/push/merge/reset/checkout), or modify GitHub issues/PRs/labels/releases.
- **Release & Ops** — may perform release operations (merge/tag/push/`gh … merge`/
  `release create`); the "both gates green" precondition is enforced by governance
  ([GOV-005](../../governance/definition-of-done.md)), not by this hook.
- **Implementation Engineer** — may write in the repo/ticket branch, but is blocked
  from destructive ops outside the repo, secret exposure, force pushes, rewriting
  `main` history, deleting the repo, and global/system config.

## Deliberate limits (honest scope)

This is a conservative denylist, **not a perfect shell parser**. It can miss exotic
obfuscations and may occasionally over-block an unusual read-only command (e.g. a
write-mode formatter with no `--write` flag is not detected; a redirect to a file
is always treated as a write). It complements — does not replace — governance,
separation of duties, and the human PR-approval gate.

## Tests

`node .claude/hooks/bash-guard.test.mjs` — 200+ assertions across all roles
(allowed and blocked examples). Run in CI by
[`governance-validation.yml`](../../.github/workflows/governance-validation.yml).
