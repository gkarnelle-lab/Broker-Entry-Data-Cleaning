"""Clean fictional customs entry lines. Python standard library only."""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['tax_id', 'importer_name', 'entry_number', 'entry_line_number',
          'entry_date', 'coo', 'coe', 'hts', 'part_number', 'description',
          'quantity', 'unit_of_measure', 'value', 'currency', 'supplier',
          'manufacturer', 'duty_amount']
NULLS = {'', 'n/a', 'null', '-'}
COUNTRIES = {'us': 'US', 'usa': 'US', 'united states': 'US', 'cn': 'CN',
             'china': 'CN', 'mx': 'MX', 'mexico': 'MX', 'ca': 'CA',
             'canada': 'CA', 'vn': 'VN', 'vietnam': 'VN'}
REQUIRED = {'tax_id', 'importer_name', 'entry_number', 'entry_line_number',
            'entry_date', 'coo', 'coe', 'hts', 'quantity', 'unit_of_measure',
            'value', 'currency', 'supplier'}
KEY = ['tax_id', 'entry_number', 'entry_line_number']


def normalize(field, raw, config):
    """Return normalized value plus an issue, without guessing invalid values."""
    value = ' '.join((raw or '').split())
    if value.casefold() in NULLS:
        return '', 'required value missing' if field in REQUIRED else ''
    if field == 'entry_date':
        for fmt in config['date_formats']:
            try:
                return datetime.strptime(value, fmt).date().isoformat(), ''
            except ValueError:
                pass
        return value, 'invalid date for configured broker formats'
    if field in ('coo', 'coe'):
        if value.casefold() in COUNTRIES:
            return COUNTRIES[value.casefold()], ''
        return value, 'unmapped country; expand reviewed lookup'
    if field in ('tax_id', 'hts'):
        compact = re.sub(r'[-.\s]', '', value)
        length = 9 if field == 'tax_id' else 10
        if not re.fullmatch(r'[0-9]{%d}' % length, compact):
            return value, f'expected {length} digits under demo rules'
        return compact, ''
    if field == 'entry_line_number':
        if value.isascii() and value.isdigit() and int(value) > 0:
            return str(int(value)), ''
        return value, 'expected positive integer'
    if field in ('value', 'duty_amount', 'quantity'):
        number = value
        if field != 'quantity':
            number = re.sub(r'(?i)\bUSD\b', '', number).replace('$', '').strip()
        # Only US-style numeric grouping is accepted by this demo.
        if not re.fullmatch(r'-?(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?', number):
            return value, 'invalid number; expected US numeric format'
        try:
            parsed = Decimal(number.replace(',', ''))
            if parsed < 0:
                return value, 'negative amount or quantity requires review'
            if field != 'quantity' and parsed.as_tuple().exponent < -2:
                return value, 'more than two decimal places; no automatic rounding'
            return (format(parsed, '.2f') if field != 'quantity' else format(parsed, 'f')), ''
        except InvalidOperation:
            return value, 'invalid number'
    if field == 'currency':
        value = value.upper()
        return value, '' if value in {'USD', 'CAD', 'MXN'} else 'unsupported demo currency'
    if field == 'unit_of_measure':
        units = {'pcs': 'PCS', 'pieces': 'PCS', 'each': 'PCS', 'kg': 'KG', 'kilograms': 'KG'}
        return units.get(value.casefold(), value), '' if value.casefold() in units else 'unmapped unit'
    if field in ('supplier', 'manufacturer', 'importer_name'):
        return value.upper(), ''
    return value, ''


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(input_dir, output_dir, mapping_path):
    mappings = json.loads(mapping_path.read_text())
    records, issues, changes = [], [], []
    before = Counter()
    files = sorted(input_dir.glob('*.csv'))
    if not files:
        raise ValueError('No input CSV files found')
    for file in files:
        if file.name not in mappings:
            raise ValueError(f'No explicit broker mapping for {file.name}')
        config = mappings[file.name]
        with file.open(newline='', encoding='utf-8-sig') as handle:
            reader = csv.DictReader(handle, delimiter=config.get('delimiter', ','))
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError(f'{file.name}: missing or repeated column headers')
            if set(reader.fieldnames) != set(config['columns']):
                raise ValueError(f'{file.name}: columns differ from reviewed mapping')
            if set(config['columns'].values()) != set(FIELDS):
                raise ValueError(f'{file.name}: mapping must cover all standard fields')
            for row_number, source in enumerate(reader, 2):
                if None in source or any(v is None for v in source.values()):
                    raise ValueError(f'{file.name}:{row_number}: malformed CSV row')
                provenance = {'record_id': f'{file.name}:{row_number}',
                              'broker': config['broker'], 'source_file': file.name,
                              'source_row': row_number}
                row = dict(provenance)
                row_issues = []
                invalid = set()
                for source_col, field in config['columns'].items():
                    raw = source[source_col]
                    before[field] += ' '.join(raw.split()).casefold() in NULLS
                    value, issue = normalize(field, raw, config)
                    row[field] = value
                    if raw != value:
                        changes.append({**provenance, 'field': field, 'original': raw, 'cleaned': value})
                    if issue:
                        invalid.add(field)
                        row_issues.append(f'{field}: {issue}')
                        issues.append({**provenance, 'field': field, 'issue': issue, 'original': raw})
                row['_issues'] = row_issues
                row['_key_valid'] = all(row[k] and k not in invalid for k in KEY)
                records.append(row)

    # First remove exact normalized business records. Broker provenance is retained separately.
    seen, retained, duplicate_log = {}, [], []
    for row in records:
        signature = tuple(row[f] for f in FIELDS)
        if row['_key_valid'] and signature in seen:
            keeper = seen[signature]
            duplicate_log.append({'removed_record_id': row['record_id'],
                                  'retained_record_id': keeper['record_id'],
                                  'reason': 'exact normalized business record'})
        else:
            retained.append(row)
            if row['_key_valid']:
                seen[signature] = row
    groups = defaultdict(list)
    for row in retained:
        if row['_key_valid']:
            groups[tuple(row[k] for k in KEY)].append(row)
    for group in groups.values():
        if len(group) > 1:
            differing = [f for f in FIELDS if len({r[f] for r in group}) > 1]
            for row in group:
                issue = 'conflicting entry line: ' + ', '.join(differing)
                row['_issues'].append(issue)
                issues.append({**{k: row[k] for k in ['record_id', 'broker', 'source_file', 'source_row']},
                               'field': '|'.join(differing), 'issue': issue, 'original': ''})
                row['duplicate_flag'] = 'conflict'
    for row in retained:
        row.setdefault('duplicate_flag', 'none')
        row['validation_status'] = 'needs_review' if row['_issues'] else 'passed'
        row['validation_issues'] = '; '.join(row['_issues'])
        row['part_number_missing'] = 'yes' if not row['part_number'] else 'no'
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = ['record_id', 'broker', 'source_file', 'source_row'] + FIELDS + [
        'part_number_missing', 'duplicate_flag', 'validation_status', 'validation_issues']
    public_rows = [{f: r[f] for f in fields} for r in retained]
    write_csv(output_dir / 'cleaned_entries.csv', fields, public_rows)
    write_csv(output_dir / 'exceptions.csv', fields, [r for r in public_rows if r['validation_status'] == 'needs_review'])
    write_csv(output_dir / 'quality_issues.csv', ['record_id', 'broker', 'source_file', 'source_row', 'field', 'issue', 'original'], issues)
    write_csv(output_dir / 'change_log.csv', ['record_id', 'broker', 'source_file', 'source_row', 'field', 'original', 'cleaned'], changes)
    write_csv(output_dir / 'removed_duplicates.csv', ['removed_record_id', 'retained_record_id', 'reason'], duplicate_log)
    summary = {
        'input_rows': len(records), 'output_rows': len(retained),
        'exact_duplicates_removed': len(duplicate_log),
        'conflicting_rows_retained': sum(r['duplicate_flag'] == 'conflict' for r in retained),
        'rows_needing_review': sum(r['validation_status'] == 'needs_review' for r in retained),
        'allowed_blank_part_numbers': sum(not r['part_number'] for r in retained),
        'changed_cells': len(changes),
        'nulls_before': {f: before[f] for f in FIELDS},
        'nulls_after': {f: sum(not r[f] for r in retained) for f in FIELDS}}
    (output_dir / 'quality_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    lines = ['# Data quality report', '', 'Synthetic demonstration data only.', '',
             '| Metric | Count |', '|---|---:|']
    lines += [f'| {k.replace("_", " ").capitalize()} | {v} |' for k, v in summary.items() if isinstance(v, int)]
    lines += ['', '## Completeness', '',
              'Before counts use all input rows; after counts use retained rows. Nulls are not imputed. Counts may fall when duplicate rows are removed.', '',
              '| Field | Nulls before | Nulls after |', '|---|---:|---:|']
    lines += [f'| {f} | {before[f]} | {summary["nulls_after"][f]} |' for f in FIELDS]
    lines += ['', '## Interpretation', '',
              'Blank part numbers are allowed and do not by themselves create an exception. '
              'Conflicting versions are retained; no broker is assumed authoritative. '
              'Passed means the configured structural rules passed, not that customs accuracy was verified. '
              'Invalid nonblank values remain visible in the cleaned output with review flags. '
              'Quality issues and change logs include input rows subsequently removed as duplicates.', '']
    (output_dir / 'data_quality_report.md').write_text('\n'.join(lines))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/raw')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--mapping', type=Path, default=ROOT / 'config/broker_mappings.json')
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output, args.mapping), indent=2))
