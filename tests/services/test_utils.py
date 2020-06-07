import unittest

from pycareer.services.utils import convert_to_list


class TestConvertToList(unittest.TestCase):
    def test_str_param(self):
        title = 'Title'
        res = convert_to_list(title)
        self.assertListEqual(res, [title])

    def test_list_param(self):
        expected = [1, 'title']
        res = convert_to_list(expected)
        self.assertListEqual(res, expected)

    def test_long_param(self):
        expected = long(12132121)
        res = convert_to_list(expected)
        print res
        self.assertListEqual(res, [expected])

    def test_int_param(self):
        expected = 1237
        res = convert_to_list(expected)
        self.assertListEqual(res, [expected])
