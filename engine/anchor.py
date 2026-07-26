"""§4 — the ATH anchor, computed as-of-time over the available prefix.

``A_t = (tA, HA)`` with ``HA = max over S_t of H[.]`` and ``tA`` the **earliest**
bar of ``S_t`` attaining it (D-TL-02: the resistance line should span the
longest descent).  Undefined for an empty prefix.

The function sees a :class:`~engine.bars.Prefix` and nothing else, so it cannot
consider a bar outside the prefix it was handed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .bars import Prefix

__all__ = ["Anchor", "anchor_of"]


@dataclass(frozen=True)
class Anchor:
    t: int
    high: float
    y: float


def anchor_of(prefix: Prefix) -> Optional[Anchor]:
    """``A_t`` over ``prefix``; ``None`` when ``S_t`` is empty (§21.1)."""
    if prefix.length == 0:
        return None
    best_index = 0
    best_high = prefix.high[0]
    for index in range(1, prefix.length):
        # Strict `>` keeps the EARLIEST bar of a tie (D-TL-02).  Using `>=`
        # here is mutation M-14 and is caught by GX-12.
        if prefix.high[index] > best_high:
            best_high = prefix.high[index]
            best_index = index
    return Anchor(best_index, best_high, prefix.y[best_index])
