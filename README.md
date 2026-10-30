# Broker Import Entry Data Cleaning & Standardization

A beginner-friendly data analyst portfolio project that brings three inconsistent broker extracts into one traceable entry-line dataset.

**Focus:** handling nulls, deduplication, consistent formatting, and documenting data quality. Blank part numbers are allowed.

All records, brokers, suppliers, tax IDs, entry numbers, and tariff codes are fictional. Tariff codes are intentionally synthetic identifiers, not verified classifications. This project demonstrates data engineering rules, not customs compliance or filing validation.

## Results from the included example

| Measure | Result |
|---|---:|
| Input rows across three brokers | 23 |
| Exact normalized duplicates removed | 3 |
| Retained rows | 20 |
| Conflicting rows retained for review | 4 |
| Rows needing review, including conflicts | 13 |
| Allowed blank part numbers in retained rows | 4 |
| Standardized cells across all input rows | 75 |

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

These extracts represent the same business line, with different headers, order, and formatting:

| Field | Broker ABC | Broker USA | Standardized |
|---|---|---|---|
| Tax ID | `00-1234567` | `001234567` | `001234567` |
| Entry date | `09/15/2026` | `2026-09-15` | `2026-09-15` |
| COO | `China` | `CN` | `CN` |
| Synthetic HTS | `0000.00.0001` | `0000000001` | `0000000001` |
| Value | `$125.00` | `125.00` | `125.00` |
| Supplier | `  demo supplier ltd  ` | `DEMO SUPPLIER LTD` | `DEMO SUPPLIER LTD` |

The full business fields must match after normalization before an automatic duplicate removal occurs. A shared match key with a different value or part number becomes a conflict. A blank part number never acts as a match key.

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
