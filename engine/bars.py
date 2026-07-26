"""Immutable bars, the bar series, and the causal :class:`Prefix`.

The :class:`Prefix` is the structural guarantee against look-ahead.  It is a
*genuine slice*, not a view with a length field: a geometry function that holds
a ``Prefix`` has no reference through which a future bar is reachable, so
§21's "no bar at index >= t may influence the line that judges bar t" is a
property of the call graph rather than something the tests must police.

Spec refs: §1 (ordering, ordinal indexing, required fields), §21.1 (``S_t``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence, Tuple

from .state import PreconditionError

__all__ = ["Bar", "BarSeries", "Prefix", "Provenance"]


@dataclass(frozen=True)
class Bar:
    """One OHLCV bar.  ``t`` is the ordinal position in the delivered series
    (§1) — never a calendar-day count.

    Every price is ``Optional`` because §18 must be able to *see* a missing
    ``high`` or ``close`` in order to reject the bar-set for it.  Geometry never
    reads a bar until the guards have passed.
    """

    t: int
    timestamp: Any
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    volume: Optional[float]

    def prices(self) -> Tuple[Tuple[str, Optional[float]], ...]:
        return (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
        )


@dataclass(frozen=True)
class Provenance:
    """What ``data/`` declares about the series (DI-01, DI-04, DI-05, DI-06).

    The engine *records* every field and *reads* none of them in logic.  In
    particular ``as_of`` is carried so a signal is replayable, and never
    consulted: there is no clock in ``engine/``.
    """

    adjustment_basis: Optional[str] = None
    wick_semantics: Optional[str] = None
    upstream_source: Optional[str] = None
    as_of: Optional[str] = None
    provider: Optional[str] = None
    snapshot_id: Optional[str] = None

    #: HD-01 / DI-01: the only basis this detector's geometry is defined over.
    ACCEPTED_BASIS = "SPLIT_ADJUSTED_DIVIDEND_UNADJUSTED"


class BarSeries:
    """An ordered, de-duplicated, immutable bar series (§1).

    Ordering violations raise :class:`PreconditionError` rather than emitting a
    reason code: §1 states ordering as an *assumption*, and the reason-code set
    is closed by schema.  (Plan §9.2 OQ-E — escalated, not decided here.)
    """

    __slots__ = ("_bars",)

    def __init__(self, bars: Sequence[Bar]) -> None:
        tup = tuple(bars)
        for index, bar in enumerate(tup):
            if bar.t != index:
                raise PreconditionError(
                    "bar %d carries ordinal t=%r; t must equal position (§1)" % (index, bar.t)
                )
        for previous, current in zip(tup, tup[1:]):
            if previous.timestamp is not None and current.timestamp is not None:
                if not previous.timestamp < current.timestamp:
                    raise PreconditionError(
                        "timestamps must be strictly ascending and de-duplicated (§1): "
                        "%r then %r" % (previous.timestamp, current.timestamp)
                    )
        self._bars = tup

    def __len__(self) -> int:
        return len(self._bars)

    def __getitem__(self, index: int) -> Bar:
        return self._bars[index]

    def __iter__(self):
        return iter(self._bars)

    @property
    def bars(self) -> Tuple[Bar, ...]:
        return self._bars


class Prefix:
    """``S_t`` — the bars strictly before evaluation bar ``t`` (§21.1).

    Holds only cached log-highs and highs, both of exactly ``length`` entries.
    ``length`` is redundant with ``len(...)`` on purpose: the constructor
    asserts them equal, so an off-by-one that leaks bar ``t`` into ``Λ_t`` is an
    assertion failure rather than a subtly wrong number.
    """

    __slots__ = ("y", "high", "length")

    def __init__(self, y: Tuple[float, ...], high: Tuple[float, ...], length: int) -> None:
        if len(y) != length or len(high) != length:
            raise AssertionError(
                "Prefix length %d does not match its data (%d log-highs, %d highs) — "
                "a future bar may have leaked into S_t (§21.1)" % (length, len(y), len(high))
            )
        self.y = y
        self.high = high
        self.length = length

    @classmethod
    def empty(cls) -> "Prefix":
        return cls((), (), 0)

    def extended(self, y_value: float, high_value: float) -> "Prefix":
        """``S_{t+1} = S_t ∪ {bar[t]}`` — §21.2 step 4."""
        return Prefix(self.y + (y_value,), self.high + (high_value,), self.length + 1)

    def indices(self):
        return range(self.length)

    def __len__(self) -> int:
        return self.length

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return "Prefix(length=%d)" % self.length
