#!/usr/bin/env node
// 4UR4 — causal (as-of-time) golden-fixture reference model & replay harness.
//
// WHAT THIS IS
//   Phase-0 EVIDENCE TOOLING under the GOV-015 build-freeze. It exists so that
//   every expected value in product/fixtures/golden/** can be re-derived
//   mechanically, by an independent verifier, from input.csv + the approved
//   specification — instead of by hand arithmetic that has already been shown to
//   drift (Issue #16).
//
// WHAT THIS IS NOT
//   It is NOT the product detector and confers no Phase-2 credit. It lives in
//   tools/ alongside validate.mjs, creates no product-code directory, is not
//   wired into any product surface, and deliberately implements only the subset
//   of trendline-specification.md that the golden fixtures assert. A future,
//   build-lifted engine must be written separately and must reproduce the
//   fixtures; reproducing THIS script is not the contract.
//
// THE SPECIFICATION IS AUTHORITATIVE, NOT THIS FILE
//   Where this model and product/trendline-specification.md disagree, the
//   specification governs and the divergence is a SPEC DEFECT REPORT or a MODEL
//   BUG — never a silent model behaviour. Known divergences, disclosed:
//
//   1. §16 `h_hold` — NOT IMPLEMENTED. The spec allows the retest hold leg to be
//      satisfied "within h_hold = 3 bars" of the return; this model requires both
//      legs on the same bar, so it is STRICTER than the spec and could miss a
//      deferred-hold retest. Verified against every post-breakout bar of every
//      fixture: no fixture contains such a case, so no expected value depends on
//      it. A fixture exercising the clause is outstanding work.
//   2. §12 touch counting and `eps_touch` — NOT IMPLEMENTED (confidence input
//      only; no fixture asserts a touch list).
//   3. §13.4 volume / `LOW_VOLUME` — NOT IMPLEMENTED. `flags` are authored per
//      fixture and are NOT compared by `compare()`.
//   4. §1 OHLC coherence is enforced here as an input guard although the spec
//      only assumes it; a fixture with an impossible bar is rejected rather than
//      silently evaluated.
//
//   Consequently "23/23 reproduce exactly" means: anchors, second anchor, slope,
//   intercept, line values, state transitions, reason codes, final state and
//   breakout bar. It does NOT cover flags, touches, volume or the h_hold branch.
//
// SPEC BASIS (product/trendline-specification.md)
//   §3 log transform · §4/D-TL-02 anchor · §6 candidacy (all later bar highs,
//   HD-11) · §7 slope/intercept · §8/D-TL-04/D-TL-05 all-highs upper log hull ·
//   §9 tolerances · §10 invalidation · §11 states · §13/HD-03 breakout ·
//   §14 wick · §15 failure · §16 retest · §17 expiry · §18 edge cases ·
//   §21/HD-12/D-TL-11 as-of-time (rolling causal) evaluation.
//
// USAGE
//   node tools/fixture-replay.mjs                 # replay + compare all fixtures
//   node tools/fixture-replay.mjs --audit GX-01   # per-bar causal trace
//   node tools/fixture-replay.mjs --hull          # brute-force hull at every prefix
//   node tools/fixture-replay.mjs --nolookahead   # prefix-truncation invariance
//   node tools/fixture-replay.mjs --ohlc          # OHLC coherence over every bar
//   node tools/fixture-replay.mjs --robustness    # eps_break sensitivity sweep
//   node tools/fixture-replay.mjs --all           # every check above
//   node tools/fixture-replay.mjs --json          # machine-readable replay output

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const GOLDEN = join(ROOT, 'product/fixtures/golden');

const SPLIT_LOG_JUMP = Math.log(1.5); // §18 SUSPECTED_UNADJUSTED_SPLIT
const FP = 1e-12;                     // float comparison guard

// ---------------------------------------------------------------- utilities --
export const sig6 = (x) => (x === null || x === undefined ? null : Number(Number(x).toPrecision(6)));
const near = (a, b, tol = 5e-7) => a === null && b === null ? true
  : (a === null || b === null ? false : Math.abs(a - b) <= tol * Math.max(1, Math.abs(b)));

export function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const head = lines[0].split(',').map((s) => s.trim());
  const idx = Object.fromEntries(head.map((h, i) => [h, i]));
  const num = (s) => {
    if (s === undefined) return null;
    const v = s.trim();
    if (v === '' || v.toUpperCase() === 'NA' || v.toUpperCase() === 'NAN') return null;
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
  };
  return lines.slice(1).map((ln) => {
    const c = ln.split(',');
    return {
      t: num(c[idx.timestamp]),
      open: num(c[idx.open]),
      high: num(c[idx.high]),
      low: num(c[idx.low]),
      close: num(c[idx.close]),
      volume: num(c[idx.volume]),
    };
  });
}

// ------------------------------------------------------------- input guards --
// §18: whole-bar-set guards. These are evaluated before any geometry is fitted.
export function inputGuards(bars) {
  const codes = [];
  const transitions = [];
  for (let t = 0; t < bars.length; t++) {
    const b = bars[t];
    if (b.high === null || b.open === null || b.low === null || b.close === null) {
      codes.push('INVALID_INPUT');
      transitions.push({ bar: t, from: 'NONE', to: 'NONE', reason_code: 'INVALID_INPUT' });
      break;
    }
  }
  for (let t = 0; t < bars.length; t++) {
    const b = bars[t];
    for (const f of ['open', 'high', 'low', 'close']) {
      if (b[f] !== null && b[f] <= 0) {
        codes.push('INVALID_PRICE');
        transitions.push({ bar: t, from: 'NONE', to: 'NONE', reason_code: 'INVALID_PRICE' });
        t = bars.length;
        break;
      }
    }
  }
  if (codes.length) return { rejected: true, codes, transitions };

  // OHLC coherence (§1): a bar whose open/close fall outside [low, high], or whose
  // low exceeds its high, is not a possible bar. The spec assumes well-formed OHLCV
  // rather than stating this, so it is enforced here as an INPUT guard and is
  // asserted over the whole fixture set by --ohlc (and by --all).
  for (let t = 0; t < bars.length; t++) {
    const b = bars[t];
    if (b.low > b.high + FP || b.open < b.low - FP || b.open > b.high + FP
      || b.close < b.low - FP || b.close > b.high + FP) {
      return {
        rejected: true,
        codes: ['INVALID_INPUT'],
        transitions: [{ bar: t, from: 'NONE', to: 'NONE', reason_code: 'INVALID_INPUT' }],
        detail: { bar: t, reason: 'OHLC incoherent', open: b.open, high: b.high, low: b.low, close: b.close },
      };
    }
  }

  for (let t = 1; t < bars.length; t++) {
    const jump = Math.abs(Math.log(bars[t].high) - Math.log(bars[t - 1].high));
    if (jump > SPLIT_LOG_JUMP + FP) {
      return {
        rejected: true,
        codes: ['SUSPECTED_UNADJUSTED_SPLIT'],
        transitions: [{ bar: t, from: 'NONE', to: 'NONE', reason_code: 'SUSPECTED_UNADJUSTED_SPLIT' }],
        detail: { bar: t, log_jump: jump },
      };
    }
  }
  return { rejected: false, codes: [], transitions: [] };
}

// ------------------------------------------------------- as-of-time geometry --
// A_t (§21.1): earliest argmax high over the available prefix S_t = bars[0..t-1].
export function anchorAt(y, upto) {
  if (upto <= 0) return null;
  let bi = 0;
  for (let i = 1; i < upto; i++) if (y[i] > y[bi] + FP) bi = i;
  return { t: bi, y: y[bi] };
}

// B*_t (§8 over S_t): the shallowest descending line from A that dominates EVERY
// bar high in S_t within eps. Brute force — this is the normative definition;
// the §21.4 running-max lemma is checked against it by --hull.
export function bStarAt(y, upto, tA, eps) {
  let best = null;
  for (let i = tA + 1; i < upto; i++) {
    if (!(y[i] < y[tA] - FP)) continue;             // §6.2 strictly below the ATH
    const m = (y[i] - y[tA]) / (i - tA);
    let worst = -Infinity;
    let ok = true;
    for (let j = tA + 1; j < upto; j++) {
      const gap = y[j] - (y[tA] + m * (j - tA));    // §8.3 domination over ALL highs
      if (gap > worst) worst = gap;
      if (gap > eps + FP) { ok = false; break; }
    }
    if (!ok) continue;
    // argmax slope, with NO slack: a strictly steeper candidate must never replace
    // the incumbent, and a BIT-EXACT tie goes to the later bar (§18
    // ENVELOPE_TIE_LATER; ascending i, so `>=` implements "later wins").
    if (best === null || m >= best.m) best = { t: i, y: y[i], m, worstGap: worst, tie: best !== null && m === best.m };
  }
  if (!best) return null;
  return { t: best.t, y: best.y, m: best.m, b: y[tA] - best.m * tA, worstGap: best.worstGap, tie: best.tie };
}

// The full as-of-time candidate/eligibility picture at evaluation bar t.
export function lambdaAt(y, t, params) {
  const { eps, min_formation_bars, min_ath_age_bars } = params;
  const A = anchorAt(y, t);
  // Each gate is evaluated independently so an auditor can see WHICH one binds
  // and that the others are already clear (§21.3 F1/F2/F3).
  const F1 = t >= min_formation_bars;
  const F2 = A !== null && A.t <= t - 1 - min_ath_age_bars;
  const B = A === null ? null : bStarAt(y, t, A.t, eps);
  const F3 = B !== null;
  const gates = { F1, F2, F3, bars_available: t, tA: A ? A.t : null };
  const reason = !F1 ? 'INSUFFICIENT_BARS' : (!F2 ? 'ATH_TOO_RECENT' : (!F3 ? 'NO_VALID_SECOND_ANCHOR' : null));
  if (reason) return { lambda: null, A, reason, gates };
  return {
    lambda: { A: { t: A.t, y: A.y }, B: { t: B.t, y: B.y }, m: B.m, b: B.b, worstGap: B.worstGap, tie: B.tie },
    A, reason: null, gates,
  };
}

const yhat = (L, u) => L.m * u + L.b;

// -------------------------------------------------------------- causal replay --
// §21.2 authoritative processing order, applied bar by bar.
export function replay(bars, paramsIn) {
  const params = {
    eps: 0.02, eps_touch: 0.01, eps_break: 0.01,
    eps_fail: 0.01, F_fail: 10, eps_retest: 0.01, W_retest: 20, h_hold: 3,
    E_expiry: 100, min_formation_bars: 8, min_ath_age_bars: 3,
    ...paramsIn,
  };
  const guards = inputGuards(bars);
  if (guards.rejected) {
    return {
      params, rejected: true, guards,
      final_state: 'NONE', breakout_bar: null, confirmed_bar: null,
      transitions: guards.transitions, reason_codes: [...new Set(guards.codes)],
      line: null, frozen: null, bars: [], reselections: [], events: [],
    };
  }

  const y = bars.map((b) => Math.log(b.high));
  const n = bars.length;

  let state = 'NONE';
  let frozen = null;          // Λ^F (§21.5)
  let lastFrozen = null;      // retained for reporting after EXPIRED/RESET
  let breakout_bar = null;
  let eventBreakoutBar = null; // the breakout bar reported by the fixture
  let lastLambda = null;      // Λ_t of the previous bar (for re-selection reporting)
  let episodeAnchor = null;
  let everFormed = false;
  let standingReason = null;
  const transitions = [];
  const reason_codes = [];
  const perBar = [];
  const reselections = [];
  const events = [];
  const push = (bar, from, to, reason_code) => {
    transitions.push({ bar, from, to, reason_code });
    if (!reason_codes.includes(reason_code)) reason_codes.push(reason_code);
  };

  for (let t = 0; t < n; t++) {
    // ---- step 1: build Λ_t from S_t only ------------------------------------
    const post = state === 'BROKEN_OUT' || state === 'RETESTED' || state === 'FAILED_BREAKOUT';
    const g = lambdaAt(y, t, params);
    const L = post ? frozen : g.lambda;              // line judging bar t
    const startState = post ? state : (g.lambda ? 'ACTIVE' : 'NONE');

    // §21.2 step 1: the line effective at THIS bar is established before the bar is
    // judged, so a pre-breakout re-selection that took effect here is recorded here,
    // ahead of whatever event this bar then produces. Emitting it afterwards
    // produced a transition list that was not a valid walk of the §11 machine
    // (`from: ACTIVE` after the state had already moved to BROKEN_OUT) — found by
    // Verification, Code Review and Strategic Review at head c0ede4d.
    if (!post && state === 'ACTIVE' && lastLambda && L && lastLambda.B.t !== L.B.t) {
      const tie = lastLambda.m === L.m;
      reselections.push({ effective_bar: t, from: lastLambda.B.t, to: L.B.t, m: L.m, tie });
      push(t, 'ACTIVE', 'ACTIVE', 'LINE_ESTABLISHED');
      if (tie) push(t, 'ACTIVE', 'ACTIVE', 'ENVELOPE_TIE_LATER');
    }

    // NONE -> ACTIVE (§11, §21.3) or ACTIVE -> NONE (F2/F3 lost)
    if (!post) {
      if (g.lambda && state === 'NONE') {
        push(t, 'NONE', 'ACTIVE', 'LINE_ESTABLISHED');
        if (g.lambda.tie && !reason_codes.includes('ENVELOPE_TIE_LATER')) reason_codes.push('ENVELOPE_TIE_LATER');
        state = 'ACTIVE';
        episodeAnchor = g.lambda.A.t;
      } else if (!g.lambda && state === 'ACTIVE') {
        push(t, 'ACTIVE', 'NONE', g.reason);
        state = 'NONE';
      } else if (!g.lambda && state === 'NONE'
        && g.reason && g.reason !== 'INSUFFICIENT_BARS' && g.reason !== standingReason) {
        // The state is NONE and the block is no longer merely bar count: record
        // the standing formation-gate reason once per contiguous NONE run
        // (§18/§21.3 — e.g. ATH_TOO_RECENT after a reset, NO_VALID_SECOND_ANCHOR
        // for GX-20). Plain INSUFFICIENT_BARS at the head of a series is not
        // recorded as an event; it is visible in causal_record.formation.
        standingReason = g.reason;
        push(t, 'NONE', 'NONE', g.reason);
      }
      if (g.lambda) { everFormed = true; standingReason = null; }
    }

    const rec = {
      t, state_at_start: startState,
      line: L ? { tA: L.A.t, tB: L.B.t, m: L.m, b: L.b, y_hat: yhat(L, t), line: Math.exp(yhat(L, t)) } : null,
      frozen: post,
      no_line_reason: L ? null : g.reason,
      close_margin: L ? Math.log(bars[t].close) - yhat(L, t) - params.eps_break : null,
      high_margin: L ? y[t] - yhat(L, t) - params.eps : null,
      event: null,
    };

    // ---- step 5 first: new ATH takes precedence (§21.2 rule 5, §21.7) --------
    const newAth = g.A !== null && y[t] > g.A.y + FP;
    if (newAth) {
      if (state === 'ACTIVE' || post) {
        push(t, state, 'NONE', 'RESET_NEW_ATH');
        rec.event = 'RESET_NEW_ATH';
        events.push({ bar: t, event: 'RESET_NEW_ATH', prior_state: state });
      }
      state = 'NONE'; frozen = null; breakout_bar = null; episodeAnchor = null; standingReason = null;
      perBar.push(rec); lastLambda = null;
      continue;
    }

    if (state === 'ACTIVE' && L) {
      const yh = yhat(L, t);
      // ---- step 2/3: breakout test against Λ_t (§13.1, §13.2) ---------------
      if (Math.log(bars[t].close) > yh + params.eps_break + FP) {
        frozen = { ...L, breakout_bar: t };
        lastFrozen = frozen;
        breakout_bar = t;
        eventBreakoutBar = t;
        push(t, 'ACTIVE', 'BROKEN_OUT', 'BREAKOUT_CONFIRMED');
        state = 'BROKEN_OUT';
        rec.event = 'BREAKOUT_CONFIRMED';
        events.push({
          bar: t, event: 'BREAKOUT_CONFIRMED',
          line: { tA: L.A.t, tB: L.B.t, m: L.m, b: L.b },
          y_hat: yh, line_value: Math.exp(yh),
          close: bars[t].close, ln_close: Math.log(bars[t].close),
          margin: Math.log(bars[t].close) - (yh + params.eps_break),
        });
      } else {
        // ---- §14 wick-break / §10.1 structural pierce ------------------------
        if (y[t] > yh + params.eps + FP) {
          push(t, 'ACTIVE', 'ACTIVE', 'WICK_BREAK');
          if (!reason_codes.includes('INVALID_PIERCE')) reason_codes.push('INVALID_PIERCE');
          rec.event = 'WICK_BREAK';
          events.push({
            bar: t, event: 'WICK_BREAK',
            y_hat: yh, high: bars[t].high, ln_high: y[t],
            pierce: y[t] - yh, close: bars[t].close,
            close_margin: Math.log(bars[t].close) - (yh + params.eps_break),
          });
        }
      }
    } else if (state === 'BROKEN_OUT' || state === 'RETESTED') {
      const yF = yhat(frozen, t);
      if (t - breakout_bar >= params.E_expiry) {
        push(t, state, 'NONE', 'EXPIRED_POST_BREAKOUT');
        rec.event = 'EXPIRED_POST_BREAKOUT';
        events.push({ bar: t, event: 'EXPIRED_POST_BREAKOUT', bars_since_breakout: t - breakout_bar });
        state = 'NONE'; frozen = null; breakout_bar = null;
      } else if (state === 'BROKEN_OUT' && t > breakout_bar && t - breakout_bar <= params.F_fail
        && Math.log(bars[t].close) < yF - params.eps_fail - FP) {
        push(t, 'BROKEN_OUT', 'FAILED_BREAKOUT', 'FAILED_BREAKOUT');
        rec.event = 'FAILED_BREAKOUT';
        events.push({
          bar: t, event: 'FAILED_BREAKOUT', y_hat_frozen: yF, line_value: Math.exp(yF),
          close: bars[t].close, margin: (yF - params.eps_fail) - Math.log(bars[t].close),
        });
        state = 'FAILED_BREAKOUT';
      } else if (state === 'BROKEN_OUT' && t > breakout_bar && t - breakout_bar <= params.W_retest
        && Math.log(bars[t].low) <= yF + params.eps_retest + FP
        && Math.log(bars[t].close) >= yF - params.eps_retest - FP) {
        push(t, 'BROKEN_OUT', 'RETESTED', 'RETEST_HELD');
        rec.event = 'RETEST_HELD';
        events.push({
          bar: t, event: 'RETEST_HELD', y_hat_frozen: yF, line_value: Math.exp(yF),
          low: bars[t].low, close: bars[t].close,
          return_margin: (yF + params.eps_retest) - Math.log(bars[t].low),
          hold_margin: Math.log(bars[t].close) - (yF - params.eps_retest),
        });
        state = 'RETESTED';
      }
    }

    // ---- step 4: roll B* forward, effective t+1 (§21.6) ----------------------
    // The roll is *recorded* at the top of the bar it takes effect on (see above);
    // here we only carry Λ forward. A tie is BIT-EXACT equality of the two computed
    // slopes — no slack, because §20.3 requires order-stable tie rules and a
    // tolerance would make the outcome depend on an unnamed constant.
    lastLambda = rec.frozen ? lastLambda : g.lambda;
    perBar.push(rec);
  }

  // Governing line reported by the fixture: the frozen EVENT line whenever a
  // confirmed breakout occurred in the series (it stays the line the market
  // actually broke, even after EXPIRED_POST_BREAKOUT); otherwise Λ_n, the line
  // in force after the last bar is processed — what a live detector reports.
  const tail = lambdaAt(y, n, params);
  const governing = lastFrozen ? lastFrozen : tail.lambda;
  const finalAnchor = anchorAt(y, n);

  // Post-breakout non-retroactive challengers (§21.5, §21.8): later highs that a
  // full-series hull WOULD have selected but which must not move the frozen B*.
  const challengers = [];
  if (lastFrozen && eventBreakoutBar !== null) {
    const mF = lastFrozen.m, tA = lastFrozen.A.t;
    for (let u = eventBreakoutBar; u < n; u++) {
      if (u <= tA) continue;
      const s = (y[u] - y[tA]) / (u - tA);
      if (s > mF + FP && y[u] < y[tA] - FP) {
        challengers.push({ bar: u, high: bars[u].high, slope_if_selected: s, frozen_slope: mF });
      }
    }
  }

  return {
    params, rejected: false, guards,
    final_state: state, breakout_bar: eventBreakoutBar, confirmed_bar: eventBreakoutBar,
    transitions, reason_codes,
    anchor: finalAnchor ? { t: finalAnchor.t, H: Math.exp(finalAnchor.y) } : null,
    line: governing ? {
      A: { t: governing.A.t, H: Math.exp(governing.A.y) },
      B: { t: governing.B.t, H: Math.exp(governing.B.y) },
      m: governing.m, b: governing.b,
    } : null,
    frozen: lastFrozen ? { A: lastFrozen.A, B: lastFrozen.B, m: lastFrozen.m, b: lastFrozen.b, breakout_bar: eventBreakoutBar } : null,
    tail_line: tail.lambda ? {
      A: { t: tail.lambda.A.t, H: Math.exp(tail.lambda.A.y) },
      B: { t: tail.lambda.B.t, H: Math.exp(tail.lambda.B.y) },
      m: tail.lambda.m, b: tail.lambda.b,
    } : null,
    t_form: (perBar.find((r) => r.state_at_start === 'ACTIVE') || {}).t ?? null,
    bars: perBar, reselections, events, challengers,
  };
}

// ------------------------------------------------------------------ fixtures --
export function listFixtures() {
  return readdirSync(GOLDEN).filter((d) => /^GX-\d\d$/.test(d)).sort();
}

export function loadFixture(id) {
  const dir = join(GOLDEN, id);
  const expected = JSON.parse(readFileSync(join(dir, 'expected.json'), 'utf8'));
  const bars = parseCsv(readFileSync(join(dir, 'input.csv'), 'utf8'));
  return { id, dir, expected, bars };
}

function paramsOf(expected) {
  const p = expected.params || {};
  return {
    eps: p.eps ?? 0.02, eps_touch: p.eps_touch ?? 0.01, eps_break: p.eps_break ?? 0.01,
    eps_fail: p.eps_fail ?? 0.01, F_fail: p.F_fail ?? 10,
    eps_retest: p.eps_retest ?? 0.01, W_retest: p.W_retest ?? 20, h_hold: p.h_hold ?? 3,
    E_expiry: p.E_expiry ?? 100,
    min_formation_bars: p.min_formation_bars ?? 8,
    min_ath_age_bars: p.min_ath_age_bars ?? 3,
  };
}

// -------------------------------------------------------------- comparison ----
export function compare(fx, r) {
  const e = fx.expected;
  const diffs = [];
  const eq = (label, got, want) => { if (JSON.stringify(got) !== JSON.stringify(want)) diffs.push(`${label}: got ${JSON.stringify(got)} want ${JSON.stringify(want)}`); };

  // The anchor exists whenever the input is accepted, even if no B* ever does.
  const gotA = r.line ? { t: r.line.A.t, H: sig6(r.line.A.H) }
    : (r.anchor ? { t: r.anchor.t, H: sig6(r.anchor.H) } : null);
  const wantA = e.expected_ath_anchor ? { t: e.expected_ath_anchor.t, H: sig6(e.expected_ath_anchor.H) } : null;
  eq('ath_anchor', gotA, wantA);

  const gotB = r.line ? { t: r.line.B.t, H: sig6(r.line.B.H) } : null;
  const wantB = (e.expected_second_anchor && e.expected_second_anchor.t !== null && e.expected_second_anchor.t !== undefined)
    ? { t: e.expected_second_anchor.t, H: sig6(e.expected_second_anchor.H) } : null;
  eq('second_anchor', gotB, wantB);

  // Geometry is pinned to 6 significant figures (fixtures/README §2), so the
  // test is exact equality of the 6-sig-fig rounding, not a fuzzy tolerance.
  eq('log_slope', r.line ? sig6(r.line.m) : null, e.expected_log_slope ?? null);
  eq('intercept', r.line ? sig6(r.line.b) : null, e.expected_intercept ?? null);

  eq('final_state', r.final_state, e.expected_final_state);
  eq('breakout_bar', r.breakout_bar, e.breakout_bar ?? null);
  eq('confirmed_bar', r.confirmed_bar, e.confirmed_bar ?? null);
  eq('transitions', r.transitions, e.expected_state_transitions);
  eq('reason_codes', [...r.reason_codes].sort(), [...(e.expected_reason_codes || [])].sort());

  if (e.expected_line_values) {
    for (const [k, v] of Object.entries(e.expected_line_values)) {
      const u = Number(k);
      if (!r.line) { diffs.push(`line_values[${k}]: no line computed`); continue; }
      const yh = r.line.m * u + r.line.b;
      eq(`line_values[${k}].y_hat`, sig6(yh), v.y_hat);
      eq(`line_values[${k}].line`, sig6(Math.exp(yh)), v.line);
    }
  }
  return diffs;
}

// ------------------------------------------------------- pivots (DESCRIPTIVE) --
// §5 definition: strict `>` on the left, `>=` on the right, over k bars. Pivot
// status is NON-AUTHORITATIVE (D-TL-03, HD-11) — it never gates candidacy,
// selection or formation eligibility. Computed here purely as evidence.
export function confirmedPivots(highs, k, upto = highs.length) {
  const out = [];
  for (let p = k; p + k < upto; p++) {
    let ok = true;
    for (let i = p - k; i < p && ok; i++) if (!(highs[p] > highs[i])) ok = false;
    for (let j = p + 1; j <= p + k && ok; j++) if (!(highs[p] >= highs[j])) ok = false;
    if (ok) out.push(p);
  }
  return out;
}

// ---------------------------------------------------- causal evidence record --
// Emits the block embedded as `causal_record` in each expected.json: the
// as-of-time candidate set, the active B* before every relevant event bar, the
// slope/intercept/line value at those bars, the breakout margin, the frozen
// event line and the later non-retroactive challengers (Issue #16 instruction A).
export function buildRecord(fx) {
  const p = paramsOf(fx.expected);
  const r = replay(fx.bars, p);
  if (r.rejected) {
    return {
      semantics: CAUSAL_NOTE,
      input_guard: { rejected: true, codes: r.reason_codes, detail: r.guards.detail ?? null },
      note: 'Input guards (§18) reject the bar-set before any geometry is fitted, so no as-of-time line exists at any prefix.',
    };
  }
  const y = fx.bars.map((b) => Math.log(b.high));

  // formation gate trace
  const gate = [];
  for (let t = 0; t <= fx.bars.length; t++) {
    const g = lambdaAt(y, t, p);
    gate.push({ t, eligible: !!g.lambda, reason: g.reason, gates: g.gates });
  }
  const t_form = (gate.find((x) => x.eligible) || {}).t ?? null;
  const gateLine = (x) => {
    const g = x.gates || {};
    const f1 = `F1 |S_t|=${g.bars_available}>=${p.min_formation_bars}:${g.F1 ? 'ok' : 'FAIL'}`;
    const f2 = `F2 tA=${g.tA}<=(t-1)-${p.min_ath_age_bars}:${g.F2 ? 'ok' : 'FAIL'}`;
    const f3 = `F3 B*_t exists:${g.F3 ? 'ok' : 'FAIL'}`;
    return `t=${x.t}: ${x.eligible ? 'ELIGIBLE' : x.reason} [${f1}; ${f2}; ${f3}]`;
  };

  // When no line EVER forms, prove it from every evaluable prefix: show the
  // shallowest descending candidate and the pierce inflicted on it by the
  // ATH-tying bar (§10.4 / §18 — the GX-20 construction).
  let noAnchorProof = null;
  if (!gate.some((x) => x.eligible)) {
    const rows = [];
    for (let t = p.min_formation_bars; t <= fx.bars.length; t++) {
      const A = anchorAt(y, t);
      if (!A) continue;
      let arg = null, bestSlope = -Infinity;
      for (let i = A.t + 1; i < t; i++) {
        if (!(y[i] < y[A.t] - FP)) continue;
        const s = (y[i] - y[A.t]) / (i - A.t);
        if (s >= bestSlope) { bestSlope = s; arg = i; }
      }
      const ties = [];
      for (let i = A.t + 1; i < t; i++) if (Math.abs(y[i] - y[A.t]) <= FP) ties.push(i);
      const pierce = arg === null ? null : Math.max(...ties.map((u) => y[u] - (y[A.t] + bestSlope * (u - A.t))), -Infinity);
      rows.push({
        at_bar: t, prefix: `S_${t}`,
        ath_tie_bars: ties,
        shallowest_candidate: arg === null ? null : { t: arg, H: sig6(fx.bars[arg].high), slope: sig6(bestSlope) },
        pierce_at_tie_bar: pierce === null || pierce === -Infinity ? null : sig6(pierce),
        exceeds_eps_by: pierce === null || pierce === -Infinity ? null : sig6(pierce / p.eps),
        envelope_valid_candidates: 0,
      });
    }
    noAnchorProof = {
      eps: p.eps,
      note: 'At EVERY evaluable prefix the shallowest descending candidate is already pierced beyond eps by the bar that ties the ATH, and the shallowest candidate minimises that pierce — so no candidate is envelope-valid at any prefix and no line ever becomes ACTIVE. Because no line exists, eps_break is never consulted: the outcome is invariant across the whole 0.5x-2x eps_break sweep.',
      per_prefix: rows,
    };
  }

  // as-of-time candidate set at the formation bar
  let candSet = null;
  if (t_form !== null) {
    const A = anchorAt(y, t_form);
    const cands = [];
    for (let i = A.t + 1; i < t_form; i++) {
      if (!(y[i] < y[A.t] - FP)) continue;
      const m = (y[i] - y[A.t]) / (i - A.t);
      let worst = -Infinity;
      for (let j = A.t + 1; j < t_form; j++) worst = Math.max(worst, y[j] - (y[A.t] + m * (j - A.t)));
      cands.push({ t: i, H: sig6(fx.bars[i].high), slope: sig6(m), worst_gap: sig6(worst), envelope_valid: worst <= p.eps + FP });
    }
    const sel = bStarAt(y, t_form, A.t, p.eps);
    candSet = {
      at_bar: t_form,
      available_prefix: `S_${t_form} = bars 0..${t_form - 1}`,
      anchor: { t: A.t, H: sig6(fx.bars[A.t].high) },
      candidates: cands,
      selected: sel ? { t: sel.t, H: sig6(fx.bars[sel.t].high), slope: sig6(sel.m) } : null,
      note: 'Candidacy is over EVERY later bar high (§6, HD-11); pivot status is not consulted. Domination is tested over all bar highs in the prefix (D-TL-05).',
    };
  }

  // active B* before each relevant event bar
  const eventBars = new Set([...r.events.map((e) => e.bar), ...(t_form !== null ? [t_form] : []), fx.bars.length - 1]);
  const active = [...eventBars].sort((a, b) => a - b).map((t) => {
    const rec = r.bars[t];
    if (!rec || !rec.line) return { bar: t, line: null, state_at_start: rec ? rec.state_at_start : null, reason: rec ? rec.no_line_reason : null };
    return {
      bar: t,
      state_at_start: rec.state_at_start,
      line_source: rec.frozen ? 'frozen event line Λ^F (§21.5)' : `Λ_${t} built from S_${t} = bars 0..${t - 1}`,
      B_star: { t: rec.line.tB, H: sig6(fx.bars[rec.line.tB].high) },
      m: sig6(rec.line.m), b: sig6(rec.line.b),
      y_hat_at_bar: sig6(rec.line.y_hat), line_at_bar: sig6(rec.line.line),
      close_vs_line_plus_eps_break: sig6(rec.close_margin),
      high_vs_line_plus_eps: sig6(rec.high_margin),
    };
  });

  return {
    semantics: CAUSAL_NOTE,
    formation: {
      min_formation_bars: p.min_formation_bars,
      min_ath_age_bars: p.min_ath_age_bars,
      t_form,
      rule: 'FORMATION_ELIGIBLE(t) iff |S_t| >= min_formation_bars (F1) AND tA <= (t-1) - min_ath_age_bars (F2) AND B*_t exists (F3). Both thresholds are first-class versioned parameters, independent of the pivot window k (§21.3, D-TL-12).',
      gate_trace: gate.filter((x) => x.t <= (t_form ?? gate.length - 1) + 1).map(gateLine),
      // Only emitted when it adds information beyond gate_trace.
      ...(t_form !== null && t_form + 1 < gate.length ? {
        gate_trace_full: gate.map(gateLine),
        gate_trace_full_caveat: 'This trace re-evaluates the §21.3 gates statelessly at every bar, INCLUDING bars at which the state is BROKEN_OUT/RETESTED. While the state is frozen (§21.5) re-selection is suspended and no formation occurs, so an "ELIGIBLE" entry after the breakout bar describes gate arithmetic only, not an active line. It also runs to t = bar_count, the line that would judge a hypothetical next bar.',
      } : {}),
    },
    as_of_time_candidate_set: candSet,
    ...(noAnchorProof ? { no_anchor_proof: noAnchorProof } : {}),
    pivot_context: (() => {
      const highs = fx.bars.map((b) => b.high);
      const k = p.k ?? 3;
      const full = confirmedPivots(highs, k);
      const atForm = t_form === null ? null : confirmedPivots(highs, k, t_form);
      const bStar = r.line ? r.line.B.t : null;
      return {
        k,
        definition: 'isPivotHigh(p,k): strict > against the k bars on the left, >= against the k bars on the right (§5).',
        confirmed_pivots_full_series: full,
        confirmed_pivots_in_formation_prefix: atForm,
        b_star_bar: bStar,
        b_star_is_confirmed_pivot: bStar === null ? null : full.includes(bStar),
        note: 'DESCRIPTIVE ONLY. Pivot status is non-authoritative (§5, D-TL-03, HD-11): it never removes a candidate from §6/§8, never changes B*, and never affects formation eligibility (§21.3, D-TL-12). Replacing k here changes nothing in this fixture except this block.',
      };
    })(),
    active_line_before_event_bars: active,
    events: r.events.map((e) => Object.fromEntries(Object.entries(e).map(([k, v]) => [k, typeof v === 'number' ? sig6(v) : v]))),
    reselections: r.reselections.map((x) => ({ ...x, m: sig6(x.m) })),
    frozen_event_line: r.frozen ? {
      A: { t: r.frozen.A.t, H: sig6(Math.exp(r.frozen.A.y)) },
      B_star: { t: r.frozen.B.t, H: sig6(Math.exp(r.frozen.B.y)) },
      m: sig6(r.frozen.m), b: sig6(r.frozen.b),
      breakout_bar: r.frozen.breakout_bar, confirmed_bar: r.frozen.breakout_bar,
      tolerance_version: fx.expected.params.tolerance_version,
      binding: 'Failure (§15), retest (§16) and expiry (§17) are evaluated against THIS line; re-selection is suspended (§21.5).',
    } : null,
    non_retroactive_challengers: r.challengers.length ? {
      note: 'Later highs whose A→high slope is shallower than the frozen line. Under a full-series hull they would re-select B*; §21.5/§21.8 forbid it, so the frozen line stands.',
      bars: r.challengers.map((c) => ({ bar: c.bar, H: sig6(c.high), slope_if_selected: sig6(c.slope_if_selected) })),
    } : { note: 'No later high has a shallower slope than the governing line; nothing could have re-selected B* even under a full-series reading.', bars: [] },
    eps_break_robustness: {
      documented_default: p.eps_break,
      sweep: robustness(fx, [0.5, 0.8, 1.0, 1.2, 2.0]).map((x) => ({ scale: x.scale, eps_break: x.eps_break, final_state: x.state, breakout_bar: x.breakout_bar })),
    },
  };
}

const CAUSAL_NOTE = 'As-of-time (rolling causal) evaluation per §21 / HD-12 / D-TL-11. Every value below is derived ONLY from bars strictly earlier than the bar it judges; no expectation here uses a full-series hull.';

// ------------------------------------------------------------------- checks ---
function checkHull(fx) {
  // §21.4 lemma vs §8 brute force at EVERY evaluable prefix.
  const p = paramsOf(fx.expected);
  if (inputGuards(fx.bars).rejected) return [];
  const y = fx.bars.map((b) => Math.log(b.high));
  const problems = [];
  for (let t = 1; t <= fx.bars.length; t++) {
    const A = anchorAt(y, t);
    if (!A) continue;
    const brute = bStarAt(y, t, A.t, p.eps);
    // running-max-slope characterisation
    let arg = null, bestSlope = -Infinity;
    for (let i = A.t + 1; i < t; i++) {
      if (!(y[i] < y[A.t] - FP)) continue;
      const s = (y[i] - y[A.t]) / (i - A.t);
      if (s > bestSlope - FP) { bestSlope = Math.max(bestSlope, s); arg = i; }
    }
    let lemma = null;
    if (arg !== null) {
      const m = (y[arg] - y[A.t]) / (arg - A.t);
      let worst = -Infinity;
      for (let j = A.t + 1; j < t; j++) worst = Math.max(worst, y[j] - (y[A.t] + m * (j - A.t)));
      lemma = worst > p.eps + FP ? null : arg;      // §10.4 when the ATH tie pierces
    }
    const bt = brute ? brute.t : null;
    if (bt !== lemma) problems.push(`prefix t=${t}: brute B*=${bt} vs running-max lemma B*=${lemma}`);
  }
  return problems;
}

function checkNoLookahead(fx) {
  // §21.8: truncating the series at any bar must not change any classification
  // at or before that bar.
  const p = paramsOf(fx.expected);
  const full = replay(fx.bars, p);
  const problems = [];
  for (let cut = 1; cut <= fx.bars.length; cut++) {
    const part = replay(fx.bars.slice(0, cut), p);
    const a = JSON.stringify(full.transitions.filter((x) => x.bar === null || x.bar < cut));
    const b = JSON.stringify(part.transitions.filter((x) => x.bar === null || x.bar < cut));
    if (a !== b) problems.push(`cut=${cut}: prefix transitions differ\n    full: ${a}\n    part: ${b}`);
    if (problems.length > 3) break;
  }
  return problems;
}

// §21.3 / D-TL-12 formation-gate regression, asserted mechanically:
//   (a) no formation before min_formation_bars;
//   (b) no formation before min_ath_age_bars after the governing anchor;
//   (c) formation is eligible IMMEDIATELY once both gates and B* are satisfied;
//   (d) pivot status is irrelevant — varying k changes nothing at all.
function checkFormation(fx) {
  const p = paramsOf(fx.expected);
  const problems = [];
  const r = replay(fx.bars, p);
  if (r.rejected) return problems;
  const y = fx.bars.map((b) => Math.log(b.high));

  for (const rec of r.bars) {
    if (rec.state_at_start === 'NONE') continue;
    if (rec.t < p.min_formation_bars) problems.push(`(a) bar ${rec.t}: a line is active before min_formation_bars=${p.min_formation_bars}`);
    const tA = rec.line ? rec.line.tA : null;
    if (tA !== null && rec.t < tA + p.min_ath_age_bars + 1) {
      problems.push(`(b) bar ${rec.t}: a line is active only ${rec.t - tA} bars after its anchor tA=${tA} (min_ath_age_bars=${p.min_ath_age_bars})`);
    }
  }
  // (c) the first ACTIVE bar is the least t satisfying all three gates
  const firstActive = (r.bars.find((x) => x.state_at_start === 'ACTIVE') || {}).t ?? null;
  let leastEligible = null;
  for (let t = 0; t <= fx.bars.length; t++) if (lambdaAt(y, t, p).lambda) { leastEligible = t; break; }
  if (firstActive !== leastEligible) problems.push(`(c) first ACTIVE bar ${firstActive} != least eligible bar ${leastEligible}`);

  // (d) k-independence. NOTE ON WHAT THIS DOES AND DOES NOT PROVE: `replay()` never
  // reads `params.k` at all — k-independence is STRUCTURAL in this model, not an
  // empirical result, so a k-sweep here cannot fail and is not evidence. What the
  // sweep does establish is that no k leaks in indirectly (via defaults, or via a
  // future edit). The load-bearing evidence that k is non-authoritative is the
  // fixture data: GX-08 (zero pivots, canonical anchor exists), GX-19/GX-23
  // (non-pivot B*), and 9 of 20 geometry fixtures with a non-pivot B*.
  const base = JSON.stringify({ tr: r.transitions, st: r.final_state, bo: r.breakout_bar, line: r.line });
  for (const k of [1, 2, 3, 4, 5, 8]) {
    const alt = replay(fx.bars, { ...p, k });
    if (JSON.stringify({ tr: alt.transitions, st: alt.final_state, bo: alt.breakout_bar, line: alt.line }) !== base) {
      problems.push(`(d) changing the pivot window to k=${k} changed the outcome — formation/selection must be k-independent (HD-11, D-TL-12)`);
    }
  }
  // (e) POSITIVE CONTROL for (d): the formation parameters MUST be outcome-bearing.
  // If perturbing them changes nothing, the gates are not wired up and (a)-(d)
  // would pass vacuously. Every fixture that forms a line must react.
  if (r.line || r.bars.some((x) => x.state_at_start === 'ACTIVE')) {
    const later = replay(fx.bars, { ...p, min_formation_bars: p.min_formation_bars + 1 });
    const older = replay(fx.bars, { ...p, min_ath_age_bars: p.min_ath_age_bars + 1 });
    const same = (a, b) => JSON.stringify(a.transitions) === JSON.stringify(b.transitions);
    if (same(later, r) && same(older, r)) {
      problems.push('(e) positive control FAILED: neither min_formation_bars+1 nor min_ath_age_bars+1 changed any transition — the formation gates are not outcome-bearing in this fixture, so checks (a)-(d) pass vacuously');
    }
  }
  return problems;
}

// §21.5 / §21.8: the reported event line must BE the line active at the start of
// the breakout bar, and no later bar may alter it.
function checkFrozen(fx) {
  const p = paramsOf(fx.expected);
  const r = replay(fx.bars, p);
  if (r.rejected || r.breakout_bar === null) return [];
  const problems = [];
  const y = fx.bars.map((b) => Math.log(b.high));
  const atBreak = lambdaAt(y, r.breakout_bar, p).lambda;
  if (!atBreak) { problems.push(`no line existed at the start of breakout bar ${r.breakout_bar}`); return problems; }
  const F = r.frozen;
  if (F.A.t !== atBreak.A.t || F.B.t !== atBreak.B.t || sig6(F.m) !== sig6(atBreak.m) || sig6(F.b) !== sig6(atBreak.b)) {
    problems.push(`frozen line != Λ_${r.breakout_bar}: frozen B*=${F.B.t} m=${sig6(F.m)} vs start-of-bar B*=${atBreak.B.t} m=${sig6(atBreak.m)}`);
  }
  for (const rec of r.bars.filter((x) => x.t > r.breakout_bar && x.line)) {
    if (rec.frozen && (rec.line.tB !== F.B.t || sig6(rec.line.m) !== sig6(F.m))) {
      problems.push(`bar ${rec.t}: post-breakout line moved (B*=${rec.line.tB})`);
    }
  }
  // the fixture must actually EXERCISE the freeze: a shallower later high exists
  if (!r.challengers.length && fx.bars.length > r.breakout_bar + 1) {
    problems.push('note: no post-breakout challenger exists, so the freeze is not exercised by this fixture');
  }
  return problems;
}

// §11: the recorded transition list must be a valid WALK of the state machine —
// each entry's `from` must equal the previous entry's `to`. `compare()` checks the
// list by exact equality, so an incoherent list would otherwise be baked into the
// contract invisibly (found at head c0ede4d).
function checkTransitionChain(fx) {
  const p = paramsOf(fx.expected);
  const r = replay(fx.bars, p);
  const problems = [];
  let state = 'NONE';
  for (const tr of r.transitions) {
    if (tr.from !== state) {
      problems.push(`transition at bar ${tr.bar} (${tr.reason_code}) declares from=${tr.from} but the machine is in ${state}`);
    }
    state = tr.to;
  }
  if (state !== r.final_state) problems.push(`walking the transitions ends in ${state} but final_state is ${r.final_state}`);
  return problems;
}

// §1 OHLC coherence over the whole set. GX-18's incoherence is deliberate and is
// caught earlier by the INVALID_INPUT/INVALID_PRICE guards, so it is exempt.
function checkOhlc(fx) {
  const problems = [];
  const guards = inputGuards(fx.bars);
  if (guards.rejected && guards.codes.some((c) => c === 'INVALID_INPUT' || c === 'INVALID_PRICE')) return problems;
  for (const [t, b] of fx.bars.entries()) {
    if ([b.open, b.high, b.low, b.close].some((v) => v === null)) continue;
    if (b.low > b.high || b.open < b.low || b.open > b.high || b.close < b.low || b.close > b.high) {
      problems.push(`bar ${t}: incoherent OHLC ${b.open}/${b.high}/${b.low}/${b.close}`);
    }
  }
  return problems;
}

// HD-13 rule 1 is a MUST: every ORDINARY fixture's classification is invariant
// under ±20% around the documented eps_break. GX-15 is the one fixture HD-13
// exempts by design. This must FAIL the run, not merely print.
const EPS_BREAK_BOUNDARY_EXEMPT = new Set(['GX-15']);
function checkEpsBreakRule(fx) {
  if (EPS_BREAK_BOUNDARY_EXEMPT.has(fx.id)) return [];
  const outcomes = new Set(robustness(fx, [0.8, 1.0, 1.2]).map((x) => `${x.state}/${x.breakout_bar}`));
  return outcomes.size === 1 ? []
    : [`HD-13 rule 1 violated: classification is not invariant under ±20% of eps_break (${[...outcomes].join(' vs ')})`];
}

function robustness(fx, scales = [0.8, 1.0, 1.2]) {
  const p = paramsOf(fx.expected);
  return scales.map((s) => {
    const r = replay(fx.bars, { ...p, eps_break: p.eps_break * s });
    return { scale: s, eps_break: sig6(p.eps_break * s), state: r.final_state, breakout_bar: r.breakout_bar, B: r.line ? r.line.B.t : null };
  });
}

// --------------------------------------------------------------------- main ---
const argv = process.argv.slice(2);
const has = (f) => argv.includes(f);
const argOf = (f) => { const i = argv.indexOf(f); return i >= 0 ? argv[i + 1] : null; };
const only = argv.find((a) => /^GX-\d\d$/.test(a)) || argOf('--audit');

if (import.meta.url === `file://${process.argv[1]}`) {
  const ids = only ? [only] : listFixtures();
  let failures = 0;
  const report = [];

  if (has('--record') && only) {
    console.log(JSON.stringify(buildRecord(loadFixture(only)), null, 2));
    process.exit(0);
  }

  if (has('--audit') && only) {
    const fx = loadFixture(only);
    const p = paramsOf(fx.expected);
    const r = replay(fx.bars, p);
    console.log(`# ${only} causal audit  (params: ${JSON.stringify(p)})`);
    if (r.rejected) { console.log('  REJECTED by input guards:', JSON.stringify(r.guards)); }
    for (const rec of r.bars) {
      const L = rec.line;
      console.log(
        `t=${String(rec.t).padStart(3)} ${rec.state_at_start.padEnd(15)}` +
        (L ? ` B*=${String(L.tB).padStart(3)} m=${L.m.toFixed(7)} yhat=${L.y_hat.toFixed(6)} line=${L.line.toFixed(4)}` +
             ` closeMargin=${rec.close_margin.toFixed(6)} highMargin=${rec.high_margin.toFixed(6)}`
           : ` (no line: ${rec.no_line_reason})`) +
        (rec.frozen ? ' [FROZEN]' : '') + (rec.event ? `  << ${rec.event}` : '')
      );
    }
    console.log('\ntransitions:', JSON.stringify(r.transitions));
    console.log('reason_codes:', JSON.stringify(r.reason_codes));
    console.log('reselections:', JSON.stringify(r.reselections));
    console.log('events:', JSON.stringify(r.events, null, 2));
    console.log('challengers:', JSON.stringify(r.challengers));
    console.log('governing line:', JSON.stringify(r.line));
    console.log('final:', r.final_state, 'breakout_bar:', r.breakout_bar);
    process.exit(0);
  }

  for (const id of ids) {
    const fx = loadFixture(id);
    const p = paramsOf(fx.expected);
    const r = replay(fx.bars, p);
    const diffs = compare(fx, r);
    const extra = [];
    if (has('--hull') || has('--all')) extra.push(...checkHull(fx).map((s) => `hull: ${s}`));
    if (has('--nolookahead') || has('--all')) extra.push(...checkNoLookahead(fx).map((s) => `lookahead: ${s}`));
    if (has('--formation') || has('--all')) extra.push(...checkFormation(fx).map((s) => `formation: ${s}`));
    if (has('--frozen') || has('--all')) extra.push(...checkFrozen(fx).filter((s) => !s.startsWith('note:')).map((s) => `frozen: ${s}`));
    if (has('--ohlc') || has('--all')) extra.push(...checkOhlc(fx).map((s) => `ohlc: ${s}`));
    if (has('--all')) extra.push(...checkTransitionChain(fx).map((s) => `chain: ${s}`));
    if (has('--all')) extra.push(...checkEpsBreakRule(fx).map((s) => `eps_break: ${s}`));
    const all = [...diffs, ...extra];
    if (all.length) failures++;
    report.push({ id, ok: all.length === 0, diffs: all, replay: r });
    if (!has('--json')) {
      console.log(`${all.length ? '✗' : '✓'} ${id}  ${r.final_state}` +
        `${r.breakout_bar !== null ? ` BO@${r.breakout_bar}` : ''}` +
        `${r.line ? ` B*=(${r.line.B.t},${sig6(r.line.B.H)}) m=${sig6(r.line.m)}` : ' no-line'}`);
      for (const d of all) console.log(`    ${d}`);
      if (has('--robustness') || has('--all')) {
        const rb = robustness(fx, [0.5, 0.8, 1.0, 1.2, 2.0]);
        const states = [...new Set(rb.map((x) => `${x.state}/${x.breakout_bar}`))];
        console.log(`    eps_break sweep: ${rb.map((x) => `${x.scale}x→${x.state}${x.breakout_bar !== null ? '@' + x.breakout_bar : ''}`).join('  ')}` +
          `   ${states.length === 1 ? '[ROBUST 0.5x–2x]' : (new Set(robustness(fx).map((x) => `${x.state}/${x.breakout_bar}`)).size === 1 ? '[ROBUST ±20%]' : '[FRAGILE ±20%]')}`);
      }
    }
  }
  if (has('--json')) console.log(JSON.stringify(report, null, 2));
  else console.log(`\n${ids.length - failures}/${ids.length} fixtures reproduce exactly under as-of-time (§21/HD-12) replay.`);
  process.exit(failures ? 1 : 0);
}
