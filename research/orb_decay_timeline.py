from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import time, timedelta
from pathlib import Path

import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/BrianWeiss1/StockList/main/5min_data_SPY_2015_to_2024.csv"
OPENING_RANGES = (15, 30, 60)
ROUND_TRIP_COST_BPS = 10


@dataclass(frozen=True)
class Trade:
    date: str
    opening_range_minutes: int
    entry_time: str
    exit_reason: str
    gross_r: float
    net_r: float


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_bars(path: Path) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(path, parse_dates=[0])
    raw = raw.rename(columns={raw.columns[0]: "datetime"})
    duplicate_rows = int(raw.duplicated().sum())
    bars = raw.drop_duplicates().set_index("datetime").sort_index()
    bars = bars.between_time("09:30", "16:00")
    metadata = {
        "raw_rows": len(raw),
        "duplicate_rows_removed": duplicate_rows,
        "rth_rows": len(bars),
        "start": bars.index.min().isoformat(),
        "end": bars.index.max().isoformat(),
        "sha256": sha256(path),
    }
    return bars, metadata


def run_day(day: pd.DataFrame, opening_range_minutes: int) -> Trade | None:
    if day.empty:
        return None
    session_date = day.index[0].date()
    open_at = pd.Timestamp.combine(session_date, time(9, 30))
    range_end = open_at + timedelta(minutes=opening_range_minutes)
    opening = day[(day.index >= open_at) & (day.index < range_end)]
    expected_bars = opening_range_minutes // 5
    if len(opening) < expected_bars:
        return None
    range_high = float(opening["High"].max())
    range_low = float(opening["Low"].min())
    risk = range_high - range_low
    if risk <= 0:
        return None

    candidates = day[(day.index >= range_end) & (day.index.time <= time(15, 45))]
    breakouts = candidates[candidates["Close"] > range_high]
    if breakouts.empty:
        return None

    entry_at = breakouts.index[0]
    entry = float(breakouts.iloc[0]["Close"])
    target = entry + risk
    stop = entry - risk
    later = day[(day.index > entry_at) & (day.index.time <= time(15, 55))]
    gross_r = 0.0
    reason = "session_close"
    exit_price = float(day[day.index.time <= time(15, 55)].iloc[-1]["Close"])

    for _, bar in later.iterrows():
        hit_stop = float(bar["Low"]) <= stop
        hit_target = float(bar["High"]) >= target
        if hit_stop and hit_target:
            gross_r = -1.0
            reason = "both_hit_stop_first"
            exit_price = stop
            break
        if hit_stop:
            gross_r = -1.0
            reason = "stop"
            exit_price = stop
            break
        if hit_target:
            gross_r = 1.0
            reason = "target"
            exit_price = target
            break
    else:
        gross_r = (exit_price - entry) / risk

    cost_r = (entry * (ROUND_TRIP_COST_BPS / 10_000)) / risk
    return Trade(
        date=session_date.isoformat(),
        opening_range_minutes=opening_range_minutes,
        entry_time=entry_at.isoformat(),
        exit_reason=reason,
        gross_r=round(gross_r, 8),
        net_r=round(gross_r - cost_r, 8),
    )


def build_trades(bars: pd.DataFrame) -> pd.DataFrame:
    trades: list[dict] = []
    for _, day in bars.groupby(bars.index.date):
        for opening_range in OPENING_RANGES:
            trade = run_day(day, opening_range)
            if trade:
                trades.append(trade.__dict__)
    frame = pd.DataFrame(trades)
    frame["year"] = pd.to_datetime(frame["date"]).dt.year
    return frame


def maximum_drawdown(values: pd.Series) -> float:
    equity = values.cumsum()
    drawdown = equity.cummax() - equity
    return float(drawdown.max()) if not drawdown.empty else 0.0


def summarize(frame: pd.DataFrame) -> dict:
    years = sorted(int(year) for year in frame["year"].unique())
    yearly_by_parameter = []
    for (year, opening_range), group in frame.groupby(["year", "opening_range_minutes"]):
        yearly_by_parameter.append(
            {
                "year": int(year),
                "opening_range_minutes": int(opening_range),
                "trades": len(group),
                "gross_expectancy_r": round(float(group["gross_r"].mean()), 6),
                "net_expectancy_r": round(float(group["net_r"].mean()), 6),
                "net_total_r": round(float(group["net_r"].sum()), 6),
                "win_rate": round(float((group["net_r"] > 0).mean()), 6),
                "max_drawdown_r": round(maximum_drawdown(group["net_r"]), 6),
            }
        )

    walk_forward = []
    for year in years:
        train = frame[(frame["year"] >= year - 2) & (frame["year"] < year)]
        test = frame[frame["year"] == year]
        if train.empty or test.empty or train["year"].nunique() < 2:
            continue
        train_scores = train.groupby("opening_range_minutes")["net_r"].mean()
        selected = int(train_scores.sort_values(ascending=False).index[0])
        selected_test = test[test["opening_range_minutes"] == selected]
        walk_forward.append(
            {
                "oos_year": year,
                "train_years": [year - 2, year - 1],
                "selected_opening_range_minutes": selected,
                "train_expectancy_r": round(float(train_scores.loc[selected]), 6),
                "oos_trades": len(selected_test),
                "oos_expectancy_r": round(float(selected_test["net_r"].mean()), 6),
                "oos_total_r": round(float(selected_test["net_r"].sum()), 6),
                "oos_win_rate": round(float((selected_test["net_r"] > 0).mean()), 6),
                "oos_max_drawdown_r": round(maximum_drawdown(selected_test["net_r"]), 6),
            }
        )

    return {
        "opening_range_minutes_tested": list(OPENING_RANGES),
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "yearly_by_parameter": yearly_by_parameter,
        "walk_forward": walk_forward,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bars, metadata = load_bars(args.data)
    trades = build_trades(bars)
    output = {
        "schema_version": 1,
        "artifact_id": "part-time-larry-decay-timeline-01",
        "page_version": "1.0.0",
        "status": "reconstructed_from_cited_rules",
        "tutorial_url": "https://www.youtube.com/watch?v=ouveMWaInn8",
        "prior_tutorial_url": "https://www.youtube.com/watch?v=RZ_4OI_K6Aw",
        "data_source_url": DATA_URL,
        "data_license": "not specified by source repository; raw data is not redistributed",
        "data": metadata,
        "reconstruction": {
            "bar_minutes": 5,
            "session": "09:30-16:00 America/New_York naive local timestamps",
            "opening_ranges_minutes": list(OPENING_RANGES),
            "direction": "long only",
            "entry": "first post-range 5-minute close above opening-range high, no entries after 15:45",
            "stop": "entry minus opening-range size",
            "target": "entry plus opening-range size (1R)",
            "ambiguous_same_bar": "if stop and target hit in one bar, stop is applied first",
            "session_exit": "last bar at or before 15:55",
        },
        "results": summarize(trades),
        "limitations": [
            "This is a cited reconstruction, not the unavailable original tutorial source.",
            "The public dataset uses adjusted prices, duplicated rows that were removed, naive timestamps, and no published license.",
            "Five-minute bars replace the tutorial's minute database; 15/30/60 minute ranges become 3/6/12 bars.",
            "The timeline is evidence about this reconstruction only and does not imply endorsement by Part Time Larry.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output} with {len(trades)} trades")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
