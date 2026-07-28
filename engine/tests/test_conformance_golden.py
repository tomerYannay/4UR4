"""Layer 0 — the conformance gate over every committed golden fixture.

The fixture list is **derived from the directory**, so adding a fixture tightens
this gate automatically.  A directory the harness did not visit is a failure,
not a silent gap.

Two properties of the gate itself are asserted here, because a gate that is
merely large is not the same as a gate that is complete:

* :class:`Phase3OutcomeCensus` — the number of asserted post-breakout outcomes
  is **derived from the committed robustness blocks**, never pinned in source,
  so adding a fixture or a sweep scale tightens the gate without an edit.
* :class:`UnassertedKeyCensus` — the OQ-P3-7 remedy.  Every recorded key no
  assertion reads is measured and matched against the harness's declared
  allow-list, in both directions.
"""

from __future__ import annotations

import os
import unittest
from typing import List, Optional, Set, Tuple

from ..detector import detect
from ..params import DetectorParams
from .conformance import SPEC_VERSION, UNASSERTED_KEY_ALLOW_LIST, compare_golden
from .fixtures_io import (
    GOLDEN_DIR,
    KeyTracker,
    all_key_paths,
    golden_fixture_ids,
    load_expected,
    load_series,
    tracked,
)

VISITED = set()


def _run_fixture(fixture_id: str, tracker: Optional[KeyTracker] = None):
    """Compare one fixture in full.

    ``tracker``, when supplied, records every key path the comparison reads —
    which is what makes the unasserted-key census a *measurement* rather than a
    hand-maintained claim.  The tracked document is used for the parameter parse
    as well as the comparison, so a key read only by ``from_fixture_params``
    counts as read.
    """
    expected = load_expected(fixture_id)
    if tracker is not None:
        expected = tracked(expected, tracker)
    series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
    params = DetectorParams.from_fixture_params(expected["params"], spec_version=SPEC_VERSION)
    result = detect(series, params)

    def sweep_runner(eps_break: float):
        return detect(series, params.with_eps_break(eps_break))

    return compare_golden(fixture_id, expected, result, series, sweep_runner)


class GoldenFixtureConformance(unittest.TestCase):
    """One test method per committed fixture; generated below."""


def _make_test(fixture_id: str):
    def test(self):
        VISITED.add(fixture_id)
        report = _run_fixture(fixture_id)
        self.assertTrue(report.ok, "\n" + report.render())

    test.__name__ = "test_%s" % fixture_id.replace("-", "_").lower()
    test.__doc__ = "Conformance: %s" % fixture_id
    return test


for _fixture_id in golden_fixture_ids():
    setattr(GoldenFixtureConformance, _make_test(_fixture_id).__name__, _make_test(_fixture_id))


class GateCoverage(unittest.TestCase):
    """A-5 — the gate must be derived, and must fail on an unvisited directory."""

    def test_every_golden_directory_has_a_generated_test(self) -> None:
        generated = {
            name[len("test_"):].replace("_", "-").upper()
            for name in dir(GoldenFixtureConformance)
            if name.startswith("test_gx_")
        }
        self.assertEqual(
            generated,
            set(golden_fixture_ids()),
            "a golden fixture directory has no generated conformance test",
        )

    def test_directory_walk_is_not_hand_maintained(self) -> None:
        ids = golden_fixture_ids()
        self.assertTrue(ids, "the golden fixture walk found nothing")
        for fixture_id in ids:
            self.assertTrue(
                os.path.exists(os.path.join(GOLDEN_DIR, fixture_id, "expected.json")),
                "%s carries no expected.json" % fixture_id,
            )
            self.assertTrue(
                os.path.exists(os.path.join(GOLDEN_DIR, fixture_id, "input.csv")),
                "%s carries no input.csv" % fixture_id,
            )


def post_breakout_outcomes() -> List[Tuple[str, str]]:
    """Every configuration on the committed corpus that reaches a breakout.

    DERIVED, never pinned.  One entry per ``(fixture, configuration)`` whose
    recorded outcome carries a confirmed breakout: the fixture's own run when its
    ``confirmed_bar`` is non-null, plus every recorded ``eps_break`` sweep point
    whose ``breakout_bar`` is non-null at a fixture whose baseline has none.

    The second group is the one the Phase-2 harness could not see: it compared a
    sweep point's ``final_state`` **only when that point's ``breakout_bar`` was
    null**, so every sweep outcome that reached a post-breakout state was
    unasserted.  Removing that guard is what brings those configurations into
    the gate.
    """
    out: List[Tuple[str, str]] = []
    for fixture_id in golden_fixture_ids():
        expected = load_expected(fixture_id)
        baseline = expected.get("confirmed_bar")
        if baseline is not None:
            out.append((fixture_id, "baseline"))
        sweep = (
            (expected.get("causal_record") or {}).get("eps_break_robustness") or {}
        ).get("sweep") or []
        for point in sweep:
            if point["breakout_bar"] is None:
                continue
            if baseline is not None and point["breakout_bar"] == baseline:
                continue  # the baseline configuration, already counted
            out.append((fixture_id, "eps_break x%s" % point["scale"]))
    return out


class Phase3OutcomeCensus(unittest.TestCase):
    """The size of the post-breakout gate, measured rather than asserted.

    The count is **not** written down here.  It is derived from the committed
    robustness blocks, so adding a fixture or a sweep scale tightens the gate
    with no edit to this file — which is the whole point of stating the criterion
    by deferral instead of by a list.
    """

    def test_every_derived_post_breakout_outcome_is_actually_compared(self) -> None:
        outcomes = post_breakout_outcomes()
        self.assertGreater(len(outcomes), 0, "the census found no post-breakout outcome at all")
        baseline = [item for item in outcomes if item[1] == "baseline"]
        sweep_only = [item for item in outcomes if item[1] != "baseline"]
        # Every one of them must be reproduced by the engine.  This is the same
        # comparison the per-fixture tests run; it is re-run here over the
        # derived census so the census cannot claim coverage it does not have.
        for fixture_id in sorted({item[0] for item in outcomes}):
            report = _run_fixture(fixture_id)
            self.assertTrue(report.ok, "\n" + report.render())
        self.assertEqual(
            len(outcomes), len(baseline) + len(sweep_only), "the census double-counted"
        )

    def test_the_sweep_guard_removal_widened_the_gate(self) -> None:
        """The Phase-2 harness compared ``final_state`` only where
        ``breakout_bar`` was null.  Measure what that hid: the outcomes it could
        not see must be a **non-empty** subset of the census."""
        hidden = [item for item in post_breakout_outcomes() if item[1] != "baseline"]
        self.assertGreater(
            len(hidden),
            0,
            "no sweep point reaches a post-breakout state, so removing the "
            "Phase-2 guard asserted nothing new — the corpus changed",
        )
        # ...and each hidden outcome is genuinely asserted now.
        for fixture_id, _label in hidden:
            expected = load_expected(fixture_id)
            series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
            params = DetectorParams.from_fixture_params(
                expected["params"], spec_version=SPEC_VERSION
            )
            sweep = expected["causal_record"]["eps_break_robustness"]["sweep"]
            for point in sweep:
                if point["breakout_bar"] is None:
                    continue
                outcome = detect(series, params.with_eps_break(float(point["eps_break"])))
                self.assertEqual(outcome.stop_bar, point["breakout_bar"], fixture_id)
                self.assertEqual(
                    None if outcome.final_state is None else outcome.final_state.value,
                    point["final_state"],
                    "%s at scale %s" % (fixture_id, point["scale"]),
                )


class UnassertedKeyCensus(unittest.TestCase):
    """OQ-P3-7 — every recorded key that no assertion reads, against a declared
    allow-list, failing in BOTH directions.

    Measured, not declared: the expectation document is wrapped so that every
    read records its path, and the full key set of the corpus is walked under the
    same normalisation.  A key that is unasserted and not on the list fails.  A
    listed key that has since become asserted, or that no fixture carries any
    more, fails too — so the list cannot rot into a blanket exemption.
    """

    def _census(self) -> Tuple[Set[str], Set[str]]:
        tracker = KeyTracker()
        present: Set[str] = set()
        for fixture_id in golden_fixture_ids():
            present |= all_key_paths(load_expected(fixture_id))
            report = _run_fixture(fixture_id, tracker)
            self.assertTrue(report.ok, "\n" + report.render())
        return present, tracker.read

    def test_the_unasserted_key_set_equals_the_declared_allow_list(self) -> None:
        present, read = self._census()
        unasserted = present - read
        declared = set(UNASSERTED_KEY_ALLOW_LIST)
        self.assertEqual(
            sorted(unasserted - declared),
            [],
            "recorded key(s) that NO assertion reads and that are not on the "
            "declared allow-list — a key passed over in silence is the failure "
            "mode OQ-P3-7 exists to remove",
        )
        self.assertEqual(
            sorted(declared - unasserted),
            [],
            "allow-listed key(s) that are now asserted, or that no fixture "
            "carries any more — the list has gone stale and must be trimmed",
        )

    def test_the_census_is_capable_of_failing(self) -> None:
        """Anti-vacuity, in both directions.

        If the tracker recorded nothing the first assertion would flag the whole
        corpus; if it recorded everything the second would flag the whole list.
        Neither happens, and the key set is large.
        """
        present, read = self._census()
        self.assertGreater(len(present), 100, "the key walk found suspiciously little")
        self.assertGreater(len(read), 100, "the tracker recorded suspiciously little")
        self.assertTrue(read <= present, "the tracker recorded a path no fixture carries: %r"
                        % sorted(read - present)[:5])
        self.assertIn("flags", UNASSERTED_KEY_ALLOW_LIST)
        self.assertNotIn("expected_final_state", UNASSERTED_KEY_ALLOW_LIST)

    def test_the_allow_list_has_no_duplicates(self) -> None:
        self.assertEqual(
            len(UNASSERTED_KEY_ALLOW_LIST), len(set(UNASSERTED_KEY_ALLOW_LIST))
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
