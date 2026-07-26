"""Layer 4 — architectural tests.  **These are the ones that can fail.**

They replace claims that cannot: an unfalsifiable ``k``-sweep, a prose assertion
of purity, a hand-maintained fixture list.  Each is a static fact about the
committed source, checkable by anyone at any time.

===  =======================================================================
A-1  no geometry/formation/causal module imports ``engine.pivots`` or reads ``k``
A-2  no engine module imports a clock, randomness, I/O or a numeric library
A-3  nothing under ``engine/`` references, imports or executes any sibling
     top-level directory of the repository — which is how the evidence-tooling
     tree is excluded without this file naming it
A-4  ``ReasonCode`` and ``LineState`` are exactly the committed schema's closed sets
A-5  the conformance harness derives its fixture list from the directory
===  =======================================================================
"""

from __future__ import annotations

import ast
import os
import unittest
from typing import Dict, List, Set

from ..state import LineState, ReasonCode
from .fixtures_io import REPO_ROOT, golden_fixture_ids, load_json

ENGINE_DIR = os.path.join(REPO_ROOT, "engine")
TESTS_DIR = os.path.join(ENGINE_DIR, "tests")
SCHEMA_PATH = os.path.join(
    REPO_ROOT, "product", "fixtures", "schema", "fixture.schema.json"
)

#: The *product* modules.  ``engine/tests/`` is excluded by design: the test
#: infrastructure must read fixtures from disk, and it is not shipped behaviour.
PRODUCT_MODULES = sorted(
    name for name in os.listdir(ENGINE_DIR) if name.endswith(".py")
)

BANNED_IMPORTS = {
    "time",
    "datetime",
    "random",
    "secrets",
    "uuid",
    "os",
    "sys",
    "socket",
    "urllib",
    "requests",
    "http",
    "sqlite3",
    "subprocess",
    "pathlib",
    "numpy",
    "pandas",
    "scipy",
    "json",
    "csv",
    "io",
    "shutil",
    "tempfile",
    "threading",
    "multiprocessing",
}

BANNED_CALLS = {"open", "input", "eval", "exec", "compile", "__import__"}

#: Modules on the geometry / formation / causal path, which must never depend on
#: the non-authoritative pivot window.
NON_PIVOT_PATH = (
    "anchor.py",
    "envelope.py",
    "formation.py",
    "causal.py",
    "detector.py",
    "trace.py",
    "logspace.py",
    "guards.py",
    "bars.py",
)

#: The one directory the engine may reference: the committed fixture data, which
#: is the correctness contract.  Everything else at the top level is off limits.
PERMITTED_SIBLINGS = {"engine", "product"}


def sibling_directories() -> List[str]:
    """Every top-level repository directory, derived rather than enumerated.

    Deriving the list means a directory added later is covered automatically —
    including a successor to the current evidence tooling, which is exactly the
    case E2-AUTHOR-A must keep covering.
    """
    return sorted(
        name
        for name in os.listdir(REPO_ROOT)
        if os.path.isdir(os.path.join(REPO_ROOT, name))
        and not name.startswith(".")
        and name not in PERMITTED_SIBLINGS
    )


def _parse(path: str) -> ast.Module:
    with open(path, "r", encoding="utf-8") as handle:
        return ast.parse(handle.read(), filename=path)


def _imported_names(tree: ast.Module) -> List[str]:
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import within the package
                names.append("." * node.level + (node.module or ""))
            elif node.module:
                names.append(node.module)
    return names


def _source(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _engine_sources() -> Dict[str, str]:
    sources = {name: _source(os.path.join(ENGINE_DIR, name)) for name in PRODUCT_MODULES}
    for name in sorted(os.listdir(TESTS_DIR)):
        if name.endswith(".py"):
            sources["tests/" + name] = _source(os.path.join(TESTS_DIR, name))
    return sources


class A1PivotIndependence(unittest.TestCase):
    def test_no_geometry_or_formation_module_imports_pivots(self) -> None:
        for name in NON_PIVOT_PATH:
            tree = _parse(os.path.join(ENGINE_DIR, name))
            for imported in _imported_names(tree):
                self.assertNotIn(
                    "pivots",
                    imported,
                    "%s imports the non-authoritative pivot module (HD-11)" % name,
                )

    def test_no_module_on_that_path_reads_k(self) -> None:
        for name in NON_PIVOT_PATH:
            tree = _parse(os.path.join(ENGINE_DIR, name))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr == "k":
                    self.fail("%s reads a `.k` attribute (HD-11, HD-14)" % name)
                if isinstance(node, ast.Name) and node.id == "k":
                    self.fail("%s binds a name `k` on the geometry path" % name)

    def test_pivots_is_imported_by_nothing_in_the_package(self) -> None:
        for name in PRODUCT_MODULES:
            if name == "pivots.py":
                continue
            for imported in _imported_names(_parse(os.path.join(ENGINE_DIR, name))):
                self.assertNotIn("pivots", imported, name)


class A2Purity(unittest.TestCase):
    def test_no_engine_module_imports_a_clock_randomness_or_io(self) -> None:
        for name in PRODUCT_MODULES:
            tree = _parse(os.path.join(ENGINE_DIR, name))
            for imported in _imported_names(tree):
                root = imported.split(".")[0]
                self.assertNotIn(
                    root,
                    BANNED_IMPORTS,
                    "%s imports %r — engine/ must be pure (§20)" % (name, imported),
                )

    def test_no_engine_module_performs_io_or_dynamic_execution(self) -> None:
        for name in PRODUCT_MODULES:
            tree = _parse(os.path.join(ENGINE_DIR, name))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(
                        node.func.id, BANNED_CALLS, "%s calls %s" % (name, node.func.id)
                    )

    def test_the_only_dependency_is_a_narrow_standard_library_subset(self) -> None:
        allowed = {"math", "decimal", "dataclasses", "enum", "typing", "__future__"}
        for name in PRODUCT_MODULES:
            for imported in _imported_names(_parse(os.path.join(ENGINE_DIR, name))):
                if imported.startswith("."):
                    continue
                self.assertIn(imported.split(".")[0], allowed, "%s imports %r" % (name, imported))

    def test_running_the_corpus_twice_gives_identical_output(self) -> None:
        """A runtime companion to the static scan: a hidden clock or RNG breaks it."""
        from ..detector import detect
        from ..params import DetectorParams
        from .conformance import SPEC_VERSION
        from .fixtures_io import GOLDEN_DIR, load_expected, load_series

        for fixture_id in golden_fixture_ids():
            expected = load_expected(fixture_id)
            series = load_series(os.path.join(GOLDEN_DIR, fixture_id, "input.csv"))
            params = DetectorParams.from_fixture_params(
                expected["params"], spec_version=SPEC_VERSION
            )
            first = detect(series, params)
            second = detect(series, params)
            self.assertEqual(
                [r.as_tuple() for r in first.transitions],
                [r.as_tuple() for r in second.transitions],
                fixture_id,
            )


class A3NoReferenceModel(unittest.TestCase):
    """E2-AUTHOR-A's executable senses, asserted from inside the engine's own suite.

    The engine must not **import, copy, execute or mechanically translate** the
    reference model.  Import and execution are statically detectable and are
    checked here.  Rather than naming one file, the check forbids **every**
    sibling top-level directory of the repository except the fixture data, so a
    successor model is covered without this file being edited — and without this
    file spelling a quarantined path.

    Copying and mechanical translation are assessed by a reader comparing
    structure, control flow, naming and constant derivation.  That is a check no
    test can perform, and this one does not pretend to.
    """

    def test_no_engine_source_references_a_forbidden_sibling_directory(self) -> None:
        forbidden = sibling_directories()
        self.assertTrue(forbidden, "no sibling directories found; the check is vacuous")
        for name, source in _engine_sources().items():
            if name == "tests/" + os.path.basename(__file__):
                continue  # this file derives the names in order to forbid them
            for directory in forbidden:
                self.assertNotIn(
                    directory + "/",
                    source,
                    "%s references a forbidden sibling directory" % name,
                )
                self.assertNotIn(
                    '"%s"' % directory,
                    source,
                    "%s names a forbidden sibling directory" % name,
                )

    def test_the_forbidden_set_is_derived_and_non_empty(self) -> None:
        """Anti-vacuity: if the derivation ever returns nothing, the check above
        passes while asserting nothing."""
        self.assertGreaterEqual(len(sibling_directories()), 3)
        self.assertNotIn("engine", sibling_directories())

    def test_nothing_under_engine_can_execute_an_external_process(self) -> None:
        for name in PRODUCT_MODULES:
            for imported in _imported_names(_parse(os.path.join(ENGINE_DIR, name))):
                for banned in ("subprocess", "runpy"):
                    self.assertNotIn(banned, imported, "%s imports %r" % (name, imported))


class A4ClosedSets(unittest.TestCase):
    """The engine's sets must EQUAL the committed schema's, not merely be
    contained in them — drift in either direction is a defect."""

    def _schema_enums(self) -> Dict[str, Set[str]]:
        schema = load_json(SCHEMA_PATH)
        properties = schema["properties"]
        states = set(properties["expected_final_state"]["enum"])
        codes = set(properties["expected_reason_codes"]["items"]["enum"])
        transition = properties["expected_state_transitions"]["items"]["properties"]
        return {
            "states": states,
            "codes": codes,
            "transition_from": set(transition["from"]["enum"]),
            "transition_to": set(transition["to"]["enum"]),
            "transition_reason": set(transition["reason_code"]["enum"]),
        }

    def test_reason_codes_equal_the_schema(self) -> None:
        enums = self._schema_enums()
        self.assertEqual({code.value for code in ReasonCode}, enums["codes"])
        self.assertEqual({code.value for code in ReasonCode}, enums["transition_reason"])

    def test_line_states_equal_the_schema(self) -> None:
        enums = self._schema_enums()
        self.assertEqual({state.value for state in LineState}, enums["states"])
        self.assertEqual({state.value for state in LineState}, enums["transition_from"])
        self.assertEqual({state.value for state in LineState}, enums["transition_to"])

    def test_wick_break_is_not_a_state(self) -> None:
        self.assertNotIn("WICK_BREAK", {state.value for state in LineState})
        self.assertIn("WICK_BREAK", {code.value for code in ReasonCode})


class A5DerivedGate(unittest.TestCase):
    def test_the_harness_walks_the_directory(self) -> None:
        source = _source(os.path.join(TESTS_DIR, "test_conformance_golden.py"))
        self.assertIn("golden_fixture_ids()", source)
        walk_source = _source(os.path.join(TESTS_DIR, "fixtures_io.py"))
        for fixture_id in golden_fixture_ids():
            self.assertNotIn(
                fixture_id, walk_source, "the fixture walk names %s explicitly" % fixture_id
            )

    def test_every_committed_golden_directory_is_covered(self) -> None:
        from .test_conformance_golden import GoldenFixtureConformance

        generated = {
            name[len("test_"):].replace("_", "-").upper()
            for name in dir(GoldenFixtureConformance)
            if name.startswith("test_gx_")
        }
        self.assertEqual(generated, set(golden_fixture_ids()))


class ScopeDiscipline(unittest.TestCase):
    """Phase-3 scope creep, checked as a property of the source."""

    def test_no_phase_3_reason_code_is_ever_emitted(self) -> None:
        for name in PRODUCT_MODULES:
            if name == "state.py":
                continue  # the closed set must NAME them; it must not emit them
            source = _source(os.path.join(ENGINE_DIR, name))
            for token in (
                "ReasonCode.BREAKOUT_CONFIRMED",
                "ReasonCode.RETEST_HELD",
                "ReasonCode.FAILED_BREAKOUT",
                "ReasonCode.EXPIRED_POST_BREAKOUT",
            ):
                self.assertNotIn(token, source, "%s emits a Phase-3 reason code" % name)

    def test_no_phase_3_state_is_ever_assigned(self) -> None:
        for name in PRODUCT_MODULES:
            if name == "state.py":
                continue
            source = _source(os.path.join(ENGINE_DIR, name))
            for token in (
                "LineState.BROKEN_OUT",
                "LineState.RETESTED",
                "LineState.FAILED_BREAKOUT",
                "LineState.EXPIRED",
            ):
                self.assertNotIn(token, source, "%s assigns a Phase-3 state" % name)

    def test_engine_is_the_only_product_directory(self) -> None:
        product_like = {"src", "app", "lib", "server", "api", "worker", "scanner", "dashboard"}
        for name in os.listdir(REPO_ROOT):
            self.assertNotIn(
                name, product_like, "a product directory outside engine/ appeared: %s" % name
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
