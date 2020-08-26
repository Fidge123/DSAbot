from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot import dice_roll
from test.mocks import MockAuthor, MockMessage


def create_response(content):
    return dice_roll.create_response(MockMessage(MockAuthor("TestUser"), content))[0]


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
        self.assertIsNone(dice_roll.parse("!  4W20"))
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

    def test_parse_with_comment(self):
        self.assertIsNotNone(dice_roll.parse("2d6+3 test"))
        self.assertIsNotNone(dice_roll.parse("3d20-4 this is a comment"))
        self.assertIsNotNone(dice_roll.parse("3w20+1-4 lolololol"))
        self.assertIsNotNone(dice_roll.parse("3w20 + 1 - 4 can I put anything here? 🤔"))

    def test_parse_with_other_commands(self):
        self.assertIsNone(dice_roll.parse("!13,13,13@8"))
        self.assertIsNone(dice_roll.parse("13"))
        self.assertIsNone(dice_roll.parse("!13 d"))
        self.assertIsNone(dice_roll.parse("note:foobar"))
        self.assertIsNone(dice_roll.parse("SUMMON"))
        self.assertIsNone(dice_roll.parse("BEGONE"))
        self.assertIsNone(dice_roll.parse("DIE"))

    def test_parse_results(self):
        parsed = dice_roll.parse("3d20-2 Sinnesschärfe")
        self.assertEqual(parsed.group("amount"), "3")
        self.assertEqual(parsed.group("sides"), "20")
        self.assertEqual(parsed.group("mod"), "-2")
        self.assertEqual(parsed.group("comment"), "Sinnesschärfe")

        parsed = dice_roll.parse("! 1337w100 + 1 - 4")
        self.assertEqual(parsed.group("amount"), "1337")
        self.assertEqual(parsed.group("sides"), "100")
        self.assertEqual(parsed.group("mod"), "+ 1 - 4")
        self.assertEqual(parsed.group("comment"), "")

        parsed = dice_roll.parse("!13w3d20")
        self.assertEqual(parsed.group("amount"), "13")
        self.assertEqual(parsed.group("sides"), "3")
        self.assertEqual(parsed.group("mod"), "")
        self.assertEqual(parsed.group("comment"), "d20")

    @patch("random.randint", new_callable=MagicMock())
    def test_response(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        self.assertEqual(create_response("3d6"), "@TestUser \n1 + 1 + 1 = 3")

    @patch("random.randint", new_callable=MagicMock())
    def test_response_with_modifier(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        self.assertEqual(create_response("3d6 + 3"), "@TestUser \n1 + 1 + 1 (+3) = 6")
        self.assertEqual(create_response("d6 - 4"), "@TestUser \n1 (-4) = -3")
        self.assertEqual(create_response("d6 - 4 + 6 - 5"), "@TestUser \n1 (-3) = -2")
        self.assertEqual(
            create_response("5d6 + 3-2"), "@TestUser \n1 + 1 + 1 + 1 + 1 (+1) = 6"
        )
