from __future__ import annotations

import argparse
from pathlib import Path

from .dashboard import render_dashboard
from .extractor import extract_commitments
from .ingest import load_transcript
from .risk import score_commitments
from .routing import route_signals


def run_demo(data_path: Path, output_path: Path) -> Path:
    transcript = load_transcript(data_path)
    commitments = extract_commitments(transcript)
    signals = score_commitments(commitments)
    routed_actions = route_signals(signals)
    return render_dashboard(routed_actions, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NICU Guardian demo pipeline.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/sample/rounds_transcript.json"),
        help="Path to the demo transcript JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("demo_dashboard.html"),
        help="Path for the generated dashboard HTML.",
    )
    args = parser.parse_args()
    output = run_demo(args.data, args.output)
    print(f"Created dashboard: {output.resolve()}")


if __name__ == "__main__":
    main()

