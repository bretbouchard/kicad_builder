import sys
import pathlib


# Ensure the repository root is on sys.path so tests can import the
# `tools` package regardless of how pytest is invoked (pre-commit hooks,
# IDE runners, or from deeper working directories).
ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
