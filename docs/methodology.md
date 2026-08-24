# Field Note 01 Methodology

## Reproducible inputs

- Strategy: `Bandtastic.py`
- Strategy commit: `eff78d3ce3456b52c68a4e9a33cc055a56b801ff`
- Freqtrade image: `freqtradeorg/freqtrade:2026.7`
- Image digest: `sha256:da3428fde0f7f9f976eaafba8abc7eba42bf978f23e4808347e15d476ad9a643`
- Data: Binance spot, ten USDT pairs, 15-minute candles
- Download range: 2025-01-01 through 2025-09-01
- Fixed benchmark range: 2025-01-01 through 2025-07-01
- Untouched OOS range: 2025-07-01 through 2025-09-01
- Fee: 0.001 on entry and exit
- Starting wallet: 10,000 USDT
- Stake: 100 USDT
- Maximum open trades: 5

## Fixed backtest

Two repetitions used `--cache none`; Docker startup is included in wall time. They completed in 15.5549233 and 15.6749620 seconds and produced identical metrics. Maximum measured memory was 594,018,304 bytes.

## Hyperopt

The separate workload used:

- 500 epochs
- 8 workers
- random state 42
- `SharpeHyperOptLossDaily`
- buy and sell spaces

It completed in 2,608.9872605 seconds and peaked at 8,927,089,524 bytes. Hyperopt is excluded from nightly fixed-backtest economics and is treated as weekly, monthly, on-demand, or bring-your-own compute.

## OOS replay

The best in-sample parameters were exported and replayed on the untouched OOS range. The replay contained 22 trades. It proves that train/export/replay works; it does not establish parameter robustness.

## Monthly economics

Formula:

```text
cost per window-run
× rolling windows per scheduled run
× scheduled runs per month
× strategies per user
+ retained result storage
+ egress
```

Illustrative assumptions—not a provider quote:

- General worker: $0.10/hour
- Minimum billable duration: 60 seconds/job
- 30 scheduled runs/month
- 30-day result retention
- Object storage: $0.023/GB-month
- Egress: $0.09/GB, assuming each retained result is downloaded once

Excluded: orchestration, database, observability, support, paid data, retries, taxes, and idle capacity.

## Public evidence files

- [`report-data.json`](../raw/report-data.json)
- [`verification.json`](../raw/verification.json)
- [`economics.json`](../raw/economics.json)

This research is not investment advice and makes no profitability claim.
