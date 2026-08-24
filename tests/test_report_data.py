import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReportDataTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "raw/report-data.json").read_text(encoding="utf-8"))

    def test_measured_claims_are_pinned(self):
        self.assertEqual(self.data["artifact_id"], "bandtastic-field-note-01")
        self.assertEqual(
            self.data["headline"],
            "Nightly backtests pass. Hyperopt needs its own cadence.",
        )
        fixed = self.data["fixed_backtest"]
        self.assertEqual(fixed["wall_seconds"], [15.554923300005612, 15.674962000004598])
        self.assertEqual(fixed["peak_memory_bytes"], 594018304)
        self.assertEqual(fixed["trades"], 1676)
        hyperopt = self.data["hyperopt"]
        self.assertEqual(hyperopt["epochs"], 500)
        self.assertEqual(hyperopt["wall_seconds"], 2608.9872604999982)
        self.assertEqual(hyperopt["peak_memory_bytes"], 8927089524)
        self.assertEqual(self.data["oos"]["trades"], 22)

    def test_monthly_scenarios_include_all_runs(self):
        expected = [
            (1, 1, 30, 0.05420888501),
            (1, 6, 180, 0.32525331006),
            (5, 6, 900, 1.6262665503),
        ]
        actual = [
            (
                row["strategies"],
                row["windows_per_run"],
                row["jobs_per_month"],
                row["monthly_total_usd"],
            )
            for row in self.data["monthly_scenarios"]
        ]
        self.assertEqual(actual, expected)

    def test_limitations_prevent_overclaiming(self):
        limitations = " ".join(self.data["limitations"]).lower()
        for term in ("profitability", "robustness", "demand", "nfi"):
            self.assertIn(term, limitations)


if __name__ == "__main__":
    unittest.main()
