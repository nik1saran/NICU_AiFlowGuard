from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.nicu_guardian.cli import run_demo
from src.nicu_guardian.extractor import extract_commitments
from src.nicu_guardian.ingest import load_transcript
from src.nicu_guardian.risk import score_commitments
from src.nicu_guardian.routing import route_signals


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA = ROOT / "data" / "sample" / "rounds_transcript.json"


class PipelineTests(unittest.TestCase):
    def test_pipeline_extracts_scores_and_routes_commitments(self) -> None:
        transcript = load_transcript(SAMPLE_DATA)
        commitments = extract_commitments(transcript)
        signals = score_commitments(commitments)
        actions = route_signals(signals)

        self.assertGreaterEqual(len(commitments), 4)
        self.assertEqual(len(actions), len(commitments))
        self.assertEqual(actions[0].signal.level, "High")
        self.assertTrue(actions[0].next_step)

    def test_demo_creates_dashboard_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dashboard.html"
            result = run_demo(SAMPLE_DATA, output)
            html = result.read_text(encoding="utf-8")

        self.assertIn("NICU Guardian", html)
        self.assertIn("Risk score", html)


if __name__ == "__main__":
    unittest.main()

