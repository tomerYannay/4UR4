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
* **B-clause** — as-of-time behaviour, **within the scope this record claims**:
  the formation trace, the selection over bars 0-9, and ``line_at_stop`` at the
  **engine-derived** stop.

  **The B-clause was RE-SCOPED for Phase 3, not weakened.**  It previously
  asserted that the engine produced no ``BROKEN_OUT`` state, no
  ``BREAKOUT_CONFIRMED`` code and no record after the stop.  SPR-D-01 limit 1
  says the claim is made "within Phase-2-owned behaviour only" and that those
  things are "Phase 3's to gate and are **not** claimed here" — a statement about
  the **scope of the claim**, not a prediction that the engine cannot produce
  them, and the record lists them under ``not_asserted``: *not asserted*, not
  *forbidden*.  Phase 2 implemented "not asserted" as "must not occur", which was
  a legitimate strengthening while the engine was incapable of it and is an
  over-reading now.

  The replacement is **stronger in the respect that matters**: instead of
  asserting that no post-breakout emission exists anywhere, it asserts that none
  exists strictly before the stop and that the **first** one is at exactly the
  bar the engine derived for itself.  Nothing is asserted about RM-01's post-stop
  behaviour, and a test asserts *that nothing is*.

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
from ..state import PHASE3_REASON_CODES, LineState, ReasonCode
from .conformance import SPEC_VERSION, Report
from .fixtures_io import (
    REAL_DIR,
    KeyTracker,
    all_key_paths,
    as_decimal,
    load_json,
    load_series,
    parse_gate_fields,
    real_fixture_ids,
    tracked,
)

RM01 = os.path.join(REAL_DIR, "RM-01")

#: Records every key path the B-clause reads out of ``expected-causal.json``.
#: Module-level and never reset, so :class:`RM01NotAssertedScope` can check the
#: SPR-D-01 limit-1 scope as a *measured* property of this test module rather
#: than as a hand-written list of "things we promise not to read".
RECORD_TRACKER = KeyTracker()


def _tracked_record():
    return tracked(load_json(os.path.join(RM01, "expected-causal.json")), RECORD_TRACKER)


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
        # Positive form of the same claim: §21 froze the line at bar 9, long
        # before bar 25 — so the A-clause's answer is unreachable through the
        # pipeline because the freeze happened, not merely because it is absent.
        assert result.frozen_line is not None
        self.assertEqual(result.frozen_line.line.t_b, 9)


class RM01HalfB(unittest.TestCase):
    """As-of-time behaviour, within Phase-2-owned behaviour only."""

    def setUp(self) -> None:
        self.expected = _tracked_record()
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

    def test_nothing_post_breakout_is_emitted_before_the_engine_derived_stop(self) -> None:
        """SPR-D-01 limit 1, re-scoped to the window the record actually claims.

        Two assertions, and the second is the one that is *stronger* than what it
        replaces: no post-breakout state or code appears strictly before the
        engine-derived stop, **and** the first that appears is at exactly that
        bar.  The engine must not merely avoid post-breakout behaviour early — it
        must place the boundary at precisely the index it derived for itself,
        from the series and the parameters alone.
        """
        stop_bar = self.result.stop_bar
        self.assertIsNotNone(stop_bar)
        post_breakout_states = (
            LineState.BROKEN_OUT,
            LineState.RETESTED,
            LineState.FAILED_BREAKOUT,
        )
        for record in self.result.transitions:
            if record.bar < stop_bar:
                self.assertNotIn(record.to, post_breakout_states, record)
                self.assertNotIn(record.frm, post_breakout_states, record)
                self.assertNotIn(record.reason, PHASE3_REASON_CODES, record)
        first_post_breakout = [
            record.bar
            for record in self.result.transitions
            if record.reason in PHASE3_REASON_CODES
        ]
        self.assertTrue(first_post_breakout, "the engine emitted no breakout at all")
        self.assertEqual(
            min(first_post_breakout),
            stop_bar,
            "the first post-breakout emission is not at the engine-derived stop",
        )

    def test_the_frozen_line_is_the_line_at_stop(self) -> None:
        """The Phase-2/Phase-3 bridge, converted from a risk into an assertion.

        ``Λ^F`` is built by **wrapping** the object the stop already holds, so the
        line this file asserts field-by-field in ``test_line_at_stop`` and the
        line the golden fixtures assert as ``frozen_event_line`` are the same
        object.  Computed independently they could drift, and both gates would
        still pass — on different numbers.

        Nothing here reads a ``frozen_line`` key from the record: RM-01 carries
        none, and under HD-22 none may be added to accommodate the engine.  The
        comparison is against ``line_at_stop``, which the record does assert.
        """
        self.assertIsNotNone(self.result.frozen_line)
        assert self.result.frozen_line is not None
        self.assertIs(self.result.frozen_line.line, self.result.line_at_stop)
        self.assertEqual(self.result.frozen_line.breakout_bar, self.result.stop_bar)
        self.assertEqual(self.result.frozen_line.confirmed_bar, self.result.stop_bar)
        self.assertEqual(
            self.result.frozen_line.tolerance_version, self.params.tolerance_version
        )
        self.assertEqual(len(self.result.episodes), 1)

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


class RM01NotAssertedScope(unittest.TestCase):
    """SPR-D-01 limit 1 as a **checkable property of this test module**.

    The record names five fields under ``not_asserted``.  Phase 2 honoured that
    by asserting the engine could not produce them, which was an over-reading.
    Phase 3 honours it the way the record states it: **this module reads none of
    those fields out of the record**, and the record carries none of them.  Both
    halves are computed from the record itself rather than hand-listed, so
    neither can drift.

    The B-clause's own tests are re-run inside this one so that the measured read
    set is complete regardless of the order the runner happens to choose.
    """

    def _read_paths(self) -> set:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(RM01HalfB)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.errors, [], result.errors)
        self.assertEqual(result.failures, [], result.failures)
        return set(RECORD_TRACKER.read)

    def test_the_module_reads_no_field_the_record_declares_unasserted(self) -> None:
        record = load_json(os.path.join(RM01, "expected-causal.json"))
        not_asserted = list(record["not_asserted"]["fields"])
        self.assertTrue(not_asserted, "the not_asserted list is empty; nothing is scoped")
        read = self._read_paths()
        self.assertTrue(read, "the tracker recorded nothing; the check is vacuous")
        touched = sorted(
            path
            for path in read
            for field_name in not_asserted
            if path.split(".")[-1] == field_name
        )
        self.assertEqual(
            touched,
            [],
            "the RM-01 suite reads a field the record declares NOT ASSERTED — "
            "SPR-D-01 limit 1 scopes the claim, and reading one of these would "
            "quietly widen it",
        )

    def test_the_record_carries_none_of_those_fields(self) -> None:
        """The other direction, which is the record's own stated contract: it
        fails if the fixture starts carrying a forbidden field.  Under HD-22 the
        remedy would be an escalation, never an edit."""
        record = load_json(os.path.join(RM01, "expected-causal.json"))
        not_asserted = set(record["not_asserted"]["fields"])
        present = {path.split(".")[-1] for path in all_key_paths(record)}
        self.assertEqual(
            sorted(present & not_asserted),
            [],
            "RM-01 now carries a field its own not_asserted list names",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
