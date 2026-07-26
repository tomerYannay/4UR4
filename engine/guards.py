"""§18 input guards — a whole-bar-set pre-pass.

Three conditions, and only these three (adding a fourth is a product-definition
change, plan §9.2 OQ-F, escalated rather than taken):

============================== ============================== ========
condition                       code                           fixture
============================== ============================== ========
a bar missing ``high``/``close`` ``INVALID_INPUT``              GX-18
any non-positive price          ``INVALID_PRICE``              GX-18
``|y[t]-y[t-1]| > ln(1.5)``     ``SUSPECTED_UNADJUSTED_SPLIT`` GX-10
============================== ============================== ========

All three **reject the bar-set**, before any geometry is fitted, so no
as-of-time line exists at any prefix.  This is the engine's one deliberately
non-causal element: it is confined to this pre-pass, it can only ever produce a
whole-series rejection, and the prefix-truncation property test carries an
explicit positive control for it rather than exempting it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .bars import BarSeries
from .logspace import ln_price
from .params import DetectorParams
from .state import LineState, ReasonCode, TransitionRecord

__all__ = ["GuardVerdict", "run_guards"]


@dataclass(frozen=True)
class GuardVerdict:
    rejected: bool
    records: Tuple[TransitionRecord, ...]
    codes: Tuple[ReasonCode, ...]
    detail: Optional[Dict[str, Any]]

    @staticmethod
    def clean() -> "GuardVerdict":
        return GuardVerdict(False, (), (), None)


def _is_missing(value: Optional[float]) -> bool:
    return value is None


def run_guards(series: BarSeries, params: DetectorParams) -> GuardVerdict:
    """Evaluate §18's three whole-bar-set guards over the delivered series.

    Records are emitted in bar order; within a bar, ``INVALID_INPUT`` precedes
    ``INVALID_PRICE`` because a missing field cannot then be tested for
    positivity.  A bar whose ``high`` is missing or non-positive is excluded from
    the split-jump scan for the same reason.
    """
    records: List[TransitionRecord] = []
    codes: List[ReasonCode] = []
    detail: Optional[Dict[str, Any]] = None

    def emit(bar_index: int, code: ReasonCode) -> None:
        records.append(TransitionRecord(bar_index, LineState.NONE, LineState.NONE, code))
        if code not in codes:
            codes.append(code)

    usable_high: Dict[int, float] = {}

    for bar in series:
        if _is_missing(bar.high) or _is_missing(bar.close):
            # §18 row "a bar missing high or close is invalid input".
            emit(bar.t, ReasonCode.INVALID_INPUT)
            continue
        non_positive = [
            name for name, value in bar.prices() if value is not None and value <= 0
        ]
        if non_positive:
            # §1 positivity / §18 row "Non-positive price -> reject bar-set".
            emit(bar.t, ReasonCode.INVALID_PRICE)
            continue
        usable_high[bar.t] = float(bar.high)

    # §18 split guard, on the HIGH series (the field that feeds y, §3).
    previous_index: Optional[int] = None
    for bar in series:
        if bar.t not in usable_high:
            previous_index = None
            continue
        if previous_index is not None and previous_index == bar.t - 1:
            jump = abs(
                ln_price(usable_high[bar.t]) - ln_price(usable_high[previous_index])
            )
            if jump > params.split_log_jump_threshold:
                emit(bar.t, ReasonCode.SUSPECTED_UNADJUSTED_SPLIT)
                if detail is None:
                    detail = {"bar": bar.t, "log_jump": jump}
        previous_index = bar.t

    records.sort(key=lambda record: (record.bar, _CODE_ORDER[record.reason]))
    # Reduce `codes` from the sorted records so the list is genuinely in
    # first-emission order rather than in pass order.
    codes = []
    for record in records:
        if record.reason not in codes:
            codes.append(record.reason)
    return GuardVerdict(bool(records), tuple(records), tuple(codes), detail)


_CODE_ORDER = {
    ReasonCode.INVALID_INPUT: 0,
    ReasonCode.INVALID_PRICE: 1,
    ReasonCode.SUSPECTED_UNADJUSTED_SPLIT: 2,
}
