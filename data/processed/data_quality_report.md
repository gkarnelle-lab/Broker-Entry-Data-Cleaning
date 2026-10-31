# Data quality report

Synthetic demonstration data only.

| Metric | Count |
|---|---:|
| Input rows | 23 |
| Output rows | 20 |
| Exact duplicates removed | 3 |
| Conflicting rows retained | 4 |
| Rows needing review | 13 |
| Allowed blank part numbers | 4 |
| Changed cells | 75 |

## Completeness

Before counts use all input rows; after counts use retained rows. Nulls are not imputed. Counts may fall when duplicate rows are removed.

| Field | Nulls before | Nulls after |
|---|---:|---:|
| tax_id | 1 | 1 |
| importer_name | 0 | 0 |
| entry_number | 0 | 0 |
| entry_line_number | 0 | 0 |
| entry_date | 0 | 0 |
| coo | 0 | 0 |
| coe | 0 | 0 |
| hts | 1 | 1 |
| part_number | 5 | 4 |
| description | 0 | 0 |
| quantity | 0 | 0 |
| unit_of_measure | 0 | 0 |
| value | 0 | 0 |
| currency | 0 | 0 |
| supplier | 1 | 1 |
| manufacturer | 23 | 20 |
| duty_amount | 0 | 0 |

## Interpretation

Blank part numbers are allowed and do not by themselves create an exception. Conflicting versions are retained; no broker is assumed authoritative. Passed means the configured structural rules passed, not that customs accuracy was verified. Invalid nonblank values remain visible in the cleaned output with review flags. Quality issues and change logs include input rows subsequently removed as duplicates.
