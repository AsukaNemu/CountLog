import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from countLog import count_logs


class CountLogsTests(unittest.TestCase):
    def test_empty_file_has_zero_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'empty.log'
            path.write_text('', encoding='utf-8')
            result = count_logs(path)
        self.assertEqual(result['total_lines'], 0)
        self.assertEqual(result['ip_count'], {})
        self.assertTrue(all(count == 0 for count in result['log_level'].values()))

    def test_counts_records_and_physical_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'records.log'
            path.write_text(
                '[INFO] 192.168.1.1 ready\n\n'
                '[ERROR] 192.168.1.1 failed\n'
                '[OTHER] 999.1.1.1 ignored\n', encoding='utf-8')
            result = count_logs(path)
        self.assertEqual(result['total_lines'], 4)
        self.assertEqual(result['log_level'], {
            'INFO': 1, 'WARN': 0, 'ERROR': 1, 'DEBUG': 0, 'UNKNOWN': 1})
        self.assertEqual(result['ip_count'], {'192.168.1.1': 2})

    def test_unreadable_file_returns_none(self):
        output = io.StringIO()
        with patch('builtins.open', side_effect=PermissionError('denied')):
            with contextlib.redirect_stdout(output):
                self.assertIsNone(count_logs('unreadable.log'))
        self.assertIn('行号：0', output.getvalue())

    def test_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertIsNone(count_logs(Path(directory) / 'missing.log'))


if __name__ == '__main__':
    unittest.main()
