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

Several claims below are **measurements**, and a measurement whose enumeration is
unstated cannot be re-derived by a later gate.  Two enumerations are therefore
named once here and cited by name; both use ``ε = 0.02`` and both are re-derivable
from ``engine`` alone:

* **CORPUS-ATH** — every series under ``product/fixtures/golden/`` and
  ``product/fixtures/real/`` (24 series), each truncated to every prefix length
  ``L = 1 … N`` that :func:`detector.prefix_of` accepts (GX-18 stops at ``L = 3``:
  its bar 3 has no usable high), evaluated at ``tA = anchor_of(prefix).t`` — the §4
  anchor the engine actually uses.  **13,434** candidates.
* **CORPUS-SWEEP** — the same series and the same prefixes, but with ``tA`` swept
  over **every** bar ``0 … L−1`` instead of taken from §4.  **104,810** candidates,
  a superset of CORPUS-ATH.  It is deliberately *not* engine-realistic: it is the
  wider net that makes floating-point edges visible at all, and a count taken under
  it says nothing on its own about what the engine does at the §4 anchor.
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
    #: never negative" does not follow *as a general invariant*: it goes tiny-
    #: negative — ``-2^-50`` or ``-2^-51``, two distinct values — wherever the
    #: ``j == i`` residual is negative and every other dominated bar sits strictly
    #: below the line.  How often depends entirely on the enumeration, so both are
    #: stated: **0 of 13,434** under CORPUS-ATH, and **47 of 104,810** under
    #: CORPUS-SWEEP (41 at ``-2^-50``, 6 at ``-2^-51``).  At the §4 anchor the
    #: engine actually uses, on this corpus, it never happened.
    #:
    #: Non-negativity is therefore asserted **only where it was measured to hold**
    #: and never as a law: ``test_worst_gap_is_exactly_zero_at_the_candidate_itself``
    #: asserts ``>= 0`` over GX-01's 8-bar prefix at the §4 anchor and says in its
    #: docstring that this is a statement about that case.  What the fixtures assert
    #: is narrower still and does hold — of the 143 recorded ``worst_gap`` entries
    #: across GX-01…GX-23, 19 are exactly ``0`` and none is negative.
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
      module "up to rounding" is the whole content (M-1, M-2).  The residual
      ``yB - ŷ_B(tB)``, measured at every ``(tA, tB)`` candidate pair of both stated
      enumerations:

      - **CORPUS-ATH** — exactly ``0`` at all **13,434** pairs.  At the §4 anchor,
        on this corpus, the inclusion is inert even at ``ε = 0``.
      - **CORPUS-SWEEP** — exactly ``0`` at 102,544 of **104,810** (97.84%),
        strictly negative at 1,262, and **strictly positive at 1,004 (0.96%)**; at
        each of those 1,004, ``exceeds(yB, ŷ_B(tB), 0.0)`` is ``True``.

      So at ``ε = 0``, which ``params.py`` accepts (it rejects only ``ε < 0``), such
      a candidate is invalidated by its **own** bar ``tB`` and the selection can
      return ``NO_VALID_SECOND_ANCHOR`` where §8 — which excludes ``tB`` — has a
      line: the deviation is **not** in the conservative direction.  That it does
      not arise under CORPUS-ATH is a property of this corpus, not a bound.  No
      decimal constant is the bound either, because the residual is a couple of ulps
      of the intermediate ``m·tB`` and so grows with the index: ``8.9e-16``
      (``2^-50``) is the largest residual in **either** direction anywhere in
      CORPUS-SWEEP, and CORPUS-ATH produces none at all in either direction; a
      constructed draw with ``tA`` near ``1e5`` and ``tB`` within twenty bars of it
      reaches ``1.5e-11``.  At the
      ratified ``ε = 0.02`` the inclusion is inert by thirteen orders of magnitude,
      and ``ε = 1e-15`` already suffices across both enumerations.  It is kept
      because D-TL-05 says domination is over *every* bar high, and because
      ``Candidate.worst_gap``'s documented ``0`` at ``j == i`` — which the fixtures
      assert — is that inclusion.  Narrowing the set to §8's exact quantifier is a
      behaviour change, and is not this docstring's to authorize.

    **The asymmetry this docstring does not resolve.**  The two ends are justified
    from different places, and the justifications are in tension.  ``tB`` is kept on
    D-TL-05's "every bar high", which §21.1 echoes as domination over *all* bar highs
    in ``S_t``; read that way, the same sentence would keep ``tA`` — which the near-end
    bullet above excludes on §8 step 3's strict ``tA < t_i``.  Read the other way,
    §8's strict quantifier governs and ``tB`` should go.  Nothing here reconciles
    them, and this docstring does not claim the specification settles it: it records
    that the engine takes the strict reading at the near end and the "every bar high"
    reading at ``tB``, and that both endpoints are pinned structurally by
    ``EnvelopeDominationRange`` so that neither can drift silently.  Changing either
    is a behaviour change and belongs to whoever can authorize one.

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
