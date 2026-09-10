# Code Sections

Run these files from the repository root in sequence:

```powershell
python code\01_ingest_and_extract.py
python code\02_score_risk.py
python code\03_route_actions.py
python code\04_generate_dashboard.py
```

## Section map

| File | What it demonstrates |
| --- | --- |
| `01_ingest_and_extract.py` | Loads Dragon Copilot-style transcript text and extracts commitments |
| `02_score_risk.py` | Scores commitments by urgency, clinical impact, dependency, and ownership |
| `03_route_actions.py` | Routes high-priority actions to accountable roles |
| `04_generate_dashboard.py` | Builds the final HTML dashboard |

