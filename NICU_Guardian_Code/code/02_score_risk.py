from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nicu_guardian.extractor import extract_commitments
from src.nicu_guardian.ingest import load_transcript
from src.nicu_guardian.risk import score_commitments


DATA_PATH = Path("data/sample/rounds_transcript.json")


def main() -> None:
    transcript = load_transcript(DATA_PATH)
    commitments = extract_commitments(transcript)
    signals = score_commitments(commitments)

    print("Prioritized risk signals")
    print("========================")
    for signal in signals:
        print(f"{signal.level} | {signal.score}/100 | {signal.commitment.bed_id}")
        print(f"  {signal.commitment.action}")
        print(f"  reasons: {', '.join(signal.reasons)}")


if __name__ == "__main__":
    main()
