from unittest import TestCase

from bot import string_math


class TestStringMath(TestCase):
    def test_calc(self):
        self.assertEqual(string_math.calc("1"), 1)
        self.assertEqual(string_math.calc("1+1"), 2)
        self.assertEqual(string_math.calc("1-1"), 0)
        self.assertEqual(string_math.calc("-1"), -1)
        self.assertEqual(string_math.calc("(2 + 1 * 2) / 2"), 2)
