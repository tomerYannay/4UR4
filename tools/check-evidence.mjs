#!/usr/bin/env node
// 4UR4 — evidence validation: JSON Schema + documentation links.
//
// Phase-0 EVIDENCE TOOLING under the GOV-015 build-freeze (see tools/validate.mjs
// and tools/fixture-replay.mjs). Not product code: it reads repository artifacts
// and asserts they are internally consistent.
//
//   1. Every product/fixtures/golden/GX-*/expected.json validates against
//      product/fixtures/schema/fixture.schema.json, and the RM-01 annotation
//      against real-annotation.schema.json.
//   2. Every relative markdown link in the repository resolves — file AND #anchor.
//
// Usage: node tools/check-evidence.mjs   (exit 1 on any failure)
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

// ---------------------------------------------------------------- JSON schema
const errs = [];
function chk(inst, sch, path, id, sink = errs) {
  if (sch.type) {
    const types = Array.isArray(sch.type) ? sch.type : [sch.type];
    const t = inst === null ? 'null' : Array.isArray(inst) ? 'array'
      : typeof inst === 'number' ? (Number.isInteger(inst) ? 'integer' : 'number') : typeof inst;
    if (!types.some((x) => x === t || (x === 'number' && t === 'integer'))) {
      sink.push(`${id} ${path}: type ${t} not in ${types.join('|')}`); return;
    }
  }
  if (sch.const !== undefined && inst !== sch.const) sink.push(`${id} ${path}: const mismatch ${JSON.stringify(inst)}`);
  if (sch.enum && !sch.enum.includes(inst)) sink.push(`${id} ${path}: not in enum`);
  if (sch.pattern && typeof inst === 'string' && !new RegExp(sch.pattern).test(inst)) sink.push(`${id} ${path}: pattern`);
  if (sch.minimum !== undefined && inst < sch.minimum) sink.push(`${id} ${path}: < minimum`);
  if (sch.minItems !== undefined && Array.isArray(inst) && inst.length < sch.minItems) sink.push(`${id} ${path}: minItems`);
  if (Array.isArray(inst) && sch.items) inst.forEach((v, i) => chk(v, sch.items, `${path}[${i}]`, id, sink));
  if (inst && typeof inst === 'object' && !Array.isArray(inst)) {
    for (const r of sch.required || []) if (!(r in inst)) sink.push(`${id} ${path}: missing required ${r}`);
    for (const [k, v] of Object.entries(inst)) {
      const ps = (sch.properties || {})[k];
      if (ps) chk(v, ps, `${path}.${k}`, id, sink);
      // `$schema` is a JSON-Schema keyword, not instance data; RM-01 carries a
      // self-pointer that predates this check.
      else if (sch.additionalProperties === false && k !== '$schema') sink.push(`${id} ${path}: additional property ${k}`);
      else if (sch.additionalProperties && typeof sch.additionalProperties === 'object') chk(v, sch.additionalProperties, `${path}.${k}`, id, sink);
    }
  }
}
const schema = JSON.parse(readFileSync(join(ROOT, 'product/fixtures/schema/fixture.schema.json'), 'utf8'));
const ids = readdirSync(join(ROOT, 'product/fixtures/golden')).filter((d) => /^GX-\d\d$/.test(d)).sort();
for (const id of ids) chk(JSON.parse(readFileSync(join(ROOT, `product/fixtures/golden/${id}/expected.json`), 'utf8')), schema, '', id);

// RM-01 annotation against its own schema
const ras = JSON.parse(readFileSync(join(ROOT, 'product/fixtures/schema/real-annotation.schema.json'), 'utf8'));
chk(JSON.parse(readFileSync(join(ROOT, 'product/fixtures/real/RM-01/annotation.json'), 'utf8')), ras, '', 'RM-01');

// NEGATIVE CONTROL. A validator that silently regressed to a no-op would print PASS
// forever — exactly the failure mode this file exists to prevent, and the same reason
// tools/fixture-replay.mjs carries a positive control on its formation checks. Feed a
// known-bad instance through and require it to complain in each of the keyword
// classes listed in MUST_CATCH. `type` and `minimum` are the two schema keywords this
// instance does not trip — every field it carries is of the right type by
// construction, and nothing it carries has a numeric lower bound.
const control = [];
chk({
  fixture_id: 'BAD-1',                                        // fails `pattern`
  purpose: 'x', category: 'x', spec_refs: [],                 // fails `minItems`
  params: { tolerance_version: 'x', eps_break_locked: true }, // fails `const`
  expected_ath_anchor: null, expected_second_anchor: null,
  expected_state_transitions: [{ bar: 0, from: 'NOPE', to: 'ACTIVE', reason_code: 'MADE_UP' }],
  expected_reason_codes: [], rejection_rationale: [], geometry_check: {},
  not_a_real_field: 1,                                        // fails additionalProperties
}, schema, '', 'NEGATIVE-CONTROL', control);
const MUST_CATCH = ['pattern', 'const mismatch', 'not in enum', 'additional property', 'minItems', 'missing required'];
const missed = MUST_CATCH.filter((k) => !control.some((e) => e.includes(k)));
if (missed.length) {
  errs.push(`NEGATIVE CONTROL FAILED — validator did not detect: ${missed.join(', ')}`
    + ` (it reported: ${control.join(' | ') || 'nothing'})`);
} else {
  console.log(`negative control: PASS — a known-bad instance produced ${control.length} errors`
    + ` covering all ${MUST_CATCH.length} asserted keyword classes`);
}

console.log(errs.length ? `SCHEMA: ${errs.length} error(s)\n  ` + errs.join('\n  ')
  : `schema: PASS — ${ids.length} golden fixtures + RM-01 annotation validate`);

// ------------------------------------------------------- documentation links
const md = [];
(function walk(d) {
  for (const f of readdirSync(d)) {
    if (f === '.git' || f === 'node_modules') continue;
    const p = join(d, f);
    if (statSync(p).isDirectory()) walk(p);
    else if (f.endsWith('.md')) md.push(p);
  }
})(ROOT);

const broken = [];
const anchorsOf = (txt) => new Set(txt.split('\n').filter((l) => /^#{1,6}\s/.test(l))
  // GitHub slug rules: lowercase, drop non-word chars, each space -> one hyphen.
  .map((l) => l.replace(/^#{1,6}\s+/, '').toLowerCase()
    .replace(/[^\w\s-]/g, '').trim().replace(/ /g, '-')));
for (const f of md) {
  const txt = readFileSync(f, 'utf8');
  for (const m of txt.matchAll(/\[[^\]]*\]\(([^)\s]+)\)/g)) {
    let link = m[1];
    if (/^(https?:|mailto:|#)/.test(link)) continue;
    const [rel, anchor] = link.split('#');
    const target = resolve(dirname(f), rel);
    if (!existsSync(target)) { broken.push(`${f.replace(ROOT + '/', '')} -> ${link} (missing file)`); continue; }
    if (anchor && target.endsWith('.md')) {
      if (!anchorsOf(readFileSync(target, 'utf8')).has(anchor.toLowerCase())) {
        broken.push(`${f.replace(ROOT + '/', '')} -> ${link} (missing anchor)`);
      }
    }
  }
}
console.log(broken.length ? `DOC LINKS: ${broken.length} broken\n  ` + broken.join('\n  ')
  : `doc links: PASS — ${md.length} markdown files, 0 broken links`);
process.exit(errs.length || broken.length ? 1 : 0);
