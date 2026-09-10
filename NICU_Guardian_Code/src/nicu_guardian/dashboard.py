from __future__ import annotations

from html import escape
from pathlib import Path

from .models import RoutedAction


def render_dashboard(actions: list[RoutedAction], output_path: str | Path) -> Path:
    output = Path(output_path)
    rows = "\n".join(_action_card(action) for action in actions)
    high = sum(1 for action in actions if action.signal.level == "High")
    medium = sum(1 for action in actions if action.signal.level == "Medium")
    monitoring = sum(1 for action in actions if action.status == "Monitoring")

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NICU Guardian Dashboard</title>
  <style>
    :root {{
      --bg: #04101f;
      --panel: rgba(7, 28, 45, 0.86);
      --cyan: #43e8ff;
      --mint: #4dffcf;
      --warning: #ffcf5a;
      --danger: #ff5f7d;
      --text: #f3fbff;
      --muted: #a9c8da;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      background:
        radial-gradient(circle at 78% 18%, rgba(67, 232, 255, 0.32), transparent 34rem),
        radial-gradient(circle at 18% 82%, rgba(77, 255, 207, 0.15), transparent 28rem),
        linear-gradient(135deg, #03101d 0%, #08264b 52%, #03101d 100%);
    }}
    .shell {{ max-width: 1180px; margin: 0 auto; padding: 42px 28px; }}
    .hero {{
      border: 1px solid rgba(67, 232, 255, 0.38);
      background: rgba(3, 14, 26, 0.72);
      border-radius: 28px;
      padding: 32px;
      box-shadow: 0 22px 80px rgba(0, 0, 0, 0.28);
    }}
    .eyebrow {{ color: var(--mint); letter-spacing: 0.16em; text-transform: uppercase; font-weight: 700; }}
    h1 {{ margin: 12px 0; font-size: clamp(2.4rem, 5vw, 4.7rem); line-height: 0.95; }}
    .subtitle {{ color: var(--muted); font-size: 1.25rem; max-width: 760px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin: 26px 0; }}
    .metric {{
      background: var(--panel);
      border: 1px solid rgba(67, 232, 255, 0.26);
      border-radius: 22px;
      padding: 22px;
    }}
    .metric strong {{ display: block; font-size: 2.2rem; }}
    .metric span {{ color: var(--muted); }}
    .feed {{ display: grid; gap: 16px; margin-top: 24px; }}
    .card {{
      background: var(--panel);
      border: 1px solid rgba(67, 232, 255, 0.28);
      border-left: 7px solid var(--cyan);
      border-radius: 22px;
      padding: 22px;
    }}
    .card.High {{ border-left-color: var(--danger); }}
    .card.Medium {{ border-left-color: var(--warning); }}
    .topline {{ display: flex; justify-content: space-between; gap: 16px; align-items: center; }}
    .level {{ border-radius: 999px; padding: 6px 12px; font-weight: 700; background: rgba(67, 232, 255, 0.14); }}
    .High .level {{ color: var(--danger); }}
    .Medium .level {{ color: var(--warning); }}
    .score {{ color: var(--mint); font-weight: 700; }}
    .action {{ font-size: 1.18rem; margin: 14px 0; }}
    .meta {{ color: var(--muted); display: grid; gap: 8px; }}
    @media (max-width: 760px) {{
      .metrics {{ grid-template-columns: 1fr; }}
      .topline {{ align-items: flex-start; flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="eyebrow">Dragon Copilot Healthcare Hackathon</div>
      <h1>NICU Guardian</h1>
      <p class="subtitle">A closed-loop AI safety layer that turns clinical conversation into accountable follow-up actions visible until closure.</p>
      <div class="metrics">
        <div class="metric"><strong>{high}</strong><span>high-priority loops</span></div>
        <div class="metric"><strong>{medium}</strong><span>medium-priority loops</span></div>
        <div class="metric"><strong>{monitoring}</strong><span>items in monitoring</span></div>
      </div>
    </section>
    <section class="feed">
      {rows}
    </section>
  </main>
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")
    return output


def _action_card(action: RoutedAction) -> str:
    signal = action.signal
    commitment = signal.commitment
    reasons = ", ".join(signal.reasons)
    return f"""<article class="card {escape(signal.level)}">
  <div class="topline">
    <span class="level">{escape(signal.level)} priority</span>
    <span class="score">Risk score {signal.score}/100</span>
  </div>
  <div class="action">{escape(commitment.action)}</div>
  <div class="meta">
    <span><strong>Bed:</strong> {escape(commitment.bed_id)}</span>
    <span><strong>Owner:</strong> {escape(action.owner_role)}</span>
    <span><strong>Next step:</strong> {escape(action.next_step)}</span>
    <span><strong>Why flagged:</strong> {escape(reasons)}</span>
    <span><strong>Status:</strong> {escape(action.status)}</span>
  </div>
</article>"""

