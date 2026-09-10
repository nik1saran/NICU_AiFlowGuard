from __future__ import annotations

from .models import Commitment, RiskSignal


HIGH_IMPACT_TERMS = ("cardiology", "murmur", "bilirubin", "oxygen", "blood gas", "medication")


def score_commitments(commitments: list[Commitment]) -> list[RiskSignal]:
    signals = [score_commitment(commitment) for commitment in commitments]
    return sorted(signals, key=lambda signal: signal.score, reverse=True)


def score_commitment(commitment: Commitment) -> RiskSignal:
    score = 20
    reasons: list[str] = []

    if commitment.minutes_since_mentioned >= commitment.due_minutes:
        score += 35
        reasons.append("past due")
    elif commitment.minutes_since_mentioned >= commitment.due_minutes * 0.75:
        score += 22
        reasons.append("approaching due time")

    if any(term in commitment.clinical_context.lower() for term in HIGH_IMPACT_TERMS):
        score += 25
        reasons.append("clinical impact keyword")

    if commitment.dependency != "none detected":
        score += 15
        reasons.append(f"dependency: {commitment.dependency}")

    if commitment.owner_hint == "Unclear owner":
        score += 20
        reasons.append("unclear owner")
    else:
        score += 8
        reasons.append(f"owner hint: {commitment.owner_hint}")

    score = min(score, 100)
    return RiskSignal(commitment=commitment, score=score, level=_level(score), reasons=tuple(reasons))


def _level(score: int) -> str:
    if score >= 80:
        return "High"
    if score >= 55:
        return "Medium"
    return "Low"

