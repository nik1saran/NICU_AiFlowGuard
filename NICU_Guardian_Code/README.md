# NICU Guardian for Dragon Copilot

NICU Guardian is a hackathon prototype that extends Dragon Copilot from ambient documentation into a closed-loop care coordination layer for the NICU.

The prototype turns rounds and handoff text into structured commitments, scores workflow risk, routes follow-up actions to the right owner, and generates an executive-ready safety dashboard.

## Project sections

| Section | Folder | Purpose |
| --- | --- | --- |
| 00 | `notebooks/00_project_overview` | Business problem, solution framing, and demo flow |
| 01 | `notebooks/01_commitment_extraction` | Extract commitments from rounds and handoff text |
| 02 | `notebooks/02_risk_scoring` | Score urgency, ownership health, dependencies, and clinical impact |
| 03 | `notebooks/03_routing_and_dashboard` | Route actions and generate the dashboard artifact |
| Source | `src/nicu_guardian` | Reusable application modules |
| Data | `data/sample` | Safe synthetic demo data |
| Docs | `docs` | Architecture and submission notes |

## Quick start

```powershell
python -m src.nicu_guardian.cli --output demo_dashboard.html
```

Open `demo_dashboard.html` in a browser to view the generated dashboard.

## Run tests

```powershell
python -m unittest discover -s tests
```

## What the demo shows

1. Dragon Copilot captures clinical conversation during rounds and handoffs.
2. NICU Guardian extracts commitments such as consult follow-ups, lab review, medication readiness, and family update preparation.
3. The risk engine prioritizes work using due time, clinical keywords, dependencies, and owner clarity.
4. The router maps each commitment to an accountable role.
5. The dashboard shows the prioritized safety feed and proof-of-closure status.

## Repository readiness

This folder is ready to upload to GitHub as the code portion of the hackathon submission. It includes:

- `README.md`
- `.gitignore`
- `requirements.txt`
- modular Python source
- sample demo data
- tests
- architecture and submission docs

