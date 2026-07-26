"""Run the whole engine suite from a clean checkout, with no network.

    python3 -m engine.tests.run_all

Standard library only — there is no third-party test dependency, so the suite
runs anywhere the engine runs.
"""

from __future__ import annotations

import os
import sys
import unittest


def build_suite() -> unittest.TestSuite:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, os.pardir, os.pardir))
    return unittest.defaultTestLoader.discover(start_dir=here, top_level_dir=root)


def main() -> int:
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(build_suite())
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
