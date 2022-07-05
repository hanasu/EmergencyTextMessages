from sender import init_parser, is_error, test_error_range
from unittest import TestCase
from io import StringIO
from unittest.mock import patch
from decimal import Decimal
from argparse import ArgumentError


class ParserTest(TestCase):
    def setUp(self):
        self.parser = init_parser()

    def test_mean_wait_good_values(self):
        parsed = self.parser.parse_args(['-w', '9', '-e', '.05'])
        self.assertEqual(parsed.mean_wait, 9)
        self.assertEqual(parsed.error, Decimal('0.05'))

    @patch('sys.stderr', new_callable=StringIO)
    def test_mean_wait_out_of_range(self, mock_stderr):
        with self.assertRaises(SystemExit):
            parsed = self.parser.parse_args(['-w', '190', '-e', '.05'])
        self.assertRaises(ArgumentError)
        self.assertRegexpMatches(mock_stderr.getvalue(),
                                 r"invalid choice")

    @patch('sys.stderr', new_callable=StringIO)
    def test_mean_wait_missing_param(self, mock_stderr):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['-w'])
        self.assertRegexpMatches(mock_stderr.getvalue(),
                                 r"expected one argument")

    @patch('sys.stderr', new_callable=StringIO)
    def test_error_missing_param(self, mock_stderr):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['-e'])
        self.assertRegexpMatches(mock_stderr.getvalue(),
                                 r"expected one argument")

    @patch('sys.stderr', new_callable=StringIO)
    def test_error_out_of_range(self, mock_stderr):
        with self.assertRaises(SystemExit):
            args = self.parser.parse_args(['-w', '9', '-e', '7.0'])
            test_error_range(args, self.parser)                    


class ErrorRateTest(TestCase):
    @patch('random.random')
    def test_error_rate_zero(self, random_mock):
        random_mock.return_value = 0
        self.assertFalse(is_error(0))

    @patch('random.random')
    def test_error_rate_less_than_false(self, random_mock):
            random_mock.return_value = 0.1
            self.assertFalse(is_error(0))

    @patch('random.random')
    def test_error_rate_greater_than_true(self, random_mock):
            random_mock.return_value = 0
            self.assertTrue(is_error(0.9))
