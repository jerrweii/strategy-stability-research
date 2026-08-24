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
        expected_jobs = (
            row.get("strategies", 0)
            * row.get("windows_per_run", 0)
            * row.get("scheduled_runs_per_month", 0)
        )
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
