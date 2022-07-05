from monitor import init_parser
from unittest import TestCase

class ParserTest(TestCase):
    def setUp(self):
        self.parser = init_parser()

    def test_frequency_valid_value(self):
        parsed = self.parser.parse_args(['-f', '6', '-n', 'test', '-w', 
                                         'test2'])
        self.assertEqual(parsed.frequency, 6)
    
    def test_username_valid_value(self):
        parsed = self.parser.parse_args(['-f', '6', '-n', 'test', '-w', 
                                         'test2'])
        self.assertEqual(parsed.username, 'test')

    def test_password_valid_value(self):
        parsed = self.parser.parse_args(['-f', '6', '-n', 'test', '-w', 
                                         'test2'])
        self.assertEqual(parsed.password, 'test2')

    def test_hostname_valid_value(self):
        parsed = self.parser.parse_args(['-f', '6', '-n', 'test', '-w', 
                                         'test2', '-u', 'test.xyz'])
        self.assertEqual(parsed.hostname, 'test.xyz')

    def test_password_server_port_value(self):
        parsed = self.parser.parse_args(['-f', '6', '-n', 'test', '-w', 
                                         'test2', '-p', '1234'])
        self.assertEqual(parsed.server_port, 1234)

    def test_password_api_port_value(self):
        parsed = self.parser.parse_args(['-f', '6', '-n', 'test', '-w', 
                                         'test2', '-a', '2345'])
        self.assertEqual(parsed.api_port, 2345)