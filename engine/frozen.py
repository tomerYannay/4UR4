"""§21.5's frozen event line ``Λ^F`` and the three post-breakout predicates.

Everything here is **pure**: each predicate receives a :class:`FrozenLine`, the
one bar under test, and the parameters.  None of them ever receives the series
or a prefix, so §21.8's "no bar at index >= t may influence bar t" is a property
of the call graph rather than something the tests must police.

**The type is the guard.**  §15, §16 and §17 must be evaluated against ``Λ^F``
and never against a re-selected ``Λ_t`` (§21.5).  The predicates below accept a
:class:`FrozenLine` and nothing else, so an edit that accidentally passed the
rolled hull into a failure test is a type error rather than a wrong number.

Window edges, **ruled by ESC-3 (Product Steward, 2026-07-28)** — left edge open,
right edges closed::

    §15 failure       breakout_bar <  t  <=  breakout_bar + F_fail
    §16 return leg    breakout_bar <  r  <=  breakout_bar + W_retest
    §16 hold leg      r            <=  u  <=  r + h_hold
    §17 expiry        t - breakout_bar    >=  E_expiry

``W_retest`` bounds the **return leg only**: a hold window opened at a legal
return bar may complete after the return window closes.  No fixture exercises
any right edge (the largest event gap in the corpus is 4 bars against windows of
10 and 20), so the edges are owed **constructed unit tests**, which is where they
are asserted.

Strictness is taken verbatim from the specification's own inequality glyphs:
§15 writes ``<``, §16's return leg writes ``<=``, §16's hold leg writes ``>=``.
Each has exactly one spelling, in :mod:`engine.logspace`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .line import Line
from .logspace import at_or_above, at_or_below, falls_below, ln_price, log_slope
from .params import DetectorParams
from .state import PreconditionError

__all__ = [
    "FrozenLine",
    "Challenger",
    "HoldWindow",
    "FailureDetail",
    "ReturnDetail",
    "HoldDetail",
    "in_failure_window",
    "in_return_window",
    "failed_breakout_at",
    "retest_return_at",
    "retest_hold_at",
    "expired_at",
    "challengers_over",
]


@dataclass(frozen=True)
class FrozenLine:
    """``Λ^F`` — §21.5's frozen-field table, one field per row and nothing more.

    §21.5's table has six rows: ``A``, ``B*``, ``m``, ``b``, ``tolerance_version``
    and ``breakout_bar == confirmed_bar``.  :class:`~engine.line.Line` already
    carries the first four exactly, so this type adds the two it lacks.

    ``frozen=True``, so "retained verbatim" is a type-level fact rather than a
    convention: the line a breakout froze cannot be mutated by a later bar.
    """

    line: Line
    tolerance_version: str
    breakout_bar: int

    @property
    def confirmed_bar(self) -> int:
        """HD-03: the alert fires on the first qualifying close, so the breakout
        bar and the confirmed bar are the same bar named twice."""
        return self.breakout_bar

    def y_hat_at(self, u: int) -> float:
        return self.line.y_hat_at(u)

    def price_at(self, u: int) -> float:
        return self.line.price_at(u)


@dataclass(frozen=True)
class Challenger:
    """A post-breakout high that *would* have re-bound ``B*`` under a full-series
    hull, and which §21.5 forbids from doing so.

    This is the **positive** evidence that re-selection was suspended: the engine
    both names the highs that would have moved the line and demonstrably did not
    use them.  It is reporting only — nothing in the fold reads it.
    """

    bar: int
    high: float
    slope_if_selected: float


@dataclass(frozen=True)
class HoldWindow:
    """One open §16 hold window ``[r, r + h_hold]``, opened by a qualifying
    return bar ``r``.

    **OQ-P3-3 (ruled):** *every* qualifying bar inside the return window opens
    its own window; windows may overlap; a window that lapses without a
    qualifying close emits nothing at all.
    """

    return_bar: int
    last_bar: int
    low: float
    ln_low: float
    return_margin: float

    def contains(self, u: int) -> bool:
        return self.return_bar <= u <= self.last_bar

    def lapsed(self, u: int) -> bool:
        return u > self.last_bar


@dataclass(frozen=True)
class FailureDetail:
    y_hat_frozen: float
    line_value: float
    close: float
    ln_close: float
    #: ``(y_hat_F(t) - eps_fail) - ln C[t]`` — the pinned algebraic form.
    margin: float


@dataclass(frozen=True)
class ReturnDetail:
    low: float
    ln_low: float
    #: ``(y_hat_F(r) + eps_retest) - ln L[r]``.
    return_margin: float


@dataclass(frozen=True)
class HoldDetail:
    y_hat_frozen: float
    line_value: float
    close: float
    ln_close: float
    #: ``ln C[u] - (y_hat_F(u) - eps_retest)``.
    hold_margin: float


def in_failure_window(frozen: FrozenLine, t: int, params: DetectorParams) -> bool:
    """``breakout_bar < t <= breakout_bar + F_fail`` (§15, ESC-3)."""
    return frozen.breakout_bar < t <= frozen.breakout_bar + params.F_fail


def in_return_window(frozen: FrozenLine, t: int, params: DetectorParams) -> bool:
    """``breakout_bar < r <= breakout_bar + W_retest`` (§16 return leg, ESC-3)."""
    return frozen.breakout_bar < t <= frozen.breakout_bar + params.W_retest


def failed_breakout_at(
    frozen: FrozenLine, close: float, t: int, params: DetectorParams
) -> Optional[FailureDetail]:
    """§15 — ``ln C[t] < y_hat_F(t) - eps_fail`` inside the failure window."""
    if not in_failure_window(frozen, t, params):
        return None
    y_hat_value = frozen.y_hat_at(t)
    ln_close = ln_price(close)
    if not falls_below(ln_close, y_hat_value, params.eps_fail):
        return None
    return FailureDetail(
        y_hat_frozen=y_hat_value,
        line_value=frozen.price_at(t),
        close=close,
        ln_close=ln_close,
        margin=(y_hat_value - params.eps_fail) - ln_close,
    )


def retest_return_at(
    frozen: FrozenLine, low: Optional[float], t: int, params: DetectorParams
) -> Optional[ReturnDetail]:
    """§16 return leg — ``ln L[r] <= y_hat_F(r) + eps_retest`` inside the window.

    **ESC-5(a) (ruled):** a bar whose ``low`` is absent must not reach this
    predicate.  If it does, that is a **caller defect** — the same class as a
    non-positive basis or an out-of-order series — and it raises rather than
    minting a reason code, because the schema's reason-code set is closed and
    adding a member is a product-definition change, not an implementer's.
    """
    if not in_return_window(frozen, t, params):
        return None
    if low is None:
        raise PreconditionError(
            "bar %d reached the §16 return predicate with no `low` (§1 lists it "
            "among the required input fields; ESC-5(a) makes this a caller "
            "defect, not a reason code)" % t
        )
    y_hat_value = frozen.y_hat_at(t)
    ln_low = ln_price(low)
    if not at_or_below(ln_low, y_hat_value, params.eps_retest):
        return None
    return ReturnDetail(
        low=low,
        ln_low=ln_low,
        return_margin=(y_hat_value + params.eps_retest) - ln_low,
    )


def retest_hold_at(
    frozen: FrozenLine, close: float, u: int, params: DetectorParams
) -> Optional[HoldDetail]:
    """§16 hold leg — ``ln C[u] >= y_hat_F(u) - eps_retest``.

    **OQ-P3-1 (ruled):** ``y_hat_F`` is evaluated at the index of the bar under
    test — the hold bar ``u``, never the return bar ``r``.  Reading it at ``r``
    would judge bar ``u`` by another bar's geometry, which is the one thing §21
    exists to forbid.  The caller supplies the window membership test.
    """
    y_hat_value = frozen.y_hat_at(u)
    ln_close = ln_price(close)
    if not at_or_above(ln_close, y_hat_value, params.eps_retest):
        return None
    return HoldDetail(
        y_hat_frozen=y_hat_value,
        line_value=frozen.price_at(u),
        close=close,
        ln_close=ln_close,
        hold_margin=ln_close - (y_hat_value - params.eps_retest),
    )


def expired_at(frozen: FrozenLine, t: int, params: DetectorParams) -> Optional[int]:
    """§17 — ``t - breakout_bar >= E_expiry``; returns the elapsed bar count.

    Written as ``>=`` on the elapsed count because §17 writes it that way, and
    GX-07 pins it at exactly ``E_expiry``.
    """
    elapsed = t - frozen.breakout_bar
    if elapsed >= params.E_expiry:
        return elapsed
    return None


def open_hold_windows(windows: List[HoldWindow], u: int) -> List[HoldWindow]:
    """Drop the windows that lapsed before bar ``u``.  A lapsed window emits
    nothing at all (OQ-P3-3)."""
    return [window for window in windows if not window.lapsed(u)]


def earliest_open_window(windows: List[HoldWindow], u: int) -> Optional[HoldWindow]:
    """The earliest still-open window containing ``u``.

    OQ-P3-3 fixes the *bar* at which the hold fires — the earliest bar satisfying
    **any** open window, which is ``u`` itself because every bar is tested in
    order.  Which window is credited in the event record is a record detail, not
    a behaviour: the transition bar, the state and the hold margin are identical
    whichever is chosen.  The earliest return leg is credited, because it is the
    leg the market opened first.  Unexercised by the corpus, where every recorded
    retest has exactly one window and ``r == u``.
    """
    candidates = [window for window in windows if window.contains(u)]
    if not candidates:
        return None
    return min(candidates, key=lambda window: window.return_bar)


def challengers_over(
    frozen: FrozenLine, highs: Tuple[float, ...], log_highs: Tuple[float, ...]
) -> Tuple[Challenger, ...]:
    """Every bar ``u >= breakout_bar`` whose ``slope(A^F, (u, H[u]))`` exceeds
    ``m^F`` — the highs a full-series hull would have re-selected.

    Reporting only; nothing in the fold reads the result.  It is computed after
    the fold from the log-highs the fold accumulated, so it cannot influence a
    classification even by accident.
    """
    line = frozen.line
    out: List[Challenger] = []
    for u in range(frozen.breakout_bar, len(highs)):
        if u == line.t_anchor:
            continue
        slope = log_slope(log_highs[u], line.y_anchor, u, line.t_anchor)
        if slope > line.m:
            out.append(Challenger(bar=u, high=highs[u], slope_if_selected=slope))
    return tuple(out)
