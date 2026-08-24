# Demand Gate Operations

The campaign requires three published value-first artifacts and eight unique qualified people. Artifact 1 starts an immutable 14-day clock.

## Before launch

1. Confirm the exact first external distribution target and post copy.
2. Confirm the production Artifact 1 URL and shared Tally form.
3. Keep all Tally exports, spam lists, gate configuration, and gate results under ignored `private/`.

## Start the clock

Immediately before sharing Artifact 1:

```bash
python scripts/gate_config.py freeze private/gate-config.json "https://confirmed-artifact-one-url" --response-timezone "+00:00"
```

This records `launch_at`, computes `cutoff_at = launch_at + 14 days`, records Artifact 1, and freezes how naive Tally CSV timestamps are interpreted. The verified prelaunch export used UTC (`+00:00`) while the UI displayed local `+08:00`; re-verify the CSV behavior before launch and pass the observed offset explicitly. There is no reset or extension command.

## Record follow-up artifacts

After externally publishing Artifact 2 or Artifact 3:

```bash
python scripts/gate_config.py publish private/gate-config.json ARTIFACT_ID "https://confirmed-public-url"
```

Both follow-up artifacts must be recorded before cutoff. A missing or late artifact fails the campaign even if eight people sign up.

## Evaluate at cutoff

1. Export Tally responses to `private/tally-responses.csv`.
2. Put manually reviewed spam emails, one per line, in `private/spam.txt`.
3. Run:

```bash
python scripts/evaluate_gate.py private/tally-responses.csv private/gate-config.json private/spam.txt private/gate-result.json
```

The evaluator normalizes email with Unicode NFKC, trimming, and case folding; it does not strip provider aliases or dots. It keeps the earliest qualifying response and excludes prelaunch tests, post-cutoff rows, incomplete/invalid rows, duplicates, and reviewed spam. The private output contains email hashes rather than raw email addresses.

- PASS: all three artifacts were published inside the window and at least eight unique qualified people remain.
- FAIL: any artifact is missing/late or fewer than eight unique qualified people remain.

PASS permits only a cron-concierge activation test. A scheduler product remains blocked until at least 25% of the included cohort schedules one automated re-backtest within seven days of access.
