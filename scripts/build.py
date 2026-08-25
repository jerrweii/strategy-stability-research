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

def render_campaign_artifact(
    data: dict,
    tally_form_id: str,
    source_dir: Path,
    template_name: str,
    extra_values: dict[str, str] | None = None,
) -> str:
    if not tally_form_id.strip():
        raise ValueError("Tally form ID is required")
    for key in ("artifact_id", "page_version"):
        if not data.get(key):
            raise ValueError(f"{key} is required")
    values = {
        "TALLY_FORM_ID": escape(tally_form_id.strip()),
        "ARTIFACT_ID": escape(data["artifact_id"]),
        "PAGE_VERSION": escape(data["page_version"]),
    }
    values.update(extra_values or {})
    template = Template((source_dir / template_name).read_text(encoding="utf-8"))
    return template.substitute(values)


def build(
    data_path: Path,
    source_dir: Path,
    output_dir: Path,
    tally_form_id: str,
) -> None:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    html = render(data, tally_form_id, source_dir)
    tutorial_data_path = data_path.parent / "orb-decay-timeline.json"
    tutorial_data = json.loads(tutorial_data_path.read_text(encoding="utf-8"))
    walk_forward = tutorial_data["results"]["walk_forward"]
    timeline_rows = "".join(
        "<tr>"
        f"<td>{row['oos_year']}</td>"
        f"<td>{row['selected_opening_range_minutes']}m</td>"
        f"<td>{row['oos_trades']}</td>"
        f"<td>{row['oos_expectancy_r']:.3f}R</td>"
        f"<td>{row['oos_total_r']:.2f}R</td>"
        f"<td>{row['oos_max_drawdown_r']:.2f}R</td>"
        "</tr>"
        for row in walk_forward
    )
    selected_ranges = {row["selected_opening_range_minutes"] for row in walk_forward}
    expectancy = [row["oos_expectancy_r"] for row in walk_forward]
    tutorial_html = render_campaign_artifact(
        tutorial_data,
        tally_form_id,
        source_dir,
        "tutorial-decay-audit.template.html",
        {
            "OOS_YEARS": str(len(walk_forward)),
            "TOTAL_OOS_TRADES": str(sum(row["oos_trades"] for row in walk_forward)),
            "SELECTED_RANGE": (
                f"{next(iter(selected_ranges))}m in {len(walk_forward)}/{len(walk_forward)}"
                if len(selected_ranges) == 1
                else ", ".join(f"{value}m" for value in sorted(selected_ranges))
            ),
            "EXPECTANCY_RANGE": f"{min(expectancy):.3f} to {max(expectancy):.3f}R",
            "TIMELINE_ROWS": timeline_rows,
            "DATA_START": escape(tutorial_data["data"]["start"][:10]),
            "DATA_END": escape(tutorial_data["data"]["end"][:10]),
            "DUPLICATES": f"{tutorial_data['data']['duplicate_rows_removed']:,}",
        },
    )
    reconciliation_data_path = data_path.parent / "reconciliation-example.json"
    reconciliation_data = json.loads(
        reconciliation_data_path.read_text(encoding="utf-8")
    )
    summary = reconciliation_data["summary"]
    tolerances = reconciliation_data["tolerances"]
    reconciliation_rows = "".join(
        "<tr>"
        f"<td>{escape(row['trade_id'])}</td>"
        f"<td>{escape(row['status'].replace('_', ' ').replace('multi factor', 'multi-factor'))}</td>"
        f"<td>{escape(', '.join(row['discrepancy_flags']) or 'none')}</td>"
        f"<td>{row.get('max_timing_delta_seconds', '—')}{'s' if 'max_timing_delta_seconds' in row else ''}</td>"
        f"<td>{f'{row['max_price_delta_bps']:.1f} bps' if 'max_price_delta_bps' in row else '—'}</td>"
        f"<td>{f'${row['fee_delta_usd']:.2f}' if 'fee_delta_usd' in row else '—'}</td>"
        f"<td>{f'${row['pnl_gap_usd']:+.2f}' if row['pnl_gap_usd'] is not None else '—'}</td>"
        "</tr>"
        for row in reconciliation_data["rows"]
    )
    reconciliation_html = render_campaign_artifact(
        reconciliation_data,
        tally_form_id,
        source_dir,
        "reconciliation-notebook.template.html",
        {
            "TOTAL_KEYS": str(summary["total_keys"]),
            "MATCHED_PAIRS": str(summary["matched_pairs"]),
            "EXACT_PAIRS": str(summary["exact_pairs"]),
            "MISMATCH_KEYS": str(summary["mismatch_keys"]),
            "TIMING_TOLERANCE": str(tolerances["timing_seconds"]),
            "PRICE_TOLERANCE": f"{tolerances['price_bps']:.1f}",
            "FEE_TOLERANCE": f"{tolerances['fees_usd']:.2f}",
            "RECONCILIATION_ROWS": reconciliation_rows,
        },
    )
    assets = output_dir / "assets"
    raw = output_dir / "raw"
    tutorial_output = output_dir / "tutorial-decay-audit"
    reconciliation_output = output_dir / "reconciliation-notebook"
    assets.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    tutorial_output.mkdir(parents=True, exist_ok=True)
    reconciliation_output.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    (tutorial_output / "index.html").write_text(tutorial_html, encoding="utf-8")
    (reconciliation_output / "index.html").write_text(
        reconciliation_html, encoding="utf-8"
    )
    copy2(source_dir / "styles.css", assets / "styles.css")
    copy2(source_dir / "tally.js", assets / "tally.js")
    for name in (
        "report-data.json",
        "verification.json",
        "economics.json",
        "tutorial-decay-audit.json",
        "decay-run-manifest.schema.json",
        "orb-decay-timeline.json",
        "reconciliation-expected-sample.csv",
        "reconciliation-actual-sample.csv",
        "reconciliation-example.json",
    ):
        copy2(data_path.parent / name, raw / name)
    copy2(
        source_dir.parent / "research/reconcile_live_vs_backtest.py",
        raw / "reconcile_live_vs_backtest.py",
    )


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
