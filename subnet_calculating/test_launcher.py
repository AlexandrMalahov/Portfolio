"""Python 3.7. Test module launcher.py."""
import unittest
import launcher


class TestLauncher(unittest.TestCase):
    def test_check_version(self):
        """Test check_version(version)."""
        self.assertEqual(launcher.check_version('4'), 4)
        self.assertNotEqual(launcher.check_ip('10'), 10)

    def test_check_file(self):
        """Test check_file(file)."""
        self.assertEqual(launcher.check_file('files_for_tests/1.txt'), 'files_for_tests/1.txt')
        self.assertRaises(FileNotFoundError, launcher.check_file, '2.txt')

    def test_check_ip(self):
        """Test check_ip(ip)."""
        self.assertEqual(launcher.check_ip('127.0.1.7'), True)
        self.assertEqual(launcher.check_ip('217:1.0.8'), False)

    def test_parse_file_data(self):
        """Test parse_file_data(query_params)."""
        self.assertEqual(launcher.parse_file_data(
            {'file': 'files_for_tests/1.txt', 'version': 4}), {'first_ip': '10.168.0.1', 'last_ip': '10.168.0.3'})
        self.assertNotEqual(launcher.parse_file_data(
            {'file': 'files_for_tests/1.txt', 'version': 4}), {'first_ip': '10.168.0.2', 'last_ip': '10.168.0.3'})
