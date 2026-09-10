from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nicu_guardian.cli import run_demo


DATA_PATH = Path("data/sample/rounds_transcript.json")
OUTPUT_PATH = Path("demo_dashboard.html")


def main() -> None:
    output = run_demo(DATA_PATH, OUTPUT_PATH)
    print(f"Dashboard created: {output.resolve()}")


if __name__ == "__main__":
    main()
