"""The named, versioned detector configuration (§20.2, D-TL-12).

Two deliberate omissions:

* **There is no ``k`` here.**  The pivot window is non-authoritative for
  selection *and* for formation (HD-11, HD-14 / D-TL-12), so it does not live in
  the detector's parameter object at all.  It lives in :class:`PivotParams`,
  which only ``engine/pivots.py`` consumes.  This makes architectural test A-1
  ("no geometry or formation module reads ``k``") true by construction rather
  than by inspection.
* **The six §15/§16/§17 parameters have defaults; ``eps_break`` still does
  not.**  These two cases look alike and are not.  ``eps_break`` is *unlocked by
  ruling* — HD-03 and §13.5 say "no locked default" — so this module must keep
  refusing to invent one.  ``eps_fail``, ``F_fail``, ``eps_retest``,
  ``W_retest``, ``h_hold`` and ``E_expiry`` come from D-TL-08, D-TL-09 and
  D-TL-10, each **`Human-approval: no` with a stated default**, so carrying that
  default here is the specification's own instruction rather than an engine
  choice.  Five of the ten fixture configurations with post-breakout behaviour
  supply none of them, so they cannot come from the fixtures.

  They are deliberately **not** added to :data:`REQUIRED_FIXTURE_PARAMS`: that
  tuple names parameters a caller may never omit, and those five fixtures
  legitimately do.  The safeguard is the other way round —
  :meth:`DetectorParams.from_fixture_params` reads each of the six **when
  present**, and a test asserts that every carried value equals the default here,
  so a future fixture carrying a non-default value fails loudly instead of being
  silently overridden.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from .logspace import SPLIT_LOG_JUMP_THRESHOLD

__all__ = [
    "DetectorParams",
    "PivotParams",
    "REQUIRED_FIXTURE_PARAMS",
    "POST_BREAKOUT_FIXTURE_PARAMS",
]


#: Parameters that change a Phase-2 outcome and therefore may never be defaulted
#: silently when a caller supplies a parameter block.
REQUIRED_FIXTURE_PARAMS = ("eps", "eps_break", "min_formation_bars", "min_ath_age_bars")

#: The six §15/§16/§17 parameters, named once so the harness can cross-check a
#: fixture-carried value against this module's default without re-listing them.
#: Read when a fixture carries one; defaulted when it does not (see the module
#: docstring for why that is safe here and is not safe for ``eps_break``).
POST_BREAKOUT_FIXTURE_PARAMS = (
    "eps_fail",
    "F_fail",
    "eps_retest",
    "W_retest",
    "h_hold",
    "E_expiry",
)


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
    #: confidence input and is out of Phase-3 scope, so nothing reads it.
    eps_touch: Optional[float] = None
    #: §15, D-TL-08 — failed-breakout tolerance and window.  Carried by GX-04,
    #: GX-05 and GX-17 at exactly these values; defaulted where omitted.
    eps_fail: float = 0.01
    F_fail: int = 10
    #: §16, D-TL-09 — retest tolerance, return window and hold window.  Carried
    #: by GX-04 and GX-17 at exactly these values.
    eps_retest: float = 0.01
    W_retest: int = 20
    h_hold: int = 3
    #: §17, D-TL-10 — post-breakout expiry horizon.  Carried by GX-07.
    E_expiry: int = 100

    def __post_init__(self) -> None:
        if self.eps < 0:
            raise ValueError("eps must be >= 0")
        if self.eps_break < 0:
            raise ValueError("eps_break must be >= 0")
        if self.min_formation_bars < 0:
            raise ValueError("min_formation_bars must be >= 0")
        if self.min_ath_age_bars < 0:
            raise ValueError("min_ath_age_bars must be >= 0")
        if self.eps_fail < 0:
            raise ValueError("eps_fail must be >= 0")
        if self.eps_retest < 0:
            raise ValueError("eps_retest must be >= 0")
        if self.F_fail < 0:
            raise ValueError("F_fail must be >= 0")
        if self.W_retest < 0:
            raise ValueError("W_retest must be >= 0")
        if self.h_hold < 0:
            raise ValueError("h_hold must be >= 0")
        if self.E_expiry < 1:
            raise ValueError("E_expiry must be >= 1")

    def _as_kwargs(self) -> Dict[str, Any]:
        """Every field, DERIVED from the dataclass rather than re-listed.

        Both copy constructors below built a hand-written kwarg dict, and a field
        forgotten there does not fail — it silently resets to its default in
        every sweep the tests run.  Deriving the dict makes that class of defect
        impossible for the six parameters this build adds and for any added
        later.
        """
        return {name: getattr(self, name) for name in self.__dataclass_fields__}

    def with_eps_break(self, eps_break: float) -> "DetectorParams":
        """A copy at a different breakout tolerance — used by the HD-13 sweep."""
        return self.replace(eps_break=eps_break)

    def replace(self, **changes: Any) -> "DetectorParams":
        base = self._as_kwargs()
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

        Raises if any outcome-affecting parameter is absent.  ``k`` is
        deliberately ignored (HD-11: non-authoritative).  Each of
        :data:`POST_BREAKOUT_FIXTURE_PARAMS` is **read when the fixture carries
        it** and defaulted when it does not — never silently overridden.

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
        carried: Dict[str, Any] = {}
        for key in POST_BREAKOUT_FIXTURE_PARAMS:
            if key in params:
                field = cls.__dataclass_fields__[key]
                carried[key] = (
                    int(params[key]) if field.type == "int" else float(params[key])
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
            **carried,
        )


@dataclass(frozen=True)
class PivotParams:
    """§5 — the pivot window, for descriptive output only (D-TL-03, HD-11).

    Kept in its own type so that no geometry or formation module can reach it.
    """

    k: int = 3
