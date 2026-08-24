# Strategy Stability Evidence Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first public, evidence-first GitHub Pages artifact from the verified Bandtastic spike, connect a private four-field Tally CTA, and provide auditable tooling for the locked three-artifact/eight-person demand gate without building a scheduler.

**Architecture:** A zero-framework static site is rendered at build time from a pinned public JSON summary. Python standard-library validators prevent headline, benchmark, and monthly-cost drift. Separate private gate tools freeze the non-resettable 14-day clock when Artifact 1 is first shared, record publication of all three artifacts, normalize and deduplicate Tally CSV responses, and produce a hashed ledger; raw emails never enter the public repository.

**Tech Stack:** Semantic HTML5, CSS, minimal vanilla JavaScript for progressive Tally popup enhancement, Python 3.13 standard library, `unittest`, GitHub Actions, GitHub Pages, Tally.

---

## Scope boundary

This plan delivers:

- Artifact 1: `bandtastic-field-note-01`.
- Shared Tally form contract.
- Shared three-artifact gate clock, publication ledger, and response evaluator.
- A local Git repository and launch-ready GitHub Pages workflow.

The campaign also requires separately designed value-first artifacts:

1. `part-time-larry-decay-timeline-01`.
2. `live-reconciliation-notebook-01`.

The clock starts when Artifact 1 is first shared externally. Artifacts 2 and 3 must publish inside that same 14-day window; missing or late artifacts fail the gate and never pause, reset, or extend it. Scheduler implementation remains out of scope until the campaign publishes all three artifacts, yields at least eight unique qualified people, and the later 25% automated-scheduling activation test passes.

## File map

```text
strategy-stability-research/
  .gitignore
  README.md
  docs/
    specs/2026-08-24-strategy-stability-evidence-ledger-design.md
    methodology.md
    gate-operations.md
  raw/
    report-data.json
    verification.json
    economics.json
  src/
    index.template.html
    styles.css
    tally.js
  scripts/
    build.py
    validate_report_data.py
    gate_config.py
    evaluate_gate.py
  tests/
    test_build.py
    test_evaluate_gate.py
    test_gate_config.py
    test_report_data.py
  .github/workflows/
    ci.yml
    pages.yml
  site/                         # generated and ignored locally
  private/                      # ignored: Tally CSV, spam list, gate config, ledger
```

Each file has one responsibility: public evidence data, static presentation, form enhancement, deterministic build, public-data validation, private clock/publication state, or private response evaluation.

### Task 1: Create the local artifact repository and commit the approved specification

**Files:**
- Create: `strategy-stability-research/.gitignore`
- Create: `strategy-stability-research/README.md`
- Copy: `docs/superpowers/specs/2026-08-24-strategy-stability-evidence-ledger-design.md` → `strategy-stability-research/docs/specs/2026-08-24-strategy-stability-evidence-ledger-design.md`

- [ ] **Step 1: Create an isolated local repository**

Run from `C:/Demo/Research`:

```bash
mkdir -p strategy-stability-research/docs/specs
cd strategy-stability-research
git init -b main
cp ../docs/superpowers/specs/2026-08-24-strategy-stability-evidence-ledger-design.md docs/specs/
```

Expected: an empty local `main` repository containing the approved specification. Do not create a GitHub remote.

- [ ] **Step 2: Add privacy and build-output exclusions**

Create `.gitignore`:

```gitignore
__pycache__/
*.pyc
.pytest_cache/
site/
private/
.env
.superpowers/
```

`private/` is load-bearing: raw Tally exports and email-derived ledgers must never be committed.

- [ ] **Step 3: Add repository scope**

Create `README.md`:

```markdown
# Strategy Stability Research

Independent, reproducible field notes about scheduled strategy validation for self-hosting algo traders.

Field Note 01 separates a pinned Freqtrade fixed-parameter backtest from Hyperopt and projects full-month unit costs. It makes no profitability or investment-performance claim.

## Demand gate

The locked campaign starts when Field Note 01 is first shared externally. Two additional value-first artifacts must publish in the same non-resettable 14-day window, and the campaign must yield eight unique qualified people. This repository does not implement a scheduler.
```

- [ ] **Step 4: Verify and commit locally**

```bash
git status --short
git add .gitignore README.md docs/specs/2026-08-24-strategy-stability-evidence-ledger-design.md
git commit -m "docs: add approved Evidence Ledger specification"
```

Expected: first local commit; no remote and no public side effect. This completes the previously blocked specification commit.

### Task 2: Pin the public benchmark data contract

**Files:**
- Create: `strategy-stability-research/raw/report-data.json`
- Copy: `Bandtastic-feasibility/benchmarks/verification.json` → `strategy-stability-research/raw/verification.json`
- Copy: `Bandtastic-feasibility/benchmarks/economics.json` → `strategy-stability-research/raw/economics.json`
- Test: `strategy-stability-research/tests/test_report_data.py`

- [ ] **Step 1: Write the failing public-data contract test**

Create `tests/test_report_data.py`:

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReportDataTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "raw/report-data.json").read_text(encoding="utf-8"))

    def test_measured_claims_are_pinned(self):
        self.assertEqual(self.data["artifact_id"], "bandtastic-field-note-01")
        self.assertEqual(self.data["headline"], "Nightly backtests pass. Hyperopt needs its own cadence.")
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
        expected = [(1, 1, 30, 0.05420888501), (1, 6, 180, 0.32525331006), (5, 6, 900, 1.6262665503)]
        actual = [
            (row["strategies"], row["windows_per_run"], row["jobs_per_month"], row["monthly_total_usd"])
            for row in self.data["monthly_scenarios"]
        ]
        self.assertEqual(actual, expected)

    def test_limitations_prevent_overclaiming(self):
        limitations = " ".join(self.data["limitations"]).lower()
        for term in ("profitability", "robustness", "demand", "nfi"):
            self.assertIn(term, limitations)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Confirm the test fails because data is absent**

```bash
python -m unittest tests.test_report_data -v
```

Expected: ERROR reading `raw/report-data.json`.

- [ ] **Step 3: Create the exact public summary**

Create `raw/report-data.json`:

```json
{
  "schema_version": 1,
  "artifact_id": "bandtastic-field-note-01",
  "page_version": "1.0.0",
  "publisher": "Strategy Stability Research",
  "headline": "Nightly backtests pass. Hyperopt needs its own cadence.",
  "verdict": "Technical gate passed for one 7.3 KB public strategy. Demand, provider pricing, and NFI-scale economics remain unproven.",
  "provenance": {
    "strategy": "Bandtastic",
    "strategy_commit": "eff78d3ce3456b52c68a4e9a33cc055a56b801ff",
    "strategy_url": "https://github.com/freqtrade/freqtrade-strategies/blob/eff78d3ce3456b52c68a4e9a33cc055a56b801ff/user_data/strategies/Bandtastic.py",
    "freqtrade_image": "freqtradeorg/freqtrade:2026.7",
    "image_digest": "sha256:da3428fde0f7f9f976eaafba8abc7eba42bf978f23e4808347e15d476ad9a643",
    "pairs": 10,
    "timeframe": "15m",
    "timerange": "20250101-20250701",
    "fee_each_side": 0.001
  },
  "fixed_backtest": {
    "wall_seconds": [15.554923300005612, 15.674962000004598],
    "peak_memory_bytes": 594018304,
    "trades": 1676,
    "profit_total_pct": -3.53,
    "profit_factor": 0.7583406681409702,
    "expectancy": -0.21066702968377082,
    "max_drawdown_pct": 4.48
  },
  "hyperopt": {
    "epochs": 500,
    "workers": 8,
    "wall_seconds": 2608.9872604999982,
    "peak_memory_bytes": 8927089524,
    "result_bytes": 53001014,
    "ephemeral_cache_bytes": 542235623
  },
  "oos": {
    "timerange": "20250701-20250901",
    "wall_seconds": 8.571204099993338,
    "peak_memory_bytes": 461792870,
    "trades": 22,
    "profit_total_pct": 0.06,
    "profit_factor": 2.2826535293031127,
    "expectancy": 0.25446216818181816,
    "max_drawdown_pct": 0.04
  },
  "monthly_scenarios": [
    {"strategies": 1, "windows_per_run": 1, "scheduled_runs_per_month": 30, "jobs_per_month": 30, "monthly_total_usd": 0.05420888501},
    {"strategies": 1, "windows_per_run": 6, "scheduled_runs_per_month": 30, "jobs_per_month": 180, "monthly_total_usd": 0.32525331006},
    {"strategies": 5, "windows_per_run": 6, "scheduled_runs_per_month": 30, "jobs_per_month": 900, "monthly_total_usd": 1.6262665503}
  ],
  "limitations": [
    "No profitability claim: the default fixed-parameter period lost 3.53%.",
    "No robustness claim: the untouched OOS replay contained only 22 trades.",
    "No demand validation: signup and activation gates have not run.",
    "No NFI-scale extrapolation: Bandtastic is 7.3 KB while current NFI strategies are materially larger.",
    "Illustrative cloud rates exclude orchestration, database, observability, support, paid data, retries, taxes, and idle capacity."
  ]
}
```

Copy verified public inputs:

```bash
cp ../Bandtastic-feasibility/benchmarks/verification.json raw/verification.json
cp ../Bandtastic-feasibility/benchmarks/economics.json raw/economics.json
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m unittest tests.test_report_data -v
git add raw tests/test_report_data.py
git commit -m "feat: pin public Bandtastic evidence contract"
```

Expected: 3 tests PASS.

### Task 3: Add build-time evidence validation

**Files:**
- Create: `strategy-stability-research/scripts/validate_report_data.py`
- Modify: `strategy-stability-research/tests/test_report_data.py`

- [ ] **Step 1: Add failing validator tests**

Insert before the existing `if __name__ == "__main__"` block:

```python
from scripts.validate_report_data import validate


class ValidatorTest(unittest.TestCase):
    def test_valid_contract_has_no_errors(self):
        data = json.loads((ROOT / "raw/report-data.json").read_text(encoding="utf-8"))
        self.assertEqual(validate(data), [])

    def test_rejects_incorrect_headline_and_monthly_math(self):
        data = json.loads((ROOT / "raw/report-data.json").read_text(encoding="utf-8"))
        data["headline"] = "Nightly Hyperopt does not pass."
        data["monthly_scenarios"][1]["jobs_per_month"] = 6
        errors = validate(data)
        self.assertIn("incorrect measured headline", errors)
        self.assertIn("monthly scenario 1 omits scheduled runs", errors)
```

- [ ] **Step 2: Verify import failure**

```bash
python -m unittest tests.test_report_data.ValidatorTest -v
```

Expected: FAIL importing `scripts.validate_report_data`.

- [ ] **Step 3: Implement the validator**

Create `scripts/validate_report_data.py`:

```python
import json
import sys
from pathlib import Path

CORRECT_HEADLINE = "Nightly backtests pass. Hyperopt needs its own cadence."


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("headline") != CORRECT_HEADLINE:
        errors.append("incorrect measured headline")
    if data.get("artifact_id") != "bandtastic-field-note-01":
        errors.append("unexpected artifact_id")
    for index, row in enumerate(data.get("monthly_scenarios", [])):
        expected_jobs = row.get("strategies", 0) * row.get("windows_per_run", 0) * row.get("scheduled_runs_per_month", 0)
        if row.get("jobs_per_month") != expected_jobs:
            errors.append(f"monthly scenario {index} omits scheduled runs")
    limitations = " ".join(data.get("limitations", [])).lower()
    for term in ("profitability", "robustness", "demand", "nfi"):
        if term not in limitations:
            errors.append(f"missing limitation: {term}")
    return errors


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "raw/report-data.json")
    errors = validate(json.loads(path.read_text(encoding="utf-8")))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run and commit**

```bash
python -m unittest tests.test_report_data -v
python scripts/validate_report_data.py raw/report-data.json
git add scripts/validate_report_data.py tests/test_report_data.py
git commit -m "test: guard Evidence Ledger claims"
```

Expected: tests PASS; CLI prints `validated raw/report-data.json`.

### Task 4: Implement the private unique-person gate evaluator

**Files:**
- Create: `strategy-stability-research/scripts/evaluate_gate.py`
- Create: `strategy-stability-research/tests/test_evaluate_gate.py`

- [ ] **Step 1: Write failing tests for unique-person counting**

Create `tests/test_evaluate_gate.py`:

```python
import json
import unittest

from scripts.evaluate_gate import evaluate_gate, normalize_email

ARTIFACTS = {
    "bandtastic-field-note-01": {"url": "https://example.test/a", "published_at": "2026-09-01T00:00:00+00:00"},
    "part-time-larry-decay-timeline-01": {"url": "https://example.test/b", "published_at": "2026-09-02T00:00:00+00:00"},
    "live-reconciliation-notebook-01": {"url": "https://example.test/c", "published_at": "2026-09-03T00:00:00+00:00"},
}
CONFIG = {
    "launch_at": "2026-09-01T00:00:00+00:00",
    "cutoff_at": "2026-09-15T00:00:00+00:00",
    "artifacts": ARTIFACTS,
}


def row(email, timestamp="2026-09-05T00:00:00+00:00", artifact="bandtastic-field-note-01"):
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
        self.assertTrue({"duplicate", "prelaunch_test", "post_cutoff", "spam", "incomplete", "invalid_email"}.issubset(reasons))
        serialized = json.dumps(result["ledger"])
        self.assertNotIn("@", serialized)
        self.assertTrue(all(len(item["email_sha256"]) == 64 for item in result["ledger"]))

    def test_missing_or_late_publication_forces_fail(self):
        eight = [row(f"person{i}@example.com") for i in range(8)]
        missing = json.loads(json.dumps(CONFIG))
        missing["artifacts"]["live-reconciliation-notebook-01"] = {"url": None, "published_at": None}
        self.assertEqual(evaluate_gate(eight, missing, set())["result"], "FAIL")
        late = json.loads(json.dumps(CONFIG))
        late["artifacts"]["live-reconciliation-notebook-01"]["published_at"] = "2026-09-15T00:00:00+00:00"
        self.assertEqual(evaluate_gate(eight, late, set())["result"], "FAIL")


if __name__ == "__main__":
    unittest.main()
```

Run before implementation:

```bash
python -m unittest tests.test_evaluate_gate -v
```

Expected: FAIL importing `scripts.evaluate_gate`.

- [ ] **Step 2: Implement deterministic evaluation**

Create `scripts/evaluate_gate.py` with these exact constants and interfaces:

```python
import csv
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

EXPECTED_ARTIFACTS = {
    "bandtastic-field-note-01",
    "part-time-larry-decay-timeline-01",
    "live-reconciliation-notebook-01"
}
REQUIRED_FIELDS = (
    "Email", "Framework", "Number of live strategies", "Current monitoring method",
    "artifact_id", "page_version", "source"
)
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalize_email(value: str) -> str:
    return unicodedata.normalize("NFKC", value.strip()).casefold()


def email_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def publications_complete(config: dict) -> bool:
    launch = parse_time(config["launch_at"])
    cutoff = parse_time(config["cutoff_at"])
    artifacts = config.get("artifacts", {})
    if set(artifacts) != EXPECTED_ARTIFACTS:
        return False
    for record in artifacts.values():
        if not record.get("url") or not record.get("published_at"):
            return False
        published = parse_time(record["published_at"])
        if not (launch <= published < cutoff):
            return False
    return True


def evaluate_gate(rows: list[dict], config: dict, spam_emails: set[str]) -> dict:
    launch = parse_time(config["launch_at"])
    cutoff = parse_time(config["cutoff_at"])
    spam = {normalize_email(value) for value in spam_emails}
    included: set[str] = set()
    ledger: list[dict] = []

    for row in sorted(rows, key=lambda item: parse_time(item["Submitted at"])):
        normalized = normalize_email(row.get("Email", ""))
        submitted = parse_time(row["Submitted at"])
        reason = ""
        if submitted < launch:
            reason = "prelaunch_test"
        elif submitted >= cutoff:
            reason = "post_cutoff"
        elif any(not row.get(field, "").strip() for field in REQUIRED_FIELDS):
            reason = "incomplete"
        elif not EMAIL.fullmatch(normalized):
            reason = "invalid_email"
        elif row["artifact_id"] not in EXPECTED_ARTIFACTS:
            reason = "incomplete"
        elif normalized in spam:
            reason = "spam"
        elif normalized in included:
            reason = "duplicate"
        else:
            included.add(normalized)

        ledger.append({
            "email_sha256": email_hash(normalized),
            "submitted_at": row["Submitted at"],
            "artifact_id": row.get("artifact_id", ""),
            "included": reason == "",
            "reason": reason
        })

    complete = publications_complete(config)
    count = len(included)
    return {
        "result": "PASS" if complete and count >= 8 else "FAIL",
        "artifacts_complete": complete,
        "included_unique_people": count,
        "required_unique_people": 8,
        "launch_at": config["launch_at"],
        "cutoff_at": config["cutoff_at"],
        "ledger": ledger
    }


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: evaluate_gate.py RESPONSES.csv CONFIG.json SPAM.txt OUTPUT.json", file=sys.stderr)
        return 2
    responses_path, config_path, spam_path, output_path = map(Path, sys.argv[1:])
    with responses_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    spam = {line.strip() for line in spam_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    result = evaluate_gate(rows, config, spam)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['result']}: {result['included_unique_people']}/8 unique people")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run tests and commit**

```bash
python -m unittest tests.test_evaluate_gate -v
git add scripts/evaluate_gate.py tests/test_evaluate_gate.py
git commit -m "feat: evaluate locked unique-person demand gate"
```

Expected: all synthetic gate cases PASS; ledger output has no raw email field.

### Task 5: Implement the non-resettable clock and three-artifact publication ledger

**Files:**
- Create: `strategy-stability-research/scripts/gate_config.py`
- Create: `strategy-stability-research/tests/test_gate_config.py`
- Create: `strategy-stability-research/docs/gate-operations.md`

- [ ] **Step 1: Write failing clock tests**

Create `tests/test_gate_config.py`:

```python
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.gate_config import ARTIFACT_ONE, EXPECTED_ARTIFACTS, freeze, record_publication

LAUNCH = datetime(2026, 9, 1, tzinfo=timezone.utc)


class GateConfigTest(unittest.TestCase):
    def test_freeze_records_artifact_one_and_exact_cutoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            data = freeze(path, "https://example.test/a", LAUNCH)
            self.assertEqual(data["cutoff_at"], (LAUNCH + timedelta(days=14)).isoformat())
            self.assertEqual(set(data["artifacts"]), set(EXPECTED_ARTIFACTS))
            self.assertEqual(data["artifacts"][ARTIFACT_ONE]["published_at"], LAUNCH.isoformat())
            self.assertIsNone(data["artifacts"][EXPECTED_ARTIFACTS[1]]["published_at"])
            self.assertIsNone(data["artifacts"][EXPECTED_ARTIFACTS[2]]["published_at"])

    def test_freeze_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            freeze(path, "https://example.test/a", LAUNCH)
            with self.assertRaises(FileExistsError):
                freeze(path, "https://example.test/a", LAUNCH + timedelta(days=1))

    def test_publish_records_followup_without_changing_clock(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            before = freeze(path, "https://example.test/a", LAUNCH)
            after = record_publication(
                path,
                EXPECTED_ARTIFACTS[1],
                "https://example.test/b",
                LAUNCH + timedelta(days=1),
            )
            self.assertEqual(after["launch_at"], before["launch_at"])
            self.assertEqual(after["cutoff_at"], before["cutoff_at"])
            self.assertEqual(after["artifacts"][EXPECTED_ARTIFACTS[1]]["url"], "https://example.test/b")

    def test_publish_rejects_first_unknown_duplicate_and_late(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gate.json"
            freeze(path, "https://example.test/a", LAUNCH)
            with self.assertRaises(ValueError):
                record_publication(path, ARTIFACT_ONE, "https://example.test/a2", LAUNCH)
            with self.assertRaises(ValueError):
                record_publication(path, "unknown", "https://example.test/x", LAUNCH)
            record_publication(path, EXPECTED_ARTIFACTS[1], "https://example.test/b", LAUNCH + timedelta(days=1))
            with self.assertRaises(ValueError):
                record_publication(path, EXPECTED_ARTIFACTS[1], "https://example.test/b2", LAUNCH + timedelta(days=2))
            with self.assertRaises(ValueError):
                record_publication(path, EXPECTED_ARTIFACTS[2], "https://example.test/c", LAUNCH + timedelta(days=14))


if __name__ == "__main__":
    unittest.main()
```

Run before implementation:

```bash
python -m unittest tests.test_gate_config -v
```

Expected: FAIL importing `scripts.gate_config`.

- [ ] **Step 2: Implement `scripts/gate_config.py`**

Create `scripts/gate_config.py`:

```python
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ARTIFACT_ONE = "bandtastic-field-note-01"
EXPECTED_ARTIFACTS = (
    ARTIFACT_ONE,
    "part-time-larry-decay-timeline-01",
    "live-reconciliation-notebook-01",
)


def iso(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def valid_url(value: str) -> bool:
    return value.startswith("https://") and len(value) > len("https://")


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def freeze(path: Path, artifact_one_url: str, launch_at: datetime) -> dict:
    if path.exists():
        raise FileExistsError(f"gate config already exists: {path}")
    if not valid_url(artifact_one_url):
        raise ValueError("Artifact 1 URL must be absolute HTTPS")
    launch = launch_at.astimezone(timezone.utc)
    config = {
        "launch_at": iso(launch),
        "cutoff_at": iso(launch + timedelta(days=14)),
        "artifacts": {
            ARTIFACT_ONE: {"url": artifact_one_url, "published_at": iso(launch)},
            EXPECTED_ARTIFACTS[1]: {"url": None, "published_at": None},
            EXPECTED_ARTIFACTS[2]: {"url": None, "published_at": None},
        },
    }
    write_atomic(path, config)
    return config


def record_publication(path: Path, artifact_id: str, url: str, published_at: datetime) -> dict:
    if artifact_id not in EXPECTED_ARTIFACTS:
        raise ValueError(f"unknown artifact_id: {artifact_id}")
    if artifact_id == ARTIFACT_ONE:
        raise ValueError("Artifact 1 is recorded only by freeze")
    if not valid_url(url):
        raise ValueError("publication URL must be absolute HTTPS")
    config = json.loads(path.read_text(encoding="utf-8"))
    record = config["artifacts"][artifact_id]
    if record["published_at"] is not None:
        raise ValueError(f"artifact already published: {artifact_id}")
    published = published_at.astimezone(timezone.utc)
    launch = parse_time(config["launch_at"])
    cutoff = parse_time(config["cutoff_at"])
    if not launch <= published < cutoff:
        raise ValueError("publication is outside the frozen campaign window")
    record.update({"url": url, "published_at": iso(published)})
    write_atomic(path, config)
    return config


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    freeze_parser = commands.add_parser("freeze")
    freeze_parser.add_argument("path", type=Path)
    freeze_parser.add_argument("artifact_one_url")
    publish_parser = commands.add_parser("publish")
    publish_parser.add_argument("path", type=Path)
    publish_parser.add_argument("artifact_id")
    publish_parser.add_argument("url")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    if args.command == "freeze":
        result = freeze(args.path, args.artifact_one_url, now)
    else:
        result = record_publication(args.path, args.artifact_id, args.url, now)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The CLI is:

```text
python scripts/gate_config.py freeze private/gate-config.json ARTIFACT_ONE_URL
python scripts/gate_config.py publish private/gate-config.json ARTIFACT_ID URL
```

Both commands use current UTC. No command accepts a reset or extension.

- [ ] **Step 3: Document operations**

`docs/gate-operations.md` states:

1. Confirm the exact first distribution post before freeze.
2. Run freeze immediately before sharing Artifact 1; this starts the immutable window.
3. Publish and record Artifacts 2/3 before cutoff; a miss fails the gate.
4. Export Tally CSV only at cutoff, manually review spam, then evaluate.
5. Never commit `private/`.
6. PASS permits only the cron-concierge activation test; no scheduler product.

- [ ] **Step 4: Run and commit**

```bash
python -m unittest tests.test_gate_config -v
git add scripts/gate_config.py tests/test_gate_config.py docs/gate-operations.md
git commit -m "feat: freeze immutable campaign clock"
```

### Task 6: Build the Evidence Ledger from validated data

**Files:**
- Create: `strategy-stability-research/src/index.template.html`
- Create: `strategy-stability-research/src/styles.css`
- Create: `strategy-stability-research/src/tally.js`
- Create: `strategy-stability-research/scripts/build.py`
- Create: `strategy-stability-research/tests/test_build.py`

- [ ] **Step 1: Write failing build tests**

Create `tests/test_build.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build import build, render

ROOT = Path(__file__).resolve().parents[1]


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "raw/report-data.json").read_text(encoding="utf-8"))

    def test_rendered_claims_and_order_are_exact(self):
        html = render(self.data, "testForm123", ROOT / "src")
        headline = "Nightly backtests pass. Hyperopt needs its own cadence."
        self.assertEqual(html.count(headline), 1)
        self.assertNotIn("Nightly Hyperopt does not", html)
        for value in ("15.6s", "594MB", "43m 29s", "8.31GiB", "$0.325", "22 trades"):
            self.assertIn(value, html)
        self.assertLess(html.index('id="limits-title"'), html.index('id="request"'))
        self.assertNotIn("${", html)

    def test_tally_fallback_and_field_contract(self):
        html = render(self.data, "testForm123", ROOT / "src")
        self.assertIn("https://tally.so/r/testForm123?artifact_id=bandtastic-field-note-01", html)
        for field in ("Email", "Framework", "Number of live strategies", "Current monitoring method"):
            self.assertIn(field, html)
        self.assertIn("No broker keys.", html)
        self.assertNotIn("Enter broker key", html)
        self.assertNotIn("repository upload", html.lower())

    def test_empty_form_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Tally form ID is required"):
            render(self.data, "", ROOT / "src")

    def test_build_copies_only_public_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build(ROOT / "raw/report-data.json", ROOT / "src", output, "testForm123")
            expected = {
                "index.html",
                "assets/styles.css",
                "assets/tally.js",
                "raw/report-data.json",
                "raw/verification.json",
                "raw/economics.json",
            }
            actual = {
                str(path.relative_to(output)).replace("\\\\", "/")
                for path in output.rglob("*")
                if path.is_file()
            }
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
```

Run before implementation:

```bash
python -m unittest tests.test_build -v
```

Expected: FAIL importing `scripts.build`.

- [ ] **Step 2: Implement deterministic rendering**

Create `scripts/build.py`:

```python
import argparse
import json
from html import escape
from pathlib import Path
from shutil import copy2
from string import Template

try:
    from scripts.validate_report_data import validate
except ModuleNotFoundError:
    from validate_report_data import validate


def human_duration(seconds: float) -> str:
    minutes, second = divmod(round(seconds), 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours}m {minute:02d}s" if hours else f"{minute}m {second:02d}s"


def render(data: dict, tally_form_id: str, source_dir: Path) -> str:
    errors = validate(data)
    if errors:
        raise ValueError("; ".join(errors))
    if not tally_form_id.strip():
        raise ValueError("Tally form ID is required")

    scenarios = "".join(
        "<tr>"
        f"<td>{row['strategies']}</td>"
        f"<td>{row['windows_per_run']}</td>"
        f"<td>{row['jobs_per_month']}</td>"
        f"<td><strong>${row['monthly_total_usd']:.3f}</strong></td>"
        "</tr>"
        for row in data["monthly_scenarios"]
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in data["limitations"])
    fixed_seconds = sum(data["fixed_backtest"]["wall_seconds"]) / len(data["fixed_backtest"]["wall_seconds"])
    values = {
        "PUBLISHER": escape(data["publisher"]),
        "HEADLINE": escape(data["headline"]),
        "VERDICT": escape(data["verdict"]),
        "FIXED_SECONDS": f"{fixed_seconds:.1f}s",
        "FIXED_MEMORY_MB": f"{data['fixed_backtest']['peak_memory_bytes'] / 1_000_000:.0f}MB",
        "HYPEROPT_TIME": human_duration(data["hyperopt"]["wall_seconds"]),
        "HYPEROPT_MEMORY_GIB": f"{data['hyperopt']['peak_memory_bytes'] / (1 << 30):.2f}GiB",
        "STRATEGY_COMMIT": escape(data["provenance"]["strategy_commit"][:7]),
        "IMAGE_DIGEST": escape(data["provenance"]["image_digest"]),
        "OOS_TRADES": str(data["oos"]["trades"]),
        "SCENARIO_ROWS": scenarios,
        "LIMITATIONS": limitations,
        "TALLY_FORM_ID": escape(tally_form_id.strip()),
        "ARTIFACT_ID": escape(data["artifact_id"]),
        "PAGE_VERSION": escape(data["page_version"]),
    }
    template = Template((source_dir / "index.template.html").read_text(encoding="utf-8"))
    return template.substitute(values)


def build(data_path: Path, source_dir: Path, output_dir: Path, tally_form_id: str) -> None:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    html = render(data, tally_form_id, source_dir)
    assets = output_dir / "assets"
    raw = output_dir / "raw"
    assets.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    copy2(source_dir / "styles.css", assets / "styles.css")
    copy2(source_dir / "tally.js", assets / "tally.js")
    for name in ("report-data.json", "verification.json", "economics.json"):
        copy2(data_path.parent / name, raw / name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tally-form-id", required=True)
    parser.add_argument("--data", type=Path, default=Path("raw/report-data.json"))
    parser.add_argument("--source-dir", type=Path, default=Path("src"))
    parser.add_argument("--output-dir", type=Path, default=Path("site"))
    args = parser.parse_args()
    build(args.data, args.source_dir, args.output_dir, args.tally_form_id)
    print(f"built {args.output_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

This validates before rendering, fails on missing form ID or unresolved template tokens, copies only the three approved public raw files, and never reads `private/`.

The CTA is a normal fallback link:

```html
<a id="report-request" class="cta-button"
   href="https://tally.so/r/${TALLY_FORM_ID}?artifact_id=${ARTIFACT_ID}&page_version=${PAGE_VERSION}&source=direct"
   data-form-id="${TALLY_FORM_ID}"
   data-artifact-id="${ARTIFACT_ID}"
   data-page-version="${PAGE_VERSION}">Request a scheduled stability report</a>
```

- [ ] **Step 3: Implement progressive Tally enhancement**

Create `src/tally.js`:

```javascript
(() => {
  const trigger = document.querySelector("#report-request");
  if (!trigger) return;
  trigger.addEventListener("click", (event) => {
    if (!window.Tally || typeof window.Tally.openPopup !== "function") return;
    event.preventDefault();
    const query = new URLSearchParams(window.location.search);
    window.Tally.openPopup(trigger.dataset.formId, {
      layout: "modal",
      width: 500,
      hiddenFields: {
        artifact_id: trigger.dataset.artifactId,
        page_version: trigger.dataset.pageVersion,
        source: query.get("utm_source") || "direct"
      }
    });
  });
})();
```

If JavaScript/Tally is blocked, the normal link opens the hosted form.

- [ ] **Step 4: Implement the approved semantic page**

Create `src/index.template.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A pinned Freqtrade experiment separating scheduled backtests from Hyperopt.">
  <title>Field Note 01 · $PUBLISHER</title>
  <link rel="stylesheet" href="assets/styles.css">
  <script async src="https://tally.so/widgets/embed.js"></script>
  <script defer src="assets/tally.js"></script>
</head>
<body>
  <header class="site-header">
    <a class="identity" href="#top">$PUBLISHER / Field Note 01</a>
    <nav aria-label="Report">
      <a href="#method">Method</a>
      <a href="raw/report-data.json">Raw artifacts</a>
      <a href="#request">Request report</a>
    </nav>
  </header>

  <main id="top" class="shell">
    <section class="hero" aria-labelledby="report-title">
      <div>
        <p class="eyebrow">Measured · pinned · reproducible</p>
        <h1 id="report-title">$HEADLINE</h1>
        <p class="lede">A public Freqtrade experiment separates the cheap monitoring loop from the heavy optimization job—and prices both across a full month of scheduled runs.</p>
      </div>
      <aside class="verdict" aria-label="Bounded verdict">
        <span>Verdict</span>
        <strong>Technical gate passed</strong>
        <p>$VERDICT</p>
      </aside>
    </section>

    <section class="metric-grid" aria-label="Measured workload summary">
      <article><strong>$FIXED_SECONDS</strong><span>Fixed backtest</span></article>
      <article><strong>$FIXED_MEMORY_MB</strong><span>Fixed peak memory</span></article>
      <article><strong>$HYPEROPT_TIME</strong><span>500-epoch Hyperopt</span></article>
      <article><strong>$HYPEROPT_MEMORY_GIB</strong><span>Hyperopt peak memory</span></article>
    </section>

    <div class="evidence-grid" id="method">
      <section class="panel">
        <p class="section-number">01 / What we ran</p>
        <h2>Pinned benchmark</h2>
        <ul>
          <li>Freqtrade 2026.7 at a pinned image digest</li>
          <li>Bandtastic at commit <code>$STRATEGY_COMMIT</code></li>
          <li>Ten Binance spot pairs on 15-minute data</li>
          <li>Two uncached fixed runs and an untouched OOS replay</li>
        </ul>
        <details><summary>Full image digest</summary><code>$IMAGE_DIGEST</code></details>
      </section>
      <section class="panel">
        <p class="section-number">02 / What changed</p>
        <h2>Two workloads, two cadences</h2>
        <p>Fixed-parameter checks are cheap enough to schedule nightly in this small benchmark. Optimization is materially slower and heavier, so it moves to weekly, monthly, on-demand, or bring-your-own compute.</p>
        <p>The untouched OOS replay contained only <strong>$OOS_TRADES trades</strong>. It proves the export/replay path, not robustness.</p>
      </section>
    </div>

    <section class="panel economics" aria-labelledby="economics-title">
      <p class="section-number">03 / Full-month economics</p>
      <h2 id="economics-title">Every scheduled night included</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th scope="col">Strategies</th><th scope="col">Windows/night</th><th scope="col">Jobs/month</th><th scope="col">Projected total</th></tr></thead>
          <tbody>$SCENARIO_ROWS</tbody>
        </table>
      </div>
      <p class="fine-print">Illustrative rates; excludes orchestration, database, observability, support, paid data, retries, taxes, and idle capacity.</p>
    </section>

    <section class="limitations" aria-labelledby="limits-title">
      <p class="section-number">04 / What this does not prove</p>
      <h2 id="limits-title">Boundaries before conclusions</h2>
      <ul>$LIMITATIONS</ul>
    </section>

    <section id="request" class="request" aria-labelledby="request-title">
      <div>
        <p class="section-number">Validation cohort</p>
        <h2 id="request-title">Request a scheduled stability report</h2>
        <p>We are testing whether self-hosting algo traders will schedule recurring checks—not selling strategies or changing parameters automatically.</p>
        <p class="fine-print">Private responses in Tally. No broker keys. No write access. No performance promise. Cohort review does not guarantee a report.</p>
      </div>
      <div>
        <p class="field-label">Four required fields</p>
        <ul class="field-list"><li>Email</li><li>Framework</li><li>Number of live strategies</li><li>Current monitoring method</li></ul>
        <a id="report-request" class="cta-button"
           href="https://tally.so/r/$TALLY_FORM_ID?artifact_id=$ARTIFACT_ID&amp;page_version=$PAGE_VERSION&amp;source=direct"
           data-form-id="$TALLY_FORM_ID"
           data-artifact-id="$ARTIFACT_ID"
           data-page-version="$PAGE_VERSION">Request a scheduled stability report</a>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div><a href="raw/report-data.json">Report data</a> · <a href="raw/verification.json">Verification</a> · <a href="raw/economics.json">Economics</a></div>
    <div>Independent research. Not investment advice.</div>
  </footer>
</body>
</html>
```

The template contains every approved section in order and includes no trading imagery, price widget, performance promise, or public signup counter.

- [ ] **Step 5: Implement Evidence Ledger CSS**

Create `src/styles.css`:

```css
:root {
  color-scheme: dark;
  --bg: #0d1412;
  --panel: #15201c;
  --panel-strong: #17221e;
  --line: #2a4036;
  --text: #e9f1ec;
  --muted: #a9bbb2;
  --accent: #75d5a6;
  --caveat: #d2a85a;
  --max: 1120px;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-variant-numeric: tabular-nums;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--text); line-height: 1.55; }
a { color: var(--accent); text-underline-offset: .2em; }
a:hover { text-decoration-thickness: .14em; }
a:focus-visible, summary:focus-visible {
  outline: 3px solid var(--caveat);
  outline-offset: 4px;
  border-radius: 3px;
}

.site-header, .site-footer, .shell { width: min(calc(100% - 40px), var(--max)); margin-inline: auto; }
.site-header {
  min-height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  border-bottom: 1px solid var(--line);
  font-size: .82rem;
  letter-spacing: .04em;
}
.site-header nav { display: flex; gap: 18px; }
.identity { color: var(--text); font-weight: 700; text-decoration: none; }
.shell { padding-block: 72px; }

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(260px, .55fr);
  gap: 32px;
  align-items: end;
}
.eyebrow, .section-number, .field-label {
  margin: 0;
  color: var(--accent);
  font-size: .72rem;
  font-weight: 750;
  letter-spacing: .11em;
  text-transform: uppercase;
}
h1 { max-width: 820px; margin: 12px 0; font-size: clamp(2.5rem, 6vw, 4.8rem); line-height: .99; letter-spacing: -.055em; }
h2 { margin: 9px 0 12px; font-size: clamp(1.35rem, 3vw, 2rem); line-height: 1.14; }
.lede { max-width: 700px; color: var(--muted); font-size: 1.05rem; }
.verdict, .panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); }
.verdict { padding: 20px; }
.verdict span { color: var(--muted); font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; }
.verdict strong { display: block; margin: 7px 0; color: #dff5e9; font-size: 1.4rem; }
.verdict p, .panel p, .panel li { color: var(--muted); }

.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 30px 0; }
.metric-grid article { min-width: 0; padding: 18px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); }
.metric-grid strong { display: block; font-size: clamp(1.7rem, 4vw, 2.25rem); line-height: 1.1; }
.metric-grid span { color: var(--muted); font-size: .8rem; }
.evidence-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { padding: 22px; }
.panel ul { padding-left: 20px; }
details { margin-top: 16px; color: var(--muted); }
details code { display: block; margin-top: 8px; overflow-wrap: anywhere; }

.economics { margin-top: 16px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 600px; border-collapse: collapse; }
th, td { padding: 12px 10px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; }
td strong { color: #dff5e9; }
.fine-print { color: #879a90; font-size: .76rem; }

.limitations { margin-top: 20px; padding: 22px; border-left: 4px solid var(--caveat); background: #171d1a; }
.limitations .section-number { color: var(--caveat); }
.limitations li { margin-block: 7px; color: #c5cec9; }
.request {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
  margin-top: 28px;
  padding: 28px;
  border-radius: 12px;
  background: #e7f3ec;
  color: #122019;
}
.request .section-number { color: #3c6b53; }
.request p { color: #456052; }
.field-label { color: #3c6b53; }
.field-list { display: grid; grid-template-columns: 1fr 1fr; gap: 7px 18px; padding-left: 20px; color: #2d493b; }
.cta-button {
  display: inline-block;
  margin-top: 10px;
  padding: 12px 16px;
  border-radius: 7px;
  background: #153c2b;
  color: #fff;
  font-weight: 750;
  text-decoration: none;
}
.cta-button:focus-visible { outline-color: #7b4510; }
.site-footer { display: flex; justify-content: space-between; gap: 24px; padding-block: 26px; border-top: 1px solid var(--line); color: #879a90; font-size: .78rem; }

@media (max-width: 900px) {
  .hero, .request { grid-template-columns: 1fr; }
  .metric-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 700px) {
  .site-header { align-items: flex-start; flex-direction: column; justify-content: center; padding-block: 16px; }
  .site-header nav { flex-wrap: wrap; }
  .shell { padding-block: 44px; }
  .evidence-grid { grid-template-columns: 1fr; }
  .site-footer { flex-direction: column; }
}
@media (max-width: 520px) {
  .site-header, .site-footer, .shell { width: min(calc(100% - 24px), var(--max)); }
  .metric-grid { grid-template-columns: 1fr; }
  .field-list { grid-template-columns: 1fr; }
  .request, .panel, .limitations { padding: 18px; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}
@media print {
  :root { color-scheme: light; }
  body { background: #fff; color: #111; }
  .site-header nav, script { display: none; }
  .verdict, .panel, .metric-grid article, .limitations, .request { background: #fff; color: #111; border-color: #bbb; }
  .cta-button { padding: 0; background: transparent; color: #111; }
  .cta-button::after { content: " (" attr(href) ")"; font-weight: 400; }
}
```

The stylesheet implements the approved palette, responsive grids, table overflow, AA-oriented contrast, visible focus, reduced motion, and print fallback URL.

- [ ] **Step 6: Run and commit**

```bash
python -m unittest tests.test_build -v
python scripts/build.py --tally-form-id testForm123 --output-dir site
git add src scripts/build.py tests/test_build.py
git commit -m "feat: render Evidence Ledger report"
```

Expected: tests PASS and generated HTML contains no unresolved token.

### Task 7: Add CI, Pages, methodology, and real-surface verification

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/pages.yml`
- Create: `docs/methodology.md`

- [ ] **Step 1: Add CI**

Create `.github/workflows/ci.yml`:

```yaml
name: CI
on:
  push:
  pull_request:
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: python -m unittest discover -s tests -v
      - run: python scripts/validate_report_data.py raw/report-data.json
      - run: python scripts/build.py --tally-form-id testForm123 --output-dir site
```

The CI build uses a non-public test form ID and never deploys.

- [ ] **Step 2: Add fail-closed Pages deployment**

Create `.github/workflows/pages.yml`:

```yaml
name: Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      TALLY_FORM_ID: ${{ vars.TALLY_FORM_ID }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - name: Require production Tally form
        run: test -n "$TALLY_FORM_ID"
      - run: python -m unittest discover -s tests -v
      - run: python scripts/validate_report_data.py raw/report-data.json
      - run: python scripts/build.py --tally-form-id "$TALLY_FORM_ID" --output-dir site
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

The workflow fails closed if the repository variable is missing and uploads only `site/`; it never references `private/`.

- [ ] **Step 3: Write methodology**

Record exact strategy commit, image digest, pairs, timeframe, ranges, fee, uncached repetitions, Hyperopt seed/workers/epochs/loss, monthly formula, illustrative rates, exclusions, and public raw links.

- [ ] **Step 4: Browser-verify locally**

Start `python -m http.server 8000 --directory site` through the supervised process manager. Use the browser tool at desktop/mobile widths. Verify corrected claims, limitations before CTA, keyboard focus, fallback URL, no page overflow, and no console errors except an expected invalid test form when deliberately clicked.

- [ ] **Step 5: Commit**

```bash
git add .github docs/methodology.md
git commit -m "ci: add fail-closed Pages publication"
```

### Task 8: Create production Tally and publish Artifact 1

**External side effects:** form creation, public repository creation, push, repository variable, Pages publication. Confirm immediately before each.

- [ ] **Step 1: Confirm and create the exact Tally form**

Confirm signed-in Tally account and title `Scheduled Strategy Stability Report — Validation Cohort` before creation.

Visible required fields:

1. Email.
2. Framework: Freqtrade, Jesse, Backtrader, Other.
3. Number of live strategies: 0, 1, 2–5, 6–10, 11+.
4. Current monitoring method: manual reruns, cron/scripts, platform-native tooling, nothing, other.

Hidden: `artifact_id`, `page_version`, `source`. Confirmation copy says cohort review does not guarantee a report. Submit/export one prelaunch test to verify headers.

- [ ] **Step 2: Confirm the GitHub target**

Run read-only:

```bash
gh api user --jq .login
git log --oneline --decorate -5
```

Present resolved owner, repository `strategy-stability-research`, public visibility, commits, and Tally form ID. Confirm before creation/push.

- [ ] **Step 3: Create repository and deploy Pages**

After confirmation:

```bash
OWNER="$(gh api user --jq .login)"
gh repo create "$OWNER/strategy-stability-research" --public --source . --remote origin --push
gh variable set TALLY_FORM_ID --body "$TALLY_FORM_ID"
gh workflow run pages.yml
```

Wait for CI/Pages and browser-verify the production URL/Tally form. A live but undistributed page does not start the campaign clock.

### Task 9: Start and apply the immutable three-artifact gate

**Dependency:** Artifact 2 and Artifact 3 need separate approved specs/implementations. Sharing Artifact 1 starts the clock even if they are unfinished.

- [ ] **Step 1: Confirm the first external distribution post**

Present exact target, copy, Artifact 1 URL, Tally form, and warning: confirmation starts an immutable 14-day window; late/missing Artifacts 2/3 fail it. Obtain immediate confirmation.

- [ ] **Step 2: Freeze immediately before sharing Artifact 1**

```bash
python scripts/gate_config.py freeze private/gate-config.json "$ARTIFACT_ONE_URL"
```

Publish the confirmed post. Do not reset if copy, channel, or later artifacts underperform.

- [ ] **Step 3: Publish and record Artifacts 2 and 3 inside the same window**

After each confirmed external publication:

```bash
python scripts/gate_config.py publish private/gate-config.json ARTIFACT_ID PUBLIC_URL
```

A missing/late record is a campaign FAIL.

- [ ] **Step 4: Evaluate at cutoff**

Export private Tally CSV, review obvious spam into `private/spam.txt`, then:

```bash
python scripts/evaluate_gate.py private/tally-responses.csv private/gate-config.json private/spam.txt private/gate-result.json
```

Expected: `PASS: N/8 unique people` or `FAIL: N/8 unique people`.

- [ ] **Step 5: Enforce outcome**

FAIL: kill; no scheduler. PASS: offer the entire included cohort a minimal cron-concierge test. Activation passes only if at least 25% schedule one automated re-backtest within seven days of access. Opens, replies, and acceptance of manual reports never count.

## Plan self-review

- Spec coverage: corrected headline, exact measurements, full-month economics, Tally fallback, four fields, private boundary, Artifact-1 clock, three-artifact requirement, unique-person dedupe, immutable cutoff, and separate 25% activation gate each map to a task.
- Scope: this plan builds Artifact 1 and gate tooling; campaign execution explicitly depends on two separate artifact implementations but does not wait or reset once Artifact 1 is shared.
- Unfinished-marker scan: no deferred implementation steps. Runtime GitHub/Tally IDs and public URLs are obtained from confirmed systems and fail closed.
- Type consistency: artifact IDs, CSV headers, JSON fields, form hidden fields, and exclusion reasons match across spec, tests, scripts, and operations.
