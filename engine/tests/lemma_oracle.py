"""§21.4's running-maximum lemma, written as an independent test oracle.

The §8 brute force is the *definition* and the engine's production path.  The
lemma is explicitly "an optimization, not the definition", usable only if
lossless against that recomputation, with mandatory fallback when the anchor
changes, a candidate ties the ATH, or ``B*_t = ⊥``.

Implementing it here rather than in the engine buys a two-version check at zero
product risk: this module is written from §21.4's closed form, the engine from
§8's brute force.

CORRECTION (Code Review, measured).  An earlier version of this docstring said
"the only code they share is :mod:`engine.logspace`".  That was FALSE, and it
overstated the strongest independence control in this suite.  §21.4's own last
bullet MANDATES a fallback -- when the anchor changes, a candidate ties the ATH,
or no previous ``B*`` exists, the closed form does not apply and the oracle must
re-select, which it does by calling the engine's own :func:`anchor_of` and
:func:`select_second_anchor`.  Measured over the corpus, the oracle decides
**77 of 590 prefixes by calling the engine's own selector** and 513 by the closed
form.  Those 77 are the formation-critical early prefixes and every post-reset
prefix -- exactly the transitions where an independent check is worth most.  The
DESIGN is correct and §21.4 requires it; only the claim about its independence
was wrong.  Read this as a two-version check on the 513, and a self-consistency
check on the 77.

The lemma::

    B*_{t+1} = (t, H[t])   if  y[t] >= y_hat_t(t)
             = B*_t         otherwise
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from ..anchor import anchor_of
from ..bars import Prefix
from ..envelope import select_second_anchor
from ..logspace import log_intercept, log_slope, reaches, y_hat

__all__ = ["rolling_b_star"]


def rolling_b_star(
    logs: List[float], highs: List[float], eps: float
) -> List[Optional[int]]:
    """``[B*_t for t in 0..n]`` by the §21.4 closed form, with its own fallbacks.

    Returns the *bar index* of ``B*_t``, or ``None`` where no candidate is
    envelope-valid.  Index ``t`` of the result is the selection over ``S_t``.
    """
    n = len(logs)
    out: List[Optional[int]] = []

    previous_anchor: Optional[int] = None
    previous_b: Optional[int] = None

    for t in range(n + 1):
        prefix = Prefix(tuple(logs[:t]), tuple(highs[:t]), t)
        anchor = anchor_of(prefix)
        if anchor is None:
            out.append(None)
            previous_anchor, previous_b = None, None
            continue

        if t == 0:
            out.append(None)
            previous_anchor, previous_b = anchor.t, None
            continue

        bar = t - 1  # the bar just incorporated
        anchor_changed = previous_anchor != anchor.t
        ties_the_ath = highs[bar] == anchor.high and bar != anchor.t

        if anchor_changed or previous_b is None or ties_the_ath:
            # Mandated fallback to the §8 recomputation (§21.4, last bullet).
            selection = select_second_anchor(prefix, anchor.t, eps)
            current = None if selection.selected is None else selection.selected.t
        else:
            slope = log_slope(logs[previous_b], anchor.y, previous_b, anchor.t)
            intercept = log_intercept(anchor.y, slope, anchor.t)
            if reaches(logs[bar], y_hat(slope, intercept, bar)):
                current = bar
            else:
                current = previous_b

        out.append(current)
        previous_anchor, previous_b = anchor.t, current

    return out
