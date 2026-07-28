"""Constructed unit tests for §15, §16, §17 — **required evidence, not polish**.

Measured across the committed corpus: **every `RETEST_HELD` has its hold leg on
the same bar as its return leg** (GX-04 at 20, GX-19 at 17, GX-15 at 0.5x at 29),
so an engine that implemented ``h_hold = 0`` would pass all 24 committed
fixtures.  Fixture conformance is therefore **not evidence** that the hold window
is a window at all.  Likewise no fixture reaches the right edge of ``F_fail`` or
``W_retest`` — the largest event gap anywhere in the corpus is 4 bars against
windows of 10 and 20 — and the ESC-3, ESC-5(a), OQ-P3-1, OQ-P3-2, OQ-P3-3,
OQ-P3-4, OQ-P3-5 and OQ-P3-6 rulings are all *unexercised* by it.

So the cases below are built from the specification, with ``make_series``, and
**no fixture is added, edited or reinterpreted** — the pattern
``test_mutations.py`` already established for the two mutations the
6-significant-figure comparison cannot catch.

The construction, once, so every case below reads as arithmetic rather than as
magic numbers:

* highs ``100, 96, 94, 93, 92, 91.5, 91, 90.5, 90`` over bars 0–8.  The hull's
  maximum-slope candidate is the latest bar each time, so ``Λ_9`` runs from
  ``A = (0, 100)`` to ``B* = (8, 90)``.
* bar 9 closes at 92, which clears ``ŷ_9(9) + ε_break`` — a confirmed breakout at
  bar 9, and ``Λ^F`` is frozen there.
* every later bar is **neutral** by default: a high of 95 (never a new ATH), and
  a low and close 5% above the frozen line in price terms, which satisfies
  neither the §15 failure predicate nor the §16 return leg.  A case then
  overrides exactly the bars it is about.

**Why several cases set ``F_fail = 0`` or ``W_retest = 0``.**  At the documented
defaults ``ε_fail == ε_retest == 0.01``, so a close that *fails* the §16 hold leg
(``< ŷ_F − ε_retest``) necessarily *satisfies* the §15 failure predicate
(``< ŷ_F − ε_fail``) — the two legs are inseparable at those values, which is
also why no fixture can separate them.  Emptying the other window is the
narrowest way to isolate one section's arithmetic; both are named, versioned
config, so neither value is invented here.
"""

from __future__ import annotations

import math
import unittest
from typing import Dict, List, Optional, Tuple

from ..detector import detect
from ..frozen import (
    FrozenLine,
    at_or_above,
    at_or_below,
    falls_below,
    in_failure_window,
    in_return_window,
)
from ..params import POST_BREAKOUT_FIXTURE_PARAMS, DetectorParams
from ..state import LineState, PreconditionError, ReasonCode
from .support import default_params, make_series

#: Bars 0–8 form the line; bar 9 breaks out.
HEAD_HIGHS: Tuple[float, ...] = (100.0, 96.0, 94.0, 93.0, 92.0, 91.5, 91.0, 90.5, 90.0, 93.0)
HEAD_CLOSES: Tuple[float, ...] = tuple(high * 0.9 for high in HEAD_HIGHS[:9]) + (92.0,)
BREAKOUT_BAR = 9
NEUTRAL_HIGH = 95.0


_FROZEN: List[FrozenLine] = []


def frozen_line() -> FrozenLine:
    """``Λ^F`` as the engine itself freezes it on the head construction.

    Derived by running the detector on the head rather than by restating the
    arithmetic here: a constructed case that hard-coded the slope would stop
    testing the engine the moment the two disagreed.
    """
    if not _FROZEN:
        highs = list(HEAD_HIGHS)
        closes = list(HEAD_CLOSES)
        lows = [min(h, c) * 0.95 for h, c in zip(highs, closes)]
        result = detect(make_series(highs, closes, lows), default_params())
        assert result.frozen_line is not None
        _FROZEN.append(result.frozen_line)
    return _FROZEN[0]


def y_frozen(t: int) -> float:
    """``ŷ_F(t)`` for the head construction — derived from the frozen line."""
    return frozen_line().y_hat_at(t)


def at_offset(t: int, offset: float) -> float:
    """A price whose log sits exactly ``offset`` from ``ŷ_F(t)``."""
    return math.exp(y_frozen(t) + offset)


def _series(length: int, overrides: Dict[int, Tuple[Optional[float], Optional[float], float]]):
    """The head, extended to ``length`` bars, with named bars overridden.

    ``overrides[t] = (high, low, close)``; a ``high`` of ``None`` keeps the
    neutral value, and a ``low`` of ``None`` is a genuinely absent field (which
    §18 does **not** guard — ESC-5(a)).
    """
    highs: List[Optional[float]] = list(HEAD_HIGHS)
    closes: List[Optional[float]] = list(HEAD_CLOSES)
    lows: List[Optional[float]] = [
        min(float(h), float(c)) * 0.95 for h, c in zip(highs, closes)
    ]
    line = frozen_line().line
    for t in range(len(HEAD_HIGHS), length):
        neutral = math.exp(line.y_hat_at(t)) * 1.05
        highs.append(NEUTRAL_HIGH)
        closes.append(neutral)
        lows.append(neutral)
    for t, (high, low, close) in overrides.items():
        if high is not None:
            highs[t] = high
        lows[t] = low
        closes[t] = close
    return make_series(highs, closes, lows)


def _run(length: int, overrides, params: Optional[DetectorParams] = None):
    return detect(_series(length, overrides), params or default_params())


def _records(result):
    return [record.as_tuple() for record in result.transitions]


def _bars_with(result, reason: ReasonCode) -> List[int]:
    return [record.bar for record in result.transitions if record.reason is reason]


class TheConstruction(unittest.TestCase):
    """The fixture-free scaffold these cases stand on, asserted once."""

    def test_the_head_breaks_out_at_the_expected_bar_and_freezes_there(self) -> None:
        result = _run(len(HEAD_HIGHS), {})
        self.assertEqual(result.stop_bar, BREAKOUT_BAR)
        self.assertEqual(result.confirmed_bar, BREAKOUT_BAR)
        assert result.frozen_line is not None
        self.assertEqual(result.frozen_line.line.t_anchor, 0)
        self.assertEqual(result.frozen_line.line.t_b, 8)
        self.assertEqual(result.frozen_line.breakout_bar, BREAKOUT_BAR)

    def test_a_neutral_tail_produces_no_post_breakout_event(self) -> None:
        result = _run(40, {})
        self.assertEqual(result.final_state, LineState.BROKEN_OUT)
        self.assertEqual(
            [record.reason for record in result.transitions if record.bar > BREAKOUT_BAR],
            [],
            "the neutral tail is not neutral; every case below would be confounded",
        )

    def test_re_selection_is_suspended_for_the_whole_episode(self) -> None:
        """§21.5, checked directly rather than only through the frozen line.

        Every bar of the neutral tail has a high of 95, which is far above the
        frozen line — under §21.2 step 4 each of them would re-bind ``B*`` and
        emit a ``LINE_ESTABLISHED`` effective the next bar.  While the episode is
        open, none does.  The challenger list is the positive half: the engine
        names every one of those highs and used none of them.
        """
        result = _run(30, {})
        after = [
            record
            for record in result.transitions
            if record.bar > BREAKOUT_BAR
        ]
        self.assertEqual(after, [], "a record was emitted while the line was frozen")
        assert result.causal is not None
        self.assertEqual(
            [item for item in result.causal.reselections if item.effective_bar > BREAKOUT_BAR],
            [],
            "a re-selection was registered while re-selection was suspended",
        )
        self.assertGreater(
            len(result.challengers), 15, "no high would have re-bound B*; the case is idle"
        )

    def test_a_later_high_does_not_move_the_frozen_line(self) -> None:
        """§21.9's bar-22 walkthrough, on a constructed series: a post-breakout
        high that a full-series hull WOULD have selected leaves ``Λ^F`` alone."""
        baseline = _run(20, {})
        assert baseline.frozen_line is not None
        raised = _run(20, {12: (99.0, at_offset(12, 0.05), at_offset(12, 0.05))})
        self.assertEqual(raised.frozen_line, baseline.frozen_line)
        self.assertTrue(
            any(item.bar == 12 for item in raised.challengers),
            "bar 12's high does not challenge the frozen slope, so the case is idle",
        )


class FailureWindowEdges(unittest.TestCase):
    """§15 and ESC-3 — ``breakout_bar < t <= breakout_bar + F_fail``.

    The right edge is evidenced by **no fixture and cannot be**: the largest
    event gap in the corpus is 4 against a window of 10.  It is asserted here.
    """

    #: §16 emptied so a close below the line cannot also open a retest leg.
    PARAMS = default_params(W_retest=0)

    def _failing_close(self, t: int):
        # ln C < ŷ_F(t) − ε_fail, comfortably.
        return (None, at_offset(t, -0.10), at_offset(t, -0.10))

    def test_the_breakout_bar_itself_is_not_in_the_failure_window(self) -> None:
        """The left edge is open, and it is fixture-forced: on GX-04 the §16
        legs both hold at the breakout bar, so an engine evaluating the window
        there would emit at bar 16 where the fixture records bar 20."""
        frozen = frozen_line()
        self.assertFalse(in_failure_window(frozen, BREAKOUT_BAR, self.PARAMS))
        self.assertTrue(in_failure_window(frozen, BREAKOUT_BAR + 1, self.PARAMS))

    def test_a_qualifying_close_at_the_right_edge_fails(self) -> None:
        edge = BREAKOUT_BAR + self.PARAMS.F_fail
        result = _run(edge + 5, {edge: self._failing_close(edge)}, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.FAILED_BREAKOUT), [edge])
        self.assertEqual(result.final_state, LineState.FAILED_BREAKOUT)

    def test_one_bar_past_the_right_edge_does_not(self) -> None:
        past = BREAKOUT_BAR + self.PARAMS.F_fail + 1
        result = _run(past + 5, {past: self._failing_close(past)}, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.FAILED_BREAKOUT), [])
        self.assertEqual(result.final_state, LineState.BROKEN_OUT)

    def test_the_predicate_is_strict_at_the_tolerance(self) -> None:
        """§15 writes ``<``.  A close exactly on ``ŷ_F − ε_fail`` does not fail."""
        params = self.PARAMS
        frozen = frozen_line()
        bar = BREAKOUT_BAR + 1
        exact = frozen.y_hat_at(bar) - params.eps_fail
        self.assertFalse(falls_below(exact, frozen.y_hat_at(bar), params.eps_fail))
        self.assertTrue(
            falls_below(
                math.nextafter(exact, -math.inf), frozen.y_hat_at(bar), params.eps_fail
            )
        )


class ReturnWindowEdges(unittest.TestCase):
    """§16 return leg and ESC-3 — and the ruling that ``W_retest`` bounds the
    **return leg only**, so a hold opened inside the window may complete after
    it."""

    #: §15 emptied: at the documented defaults ``ε_fail == ε_retest``, so a close
    #: that fails the hold leg also trips the failure predicate.
    PARAMS = default_params(F_fail=0)

    def _return_and_hold(self, t: int):
        return (None, at_offset(t, 0.0), at_offset(t, 0.0))

    def _return_only(self, t: int):
        # low touches the line; close is below ŷ_F − ε_retest, so the hold fails.
        return (None, at_offset(t, 0.0), at_offset(t, -0.05))

    def test_the_breakout_bar_itself_is_not_a_return_bar(self) -> None:
        """The left edge, and the case that makes it fixture-forced: at the
        breakout bar the close is above the line **by construction** — that is
        what a breakout is — so an engine that evaluated §16 there would emit
        ``RETEST_HELD`` at the breakout bar itself whenever the low reached the
        line."""
        frozen = frozen_line()
        self.assertFalse(in_return_window(frozen, BREAKOUT_BAR, self.PARAMS))
        result = _run(
            20,
            {BREAKOUT_BAR: (93.0, at_offset(BREAKOUT_BAR, 0.0), 92.0)},
            self.PARAMS,
        )
        self.assertEqual(result.stop_bar, BREAKOUT_BAR)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [])

    def test_a_return_at_the_right_edge_can_complete(self) -> None:
        edge = BREAKOUT_BAR + self.PARAMS.W_retest
        result = _run(edge + 5, {edge: self._return_and_hold(edge)}, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [edge])

    def test_a_return_one_bar_past_the_right_edge_cannot(self) -> None:
        past = BREAKOUT_BAR + self.PARAMS.W_retest + 1
        result = _run(past + 5, {past: self._return_and_hold(past)}, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [])
        self.assertEqual(result.final_state, LineState.BROKEN_OUT)

    def test_a_hold_opened_inside_the_window_may_complete_after_it(self) -> None:
        """ESC-3, stated explicitly: ``W_retest`` bounds the **return leg only**.

        The return lands on the last legal bar; the hold arrives two bars later,
        outside the return window but inside ``[r, r + h_hold]``.
        """
        params = self.PARAMS
        r = BREAKOUT_BAR + params.W_retest
        u = r + 2
        self.assertGreater(u, BREAKOUT_BAR + params.W_retest)
        self.assertLessEqual(u, r + params.h_hold)
        result = _run(
            u + 5,
            {
                r: self._return_only(r),
                r + 1: (None, at_offset(r + 1, 0.05), at_offset(r + 1, -0.05)),
                u: (None, at_offset(u, 0.05), at_offset(u, 0.0)),
            },
            params,
        )
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [u])
        self.assertEqual(result.final_state, LineState.RETESTED)

    def test_the_return_predicate_is_non_strict_at_the_tolerance(self) -> None:
        """§16 condition 1 writes ``≤``: a low exactly on ``ŷ_F + ε_retest``
        returns."""
        frozen = frozen_line()
        bar = BREAKOUT_BAR + 1
        exact = frozen.y_hat_at(bar) + self.PARAMS.eps_retest
        self.assertTrue(at_or_below(exact, frozen.y_hat_at(bar), self.PARAMS.eps_retest))
        self.assertFalse(
            at_or_below(
                math.nextafter(exact, math.inf), frozen.y_hat_at(bar), self.PARAMS.eps_retest
            )
        )


class HoldWindowIsAWindow(unittest.TestCase):
    """§16 hold leg, ESC-3 and OQ-P3-3.

    **This class is the evidence the corpus cannot supply.**  Every committed
    retest holds on its own return bar, so ``h_hold = 0`` passes all 24 fixtures.
    """

    PARAMS = default_params(F_fail=0)

    def _return_no_hold(self, t: int):
        return (None, at_offset(t, 0.0), at_offset(t, -0.05))

    def _hold_only(self, t: int):
        return (None, at_offset(t, 0.05), at_offset(t, 0.0))

    def test_the_return_bar_itself_is_a_valid_hold_bar(self) -> None:
        r = BREAKOUT_BAR + 2
        result = _run(r + 5, {r: (None, at_offset(r, 0.0), at_offset(r, 0.0))}, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [r])

    def test_a_hold_at_the_last_bar_of_the_window_fires(self) -> None:
        r = BREAKOUT_BAR + 2
        u = r + self.PARAMS.h_hold
        overrides = {r: self._return_no_hold(r), u: self._hold_only(u)}
        for between in range(r + 1, u):
            overrides[between] = (None, at_offset(between, 0.05), at_offset(between, -0.05))
        result = _run(u + 5, overrides, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [u])

    def test_a_hold_one_bar_past_the_window_does_not(self) -> None:
        r = BREAKOUT_BAR + 2
        late = r + self.PARAMS.h_hold + 1
        overrides = {r: self._return_no_hold(r), late: self._hold_only(late)}
        for between in range(r + 1, late):
            overrides[between] = (None, at_offset(between, 0.05), at_offset(between, -0.05))
        result = _run(late + 5, overrides, self.PARAMS)
        self.assertEqual(
            _bars_with(result, ReasonCode.RETEST_HELD),
            [],
            "the hold window is not a window: h_hold is being ignored",
        )
        self.assertEqual(result.final_state, LineState.BROKEN_OUT)

    def test_h_hold_zero_would_change_the_outcome(self) -> None:
        """Anti-vacuity for this whole class: the case above genuinely depends on
        ``h_hold``, so an engine that ignored it is detected here."""
        r = BREAKOUT_BAR + 2
        u = r + 3
        overrides = {r: self._return_no_hold(r), u: self._hold_only(u)}
        for between in range(r + 1, u):
            overrides[between] = (None, at_offset(between, 0.05), at_offset(between, -0.05))
        with_window = _run(u + 5, overrides, self.PARAMS.replace(h_hold=3))
        without = _run(u + 5, overrides, self.PARAMS.replace(h_hold=0))
        self.assertEqual(_bars_with(with_window, ReasonCode.RETEST_HELD), [u])
        self.assertEqual(_bars_with(without, ReasonCode.RETEST_HELD), [])

    def test_a_lapsed_window_emits_nothing_and_a_fresh_return_may_open(self) -> None:
        """OQ-P3-3: a hold window that lapses without a qualifying close emits
        **nothing at all**, and any bar still inside the return window may open a
        new one."""
        params = self.PARAMS
        first = BREAKOUT_BAR + 1
        second = first + params.h_hold + 2  # strictly after the first window lapsed
        overrides = {first: self._return_no_hold(first)}
        for between in range(first + 1, second):
            overrides[between] = (None, at_offset(between, 0.05), at_offset(between, -0.05))
        overrides[second] = (None, at_offset(second, 0.0), at_offset(second, 0.0))
        result = _run(second + 5, overrides, params)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [second])
        self.assertEqual(
            [record.bar for record in result.transitions if record.bar == first],
            [],
            "the lapsed return leg emitted a record of its own",
        )

    def test_overlapping_windows_fire_at_the_earliest_qualifying_bar(self) -> None:
        """OQ-P3-3: every qualifying bar opens its OWN window, windows may
        overlap, and the hold fires at the earliest bar satisfying any of them."""
        params = self.PARAMS
        first, second = BREAKOUT_BAR + 1, BREAKOUT_BAR + 2
        hold = second + 1
        overrides = {
            first: self._return_no_hold(first),
            second: self._return_no_hold(second),
            hold: self._hold_only(hold),
        }
        result = _run(hold + 5, overrides, params)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [hold])
        self.assertLessEqual(hold, first + params.h_hold)

    def test_at_most_one_retest_held_per_episode(self) -> None:
        """OQ-P3-3: §11 has no ``RETESTED -> RETESTED`` edge."""
        params = self.PARAMS
        first = BREAKOUT_BAR + 1
        second = BREAKOUT_BAR + 6
        overrides = {
            first: (None, at_offset(first, 0.0), at_offset(first, 0.0)),
            second: (None, at_offset(second, 0.0), at_offset(second, 0.0)),
        }
        result = _run(second + 5, overrides, params)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [first])
        self.assertEqual(result.final_state, LineState.RETESTED)

    def test_the_hold_predicate_is_non_strict_at_the_tolerance(self) -> None:
        """§16 condition 2 writes ``≥``."""
        frozen = frozen_line()
        bar = BREAKOUT_BAR + 1
        exact = frozen.y_hat_at(bar) - self.PARAMS.eps_retest
        self.assertTrue(at_or_above(exact, frozen.y_hat_at(bar), self.PARAMS.eps_retest))
        self.assertFalse(
            at_or_above(
                math.nextafter(exact, -math.inf), frozen.y_hat_at(bar), self.PARAMS.eps_retest
            )
        )


class HoldIsJudgedAtItsOwnBar(unittest.TestCase):
    """OQ-P3-1 and OQ-P3-2 — which bar is ``t``, asked two ways.

    Both are unexercised by the corpus for the same measured reason: **no
    ``return_bar`` field exists in any committed event**, so nothing separates
    the two legs there at all.
    """

    PARAMS = default_params(F_fail=0)

    def test_the_hold_leg_uses_y_hat_at_the_hold_bar_not_the_return_bar(self) -> None:
        """OQ-P3-1.  The close is constructed to hold against ``ŷ_F(u)`` and to
        FAIL against ``ŷ_F(r)`` — the line falls between the two bars, so reading
        it at ``r`` would judge bar ``u`` by another bar's geometry."""
        params = self.PARAMS
        frozen = frozen_line()
        r = BREAKOUT_BAR + 1
        u = r + params.h_hold
        close_log = frozen.y_hat_at(u) - 0.005
        self.assertTrue(at_or_above(close_log, frozen.y_hat_at(u), params.eps_retest))
        self.assertFalse(
            at_or_above(close_log, frozen.y_hat_at(r), params.eps_retest),
            "the two bars' line values are too close for this case to discriminate",
        )
        overrides = {r: (None, at_offset(r, 0.0), at_offset(r, -0.05))}
        for between in range(r + 1, u):
            overrides[between] = (None, at_offset(between, 0.05), at_offset(between, -0.05))
        overrides[u] = (None, at_offset(u, 0.05), math.exp(close_log))
        result = _run(u + 5, overrides, params)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [u])

    def test_the_record_lands_on_the_hold_bar_and_the_return_leg_emits_nothing(self) -> None:
        """OQ-P3-2, forced by §21.8 rule 1: recording at the return bar ``r``
        would require a later bar ``u > r`` to establish ``r``'s
        classification."""
        params = self.PARAMS
        r = BREAKOUT_BAR + 1
        u = r + 2
        overrides = {r: (None, at_offset(r, 0.0), at_offset(r, -0.05))}
        overrides[r + 1] = (None, at_offset(r + 1, 0.05), at_offset(r + 1, -0.05))
        overrides[u] = (None, at_offset(u, 0.05), at_offset(u, 0.0))
        result = _run(u + 5, overrides, params)
        self.assertEqual(
            [record.as_tuple() for record in result.transitions if record.bar >= r],
            [(u, "BROKEN_OUT", "RETESTED", "RETEST_HELD")],
        )
        assert result.causal is not None
        held = [event for event in result.causal.events if event.event is ReasonCode.RETEST_HELD]
        self.assertEqual(len(held), 1)
        self.assertEqual(held[0].bar, u)
        # The event still names the return leg it completes, which is evidence
        # rather than a second record.
        self.assertEqual(held[0].detail["return_bar"], r)


class MissingLowIsACallerDefect(unittest.TestCase):
    """ESC-5(a) — a bar whose ``low`` is absent must not reach a §16 predicate.

    §1 lists ``low`` among the required input fields but §18's table names only a
    missing ``high`` or ``close``, so the §18 pre-pass does not reject it.  The
    ruling: this is a **caller defect**, in the same class as a non-positive
    basis or an out-of-order series.  It raises, and it mints **no** reason code
    — the schema's reason-code set is closed, and adding a member is a
    product-definition change that is not an implementer's to make.
    """

    PARAMS = default_params(F_fail=0)

    def test_a_missing_low_in_the_return_window_raises_naming_field_and_bar(self) -> None:
        bar = BREAKOUT_BAR + 1
        with self.assertRaises(PreconditionError) as caught:
            _run(bar + 5, {bar: (None, None, at_offset(bar, 0.05))}, self.PARAMS)
        message = str(caught.exception)
        self.assertIn("low", message)
        self.assertIn(str(bar), message)

    def test_no_reason_code_is_minted_for_it(self) -> None:
        """The negative half, and the one that matters: the failure mode this
        forbids is inventing a code, not raising."""
        bar = BREAKOUT_BAR + 1
        try:
            _run(bar + 5, {bar: (None, None, at_offset(bar, 0.05))}, self.PARAMS)
        except PreconditionError as error:
            for code in ReasonCode:
                self.assertNotIn(code.value, str(error))
        else:  # pragma: no cover - the case above must raise
            self.fail("a missing low did not raise")

    def test_a_missing_low_outside_the_window_is_not_reached_and_does_not_raise(self) -> None:
        """An unevaluable leg is NOT an evaluated-and-failed leg: outside the
        return window the predicate is never reached, so nothing raises and
        nothing is classified."""
        bar = BREAKOUT_BAR + self.PARAMS.W_retest + 1
        result = _run(bar + 3, {bar: (None, None, at_offset(bar, 0.05))}, self.PARAMS)
        self.assertEqual(result.final_state, LineState.BROKEN_OUT)
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [])


class NewAthRetiresEveryPostBreakoutState(unittest.TestCase):
    """§21.7 as amended by HD-25, and §11's edge list as corrected 2026-07-28.

    Unexercised by the corpus: GX-06 and GX-22 both reset from ``ACTIVE``, and no
    fixture has a post-failure new ATH.
    """

    PARAMS = default_params(F_fail=0)
    NEW_ATH = 120.0

    def _reset_bar(self, t: int):
        # A new ATH whose close ALSO clears the line: §21.7 says such a bar is a
        # reset, not a breakout of the line the same high retired.
        return (self.NEW_ATH, self.NEW_ATH * 0.99, self.NEW_ATH * 0.99)

    def test_a_new_ath_resets_from_broken_out(self) -> None:
        bar = BREAKOUT_BAR + 2
        result = _run(bar + 6, {bar: self._reset_bar(bar)}, self.PARAMS)
        self.assertIn((bar, "BROKEN_OUT", "NONE", "RESET_NEW_ATH"), _records(result))
        self.assertEqual(
            [record for record in _records(result) if record[0] == bar and record[3] == "BREAKOUT_CONFIRMED"],
            [],
            "a bar whose high made a new ATH was also recorded as a breakout (§21.7)",
        )

    def test_a_new_ath_resets_from_retested(self) -> None:
        held = BREAKOUT_BAR + 1
        bar = held + 2
        result = _run(
            bar + 6,
            {
                held: (None, at_offset(held, 0.0), at_offset(held, 0.0)),
                bar: self._reset_bar(bar),
            },
            self.PARAMS,
        )
        self.assertIn((held, "BROKEN_OUT", "RETESTED", "RETEST_HELD"), _records(result))
        self.assertIn((bar, "RETESTED", "NONE", "RESET_NEW_ATH"), _records(result))

    def test_a_new_ath_resets_from_failed_breakout(self) -> None:
        """HD-25's substance: under the superseded reading the first failed
        breakout in a name's history silenced that name permanently."""
        params = default_params(W_retest=0)
        failed = BREAKOUT_BAR + 1
        bar = failed + 2
        result = _run(
            bar + 6,
            {
                failed: (None, at_offset(failed, -0.10), at_offset(failed, -0.10)),
                bar: self._reset_bar(bar),
            },
            params,
        )
        self.assertIn((failed, "BROKEN_OUT", "FAILED_BREAKOUT", "FAILED_BREAKOUT"), _records(result))
        self.assertIn((bar, "FAILED_BREAKOUT", "NONE", "RESET_NEW_ATH"), _records(result))

    def test_the_reported_frozen_line_survives_the_reset(self) -> None:
        """OQ-P3-4: ``Λ^F`` remains the reported line after a new ATH retires it,
        exactly as it remains after expiry.  A reported line that vanished on
        reset would make the answer depend on the exit route rather than on the
        event."""
        bar = BREAKOUT_BAR + 2
        baseline = _run(len(HEAD_HIGHS), {})
        result = _run(bar + 6, {bar: self._reset_bar(bar)}, self.PARAMS)
        self.assertIn((bar, "BROKEN_OUT", "NONE", "RESET_NEW_ATH"), _records(result))
        self.assertEqual(result.frozen_line, baseline.frozen_line)
        assert result.frozen_line is not None
        self.assertEqual(
            result.reported_line,
            result.frozen_line.line,
            "the reported line vanished on reset, making the answer depend on "
            "the exit route rather than on the event (OQ-P3-4)",
        )
        self.assertEqual(result.ath_anchor, (0, 100.0))


class ExpiryRetiresEveryPostBreakoutState(unittest.TestCase):
    """§17, ESC-1 and HD-25 — one record, from any of the three states."""

    #: A short horizon so the constructed series stays readable.  ``E_expiry`` is
    #: named, versioned config (D-TL-10); the value is not invented here, only
    #: shortened, and the DEFAULT horizon is exercised by GX-07.
    PARAMS = default_params(E_expiry=6, F_fail=0)

    def test_expiry_emits_exactly_one_record_at_the_elapsed_count(self) -> None:
        """ESC-1: **one** record, ``BROKEN_OUT -> NONE``, not two through an
        intermediate state."""
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        result = _run(expiry + 3, {}, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.EXPIRED_POST_BREAKOUT), [expiry])
        self.assertIn((expiry, "BROKEN_OUT", "NONE", "EXPIRED_POST_BREAKOUT"), _records(result))
        assert result.causal is not None
        self.assertNotIn(
            result.causal.state_at(expiry + 1),
            (LineState.BROKEN_OUT, LineState.RETESTED, LineState.FAILED_BREAKOUT),
            "the episode did not actually end",
        )

    def test_a_series_ending_at_the_expiry_bar_ends_in_none(self) -> None:
        """The shape GX-07 records: expiry on the last bar, so no new line has
        formed yet and the final state is ``NONE`` — while the REPORTED line is
        still ``Λ^F``, which is the deliberate consequence §21.4 names."""
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        result = _run(expiry + 1, {}, self.PARAMS)
        self.assertEqual(result.final_state, LineState.NONE)
        assert result.frozen_line is not None
        self.assertEqual(result.reported_line, result.frozen_line.line)

    def test_one_bar_short_of_the_horizon_nothing_expires(self) -> None:
        short = BREAKOUT_BAR + self.PARAMS.E_expiry - 1
        result = _run(short + 1, {}, self.PARAMS)
        self.assertEqual(_bars_with(result, ReasonCode.EXPIRED_POST_BREAKOUT), [])
        self.assertEqual(result.final_state, LineState.BROKEN_OUT)

    def test_expiry_from_retested(self) -> None:
        held = BREAKOUT_BAR + 1
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        result = _run(
            expiry + 3,
            {held: (None, at_offset(held, 0.0), at_offset(held, 0.0))},
            self.PARAMS,
        )
        self.assertIn((expiry, "RETESTED", "NONE", "EXPIRED_POST_BREAKOUT"), _records(result))

    def test_expiry_from_failed_breakout(self) -> None:
        params = default_params(E_expiry=6, W_retest=0)
        failed = BREAKOUT_BAR + 1
        expiry = BREAKOUT_BAR + params.E_expiry
        result = _run(
            expiry + 3,
            {failed: (None, at_offset(failed, -0.10), at_offset(failed, -0.10))},
            params,
        )
        self.assertIn(
            (expiry, "FAILED_BREAKOUT", "NONE", "EXPIRED_POST_BREAKOUT"), _records(result)
        )

    def test_no_intermediate_expired_state_is_ever_entered(self) -> None:
        """ESC-1: §11 draws ONE edge; the ``EXPIRED`` enum member is reserved and
        unreachable."""
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        result = _run(expiry + 3, {}, self.PARAMS)
        for record in result.transitions:
            self.assertNotEqual(record.frm, LineState.EXPIRED)
            self.assertNotEqual(record.to, LineState.EXPIRED)
        assert result.causal is not None
        for state in result.causal.state_at_start:
            self.assertNotEqual(state, LineState.EXPIRED)

    def test_the_reported_frozen_line_survives_expiry_and_the_next_formation(self) -> None:
        """§21.4: ``Λ^F`` is the reported line "if a confirmed breakout occurred
        **anywhere** in the series" — so it outlives not only the expiry but the
        line that forms afterwards, until a LATER episode's freeze replaces it.
        GX-07 is the committed case, and it reports ``B* = (6, 94)`` with a final
        state of ``NONE``."""
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        baseline = _run(len(HEAD_HIGHS), {})
        result = _run(expiry + 3, {}, self.PARAMS)
        self.assertEqual(result.frozen_line, baseline.frozen_line)
        self.assertEqual(result.final_state, LineState.ACTIVE, "no line re-formed at all")
        assert result.frozen_line is not None
        self.assertEqual(
            result.reported_line,
            result.frozen_line.line,
            "the newly formed line displaced Λ^F as the REPORTED line",
        )

    def test_the_post_expiry_reformation_sees_the_whole_grown_prefix(self) -> None:
        """OQ-P3-6 — and the reason §21.4's running-maximum Lemma must not be
        seeded across an episode boundary.

        The bars the episode covered are ordinary members of ``S_t`` once it
        ends: §21.1 makes ``B*_t`` a pure function of the prefix and §17 says the
        detector recomputes "over the full **available** history".  Here the new
        ``B*`` is a bar the freeze forbade rolling to, so an implementation that
        resumed the pre-breakout candidate set would pick bar 8 instead.
        """
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        result = _run(expiry + 6, {}, self.PARAMS)
        reformed = [
            record
            for record in result.transitions
            if record.bar > expiry and record.reason is ReasonCode.LINE_ESTABLISHED
        ]
        self.assertTrue(reformed, "no line re-formed after expiry")
        assert result.causal is not None
        sealed = result.causal.sealed_at(reformed[0].bar)
        assert sealed is not None and sealed.line is not None
        self.assertGreater(
            sealed.line.t_b,
            BREAKOUT_BAR,
            "the re-formed B* is a pre-breakout bar: the candidate set was "
            "carried across the episode boundary (OQ-P3-6)",
        )
        self.assertEqual(sealed.line.t_b, expiry)

    def test_the_post_expiry_reformation_is_a_formation_not_a_re_selection(self) -> None:
        """It is a ``NONE -> ACTIVE`` record.  §21.6's roll is an
        ``ACTIVE -> ACTIVE`` record and did not happen here — the geometry moved
        because the episode ended, not because a high reached a live line."""
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        result = _run(expiry + 6, {}, self.PARAMS)
        reformed = [
            record
            for record in result.transitions
            if record.bar > expiry and record.reason is ReasonCode.LINE_ESTABLISHED
        ]
        self.assertEqual(reformed[0].frm, LineState.NONE)
        self.assertEqual(reformed[0].to, LineState.ACTIVE)
        assert result.causal is not None
        self.assertEqual(
            [item for item in result.causal.reselections if item.effective_bar == reformed[0].bar],
            [],
            "a re-formation after expiry was recorded as a pre-breakout roll",
        )


class EpisodeTerminality(unittest.TestCase):
    """Once ``FAILED_BREAKOUT`` or ``RETESTED`` is recorded, §15 and §16 are not
    evaluated again for that episode.

    Neither is fixture-forced beyond GX-12 at 0.5x, and the second is pinned by
    nothing in the corpus at all — every post-retest close in both ``RETESTED``
    fixtures clears the failure band.
    """

    def test_no_retest_after_a_failed_breakout(self) -> None:
        params = default_params()
        failed = BREAKOUT_BAR + 1
        later = failed + 2
        result = _run(
            later + 5,
            {
                failed: (None, at_offset(failed, -0.10), at_offset(failed, -0.10)),
                later: (None, at_offset(later, 0.0), at_offset(later, 0.0)),
            },
            params,
        )
        self.assertEqual(_bars_with(result, ReasonCode.FAILED_BREAKOUT), [failed])
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [])
        self.assertEqual(result.final_state, LineState.FAILED_BREAKOUT)

    def test_no_second_failure_in_the_same_episode(self) -> None:
        params = default_params(W_retest=0)
        first = BREAKOUT_BAR + 1
        second = first + 2
        result = _run(
            second + 5,
            {
                first: (None, at_offset(first, -0.10), at_offset(first, -0.10)),
                second: (None, at_offset(second, -0.10), at_offset(second, -0.10)),
            },
            params,
        )
        self.assertEqual(_bars_with(result, ReasonCode.FAILED_BREAKOUT), [first])

    def test_no_failure_after_a_held_retest(self) -> None:
        """There is no ``RETESTED -> FAILED_BREAKOUT`` edge.  §15's predicate
        carries no state qualifier, so the close below is *arithmetically* inside
        the failure window — §11, OQ-P3-3 and §16 condition 3 are what stop it."""
        params = default_params()
        held = BREAKOUT_BAR + 1
        below = held + 2
        self.assertTrue(in_failure_window(frozen_line(), below, params))
        result = _run(
            below + 5,
            {
                held: (None, at_offset(held, 0.0), at_offset(held, 0.0)),
                below: (None, at_offset(below, -0.10), at_offset(below, -0.10)),
            },
            params,
        )
        self.assertEqual(_bars_with(result, ReasonCode.RETEST_HELD), [held])
        self.assertEqual(_bars_with(result, ReasonCode.FAILED_BREAKOUT), [])
        self.assertEqual(result.final_state, LineState.RETESTED)


class TwoEpisodes(unittest.TestCase):
    """OQ-P3-5 — the LATEST episode supplies the reported ``Λ^F`` and
    ``confirmed_bar``.

    **Zero committed fixtures carry more than one ``BREAKOUT_CONFIRMED``**, which
    is precisely why the ruling had to be made by a decision-maker rather than
    discovered by a test — and why this constructed case is the only evidence
    there is that the engine does not encode the ``stop_bar``-as-``confirmed_bar``
    alias the Phase-3 plan's §8.3 M4 was corrected for.
    """

    PARAMS = default_params(E_expiry=6, F_fail=0)

    def _two_episode_run(self):
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        # After expiry the line re-forms; a close clearing it opens a SECOND
        # episode.  The bar's high stays below the anchor, so it is a breakout
        # and not a reset.
        second = expiry + 4
        overrides = {second: (NEUTRAL_HIGH, NEUTRAL_HIGH * 0.9, 99.0)}
        return _run(second + 3, overrides, self.PARAMS)

    def test_the_engine_records_both_episodes(self) -> None:
        result = self._two_episode_run()
        self.assertEqual(len(result.episodes), 2, "the construction produced one episode")
        self.assertEqual(len(_bars_with(result, ReasonCode.BREAKOUT_CONFIRMED)), 2)

    def test_the_stop_bar_is_the_first_and_the_confirmed_bar_is_the_latest(self) -> None:
        result = self._two_episode_run()
        first, latest = result.episodes[0], result.episodes[-1]
        self.assertEqual(result.stop_bar, first.breakout_bar)
        self.assertEqual(result.confirmed_bar, latest.breakout_bar)
        self.assertNotEqual(
            result.stop_bar,
            result.confirmed_bar,
            "the two indices coincide, so this case cannot detect the alias",
        )
        self.assertIs(result.frozen_line, latest)
        self.assertEqual(result.reported_line, latest.line)
        # Neither episode is erased: each keeps its own BREAKOUT_CONFIRMED.
        self.assertEqual(
            sorted(_bars_with(result, ReasonCode.BREAKOUT_CONFIRMED)),
            [first.breakout_bar, latest.breakout_bar],
        )

    def test_the_truncation_invariant_holds_only_from_the_latest_freeze(self) -> None:
        """The plan's §6 / EV-P3-10 clause, restated as the ruling requires.

        "For every ``k >= confirmed_bar`` the frozen line is field-identical to
        the full run's" is **false the moment a later episode exists**:
        truncating between the two breakouts reports the EARLIER ``Λ^F``.  Sound
        only for ``k >=`` the LATEST episode's confirmed bar, and asserted that
        way.
        """
        from ..bars import BarSeries

        result = self._two_episode_run()
        series = self._two_episode_series()
        first, latest = result.episodes[0], result.episodes[-1]
        between = detect(
            BarSeries(list(series.bars)[: latest.breakout_bar]), self.PARAMS
        )
        self.assertEqual(
            between.frozen_line, first, "truncating before the second freeze must report the first"
        )
        for k in range(latest.breakout_bar, len(series)):
            truncated = detect(BarSeries(list(series.bars)[: k + 1]), self.PARAMS)
            self.assertEqual(truncated.frozen_line, latest, "truncation at k=%d" % k)

    def _two_episode_series(self):
        expiry = BREAKOUT_BAR + self.PARAMS.E_expiry
        second = expiry + 4
        return _series(second + 3, {second: (NEUTRAL_HIGH, NEUTRAL_HIGH * 0.9, 99.0)})


class ParameterDiscipline(unittest.TestCase):
    """The six §15/§16/§17 parameters, as named versioned config."""

    def test_replace_and_with_eps_break_carry_every_field(self) -> None:
        """Both copy constructors built a hand-written kwarg dict, where a
        forgotten field silently resets to its default in every sweep."""
        params = default_params(
            eps_fail=0.02, F_fail=7, eps_retest=0.03, W_retest=11, h_hold=5, E_expiry=42
        )
        self.assertEqual(params.replace(), params)
        for name in POST_BREAKOUT_FIXTURE_PARAMS:
            self.assertEqual(
                getattr(params.with_eps_break(0.5), name),
                getattr(params, name),
                "with_eps_break dropped %s" % name,
            )

    def test_the_defaults_are_the_specification_defaults(self) -> None:
        fields = DetectorParams.__dataclass_fields__
        self.assertEqual(fields["eps_fail"].default, 0.01)  # D-TL-08
        self.assertEqual(fields["F_fail"].default, 10)  # D-TL-08
        self.assertEqual(fields["eps_retest"].default, 0.01)  # D-TL-09
        self.assertEqual(fields["W_retest"].default, 20)  # D-TL-09
        self.assertEqual(fields["h_hold"].default, 3)  # D-TL-09
        self.assertEqual(fields["E_expiry"].default, 100)  # D-TL-10

    def test_eps_break_still_has_no_default(self) -> None:
        """HD-03 / §13.5 — ``eps_break`` is unlocked BY RULING, so the engine
        must keep refusing to invent one.  The six above are
        ``Human-approval: no`` decisions with stated defaults, which is a
        different case and is why they may be defaulted."""
        self.assertIs(
            DetectorParams.__dataclass_fields__["eps_break"].default,
            __import__("dataclasses").MISSING,
        )

    def test_out_of_range_values_are_rejected(self) -> None:
        for change in (
            {"eps_fail": -0.1}, {"eps_retest": -0.1}, {"F_fail": -1},
            {"W_retest": -1}, {"h_hold": -1}, {"E_expiry": 0},
        ):
            with self.assertRaises(ValueError, msg=repr(change)):
                default_params(**change)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
