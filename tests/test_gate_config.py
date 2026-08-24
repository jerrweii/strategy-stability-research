import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.gate_config import (
    ARTIFACT_ONE,
    EXPECTED_ARTIFACTS,
    freeze,
    record_publication,
)

LAUNCH = datetime(2026, 9, 1, tzinfo=timezone.utc)


class GateConfigTest(unittest.TestCase):
    def test_freeze_records_artifact_one_and_exact_cutoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            data = freeze(path, "https://example.test/a", LAUNCH, "+00:00")
            self.assertEqual(
                data["cutoff_at"],
                (LAUNCH + timedelta(days=14)).isoformat(),
            )
            self.assertEqual(data["response_timezone"], "+00:00")
            self.assertEqual(set(data["artifacts"]), set(EXPECTED_ARTIFACTS))
            self.assertEqual(
                data["artifacts"][ARTIFACT_ONE]["published_at"],
                LAUNCH.isoformat(),
            )
            self.assertIsNone(
                data["artifacts"][EXPECTED_ARTIFACTS[1]]["published_at"]
            )
            self.assertIsNone(
                data["artifacts"][EXPECTED_ARTIFACTS[2]]["published_at"]
            )

    def test_freeze_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            freeze(path, "https://example.test/a", LAUNCH, "+00:00")
            with self.assertRaises(FileExistsError):
                freeze(
                    path,
                    "https://example.test/a",
                    LAUNCH + timedelta(days=1),
                    "+00:00",
                )

    def test_publish_records_followup_without_changing_clock(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            before = freeze(path, "https://example.test/a", LAUNCH, "+00:00")
            after = record_publication(
                path,
                EXPECTED_ARTIFACTS[1],
                "https://example.test/b",
                LAUNCH + timedelta(days=1),
            )
            self.assertEqual(after["launch_at"], before["launch_at"])
            self.assertEqual(after["cutoff_at"], before["cutoff_at"])
            self.assertEqual(
                after["artifacts"][EXPECTED_ARTIFACTS[1]]["url"],
                "https://example.test/b",
            )

    def test_publish_rejects_first_unknown_duplicate_and_late(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            freeze(path, "https://example.test/a", LAUNCH, "+00:00")
            with self.assertRaises(ValueError):
                record_publication(
                    path,
                    ARTIFACT_ONE,
                    "https://example.test/a2",
                    LAUNCH,
                )
            with self.assertRaises(ValueError):
                record_publication(
                    path,
                    "unknown",
                    "https://example.test/x",
                    LAUNCH,
                )
            record_publication(
                path,
                EXPECTED_ARTIFACTS[1],
                "https://example.test/b",
                LAUNCH + timedelta(days=1),
            )
            with self.assertRaises(ValueError):
                record_publication(
                    path,
                    EXPECTED_ARTIFACTS[1],
                    "https://example.test/b2",
                    LAUNCH + timedelta(days=2),
                )
            with self.assertRaises(ValueError):
                record_publication(
                    path,
                    EXPECTED_ARTIFACTS[2],
                    "https://example.test/c",
                    LAUNCH + timedelta(days=14),
                )

    def test_freeze_requires_explicit_valid_response_timezone(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            with self.assertRaisesRegex(ValueError, "response_timezone"):
                freeze(path, "https://example.test/a", LAUNCH, "UTC")


if __name__ == "__main__":
    unittest.main()
