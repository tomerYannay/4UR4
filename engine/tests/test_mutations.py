"""Layer 5 — seeded mutations.  The anti-vacuity backbone.

Each seeded defect must be caught by at least one named check.  **A mutation
that survives is a finding, not a pass**: two of them (M-1 and M-2) survive the
6-significant-figure fixture comparison entirely, and rather than being quietly
dropped they are recorded here and given constructed adversarial cases that do
catch them.  Those constructions are engine-local tests; **no fixture was added,
edited or reinterpreted** to accommodate them.

Most mutations are expressed as an explicit *alternative computation* written
beside the engine's, rather than as a monkeypatch.  That form asserts something
stronger: not merely "the engine is right", but "the corpus can tell the two
apart" — which is the property a mutation table exists to establish.
"""

from __future__ import annotations

import math
import os
import unittest
from typing import List, Optional

from ..anchor import anchor_of
from ..bars import Bar, BarSeries, Prefix
from ..causal import Line, _seal
from ..detector import detect, prefix_of
from ..envelope import select_second_anchor
from ..guards import run_guards
from ..logspace import exceeds, ln_price, log_intercept, log_slope, sig6, y_hat
from ..params import DetectorParams
from ..state import ReasonCode
from .conformance import SPEC_VERSION
from .fixtures_io import GOLDEN_DIR, golden_fixture_ids, load_expected, load_series
from .support import default_params, make_series


def _load(fixture_id: str):
    expected = load_expected(fixture_id)
    series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
    params = DetectorParams.from_fixture_params(expected["params"], spec_version=SPEC_VERSION)
    return expected, series, params


def _alternative_select(
    prefix: Prefix,
    t_anchor: int,
    eps: float,
    *,
    slope_form: str = "difference",
    candidacy: str = "strict",
    domination: str = "all-highs",
    tie: str = "later",
) -> Optional[int]:
    """§8, re-implemented with one rule deliberately wrong.  Returns ``B*``'s bar.

    Every axis here is a *deliberate* deviation, so the axes that are **not** being
    mutated must be the sanctioned rules — otherwise a disagreement cannot be
    attributed to the axis under test.  The envelope predicate is therefore the
    pinned ``lhs > y_hat + tol`` via :func:`logspace.exceeds` and not the
    ``worst_gap > eps`` this function used to spell, which is precisely the form
    plan §4.3 forbids: it was the last instance of it **as an envelope predicate**
    under ``engine/`` after the production path dropped it, and it sat inside the
    oracle that M-1 compares the engine's now-pinned predicate against.  The literal
    shape survives twice in ``test_units`` — ``worst_gap > 0.02`` in
    ``test_a_tying_high_is_excluded_from_candidacy_but_dominates`` and
    ``worst_gap >= 0.0`` in ``test_worst_gap_is_exactly_zero_at_the_candidate_itself``
    — where each asserts something about a *reported number* and decides no
    candidate's validity.  That is why the qualifier matters and the claim is not
    "no occurrences remain".

    Measured before the swap, over **9,264** evaluations — every prefix of every
    evaluable golden fixture crossed with all sixteen axis combinations, plus the
    M-1 adversarial construction: **0** disagreements between the two forms.  The
    M-1 separation is unaffected (``difference`` still selects bar 18 and ``ratio``
    bar 9), so nothing this file asserts is weakened; what changes is that a future
    disagreement can no longer be blamed on the oracle's comparison form.
    """
    y_anchor = prefix.y[t_anchor]
    high_anchor = prefix.high[t_anchor]
    all_later = list(range(t_anchor + 1, prefix.length))

    candidates: List[int] = []
    for i in all_later:
        if candidacy == "strict" and not prefix.high[i] < high_anchor:
            continue
        if candidacy == "loose" and not prefix.high[i] <= high_anchor:
            continue
        candidates.append(i)

    dominated = candidates if domination == "candidates-only" else all_later

    best: Optional[tuple] = None
    for i in candidates:
        if slope_form == "difference":
            m = log_slope(prefix.y[i], y_anchor, i, t_anchor)
        else:  # the algebraically identical ratio form
            m = math.log(prefix.high[i] / high_anchor) / (i - t_anchor)
        b = log_intercept(y_anchor, m, t_anchor)
        if any(exceeds(prefix.y[j], y_hat(m, b, j), eps) for j in dominated):
            continue
        if best is None:
            best = (m, i)
        elif m > best[0]:
            best = (m, i)
        elif m == best[0] and tie == "later":
            best = (m, i)
    return None if best is None else best[1]


class M1SlopeForm(unittest.TestCase):
    """M-1 — slope via ``ln(H_i/H_a)`` instead of a difference of cached logs.

    **FINDING: this mutation SURVIVES the committed corpus.**  Across every
    evaluable prefix of all 23 golden fixtures and RM-01, the two forms select
    the identical anchor and agree to 6 significant figures; they differ only in
    the last one or two bits, and 1 ulp is ~1e-16 against a gate resolution of
    ~1e-7.  The plan expects GX-14's tie to catch it; GX-14 does not, because the
    tie is preserved under both forms.

    That is recorded rather than absorbed, and the constructed case below is the
    dedicated adversarial replacement.  It is an engine-local test — no fixture
    was added or changed.
    """

    def test_the_corpus_cannot_distinguish_the_two_forms(self) -> None:
        differences = 0
        for fixture_id in golden_fixture_ids():
            expected, series, params = _load(fixture_id)
            if (expected.get("causal_record") or {}).get("input_guard"):
                continue
            full = prefix_of(series)
            for t in range(2, full.length + 1):
                prefix = Prefix(full.y[:t], full.high[:t], t)
                anchor = anchor_of(prefix)
                assert anchor is not None
                a = _alternative_select(prefix, anchor.t, params.eps, slope_form="difference")
                b = _alternative_select(prefix, anchor.t, params.eps, slope_form="ratio")
                if a != b:
                    differences += 1
        self.assertEqual(
            differences,
            0,
            "the corpus now DOES distinguish the two §7 slope forms — update this "
            "recorded finding rather than deleting it",
        )

    @staticmethod
    def adversarial_highs() -> List[float]:
        """``A = (0, 100)``, a candidate at ``t=9`` (60.0) and one at ``t=18``.

        ``36 = 60^2 / 100`` puts ``(18, 36)`` exactly ON the line through
        ``(0, 100)`` and ``(9, 60)``, so the two candidates are collinear and
        their slopes tie in the reals.  Dropping the later high by two ulps
        breaks the tie by an amount smaller than either form's rounding error —
        and the two forms then break it in OPPOSITE directions.

        Every other bar sits 3% below that line, which keeps it out of the
        argmax (steeper) and out of the envelope-valid set (its own line would
        pass 0.03 log units below the ``t=9`` high, beyond ``eps = 0.02``), so
        the selection is genuinely between the two tied candidates.
        """
        highs: List[float] = []
        for t in range(19):
            if t == 0:
                highs.append(100.0)
            elif t == 9:
                highs.append(60.0)
            elif t == 18:
                highs.append(35.99999999999999)  # two ulps below 60^2/100
            else:
                highs.append(100.0 * (0.6 ** (t / 9.0)) * 0.97)
        return highs

    def test_the_constructed_adversarial_case_does_distinguish_them(self) -> None:
        highs = self.adversarial_highs()
        self.assertEqual(len(highs), 19)
        self.assertEqual(highs[9], 60.0)
        prefix = prefix_of(make_series(highs))
        pinned = _alternative_select(prefix, 0, 0.02, slope_form="difference")
        ratio = _alternative_select(prefix, 0, 0.02, slope_form="ratio")
        self.assertNotEqual(
            pinned, ratio, "the constructed case no longer separates the two forms"
        )
        engine = select_second_anchor(prefix, 0, 0.02)
        assert engine.selected is not None
        self.assertEqual(
            engine.selected.t,
            pinned,
            "the engine does not use the pinned difference-of-logs form (§7, M-1)",
        )


class M2LineEvaluationForm(unittest.TestCase):
    """M-2 — ``y_hat`` as ``y_a + m*(u - t_a)`` instead of ``m*u + b``.

    **FINDING: this mutation also survives the 6-significant-figure comparison.**
    On GX-06 the two forms differ by exactly 1 ulp at bar 20 and agree at 6 s.f.;
    on RM-01 (``tA = 2``) they agree bit-for-bit at every asserted index.  A
    1-ulp arithmetic-form change is undetectable by *any* 6-s.f. comparison — it
    is detectable only where the difference crosses a **strict threshold**.

    The construction below is exactly that: GX-06's own post-reset line, with
    bar 20's close chosen so that ``ln(close)`` lands **exactly on** the pinned
    form's ``y_hat + eps_break``.  The pinned form then reports no breakout
    (``>`` is strict) and the alternative form reports one.
    """

    def _gx06_line(self) -> Line:
        _expected, series, params = _load("GX-06")
        line = detect(series, params).reported_line
        assert line is not None
        return line

    def test_the_two_forms_agree_to_six_significant_figures_everywhere(self) -> None:
        offenders = []
        for fixture_id in golden_fixture_ids():
            expected, series, params = _load(fixture_id)
            result = detect(series, params)
            line = result.reported_line
            if line is None:
                continue
            for key in expected.get("expected_line_values") or {}:
                u = int(key)
                pinned = y_hat(line.m, line.b, u)
                alternative = line.y_anchor + line.m * (u - line.t_anchor)
                if sig6(pinned) != sig6(alternative):
                    offenders.append((fixture_id, u))
        self.assertEqual(
            offenders,
            [],
            "the 6-s.f. gate now DOES catch M-2 — update this recorded finding",
        )

    def test_a_constructed_close_makes_the_forms_disagree_about_a_breakout(self) -> None:
        line = self._gx06_line()
        params = _load("GX-06")[2]
        bar = 20
        pinned_threshold = y_hat(line.m, line.b, bar) + params.eps_break
        alternative_threshold = (
            line.y_anchor + line.m * (bar - line.t_anchor)
        ) + params.eps_break
        self.assertNotEqual(pinned_threshold, alternative_threshold)

        close = self._close_landing_on(pinned_threshold)
        self.assertIsNotNone(close, "no double whose log lands on the threshold")
        assert close is not None
        self.assertFalse(ln_price(close) > pinned_threshold, "pinned form: no breakout")
        self.assertTrue(ln_price(close) > alternative_threshold, "alternative form: breakout")

        # ...and end to end, through detect().
        _expected, series, _params = _load("GX-06")
        bars = list(series.bars)
        original = bars[bar]
        bars[bar] = Bar(
            t=original.t,
            timestamp=original.timestamp,
            open=original.open,
            high=max(float(original.high), close),
            low=original.low,
            close=close,
            volume=original.volume,
        )
        mutated_series = BarSeries(bars)
        self.assertIsNone(detect(mutated_series, params).stop_bar)

        saved = Line.y_hat_at
        try:
            Line.y_hat_at = lambda self, u: self.y_anchor + self.m * (u - self.t_anchor)
            self.assertEqual(
                detect(mutated_series, params).stop_bar,
                bar,
                "the M-2 mutation was not caught by the constructed case",
            )
        finally:
            Line.y_hat_at = saved

    @staticmethod
    def _close_landing_on(target: float) -> Optional[float]:
        candidate = math.exp(target)
        for step in range(-8, 9):
            probe = candidate
            for _ in range(abs(step)):
                probe = math.nextafter(probe, math.inf if step > 0 else 0.0)
            if ln_price(probe) == target:
                return probe
        return None


class M3BreakoutStrictness(unittest.TestCase):
    """M-3 — ``>=`` for ``>`` in §13.1.  Caught by GX-15's boundary."""

    def test_at_the_exact_boundary_only_a_relaxed_predicate_fires(self) -> None:
        _expected, series, params = _load("GX-15")
        result = detect(series, params)
        sealed = result.causal.sealed_at(28)
        assert sealed is not None and sealed.line is not None
        clearance = ln_price(float(series[28].close)) - sealed.line.y_hat_at(28)
        at_boundary = params.with_eps_break(clearance)
        self.assertIsNone(detect(series, at_boundary).stop_bar)

        from .. import causal as causal_module

        saved = causal_module.exceeds
        try:
            causal_module.exceeds = (
                lambda lhs, y_hat_value, tolerance: lhs >= y_hat_value + tolerance
                if tolerance == clearance
                else lhs > y_hat_value + tolerance
            )
            self.assertEqual(
                detect(series, at_boundary).stop_bar,
                28,
                "M-3 was not caught: relaxing §13.1 to `>=` changed nothing",
            )
        finally:
            causal_module.exceeds = saved


class M4ReselectionEffectiveBar(unittest.TestCase):
    """M-4 — a re-selection recorded at ``t`` instead of ``t+1``."""

    def test_shifting_every_effective_bar_by_one_breaks_the_corpus(self) -> None:
        broken = 0
        for fixture_id in ("GX-03", "GX-09", "GX-12", "GX-14", "GX-15", "GX-19"):
            expected, series, params = _load(fixture_id)
            recorded = (expected["causal_record"] or {}).get("reselections") or []
            result = detect(series, params)
            assert result.causal is not None
            engine = [item.effective_bar for item in result.causal.reselections]
            self.assertEqual(engine, [int(item["effective_bar"]) for item in recorded], fixture_id)
            if [bar - 1 for bar in engine] != [int(i["effective_bar"]) for i in recorded]:
                broken += 1
        self.assertEqual(broken, 6, "shifting the effective bar is not detected somewhere")


class M5LookAhead(unittest.TestCase):
    """M-5 — ``H[t]`` incorporated before bar ``t`` is evaluated.

    Structurally prevented rather than merely detected: the ``Prefix``
    constructor asserts its own length and the fold asserts the sealed bar index.
    Both guards are exercised here so they are known to be live.
    """

    def test_the_prefix_length_assertion_is_live(self) -> None:
        with self.assertRaises(AssertionError):
            Prefix((0.0, 1.0), (1.0, 2.0), 3)

    def test_sealing_always_produces_the_matching_bar_index(self) -> None:
        _expected, series, params = _load("GX-03")
        full = prefix_of(series)
        for t in range(full.length + 1):
            prefix = Prefix(full.y[:t], full.high[:t], t)
            self.assertEqual(_seal(prefix, params).t, t)

    def test_including_the_evaluation_bar_changes_its_own_classification(self) -> None:
        """The concrete harm: GX-03's bar 16 wick-breaks against ``Λ_16``.  A line
        built from ``S_17`` is bound AT bar 16, so the bar could not pierce it and
        the wick-break would vanish — the evaluation bar redefining its own judge.
        """
        _expected, series, params = _load("GX-03")
        full = prefix_of(series)
        causal_prefix = Prefix(full.y[:16], full.high[:16], 16)
        lookahead_prefix = Prefix(full.y[:17], full.high[:17], 17)
        causal_b = select_second_anchor(causal_prefix, 0, params.eps).selected
        lookahead_b = select_second_anchor(lookahead_prefix, 0, params.eps).selected
        assert causal_b is not None and lookahead_b is not None
        self.assertEqual(causal_b.t, 6)
        self.assertEqual(lookahead_b.t, 16)
        result = detect(series, params)
        self.assertIn(ReasonCode.WICK_BREAK, result.reason_codes)


class M6M7CandidacyAndDomination(unittest.TestCase):
    """M-6 — candidacy ``<=`` instead of ``<``.  M-7 — dominate over candidates only."""

    def test_loose_candidacy_changes_gx12_and_gx20(self) -> None:
        changed = 0
        for fixture_id in ("GX-12", "GX-20"):
            _expected, series, params = _load(fixture_id)
            full = prefix_of(series)
            for t in range(2, full.length + 1):
                prefix = Prefix(full.y[:t], full.high[:t], t)
                anchor = anchor_of(prefix)
                assert anchor is not None
                strict = _alternative_select(prefix, anchor.t, params.eps, candidacy="strict")
                loose = _alternative_select(prefix, anchor.t, params.eps, candidacy="loose")
                if strict != loose:
                    changed += 1
        self.assertGreater(changed, 0, "M-6 survives: no prefix distinguishes `<` from `<=`")

    def test_dominating_only_over_candidates_changes_gx12_and_gx20(self) -> None:
        changed = 0
        for fixture_id in ("GX-12", "GX-20"):
            _expected, series, params = _load(fixture_id)
            full = prefix_of(series)
            for t in range(2, full.length + 1):
                prefix = Prefix(full.y[:t], full.high[:t], t)
                anchor = anchor_of(prefix)
                assert anchor is not None
                everything = _alternative_select(
                    prefix, anchor.t, params.eps, domination="all-highs"
                )
                narrowed = _alternative_select(
                    prefix, anchor.t, params.eps, domination="candidates-only"
                )
                if everything != narrowed:
                    changed += 1
        self.assertGreater(changed, 0, "M-7 survives: domination set is untested")


class M8EnvelopeTie(unittest.TestCase):
    """M-8 — the envelope tie broken toward the EARLIER anchor."""

    def test_gx14_selects_the_earlier_bar_under_the_mutation(self) -> None:
        _expected, series, params = _load("GX-14")
        full = prefix_of(series)
        prefix = Prefix(full.y[:19], full.high[:19], 19)
        self.assertEqual(_alternative_select(prefix, 0, params.eps, tie="later"), 18)
        self.assertEqual(_alternative_select(prefix, 0, params.eps, tie="earlier"), 9)


class M9GuardScope(unittest.TestCase):
    """M-9 — guards applied per bar rather than to the bar-set.

    GX-10 alone cannot separate the two readings: its split is a *level shift*,
    so deleting the offending bar leaves the neighbouring pair still a bar apart
    across the same shift, and a per-bar guard trips on the next bar anyway.  The
    discriminating case is therefore constructed: a single-bar artifact between
    two otherwise contiguous, clean levels.
    """

    #: One impossible bar between two clean, adjacent levels.
    ARTIFACT_HIGHS = [100.0, 99.0, 98.0, 97.0, 200.0, 96.0, 95.0, 94.0, 93.0, 92.0]

    def test_gx10_is_rejected_as_a_whole_bar_set(self) -> None:
        _expected, series, params = _load("GX-10")
        result = detect(series, params)
        self.assertTrue(result.rejected)
        self.assertIsNone(result.causal, "no geometry may be fitted at any prefix")

    def test_a_per_bar_guard_would_fit_geometry_where_the_bar_set_guard_does_not(self) -> None:
        params = default_params()
        series = make_series(self.ARTIFACT_HIGHS)
        rejected = detect(series, params)
        self.assertTrue(rejected.rejected)
        self.assertIsNone(rejected.reported_line)

        # The mutation: drop the offending bar and carry on.
        kept = [bar for bar in series.bars if bar.t != 4]
        renumbered = BarSeries(
            [
                Bar(index, index, bar.open, bar.high, bar.low, bar.close, bar.volume)
                for index, bar in enumerate(kept)
            ]
        )
        mutant = detect(renumbered, params)
        self.assertFalse(mutant.rejected)
        self.assertIsNotNone(
            mutant.reported_line,
            "M-9 survives: the per-bar and bar-set readings are indistinguishable",
        )


class M10FormationScope(unittest.TestCase):
    """M-10 — formation gates evaluated over the FULL series."""

    def test_full_series_gates_would_form_gx21_at_bar_2(self) -> None:
        _expected, series, params = _load("GX-21")
        full = prefix_of(series)
        # The mutation: judge F1 by the whole delivered length, not |S_t|.
        first_full_series_eligible = None
        for t in range(full.length + 1):
            prefix = Prefix(full.y[:t], full.high[:t], t)
            anchor = anchor_of(prefix)
            if anchor is None:
                continue
            f1 = full.length >= params.min_formation_bars  # <- the defect
            f2 = anchor.t <= (t - 1) - params.min_ath_age_bars
            f3 = select_second_anchor(prefix, anchor.t, params.eps).exists
            if f1 and f2 and f3:
                first_full_series_eligible = t
                break
        result = detect(series, params)
        assert result.causal is not None
        self.assertEqual(result.causal.t_form, 8)
        self.assertEqual(first_full_series_eligible, 4)
        self.assertNotEqual(result.causal.t_form, first_full_series_eligible)


class M11M12NewAth(unittest.TestCase):
    def test_m11_a_new_ath_bar_is_not_a_breakout(self) -> None:
        """GX-06's bar 10 close clears its active line by 0.2 log units, so an
        engine that tested the breakout predicate before the new-ATH test would
        stop there."""
        _expected, series, params = _load("GX-06")
        result = detect(series, params)
        sealed = result.causal.sealed_at(10)
        assert sealed is not None and sealed.line is not None
        clearance = ln_price(float(series[10].close)) - sealed.line.y_hat_at(10)
        self.assertGreater(clearance, params.eps_break, "GX-06 no longer tests M-11")
        self.assertIsNone(result.stop_bar)
        self.assertIn(ReasonCode.RESET_NEW_ATH, result.reason_codes)

    def test_m12_an_equal_high_is_not_a_new_ath(self) -> None:
        _expected, series, params = _load("GX-12")
        self.assertEqual(float(series[0].high), float(series[2].high))
        result = detect(series, params)
        self.assertNotIn(ReasonCode.RESET_NEW_ATH, result.reason_codes)


class M13NoneRunEncoding(unittest.TestCase):
    def test_per_bar_emission_would_multiply_gx20s_record(self) -> None:
        _expected, series, params = _load("GX-20")
        result = detect(series, params)
        records = [r for r in result.transitions if r.reason is ReasonCode.NO_VALID_SECOND_ANCHOR]
        self.assertEqual(len(records), 1)
        assert result.causal is not None
        per_bar = [
            sealed
            for sealed in result.causal.sealed
            if sealed.verdict.reason is ReasonCode.NO_VALID_SECOND_ANCHOR
        ]
        self.assertGreater(len(per_bar), 15, "GX-20's run is no longer long enough to test M-13")


class M14AthTie(unittest.TestCase):
    def test_latest_wins_would_move_gx12s_anchor(self) -> None:
        _expected, series, params = _load("GX-12")
        prefix = prefix_of(series)
        anchor = anchor_of(prefix)
        assert anchor is not None
        self.assertEqual(anchor.t, 0)
        latest = max(range(prefix.length), key=lambda i: (prefix.high[i], i))
        self.assertEqual(latest, 2)
        self.assertNotEqual(anchor.t, latest, "GX-12 no longer distinguishes the tie rule")


class M15WorstGap(unittest.TestCase):
    def test_a_clamped_worst_gap_would_validate_every_candidate(self) -> None:
        _expected, series, params = _load("GX-01")
        prefix = prefix_of(series, 8)
        selection = select_second_anchor(prefix, 0, params.eps)
        invalid = [c for c in selection.candidates if not c.envelope_valid]
        self.assertTrue(invalid, "GX-01's candidate set no longer contains invalid candidates")
        for candidate in invalid:
            self.assertGreater(
                candidate.worst_gap, params.eps,
                "a clamped worst_gap would report <= eps and validate this candidate",
            )

    def test_the_wrong_domination_set_changes_the_recorded_gaps(self) -> None:
        """GX-01 cannot distinguish the two domination sets — every later high is
        below the ATH, so candidates and domination coincide.  GX-12 can: its
        bar 2 TIES the ATH, so it is in the domination set and not in candidacy.
        Naming which fixture bites is the point; a check run on GX-01 would pass
        vacuously.
        """
        _expected, series, params = _load("GX-12")
        prefix = prefix_of(series, 8)
        selection = select_second_anchor(prefix, 0, params.eps)
        self.assertTrue(selection.candidates)
        differing = 0
        for candidate in selection.candidates:
            narrowed = max(
                (
                    prefix.y[j] - y_hat(candidate.slope, candidate.intercept, j)
                    for j in range(1, prefix.length)
                    if prefix.high[j] < prefix.high[0]
                ),
                default=0.0,
            )
            if narrowed != candidate.worst_gap:
                differing += 1
        self.assertGreater(
            differing, 0, "GX-12's candidate set cannot distinguish the two domination sets"
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
