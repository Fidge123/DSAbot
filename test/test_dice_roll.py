from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot import dice_roll
from test.mocks import MockAuthor, MockMessage


def create_response(content):
    res = dice_roll.create_response(MockMessage(MockAuthor("TestUser"), content))
    return res.messages[0]["args"][0]


class TestDiceRoll(TestCase):
    def test_parse_with_d_or_w(self):
        self.assertIsNotNone(dice_roll.parse("3d6"))
        self.assertIsNotNone(dice_roll.parse("2D12"))
        self.assertIsNotNone(dice_roll.parse("w3"))
        self.assertIsNotNone(dice_roll.parse("4W20"))

    def test_parse_with_prefix(self):
        self.assertIsNotNone(dice_roll.parse("!3d6"))
        self.assertIsNotNone(dice_roll.parse("! 2D12"))

        self.assertIsNone(dice_roll.parse("!!1w3"))
        self.assertIsNone(dice_roll.parse("!?4W20"))
        self.assertIsNone(dice_roll.parse("#4W20"))

    def test_parse_with_large_numbers(self):
        self.assertIsNotNone(dice_roll.parse("1337d1337"))
        self.assertIsNotNone(dice_roll.parse("100000D100000"))
        self.assertIsNotNone(dice_roll.parse("9999999D88888888"))

    def test_parse_with_modifiers(self):
        self.assertIsNotNone(dice_roll.parse("2d6+3"))
        self.assertIsNotNone(dice_roll.parse("3d20-4"))
        self.assertIsNotNone(dice_roll.parse("3w20+1-4"))
        self.assertIsNotNone(dice_roll.parse("3w20 + 1 - 4"))
        self.assertIsNotNone(dice_roll.parse("14+1d6"))
        self.assertIsNotNone(dice_roll.parse("5+1w6+2"))
        self.assertIsNotNone(dice_roll.parse("(2d6+4+8)*2"))
        self.assertIsNotNone(dice_roll.parse("2*(3w10+4)"))

    def test_parse_with_comment(self):
        self.assertIsNotNone(dice_roll.parse("2d6+3 test"))
        self.assertIsNotNone(dice_roll.parse("3d20-4 this is a comment"))
        self.assertIsNotNone(dice_roll.parse("3w20+1-4 lolololol"))
        self.assertIsNotNone(dice_roll.parse("3w20 + 1 - 4 can I put anything here? 🤔"))

    def test_parse_results(self):
        parsed = dice_roll.parse("3d20-2 Sinnesschärfe")
        self.assertEqual(parsed.group("calc"), "3d20-2 ")
        self.assertEqual(parsed.group("comment"), "Sinnesschärfe")

        parsed = dice_roll.parse("! 1337w100 + 1 - 4")
        self.assertEqual(parsed.group("calc"), "1337w100 + 1 - 4")
        self.assertEqual(parsed.group("comment"), "")

        parsed = dice_roll.parse("!13w3d20")
        self.assertEqual(parsed.group("calc"), "13w3d20")
        self.assertEqual(parsed.group("comment"), "")

    @patch("random.randint", new_callable=MagicMock())
    def test_response(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        self.assertEqual(
            create_response("3d6"), "@TestUser \n[1 + 1 + 1]\nErgebnis: **3**"
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_response_with_modifier(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        self.assertEqual(
            create_response("3d6 + 3"), "@TestUser \n[1 + 1 + 1]\nErgebnis: **6**"
        )
        self.assertEqual(create_response("d6 - 4"), "@TestUser \n[1]\nErgebnis: **-3**")
        self.assertEqual(
            create_response("d6 - 4 + 6 - 5"), "@TestUser \n[1]\nErgebnis: **-2**"
        )
        self.assertEqual(
            create_response("5d6 + 3-2"),
            "@TestUser \n[1 + 1 + 1 + 1 + 1]\nErgebnis: **6**",
        )
        self.assertEqual(create_response("14+1d6"), "@TestUser \n[1]\nErgebnis: **15**")
        self.assertEqual(create_response("5+w6+2"), "@TestUser \n[1]\nErgebnis: **8**")
        self.assertEqual(
            create_response("(2d6+4+8)*2"), "@TestUser \n[1 + 1]\nErgebnis: **28**"
        )
        self.assertEqual(
            create_response("2*(3w10+4)"), "@TestUser \n[1 + 1 + 1]\nErgebnis: **14**"
        )
