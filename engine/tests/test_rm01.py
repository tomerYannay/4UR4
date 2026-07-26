"""RM-01 — the corpus's only real-market evidence.  Its two halves differ in kind.

The synthetic set is spec-derived: it can prove the engine is self-consistent
with the written specification, not that the specification describes the object
the Product Owner drew.  RM-01 is 29 bars of real, undesigned prices.

**Non-circularity attaches to Half A ONLY, and this docstring used to claim it
for both.**  That was false, and it is the same overstatement class corrected in
:mod:`lemma_oracle` and :mod:`engine.causal` at this head -- found by the
Strategic gate (MJ-1), one file over from where the others were fixed.

* **Half A is the non-circular anchor**: real prices plus geometry a human
  approved.  Of it, "an engine fitted to the synthetic fixtures has no route to
  its answer except by implementing §8 correctly" is TRUE.
* **Half B (`expected-causal.json`) is replay-generated** -- produced by the
  quarantined causal reference model, the very artifact the engine must be
  independent of.  (Named only by role here: architectural test A3 forbids this
  package from spelling that path at all, and it caught the first draft of this
  docstring doing exactly that.)  Reproducing it earns **conformance credit
  only**: no
  independence credit (HD-15 condition 1 -- agreement with the model earns none)
  and no non-circularity credit (SPR-D-01 limit 3).  Half B is a regression guard
  against today's reference model, not independent verification, and the
  sentence above must not be read onto it.

Both halves are asserted, neither superseding the other:

* **A-clause** — the exported, pure §8 selector called directly on the full
  29-bar prefix returns ``B* = (25, 129.88)``, ``m = -0.0240143``,
  ``b = 5.46697``, 0 envelope violations.  Asserted at **unit level**, because a
  §21-conforming detector never reaches bar 25.
* **B-clause** — as-of-time behaviour, **within Phase-2-owned behaviour only**:
  the formation trace, the selection over bars 0-9, and ``line_at_stop`` at the
  **engine-derived** stop.  ``line_at_stop``, not ``Λ^F``; no ``BROKEN_OUT``
  state and no ``BREAKOUT_CONFIRMED`` reason code — those are Phase 3's.

**The stop index is derived here, never read.**  ``detect()`` is called with the
series and the parameters and nothing else; the fixture's ``stop_index`` is only
ever the right-hand side of a comparison.  If it were handed in, the B-clause
would assert nothing about the engine's own detection.
"""

from __future__ import annotations

import hashlib
import math
import os
import unittest

from ..detector import detect, prefix_of, second_anchor_over
from ..anchor import anchor_of
from ..envelope import envelope_violations
from ..logspace import sig6, y_hat
from ..params import DetectorParams
from ..state import LineState, ReasonCode
from .conformance import SPEC_VERSION, Report
from .fixtures_io import REAL_DIR, as_decimal, load_json, load_series, parse_gate_fields, real_fixture_ids

RM01 = os.path.join(REAL_DIR, "RM-01")


def _params(expected_causal, **overrides) -> DetectorParams:
    params = DetectorParams.from_fixture_params(
        expected_causal["params"], spec_version=SPEC_VERSION
    )
    return params.replace(**overrides) if overrides else params


class RealFixtureWalk(unittest.TestCase):
    """The ``real/*`` walk must FAIL on a missing artifact, never skip."""

    def test_every_real_fixture_carries_its_causal_contract(self) -> None:
        ids = real_fixture_ids()
        self.assertTrue(ids, "the real fixture walk found nothing")
        for fixture_id in ids:
            for required in ("input.csv", "expected-causal.json", "annotation.json"):
                self.assertTrue(
                    os.path.exists(os.path.join(REAL_DIR, fixture_id, required)),
                    "%s carries no %s — a real/* walk that finds no comparison "
                    "contract must fail, not pass vacuously" % (fixture_id, required),
                )

    def test_only_rm01_is_committed(self) -> None:
        # If this ever fails, a real fixture has been added and needs its own
        # assertions here.  Failing loudly beats silently covering one of two.
        self.assertEqual(real_fixture_ids(), ["RM-01"])


class RM01InputIntegrity(unittest.TestCase):
    def test_input_csv_matches_the_recorded_hash(self) -> None:
        expected_causal = load_json(os.path.join(RM01, "expected-causal.json"))
        binding = expected_causal["input_binding"]
        with open(os.path.join(RM01, "input.csv"), "rb") as handle:
            digest = hashlib.sha256(handle.read()).hexdigest()
        self.assertEqual(digest, binding["input_csv_sha256"])
        series = load_series(os.path.join(RM01, "input.csv"))
        self.assertEqual(len(series), binding["bar_count"])


class RM01HalfA(unittest.TestCase):
    """Full-series §8 geometry, at unit level on the exported pure selector."""

    def setUp(self) -> None:
        self.annotation = load_json(os.path.join(RM01, "annotation.json"))
        self.expected_causal = load_json(os.path.join(RM01, "expected-causal.json"))
        self.series = load_series(os.path.join(RM01, "input.csv"))
        self.eps = float(self.expected_causal["params"]["eps"])

    def test_full_series_hull(self) -> None:
        report = Report("RM-01 Half A")
        verified = self.annotation["verified_market_data"]

        prefix = prefix_of(self.series)
        self.assertEqual(len(prefix), 29)

        anchor = anchor_of(prefix)
        assert anchor is not None
        report.equal(anchor.t, verified["ath_anchor"]["t"], "anchor.t")
        report.price_equal(anchor.high, verified["ath_anchor"]["H"], "anchor.H")

        selection = second_anchor_over(prefix, anchor.t, self.eps)
        chosen = selection.selected
        if not report.check(chosen is not None, "no envelope-valid B* over the full prefix"):
            self.fail(report.render())
        assert chosen is not None
        report.equal(chosen.t, verified["second_anchor"]["t"], "B*.t")
        report.price_equal(chosen.high, verified["second_anchor"]["H"], "B*.H")
        report.sig6_equal(chosen.slope, verified["log_slope"], "log_slope")
        report.sig6_equal(chosen.intercept, verified["intercept"], "intercept")
        report.equal(
            envelope_violations(prefix, anchor.t, chosen, self.eps), 0, "envelope violations"
        )

        # The approved record's line at every bar, by date (29 values).
        for index in range(len(self.series)):
            date = self.series[index].timestamp
            price = math.exp(y_hat(chosen.slope, chosen.intercept, index))
            report.sig6_equal(price, verified["line_values"][date], "line(%s)" % date)

        self.assertTrue(report.ok, "\n" + report.render())

    def test_half_a_is_not_reachable_through_the_pipeline(self) -> None:
        """The A-clause is a unit assertion, and must not be restated as a
        pipeline one: a §21-conforming detector stops long before bar 25."""
        result = detect(self.series, _params(self.expected_causal))
        self.assertIsNotNone(result.stop_bar)
        self.assertLess(result.stop_bar, 25)
        assert result.reported_line is not None
        self.assertNotEqual(result.reported_line.t_b, 25)


class RM01HalfB(unittest.TestCase):
    """As-of-time behaviour, within Phase-2-owned behaviour only."""

    def setUp(self) -> None:
        self.expected = load_json(os.path.join(RM01, "expected-causal.json"))
        self.series = load_series(os.path.join(RM01, "input.csv"))
        self.params = _params(self.expected)
        # Called with the series and the parameters only.  Nothing about the
        # expected stop index reaches the engine.
        self.result = detect(self.series, self.params)

    def test_formation_and_gate_trace(self) -> None:
        report = Report("RM-01 Half B / formation")
        formation = self.expected["formation"]
        causal = self.result.causal
        assert causal is not None

        report.equal(causal.t_form, formation["t_form"], "t_form")

        sealed = causal.sealed_at(int(formation["t_form"]))
        if report.check(sealed is not None and sealed.line is not None, "no line at t_form"):
            assert sealed is not None and sealed.line is not None
            report.equal(sealed.line.t_b, formation["B_star_at_formation"]["t"], "B* at formation")
            report.price_equal(
                sealed.line.high_b, formation["B_star_at_formation"]["H"], "B* high at formation"
            )
            report.sig6_equal(
                sealed.line.m, formation["log_slope_at_formation"], "slope at formation"
            )

        engine_trace = {item.t: item.verdict.structural() for item in causal.sealed}
        compared = 0
        for entry in formation["gate_trace"]:
            parsed = parse_gate_fields(entry)
            t = parsed[0]
            if t not in engine_trace:
                continue
            compared += 1
            report.equal(engine_trace[t], parsed, "gate_trace t=%d" % t)
        report.equal(compared, len(formation["gate_trace"]), "gate_trace entries compared")

        self.assertTrue(report.ok, "\n" + report.render())

    def test_as_of_time_selection_bars_0_to_9(self) -> None:
        report = Report("RM-01 Half B / as-of-time selection")
        causal = self.result.causal
        assert causal is not None
        for entry in self.expected["as_of_time_selection"]:
            t = int(entry["t"])
            label = "t=%d" % t
            sealed = causal.sealed_at(t)
            if not report.check(sealed is not None, "%s: no sealed state" % label):
                continue
            assert sealed is not None
            if entry["B_star_t"] is None:
                report.equal(sealed.line, None, "%s: expected no line" % label)
                report.equal(
                    None if sealed.verdict.reason is None else sealed.verdict.reason.value,
                    entry["no_line_reason"],
                    "%s: no_line_reason" % label,
                )
                continue
            if not report.check(sealed.line is not None, "%s: engine produced no line" % label):
                continue
            assert sealed.line is not None
            report.equal(sealed.line.t_b, entry["B_star_t"], "%s: B*.t" % label)
            report.price_equal(sealed.line.high_b, entry["B_star_H"], "%s: B*.H" % label)
            report.sig6_equal(sealed.line.m, entry["log_slope"], "%s: log_slope" % label)
            report.sig6_equal(sealed.line.b, entry["intercept"], "%s: intercept" % label)
            report.sig6_equal(sealed.line.y_hat_at(t), entry["y_hat"], "%s: y_hat" % label)
            report.sig6_equal(sealed.line.price_at(t), entry["line"], "%s: line" % label)
        self.assertTrue(report.ok, "\n" + report.render())

    def test_reselections(self) -> None:
        report = Report("RM-01 Half B / reselections")
        causal = self.result.causal
        assert causal is not None
        engine = [
            (item.effective_bar, item.frm, item.to, sig6(item.m), bool(item.tie))
            for item in causal.reselections
        ]
        expected = [
            (int(item["effective_bar"]), int(item["from"]), int(item["to"]),
             as_decimal(item["log_slope"]), bool(item["tie"]))
            for item in self.expected["reselections"]
        ]
        report.equal(len(engine), len(expected), "reselection count")
        for index in range(max(len(engine), len(expected))):
            got = engine[index] if index < len(engine) else None
            want = expected[index] if index < len(expected) else None
            report.equal(got, want, "reselections[%d]" % index)
        self.assertTrue(report.ok, "\n" + report.render())

    def test_bar_9_pierces_and_wick_breaks(self) -> None:
        """The re-selection at bar 9 is what binds the line that judges bar 10."""
        codes_by_bar = {}
        for record in self.result.transitions:
            codes_by_bar.setdefault(record.bar, []).append(record.reason)
        self.assertIn(ReasonCode.WICK_BREAK, codes_by_bar.get(9, []))
        self.assertIn(ReasonCode.INVALID_PIERCE, self.result.reason_codes)

    def test_line_at_stop(self) -> None:
        report = Report("RM-01 Half B / line_at_stop")
        expected = self.expected["line_at_stop"]
        causal = self.result.causal
        assert causal is not None

        report.equal(self.result.stop_bar, expected["stop_index"], "engine-derived stop index")
        stop = causal.stop
        if not report.check(stop is not None, "engine produced no stop"):
            self.fail(report.render())
        assert stop is not None

        report.equal(stop.line.t_anchor, expected["A"]["t"], "line_at_stop.A.t")
        report.price_equal(stop.line.high_anchor, expected["A"]["H"], "line_at_stop.A.H")
        report.equal(stop.line.t_b, expected["B"]["t"], "line_at_stop.B.t")
        report.price_equal(stop.line.high_b, expected["B"]["H"], "line_at_stop.B.H")
        report.sig6_equal(stop.line.m, expected["log_slope"], "line_at_stop.log_slope")
        report.sig6_equal(stop.line.b, expected["intercept"], "line_at_stop.intercept")
        report.sig6_equal(stop.y_hat, expected["y_hat"], "line_at_stop.y_hat")
        report.sig6_equal(stop.line_value, expected["line"], "line_at_stop.line")
        report.price_equal(stop.close, expected["close"], "line_at_stop.close")
        report.sig6_equal(
            stop.clearance, expected["close_vs_line_log"], "line_at_stop.close_vs_line_log"
        )
        report.sig6_equal(
            stop.clearance_net_of_eps_break,
            expected["close_vs_line_plus_eps_break_log"],
            "line_at_stop.close_vs_line_plus_eps_break_log",
        )
        # The margin identity the record states: the two clearances differ by
        # exactly eps_break.  An engine asserting the documented 0.0864461
        # against the net field would fail by exactly 0.01.
        report.check(
            sig6(stop.clearance - stop.clearance_net_of_eps_break) == sig6(self.params.eps_break),
            "line_at_stop: margin identity (raw - net == eps_break)",
        )
        self.assertTrue(report.ok, "\n" + report.render())

    def test_not_asserted_fields_are_genuinely_absent(self) -> None:
        """SPR-D-01 limit 1, checked in both directions on the engine's side."""
        forbidden = set(self.expected["not_asserted"]["fields"])
        self.assertIn("frozen_line", forbidden)
        self.assertIn("BREAKOUT_CONFIRMED", forbidden)
        self.assertIsNone(self.result.final_state, "Phase 2 claims no final state at a stop")
        self.assertNotIn(ReasonCode.BREAKOUT_CONFIRMED, self.result.reason_codes)
        for record in self.result.transitions:
            self.assertNotIn(record.to, (LineState.BROKEN_OUT, LineState.RETESTED))
            self.assertNotIn(record.frm, (LineState.BROKEN_OUT, LineState.RETESTED))
        # And no record beyond the stop bar.
        for record in self.result.transitions:
            self.assertLessEqual(record.bar, self.result.stop_bar)

    def test_robustness_sweeps(self) -> None:
        report = Report("RM-01 Half B / robustness")
        robustness = self.expected["robustness"]

        for point in robustness["eps_break_sweep"]:
            result = detect(self.series, self.params.with_eps_break(float(point["eps_break"])))
            label = "eps_break=%s" % point["eps_break"]
            report.equal(
                None if result.causal is None else result.causal.t_form,
                point["t_form"], "%s: t_form" % label,
            )
            report.equal(result.stop_bar, point["stop_index"], "%s: stop_index" % label)

        for point in robustness["eps_sweep"]:
            result = detect(self.series, self.params.replace(eps=float(point["eps"])))
            label = "eps=%s" % point["eps"]
            report.equal(
                None if result.causal is None else result.causal.t_form,
                point["t_form"], "%s: t_form" % label,
            )
            report.equal(result.stop_bar, point["stop_index"], "%s: stop_index" % label)

        for point in robustness["min_formation_bars_sweep"]:
            result = detect(
                self.series,
                self.params.replace(min_formation_bars=int(point["min_formation_bars"])),
            )
            label = "min_formation_bars=%s" % point["min_formation_bars"]
            report.equal(
                None if result.causal is None else result.causal.t_form,
                point["t_form"], "%s: t_form" % label,
            )
            report.equal(result.stop_bar, point["stop_index"], "%s: stop_index" % label)

        self.assertTrue(report.ok, "\n" + report.render())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
