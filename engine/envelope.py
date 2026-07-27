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
from .logspace import exceeds, log_intercept, log_slope, y_hat

__all__ = [
    "Candidate",
    "Selection",
    "domination_set",
    "select_second_anchor",
    "envelope_violations",
]


@dataclass(frozen=True)
class Candidate:
    t: int
    high: float
    y: float
    slope: float
    intercept: float
    #: ``max`` over the domination set of ``y[j] - y_hat_i(j)``.  ``0`` at
    #: ``j == i`` **up to rounding** (see :func:`domination_set`), so "therefore
    #: never negative" does not follow and is not asserted: measured over every
    #: evaluable prefix of the corpus it is a tiny negative (``-2^-50``) at 47 of
    #: 104862 candidates, wherever the ``j == i`` residual is negative and every
    #: other dominated bar sits strictly below the line.  What the fixtures assert
    #: is narrower and does hold — 19 recorded entries across GX-01…GX-23 are
    #: exactly ``0``.
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


def domination_set(t_anchor: int, length: int) -> Tuple[int, ...]:
    """The §8 domination set over a prefix of ``length`` bars — **the** definition.

    Derived from the specification, endpoint by endpoint.  It is written out
    because ``EnvelopeDominationRange`` pins this endpoint and a test cannot derive
    its expectation from the code it is testing:

    * **near end — ``t_anchor + 1``.**  §8's algorithm step 3 reads "for EVERY bar
      high ... with ``tA < t_i < tB`` AND for every bar high with ``t_i > tB``".
      Both halves require ``t_i > tA`` **strictly**, and §1/Notation makes ``t`` an
      integer ordinal (``t ∈ {0,1,…,N−1}``), so ``t_i > tA`` on the integers is
      ``t_i >= tA + 1``.  The anchor bar itself is therefore **excluded**: ``A`` is
      the line's own endpoint, not something the line has to dominate.
    * **far end — ``length``, exclusive.**  §8's as-of-time note and §21.1 restrict
      the rule to the available prefix ``S_t`` = bars ``0 … t−1``, which this
      ``Prefix`` *is*; so the last dominated bar is ``length - 1``.
    * **``tB`` is included**, although §8 step 3's union formally omits it.  That is
      a superset, and one that is inert only for ``ε`` **well above rounding** — it
      is *not* inert "for ``ε >= 0``", and no proof of that is available here: §7
      fixes ``b`` so that ``ŷ_B(tB)`` is ``yB`` *zero up to rounding*, and in this
      module "up to rounding" is the whole content (M-1, M-2).  Measured over the
      6754 ``(tA, i)`` candidate pairs of the corpus, ``yB - ŷ_B(tB)`` is exactly
      ``0`` in 6528 (96.65%), strictly negative in 126, and **strictly positive in
      100 (1.48%)** — and at those 100, ``exceeds(yB, ŷ_B(tB), 0.0)`` is ``True``.
      So at ``ε = 0``, which ``params.py`` accepts (it rejects only ``ε < 0``), those
      candidates are invalidated by their **own** bar ``tB`` and the selection can
      return ``NO_VALID_SECOND_ANCHOR`` where §8 — which excludes ``tB`` — has a
      line: the deviation is **not** in the conservative direction.  No decimal
      constant is the bound, because the residual is a couple of ulps of the
      intermediate ``m·tB`` and so grows with the index: ``8.9e-16`` (``2^-50``) is
      the measured maximum over this corpus, while random draws at ``t ~ 1e5`` reach
      ``~1e-11``.  At the ratified ``ε = 0.02`` the inclusion is inert by thirteen
      orders of magnitude, and ``ε = 1e-15`` already suffices across the corpus.  It
      is kept because D-TL-05 says domination is over *every* bar high, and because
      ``Candidate.worst_gap``'s documented ``0`` at ``j == i`` — which the fixtures
      assert — is that inclusion.  Narrowing the set to §8's exact quantifier is a
      behaviour change, and is not this docstring's to authorize.

    The two ways to get the near end wrong, and why only one of them is visible in
    an outcome: ``range(t_anchor, …)`` adds the constraint ``yA <= ŷ_B(tA) + ε``,
    which is a *different predicate* from §8's and yet holds everywhere, because §7
    fixes ``b`` so the gap at ``tA`` is zero up to rounding — measured across the
    whole corpus, it changes **no** test outcome, which is why it must be pinned
    structurally rather than by re-running fixtures.  ``range(t_anchor + 2, …)``
    drops a bar §8 requires to be dominated, and is visible.
    """
    return tuple(range(t_anchor + 1, length))


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

    domination = domination_set(t_anchor, prefix.length)

    candidates: List[Candidate] = []
    # Candidacy iterates the same bars — ``i > tA`` — and is narrowed to the
    # DIFFERENT set by the strict ``H[i] < HA`` filter on the next line.
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
                envelope_valid=_is_envelope_valid(prefix, domination, slope, intercept, eps),
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


def _is_envelope_valid(
    prefix: Prefix,
    domination: Tuple[int, ...],
    slope: float,
    intercept: float,
    eps: float,
) -> bool:
    """Envelope validity, through the ONE pinned comparison: :func:`logspace.exceeds`.

    Plan §4.3 pins the right-hand side to be formed FIRST -- ``lhs > y_hat + eps`` --
    and explicitly forbids ``lhs - y_hat > eps``.  This predicate has been through
    both mistakes.  It first used ``worst_gap <= eps``, the forbidden form, twelve
    lines above :func:`envelope_violations` using the pinned one; that was fixed by
    *spelling* the pinned form here, which left the module with a second copy of an
    expression whose single site ``logspace`` claims to be.  Two spellings of ONE
    predicate in one module is the hazard the pin exists to prevent either way: at a
    boundary they can disagree by an ulp, which would yield ``envelope_valid=True``
    alongside ``envelope_violations() > 0`` for the same candidate -- an internal
    contradiction RM-01's Half-A assertion depends on being impossible.  So the call
    goes to ``exceeds`` now, and there is one spelling.

    Both gates measured the ``worst_gap <= eps`` form against the pinned one and
    neither found a disagreement: Code Review 0 over **13,043** candidate
    evaluations, and Verification -- which patched this predicate to compute both
    forms and ran the whole suite -- 0 over **436,691**, a superset.  Nothing moved
    then and nothing moves now (routing an identical expression through a call
    changes no arithmetic).  It is unified anyway, because "measured identical on
    this corpus" is precisely the argument that mutations M-1 and M-2 defeated: a
    6-significant-figure corpus cannot pin arithmetic form.

    ``domination`` is passed in rather than rebuilt: :func:`domination_set` is the
    only place the range is written down (M-28).

    ``worst_gap`` is retained as REPORTING-ONLY -- the fixtures assert it.
    """
    for j in domination:
        if exceeds(prefix.y[j], y_hat(slope, intercept, j), eps):
            return False
    return True


def envelope_violations(
    prefix: Prefix, t_anchor: int, candidate: Candidate, eps: float
) -> int:
    """How many bar highs in the domination set pierce ``candidate``'s line
    beyond ``eps``.  Zero for an envelope-valid candidate, by definition; the
    count is reported because RM-01's approved record states it.

    Same two rules as :func:`_is_envelope_valid`, and deliberately not a second
    statement of either: the range comes from :func:`domination_set` and the
    comparison from :func:`logspace.exceeds`.  ``t_anchor`` rather than the set
    itself, because this is the module's public reporting entry point and its
    callers hold the anchor, not the set."""
    count = 0
    for j in domination_set(t_anchor, prefix.length):
        if exceeds(prefix.y[j], y_hat(candidate.slope, candidate.intercept, j), eps):
            count += 1
    return count
