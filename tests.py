import unittest
from pytextnow.TNAPI import Client

class TestReplaceNewLines(unittest.TestCase):
    tests = [
        {
            'in': "Hello, world!",
            'out': "Hello, world!",
        },
        {
            'in': "Hello,\nworld!",
            'out': "Hello,\\nworld!",
        },
        {
            'in': "Hello,\\nworld!",
            'out': "Hello,\\nworld!",
        },
        {
            'in': "Hello,\nworld!\nHow are you?",
            'out': "Hello,\\nworld!\\nHow are you?",
        },
        {
            'in': "Hello,\nworld!\\nHow are you?",
            'out': "Hello,\\nworld!\\nHow are you?",
        },
    ]

    def test_replace_newlines(self):
        client = Client(username='test', sid_cookie='test', csrf_cookie='test')

        for test in self.tests:
            i = test['in']
            o = test['out']
            self.assertEqual(client._replace_newlines(i), o)

if __name__ == '__main__':
    unittest.main()
