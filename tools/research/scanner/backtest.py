"""Exploratory, survivor-biased backtest of the 4UR4 engine on vendor data.

**SURVIVOR-BIASED EXPLORATORY REAL-MARKET VALIDATION — authorized by HD-26.**
**This is NOT Phase 4 entry, NOT Phase 4 implementation, and NOT Phase 4 exit
evidence, and must never be cited as any of them.** Phase 4's exit criterion is a backtest over the
historical 4UR4 US Large-Cap 500 at each date's point-in-time membership; this
is a handful of tickers that happen to exist today, over a window of whatever
length the free tier returns.

Four limits, stated here because every number this module produces inherits all
of them and none is recoverable by analysis:

1. **SURVIVORSHIP BIAS.** The universe is tickers that exist *today*. Every name
   that delisted, was acquired or went to zero is absent, and those are
   disproportionately the ones a breakout strategy would have lost money on.
   This biases every aggregate **upward** by an unknown amount. HD-07 exists
   because of exactly this, and it is unresolved.

2. **THE ANCHOR IS AN ALL-TIME HIGH *OF THE DELIVERED WINDOW*.** The premium
   key returns full history (~6,700 daily bars back to 1999 for the names here),
   so the anchor is a genuine multi-decade high and this does test the thesis
   rather than a proxy. It is still bounded by what the vendor delivers: a name
   whose true all-time high predates the window would be anchored on a lower
   maximum. *(An earlier form of this note said the free tier's ~100 bars made
   the anchor a 5-month local high. That was true of the free tier and is not
   true of the data actually used — corrected rather than left standing.)*

3. **NO MULTIPLE-COMPARISON CONTROL.** One parameter set, one window, one
   universe, and every metric reported. Treat any apparent edge as a hypothesis
   to test, never as a result.

4. **FORWARD RETURNS ARE MEASURED, NOT TRADED.** No costs, no slippage, no
   borrow, no fills. Entry is the breakout bar's close, which is not obtainable
   in practice — the signal is *known* at that close, so the earliest realistic
   entry is the next open.

The engine itself is causal (§21.8): a breakout at bar ``b`` is determined by
bars ``0..b`` alone. Forward returns are a post-hoc measurement over realized
bars **after** ``b``, which is what a backtest is; the look-ahead question does
not arise for the *signal*, only for the *entry price*, and limit 4 records that.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

from engine.bars import Bar as EngineBar
from engine.bars import BarSeries
from engine.detector import DetectionResult, detect
from engine.guards import CorporateActions
from engine.params import DetectorParams
from engine.state import LineState

#: Horizons in **trading days** (bars), not calendar days.
HORIZONS = (1, 5, 10, 20)

#: Longest horizon; also the excursion window.
MAX_HORIZON = max(HORIZONS)


@dataclass(frozen=True)
class BreakoutOutcome:
    """One confirmed breakout and everything measured after it.

    A horizon whose bars are not all present is ``None``, never ``0.0`` — a
    truncated window is missing evidence, and substituting a number would let a
    short series pull the mean toward zero without being visible.
    """

    symbol: str
    breakout_bar: int
    breakout_date: str
    entry_close: float
    #: Engine slope of the frozen line, for context on how steep the broken line was.
    frozen_slope: float
    #: Bars available after the breakout, capped at :data:`MAX_HORIZON`.
    bars_available: int
    forward_returns: dict[int, Optional[float]]
    #: Max favorable excursion: highest high after entry, as a return. ``None``
    #: when no post-breakout bar exists.
    mfe: Optional[float]
    #: Max adverse excursion: lowest low after entry, as a return.
    mae: Optional[float]
    #: The engine's own verdict on the episode, from its transitions.
    engine_outcome: str
    #: The whole series' final state.
    final_state: str
    #: True when the horizon ran past the end of the delivered series.
    truncated: bool


@dataclass
class SymbolReport:
    symbol: str
    bars: int
    first_date: str
    last_date: str
    breakouts: list[BreakoutOutcome] = field(default_factory=list)
    final_state: str = "NONE"
    reason_codes: tuple[str, ...] = ()
    error: Optional[str] = None
    #: HD-27 §5/§6 — a rejection must be observable, never inferable from
    #: ``final_state == NONE`` plus an absence of breakouts.
    guard_rejected: bool = False
    guard_rejections: list = field(default_factory=list)
    guard_observations: list = field(default_factory=list)
    splits: int = 0


def to_bar_series(symbol_bars: Sequence, ) -> BarSeries:
    """Convert provider bars into the engine's :class:`BarSeries`.

    ``t`` must equal position (§1) and timestamps must be strictly ascending;
    the engine raises if either is violated, which is the behaviour we want —
    a provider that returns duplicate or out-of-order dates is a defect, not a
    market condition.
    """
    return BarSeries(
        [
            EngineBar(
                t=index,
                timestamp=b.date,
                open=b.open,
                high=b.high,
                low=b.low,
                close=b.close,
                volume=float(b.volume),
            )
            for index, b in enumerate(symbol_bars)
        ]
    )


#: The four §21 terminal transitions an episode can reach after its breakout.
#: Anything else leaves the episode open.
TERMINAL_OUTCOMES = ("RETEST_HELD", "FAILED_BREAKOUT", "EXPIRED_POST_BREAKOUT", "RESET_NEW_ATH")


def _episode_outcome(result: DetectionResult, breakout_bar: int) -> str:
    """Name what the engine did to the episode that froze at ``breakout_bar``.

    Read from the transition record rather than inferred, so the label is the
    engine's own and not this module's opinion. The first post-breakout
    transition is the episode's fate; if none exists the episode was still open
    when the series ended.

    **This function was silently vacuous and a whole pilot pass was run on it.**
    It read ``record.reason_code``; ``TransitionRecord``'s field is ``reason``.
    ``getattr(record, "reason_code", None)`` therefore returned ``None`` on every
    record, every iteration hit ``continue``, and all 306 measured breakouts came
    back ``OPEN_AT_SERIES_END`` — a uniform answer that is arithmetically
    impossible across 40 independent symbols, which is the only reason it was
    caught. Attribute access is direct now: a future rename raises
    ``AttributeError`` here instead of quietly turning this into a constant
    function. Defaulted ``getattr`` on a field you require is not defensive, it
    is a silenced error.
    """
    for record in result.transitions:
        if record.bar <= breakout_bar:
            continue
        name = record.reason.name
        if name in TERMINAL_OUTCOMES:
            return name
    return "OPEN_AT_SERIES_END"


def measure_breakout(
    symbol: str,
    bars: Sequence,
    result: DetectionResult,
    frozen,
) -> BreakoutOutcome:
    """Measure forward returns and excursions for one episode's breakout."""
    b = frozen.breakout_bar
    entry = bars[b].close
    last_index = len(bars) - 1
    available = min(MAX_HORIZON, last_index - b)

    forward: dict[int, Optional[float]] = {}
    for h in HORIZONS:
        target = b + h
        forward[h] = (bars[target].close / entry - 1.0) if target <= last_index else None

    window = bars[b + 1 : b + 1 + available] if available > 0 else []
    mfe = (max(x.high for x in window) / entry - 1.0) if window else None
    mae = (min(x.low for x in window) / entry - 1.0) if window else None

    return BreakoutOutcome(
        symbol=symbol,
        breakout_bar=b,
        breakout_date=bars[b].date,
        entry_close=entry,
        frozen_slope=frozen.line.m,
        bars_available=available,
        forward_returns=forward,
        mfe=mfe,
        mae=mae,
        engine_outcome=_episode_outcome(result, b),
        final_state=(result.final_state.name if result.final_state else "NONE"),
        truncated=available < MAX_HORIZON,
    )


def run_symbol(symbol: str, series, params: DetectorParams) -> SymbolReport:
    """Run the engine over one symbol and measure every confirmed breakout."""
    bars = series.bars
    report = SymbolReport(
        symbol=symbol,
        bars=len(bars),
        first_date=bars[0].date if bars else "",
        last_date=bars[-1].date if bars else "",
    )
    # HD-27: supply split-event evidence so the guard can tell a crash from an
    # adjustment defect. Without this the engine falls back to the jump-only
    # rule and rejects any symbol that ever moved >~50% in a day.
    index_of = {b.date: i for i, b in enumerate(bars)}
    actions = CorporateActions(
        symbol=symbol,
        splits={
            index_of[d]: c for d, c in getattr(series, "splits_applied", ()) if d in index_of
        },
    )
    report.splits = len(actions.splits)
    try:
        engine_series = to_bar_series(bars)
        result = detect(engine_series, params, corporate_actions=actions)
    except Exception as exc:  # provider/precondition defects must not kill the run
        report.error = f"{type(exc).__name__}: {exc}"
        return report

    report.guard_rejected = result.guard.rejected
    report.guard_rejections = [r.describe() for r in result.guard.rejections]
    report.guard_observations = [
        {"bar": o.bar, "date": o.date, "log_jump": round(o.log_jump, 6),
         "split_coefficient": o.split_coefficient, "verdict": o.verdict}
        for o in result.guard.observations
    ]

    report.final_state = result.final_state.name if result.final_state else "NONE"
    report.reason_codes = tuple(
        getattr(c, "name", str(c)) for c in result.reason_codes
    )
    # EVERY confirmed breakout, not just the reported one (OQ-P3-5 makes
    # `confirmed_bar` the latest episode's; `episodes` carries them all).
    for frozen in result.episodes:
        report.breakouts.append(measure_breakout(symbol, bars, result, frozen))
    return report


def _stats(values: Iterable[Optional[float]]) -> dict[str, Optional[float]]:
    present = [v for v in values if v is not None]
    if not present:
        return {"n": 0, "mean": None, "median": None, "stdev": None, "min": None, "max": None}
    return {
        "n": len(present),
        "mean": statistics.fmean(present),
        "median": statistics.median(present),
        "stdev": statistics.stdev(present) if len(present) > 1 else None,
        "min": min(present),
        "max": max(present),
    }


def aggregate(reports: Sequence[SymbolReport]) -> dict:
    """Aggregate across every measured breakout.

    ``hit_rate`` is computed **only over breakouts whose horizon is complete**,
    and the excluded count is reported beside it. A truncated window is not a
    miss.
    """
    outcomes = [o for r in reports for o in r.breakouts]
    summary: dict = {
        "symbols_requested": len(reports),
        "symbols_with_data": sum(1 for r in reports if r.error is None and r.bars > 0),
        "symbols_errored": sum(1 for r in reports if r.error is not None),
        "total_breakouts": len(outcomes),
        "breakouts_truncated": sum(1 for o in outcomes if o.truncated),
        "symbols_guard_rejected": sum(1 for r in reports if r.guard_rejected),
        "guard_rejections": [
            {"symbol": r.symbol, "detail": r.guard_rejections} for r in reports if r.guard_rejected
        ],
        "large_jumps_inspected_and_accepted": sum(len(r.guard_observations) for r in reports),
        "engine_outcomes": {},
        "final_states": {},
        "horizons": {},
        "excursions": {},
    }
    for o in outcomes:
        summary["engine_outcomes"][o.engine_outcome] = (
            summary["engine_outcomes"].get(o.engine_outcome, 0) + 1
        )
    for r in reports:
        summary["final_states"][r.final_state] = summary["final_states"].get(r.final_state, 0) + 1

    for h in HORIZONS:
        vals = [o.forward_returns[h] for o in outcomes]
        st = _stats(vals)
        present = [v for v in vals if v is not None]
        st["hit_rate"] = (sum(1 for v in present if v > 0) / len(present)) if present else None
        st["excluded_incomplete"] = sum(1 for v in vals if v is None)
        summary["horizons"][h] = st

    summary["excursions"]["mfe"] = _stats([o.mfe for o in outcomes])
    summary["excursions"]["mae"] = _stats([o.mae for o in outcomes])
    return summary
