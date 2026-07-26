"""Layer 2 — property-based tests.

Every generator here carries a **generator-quality assertion**: a property is
only as strong as the corpus it is checked on, and "no look-ahead" is trivially
true on a series in which nothing could ever re-bind.  The suite fails if the
generated corpus is degenerate, before it reports the property as holding.

Randomness lives here, in the tests, and is seeded.  There is none in
``engine/`` — architectural test A-2 asserts that.
"""

from __future__ import annotations

import math
import os
import random
import unittest
from typing import List, Tuple

from ..bars import Bar, BarSeries
from ..detector import detect
from ..params import DetectorParams
from ..state import LineState, ReasonCode
from .conformance import SPEC_VERSION
from .fixtures_io import GOLDEN_DIR, golden_fixture_ids, load_expected, load_series
from .support import default_params, make_series

SEED = 20260726
SERIES_COUNT = 60
SERIES_LENGTH = 26


def _random_series(rng: random.Random, length: int = SERIES_LENGTH) -> BarSeries:
    """A positive, guard-passing series with enough structure to be interesting.

    Highs random-walk downward with occasional rallies, so re-selections,
    wick-breaks and formations all occur across the corpus — which the
    generator-quality assertions then verify rather than assume.
    """
    highs: List[float] = [100.0]
    for _ in range(length - 1):
        drift = rng.uniform(-0.05, 0.035)
        highs.append(max(1.0, highs[-1] * math.exp(drift)))
    closes = [high * rng.uniform(0.93, 0.999) for high in highs]
    lows = [min(h, c) * rng.uniform(0.9, 0.99) for h, c in zip(highs, closes)]
    return make_series(highs, closes, lows)


def _mutate_suffix_bar(rng: random.Random, series: BarSeries, index: int) -> BarSeries:
    bars = list(series.bars)
    original = bars[index]
    factor = rng.choice([0.85, 0.95, 1.05, 1.25, 1.6])
    bars[index] = Bar(
        t=original.t,
        timestamp=original.timestamp,
        open=original.open,
        high=max(1.0, float(original.high) * factor),
        low=original.low,
        close=max(0.5, float(original.close) * factor),
        volume=original.volume,
    )
    return BarSeries(bars)


def _records(result) -> List[Tuple]:
    return [record.as_tuple() for record in result.transitions]


class GeneratorQuality(unittest.TestCase):
    """The corpus must be capable of falsifying the properties below."""

    def test_the_generated_corpus_is_not_degenerate(self) -> None:
        rng = random.Random(SEED)
        params = default_params()
        with_reselection = 0
        with_wick = 0
        with_formation = 0
        with_stop = 0
        with_reset = 0
        for _ in range(SERIES_COUNT):
            result = detect(_random_series(rng), params)
            if result.causal is None:
                continue
            if result.causal.reselections:
                with_reselection += 1
            if ReasonCode.WICK_BREAK in result.reason_codes:
                with_wick += 1
            if any(
                record.frm is LineState.NONE and record.to is LineState.ACTIVE
                for record in result.transitions
            ):
                with_formation += 1
            if result.stop_bar is not None:
                with_stop += 1
            if ReasonCode.RESET_NEW_ATH in result.reason_codes:
                with_reset += 1
        self.assertGreaterEqual(with_formation, SERIES_COUNT // 4, "too few NONE->ACTIVE")
        self.assertGreaterEqual(with_reselection, SERIES_COUNT // 5, "too few re-selections")
        self.assertGreaterEqual(with_wick, 3, "too few wick-breaks")
        self.assertGreaterEqual(with_stop, 3, "too few stops")
        self.assertGreaterEqual(with_reset, 3, "too few new-ATH resets")


class P1NoLookAhead(unittest.TestCase):
    """Mutating any bar at index > t leaves every record at bars <= t unchanged.

    This is the single most important property in the build, so it is checked
    against a corpus proven above to contain the events it could disturb.
    """

    def test_a_suffix_mutation_cannot_change_an_earlier_record(self) -> None:
        rng = random.Random(SEED + 1)
        params = default_params()
        mutations_that_changed_something = 0
        guard_rejections = 0
        comparisons = 0
        for _ in range(SERIES_COUNT):
            series = _random_series(rng)
            baseline = detect(series, params)
            base_records = _records(baseline)
            for cut in (10, 14, 18, 22):
                if cut >= len(series) - 1:
                    continue
                mutated_index = rng.randrange(cut + 1, len(series))
                mutated = detect(_mutate_suffix_bar(rng, series, mutated_index), params)

                if mutated.rejected and not baseline.rejected:
                    # The §18 pre-pass is whole-series — the engine's one
                    # deliberately non-causal element.  It is NOT exempted here:
                    # the mutation must be shown to have tripped a guard at a bar
                    # AFTER the cut, and the only effect must be the whole-series
                    # rejection.  A guard that fired at or before the cut would be
                    # a genuine look-ahead defect and fails.
                    guard_rejections += 1
                    self.assertGreater(
                        min(record.bar for record in mutated.transitions),
                        cut,
                        "the whole-series §18 guard fired at or before the cut",
                    )
                    continue

                comparisons += 1
                self.assertEqual(
                    [r for r in _records(mutated) if r[0] <= cut],
                    [r for r in base_records if r[0] <= cut],
                    "a bar at index %d changed a record at or before bar %d"
                    % (mutated_index, cut),
                )
                if _records(mutated) != base_records:
                    mutations_that_changed_something += 1
        self.assertGreater(
            mutations_that_changed_something,
            0,
            "no suffix mutation changed anything at all — the property held vacuously",
        )
        self.assertGreater(comparisons, SERIES_COUNT, "too few real comparisons")
        self.assertGreater(
            guard_rejections, 0, "the guard-interaction branch was never exercised"
        )


class P2PrefixTruncationInvariance(unittest.TestCase):
    """Running on ``bars[0..k]`` yields exactly the record prefix of the full run.

    This replaces §21.8.3's "streaming equals batch" operational test, which is
    **vacuous here by construction** — ``detect`` is a fold, so there is no
    separate batch path for it to disagree with.  Prefix-truncation invariance
    can fail, and so is worth asserting.
    """

    def _truncate(self, series: BarSeries, k: int) -> BarSeries:
        return BarSeries(list(series.bars)[: k + 1])

    def test_every_truncation_of_every_geometry_fixture(self) -> None:
        for fixture_id in golden_fixture_ids():
            expected = load_expected(fixture_id)
            if (expected.get("causal_record") or {}).get("input_guard"):
                continue  # handled by the positive control below
            series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
            params = DetectorParams.from_fixture_params(
                expected["params"], spec_version=SPEC_VERSION
            )
            full = detect(series, params)
            full_records = _records(full)
            for k in range(len(series)):
                truncated = detect(self._truncate(series, k), params)
                self.assertEqual(
                    _records(truncated),
                    [record for record in full_records if record[0] <= k],
                    "%s: truncating after bar %d changed an earlier record" % (fixture_id, k),
                )
                if full.stop_bar is not None and k >= full.stop_bar:
                    self.assertEqual(truncated.stop_bar, full.stop_bar, fixture_id)

    def test_positive_control_the_guard_exemption_cannot_hide_a_defect(self) -> None:
        """A guard-rejected series legitimately breaks the property, because the
        pre-pass is whole-series.  Conditioning the property on guard status is
        therefore indistinguishable from exempting the class it targets — unless
        the converse is asserted: truncated before its split, GX-10 must produce
        a real, non-rejected run.
        """
        expected = load_expected("GX-10")
        series = load_series(os.path.join(GOLDEN_DIR, "GX-10", "input.csv"))
        params = DetectorParams.from_fixture_params(expected["params"], spec_version=SPEC_VERSION)
        self.assertTrue(detect(series, params).rejected)
        head = BarSeries(list(series.bars)[:4])
        self.assertFalse(
            detect(head, params).rejected,
            "GX-10 truncated before its bar-4 split must NOT be rejected",
        )
        # ...and every truncation that still contains bar 4 must be rejected.
        for k in range(4, len(series)):
            self.assertTrue(
                detect(BarSeries(list(series.bars)[: k + 1]), params).rejected,
                "GX-10 truncated after bar %d is no longer rejected" % k,
            )


class P3StopStability(unittest.TestCase):
    """Once the predicate fires at ``t``, nothing later changes ``line_at_stop``.

    **Near-vacuous in Phase 2 by construction** — the engine halts at ``t``, so
    there are no later bars to change anything.  It is stated as such and kept
    because it becomes load-bearing the moment Phase 3 continues past the stop,
    where it will be asserted against the frozen line.
    """

    def test_no_record_is_emitted_after_the_stop(self) -> None:
        rng = random.Random(SEED + 2)
        params = default_params()
        stops = 0
        for _ in range(SERIES_COUNT):
            result = detect(_random_series(rng), params)
            if result.stop_bar is None:
                continue
            stops += 1
            for record in result.transitions:
                self.assertLessEqual(record.bar, result.stop_bar)
        self.assertGreater(stops, 0)


class P4HullValidityAtEveryPrefix(unittest.TestCase):
    """At every prefix, ``B*`` is envelope-valid and no valid candidate is
    strictly shallower; ties resolve later.

    The checker **re-enumerates candidates independently** rather than trusting
    the selector's own enumeration, so a candidate the selector wrongly pruned
    cannot hide.
    """

    def test_selection_is_the_argmax_over_an_independent_enumeration(self) -> None:
        from ..anchor import anchor_of
        from ..bars import Prefix
        from ..envelope import select_second_anchor
        from ..logspace import ln_price, log_intercept, log_slope, y_hat

        rng = random.Random(SEED + 3)
        checked = 0
        for _ in range(20):
            series = _random_series(rng)
            highs = [float(bar.high) for bar in series]
            logs = [ln_price(high) for high in highs]
            eps = 0.02
            for t in range(2, len(highs) + 1):
                prefix = Prefix(tuple(logs[:t]), tuple(highs[:t]), t)
                anchor = anchor_of(prefix)
                assert anchor is not None
                selection = select_second_anchor(prefix, anchor.t, eps)

                # Independent re-enumeration, from §6 and §8 directly.
                valid = []
                for i in range(anchor.t + 1, t):
                    if not highs[i] < anchor.high:
                        continue
                    m = log_slope(logs[i], logs[anchor.t], i, anchor.t)
                    b = log_intercept(logs[anchor.t], m, anchor.t)
                    if all(
                        logs[j] <= y_hat(m, b, j) + eps for j in range(anchor.t + 1, t)
                    ):
                        valid.append((m, i))
                if not valid:
                    self.assertIsNone(selection.selected)
                else:
                    best_slope = max(slope for slope, _ in valid)
                    best_index = max(i for slope, i in valid if slope == best_slope)
                    assert selection.selected is not None
                    self.assertEqual(selection.selected.t, best_index)
                    self.assertEqual(selection.selected.slope, best_slope)
                    self.assertTrue(selection.selected.envelope_valid)
                checked += 1
        self.assertGreater(checked, 300)


class P5FormationGateKIndependence(unittest.TestCase):
    """**Structurally incapable of failing, and therefore not offered as proof.**

    The formation predicate does not mention ``k``; ``DetectorParams`` has no
    ``k`` field at all.  A k-sweep here could not fail.  The falsifiable
    replacement is the architectural import test (A-1), which fails the moment
    ``formation`` or ``envelope`` acquires a dependency on ``pivots``.  This case
    is retained as a cheap regression and is **labelled unfalsifiable** so it
    cannot be counted as evidence.
    """

    def test_labelled_unfalsifiable(self) -> None:
        self.assertNotIn("k", DetectorParams.__dataclass_fields__)


class P6MonotoneShallowing(unittest.TestCase):
    def test_slope_never_steepens_within_an_episode(self) -> None:
        rng = random.Random(SEED + 4)
        params = default_params()
        comparisons = 0
        for _ in range(SERIES_COUNT):
            result = detect(_random_series(rng), params)
            if result.causal is None:
                continue
            previous = None
            for sealed in result.causal.sealed:
                if sealed.line is None:
                    previous = None
                    continue
                if previous is not None and previous.t_anchor == sealed.line.t_anchor:
                    self.assertGreaterEqual(sealed.line.m, previous.m)
                    comparisons += 1
                previous = sealed.line
        self.assertGreater(comparisons, 200, "too few in-episode comparisons to be meaningful")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
