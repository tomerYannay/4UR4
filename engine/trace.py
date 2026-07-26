"""The structured evidence record.

Everything here is **structural**, never prose.  The engine must reproduce the
*values* a fixture's ``causal_record`` carries; it must not reproduce another
implementation's *formatting*.  Requiring string equality on a gate trace would
quietly make "author an engine whose log strings match the reference model" part
of the correctness contract — the precise circularity the independence
requirement exists to prevent, and a way for an engine fitted to the fixtures to
look more conformant than it is.  The harness parses the fixture's strings into
these structures instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .causal import CausalResult, Line
from .envelope import Selection
from .logspace import ln_price
from .state import LineState

__all__ = [
    "CandidateEvidence",
    "CandidateSetEvidence",
    "ActiveLineEvidence",
    "candidate_set_at",
    "active_line_at",
    "line_values",
]


@dataclass(frozen=True)
class CandidateEvidence:
    t: int
    high: float
    slope: float
    worst_gap: float
    envelope_valid: bool


@dataclass(frozen=True)
class CandidateSetEvidence:
    at_bar: int
    prefix_length: int
    anchor_t: int
    anchor_high: float
    candidates: Tuple[CandidateEvidence, ...]
    selected_t: Optional[int]
    selected_high: Optional[float]
    selected_slope: Optional[float]


@dataclass(frozen=True)
class ActiveLineEvidence:
    """The line in force at the start of a bar, and that bar's two margins."""

    bar: int
    state_at_start: LineState
    line: Optional[Line]
    y_hat_at_bar: Optional[float]
    line_at_bar: Optional[float]
    close_vs_line_plus_eps_break: Optional[float]
    high_vs_line_plus_eps: Optional[float]


def candidate_set_at(result: CausalResult, bar: int) -> Optional[CandidateSetEvidence]:
    """The as-of-time §8 candidate set evaluated over ``S_bar``."""
    sealed = result.sealed_at(bar)
    if sealed is None or sealed.verdict.anchor is None:
        return None
    selection: Optional[Selection] = sealed.verdict.selection
    if selection is None:
        return None
    anchor = sealed.verdict.anchor
    chosen = selection.selected
    return CandidateSetEvidence(
        at_bar=bar,
        prefix_length=sealed.verdict.prefix_length,
        anchor_t=anchor.t,
        anchor_high=anchor.high,
        candidates=tuple(
            CandidateEvidence(
                t=candidate.t,
                high=candidate.high,
                slope=candidate.slope,
                worst_gap=candidate.worst_gap,
                envelope_valid=candidate.envelope_valid,
            )
            for candidate in selection.candidates
        ),
        selected_t=None if chosen is None else chosen.t,
        selected_high=None if chosen is None else chosen.high,
        selected_slope=None if chosen is None else chosen.slope,
    )


def active_line_at(
    result: CausalResult,
    bar: int,
    high: Optional[float],
    close: Optional[float],
    eps: float,
    eps_break: float,
) -> ActiveLineEvidence:
    """Evidence for one bar.

    For a bar the engine evaluated, the line is ``Λ_bar``.  For a bar at or after
    the stop the engine performs no evaluation, so the line reported is the
    reported line and the two margins are **pure arithmetic on it** — which is
    what ``expected_line_values`` at post-stop indices already requires, and
    performs no state transition.
    """
    sealed = result.sealed_at(bar)
    evaluated = sealed is not None and (result.stop is None or bar <= result.stop.bar)
    if evaluated:
        state = sealed.state
        line = sealed.line
    else:
        # Beyond the engine's reach: report the reported line and pure
        # arithmetic on it.  The state is deliberately not claimed.
        state = LineState.NONE if result.reported_line is None else LineState.ACTIVE
        line = result.reported_line

    if line is None:
        return ActiveLineEvidence(bar, state, None, None, None, None, None)

    y_hat_value = line.y_hat_at(bar)
    return ActiveLineEvidence(
        bar=bar,
        state_at_start=state,
        line=line,
        y_hat_at_bar=y_hat_value,
        line_at_bar=line.price_at(bar),
        close_vs_line_plus_eps_break=(
            None if close is None else ln_price(close) - (y_hat_value + eps_break)
        ),
        high_vs_line_plus_eps=(
            None if high is None else ln_price(high) - (y_hat_value + eps)
        ),
    )


def line_values(line: Optional[Line], indices) -> Dict[int, Tuple[float, float]]:
    """``{u: (y_hat(u), line(u))}`` — pure arithmetic on the reported line,
    evaluable at any index including ones after the stop."""
    if line is None:
        return {}
    return {int(u): (line.y_hat_at(int(u)), line.price_at(int(u))) for u in indices}
