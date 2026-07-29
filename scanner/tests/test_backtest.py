"""Tests for the backtest measurement layer. No network, no vendor data.

The metrics are arithmetic over realized bars, so they are tested against
hand-computed values on constructed series rather than against the engine's
output — a test that recomputed the metric the same way the code does would
prove nothing.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from scanner import backtest


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
