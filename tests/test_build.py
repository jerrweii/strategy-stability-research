import json
import tempfile
import unittest
from pathlib import Path

from scripts.build import build, render

ROOT = Path(__file__).resolve().parents[1]


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(
            (ROOT / "raw/report-data.json").read_text(encoding="utf-8")
        )
        self.timeline_data = json.loads(
            (ROOT / "raw/orb-decay-timeline.json").read_text(encoding="utf-8")
        )

    def test_rendered_claims_and_order_are_exact(self):
        html = render(self.data, "testForm123", ROOT / "src")
        headline = "Nightly backtests pass. Hyperopt needs its own cadence."
        self.assertEqual(html.count(headline), 1)
        self.assertNotIn("Nightly Hyperopt does not", html)
        for value in (
            "15.6s",
            "594MB",
            "43m 29s",
            "8.31GiB",
            "$0.325",
            "22 trades",
        ):
            self.assertIn(value, html)
        self.assertLess(html.index('id="limits-title"'), html.index('id="request"'))
        self.assertNotIn("${", html)

    def test_tally_fallback_and_field_contract(self):
        html = render(self.data, "testForm123", ROOT / "src")
        self.assertIn(
            "https://tally.so/r/testForm123?artifact_id=bandtastic-field-note-01",
            html,
        )
        for field in (
            "Email",
            "Framework",
            "Number of live strategies",
            "Current monitoring method",
        ):
            self.assertIn(field, html)
        self.assertIn("No broker keys.", html)
        self.assertNotIn("Enter broker key", html)
        self.assertNotIn("repository upload", html.lower())

    def test_tutorial_timeline_is_measured_and_bounded(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build(
                ROOT / "raw/report-data.json",
                ROOT / "src",
                output,
                "testForm123",
            )
            html = (output / "tutorial-decay-audit/index.html").read_text(
                encoding="utf-8"
            )
        self.assertIn(
            "This ORB reconstruction never earned positive OOS expectancy",
            html,
        )
        self.assertIn("2017", html)
        self.assertIn("-0.319R", html)
        self.assertIn("This timeline describes that cited reconstruction only", html)
        self.assertNotIn("Larry's strategy decayed", html)
        self.assertIn(
            "artifact_id=part-time-larry-decay-timeline-01",
            html,
        )

    def test_empty_form_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Tally form ID is required"):
            render(self.data, "", ROOT / "src")

    def test_build_copies_only_public_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build(
                ROOT / "raw/report-data.json",
                ROOT / "src",
                output,
                "testForm123",
            )
            expected = {
                "index.html",
                "assets/styles.css",
                "assets/tally.js",
                "tutorial-decay-audit/index.html",
                "raw/report-data.json",
                "raw/verification.json",
                "raw/economics.json",
                "raw/tutorial-decay-audit.json",
                "raw/decay-run-manifest.schema.json",
                "raw/orb-decay-timeline.json",
            }
            actual = {
                str(path.relative_to(output)).replace("\\", "/")
                for path in output.rglob("*")
                if path.is_file()
            }
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
