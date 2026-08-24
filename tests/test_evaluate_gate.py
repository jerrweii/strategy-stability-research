import json
import unittest

from scripts.evaluate_gate import evaluate_gate, normalize_email

ARTIFACTS = {
    "bandtastic-field-note-01": {
        "url": "https://example.test/a",
        "published_at": "2026-09-01T00:00:00+00:00",
    },
    "part-time-larry-decay-timeline-01": {
        "url": "https://example.test/b",
        "published_at": "2026-09-02T00:00:00+00:00",
    },
    "live-reconciliation-notebook-01": {
        "url": "https://example.test/c",
        "published_at": "2026-09-03T00:00:00+00:00",
    },
}
CONFIG = {
    "launch_at": "2026-09-01T00:00:00+00:00",
    "cutoff_at": "2026-09-15T00:00:00+00:00",
    "artifacts": ARTIFACTS,
}


def row(
    email,
    timestamp="2026-09-05T00:00:00+00:00",
    artifact="bandtastic-field-note-01",
):
    return {
        "Submitted at": timestamp,
        "Email": email,
        "Framework": "Freqtrade",
        "Number of live strategies": "1",
        "Current monitoring method": "manual reruns",
        "artifact_id": artifact,
        "page_version": "1.0.0",
        "source": "direct",
    }


class GateEvaluatorTest(unittest.TestCase):
    def test_normalizes_case_and_whitespace_but_not_provider_aliases(self):
        self.assertEqual(normalize_email(" Alice@Example.COM "), "alice@example.com")
        self.assertNotEqual(normalize_email("a.b@gmail.com"), normalize_email("ab@gmail.com"))
        self.assertNotEqual(normalize_email("a+one@gmail.com"), normalize_email("a@gmail.com"))

    def test_seven_fail_and_eight_pass(self):
        seven = [row(f"person{i}@example.com") for i in range(7)]
        self.assertEqual(evaluate_gate(seven, CONFIG, set())["result"], "FAIL")
        result = evaluate_gate(seven + [row("person7@example.com")], CONFIG, set())
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["included_unique_people"], 8)

    def test_exclusions_and_hash_only_ledger(self):
        rows = [
            row("dup@example.com"),
            row(" DUP@example.com ", "2026-09-06T00:00:00+00:00"),
            row("before@example.com", "2026-08-31T23:59:59+00:00"),
            row("after@example.com", "2026-09-15T00:00:00+00:00"),
            row("spam@example.com"),
            {**row("incomplete@example.com"), "Framework": ""},
            row("not-an-email"),
            row("unknown@example.com", artifact="unknown"),
        ]
        result = evaluate_gate(rows, CONFIG, {"spam@example.com"})
        self.assertEqual(result["included_unique_people"], 1)
        reasons = {item["reason"] for item in result["ledger"] if item["reason"]}
        self.assertTrue(
            {
                "duplicate",
                "prelaunch_test",
                "post_cutoff",
                "spam",
                "incomplete",
                "invalid_email",
            }.issubset(reasons)
        )
        serialized = json.dumps(result["ledger"])
        self.assertNotIn("@", serialized)
        self.assertTrue(all(len(item["email_sha256"]) == 64 for item in result["ledger"]))

    def test_missing_or_late_publication_forces_fail(self):
        eight = [row(f"person{i}@example.com") for i in range(8)]
        missing = json.loads(json.dumps(CONFIG))
        missing["artifacts"]["live-reconciliation-notebook-01"] = {
            "url": None,
            "published_at": None,
        }
        self.assertEqual(evaluate_gate(eight, missing, set())["result"], "FAIL")
        late = json.loads(json.dumps(CONFIG))
        late["artifacts"]["live-reconciliation-notebook-01"]["published_at"] = (
            "2026-09-15T00:00:00+00:00"
        )
        self.assertEqual(evaluate_gate(eight, late, set())["result"], "FAIL")


if __name__ == "__main__":
    unittest.main()
