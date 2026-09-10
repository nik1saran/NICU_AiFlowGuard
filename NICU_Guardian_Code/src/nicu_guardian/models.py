from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptEntry:
    bed_id: str
    speaker: str
    text: str
    minutes_since_mentioned: int


@dataclass(frozen=True)
class Commitment:
    id: str
    bed_id: str
    source_speaker: str
    action: str
    owner_hint: str
    due_minutes: int
    dependency: str
    clinical_context: str
    minutes_since_mentioned: int


@dataclass(frozen=True)
class RiskSignal:
    commitment: Commitment
    score: int
    level: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RoutedAction:
    signal: RiskSignal
    owner_role: str
    next_step: str
    status: str

