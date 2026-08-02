"""Tests for the backtest measurement layer. No network, no vendor data.

The metrics are arithmetic over realized bars, so they are tested against
hand-computed values on constructed series rather than against the engine's
output — a test that recomputed the metric the same way the code does would
prove nothing.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from engine.params import DetectorParams
from tools.research.scanner import backtest

#: Minimal params for the call-site pin; the geometry is irrelevant to it.
_PARAMS_FOR_PIN = DetectorParams(
    eps=0.02, eps_break=0.01, min_formation_bars=8, min_ath_age_bars=3,
    tolerance_version="tol-2026.07-illustrative", spec_version="UNVERSIONED-PENDING-OQ-J",
)


@dataclass(frozen=True)
class FakeBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class FakeLine:
    m: float


@dataclass(frozen=True)
class FakeFrozen:
    breakout_bar: int
    line: FakeLine


@dataclass
class FakeResult:
    transitions: tuple = ()
    final_state = None


def bars(closes, highs=None, lows=None):
    highs = highs or [c * 1.02 for c in closes]
    lows = lows or [c * 0.98 for c in closes]
    return [
        FakeBar(f"2026-01-{i + 1:02d}", c, h, lo, c, 1000)
        for i, (c, h, lo) in enumerate(zip(closes, highs, lows))
    ]


class ForwardReturns(unittest.TestCase):
    def test_returns_are_measured_from_the_breakout_close(self):
        # entry 100; +1 -> 110, +5 -> 150
        closes = [100.0] + [100.0 + 10.0 * k for k in range(1, 25)]
        b = bars(closes)
        out = backtest.measure_breakout("T", b, FakeResult(), FakeFrozen(0, FakeLine(-0.01)))
        self.assertAlmostEqual(out.forward_returns[1], 0.10)
        self.assertAlmostEqual(out.forward_returns[5], 0.50)
        self.assertAlmostEqual(out.forward_returns[20], 2.00)
        self.assertFalse(out.truncated)

    def test_a_short_series_yields_None_not_zero(self):
        # A truncated horizon is missing evidence. Substituting 0.0 would drag
        # the mean toward zero invisibly.
        b = bars([100.0, 101.0, 102.0])
        out = backtest.measure_breakout("T", b, FakeResult(), FakeFrozen(0, FakeLine(-0.01)))
        self.assertAlmostEqual(out.forward_returns[1], 0.01)
        self.assertIsNone(out.forward_returns[5])
        self.assertIsNone(out.forward_returns[20])
        self.assertTrue(out.truncated)
        self.assertEqual(out.bars_available, 2)

    def test_a_breakout_on_the_last_bar_has_no_forward_window(self):
        b = bars([100.0, 101.0])
        out = backtest.measure_breakout("T", b, FakeResult(), FakeFrozen(1, FakeLine(-0.01)))
        self.assertEqual(out.bars_available, 0)
        self.assertIsNone(out.mfe)
        self.assertIsNone(out.mae)
        self.assertTrue(all(v is None for v in out.forward_returns.values()))


class Excursions(unittest.TestCase):
    def test_mfe_and_mae_use_high_and_low_after_entry_only(self):
        closes = [100.0, 100.0, 100.0, 100.0]
        highs = [999.0, 120.0, 110.0, 105.0]  # bar 0's high must be ignored
        lows = [1.0, 95.0, 90.0, 97.0]        # bar 0's low must be ignored
        b = bars(closes, highs, lows)
        out = backtest.measure_breakout("T", b, FakeResult(), FakeFrozen(0, FakeLine(-0.01)))
        self.assertAlmostEqual(out.mfe, 0.20)   # 120/100 - 1
        self.assertAlmostEqual(out.mae, -0.10)  # 90/100 - 1


class Aggregation(unittest.TestCase):
    def make_outcome(self, ret20, mfe=0.1, mae=-0.05, truncated=False):
        return backtest.BreakoutOutcome(
            symbol="T", breakout_bar=0, breakout_date="d", entry_close=100.0,
            frozen_slope=-0.01, bars_available=20 if not truncated else 3,
            forward_returns={1: 0.01, 5: 0.02, 10: 0.03, 20: ret20},
            mfe=mfe, mae=mae, engine_outcome="OPEN_AT_SERIES_END",
            final_state="BROKEN_OUT", truncated=truncated,
        )

    def test_hit_rate_excludes_incomplete_horizons_and_says_how_many(self):
        r = backtest.SymbolReport("T", 100, "a", "b")
        r.breakouts = [self.make_outcome(0.05), self.make_outcome(-0.02), self.make_outcome(None, truncated=True)]
        agg = backtest.aggregate([r])
        h20 = agg["horizons"][20]
        self.assertEqual(h20["n"], 2)                    # the None is excluded
        self.assertEqual(h20["excluded_incomplete"], 1)  # and counted
        self.assertAlmostEqual(h20["hit_rate"], 0.5)
        self.assertEqual(agg["total_breakouts"], 3)
        self.assertEqual(agg["breakouts_truncated"], 1)

    def test_no_breakouts_yields_none_rather_than_a_fabricated_rate(self):
        r = backtest.SymbolReport("T", 100, "a", "b")
        agg = backtest.aggregate([r])
        self.assertEqual(agg["total_breakouts"], 0)
        self.assertIsNone(agg["horizons"][20]["hit_rate"])
        self.assertIsNone(agg["horizons"][20]["mean"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()


class EpisodeOutcomeIsReadFromTheEngineNotDefaulted(unittest.TestCase):
    """The classifier was silently vacuous; these tests exist so it cannot be again.

    It read ``record.reason_code`` while ``TransitionRecord``'s field is
    ``reason``, so a defaulted ``getattr`` turned every episode into
    ``OPEN_AT_SERIES_END``. A whole 40-symbol pass was measured on it and
    reported 306 of 306 events open at the series end — impossible across 40
    independent symbols, and the only reason it surfaced.

    Real ``ReasonCode`` and ``TransitionRecord`` objects are used rather than
    fakes: the defect was precisely a mismatch between this module's assumption
    and the engine's actual field name, and a fake carrying whatever field the
    test author imagined would reproduce the bug rather than catch it.
    """

    def _result(self, *records):
        from engine.state import LineState, ReasonCode, TransitionRecord

        return FakeResult(transitions=tuple(
            TransitionRecord(bar, LineState.BROKEN_OUT, LineState.NONE, ReasonCode[name])
            for bar, name in records
        ))

    def test_every_terminal_outcome_name_exists_on_the_engines_ReasonCode(self):
        # If the engine renames one, this fails here rather than degrading the
        # classifier to a constant.
        from engine.state import ReasonCode

        for name in backtest.TERMINAL_OUTCOMES:
            self.assertTrue(hasattr(ReasonCode, name), f"{name} is not a ReasonCode")

    def test_a_post_breakout_terminal_transition_is_returned(self):
        for name in backtest.TERMINAL_OUTCOMES:
            with self.subTest(outcome=name):
                result = self._result((12, name))
                self.assertEqual(backtest._episode_outcome(result, 10), name)

    def test_a_transition_at_or_before_the_breakout_bar_is_not_this_episodes_fate(self):
        result = self._result((10, "RETEST_HELD"), (8, "FAILED_BREAKOUT"))
        self.assertEqual(backtest._episode_outcome(result, 10), "OPEN_AT_SERIES_END")

    def test_the_FIRST_post_breakout_terminal_transition_wins(self):
        result = self._result((12, "RETEST_HELD"), (15, "FAILED_BREAKOUT"))
        self.assertEqual(backtest._episode_outcome(result, 10), "RETEST_HELD")

    def test_a_non_terminal_post_breakout_transition_leaves_the_episode_open(self):
        result = self._result((12, "WICK_BREAK"))
        self.assertEqual(backtest._episode_outcome(result, 10), "OPEN_AT_SERIES_END")

    def test_it_raises_rather_than_defaulting_when_the_record_shape_is_wrong(self):
        # The regression itself: a record lacking `reason` must be an error, not
        # a silent OPEN_AT_SERIES_END.
        @dataclass(frozen=True)
        class RecordWithoutReason:
            bar: int

        with self.assertRaises(AttributeError):
            backtest._episode_outcome(FakeResult(transitions=(RecordWithoutReason(12),)), 10)


class TheCompletenessDeclarationIsPinned(unittest.TestCase):
    """`complete_history=True` had no test, and deleting it stayed green.

    Code Review measured it at `43282fd`: the argument at `run_symbol`'s
    `CorporateActions` construction is what preserves AAPL 2000-09-29 under
    HD-29 (ii), and removing it left BOTH the engine suite and this suite
    passing while silently reverting that preservation and moving the published
    306/255 event counts. A silent measurement defect is exactly what the CI
    harness step exists to catch, so it is caught here rather than logged.

    This asserts the call site, not the engine's behaviour — the engine's half
    is pinned by `AnEmptyFeedIsAbsentEvidenceNotEvidenceOfAbsence`.
    """

    def test_run_symbol_declares_the_feed_complete(self):
        captured = {}
        real = backtest.CorporateActions

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        backtest.CorporateActions = spy
        try:
            bars = [FakeBar(f"d{i:03d}", 10.0, 10.0, 9.0, 10.0, 100) for i in range(30)]

            @dataclass
            class FakeSeries:
                bars: list
                splits_applied: tuple = ()

            backtest.run_symbol("X", FakeSeries(bars=bars), _PARAMS_FOR_PIN)
        finally:
            backtest.CorporateActions = real

        self.assertIn(
            "complete_history", captured,
            "run_symbol no longer declares feed completeness — HD-29 (ii) makes an "
            "undeclared feed absent evidence, so every symbol whose supra-threshold "
            "jump lands on a non-split bar silently reverts to REJECT, AAPL included",
        )
        self.assertTrue(captured["complete_history"])

    def test_the_declaration_is_what_the_provider_actually_supports(self):
        """The invariant the declaration rests on, asserted structurally.

        This method previously read `normalize`'s SOURCE and asserted the
        substring "split" appeared in it. That cannot fail for any recognisable
        version of the function — the docstring alone satisfies it — and Code
        Review measured it **green against a `normalize()` whose
        `splits_applied` is hardcoded to `()`**, which is M-74's exact failure.
        A test that passes against the defect it names is worse than no test,
        and it was the M-70 shape (a substring check that does not do what its
        name says) reintroduced by the commit whose subject was that a
        load-bearing line had no test.

        What actually makes `complete_history=True` honest is that `normalize`
        derives `splits_applied` from the same payload rows it builds `bars`
        from, so every split date IS a bar date and a bar with no entry is one
        the vendor recorded as 1.0. That is asserted here on a real normalized
        payload, not read out of the source text.
        """
        from tools.research.providers import alphavantage as av

        payload = {
            "Meta Data": {"3. Last Refreshed": "2020-01-03", "4. Output Size": "full"},
            "Time Series (Daily)": {
                "2020-01-02": {"1. open": "100.0", "2. high": "101.0", "3. low": "99.0",
                               "4. close": "100.0", "6. volume": "1000",
                               "8. split coefficient": "1.0"},
                "2020-01-03": {"1. open": "50.0", "2. high": "51.0", "3. low": "49.0",
                               "4. close": "50.0", "6. volume": "2000",
                               "8. split coefficient": "2.0"},
            },
        }
        series = av.normalize(payload, "X")

        bar_dates = {b.date for b in series.bars}
        split_dates = {d for d, _ in series.splits_applied}

        # 1. The split was recorded at all — this is what the old assertion
        #    could not detect.
        self.assertEqual(split_dates, {"2020-01-03"})
        # 2. Every split date is a bar date. This is the invariant
        #    `complete_history=True` depends on: a bar with no entry is a bar
        #    the vendor said had no split, not a bar the feed forgot.
        self.assertTrue(split_dates <= bar_dates,
                        "a split date is not a bar date; `complete_history=True` "
                        "would be a false declaration (M-74)")
