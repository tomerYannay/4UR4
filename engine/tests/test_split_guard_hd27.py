"""HD-27 regression tests: a crash is not an adjustment defect.

The defect this pins was found on real data, not in review. AAPL fell **51.9% on
2000-09-29** on a profit warning — split coefficient 1.0, no corporate action —
and the §18 guard read it as ``SUSPECTED_UNADJUSTED_SPLIT`` and rejected the
**entire 26-year bar-set**. The engine emitted nothing for AAPL: ``final_state
NONE``, zero breakouts, and no diagnostic that said why.

The engine has grown further branches under HD-29; the authoritative list is
`_adjudicate_jump` in source order, and no count is restated here — every
restatement of it in this repository has gone stale at least once.

The four cases the Product Owner named are each a test below, and the real
numbers are used rather than invented ones — a synthetic 50% drop would prove
the arithmetic but not that the guard behaves correctly on the event that
actually broke it.

**HD-29 (2026-07-29) moved two verdicts and this file records both.** (i) A
supra-threshold move whose direction is inconsistent with the recorded split now
REJECTS instead of accepting, so ``AnOverAdjustedSeriesIsRejectedAsUnexplained``
is the inversion of a class that used to pin the opposite. (ii) A feed holding no
split data is absent evidence, so ``CorporateActions`` carries an explicit
``complete_history`` flag and the AAPL cases declare it rather than relying on an
empty dict to mean two different things.
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
    """Case 1 — AAPL 2000-09-29: a genuine >50% decline must be ACCEPTED.

    Every feed here declares ``complete_history=True``, which is the fact these
    cases always relied on and, before HD-29, expressed only by accident. The
    vendor payload the pilot fetches carries the whole split history for the
    range it returns, so "no entry at bar 7" is a **record** that no split
    happened, not a silence. HD-29 (ii) made the difference sayable; it did not
    change what is true of AAPL.
    """

    # The vendor's own as-traded closes across the event, split coefficient 1.0
    # on every one of them.
    CLOSES = [61.05, 56.69, 52.19, 53.50, 51.44, 48.94, 53.50, 25.75, 24.25, 22.31,
              23.62, 22.06, 22.19, 21.75, 20.62, 19.75, 20.12, 19.25, 18.94, 19.50]

    @staticmethod
    def feed():
        """The complete-history feed these cases have always meant."""
        return CorporateActions(symbol="AAPL", splits={}, complete_history=True)

    def test_the_jump_really_does_exceed_the_threshold(self):
        # If it did not, the rest of this class would pass vacuously.
        jump = abs(math.log(25.75) - math.log(53.50))
        self.assertGreater(jump, PARAMS.split_log_jump_threshold)
        self.assertAlmostEqual(jump, 0.7312, places=3)

    def test_with_a_COMPLETE_feed_showing_no_split_the_series_is_ACCEPTED(self):
        # Renamed from ...with_a_split_feed_showing_no_split...: it passed ``{}``,
        # which is a feed showing NOTHING, and the name said "showing no split".
        # The conflation HD-29 (ii) removes had become load-bearing in the name
        # of the test that pins the whole point of HD-27.
        s = series_from(self.CLOSES)
        verdict = run_guards(s, PARAMS, self.feed())
        self.assertFalse(verdict.rejected, "a real crash was rejected as a split defect")
        self.assertEqual(verdict.rejections, ())
        self.assertNotIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)

    def test_the_accepted_jump_is_OBSERVED_not_silently_swallowed(self):
        # Requirement 5: never fail silently. An accepted jump and an untested
        # one must not look identical.
        s = series_from(self.CLOSES)
        verdict = run_guards(s, PARAMS, self.feed())
        self.assertEqual(len(verdict.observations), 1)
        obs = verdict.observations[0]
        self.assertEqual(obs.bar, 7)
        self.assertAlmostEqual(obs.split_coefficient, 1.0)
        self.assertGreater(obs.log_jump, obs.threshold)
        self.assertIn("no split", obs.verdict)
        # HD-29 cites this exact clause as the proof that coverage is visible in
        # the emitted evidence rather than only in the code. Deleting it killed
        # zero tests until this line existed — a record citing a string nothing
        # pinned. Found by Code Review at 43282fd.
        self.assertIn("on a feed that covers it", obs.verdict)

    def test_the_engine_now_runs_geometry_instead_of_returning_NONE(self):
        s = series_from(self.CLOSES)
        result = detect(s, PARAMS, corporate_actions=self.feed())
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


class AnEmptyFeedIsAbsentEvidenceNotEvidenceOfAbsence(unittest.TestCase):
    """HD-29 (ii) / M-65 — ``{}`` is a feed holding nothing, not reporting nothing.

    Before HD-29, ``None`` and ``CorporateActions(sym, {})`` were two spellings of
    *"I hold no split data"* that produced **opposite** verdicts: ``None``
    rejected conservatively, ``{}`` was believed and ACCEPTED, emitting an
    observation that affirmatively denied a split had occurred. M-65 measured
    that on real raw NVDA — an unadjusted 10:1 admitted, then read by the engine
    as a 90% drawdown, which is exactly the false-ATH failure HD-01 names.

    The fix is a declared coverage field, not a rule that empty means unknown:
    the distinction lives on the *bar*, so a complete feed's silence at a bar is
    still a record. Both halves are pinned here, because getting only the first
    half re-breaks AAPL.
    """

    AAPL = AaplCrashIsRealMarketData.CLOSES

    def test_a_bare_empty_feed_REJECTS_the_supra_threshold_jump(self):
        # Was: rejected=False, observation "no split at this bar".
        verdict = run_guards(series_from(self.AAPL), PARAMS,
                             CorporateActions("AAPL", {}))
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertEqual(verdict.observations, ())
        self.assertEqual(verdict.rejections[0].bar, 7)

    def test_the_default_is_the_SAFE_direction(self):
        # A caller that forgets to declare coverage must not have its ignorance
        # promoted into a positive claim.
        self.assertFalse(CorporateActions("AAPL", {}).complete_history)
        self.assertFalse(CorporateActions("AAPL", {}).covers(7))
        self.assertTrue(CorporateActions("AAPL", {}, True).covers(7))

    def test_the_evidence_claims_only_that_the_feed_is_silent(self):
        evidence = run_guards(series_from(self.AAPL), PARAMS,
                              CorporateActions("AAPL", {})).rejections[0].evidence
        self.assertIn("holds no entry at this bar", evidence)
        self.assertIn("absent evidence", evidence)
        # It must assert nothing about the cause, in either direction.
        self.assertNotIn("already adjusted", evidence)
        self.assertNotIn("unadjusted for this split", evidence)
        self.assertNotIn("no split at this bar", evidence)

    def test_a_feed_DECLARING_complete_coverage_still_ACCEPTS_the_AAPL_crash(self):
        # The regression guard for the trap: if an empty dict alone came to mean
        # "no data", AAPL 2000-09-29 would be rejected again and HD-27's whole
        # point would be undone by its own fix.
        verdict = run_guards(series_from(self.AAPL), PARAMS,
                             CorporateActions("AAPL", {}, complete_history=True))
        self.assertFalse(verdict.rejected, "HD-27's own case was rejected again")
        self.assertEqual(verdict.rejections, ())
        self.assertEqual(len(verdict.observations), 1)
        self.assertAlmostEqual(verdict.observations[0].split_coefficient, 1.0)

    def test_coverage_is_read_per_BAR_not_per_feed(self):
        # A feed with an entry elsewhere is still silent about bar 7, so the
        # non-emptiness of the dict must not be mistaken for coverage of it.
        verdict = run_guards(series_from(self.AAPL), PARAMS,
                             CorporateActions("AAPL", {2: 2.0}))
        self.assertTrue(verdict.rejected)
        self.assertIn("holds no entry at this bar", verdict.rejections[0].evidence)

    def test_an_entry_AT_the_bar_is_coverage_even_without_the_declaration(self):
        # The feed recorded something here, so it is not silent, and the existing
        # branches judge what it recorded. Coverage does not gate that.
        verdict = run_guards(
            series_from([99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]),
            PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertTrue(verdict.rejected)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)

    def test_a_subthreshold_series_is_untouched_by_coverage(self):
        # Coverage is consulted only where a jump triggered inspection, so an
        # undeclared feed does not reject a quiet series.
        verdict = run_guards(
            series_from([99.0, 97.0, 99.0, 96.0, 97.5, 98.0, 96.5, 97.0]),
            PARAMS, CorporateActions("X", {}))
        self.assertFalse(verdict.rejected)
        self.assertEqual(verdict.observations, ())

    def test_it_reaches_the_public_detect_entry_point(self):
        result = detect(series_from(self.AAPL), PARAMS,
                        corporate_actions=CorporateActions("AAPL", {}))
        self.assertTrue(result.guard.rejected)
        self.assertEqual(result.final_state, LineState.NONE)
        self.assertTrue(result.diagnostics["guard_rejections"])


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

    **N1's claim survives HD-29 (i); only the verdict moved.** The false
    *reason* — "the series is unadjusted for this split" — is still forbidden
    here, because it is still false. What HD-29 changed is that the bar-set is
    now REJECTED for the honest reason (the direction is inconsistent with the
    recorded split and the cause is not established) instead of ACCEPTED for
    want of a hypothesis. So these cases assert the same thing about the
    evidence and the opposite thing about ``rejected``.
    """

    def test_a_doubling_on_a_2_to_1_split_bar_is_not_called_that_split(self):
        # Renamed from ..._is_not_rejected_as_that_split: it now IS rejected,
        # just not AS that split. Was rejected=True with the false reason before
        # N1, ACCEPT after N1, and rejected=True with an honest reason after
        # HD-29 — the reason is what N1 was ever about.
        closes = [48.0, 47.5, 48.0, 48.0, 96.0, 97.0, 95.0, 96.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertEqual(verdict.observations, ())
        self.assertNotIn("unadjusted for this split", verdict.rejections[0].evidence)

    def test_the_evidence_names_the_direction_and_makes_no_false_claim(self):
        closes = [48.0, 47.5, 48.0, 48.0, 96.0, 97.0, 95.0, 96.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertEqual(len(verdict.rejections), 1)
        evidence = verdict.rejections[0].evidence
        self.assertIn("wrong direction", evidence)
        self.assertNotIn("unadjusted for this split", evidence)

    def test_a_reverse_split_still_rejects_on_the_RISE_it_actually_produces(self):
        # Positive control for the direction rule's other half: an unadjusted
        # 1:10 makes prices rise tenfold, so |ln(0.1)| = 2.303 UP is the match.
        # Over-correcting the sign test would silently break this — and now that
        # BOTH directions reject, the control is about the REASON: only this one
        # may say "unadjusted for this split".
        closes = [10.0, 10.1, 9.9, 10.0, 100.0, 99.0, 101.0, 100.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 0.1}))
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)
        self.assertNotIn("wrong direction", verdict.rejections[0].evidence)

    def test_a_crash_on_a_reverse_split_bar_is_a_direction_mismatch(self):
        # The mirror of the 48 -> 96 case: a 1:10 reverse cannot explain a FALL.
        closes = [100.0, 99.0, 101.0, 100.0, 10.0, 10.1, 9.9, 10.0]
        verdict = run_guards(series_from(closes), PARAMS,
                             CorporateActions("X", {4: 0.1}))
        self.assertTrue(verdict.rejected)
        self.assertIn("wrong direction", verdict.rejections[0].evidence)


class AnOverAdjustedSeriesIsRejectedAsUnexplained(unittest.TestCase):
    """B6 / HD-29 (i) — the wrong-direction shape REJECTS, claiming no cause.

    **This class inverts.** It used to be
    ``AnOverAdjustedSeriesIsAcceptedAndTheGapIsDisclosed`` and pinned an ACCEPT
    as a "detection gap accepted deliberately". It is no longer a gap and no
    longer an accept: HD-29 (i) rules that a supra-threshold move whose direction
    is inconsistent with the recorded split REJECTS the bar-set.

    Why the old reasoning failed. The ACCEPT rested on "the two hypotheses cannot
    be separated, and closing the gap would need a distinct over-adjustment
    hypothesis that no ruling supplies". The Strategic Product Reviewer found the
    guard reasoning from that *identical* premise to the *opposite* verdict sixty
    lines earlier — the unusable-coefficient branch says that where the
    hypotheses cannot be separated "the safe direction is to reject" — and that
    the missing-hypothesis argument is true for DETECTING over-adjustment and
    false for REJECTING an ambiguous bar-set. Rejecting needs no hypothesis about
    the cause; it needs only the honest report that none was established.

    So what is pinned here is a rejection whose evidence claims **only the
    direction mismatch**. It must not say the series is over-adjusted and it must
    not say the prices are already adjusted: those remain untested hypotheses,
    and asserting either would be the wording defect B6 and B2 both attacked.
    Over-adjustment is still the shape that motivates the case — a spurious
    coefficient makes ``normalize()`` divide every EARLIER bar by ``c``, leaving
    ``+ln(c)`` at the split bar instead of ``-ln(c)`` — but it remains a
    hypothesis about the world, not a finding of this guard.
    """

    # +ln(2) at the split bar: every bar before it divided by 2 a second time.
    OVER_ADJUSTED = [48.0, 47.5, 48.0, 48.0, 96.0, 97.0, 95.0, 96.0]

    def test_the_over_adjusted_shape_really_is_plus_ln_c_at_the_split_bar(self):
        # Non-vacuity, kept verbatim in intent: if this were not a same-magnitude
        # opposite-direction move it would not reach the direction gate and would
        # pin nothing.
        signed = math.log(self.OVER_ADJUSTED[4]) - math.log(self.OVER_ADJUSTED[3])
        self.assertAlmostEqual(signed, +math.log(2.0), places=9)
        self.assertGreater(abs(signed), PARAMS.split_log_jump_threshold)

    def test_an_over_adjusted_series_is_REJECTED(self):
        # Was ACCEPTED (rejected=False, one observation) before HD-29.
        verdict = run_guards(series_from(self.OVER_ADJUSTED), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertEqual(verdict.observations, ())
        self.assertEqual(verdict.rejections[0].bar, 4)

    def test_the_rejection_claims_ONLY_the_direction_mismatch(self):
        # HD-29 forbids this branch from claiming over-adjustment just as firmly
        # as it forbade it from claiming the jump was unrelated to the split. The
        # verdict changed; the wording rule did not.
        verdict = run_guards(series_from(self.OVER_ADJUSTED), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        self.assertEqual(len(verdict.rejections), 1)
        evidence = verdict.rejections[0].evidence
        for false_claim in ("not that split", "is not the split",
                            "unrelated to the split", "already adjusted",
                            "unadjusted for this split", "over-adjusted",
                            "over-adjustment"):
            self.assertNotIn(
                false_claim, evidence,
                f"the wrong-direction evidence asserts {false_claim!r}, which it "
                f"never established: {evidence}",
            )
        self.assertIn("no cause for the move is established", evidence)

    def test_the_rejection_still_reports_the_numbers_it_measured(self):
        # Changing the verdict must not cost the evidence: the implied and
        # observed signed moves are what a reader needs to see the mismatch.
        verdict = run_guards(series_from(self.OVER_ADJUSTED), PARAMS,
                             CorporateActions("X", {4: 2.0}))
        r = verdict.rejections[0]
        self.assertIn("wrong direction", r.evidence)
        self.assertIn(f"{-math.log(2.0):+.6f}", r.evidence)   # implied  -0.693147
        self.assertIn(f"{+math.log(2.0):+.6f}", r.evidence)   # observed +0.693147
        self.assertAlmostEqual(r.split_coefficient, 2.0)
        self.assertGreater(r.log_jump, r.threshold)

    def test_it_is_the_same_at_other_coefficients_and_in_the_mirror(self):
        # c=10.0 and the reverse-split mirror c=0.1 behave identically, so this
        # is a property of the gate and not of one arithmetic accident. Both were
        # ACCEPTED before HD-29. The construction is coefficient-matched: each c
        # gets ITS OWN +ln(c) series, which is what over-adjustment actually is
        # for that c.
        cases = (
            (10.0, [48.0, 47.5, 48.0, 48.0, 480.0, 485.0, 475.0, 480.0]),
            (0.1, [100.0, 99.0, 101.0, 100.0, 10.0, 10.1, 9.9, 10.0]),
        )
        for coefficient, closes in cases:
            with self.subTest(coefficient=coefficient):
                # Non-vacuity per case: the jump really is +/-ln(c) exactly.
                signed = math.log(closes[4]) - math.log(closes[3])
                self.assertAlmostEqual(abs(signed), abs(math.log(coefficient)),
                                       places=9)
                verdict = run_guards(series_from(closes), PARAMS,
                                     CorporateActions("X", {4: coefficient}))
                self.assertTrue(verdict.rejected)
                self.assertEqual(verdict.observations, ())
                evidence = verdict.rejections[0].evidence
                self.assertIn("wrong direction", evidence)
                self.assertNotIn("not that split", evidence)
                self.assertNotIn("unadjusted for this split", evidence)

    def test_the_RIGHT_direction_shape_keeps_its_own_distinct_reason(self):
        # Positive control, retained: now that both directions reject, the thing
        # to protect is that they do NOT collapse into one reason. Only a
        # genuinely unadjusted 2:1 may be called unadjusted for that split.
        verdict = run_guards(
            series_from([99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]),
            PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertTrue(verdict.rejected)
        self.assertIn("unadjusted for this split", verdict.rejections[0].evidence)
        self.assertNotIn("wrong direction", verdict.rejections[0].evidence)

    def test_a_real_move_that_does_not_match_the_split_is_still_ACCEPTED(self):
        # Second control, against over-correction: HD-29 rejects on DIRECTION,
        # not on "anything at a split bar". A right-direction magnitude mismatch
        # is untouched, so HD-27's core accept still stands.
        verdict = run_guards(
            series_from([99.0, 97.0, 99.0, 96.0, 30.0, 29.0, 31.0, 30.5]),
            PARAMS, CorporateActions("X", {4: 2.0}))
        self.assertFalse(verdict.rejected)
        self.assertEqual(len(verdict.observations), 1)


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
    """Finite but absurd ratios must not claim a reason — magnitude branch.

    1e-12, 1e12 and 5e-324 are finite and positive, so they pass the usability
    guard, and this class used to assert one verdict for all three. It cannot any
    more, because they do not reach the same branch and HD-29 moved one of those
    branches. **Which one an absurd coefficient reaches is a property of the
    jump's SIGN, not of** ``|ln c|``: ``|ln 1e-12| == |ln 1e12| == 27.631021``,
    and on an upward series the assignment inverts.

    On this class's DOWNWARD series only ``1e12`` has the right direction, so
    only it reaches the magnitude-mismatch ACCEPT — the branch that asserted
    "prices are already adjusted, so this is market movement", an assertion no
    better established than it was for the ``nan`` case B2 fixed. Its verdict is
    unchanged by HD-29; only the claim was ever at issue. ``1e-12`` and
    ``5e-324`` are the sibling class below.

    No plausibility threshold is added: bounding what counts as a credible
    coefficient would be a product-definition change, out of scope here.
    """

    CLOSES = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]
    #: Same sign as the implied move, so the direction gate passes it through.
    RIGHT_DIRECTION = 1e12

    def test_the_series_really_falls_so_only_a_c_above_one_reaches_this_branch(self):
        # Non-vacuity: pins the premise that splits this class from the next.
        signed = math.log(self.CLOSES[4]) - math.log(self.CLOSES[3])
        self.assertLess(signed, 0.0)
        self.assertLess(-math.log(self.RIGHT_DIRECTION), 0.0)

    def test_it_is_still_ACCEPTED_no_threshold_was_smuggled_in(self):
        verdict = run_guards(series_from(self.CLOSES), PARAMS,
                             CorporateActions("X", {4: self.RIGHT_DIRECTION}))
        self.assertFalse(verdict.rejected)
        self.assertEqual(len(verdict.observations), 1)

    def test_the_evidence_asserts_no_cause_for_the_move(self):
        verdict = run_guards(series_from(self.CLOSES), PARAMS,
                             CorporateActions("X", {4: self.RIGHT_DIRECTION}))
        evidence = verdict.observations[0].verdict
        self.assertIn("no cause for the move is established", evidence)
        self.assertNotIn("so this is market movement", evidence)
        # It reached the MAGNITUDE branch, not the direction gate.
        self.assertNotIn("wrong direction", evidence)


class AnAbsurdCoefficientInTheWrongDirectionNowRejects(unittest.TestCase):
    """The other half of the split — ``1e-12`` and ``5e-324`` on a FALLING series.

    A coefficient below 1 implies a RISE in an unadjusted series, so on this
    downward jump both land at the direction gate rather than the magnitude one.
    Before HD-29 that gate accepted and they were indistinguishable in outcome
    from ``1e12``; after HD-29 it rejects, and the old class's single
    all-three assertion would have been half true. Each assertion here is about
    the branch it actually reaches.

    Still no plausibility threshold: these reject because their DIRECTION is
    inconsistent with the observed move, exactly as ``c=2.0`` does on the
    over-adjusted shape — not because 5e-324 is an implausible ratio.
    """

    CLOSES = [99.0, 97.0, 99.0, 96.0, 49.5, 49.0, 50.0, 48.5]
    WRONG_DIRECTION = (1e-12, 5e-324)

    def test_they_really_do_reach_the_direction_gate(self):
        # Non-vacuity: sign disagreement, on a series that falls.
        signed = math.log(self.CLOSES[4]) - math.log(self.CLOSES[3])
        for coefficient in self.WRONG_DIRECTION:
            with self.subTest(coefficient=coefficient):
                self.assertLess(signed * -math.log(coefficient), 0.0)

    def test_they_are_REJECTED_at_the_direction_gate(self):
        for coefficient in self.WRONG_DIRECTION:
            with self.subTest(coefficient=coefficient):
                verdict = run_guards(series_from(self.CLOSES), PARAMS,
                                     CorporateActions("X", {4: coefficient}))
                self.assertTrue(verdict.rejected)
                self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
                self.assertEqual(verdict.observations, ())

    def test_the_evidence_asserts_no_cause_and_does_not_claim_the_magnitude(self):
        for coefficient in self.WRONG_DIRECTION:
            with self.subTest(coefficient=coefficient):
                verdict = run_guards(series_from(self.CLOSES), PARAMS,
                                     CorporateActions("X", {4: coefficient}))
                evidence = verdict.rejections[0].evidence
                self.assertIn("wrong direction", evidence)
                self.assertIn("no cause for the move is established", evidence)
                self.assertNotIn("already adjusted", evidence)
                self.assertNotIn("unadjusted for this split", evidence)
                # The magnitudes here differ by ~27 in log space, so the reason
                # must not assert the move matched the split in size.
                self.assertNotIn("split magnitude", evidence)


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
