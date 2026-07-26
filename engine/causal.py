"""§21.2 — the as-of-time evaluation fold.  This is the heart of the engine.

The single invariant, in the specification's own words (§21.6): **"The
evaluation bar MUST NEVER redefine the line against which its own event is
judged."**

Three structural mechanisms make that a property of the code rather than
something the tests must police:

1. **The batch API *is* the streaming API.**  :func:`run` is a left fold over
   bars; there is no separate batch path, so "streaming equals batch" is true by
   construction.  (Which also makes §21.8.3's operational test *vacuous* — said
   out loud here, because a test that cannot fail is exactly the failure mode
   this repository keeps repeating.  Prefix-truncation invariance replaces it,
   and that one can fail.)
2. **No geometry function ever receives the series.**  :func:`_seal` hands
   :mod:`engine.formation` a :class:`~engine.bars.Prefix` of length exactly
   ``t``.  The evaluation bar arrives as a separate argument and is never
   appended before evaluation.
3. **The line that judges bar ``t`` is sealed before bar ``t`` is read**, and
   ``Prefix``'s constructor asserts its own length, so an off-by-one that leaked
   ``H[t]`` into ``Λ_t`` is an assertion failure, not a subtly wrong number.

Per-bar order (§21.2, §21.6 rule 2):

===  ==========================================================================
 a   emit line records attributable to bar ``t`` — ``LINE_ESTABLISHED``,
     ``ENVELOPE_TIE_LATER``, or the head-of-run ``NONE`` reason.  Line records
     always precede the bar's own event records.
 b   **new-ATH test first** — takes precedence over the breakout predicate and
     over the roll (§21.2 rule 5).  ``H[t] == HA`` is *not* a new ATH (D-TL-02).
 c   if ``Λ_t = ⊥`` no event test may run — "a bar that cannot be evaluated MUST
     NOT be evaluated later" (§21.3).
 d   otherwise judge bar ``t`` against ``Λ_t``: the §13.1 breakout predicate
     (→ **stop**), else the §10.1 pierce (→ ``INVALID_PIERCE`` in the bar's code
     set and a ``WICK_BREAK`` record, §14).
 e   seal for ``t+1``: append ``y[t]``, recompute over ``S_{t+1}``, register any
     re-selection **effective at ``t+1``**.  *No line ever takes effect on the
     bar that caused it to be computed* (§17).
===  ==========================================================================

**Phase-2 scope.**  §13.1's predicate must exist here or §14 is not definable
(its second conjunct is the negated predicate) and §21.2 step 4 is not
implementable (the roll is conditioned on "no confirmed breakout").  The
predicate is all that exists: there is no ``BREAKOUT_CONFIRMED`` code, no
``ACTIVE → BROKEN_OUT`` transition and no ``BROKEN_OUT`` state.  The episode
**halts** at the first bar where the predicate holds, returning the line that
was active at the start of that bar as ``line_at_stop``.  Retaining it as
``Λ^F`` and suspending re-selection is §21.5's act, and Phase 3's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .bars import BarSeries, Prefix
from .formation import GateVerdict, evaluate_formation
from .envelope import Selection
from .logspace import exceeds, line_price, ln_price, log_intercept, log_slope, y_hat
from .params import DetectorParams
from .state import EngineDefect, LineState, ReasonCode, TransitionRecord

__all__ = ["Line", "SealedBar", "Reselection", "BarEvent", "StopRecord", "CausalResult", "run"]


#: States that carry a line and can therefore be *retired* by a new ATH.
#:
#: AMBIGUITY, resolved here: §21.7 says a new ATH invalidates "the previous
#: structure" and enumerates the states it applies to as ACTIVE, BROKEN_OUT and
#: RETESTED — ``NONE`` is not among them, and §11's machine has no
#: ``NONE -> NONE`` new-ATH edge.  So ``RESET_NEW_ATH`` is emitted only when a
#: line-bearing state is actually retired.  A new high while the state is
#: ``NONE`` still moves the as-of-time anchor (that is automatic, the anchor
#: being a pure function of the prefix); it simply records no reset, because
#: there was no structure to invalidate.  RM-01 exercises this at bars 1 and 2
#: and its committed record asserts no transition there either way.
#: Phase 3 adds ``BROKEN_OUT`` and ``RETESTED`` to this tuple.
_LINE_BEARING = (LineState.ACTIVE,)


@dataclass(frozen=True)
class Line:
    """``Λ_t`` — the line active at the start of a bar (§21.1)."""

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


@dataclass(frozen=True)
class SealedBar:
    """Everything about bar ``t`` that was decided before bar ``t`` was read."""

    t: int
    verdict: GateVerdict
    state: LineState
    line: Optional[Line]

    @property
    def selection(self) -> Optional[Selection]:
        return self.verdict.selection


@dataclass(frozen=True)
class Reselection:
    effective_bar: int
    frm: int
    to: int
    m: float
    tie: bool


@dataclass(frozen=True)
class BarEvent:
    bar: int
    event: ReasonCode
    detail: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StopRecord:
    """The first bar at which §13.1's predicate held, and the line that judged it.

    ``line`` is ``Λ_stop`` — the line active while the structure was still
    ``ACTIVE``, which Phase 2 computes anyway.  It is deliberately **not** named
    ``Λ^F``: freezing is §21.5's act and Phase 3's.
    """

    bar: int
    line: Line
    y_hat: float
    line_value: float
    close: float
    ln_close: float
    #: ``ln(close) - y_hat`` — the RAW clearance over the line.
    clearance: float
    #: ``ln(close) - (y_hat + eps_break)`` — the same quantity net of eps_break.
    clearance_net_of_eps_break: float


@dataclass
class CausalResult:
    bars_evaluated: int
    sealed: Tuple[SealedBar, ...]
    transitions: Tuple[TransitionRecord, ...]
    reason_codes: Tuple[ReasonCode, ...]
    reselections: Tuple[Reselection, ...]
    events: Tuple[BarEvent, ...]
    stop: Optional[StopRecord]
    final_state: Optional[LineState]
    t_form: Optional[int]
    reported_line: Optional[Line]
    reported_anchor: Optional[Tuple[int, float]]

    def sealed_at(self, t: int) -> Optional[SealedBar]:
        for sealed in self.sealed:
            if sealed.t == t:
                return sealed
        return None


def _seal(prefix: Prefix, params: DetectorParams) -> SealedBar:
    """Compute ``Λ_t`` and its formation verdict from ``S_t`` alone."""
    verdict = evaluate_formation(prefix, params)
    if not verdict.eligible:
        return SealedBar(t=prefix.length, verdict=verdict, state=LineState.NONE, line=None)

    anchor = verdict.anchor
    selection = verdict.selection
    if anchor is None or selection is None or selection.selected is None:
        raise EngineDefect("eligible verdict without an anchor and a B* (§21.3)")
    chosen = selection.selected
    m = log_slope(chosen.y, anchor.y, chosen.t, anchor.t)
    b = log_intercept(anchor.y, m, anchor.t)
    line = Line(
        t_anchor=anchor.t,
        high_anchor=anchor.high,
        y_anchor=anchor.y,
        t_b=chosen.t,
        high_b=chosen.high,
        m=m,
        b=b,
    )
    return SealedBar(t=prefix.length, verdict=verdict, state=LineState.ACTIVE, line=line)


def run(series: BarSeries, params: DetectorParams) -> CausalResult:
    """Fold §21.2's per-bar order over the series.

    The caller must have run the §18 guards first; this function assumes every
    ``high`` and ``close`` is present and positive.
    """
    bar_count = len(series)

    prefix = Prefix.empty()
    sealed_bars: List[SealedBar] = []
    transitions: List[TransitionRecord] = []
    codes: List[ReasonCode] = []
    reselections: List[Reselection] = []
    events: List[BarEvent] = []

    current_state = LineState.NONE
    run_reason: Optional[ReasonCode] = None
    run_start: Optional[int] = None
    previous_sealed: Optional[SealedBar] = None
    stop: Optional[StopRecord] = None
    t_form: Optional[int] = None

    def emit(bar_index: int, to: LineState, reason: ReasonCode) -> None:
        nonlocal current_state
        transitions.append(TransitionRecord(bar_index, current_state, to, reason))
        current_state = to
        if reason not in codes:
            codes.append(reason)

    def note_code(reason: ReasonCode) -> None:
        """A reason code that characterises the bar but is not its own record
        (§21.6 event-record form, rule 4)."""
        if reason not in codes:
            codes.append(reason)

    for t in range(bar_count):
        bar = series[t]
        if bar.high is None or bar.close is None:  # pragma: no cover - guarded upstream
            raise EngineDefect("run() reached a bar the §18 guards should have rejected")

        sealed = _seal(prefix, params)
        if sealed.t != t:
            raise EngineDefect(
                "sealed state for bar %d was built from a prefix of length %d (§21.1)"
                % (t, sealed.t)
            )
        sealed_bars.append(sealed)
        if t_form is None and sealed.state is LineState.ACTIVE:
            t_form = t

        previous_state = previous_sealed.state if previous_sealed is not None else LineState.NONE
        previous_line = previous_sealed.line if previous_sealed is not None else None

        # ---- (a) line records attributable to bar t ------------------------
        if sealed.state is LineState.ACTIVE:
            assert sealed.line is not None
            changed = (
                previous_state is not LineState.ACTIVE
                or previous_line is None
                or previous_line.identity != sealed.line.identity
            )
            if changed:
                emit(t, LineState.ACTIVE, ReasonCode.LINE_ESTABLISHED)
                selection = sealed.selection
                if selection is not None and selection.tie:
                    emit(t, LineState.ACTIVE, ReasonCode.ENVELOPE_TIE_LATER)
                if previous_state is LineState.ACTIVE and previous_line is not None:
                    reselections.append(
                        Reselection(
                            effective_bar=t,
                            frm=previous_line.t_b,
                            to=sealed.line.t_b,
                            m=sealed.line.m,
                            tie=bool(selection is not None and selection.tie),
                        )
                    )
            elif current_state is not LineState.ACTIVE:
                # §21.6 rule 3: the emitted sequence must be a valid walk of
                # §11, so the state may never change without a record.
                raise EngineDefect(
                    "bar %d is ACTIVE with an unchanged line but the running "
                    "state is %s (§21.6 rule 3)" % (t, current_state.value)
                )
            run_reason = None
            run_start = None
        else:
            reason = sealed.verdict.reason
            if reason is None:  # pragma: no cover - impossible by construction
                raise EngineDefect("ineligible verdict without a reason code (§21.3)")
            if current_state is not LineState.NONE:
                run_start = t
                run_reason = None
            if run_start is None:
                run_start = t
            if reason is not run_reason:
                run_reason = reason
                suppressed = (
                    reason is ReasonCode.INSUFFICIENT_BARS and run_start == 0
                )
                if suppressed:
                    # §21.3: "a run whose reason is merely INSUFFICIENT_BARS at
                    # the head of a series is not recorded as an event at all"
                    # — every series begins short, so the record would carry no
                    # information.
                    current_state = LineState.NONE
                else:
                    emit(t, LineState.NONE, reason)
            else:
                current_state = LineState.NONE

        # ---- (b) new-ATH test, BEFORE the breakout predicate and the roll ---
        anchor = sealed.verdict.anchor
        high = float(bar.high)
        if anchor is not None and high > anchor.high:  # `==` is NOT a new ATH (D-TL-02)
            if current_state in _LINE_BEARING:
                prior = current_state
                emit(t, LineState.NONE, ReasonCode.RESET_NEW_ATH)
                events.append(
                    BarEvent(t, ReasonCode.RESET_NEW_ATH, {"prior_state": prior.value})
                )
                run_reason = None
                run_start = None
            prefix = prefix.extended(ln_price(high), high)
            previous_sealed = sealed
            continue

        # ---- (c)/(d) judge bar t against Λ_t --------------------------------
        if sealed.state is LineState.ACTIVE and sealed.line is not None:
            line = sealed.line
            y_hat_value = line.y_hat_at(t)
            close = float(bar.close)
            ln_close = ln_price(close)
            ln_high = ln_price(high)

            if exceeds(ln_close, y_hat_value, params.eps_break):
                # §13.1 predicate holds.  Phase 2 halts here; the transition,
                # its reason code and everything downstream are Phase 3's.
                stop = StopRecord(
                    bar=t,
                    line=line,
                    y_hat=y_hat_value,
                    line_value=line.price_at(t),
                    close=close,
                    ln_close=ln_close,
                    clearance=ln_close - y_hat_value,
                    clearance_net_of_eps_break=ln_close - (y_hat_value + params.eps_break),
                )
                previous_sealed = sealed
                break

            if exceeds(ln_high, y_hat_value, params.eps):
                # §10.1 structural pierce.  The close did not confirm (we are in
                # the else branch), so §14's second conjunct holds and the bar is
                # a wick-break: ACTIVE -> ACTIVE, plus INVALID_PIERCE for the
                # superseded line carried in the code set (§21.6 rule 4).
                emit(t, LineState.ACTIVE, ReasonCode.WICK_BREAK)
                note_code(ReasonCode.INVALID_PIERCE)
                events.append(
                    BarEvent(
                        t,
                        ReasonCode.WICK_BREAK,
                        {
                            "y_hat": y_hat_value,
                            "high": high,
                            "ln_high": ln_high,
                            "pierce": ln_high - y_hat_value,
                            "close": close,
                            "close_margin": ln_close - (y_hat_value + params.eps_break),
                        },
                    )
                )

        # ---- (e) seal for t+1 ----------------------------------------------
        prefix = prefix.extended(ln_price(high), high)
        previous_sealed = sealed

    reported_line: Optional[Line]
    reported_anchor: Optional[Tuple[int, float]]
    final_state: Optional[LineState]

    if stop is not None:
        reported_line = stop.line
        reported_anchor = (stop.line.t_anchor, stop.line.high_anchor)
        final_state = None  # the state at and after the stop is Phase 3's
    else:
        # Λ_n — the line in force after the last available bar (§21.4, "the line
        # a detector REPORTS").  Sealing at t = n is the same pure computation
        # as any other bar's; it judges a hypothetical next bar.
        tail = _seal(prefix, params)
        sealed_bars.append(tail)
        reported_line = tail.line
        reported_anchor = (
            None if tail.verdict.anchor is None
            else (tail.verdict.anchor.t, tail.verdict.anchor.high)
        )
        final_state = current_state

    return CausalResult(
        bars_evaluated=(stop.bar + 1 if stop is not None else bar_count),
        sealed=tuple(sealed_bars),
        transitions=tuple(transitions),
        reason_codes=tuple(codes),
        reselections=tuple(reselections),
        events=tuple(events),
        stop=stop,
        final_state=final_state,
        t_form=t_form,
        reported_line=reported_line,
        reported_anchor=reported_anchor,
    )
