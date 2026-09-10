from __future__ import annotations

import hashlib
import re

from .models import Commitment, TranscriptEntry


OWNER_PATTERNS = {
    "cardiology": "Cardiology",
    "bilirubin": "Resident",
    "medication": "Resident",
    "family": "Bedside clinician",
    "parents": "Bedside clinician",
    "respiratory": "Respiratory therapy",
    "oxygen": "Respiratory therapy",
}

DEPENDENCY_PATTERNS = {
    "before feeding": "feeding advancement",
    "before the evening medication": "medication adjustment",
    "before afternoon rounds": "family readiness",
    "after the next blood gas": "blood gas result",
}


def extract_commitments(entries: list[TranscriptEntry]) -> list[Commitment]:
    commitments: list[Commitment] = []
    for entry in entries:
        text = entry.text.strip()
        lowered = text.lower()
        if not _looks_actionable(lowered):
            continue
        commitments.append(
            Commitment(
                id=_stable_id(entry.bed_id, text),
                bed_id=entry.bed_id,
                source_speaker=entry.speaker,
                action=_summarize_action(text),
                owner_hint=_owner_hint(lowered),
                due_minutes=_due_minutes(lowered),
                dependency=_dependency(lowered),
                clinical_context=text,
                minutes_since_mentioned=entry.minutes_since_mentioned,
            )
        )
    return commitments


def _looks_actionable(text: str) -> bool:
    return any(token in text for token in ("follow up", "review", "prepare", "confirm", "need"))


def _owner_hint(text: str) -> str:
    for token, owner in OWNER_PATTERNS.items():
        if token in text:
            return owner
    return "Unclear owner"


def _dependency(text: str) -> str:
    for token, dependency in DEPENDENCY_PATTERNS.items():
        if token in text:
            return dependency
    return "none detected"


def _due_minutes(text: str) -> int:
    match = re.search(r"within\s+(\d+)\s+minutes", text)
    if match:
        return int(match.group(1))
    if "evening" in text:
        return 240
    if "afternoon" in text:
        return 180
    if "next" in text:
        return 90
    return 120


def _summarize_action(text: str) -> str:
    sentence = text.split(".")[0]
    return sentence[:140]


def _stable_id(bed_id: str, text: str) -> str:
    digest = hashlib.sha1(f"{bed_id}:{text}".encode("utf-8")).hexdigest()[:8]
    return f"commitment-{digest}"

