"""§8 — the upper-log-hull envelope rule: selecting **the** canonical line.

The normative definition is the §8 brute force over the available prefix, and
that is what this module implements as the production path.  §21.4's
running-maximum lemma is an *optimization, not the definition*; it lives in the
test suite as an independently written oracle and is asserted equal to this
brute force at every evaluable prefix of every fixture.

The two sets below are **different sets**, and conflating them is the single
easiest way to get §8 wrong:

* **candidacy** — bar highs with ``i > tA`` **and** ``H[i] < HA`` (strict, §6
  rule 2);
* **domination** — **every** bar high ``j`` in the prefix with ``j > tA``
  (D-TL-05: all bar highs, never a pivot subset, never only the candidates).

A later high that *ties* the ATH is therefore excluded from candidacy while
remaining in the domination set, where it pierces every descending candidate —
which is exactly ``NO_VALID_SECOND_ANCHOR`` (GX-20 permanently, GX-12
transiently).

Pivot status is never consulted here (HD-11); this module does not import
``engine.pivots`` and architectural test A-1 asserts that it cannot.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .bars import Prefix
from .logspace import log_intercept, log_slope, y_hat

__all__ = ["Candidate", "Selection", "select_second_anchor", "envelope_violations"]


@dataclass(frozen=True)
class Candidate:
    t: int
    high: float
    y: float
    slope: float
    intercept: float
    #: ``max`` over the domination set of ``y[j] - y_hat_i(j)``.  Exactly ``0``
    #: at ``j == i`` and therefore never negative.
    worst_gap: float
    envelope_valid: bool


@dataclass(frozen=True)
class Selection:
    candidates: Tuple[Candidate, ...]
    selected: Optional[Candidate]
    #: True when two or more envelope-valid candidates share the exact maximum
    #: slope and ``ENVELOPE_TIE_LATER`` (§18) decided the outcome.
    tie: bool
    tied_bars: Tuple[int, ...]

    @property
    def exists(self) -> bool:
        return self.selected is not None


def select_second_anchor(prefix: Prefix, t_anchor: int, eps: float) -> Selection:
    """``B*_t`` — the §8 all-highs upper-log-hull vertex over ``prefix``.

    1. candidates: every ``i`` in the prefix with ``i > tA`` and ``H[i] < HA``;
    2. ``slope(i) = (y[i] - y[tA]) / (i - tA)``;
    3. ``envelope_valid(i)`` iff for every bar high ``j > tA`` in the prefix,
       ``y[j] <= y_hat_i(j) + eps``;
    4. ``B*`` is the maximum-slope valid candidate, **later ``i`` wins exact
       ties** (``ENVELOPE_TIE_LATER``);
    5. ``B* = None`` when no candidate is envelope-valid (§10.4).
    """
    y_anchor = prefix.y[t_anchor]
    high_anchor = prefix.high[t_anchor]

    domination = tuple(range(t_anchor + 1, prefix.length))

    candidates: List[Candidate] = []
    for i in domination:
        if not prefix.high[i] < high_anchor:  # §6 rule 2 — STRICT.
            continue
        slope = log_slope(prefix.y[i], y_anchor, i, t_anchor)
        intercept = log_intercept(y_anchor, slope, t_anchor)
        worst_gap = _worst_gap(prefix, domination, slope, intercept)
        candidates.append(
            Candidate(
                t=i,
                high=prefix.high[i],
                y=prefix.y[i],
                slope=slope,
                intercept=intercept,
                worst_gap=worst_gap,
                envelope_valid=_is_envelope_valid(prefix, t_anchor, slope, intercept, eps),
            )
        )

    selected: Optional[Candidate] = None
    tied_bars: List[int] = []
    for candidate in candidates:  # ascending in t, so `>=` implements "later wins"
        if not candidate.envelope_valid:
            continue
        if selected is None or candidate.slope > selected.slope:
            selected = candidate
            tied_bars = [candidate.t]
        elif candidate.slope == selected.slope:  # EXACT equality; no near-tie.
            selected = candidate
            tied_bars.append(candidate.t)

    return Selection(
        candidates=tuple(candidates),
        selected=selected,
        tie=len(tied_bars) > 1,
        tied_bars=tuple(tied_bars),
    )


def _worst_gap(
    prefix: Prefix, domination: Tuple[int, ...], slope: float, intercept: float
) -> float:
    worst = float("-inf")
    for j in domination:
        gap = prefix.y[j] - y_hat(slope, intercept, j)
        if gap > worst:
            worst = gap
    return worst


def _is_envelope_valid(prefix, t_anchor: int, slope: float, intercept: float, eps: float) -> bool:
    """Envelope validity in the PINNED comparison form: ``lhs > y_hat + eps``.

    Plan §4.3 pins the right-hand side to be formed FIRST -- ``lhs > y_hat + eps`` --
    and explicitly forbids ``lhs - y_hat > eps``.  This predicate previously used
    ``worst_gap <= eps``, which is the forbidden form, twelve lines above
    :func:`envelope_violations` using the pinned one.  Two forms of ONE predicate in one
    module is exactly the hazard the pin exists to prevent: at a boundary they can
    disagree by an ulp, which would yield ``envelope_valid=True`` alongside
    ``envelope_violations() > 0`` for the same candidate -- an internal contradiction
    RM-01's Half-A assertion depends on being impossible.

    Both gates measured the two forms against each other and neither found a
    disagreement: Code Review 0 over **13,043** candidate evaluations, and
    Verification -- which patched this predicate to compute both forms and ran the
    whole suite -- 0 over **436,691**, a superset.  So nothing moves today.  It is
    unified anyway, because "measured
    identical on this corpus" is precisely the argument that mutations M-1 and M-2
    defeated: a 6-significant-figure corpus cannot pin arithmetic form.

    ``worst_gap`` is retained as REPORTING-ONLY -- the fixtures assert it.
    """
    for j in range(t_anchor + 1, prefix.length):
        if prefix.y[j] > y_hat(slope, intercept, j) + eps:
            return False
    return True


def envelope_violations(
    prefix: Prefix, t_anchor: int, candidate: Candidate, eps: float
) -> int:
    """How many bar highs in the domination set pierce ``candidate``'s line
    beyond ``eps``.  Zero for an envelope-valid candidate, by definition; the
    count is reported because RM-01's approved record states it."""
    count = 0
    for j in range(t_anchor + 1, prefix.length):
        if prefix.y[j] > y_hat(candidate.slope, candidate.intercept, j) + eps:
            count += 1
    return count
