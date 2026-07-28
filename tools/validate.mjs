#!/usr/bin/env node
// 4UR4 Agent Operating System — structural & governance validator.
// No dependencies. Exit code 0 = PASS, 1 = FAIL. Safe to run in CI.
//
// Enforces both the GOVERNANCE model and Claude Code EXECUTABILITY:
//   - canonical executable agents live under .claude/agents/ (single source of truth)
//   - each agent has valid Claude Code frontmatter (name, description, real tools, ...)
//   - governance metadata lives in a machine-readable body block (not custom frontmatter)
//   - permanent-agent ceiling (<= 10), separation of duties, handoff integrity
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
const MAX_PERMANENT_AGENTS = 10;

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
// Every directory the freeze is meant to forbid must be NAMED here — the check is a name
// list, not a heuristic, so an unlisted directory is unguarded no matter what the prose says.
// The second row is drawn from the surfaces build-freeze.md's own NOT-authorized list names.
const PRODUCT_CODE_DIRS = [
  'src', 'lib', 'app', 'server', 'client', 'packages', 'engine',
  'api', 'services', 'scanner', 'worker', 'dashboard', 'web', 'backend', 'frontend', 'db',
  'alerts', 'billing', 'providers',
];
// INVARIANT: this list and the enumeration in governance/build-freeze.md's scoped-lift
// section must agree. The reason is a real over-claim, stated accurately: 685b65a's prose
// said the list "was extended to cover the surfaces the NOT-authorized list above names"
// while `alerts`, `billing` and provider integration were named as forbidden and left
// unguarded. (An earlier version of this comment said the two LISTS had drifted in that
// commit. They had not — both held the same 16 names; the divergence existed only in an
// uncommitted working tree. The over-claim was real, the drift framing was not.)
// The parity check below makes any future divergence a build failure, not a discovery.

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
let freezeScope = [];
if (existsSync(freezeFile)) {
  const t = readFileSync(freezeFile, 'utf8');
  // Parse the MACHINE-READABLE MARKER ONLY. Scanning the whole file let PROSE satisfy the
  // gate: the Enforcement paragraph contains the literal string "build_freeze: ON", so
  // flipping the marker to OFF still passed. The most-cited control in the repository was
  // therefore never actually enforced. Anchoring to the fenced block fixes that, and fixes
  // the same class of hole in the `scope:` parse below, which previously took the first
  // line-initial `scope:` anywhere in the file.
  const markers = [...t.matchAll(/##[ \t]*Freeze marker[^\r\n]*(?:\r?\n)+```ya?ml\r?\n([\s\S]*?)```/g)];
  // Exactly one marker, or none of this means anything. First-wins would let an
  // illustrative block placed ABOVE the real one shadow it, which fails OPEN.
  let marker = null;   // assigned only on the single-valid-marker path below
  if (markers.length === 0) {
    err('build-freeze.md: no machine-readable freeze marker block found'
      + ' (expected a ```yaml fence under a `## Freeze marker` heading)');
  } else if (markers.length > 1) {
    err(`build-freeze.md: ${markers.length} freeze marker blocks found, expected exactly 1 —`
      + ` a duplicate block would shadow the real marker`);
  } else if (!/^build_freeze:\s*ON\s*$/m.test(markers[0][1])) {
    err('build-freeze.md: expected `build_freeze: ON` in the freeze marker block');
  } else {
    marker = markers[0][1];
    freezeOn = true;
    // A scoped lift is only a scope if it is enumerated. `scope:` in the freeze marker
    // names the product-code directories the Product Owner has authorized; every other
    // guarded directory still fails. Deleting an entry re-freezes that directory on the
    // next CI run, which is what makes the boundary mechanical rather than declaratory.
    const scopeLine = (marker.match(/^\s*scope:\s*(.+)$/m) || [])[1] || 'null';
    freezeScope = [...scopeLine.matchAll(/["']([^"']+)["']/g)].map((m) => m[1].replace(/\/+$/, ''));
    for (const d of PRODUCT_CODE_DIRS) {
      if (!existsSync(join(ROOT, d))) continue;
      if (freezeScope.includes(d)) continue;   // authorized by the recorded lift
      err(`build-freeze ON but product-code dir '${d}/' exists and is not in the recorded`
        + ` lift scope [${freezeScope.join(', ') || 'none'}] (GOV-015)`);
    }
  }
} else err('missing governance/build-freeze.md');

// ---- agent / ROLE_POLICY parity ---------------------------------------------
// Every permanent agent must appear in bash-guard's ROLE_POLICY. This is not tidiness:
// AC-4 makes an UNKNOWN role inherit the implementation-engineer quarantine, so an agent
// missing from that table is SILENTLY DENIED the quarantined paths. It happened to
// strategic-product-reviewer, which was thereby denied the very document it is asked to
// rule on. A register nobody asserts against reality drifts; this makes the drift fail CI.
try {
  const guardSrc = readFileSync(join(ROOT, '.claude/hooks/bash-guard.mjs'), 'utf8');
  const policyBlock = (guardSrc.match(/ROLE_POLICY\s*=\s*\{([\s\S]*?)\n\};/) || [])[1] || '';
  if (!policyBlock) {
    err('bash-guard.mjs: ROLE_POLICY block not found — agent/role parity cannot be checked');
  } else {
    const mapped = new Set([...policyBlock.matchAll(/^\s*'?([a-z][a-z0-9-]*)'?\s*:/gm)].map((m) => m[1]));
    const unmapped = agents.filter((a) => a.gov && a.gov.status === 'permanent' && !mapped.has(a.gov.id))
      .map((a) => a.gov.id);
    if (unmapped.length) {
      err(`bash-guard ROLE_POLICY is missing permanent agent(s): ${unmapped.join(', ')}.`
        + ` Unmapped roles inherit the E2-AUTHOR quarantine (AC-4) and are silently denied.`);
    }
  }
} catch (e) {
  err(`agent/ROLE_POLICY parity check could not run: ${e.message}`);
}

// ---- freeze-list parity -----------------------------------------------------
// The prose list in build-freeze.md and PRODUCT_CODE_DIRS are two statements of one fact,
// and two statements of one fact drift. This makes the drift a build failure rather than
// something a reviewer has to notice.
if (existsSync(freezeFile)) {
  const ft = readFileSync(freezeFile, 'utf8');
  // Anchored on an explicit marker comment, not on prose wording, and CRLF-tolerant.
  // The first version keyed on a sentence and was gated behind `if (sec)`, so renaming
  // the paragraph — or checking out with CRLF — made the check SILENTLY DISAPPEAR. A
  // drift detector that vanishes when its anchor moves is the failure it exists to catch,
  // so a missing anchor is now an error rather than a skip.
  const sec = (ft.match(/<!-- GUARDED-DIRS-LIST[\s\S]*?-->([\s\S]*?)<!--\s*\/GUARDED-DIRS-LIST\s*-->/) || [])[1];
  if (sec === undefined) {
    err('build-freeze.md: GUARDED-DIRS-LIST markers not found — the prose/code parity check'
      + ' cannot run, so the guarded-directory list is unverified');
  } else {
    const named = [...sec.matchAll(/`([a-z]+)`/g)].map((m) => m[1]);
    const codeOnly = PRODUCT_CODE_DIRS.filter((d) => !named.includes(d));
    const proseOnly = named.filter((d) => !PRODUCT_CODE_DIRS.includes(d));
    if (codeOnly.length || proseOnly.length) {
      err('build-freeze.md prose and PRODUCT_CODE_DIRS disagree on guarded directories —'
        + (proseOnly.length ? ` prose names but code does not guard: ${proseOnly.join(', ')}.` : '')
        + (codeOnly.length ? ` code guards but prose does not name: ${codeOnly.join(', ')}.` : ''));
    }
  }
}

// ---- required infrastructure ------------------------------------------------
if (!existsSync(join(ROOT, CI_WORKFLOW))) err(`missing CI workflow: ${CI_WORKFLOW}`);
else {
  // The workflow's PRESENCE was asserted; its CONTENT was not. That gap let a step be
  // deleted silently: a commit rewriting the fixture-immutability guard spliced on the next
  // step's header as its end boundary and swallowed `actions/setup-node@v4`, on which four
  // of the five required checks run. CI stayed green, because the runner's default Node was
  // adequate -- which is precisely the failure mode the pinning exists to prevent.
  //
  // HONEST LIMIT, stated because the alternative is a control that overstates itself:
  // this check lives in the same repository as the workflow, so a single PR can delete the
  // step AND this assertion together. It does not make the gate tamper-proof. What it does
  // is convert a SILENT one-hunk deletion into a deliberate two-file edit that shows up in
  // the diff as an assertion being removed. Real closure is a required reviewer or a second
  // identity (#21, #34, HD-22 part 3), neither of which exists yet.
  // Needles are matched against WHOLE TRIMMED LINES, not as free substrings.
  //
  // This check has now been wrong three times in the same shape, and each fix closed the
  // instance while leaving the class open:
  //   1. whole-file scan       -- `--no-renames` was already in two comments: dead on arrival;
  //   2. full command pinned   -- but `-- product/fixtures/` is a SUBSTRING of
  //                               `-- product/fixtures/schema/`, so the pathspec could be
  //                               narrowed to a subdirectory and still pass;
  //   3. full-line comments stripped -- but only lines STARTING with `#`. A TRAILING comment
  //                               survived, so `uses: actions/setup-python@v5  # engine.tests.run_all`
  //                               satisfied the engine-suite needle while the suite was deleted.
  // Each of (2) and (3) was introduced by the commit that announced the previous one fixed.
  //
  // Whole-line equality ends the SUBSTRING class -- a trailing comment, an appended
  // `&& false`, or any other suffix changes the line and fails the match -- and that is ALL
  // it ends. The CARRIER class survives, measured: neuter the guard's failure path to
  // `exit 0` and put a bare `exit 1` line in any other step's `run:` block, and this check
  // passes. `exit 1` is the weakest needle for exactly that reason. Defeating it now takes
  // deliberate evasion rather than good-faith prose, which is a real improvement and is not
  // the same thing as closure.
  //
  // WHAT THIS STILL DOES NOT DO -- stated because the last three attempts overclaimed:
  // it pins the presence of exact lines, NOT the behaviour of the step. Adding a line
  // (`changed=""` after the diff) leaves every pinned line intact and the guard inert. So
  // does inverting the TRIGGER test (`-z`->`-n` on the engine/ diff), which early-exits 0
  // exactly when engine/ changed. Inverting the BLOCKING test is different and must not be
  // described the same way: it lets the attacking PR through but hard-fails every engine PR
  // with a clean fixture tree, so it is loud, not inert. `continue-on-error` is forbidden below as a YAML KEY IN ANY
  // SPELLINGS ENUMERATED AND TESTED BELOW -- and NOT in any spelling, which is a claim no
  // line-anchored regex can support over YAML. Caught, each measured: bare, "double-quoted",
  // 'single-quoted', space-before-colon, and DASH-LED (`- continue-on-error: true`, the key
  // leading a step). That last one is ordinary Actions YAML -- every step here happens to be
  // written `- name:`, so leading with this key instead is idiomatic, not exotic -- and it
  // evaded the previous regex while leaving the engine suite's pinned `run:` line intact,
  // making the 136-test HD-22 exit gate advisory in one added line.
  //
  // NOT caught, and this list is the honest boundary rather than a to-do: flow-style step
  // mappings (`- {name: X, continue-on-error: true}`), the explicit-key indicator
  // (`? continue-on-error`), and escape sequences in double-quoted scalars
  // (`"continue-on-err\u006Fr"`). All resolve to the same key. Closing them requires PARSING
  // the workflow as YAML and testing the object graph; this repository carries no YAML parser
  // and adding one is an architectural change, not a fix. The structural point, which cost
  // several rounds to reach: widening the regex again while keeping absolute wording would be
  // wrong for the same reason it was wrong before. Either parse, or scope the claim. This
  // scopes the claim. The ban is here not because it is the cheapest neutering (a one-character `-z`->`-n` on the
  // trigger is cheaper) but because it is a whole-step off switch. The gap is real: M-39.

  const wfLines = readFileSync(join(ROOT, CI_WORKFLOW), 'utf8')
    .split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));
  const hasLine = (needle) => wfLines.includes(needle);

  const requiredLines = [
    ['uses: actions/setup-node@v4', 'the pinned Node toolchain four required checks run on'],
    ['uses: actions/setup-python@v5', 'the pinned Python the engine conformance suite runs on'],
    ['- name: Fixture immutability — a fixture may not be edited to make the engine pass',
     'the HD-22 fixture-immutability guard step'],
    ["if: github.event_name == 'pull_request'",
     "the fixture guard's trigger (`if: false`, or an appended `&& false`, neuters it silently)"],
    ['changed="$(git diff --no-renames --name-only --diff-filter=MDT "$merge_base" HEAD -- product/fixtures/)"',
     "the guard's rename/typechange fix AND its full pathspec"],
    ['exit 1', "the fixture guard's failure path (`exit 0` neuters it silently)"],
    ['run: python3 -m engine.tests.run_all', 'the Phase 2 engine conformance suite'],
  ];
  for (const [line, why] of requiredLines) {
    if (!hasLine(line)) err(`${CI_WORKFLOW} no longer contains the exact line \`${line}\` — ${why}`);
  }
  // Negative assertion: one line anywhere in this job makes any failing step non-fatal.
  // Matched as a YAML KEY in any spelling, not by string prefix. The first version was
  // `l.startsWith('continue-on-error')`, which a QUOTED key defeats -- `"continue-on-error":
  // true` trims to a line starting with `"`. Code Review's eleventh mutation, and the same
  // defect once more: the word in the record was "forbidden outright" while the code tested
  // one spelling. Widening the test is preferred over narrowing the claim here, because it
  // makes the sentence true regardless of how GitHub's YAML parser treats quoted keys --
  // which Code Review explicitly declined to assert, having no parser available to measure it.
  if (wfLines.some((l) => /^(-\s+)?["']?continue-on-error["']?\s*:/.test(l))) {
    err(`${CI_WORKFLOW}: \`continue-on-error\` makes a failing gate non-fatal — it has no legitimate use here`);
  }
}
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
console.log(`Build-freeze:  ${freezeOn
  ? (freezeScope.length
    ? `ON — lifted scope: ${freezeScope.map((d) => `${d}/`).join(', ')} (all other product dirs frozen)`
    : 'ON (autonomous implementation disabled)')
  : 'UNKNOWN'}`);
console.log(`CI workflow:   ${existsSync(join(ROOT, CI_WORKFLOW)) ? 'present, content asserted' : 'MISSING'}`);
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
