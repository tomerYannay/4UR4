"""Determinism, evidence and the HD-13 tolerance sweep as a GATING check.

===  ======================================================================
D-1  6-significant-figure geometry, compared exactly, one ``sig6``
D-2  no dependence on floating-point associativity (single-site forms)
D-3  stable ordering everywhere, including under a varied ``PYTHONHASHSEED``
D-4  no wall clock, no randomness
D-6  same input twice -> byte-identical serialized output, over all 24 fixtures
D-7  causal evaluation, checked by prefix-truncation invariance (test_properties)
D-8  every output carries ``spec_version`` and ``tolerance_version``
C-1  every ordinary fixture is invariant at 0.8x and 1.2x ``eps_break``
C-2  the engine's sweep EQUALS the committed sweep at every recorded scale
C-3  anti-vacuity on the tolerance-boundary whitelist
C-4  tie-proximity audit: no compared value sits within 1 ulp of a rounding tie
C-5  the sweep is shown capable of failing
===  ======================================================================
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from typing import Any, Dict, List

from ..detector import DetectionResult, detect
from ..logspace import sig6, sig6_stable
from ..params import DetectorParams
from ..state import LineState, ReasonCode
from .conformance import SPEC_VERSION
from .fixtures_io import (
    GOLDEN_DIR,
    REAL_DIR,
    REPO_ROOT,
    golden_fixture_ids,
    load_expected,
    load_json,
    load_series,
)


def _load(fixture_id: str):
    expected = load_expected(fixture_id)
    series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
    params = DetectorParams.from_fixture_params(expected["params"], spec_version=SPEC_VERSION)
    return expected, series, params


def serialize(result: DetectionResult) -> str:
    """A canonical, fixed-key-order rendering of everything the engine reports.

    ``frozen_line``, ``confirmed_bar`` and ``state_at_start`` are in the digest
    deliberately.  Without them D-3 and D-6 would certify a corpus in which every
    quantity Phase 3 added was unobserved — the digest would be byte-identical
    across two runs that disagreed about the frozen line.
    """
    line = result.reported_line
    frozen = result.frozen_line
    payload: Dict[str, Any] = {
        "spec_version": result.spec_version,
        "tolerance_version": result.tolerance_version,
        "rejected": result.rejected,
        "ath_anchor": None if result.ath_anchor is None else list(result.ath_anchor),
        "reported_line": None
        if line is None
        else {
            "t_anchor": line.t_anchor,
            "high_anchor": repr(line.high_anchor),
            "t_b": line.t_b,
            "high_b": repr(line.high_b),
            "m": repr(line.m),
            "b": repr(line.b),
        },
        "stop_bar": result.stop_bar,
        "confirmed_bar": result.confirmed_bar,
        "frozen_line": None
        if frozen is None
        else {
            "t_anchor": frozen.line.t_anchor,
            "high_anchor": repr(frozen.line.high_anchor),
            "t_b": frozen.line.t_b,
            "high_b": repr(frozen.line.high_b),
            "m": repr(frozen.line.m),
            "b": repr(frozen.line.b),
            "tolerance_version": frozen.tolerance_version,
            "breakout_bar": frozen.breakout_bar,
        },
        "challengers": [
            [item.bar, repr(item.high), repr(item.slope_if_selected)]
            for item in result.challengers
        ],
        "final_state": None if result.final_state is None else result.final_state.value,
        "state_at_start": []
        if result.causal is None
        else [state.value for state in result.causal.state_at_start],
        "transitions": [list(record.as_tuple()) for record in result.transitions],
        "reason_codes": [code.value for code in result.reason_codes],
        "reselections": []
        if result.causal is None
        else [
            [item.effective_bar, item.frm, item.to, repr(item.m), item.tie]
            for item in result.causal.reselections
        ],
        "gate_trace": []
        if result.causal is None
        else [list(sealed.verdict.structural()) for sealed in result.causal.sealed],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def serialize_corpus() -> str:
    parts: List[str] = []
    for fixture_id in golden_fixture_ids():
        _expected, series, params = _load(fixture_id)
        parts.append(fixture_id + "=" + serialize(detect(series, params)))
    expected_causal = load_json(os.path.join(REAL_DIR, "RM-01", "expected-causal.json"))
    series = load_series(os.path.join(REAL_DIR, "RM-01", "input.csv"))
    params = DetectorParams.from_fixture_params(
        expected_causal["params"], spec_version=SPEC_VERSION
    )
    parts.append("RM-01=" + serialize(detect(series, params)))
    return "\n".join(parts)


class D6Determinism(unittest.TestCase):
    def test_same_input_twice_gives_byte_identical_output(self) -> None:
        self.assertEqual(serialize_corpus(), serialize_corpus())

    def test_the_corpus_covers_all_24_fixtures(self) -> None:
        self.assertEqual(len(serialize_corpus().splitlines()), len(golden_fixture_ids()) + 1)


class D3StableOrdering(unittest.TestCase):
    """Ordering must not depend on hash randomisation.

    Run in a child process precisely because ``PYTHONHASHSEED`` is fixed at
    interpreter start-up: an in-process test of it could not fail.  This module
    is the only one in the suite that spawns a process, and it spawns only this
    interpreter running this package.
    """

    def _run_child(self, seed: str) -> str:
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = seed
        return subprocess.check_output(
            [
                sys.executable,
                "-c",
                "from engine.tests.test_determinism import serialize_corpus;"
                "print(serialize_corpus())",
            ],
            cwd=REPO_ROOT,
            env=env,
        ).decode("utf-8")

    def test_output_is_identical_under_varied_hash_seeds(self) -> None:
        first = self._run_child("0")
        second = self._run_child("987654321")
        self.assertEqual(first, second)
        self.assertEqual(first.strip(), serialize_corpus().strip())

    def test_no_output_path_iterates_a_set(self) -> None:
        import ast

        engine_dir = os.path.join(REPO_ROOT, "engine")
        for name in sorted(os.listdir(engine_dir)):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(engine_dir, name), "r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.comprehension)):
                    iterated = node.iter
                    self.assertNotIsInstance(
                        iterated, ast.Set, "%s iterates a set literal" % name
                    )
                    if isinstance(iterated, ast.Call) and isinstance(iterated.func, ast.Name):
                        self.assertNotIn(
                            iterated.func.id,
                            {"set", "frozenset"},
                            "%s iterates a set" % name,
                        )


class D8Versioning(unittest.TestCase):
    def test_every_result_carries_both_versions(self) -> None:
        for fixture_id in golden_fixture_ids():
            expected, series, params = _load(fixture_id)
            result = detect(series, params)
            self.assertEqual(result.spec_version, SPEC_VERSION)
            self.assertEqual(
                result.tolerance_version, expected["params"]["tolerance_version"], fixture_id
            )

    def test_spec_version_has_no_silent_default(self) -> None:
        """OQ-J: the specification declares no version number and the value is
        the Product Steward's to define.  The engine must not invent one."""
        with self.assertRaises(TypeError):
            DetectorParams(  # type: ignore[call-arg]
                eps=0.02,
                eps_break=0.01,
                min_formation_bars=8,
                min_ath_age_bars=3,
                tolerance_version="x",
            )


class C4TieProximityAudit(unittest.TestCase):
    """No value the gate compares may sit within 1 ulp of a 6-s.f. rounding tie.

    If one ever does, ``sig6``'s rounding mode becomes an undeclared platform
    dependency and the gate is passing on luck.  Any hit is ESCALATED, not
    absorbed — the message says so, and the assertion does not soften.
    """

    def _values(self) -> List:
        out = []
        for fixture_id in golden_fixture_ids():
            expected, series, params = _load(fixture_id)
            result = detect(series, params)
            line = result.reported_line
            if line is not None:
                out.append(("%s.m" % fixture_id, line.m))
                out.append(("%s.b" % fixture_id, line.b))
                for key in (expected.get("expected_line_values") or {}):
                    out.append(("%s.y_hat[%s]" % (fixture_id, key), line.y_hat_at(int(key))))
                    out.append(("%s.line[%s]" % (fixture_id, key), line.price_at(int(key))))
            if result.causal is None:
                continue
            for sealed in result.causal.sealed:
                selection = sealed.verdict.selection
                if selection is None:
                    continue
                for candidate in selection.candidates:
                    out.append(("%s.slope@%d" % (fixture_id, sealed.t), candidate.slope))
                    out.append(("%s.gap@%d" % (fixture_id, sealed.t), candidate.worst_gap))
            # The four post-breakout margin quantities the fixtures record, and
            # the challenger slopes.  Without these the audit would certify a
            # corpus in which every Phase-3 comparison was unexamined.
            for event in result.causal.events:
                for key in ("margin", "return_margin", "hold_margin", "y_hat",
                            "y_hat_frozen", "line_value", "ln_close", "pierce",
                            "close_margin", "ln_high"):
                    value = event.detail.get(key)
                    if isinstance(value, float):
                        out.append(
                            ("%s.%s.%s@%d" % (fixture_id, event.event.value, key, event.bar), value)
                        )
            for item in result.challengers:
                out.append(("%s.challenger@%d" % (fixture_id, item.bar), item.slope_if_selected))
            if result.frozen_line is not None:
                out.append(("%s.frozen.m" % fixture_id, result.frozen_line.line.m))
                out.append(("%s.frozen.b" % fixture_id, result.frozen_line.line.b))
        return out

    def test_no_compared_value_is_within_one_ulp_of_a_rounding_tie(self) -> None:
        offenders = [name for name, value in self._values() if not sig6_stable(value)]
        self.assertEqual(
            offenders,
            [],
            "these values round differently one ulp either way, so the 6-s.f. gate "
            "depends on the rounding mode: %r. ESCALATE — do not change the rounding "
            "mode or the fixture to make this pass." % offenders[:10],
        )

    def test_the_audit_is_capable_of_failing(self) -> None:
        """Anti-vacuity: a constructed value on an exact tie must be flagged."""
        self.assertFalse(sig6_stable(1.0000050000000000))
        self.assertGreater(len(self._values()), 500)


class HD13EpsBreakSweep(unittest.TestCase):
    """HD-13 rule 1, run against the engine and gating."""

    SWEEP_SCALES = (0.5, 0.8, 1.0, 1.2, 2.0)
    #: The dedicated tolerance-boundary fixtures, DERIVED from the committed
    #: data rather than whitelisted: a fixture is exempt from invariance iff its
    #: own recorded sweep is non-invariant.
    def _recorded_sweep(self, expected) -> List[Dict[str, Any]]:
        return ((expected.get("causal_record") or {}).get("eps_break_robustness") or {}).get(
            "sweep"
        ) or []

    def _non_invariant_fixtures(self) -> List[str]:
        out = []
        for fixture_id in golden_fixture_ids():
            sweep = self._recorded_sweep(load_expected(fixture_id))
            ordinary = [p for p in sweep if p["scale"] in (0.8, 1.0, 1.2)]
            if len({(p["final_state"], p["breakout_bar"]) for p in ordinary}) > 1:
                out.append(fixture_id)
        return out

    def test_c1_ordinary_fixtures_are_invariant_at_plus_minus_20_percent(self) -> None:
        exempt = set(self._non_invariant_fixtures())
        checked = 0
        for fixture_id in golden_fixture_ids():
            if fixture_id in exempt:
                continue
            expected, series, params = _load(fixture_id)
            base = params.eps_break
            outcomes = {
                (
                    detect(series, params.with_eps_break(base * scale)).stop_bar,
                    None
                    if detect(series, params.with_eps_break(base * scale)).final_state is None
                    else detect(series, params.with_eps_break(base * scale)).final_state.value,
                )
                for scale in (0.8, 1.0, 1.2)
            }
            self.assertEqual(
                len(outcomes), 1, "%s is not tolerance-robust at +/-20%% (HD-13)" % fixture_id
            )
            checked += 1
        self.assertGreater(checked, 15)

    def test_c2_the_engine_sweep_equals_the_committed_sweep(self) -> None:
        """C-1 alone is self-consistency — an engine that ignored ``eps_break``
        entirely would pass it.  This is the falsifiable half."""
        compared = 0
        movers = 0
        for fixture_id in golden_fixture_ids():
            expected, series, params = _load(fixture_id)
            for point in self._recorded_sweep(expected):
                result = detect(series, params.with_eps_break(float(point["eps_break"])))
                self.assertEqual(
                    result.stop_bar,
                    point["breakout_bar"],
                    "%s at scale %s: stop index" % (fixture_id, point["scale"]),
                )
                # Compared at EVERY point.  The Phase-2 form guarded this on
                # ``breakout_bar is None``, which left every post-breakout sweep
                # outcome — GX-12 at 0.5x and GX-15 at 0.5x and 0.8x among them —
                # unasserted.
                self.assertEqual(
                    None if result.final_state is None else result.final_state.value,
                    point["final_state"],
                    "%s at scale %s: final_state" % (fixture_id, point["scale"]),
                )
                compared += 1
            if fixture_id in self._non_invariant_fixtures():
                movers += 1
        self.assertGreater(compared, 90)
        self.assertGreater(movers, 0, "no fixture moves across the sweep — nothing is tested")

    def test_c3_the_exemption_is_derived_and_still_bites(self) -> None:
        """A whitelist is unfalsifiable; this exemption is DERIVED from the
        committed data.  It must still name a real, non-empty, minimal set."""
        non_invariant = self._non_invariant_fixtures()
        self.assertEqual(
            non_invariant,
            ["GX-15"],
            "the set of fixtures that move within +/-20%% changed; HD-13 names "
            "GX-15 as the sole dedicated tolerance-boundary fixture",
        )
        expected, series, params = _load("GX-15")
        wide = {
            detect(series, params.with_eps_break(float(point["eps_break"]))).stop_bar
            for point in self._recorded_sweep(expected)
        }
        self.assertGreater(len(wide), 1, "GX-15 is no longer non-invariant: a stale exemption")

    def test_c5_the_sweep_can_fail(self) -> None:
        """A sweep that cannot fail is a decoration.  An engine that ignored
        ``eps_break`` would produce a different sweep on at least one fixture."""
        expected, series, params = _load("GX-12")
        ignoring = detect(series, params.with_eps_break(0.0))
        honouring = detect(series, params)
        self.assertNotEqual(
            ignoring.stop_bar,
            honouring.stop_bar,
            "GX-12 no longer distinguishes an engine that ignores eps_break",
        )


class ReasonCodeCoverage(unittest.TestCase):
    """Measured by EMISSION during the conformance run, never by grepping source."""

    def test_every_code_reachable_from_the_corpus_is_emitted(self) -> None:
        """14 of the 15 closed-set codes, the four post-breakout ones included.

        The fifteenth is ``INSUFFICIENT_BARS``, which §21.3 says must NOT be
        recorded at the head of a series — it is reachable in the gate trace and
        deliberately absent from the record, asserted by its own test below.
        """
        emitted = set()
        for fixture_id in golden_fixture_ids():
            _expected, series, params = _load(fixture_id)
            emitted.update(code.value for code in detect(series, params).reason_codes)
        every_code = {code.value for code in ReasonCode}
        self.assertEqual(
            every_code - emitted,
            {"INSUFFICIENT_BARS"},
            "the set of closed-set codes NOT emitted anywhere on the corpus moved",
        )
        self.assertEqual(len(emitted), 14)
        for code in ("BREAKOUT_CONFIRMED", "RETEST_HELD", "FAILED_BREAKOUT",
                     "EXPIRED_POST_BREAKOUT"):
            self.assertIn(code, emitted, "%s is emitted by no fixture" % code)

    def test_the_expired_state_is_unreachable(self) -> None:
        """ESC-1 — ``EXPIRED`` is a reserved member of the closed set that no
        conforming detector enters.  Asserted by emission over the whole corpus,
        including the one fixture that actually expires (GX-07): no bar is
        assigned it and no record carries it as ``from`` or ``to``."""
        seen = 0
        expiries = 0
        for fixture_id in golden_fixture_ids():
            _expected, series, params = _load(fixture_id)
            result = detect(series, params)
            self.assertNotEqual(result.final_state, LineState.EXPIRED, fixture_id)
            for record in result.transitions:
                self.assertNotEqual(record.frm, LineState.EXPIRED, fixture_id)
                self.assertNotEqual(record.to, LineState.EXPIRED, fixture_id)
                if record.reason is ReasonCode.EXPIRED_POST_BREAKOUT:
                    expiries += 1
                seen += 1
            if result.causal is not None:
                for state in result.causal.state_at_start:
                    self.assertNotEqual(state, LineState.EXPIRED, fixture_id)
        self.assertGreater(seen, 0)
        self.assertEqual(
            expiries, 1, "GX-07 is the corpus's only expiry; the check is anti-vacuous"
        )
        self.assertIn("EXPIRED", {state.value for state in LineState})

    def test_insufficient_bars_is_reachable_but_deliberately_unrecorded(self) -> None:
        """§21.3: a head-of-series ``INSUFFICIENT_BARS`` run carries no
        information and is not recorded as an event.  The gate verdict still
        names it, so the code is reachable in the trace and absent from the
        record — which is exactly what the fixtures encode."""
        _expected, series, params = _load("GX-01")
        result = detect(series, params)
        self.assertNotIn("INSUFFICIENT_BARS", [c.value for c in result.reason_codes])
        assert result.causal is not None
        reasons = {
            sealed.verdict.reason.value
            for sealed in result.causal.sealed
            if sealed.verdict.reason is not None
        }
        self.assertIn("INSUFFICIENT_BARS", reasons)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
