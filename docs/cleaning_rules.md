# Cleaning rules and quality decisions

## Grain and scope

One row represents one broker-reported import entry line, not a shipment total. Each broker handles separate entries for the same importer, with two lines per entry. Each file represents a combined monthly extract that may include overlapping exports and revised versions. No sample entry appears under multiple brokers. This demo defines `entry_date` as the entry date supplied by the broker and `value` as that line's declared value in the specified currency. Real integrations must confirm both meanings before mapping. Do not substitute invoice totals, payment dates, or settlement dates.

No external tariff lookup, country registry, broker API, or official entry verification is performed. Tax IDs are modeled as nine-digit US EIN-style identifiers for this example only. Country and unit lookups are deliberately small reviewed demo lists; unmatched values are retained and flagged. These are project assumptions, not universal broker or customs requirements.

## Null handling

- Trim and collapse whitespace; treat empty strings, `N/A`, `NULL`, and `-` as null, ignoring case.
- Do not treat numeric `0` or `0.00` as null.
- Never impute identifiers, countries, amounts, or tariff classifications.
- Require the fields marked required in the dictionary. Missing required fields generate exceptions.
- Allow blank part number, description, manufacturer, and duty amount. Missing duty is unknown, not zero.
- Track blank part numbers with `part_number_missing` and summary counts. They do not invalidate a row by themselves.
- Preserve populated part numbers exactly apart from whitespace normalization; no case folding or numeric conversion.
- Placeholder rules assume these tokens mean missing in the fictional sources. Review tokens for each real source before using them, especially legitimate part numbers such as `-`.

## Formatting

- Use named header mappings, never source column positions. Require all configured columns to be present and reject unexpected schema drift.
- Parse dates only with each broker's configured formats. No automatic day/month guessing or invalid-date repair.
- Convert recognized country names to the configured two-letter codes.
- Remove approved separators from tax IDs and HTS; require nine and ten ASCII digits respectively. Do not pad short codes with zeros.
- Keep identifiers as text; reduce a positive entry line integer such as `001` to `1` for matching. Entry number and part number case remain unchanged.
- Standardize supplier, importer, and manufacturer case to uppercase, with collapsed whitespace. Do not fuzzy-merge legal entities or remove suffixes.
- Parse US numeric syntax with Decimal; accept correctly grouped commas and an optional `$` or `USD` on money fields. The supplied currency column is authoritative; `$` alone does not infer a currency. Other source conventions need reviewed parsing rules.
- Retain money to two decimal places. Flag more precise money instead of rounding it away. Preserve quantity precision. Negative values require review under demo rules; actual adjustment workflows may allow them.
- Recognize configured currencies (USD, CAD, MXN) and units (PCS, KG); no exchange-rate conversion or duty calculation.
- Keep invalid nonblank values visible, attach an issue, and preserve their original raw values in issue logs. The output therefore mixes valid numeric strings and invalid source text until exceptions are resolved.

## Deduplication and conflicts

1. Normalize all business fields while retaining file and source-record provenance.
2. Require a nonblank, structurally valid key: broker + tax ID + entry number + entry line number. Without it, retain the row even if its contents repeat.
3. Within the same broker, remove an exact normalized match only when **all 18 business fields** match. Broker identity is included; file and row provenance are excluded. Never automatically merge records across brokers.
4. Record every removed record's ID and its retained record ID. The first record in sorted file and source-record order is kept. This is deterministic retention, not broker authority.
5. Group retained rows by valid key within the same broker. If multiple versions remain, flag every version and list the differing fields. Preserve all versions, including blank-versus-populated part number conflicts. File order does not establish which version is newer. Revision timestamps are unavailable in this demo, so no final version is automatically selected.

This assumes duplicate extracts of the same entries rather than independent transactions that merely look similar. An entry-line key is a matching candidate, not proof of global uniqueness: amendments, additional detail lines, years, and source systems may require more keys. Identical records containing other validation problems can still be removed if the key is valid; the retained copy remains flagged. No fuzzy deduplication or automatic conflict resolution occurs.

## Documentation and audit trail

`source_row` is the CSV record number with header counted as 1, not a physical line number when a quoted field spans lines. `record_id` joins filename and source row. Source filenames must be unique within the input folder.

The cell change log includes null-token cleanup and formatting changes. The issue log covers original input validation issues and retained-row conflicts. Removed duplicates can have issue/change-log entries; join on `record_id` to audit them. `cleaned_entries.csv` is the retained dataset; `exceptions.csv` is its review subset, not extra records to append.

Before null counts use input rows and after counts use retained rows. A decrease due to removed duplicates is not missing-data recovery. No nulls are guessed or filled. Blank part numbers are reported separately from invalid records. Summary counts describe overlapping categories and should not be added together.

Reviewers should inspect exceptions against original sources, make justified corrections in a new reviewed input version or a separately documented override process, then rerun. This demo does not provide a manual-override interface. Raw files remain untouched.
