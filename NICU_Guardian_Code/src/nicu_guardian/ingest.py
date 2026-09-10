from __future__ import annotations

import json
from pathlib import Path

from .models import TranscriptEntry


def load_transcript(path: str | Path) -> list[TranscriptEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        TranscriptEntry(
            bed_id=item["bed_id"],
            speaker=item["speaker"],
            text=item["text"],
            minutes_since_mentioned=int(item["minutes_since_mentioned"]),
        )
        for item in data
    ]

