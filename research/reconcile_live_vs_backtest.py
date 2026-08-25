import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REQUIRED_COLUMNS = {
    "trade_id",
    "strategy_id",
    "symbol",
    "side",
    "entry_time_utc",
    "exit_time_utc",
    "quantity",
    "entry_price",
    "exit_price",
    "fees_usd",
}


def parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"timestamp must end in Z: {value}")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def read_trades(path: Path) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns in {path.name}: {', '.join(sorted(missing))}")
        trades = {}
        for row in reader:
            trade_id = row["trade_id"].strip()
            if not trade_id:
                raise ValueError(f"empty trade_id in {path.name}")
            if trade_id in trades:
                raise ValueError(f"duplicate trade_id: {trade_id}")
            if row["side"] not in {"long", "short"}:
                raise ValueError(f"invalid side for {trade_id}: {row['side']}")
            parse_utc(row["entry_time_utc"])
            parse_utc(row["exit_time_utc"])
            for field in ("quantity", "entry_price", "exit_price", "fees_usd"):
                row[field] = float(row[field])
            trades[trade_id] = row
    return trades


def pnl(trade: dict) -> float:
    direction = 1 if trade["side"] == "long" else -1
    gross = (trade["exit_price"] - trade["entry_price"]) * trade["quantity"] * direction
    return round(gross - trade["fees_usd"], 4)


def input_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile(
    expected: dict[str, dict],
    actual: dict[str, dict],
    timing_tolerance_seconds: int = 60,
    price_tolerance_bps: float = 5.0,
    fee_tolerance_usd: float = 0.01,
) -> list[dict]:
    rows = []
    for trade_id in sorted(set(expected) | set(actual)):
        expected_trade = expected.get(trade_id)
        actual_trade = actual.get(trade_id)
        if actual_trade is None:
            rows.append(
                {
                    "trade_id": trade_id,
                    "status": "missing_live",
                    "discrepancy_flags": ["missing_live"],
                    "expected_pnl_usd": pnl(expected_trade),
                    "actual_pnl_usd": None,
                    "pnl_gap_usd": None,
                }
            )
            continue
        if expected_trade is None:
            rows.append(
                {
                    "trade_id": trade_id,
                    "status": "unexpected_live",
                    "discrepancy_flags": ["unexpected_live"],
                    "expected_pnl_usd": None,
                    "actual_pnl_usd": pnl(actual_trade),
                    "pnl_gap_usd": None,
                }
            )
            continue

        entry_delta = abs(
            (parse_utc(actual_trade["entry_time_utc"]) - parse_utc(expected_trade["entry_time_utc"])).total_seconds()
        )
        exit_delta = abs(
            (parse_utc(actual_trade["exit_time_utc"]) - parse_utc(expected_trade["exit_time_utc"])).total_seconds()
        )
        entry_bps = abs(actual_trade["entry_price"] - expected_trade["entry_price"]) / expected_trade["entry_price"] * 10_000
        exit_bps = abs(actual_trade["exit_price"] - expected_trade["exit_price"]) / expected_trade["exit_price"] * 10_000
        fee_delta = abs(actual_trade["fees_usd"] - expected_trade["fees_usd"])
        quantity_delta = abs(actual_trade["quantity"] - expected_trade["quantity"])
        identity_differences = {
            field: {
                "expected": expected_trade[field],
                "actual": actual_trade[field],
            }
            for field in ("strategy_id", "symbol", "side")
            if expected_trade[field] != actual_trade[field]
        }

        flags = []
        if identity_differences:
            flags.append("identity")
        if max(entry_delta, exit_delta) > timing_tolerance_seconds:
            flags.append("timing")
        if max(entry_bps, exit_bps) > price_tolerance_bps:
            flags.append("price")
        if fee_delta > fee_tolerance_usd:
            flags.append("fee")
        if quantity_delta > 1e-9:
            flags.append("quantity")

        if not flags:
            status = "exact"
        elif len(flags) > 1:
            status = "multi_factor_drift"
        else:
            status = f"{flags[0]}_drift"
        expected_pnl = pnl(expected_trade)
        actual_pnl = pnl(actual_trade)
        rows.append(
            {
                "trade_id": trade_id,
                "status": status,
                "discrepancy_flags": flags,
                "identity_differences": identity_differences,
                "max_timing_delta_seconds": round(max(entry_delta, exit_delta), 3),
                "max_price_delta_bps": round(max(entry_bps, exit_bps), 3),
                "fee_delta_usd": round(fee_delta, 4),
                "quantity_delta": round(quantity_delta, 8),
                "expected_pnl_usd": expected_pnl,
                "actual_pnl_usd": actual_pnl,
                "pnl_gap_usd": round(actual_pnl - expected_pnl, 4),
            }
        )
    return rows


def build_report(expected_path: Path, actual_path: Path) -> dict:
    rows = reconcile(read_trades(expected_path), read_trades(actual_path))
    counts = Counter(row["status"] for row in rows)
    status_order = (
        "exact",
        "identity_drift",
        "timing_drift",
        "price_drift",
        "fee_drift",
        "quantity_drift",
        "multi_factor_drift",
        "missing_live",
        "unexpected_live",
    )
    return {
        "artifact_id": "live-reconciliation-notebook-01",
        "page_version": "2026-08-25",
        "title": "Live-vs-backtest reconciliation notebook",
        "matching_key": "trade_id",
        "tolerances": {
            "timing_seconds": 60,
            "price_bps": 5.0,
            "fees_usd": 0.01,
            "quantity_absolute": 1e-9,
        },
        "inputs": {
            "expected": {"file": expected_path.name, "sha256": input_digest(expected_path)},
            "actual": {"file": actual_path.name, "sha256": input_digest(actual_path)},
        },
        "summary": {
            "total_keys": len(rows),
            "matched_pairs": sum(1 for row in rows if row["status"] not in {"missing_live", "unexpected_live"}),
            "exact_pairs": counts["exact"],
            "mismatch_keys": len(rows) - counts["exact"],
            "status_counts": {status: counts[status] for status in status_order if counts[status]},
        },
        "rows": rows,
        "interpretation": "Synthetic data demonstrates the contract; it is not a live-performance claim.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile expected backtest trades with live executions by trade_id.")
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = build_report(args.expected, args.actual)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
