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
    limitations = "".join(
        f"<li>{escape(item)}</li>" for item in data["limitations"]
    )
    fixed_seconds = sum(data["fixed_backtest"]["wall_seconds"]) / len(
        data["fixed_backtest"]["wall_seconds"]
    )
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
    template = Template(
        (source_dir / "index.template.html").read_text(encoding="utf-8")
    )
    return template.substitute(values)


def build(
    data_path: Path,
    source_dir: Path,
    output_dir: Path,
    tally_form_id: str,
) -> None:
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
