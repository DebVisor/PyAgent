"""Top-level package shim for tests that import `logic.*`.

This makes `import logic...` resolve to the sources under `src/logic` without
requiring changes to sys.path in every test. Kept minimal and safe.
"""
import os
__path__.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "logic"))
