"""Convenience wrapper to run the travel PoC demo without setting PYTHONPATH."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from travel_poc.demo import run_demo  # noqa: E402


if __name__ == "__main__":
    run_demo()
