"""Small builders shared by the unit, property and mutation suites."""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

from ..bars import Bar, BarSeries
from ..params import DetectorParams
from .conformance import SPEC_VERSION

__all__ = ["make_series", "default_params"]


def default_params(**overrides) -> DetectorParams:
    """The ratified defaults (HD-14 / D-TL-12) with an illustrative eps_break.

    ``eps_break`` is unlocked (HD-03 / §13.5); the value used here is the one the
    fixtures document as illustrative, and every test that depends on it says so.
    """
    params = DetectorParams(
        eps=0.02,
        eps_break=0.01,
        min_formation_bars=8,
        min_ath_age_bars=3,
        tolerance_version="tol-2026.07-illustrative",
        spec_version=SPEC_VERSION,
    )
    return params.replace(**overrides) if overrides else params


def make_series(
    highs: Sequence[float],
    closes: Optional[Sequence[float]] = None,
    lows: Optional[Sequence[float]] = None,
    opens: Optional[Sequence[float]] = None,
) -> BarSeries:
    """Build a synthetic series from highs, defaulting the other fields safely.

    Closes default to ``0.9 * high`` so they never accidentally clear a line: a
    constructed case must test the thing it names, not a breakout it did not
    intend.
    """
    n = len(highs)
    closes = list(closes) if closes is not None else [h * 0.9 for h in highs]
    lows = list(lows) if lows is not None else [min(h, c) * 0.95 for h, c in zip(highs, closes)]
    opens = list(opens) if opens is not None else list(closes)
    bars: List[Bar] = []
    for index in range(n):
        bars.append(
            Bar(
                t=index,
                timestamp=index,
                open=opens[index],
                high=highs[index],
                low=lows[index],
                close=closes[index],
                volume=1_000_000.0,
            )
        )
    return BarSeries(bars)
