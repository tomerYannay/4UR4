"""The closed state and reason-code sets, and the transition record.

Both sets mirror ``product/fixtures/schema/fixture.schema.json`` exactly; test
``A-4`` asserts that equality against the committed schema so the two cannot
drift.  Adding a member here is a product-definition change (§10, §18) and is
not the engine author's to make.

Every member of both sets is now reachable **except one**, and that one
exception is deliberate — see :class:`LineState`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet

__all__ = [
    "LineState",
    "ReasonCode",
    "PHASE2_REASON_CODES",
    "PHASE3_REASON_CODES",
    "TransitionRecord",
]


class LineState(str, Enum):
    """§11 — the line state machine.  ``WICK_BREAK`` is deliberately absent: it
    is a reason code, not a state (§11, §14).

    **``EXPIRED`` IS RESERVED AND UNREACHABLE.  DO NOT "FIX" IT.**  This is said
    at the definition site because ESC-1 ruled it there, and because a later
    reader who noticed an enum member no code assigns would otherwise repair the
    gap by inserting an ``EXPIRED`` record — and break GX-07.

    The history, in one paragraph so the ruling can be checked rather than
    taken.  §11 originally drew expiry as **two** edges through a state of this
    name (``BROKEN_OUT``/``RETESTED`` → ``EXPIRED`` → ``NONE``) while fixture
    GX-07 records **one** transition, ``bar 110: BROKEN_OUT → NONE /
    EXPIRED_POST_BREAKOUT``.  HD-22 forbids editing the fixture.  The Product
    Steward ruled on 2026-07-28 (§11, §17, §22) that §11 draws **one** edge,
    which is the reading GX-07 already encoded — a clarification, not a
    behaviour change, and GX-07 is the only fixture in the corpus that expires.
    The member stays because architectural test A-4 requires this set to
    **equal** the committed schema's closed set, and the schema carries it.

    So: no bar is ever assigned ``LineState.EXPIRED``, and no emitted record
    carries it as ``from`` or as ``to``.  Both halves are asserted by the suite,
    and an architectural test asserts that this docstring is the only place in
    ``engine/`` that names the member at all.
    """

    NONE = "NONE"
    ACTIVE = "ACTIVE"
    BROKEN_OUT = "BROKEN_OUT"
    RETESTED = "RETESTED"
    FAILED_BREAKOUT = "FAILED_BREAKOUT"
    EXPIRED = "EXPIRED"


class ReasonCode(str, Enum):
    """§10, §11, §18, §21.6 — every accept/reject carries one of these."""

    LINE_ESTABLISHED = "LINE_ESTABLISHED"
    ENVELOPE_TIE_LATER = "ENVELOPE_TIE_LATER"
    WICK_BREAK = "WICK_BREAK"
    INVALID_PIERCE = "INVALID_PIERCE"
    BREAKOUT_CONFIRMED = "BREAKOUT_CONFIRMED"
    FAILED_BREAKOUT = "FAILED_BREAKOUT"
    RETEST_HELD = "RETEST_HELD"
    RESET_NEW_ATH = "RESET_NEW_ATH"
    EXPIRED_POST_BREAKOUT = "EXPIRED_POST_BREAKOUT"
    ATH_TOO_RECENT = "ATH_TOO_RECENT"
    INSUFFICIENT_BARS = "INSUFFICIENT_BARS"
    NO_VALID_SECOND_ANCHOR = "NO_VALID_SECOND_ANCHOR"
    SUSPECTED_UNADJUSTED_SPLIT = "SUSPECTED_UNADJUSTED_SPLIT"
    INVALID_PRICE = "INVALID_PRICE"
    INVALID_INPUT = "INVALID_INPUT"


#: Codes the pre-breakout layer owns — behaviour evaluated while the structure
#: is still ``ACTIVE``, plus the §18 input guards.
PHASE2_REASON_CODES: FrozenSet[ReasonCode] = frozenset(
    {
        ReasonCode.LINE_ESTABLISHED,
        ReasonCode.ENVELOPE_TIE_LATER,
        ReasonCode.WICK_BREAK,
        ReasonCode.INVALID_PIERCE,
        ReasonCode.RESET_NEW_ATH,
        ReasonCode.ATH_TOO_RECENT,
        ReasonCode.INSUFFICIENT_BARS,
        ReasonCode.NO_VALID_SECOND_ANCHOR,
        ReasonCode.SUSPECTED_UNADJUSTED_SPLIT,
        ReasonCode.INVALID_PRICE,
        ReasonCode.INVALID_INPUT,
    }
)

#: Codes the frozen-line layer owns.  Nothing before ``confirmed_bar`` may emit
#: one — asserted on RM-01 and on every golden fixture, where the first bar
#: carrying one of these must be exactly the engine-derived stop.
PHASE3_REASON_CODES: FrozenSet[ReasonCode] = frozenset(
    {
        ReasonCode.BREAKOUT_CONFIRMED,
        ReasonCode.FAILED_BREAKOUT,
        ReasonCode.RETEST_HELD,
        ReasonCode.EXPIRED_POST_BREAKOUT,
    }
)

assert PHASE2_REASON_CODES | PHASE3_REASON_CODES == frozenset(ReasonCode)
assert not (PHASE2_REASON_CODES & PHASE3_REASON_CODES)


@dataclass(frozen=True)
class TransitionRecord:
    """One replayable state-machine record (§21.6 event-record form, rule 4).

    ``INVALID_PIERCE`` is a *characterisation of the superseded line* rather than
    an event of its own, so it never appears as a record — it travels in the
    bar's reason-code set alongside that bar's ``WICK_BREAK`` record.
    """

    bar: int
    frm: LineState
    to: LineState
    reason: ReasonCode

    def as_tuple(self):
        return (self.bar, self.frm.value, self.to.value, self.reason.value)


class EngineDefect(AssertionError):
    """An internal invariant of §21 was violated.  Never caught, never softened."""


class PreconditionError(ValueError):
    """A caller defect: an input the specification assumes cannot occur (§1).

    Non-ascending or duplicated timestamps land here rather than becoming a
    reason code, because the reason-code set is closed by schema and minting a
    member is a product-definition change (plan §9.2 OQ-E, escalated).
    """
