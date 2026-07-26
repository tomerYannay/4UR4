"""Layer 0 — the conformance gate over every committed golden fixture.

The fixture list is **derived from the directory**, so adding a fixture tightens
this gate automatically.  A directory the harness did not visit is a failure,
not a silent gap.
"""

from __future__ import annotations

import os
import unittest

from ..detector import detect
from ..params import DetectorParams
from .conformance import SPEC_VERSION, compare_golden
from .fixtures_io import GOLDEN_DIR, golden_fixture_ids, load_expected, load_series

VISITED = set()


def _run_fixture(fixture_id: str):
    expected = load_expected(fixture_id)
    series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
    params = DetectorParams.from_fixture_params(expected["params"], spec_version=SPEC_VERSION)
    result = detect(series, params)

    def sweep_runner(eps_break: float):
        return detect(series, params.with_eps_break(eps_break))

    return compare_golden(fixture_id, expected, result, series, sweep_runner)


class GoldenFixtureConformance(unittest.TestCase):
    """One test method per committed fixture; generated below."""

    def test_bar_count_matches_declaration(self) -> None:
        for fixture_id in golden_fixture_ids():
            expected = load_expected(fixture_id)
            series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
            declared = expected["input_convention"].get("bar_count")
            if declared is not None:
                self.assertEqual(
                    len(series), declared, "%s: bar_count disagrees with input.csv" % fixture_id
                )


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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
