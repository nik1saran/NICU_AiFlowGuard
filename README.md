# NICU Guardian

FlowGuard AI for Dragon Copilot helps care teams detect, prioritize, and close clinical workflow risks before they become operational or patient-safety failures. It monitors signals such as unacknowledged critical results, overdue follow-ups, incomplete handoffs, bed-flow pressure, staffing demand, and family-communication readiness, then surfaces the highest-risk issues through Dragon Copilot as clear, clinician-ready action cards.

The business value is faster risk recognition, clearer accountability, reduced escalation friction, improved bed and staffing visibility, and stronger proof of closure. Instead of forcing teams to search across dashboards, messages, queues, and handoff notes, FlowGuard brings the most important operational risks into the clinician’s natural workflow.

The problem it solves is fragmented clinical operations. Hospitals often have the data needed to spot risk, but it is scattered across EHR systems, lab workflows, bed-management tools, staffing rosters, and care coordination processes. As a result, ownership can be unclear, critical follow-ups can age silently, and leaders may lack real-time confidence that high-risk workflows were actually resolved.

The approach is to use FlowGuard as an intelligence layer behind Dragon Copilot. FlowGuard normalizes operational signals, scores workflow risk, recommends the accountable role, generates next-step guidance, and records an audit trail. Dragon Copilot then becomes the conversational front door where clinicians can ask what needs attention, understand why an alert matters, take approved actions, and document closure while keeping humans in control.

## Run locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

```text
Repository: nik1saran/NICU_AiFlowGuard
Branch: main
Main file path: app.py
```

## Demo pages

- **NICU Mission Control** - high-signal command surface with live bed/incubator map, NICU pulse, priority action queue, Dragon Copilot command panel, clinical trajectory ribbon, care constellation, capacity horizon, flow river, and scenario impact planner.
- **Guardian Command Center** - executive dashboard for open clinical commitments, overdue follow-ups, unacknowledged consults, discharge blockers, and one-click solution drilldowns.
- **Guardian Agent** - interactive in-app agent grounded in the synthetic NICU commitment graph, discharge blockers, staffing model, value case, and audit trail.
- **Dragon Copilot Intake** - Clinical Intent Gateway showing how Dragon Copilot transcript context becomes structured commitments, reconciled evidence, and action cards.
- **Baby Journey** - one premature infant's NICU day with system star map, clean event timeline, intent, evidence, exceptions, and staffing pressure.
- **Handoff & Discharge** - Dragon Copilot delta handoff plus discharge readiness and unresolved blockers.
- **Governance** - human authority, no autonomous clinical decisioning, no autonomous EHR mutation, governance control radar, production safety-case map, and hash-chained audit events.

## Executive story

Most healthcare tools show what happened. NICU Guardian asks: **what was supposed to happen, did it happen, who owns it, and what must happen next?**

This is not a generic documentation or summarization demo. It is a focused operational workflow app for NICU care coordination, using Dragon Copilot as the clinical-intent and assistance layer.

## Important

Synthetic executive prototype only. It does not provide diagnosis, treatment recommendations, autonomous staffing decisions, or autonomous EHR writeback.
