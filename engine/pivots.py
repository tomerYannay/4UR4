"""§5 — pivot highs.  **SECONDARY / NON-AUTHORITATIVE** (HD-11, D-TL-03).

A pivot filter may be used for visualization, descriptive metadata, confidence
features and provably-lossless optimization — and for **nothing else**.  It
never removes a candidate from §6/§8, never changes ``B*``, and never affects
formation eligibility (§21.3, D-TL-12).

This module exists so the descriptive ``pivot_context`` a fixture records can be
reproduced, and so that the *absence* of an import of it from
``envelope``/``formation``/``causal``/``detector`` is a checkable fact
(architectural test A-1).  Nothing in this package imports it.
"""

from __future__ import annotations

from typing import List, Sequence

from .params import PivotParams

__all__ = ["is_pivot_high", "confirmed_pivots"]


def is_pivot_high(highs: Sequence[float], p: int, k: int) -> bool:
    """``H[p] > H[p-i]`` for all ``i in 1..k`` and ``H[p] >= H[p+j]`` for all
    ``j in 1..k`` (§5).

    Strict ``>`` on the left, ``>=`` on the right, so the **earliest** bar of a
    flat-topped plateau is the pivot.  A bar within ``k`` of either end cannot be
    confirmed.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    if p - k < 0 or p + k >= len(highs):
        return False
    for i in range(1, k + 1):
        if not highs[p] > highs[p - i]:
            return False
    for j in range(1, k + 1):
        if not highs[p] >= highs[p + j]:
            return False
    return True


def confirmed_pivots(highs: Sequence[float], params: PivotParams) -> List[int]:
    """Every confirmed ``k``-pivot high in ``highs``.  Descriptive output only."""
    return [p for p in range(len(highs)) if is_pivot_high(highs, p, params.k)]
