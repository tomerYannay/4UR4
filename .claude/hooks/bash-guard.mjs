#!/usr/bin/env node
// 4UR4 Bash safety hook — deterministic, dependency-free PreToolUse guard.
//
// Decides whether a Bash command may run, based on the ACTING AGENT ROLE
// (Claude Code passes `agent_type` on the PreToolUse stdin when a subagent runs).
//
// It is intentionally conservative and NOT a full shell parser (per hook policy):
// it FAILS CLOSED for a small set of clearly dangerous commands, and applies
// role-scoped mutation rules — while leaving ordinary test/build/lint/format/dev
// commands untouched.
//
// The pure decision function `evaluate(role, command)` is exported and unit-tested
// by bash-guard.test.mjs. The CLI wrapper reads the PreToolUse JSON from stdin and
// blocks by exiting 2 with a reason on stderr (Claude Code's documented block path).

// ----------------------------------------------------------------------------
// Roles → which categories are BLOCKED. DANGER is always blocked (fail closed).
//   FILE = file mutation (create/edit/delete/move)
//   GIT  = git state change (commit/push/merge/reset/checkout/…)
//   GH   = GitHub state change (gh create/edit/merge/close/label/release/…)
// ----------------------------------------------------------------------------
export const ROLE_POLICY = {
  // Primary session (Agent Zero) / unknown: only clearly dangerous commands blocked.
  default: ['DANGER'],
  orchestrator: ['DANGER'],
  // Sole code author: may write in-repo; only dangerous ops blocked.
  'implementation-engineer': ['DANGER'],
  // Inspect & test only — no mutation of files, git, or GitHub.
  verification: ['DANGER', 'FILE', 'GIT', 'GH'],
  'code-reviewer': ['DANGER', 'FILE', 'GIT', 'GH'],
  // Read-only advisory agents (they also have no Bash tool): block every mutation.
  'product-innovation': ['DANGER', 'FILE', 'GIT', 'GH'],
  'project-auditor': ['DANGER', 'FILE', 'GIT', 'GH'],
  // Release & Ops: may run release ops (git/gh); still no file edits or danger.
  // Gate-green (Verification + Review) is enforced by GOVERNANCE, not this hook.
  'release-ops': ['DANGER', 'FILE'],
  // Doc-writing agents that have no Bash tool; if ever invoked, treat as read-only.
  'product-steward': ['DANGER', 'FILE', 'GIT', 'GH'],
  architect: ['DANGER', 'FILE', 'GIT', 'GH'],
};
export const KNOWN_ROLES = Object.keys(ROLE_POLICY);

// ----------------------------------------------------------------------------
// QUARANTINE — paths a role may not read (Issue #20, HD-15 condition 2, E2-AUTHOR).
//
// The Phase-2 engine must be authored independently of the causal reference model.
// E2-AUTHOR-B (the read restriction) is the PREVENTIVE control; E2-AUTHOR-A (the
// committed engine/ must not import, copy, execute or mechanically translate the
// model) is what is assessed at the gate and GOVERNS where the two diverge. This
// hook is the cheapest place to stop an A-violation from ever being written.
//
// Scoped to the ONE role that authors product code. Every other role must be able to
// read these files: Verification and Code Review re-derive fixture values from the
// model, and the Project Auditor reads everything.
//
// NOT quarantined, deliberately: the fixtures themselves. They are the conformance
// CONTRACT the engine must satisfy, and phase2-independence-mechanism.md classifies
// product/fixtures/golden/** — including every causal_record — as R2, "PERMEABLE by
// necessity". Quarantining the contract would make the gate unreadable by the author
// who has to pass it. (product/fixtures/real/** is unclassified — M-09, open.)
// ----------------------------------------------------------------------------
export const QUARANTINE = {
  'implementation-engineer': [
    'tools/fixture-replay.mjs',                            // the causal reference model
    'product/fixtures/VERIFICATION.md',                    // quarantined by the mechanism doc
    'docs/architecture/phase2-independence-mechanism.md',  // describes the controls themselves
  ],
};

const QUARANTINE_NOTE =
  'HD-15 condition 2 / E2-AUTHOR-B: the Phase-2 engine must be authored by an agent that has '
  + 'not read the causal reference model. Derive behaviour from product/trendline-specification.md, '
  + 'product/human-decisions.md and the fixture DATA instead. If you believe you need this file, '
  + 'STOP and escalate — do not work around it.';

// Match a quarantined path inside arbitrary text (a tool argument or a shell command).
// Compares normalised POSIX tails, so an absolute path, a ./-relative path and a bare
// repo-relative path all match. Also catches the bare basename, because `cat
// fixture-replay.mjs` from inside tools/ is the same read.
export function hitsQuarantine(role, text) {
  const paths = QUARANTINE[role];
  if (!paths || !text) return null;
  const hay = String(text).replace(/\\/g, '/');
  for (const p of paths) {
    const base = p.split('/').pop();
    const esc = base.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (hay.includes(p) || new RegExp(`(^|[^\\w./-])${esc}([^\\w-]|$)`).test(hay)) return p;
  }
  return null;
}

export function quarantineBlock(role, text) {
  const hit = hitsQuarantine(role, text);
  if (!hit) return null;
  return {
    decision: 'block', category: 'QUARANTINE', role, path: hit,
    reason: `'${hit}' is QUARANTINED from '${role}' — ${QUARANTINE_NOTE}`,
  };
}

// File-access decision for non-Bash tools (Read, Grep, Glob, Edit, Write, ...).
// Every field a file-ish tool might carry a path in is checked as one blob, so a tool
// with a differently-named path field fails CLOSED rather than open.
export function evaluateFileAccess(role, toolInput = {}) {
  const blob = [
    toolInput.file_path, toolInput.filePath, toolInput.path, toolInput.notebook_path,
    toolInput.pattern, toolInput.glob, toolInput.pathspec, toolInput.command,
  ].filter(Boolean).join(' \n ');
  return quarantineBlock(role, blob) || { decision: 'allow', role };
}

// ----------------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------------
const has = (cmd, re) => re.test(cmd);
function stripHarmlessRedirects(cmd) {
  return cmd
    .replace(/\d*>>?\s*\/dev\/null/g, ' ')
    .replace(/&>>?\s*\/dev\/null/g, ' ')
    .replace(/2>&1/g, ' ');
}
// Split a compound command into segments on shell separators (keep redirects intact).
function segments(cmd) {
  return cmd.split(/\s*(?:\|\||&&|;|\n|\|)\s*/).map((s) => s.trim()).filter(Boolean);
}

// ---- git classification -----------------------------------------------------
const GIT_RO_SUBCMDS = new Set([
  'status', 'diff', 'log', 'show', 'blame', 'rev-parse', 'rev-list', 'describe',
  'cat-file', 'ls-files', 'ls-tree', 'shortlog', 'for-each-ref', 'reflog', 'grep',
  'whatchanged', 'name-rev', 'merge-base', 'symbolic-ref', 'var', 'count-objects', 'help', 'version',
]);
const GIT_AMBIGUOUS = new Set(['branch', 'tag', 'remote', 'config', 'stash', 'notes', 'worktree']);
function gitIsMutating(seg) {
  if (!/\bgit\b/.test(seg)) return false;
  const after = seg.replace(/^[\s\S]*?\bgit\b/, '').trim();
  const tokens = after ? after.split(/\s+/) : [];
  let i = 0;
  while (i < tokens.length) {              // skip global options and their args
    const t = tokens[i];
    if (t === '-C' || t === '-c' || t === '--git-dir' || t === '--work-tree') { i += 2; continue; }
    if (t.startsWith('-')) { i += 1; continue; }
    break;
  }
  const sub = tokens[i];
  if (!sub) return false;                  // bare `git`
  const rest = tokens.slice(i + 1);
  if (GIT_RO_SUBCMDS.has(sub)) return false;
  if (GIT_AMBIGUOUS.has(sub)) {
    if (rest.length === 0) return false;
    if (/^(-l|--list|-v|-a|-r|--verbose|--get.*|--show-current|--get-url|list)$/.test(rest[0])) return false;
    return true;
  }
  return true; // add, rm, mv, commit, merge, rebase, reset, checkout, switch, restore,
               // push, pull, fetch, cherry-pick, revert, clean, apply, am, init, clone, …
}

// ---- gh (GitHub CLI) classification ----------------------------------------
const GH_RO_VERBS = new Set(['view', 'list', 'status', 'diff', 'checks', 'browse']);
function ghIsMutating(seg) {
  const m = seg.match(/\bgh\s+([a-z-]+)(?:\s+([a-z-]+))?/);
  if (!m) return false;
  const group = m[1];
  const verb = m[2] || '';
  if (group === 'api') return /(-X|--method)\s*(POST|PATCH|PUT|DELETE)/i.test(seg);
  if (['auth', 'config', 'alias', 'extension', 'gist', 'secret', 'ssh-key', 'gpg-key'].includes(group)) {
    return /\b(login|logout|set|add|remove|delete|create|edit|import|refresh|clear)\b/.test(seg);
  }
  if (GH_RO_VERBS.has(verb)) return false;
  if (verb === '' && GH_RO_VERBS.has(group)) return false;
  return true; // create/edit/delete/close/merge/comment/review/label/release/ready/…
}

// ---- file mutation (conservative; does NOT match ordinary format/lint/test) --
function fileMutation(seg) {
  const c = stripHarmlessRedirects(seg);
  if (has(c, /(^|[|;&]|\s)(rm|unlink|shred|truncate|rmdir)\b/)) return 'deletes files (rm/unlink/shred/truncate)';
  if (has(c, /(^|[|;&]|\s)(mv|cp|ln|install)\b/)) return 'moves/copies files (mv/cp/ln/install)';
  if (has(c, /(^|[|;&]|\s)(touch|mkdir)\b/)) return 'creates files/dirs (touch/mkdir)';
  if (has(c, /\b(sed|perl|gsed)\b[^|>]*\s-(?:[a-wyz]*i[a-wyz]*)\b/)) return 'in-place edit (sed/perl -i)';
  if (has(c, /(^|[|;&]|\s)(tee|dd)\b/)) return 'writes files (tee/dd)';
  if (has(c, /\s--(write|fix|in-place)\b/)) return 'formatter/fixer in write mode (--write/--fix/--in-place)';
  if (has(c, />>?/)) return 'redirects output to a file (>, >>)';
  return null;
}

// ----------------------------------------------------------------------------
// DANGER detectors (blocked for EVERY role, including the primary session)
// ----------------------------------------------------------------------------
function dangerReason(cmd) {
  const c = cmd;
  if (has(c, /\b(curl|wget|fetch)\b[^|]*\|\s*(sudo\s+)?(sh|bash|zsh|python3?|node|ruby|perl)\b/)) return 'pipes remote content into a shell (curl|wget … | sh)';
  if (has(c, /(^|[|;&]|\s)(sudo|su|doas)\b/)) return 'privilege escalation (sudo/su/doas)';
  if (has(c, /\bgit\s+config\b[^\n]*\s(--global|--system)\b/)) return 'modifies global/system git config';
  if (has(c, /(^|[|;&]|\s)(rm|mv|cp|dd|chmod|chown|tee)\b[^\n]*\s\/(etc|usr|bin|sbin|var|System|Library)(\/|\s|$)/)) return 'writes to system directories';
  if (has(c, />\s*\/(etc|dev\/sd|dev\/disk|dev\/nvme|System)/)) return 'writes to a system/device path';
  const rmRecursive = /\brm\b[^\n]*\s-\S*[rf]/.test(c);
  if (rmRecursive && has(c, /(\s|=)(\/(\s|$|\*)|~(\/|\s|$)|\$HOME\b|\/\*(\s|$)|\.\.(\/|\s|$))/)) return 'recursive delete of root/home/parent path';
  if (rmRecursive && has(c, /\s\/(etc|usr|bin|var|Users|home|System|Library)(\/|\s|$)/)) return 'recursive delete of a system/user directory';
  if (has(c, /\brm\b[^\n]*(\.git(\/|\s|$)|\$CLAUDE_PROJECT_DIR\b)/)) return 'deletes the repository (.git)';
  if (has(c, /\b(mkfs|fdisk|:\(\)\s*\{)/)) return 'destructive/system command (mkfs/fork-bomb)';
  if (has(c, /\bgit\s+push\b[^\n]*(--force\b|--force-with-lease\b|\s-f\b)/)) return 'force push';
  if (has(c, /\bgit\s+push\b[^\n]*\s\+[\w./-]+:/)) return 'force push (refspec +)';
  if (has(c, /\bgit\s+filter-branch\b/)) return 'history rewrite (filter-branch)';
  if (has(c, /\bgit\s+(reset\s+--hard|rebase|commit\s+--amend|branch\s+-[MmfCc]|update-ref)\b[^\n]*\b(main|master|origin\/(main|master))\b/)) return 'rewrites main/master history';
  if (has(c, /\b(cat|less|more|head|tail|xxd|base64|strings|nl|od)\b[^|\n]*(\.env\b|\.pem\b|id_rsa\b|id_ed25519\b|\.ssh\/|\.aws\/credentials|\.netrc\b|\.git-credentials\b|secrets?\b|credentials?\b)/i)) return 'reads secret/credential files';
  if (has(c, /\b(env|printenv|set)\b[^\n]*\|\s*(curl|wget|nc|ncat|telnet)\b/)) return 'exfiltrates environment to the network';
  if (has(c, /\b(curl|wget|nc|ncat)\b[^\n]*(\$\(|`|\bcat\b)[^\n]*(\.env|id_rsa|\.ssh\/|credentials|secret|TOKEN|SECRET|PASSWORD|API[_-]?KEY)/i)) return 'exfiltrates secrets over the network';
  return null;
}

// ----------------------------------------------------------------------------
// Pure decision function
// ----------------------------------------------------------------------------
export function evaluate(role, command) {
  const cmd = String(command || '').trim();
  if (!cmd) return { decision: 'allow', role };
  const blocked = ROLE_POLICY[role] || ROLE_POLICY.default;

  const danger = dangerReason(cmd);
  if (danger) return { decision: 'block', category: 'DANGER', role, reason: `blocked (danger): ${danger}` };

  for (const seg of segments(cmd)) {
    if (blocked.includes('FILE')) {
      const fm = fileMutation(seg);
      if (fm) return { decision: 'block', category: 'FILE', role, reason: `blocked for '${role}' (no file mutation): ${fm}` };
    }
    if (blocked.includes('GIT') && gitIsMutating(seg)) return { decision: 'block', category: 'GIT', role, reason: `blocked for '${role}' (no git state change)` };
    if (blocked.includes('GH') && ghIsMutating(seg)) return { decision: 'block', category: 'GH', role, reason: `blocked for '${role}' (no GitHub state change)` };
  }
  return { decision: 'allow', role };
}

// ----------------------------------------------------------------------------
// Role resolution: prefer explicit --role, then env, then the PreToolUse payload
// (`agent_type` is the documented field; others are accepted defensively).
// ----------------------------------------------------------------------------
export function resolveRole({ argv = [], env = {}, payload = {} } = {}) {
  const flagIdx = argv.indexOf('--role');
  if (flagIdx !== -1 && argv[flagIdx + 1]) return argv[flagIdx + 1];
  if (env.CLAUDE_AGENT_ROLE) return env.CLAUDE_AGENT_ROLE;
  const p = payload || {};
  const c = p.agent_type || p.agentType || p.agent || p.agent_name || p.agentName || p.subagent_type || p.subagentType || p.subagent;
  return c || 'default';
}

// ----------------------------------------------------------------------------
// CLI: read PreToolUse JSON from stdin, decide, block via exit 2 if needed.
// ----------------------------------------------------------------------------
function isMain() {
  try { return import.meta.url === `file://${process.argv[1]}`; } catch { return false; }
}
if (isMain()) {
  let input = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (c) => (input += c));
  process.stdin.on('end', () => {
    let payload = {};
    try { payload = input ? JSON.parse(input) : {}; } catch { payload = {}; }
    const toolName = payload.tool_name || payload.toolName;
    const role0 = resolveRole({ argv: process.argv.slice(2), env: process.env, payload });
    // File-ish tools are gated for QUARANTINE only (Issue #20). Bash falls through to the
    // full mutation policy below, which also applies the quarantine.
    const FILE_TOOLS = new Set(['Read', 'Grep', 'Glob', 'Edit', 'Write', 'MultiEdit', 'NotebookEdit']);
    if (toolName && FILE_TOOLS.has(toolName)) {
      const q = evaluateFileAccess(role0, payload.tool_input || {});
      if (q.decision === 'block') {
        process.stderr.write(`[4UR4 quarantine] ${q.reason}\n`);
        process.exit(2);
      }
      process.exit(0);
    }
    if (toolName && toolName !== 'Bash') process.exit(0);   // only gate Bash
    const command = (payload.tool_input && (payload.tool_input.command ?? payload.tool_input.cmd)) || payload.command || '';
    const role = resolveRole({ argv: process.argv.slice(2), env: process.env, payload });
    const q = quarantineBlock(role, command);
    if (q) {
      process.stderr.write(`[4UR4 quarantine] ${q.reason}\n`);
      process.exit(2);
    }
    const result = evaluate(role, command);
    if (result.decision === 'block') {
      process.stderr.write(`[4UR4 bash-guard] ${result.reason}\n`);
      process.exit(2);   // exit 2 = block; stderr is returned to the model
    }
    process.exit(0);
  });
}
