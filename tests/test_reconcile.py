import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReconciliationNotebookTest(unittest.TestCase):
    def test_sample_classifies_each_observable_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "reconciliation.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "research/reconcile_live_vs_backtest.py"),
                    "--expected",
                    str(ROOT / "raw/reconciliation-expected-sample.csv"),
                    "--actual",
                    str(ROOT / "raw/reconciliation-actual-sample.csv"),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(
            report["summary"]["status_counts"],
            {
                "exact": 1,
                "timing_drift": 1,
                "price_drift": 1,
                "fee_drift": 1,
                "multi_factor_drift": 1,
                "missing_live": 1,
                "unexpected_live": 1,
            },
        )
        by_id = {row["trade_id"]: row for row in report["rows"]}
        self.assertEqual(
            by_id["T-005"]["discrepancy_flags"],
            ["timing", "price", "fee"],
        )
        self.assertEqual(by_id["T-006"]["status"], "missing_live")
        self.assertEqual(by_id["T-007"]["status"], "unexpected_live")

    def test_duplicate_trade_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            duplicate = Path(temporary) / "duplicate.csv"
            duplicate.write_text(
                "trade_id,strategy_id,symbol,side,entry_time_utc,exit_time_utc,quantity,entry_price,exit_price,fees_usd\n"
                "T-001,orb-v1,SPY,long,2024-01-02T15:00:00Z,2024-01-02T16:00:00Z,10,470,471,0.50\n"
                "T-001,orb-v1,SPY,long,2024-01-02T15:00:00Z,2024-01-02T16:00:00Z,10,470,471,0.50\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "research/reconcile_live_vs_backtest.py"),
                    "--expected",
                    str(duplicate),
                    "--actual",
                    str(ROOT / "raw/reconciliation-actual-sample.csv"),
                    "--output",
                    str(Path(temporary) / "out.json"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate trade_id: T-001", result.stderr)

    def test_shared_trade_id_detects_identity_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            actual = Path(temporary) / "actual.csv"
            actual.write_text(
                "trade_id,strategy_id,symbol,side,entry_time_utc,exit_time_utc,quantity,entry_price,exit_price,fees_usd\n"
                "T-001,orb-v1,SPY,short,2024-01-02T15:00:00Z,2024-01-02T16:00:00Z,10,470,471,0.50\n",
                encoding="utf-8",
            )
            output = Path(temporary) / "out.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "research/reconcile_live_vs_backtest.py"),
                    "--expected",
                    str(ROOT / "raw/reconciliation-expected-sample.csv"),
                    "--actual",
                    str(actual),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))

        by_id = {row["trade_id"]: row for row in report["rows"]}
        self.assertEqual(by_id["T-001"]["status"], "identity_drift")
        self.assertEqual(by_id["T-001"]["discrepancy_flags"], ["identity"])


if __name__ == "__main__":
    unittest.main()
