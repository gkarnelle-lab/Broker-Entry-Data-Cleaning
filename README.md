# Broker Import Entry Data Cleaning & Standardization

A beginner-friendly data analyst portfolio project that brings three inconsistent broker extracts into one traceable entry-line dataset.

**Focus:** handling nulls, deduplication, consistent formatting, and documenting data quality. Blank part numbers are allowed.

All records, brokers, suppliers, tax IDs, entry numbers, and tariff codes are fictional. Tariff codes are intentionally synthetic identifiers, not verified classifications. This project demonstrates data engineering rules, not customs compliance or filing validation.

## Business scenario

A company receives monthly import entry reports from Broker ABC, Broker USA, and Broker XYZ. Each broker handles different entries for the same importer. The analyst combines the reports into a consistent dataset for review and analysis.

Each sample file is a combined monthly extract. Overlapping exports can repeat a line, and revised exports can report a different value or fill a previously blank part number. These issues occur within a broker's data, not because three brokers handled the same entry.

| Broker | Entries handled | Example quality issue |
|---|---|---|
| Broker ABC | DEMO-000001 through DEMO-000003 | Repeated line and differing value versions |
| Broker USA | DEMO-000004 through DEMO-000006 | Repeated lines and blank-versus-populated part number versions |
| Broker XYZ | DEMO-000007 through DEMO-000009 | Invalid quantity, HTS, and currency |

There are nine distinct entries, each with two entry lines before duplicates and revisions. No entry is shared across brokers. Without revision timestamps or broker confirmation, differing versions are kept for review rather than assumed to be corrections.

## Results from the included example

| Measure | Result |
|---|---:|
| Input rows across three brokers | 23 |
| Exact normalized duplicates removed | 3 |
| Retained rows | 20 |
| Conflicting rows retained for review | 4 |
| Rows needing review, including conflicts | 13 |
| Allowed blank part numbers in retained rows | 4 |
| Standardized cells across all input rows | 79 |

The intentionally small dataset makes every decision easy to inspect. A review flag is a useful output: cleaning should expose unresolved problems rather than conceal them.

## Run it

Requires Python 3.9 or later. No third-party packages, accounts, or installation steps are needed.

From this project's folder:

```bash
python3 src/clean.py
python3 -m unittest discover -s tests -v
```

On Windows, use `python` if that is your Python command.

To use different folders and a reviewed mapping:

```bash
python3 src/clean.py --input path/to/raw --output path/to/results --mapping path/to/mappings.json
```

The script never modifies raw files. Re-running overwrites the named result files with deterministic results. Use separate input and output folders. Unexpected headers or malformed CSV rows stop processing instead of silently dropping data.

## Before and after

These are formatting examples from different brokers, not matching transactions:

| Field | Broker ABC raw → cleaned | Broker USA raw → cleaned |
|---|---|---|
| Entry / line | `DEMO-000001` / `1` → unchanged | `DEMO-000004` / `2` → unchanged |
| Tax ID | `00-1234567` → `001234567` | `001234567` → unchanged |
| Entry date | `09/15/2026` → `2026-09-15` | `2026-09-15` → unchanged |
| COO | `China` → `CN` | `CN` → unchanged |
| Synthetic HTS | `0000.00.0001` → `0000000001` | `0000000001` → unchanged |
| Value | `$125.00` → `125.00` | `1000.00` → unchanged |
| Part number | `00001-A` → unchanged | whitespace → null (allowed) |

The matching key is **broker + tax ID + entry number + entry line number**. All 18 business fields must match within that broker before automatic duplicate removal. A different value or part number on the same key becomes a conflict. A blank part number is allowed and never acts as a match key.

## What is included

```text
config/broker_mappings.json     Explicit header mappings and broker date formats
data/raw/                      Three messy fictional broker files
data/processed/                Reproducible example results
docs/cleaning_rules.md          Decisions, scope, and limitations
docs/data_dictionary.md         Field definitions and requirements
src/clean.py                   Standard-library cleaning pipeline
tests/test_clean.py             Automated behavior checks
```

Broker ABC uses commas and US-style dates; Broker USA changes names and reverses column order; Broker XYZ uses semicolons, another column order, and year/month/day dates. Row order varies. The files contain missing values, placeholders, extra whitespace, exact duplicates, conflicting versions, and invalid data.

## Review the results

1. Start with [the data quality report](data/processed/data_quality_report.md).
2. Inspect [cleaned entries](data/processed/cleaned_entries.csv), including status and source columns.
3. Review [exceptions](data/processed/exceptions.csv) before using the data for analysis.
4. Trace changes through [the cell change log](data/processed/change_log.csv) and [duplicate removal log](data/processed/removed_duplicates.csv).

`quality_issues.csv` records individual issues; `quality_summary.json` supplies machine-readable metrics. The cleaned file includes unresolved values with flags, so filter or resolve `needs_review` rows before downstream analysis. The exceptions file contains the full rows needing review.

## Skills demonstrated

- Mapping heterogeneous source schemas without relying on column positions.
- Normalizing null placeholders without confusing missing values with zero.
- Preserving leading zeros in identifiers and allowing blank part numbers.
- Comparing normalized business records while preserving source lineage.
- Separating exact duplicates from conflicting records.
- Applying explicit, testable rules and documenting unresolved quality issues.
