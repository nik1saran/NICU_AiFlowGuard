from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nicu_guardian.extractor import extract_commitments
from src.nicu_guardian.ingest import load_transcript


DATA_PATH = Path("data/sample/rounds_transcript.json")


def main() -> None:
    transcript = load_transcript(DATA_PATH)
    commitments = extract_commitments(transcript)

    print("Extracted commitments")
    print("=====================")
    for commitment in commitments:
        print(f"{commitment.bed_id}: {commitment.action}")
        print(f"  owner hint: {commitment.owner_hint}")
        print(f"  due minutes: {commitment.due_minutes}")
        print(f"  dependency: {commitment.dependency}")


if __name__ == "__main__":
    main()
