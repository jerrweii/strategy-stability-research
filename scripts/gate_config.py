import argparse
import json
import re
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

def valid_response_timezone(value: str) -> bool:
    match = re.fullmatch(r"([+-])(\d{2}):(\d{2})", value)
    return bool(match and int(match.group(2)) <= 23 and int(match.group(3)) <= 59)


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def freeze(
    path: Path,
    artifact_one_url: str,
    launch_at: datetime,
    response_timezone: str,
) -> dict:
    if path.exists():
        raise FileExistsError(f"gate config already exists: {path}")
    if not valid_url(artifact_one_url):
        raise ValueError("Artifact 1 URL must be absolute HTTPS")
    if not valid_response_timezone(response_timezone):
        raise ValueError("response_timezone must use a valid ±HH:MM offset")
    launch = launch_at.astimezone(timezone.utc)
    config = {
        "launch_at": iso(launch),
        "cutoff_at": iso(launch + timedelta(days=14)),
        "response_timezone": response_timezone,
        "artifacts": {
            ARTIFACT_ONE: {"url": artifact_one_url, "published_at": iso(launch)},
            EXPECTED_ARTIFACTS[1]: {"url": None, "published_at": None},
            EXPECTED_ARTIFACTS[2]: {"url": None, "published_at": None},
        },
    }
    write_atomic(path, config)
    return config


def record_publication(
    path: Path,
    artifact_id: str,
    url: str,
    published_at: datetime,
) -> dict:
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
    freeze_parser.add_argument("--response-timezone", required=True)
    publish_parser = commands.add_parser("publish")
    publish_parser.add_argument("path", type=Path)
    publish_parser.add_argument("artifact_id")
    publish_parser.add_argument("url")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    if args.command == "freeze":
        result = freeze(
            args.path,
            args.artifact_one_url,
            now,
            args.response_timezone,
        )
    else:
        result = record_publication(args.path, args.artifact_id, args.url, now)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
