from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nicu_guardian.extractor import extract_commitments
from src.nicu_guardian.ingest import load_transcript
from src.nicu_guardian.risk import score_commitments
from src.nicu_guardian.routing import route_signals


DATA_PATH = Path("data/sample/rounds_transcript.json")


def main() -> None:
    transcript = load_transcript(DATA_PATH)
    commitments = extract_commitments(transcript)
    signals = score_commitments(commitments)
    actions = route_signals(signals)

    print("Routed actions")
    print("==============")
    for action in actions:
        print(f"{action.signal.commitment.bed_id} -> {action.owner_role}")
        print(f"  status: {action.status}")
        print(f"  next step: {action.next_step}")


if __name__ == "__main__":
    main()
