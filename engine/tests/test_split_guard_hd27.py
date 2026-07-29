"""HD-27 regression tests: a crash is not an adjustment defect.

The defect this pins was found on real data, not in review. AAPL fell **51.9% on
2000-09-29** on a profit warning — split coefficient 1.0, no corporate action —
and the §18 guard read it as ``SUSPECTED_UNADJUSTED_SPLIT`` and rejected the
**entire 26-year bar-set**. The engine emitted nothing for AAPL: ``final_state
NONE``, zero breakouts, and no diagnostic that said why.

The four cases the Product Owner named are each a test below (the engine now
implements five — the unusable-coefficient and direction branches were added later), and the real
numbers are used rather than invented ones — a synthetic 50% drop would prove
the arithmetic but not that the guard behaves correctly on the event that
actually broke it.
"""

from __future__ import annotations

import math
import unittest

from engine.bars import Bar, BarSeries
from engine.detector import detect
from engine.guards import SPLIT_MATCH_TOLERANCE, CorporateActions, run_guards
from engine.params import DetectorParams
from engine.state import LineState, ReasonCode

PARAMS = DetectorParams(
    eps=0.02,
    eps_break=0.01,
    min_formation_bars=8,
    min_ath_age_bars=3,
    tolerance_version="tol-2026.07-illustrative",
    spec_version="UNVERSIONED-PENDING-OQ-J",
)


def series_from(closes, highs=None):
    """Build a BarSeries; high defaults just above close, low just below."""
    highs = highs if highs is not None else [c * 1.01 for c in closes]
    return BarSeries(
        [
            Bar(t=i, timestamp=f"d{i:04d}", open=c, high=h, low=c * 0.99,
                close=c, volume=1_000_000.0)
            for i, (c, h) in enumerate(zip(closes, highs))
        ]
    )


class AaplCrashIsRealMarketData(unittest.TestCase):
    """Case 1 — AAPL 2000-09-29: a genuine >50% decline must be ACCEPTED."""

    # The vendor's own as-traded closes across the event, split coefficient 1.0
    # on every one of them.
    CLOSES = [61.05, 56.69, 52.19, 53.50, 51.44, 48.94, 53.50, 25.75, 24.25, 22.31,
              23.62, 22.06, 22.19, 21.75, 20.62, 19.75, 20.12, 19.25, 18.94, 19.50]

    def test_the_jump_really_does_exceed_the_threshold(self):
        # If it did not, the rest of this class would pass vacuously.
        jump = abs(math.log(25.75) - math.log(53.50))
        self.assertGreater(jump, PARAMS.split_log_jump_threshold)
        self.assertAlmostEqual(jump, 0.7312, places=3)

    def test_with_a_split_feed_showing_no_split_the_series_is_ACCEPTED(self):
        s = series_from(self.CLOSES)
        actions = CorporateActions(symbol="AAPL", splits={})  # no split anywhere
        verdict = run_guards(s, PARAMS, actions)
        self.assertFalse(verdict.rejected, "a real crash was rejected as a split defect")
        self.assertEqual(verdict.rejections, ())
        self.assertNotIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)

    def test_the_accepted_jump_is_OBSERVED_not_silently_swallowed(self):
        # Requirement 5: never fail silently. An accepted jump and an untested
        # one must not look identical.
        s = series_from(self.CLOSES)
        verdict = run_guards(s, PARAMS, CorporateActions("AAPL", {}))
        self.assertEqual(len(verdict.observations), 1)
        obs = verdict.observations[0]
        self.assertEqual(obs.bar, 7)
        self.assertAlmostEqual(obs.split_coefficient, 1.0)
        self.assertGreater(obs.log_jump, obs.threshold)
        self.assertIn("no split", obs.verdict)

    def test_the_engine_now_runs_geometry_instead_of_returning_NONE(self):
        s = series_from(self.CLOSES)
        result = detect(s, PARAMS, corporate_actions=CorporateActions("AAPL", {}))
        self.assertFalse(result.guard.rejected)
        # The whole point: the series reaches the causal fold at all.
        self.assertIsNotNone(result.causal)

    def test_without_a_feed_it_is_still_rejected_and_says_so(self):
        # The pre-HD-27 behaviour is retained where evidence is unavailable —
        # but it must now be *explained*, not inferable from final_state alone.
        s = series_from(self.CLOSES)
        verdict = run_guards(s, PARAMS, None)
        self.assertTrue(verdict.rejected)
        self.assertEqual(len(verdict.rejections), 1)
        self.assertIn("no corporate-action feed", verdict.rejections[0].evidence)


class TrulyUnadjustedSplitIsRejected(unittest.TestCase):
    """Case 3 — a real adjustment defect must still be caught."""

    def test_a_2_to_1_unadjusted_split_is_rejected_when_the_feed_confirms_it(self):
        # Prices halve at bar 4 AND the feed says a 2:1 happened there.
        closes = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]
        s = series_from(closes)
        verdict = run_guards(s, PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        r = verdict.rejections[0]
        self.assertEqual(r.bar, 4)
        self.assertEqual(r.split_coefficient, 2.0)
        self.assertIn("unadjusted for this split", r.evidence)

    def test_the_rejection_carries_every_field_the_ruling_named(self):
        # Requirement 6: symbol, date, jump, threshold, coefficient, reason.
        closes = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]
        verdict = run_guards(series_from(closes), PARAMS, CorporateActions("X", {4: 2.0}))
        r = verdict.rejections[0]
        self.assertEqual(r.symbol, "X")
        self.assertEqual(r.date, "d0004")
        self.assertIsNotNone(r.log_jump)
        self.assertIsNotNone(r.threshold)
        self.assertIsNotNone(r.split_coefficient)
        self.assertEqual(r.reason, "SUSPECTED_UNADJUSTED_SPLIT")
        described = r.describe()
        for token in ("X", "d0004", "log_jump", "threshold", "split_coefficient"):
            self.assertIn(token, described)


class AlreadyAdjustedIsNotAdjustedTwice(unittest.TestCase):
    """Case 4 — a split that IS already applied must not re-trigger."""

    def test_a_split_date_with_normal_prices_produces_no_jump_and_no_rejection(self):
        # Prices are already adjusted, so there is no discontinuity to see even
        # though a split occurred at bar 4.
        closes = [99.0, 97.0, 99.0, 96.0, 97.5, 98.0, 96.5, 97.0]
        verdict = run_guards(series_from(closes), PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertFalse(verdict.rejected)
        self.assertEqual(verdict.observations, ())  # nothing even reached inspection

    def test_a_crash_that_lands_on_a_split_date_is_not_misattributed(self):
        # A 2:1 implies ln(2)=0.693. This drop is 3.2x -> ln=1.163, a
        # discrepancy of 0.47 against a tolerance of 0.15, so it plainly is not
        # the split. The prices are already adjusted and the move is real.
        # Accepting is the difference between "adjust twice" and "read the
        # evidence".
        closes = [99.0, 97.0, 99.0, 96.0, 30.0, 29.0, 31.0, 30.5]
        verdict = run_guards(series_from(closes), PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertFalse(verdict.rejected, "a real move on a split date was misattributed")
        self.assertEqual(len(verdict.observations), 1)
        self.assertIn("already adjusted", verdict.observations[0].verdict)


class ToleranceIsPinnedAtTheRulingsOwnCase(unittest.TestCase):
    """``SPLIT_MATCH_TOLERANCE`` is pinned by measurement, not by prose.

    HD-27 records that a regression test caught an initial tolerance of 0.25 by
    misattributing a genuine crash on a split date.  No test actually did: the
    suite was green at 0.031, 0.15, 0.3, 0.4 **and 0.47**, because the only case
    in that region (``test_a_crash_that_lands_on_a_split_date_is_not_misattributed``)
    has a discrepancy of 0.47 and so passes at every tolerance below it.

    This class supplies the missing pin, at the case the ruling reasons about:

    * a **2.34x drop** at a bar whose feed carries ``{4: 2.0}``,
    * observed log jump ``0.8502``, implied ``ln 2 = 0.6931``,
    * **discrepancy 0.157**.

    That discriminates exactly the two tolerances in the ruling: at **0.15** the
    move is ACCEPTED as real market movement (0.157 > 0.15), at **0.25** it is
    REJECTED as an adjustment defect (0.157 <= 0.25) — the misattribution HD-27
    was written to stop.  The constant therefore cannot be widened past 0.157
    without failing here.
    """

    # A 2.34x drop landing exactly on the 2:1 split bar.
    PRE = 96.0
    CLOSES = [99.0, 97.0, 99.0, PRE, PRE / 2.34, 41.0, 42.0, 41.5]

    def test_the_discrepancy_really_is_0_157(self):
        # Non-vacuity: if the arithmetic drifted, the pin below would stop
        # discriminating 0.15 from 0.25 and would silently pin nothing.
        jump = abs(math.log(self.CLOSES[4]) - math.log(self.CLOSES[3]))
        self.assertAlmostEqual(jump, 0.8502, places=4)
        self.assertGreater(jump, PARAMS.split_log_jump_threshold)
        self.assertAlmostEqual(abs(jump - math.log(2.0)), 0.157, places=3)

    def test_a_2_34x_drop_on_a_2_to_1_split_bar_is_ACCEPTED_at_this_tolerance(self):
        # Fails at 0.25 (and at 0.3, 0.4, 0.47): the guard would reject.
        verdict = run_guards(series_from(self.CLOSES), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertFalse(
            verdict.rejected,
            "a 2.34x crash on a split date was misattributed as an adjustment "
            "defect — the HD-27 defect itself, at a wider tolerance",
        )
        self.assertNotIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertEqual(len(verdict.observations), 1)
        self.assertIn("already adjusted", verdict.observations[0].verdict)

    def test_the_constant_cannot_be_widened_past_this_case(self):
        # Stated against the measured discrepancy rather than a literal, so the
        # bound tracks the case instead of drifting away from it.
        discrepancy = abs(
            abs(math.log(self.CLOSES[4]) - math.log(self.CLOSES[3])) - math.log(2.0)
        )
        self.assertLess(
            SPLIT_MATCH_TOLERANCE, discrepancy,
            f"SPLIT_MATCH_TOLERANCE={SPLIT_MATCH_TOLERANCE} is wide enough to "
            f"swallow a {discrepancy:.3f} discrepancy, so a genuine 2.34x crash "
            f"on a split date would be rejected as an adjustment defect (HD-27)",
        )


class AnUnusableCoefficientIsAbsentEvidenceNotAMismatch(unittest.TestCase):
    """B2 — 0, negative and NaN coefficients must not crash or be waved through.

    ``ln`` is undefined on all three, so there is no implied jump to compare the
    observation against.  The §18 guard's job is to turn bad input into a
    *structured rejection*; raising out of ``detect()`` fails that, and so does
    falling through to ACCEPT with evidence positively asserting that the prices
    are already adjusted — a claim nothing established.
    """

    # The 2:1 unadjusted shape, so a genuine defect is present to be missed.
    CLOSES = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]

    def _verdict(self, coefficient):
        return run_guards(series_from(self.CLOSES), PARAMS,
                          CorporateActions("X", {4: coefficient}))

    def test_a_zero_coefficient_rejects_instead_of_raising(self):
        # Was: ValueError('math domain error') escaping detect().
        verdict = self._verdict(0.0)
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)

    def test_a_negative_coefficient_rejects_instead_of_raising(self):
        verdict = self._verdict(-2.0)
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)

    def test_a_nan_coefficient_is_REJECTED_not_accepted_as_market_movement(self):
        # Was: rejected=False. A genuinely unadjusted 2:1 admitted as market
        # movement, because abs(jump - nan) <= tol is False and control fell
        # through to ACCEPT.
        verdict = self._verdict(float("nan"))
        self.assertTrue(verdict.rejected)
        self.assertEqual(verdict.observations, ())

    def test_the_evidence_names_the_unusable_value_and_claims_nothing_else(self):
        for coefficient, token in ((0.0, "0.0"), (-2.0, "-2.0"), (float("nan"), "nan")):
            with self.subTest(coefficient=coefficient):
                evidence = self._verdict(coefficient).rejections[0].evidence
                self.assertIn("not a usable ratio", evidence)
                self.assertIn(token, evidence)
                # It must not assert a reason it never established.
                self.assertNotIn("already adjusted", evidence)
                self.assertNotIn("unadjusted for this split", evidence)

    def test_it_escapes_neither_run_guards_nor_the_public_detect_entry_point(self):
        result = detect(series_from(self.CLOSES), PARAMS,
                        corporate_actions=CorporateActions("X", {4: 0.0}))
        self.assertTrue(result.guard.rejected)
        self.assertEqual(result.final_state, LineState.NONE)
        self.assertTrue(result.diagnostics["guard_rejections"])

    def test_the_same_series_with_a_USABLE_coefficient_adjudicates_normally(self):
        # Control: the new branch intercepts only unusable values, and this
        # series really does carry the defect the NaN case was admitting.
        verdict = self._verdict(2.0)
        self.assertTrue(verdict.rejected)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)


class ADirectionMismatchIsNotThatSplit(unittest.TestCase):
    """N1 — an UP-move cannot be a forward split, whatever its magnitude.

    An unadjusted series moves by exactly ``1/c`` across the split bar: a forward
    split (c > 1) makes prices FALL, a reverse split (c < 1) makes them RISE.
    Comparing magnitudes alone let 48 -> 96 "match" a 2:1 and produce evidence
    asserting "the series is unadjusted for this split" — a statement that is
    simply false, since an unadjusted 2:1 halves prices.
    """

    def test_a_doubling_on_a_2_to_1_split_bar_is_not_rejected_as_that_split(self):
        # Was: rejected=True, evidence "implies a log jump of 0.693147 and the
        # observed jump is 0.693147; the series is unadjusted for this split".
        closes = [48.0, 47.5, 48.0, 48.0, 96.0, 97.0, 95.0, 96.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertFalse(verdict.rejected)
        self.assertNotIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertEqual(verdict.rejections, ())

    def test_the_evidence_names_the_direction_and_makes_no_false_claim(self):
        closes = [48.0, 47.5, 48.0, 48.0, 96.0, 97.0, 95.0, 96.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertEqual(len(verdict.observations), 1)
        evidence = verdict.observations[0].verdict
        self.assertIn("wrong direction", evidence)
        self.assertNotIn("unadjusted for this split", evidence)

    def test_a_reverse_split_still_rejects_on_the_RISE_it_actually_produces(self):
        # Positive control for the direction rule's other half: an unadjusted
        # 1:10 makes prices rise tenfold, so |ln(0.1)| = 2.303 UP is the match.
        # Over-correcting the sign test would silently break this.
        closes = [10.0, 10.1, 9.9, 10.0, 100.0, 99.0, 101.0, 100.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 0.1}))
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)

    def test_a_crash_on_a_reverse_split_bar_is_a_direction_mismatch(self):
        # The mirror of the 48 -> 96 case: a 1:10 reverse cannot explain a FALL.
        closes = [100.0, 99.0, 101.0, 100.0, 10.0, 10.1, 9.9, 10.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 0.1}))
        self.assertFalse(verdict.rejected)
        self.assertIn("wrong direction", verdict.observations[0].verdict)


class AnOverAdjustedSeriesIsAcceptedAndTheGapIsDisclosed(unittest.TestCase):
    """B6 — the direction gate's cost, pinned so it cannot go back to silent.

    **This ACCEPT is not a desired outcome.** It is a detection gap the direction
    gate introduced, accepted deliberately and disclosed. Nothing here endorses
    it, and a reader must not take these assertions as saying an over-adjusted
    series *should* pass.

    Over-adjustment is the mirror vendor defect: a spurious split coefficient is
    reported, ``normalize()`` divides every earlier bar by it, and the split bar
    is left carrying ``+ln(c)`` instead of the ``-ln(c)`` an unadjusted series
    would show. Before the direction gate the guard REJECTED that shape as "the
    series is unadjusted for this split"; after it, the guard ACCEPTS. That
    change shipped undisclosed, which is what B6 was raised about.

    It is left as an ACCEPT because a ``+ln(c)`` step at a split bar genuinely
    cannot be separated from a real c-times move on the day, and HD-27 clause 2
    errs toward accepting where the hypotheses are indistinguishable. Separating
    them needs a distinct over-adjustment hypothesis that no ruling has supplied,
    so forcing a verdict here would be a product-definition change (GOV-007).

    What these tests do enforce is the honesty of the evidence: the guard may not
    claim the jump is unrelated to the split, because in the over-adjusted case
    the jump IS that split's adjustment, applied twice.
    """

    # +ln(2) at the split bar: every bar before it divided by 2 a second time.
    OVER_ADJUSTED = [48.0, 47.5, 48.0, 48.0, 96.0, 97.0, 95.0, 96.0]

    def test_the_over_adjusted_shape_really_is_plus_ln_c_at_the_split_bar(self):
        # Non-vacuity: if this were not a same-magnitude opposite-direction move
        # it would not reach the direction gate and would pin nothing.
        signed = math.log(self.OVER_ADJUSTED[4]) - math.log(self.OVER_ADJUSTED[3])
        self.assertAlmostEqual(signed, +math.log(2.0), places=9)
        self.assertGreater(abs(signed), PARAMS.split_log_jump_threshold)

    def test_an_over_adjusted_series_is_ACCEPTED_a_disclosed_detection_gap(self):
        # Before the direction gate this was REJECT "unadjusted for this split".
        # Pinned as the current, disclosed behaviour — NOT as a desired one.
        verdict = run_guards(series_from(self.OVER_ADJUSTED), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertFalse(verdict.rejected)
        self.assertEqual(verdict.rejections, ())
        self.assertNotIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)

    def test_the_verdict_does_not_claim_the_jump_is_not_that_split(self):
        # The false claim this replaces: "...so this jump is not that split".
        # In the over-adjusted case the jump IS that split's adjustment, applied
        # twice, so asserting otherwise states as fact something never measured —
        # the rule test_the_evidence_names_the_unusable_value_and_claims_nothing
        # _else already enforces on the neighbouring branch.
        verdict = run_guards(series_from(self.OVER_ADJUSTED), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertEqual(len(verdict.observations), 1)
        evidence = verdict.observations[0].verdict
        for false_claim in ("not that split", "is not the split",
                            "unrelated to the split", "already adjusted"):
            self.assertNotIn(
                false_claim, evidence,
                f"the wrong-direction evidence asserts {false_claim!r}, which it "
                f"never established and which is false when the series is "
                f"over-adjusted: {evidence}",
            )

    def test_the_verdict_still_reports_the_numbers_it_measured(self):
        # Restating the claim must not cost the evidence: the implied and
        # observed signed moves are what a reader needs to see the mismatch.
        verdict = run_guards(series_from(self.OVER_ADJUSTED), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        evidence = verdict.observations[0].verdict
        self.assertIn("wrong direction", evidence)
        self.assertIn(f"{-math.log(2.0):+.6f}", evidence)   # implied  -0.693147
        self.assertIn(f"{+math.log(2.0):+.6f}", evidence)   # observed +0.693147
        self.assertAlmostEqual(verdict.observations[0].split_coefficient, 2.0)

    def test_the_gap_is_the_same_at_other_coefficients_and_in_the_mirror(self):
        # c=10.0 and the reverse-split mirror c=0.1 behave identically, so the
        # gap is a property of the gate and not of one arithmetic accident.
        cases = (
            (10.0, [48.0, 47.5, 48.0, 48.0, 480.0, 485.0, 475.0, 480.0]),
            (0.1, [100.0, 99.0, 101.0, 100.0, 10.0, 10.1, 9.9, 10.0]),
        )
        for coefficient, closes in cases:
            with self.subTest(coefficient=coefficient):
                verdict = run_guards(series_from(closes), PARAMS,
                                     CorporateActions("X", {4: coefficient}))
                self.assertFalse(verdict.rejected)
                self.assertNotIn("not that split", verdict.observations[0].verdict)

    def test_the_gap_is_confined_to_the_wrong_direction_shape(self):
        # Control: the RIGHT-direction unadjusted 2:1 is still rejected, so this
        # class pins a gap rather than documenting a general failure to detect.
        verdict = run_guards(
            series_from([99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]),
            PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertTrue(verdict.rejected)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)


class ANonNumericCoefficientRejectsInsteadOfRaising(unittest.TestCase):
    """B2's escape class, one layer earlier: in ``coefficient_at`` itself.

    ``float(self.splits.get(...))` ran BEFORE the ``isfinite`` guard could see
    the value, so a feed recording ``None`` for a blank cell raised ``TypeError``
    and ``'n/a'`` for an unknown one raised ``ValueError`` — both escaping
    ``detect()`` instead of becoming the structured rejection §18 owes.
    """

    CLOSES = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]

    def _verdict(self, coefficient):
        return run_guards(series_from(self.CLOSES), PARAMS,
                          CorporateActions("X", {4: coefficient}))

    def test_none_and_a_string_reach_the_unusable_ratio_rejection(self):
        for coefficient in (None, "n/a", "", [], {}):
            with self.subTest(coefficient=coefficient):
                verdict = self._verdict(coefficient)  # was: TypeError/ValueError
                self.assertTrue(verdict.rejected)
                self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
                self.assertEqual(verdict.observations, ())

    def test_the_rejection_names_what_the_feed_RECORDED_not_the_nan_it_became(self):
        for coefficient in (None, "n/a"):
            with self.subTest(coefficient=coefficient):
                evidence = self._verdict(coefficient).rejections[0].evidence
                self.assertIn("not a usable ratio", evidence)
                self.assertIn(repr(coefficient), evidence)
                self.assertNotIn("already adjusted", evidence)
                self.assertNotIn("unadjusted for this split", evidence)

    def test_it_escapes_neither_run_guards_nor_the_public_detect_entry_point(self):
        result = detect(series_from(self.CLOSES), PARAMS,
                        corporate_actions=CorporateActions("X", {4: None}))
        self.assertTrue(result.guard.rejected)
        self.assertEqual(result.final_state, LineState.NONE)
        self.assertTrue(result.diagnostics["guard_rejections"])

    def test_a_NUMERIC_STRING_still_adjudicates_as_that_number(self):
        # Coercion is attempted, not type-checked: '2.0' was already handled and
        # must keep its verdict, so this fix widens nothing.
        verdict = self._verdict("2.0")
        self.assertTrue(verdict.rejected)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)


class AnAbsurdCoefficientAssertsNoCauseItDidNotEstablish(unittest.TestCase):
    """Finite but absurd ratios reach ACCEPT and must not claim a reason.

    1e-12, 1e12 and 5e-324 are finite and positive, so they pass the usability
    guard and are accepted. On this class's DOWNWARD series only ``1e12`` reaches
    the magnitude-mismatch ACCEPT that asserted "prices are already adjusted, so
    this is market movement" — an assertion no better established than it was for
    the ``nan`` case B2 fixed. ``1e-12`` and ``5e-324`` exit at the direction gate
    instead. That split is a property of the jump's SIGN, not of ``|ln c|``:
    ``|ln 1e-12| == |ln 1e12| == 27.631021``, and on an upward series the
    assignment inverts.

    No plausibility threshold is added: bounding what counts as a credible
    coefficient would be a product-definition change, out of scope here. The
    verdict is unchanged; only the claim is.
    """

    CLOSES = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]

    def test_they_are_still_ACCEPTED_no_threshold_was_smuggled_in(self):
        for coefficient in (1e-12, 1e12, 5e-324):
            with self.subTest(coefficient=coefficient):
                verdict = run_guards(series_from(self.CLOSES), PARAMS,
                                     CorporateActions("X", {4: coefficient}))
                self.assertFalse(verdict.rejected)
                self.assertEqual(len(verdict.observations), 1)

    def test_the_evidence_asserts_no_cause_for_the_move(self):
        for coefficient in (1e-12, 1e12, 5e-324):
            with self.subTest(coefficient=coefficient):
                verdict = run_guards(series_from(self.CLOSES), PARAMS,
                                     CorporateActions("X", {4: coefficient}))
                evidence = verdict.observations[0].verdict
                self.assertIn("no cause for the move is established", evidence)
                self.assertNotIn("so this is market movement", evidence)


class RecordedJumpFieldsKeepTheirMeaning(unittest.TestCase):
    """Carrying the sign into adjudication must not change what is REPORTED."""

    def test_log_jump_stays_a_magnitude_on_both_rejections_and_observations(self):
        rejected = run_guards(
            series_from([99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]),
            PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertGreater(rejected.rejections[0].log_jump, 0.0)
        accepted = run_guards(
            series_from([99.0, 97.0, 99.0, 96.0, 30.0, 29.0, 31.0, 30.5]),
            PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertGreater(accepted.observations[0].log_jump, 0.0)


class Gx10ContractIsPreserved(unittest.TestCase):
    """GX-10 is HD-22-immutable and carries no feed; it must still reject."""

    def test_the_committed_fixture_shape_still_rejects_without_a_feed(self):
        closes = [99.0, 97.0, 99.0, 96.0, 49.5]
        verdict = run_guards(series_from(closes), PARAMS, None)
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertEqual(verdict.rejections[0].bar, 4)




class UncoercibleIsUnusableIncludingTheTypesThatCoerceTooWell(unittest.TestCase):
    """Two escapes the earlier rounds missed, for opposite reasons.

    ``10**400`` raises ``OverflowError`` — an ``ArithmeticError``, so the
    ``(TypeError, ValueError)`` catch added for ``None`` and ``'n/a'`` did not
    cover it, and it escaped ``detect()``. ``True`` is the mirror: it coerces
    *cleanly* to 1.0, which the guard reads as "no split at this bar" and then
    emits evidence affirmatively denying a split. A malformed feed value
    becoming a positive claim is the HD-27 defect in miniature.
    """

    CLOSES = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]

    def _verdict(self, coefficient):
        return run_guards(series_from(self.CLOSES), PARAMS,
                          CorporateActions("X", {4: coefficient}))

    def test_a_huge_integer_rejects_instead_of_raising_OverflowError(self):
        verdict = self._verdict(10 ** 400)
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertIn("not a usable ratio", verdict.rejections[0].evidence)

    def test_it_escapes_neither_run_guards_nor_the_public_detect_entry_point(self):
        # The defect was an exception crossing the public boundary, so the
        # public boundary is where it is pinned.
        result = detect(series_from(self.CLOSES), PARAMS,
                        corporate_actions=CorporateActions("X", {4: 10 ** 400}))
        self.assertTrue(result.guard.rejected)

    def test_a_bool_is_unusable_not_a_coefficient_of_one(self):
        # float(True) == 1.0 would mean "no split", and the guard would then
        # ACCEPT the jump while claiming no split occurred.
        verdict = self._verdict(True)
        self.assertTrue(verdict.rejected, "a bool was read as 'no split at this bar'")
        self.assertIn("not a usable ratio", verdict.rejections[0].evidence)
        self.assertEqual(verdict.observations, ())

    def test_the_numeric_string_contract_is_untouched(self):
        # The bool check must not become a blanket type-check: '2.0' still
        # adjudicates as 2.0, which is a genuine unadjusted 2:1 here.
        verdict = self._verdict("2.0")
        self.assertTrue(verdict.rejected)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
