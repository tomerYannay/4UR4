#!/usr/bin/env node
// 4UR4 Agent Operating System — structural & governance validator.
// No dependencies. Exit code 0 = PASS, 1 = FAIL. Safe to run in CI.
//
// Checks: agent-count ceiling, unique ids, required frontmatter + body sections,
// valid agent classes, handoff integrity, governance cross-references,
// single-owner capabilities (separation of duties), and the build-freeze state.

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
const warns = [];
const err = (m) => errors.push(m);
const warn = (m) => warns.push(m);

// ---- config -----------------------------------------------------------------
const MAX_PERMANENT_AGENTS = 9;
const AGENT_CLASSES = ['deterministic', 'bounded-creative', 'mixed'];
const AGENT_STATUSES = ['permanent', 'experimental'];
const AGENT_REQUIRED_KEYS = [
  'id', 'name', 'class', 'status', 'version', 'mission',
  'allowed_tools', 'forbidden_actions', 'inputs', 'outputs',
  'handoff_from', 'handoff_to', 'bindings',
];
const AGENT_REQUIRED_SECTIONS = [
  '## Mission', '## Responsibilities', '## Allowed Tools', '## Forbidden Actions',
  '## Expected Inputs', '## Mandatory Outputs', '## Handoffs', '## Governance Bindings',
];
const LIST_KEYS = new Set([
  'allowed_tools', 'forbidden_actions', 'inputs', 'outputs',
  'handoff_from', 'handoff_to', 'bindings',
]);
// Capabilities that must belong to exactly ONE agent (GOV-011).
const SINGLE_OWNER_TOOLS = {
  roadmap_write: 'product-steward',
  ideas_write_inbox: 'product-innovation',
  write_code: 'implementation-engineer',
  github_pr_merge: 'release-ops',
};
const PSEUDO_AGENTS = new Set(['human']);
// Directories that would indicate product implementation under freeze (GOV-015).
const PRODUCT_CODE_DIRS = ['src', 'lib', 'app', 'server', 'client', 'packages'];

// ---- tiny frontmatter parser (YAML subset: scalars + inline flow lists) -----
function parseFrontmatter(text, file) {
  if (!text.startsWith('---')) { err(`${file}: missing frontmatter`); return { fm: {}, body: text }; }
  const end = text.indexOf('\n---', 3);
  if (end === -1) { err(`${file}: unterminated frontmatter`); return { fm: {}, body: text }; }
  const raw = text.slice(3, end).trim();
  const body = text.slice(text.indexOf('\n', end + 1) + 1);
  const fm = {};
  for (const line of raw.split('\n')) {
    if (!line.trim() || line.trimStart().startsWith('#')) continue;
    const i = line.indexOf(':');
    if (i === -1) continue;
    const key = line.slice(0, i).trim();
    let val = line.slice(i + 1).trim();
    if (val.startsWith('[') && val.endsWith(']')) {
      val = val.slice(1, -1).split(',').map((s) => unquote(s.trim())).filter(Boolean);
    } else {
      val = unquote(val);
    }
    fm[key] = val;
  }
  return { fm, body };
}
const unquote = (s) => s.replace(/^["']|["']$/g, '');

function readDirMd(dir) {
  const p = join(ROOT, dir);
  if (!existsSync(p)) { err(`missing directory: ${dir}/`); return []; }
  return readdirSync(p).filter((f) => f.endsWith('.md')).sort()
    .map((f) => ({ file: `${dir}/${f}`, text: readFileSync(join(p, f), 'utf8') }));
}

// ---- load governance --------------------------------------------------------
const govFiles = readDirMd('governance');
const govIds = new Set();
for (const { file, text } of govFiles) {
  const { fm } = parseFrontmatter(text, file);
  if (!fm.id) { err(`${file}: governance file missing 'id'`); continue; }
  if (!/^GOV-\d{3}$/.test(fm.id)) err(`${file}: bad rule id '${fm.id}' (want GOV-###)`);
  govIds.add(fm.id);
  const extra = fm.also_defines
    ? (Array.isArray(fm.also_defines) ? fm.also_defines : [fm.also_defines])
    : [];
  for (const e of extra) govIds.add(unquote(e).replace(/[[\]]/g, ''));
}

// registry (GOVERNANCE.md) must list exactly the discovered rules
const govRegistry = readFileSync(join(ROOT, 'GOVERNANCE.md'), 'utf8');
const registryIds = new Set((govRegistry.match(/GOV-\d{3}/g) || []));
for (const id of govIds) if (!registryIds.has(id)) err(`GOVERNANCE.md: rule ${id} defined in governance/ but not listed in registry`);
for (const id of registryIds) if (!govIds.has(id)) err(`GOVERNANCE.md: registry lists ${id} but no governance/ file defines it`);

// ---- load agents ------------------------------------------------------------
const agentFiles = readDirMd('agents');
const agents = [];
for (const { file, text } of agentFiles) {
  const { fm, body } = parseFrontmatter(text, file);
  for (const k of AGENT_REQUIRED_KEYS) {
    if (fm[k] === undefined || fm[k] === '' || (LIST_KEYS.has(k) && (!Array.isArray(fm[k]) || fm[k].length === 0))) {
      err(`${file}: missing/empty required field '${k}'`);
    }
  }
  if (fm.class && !AGENT_CLASSES.includes(fm.class)) err(`${file}: invalid class '${fm.class}'`);
  if (fm.status && !AGENT_STATUSES.includes(fm.status)) err(`${file}: invalid status '${fm.status}'`);
  if (fm.version && !/^\d+\.\d+\.\d+$/.test(fm.version)) err(`${file}: version '${fm.version}' not semver`);
  for (const s of AGENT_REQUIRED_SECTIONS) if (!body.includes(s)) err(`${file}: missing body section '${s}'`);
  for (const b of (fm.bindings || [])) if (!govIds.has(b)) err(`${file}: binding '${b}' is not a defined governance rule`);
  agents.push({ file, fm });
}

const permanent = agents.filter((a) => a.fm.status === 'permanent');
const ids = new Set();
for (const a of agents) {
  if (ids.has(a.fm.id)) err(`duplicate agent id '${a.fm.id}'`);
  ids.add(a.fm.id);
}

// count ceiling
if (permanent.length > MAX_PERMANENT_AGENTS) {
  err(`too many permanent agents: ${permanent.length} > ${MAX_PERMANENT_AGENTS}`);
}

// handoff integrity
const knownTargets = new Set([...ids, ...PSEUDO_AGENTS]);
for (const a of agents) {
  for (const t of [...(a.fm.handoff_to || []), ...(a.fm.handoff_from || [])]) {
    if (!knownTargets.has(t)) err(`${a.file}: handoff references unknown agent '${t}'`);
  }
}

// single-owner capabilities (separation of duties, GOV-011)
for (const [tool, owner] of Object.entries(SINGLE_OWNER_TOOLS)) {
  const holders = agents.filter((a) => (a.fm.allowed_tools || []).includes(tool)).map((a) => a.fm.id);
  if (holders.length === 0) warn(`no agent holds single-owner capability '${tool}'`);
  else if (holders.length > 1) err(`capability '${tool}' held by multiple agents [${holders}] — violates GOV-011`);
  else if (holders[0] !== owner) err(`capability '${tool}' held by '${holders[0]}', expected '${owner}'`);
}

// unique missions (non-overlap heuristic)
const missions = new Map();
for (const a of agents) {
  const m = (a.fm.mission || '').toLowerCase();
  if (missions.has(m)) err(`${a.file}: duplicate mission shared with '${missions.get(m)}'`);
  else missions.set(m, a.fm.id);
}

// ---- build-freeze -----------------------------------------------------------
const freezeFile = join(ROOT, 'governance/build-freeze.md');
if (existsSync(freezeFile)) {
  const t = readFileSync(freezeFile, 'utf8');
  if (!/build_freeze:\s*ON/.test(t)) err('build-freeze.md: expected machine-readable marker `build_freeze: ON`');
  else {
    for (const d of PRODUCT_CODE_DIRS) {
      if (existsSync(join(ROOT, d))) err(`build-freeze is ON but product-code directory '${d}/' exists (GOV-015)`);
    }
  }
} else err('missing governance/build-freeze.md');

// ---- report -----------------------------------------------------------------
const classCounts = AGENT_CLASSES.map((c) => `${c}: ${agents.filter((a) => a.fm.class === c).length}`).join(', ');
console.log('4UR4 Agent OS — validation');
console.log('─'.repeat(52));
console.log(`Agents:      ${agents.length} (permanent ${permanent.length}/${MAX_PERMANENT_AGENTS})`);
console.log(`Classes:     ${classCounts}`);
console.log(`Gov rules:   ${govIds.size} defined, ${registryIds.size} in registry`);
console.log(`Build-freeze: ON (autonomous implementation disabled)`);
console.log('─'.repeat(52));
for (const w of warns) console.log(`  ⚠︎  ${w}`);
if (errors.length === 0) {
  console.log(`\n✅ PASS — ${agents.length} agents, ${govIds.size} rules, 0 errors${warns.length ? `, ${warns.length} warning(s)` : ''}.`);
  process.exit(0);
} else {
  for (const e of errors) console.log(`  ✗  ${e}`);
  console.log(`\n❌ FAIL — ${errors.length} error(s).`);
  process.exit(1);
}
