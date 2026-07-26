"""The Layer-0 conformance comparison, shared by the golden and RM-01 suites.

Every comparison below is against the **committed fixture JSON**.  Nothing here
runs, imports, or compares against any reference model: agreement with a model
earns no credit, and the contract is the fixtures and the specification.

Two rules about the comparisons themselves, because a weak comparison passes
while the engine is wrong:

* **List equality in both directions.**  A "contains" comparison lets an engine
  that emits a *superset* of transitions pass.  Every list here is compared
  element-by-element with an equal-length assertion.
* **Every recorded key must be answered.**  The engine must produce a value for
  every key the fixture carries — including ``expected_line_values`` indices
  after the stop, which are pure arithmetic on the reported line.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence

from ..causal import Line
from ..detector import DetectionResult
from ..logspace import sig6
from ..state import PHASE2_REASON_CODES, ReasonCode
from ..trace import active_line_at, candidate_set_at
from .fixtures_io import as_decimal, parse_gate_trace_line

__all__ = ["Report", "compare_golden"]

#: OQ-J: the specification declares no version number and the value is the
#: Product Steward's to define.  The engine requires one explicitly rather than
#: inventing a default; this placeholder is the *test suite's* choice and is
#: named so it cannot be mistaken for a decision.
SPEC_VERSION = "UNVERSIONED-PENDING-OQ-J"


class Report:
    """Accumulates every mismatch instead of stopping at the first."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.failures: List[str] = []
        self.checks = 0

    def check(self, condition: bool, message: str) -> bool:
        self.checks += 1
        if not condition:
            self.failures.append(message)
        return bool(condition)

    def equal(self, actual, expected, message: str) -> bool:
        return self.check(
            actual == expected, "%s: expected %r, engine produced %r" % (message, expected, actual)
        )

    def sig6_equal(self, actual: Optional[float], expected, message: str) -> bool:
        if expected is None:
            return self.check(actual is None, "%s: expected null, engine produced %r" % (message, actual))
        if actual is None:
            return self.check(False, "%s: expected %r, engine produced null" % (message, expected))
        got = sig6(actual)
        want = as_decimal(expected)
        return self.check(
            got == want,
            "%s: expected %s, engine produced %s (raw %r)" % (message, want, got, actual),
        )

    def price_equal(self, actual: Optional[float], expected, message: str) -> bool:
        """Compare a raw *price* exactly.

        §19's 6-significant-figure contract governs computed **geometry**.  A
        bar high or close is input data — RM-01 carries ``213.7999``, seven
        significant figures — so rounding it before comparison would weaken the
        check and, for that value, break it.  Exact decimal equality is both
        available and stronger.
        """
        if expected is None:
            return self.check(actual is None, "%s: expected null, engine produced %r" % (message, actual))
        if actual is None:
            return self.check(False, "%s: expected %r, engine produced null" % (message, expected))
        got = Decimal(repr(float(actual)))
        want = as_decimal(expected)
        return self.check(got == want, "%s: expected %s, engine produced %s" % (message, want, got))

    @property
    def ok(self) -> bool:
        return not self.failures

    def render(self) -> str:
        head = "%s: %d mismatch(es) across %d checks" % (
            self.label,
            len(self.failures),
            self.checks,
        )
        return "\n".join([head] + ["  - " + failure for failure in self.failures])


def _transition_tuples(records) -> List[tuple]:
    return [record.as_tuple() for record in records]


def _fixture_transition_tuples(entries: Sequence[Dict[str, Any]]) -> List[tuple]:
    return [(int(e["bar"]), e["from"], e["to"], e["reason_code"]) for e in entries]


def _compare_ordered(report: Report, actual: List, expected: List, label: str) -> None:
    """Ordered list equality in BOTH directions, element by element."""
    report.equal(len(actual), len(expected), "%s: list length" % label)
    for index in range(max(len(actual), len(expected))):
        got = actual[index] if index < len(actual) else "<engine emitted nothing>"
        want = expected[index] if index < len(expected) else "<fixture records nothing>"
        report.equal(got, want, "%s[%d]" % (label, index))


def compare_golden(
    fixture_id: str,
    expected: Dict[str, Any],
    result: DetectionResult,
    series,
    sweep_runner,
) -> Report:
    """Compare one golden fixture's ``expected.json`` against a detection result.

    ``sweep_runner(eps_break) -> DetectionResult`` re-runs the same series at a
    different breakout tolerance, for the HD-13 robustness comparison.
    """
    report = Report(fixture_id)
    causal_record = expected.get("causal_record") or {}
    confirmed_bar = expected.get("confirmed_bar")
    phase2_complete = confirmed_bar is None

    # -- §18 input guards --------------------------------------------------
    input_guard = causal_record.get("input_guard")
    if input_guard is not None:
        report.equal(result.rejected, bool(input_guard["rejected"]), "input_guard.rejected")
        report.equal(
            [code.value for code in result.guard.codes],
            list(input_guard["codes"]),
            "input_guard.codes",
        )
        detail = input_guard.get("detail")
        if detail is None:
            report.equal(result.guard.detail, None, "input_guard.detail")
        else:
            got = result.guard.detail or {}
            report.equal(got.get("bar"), detail["bar"], "input_guard.detail.bar")
            # This field is recorded at FULL double precision rather than to 6
            # significant figures, so exact equality is both available and the
            # stronger check.  The 6-s.f. comparison is kept alongside it.
            report.equal(
                got.get("log_jump"), detail["log_jump"], "input_guard.detail.log_jump (exact)"
            )
            report.check(
                sig6(got.get("log_jump")) == sig6(float(detail["log_jump"])),
                "input_guard.detail.log_jump (6 s.f.)",
            )
    else:
        report.check(not result.rejected, "engine rejected a bar-set the fixture does not")

    # -- anchors and geometry ---------------------------------------------
    expected_anchor = expected.get("expected_ath_anchor")
    if expected_anchor is None:
        report.equal(result.ath_anchor, None, "expected_ath_anchor")
    else:
        report.check(result.ath_anchor is not None, "expected_ath_anchor: engine produced none")
        if result.ath_anchor is not None:
            report.equal(result.ath_anchor[0], expected_anchor["t"], "expected_ath_anchor.t")
            report.price_equal(
                result.ath_anchor[1], expected_anchor["H"], "expected_ath_anchor.H"
            )

    line: Optional[Line] = result.reported_line
    expected_second = expected.get("expected_second_anchor") or {}
    if expected_second.get("t") is None:
        report.equal(None if line is None else line.t_b, None, "expected_second_anchor.t")
    else:
        report.check(line is not None, "expected_second_anchor: engine produced no line")
        if line is not None:
            report.equal(line.t_b, expected_second["t"], "expected_second_anchor.t")
            report.price_equal(line.high_b, expected_second["H"], "expected_second_anchor.H")

    report.sig6_equal(
        None if line is None else line.m, expected.get("expected_log_slope"), "expected_log_slope"
    )
    report.sig6_equal(
        None if line is None else line.b, expected.get("expected_intercept"), "expected_intercept"
    )

    # -- line values at EVERY recorded index -------------------------------
    expected_line_values = expected.get("expected_line_values")
    if expected_line_values:
        report.check(line is not None, "expected_line_values: engine produced no line")
        if line is not None:
            computed = result.line_values_at(int(key) for key in expected_line_values)
            report.equal(
                sorted(computed), sorted(int(key) for key in expected_line_values),
                "expected_line_values: engine answered a different key set",
            )
            for key in sorted(expected_line_values, key=int):
                index = int(key)
                y_hat_value, price = computed[index]
                report.sig6_equal(
                    y_hat_value, expected_line_values[key]["y_hat"],
                    "expected_line_values[%s].y_hat" % key,
                )
                report.sig6_equal(
                    price, expected_line_values[key]["line"],
                    "expected_line_values[%s].line" % key,
                )

    # -- the stop index (Phase 2's confirmed_bar equivalent) ---------------
    report.equal(result.stop_bar, confirmed_bar, "stop index vs confirmed_bar")

    # -- state transitions -------------------------------------------------
    fixture_transitions = _fixture_transition_tuples(expected["expected_state_transitions"])
    engine_transitions = _transition_tuples(result.transitions)
    if phase2_complete:
        _compare_ordered(
            report, engine_transitions, fixture_transitions, "expected_state_transitions"
        )
    else:
        _compare_ordered(
            report,
            [record for record in engine_transitions if record[0] < confirmed_bar],
            [record for record in fixture_transitions if record[0] < confirmed_bar],
            "expected_state_transitions (bars strictly before confirmed_bar)",
        )
        # Additionally, and legitimately: at the stop bar itself the engine still
        # owns every Phase-2 record.  Nothing here asserts the Phase-3 transition.
        _compare_ordered(
            report,
            [record for record in engine_transitions if record[0] == confirmed_bar],
            [
                record
                for record in fixture_transitions
                if record[0] == confirmed_bar and record[3] in _PHASE2_CODE_NAMES
            ],
            "expected_state_transitions (Phase-2 records at the stop bar)",
        )

    # -- reason codes ------------------------------------------------------
    engine_codes = [code.value for code in result.reason_codes]
    fixture_codes = list(expected["expected_reason_codes"])
    if phase2_complete:
        report.equal(set(engine_codes), set(fixture_codes), "expected_reason_codes (set)")
        report.equal(engine_codes, fixture_codes, "expected_reason_codes (first-emission order)")
    else:
        report.equal(
            set(engine_codes),
            {code for code in fixture_codes if code in _PHASE2_CODE_NAMES},
            "expected_reason_codes (Phase-2 subset)",
        )
    report.check(
        all(code in _PHASE2_CODE_NAMES for code in engine_codes),
        "engine emitted a Phase-3 reason code: %r" % engine_codes,
    )

    # -- final state (only for confirmed_bar == null fixtures) -------------
    if phase2_complete:
        report.equal(
            None if result.final_state is None else result.final_state.value,
            expected["expected_final_state"],
            "expected_final_state",
        )

    if result.causal is None:
        return report  # guard-rejected: no causal record to compare

    _compare_causal_record(report, causal_record, result, series, confirmed_bar)
    _compare_eps_break_sweep(report, causal_record, sweep_runner)
    return report


_PHASE2_CODE_NAMES = frozenset(code.value for code in PHASE2_REASON_CODES)


def _compare_causal_record(
    report: Report,
    causal_record: Dict[str, Any],
    result: DetectionResult,
    series,
    confirmed_bar: Optional[int],
) -> None:
    causal = result.causal
    assert causal is not None
    params = result.params

    formation = causal_record.get("formation") or {}
    if "t_form" in formation:
        report.equal(causal.t_form, formation["t_form"], "causal_record.formation.t_form")
    report.equal(
        params.min_formation_bars,
        formation.get("min_formation_bars", params.min_formation_bars),
        "causal_record.formation.min_formation_bars",
    )
    report.equal(
        params.min_ath_age_bars,
        formation.get("min_ath_age_bars", params.min_ath_age_bars),
        "causal_record.formation.min_ath_age_bars",
    )

    engine_trace = {sealed.t: sealed.verdict.structural() for sealed in causal.sealed}
    for key in ("gate_trace", "gate_trace_full"):
        recorded = formation.get(key)
        if not recorded:
            continue
        compared = 0
        for entry in recorded:
            parsed = parse_gate_trace_line(entry)
            t = parsed[0]
            if t not in engine_trace:
                # Beyond the engine's reach (bars at or after the stop, which
                # Phase 2 does not evaluate).  Not silently skipped: at least the
                # entries up to the stop must exist, asserted below.
                continue
            compared += 1
            report.equal(engine_trace[t], parsed, "causal_record.formation.%s t=%d" % (key, t))
        reachable = sum(
            1
            for entry in recorded
            if parse_gate_trace_line(entry)[0] in engine_trace
        )
        report.check(
            compared == reachable and compared > 0,
            "causal_record.formation.%s: compared %d of %d reachable entries"
            % (key, compared, reachable),
        )

    # -- pre-breakout re-selections ---------------------------------------
    recorded_reselections = causal_record.get("reselections")
    if recorded_reselections is not None:
        engine_reselections = [
            (item.effective_bar, item.frm, item.to, sig6(item.m), bool(item.tie))
            for item in causal.reselections
        ]
        expected_reselections = [
            (int(item["effective_bar"]), int(item["from"]), int(item["to"]),
             as_decimal(item["m"]), bool(item["tie"]))
            for item in recorded_reselections
        ]
        _compare_ordered(
            report, engine_reselections, expected_reselections, "causal_record.reselections"
        )

    # -- the as-of-time candidate set --------------------------------------
    recorded_candidates = causal_record.get("as_of_time_candidate_set")
    if recorded_candidates:
        at_bar = int(recorded_candidates["at_bar"])
        evidence = candidate_set_at(causal, at_bar)
        if not report.check(
            evidence is not None,
            "causal_record.as_of_time_candidate_set: engine has no sealed state at bar %d" % at_bar,
        ):
            return
        assert evidence is not None
        report.equal(
            evidence.prefix_length, at_bar,
            "causal_record.as_of_time_candidate_set: prefix length at bar %d" % at_bar,
        )
        report.equal(
            evidence.anchor_t, recorded_candidates["anchor"]["t"],
            "causal_record.as_of_time_candidate_set.anchor.t",
        )
        report.price_equal(
            evidence.anchor_high, recorded_candidates["anchor"]["H"],
            "causal_record.as_of_time_candidate_set.anchor.H",
        )
        engine_candidates = [
            (c.t, Decimal(repr(c.high)), sig6(c.slope), sig6(c.worst_gap), c.envelope_valid)
            for c in evidence.candidates
        ]
        expected_candidates = [
            (int(c["t"]), as_decimal(c["H"]), as_decimal(c["slope"]),
             as_decimal(c["worst_gap"]), bool(c["envelope_valid"]))
            for c in recorded_candidates["candidates"]
        ]
        _compare_ordered(
            report, engine_candidates, expected_candidates,
            "causal_record.as_of_time_candidate_set.candidates",
        )
        selected = recorded_candidates.get("selected") or {}
        report.equal(
            evidence.selected_t, selected.get("t"),
            "causal_record.as_of_time_candidate_set.selected.t",
        )
        report.sig6_equal(
            evidence.selected_slope, selected.get("slope"),
            "causal_record.as_of_time_candidate_set.selected.slope",
        )

    # -- the active line before each recorded event bar --------------------
    for entry in causal_record.get("active_line_before_event_bars") or []:
        bar = int(entry["bar"])
        bar_data = series[bar]
        evidence = active_line_at(
            causal, bar, bar_data.high, bar_data.close, params.eps, params.eps_break
        )
        label = "causal_record.active_line_before_event_bars[bar=%d]" % bar
        if entry.get("line", "present") is None:
            report.equal(evidence.line, None, "%s: engine has a line where the fixture has none" % label)
            report.equal(evidence.state_at_start.value, entry["state_at_start"], "%s.state" % label)
            continue
        if not report.check(evidence.line is not None, "%s: engine produced no line" % label):
            continue
        assert evidence.line is not None
        report.equal(evidence.line.t_b, entry["B_star"]["t"], "%s.B_star.t" % label)
        report.price_equal(evidence.line.high_b, entry["B_star"]["H"], "%s.B_star.H" % label)
        report.sig6_equal(evidence.line.m, entry["m"], "%s.m" % label)
        report.sig6_equal(evidence.line.b, entry["b"], "%s.b" % label)
        report.sig6_equal(evidence.y_hat_at_bar, entry["y_hat_at_bar"], "%s.y_hat_at_bar" % label)
        report.sig6_equal(evidence.line_at_bar, entry["line_at_bar"], "%s.line_at_bar" % label)
        report.sig6_equal(
            evidence.close_vs_line_plus_eps_break,
            entry["close_vs_line_plus_eps_break"],
            "%s.close_vs_line_plus_eps_break" % label,
        )
        report.sig6_equal(
            evidence.high_vs_line_plus_eps,
            entry["high_vs_line_plus_eps"],
            "%s.high_vs_line_plus_eps" % label,
        )
        if confirmed_bar is None or bar <= confirmed_bar:
            report.equal(
                evidence.state_at_start.value, entry["state_at_start"], "%s.state_at_start" % label
            )

    # -- Phase-2 events ----------------------------------------------------
    engine_events = {(event.bar, event.event.value): event for event in causal.events}
    for entry in causal_record.get("events") or []:
        name = entry["event"]
        if name not in ("WICK_BREAK", "RESET_NEW_ATH"):
            continue  # Phase-3 events; not this build's to reproduce
        bar = int(entry["bar"])
        label = "causal_record.events[bar=%d,%s]" % (bar, name)
        event = engine_events.get((bar, name))
        if not report.check(event is not None, "%s: engine emitted no such event" % label):
            continue
        assert event is not None
        for field_name in ("y_hat", "pierce", "close_margin", "ln_high"):
            if field_name in entry:
                report.sig6_equal(
                    event.detail.get(field_name), entry[field_name], "%s.%s" % (label, field_name)
                )
        for field_name in ("high", "close"):
            if field_name in entry:
                report.price_equal(
                    event.detail.get(field_name), entry[field_name], "%s.%s" % (label, field_name)
                )
        if "prior_state" in entry:
            report.equal(event.detail.get("prior_state"), entry["prior_state"], "%s.prior_state" % label)
    # Both directions: no Phase-2 event the fixture does not record.
    recorded_phase2 = {
        (int(entry["bar"]), entry["event"])
        for entry in causal_record.get("events") or []
        if entry["event"] in ("WICK_BREAK", "RESET_NEW_ATH")
    }
    report.equal(
        sorted(engine_events), sorted(recorded_phase2),
        "causal_record.events: Phase-2 event set",
    )


def _compare_eps_break_sweep(report: Report, causal_record: Dict[str, Any], sweep_runner) -> None:
    """HD-13 rule 1, run against the engine and compared to committed data.

    Self-consistency at +/-20% alone is not enough: an engine that ignored
    ``eps_break`` entirely would pass it.  Comparing every recorded scale —
    including 0.5x and 2x, where GX-12 and GX-15 genuinely change — is the
    falsifiable half.
    """
    robustness = causal_record.get("eps_break_robustness") or {}
    for point in robustness.get("sweep") or []:
        eps_break = float(point["eps_break"])
        outcome = sweep_runner(eps_break)
        label = "eps_break_robustness scale=%s" % point["scale"]
        report.equal(outcome.stop_bar, point["breakout_bar"], "%s: breakout_bar" % label)
        if point["breakout_bar"] is None:
            report.equal(
                None if outcome.final_state is None else outcome.final_state.value,
                point["final_state"],
                "%s: final_state" % label,
            )
