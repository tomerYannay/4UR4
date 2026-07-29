"""HD-27 regression tests: a crash is not an adjustment defect.

The defect this pins was found on real data, not in review. AAPL fell **51.9% on
2000-09-29** on a profit warning — split coefficient 1.0, no corporate action —
and the §18 guard read it as ``SUSPECTED_UNADJUSTED_SPLIT`` and rejected the
**entire 26-year bar-set**. The engine emitted nothing for AAPL: ``final_state
NONE``, zero breakouts, and no diagnostic that said why.

The four cases the Product Owner named are each a test below, and the real
numbers are used rather than invented ones — a synthetic 50% drop would prove
the arithmetic but not that the guard behaves correctly on the event that
actually broke it.
"""

from __future__ import annotations

import math
import unittest

from engine.bars import Bar, BarSeries
from engine.detector import detect
from engine.guards import CorporateActions, run_guards
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


class Gx10ContractIsPreserved(unittest.TestCase):
    """GX-10 is HD-22-immutable and carries no feed; it must still reject."""

    def test_the_committed_fixture_shape_still_rejects_without_a_feed(self):
        closes = [99.0, 97.0, 99.0, 96.0, 49.5]
        verdict = run_guards(series_from(closes), PARAMS, None)
        self.assertTrue(verdict.rejected)
        self.assertIn(ReasonCode.SUSPECTED_UNADJUSTED_SPLIT, verdict.codes)
        self.assertEqual(verdict.rejections[0].bar, 4)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
