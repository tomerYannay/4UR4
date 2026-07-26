"""§21.3 — formation eligibility, with F1, F2 and F3 evaluated **independently**.

::

    FORMATION_ELIGIBLE(t)  iff  all of:
      (F1)  |S_t| >= min_formation_bars        # INSUFFICIENT_BARS
      (F2)  tA <= (t - 1) - min_ath_age_bars   # ATH_TOO_RECENT
      (F3)  B*_t exists                        # NO_VALID_SECOND_ANCHOR

All three gates are computed on every bar even when an earlier one already
failed, so an implementation *and* an auditor can always say which one binds;
the reason reported is the **first** unmet gate in the order F1, F2, F3.

``min_formation_bars`` (8) and ``min_ath_age_bars`` (3) are first-class,
versioned parameters **independent of the pivot window ``k``** (D-TL-12,
HD-14).  This module does not read ``k``, does not import ``engine.pivots``, and
never could: ``k`` is not a member of :class:`~engine.params.DetectorParams`.

The verdict is a pure function of the prefix, which is what makes the Phase-2
state a pure function of ``S_t``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .anchor import Anchor, anchor_of
from .bars import Prefix
from .envelope import Selection, select_second_anchor
from .params import DetectorParams
from .state import ReasonCode

__all__ = ["GateVerdict", "evaluate_formation"]


@dataclass(frozen=True)
class GateVerdict:
    """The per-bar formation trace entry (``causal_record.formation.gate_trace``)."""

    t: int
    prefix_length: int
    anchor: Optional[Anchor]
    selection: Optional[Selection]
    f1: bool
    f2: bool
    f3: bool
    eligible: bool
    #: The FIRST unmet gate's code, or ``None`` when eligible.
    reason: Optional[ReasonCode]

    @property
    def t_anchor(self) -> Optional[int]:
        return None if self.anchor is None else self.anchor.t

    def structural(self):
        """The comparison tuple used against a fixture's gate trace.

        Deliberately structural, never textual: requiring string equality on a
        trace would make "match another implementation's log formatting" part of
        the correctness contract.
        """
        return (
            self.t,
            self.prefix_length,
            self.t_anchor,
            self.f1,
            self.f2,
            self.f3,
            self.eligible,
            None if self.reason is None else self.reason.value,
        )


def evaluate_formation(prefix: Prefix, params: DetectorParams) -> GateVerdict:
    """Evaluate F1/F2/F3 at evaluation bar ``t = len(prefix)`` over ``S_t``."""
    t = prefix.length

    f1 = prefix.length >= params.min_formation_bars

    anchor = anchor_of(prefix)
    if anchor is None:
        f2 = False
        selection: Optional[Selection] = None
        f3 = False
    else:
        f2 = anchor.t <= (t - 1) - params.min_ath_age_bars
        selection = select_second_anchor(prefix, anchor.t, params.eps)
        f3 = selection.exists

    eligible = f1 and f2 and f3
    if eligible:
        reason: Optional[ReasonCode] = None
    elif not f1:
        reason = ReasonCode.INSUFFICIENT_BARS
    elif not f2:
        reason = ReasonCode.ATH_TOO_RECENT
    else:
        reason = ReasonCode.NO_VALID_SECOND_ANCHOR

    return GateVerdict(
        t=t,
        prefix_length=prefix.length,
        anchor=anchor,
        selection=selection,
        f1=f1,
        f2=f2,
        f3=f3,
        eligible=eligible,
        reason=reason,
    )
