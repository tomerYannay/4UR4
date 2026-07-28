"""Layer 1 — per-specification-section unit coverage.

Scoped deliberately against the *diverse* part of the corpus.  Seven of the
twenty geometry fixtures share bars 0-15 byte-identically and five of those
share ``B* = (6, 93)``, so "23 fixtures" is not 23 independent samples: a defect
in the shared base fails seven at once while leaving the gate looking broad.
Each case below therefore names either a diverse fixture or a constructed series
that exists precisely because no fixture distinguishes the thing being tested.
"""

from __future__ import annotations

import math
import os
import unittest
from typing import List, Tuple

from ..anchor import anchor_of
from ..bars import Prefix
from ..detector import detect, prefix_of, second_anchor_over
from ..envelope import domination_set, envelope_violations, select_second_anchor
from ..logspace import (
    SPLIT_LOG_JUMP_THRESHOLD,
    exceeds,
    ln_price,
    log_intercept,
    log_slope,
    sig6,
    y_hat,
)
from ..params import DetectorParams, PivotParams
from ..pivots import confirmed_pivots, is_pivot_high
from ..state import LineState, PreconditionError, ReasonCode
from .conformance import SPEC_VERSION
from .fixtures_io import GOLDEN_DIR, golden_fixture_ids, load_expected, load_series
from .lemma_oracle import rolling_b_star
from .support import default_params, make_series


def _golden(fixture_id: str):
    expected = load_expected(fixture_id)
    series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
    params = DetectorParams.from_fixture_params(expected["params"], spec_version=SPEC_VERSION)
    return expected, series, params


class InputGuards(unittest.TestCase):
    """§1, §18 — the three guards reject the BAR-SET, and nothing else does."""

    #: ``ln(1.5) - ln(1.0)`` is ``math.log(1.5)`` exactly, so this pair sits ON
    #: §18's boundary rather than near it.  A ratio built by repeated division
    #: lands one or two ulps off and would not test the boundary at all.
    BOUNDARY_HIGHS = [1.5, 1.0]

    def test_a_jump_of_exactly_ln_1_5_does_not_trip(self) -> None:
        """The guard is a strict ``>``.  No fixture sits on this boundary, so the
        case is constructed; without it, ``>=`` would pass the whole corpus."""
        jump = abs(ln_price(self.BOUNDARY_HIGHS[1]) - ln_price(self.BOUNDARY_HIGHS[0]))
        self.assertEqual(jump, SPLIT_LOG_JUMP_THRESHOLD, "the construction is not on the boundary")
        highs = self.BOUNDARY_HIGHS + [0.99 - 0.01 * i for i in range(8)]
        result = detect(make_series(highs), default_params())
        self.assertFalse(
            result.rejected,
            "a jump of exactly ln(1.5) tripped the guard; §18 says strictly greater",
        )

    def test_a_jump_one_ulp_above_ln_1_5_does_trip(self) -> None:
        """The other side of the same boundary, one ulp away."""
        first = math.nextafter(1.5, 2.0)
        self.assertGreater(ln_price(first) - ln_price(1.0), SPLIT_LOG_JUMP_THRESHOLD)
        highs = [first, 1.0] + [0.99 - 0.01 * i for i in range(8)]
        result = detect(make_series(highs), default_params())
        self.assertTrue(result.rejected)
        self.assertEqual(
            [code.value for code in result.guard.codes], ["SUSPECTED_UNADJUSTED_SPLIT"]
        )

    def test_guards_reject_the_bar_set_not_the_bar(self) -> None:
        """M-9: applied per bar, GX-10 would still fit geometry on the rest."""
        _expected, series, params = _golden("GX-10")
        result = detect(series, params)
        self.assertTrue(result.rejected)
        self.assertIsNone(result.reported_line)
        self.assertIsNone(result.ath_anchor)
        self.assertIsNone(result.causal, "no geometry may be fitted at any prefix")

    def test_positive_control_truncating_gx10_before_the_split(self) -> None:
        """The converse of the above, so "condition on guard status" cannot hide
        a defect: truncated before its bar-4 split, GX-10 is a normal series."""
        _expected, series, params = _golden("GX-10")
        head = make_series(
            [float(series[i].high) for i in range(4)],
            [float(series[i].close) for i in range(4)],
        )
        result = detect(head, params)
        self.assertFalse(result.rejected)
        self.assertEqual(result.final_state, LineState.NONE)  # too short to form
        self.assertEqual(
            [code.value for code in result.reason_codes],
            [],
            "a head-of-series INSUFFICIENT_BARS run is not recorded (§21.3)",
        )

    def test_non_ascending_timestamps_raise_rather_than_mint_a_code(self) -> None:
        from ..bars import Bar, BarSeries

        with self.assertRaises(PreconditionError):
            BarSeries(
                [
                    Bar(0, 5, 1.0, 1.0, 1.0, 1.0, 1.0),
                    Bar(1, 5, 1.0, 1.0, 1.0, 1.0, 1.0),
                ]
            )


class LogSpaceForms(unittest.TestCase):
    """§3, §7 — the pinned arithmetic forms."""

    def test_the_two_slope_forms_are_not_interchangeable(self) -> None:
        """GX-14 exists because these two disagree in IEEE 754.  If this ever
        stops being demonstrable the M-1 mutation is undetectable and that must
        be recorded, not assumed away."""
        disagreements = 0
        for fixture_id in golden_fixture_ids():
            _expected, series, params = _golden(fixture_id)
            highs = [b.high for b in series if b.high and b.high > 0]
            if len(highs) < 2:
                continue
            base = highs[0]
            for index in range(1, len(highs)):
                pinned = log_slope(ln_price(highs[index]), ln_price(base), index, 0)
                alternative = math.log(highs[index] / base) / index
                if pinned != alternative:
                    disagreements += 1
        self.assertGreater(
            disagreements, 0, "the corpus can no longer distinguish the two §7 slope forms"
        )

    def test_the_two_line_evaluation_forms_are_not_interchangeable(self) -> None:
        """M-2: ``m*u+b`` versus ``y_a + m*(u-t_a)``.  RM-01 (tA=2), GX-06 (tA
        moves to 10) and GX-22 (tA moves to 12) are the fixtures with tA != 0."""
        disagreements = 0
        for fixture_id, t_anchor in (("GX-06", 10), ("GX-22", 12)):
            _expected, series, params = _golden(fixture_id)
            prefix = prefix_of(series)
            y_anchor = prefix.y[t_anchor]
            for candidate in range(t_anchor + 1, prefix.length):
                m = log_slope(prefix.y[candidate], y_anchor, candidate, t_anchor)
                b = log_intercept(y_anchor, m, t_anchor)
                for u in range(prefix.length):
                    if y_hat(m, b, u) != y_anchor + m * (u - t_anchor):
                        disagreements += 1
        self.assertGreater(
            disagreements,
            0,
            "no fixture with tA != 0 distinguishes the two §7 line-evaluation forms; "
            "M-2 would survive and that is a finding, not a pass",
        )

    def test_sig6_is_round_half_even_on_the_exact_binary_value(self) -> None:
        self.assertEqual(str(sig6(1.0000005)), "1.00000")   # ties-to-even downward
        self.assertEqual(str(sig6(1.0000015)), "1.00000")   # exact binary < the tie
        self.assertEqual(str(sig6(0.0)), "0")
        self.assertEqual(str(sig6(-0.012095115472472587)), "-0.0120951")


class AnchorSelection(unittest.TestCase):
    """§4, D-TL-02 — max high, EARLIEST on ties, over ``S_t`` only."""

    def test_triple_tie_anchors_at_the_earliest(self) -> None:
        """GX-12 has a two-way tie; a triple tie is constructed because no
        fixture has one and "earliest" would otherwise be under-tested."""
        prefix = prefix_of(make_series([130.0, 120.0, 130.0, 118.0, 130.0, 115.0]))
        anchor = anchor_of(prefix)
        assert anchor is not None
        self.assertEqual(anchor.t, 0)

    def test_anchor_is_computed_over_the_prefix_only(self) -> None:
        highs = [100.0, 95.0, 300.0, 90.0]
        full = prefix_of(make_series(highs))
        early = Prefix(full.y[:2], full.high[:2], 2)
        anchor = anchor_of(early)
        assert anchor is not None
        self.assertEqual((anchor.t, anchor.high), (0, 100.0))

    def test_empty_prefix_has_no_anchor(self) -> None:
        self.assertIsNone(anchor_of(Prefix.empty()))


class EnvelopeSelection(unittest.TestCase):
    """§6, §8, D-TL-05 — candidacy and domination are DIFFERENT sets."""

    def test_a_tying_high_is_excluded_from_candidacy_but_dominates(self) -> None:
        """M-6 (``<=`` for ``<``) and M-7 (dominate only over candidates).

        GX-12 and GX-20 are the fixtures; this is the minimal statement of the
        rule, with both mutations checked directly.
        """
        highs = [130.0, 127.0, 130.0, 121.0, 118.0, 120.0, 122.0, 119.0]
        prefix = prefix_of(make_series(highs))
        selection = select_second_anchor(prefix, 0, 0.02)
        self.assertIsNone(
            selection.selected,
            "the bar that ties the ATH pierces every descending candidate (§10.4)",
        )
        self.assertNotIn(2, [c.t for c in selection.candidates], "H == HA is not a candidate")
        # ...and it IS in the domination set: every candidate's worst gap is
        # driven by it.
        for candidate in selection.candidates:
            self.assertGreater(candidate.worst_gap, 0.02)

    def test_worst_gap_is_exactly_zero_at_the_candidate_itself(self) -> None:
        """M-15: a clamped or mis-scoped worst_gap.

        Scoped to what was measured, and not to an invariant.  Over GX-01's 8-bar
        prefix at the §4 anchor the ``j == i`` residual is exactly ``0`` for all
        seven candidates, so every ``worst_gap`` here is ``>= 0`` and the selected
        one is exactly ``0``.  Non-negativity is **not** general: see
        :attr:`envelope.Candidate.worst_gap`, which records ``-2^-50`` and
        ``-2^-51`` at 47 candidates once ``tA`` is swept off the §4 anchor.  The
        ``>= 0`` below is therefore a statement about this case and nothing wider —
        it is the M-15 clamp check, not the withdrawn invariant.
        """
        _expected, series, params = _golden("GX-01")
        prefix = prefix_of(series, 8)
        selection = select_second_anchor(prefix, 0, params.eps)
        for candidate in selection.candidates:
            self.assertGreaterEqual(candidate.worst_gap, 0.0)
        assert selection.selected is not None
        self.assertEqual(selection.selected.worst_gap, 0.0)

    def test_envelope_tie_resolves_to_the_later_anchor(self) -> None:
        """M-8, on GX-14's real tie."""
        _expected, series, params = _golden("GX-14")
        prefix = prefix_of(series, 19)
        selection = select_second_anchor(prefix, 0, params.eps)
        assert selection.selected is not None
        self.assertTrue(selection.tie)
        self.assertEqual(selection.tied_bars, (9, 18))
        self.assertEqual(selection.selected.t, 18, "ENVELOPE_TIE_LATER prefers the later B")

    def test_gx14_tie_holds_on_this_platform(self) -> None:
        """A GATING preflight, never a skip.

        GX-14's tie holds because ``log(68.89) == 2*log(83) - log(100)``
        bit-for-bit.  IEEE 754 does not require ``log`` to be correctly rounded,
        so on another libm the tie breaks and ``t=18`` is selected outright — a
        different reason for the same answer.  A skipped assertion here would be
        an unfalsifiable gate; this one names the platform if it fires.
        """
        left = math.log(68.89)
        right = 2 * math.log(83.0) - math.log(100.0)
        self.assertEqual(
            left,
            right,
            "GX-14's tie does not hold on this platform: log(68.89)=%r vs %r. "
            "The fixture's ENVELOPE_TIE_LATER expectation depends on it; escalate "
            "rather than adjust anything." % (left, right),
        )
        self.assertEqual(
            log_slope(math.log(83.0), math.log(100.0), 9, 0),
            log_slope(math.log(68.89), math.log(100.0), 18, 0),
        )


class _WatchedSequence:
    """A read-recording stand-in for a ``Prefix``'s ``y`` tuple."""

    __slots__ = ("_values", "_consulted")

    def __init__(self, values: Tuple[float, ...], consulted: List[int]) -> None:
        self._values = values
        self._consulted = consulted

    def __getitem__(self, index: int) -> float:
        self._consulted.append(index)
        return self._values[index]

    def __len__(self) -> int:
        return len(self._values)


class _WatchedPrefix:
    """``Prefix``-shaped, and records **which bars** a caller asks about.

    Duck-typed rather than a subclass because ``Prefix`` fixes its ``__slots__``.
    This is an *observation*, not a re-implementation: it says nothing about what
    the right answer is, only which bar highs the engine consulted to reach it.
    """

    __slots__ = ("y", "high", "length")

    def __init__(self, prefix: Prefix, consulted: List[int]) -> None:
        self.y = _WatchedSequence(prefix.y, consulted)
        self.high = prefix.high
        self.length = prefix.length


class EnvelopeDominationRange(unittest.TestCase):
    """§8 step 3 — **where the domination set starts**, which nothing pinned.

    Measured against the 136-test corpus as it stood before this class existed:
    moving the near end to ``range(tA, …)`` failed **0** tests at every one of the
    three places the range was written, and ``range(tA + 2, …)`` failed **0** in
    ``_is_envelope_valid`` and **0** in ``envelope_violations``.  Only the copy that
    also drives the *candidacy* loop was sensitive (29 failures), and that
    sensitivity belongs to candidacy, not domination: mutating just the set handed
    to ``_worst_gap`` failed **1** (GX-08's reported gap).  So the corpus did not
    pin this endpoint in either direction, and the tests that ran over it passed
    vacuously on that dimension.

    The two **endpoints** asserted here are derived from the specification, not from
    the engine — the derivation is written out in :func:`envelope.domination_set`
    and turns on §8 algorithm step 3's ``tA < t_i`` (strict, in both halves of its
    union), §1/Notation's integer ordinals, and §21.1's ``S_t = bars 0 … t−1``.
    Pinning whatever the code happened to do would reproduce the vacuity.

    The set *between* those endpoints is a **superset** of §8 step 3's union, because
    it retains ``tB``, which step 3 omits; that retention rests on D-TL-05 rather
    than on step 3, and :func:`envelope.domination_set` records the tension instead
    of claiming the specification settles it.  This class pins the engine's set —
    endpoints and superset alike — so that neither can move unobserved.
    """

    EPS = 0.02

    #: ``A`` at bar 1, and bar 2 **ties** it.  A tying high is excluded from
    #: candidacy (§6 rule 2 is strict) and retained in domination (D-TL-05), where
    #: it undercuts every descending candidate by exactly that candidate's
    #: per-bar slope — so with ``eps = 0.02`` it kills every candidate steeper
    #: than ``-0.02``/bar, and all five candidates here are steeper.  The anchor
    #: is deliberately **not** bar 0: a range hard-coded to ``range(1, …)`` would
    #: pass a ``tA = 0`` construction by coincidence.
    HIGHS = [90.0, 100.0, 100.0, 90.0, 80.0, 75.0, 70.0, 65.0]
    T_ANCHOR = 1
    #: The set the engine dominates over ``HIGHS``, written out rather than
    #: computed, so this test cannot agree with the code by construction.  It is a
    #: **superset** of §8 step 3's union, not equal to it: step 3 quantifies over
    #: ``tA < t_i < tB`` AND ``t_i > tB``, and so omits ``tB`` itself, which this
    #: set contains for every candidate.  Why the superset is kept, why it is not
    #: inert at ``ε = 0``, and what remains unresolved about the two endpoints are
    #: all written out in :func:`envelope.domination_set`.
    EXPECTED_DOMINATION = (2, 3, 4, 5, 6, 7)

    def _prefix(self) -> Prefix:
        prefix = prefix_of(make_series(self.HIGHS))
        anchor = anchor_of(prefix)
        assert anchor is not None
        self.assertEqual(
            (anchor.t, anchor.high),
            (self.T_ANCHOR, 100.0),
            "the construction no longer anchors where it claims",
        )
        self.assertEqual(prefix.high[2], prefix.high[self.T_ANCHOR], "bar 2 must TIE the ATH")
        return prefix

    def test_the_set_runs_from_one_after_the_anchor_to_the_end_of_the_prefix(self) -> None:
        """The endpoints, stated as literals.

        ``tA`` itself is absent because §8 quantifies over ``t_i > tA`` strictly:
        the anchor is the line's own endpoint, not something the line must
        dominate — admitting it would impose ``yA <= ŷ_B(tA) + ε``, a *different*
        predicate that no fixture can distinguish.  ``tA + 1`` is present because
        ``t`` is an integer ordinal (§1), so ``t_i > tA`` begins at ``tA + 1``.
        """
        self.assertEqual(domination_set(1, 8), self.EXPECTED_DOMINATION)
        self.assertEqual(domination_set(0, 5), (1, 2, 3, 4))
        self.assertEqual(domination_set(2, 4), (3,))

        self.assertNotIn(
            1,
            domination_set(1, 8),
            "the anchor bar is in the domination set: this is `range(tA, ...)`, "
            "which is not §8's `tA < t_i`",
        )
        self.assertIn(
            2,
            domination_set(1, 8),
            "the first bar after the anchor is missing: this is `range(tA + 2, ...)`, "
            "which drops a bar §8 requires to be dominated",
        )
        self.assertEqual(domination_set(1, 8)[0], 2)

        # Far end: `length` is exclusive, so the last dominated bar is `length - 1`
        # (§21.1 — S_t is bars 0 … t-1, and this Prefix *is* S_t).
        self.assertEqual(domination_set(1, 8)[-1], 7)
        self.assertNotIn(8, domination_set(1, 8))

        # Degenerate prefixes: an anchor at the last bar dominates nothing.
        self.assertEqual(domination_set(3, 4), ())
        self.assertEqual(domination_set(0, 1), ())
        self.assertEqual(domination_set(0, 0), ())

    def test_the_first_dominated_bar_alone_decides_whether_a_line_exists(self) -> None:
        """Behavioural: bar ``tA + 1`` is the ONLY piercer, and it is decisive.

        Dropping it would resurrect the shallowest candidate and produce a line
        where §8 says there is none (``NO_VALID_SECOND_ANCHOR``, §10.4) — so the
        near end of the range is load-bearing here, not merely stated.
        """
        prefix = self._prefix()
        selection = select_second_anchor(prefix, self.T_ANCHOR, self.EPS)
        self.assertEqual([c.t for c in selection.candidates], [3, 4, 5, 6, 7])
        self.assertNotIn(2, [c.t for c in selection.candidates], "H == HA is not a candidate")

        shallowest = max(selection.candidates, key=lambda c: c.slope)
        self.assertEqual(shallowest.t, 3)

        # Anti-vacuity: bar tA+1 must be the ONLY bar piercing that candidate's
        # line, or this test is about some other bar.  The indices are literal, and
        # the predicate is the pinned one (§9, `logspace.exceeds`) — the axis under
        # test here is the RANGE, so every other axis must be the sanctioned rule.
        for j in (3, 4, 5, 6, 7):
            self.assertFalse(
                exceeds(prefix.y[j], y_hat(shallowest.slope, shallowest.intercept, j), self.EPS),
                "bar %d also pierces; bar 2 is no longer the decisive one" % j,
            )
        self.assertTrue(
            exceeds(prefix.y[2], y_hat(shallowest.slope, shallowest.intercept, 2), self.EPS)
        )

        # ...and the engine agrees, three ways: no line, the worst gap IS the gap
        # at bar tA+1, and the reported violation count is exactly that one bar.
        self.assertIsNone(
            selection.selected,
            "a line exists although the bar after the anchor pierces every "
            "candidate — the domination set has lost its first bar",
        )
        self.assertEqual(
            shallowest.worst_gap,
            prefix.y[2] - y_hat(shallowest.slope, shallowest.intercept, 2),
            "worst_gap is not the gap at bar tA+1; _worst_gap's domination set moved",
        )
        self.assertEqual(envelope_violations(prefix, self.T_ANCHOR, shallowest, self.EPS), 1)

    def test_the_reported_count_consults_exactly_those_bars_and_no_others(self) -> None:
        """The one direction no outcome can see: consulting ``tA`` is *inert*.

        The gap at the anchor is ~0 by construction (§7 fixes ``b`` so that
        ``ŷ(tA) = yA``), so ``range(tA, …)`` changes no selection, no gap at 6
        significant figures and no violation count — measured, 0 failures.  It is
        still a different predicate from §8's, so it is caught here by observing
        **which bars the engine asks about** rather than what it concludes.
        """
        prefix = self._prefix()
        selection = select_second_anchor(prefix, self.T_ANCHOR, self.EPS)
        candidate = max(selection.candidates, key=lambda c: c.slope)

        consulted: List[int] = []
        watched = _WatchedPrefix(prefix, consulted)
        count = envelope_violations(watched, self.T_ANCHOR, candidate, self.EPS)

        self.assertEqual(
            tuple(consulted),
            self.EXPECTED_DOMINATION,
            "the domination loop consulted %r; the set is the bar highs with "
            "tA < t_i <= length-1 -- the SUPERSET of §8 step 3's union (which "
            "quantifies over tA < t_i < tB and t_i > tB, omitting tB) plus tB "
            "itself.  See envelope.domination_set for why the superset is kept."
            % (consulted,),
        )
        self.assertEqual(count, 1)
        self.assertNotIn(self.T_ANCHOR, consulted, "the anchor bar was consulted")


class PierceAndWickBreak(unittest.TestCase):
    """§9, §10.1, §14 — pierce beyond eps; wick-break; and their exact coupling."""

    def test_wick_break_and_invalid_pierce_travel_together(self) -> None:
        """The §3.5 invariant: in Phase 2 a pierce always implies a wick-break,
        because reaching the pierce test means the close did not confirm.  The
        corpus must agree exactly — a divergence is a defect in one of the two.
        """
        wick = set()
        pierce = set()
        for fixture_id in golden_fixture_ids():
            expected = load_expected(fixture_id)
            codes = set(expected["expected_reason_codes"])
            if "WICK_BREAK" in codes:
                wick.add(fixture_id)
            if "INVALID_PIERCE" in codes:
                pierce.add(fixture_id)
        self.assertEqual(wick, pierce)
        self.assertEqual(wick, {"GX-02", "GX-03", "GX-09", "GX-12", "GX-13"})

        for fixture_id in sorted(wick):
            _expected, series, params = _golden(fixture_id)
            result = detect(series, params)
            self.assertIn(ReasonCode.WICK_BREAK, result.reason_codes, fixture_id)
            self.assertIn(ReasonCode.INVALID_PIERCE, result.reason_codes, fixture_id)

    def test_a_re_selection_without_a_pierce_emits_no_invalid_pierce(self) -> None:
        """The discriminating case: ``>=`` re-binds the hull, ``> eps`` pierces.

        GX-14 re-selects twice and pierces never; GX-15 re-selects fourteen
        times and pierces never.  If ``INVALID_PIERCE`` were emitted for every
        re-selection, both would carry it.
        """
        for fixture_id in ("GX-14", "GX-15"):
            _expected, series, params = _golden(fixture_id)
            result = detect(series, params)
            self.assertNotIn(ReasonCode.INVALID_PIERCE, result.reason_codes, fixture_id)
            self.assertTrue(result.causal is not None and result.causal.reselections)


class BreakoutPredicate(unittest.TestCase):
    """§13.1 — strictness and the comparison form, at GX-15's documented boundary.

    GX-15 is the dedicated tolerance-boundary fixture: its bar 28 sits just
    *inside* both boundaries at once.  The documented figures — ``0.00824265``
    in the fixture's own purpose, ``0.008242654587`` and ``0.018534340624`` in
    the roadmap — are **printed to finite precision**, so the boundary is tested
    against the engine's own full-precision clearance and the documented values
    are checked to the precision at which they were written.  Using a truncated
    figure as if it were exact tests the wrong side of the boundary.
    """

    DOCUMENTED_EPS_BREAK_BOUNDARY = 0.008242654587
    DOCUMENTED_EPS_BOUNDARY = 0.018534340624

    def setUp(self) -> None:
        self.expected, self.series, self.params = _golden("GX-15")
        result = detect(self.series, self.params)
        sealed = result.causal.sealed_at(28)
        assert sealed is not None and sealed.line is not None
        self.y_hat_28 = sealed.line.y_hat_at(28)
        self.close_clearance = ln_price(float(self.series[28].close)) - self.y_hat_28
        self.high_clearance = ln_price(float(self.series[28].high)) - self.y_hat_28

    def test_the_documented_boundaries_agree_to_their_printed_precision(self) -> None:
        self.assertEqual(sig6(self.close_clearance), sig6(0.00824265))
        self.assertAlmostEqual(
            self.close_clearance, self.DOCUMENTED_EPS_BREAK_BOUNDARY, places=12
        )
        self.assertAlmostEqual(self.high_clearance, self.DOCUMENTED_EPS_BOUNDARY, places=12)

    def test_at_the_exact_boundary_the_strict_inequality_is_not_met(self) -> None:
        at = detect(self.series, self.params.with_eps_break(self.close_clearance))
        self.assertIsNone(at.stop_bar, "at exactly the boundary, `>` is not satisfied")

    def test_one_quantum_below_the_boundary_the_predicate_fires_at_bar_28(self) -> None:
        """The meaningful quantum is one ulp of ``y_hat``, not one ulp of the
        tolerance: §13.1's right-hand side ``y_hat + eps_break`` is formed first,
        so a change smaller than the sum's own resolution cannot move it.  That
        is the pinned comparison form doing its job, and the test says so rather
        than hiding it behind a fudge factor."""
        below = detect(
            self.series, self.params.with_eps_break(self.close_clearance - self._quantum())
        )
        self.assertEqual(below.stop_bar, 28)

    def test_one_quantum_above_the_boundary_nothing_fires(self) -> None:
        above = detect(
            self.series, self.params.with_eps_break(self.close_clearance + self._quantum())
        )
        self.assertIsNone(above.stop_bar)

    def _quantum(self) -> float:
        return math.nextafter(self.y_hat_28, math.inf) - self.y_hat_28

    def test_the_envelope_boundary_moves_a_phase_2_owned_event(self) -> None:
        """Non-gating elsewhere, gating here: below this eps a WICK_BREAK
        appears at t=28, which is Phase-2-owned behaviour."""
        at = detect(self.series, self.params.replace(eps=self.high_clearance))
        self.assertNotIn(ReasonCode.WICK_BREAK, at.reason_codes)
        below = detect(
            self.series, self.params.replace(eps=self.high_clearance - self._quantum())
        )
        self.assertIn(ReasonCode.WICK_BREAK, below.reason_codes)
        self.assertIn(
            (28, "ACTIVE", "ACTIVE", "WICK_BREAK"),
            [record.as_tuple() for record in below.transitions],
        )


class FormationGates(unittest.TestCase):
    """§18 / §21.3, D-TL-12 — F1, F2, F3 independently; ``t_form`` is the least t."""

    def test_which_gate_binds_is_computed_not_inferred(self) -> None:
        """M-10 and the "single conjunction" defect: if the three gates were
        evaluated as one conjunction, "which one binds" would never be wrong
        because it would never be computed."""
        cases = {
            "GX-21": (8, "F1 alone binds"),
            "GX-22": (8, "F1 first, then F2 alone after the reset"),
            "GX-23": (8, "same t_form as GX-21, structurally different prefix"),
        }
        for fixture_id, (t_form, _why) in cases.items():
            _expected, series, params = _golden(fixture_id)
            result = detect(series, params)
            assert result.causal is not None
            self.assertEqual(result.causal.t_form, t_form, fixture_id)

        _expected, series, params = _golden("GX-21")
        result = detect(series, params)
        assert result.causal is not None
        for sealed in result.causal.sealed:
            verdict = sealed.verdict
            if sealed.t < 8 and sealed.t >= 4:
                self.assertFalse(verdict.f1, "GX-21 t=%d" % sealed.t)
                self.assertTrue(verdict.f2, "GX-21 t=%d: F2 is clear from t=4" % sealed.t)
                self.assertTrue(verdict.f3, "GX-21 t=%d: F3 is clear from t=2" % sealed.t)
                self.assertEqual(verdict.reason, ReasonCode.INSUFFICIENT_BARS)

    def test_gate_thresholds_are_independent_of_the_pivot_window(self) -> None:
        """Structural, not empirical: ``DetectorParams`` has no ``k``, so a
        k-sweep here could not fail and is not offered as proof.  The falsifiable
        control is the architectural test; this only records the fact."""
        self.assertNotIn("k", DetectorParams.__dataclass_fields__)

    def test_formation_happens_immediately_once_all_three_gates_hold(self) -> None:
        for fixture_id in golden_fixture_ids():
            expected = load_expected(fixture_id)
            formation = (expected.get("causal_record") or {}).get("formation") or {}
            if "t_form" not in formation or formation["t_form"] is None:
                continue
            _e, series, params = _golden(fixture_id)
            result = detect(series, params)
            assert result.causal is not None
            first_eligible = next(
                (s.t for s in result.causal.sealed if s.verdict.eligible), None
            )
            self.assertEqual(
                result.causal.t_form, first_eligible,
                "%s: t_form is not the least t satisfying F1 and F2 and F3" % fixture_id,
            )


class ReSelectionAndReset(unittest.TestCase):
    """§21.6, §21.7 — effective at t+1; a new ATH takes precedence."""

    def test_a_re_selection_is_recorded_at_the_bar_it_takes_effect(self) -> None:
        """M-4.  GX-14's second re-selection has an IDENTICAL slope and must
        still be recorded, at t=19 — proving the record tracks the anchor's
        identity, not the slope's value."""
        _expected, series, params = _golden("GX-14")
        result = detect(series, params)
        assert result.causal is not None
        second = result.causal.reselections[1]
        self.assertEqual((second.effective_bar, second.frm, second.to), (19, 9, 18))
        self.assertTrue(second.tie)
        first = result.causal.reselections[0]
        self.assertEqual(sig6(first.m), sig6(second.m), "the slopes are equal to the last bit")

    def test_a_new_ath_bar_is_not_a_breakout_of_the_retired_line(self) -> None:
        """M-11.  GX-06's bar 10 clears the active line by 0.2 log units and is
        still a reset, not a stop (§21.2 rule 5 precedence)."""
        _expected, series, params = _golden("GX-06")
        result = detect(series, params)
        self.assertIsNone(result.stop_bar)
        self.assertIn(
            (10, "ACTIVE", "NONE", "RESET_NEW_ATH"),
            [record.as_tuple() for record in result.transitions],
        )

    def test_an_equal_high_is_not_a_new_ath(self) -> None:
        """M-12.  GX-12's bar 2 equals the ATH exactly and must not reset."""
        _expected, series, params = _golden("GX-12")
        result = detect(series, params)
        self.assertNotIn(ReasonCode.RESET_NEW_ATH, result.reason_codes)

    def test_none_run_reason_is_recorded_once_per_run(self) -> None:
        """M-13.  GX-20's run is 19 bars long and carries ONE record; GX-12's
        four-bar run carries one; GX-06's and GX-22's post-reset runs carry one
        each."""
        for fixture_id, expected_count in (
            ("GX-20", 1), ("GX-12", 1), ("GX-06", 1), ("GX-22", 1)
        ):
            _expected, series, params = _golden(fixture_id)
            result = detect(series, params)
            none_records = [
                record
                for record in result.transitions
                if record.reason
                in (
                    ReasonCode.NO_VALID_SECOND_ANCHOR,
                    ReasonCode.ATH_TOO_RECENT,
                    ReasonCode.INSUFFICIENT_BARS,
                )
            ]
            self.assertEqual(len(none_records), expected_count, fixture_id)


class PivotsAreNonAuthoritative(unittest.TestCase):
    """§5, HD-11 — pivot status never affects selection or formation."""

    def test_gx08_has_zero_pivots_and_still_has_a_canonical_anchor(self) -> None:
        _expected, series, params = _golden("GX-08")
        highs = [float(bar.high) for bar in series]
        self.assertEqual(confirmed_pivots(highs, PivotParams(3)), [])
        result = detect(series, params)
        assert result.reported_line is not None
        self.assertEqual(result.reported_line.t_b, 1)

    def test_gx19_and_gx23_select_a_non_pivot_bar(self) -> None:
        for fixture_id in ("GX-19", "GX-23"):
            _expected, series, params = _golden(fixture_id)
            highs = [float(bar.high) for bar in series]
            result = detect(series, params)
            assert result.reported_line is not None
            self.assertFalse(
                is_pivot_high(highs, result.reported_line.t_b, 3),
                "%s: B*=%d is a confirmed k=3 pivot, so the fixture no longer "
                "proves what it exists to prove" % (fixture_id, result.reported_line.t_b),
            )

    def test_pivot_helper_uses_strict_left_and_inclusive_right(self) -> None:
        plateau = [80.0, 90.0, 100.0, 100.0, 90.0, 80.0, 70.0]
        self.assertTrue(is_pivot_high(plateau, 2, 2))
        self.assertFalse(is_pivot_high(plateau, 3, 2), "the LATER bar of a plateau is not the pivot")


class LemmaEquivalence(unittest.TestCase):
    """§21.4 — the closed form agrees with the §8 brute force at EVERY prefix.

    What this actually checks, stated at full strength -- TWO earlier drafts
    understated the sharing, both in the same direction, and both were caught:

    * draft 1: "they share only ``logspace``" -- false;
    * draft 2: "``anchor_of`` and ``select_second_anchor`` -- on the mandated
      fallback branch" -- the em-dash scoped BOTH to the fallback.  Also false.

    :func:`anchor_of` is called **unconditionally, on 611 of 611 prefixes**, above
    the branch, and the brute-force side calls the same function.  The first
    anchor is therefore **common-mode**: an ``anchor_of`` defect moves both sides
    identically and this test cannot see it.  Only
    :func:`select_second_anchor` is fallback-scoped.

    The 611 prefixes decompose as **21 + 77 + 513**: 21 where ``anchor_of``
    returns ``None`` on both sides (the empty prefix of each non-guard fixture --
    degenerate agreement), 77 decided by the engine's own selector on §21.4's
    mandated fallback, and 513 by the closed form.

    So: a two-version check on the 513, **for B\* given an engine-supplied
    anchor** -- not for the geometry as a whole -- and a self-consistency check on
    the 77.  See :mod:`lemma_oracle` for the composition of the 77 and the reason
    §21.4 mandates the fallback.
    """

    def test_lemma_matches_brute_force_on_every_fixture_prefix(self) -> None:
        checked = 0
        for fixture_id in golden_fixture_ids():
            expected, series, params = _golden(fixture_id)
            if (expected.get("causal_record") or {}).get("input_guard"):
                continue  # guard-rejected: no geometry at any prefix
            highs = [float(bar.high) for bar in series]
            logs = [ln_price(h) for h in highs]
            oracle = rolling_b_star(logs, highs, params.eps)
            for t in range(len(highs) + 1):
                prefix = Prefix(tuple(logs[:t]), tuple(highs[:t]), t)
                anchor = anchor_of(prefix)
                if anchor is None:
                    brute = None
                else:
                    selection = select_second_anchor(prefix, anchor.t, params.eps)
                    brute = None if selection.selected is None else selection.selected.t
                self.assertEqual(
                    oracle[t], brute, "%s: §21.4 lemma disagrees with §8 at S_%d" % (fixture_id, t)
                )
                checked += 1
        self.assertGreater(checked, 400, "the lemma check covered suspiciously few prefixes")

    def test_slope_is_monotonically_non_decreasing_within_an_episode(self) -> None:
        """§21.4 — the causal line can only shallow, never steepen, while the
        anchor is unchanged.  Free, and it catches a whole class of
        re-selection errors."""
        episodes_seen = 0
        for fixture_id in golden_fixture_ids():
            expected, series, params = _golden(fixture_id)
            result = detect(series, params)
            if result.causal is None:
                continue
            previous = None
            for sealed in result.causal.sealed:
                if sealed.line is None:
                    previous = None
                    continue
                if previous is not None and previous.t_anchor == sealed.line.t_anchor:
                    self.assertGreaterEqual(
                        sealed.line.m, previous.m,
                        "%s: slope steepened at t=%d (§21.4)" % (fixture_id, sealed.t),
                    )
                    episodes_seen += 1
                previous = sealed.line
        self.assertGreater(episodes_seen, 50)


class SplitThresholdReading(unittest.TestCase):
    """Ambiguity A-5: the fixtures print §18's ``ln(1.5)`` to 6 significant
    figures.  Both readings must give identical outcomes wherever the key
    appears, or the choice is not safe to make silently."""

    def test_both_readings_agree_on_every_fixture_that_carries_the_key(self) -> None:
        carriers = [
            fixture_id
            for fixture_id in golden_fixture_ids()
            if "split_log_jump_threshold" in load_expected(fixture_id)["params"]
        ]
        self.assertEqual(carriers, ["GX-10", "GX-20"])
        for fixture_id in carriers:
            expected, series, _params = _golden(fixture_id)
            printed = float(expected["params"]["split_log_jump_threshold"])
            spec_form = DetectorParams.from_fixture_params(
                expected["params"], spec_version=SPEC_VERSION
            )
            as_printed = spec_form.replace(split_log_jump_threshold=printed)
            self.assertEqual(
                [r.as_tuple() for r in detect(series, spec_form).transitions],
                [r.as_tuple() for r in detect(series, as_printed).transitions],
                "%s: the two readings of the split threshold disagree" % fixture_id,
            )

    def test_the_two_readings_are_not_the_same_number(self) -> None:
        self.assertNotEqual(SPLIT_LOG_JUMP_THRESHOLD, 0.405465)
        self.assertGreater(SPLIT_LOG_JUMP_THRESHOLD, 0.405465)


class ParameterDiscipline(unittest.TestCase):
    def test_an_omitted_outcome_affecting_parameter_is_an_error(self) -> None:
        for omitted in ("eps", "eps_break", "min_formation_bars", "min_ath_age_bars"):
            block = {
                "eps": 0.02,
                "eps_break": 0.01,
                "min_formation_bars": 8,
                "min_ath_age_bars": 3,
            }
            del block[omitted]
            with self.assertRaises(ValueError, msg=omitted):
                DetectorParams.from_fixture_params(block, spec_version=SPEC_VERSION)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
