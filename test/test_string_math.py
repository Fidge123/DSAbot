from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.string_math import calc


class TestStringMath(TestCase):
    def test_calc(self):
        self.assertEqual(calc("1"), (1, []))
        self.assertEqual(calc("1+1"), (2, []))
        self.assertEqual(calc("1-1"), (0, []))
        self.assertEqual(calc("-1"), (-1, []))
        self.assertEqual(calc("(2 + 1 * 2) / 2"), (2, []))
        self.assertEqual(calc("+ ((4 + -1 * 2) / 2) * (1+-3/4) "), (0.25, []))

    @patch("random.randint", new_callable=MagicMock())
    def test_with_dice(self, mock_randint: MagicMock):
        mock_randint.return_value = 1

        self.assertEqual(calc("1d6"), (1, [(6, [1])]))
        self.assertEqual(calc("14+1d6"), (15, [(6, [1])]))
        self.assertEqual(calc("1d6+14"), (15, [(6, [1])]))
        self.assertEqual(calc("5+1w6+2"), (8, [(6, [1])]))
        self.assertEqual(calc("3w20 + 1 - 4"), (0, [(20, [1, 1, 1])]))
        self.assertEqual(calc("1337d1337")[0], 1337)
        self.assertEqual(calc("4W20"), (4, [(20, [1, 1, 1, 1])]))
        self.assertEqual(calc("w3"), (1, [(3, [1])]))
        self.assertEqual(calc("-w6 "), (-1, [(6, [1])]))
        self.assertEqual(
            calc("1w6+2W6+3d6+4D6"),
            (
                10,
                [
                    (6, [1]),
                    (6, [1, 1]),
                    (6, [1, 1, 1]),
                    (6, [1, 1, 1, 1]),
                ],
            ),
        )

        mock_randint.return_value = 2
        self.assertEqual(
            calc("(3*2w6-4)d(1W6+2)"),
            (16, [(6, [2, 2]), (6, [2]), (4, [2, 2, 2, 2, 2, 2, 2, 2])]),
        )
