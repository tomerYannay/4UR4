"""4UR4 — deterministic pre-breakout trendline engine (Phase 2).

Scope, stated so it cannot drift: this package implements §4 (ATH anchoring),
§6/§8 (all-highs candidacy and upper-log-hull selection), §3/§7 (log-space
geometry), §21.3 (formation eligibility), §21.6 (rolling as-of-time
re-selection), §10.1 (the structural-pierce edge), §14 (wick-break) and §18 (the
input guards) of ``product/trendline-specification.md``, under §21's as-of-time
semantics (HD-12 / D-TL-11).

It does **not** implement — and does not stub — confirmed breakout, retest,
failed breakout, expiry or the freezing of ``Λ^F``.  Those are Phase 3.  The
§13.1 breakout *predicate* exists here only because §14 and §21.2 step 4 are not
definable without it; when it holds the episode **halts** and the line active at
the start of that bar is returned as ``line_at_stop``.
"""

from __future__ import annotations

from .bars import Bar, BarSeries, Prefix, Provenance
from .detector import DetectionResult, detect, prefix_of, second_anchor_over
from .params import DetectorParams, PivotParams
from .state import LineState, PreconditionError, ReasonCode, TransitionRecord

__all__ = [
    "Bar",
    "BarSeries",
    "Prefix",
    "Provenance",
    "DetectionResult",
    "detect",
    "prefix_of",
    "second_anchor_over",
    "DetectorParams",
    "PivotParams",
    "LineState",
    "ReasonCode",
    "TransitionRecord",
    "PreconditionError",
]
