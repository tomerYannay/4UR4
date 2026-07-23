#!/usr/bin/env node
// 4UR4 Agent Operating System — structural & governance validator.
// No dependencies. Exit code 0 = PASS, 1 = FAIL. Safe to run in CI.
//
// Enforces both the GOVERNANCE model and Claude Code EXECUTABILITY:
//   - canonical executable agents live under .claude/agents/ (single source of truth)
//   - each agent has valid Claude Code frontmatter (name, description, real tools, ...)
//   - governance metadata lives in a machine-readable body block (not custom frontmatter)
//   - permanent-agent ceiling (<= 9), separation of duties, handoff integrity
//   - deterministic + innovation agents cannot write (no Write/Edit tools)
//   - temporary specialist governance (GOV-016), build-freeze, and CI workflow exist

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
const warns = [];
const err = (m) => errors.push(m);
const warn = (m) => warns.push(m);

// ---- config -----------------------------------------------------------------
const AGENTS_DIR = '.claude/agents';                 // canonical, executable
const LEGACY_DIR = 'agents';                         // must NOT hold agent copies
const CI_WORKFLOW = '.github/workflows/governance-validation.yml';
const SPECIALIST_GOV = 'governance/temporary-specialists.md';
const SETTINGS = '.claude/settings.json';
const HOOK_SCRIPT = '.claude/hooks/bash-guard.mjs';
const HOOK_TESTS = '.claude/hooks/bash-guard.test.mjs';
const MAX_PERMANENT_AGENTS = 9;

// Real Claude Code subagent frontmatter fields (source: code.claude.com/docs/en/sub-agents).
const VALID_FM_FIELDS = new Set([
  'name', 'description', 'tools', 'disallowedTools', 'model', 'permissionMode',
  'maxTurns', 'skills', 'mcpServers', 'hooks', 'memory', 'background', 'effort',
  'isolation', 'color', 'initialPrompt',
]);
const REQUIRED_FM_FIELDS = ['name', 'description'];
// Real Claude Code tool identifiers usable in tools/disallowedTools.
const VALID_TOOLS = new Set([
  'Read', 'Write', 'Edit', 'Bash', 'PowerShell', 'Grep', 'Glob', 'WebFetch',
  'WebSearch', 'NotebookEdit', 'TodoWrite', 'Skill', 'ToolSearch', 'Agent',
  'EnterWorktree', 'ExitWorktree', 'Monitor', 'TaskStop', 'SendMessage', 'Artifact',
]);
const WRITE_TOOLS = ['Write', 'Edit', 'NotebookEdit'];
const MODEL_ALIASES = new Set(['sonnet', 'opus', 'haiku', 'fable', 'inherit']);
const PERMISSION_MODES = new Set(['default', 'acceptEdits', 'auto', 'dontAsk', 'bypassPermissions', 'plan', 'manual']);

const GOV_REQUIRED = ['id', 'class', 'status', 'version', 'authority', 'inputs', 'outputs', 'handoff_from', 'handoff_to', 'bindings'];
const AGENT_CLASSES = ['deterministic', 'bounded-creative', 'mixed'];
const AGENT_STATUSES = ['permanent', 'temporary'];
const NO_WRITE_CLASSES = new Set(['deterministic']);       // + product-innovation by id
const RESERVED_PERMANENT_AUTHORITIES = new Set(['merge-and-release', 'evidence-verdict']);
const PSEUDO_AGENTS = new Set(['human']);
const PRODUCT_CODE_DIRS = ['src', 'lib', 'app', 'server', 'client', 'packages'];

// ---- parsing helpers --------------------------------------------------------
const unquote = (s) => s.replace(/^["']|["']$/g, '');
function parseKeyVals(raw) {
  const obj = {};
  for (const line of raw.split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const i = line.indexOf(':');
    if (i === -1) continue;
    const key = line.slice(0, i).trim();
    let val = line.slice(i + 1).trim();
    if (val.startsWith('[') && val.endsWith(']')) {
      val = val.slice(1, -1).split(',').map((s) => unquote(s.trim())).filter(Boolean);
    } else {
      val = unquote(val);
    }
    obj[key] = val;
  }
  return obj;
}
const asList = (v) => (Array.isArray(v) ? v : (typeof v === 'string' && v ? v.split(',').map((s) => s.trim()).filter(Boolean) : []));

function splitFrontmatter(text, file) {
  if (!text.startsWith('---')) { err(`${file}: missing frontmatter`); return { fmRaw: '', body: text }; }
  const end = text.indexOf('\n---', 3);
  if (end === -1) { err(`${file}: unterminated frontmatter`); return { fmRaw: '', body: text }; }
  return { fmRaw: text.slice(3, end).trim(), body: text.slice(text.indexOf('\n', end + 1) + 1) };
}
function extractGovBlock(body, file) {
  const start = body.indexOf('<!-- 4ur4:governance');
  if (start === -1) { err(`${file}: missing '<!-- 4ur4:governance ... -->' metadata block`); return ''; }
  const end = body.indexOf('-->', start);
  if (end === -1) { err(`${file}: unterminated governance block`); return ''; }
  return body.slice(start + '<!-- 4ur4:governance'.length, end);
}
function readDirMd(dir) {
  const p = join(ROOT, dir);
  if (!existsSync(p)) { err(`missing directory: ${dir}/`); return []; }
  return readdirSync(p).filter((f) => f.endsWith('.md')).sort()
    .map((f) => ({ file: `${dir}/${f}`, text: readFileSync(join(p, f), 'utf8') }));
}

// ---- governance rules -------------------------------------------------------
const govFiles = readDirMd('governance');
const govIds = new Set();
for (const { file, text } of govFiles) {
  const { fmRaw } = splitFrontmatter(text, file);
  const fm = parseKeyVals(fmRaw);
  if (!fm.id) { err(`${file}: governance file missing 'id'`); continue; }
  if (!/^GOV-\d{3}$/.test(fm.id)) err(`${file}: bad rule id '${fm.id}'`);
  govIds.add(fm.id);
  for (const e of asList(fm.also_defines)) govIds.add(unquote(e).replace(/[[\]]/g, ''));
}
const govRegistry = readFileSync(join(ROOT, 'GOVERNANCE.md'), 'utf8');
const registryIds = new Set(govRegistry.match(/GOV-\d{3}/g) || []);
for (const id of govIds) if (!registryIds.has(id)) err(`GOVERNANCE.md: ${id} defined but not in registry`);
for (const id of registryIds) if (!govIds.has(id)) err(`GOVERNANCE.md: registry lists ${id} but no file defines it`);

// ---- single source of truth -------------------------------------------------
if (existsSync(join(ROOT, LEGACY_DIR))) {
  const legacy = readdirSync(join(ROOT, LEGACY_DIR)).filter((f) => f.endsWith('.md'));
  if (legacy.length) err(`single-source-of-truth: legacy '${LEGACY_DIR}/' still holds agent files [${legacy}] — canonical dir is ${AGENTS_DIR}/`);
}
if (!existsSync(join(ROOT, AGENTS_DIR))) err(`missing canonical agents directory: ${AGENTS_DIR}/`);

// ---- agents -----------------------------------------------------------------
const agents = [];
for (const { file, text } of readDirMd(AGENTS_DIR)) {
  const { fmRaw, body } = splitFrontmatter(text, file);
  const fm = parseKeyVals(fmRaw);
  const gov = parseKeyVals(extractGovBlock(body, file));

  // frontmatter: only real CC fields, required present
  for (const k of Object.keys(fm)) if (!VALID_FM_FIELDS.has(k)) err(`${file}: unknown Claude Code frontmatter field '${k}' (put governance metadata in the 4ur4:governance body block)`);
  for (const k of REQUIRED_FM_FIELDS) if (!fm[k]) err(`${file}: missing required frontmatter field '${k}'`);
  if (fm.name && !/^[a-z][a-z0-9-]*$/.test(fm.name)) err(`${file}: name '${fm.name}' must be lowercase letters/hyphens`);

  // tools / disallowedTools: real identifiers only
  const tools = asList(fm.tools);
  const disallowed = asList(fm.disallowedTools);
  for (const t of tools) if (!VALID_TOOLS.has(t)) err(`${file}: invalid tool identifier in tools: '${t}'`);
  for (const t of disallowed) if (!VALID_TOOLS.has(t)) err(`${file}: invalid tool identifier in disallowedTools: '${t}'`);

  // model / permissionMode
  if (fm.model && !MODEL_ALIASES.has(fm.model) && !/^claude-/.test(fm.model)) err(`${file}: invalid model '${fm.model}'`);
  if (fm.permissionMode && !PERMISSION_MODES.has(fm.permissionMode)) err(`${file}: invalid permissionMode '${fm.permissionMode}'`);

  // governance block
  for (const k of GOV_REQUIRED) {
    const v = gov[k];
    if (v === undefined || v === '' || (['inputs', 'outputs', 'handoff_from', 'handoff_to', 'bindings'].includes(k) && (!Array.isArray(v) || !v.length))) {
      err(`${file}: governance block missing/empty '${k}'`);
    }
  }
  if (gov.class && !AGENT_CLASSES.includes(gov.class)) err(`${file}: invalid class '${gov.class}'`);
  if (gov.status && !AGENT_STATUSES.includes(gov.status)) err(`${file}: invalid status '${gov.status}'`);
  if (gov.version && !/^\d+\.\d+\.\d+$/.test(gov.version)) err(`${file}: version '${gov.version}' not semver`);
  if (fm.name && gov.id && fm.name !== gov.id) err(`${file}: frontmatter name '${fm.name}' != governance id '${gov.id}'`);
  for (const b of asList(gov.bindings)) if (!govIds.has(b)) err(`${file}: binding '${b}' is not a defined rule`);

  // write-restriction for deterministic + innovation
  const noWrite = NO_WRITE_CLASSES.has(gov.class) || gov.id === 'product-innovation';
  if (noWrite) for (const w of WRITE_TOOLS) if (tools.includes(w)) err(`${file}: ${gov.class} agent '${gov.id}' must not have write tool '${w}'`);

  // temporary specialist constraints (GOV-016)
  if (gov.status === 'temporary') {
    if (!gov.ticket) err(`${file}: temporary specialist missing 'ticket'`);
    if (!gov.parent_authority) err(`${file}: temporary specialist missing 'parent_authority'`);
    if (!asList(gov.bindings).includes('GOV-016')) err(`${file}: temporary specialist must bind GOV-016`);
    if (RESERVED_PERMANENT_AUTHORITIES.has(gov.authority)) err(`${file}: temporary specialist may not claim reserved authority '${gov.authority}'`);
  }

  agents.push({ file, fm, gov, tools, disallowed });
}

const permanent = agents.filter((a) => a.gov.status === 'permanent');
const temporary = agents.filter((a) => a.gov.status === 'temporary');

// unique names & ids
const seenNames = new Set();
for (const a of agents) {
  if (a.fm.name) { if (seenNames.has(a.fm.name)) err(`duplicate agent name '${a.fm.name}'`); seenNames.add(a.fm.name); }
}

// permanent ceiling
if (permanent.length > MAX_PERMANENT_AGENTS) err(`too many permanent agents: ${permanent.length} > ${MAX_PERMANENT_AGENTS}`);

// separation of duties: unique authority among permanent
const authSeen = new Map();
for (const a of permanent) {
  const au = a.gov.authority;
  if (authSeen.has(au)) err(`permanent authority '${au}' shared by '${a.gov.id}' and '${authSeen.get(au)}' — violates GOV-011`);
  else authSeen.set(au, a.gov.id);
}

// handoff & parent integrity
const knownIds = new Set([...agents.map((a) => a.gov.id), ...PSEUDO_AGENTS]);
const permIds = new Set(permanent.map((a) => a.gov.id));
for (const a of agents) {
  for (const t of [...asList(a.gov.handoff_from), ...asList(a.gov.handoff_to)]) if (!knownIds.has(t)) err(`${a.file}: handoff references unknown agent '${t}'`);
  if (a.gov.status === 'temporary' && a.gov.parent_authority && !permIds.has(a.gov.parent_authority)) err(`${a.file}: parent_authority '${a.gov.parent_authority}' is not a permanent agent`);
}

// ---- build-freeze -----------------------------------------------------------
const freezeFile = join(ROOT, 'governance/build-freeze.md');
let freezeOn = false;
if (existsSync(freezeFile)) {
  const t = readFileSync(freezeFile, 'utf8');
  if (!/build_freeze:\s*ON/.test(t)) err('build-freeze.md: expected `build_freeze: ON`');
  else { freezeOn = true; for (const d of PRODUCT_CODE_DIRS) if (existsSync(join(ROOT, d))) err(`build-freeze ON but product-code dir '${d}/' exists (GOV-015)`); }
} else err('missing governance/build-freeze.md');

// ---- required infrastructure ------------------------------------------------
if (!existsSync(join(ROOT, CI_WORKFLOW))) err(`missing CI workflow: ${CI_WORKFLOW}`);
if (!existsSync(join(ROOT, SPECIALIST_GOV))) err(`missing temporary-specialist governance: ${SPECIALIST_GOV}`);
if (!govIds.has('GOV-016')) err('GOV-016 (temporary specialists) is not defined');

// ---- Bash safety hook -------------------------------------------------------
let hookOk = false;
if (!existsSync(join(ROOT, HOOK_SCRIPT))) err(`missing Bash safety hook script: ${HOOK_SCRIPT}`);
if (!existsSync(join(ROOT, HOOK_TESTS))) err(`missing Bash safety hook tests: ${HOOK_TESTS}`);
if (!existsSync(join(ROOT, SETTINGS))) {
  err(`missing ${SETTINGS} (PreToolUse Bash hook must be configured)`);
} else {
  try {
    const s = JSON.parse(readFileSync(join(ROOT, SETTINGS), 'utf8'));
    const pre = s?.hooks?.PreToolUse || [];
    const bashHook = pre.find((h) => h.matcher === 'Bash' && (h.hooks || []).some((x) => /bash-guard\.mjs/.test(x.command || '')));
    if (!bashHook) err(`${SETTINGS}: no PreToolUse hook matching 'Bash' that runs bash-guard.mjs`);
    else hookOk = true;
  } catch (e) { err(`${SETTINGS}: invalid JSON (${e.message})`); }
}

// ---- report -----------------------------------------------------------------
const classCounts = AGENT_CLASSES.map((c) => `${c} ${permanent.filter((a) => a.gov.class === c).length}`).join(', ');
console.log('4UR4 Agent OS — validation');
console.log('─'.repeat(58));
console.log(`Canonical dir: ${AGENTS_DIR}/`);
console.log(`Agents:        ${permanent.length} permanent (/${MAX_PERMANENT_AGENTS}), ${temporary.length} temporary`);
console.log(`Classes:       ${classCounts}`);
console.log(`Gov rules:     ${govIds.size} defined, ${registryIds.size} in registry`);
console.log(`Build-freeze:  ${freezeOn ? 'ON (autonomous implementation disabled)' : 'UNKNOWN'}`);
console.log(`CI workflow:   ${existsSync(join(ROOT, CI_WORKFLOW)) ? 'present' : 'MISSING'}`);
console.log(`Bash hook:     ${hookOk ? 'configured (PreToolUse → bash-guard.mjs)' : 'MISSING/INVALID'}`);
console.log('─'.repeat(58));
for (const w of warns) console.log(`  ⚠︎  ${w}`);
if (errors.length === 0) {
  console.log(`\n✅ PASS — ${permanent.length} permanent agents, ${govIds.size} rules, 0 errors${warns.length ? `, ${warns.length} warning(s)` : ''}.`);
  process.exit(0);
} else {
  for (const e of errors) console.log(`  ✗  ${e}`);
  console.log(`\n❌ FAIL — ${errors.length} error(s).`);
  process.exit(1);
}
