# Hackathon Submission Notes

## Project name

NICU Guardian for Dragon Copilot

## One-line pitch

An AI safety loop that turns NICU rounds and handoffs into accountable follow-up actions visible until closure.

## Problem

NICU care teams create many commitments during rounds and handoffs. Some are documented, some are routed through chat, and some remain in memory. When ownership or timing is unclear, missed follow-ups can become hidden safety risk.

## Solution

NICU Guardian extends Dragon Copilot with workflow intelligence:

- extracts commitments from clinical conversation
- assigns owners and due windows
- scores risk using urgency, clinical impact, dependency, and ownership clarity
- routes actions to the right role
- creates a proof-of-closure dashboard

## Demo command

```powershell
python -m src.nicu_guardian.cli --output demo_dashboard.html
```

## Demo artifact

The command creates `demo_dashboard.html`, a standalone executive dashboard that can be opened locally or attached to a submission.

