# Data dictionary

All identifiers are strings. Empty CSV cells mean null. Dates and decimals are serialized consistently as text in CSV. Required means required by this project's checks, not a statement about filing law.

| Field | Meaning / format | Required |
|---|---|---|
| tax_id | Fictional importer EIN-style ID; nine digits, leading zeros preserved | Yes |
| importer_name | Importing company; uppercase normalized whitespace | Yes |
| entry_number | Fictional customs entry identifier; text | Yes |
| entry_line_number | Positive integer serialized as text | Yes |
| entry_date | Broker-reported entry date, ISO `YYYY-MM-DD` | Yes |
| coo | Country of origin, reviewed demo country code | Yes |
| coe | Country of export, reviewed demo country code | Yes |
| hts | Synthetic ten-digit tariff identifier; structural checks only | Yes |
| part_number | Product identifier; text with leading zeros; blank allowed | No |
| description | Product description; whitespace normalized | No |
| quantity | Nonnegative decimal quantity, paired with unit | Yes |
| unit_of_measure | PCS or KG in demo | Yes |
| value | Broker-reported declared line value; nonnegative decimal, two places | Yes |
| currency | Currency of value and duty: USD, CAD, MXN in demo | Yes |
| supplier | Supplier name; uppercase normalized whitespace | Yes |
| manufacturer | Manufacturer if supplied; uppercase; no inference from supplier | No |
| duty_amount | Broker-reported line duty; nonnegative decimal, two places; not calculated | No |

## Traceability and quality fields

| Field | Meaning |
|---|---|
| record_id | Source filename plus CSV record number |
| broker | Broker label from reviewed mapping |
| source_file | Original input filename |
| source_row | CSV record number, header counted as 1 |
| part_number_missing | `yes` or `no`; informational |
| duplicate_flag | `none` or `conflict`; removed rows have a separate log |
| validation_status | `passed` or `needs_review` under configured checks |
| validation_issues | Semicolon-separated problems; empty when passed |

No enrichment is inferred from HTS, part number, or supplier. A passed structural check does not verify business accuracy or legal classification.
