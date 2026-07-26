"""The public API: ``detect(series, params, provenance) -> DetectionResult``.

Purity, stated as a contract and enforced by architectural test A-2: no network,
no filesystem, no clock, no randomness, no credentials.  ``as_of`` is *recorded*
in provenance and never read in logic — there is no clock in ``engine/``, so
there is nothing for a signal to depend on except its bars.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from .bars import BarSeries, Prefix, Provenance
from .causal import CausalResult, Line, run
from .envelope import Selection, select_second_anchor
from .guards import GuardVerdict, run_guards
from .logspace import ln_price
from .params import DetectorParams
from .state import LineState, PreconditionError, ReasonCode, TransitionRecord
from .trace import line_values

__all__ = ["DetectionResult", "detect", "second_anchor_over", "prefix_of"]


@dataclass
class DetectionResult:
    spec_version: str
    tolerance_version: str
    params: DetectorParams
    provenance: Optional[Provenance]
    guard: GuardVerdict
    causal: Optional[CausalResult]
    transitions: Tuple[TransitionRecord, ...]
    reason_codes: Tuple[ReasonCode, ...]
    final_state: Optional[LineState]
    ath_anchor: Optional[Tuple[int, float]]
    reported_line: Optional[Line]
    #: Phase 2's equivalent of ``confirmed_bar``: the bar at which §13.1's
    #: predicate first held.  ``None`` when it never did.
    stop_bar: Optional[int]
    diagnostics: Dict[str, object] = field(default_factory=dict)

    @property
    def rejected(self) -> bool:
        return self.guard.rejected

    @property
    def line_at_stop(self) -> Optional[Line]:
        if self.causal is None or self.causal.stop is None:
            return None
        return self.causal.stop.line

    def line_values_at(self, indices: Iterable[int]) -> Dict[int, Tuple[float, float]]:
        return line_values(self.reported_line, indices)

    def transitions_before(self, bar: Optional[int]) -> Tuple[TransitionRecord, ...]:
        if bar is None:
            return self.transitions
        return tuple(record for record in self.transitions if record.bar < bar)


def detect(
    series: BarSeries,
    params: DetectorParams,
    provenance: Optional[Provenance] = None,
) -> DetectionResult:
    """Run the §18 guards, then §21.2's causal fold.

    A ``provenance`` whose ``adjustment_basis`` is declared and is not the
    accepted basis raises rather than emitting a reason code: HD-01 makes the
    basis a *precondition*, the reason-code set is closed by schema, and a wrong
    basis is a caller defect, not a market condition.
    """
    if provenance is not None and provenance.adjustment_basis is not None:
        if provenance.adjustment_basis != Provenance.ACCEPTED_BASIS:
            raise PreconditionError(
                "adjustment basis %r is not %r (HD-01): geometry anchored on a "
                "dividend-adjusted or unadjusted series is not the product's object"
                % (provenance.adjustment_basis, Provenance.ACCEPTED_BASIS)
            )

    guard = run_guards(series, params)
    if guard.rejected:
        return DetectionResult(
            spec_version=params.spec_version,
            tolerance_version=params.tolerance_version,
            params=params,
            provenance=provenance,
            guard=guard,
            causal=None,
            transitions=guard.records,
            reason_codes=guard.codes,
            final_state=LineState.NONE,
            ath_anchor=None,
            reported_line=None,
            stop_bar=None,
            diagnostics={"guard_detail": guard.detail},
        )

    causal = run(series, params)

    diagnostics: Dict[str, object] = {}
    if causal.reported_line is not None and causal.reported_line.t_anchor == 0:
        # DI-07: an ATH at t=0 is legitimate (GX-09) but is also the signature of
        # a silently truncated history.  Non-gating.
        diagnostics["anchor_at_first_bar"] = True
    if provenance is not None and provenance.wick_semantics in (None, "UNKNOWN"):
        diagnostics["wick_semantics_unknown"] = True

    return DetectionResult(
        spec_version=params.spec_version,
        tolerance_version=params.tolerance_version,
        params=params,
        provenance=provenance,
        guard=guard,
        causal=causal,
        transitions=causal.transitions,
        reason_codes=causal.reason_codes,
        final_state=causal.final_state,
        ath_anchor=causal.reported_anchor,
        reported_line=causal.reported_line,
        stop_bar=None if causal.stop is None else causal.stop.bar,
        diagnostics=diagnostics,
    )


def prefix_of(series: BarSeries, length: Optional[int] = None) -> Prefix:
    """Build ``S_length`` from a guard-passing series.

    Exported because the RM-01 A-clause is asserted at **unit level** on the pure
    §8 selector over the full 29-bar prefix — a quantity a §21-conforming
    detector never produces in normal operation, because the stop freezes the
    line long before bar 25.
    """
    n = len(series) if length is None else length
    highs: List[float] = []
    logs: List[float] = []
    for index in range(n):
        bar = series[index]
        if bar.high is None or bar.high <= 0:
            raise PreconditionError("bar %d has no usable high (§18)" % index)
        highs.append(float(bar.high))
        logs.append(ln_price(float(bar.high)))
    return Prefix(tuple(logs), tuple(highs), n)


def second_anchor_over(prefix: Prefix, t_anchor: int, eps: float) -> Selection:
    """The exported, pure §8 canonical-second-anchor selector."""
    return select_second_anchor(prefix, t_anchor, eps)
