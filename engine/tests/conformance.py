"""The Layer-0 conformance comparison, shared by the golden and RM-01 suites.

Every comparison below is against the **committed fixture JSON**.  Nothing here
runs, imports, or compares against any reference model: agreement with a model
earns no credit, and the contract is the fixtures and the specification.

Three rules about the comparisons themselves, because a weak comparison passes
while the engine is wrong:

* **List equality in both directions.**  A "contains" comparison lets an engine
  that emits a *superset* of transitions pass.  Every list here is compared
  element-by-element with an equal-length assertion.
* **Every fixture is compared in full.**  There is no longer a branch that
  narrows the comparison for fixtures with a non-null ``confirmed_bar``: the
  whole transition list, the whole reason-code list in first-emission order, the
  final state, the frozen event line, every event and every sweep point are
  compared for all 23 fixtures alike.
* **Every recorded key must be answered, or declared unread.**  The set of keys
  no assertion reads is *measured* (see :mod:`fixtures_io`'s tracker) and
  compared against :data:`UNASSERTED_KEY_ALLOW_LIST` in both directions — a key
  that is unasserted and not on the list fails, and a list entry that has become
  asserted, or that no fixture carries any more, fails too.  Silence is the
  failure mode that rule exists to remove.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..detector import DetectionResult
from ..line import Line
from ..logspace import SPLIT_LOG_JUMP_THRESHOLD, ln_price, sig6, y_hat
from ..params import POST_BREAKOUT_FIXTURE_PARAMS, DetectorParams
from ..state import LineState, ReasonCode
from ..trace import active_line_at, candidate_set_at
from .fixtures_io import as_decimal, parse_gate_trace_line

__all__ = [
    "Report",
    "compare_golden",
    "LEGAL_TRANSITIONS",
    "UNASSERTED_KEY_ALLOW_LIST",
    "SPEC_VERSION",
]

#: OQ-J: the specification declares no version number and the value is the
#: Product Steward's to define.  The engine requires one explicitly rather than
#: inventing a default; this placeholder is the *test suite's* choice and is
#: named so it cannot be mistaken for a decision.  §22.1 rules that a real
#: ``spec_version`` must be minted before any engine pins one, in a change that
#: can move the specification header, this constant and the value fixtures
#: record together — which a code-only change cannot do.
SPEC_VERSION = "UNVERSIONED-PENDING-OQ-J"


#: §11's edge list, transcribed — ``(from, to)`` to the reason codes §11 draws on
#: that edge.  Used to assert that every emitted sequence is a **valid walk**
#: (§21.6 rule 3), which the schema describes and nothing in ``engine/`` checked
#: before Phase 3.
#:
#: Two edges here are worth naming because no fixture exercises them:
#:
#: * ``BROKEN_OUT``/``RETESTED`` → ``NONE`` on ``RESET_NEW_ATH``.  §21.5 and
#:   §21.7 both drew it while §11's diagram omitted it until 2026-07-28; the
#:   diagram was corrected rather than the behaviour, because §21.6 rule 3 would
#:   otherwise have rejected correct behaviour.  GX-06 and GX-22 both reset from
#:   ``ACTIVE``.
#: * ``FAILED_BREAKOUT`` → ``NONE`` on either exit (HD-25).  No fixture has a
#:   post-failure new ATH and none has a tail reaching ``E_expiry``.
#:
#: And one edge deliberately absent: there is **no** ``RETESTED`` →
#: ``FAILED_BREAKOUT``.  §15's predicate carries no state qualifier, so a close
#: below ``ŷ_F − ε_fail`` after a held retest is arithmetically inside the
#: failure window — but §11 draws no such edge, OQ-P3-3 reaches ``RETESTED`` at
#: most once per episode, and §16 condition 3 agrees.  The corpus pins it
#: neither way.
LEGAL_TRANSITIONS: Dict[Tuple[LineState, LineState], Tuple[ReasonCode, ...]] = {
    (LineState.NONE, LineState.ACTIVE): (ReasonCode.LINE_ESTABLISHED,),
    (LineState.NONE, LineState.NONE): (
        ReasonCode.INSUFFICIENT_BARS,
        ReasonCode.ATH_TOO_RECENT,
        ReasonCode.NO_VALID_SECOND_ANCHOR,
        ReasonCode.SUSPECTED_UNADJUSTED_SPLIT,
        ReasonCode.INVALID_PRICE,
        ReasonCode.INVALID_INPUT,
    ),
    (LineState.ACTIVE, LineState.ACTIVE): (
        ReasonCode.LINE_ESTABLISHED,
        ReasonCode.ENVELOPE_TIE_LATER,
        ReasonCode.WICK_BREAK,
    ),
    (LineState.ACTIVE, LineState.BROKEN_OUT): (ReasonCode.BREAKOUT_CONFIRMED,),
    (LineState.ACTIVE, LineState.NONE): (
        # §21.7 (new ATH) and §21.6's ⊥ clause / §10.4, which returns an ACTIVE
        # line to NONE when the recomputation over S_{t+1} finds no valid B*.
        ReasonCode.RESET_NEW_ATH,
        ReasonCode.NO_VALID_SECOND_ANCHOR,
        ReasonCode.ATH_TOO_RECENT,
        ReasonCode.INSUFFICIENT_BARS,
    ),
    (LineState.BROKEN_OUT, LineState.RETESTED): (ReasonCode.RETEST_HELD,),
    (LineState.BROKEN_OUT, LineState.FAILED_BREAKOUT): (ReasonCode.FAILED_BREAKOUT,),
    (LineState.BROKEN_OUT, LineState.NONE): (
        ReasonCode.EXPIRED_POST_BREAKOUT,
        ReasonCode.RESET_NEW_ATH,
    ),
    (LineState.RETESTED, LineState.NONE): (
        ReasonCode.EXPIRED_POST_BREAKOUT,
        ReasonCode.RESET_NEW_ATH,
    ),
    (LineState.FAILED_BREAKOUT, LineState.NONE): (
        ReasonCode.EXPIRED_POST_BREAKOUT,
        ReasonCode.RESET_NEW_ATH,
    ),
}


#: OQ-P3-7 — every recorded key that **no assertion reads**, declared with the
#: reason it is not read.  The census that checks this is mechanical, and it
#: fails in **both** directions: an unasserted key missing from this list fails,
#: and a listed key that has become asserted, or that no fixture carries any
#: more, fails too — so the list cannot rot into a blanket exemption.
#:
#: Four groups, and no fifth:
#:
#: 1. **Confidence-layer output the engine does not produce.**  ``flags``
#:    (``LOW_VOLUME`` on GX-11, ``NOT_RETESTED`` on GX-17) belongs to the
#:    confidence specification by §13.3 and §13.4, which put persistence and
#:    volume outside validity.  It is listed HERE, explicitly, rather than
#:    passed over in silence — that distinction is the whole of OQ-P3-7.
#: 2. **Prose.**  Human explanation, rationale and formula restatements.  The
#:    engine reproduces *values*, never another implementation's wording;
#:    requiring string equality would make "match the reference model's log
#:    formatting" part of the correctness contract.
#: 3. **Descriptive, ruled non-authoritative.**  The pivot context, which §5,
#:    D-TL-03 and HD-11 declare cannot affect selection, eligibility or any
#:    event.  Its one *derived* member, ``b_star_bar``, IS asserted.
#: 4. **A declaration about the input data rather than about the engine.**  The
#:    adjustment basis is carried on ``Provenance`` and checked there (HD-01);
#:    the fixture states it in prose form for a human reader.
UNASSERTED_KEY_ALLOW_LIST: Tuple[str, ...] = (
    # -- 1. confidence layer (§13.3, §13.4; OQ-P3-7) ------------------------
    "flags",
    # -- 2. prose ------------------------------------------------------------
    "purpose",
    "category",
    "spec_refs",
    "expected_second_anchor.reason",
    "rejection_rationale",
    "rejection_rationale[].candidate",
    "rejection_rationale[].rejected_because",
    "rejection_rationale[].numeric",
    "geometry_check.slope_formula",
    "geometry_check.intercept_formula",
    "geometry_check.key_inequalities",
    "geometry_check.notes",
    "params.eps_break_note",
    "params.formation_params_note",
    "causal_record.semantics",
    "causal_record.note",
    "causal_record.formation.rule",
    "causal_record.formation.gate_trace_full_caveat",
    "causal_record.as_of_time_candidate_set.note",
    "causal_record.no_anchor_proof.note",
    "causal_record.non_retroactive_challengers.note",
    "causal_record.frozen_event_line.binding",
    "causal_record.active_line_before_event_bars[].line_source",
    "causal_record.active_line_before_event_bars[].reason",
    # -- 3. descriptive, ruled non-authoritative (§5, D-TL-03, HD-11) --------
    "params.k",
    "causal_record.pivot_context.k",
    "causal_record.pivot_context.definition",
    "causal_record.pivot_context.confirmed_pivots_full_series",
    "causal_record.pivot_context.confirmed_pivots_in_formation_prefix",
    "causal_record.pivot_context.b_star_is_confirmed_pivot",
    "causal_record.pivot_context.note",
    # -- 4. a declaration about the input, not about the engine (HD-01) ------
    "input_convention.adjustment_basis",
)


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

    def exact_equal(self, actual: Optional[float], expected, message: str) -> bool:
        """Compare at FULL double precision.

        ``causal_record.events[].line`` records ``m`` and ``b`` as full repr
        doubles rather than to 6 significant figures.  That is a stronger
        comparison and it is available, so it is taken — alongside the 6-s.f.
        one, the same both-ways pattern ``input_guard.detail.log_jump`` uses.
        """
        if expected is None:
            return self.check(actual is None, "%s: expected null, engine produced %r" % (message, actual))
        if actual is None:
            return self.check(False, "%s: expected %r, engine produced null" % (message, expected))
        return self.check(
            float(actual) == float(expected),
            "%s: expected %r, engine produced %r" % (message, expected, actual),
        )

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

    report.equal(expected["fixture_id"], fixture_id, "fixture_id vs directory name")
    _compare_input_convention(report, expected, series)
    _compare_params(report, expected, result.params)

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
    _compare_geometry_check(report, expected, line)

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

    # -- the two bar indices, which are NOT the same quantity ---------------
    # ``stop_bar`` is the FIRST bar at which §13.1's predicate held;
    # ``confirmed_bar`` is the LATEST episode's freeze bar (§21.4, OQ-P3-5).
    # Every committed fixture has at most one episode, so both are compared
    # against the same recorded value here — and the engine keeps them distinct.
    report.equal(result.confirmed_bar, confirmed_bar, "confirmed_bar")
    report.equal(result.stop_bar, confirmed_bar, "engine-derived stop vs confirmed_bar")
    report.equal(expected.get("breakout_bar"), confirmed_bar, "breakout_bar == confirmed_bar (HD-03)")

    # -- state transitions, IN FULL and in both directions ------------------
    fixture_transitions = _fixture_transition_tuples(expected["expected_state_transitions"])
    engine_transitions = _transition_tuples(result.transitions)
    _compare_ordered(
        report, engine_transitions, fixture_transitions, "expected_state_transitions"
    )
    _assert_valid_walk(report, result)

    # -- reason codes, as a set AND in first-emission order ------------------
    engine_codes = [code.value for code in result.reason_codes]
    fixture_codes = list(expected["expected_reason_codes"])
    report.equal(set(engine_codes), set(fixture_codes), "expected_reason_codes (set)")
    report.equal(engine_codes, fixture_codes, "expected_reason_codes (first-emission order)")
    report.check(
        all(code in _CLOSED_CODE_NAMES for code in engine_codes),
        "engine emitted a code outside the schema's closed set: %r" % engine_codes,
    )

    # -- final state, for EVERY fixture -------------------------------------
    report.equal(
        None if result.final_state is None else result.final_state.value,
        expected["expected_final_state"],
        "expected_final_state",
    )

    if result.causal is None:
        return report  # guard-rejected: no causal record to compare

    _compare_causal_record(report, causal_record, result, series)
    _compare_frozen_event_line(report, causal_record, result)
    _compare_challengers(report, causal_record, result)
    _compare_eps_break_sweep(report, causal_record, result, sweep_runner)
    return report


_CLOSED_CODE_NAMES = frozenset(code.value for code in ReasonCode)


def _compare_input_convention(report: Report, expected: Dict[str, Any], series) -> None:
    convention = expected.get("input_convention") or {}
    if "bar_count" in convention:
        report.equal(len(series), convention["bar_count"], "input_convention.bar_count")
    if "price_field_for_geometry" in convention:
        # §3: y[t] = ln(H[t]).  The engine has exactly one geometry field and
        # ``anchor.py``/``envelope.py`` read only ``Prefix.high``.
        report.equal(
            convention["price_field_for_geometry"], "high",
            "input_convention.price_field_for_geometry",
        )
    if "timestamp_kind" in convention:
        kind = convention["timestamp_kind"]
        ordinal = all(isinstance(bar.timestamp, int) for bar in series)
        report.equal(
            "ordinal" if ordinal else "iso_date", kind, "input_convention.timestamp_kind"
        )


def _compare_params(report: Report, expected: Dict[str, Any], params: DetectorParams) -> None:
    """The parameters, in both directions.

    The six §15/§16/§17 values are the point of this function.  Five of the ten
    configurations with post-breakout behaviour carry none of them, so the
    engine must default them — and a default silently overriding a fixture that
    disagreed would be undetectable.  So: where a fixture carries one, the engine
    reads it, and the value must equal the module default.  A future fixture
    carrying a non-default value fails here loudly, which is an **escalation**,
    not a licence to override.
    """
    block = expected["params"]
    report.equal(block["eps_break_locked"], False, "params.eps_break_locked (HD-03, §13.5)")
    if "split_log_jump_threshold" in block:
        # The fixtures print §18's ln(1.5) to 6 significant figures; the engine
        # uses ln(1.5).  Equality AT that precision is the whole claim.
        report.equal(
            sig6(SPLIT_LOG_JUMP_THRESHOLD),
            as_decimal(block["split_log_jump_threshold"]),
            "params.split_log_jump_threshold is §18's ln(1.5) to 6 s.f.",
        )
    report.equal(params.eps, block["eps"], "params.eps")
    report.equal(params.eps_break, block["eps_break"], "params.eps_break")
    report.equal(params.min_formation_bars, block["min_formation_bars"], "params.min_formation_bars")
    report.equal(params.min_ath_age_bars, block["min_ath_age_bars"], "params.min_ath_age_bars")
    report.equal(params.tolerance_version, block["tolerance_version"], "params.tolerance_version")
    if "eps_touch" in block:
        report.equal(params.eps_touch, block["eps_touch"], "params.eps_touch")
    defaults = DetectorParams.__dataclass_fields__
    for key in POST_BREAKOUT_FIXTURE_PARAMS:
        if key not in block:
            continue
        report.equal(
            getattr(params, key), block[key],
            "params.%s: the engine did not read the carried value" % key,
        )
        report.equal(
            block[key], defaults[key].default,
            "params.%s: a fixture carries a NON-DEFAULT value — escalate, do not "
            "override the fixture with the module default" % key,
        )


def _compare_geometry_check(
    report: Report, expected: Dict[str, Any], line: Optional[Line]
) -> None:
    """``yA`` and ``yB`` — the two numbers in the restated arithmetic block.

    They are the logs of the two anchor highs, so they are checkable against the
    engine's reported line rather than left as human commentary.
    """
    block = expected.get("geometry_check") or {}
    if "yA" not in block and "yB" not in block:
        return
    if block.get("yA") is None:
        report.equal(line, None, "geometry_check.yA is null but the engine has a line")
        report.equal(block.get("yB"), None, "geometry_check.yB")
        return
    if not report.check(line is not None, "geometry_check: engine produced no line"):
        return
    assert line is not None
    report.sig6_equal(ln_price(line.high_anchor), block["yA"], "geometry_check.yA")
    report.sig6_equal(ln_price(line.high_b), block["yB"], "geometry_check.yB")


def _assert_valid_walk(report: Report, result: DetectionResult) -> None:
    """§21.6 rule 3 — the emitted sequence must be a valid walk of §11.

    Two properties, both on the engine's own output: each record's ``from``
    equals the previous record's ``to`` (continuity), and each ``(from, to,
    reason)`` triple is an edge §11 actually draws (legality).  Continuity alone
    is what the schema asserts, and it does not reject an edge §11 omits.
    """
    state = LineState.NONE
    for record in result.transitions:
        report.equal(record.frm, state, "state walk: `from` at bar %d" % record.bar)
        legal = LEGAL_TRANSITIONS.get((record.frm, record.to))
        report.check(
            legal is not None and record.reason in legal,
            "state walk: %s -> %s / %s at bar %d is not an edge §11 draws"
            % (record.frm.value, record.to.value, record.reason.value, record.bar),
        )
        state = record.to
    if result.final_state is not None:
        report.equal(result.final_state, state, "state walk: last `to` is the final state")
    report.check(
        all(
            record.frm is not LineState.EXPIRED and record.to is not LineState.EXPIRED
            for record in result.transitions
        ),
        "LineState.EXPIRED is reserved and unreachable (ESC-1) but a record carries it",
    )


def _compare_causal_record(
    report: Report,
    causal_record: Dict[str, Any],
    result: DetectionResult,
    series,
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
            if not report.check(
                t in engine_trace,
                "causal_record.formation.%s: engine sealed no prefix at t=%d" % (key, t),
            ):
                continue
            compared += 1
            report.equal(engine_trace[t], parsed, "causal_record.formation.%s t=%d" % (key, t))
        # Phase 3 evaluates every bar and seals every prefix including t = n, so
        # EVERY recorded entry is compared — there is no longer a class "beyond
        # the engine's reach".
        report.check(
            compared == len(recorded) and compared > 0,
            "causal_record.formation.%s: compared %d of %d recorded entries"
            % (key, compared, len(recorded)),
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
        # §21.5: re-selection is SUSPENDED once a line is frozen.  No
        # re-selection may be registered at or after the freeze bar of the
        # episode that owns it.
        if result.confirmed_bar is not None:
            report.check(
                all(item.effective_bar <= result.confirmed_bar for item in causal.reselections),
                "a re-selection was registered after the freeze bar (§21.5)",
            )

    _compare_candidate_set(report, causal_record, causal)
    _compare_no_anchor_proof(report, causal_record, causal, series, params)
    _compare_pivot_context(report, causal_record, result)

    # -- the active line before each recorded event bar --------------------
    for entry in causal_record.get("active_line_before_event_bars") or []:
        bar = int(entry["bar"])
        bar_data = series[bar]
        evidence = active_line_at(
            causal, bar, bar_data.high, bar_data.close, params.eps, params.eps_break
        )
        label = "causal_record.active_line_before_event_bars[bar=%d]" % bar
        report.equal(evidence.state_at_start.value, entry["state_at_start"], "%s.state_at_start" % label)
        if entry.get("line", "present") is None:
            report.equal(evidence.line, None, "%s: engine has a line where the fixture has none" % label)
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

    _compare_events(report, causal_record, causal)


def _compare_candidate_set(report: Report, causal_record: Dict[str, Any], causal) -> None:
    recorded_candidates = causal_record.get("as_of_time_candidate_set")
    if not recorded_candidates:
        return
    at_bar = int(recorded_candidates["at_bar"])
    report.equal(
        recorded_candidates["available_prefix"], "S_%d = bars 0..%d" % (at_bar, at_bar - 1),
        "causal_record.as_of_time_candidate_set.available_prefix",
    )
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
    report.price_equal(
        evidence.selected_high, selected.get("H"),
        "causal_record.as_of_time_candidate_set.selected.H",
    )
    report.sig6_equal(
        evidence.selected_slope, selected.get("slope"),
        "causal_record.as_of_time_candidate_set.selected.slope",
    )


def _compare_no_anchor_proof(
    report: Report, causal_record: Dict[str, Any], causal, series, params: DetectorParams
) -> None:
    """§10.4 / GX-20 — why NO candidate is envelope-valid at ANY prefix.

    Every number in this block is derivable from the engine's own candidate sets,
    so none of it needs to be taken on trust: the count of envelope-valid
    candidates, the shallowest (maximum-slope) candidate, the bars that tie the
    ATH, and how far the shallowest candidate is pierced at one of them.
    """
    proof = causal_record.get("no_anchor_proof")
    if not proof:
        return
    report.equal(proof["eps"], params.eps, "causal_record.no_anchor_proof.eps")
    for entry in proof.get("per_prefix") or []:
        at_bar = int(entry["at_bar"])
        label = "causal_record.no_anchor_proof.per_prefix[at_bar=%d]" % at_bar
        report.equal(entry["prefix"], "S_%d" % at_bar, "%s.prefix" % label)
        sealed = causal.sealed_at(at_bar)
        if not report.check(
            sealed is not None and sealed.verdict.selection is not None,
            "%s: engine sealed no candidate set" % label,
        ):
            continue
        assert sealed is not None
        selection = sealed.verdict.selection
        anchor = sealed.verdict.anchor
        assert selection is not None and anchor is not None
        valid = [c for c in selection.candidates if c.envelope_valid]
        report.equal(
            len(valid), entry["envelope_valid_candidates"], "%s.envelope_valid_candidates" % label
        )
        ties = [
            j for j in range(anchor.t + 1, at_bar) if float(series[j].high) == anchor.high
        ]
        report.equal(ties, list(entry["ath_tie_bars"]), "%s.ath_tie_bars" % label)
        if not selection.candidates:
            continue
        shallowest = max(selection.candidates, key=lambda c: (c.slope, c.t))
        recorded = entry["shallowest_candidate"]
        report.equal(shallowest.t, recorded["t"], "%s.shallowest_candidate.t" % label)
        report.price_equal(shallowest.high, recorded["H"], "%s.shallowest_candidate.H" % label)
        report.sig6_equal(shallowest.slope, recorded["slope"], "%s.shallowest_candidate.slope" % label)
        if not ties:
            continue
        pierce = max(
            ln_price(float(series[j].high))
            - y_hat(shallowest.slope, shallowest.intercept, j)
            for j in ties
        )
        report.sig6_equal(pierce, entry["pierce_at_tie_bar"], "%s.pierce_at_tie_bar" % label)
        report.sig6_equal(pierce / params.eps, entry["exceeds_eps_by"], "%s.exceeds_eps_by" % label)


def _compare_pivot_context(report: Report, causal_record: Dict[str, Any], result) -> None:
    """One derived member of a block that is otherwise descriptive.

    §5, D-TL-03 and HD-11 make pivot status non-authoritative, so the pivot
    counts are on the unasserted allow-list.  ``b_star_bar`` is not a pivot fact
    — it is the reported ``B*``, restated — so it is compared.
    """
    context = causal_record.get("pivot_context")
    if not context or "b_star_bar" not in context:
        return
    report.equal(
        None if result.reported_line is None else result.reported_line.t_b,
        context["b_star_bar"],
        "causal_record.pivot_context.b_star_bar",
    )


#: Which recorded fields each event type carries, and how each is compared.
#: ``exact`` values are compared at full double precision AND to 6 s.f.
_EVENT_FIELDS: Dict[str, Dict[str, str]] = {
    "WICK_BREAK": {
        "y_hat": "sig6", "pierce": "sig6", "close_margin": "sig6", "ln_high": "sig6",
        "high": "price", "close": "price",
    },
    "RESET_NEW_ATH": {"prior_state": "raw"},
    "BREAKOUT_CONFIRMED": {
        "y_hat": "sig6", "line_value": "sig6", "margin": "sig6", "ln_close": "sig6",
        "close": "price",
    },
    "FAILED_BREAKOUT": {
        "y_hat_frozen": "sig6", "line_value": "sig6", "margin": "sig6", "close": "price",
    },
    "RETEST_HELD": {
        "y_hat_frozen": "sig6", "line_value": "sig6", "return_margin": "sig6",
        "hold_margin": "sig6", "low": "price", "close": "price",
    },
    "EXPIRED_POST_BREAKOUT": {"bars_since_breakout": "raw"},
}


def _compare_events(report: Report, causal_record: Dict[str, Any], causal) -> None:
    """Every recorded event, of every type, in both directions."""
    engine_events = {(event.bar, event.event.value): event for event in causal.events}
    for entry in causal_record.get("events") or []:
        name = entry["event"]
        bar = int(entry["bar"])
        label = "causal_record.events[bar=%d,%s]" % (bar, name)
        event = engine_events.get((bar, name))
        if not report.check(event is not None, "%s: engine emitted no such event" % label):
            continue
        assert event is not None
        fields = _EVENT_FIELDS.get(name)
        if not report.check(fields is not None, "%s: no field map for this event type" % label):
            continue
        assert fields is not None
        for field_name, kind in fields.items():
            if field_name not in entry:
                continue
            value = event.detail.get(field_name)
            if kind == "sig6":
                report.sig6_equal(value, entry[field_name], "%s.%s" % (label, field_name))
            elif kind == "price":
                report.price_equal(value, entry[field_name], "%s.%s" % (label, field_name))
            else:
                report.equal(value, entry[field_name], "%s.%s" % (label, field_name))
        if "line" in entry:
            # Recorded at FULL double precision: a stronger comparison than
            # 6 s.f., available, and therefore taken as well as the 6-s.f. one.
            engine_line = event.detail.get("line")
            if report.check(engine_line is not None, "%s.line: engine carries none" % label):
                recorded = entry["line"]
                report.equal(engine_line.t_anchor, recorded["tA"], "%s.line.tA" % label)
                report.equal(engine_line.t_b, recorded["tB"], "%s.line.tB" % label)
                report.exact_equal(engine_line.m, recorded["m"], "%s.line.m (exact)" % label)
                report.exact_equal(engine_line.b, recorded["b"], "%s.line.b (exact)" % label)
                report.sig6_equal(engine_line.m, sig6(float(recorded["m"])), "%s.line.m (6 s.f.)" % label)
                report.sig6_equal(engine_line.b, sig6(float(recorded["b"])), "%s.line.b (6 s.f.)" % label)
    # Both directions: no event the fixture does not record, and none missing.
    recorded_events = {
        (int(entry["bar"]), entry["event"]) for entry in causal_record.get("events") or []
    }
    report.equal(sorted(engine_events), sorted(recorded_events), "causal_record.events: event set")


def _compare_frozen_event_line(
    report: Report, causal_record: Dict[str, Any], result: DetectionResult
) -> None:
    """``Λ^F`` against §21.5's frozen-field table, including the null case."""
    if "frozen_event_line" not in causal_record:
        return
    recorded = causal_record["frozen_event_line"]
    frozen = result.frozen_line
    if recorded is None:
        report.equal(frozen, None, "causal_record.frozen_event_line: expected null")
        return
    if not report.check(frozen is not None, "causal_record.frozen_event_line: engine froze nothing"):
        return
    assert frozen is not None
    label = "causal_record.frozen_event_line"
    report.equal(frozen.line.t_anchor, recorded["A"]["t"], "%s.A.t" % label)
    report.price_equal(frozen.line.high_anchor, recorded["A"]["H"], "%s.A.H" % label)
    report.equal(frozen.line.t_b, recorded["B_star"]["t"], "%s.B_star.t" % label)
    report.price_equal(frozen.line.high_b, recorded["B_star"]["H"], "%s.B_star.H" % label)
    report.sig6_equal(frozen.line.m, recorded["m"], "%s.m" % label)
    report.sig6_equal(frozen.line.b, recorded["b"], "%s.b" % label)
    report.equal(frozen.breakout_bar, recorded["breakout_bar"], "%s.breakout_bar" % label)
    report.equal(frozen.confirmed_bar, recorded["confirmed_bar"], "%s.confirmed_bar" % label)
    report.equal(
        frozen.tolerance_version, recorded["tolerance_version"], "%s.tolerance_version" % label
    )
    # §21.5 row 6, and the Phase-2/Phase-3 bridge: Λ^F IS the line the engine's
    # own stop recorded, by object identity in the fold.
    report.check(
        result.line_at_stop is frozen.line,
        "%s: Λ^F is not the very object line_at_stop holds (§21.5)" % label,
    )


def _compare_challengers(
    report: Report, causal_record: Dict[str, Any], result: DetectionResult
) -> None:
    """``non_retroactive_challengers`` — suspension proven POSITIVELY.

    Absence of a re-selection record shows only that nothing happened.  This
    shows the engine *knew* which post-breakout highs a full-series hull would
    have selected — 7 bars on GX-04, 101 on GX-07 — and did not use one of them.
    The empty case on the fixtures with no breakout is asserted too.
    """
    block = causal_record.get("non_retroactive_challengers")
    if block is None:
        return
    engine = [
        (item.bar, Decimal(repr(item.high)), sig6(item.slope_if_selected))
        for item in result.challengers
    ]
    recorded = [
        (int(item["bar"]), as_decimal(item["H"]), as_decimal(item["slope_if_selected"]))
        for item in block["bars"]
    ]
    _compare_ordered(report, engine, recorded, "causal_record.non_retroactive_challengers.bars")
    if result.frozen_line is not None:
        report.check(
            all(item.slope_if_selected > result.frozen_line.line.m for item in result.challengers),
            "a challenger does not actually challenge the frozen slope",
        )


def _compare_eps_break_sweep(
    report: Report, causal_record: Dict[str, Any], result: DetectionResult, sweep_runner
) -> None:
    """HD-13 rule 1, run against the engine and compared to committed data.

    Self-consistency at +/-20% alone is not enough: an engine that ignored
    ``eps_break`` entirely would pass it.  Comparing every recorded scale —
    including 0.5x and 2x, where GX-12 and GX-15 genuinely change — is the
    falsifiable half.

    ``final_state`` is compared at **every** recorded point.  The Phase-2 harness
    compared it only where ``breakout_bar`` was null, which left every
    post-breakout sweep outcome unasserted.
    """
    robustness = causal_record.get("eps_break_robustness") or {}
    if not robustness:
        return
    documented = robustness.get("documented_default")
    if documented is not None:
        report.equal(documented, result.params.eps_break, "eps_break_robustness.documented_default")
    for point in robustness.get("sweep") or []:
        eps_break = float(point["eps_break"])
        outcome = sweep_runner(eps_break)
        label = "eps_break_robustness scale=%s" % point["scale"]
        if documented is not None:
            report.equal(
                sig6(eps_break), sig6(float(documented) * float(point["scale"])),
                "%s: eps_break is scale x documented_default" % label,
            )
        report.equal(outcome.stop_bar, point["breakout_bar"], "%s: breakout_bar" % label)
        report.equal(
            None if outcome.final_state is None else outcome.final_state.value,
            point["final_state"],
            "%s: final_state" % label,
        )
