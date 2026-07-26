"""Engine-local test infrastructure and the conformance suite.

The modules in this package are the only place under ``engine/`` that touch the
filesystem: the engine itself is pure (architectural test A-2 asserts that, and
scopes its scan to the product modules, i.e. ``engine/*.py``).
"""
