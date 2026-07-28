"""``Λ_t`` — the line active at the start of a bar (§21.1).

Its own module for one structural reason: :mod:`engine.frozen` wraps a ``Line``
as ``Λ^F`` and :mod:`engine.causal` builds both, so a ``Line`` living in
``causal`` would make the dependency circular.  ``causal`` re-exports the name,
so every existing import site is unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .logspace import line_price, y_hat

__all__ = ["Line"]


@dataclass(frozen=True)
class Line:
    """``Λ_t`` — anchor, canonical second anchor, slope and intercept (§21.1).

    Exactly §21.5's frozen-field rows 1–4 and nothing else, so freezing a line is
    a wrap rather than a copy: :class:`engine.frozen.FrozenLine` adds only the
    two rows this type lacks.
    """

    t_anchor: int
    high_anchor: float
    y_anchor: float
    t_b: int
    high_b: float
    m: float
    b: float

    @property
    def identity(self) -> Tuple[int, int]:
        return (self.t_anchor, self.t_b)

    def y_hat_at(self, u: int) -> float:
        return y_hat(self.m, self.b, u)

    def price_at(self, u: int) -> float:
        return line_price(self.m, self.b, u)
