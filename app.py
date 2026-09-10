import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="NICU Guardian - Dragon Copilot Closed-Loop Care",
    page_icon="NG",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# THEME
# =============================================================================
COLORS = {
    "bg": "#030712",
    "panel": "#0b1220",
    "panel2": "#111827",
    "text": "#f8fafc",
    "muted": "#cbd5e1",
    "cyan": "#38e8ff",
    "blue": "#93c5fd",
    "violet": "#a78bfa",
    "green": "#4ade80",
    "amber": "#fbbf24",
    "red": "#fb7185",
    "pink": "#f0abfc",
}

SEVERITY_COLORS = {
    "Critical": COLORS["red"],
    "High": COLORS["amber"],
    "Medium": COLORS["blue"],
    "Closed": COLORS["green"],
    "Open": COLORS["cyan"],
}

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = [
    COLORS["cyan"],
    COLORS["violet"],
    COLORS["amber"],
    COLORS["green"],
    COLORS["blue"],
    COLORS["pink"],
]

st.markdown(
    """
    <style>
      :root {
        --bg:#030712;
        --panel:#0b1220;
        --panel2:#111827;
        --panel3:#172033;
        --text:#f8fafc;
        --muted:#cbd5e1;
        --soft:#e2e8f0;
        --cyan:#38e8ff;
        --blue:#93c5fd;
        --violet:#a78bfa;
        --green:#4ade80;
        --amber:#fbbf24;
        --red:#fb7185;
        --border:rgba(203,213,225,.24);
      }
      .stApp {
        background:
          radial-gradient(circle at 12% 0%, rgba(34,211,238,.18), transparent 28%),
          radial-gradient(circle at 80% 4%, rgba(139,92,246,.16), transparent 30%),
          radial-gradient(circle at 50% 96%, rgba(59,130,246,.10), transparent 32%),
          linear-gradient(180deg, #030712 0%, #08111f 46%, #020617 100%);
        color: var(--text);
      }
      .stApp, .stApp p, .stApp label, .stApp h1,
      .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp li {
        color: var(--text);
        font-family: "Segoe UI", Inter, Arial, sans-serif;
      }
      [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {
        font-family: "Segoe UI", Inter, Arial, sans-serif;
      }
      [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: "liga" !important;
        -webkit-font-smoothing: antialiased !important;
        font-feature-settings: "liga" !important;
      }
      .stApp h1, .stApp h2, .stApp h3 {
        color:#ffffff !important;
        font-weight:900 !important;
        letter-spacing:-.03em;
      }
      .stApp p, .stApp li, .stApp [data-testid="stMarkdownContainer"] {
        color:var(--soft) !important;
      }
      .stCaptionContainer, [data-testid="stCaptionContainer"] {
        color:#dbeafe !important;
        opacity:1 !important;
      }
      [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617, #0b1220);
        border-right: 1px solid var(--border);
      }
      [data-testid="stSidebar"] * { color:#dbeafe !important; }
      [data-testid="stSidebar"] [role="radiogroup"] label {
        background:rgba(15,23,42,.72);
        border:1px solid rgba(203,213,225,.12);
        border-radius:14px;
        padding:6px 8px;
        margin-bottom:4px;
      }
      .block-container {
        max-width: 100%;
        padding: .85rem 1.1rem 2.2rem 1.1rem;
      }
      .hero {
        border:1px solid rgba(56,232,255,.38);
        border-radius:30px;
        padding:26px 30px;
        margin-bottom:18px;
        background:
          radial-gradient(circle at 10% 0%, rgba(34,211,238,.28), transparent 34%),
          radial-gradient(circle at 82% 22%, rgba(139,92,246,.24), transparent 30%),
          linear-gradient(135deg, rgba(11,18,32,.99), rgba(3,7,18,.96));
        box-shadow: 0 28px 110px rgba(0,0,0,.42), inset 0 1px 0 rgba(255,255,255,.08);
      }
      .hero-title { color:#ffffff !important; font-size:2.45rem; font-weight:950; letter-spacing:-.045em; }
      .hero-sub { color:#e0f2fe !important; margin-top:7px; font-size:1.02rem; line-height:1.45; max-width:1180px; }
      .chip {
        display:inline-block; margin:12px 7px 0 0; padding:5px 11px; border-radius:999px;
        border:1px solid rgba(125,211,252,.36); color:#eff6ff !important;
        background:rgba(14,116,144,.18); font-size:.78rem; font-weight:800;
      }
      .dragon {
        display:inline-block; padding:0 7px 1px 7px; border-radius:999px;
        color:#fff !important; font-weight:950;
        background:linear-gradient(90deg, rgba(34,211,238,.34), rgba(139,92,246,.36));
        border:1px solid rgba(125,211,252,.42);
        box-shadow:0 0 24px rgba(34,211,238,.18);
      }
      .metric {
        border:1px solid var(--border); border-radius:20px; padding:16px 18px;
        min-height:126px;
        background:
          radial-gradient(circle at top right, rgba(56,232,255,.10), transparent 36%),
          linear-gradient(180deg, rgba(17,24,39,.98), rgba(11,18,32,.96));
        box-shadow: 0 18px 55px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.05);
      }
      .metric-label { color:#7dd3fc !important; font-size:.72rem; text-transform:uppercase; letter-spacing:.10em; font-weight:900; }
      .metric-value { color:#ffffff !important; font-size:1.9rem; font-weight:950; letter-spacing:-.035em; margin-top:4px; overflow-wrap:anywhere; }
      .metric-note { color:#dbeafe !important; font-size:.84rem; margin-top:5px; line-height:1.35; }
      .panel {
        border:1px solid var(--border); border-radius:22px; padding:18px 20px;
        background:linear-gradient(180deg, rgba(17,24,39,.98), rgba(11,18,32,.94));
      }
      .copilot {
        border:1px solid rgba(56,232,255,.42); border-radius:22px; padding:18px 20px;
        background:
          radial-gradient(circle at 14% 0%, rgba(56,232,255,.20), transparent 32%),
          radial-gradient(circle at 94% 8%, rgba(167,139,250,.18), transparent 28%),
          rgba(11,18,32,.98);
        box-shadow: 0 22px 70px rgba(8,47,73,.22);
      }
      .kicker { color:#67e8f9 !important; font-size:.72rem; text-transform:uppercase; letter-spacing:.11em; font-weight:850; }
      .line { color:#f8fafc !important; font-size:1rem; line-height:1.55; margin-top:8px; }
      .alert-card {
        border:1px solid var(--border); border-left:6px solid var(--amber);
        border-radius:18px; padding:15px 17px; margin-bottom:12px;
        background:rgba(11,18,32,.98);
      }
      .alert-critical { border-left-color: var(--red); background:linear-gradient(180deg, rgba(76,29,38,.84), rgba(11,18,32,.96)); }
      .alert-title { color:#ffffff !important; font-weight:930; font-size:1.02rem; }
      .alert-meta { color:#dbeafe !important; font-size:.85rem; margin-top:3px; }
      .alert-copy { color:#f1f5f9 !important; font-size:.91rem; line-height:1.42; margin-top:8px; }
      .status-pill {
        display:inline-block; padding:4px 9px; border-radius:999px; margin-right:6px;
        border:1px solid rgba(203,213,225,.30); background:rgba(2,6,23,.78);
        font-size:.74rem; font-weight:850;
      }
      .ok { color:#86efac !important; } .warn { color:#fcd34d !important; } .bad { color:#fecaca !important; }
      .stButton button {
        border-radius:14px !important;
        font-weight:900 !important;
        color:#e0f2fe !important;
        background:linear-gradient(135deg, rgba(14,116,144,.42), rgba(30,41,59,.96)) !important;
        border:1px solid rgba(125,211,252,.42) !important;
        box-shadow:0 12px 34px rgba(0,0,0,.25);
        min-height:3rem;
        white-space:normal;
      }
      .stButton button:hover {
        color:#ffffff !important;
        border-color:rgba(56,232,255,.78) !important;
        background:linear-gradient(135deg, rgba(8,145,178,.58), rgba(88,28,135,.52)) !important;
      }
      .stButton button[kind="primary"] {
        color:#ffffff !important;
        background:linear-gradient(135deg, #0891b2, #6d28d9) !important;
        border-color:rgba(186,230,253,.72) !important;
      }
      [data-testid="stHorizontalBlock"] { gap: .85rem; }
      .galaxy-card {
        border:1px solid rgba(125,211,252,.34);
        border-radius:26px;
        padding:18px 20px;
        background:
          radial-gradient(circle at 18% 0%, rgba(56,232,255,.18), transparent 34%),
          radial-gradient(circle at 82% 12%, rgba(167,139,250,.16), transparent 34%),
          linear-gradient(180deg, rgba(17,24,39,.98), rgba(11,18,32,.96));
        box-shadow: 0 24px 80px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.06);
      }
      .galaxy-title {color:#ffffff !important; font-size:1.15rem; font-weight:930; letter-spacing:-.02em; margin-bottom:5px;}
      .galaxy-copy {color:#e2e8f0 !important; font-size:.91rem; line-height:1.45;}
      .agent-chip {
        display:inline-block; padding:5px 10px; margin:0 6px 8px 0; border-radius:999px;
        border:1px solid rgba(125,211,252,.28); background:rgba(8,47,73,.22);
        color:#e0f2fe !important; font-size:.78rem; font-weight:820;
      }
      .multiverse-hero {
        border:1px solid rgba(56,232,255,.34);
        border-radius:30px;
        padding:20px 22px;
        background:
          radial-gradient(circle at 18% 8%, rgba(56,232,255,.20), transparent 32%),
          radial-gradient(circle at 88% 10%, rgba(167,139,250,.18), transparent 30%),
          linear-gradient(135deg, rgba(11,18,32,.98), rgba(3,7,18,.96));
        box-shadow:0 28px 110px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.08);
        margin-bottom:14px;
      }
      .multiverse-title {
        color:#ffffff !important;
        font-size:2.1rem;
        line-height:1.05;
        font-weight:950;
        letter-spacing:-.045em;
      }
      .multiverse-sub {color:#dbeafe !important; font-size:1rem; line-height:1.42; margin-top:8px; max-width:980px;}
      .why-card {
        border:1px solid rgba(251,191,36,.34);
        border-left:5px solid var(--amber);
        border-radius:20px;
        padding:15px 17px;
        background:linear-gradient(180deg, rgba(69,26,3,.42), rgba(11,18,32,.94));
        margin-bottom:10px;
      }
      .why-title {color:#ffffff !important; font-size:1rem; font-weight:920; margin-bottom:5px;}
      .why-copy {color:#fef3c7 !important; font-size:.9rem; line-height:1.38;}
      .mission-shell {
        display:grid;
        grid-template-columns: 1.15fr .95fr .9fr;
        gap:14px;
        align-items:stretch;
        margin-top:10px;
      }
      .mission-panel {
        border:1px solid rgba(125,211,252,.28);
        border-radius:24px;
        padding:16px 18px;
        background:
          radial-gradient(circle at 18% 0%, rgba(56,232,255,.12), transparent 34%),
          linear-gradient(180deg, rgba(15,23,42,.98), rgba(3,7,18,.96));
        box-shadow:0 20px 70px rgba(0,0,0,.26), inset 0 1px 0 rgba(255,255,255,.06);
        min-height:360px;
      }
      .mission-title {font-size:1.08rem; font-weight:950; color:#ffffff !important; margin-bottom:5px;}
      .mission-sub {font-size:.84rem; color:#cbd5e1 !important; margin-bottom:12px; line-height:1.34;}
      .nicu-bed-grid {
        display:grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap:9px;
      }
      .bed {
        border:1px solid rgba(203,213,225,.20);
        border-radius:14px;
        padding:9px 8px;
        min-height:66px;
        background:rgba(15,23,42,.90);
      }
      .bed-critical {border-color:rgba(251,113,133,.72); box-shadow:0 0 26px rgba(251,113,133,.20);}
      .bed-watch {border-color:rgba(251,191,36,.58); box-shadow:0 0 20px rgba(251,191,36,.14);}
      .bed-ready {border-color:rgba(74,222,128,.42);}
      .bed-id {font-size:.74rem; color:#93c5fd !important; font-weight:900;}
      .bed-score {font-size:1.1rem; color:#ffffff !important; font-weight:950; margin-top:2px;}
      .bed-state {font-size:.68rem; color:#dbeafe !important; margin-top:1px;}
      .pulse-ring {
        width:158px;
        height:158px;
        border-radius:50%;
        margin:0 auto 12px auto;
        display:flex;
        align-items:center;
        justify-content:center;
        background:
          radial-gradient(circle at center, #0b1220 0 52%, transparent 53%),
          conic-gradient(#fb7185 0 24%, #fbbf24 24% 63%, #38e8ff 63% 87%, rgba(148,163,184,.22) 87% 100%);
        box-shadow:0 0 48px rgba(56,232,255,.22);
      }
      .pulse-value {font-size:2rem; font-weight:950; color:#ffffff !important;}
      .action-row {
        display:grid;
        grid-template-columns: auto 1fr auto;
        gap:10px;
        align-items:center;
        padding:10px 0;
        border-bottom:1px solid rgba(148,163,184,.14);
      }
      .action-row:last-child {border-bottom:0;}
      .action-dot {
        width:14px;
        height:14px;
        border-radius:50%;
        box-shadow:0 0 18px currentColor;
      }
      .action-main {font-weight:900; color:#ffffff !important; font-size:.93rem;}
      .action-meta {color:#cbd5e1 !important; font-size:.78rem; margin-top:2px;}
      .action-owner {color:#7dd3fc !important; font-size:.75rem; font-weight:900;}
      @media (max-width: 1200px) {.mission-shell {grid-template-columns:1fr;} .nicu-bed-grid {grid-template-columns: repeat(4, minmax(0, 1fr));}}
      [data-testid="stDataFrame"] { color-scheme: dark; }
      [data-testid="stDataFrame"] * { color:#f8fafc !important; }
      [data-testid="stTable"] * { color:#f8fafc !important; }
      [data-testid="stExpander"] {
        background:rgba(11,18,32,.98) !important;
        border:1px solid rgba(125,211,252,.28) !important;
        border-radius:18px !important;
        overflow:visible !important;
        margin-top:14px !important;
      }
      [data-testid="stExpander"] details {
        background:rgba(11,18,32,.98) !important;
      }
      [data-testid="stExpander"] summary {
        min-height:52px !important;
        padding:14px 18px !important;
        background:linear-gradient(135deg, rgba(15,23,42,.98), rgba(30,41,59,.92)) !important;
        border-bottom:1px solid rgba(125,211,252,.18) !important;
      }
      [data-testid="stExpander"] summary * {
        color:#f8fafc !important;
        font-weight:850 !important;
        line-height:1.45 !important;
        white-space:normal !important;
        overflow:visible !important;
      }
      [data-testid="stExpander"] summary svg {
        color:#38e8ff !important;
        fill:#38e8ff !important;
      }
      [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
        color:transparent !important;
        flex:0 0 auto !important;
        width:0 !important;
        min-width:0 !important;
        max-width:0 !important;
        font-size:0 !important;
        overflow:hidden !important;
      }
      [data-testid="stExpander"] summary > span:first-child {
        width:26px !important;
        min-width:26px !important;
        max-width:26px !important;
        display:inline-flex !important;
        align-items:center !important;
        justify-content:center !important;
      }
      [data-testid="stExpander"] summary > span:first-child::before {
        content:">";
        color:#38e8ff !important;
        font-family:"Segoe UI", Inter, Arial, sans-serif !important;
        font-size:20px !important;
        font-weight:900 !important;
        line-height:1 !important;
      }
      [data-testid="stExpander"] summary p {
        margin:0 !important;
        padding-left:8px !important;
      }
      [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        background:transparent !important;
        color:#e2e8f0 !important;
      }
      [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background:rgba(11,18,32,.98) !important;
        padding:16px !important;
      }
      [data-testid="stAlert"] {
        background:rgba(11,18,32,.96);
        border:1px solid var(--border);
      }
      [data-testid="stAlert"] * { color:#f8fafc !important; }
      [data-baseweb="select"] *, [data-baseweb="input"] *, textarea, input { color:#f8fafc !important; }
      [data-baseweb="select"] > div, [data-baseweb="input"] > div, textarea, input {
        background-color:rgba(11,18,32,.98) !important; border-color:rgba(203,213,225,.30) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# DATA
# =============================================================================
BABY = {
    "name": "Baby Sky",
    "id": "NICU-017",
    "bed": "Pod B / Bed 14",
    "ga": "29w + 4d",
    "day": "Day 18",
    "primary": "Prematurity, respiratory support, feeding progression",
}

ROUNDS_TRANSCRIPT = """07:05 AM NICU rounds
Neonatologist: Let's advance feeds to 35 mL every three hours.
Respiratory Therapy: We can wean CPAP from 6 to 5 and check a blood gas two hours after the change.
Neonatologist: Repeat bilirubin at 4 PM. If it continues climbing, restart phototherapy.
Cardiology should see her today before we make the discharge plan.
Nurse: Parents still need CPR teaching and the car-seat challenge needs scheduling before discharge.
Neonatologist: If oral feeds continue improving, discharge this weekend is possible."""


BASE_COMMITMENTS = pd.DataFrame(
    [
        ["C-001", "Respiratory", "Wean CPAP 6 -> 5", "Respiratory Therapist + Bedside RN", "11:00", "CPAP documented at 5", "Closed", "High", 88, "Completed at 10:48"],
        ["C-002", "Nutrition", "Advance feeds to 35 mL q3h", "Bedside RN", "13:00", "Flowsheet shows 35 mL", "Closed", "Medium", 68, "Completed at 12:54"],
        ["C-003", "Lab follow-up", "Repeat bilirubin", "Bedside RN + Lab", "16:00", "No result by 16:20", "Overdue", "Critical", 97, "Escalate critical-result lane"],
        ["C-004", "Consult", "Cardiology consult before discharge plan", "Cardiology + Charge RN", "15:00", "Consult not acknowledged", "Unacknowledged", "Critical", 94, "Route owner confirmation"],
        ["C-005", "Family readiness", "Parent CPR teaching", "Nurse educator", "Before discharge", "Not scheduled", "Open", "High", 79, "Schedule education"],
        ["C-006", "Discharge test", "Car-seat challenge", "Bedside RN", "Before discharge", "Not scheduled", "Open", "High", 76, "Schedule test"],
        ["C-007", "Respiratory", "Blood gas two hours after CPAP wean", "RT + Lab", "13:00", "Result detected at 13:09", "Closed", "High", 82, "Closed loop"],
    ],
    columns=["id", "domain", "commitment", "owner", "due", "evidence", "status", "severity", "risk", "recommended_action"],
)

DISCHARGE_BLOCKERS = pd.DataFrame(
    [
        ["Respiratory stability", "Complete", 100, "CPAP weaned and tolerated"],
        ["Oral feeding", "In progress", 68, "Needs 80% PO for discharge readiness"],
        ["Bilirubin plan", "At risk", 42, "Repeat result overdue at 16:20"],
        ["Cardiology clearance", "Blocked", 25, "Consult not acknowledged"],
        ["Parent CPR education", "Not scheduled", 0, "Required before discharge"],
        ["Car-seat challenge", "Not scheduled", 0, "Required before discharge"],
    ],
    columns=["Requirement", "Status", "Readiness %", "Evidence"],
)

SHIFT_EVENTS = pd.DataFrame(
    [
        ["07:05", "Dragon Copilot captures rounds transcript", "Intent sensor"],
        ["07:07", "NICU Guardian extracts 7 commitments", "Workflow graph"],
        ["10:48", "CPAP wean completed", "EHR/flowsheet evidence"],
        ["12:54", "Feeds advanced to 35 mL", "EHR/flowsheet evidence"],
        ["15:00", "Cardiology consult due", "No acknowledgement"],
        ["15:05", "Guardian escalates consult ownership", "Exception engine"],
        ["16:20", "Bilirubin overdue", "Lab/EHR gap"],
        ["17:00", "Bilirubin result detected", "Loop can close"],
        ["19:00", "Incoming nurse requests delta handoff", "Dragon Copilot"],
    ],
    columns=["Time", "Event", "Source"],
)

STAFFING = pd.DataFrame(
    [["Bedside RN", 8, 10], ["Charge RN", 2, 3], ["RT", 3, 4], ["Neonatologist", 2, 2], ["Care coordinator", 1, 2], ["Nurse educator", 1, 2]],
    columns=["Role", "Available", "Required"],
)

CARE_TEAM = pd.DataFrame(
    [
        [
            "NICU Registered Nurses (RNs)",
            "Around-the-clock bedside monitoring, medication administration, parent coaching, holding, and bonding support.",
            "Bedside monitoring",
            "High",
            24,
        ],
        [
            "Respiratory Therapists (RTs)",
            "Ventilators, CPAP, oxygen therapy, respiratory weaning, and fragile-lung support.",
            "Respiratory stability",
            "Critical",
            18,
        ],
        [
            "Dietitians & Nutritionists",
            "Precise caloric, fluid, vitamin, and mineral planning so the baby grows steadily.",
            "Growth velocity",
            "Medium",
            9,
        ],
        [
            "Lactation Consultants",
            "Milk supply, pumping, breastfeeding transition, and family feeding confidence.",
            "Feeding progression",
            "Medium",
            7,
        ],
        [
            "Speech & Occupational Therapists (SLP/OT)",
            "Oral feeding, swallowing mechanics, early developmental therapy, and safe physical positioning.",
            "Safe oral feeding",
            "High",
            11,
        ],
        [
            "Social Workers & Case Managers",
            "Mental health support, insurance navigation, equipment coordination, and home-discharge setup.",
            "Discharge readiness",
            "High",
            13,
        ],
    ],
    columns=["Service provider", "Crucial role for the baby", "Guardian signal", "Priority", "Open tasks"],
)

OUTCOME_TRENDS = pd.DataFrame(
    {
        "Hour": ["07:00", "09:00", "11:00", "13:00", "15:00", "17:00", "19:00"],
        "Open commitments": [7, 7, 6, 4, 5, 4, 3],
        "Exception risk": [42, 48, 53, 61, 88, 93, 71],
        "Discharge readiness": [78, 78, 80, 82, 80, 84, 86],
        "Nursing cognitive load": [68, 72, 70, 78, 91, 86, 73],
    }
)

VALUE_CASE = pd.DataFrame(
    [
        ["Missed follow-up recovery", "20 min bilirubin delay surfaced", "Avoids silent workflow debt", 4.8],
        ["Consult acknowledgement", "Cardiology owner routed", "Prevents discharge-plan stall", 2.7],
        ["Shift handoff quality", "Delta handoff generated", "Reduces cognitive load at shift change", 1.9],
        ["Discharge readiness", "4 blockers visible", "Reduces avoidable LOS friction", 3.5],
    ],
    columns=["Value lever", "Demo proof", "Executive value", "Modeled value $M"],
)


def init_state():
    if "status_overrides" not in st.session_state:
        st.session_state.status_overrides = {}
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = [
            {
                "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "event": "DRAGON_TRANSCRIPT_RECEIVED",
                "actor": "Dragon Copilot",
                "commitment": "Rounds transcript",
                "details": "Ambient clinical conversation captured for workflow app.",
            },
            {
                "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "event": "COMMITMENTS_EXTRACTED",
                "actor": "NICU Guardian",
                "commitment": "7 commitments",
                "details": "Clinical intent converted into workflow graph.",
            },
        ]


init_state()


def commitments() -> pd.DataFrame:
    df = BASE_COMMITMENTS.copy()
    for cid, status in st.session_state.status_overrides.items():
        df.loc[df["id"] == cid, "status"] = status
        if status == "Closed":
            df.loc[df["id"] == cid, "evidence"] = "Closed by human-reviewed workflow action"
    return df


def add_audit(event: str, actor: str, commitment: str, details: str):
    st.session_state.audit_log.append(
        {
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event,
            "actor": actor,
            "commitment": commitment,
            "details": details,
        }
    )


def audit_with_hashes() -> pd.DataFrame:
    prev = "GENESIS"
    rows = []
    for event in st.session_state.audit_log:
        payload = json.dumps(event, sort_keys=True, separators=(",", ":"))
        event_hash = hashlib.sha256((prev + payload).encode()).hexdigest()
        rows.append({**event, "previous_hash": prev, "event_hash": event_hash})
        prev = event_hash
    return pd.DataFrame(rows)


def highlight_dragon(text) -> str:
    return str(text).replace("Dragon Copilot", "<span class='dragon'>Dragon Copilot</span>")


# =============================================================================
# UI HELPERS
# =============================================================================
def hero():
    st.markdown(
        """
        <div class="hero">
          <div class="hero-title">NICU Guardian</div>
          <div class="hero-sub"><b>From clinical conversation to closed-loop care with <span class="dragon">Dragon Copilot</span></b><br>
          Dragon captures clinical intent. NICU Guardian detects whether the care plan actually happened.</div>
          <span class="chip">Clinical intent sensor</span>
          <span class="chip">Intent vs reality monitor</span>
          <span class="chip">Exception command center</span>
          <span class="chip">Delta handoff intelligence</span>
          <span class="chip">Discharge readiness navigator</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric">
          <div class="metric-label">{highlight_dragon(label)}</div>
          <div class="metric-value">{highlight_dragon(value)}</div>
          <div class="metric-note">{highlight_dragon(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sparkline_svg(values, color=COLORS["cyan"]) -> str:
    values = np.asarray(values, dtype=float)
    lo, hi = values.min(), values.max()
    span = max(hi - lo, 1)
    points = []
    for i, v in enumerate(values):
        x = 5 + i * (110 / max(len(values) - 1, 1))
        y = 42 - ((v - lo) / span * 32)
        points.append(f"{x:.1f},{y:.1f}")
    return f"<svg viewBox='0 0 120 48' width='100%' height='42'><polyline points='{' '.join(points)}' fill='none' stroke='{color}' stroke-width='3.2' stroke-linecap='round'/><circle cx='{points[-1].split(',')[0]}' cy='{points[-1].split(',')[1]}' r='4' fill='{color}'/></svg>"


def spark_metric(label, value, delta, trend, color):
    st.markdown(
        f"""
        <div class="metric">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value} <span style="font-size:.9rem;color:{color};">{delta}</span></div>
          {sparkline_svg(trend, color)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def copilot_panel(title, prompt, answer):
    st.markdown(
        f"""
        <div class="copilot">
          <div class="kicker">{highlight_dragon(title)}</div>
          <div class="line"><b>Ask:</b> {prompt}</div>
          <div class="line"><b>{highlight_dragon('Dragon Copilot')}:</b> {answer}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status):
    klass = "ok" if status == "Closed" else "bad" if status in ["Overdue", "Unacknowledged"] else "warn"
    return f"<span class='status-pill {klass}'>{status}</span>"


def render_commitment_cards(df: pd.DataFrame):
    for _, row in df.sort_values(["risk"], ascending=False).head(5).iterrows():
        critical = "alert-critical" if row["severity"] == "Critical" and row["status"] != "Closed" else ""
        st.markdown(
            f"""
            <div class="alert-card {critical}">
              <div class="alert-title">{status_badge(row['status'])}{row['commitment']}</div>
              <div class="alert-meta">{row['id']} | {row['domain']} | Owner: {row['owner']} | Due: {row['due']} | Risk {int(row['risk'])}/100</div>
              <div class="alert-copy">Evidence: {row['evidence']}<br>Action: {row['recommended_action']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def bullet(label, actual, target, danger=85):
    color = COLORS["red"] if actual < 35 else COLORS["amber"] if actual < target else COLORS["green"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[100], y=[label], orientation="h", marker_color="rgba(148,163,184,.18)", showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Bar(x=[actual], y=[label], orientation="h", marker_color=color, showlegend=False, name="Actual"))
    fig.add_vline(x=target, line_color="#e5e7eb", line_width=3)
    fig.add_vrect(x0=danger, x1=100, fillcolor="rgba(34,197,94,.08)", line_width=0)
    fig.update_layout(barmode="overlay", height=120, title=f"{label}: {actual}% ready; target {target}%", xaxis_range=[0, 100], margin=dict(l=10, r=10, t=48, b=8))
    return fig


def apply_chart_theme(fig, height=None):
    fig.update_layout(
        paper_bgcolor="rgba(11,18,32,.96)",
        plot_bgcolor="rgba(3,7,18,.50)",
        font=dict(family="Segoe UI, Inter, Arial", color=COLORS["text"], size=13),
        title=dict(font=dict(color="#ffffff", size=16), x=.02, xanchor="left", y=.96),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font=dict(color="#e2e8f0", size=11),
        ),
        margin=dict(l=18, r=18, t=58, b=18),
        xaxis=dict(
            color="#e2e8f0",
            gridcolor="rgba(148,163,184,.16)",
            zerolinecolor="rgba(148,163,184,.22)",
            title_font=dict(color="#f8fafc"),
            tickfont=dict(color="#dbeafe"),
        ),
        yaxis=dict(
            color="#e2e8f0",
            gridcolor="rgba(148,163,184,.16)",
            zerolinecolor="rgba(148,163,184,.22)",
            title_font=dict(color="#f8fafc"),
            tickfont=dict(color="#dbeafe"),
        ),
        hoverlabel=dict(bgcolor="#020617", bordercolor="#38e8ff", font=dict(color="#f8fafc", size=13)),
    )
    if height:
        fig.update_layout(height=height)
    return fig


def intent_sankey(df: pd.DataFrame):
    labels = ["Dragon transcript", "Clinical commitments", "EHR/FHIR evidence", "Lab feed", "Task/consult queue", "Exceptions", "Owner routed", "Closed-loop care"]
    idx = {label: i for i, label in enumerate(labels)}
    open_count = int((df["status"] != "Closed").sum())
    closed_count = int((df["status"] == "Closed").sum())
    fig = go.Figure(
        go.Sankey(
            node=dict(label=labels, pad=18, thickness=18, color=[COLORS["violet"], COLORS["cyan"], COLORS["blue"], COLORS["amber"], COLORS["pink"], COLORS["red"], COLORS["amber"], COLORS["green"]]),
            link=dict(
                source=[idx["Dragon transcript"], idx["Clinical commitments"], idx["Clinical commitments"], idx["Clinical commitments"], idx["EHR/FHIR evidence"], idx["Lab feed"], idx["Task/consult queue"], idx["Exceptions"], idx["Owner routed"]],
                target=[idx["Clinical commitments"], idx["EHR/FHIR evidence"], idx["Lab feed"], idx["Task/consult queue"], idx["Closed-loop care"], idx["Exceptions"], idx["Exceptions"], idx["Owner routed"], idx["Closed-loop care"]],
                value=[7, 3, 2, 2, closed_count, 1, max(open_count - 1, 1), open_count, max(open_count - 1, 1)],
                color="rgba(34,211,238,.25)",
            ),
        )
    )
    fig.update_layout(title="Clinical intent to closed-loop care")
    return apply_chart_theme(fig, 430)


def journey_timeline():
    work = SHIFT_EVENTS.copy()
    work["Step"] = np.arange(1, len(work) + 1)
    fig = px.scatter(
        work,
        x="Time",
        y="Source",
        color="Source",
        size=[18] * len(work),
        hover_data=["Event"],
        title="NICU day timeline",
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="white")), text=None)
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        height=390,
        showlegend=False,
        margin=dict(l=12, r=12, t=46, b=12),
    )
    fig = apply_chart_theme(fig, 390)
    fig.update_layout(title_text="", showlegend=False, margin=dict(l=0, r=0, t=6, b=0))
    return fig


def executive_signal_ribbon():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=OUTCOME_TRENDS["Hour"],
        y=OUTCOME_TRENDS["Exception risk"],
        mode="lines+markers",
        name="Exception risk",
        line=dict(color=COLORS["red"], width=4, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(239,68,68,.12)",
    ))
    fig.add_trace(go.Scatter(
        x=OUTCOME_TRENDS["Hour"],
        y=OUTCOME_TRENDS["Discharge readiness"],
        mode="lines+markers",
        name="Discharge readiness",
        line=dict(color=COLORS["green"], width=4, shape="spline"),
    ))
    fig.add_trace(go.Scatter(
        x=OUTCOME_TRENDS["Hour"],
        y=OUTCOME_TRENDS["Nursing cognitive load"],
        mode="lines+markers",
        name="Nursing cognitive load",
        line=dict(color=COLORS["amber"], width=3, dash="dot", shape="spline"),
    ))
    fig.update_layout(title="Executive signal ribbon: risk, readiness, cognitive load", yaxis_title="Index", xaxis_title="")
    return apply_chart_theme(fig, 430)


def commitment_orbit(df: pd.DataFrame):
    work = df.copy()
    angles = np.linspace(0, 360, len(work), endpoint=False)
    radius = work["risk"] / 100
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radius,
        theta=angles,
        mode="markers+text",
        text=work["id"],
        textposition="top center",
        marker=dict(
            size=work["risk"] / 4,
            color=work["severity"].map(SEVERITY_COLORS),
            line=dict(color="white", width=1),
            opacity=.92,
        ),
        hovertext=work["commitment"] + "<br>Status: " + work["status"] + "<br>Owner: " + work["owner"],
        hovertemplate="%{hovertext}<extra></extra>",
        name="Commitments",
    ))
    fig.update_layout(
        title="Commitment orbit: every clinical intent has owner, evidence, and risk",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9)),
            angularaxis=dict(visible=False),
        ),
        showlegend=False,
    )
    return apply_chart_theme(fig, 430)


def value_waterfall():
    fig = go.Figure(go.Waterfall(
        x=VALUE_CASE["Value lever"],
        y=VALUE_CASE["Modeled value $M"],
        measure=["relative"] * len(VALUE_CASE),
        text=[f"${v:.1f}M" for v in VALUE_CASE["Modeled value $M"]],
        connector={"line": {"color": "rgba(148,163,184,.35)"}},
        increasing={"marker": {"color": COLORS["green"]}},
    ))
    fig.update_layout(title="Board story: modeled value unlocked by closed-loop care", yaxis_title="$M opportunity")
    fig = apply_chart_theme(fig, 390)
    fig.update_layout(title_text="", showlegend=False, margin=dict(l=4, r=4, t=6, b=4))
    return fig


def exception_heatmap(df: pd.DataFrame):
    pivot = pd.crosstab(df["domain"], df["status"]).reindex(columns=["Closed", "Open", "Unacknowledged", "Overdue"], fill_value=0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        text=pivot.values,
        texttemplate="%{text}",
        colorscale=[[0, "#020617"], [.35, "#0e7490"], [.72, "#f59e0b"], [1, "#ef4444"]],
        hovertemplate="%{y}<br>%{x}: %{z}<extra></extra>",
    ))
    fig.update_layout(title="Exception heatmap: domain by closure state", xaxis_title="", yaxis_title="")
    return apply_chart_theme(fig, 330)


def baby_system_star_map(df: pd.DataFrame):
    domains = ["Respiratory", "Nutrition", "Lab follow-up", "Consult", "Family readiness", "Discharge test"]
    status_score = {"Closed": .95, "Open": .55, "Acknowledged": .68, "Escalated": .72, "Unacknowledged": .22, "Overdue": .14}
    rows = []
    for i, domain in enumerate(domains):
        subset = df[df["domain"] == domain]
        if len(subset):
            risk = float(subset["risk"].max())
            status = subset.sort_values("risk", ascending=False).iloc[0]["status"]
            readiness = status_score.get(status, .45)
        else:
            risk, status, readiness = 35, "Open", .5
        angle = i / len(domains) * 2 * np.pi
        rows.append({
            "Domain": domain,
            "x": np.cos(angle) * readiness,
            "y": np.sin(angle) * readiness,
            "Risk": risk,
            "Status": status,
        })
    work = pd.DataFrame(rows)
    fig = go.Figure()
    for _, row in work.iterrows():
        fig.add_trace(go.Scatter(
            x=[0, row["x"]],
            y=[0, row["y"]],
            mode="lines",
            line=dict(width=3, color="rgba(148,163,184,.28)"),
            hoverinfo="skip",
            showlegend=False,
        ))
    fig.add_trace(go.Scatter(
        x=work["x"],
        y=work["y"],
        mode="markers+text",
        text=work["Domain"],
        textposition="top center",
        marker=dict(
            size=np.clip(work["Risk"] / 3, 16, 34),
            color=work["Status"].map(SEVERITY_COLORS).fillna(COLORS["amber"]),
            line=dict(color="#ffffff", width=1),
        ),
        hovertemplate="<b>%{text}</b><br>Status: %{customdata[0]}<br>Risk: %{customdata[1]}<extra></extra>",
        customdata=np.stack([work["Status"], work["Risk"]], axis=-1),
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers+text", text=["Baby Sky"], textposition="middle center", marker=dict(size=54, color=COLORS["violet"], line=dict(color="#ffffff", width=2)), showlegend=False))
    fig.update_layout(
        title="Baby Sky system star map",
        xaxis=dict(visible=False, range=[-1.25, 1.25]),
        yaxis=dict(visible=False, range=[-1.25, 1.25], scaleanchor="x", scaleratio=1),
        height=430,
    )
    return apply_chart_theme(fig, 430)


def scenario_impact(base_readiness: int, bilirubin_done: bool, cardiology_done: bool, education_done: bool) -> dict:
    lift = 0
    lift += 8 if bilirubin_done else 0
    lift += 10 if cardiology_done else 0
    lift += 7 if education_done else 0
    new_readiness = min(100, base_readiness + lift)
    risk_drop = lift * 1.8
    los_gain = lift / 25
    return {"readiness": new_readiness, "risk_drop": risk_drop, "los_gain": los_gain}


def scenario_waterfall(base_readiness: int, scenario: dict):
    fig = go.Figure(go.Waterfall(
        x=["Current", "Bilirubin closed", "Cardiology ack", "Family education", "Projected"],
        y=[base_readiness, 8, 10, 7, scenario["readiness"]],
        measure=["absolute", "relative", "relative", "relative", "total"],
        text=[f"{base_readiness}%", "+8", "+10", "+7", f"{scenario['readiness']}%"],
        connector={"line": {"color": "rgba(148,163,184,.35)"}},
        increasing={"marker": {"color": COLORS["green"]}},
        totals={"marker": {"color": COLORS["cyan"]}},
    ))
    fig.update_layout(title="Dragon scenario planner: discharge readiness lift", yaxis_title="Readiness %")
    return apply_chart_theme(fig, 360)


def governance_radar():
    categories = ["Human control", "Explainability", "Auditability", "Privacy boundary", "Action traceability", "Clinical safety"]
    score = [96, 88, 94, 86, 91, 98]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=score + [score[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="Guardian control maturity",
        line=dict(color=COLORS["cyan"], width=4),
        fillcolor="rgba(56,232,255,.18)",
    ))
    fig.update_layout(
        title="Governance control radar",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#dbeafe")), angularaxis=dict(tickfont=dict(color="#f8fafc"))),
        showlegend=False,
    )
    return apply_chart_theme(fig, 430)


def safety_case_map():
    controls = pd.DataFrame([
        ["Clinical intent capture", "Dragon Copilot transcript context", "Human-verifiable", "Ready"],
        ["Commitment extraction", "Structured workflow graph", "Explainable source sentence", "Ready"],
        ["Reality reconciliation", "FHIR/lab/task evidence check", "No diagnosis or treatment inference", "Ready"],
        ["Action routing", "Owner, escalation path, on-call directory", "Human approval required", "Ready"],
        ["Writeback boundary", "No autonomous EHR mutation", "Hard safety boundary", "Ready"],
        ["Model governance", "Synthetic rules + deterministic demo agent", "Needs clinical validation before production", "Pilot gate"],
    ], columns=["Capability", "Evidence", "Guardrail", "Maturity"])
    return controls


def bed_grid_html() -> str:
    beds = [
        ("A01", 41, "stable", "bed-ready"), ("A02", 55, "watch", "bed-watch"), ("A03", 37, "stable", "bed-ready"), ("A04", 62, "feeding", "bed-watch"),
        ("A05", 31, "ready", "bed-ready"), ("A06", 48, "labs", "bed-ready"), ("A07", 58, "handoff", "bed-watch"),
        ("B08", 73, "RT review", "bed-watch"), ("B09", 69, "CPAP", "bed-watch"), ("B10", 52, "feeds", "bed-ready"), ("B11", 81, "consult", "bed-watch"),
        ("B12", 64, "labs", "bed-watch"), ("B13", 46, "stable", "bed-ready"), ("B14", 97, "bilirubin", "bed-critical"),
        ("C15", 72, "transport", "bed-watch"), ("C16", 66, "oxygen", "bed-watch"), ("C17", 38, "stable", "bed-ready"), ("C18", 88, "handoff", "bed-critical"),
        ("C19", 43, "feeds", "bed-ready"), ("C20", 51, "family", "bed-ready"), ("ISO1", 78, "isolation", "bed-watch"),
    ]
    return "".join(
        f"<div class='bed {klass}'><div class='bed-id'>{bed}</div><div class='bed-score'>{score}</div><div class='bed-state'>{state}</div></div>"
        for bed, score, state, klass in beds
    )


def render_mission_pulse():
    st.markdown(
        """
        <div class="mission-panel">
          <div class="mission-title">NICU Pulse</div>
          <div class="mission-sub">One-glance board signal: capacity, exceptions, staffing, and discharge leverage.</div>
          <div class="pulse-ring"><div class="pulse-value">87%</div></div>
          <div class="action-row"><span class="action-dot" style="color:#fb7185;background:#fb7185;"></span><div><div class="action-main">4 high-risk babies</div><div class="action-meta">2 critical care-loop exceptions</div></div><div class="action-owner">NOW</div></div>
          <div class="action-row"><span class="action-dot" style="color:#fbbf24;background:#fbbf24;"></span><div><div class="action-main">2 staff gaps</div><div class="action-meta">RN/RT workload mismatch</div></div><div class="action-owner">+3H</div></div>
          <div class="action-row"><span class="action-dot" style="color:#4ade80;background:#4ade80;"></span><div><div class="action-main">3 discharge-ready</div><div class="action-meta">If admin blockers clear</div></div><div class="action-owner">+6H</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_live_bed_map():
    st.markdown(
        f"""
        <div class="mission-panel">
          <div class="mission-title">NICU Digital Twin</div>
          <div class="mission-sub">Every bed/incubator appears as a live operating object. Red = act now, amber = watch, green = stable/readiness.</div>
          <div class="nicu-bed-grid">{bed_grid_html()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_stack():
    actions = [
        ("#fb7185", "Repeat bilirubin overdue", "Baby Sky | Bed B14 | Lab/RN owner", "OPEN"),
        ("#fb7185", "Handoff exception forming", "Baby C18 | review overdue by 18 min", "OPEN"),
        ("#fbbf24", "Cardiology consult unacknowledged", "Baby Sky | discharge plan blocked", "ROUTE"),
        ("#38e8ff", "Parent CPR education unscheduled", "Baby Sky | discharge blocker", "PLAN"),
    ]
    rows = "".join(
        f"<div class='action-row'><span class='action-dot' style='color:{color};background:{color};'></span><div><div class='action-main'>{title}</div><div class='action-meta'>{meta}</div></div><div class='action-owner'>{action}</div></div>"
        for color, title, meta, action in actions
    )
    st.markdown(
        f"""
        <div class="mission-panel">
          <div class="mission-title">What blocks care?</div>
          <div class="mission-sub">Priority workbench. Each row can open a solution overlay instead of sending leaders into another report.</div>
          {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def clinical_trajectory_ribbon():
    rows = ["Respiratory", "Feeding", "Labs", "Consults", "Family readiness"]
    cols = ["07:00", "10:00", "13:00", "16:00", "19:00"]
    z = np.array([
        [48, 42, 38, 46, 44],
        [58, 52, 40, 38, 34],
        [35, 44, 51, 94, 62],
        [28, 33, 54, 88, 76],
        [60, 62, 66, 72, 74],
    ])
    fig = go.Figure(go.Heatmap(
        z=z,
        x=cols,
        y=rows,
        colorscale=[[0, "#102a43"], [.35, "#0891b2"], [.72, "#fbbf24"], [1, "#fb7185"]],
        text=z,
        texttemplate="%{text}",
        hovertemplate="%{y} at %{x}<br>Pressure: %{z}<extra></extra>",
    ))
    fig.update_layout(title="Baby Clinical Trajectory - one ribbon across systems", xaxis_title="", yaxis_title="", height=330)
    return apply_chart_theme(fig, 330)


def nicu_digital_twin(df: pd.DataFrame, horizon: int):
    beds = []
    pods = ["Pod A", "Pod B", "Pod C", "Isolation"]
    rng = np.random.default_rng(7 + horizon)
    open_risk = int(df[df["status"] != "Closed"]["risk"].mean())
    for p_i, pod in enumerate(pods):
        count = 8 if pod != "Isolation" else 4
        for bed in range(count):
            risk = int(np.clip(rng.normal(open_risk + p_i * 5, 18), 20, 99))
            status = "Critical" if risk > 86 else "Pressure" if risk > 68 else "Stable"
            beds.append([pod, bed + 1, p_i * 4 + bed % 4, bed // 4, risk, status])
    twin = pd.DataFrame(beds, columns=["Pod", "Bed", "x", "y", "Risk", "Status"])
    fig = px.scatter(
        twin,
        x="x",
        y="y",
        color="Status",
        size="Risk",
        color_discrete_map={"Critical": COLORS["red"], "Pressure": COLORS["amber"], "Stable": COLORS["green"]},
        hover_data=["Pod", "Bed", "Risk"],
        title=f"NICU Digital Twin - live bed/incubator field (+{horizon}h)",
    )
    for pod_i, pod in enumerate(pods):
        fig.add_annotation(x=pod_i * 4 + 1.5, y=2.15, text=pod, showarrow=False, font=dict(color="#e0f2fe", size=12))
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1), height=390, showlegend=True)
    fig = apply_chart_theme(fig, 390)
    fig.update_layout(title_text="", showlegend=False, margin=dict(l=0, r=0, t=6, b=0))
    return fig


def future_cone(intervention_strength: int, horizon: int):
    stable = min(72, 42 + intervention_strength * .5 + horizon * .8)
    escalation = max(8, 31 - intervention_strength * .35 + horizon * .15)
    sepsis = max(5, 19 - intervention_strength * .12)
    critical = max(2, 8 - intervention_strength * .08 + horizon * .05)
    total = stable + escalation + sepsis + critical
    vals = np.array([stable, escalation, sepsis, critical]) / total * 100
    labels = ["Stable", "Respiratory", "Sepsis", "Critical"]
    colors = [COLORS["green"], COLORS["amber"], COLORS["violet"], COLORS["red"]]
    fig = go.Figure()
    endpoints = [(4, 1.4, .65), (4, .35, .28), (4, -.65, .18), (4, -1.35, .08)]
    for i, (label, val) in enumerate(zip(labels, vals)):
        x = [0, 1.4, 2.8, endpoints[i][0]]
        y = [0, endpoints[i][1] * .35, endpoints[i][1] * .75, endpoints[i][1]]
        z = [0, endpoints[i][2] * .7, endpoints[i][2], endpoints[i][2]]
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines+markers",
            line=dict(color=colors[i], width=max(5, val / 2.2)),
            marker=dict(size=[9, 8, 8, 11], color=colors[i]),
            name=label,
            hovertemplate=f"{label}<br>Probability: {val:.1f}%<extra></extra>",
        ))
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers+text", text=["Now"], textposition="top center", marker=dict(size=18, color=COLORS["cyan"], line=dict(color="#ffffff", width=2)), name="Current"))
    fig.update_layout(
        title=None,
        height=390,
        showlegend=False,
        margin=dict(l=0, r=0, t=6, b=0),
        scene=dict(
            xaxis=dict(title="Time", visible=False),
            yaxis=dict(title="Trajectory", visible=False),
            zaxis=dict(title="Stability", visible=False),
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.6, y=1.8, z=.9)),
        ),
    )
    return apply_chart_theme(fig, 390)


def exception_gravity_map(df: pd.DataFrame):
    active = df[df["status"] != "Closed"].copy()
    active["theta"] = np.linspace(30, 330, len(active), endpoint=True)
    active["radius"] = 1.1 - active["risk"] / 120
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[0],
        theta=[0],
        mode="markers+text",
        text=["Baby 07"],
        textposition="middle center",
        marker=dict(size=42, color=COLORS["cyan"], line=dict(color="#ffffff", width=2)),
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=active["radius"],
        theta=active["theta"],
        mode="markers+text",
        text=active["id"],
        textposition="top center",
        marker=dict(size=np.clip(active["risk"] / 2.2, 18, 42), color=active["severity"].map(SEVERITY_COLORS), opacity=.92, line=dict(color="#ffffff", width=1)),
        customdata=np.stack([active["commitment"], active["status"], active["owner"], active["risk"]], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>Status: %{customdata[1]}<br>Owner: %{customdata[2]}<br>Risk: %{customdata[3]}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        title="Exception Gravity Map - urgency pulls closer to Baby 07",
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, range=[0, 1.05]), angularaxis=dict(visible=False)),
        height=390,
    )
    return apply_chart_theme(fig, 390)


def nicu_flow_river():
    labels = ["Expected deliveries", "EMS/transfer inbound", "Level IV NICU", "Pod A", "Pod B", "Pod C", "Step-down", "Discharge", "Diversion risk"]
    idx = {label: i for i, label in enumerate(labels)}
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=labels, pad=18, thickness=18, color=[COLORS["violet"], COLORS["blue"], COLORS["cyan"], COLORS["green"], COLORS["amber"], COLORS["red"], COLORS["green"], COLORS["green"], COLORS["red"]]),
        link=dict(
            source=[idx["Expected deliveries"], idx["EMS/transfer inbound"], idx["Level IV NICU"], idx["Level IV NICU"], idx["Level IV NICU"], idx["Pod B"], idx["Pod C"], idx["Step-down"]],
            target=[idx["Level IV NICU"], idx["Level IV NICU"], idx["Pod A"], idx["Pod B"], idx["Pod C"], idx["Step-down"], idx["Diversion risk"], idx["Discharge"]],
            value=[9, 7, 5, 8, 6, 4, 3, 5],
            color=["rgba(167,139,250,.30)", "rgba(147,197,253,.30)", "rgba(74,222,128,.26)", "rgba(251,191,36,.30)", "rgba(251,113,133,.30)", "rgba(74,222,128,.30)", "rgba(251,113,133,.42)", "rgba(74,222,128,.34)"],
        ),
    ))
    fig.update_layout(title="NICU Flow River - admissions to acuity, pods, transfer, discharge", height=420)
    return apply_chart_theme(fig, 420)


def care_constellation():
    nodes = pd.DataFrame([
        ["Baby 07", 0, 0, 52, COLORS["cyan"]],
        ["Respiratory", 0, 1.1, 26, COLORS["blue"]],
        ["Labs", -1.25, .25, 24, COLORS["amber"]],
        ["Feeding", 1.25, .25, 24, COLORS["green"]],
        ["Nurse", -.55, -1.05, 28, COLORS["violet"]],
        ["Physician", .55, -1.05, 28, COLORS["pink"]],
        ["Handoff exception", 0, -1.75, 32, COLORS["red"]],
        ["CPAP", .82, 1.04, 18, COLORS["blue"]],
        ["Bilirubin", -1.65, -.45, 20, COLORS["amber"]],
    ], columns=["Node", "x", "y", "Size", "Color"])
    edges = [("Baby 07", n) for n in ["Respiratory", "Labs", "Feeding", "Nurse", "Physician"]] + [("Respiratory", "CPAP"), ("Labs", "Bilirubin"), ("Nurse", "Handoff exception"), ("Physician", "Handoff exception")]
    pos = nodes.set_index("Node")[["x", "y"]].to_dict("index")
    fig = go.Figure()
    for a, b in edges:
        fig.add_trace(go.Scatter(x=[pos[a]["x"], pos[b]["x"]], y=[pos[a]["y"], pos[b]["y"]], mode="lines", line=dict(color="rgba(203,213,225,.24)", width=3), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=nodes["x"], y=nodes["y"], mode="markers+text", text=nodes["Node"], textposition="top center",
        marker=dict(size=nodes["Size"], color=nodes["Color"], line=dict(color="#ffffff", width=1)),
        hovertemplate="%{text}<extra></extra>", showlegend=False,
    ))
    fig.add_annotation(x=0, y=-2.08, text="Primary intervention: respiratory review overdue by 18 min", showarrow=False, font=dict(color="#fef3c7", size=12))
    fig.update_layout(title="Care Constellation - dependencies around Baby 07", xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1), height=420)
    return apply_chart_theme(fig, 420)


def predictive_capacity_horizon(intervention_strength: int):
    horizons = ["Now", "+1h", "+3h", "+6h", "+12h"]
    pressure = np.array([68, 74, 83, 91, 87]) - intervention_strength * np.array([0, .08, .18, .34, .42])
    capacity = 100 - pressure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=horizons, y=pressure, mode="lines+markers", name="Expected pressure", line=dict(color=COLORS["amber"], width=5, shape="spline"), fill="tozeroy", fillcolor="rgba(251,191,36,.16)"))
    fig.add_trace(go.Scatter(x=horizons, y=capacity, mode="lines+markers", name="Remaining capacity", line=dict(color=COLORS["cyan"], width=4, shape="spline")))
    fig.add_hline(y=85, line_dash="dash", line_color=COLORS["red"], annotation_text="storm threshold")
    fig.update_layout(title="Predictive Capacity Horizon - what is forming next", yaxis_title="Pressure / capacity index", xaxis_title="")
    return apply_chart_theme(fig, 350)


def clinical_event_galaxy():
    rng = np.random.default_rng(42)
    n = 280
    clusters = ["Respiratory", "Feeding", "Labs", "Meds", "Handoff", "Family readiness"]
    cluster_idx = rng.integers(0, len(clusters), n)
    x = rng.normal(cluster_idx * 1.1, .22)
    y = rng.normal(np.sin(cluster_idx) * .8, .24)
    anomaly = rng.random(n) > .91
    events = pd.DataFrame({"x": x, "y": y, "Cluster": [clusters[i] for i in cluster_idx], "Anomaly": anomaly})
    fig = px.scatter(events, x="x", y="y", color="Cluster", opacity=.72)
    fig.update_traces(marker=dict(size=8, line=dict(width=.4, color="rgba(255,255,255,.45)")))
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), height=390, showlegend=False, margin=dict(l=4, r=4, t=6, b=4))
    return apply_chart_theme(fig, 360)


def staffing_acuity_surface():
    pods = ["Pod A", "Pod B", "Pod C", "Isolation"]
    hours = ["Now", "+1h", "+3h", "+6h", "+12h"]
    z = np.array([
        [42, 48, 55, 58, 51],
        [62, 71, 83, 91, 86],
        [52, 59, 76, 88, 82],
        [35, 39, 48, 61, 58],
    ])
    fig = go.Figure(go.Surface(z=z, x=list(range(len(hours))), y=list(range(len(pods))), colorscale=[[0, "#0f172a"], [.45, "#0891b2"], [.75, "#fbbf24"], [1, "#fb7185"]]))
    fig.update_layout(
        title=None,
        height=390,
        showlegend=False,
        margin=dict(l=0, r=0, t=6, b=0),
        scene=dict(
            xaxis=dict(title="", tickmode="array", tickvals=list(range(len(hours))), ticktext=hours),
            yaxis=dict(title="", tickmode="array", tickvals=list(range(len(pods))), ticktext=pods),
            zaxis=dict(title=""),
            camera=dict(eye=dict(x=1.45, y=1.5, z=.95)),
        ),
    )
    return apply_chart_theme(fig, 390)


def why_now_panel():
    items = [
        ("4 contributing signals", "Respiratory trend 35% | pending clinician review 27% | abnormal lab trajectory 21% | handoff dependency 17%"),
        ("Primary operational intervention", "Respiratory review and bilirubin follow-up are overdue; route RT/RN owner confirmation now."),
        ("Likely next", "Without action, Pod B pressure crosses storm threshold within +6h and discharge readiness remains blocked."),
    ]
    for title, copy in items:
        st.markdown(f"<div class='why-card'><div class='why-title'>{title}</div><div class='why-copy'>{copy}</div></div>", unsafe_allow_html=True)


def staffing_dumbbell():
    work = STAFFING.sort_values("Required")
    fig = go.Figure()
    for _, row in work.iterrows():
        fig.add_trace(go.Scatter(x=[row["Available"], row["Required"]], y=[row["Role"], row["Role"]], mode="lines", line=dict(width=5, color=COLORS["red"] if row["Required"] > row["Available"] else COLORS["green"]), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=work["Available"], y=work["Role"], mode="markers", name="Available", marker=dict(color=COLORS["cyan"], size=12)))
    fig.add_trace(go.Scatter(x=work["Required"], y=work["Role"], mode="markers", name="Required", marker=dict(color=COLORS["amber"], size=12)))
    fig.update_layout(title="Staffing ratio deficit: available vs required", xaxis_title="Role slots", yaxis_title="")
    return apply_chart_theme(fig, 360)


def care_team_signal_chart():
    fig = px.bar(
        CARE_TEAM.sort_values("Open tasks"),
        x="Open tasks",
        y="Service provider",
        orientation="h",
        color="Priority",
        color_discrete_map={"Critical": COLORS["red"], "High": COLORS["amber"], "Medium": COLORS["blue"]},
        title="Multidisciplinary care-team workload signals",
        hover_data=["Guardian signal", "Crucial role for the baby"],
    )
    fig.update_layout(xaxis_title="Open Guardian-tracked tasks", yaxis_title="", showlegend=True)
    return apply_chart_theme(fig, 420)


def care_team_cards():
    for i in range(0, len(CARE_TEAM), 3):
        cols = st.columns(3)
        for col, (_, row) in zip(cols, CARE_TEAM.iloc[i:i + 3].iterrows()):
            with col:
                st.markdown(
                    f"""
                    <div class="galaxy-card">
                      <div class="kicker">{row['Guardian signal']}</div>
                      <div class="galaxy-title">{row['Service provider']}</div>
                      <div class="galaxy-copy">{row['Crucial role for the baby']}</div>
                      <span class="agent-chip">{row['Priority']} priority</span>
                      <span class="agent-chip">{int(row['Open tasks'])} open tasks</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def discharge_overview():
    readiness = int(DISCHARGE_BLOCKERS["Readiness %"].mean())
    return readiness


def commitment_by_id(cid: str) -> pd.Series:
    return commitments().loc[commitments()["id"] == cid].iloc[0]


def guardian_agent_answer(prompt: str, df: pd.DataFrame) -> str:
    p = prompt.lower()
    open_items = df[df["status"] != "Closed"].sort_values("risk", ascending=False)
    critical = open_items[open_items["severity"] == "Critical"]
    readiness = discharge_overview()
    if any(word in p for word in ["risk", "urgent", "attention", "critical"]):
        if critical.empty:
            return "No open Critical commitments remain. The highest remaining focus is discharge-readiness completion and shift handoff continuity."
        rows = critical.head(2)
        return "Highest risk: " + " ".join(
            f"**{r['id']} {r['commitment']}** is {r['status'].lower()} for {r['owner']}, due {r['due']}."
            for _, r in rows.iterrows()
        ) + " Recommended next step: open the one-click solution overlay and route owner accountability."
    if any(word in p for word in ["handoff", "shift", "changed", "delta"]):
        return (
            "Delta handoff: CPAP moved 6 -> 5, feeds advanced to 35 mL q3h, blood gas resulted, "
            "bilirubin follow-up became overdue, and cardiology consult remains unacknowledged. "
            "Discharge blockers: oral feeding, bilirubin plan, cardiology clearance, CPR education, car-seat challenge."
        )
    if any(word in p for word in ["discharge", "ready", "blocker", "los"]):
        blockers = DISCHARGE_BLOCKERS[DISCHARGE_BLOCKERS["Readiness %"] < 80]["Requirement"].tolist()
        return f"Discharge readiness is **{readiness}%**. Primary blockers: {', '.join(blockers)}. The most preventable administrative blockers are cardiology clearance, CPR education, and car-seat challenge scheduling."
    if any(word in p for word in ["staff", "nurse", "resource", "capacity"]):
        gap = STAFFING.assign(Gap=STAFFING["Required"] - STAFFING["Available"]).sort_values("Gap", ascending=False).iloc[0]
        return f"The strongest staffing signal is **{gap['Role']}**: {int(gap['Required'])} required vs {int(gap['Available'])} available, gap {int(gap['Gap'])}. This is an operational coverage signal, not an autonomous staffing decision."
    if any(word in p for word in ["team", "role", "provider", "rt", "lactation", "social", "dietitian", "slp", "ot"]) or "who should act" in p:
        top = CARE_TEAM.sort_values("Open tasks", ascending=False).head(3)
        return "Care-team focus: " + " ".join(
            f"**{r['Service provider']}** owns {r['Guardian signal'].lower()} ({int(r['Open tasks'])} open tasks)."
            for _, r in top.iterrows()
        ) + " NICU Guardian should route each open loop to the specific discipline that can close it."
    if any(word in p for word in ["audit", "governance", "safe", "guardrail"]):
        return "Governance posture: Dragon Copilot captures and summarizes intent; NICU Guardian routes workflow exceptions; humans acknowledge, escalate, or resolve. No diagnosis, treatment recommendation, or autonomous EHR writeback."
    if any(word in p for word in ["value", "roi", "executive", "board"]):
        total = VALUE_CASE["Modeled value $M"].sum()
        return f"Board story: closed-loop care can unlock a modeled **${total:.1f}M** opportunity across follow-up recovery, consult acknowledgement, handoff quality, and discharge readiness."
    return (
        "Ask me about current risk, shift handoff, discharge blockers, staffing, governance, or executive value. "
        "I answer from the synthetic NICU Guardian workflow graph, not external clinical advice."
    )


def guardian_chat(df: pd.DataFrame):
    if "guardian_chat" not in st.session_state:
        st.session_state.guardian_chat = [
            {
                "role": "assistant",
                "content": "I am the Guardian Agent embedded with Dragon Copilot context. Ask what is at risk, what changed, what blocks discharge, or what action to take.",
            }
        ]
    quick = st.columns(5)
    quick_prompts = [
        "What is at risk now?",
        "What changed since rounds?",
        "What blocks discharge?",
        "Which care team should act?",
        "Where is staffing constrained?",
    ]
    selected_prompt = None
    for col, label in zip(quick, quick_prompts):
        if col.button(label, key=f"quick_{label}", width="stretch"):
            selected_prompt = label
    for message in st.session_state.guardian_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    typed_prompt = st.text_input(
        "Ask Guardian Agent",
        placeholder="Ask about risk, handoff, discharge blockers, staffing, governance, or value...",
        key="guardian_agent_input",
    )
    ask_clicked = st.button("Ask Guardian Agent", type="primary", width="stretch")
    prompt = selected_prompt or (typed_prompt if ask_clicked and typed_prompt else None)
    if prompt:
        answer = guardian_agent_answer(prompt, df)
        st.session_state.guardian_chat.append({"role": "user", "content": prompt})
        st.session_state.guardian_chat.append({"role": "assistant", "content": answer})
        st.rerun()


@st.dialog("One-click operational solution")
def drilldown(cid: str):
    row = commitment_by_id(cid)
    st.markdown(f"### {row['commitment']}")
    st.error(f"{row['status']} | {row['severity']} | Risk {int(row['risk'])}/100")
    st.write(f"**Dragon-captured intent:** {row['commitment']}")
    st.write(f"**Expected owner:** {row['owner']}")
    st.write(f"**Due:** {row['due']}")
    st.write(f"**Reality check:** {row['evidence']}")

    solution = pd.DataFrame(
        [
            ["Direct owner", row["owner"], "Send accountable-owner request"],
            ["Charge RN escalation", "NICU Charge RN", "Escalate if no acknowledgement"],
            ["On-call directory", "Neonatology, RT, cardiology, lab liaison", "Open secure contact path"],
            ["Regional network", "Secondary NICU / transfer center", "Prepare capacity pathway if needed"],
        ],
        columns=["Path", "Resource", "Action"],
    )
    st.dataframe(solution, hide_index=True, width="stretch")

    a, b, c = st.columns(3)
    if a.button("Acknowledge", width="stretch"):
        st.session_state.status_overrides[cid] = "Acknowledged"
        add_audit("ACKNOWLEDGED", "Human reviewer", row["commitment"], "Acknowledged from one-click drilldown.")
        st.rerun()
    if b.button("Escalate", type="primary", width="stretch"):
        st.session_state.status_overrides[cid] = "Escalated"
        add_audit("ESCALATED", "Dragon Copilot action card", row["commitment"], f"Escalated to {row['owner']}.")
        st.rerun()
    if c.button("Resolve", width="stretch"):
        st.session_state.status_overrides[cid] = "Closed"
        add_audit("CLOSED", "Human reviewer", row["commitment"], "Closed after evidence review.")
        st.rerun()


# =============================================================================
# PAGES
# =============================================================================
st.sidebar.markdown("## NICU Guardian")
st.sidebar.markdown("Embedded <span class='dragon'>Dragon Copilot</span> workflow app", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Navigate",
    [
        "NICU Mission Control",
        "Guardian Command Center",
        "Guardian Agent",
        "Dragon Copilot Intake",
        "Baby Journey",
        "Handoff & Discharge",
        "Governance",
    ],
)
st.sidebar.divider()
st.sidebar.caption("Synthetic executive prototype. No clinical decision-making.")


df = commitments()
open_df = df[df["status"] != "Closed"]
critical_open = df[(df["severity"] == "Critical") & (df["status"] != "Closed")]
readiness = discharge_overview()


if page == "NICU Mission Control":
    hero()
    st.markdown(
        """
        <div class="multiverse-hero">
          <div class="multiverse-title">NICU Mission Control</div>
          <div class="multiverse-sub"><b>A productive command surface for anticipatory neonatal operations.</b><br>
          See what is happening, why it is happening, what is likely next, what blocks care, who needs to act, and which action clears the block.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    control_a, control_b, control_c = st.columns([.8, .8, 1.4])
    horizon = control_a.select_slider("Forecast horizon", options=[1, 3, 6, 12], value=6, format_func=lambda h: f"+{h}h")
    intervention_strength = control_b.slider("Intervention strength", 0, 100, 62, 5)
    scenario = scenario_impact(readiness, True, True, intervention_strength > 60)
    with control_c:
        copilot_panel(
            "Dragon Copilot command",
            "What action clears the block?",
            "Route bilirubin follow-up to Bedside RN + Lab now, escalate cardiology acknowledgement to Charge RN, and schedule family CPR education before shift handoff.",
        )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric("NICU pulse", "87%", "Capacity pressure forming")
    with k2:
        metric("High-risk babies", "4", "Require active dependency monitoring")
    with k3:
        metric("Staff gaps", "2", "RN/RT mismatch")
    with k4:
        metric("Discharge ready", "3", "Could free capacity if blockers clear")

    st.markdown("#### Live operating surface")
    row1_a, row1_b, row1_c = st.columns([1.25, .8, .95])
    with row1_a:
        render_live_bed_map()
    with row1_b:
        render_mission_pulse()
    with row1_c:
        render_action_stack()
        if st.button("Open bilirubin solution overlay", type="primary", width="stretch"):
            drilldown("C-003")

    st.markdown("#### Storytelling visuals")
    row2_a, row2_b = st.columns([1.05, .95])
    with row2_a:
        st.plotly_chart(clinical_trajectory_ribbon(), width="stretch")
    with row2_b:
        st.plotly_chart(care_constellation(), width="stretch")

    row3_a, row3_b, row3_c = st.columns([1, 1, 1])
    with row3_a:
        st.plotly_chart(predictive_capacity_horizon(intervention_strength), width="stretch")
    with row3_b:
        st.plotly_chart(nicu_flow_river(), width="stretch")
    with row3_c:
        st.plotly_chart(scenario_waterfall(readiness, scenario), width="stretch")

    st.markdown("#### Advanced views")
    st.caption("Executive summary of future risk, signal intelligence, and staffing pressure.")
    adv1, adv2, adv3 = st.columns(3)
    with adv1:
        st.markdown(
            """
            <div class="galaxy-card">
              <div class="galaxy-title">Future cone</div>
              <div class="metric-value">+12h</div>
              <div class="galaxy-copy">Projects where pressure is forming next, before it becomes an escalation.</div>
              <div class="agent-chip">Predictive view</div><div class="agent-chip">Capacity risk</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with adv2:
        st.markdown(
            """
            <div class="galaxy-card">
              <div class="galaxy-title">Clinical event galaxy</div>
              <div class="metric-value">280</div>
              <div class="galaxy-copy">Compresses cross-system events into recognizable patterns and exception clusters.</div>
              <div class="agent-chip">Pattern discovery</div><div class="agent-chip">Signal triage</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with adv3:
        st.markdown(
            """
            <div class="galaxy-card">
              <div class="galaxy-title">Staffing x acuity terrain</div>
              <div class="metric-value">91</div>
              <div class="galaxy-copy">Highlights role mismatch, acuity pressure, and where leadership attention is needed.</div>
              <div class="agent-chip">Acuity pressure</div><div class="agent-chip">Staffing fit</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="galaxy-card" style="margin-top:16px;">
          <div class="galaxy-title">Executive narrative: what this dashboard proves</div>
          <div class="galaxy-copy">
            This dashboard is designed for fast executive storytelling: what is happening, why it matters,
            what is likely next, what blocks care, who needs to act, and which Dragon Copilot-supported action clears the block.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


elif page == "Guardian Command Center":
    hero()
    st.markdown("### Executive dashboard")
    st.caption("One baby, one NICU day, one product thesis: Dragon Copilot captures intent; NICU Guardian proves whether care closed.")

    m = st.columns(5)
    with m[0]:
        metric("Clinical commitments", str(len(df)), "Extracted from Dragon Copilot rounds")
    with m[1]:
        metric("Open loops", str(len(open_df)), "Need owner/evidence/closure")
    with m[2]:
        metric("Critical exceptions", str(len(critical_open)), "One-click solution required")
    with m[3]:
        metric("Discharge readiness", f"{readiness}%", "Blocked by consult, bilirubin, education")
    with m[4]:
        metric("Projected LOS impact", "-0.6 days", "Modeled avoidable delay if blockers close")

    s = st.columns(4)
    with s[0]:
        spark_metric("Intent extraction", "7", "+7", [0, 0, 1, 3, 5, 7], COLORS["cyan"])
    with s[1]:
        spark_metric("Open-loop risk", "91", "+18", [48, 51, 57, 63, 73, 91], COLORS["amber"])
    with s[2]:
        spark_metric("Consult ageing", "3.1h", "+1.4h", [0, .4, 1.0, 1.8, 2.5, 3.1], COLORS["red"])
    with s[3]:
        spark_metric("Readiness drift", "84%", "+6", [78, 79, 80, 82, 83, 84], COLORS["green"])

    left, right = st.columns([1.1, .9])
    with left:
        st.plotly_chart(intent_sankey(df), width="stretch")
    with right:
        copilot_panel(
            "Embedded Dragon Copilot",
            "What is at risk right now?",
            "Two commitments need action: bilirubin follow-up is overdue and cardiology consult is unacknowledged. I recommend owner routing now and a charge nurse escalation if not acknowledged.",
        )
        render_commitment_cards(df)
        for cid in critical_open["id"].tolist():
            if st.button(f"Open solution for {cid}", key=f"cmd_{cid}", type="primary", width="stretch"):
                drilldown(cid)

    c1, c2 = st.columns([1.2, .8])
    with c1:
        st.plotly_chart(journey_timeline(), width="stretch")
        st.dataframe(SHIFT_EVENTS, hide_index=True, width="stretch", height=260)
    with c2:
        st.plotly_chart(bullet("Discharge readiness", readiness, 90), width="stretch")
    st.markdown("### Who closes the loop for the baby")
    care_team_cards()


elif page == "Guardian Agent":
    hero()
    st.markdown("### Guardian Agent")
    st.caption("Interactive agent grounded in this prototype's synthetic commitments, discharge blockers, staffing model, and audit trail.")
    left, right = st.columns([.72, 1.28])
    with left:
        metric("Context", BABY["id"], BABY["bed"])
        metric("Open loops", str(len(open_df)), "Agent can explain and route")
        metric("Audit events", str(len(st.session_state.audit_log)), "Human action trail")
        copilot_panel(
            "Agent scope",
            "Can you provide clinical advice?",
            "No. I can explain workflow risk, evidence gaps, owners, handoff deltas, discharge blockers, staffing signals, governance, and executive value.",
        )
    with right:
        guardian_chat(df)


elif page == "Dragon Copilot Intake":
    hero()
    st.markdown("### Dragon Copilot Clinical Intent Gateway")
    st.caption("A workflow-app concept: Dragon Copilot streams clinical conversation into NICU Guardian, which turns intent into monitored commitments and safe action cards.")

    gw = st.columns(4)
    with gw[0]:
        metric("Input", "Ambient rounds", "Transcript + patient context")
    with gw[1]:
        metric("Extraction", "7 intents", "Tasks, consults, follow-ups")
    with gw[2]:
        metric("Reconciliation", "EHR/FHIR/Lab", "Reality sensor")
    with gw[3]:
        metric("Output", "Action cards", "Human approval required")

    transcript = st.text_area("Ambient rounds transcript captured by Dragon Copilot", value=ROUNDS_TRANSCRIPT, height=250)
    if st.button("Extract clinical commitments", type="primary"):
        add_audit("COMMITMENTS_REEXTRACTED", "Dragon Copilot workflow app", "Rounds transcript", "User reran deterministic commitment extraction.")
        st.success("7 commitments extracted into the NICU Guardian workflow graph.")

    left, right = st.columns([1.2, .8])
    with left:
        st.dataframe(df[["id", "domain", "commitment", "owner", "due", "status", "severity", "risk"]], hide_index=True, width="stretch", height=330)
    with right:
        copilot_panel(
            "Dragon Copilot developer surface",
            "Convert this encounter into commitments and safety-bounded workflow actions.",
            "I detected follow-ups, consult dependencies, discharge tasks, and respiratory/lab commitments. I will not recommend treatment; I will route workflow ownership and evidence gaps.",
        )

    st.markdown("### Unique integration blueprint")
    blueprint = pd.DataFrame(
        [
            ["1. Capture", "Dragon Copilot", "Ambient conversation, note, transcript, patient context", "Clinical intent sensor"],
            ["2. Convert", "NICU Guardian", "Commitment extraction and workflow graph", "Turns speech into monitored care loops"],
            ["3. Compare", "EHR/FHIR/Lab", "Orders, observations, results, consult status, flowsheets", "Reality sensor"],
            ["4. Detect", "Exception engine", "Intent vs reality reconciliation", "Overdue/missing/conflicting action detection"],
            ["5. Act", "Dragon action card", "Brief, explain, draft, route, escalate", "Human-controlled action"],
        ],
        columns=["Stage", "Layer", "Inputs", "Differentiator"],
    )
    st.dataframe(blueprint, hide_index=True, width="stretch")
    st.plotly_chart(intent_sankey(df), width="stretch")


elif page == "Baby Journey":
    hero()
    st.markdown(f"### {BABY['name']} - {BABY['id']}")
    st.caption(f"{BABY['bed']} | GA {BABY['ga']} | {BABY['day']} | {BABY['primary']}")

    top = st.columns(4)
    with top[0]:
        metric("Respiratory", "CPAP 5", "Down from 6 after rounds")
    with top[1]:
        metric("Feeds", "35 mL q3h", "Advanced from 32 mL")
    with top[2]:
        metric("Bilirubin", "Overdue", "Repeat expected 16:00")
    with top[3]:
        metric("Cardiology", "Unacknowledged", "Blocks discharge plan")

    l, r = st.columns([1.15, .85])
    with l:
        st.plotly_chart(baby_system_star_map(df), width="stretch")
        st.dataframe(df[["id", "domain", "commitment", "due", "evidence", "status", "risk"]], hide_index=True, width="stretch", height=310)
    with r:
        copilot_panel(
            "Dragon Copilot delta",
            "What changed since rounds?",
            "CPAP was weaned from 6 to 5. Feeds advanced to 35 mL. Blood gas resulted. Cardiology remains unacknowledged and bilirubin follow-up is overdue.",
        )
        st.plotly_chart(staffing_dumbbell(), width="stretch")
    st.markdown("### Clean event timeline")
    t1, t2 = st.columns([1.1, .9])
    with t1:
        st.plotly_chart(journey_timeline(), width="stretch")
    with t2:
        st.dataframe(SHIFT_EVENTS, hide_index=True, width="stretch", height=330)


elif page == "Handoff & Discharge":
    hero()
    st.markdown("### Shift handoff and discharge readiness")
    st.caption("Dragon Copilot produces a delta handoff; NICU Guardian tracks unresolved discharge dependencies.")

    c1, c2 = st.columns([.9, 1.1])
    with c1:
        copilot_panel(
            "Incoming nurse handoff",
            "What do I need to know about Baby Sky?",
            "Since rounds: CPAP 6 to 5, feeds 32 to 35 mL, blood gas resulted, bilirubin was delayed, cardiology consult was escalated, and discharge blockers remain CPR education, car-seat challenge, feeding readiness, and cardiology clearance.",
        )
        st.plotly_chart(bullet("Discharge readiness", readiness, 90), width="stretch")
    with c2:
        st.dataframe(DISCHARGE_BLOCKERS, hide_index=True, width="stretch", height=310)
        blocker_fig = px.bar(DISCHARGE_BLOCKERS.sort_values("Readiness %"), x="Readiness %", y="Requirement", orientation="h", color="Status", title="Discharge dependency readiness")
        st.plotly_chart(apply_chart_theme(blocker_fig, 360), width="stretch")
    st.markdown("### Family-centered discharge support team")
    st.dataframe(CARE_TEAM[["Service provider", "Crucial role for the baby", "Guardian signal"]], hide_index=True, width="stretch", height=290)


elif page == "Governance":
    hero()
    st.markdown("### Governance and audit")
    st.caption("The app routes workflow accountability. It does not diagnose, prescribe, or autonomously change the EHR.")

    g = st.columns(4)
    with g[0]:
        metric("Human authority", "Required", "Reviewer owns final disposition")
    with g[1]:
        metric("Clinical decisioning", "Blocked", "No diagnosis/treatment output")
    with g[2]:
        metric("EHR mutation", "Blocked", "No autonomous writeback")
    with g[3]:
        metric("Audit chain", "Active", "Hash-chained actions")

    g1, g2 = st.columns([.9, 1.1])
    with g1:
        st.plotly_chart(governance_radar(), width="stretch")
    with g2:
        st.markdown("### Production safety case")
        st.dataframe(safety_case_map(), hide_index=True, width="stretch", height=340)
    st.markdown("### Audit ledger")
    st.dataframe(audit_with_hashes(), hide_index=True, width="stretch", height=330)


st.divider()
st.caption("NICU Guardian is a synthetic executive prototype. Dragon Copilot integration is represented as a workflow-app pattern for demo purposes; no clinical advice or autonomous care action is performed.")
