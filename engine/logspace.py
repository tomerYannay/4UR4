"""Log-space arithmetic — the ONLY site of `ln`, slope, intercept, line evaluation
and 6-significant-figure rounding.

Every algebraic form below is *pinned*, because two algebraically identical
readings of specification §7 are not identical in IEEE 754 and have already been
demonstrated to flip a selected anchor (fixture GX-14).  The pinned forms are:

| quantity   | required form                          | forbidden                              |
|------------|----------------------------------------|----------------------------------------|
| ``y[t]``   | ``math.log(H[t])`` computed once/bar   | ``log`` of a ratio, ``log1p``          |
| ``slope``  | ``(y[i] - y[tA]) / (i - tA)``          | ``log(H[i]/H[tA]) / (i - tA)``         |
| ``b``      | ``y[tA] - m * tA``                     | any rearrangement                      |
| ``y_hat``  | ``m * u + b``                          | ``y[tA] + m * (u - tA)``               |
| compare    | ``lhs > y_hat + tol`` (RHS first)      | ``lhs - y_hat > tol``                  |
| tie test   | exact ``==`` on the slope doubles      | any epsilon-tolerant "near tie"        |

The four comparison forms below are one per specification glyph, and the glyph is
copied rather than interpreted: §10.1/§13.1 write ``>`` (:func:`exceeds`), §15
writes ``<`` (:func:`falls_below`), §16's return leg writes ``<=``
(:func:`at_or_below`), §16's hold leg writes ``>=`` (:func:`at_or_above`), and
§21.4's re-selection trigger writes ``>=`` against the line itself
(:func:`reaches`).  Every one of them forms the right-hand side first.

Spec refs: §3 (log transform), §7 (slope/intercept), §9 (tolerance), §18
(``SUSPECTED_UNADJUSTED_SPLIT`` threshold), §19 (6 significant figures), §20
(determinism).
"""

from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

__all__ = [
    "SPLIT_LOG_JUMP_THRESHOLD",
    "SIGNIFICANT_FIGURES",
    "ln_price",
    "log_slope",
    "log_intercept",
    "y_hat",
    "line_price",
    "exceeds",
    "falls_below",
    "at_or_below",
    "at_or_above",
    "reaches",
    "sig6",
    "sig6_stable",
]

#: §18 — "an impossible single-bar log jump ``|y[t] - y[t-1]| > ln(1.5)``".
#:
#: AMBIGUITY, resolved here and stated so it is reviewable: two fixtures carry a
#: ``split_log_jump_threshold`` of ``0.405465``.  That is ``ln(1.5)`` rendered to
#: 6 significant figures, not a distinct parameter value, so the specification's
#: ``ln(1.5)`` is used.  The two readings differ by ~1.1e-7 and the choice moves
#: no fixture outcome — asserted by a unit test — but it does decide the exact
#: boundary case, where the printed value would (wrongly) reject a jump of
#: exactly ``ln(1.5)`` that §18's strict ``>`` admits.
SPLIT_LOG_JUMP_THRESHOLD = math.log(1.5)

#: §19 — "values to 6 significant figures, so Verification is exact".
SIGNIFICANT_FIGURES = 6


def ln_price(price: float) -> float:
    """``y = ln(price)`` — §3.  The single site at which a price becomes a log."""
    return math.log(price)


def log_slope(y_i: float, y_a: float, i: int, t_a: int) -> float:
    """``m = (y_i - y_a) / (i - t_a)`` — §7.

    The numerator is a difference of *cached* logs and the denominator an exact
    integer difference.  Both halves matter (mutation M-1).
    """
    return (y_i - y_a) / (i - t_a)


def log_intercept(y_a: float, m: float, t_a: int) -> float:
    """``b = y_a - m * t_a`` — §7, so that ``y_hat(t_a) == y_a``."""
    return y_a - m * t_a


def y_hat(m: float, b: float, u: int) -> float:
    """``y_hat(u) = m * u + b`` — §7.

    Deliberately *not* ``y_a + m * (u - t_a)``: equal in the reals, unequal in
    IEEE 754 whenever ``t_a != 0`` (mutation M-2).
    """
    return m * u + b


def line_price(m: float, b: float, u: int) -> float:
    """``line(u) = exp(y_hat(u))`` — §7, the trendline back in price space."""
    return math.exp(y_hat(m, b, u))


def exceeds(lhs: float, y_hat_value: float, tolerance: float) -> bool:
    """``lhs > y_hat + tolerance`` — strict, right-hand side formed first.

    Used for the §10.1 pierce test (``tolerance = eps``) and the §13.1 breakout
    predicate (``tolerance = eps_break``).  Strictness is load-bearing: at
    exactly the boundary the inequality is NOT met (GX-15).
    """
    return lhs > y_hat_value + tolerance


def falls_below(lhs: float, y_hat_value: float, tolerance: float) -> bool:
    """``lhs < y_hat - tolerance`` — strict, right-hand side formed first.

    The §15 failed-breakout predicate (``tolerance = eps_fail``).  §15 writes
    ``<``; the strictness is copied from the glyph, not chosen.  Nothing in the
    corpus sits on this boundary — the tightest recorded failure margin is
    ``0.0492028`` — so a constructed unit test pins it instead.
    """
    return lhs < y_hat_value - tolerance


def at_or_below(lhs: float, y_hat_value: float, tolerance: float) -> bool:
    """``lhs <= y_hat + tolerance`` — NON-strict, right-hand side formed first.

    The §16 retest **return** leg (``tolerance = eps_retest``): §16 condition 1
    writes ``≤``, so a low that lands exactly on ``y_hat + eps_retest`` is a
    return.
    """
    return lhs <= y_hat_value + tolerance


def at_or_above(lhs: float, y_hat_value: float, tolerance: float) -> bool:
    """``lhs >= y_hat - tolerance`` — NON-strict, right-hand side formed first.

    The §16 retest **hold** leg (``tolerance = eps_retest``): §16 condition 2
    writes ``≥``, so a close exactly on ``y_hat - eps_retest`` holds.
    """
    return lhs >= y_hat_value - tolerance


def reaches(lhs: float, y_hat_value: float) -> bool:
    """``lhs >= y_hat`` — the §21.4 re-selection trigger ("a high *reaches* the
    active line").  Note ``>=``: equality re-binds and is resolved by
    ``ENVELOPE_TIE_LATER`` (§21.4 proof sketch (iv))."""
    return lhs >= y_hat_value


def sig6(value: float) -> Decimal:
    """Round the *exact binary value* of ``value`` to 6 significant figures.

    ``ROUND_HALF_EVEN`` at an exact tie (plan §9.2 OQ-B).  Returns a ``Decimal``
    so that comparison against a fixture's stored decimal is exact rather than
    another float comparison.
    """
    if value == 0:
        return Decimal(0)
    with localcontext() as ctx:
        ctx.prec = SIGNIFICANT_FIGURES
        ctx.rounding = ROUND_HALF_EVEN
        return +Decimal(value)


def sig6_stable(value: float) -> bool:
    """True iff ``sig6`` is unchanged by perturbing ``value`` by one ulp either way.

    This is the C-4 tie-proximity audit: if it is ever False for a value the
    conformance gate compares, the gate's rounding mode is an undeclared
    platform dependency and the disagreement must be escalated, not absorbed.
    """
    if value == 0 or math.isinf(value) or math.isnan(value):
        return True
    here = sig6(value)
    down = sig6(math.nextafter(value, -math.inf)) if hasattr(math, "nextafter") else here
    up = sig6(math.nextafter(value, math.inf)) if hasattr(math, "nextafter") else here
    return here == down == up
