"""§18 input guards — a whole-bar-set pre-pass.

Three conditions, and only these three (adding a fourth is a product-definition
change, plan §9.2 OQ-F, escalated rather than taken):

============================== ============================== ========
condition                       code                           fixture
============================== ============================== ========
a bar missing ``high``/``close`` ``INVALID_INPUT``              GX-18
any non-positive price          ``INVALID_PRICE``              GX-18
``|y[t]-y[t-1]| > ln(1.5)``     ``SUSPECTED_UNADJUSTED_SPLIT`` GX-10
============================== ============================== ========

All three **reject the bar-set**, before any geometry is fitted, so no
as-of-time line exists at any prefix.  This is the engine's one deliberately
non-causal element: it is confined to this pre-pass, it can only ever produce a
whole-series rejection, and the prefix-truncation property test carries an
explicit positive control for it rather than exempting it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .bars import BarSeries
from .logspace import ln_price
from .params import DetectorParams
from .state import LineState, ReasonCode, TransitionRecord

__all__ = ["GuardVerdict", "GuardRejection", "GuardObservation",
           "CorporateActions", "run_guards"]


@dataclass(frozen=True)
class CorporateActions:
    """Split-event evidence for one symbol (HD-27).

    ``splits`` maps a **bar index** to the split coefficient effective at that
    bar — 4.0 for a 4:1, 0.1 for a 1:10 reverse. Absent keys mean "no split".

    The presence of this object is itself evidence: with it the guard can tell a
    crash from an adjustment defect, and without it it cannot. That distinction
    is the whole of HD-27 and is why the type is optional rather than required.
    """

    symbol: str
    splits: Dict[int, float]

    def recorded_at(self, bar_index: int) -> Any:
        """The value the feed actually recorded, uncoerced — ``1.0`` if absent.

        Kept separate from :meth:`coefficient_at` so a rejection can name what
        the feed said (``'n/a'``, ``None``) rather than the ``nan`` it became.
        """
        return self.splits.get(bar_index, 1.0)

    def coefficient_at(self, bar_index: int) -> float:
        """The recorded value as a float, or ``nan`` when it is not one.

        A feed is a parsed vendor file, and vendor files carry ``None`` for a
        blank cell and ``'n/a'`` for an unknown one.  ``float()`` raises on both
        — ``TypeError`` and ``ValueError`` respectively — and that exception
        escaped ``detect()`` entirely, which is the same escape class as B2 one
        layer earlier: bad input crashing the caller instead of becoming a
        structured rejection.

        Uncoercible values become ``nan`` so they land on the "not a usable
        ratio" REJECT alongside 0, negatives and ``nan`` itself.  That is the
        same judgement for the same reason: ``ln`` is undefined on them, so
        there is no implied jump to compare against and no ground for saying
        the prices are already adjusted.  Coercion is *attempted* rather than
        type-checked, so a feed recording ``'2.0'`` still adjudicates as 2.0
        exactly as before — this widens no verdict, it only stops the crash.

        ``OverflowError`` is caught for the same reason and was initially
        missed: it subclasses ``ArithmeticError``, not ``TypeError`` or
        ``ValueError``, so ``{bar: 10**400}`` still escaped ``detect()`` after
        the first two were handled.  A JSON payload with a bare integer literal
        and no decimal point decodes to an arbitrary-precision ``int``, and
        ``float()`` on a large enough one raises.  **Reachable**: the pilot's
        provider coerces on the *fetch* path but its cache reader passes
        ``splits_applied`` straight out of JSON with no coercion, so a cache
        file carrying ``true`` or a 400-digit integer delivers exactly these
        values.  A first version of this docstring called it "latent, not live"
        on the strength of the fetch path alone; Code Review reproduced it
        through the cache path.  Fixed rather than documented as a caveat,
        because the paragraph above promised unconditionally that uncoercible
        values become ``nan``.

        A ``bool`` is deliberately treated as unusable rather than coerced.
        ``float(True)`` is ``1.0``, which the guard reads as *"no split at this
        bar"* and then emits evidence affirmatively denying a split occurred —
        a malformed feed value silently becoming a positive claim.  ``bool`` is
        not a ratio, and it is a type where successful coercion is worse than
        failure.  It is checked by type because that is the only way to catch
        it: unlike ``'n/a'``, it coerces cleanly.

        Not *the* one such type, which an earlier wording claimed: **any** object
        whose ``__float__`` returns 1.0 produces the same false "no split at
        this bar" claim and is not caught here.  Nothing in-product can supply
        one — A-2 restricts engine imports to a stdlib subset — so the check is
        deliberately narrow rather than a general "is this a plausible ratio"
        test, which would be the product-definition call this module keeps
        declining to take.
        """
        recorded = self.recorded_at(bar_index)
        if isinstance(recorded, bool):
            return float("nan")
        try:
            return float(recorded)
        except (TypeError, ValueError, OverflowError):
            return float("nan")


@dataclass(frozen=True)
class GuardObservation:
    """A large jump that was **inspected and accepted** as real market movement.

    Emitted rather than swallowed so that "the guard looked and decided this was
    a crash" is observable evidence rather than an absence. Without this, an
    accepted jump and a jump that was never tested look identical.
    """

    bar: int
    date: Any
    log_jump: float
    threshold: float
    split_coefficient: float
    verdict: str


@dataclass(frozen=True)
class GuardRejection:
    """Structured, observable reason for a whole-bar-set rejection (HD-27 §6).

    Every field the Product Owner named is present. A rejection must never be
    inferable only from ``final_state == NONE``.
    """

    symbol: Optional[str]
    bar: int
    date: Any
    reason: str
    log_jump: Optional[float] = None
    threshold: Optional[float] = None
    split_coefficient: Optional[float] = None
    evidence: str = ""

    def describe(self) -> str:
        parts = [f"{self.symbol or '<unknown>'} bar {self.bar}"]
        if self.date is not None:
            parts.append(f"({self.date})")
        parts.append(f"{self.reason}")
        if self.log_jump is not None:
            parts.append(f"log_jump={self.log_jump:.6f}")
        if self.threshold is not None:
            parts.append(f"threshold={self.threshold:.6f}")
        if self.split_coefficient is not None:
            parts.append(f"split_coefficient={self.split_coefficient}")
        if self.evidence:
            parts.append(f"— {self.evidence}")
        return " ".join(parts)


@dataclass(frozen=True)
class GuardVerdict:
    rejected: bool
    records: Tuple[TransitionRecord, ...]
    codes: Tuple[ReasonCode, ...]
    detail: Optional[Dict[str, Any]]
    #: Every rejection, structured. Empty when ``rejected`` is False.
    rejections: Tuple[GuardRejection, ...] = ()
    #: Large jumps inspected and **accepted** as genuine market movement.
    observations: Tuple[GuardObservation, ...] = ()

    @staticmethod
    def clean() -> "GuardVerdict":
        return GuardVerdict(False, (), (), None)


def _is_missing(value: Optional[float]) -> bool:
    return value is None


#: How close the observed jump must be to ``ln(coefficient)`` before a split is
#: judged to be the *cause* of it.
#:
#: The physics fixes the shape: if prices are unadjusted for a split of ratio
#: ``c``, then ``price[t]/price[t-1] == (1/c) * (1 + r)`` for that day's genuine
#: move ``r``, so the observed jump is ``|ln(c) - ln(1+r)|``.  The tolerance is
#: therefore a bound on ``|ln(1+r)|`` — how much real movement may ride on top of
#: a split before the match is abandoned.  0.15 admits roughly a ±16% same-day
#: move.
#:
#: **Which way this errs, stated rather than left to be discovered.**  Too WIDE
#: misattributes a crash as an adjustment defect and silences a real symbol —
#: the HD-27 defect itself.  Too NARROW lets a genuinely unadjusted split through
#: when the stock also moved hard that day.  HD-27 ruled that a legitimate crash
#: must remain valid market data, so this errs toward **accepting**: a missed
#: defect surfaces later as anomalous geometry, whereas a wrongly rejected symbol
#: produces nothing at all and looks like an absence of signal.
#:
#: **Pinned, not merely documented.**  ``ToleranceIsPinnedAtTheRulingsOwnCase``
#: in ``test_split_guard_hd27.py`` fails if this is widened past 0.157 — the
#: discrepancy of the 2.34x-drop-on-a-2:1 case HD-27 reasons about.  Before that
#: test the suite was green at every value from 0.031 to 0.47.
SPLIT_MATCH_TOLERANCE = 0.15


def _adjudicate_jump(
    signed_jump: float,
    bar_index: int,
    threshold: float,
    corporate_actions: Optional[CorporateActions],
) -> Tuple[str, Optional[float], str]:
    """Decide what a large log jump means. Returns ``(verdict, coefficient, evidence)``.

    ``signed_jump`` is ``y[t] - y[t-1]``, sign retained: the *direction* of the
    move is evidence and discarding it lets an up-move "match" a forward split.
    The magnitude is what the caller records; only this function needs the sign.

    HD-27's separation, in five cases:

    * **No split feed** — the two hypotheses are indistinguishable from prices
      alone, so the bar-set is rejected conservatively. This is the pre-HD-27
      behaviour and it is what keeps GX-10 (a synthetic 2:1 with no feed) green.
    * **Feed present, coefficient unusable** — non-finite, non-positive,
      non-numeric, **a boolean**, or **an integer too large to be a float** —
      is *absent evidence*, not a mismatch:
      ``ln`` is undefined on it and there is nothing to compare the jump
      against. Rejected on the same reasoning as no feed at all, and the
      evidence says so rather than claiming anything about adjustment.
      *(The last two are named separately because the first three words do not
      cover them, and this list twice described a branch its own code did not
      have. ``True`` is finite, positive and numeric — ``bool`` subclasses
      ``int``. ``10**400`` is finite, positive and numeric too; it is unusable
      only because ``float()`` raises ``OverflowError`` on it. Both words read
      against the RECORDED value, not the coerced coefficient. See
      ``coefficient_at``.)*
    * **Feed present, no split at this bar** — a real market event. **ACCEPT.**
      This is AAPL 2000-09-29: −51.9% on a profit warning, split coefficient 1.0.
    * **Feed present, split here, and the move matches the split in BOTH
      direction and magnitude** — a confirmed adjustment defect. **REJECT.**
    * **Feed present, split here, but the move does NOT match** — **ACCEPT**,
      because re-adjusting on an unmatched split would adjust twice. What is
      established is the mismatch itself; the cause of the move is not, and the
      evidence is worded to claim only the former. See the disclosure at the
      direction gate below: this accept-on-mismatch is what leaves an
      over-adjusted series undetected.

    This is still §18's single split condition, adjudicated; it is not a fourth
    whole-bar-set guard and it mints no new ``ReasonCode``.
    """
    if corporate_actions is None:
        return (
            "REJECT",
            None,
            "no corporate-action feed supplied; a crash and an unadjusted split "
            "are indistinguishable from prices alone, so the bar-set is rejected "
            "conservatively (HD-27)",
        )

    coefficient = corporate_actions.coefficient_at(bar_index)
    if not math.isfinite(coefficient) or coefficient <= 0.0:
        # UNUSABLE EVIDENCE, not a mismatch.  A feed encoding "unknown" as 0, a
        # blank cell parsed to NaN or to ``None``, an unknown one recorded as
        # ``'n/a'`` (both of the latter arrive here as NaN from
        # ``coefficient_at``), or a sign error yields something ``ln`` is not
        # defined on — so there is no implied jump to compare against and no
        # ground whatsoever for saying the prices are already adjusted.  Treating
        # it as a mismatch would ACCEPT a genuinely unadjusted split *and* assert
        # a reason that was never established.  HD-27 rules that where the
        # evidence is genuinely unavailable the safe direction is to reject, so
        # this lands in the same place as no feed at all.
        recorded = corporate_actions.recorded_at(bar_index)
        return (
            "REJECT",
            coefficient,
            f"the split coefficient recorded at this bar is {recorded!r}, which "
            f"is not a usable ratio (a coefficient must be finite and strictly "
            f"positive); with no usable coefficient a crash and an unadjusted "
            f"split are indistinguishable from prices alone, so the bar-set is "
            f"rejected conservatively (HD-27)",
        )

    if coefficient == 1.0:
        return (
            "ACCEPT",
            coefficient,
            "no split at this bar; genuine market movement preserved (HD-27)",
        )

    jump = abs(signed_jump)
    expected = abs(math.log(coefficient))
    # An unadjusted series moves by exactly 1/c across the split bar, so the
    # signed log change it would show is ``-ln(c)`` — NEGATIVE for a forward
    # split (2:1 unadjusted prices halve) and POSITIVE for a reverse split (1:10
    # unadjusted prices rise tenfold).  Magnitude alone cannot tell those apart
    # from their opposites, and 48 -> 96 on a 2:1 is not that split.
    expected_signed = -math.log(coefficient)
    #
    # **Which way this errs, stated rather than left to be discovered.**
    #
    # This gate ACCEPTS every same-magnitude opposite-direction move at a split
    # bar.  The consequence, named rather than left to be found: an
    # OVER-ADJUSTED series is no longer detected at all.  Over-adjustment is the
    # mirror vendor defect — prices that were already adjusted get adjusted
    # again, so every bar before the split is divided by ``c`` a second time and
    # the split bar carries a ``+ln(c)`` discontinuity instead of ``-ln(c)``.
    # That is exactly the shape this branch waves through.  Measured, on
    # ``[48, 47.5, 48, 48, 96, 97, 95, 96]`` with feed ``{4: 2.0}``: before this
    # gate the guard REJECTED it as "unadjusted for this split"; after it, the
    # guard ACCEPTS.
    #
    # ``c=10.0`` and the reverse mirror ``c=0.1`` behave the same way — and the
    # CONSTRUCTION has to be named, because the answer depends on it and two
    # successive versions of this comment each got it wrong by leaving it out:
    #
    # * **Coefficient-matched** (each ``c`` with ITS OWN over-adjusted series, so
    #   the jump is ``+ln c``: ``c=10`` with ``[48 ... 480]``, ``c=0.1`` with
    #   ``[100 ... 10]``).  This is what over-adjustment ACTUALLY IS for those
    #   coefficients, and it is the construction
    #   ``test_the_gap_is_the_same_at_other_coefficients_and_in_the_mirror``
    #   uses.  Measured: ``|jump - |ln c||`` is 0.000000 for all three, all three
    #   REJECTED before this gate and ACCEPT after.  **The gate flips all three.**
    # * **Fixed series, swapped coefficient** (keep ``[48 ... 96]`` and change
    #   only ``c``).  Then ``|jump - |ln c||`` is 1.609438 for ``c=10`` and
    #   ``c=0.1``, outside the 0.15 tolerance, so the magnitude test alone
    #   already accepted them and the gate changes nothing — it flips only
    #   ``c=2.0``.  But ``[48 ... 96]`` is not an over-adjusted series for
    #   ``c=10`` at all, so this construction does not exhibit the phenomenon.
    #
    # An earlier wording said "same for ``c=10.0`` and ``c=0.1``" without naming
    # a construction; a later one "corrected" it to "the gate flipped exactly one
    # of the three", which is true only of the construction that does not
    # exhibit over-adjustment. The first was right about the phenomenon and the
    # second was right about its own arithmetic. Naming the construction is the
    # fix; M-71 logs the pattern.
    #
    # This is a DETECTION GAP ACCEPTED DELIBERATELY, not an oversight.  A
    # ``+ln(c)`` step at a split bar is genuinely ambiguous — over-adjustment
    # and a real c-times move on the day produce an identical series — and HD-27
    # clause 2 plus the "err toward accepting" discipline behind
    # ``SPLIT_MATCH_TOLERANCE`` both point at accepting where the two hypotheses
    # cannot be separated.  Closing the gap would require a DISTINCT
    # over-adjustment hypothesis (its own evidence, its own verdict, plausibly
    # its own reason code), and no ruling has supplied one.  Inventing one here
    # would be a product-definition change, so it is escalated rather than
    # taken.  ``AnOverAdjustedSeriesIsAcceptedAndTheGapIsDisclosed`` in
    # ``test_split_guard_hd27.py`` pins the gap so it stays visible.
    if signed_jump * expected_signed <= 0.0:
        direction = "fall" if expected_signed < 0 else "rise"
        return (
            "ACCEPT",
            coefficient,
            f"a split of {coefficient} occurred here but the move is in the wrong "
            f"direction for an unadjusted series: unadjusted prices would "
            f"{direction} by {expected_signed:+.6f} in log space and the observed "
            f"change is {signed_jump:+.6f}. That direction mismatch is all that "
            f"was measured and no cause for the move is established; an "
            f"over-adjusted series carries this same shape (HD-27)",
        )

    if abs(jump - expected) <= SPLIT_MATCH_TOLERANCE:
        return (
            "REJECT",
            coefficient,
            f"split coefficient {coefficient} implies a log jump of {expected:.6f} "
            f"and the observed jump is {jump:.6f}; the series is unadjusted for "
            f"this split (HD-27)",
        )
    # The mismatch is measured; the CAUSE of it is not.  "Already adjusted" is
    # the ordinary explanation and is worth naming, but it is a hypothesis this
    # branch never tested — and a finite-but-absurd coefficient can reach here
    # and mismatch by construction, where asserting the prices are already
    # adjusted is no better established than it was for the ``nan`` case B2
    # fixed.  WHICH absurd coefficient reaches here depends on the SIGN of the
    # jump, not on how large ``|ln c|`` is: on a downward jump ``1e12`` arrives
    # here while ``1e-12`` and ``5e-324`` exit at the direction gate above; on an
    # upward jump that inverts exactly.  ``|ln 1e-12|`` and ``|ln 1e12|`` are the
    # same number (27.631021), so magnitude cannot be what separates them.  So the evidence reports the mismatch and stops.
    # No plausibility threshold is applied: bounding what counts as a credible
    # coefficient would be a product-definition change, not a wording fix.
    return (
        "ACCEPT",
        coefficient,
        f"a split of {coefficient} occurred here but the observed jump "
        f"{jump:.6f} does not match its implied {expected:.6f}; a mismatch of "
        f"this size is what already adjusted prices look like, but the mismatch "
        f"is all that was measured and no cause for the move is established. "
        f"Accepted because re-adjusting on an unmatched split would adjust "
        f"twice (HD-27)",
    )


def run_guards(
    series: BarSeries,
    params: DetectorParams,
    corporate_actions: Optional[CorporateActions] = None,
) -> GuardVerdict:
    """Evaluate §18's three whole-bar-set guards over the delivered series.

    Records are emitted in bar order; within a bar, ``INVALID_INPUT`` precedes
    ``INVALID_PRICE`` because a missing field cannot then be tested for
    positivity.  A bar whose ``high`` is missing or non-positive is excluded from
    the split-jump scan for the same reason.

    ``corporate_actions`` supplies the split-event evidence HD-27 requires. When
    it is ``None`` the split guard falls back to the pre-HD-27 jump-only rule —
    not as a convenience, but because without a feed the two hypotheses are
    genuinely indistinguishable and rejecting is the safe direction.
    """
    records: List[TransitionRecord] = []
    codes: List[ReasonCode] = []
    detail: Optional[Dict[str, Any]] = None
    rejections: List[GuardRejection] = []
    observations: List[GuardObservation] = []
    symbol = corporate_actions.symbol if corporate_actions is not None else None

    def emit(bar_index: int, code: ReasonCode) -> None:
        records.append(TransitionRecord(bar_index, LineState.NONE, LineState.NONE, code))
        if code not in codes:
            codes.append(code)

    usable_high: Dict[int, float] = {}

    for bar in series:
        if _is_missing(bar.high) or _is_missing(bar.close):
            # §18 row "a bar missing high or close is invalid input".
            emit(bar.t, ReasonCode.INVALID_INPUT)
            missing = [n for n in ("high", "close") if getattr(bar, n) is None]
            rejections.append(
                GuardRejection(
                    symbol=symbol,
                    bar=bar.t,
                    date=bar.timestamp,
                    reason="INVALID_INPUT",
                    evidence=f"missing required field(s): {', '.join(missing)} (§18)",
                )
            )
            continue
        non_positive = [
            name for name, value in bar.prices() if value is not None and value <= 0
        ]
        if non_positive:
            # §1 positivity / §18 row "Non-positive price -> reject bar-set".
            emit(bar.t, ReasonCode.INVALID_PRICE)
            rejections.append(
                GuardRejection(
                    symbol=symbol,
                    bar=bar.t,
                    date=bar.timestamp,
                    reason="INVALID_PRICE",
                    evidence=f"non-positive price in field(s): {', '.join(non_positive)} (§1/§18)",
                )
            )
            continue
        usable_high[bar.t] = float(bar.high)

    # §18 split guard, on the HIGH series (the field that feeds y, §3).
    previous_index: Optional[int] = None
    for bar in series:
        if bar.t not in usable_high:
            previous_index = None
            continue
        if previous_index is not None and previous_index == bar.t - 1:
            # The SIGN is carried into adjudication (an up-move is not a forward
            # split) but the MAGNITUDE is what the threshold tests and what the
            # recorded ``log_jump`` fields mean, unchanged.
            signed_jump = (
                ln_price(usable_high[bar.t]) - ln_price(usable_high[previous_index])
            )
            jump = abs(signed_jump)
            if jump > params.split_log_jump_threshold:
                # HD-27: a large jump TRIGGERS INSPECTION. It does not, on its
                # own, invalidate the symbol. What decides the verdict is
                # split-event evidence.
                verdict, coefficient, evidence = _adjudicate_jump(
                    signed_jump, bar.t, params.split_log_jump_threshold,
                    corporate_actions,
                )
                if verdict == "REJECT":
                    emit(bar.t, ReasonCode.SUSPECTED_UNADJUSTED_SPLIT)
                    rejections.append(
                        GuardRejection(
                            symbol=symbol,
                            bar=bar.t,
                            date=bar.timestamp,
                            reason="SUSPECTED_UNADJUSTED_SPLIT",
                            log_jump=jump,
                            threshold=params.split_log_jump_threshold,
                            split_coefficient=coefficient,
                            evidence=evidence,
                        )
                    )
                    if detail is None:
                        detail = {"bar": bar.t, "log_jump": jump}
                else:
                    # Accepted as real market movement. Recorded, never silent —
                    # an accepted jump and an untested one must not look alike.
                    observations.append(
                        GuardObservation(
                            bar=bar.t,
                            date=bar.timestamp,
                            log_jump=jump,
                            threshold=params.split_log_jump_threshold,
                            split_coefficient=coefficient,
                            verdict=evidence,
                        )
                    )
        previous_index = bar.t

    records.sort(key=lambda record: (record.bar, _CODE_ORDER[record.reason]))
    # Reduce `codes` from the sorted records so the list is genuinely in
    # first-emission order rather than in pass order.
    codes = []
    for record in records:
        if record.reason not in codes:
            codes.append(record.reason)
    rejections.sort(key=lambda r: r.bar)
    return GuardVerdict(
        bool(records),
        tuple(records),
        tuple(codes),
        detail,
        tuple(rejections),
        tuple(observations),
    )


_CODE_ORDER = {
    ReasonCode.INVALID_INPUT: 0,
    ReasonCode.INVALID_PRICE: 1,
    ReasonCode.SUSPECTED_UNADJUSTED_SPLIT: 2,
}
