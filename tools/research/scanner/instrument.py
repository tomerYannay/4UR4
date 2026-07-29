"""Lightweight profiling for the pilot — counters, not a sampling profiler.

Wraps the engine's hot functions **from outside**; no engine module is modified
and nothing here is imported by the engine (architecture test A-3 forbids the
reverse direction and is what keeps this honest).

What it measures, and why these:

* ``select_second_anchor`` calls — the §8 brute force. One call per evaluated
  bar means it is not amortised across bars.
* ``_worst_gap`` / ``domination_set`` calls — the candidate loop, the second
  factor.
* ``y_hat`` calls — the innermost operation, the third factor.

Their ratio *is* the complexity: if ``y_hat ≈ bars × candidates × dominated``
then the fold is cubic in series length, which is the finding rather than an
implementation detail.

**Binding sites, not modules.** ``engine/envelope.py`` does ``from .logspace
import y_hat``, so patching ``logspace.y_hat`` rebinds a name nobody calls and
silently counts ~0. Every module that imported a target by name must be patched
too, which is why ``_TARGETS`` lists modules rather than one canonical home. A
first version of this file patched only the defining modules and reported
``y_hat_calls: 7`` for a symbol that had run 713,172 ``_worst_gap`` calls — the
implausible ratio is what exposed it, so ``assert_wired`` below now makes that
failure mode loud instead of leaving it to be noticed.
"""

from __future__ import annotations

import resource
from dataclasses import dataclass, field

#: (attribute, modules that hold a binding for it). The first module is where
#: the function is defined; the rest imported it by name.
_TARGETS = (
    ("select_second_anchor", ("engine.envelope", "engine.detector", "engine.formation")),
    ("_worst_gap", ("engine.envelope",)),
    ("domination_set", ("engine.envelope",)),
    ("y_hat", ("engine.logspace", "engine.envelope", "engine.causal",
               "engine.trace", "engine.line", "engine.frozen")),
)


@dataclass
class Counters:
    select_second_anchor: int = 0
    worst_gap: int = 0
    y_hat: int = 0
    domination_set: int = 0
    #: Distinct ``B*`` bar indices observed — a proxy for hull re-binding.
    distinct_second_anchors: set = field(default_factory=set)

    @property
    def rebinds(self) -> int:
        """Re-binds ≈ distinct ``B*`` values minus the initial one."""
        return max(0, len(self.distinct_second_anchors) - 1)

    def snapshot(self) -> dict:
        return {
            "select_second_anchor_calls": self.select_second_anchor,
            "worst_gap_calls": self.worst_gap,
            "y_hat_calls": self.y_hat,
            "domination_set_calls": self.domination_set,
            "distinct_second_anchors": len(self.distinct_second_anchors),
            "hull_rebinds": self.rebinds,
        }


def peak_rss_mb() -> float:
    """Peak resident set size in MB. On Linux ``ru_maxrss`` is KB; on macOS bytes."""
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(raw / (1024 * 1024) if raw > 10_000_000 else raw / 1024, 1)


class Instrumented:
    """Context manager that installs counting wrappers and restores on exit."""

    def __init__(self) -> None:
        self.counters = Counters()
        self._saved: list = []

    def __enter__(self) -> "Instrumented":
        import importlib

        c = self.counters

        def make(attr, real):
            if attr == "select_second_anchor":
                def wrapper(*a, **k):
                    c.select_second_anchor += 1
                    out = real(*a, **k)
                    chosen = getattr(out, "selected", None)
                    if chosen is not None and getattr(chosen, "t", None) is not None:
                        c.distinct_second_anchors.add(chosen.t)
                    return out
            elif attr == "_worst_gap":
                def wrapper(*a, **k):
                    c.worst_gap += 1
                    return real(*a, **k)
            elif attr == "domination_set":
                def wrapper(*a, **k):
                    c.domination_set += 1
                    return real(*a, **k)
            else:
                def wrapper(*a, **k):
                    c.y_hat += 1
                    return real(*a, **k)
            return wrapper

        for attr, module_names in _TARGETS:
            # One shared wrapper per attribute so a call through any binding
            # increments the same counter exactly once.
            real = getattr(importlib.import_module(module_names[0]), attr)
            wrapper = make(attr, real)
            for name in module_names:
                mod = importlib.import_module(name)
                if getattr(mod, attr, None) is not real:
                    continue  # not bound here, or already wrapped
                setattr(mod, attr, wrapper)
                self._saved.append((mod, attr, real))
        return self

    def __exit__(self, *_exc) -> None:
        for mod, name, real in self._saved:
            setattr(mod, name, real)
        self._saved.clear()

    def assert_wired(self) -> None:
        """Fail loudly if a counter is implausibly zero.

        A silently-unpatched binding site reads as "this function was never
        called", which would understate the very cost this module exists to
        measure. Cheaper to assert than to re-derive from a suspicious ratio.
        """
        c = self.counters
        if c.select_second_anchor and not c.y_hat:
            raise RuntimeError(
                "instrumentation not wired: select_second_anchor ran "
                f"{c.select_second_anchor}x but y_hat counted 0 — a binding "
                "site is missing from _TARGETS"
            )
