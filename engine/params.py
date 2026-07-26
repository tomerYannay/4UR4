"""The named, versioned detector configuration (§20.2, D-TL-12).

Two deliberate omissions:

* **There is no ``k`` here.**  The pivot window is non-authoritative for
  selection *and* for formation (HD-11, HD-14 / D-TL-12), so it does not live in
  the detector's parameter object at all.  It lives in :class:`PivotParams`,
  which only ``engine/pivots.py`` consumes.  This makes architectural test A-1
  ("no geometry or formation module reads ``k``") true by construction rather
  than by inspection.
* **There are no Phase-3 parameters.**  ``eps_fail``, ``eps_retest``,
  ``W_retest``, ``h_hold``, ``F_fail``, ``E_expiry`` gate behaviour this build
  does not implement.  Fixtures that carry them are read through
  :meth:`DetectorParams.from_fixture_params`, which ignores unknown keys but
  refuses to *default* any key that changes a Phase-2 outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from .logspace import SPLIT_LOG_JUMP_THRESHOLD

__all__ = ["DetectorParams", "PivotParams", "REQUIRED_FIXTURE_PARAMS"]


#: Parameters that change a Phase-2 outcome and therefore may never be defaulted
#: silently when a caller supplies a parameter block.
REQUIRED_FIXTURE_PARAMS = ("eps", "eps_break", "min_formation_bars", "min_ath_age_bars")


@dataclass(frozen=True)
class DetectorParams:
    """§20.2 named config, pinned with ``spec_version`` and ``tolerance_version``.

    ``eps_break`` is **versioned and unlocked** (HD-03 / §13.5): it has no
    default here, and a caller that omits it gets an error rather than a value
    this build invented.
    """

    eps: float
    eps_break: float
    min_formation_bars: int
    min_ath_age_bars: int
    tolerance_version: str
    spec_version: str
    #: §18 — the threshold is the specification's ``ln(1.5)``.
    split_log_jump_threshold: float = SPLIT_LOG_JUMP_THRESHOLD
    #: §9 — touch tolerance.  Carried for the record; §12 touch counting is a
    #: confidence input and is out of Phase-2 scope, so nothing reads it.
    eps_touch: Optional[float] = None

    def __post_init__(self) -> None:
        if self.eps < 0:
            raise ValueError("eps must be >= 0")
        if self.eps_break < 0:
            raise ValueError("eps_break must be >= 0")
        if self.min_formation_bars < 0:
            raise ValueError("min_formation_bars must be >= 0")
        if self.min_ath_age_bars < 0:
            raise ValueError("min_ath_age_bars must be >= 0")

    def with_eps_break(self, eps_break: float) -> "DetectorParams":
        """A copy at a different breakout tolerance — used by the HD-13 sweep."""
        return DetectorParams(
            eps=self.eps,
            eps_break=eps_break,
            min_formation_bars=self.min_formation_bars,
            min_ath_age_bars=self.min_ath_age_bars,
            tolerance_version=self.tolerance_version,
            spec_version=self.spec_version,
            split_log_jump_threshold=self.split_log_jump_threshold,
            eps_touch=self.eps_touch,
        )

    def replace(self, **changes: Any) -> "DetectorParams":
        base = dict(
            eps=self.eps,
            eps_break=self.eps_break,
            min_formation_bars=self.min_formation_bars,
            min_ath_age_bars=self.min_ath_age_bars,
            tolerance_version=self.tolerance_version,
            spec_version=self.spec_version,
            split_log_jump_threshold=self.split_log_jump_threshold,
            eps_touch=self.eps_touch,
        )
        base.update(changes)
        return DetectorParams(**base)

    @classmethod
    def from_fixture_params(
        cls,
        params: Mapping[str, Any],
        *,
        spec_version: str,
        split_log_jump_threshold: Optional[float] = None,
    ) -> "DetectorParams":
        """Build from a fixture ``params`` block.

        Raises if any outcome-affecting parameter is absent.  ``k`` and the
        Phase-3 tolerances present in some fixtures are deliberately ignored.

        ``split_log_jump_threshold`` is **not** taken from the fixture: fixtures
        print it to 6 significant figures (``0.405465``), which is a rendering of
        §18's ``ln(1.5)`` rather than a distinct value (see the note in
        ``engine/logspace.py``).  A unit test asserts both readings give
        identical outcomes on the two fixtures that carry the key.
        """
        missing = [key for key in REQUIRED_FIXTURE_PARAMS if key not in params]
        if missing:
            raise ValueError(
                "fixture params omit outcome-affecting parameter(s): " + ", ".join(missing)
            )
        return cls(
            eps=float(params["eps"]),
            eps_break=float(params["eps_break"]),
            min_formation_bars=int(params["min_formation_bars"]),
            min_ath_age_bars=int(params["min_ath_age_bars"]),
            tolerance_version=str(params.get("tolerance_version", "")),
            spec_version=spec_version,
            split_log_jump_threshold=(
                SPLIT_LOG_JUMP_THRESHOLD
                if split_log_jump_threshold is None
                else float(split_log_jump_threshold)
            ),
            eps_touch=(float(params["eps_touch"]) if "eps_touch" in params else None),
        )


@dataclass(frozen=True)
class PivotParams:
    """§5 — the pivot window, for descriptive output only (D-TL-03, HD-11).

    Kept in its own type so that no geometry or formation module can reach it.
    """

    k: int = 3
