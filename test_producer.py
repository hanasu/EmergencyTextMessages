from producer import init_parser, generate_message
from unittest import TestCase
from io import StringIO
from unittest.mock import patch
from argparse import ArgumentError

class ParserTest(TestCase):
    def setUp(self):
        self.parser = init_parser()

    def test_messages_valid_value(self):
        parsed = self.parser.parse_args(['-m', '20000'])
        self.assertEqual(parsed.messages, 20000)
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_messages_invalid_value(self, mock_stderr):
        with self.assertRaises(SystemExit):
            parsed = self.parser.parse_args(['-m', 'q'])
        self.assertRaises(ArgumentError)
        self.assertRegexpMatches(mock_stderr.getvalue(), r"invalid int value")

    @patch('sys.stderr', new_callable=StringIO)
    def test_messages_missing_param(self, mock_stderr):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['-m'])
        self.assertRegexpMatches(mock_stderr.getvalue(), r"expected one argument")

class GeneratePhoneTest(TestCase):
    def test_phone_not_passed(self):
        with self.assertRaises(TypeError):
            generate_message()

class DefaultValuesTest(TestCase):
    def setUp(self):
        self.parser = init_parser()

    def test_args_missing_value(self):
        args = self.parser.parse_args()
        self.assertEqual(args.messages, 1000)
    
    def test_hostname_missing_value(self):
        args = self.parser.parse_args()
        self.assertEqual(args.hostname, "localhost")

    def test_port_missing_value(self):
        args = self.parser.parse_args()
        self.assertEqual(args.port, 5672)

    def test_queue_name_missing_value(self):
        args = self.parser.parse_args()
        self.assertEqual(args.queue_name, "emergency")