from __future__ import annotations

from .models import RiskSignal, RoutedAction


NEXT_STEPS = {
    "Cardiology": "Send focused consult acknowledgement request with bedside context.",
    "Resident": "Review clinical trend and document updated plan.",
    "Bedside clinician": "Prepare approved family update for human delivery.",
    "Respiratory therapy": "Confirm respiratory plan after dependency result is available.",
    "Unclear owner": "Escalate to charge nurse to assign accountable owner.",
}


def route_signals(signals: list[RiskSignal]) -> list[RoutedAction]:
    return [route_signal(signal) for signal in signals]


def route_signal(signal: RiskSignal) -> RoutedAction:
    role = signal.commitment.owner_hint
    return RoutedAction(
        signal=signal,
        owner_role=role,
        next_step=NEXT_STEPS.get(role, "Assign accountable owner and define closure proof."),
        status="Open" if signal.level in {"High", "Medium"} else "Monitoring",
    )

