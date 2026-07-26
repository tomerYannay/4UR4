"""Loading fixture data, and the structural parsers for the recorded traces.

Two rules this module exists to enforce:

1. **The gate is derived, not enumerated.**  :func:`golden_fixture_ids` walks
   ``product/fixtures/golden/`` and :func:`real_fixture_ids` walks
   ``product/fixtures/real/``.  Adding a fixture tightens the gate
   automatically; a hand-maintained list is the defect class this repository has
   already paid for.
2. **Recorded traces are compared structurally, never textually.**  The
   fixtures' gate traces are prose strings produced by another implementation.
   :func:`parse_gate_trace_line` turns one into a tuple of *facts*; matching
   another implementation's formatting is not part of the contract.
"""

from __future__ import annotations

import csv
import json
import os
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from ..bars import Bar, BarSeries

__all__ = [
    "REPO_ROOT",
    "GOLDEN_DIR",
    "REAL_DIR",
    "golden_fixture_ids",
    "real_fixture_ids",
    "load_expected",
    "load_json",
    "load_series",
    "parse_gate_trace_line",
    "parse_gate_fields",
    "as_decimal",
]

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir, os.pardir))
FIXTURES_DIR = os.path.join(REPO_ROOT, "product", "fixtures")
GOLDEN_DIR = os.path.join(FIXTURES_DIR, "golden")
REAL_DIR = os.path.join(FIXTURES_DIR, "real")
SCHEMA_DIR = os.path.join(FIXTURES_DIR, "schema")


def golden_fixture_ids() -> List[str]:
    """Every directory under ``product/fixtures/golden/`` — derived, not listed."""
    return sorted(
        name
        for name in os.listdir(GOLDEN_DIR)
        if os.path.isdir(os.path.join(GOLDEN_DIR, name))
    )


def real_fixture_ids() -> List[str]:
    """Every directory under ``product/fixtures/real/`` — derived, not listed.

    A ``real/*`` directory with no ``expected-causal.json`` must **fail**, never
    skip: a walk that checks nothing reports coverage it does not have.
    """
    return sorted(
        name
        for name in os.listdir(REAL_DIR)
        if os.path.isdir(os.path.join(REAL_DIR, name))
    )


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_expected(fixture_id: str) -> Dict[str, Any]:
    return load_json(os.path.join(GOLDEN_DIR, fixture_id, "expected.json"))


def _parse_price(raw: str) -> Optional[float]:
    text = raw.strip()
    if text == "":
        return None
    return float(text)


def _parse_timestamp(raw: str):
    text = raw.strip()
    try:
        return int(text)  # ordinal fixtures
    except ValueError:
        return text  # ISO date; lexicographic order is chronological


def load_series(csv_path: str) -> BarSeries:
    """Read an ``input.csv`` into a :class:`BarSeries`.

    A blank field becomes ``None`` so the §18 ``INVALID_INPUT`` guard can see it;
    parsing must not repair the input it is supposed to let the guard reject.
    """
    bars: List[Bar] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        for index, row in enumerate(csv.DictReader(handle)):
            key = "timestamp" if "timestamp" in row else "date"
            bars.append(
                Bar(
                    t=index,
                    timestamp=_parse_timestamp(row[key]),
                    open=_parse_price(row["open"]),
                    high=_parse_price(row["high"]),
                    low=_parse_price(row["low"]),
                    close=_parse_price(row["close"]),
                    volume=_parse_price(row["volume"]),
                )
            )
    return BarSeries(bars)


def golden_series(fixture_id: str) -> BarSeries:
    return load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))


def as_decimal(value) -> Optional[Decimal]:
    """A fixture's stored number as an exact ``Decimal``.

    ``repr`` of a float is its shortest round-tripping decimal, so a value the
    fixture wrote to 6 significant figures survives unchanged.
    """
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    return Decimal(repr(float(value)))


# --------------------------------------------------------------------------
# Structural parsers for the recorded formation traces.
# --------------------------------------------------------------------------

_GATE_LINE = re.compile(
    r"^t=(?P<t>\d+): (?P<label>[A-Z_]+) "
    r"\[F1 \|S_t\|=(?P<n>\d+)>=(?P<mfb>\d+):(?P<f1>ok|FAIL); "
    r"F2 tA=(?P<ta>null|\d+)<=\(t-1\)-(?P<mab>\d+):(?P<f2>ok|FAIL); "
    r"F3 B\*_t exists:(?P<f3>ok|FAIL)\]$"
)

_F1 = re.compile(r"^\|S_t\|=(?P<n>\d+)>=(?P<mfb>\d+):(?P<ok>ok|FAIL)$")
_F2 = re.compile(r"^tA=(?P<ta>null|\d+)<=\(t-1\)-(?P<mab>\d+):(?P<ok>ok|FAIL)$")
_F3 = re.compile(r"^B\*_t exists:(?P<ok>ok|FAIL)$")


def parse_gate_trace_line(line: str) -> Tuple:
    """``"t=8: ELIGIBLE [F1 ...; F2 ...; F3 ...]"`` -> a tuple of facts.

    Returns ``(t, |S_t|, tA, f1, f2, f3, eligible, reason)`` in exactly the shape
    :meth:`engine.formation.GateVerdict.structural` produces, so the comparison
    is on facts and never on formatting.
    """
    match = _GATE_LINE.match(line.strip())
    if match is None:
        raise AssertionError("unparseable gate-trace entry: %r" % line)
    label = match.group("label")
    eligible = label == "ELIGIBLE"
    return (
        int(match.group("t")),
        int(match.group("n")),
        None if match.group("ta") == "null" else int(match.group("ta")),
        match.group("f1") == "ok",
        match.group("f2") == "ok",
        match.group("f3") == "ok",
        eligible,
        None if eligible else label,
    )


def parse_gate_fields(entry: Dict[str, Any]) -> Tuple:
    """The same tuple, from ``expected-causal.json``'s structured gate entry."""
    f1 = _F1.match(entry["f1"])
    f2 = _F2.match(entry["f2"])
    f3 = _F3.match(entry["f3"])
    if not (f1 and f2 and f3):
        raise AssertionError("unparseable structured gate entry: %r" % entry)
    eligible = bool(entry["eligible"])
    return (
        int(entry["t"]),
        int(f1.group("n")),
        None if f2.group("ta") == "null" else int(f2.group("ta")),
        f1.group("ok") == "ok",
        f2.group("ok") == "ok",
        f3.group("ok") == "ok",
        eligible,
        None if eligible else entry["reason"],
    )


def gate_thresholds_from_trace_line(line: str) -> Tuple[int, int]:
    """``(min_formation_bars, min_ath_age_bars)`` as the trace itself states them."""
    match = _GATE_LINE.match(line.strip())
    if match is None:
        raise AssertionError("unparseable gate-trace entry: %r" % line)
    return int(match.group("mfb")), int(match.group("mab"))
