# Strategy Stability Evidence Ledger — Design Specification

Status: approved visual direction; implementation not started

## Problem

Self-hosting algo traders can rerun backtests and optimizations, but the jobs have materially different compute profiles. Treating both as one nightly feature hides cost and operational risk. The first value-first artifact must show the measured distinction, expose limitations, and test whether qualified readers request a scheduled stability report.

## Goals

1. Publish an independent, evidence-first report through GitHub Pages.
2. Make every headline claim traceable to the pinned Bandtastic feasibility spike.
3. Collect private, qualified signups through Tally without requesting broker credentials or write access.
4. Apply the locked demand gate without counting duplicate, test, or spam submissions.
5. Preserve the separate activation gate: at least 25% of the qualified signup cohort must schedule one automated re-backtest during week one before a scheduler becomes product work.

## Non-goals

- No broker connection, API key, repository upload, strategy execution, or parameter promotion.
- No profitability, robustness, or investment-performance claim.
- No NFI-scale extrapolation.
- No pricing checkout or subscription collection.
- No custom analytics platform, dashboard, scheduler, or backend.
- No public display of signup count or respondent data.

## Locked decisions

| Decision | Choice |
|---|---|
| Publication surface | GitHub Pages; prepare locally before selecting the public repository |
| Signup backend | Tally with private responses |
| Artifact structure | Evidence-first single-page report |
| Visual direction | Evidence Ledger |
| Publisher identity | Neutral “Strategy Stability Research” project |
| CTA | “Request a scheduled stability report” |
| Signup depth | Four visible fields: email, framework, live-strategy count, current monitoring method |
| Demand gate | Three published value-first artifacts plus eight unique qualified people within a frozen 14-day window |

## Evidence language

Primary headline:

> Nightly backtests pass. Hyperopt needs its own cadence.

This is the measured conclusion. The page must not say or imply that nightly Hyperopt is impossible. The experiment established:

- Two uncached fixed backtests completed in 15.555s and 15.675s with identical metrics.
- Peak measured fixed-backtest memory was 594,018,304 bytes.
- A separate 500-epoch, eight-worker Hyperopt completed in 43m 29s and peaked at 8.93 GB.
- Exported parameters replayed successfully on an untouched two-month OOS window; 22 trades are too few to establish robustness.
- Monthly fixed-backtest projections include every scheduled run, storage, and one result download under explicit illustrative rates.

Required caveat near the headline:

> Technical gate passed for one 7.3 KB public strategy. Demand, provider pricing, and NFI-scale economics remain unproven.

## Information architecture

The page is readable without JavaScript. Sections appear in this order:

1. **Identity and provenance navigation** — project name, field-note number, Method, Raw artifacts, GitHub.
2. **Measured verdict** — corrected headline, concise explanation, bounded verdict card.
3. **Metric ledger** — 15.6s fixed backtest, 594 MB peak RAM, 43m 29s Hyperopt, 8.31 GiB Hyperopt peak.
4. **What we ran** — pinned strategy commit, Freqtrade image digest, ten pairs, 15-minute data, uncached repetitions, untouched OOS.
5. **What changed** — nightly fixed checks and slower optimization are separate workloads and cadences.
6. **Full-month economics** — three scenarios including scheduled runs per month, result retention, storage, and egress.
7. **What this does not prove** — no profitability, robustness, demand, provider-price, or large-strategy conclusion.
8. **Qualified CTA** — Tally form and privacy/scope copy.
9. **Reproducibility footer** — raw JSON, commands, verification manifest, independent-research disclaimer.

## Visual system

- Dark forest background with mint evidence accents and warm amber caveat accents.
- Dense but calm metric cards; no gradients, trading-chart decoration, price tickers, or finance imagery.
- System sans-serif typography; tabular numerals for measurements.
- Desktop: four-column metric ledger and two-column evidence sections.
- Mobile: one-column report, two-by-two metric ledger, horizontally scrollable economics table only if required.
- Minimum WCAG AA contrast, visible focus states, semantic headings, table headers, and form labels.
- Motion is unnecessary; no animation beyond native focus/hover feedback.

## Signup form

### Visible fields

1. **Email** — required, valid email syntax.
2. **Framework** — required; Freqtrade, Jesse, Backtrader, Other.
3. **Number of live strategies** — required; 0, 1, 2–5, 6–10, 11+.
4. **Current monitoring method** — required; manual reruns, cron/scripts, platform-native tooling, nothing, other.

### Hidden fields

- `artifact_id=bandtastic-field-note-01`
- `page_version`
- `source` and standard UTM values when present

### Form copy

- “Private responses in Tally.”
- “No broker keys. No write access. No performance promise.”
- The CTA requests consideration for the validation cohort; it does not promise a report to every respondent.

### Failure behavior

- Prefer an embedded Tally form or modal.
- Always provide a normal hosted Tally link as a fallback when embedding, third-party scripts, or cookies are blocked.
- The evidence report remains fully readable if Tally is unavailable.
- A failed form submission remains on Tally’s surface; the static page must not fake success.

## Locked eight-signup gate

The gate counts people, not form rows.
The pre-committed threshold is eight unique qualified people **from a three-artifact campaign**, not eight people from this page alone. The campaign must contain:

1. `bandtastic-field-note-01` — this Evidence Ledger page.
2. `part-time-larry-decay-timeline-01` — the public tutorial-strategy decay timeline.
3. `live-reconciliation-notebook-01` — the live-vs-backtest reconciliation notebook/report.

Artifact 1 starts the gate. Artifacts 2 and 3 may follow, but both must ship inside the same frozen 14-day window. An unfinished or late artifact does not pause, reset, or extend the clock.


### Clock

- `launch_at` is frozen immediately before `bandtastic-field-note-01` is first shared externally.
- `cutoff_at = launch_at + 14 × 24 hours`.
- All three artifacts must be published within `[launch_at, cutoff_at)`; record each artifact ID, public URL, and `published_at`.
- Responses before `launch_at` are tests and never count.
- Responses after `cutoff_at` do not alter the gate result.
- Both timestamps and the three-artifact publication ledger are stored before evaluating responses.

### Qualified unique person

A person counts once when:

- all four visible fields are complete;
- the email passes basic syntax validation;
- the response timestamp is within `[launch_at, cutoff_at)`;
- the response is not an internal test, obvious spam, or duplicate.

The gate does not additionally require a nonzero live-strategy answer; that field is segmentation data rather than an unapproved hidden qualification rule.

### Normalization and deduplication

- Trim leading/trailing whitespace from email.
- Unicode-normalize and lowercase the full email.
- Do not apply provider-specific alias stripping or dot removal; those transformations can merge different people.
- Group responses by normalized email.
- Keep the earliest qualifying response per normalized email.
- Record exclusions with one reason: `prelaunch_test`, `post_cutoff`, `incomplete`, `invalid_email`, `duplicate`, or `spam`.

### Evaluation

- Export a private Tally CSV at cutoff.
- Produce a private gate ledger containing normalized identifiers, inclusion status, exclusion reason, and source artifact. Do not commit raw emails to the public repository.
- **PASS:** all three artifact IDs have valid publication records within the frozen window and at least eight included unique people exist across their deduplicated responses.
- **FAIL:** any artifact was not published within the frozen window or fewer than eight included unique people exist.
- No artifact count, threshold, cutoff, qualification rule, or exclusion rule moves after launch.

## Separate activation gate

Only after the eight-signup gate passes:

1. Offer the complete qualified cohort a minimal cron-based concierge scheduler.
2. Denominator: all included unique people from the passed demand gate.
3. Numerator: cohort members who schedule at least one automated re-backtest within the first seven days of scheduler access.
4. **PASS:** numerator / denominator ≥ 25%.
5. Accepting, opening, or requesting another manually generated report does not count.

## Page data flow

```text
Pinned benchmark JSON
        ↓ build-time validation
Static GitHub Pages report ──→ raw public artifacts
        ↓ CTA
Embedded or linked Tally form
        ↓ private responses
Cutoff CSV export
        ↓ normalize / dedupe / exclude
Private gate ledger
        ↓
PASS (≥8 unique people) → cron concierge test
FAIL (<8 unique people) → kill candidate
```

## Repository shape for implementation

The implementation plan may refine filenames but not responsibilities:

```text
strategy-stability-research/
  index.html                 # semantic report content
  assets/
    styles.css               # Evidence Ledger visual system
    report-data.json         # public measured summary only
  raw/
    verification.json
    economics.json
    benchmark-summary.json   # no large trade-level or private data
  scripts/
    validate-report-data.*   # prevents claim/data drift at build time
    evaluate-gate.*          # local/private CSV → private ledger; never published
  docs/
    methodology.md
    gate-operations.md
```

Private Tally exports and gate ledgers remain outside the GitHub Pages publication tree and are ignored by version control.

## Validation and testing

### Content integrity

- Every displayed number equals the public summary JSON.
- The corrected headline appears exactly once; “Nightly Hyperopt does not” appears nowhere.
- Monthly economics multiply by rolling windows, scheduled runs per month, and strategies per user before storage/egress.
- Limitations are visible before the CTA.

### Functional checks

- Page renders without JavaScript.
- All provenance/raw-artifact links resolve.
- Tally embed and hosted fallback both open the same form.
- Required fields reject incomplete submissions.
- Source/artifact hidden fields arrive in a test response.
- No test response can count because it precedes `launch_at`.

### Gate checks

Use a synthetic private CSV to verify:

- case and whitespace email duplicates collapse to one person;
- provider-specific aliases remain distinct;
- incomplete, invalid, spam, prelaunch, and post-cutoff rows are excluded with reasons;
- exactly seven included people fails and exactly eight passes;
- raw emails never appear in public files or logs.

### Responsive and accessibility checks

- Verify desktop and mobile layouts in a real browser.
- Keyboard navigation reaches all links and the CTA.
- Headings, tables, labels, contrast, and focus states meet the stated design.

## Publication safety

Repository creation, GitHub Pages publication, Tally form publication, and external distribution posts are external side effects. Build them locally first. Immediately before each public action, confirm the exact GitHub owner/repository, Tally account/form, public URL, launch timestamp, distribution target, and post copy.

## Acceptance criteria

- The locally prepared page matches the approved Evidence Ledger direction.
- Claims and limitations match the verified spike artifacts.
- The Tally contract contains exactly four visible required fields plus approved hidden attribution fields.
- Gate evaluation requires all three publication records and counts eight unique qualified people under the frozen rules above.
- The locked 25% automated-scheduling activation gate remains separate and unchanged.
- No scheduler implementation begins before the demand gate passes.
