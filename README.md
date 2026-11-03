# Broker Import Entry Data Cleaning & Standardization

The project demonstrates how structured data quality controls, documented transformation rules, exception reporting, and source traceability can support reliable customs operations and downstream compliance review.

**Core Focus:** Data standardization | Data governance | Exception management | Data quality controls | Audit support

> **Portfolio Disclaimer:** All records, brokers, suppliers, tax IDs, entry numbers, and tariff codes are fictional. Tariff codes are synthetic identifiers, not verified HTS classifications. This project demonstrates data engineering and operational data quality practices, not regulatory compliance determination or customs filing validation.

---

## 📋 1. Business Problem & Objective

### The Business Challenge

Organizations frequently receive import entry data from multiple customs brokers, each using different reporting formats, naming conventions, date structures, and data quality standards.

Without consistent processing controls, these differences can create duplicate records, unresolved discrepancies, unreliable reporting, and additional manual review requirements.

### The Solution

This project implements a reproducible Python pipeline that:

- Standardizes inconsistent broker data into a common schema.
- Normalizes dates, identifiers, monetary values, and missing data.
- Removes exact normalized duplicates while retaining conflicting versions.
- Identifies invalid or incomplete records requiring review.
- Generates exception reports and detailed transformation logs.
- Preserves source information to support traceability.

### Intended Business Value

Establishes a repeatable data preparation process that improves the consistency, transparency, and reviewability of customs entry data.

Rather than automatically correcting uncertain information, the pipeline flags unresolved discrepancies for investigation.

---

## 🏢 2. Fictional Business Scenario

A company receives monthly import entry reports from three independent customs brokers:

| Customs Broker | Entries Handled | Example Data Quality Issue |
|---|---|---|
| Broker ABC | DEMO-000001 to DEMO-000003 | Duplicate lines and conflicting entered values |
| Broker USA | DEMO-000004 to DEMO-000006 | Repeated records and inconsistent part number completeness |
| Ziggy & Co. Customs Brokerage | DEMO-000007 to DEMO-000009 | Invalid quantity, synthetic HTS, and currency values |

Each broker handles different entries for the same importer.

The dataset contains nine distinct entries, each with two entry lines before duplicates and revisions. No entry is shared across brokers.

Overlapping exports may contain duplicate records or conflicting versions of the same entry line. Because revision timestamps and broker confirmations are unavailable, conflicting versions are retained for review rather than assumed to be valid corrections.

---

## 🛠️ 3. Data Pipeline Architecture

### Stage 1: Data Ingestion

Three fictional broker CSV extracts are loaded from `data/raw/`.

The pipeline uses explicit configuration mappings to accommodate differences in:

- Column names and column order
- File delimiters
- Date formats
- Broker-specific source structures

### Stage 2: Standardization & Transformation

Python standard-library processing applies documented normalization rules to:

- Entry dates
- Importer tax identifiers
- Country-of-origin codes
- Synthetic tariff identifiers
- Monetary values
- Missing values and placeholders
- Part numbers

Leading zeros in identifiers are preserved, and blank part numbers remain permissible.

### Stage 3: Data Quality Controls

The pipeline evaluates records against explicit validation and duplicate-detection rules.

The matching key is:

**Broker + Tax ID + Entry Number + Entry Line Number**

All 18 business fields must match within the same broker before a record is automatically removed as an exact duplicate.

Records sharing a matching key but containing differing values are retained and flagged as conflicts.

### Stage 4: Exception Identification

Records with unresolved data quality issues are identified for further review.

The pipeline distinguishes between:

- Exact duplicates eligible for removal
- Conflicting versions requiring investigation
- Invalid or incomplete field values
- Permissible missing information

### Stage 5: Reporting & Traceability

Standardized outputs, exception reports, quality metrics, and transformation logs are generated under `data/processed/`.

Raw source files remain unchanged.

---

## 🛡️ 4. Enterprise Data Governance & Compliance Controls

This project applies foundational data governance principles to a fictional customs operations environment.

### Data Quality Control Framework

| Control Area | Implemented Control | Governance Purpose |
|---|---|---|
| Schema Consistency | Explicit broker field mappings | Standardize source data structures |
| Data Completeness | Missing-value identification | Surface incomplete records for review |
| Data Validity | Field-level validation rules | Identify invalid or unexpected values |
| Duplicate Management | Exact normalized record comparison | Prevent duplicate records in standardized outputs |
| Conflict Management | Retention and flagging of differing versions | Prevent unsupported assumptions about corrections |
| Data Traceability | Source fields and transformation logs | Support review of processing decisions |
| Quality Monitoring | Summary metrics and issue reporting | Provide visibility into data quality outcomes |

### Data Stewardship & Accountability

In an enterprise implementation, responsibility for customs data quality would typically be distributed across operational and governance functions.

An illustrative responsibility model could include:

| Role | Proposed Responsibility |
|---|---|
| Customs Operations Analyst | Review entry data exceptions and investigate discrepancies |
| Trade Compliance Team | Evaluate issues requiring regulatory interpretation |
| Data Steward | Maintain data definitions, quality rules, and issue documentation |
| Data Engineering / IT | Maintain processing logic, mappings, and technical controls |
| Internal Audit | Independently assess control design and supporting evidence |

*These responsibilities illustrate a proposed enterprise governance model. The project does not implement user assignments, approvals, or role-based access.*

### Audit Support & Traceability

The project produces several artifacts that can support data quality review:

- **Change Log:** Records standardized cell-level changes.
- **Duplicate Removal Log:** Identifies records removed through exact matching.
- **Exception Report:** Contains records requiring further investigation.
- **Data Quality Report:** Summarizes processing results and unresolved issues.
- **Source Tracking:** Preserves source information in standardized records.

These outputs provide traceable processing evidence, but do not constitute a complete enterprise audit management system.

---

## 📊 5. Results & Key Findings

The included synthetic dataset produces the following results:

| Data Quality Metric | Result |
|---|---:|
| Input records across three brokers | 23 |
| Exact normalized duplicates removed | 3 |
| Retained records | 20 |
| Conflicting records retained for review | 4 |
| Records requiring review, including conflicts | 13 |
| Permissible blank part numbers | 4 |
| Standardized cells across input records | 79 |

### Key Observations

**Duplicate Detection:** Three exact normalized duplicates were removed without automatically discarding conflicting records.

**Exception Visibility:** Thirteen retained records were identified as requiring review, including four conflicting versions.

**Controlled Standardization:** Seventy-nine cells were standardized across the input dataset.

**Preservation of Uncertainty:** Records containing unresolved issues remain available for investigation instead of being silently corrected or excluded.

The intentionally small dataset allows users to inspect individual decisions and understand the effect of each transformation rule.

---

## 🔎 6. Before & After: Data Standardization

The examples below come from different brokers and do not represent matching transactions.

| Field | Broker ABC: Raw → Cleaned | Broker USA: Raw → Cleaned |
|---|---|---|
| Entry / Line | `DEMO-000001` / `1` → unchanged | `DEMO-000004` / `2` → unchanged |
| Tax ID | `00-1234567` → `001234567` | `001234567` → unchanged |
| Entry Date | `09/15/2026` → `2026-09-15` | `2026-09-15` → unchanged |
| Country of Origin | `China` → `CN` | `CN` → unchanged |
| Synthetic HTS | `0000.00.0001` → `0000000001` | `0000000001` → unchanged |
| Entered Value | `$125.00` → `125.00` | `1000.00` → unchanged |
| Part Number | `00001-A` → unchanged | Whitespace → null (allowed) |

---

## ⚙️ 7. Setup & Installation

### Requirements

- Python 3.9 or later
- No third-party Python packages required
- No external accounts or API credentials required

### Clone the Repository

```bash
git clone https://github.com/gkarnelle-lab/Broker-Entry-Data-Cleaning.git
cd Broker-Entry-Data-Cleaning
```

### Run the Data Cleaning Pipeline

```bash
python3 src/clean.py
```

### Run Automated Tests

```bash
python3 -m unittest discover -s tests -v
```

On Windows, use `python` instead of `python3` if appropriate.

### Optional: Custom Input and Output Directories

```bash
python3 src/clean.py --input path/to/raw --output path/to/results --mapping path/to/mappings.json
```

The script never modifies raw input files. Re-running the pipeline overwrites the named output files with deterministic results.

Unexpected headers or malformed CSV rows stop processing instead of silently dropping data.

---

## 📦 8. Repository Structure

```text
Broker-Entry-Data-Cleaning/
├── config/
│   └── broker_mappings.json
├── data/
│   ├── raw/
│   └── processed/
│       ├── cleaned_entries.csv
│       ├── exceptions.csv
│       ├── quality_issues.csv
│       ├── change_log.csv
│       ├── removed_duplicates.csv
│       ├── quality_summary.json
│       └── data_quality_report.md
├── docs/
│   ├── cleaning_rules.md
│   └── data_dictionary.md
├── src/
│   └── clean.py
├── tests/
│   └── test_clean.py
└── README.md
```

### Review the Generated Outputs

1. [Data Quality Report](data/processed/data_quality_report.md) — Review overall processing results.
2. [Cleaned Entries](data/processed/cleaned_entries.csv) — Inspect standardized records and review statuses.
3. [Exceptions](data/processed/exceptions.csv) — Investigate unresolved issues.
4. [Change Log](data/processed/change_log.csv) — Trace cell-level transformations.
5. [Removed Duplicates](data/processed/removed_duplicates.csv) — Review duplicate-removal decisions.

Additional outputs include `quality_issues.csv`, which records individual issues, and `quality_summary.json`, which provides machine-readable metrics.

Records marked `needs_review` should be resolved or appropriately filtered before downstream analytical use.

---

## 🔭 9. Limitations & Future Enhancements

### Current Limitations

- All data is fictional and intentionally limited in scale.
- Synthetic tariff identifiers are not validated against official HTS schedules.
- The pipeline does not determine regulatory compliance or filing eligibility.
- Conflicting records require external verification before resolution.
- The project does not implement formal approval workflows, access controls, or evidence retention policies.

### Potential Enterprise Enhancements

- **Compliance Control Matrix:** Document control owners, objectives, evidence requirements, and review frequency.
- **Exception Management Workflow:** Introduce issue assignments, remediation statuses, and reviewer approvals.
- **Data Stewardship Framework:** Establish critical data elements and accountable data owners.
- **Audit Evidence Management:** Define retention requirements and review procedures.
- **Data Quality Scorecard:** Expand quality metrics into recurring operational monitoring.
- **Governance Documentation:** Add formalized control procedures and a responsibility matrix.

These enhancements are proposed future capabilities, not existing automated functionality.

---

## 🎯 10. Skills Demonstrated

**Technical Skills:** Python, CSV processing, schema mapping, data normalization, automated testing, and reproducible data pipelines.

**Data Governance:** Data quality rules, data dictionaries, source traceability, exception reporting, and documented transformation logic.

**Customs Operations:** Broker data reconciliation, entry-line analysis, identification of data discrepancies, and preparation of records for compliance review.

**Enterprise Thinking:** Internal control design concepts, accountability, operational risk awareness, and audit-support documentation.

---

*This portfolio project illustrates how reliable data processing and governance principles can improve the transparency and reviewability of customs operations.*
