# Architecture

NICU Guardian is organized as a lightweight workflow intelligence layer around Dragon Copilot.

## Flow

```text
Rounds / handoff text
        |
        v
Commitment extraction
        |
        v
Risk scoring
        |
        v
Role routing
        |
        v
Dashboard + proof of closure
```

## Components

| Module | Responsibility |
| --- | --- |
| `models.py` | Shared data models for transcript entries, commitments, risk signals, and routed actions |
| `ingest.py` | Loads demo rounds and handoff records |
| `extractor.py` | Converts text into structured commitments |
| `risk.py` | Scores urgency, clinical impact, dependency pressure, and ownership clarity |
| `routing.py` | Assigns the best accountable role for each commitment |
| `dashboard.py` | Generates a standalone HTML dashboard |
| `cli.py` | Runs the end-to-end demo pipeline |

## Dragon Copilot integration concept

In a production implementation, Dragon Copilot would provide the ambient clinical transcript and structured note context. NICU Guardian would subscribe to the extracted conversation events and convert action-oriented statements into workflow commitments.

The prototype uses safe synthetic sample data to demonstrate the same flow without patient data.

