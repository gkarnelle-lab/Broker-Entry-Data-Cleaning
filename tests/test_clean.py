import importlib.util
import tempfile
import unittest
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('clean', ROOT / 'src/clean.py')
clean = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean)


class CleaningTests(unittest.TestCase):
    def test_optional_part_and_leading_zeros(self):
        self.assertEqual(clean.normalize('part_number', '  ', {}), ('', ''))
        self.assertEqual(clean.normalize('part_number', ' 00042-A ', {}), ('00042-A', ''))
        self.assertEqual(clean.normalize('tax_id', '00-1234567', {}), ('001234567', ''))

    def test_invalid_and_zero_values(self):
        self.assertEqual(clean.normalize('value', '$0.00', {}), ('0.00', ''))
        for value in ['1,25', 'NaN', '-4', '1.234']:
            self.assertTrue(clean.normalize('value', value, {})[1])
        self.assertTrue(clean.normalize('entry_date', '02/30/2026', {'date_formats': ['%m/%d/%Y']})[1])

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            summary = clean.run(ROOT / 'data/raw', output, ROOT / 'config/broker_mappings.json')
            self.assertEqual(summary['input_rows'], 23)
            self.assertEqual(summary['exact_duplicates_removed'], 3)
            self.assertEqual(summary['output_rows'], 20)
            self.assertEqual(summary['conflicting_rows_retained'], 4)
            self.assertEqual(summary['allowed_blank_part_numbers'], 4)
            self.assertEqual(summary['rows_needing_review'], 13)
            with (output / 'cleaned_entries.csv').open() as handle:
                rows = list(csv.DictReader(handle))
            blank_passed = [r for r in rows if not r['part_number'] and r['validation_status'] == 'passed']
            self.assertTrue(blank_passed)
            self.assertTrue(any(r['tax_id'] == '001234567' for r in rows))
            self.assertTrue(any(r['duty_amount'] == '0.00' for r in rows))
            # A second run produces the same report and files.
            original = {p.name: p.read_bytes() for p in output.iterdir()}
            clean.run(ROOT / 'data/raw', output, ROOT / 'config/broker_mappings.json')
            self.assertEqual(original, {p.name: p.read_bytes() for p in output.iterdir()})

    def test_missing_match_key_is_never_auto_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'raw'
            source.mkdir()
            with (ROOT / 'data/raw/broker_abc.csv').open() as handle:
                reader = csv.DictReader(handle)
                fields = reader.fieldnames
                row = next(reader)
            row['tax_id'] = ''
            with (source / 'broker_abc.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows([row, row])
            summary = clean.run(source, root / 'out', ROOT / 'config/broker_mappings.json')
            self.assertEqual(summary['output_rows'], 2)
            self.assertEqual(summary['exact_duplicates_removed'], 0)


if __name__ == '__main__':
    unittest.main()
