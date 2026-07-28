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
   appended before evaluation.  The post-breakout predicates in
   :mod:`engine.frozen` receive a :class:`~engine.frozen.FrozenLine` and one
   bar's numbers — never the series, never a prefix.
3. **The line that judges bar ``t`` is sealed before bar ``t`` is read**, and
   ``Prefix``'s constructor asserts its own length, so an off-by-one that leaked
   ``H[t]`` into ``Λ_t`` is an assertion failure, not a subtly wrong number.

Per-bar order (§21.2, §21.6 rule 2, §5.3 of the Phase-3 design):

===  ==========================================================================
 a   emit line records attributable to bar ``t`` — ``LINE_ESTABLISHED``,
     ``ENVELOPE_TIE_LATER``, or the head-of-run ``NONE`` reason.  Line records
     always precede the bar's own event records.  **Suspended while a frozen
     line governs** (§21.5): this is one of the two mechanisms that stop
     re-selection.
 b   **new-ATH test first** — takes precedence over the breakout predicate and
     over the roll (§21.2 rule 5).  ``H[t] == HA`` is *not* a new ATH (D-TL-02).
     It retires ``ACTIVE``, ``BROKEN_OUT``, ``RETESTED`` **and**
     ``FAILED_BREAKOUT`` alike (§21.7 as amended by HD-25; the
     ``BROKEN_OUT``/``RETESTED`` edge was added to §11's diagram on 2026-07-28).
 c   if ``Λ_t = ⊥`` no event test may run — "a bar that cannot be evaluated MUST
     NOT be evaluated later" (§21.3).
 d   while ``ACTIVE``, judge bar ``t`` against ``Λ_t``: the §13.1 breakout
     predicate (→ ``BREAKOUT_CONFIRMED``, freeze ``Λ^F``, → ``BROKEN_OUT``),
     else the §10.1 pierce (→ ``INVALID_PIERCE`` in the bar's code set and a
     ``WICK_BREAK`` record, §14).
 e   while a frozen line governs, judge bar ``t`` against ``Λ^F`` in this order:
     §15 failure, §16 retest, §17 expiry.
 f   seal for ``t+1``: append ``y[t]``, recompute over ``S_{t+1}``, register any
     re-selection **effective at ``t+1``**.  *No line ever takes effect on the
     bar that caused it to be computed* (§17).  The append itself always runs —
     the prefix must keep growing while an episode is open so that §17's
     post-expiry recomputation sees the **whole** grown prefix (OQ-P3-6).
===  ==========================================================================

**Within-bar precedence in step (e), and why that order.**  §16 condition 3 says
"no structural failure (§15) during the window", so failure is tested first; it
is fixture-forced by GX-12 at the 0.5× sweep scale, where a failure at bar 18
pre-empts a hold that would otherwise have arrived at bar 19.  §21.8 rule 2
independently forbids the alternative, which would hold bar 18's classification
open until a later bar.  Expiry is last; at the documented defaults its window
(``t − breakout ≥ 100``) is disjoint from the other two (``≤ 10`` and ``≤ 20``),
so the order is formally rather than materially load-bearing — but the six
parameters are backtestable and a configuration with ``E_expiry ≤ W_retest``
would reach it.

**Two episodes, and the two bar indices that are NOT the same quantity.**
``StopRecord`` is the **first** bar at which §13.1's predicate held in the whole
series — Phase 2's engine-derived stop, which RM-01's B-clause asserts against.
``confirmed_bar`` is the **latest** episode's freeze bar, because §21.4 (OQ-P3-5,
ruled 2026-07-28) makes the latest episode supply the reported ``Λ^F`` and
``confirmed_bar``.  They coincide on every committed fixture — none has two
episodes — and they are kept distinct anyway, because an engine that encoded the
alias would be wrong on the first two-episode series it met.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .bars import BarSeries, Prefix
from .formation import GateVerdict, evaluate_formation
from .envelope import Selection
from .frozen import (
    Challenger,
    FrozenLine,
    HoldWindow,
    challengers_over,
    earliest_open_window,
    expired_at,
    failed_breakout_at,
    in_return_window,
    open_hold_windows,
    retest_hold_at,
    retest_return_at,
)
from .line import Line
from .logspace import exceeds, ln_price, log_intercept, log_slope
from .params import DetectorParams
from .state import EngineDefect, LineState, ReasonCode, TransitionRecord

__all__ = [
    "Line",
    "SealedBar",
    "Reselection",
    "BarEvent",
    "StopRecord",
    "CausalResult",
    "run",
]


#: States that carry a line and can therefore be *retired* by a new ATH.
#:
#: §21.7 as amended by HD-25 (Product Owner, 2026-07-28) applies the reset to
#: ``ACTIVE``, ``BROKEN_OUT``, ``RETESTED`` **and** ``FAILED_BREAKOUT``: the last
#: is episode-terminal, not name-terminal, and under the superseded reading the
#: first failed breakout in a name's history silenced that name permanently.
#: §11's diagram omitted the ``BROKEN_OUT``/``RETESTED`` edge until 2026-07-28
#: although §21.5 and §21.7 both drew it; it is now drawn, so the transition this
#: tuple produces is a legal walk of §11.
#:
#: ``NONE`` is NOT a member, and that reading is ratified rather than
#: discretionary.  §11's machine has no ``NONE -> NONE`` new-ATH edge, so
#: ``RESET_NEW_ATH`` is emitted only when a line-bearing state is actually
#: retired.  A new high while the state is ``NONE`` still moves the as-of-time
#: anchor — that is automatic, the anchor being a pure function of the prefix —
#: it simply records no reset, because there was no structure to invalidate.
#:
#: The two readings are behaviourally identical on **23 of the 24** committed
#: fixtures.  **RM-01 is the one that separates them**: setting
#: ``_LINE_BEARING = (ACTIVE, NONE)`` adds four ``NONE -> NONE`` transitions at
#: bars 1-3 (``RESET_NEW_ATH`` at 1 and 2, ``INSUFFICIENT_BARS`` at 2 and 3), and
#: those records land inside the head-of-series run that §21.3 says must "not be
#: recorded as an event at all".  Measured independently by the Verification and
#: Code Review gates, which ruled this reading CORRECT and RATIFIED.
#:
#: What remains true, and is the useful claim: **no committed expectation
#: distinguishes them.**  RM-01's ``expected-causal.json`` carries no ``events``
#: or ``reason_codes`` key, so every conformance test passes under either
#: reading.  Nothing here is load-bearing for conformance; it is load-bearing for
#: what the engine would do on a series the corpus lacks.
_LINE_BEARING = (
    LineState.ACTIVE,
    LineState.BROKEN_OUT,
    LineState.RETESTED,
    LineState.FAILED_BREAKOUT,
)

#: The states a frozen line governs (§21.5, extended to ``FAILED_BREAKOUT`` by
#: HD-25).  While the effective state is one of these, §21.2 step 4 does not run
#: and no later high may replace ``B*``.
_FROZEN_REGIME = (
    LineState.BROKEN_OUT,
    LineState.RETESTED,
    LineState.FAILED_BREAKOUT,
)


@dataclass(frozen=True)
class SealedBar:
    """Everything about bar ``t`` that was decided before bar ``t`` was read.

    ``state`` is **gate arithmetic over ``S_t``**, not the effective state: it
    reads ``ACTIVE`` on post-breakout bars whose three gates happen to pass.
    GX-04's own ``gate_trace_full_caveat`` says exactly that.  The effective
    state is :attr:`CausalResult.state_at_start`.
    """

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
    """The FIRST bar at which §13.1's predicate held, and the line that judged it.

    ``line`` is the line that was active while the structure was still
    ``ACTIVE``.  Phase 3 **freezes this very object** as ``Λ^F`` — see
    :class:`~engine.frozen.FrozenLine` — rather than recomputing it: the fold
    asserts ``frozen.line is stop.line`` by object identity, so the quantity
    RM-01's B-clause asserts (``line_at_stop``) and the quantity the golden
    fixtures assert (``causal_record.frozen_event_line``) cannot drift apart.
    The name is retained because it is Phase 2's, and because on a series with
    more than one episode the *first* stop and the *reported* ``confirmed_bar``
    are different bars (§21.4, OQ-P3-5).
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
    #: The effective state at the START of each evaluated bar — after that bar's
    #: line record, before its own event records.  This is the quantity
    #: ``causal_record.active_line_before_event_bars[].state_at_start`` records:
    #: GX-04's bar 8 is ``ACTIVE`` although the record at bar 8 is
    #: ``NONE -> ACTIVE``, because the line is established in step (a) and the
    #: bar is then judged under it.
    state_at_start: Tuple[LineState, ...] = ()
    #: The line each bar was judged against: ``Λ_t`` while ``ACTIVE``, ``Λ^F``
    #: while a frozen line governs, ``None`` while ``NONE``.
    governing: Tuple[Optional[Line], ...] = ()
    #: ``Λ^F`` of the LATEST episode that confirmed a breakout, or ``None``.
    frozen: Optional[FrozenLine] = None
    #: Every episode's ``Λ^F``, in order.  ``frozen`` is the last of them
    #: (§21.4, OQ-P3-5) and ``stop`` belongs to the first.  The corpus has no
    #: series with two, so this tuple is what makes the distinction observable
    #: at all; the property suite's random corpus does produce them.
    episodes: Tuple[FrozenLine, ...] = ()
    #: Post-breakout highs a full-series hull would have re-selected, and which
    #: §21.5 forbade.  Reporting only.
    challengers: Tuple[Challenger, ...] = ()

    def sealed_at(self, t: int) -> Optional[SealedBar]:
        for sealed in self.sealed:
            if sealed.t == t:
                return sealed
        return None

    def state_at(self, t: int) -> Optional[LineState]:
        if 0 <= t < len(self.state_at_start):
            return self.state_at_start[t]
        return None

    def governing_at(self, t: int) -> Optional[Line]:
        if 0 <= t < len(self.governing):
            return self.governing[t]
        return None


def _seal(prefix: Prefix, params: DetectorParams) -> SealedBar:
    """Compute ``Λ_t`` and its formation verdict from ``S_t`` alone.

    Note what this function does **not** carry: no memory of a previous episode.
    ``select_second_anchor`` recomputes §8 over the whole prefix on every bar, so
    §21.4's running-maximum Lemma is never *seeded* across an episode boundary —
    which is what OQ-P3-6 requires of the post-expiry re-formation.  The Lemma is
    an optimization this engine deliberately does not take on the production
    path; it lives in the test suite as an independently written oracle.
    """
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
    ``high`` and ``close`` is present and positive.  ``low`` is **not** assumed:
    §18 does not guard it, and a bar reaching a §16 return predicate without one
    raises a :class:`~engine.state.PreconditionError` (ESC-5(a)).
    """
    bar_count = len(series)

    prefix = Prefix.empty()
    sealed_bars: List[SealedBar] = []
    transitions: List[TransitionRecord] = []
    codes: List[ReasonCode] = []
    reselections: List[Reselection] = []
    events: List[BarEvent] = []
    state_at_start: List[LineState] = []
    governing: List[Optional[Line]] = []

    current_state = LineState.NONE
    run_reason: Optional[ReasonCode] = None
    run_start: Optional[int] = None
    previous_sealed: Optional[SealedBar] = None
    stop: Optional[StopRecord] = None
    t_form: Optional[int] = None

    #: ``Λ^F`` of the episode currently open, cleared when the episode ends.
    active_frozen: Optional[FrozenLine] = None
    #: ``Λ^F`` of the LATEST episode that fired, retained after the episode ends
    #: by either exit (§21.4, OQ-P3-4/OQ-P3-5) — this is what the detector
    #: reports.
    reported_frozen: Optional[FrozenLine] = None
    episodes: List[FrozenLine] = []
    hold_windows: List[HoldWindow] = []

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

    def end_episode() -> None:
        """Retire ``Λ^F`` for the open episode.  The *reported* line survives."""
        nonlocal active_frozen, run_reason, run_start
        active_frozen = None
        hold_windows.clear()
        run_reason = None
        run_start = None

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

        frozen_now = current_state in _FROZEN_REGIME
        previous_state = previous_sealed.state if previous_sealed is not None else LineState.NONE
        previous_line = previous_sealed.line if previous_sealed is not None else None

        # ---- (a) line records attributable to bar t ------------------------
        # Suspended entirely while a frozen line governs (§21.5): mechanism 1 of
        # the two that stop re-selection.  Mechanism 2 is the type of the
        # argument the §15/§16/§17 predicates accept.
        if frozen_now:
            pass
        elif sealed.state is LineState.ACTIVE:
            assert sealed.line is not None
            # ``current_state`` here is the EFFECTIVE state carried in from the
            # previous bar, before this bar records anything.  It is part of the
            # test because an episode that has just ended leaves the state at
            # ``NONE`` while the gate arithmetic in ``previous_sealed`` still
            # says ``ACTIVE``: the line that forms next is a **formation**, and
            # it must be recorded as one.
            entry_state = current_state
            changed = (
                previous_state is not LineState.ACTIVE
                or previous_line is None
                or previous_line.identity != sealed.line.identity
                or entry_state is not LineState.ACTIVE
            )
            if changed:
                emit(t, LineState.ACTIVE, ReasonCode.LINE_ESTABLISHED)
                selection = sealed.selection
                if selection is not None and selection.tie:
                    emit(t, LineState.ACTIVE, ReasonCode.ENVELOPE_TIE_LATER)
                if (
                    entry_state is LineState.ACTIVE
                    and previous_state is LineState.ACTIVE
                    and previous_line is not None
                    and previous_line.identity != sealed.line.identity
                ):
                    # A pre-breakout ROLL (§21.6), which is an ACTIVE -> ACTIVE
                    # record.  A formation and a post-expiry re-formation are
                    # NONE -> ACTIVE and are not re-selections, however much the
                    # geometry moved.
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

        # The effective state under which bar t is judged, and the line that
        # judges it.  Recorded before any of the bar's own event records.
        state_at_start.append(current_state)
        if current_state in _FROZEN_REGIME:
            if active_frozen is None:  # pragma: no cover - defended, not expected
                raise EngineDefect(
                    "bar %d is in the frozen regime with no Λ^F (§21.5)" % t
                )
            governing.append(active_frozen.line)
        elif current_state is LineState.ACTIVE:
            governing.append(sealed.line)
        else:
            governing.append(None)

        # ---- (b) new-ATH test, BEFORE every other test ----------------------
        anchor = sealed.verdict.anchor
        high = float(bar.high)
        if anchor is not None and high > anchor.high:  # `==` is NOT a new ATH (D-TL-02)
            if current_state in _LINE_BEARING:
                prior = current_state
                emit(t, LineState.NONE, ReasonCode.RESET_NEW_ATH)
                events.append(
                    BarEvent(t, ReasonCode.RESET_NEW_ATH, {"prior_state": prior.value})
                )
                end_episode()
            prefix = prefix.extended(ln_price(high), high)
            previous_sealed = sealed
            continue

        # ---- (c)/(d) judge bar t against Λ_t --------------------------------
        if current_state is LineState.ACTIVE and sealed.line is not None:
            line = sealed.line
            y_hat_value = line.y_hat_at(t)
            close = float(bar.close)
            ln_close = ln_price(close)
            ln_high = ln_price(high)

            if exceeds(ln_close, y_hat_value, params.eps_break):
                # §13.1's predicate holds: the confirmed breakout of §13.2 fires
                # on this first qualifying close, with no persistence wait
                # (HD-03).
                record = StopRecord(
                    bar=t,
                    line=line,
                    y_hat=y_hat_value,
                    line_value=line.price_at(t),
                    close=close,
                    ln_close=ln_close,
                    clearance=ln_close - y_hat_value,
                    clearance_net_of_eps_break=ln_close - (y_hat_value + params.eps_break),
                )
                if stop is None:
                    stop = record
                # §21.5: freeze the line that was active at the START of bar t,
                # by WRAPPING the object the stop already holds.  Identity, not
                # equality: two independently computed copies could drift and
                # both gates would still pass, on different numbers.
                active_frozen = FrozenLine(
                    line=record.line,
                    tolerance_version=params.tolerance_version,
                    breakout_bar=t,
                )
                if active_frozen.line is not record.line:  # pragma: no cover
                    raise EngineDefect("Λ^F is not the line the stop recorded (§21.5)")
                reported_frozen = active_frozen
                episodes.append(active_frozen)
                hold_windows.clear()
                emit(t, LineState.BROKEN_OUT, ReasonCode.BREAKOUT_CONFIRMED)
                events.append(
                    BarEvent(
                        t,
                        ReasonCode.BREAKOUT_CONFIRMED,
                        {
                            "line": line,
                            "y_hat": y_hat_value,
                            "line_value": record.line_value,
                            "close": close,
                            "ln_close": ln_close,
                            "margin": record.clearance_net_of_eps_break,
                        },
                    )
                )
                prefix = prefix.extended(ln_price(high), high)
                previous_sealed = sealed
                continue

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

        # ---- (e) judge bar t against Λ^F ------------------------------------
        elif current_state in _FROZEN_REGIME and active_frozen is not None:
            _judge_post_breakout(
                bar=bar,
                t=t,
                frozen=active_frozen,
                params=params,
                windows=hold_windows,
                state=lambda: current_state,
                emit=emit,
                events=events,
            )
            if current_state is LineState.NONE:
                end_episode()

        # ---- (f) seal for t+1 ----------------------------------------------
        prefix = prefix.extended(ln_price(high), high)
        previous_sealed = sealed

    # The tail seal at t = n is ALWAYS appended: it is the line that would judge
    # a hypothetical next bar, ``gate_trace_full`` records it, and §21.4's
    # "report Λ_n when no breakout occurred" is exactly this line.
    tail = _seal(prefix, params)
    sealed_bars.append(tail)

    reported_line: Optional[Line]
    reported_anchor: Optional[Tuple[int, float]]

    if reported_frozen is not None:
        # §21.4: the frozen event line is the reported line if a confirmed
        # breakout occurred ANYWHERE in the series — retained after
        # EXPIRED_POST_BREAKOUT and after RESET_NEW_ATH alike (OQ-P3-4), and
        # supplied by the LATEST episode when there is more than one (OQ-P3-5).
        # GX-07 is the case that breaks any implementation reporting "the
        # current line": it reports B* = (6, 94) with a final state of NONE.
        reported_line = reported_frozen.line
        reported_anchor = (reported_frozen.line.t_anchor, reported_frozen.line.high_anchor)
    else:
        reported_line = tail.line
        reported_anchor = (
            None if tail.verdict.anchor is None
            else (tail.verdict.anchor.t, tail.verdict.anchor.high)
        )

    challengers: Tuple[Challenger, ...] = ()
    if reported_frozen is not None:
        challengers = challengers_over(reported_frozen, prefix.high, prefix.y)

    return CausalResult(
        bars_evaluated=bar_count,
        sealed=tuple(sealed_bars),
        transitions=tuple(transitions),
        reason_codes=tuple(codes),
        reselections=tuple(reselections),
        events=tuple(events),
        stop=stop,
        final_state=current_state,
        t_form=t_form,
        reported_line=reported_line,
        reported_anchor=reported_anchor,
        state_at_start=tuple(state_at_start),
        governing=tuple(governing),
        frozen=reported_frozen,
        episodes=tuple(episodes),
        challengers=challengers,
    )


def _judge_post_breakout(
    bar,
    t: int,
    frozen: FrozenLine,
    params: DetectorParams,
    windows: List[HoldWindow],
    state,
    emit,
    events: List[BarEvent],
) -> None:
    """§15, then §16, then §17 — all against ``Λ^F`` (§21.5).

    ``state()`` is read again between the legs on purpose, and both §15 and §16
    are gated on ``BROKEN_OUT``.  That single gate carries two rulings at once:

    * once ``FAILED_BREAKOUT`` is recorded, §15 and §16 are **not** evaluated
      again for that episode (HD-25);
    * once ``RETESTED`` is recorded, neither is either.  §15's predicate carries
      no state qualifier, so a close below ``ŷ_F − ε_fail`` after a held retest
      is *arithmetically* inside the failure window — but §11 draws no
      ``RETESTED → FAILED_BREAKOUT`` edge, OQ-P3-3 reaches ``RETESTED`` at most
      once per episode, and §16 condition 3 points the same way.  **The corpus
      pins this neither way**: every post-retest close in both ``RETESTED``
      fixtures clears the failure band (GX-19 bars 17–20 by +0.0231, +0.0215,
      +0.0185, +0.0141; GX-04's closes sit far above its line), so nothing here
      is fixture-forced and the gate is the only thing preventing it.

    So the terminal shape of an episode is: ``BROKEN_OUT`` may reach
    ``RETESTED``, ``FAILED_BREAKOUT`` or ``NONE``; ``RETESTED`` and
    ``FAILED_BREAKOUT`` may reach **only** ``NONE``, by a new ATH or by expiry.
    """
    close = float(bar.close)

    # -- §15 failure.  BROKEN_OUT only: §11 draws no other edge into
    #    FAILED_BREAKOUT, and §15 opens "After a BROKEN_OUT state".
    if state() is LineState.BROKEN_OUT:
        failure = failed_breakout_at(frozen, close, t, params)
        if failure is not None:
            emit(t, LineState.FAILED_BREAKOUT, ReasonCode.FAILED_BREAKOUT)
            events.append(
                BarEvent(
                    t,
                    ReasonCode.FAILED_BREAKOUT,
                    {
                        "y_hat_frozen": failure.y_hat_frozen,
                        "line_value": failure.line_value,
                        "close": failure.close,
                        "margin": failure.margin,
                    },
                )
            )

    # -- §16 retest.  BROKEN_OUT only: §11 has no RETESTED -> RETESTED edge, so
    #    at most one RETEST_HELD per episode (OQ-P3-3), and a failed episode is
    #    not retested (HD-25).
    if state() is LineState.BROKEN_OUT:
        windows[:] = open_hold_windows(windows, t)
        if in_return_window(frozen, t, params):
            leg = retest_return_at(frozen, bar.low, t, params)
            if leg is not None:
                # ESC-3: the hold window is [r, r + h_hold] and the return bar
                # itself is a valid hold bar — which is what every corpus retest
                # in fact records.
                windows.append(
                    HoldWindow(
                        return_bar=t,
                        last_bar=t + params.h_hold,
                        low=leg.low,
                        ln_low=leg.ln_low,
                        return_margin=leg.return_margin,
                    )
                )
        window = earliest_open_window(windows, t)
        if window is not None:
            hold = retest_hold_at(frozen, close, t, params)
            if hold is not None:
                # OQ-P3-2: recorded at the HOLD bar, never the return bar.
                # §21.8 rule 1 forces it — recording at r would require a later
                # bar u > r to establish r's classification.
                emit(t, LineState.RETESTED, ReasonCode.RETEST_HELD)
                events.append(
                    BarEvent(
                        t,
                        ReasonCode.RETEST_HELD,
                        {
                            "y_hat_frozen": hold.y_hat_frozen,
                            "line_value": hold.line_value,
                            "low": window.low,
                            "close": hold.close,
                            "return_bar": window.return_bar,
                            "return_margin": window.return_margin,
                            "hold_margin": hold.hold_margin,
                        },
                    )
                )
                del windows[:]

    # -- §17 expiry.  Available from BROKEN_OUT, RETESTED and FAILED_BREAKOUT
    #    alike (HD-25), and emits exactly ONE record (ESC-1): there is no
    #    intermediate EXPIRED state.
    if state() in _FROZEN_REGIME:
        elapsed = expired_at(frozen, t, params)
        if elapsed is not None:
            emit(t, LineState.NONE, ReasonCode.EXPIRED_POST_BREAKOUT)
            events.append(
                BarEvent(
                    t,
                    ReasonCode.EXPIRED_POST_BREAKOUT,
                    {"bars_since_breakout": elapsed},
                )
            )
