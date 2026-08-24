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
    "live-reconciliation-notebook-01",
}
REQUIRED_FIELDS = (
    "Email",
    "Framework",
    "Number of live strategies",
    "Current monitoring method",
    "artifact_id",
    "page_version",
    "source",
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

        ledger.append(
            {
                "email_sha256": email_hash(normalized),
                "submitted_at": row["Submitted at"],
                "artifact_id": row.get("artifact_id", ""),
                "included": reason == "",
                "reason": reason,
            }
        )

    complete = publications_complete(config)
    count = len(included)
    return {
        "result": "PASS" if complete and count >= 8 else "FAIL",
        "artifacts_complete": complete,
        "included_unique_people": count,
        "required_unique_people": 8,
        "launch_at": config["launch_at"],
        "cutoff_at": config["cutoff_at"],
        "ledger": ledger,
    }


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: evaluate_gate.py RESPONSES.csv CONFIG.json SPAM.txt OUTPUT.json",
            file=sys.stderr,
        )
        return 2
    responses_path, config_path, spam_path, output_path = map(Path, sys.argv[1:])
    with responses_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    spam = {
        line.strip()
        for line in spam_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    result = evaluate_gate(rows, config, spam)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['result']}: {result['included_unique_people']}/8 unique people")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
