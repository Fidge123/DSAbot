from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot import skill_check


class MockAuthor:
    def __init__(self, name):
        self.mention = "@{}".format(name)


def create_response(input):
    return skill_check.create_response(skill_check.parse(input), MockAuthor("TestUser"))


class TestSkillCheck(TestCase):
    def test_parse(self):
        self.assertIsNotNone(skill_check.parse("13"))
        self.assertIsNotNone(skill_check.parse("1,12,18"))
        self.assertIsNotNone(skill_check.parse("8 19 1400"))
        self.assertIsNotNone(skill_check.parse("2 2, 2, 2,2,2"))

    def test_parse_with_fw(self):
        self.assertIsNotNone(skill_check.parse("13@2"))
        self.assertIsNotNone(skill_check.parse("1,12,18@18"))
        self.assertIsNotNone(skill_check.parse("8 19 1400@0"))
        self.assertIsNotNone(skill_check.parse("2 2, 2, 2,2,2@1400"))

    def test_parse_with_prefix(self):
        self.assertIsNotNone(skill_check.parse("!13 1@2"))
        self.assertIsNotNone(skill_check.parse("! 1,12,18@18"))

        self.assertIsNone(skill_check.parse("!!13 1@2"))
        self.assertIsNone(skill_check.parse("!  1 13@0"))
        self.assertIsNone(skill_check.parse("!?4"))
        self.assertIsNone(skill_check.parse("#2,2,2@2"))

    def test_parse_with_large_numbers(self):
        self.assertIsNotNone(skill_check.parse("1337@1337"))
        self.assertIsNotNone(skill_check.parse("100000 100000 1000000 @ 1000000"))
        self.assertIsNotNone(skill_check.parse("9999999@88888888"))

    def test_parse_with_modifiers(self):
        self.assertIsNotNone(skill_check.parse("12 12 12@8+3"))
        self.assertIsNotNone(skill_check.parse("8,9,10-4"))
        self.assertIsNotNone(skill_check.parse("!4 5 16 18@17-4"))
        self.assertIsNotNone(skill_check.parse("!1 + 1 - 4"))

    def test_parse_with_comment(self):
        self.assertIsNotNone(skill_check.parse("12 test"))
        self.assertIsNotNone(skill_check.parse("!12,12@8+3 this is a comment"))
        self.assertIsNotNone(skill_check.parse("!12,12@8-6 lolololol"))
        self.assertIsNotNone(skill_check.parse("20 + 1 - 4 can I put anything here? 🤔"))

    def test_parse_with_other_commands(self):
        self.assertIsNone(skill_check.parse("d3"))
        self.assertIsNone(skill_check.parse("note:foobar"))
        self.assertIsNone(skill_check.parse("SUMMON"))
        self.assertIsNone(skill_check.parse("BEGONE"))
        self.assertIsNone(skill_check.parse("DIE"))

        # Careful, these are not None. Execution order matters!
        # self.assertIsNone(skill_check.parse("!3w6"))
        # self.assertIsNone(skill_check.parse("12d12+2"))

    def test_parse_results(self):
        parsed = skill_check.parse("11,13,13@7-2 Sinnesschärfe")
        self.assertEqual(parsed.group("attr"), "11,13,13")
        self.assertEqual(parsed.group("FW"), "7")
        self.assertEqual(parsed.group("add"), None)
        self.assertEqual(parsed.group("sub"), "2")
        self.assertEqual(parsed.group("comment"), "Sinnesschärfe")

        parsed = skill_check.parse("1")
        self.assertEqual(parsed.group("attr"), "1")
        self.assertEqual(parsed.group("FW"), None)
        self.assertEqual(parsed.group("add"), None)
        self.assertEqual(parsed.group("sub"), None)
        self.assertEqual(parsed.group("comment"), "")

        parsed = skill_check.parse("!111 1337 42 1 1 @ 27 +1 - 2 🎉")
        self.assertEqual(parsed.group("attr"), "111 1337 42 1 1 ")
        self.assertEqual(parsed.group("FW"), "27")
        self.assertEqual(parsed.group("add"), "1")
        self.assertEqual(parsed.group("sub"), "2")
        self.assertEqual(parsed.group("comment"), "🎉")

    @patch("random.randint", new_callable=MagicMock())
    def test_response(self, mock_randint: MagicMock):
        mock_randint.return_value = 8
        self.assertEqual(create_response("4"), "@TestUser \n8 ===> -4")
        self.assertEqual(create_response("12, 13, 6"), "@TestUser \n8, 8, 8 ===> -2")

    @patch("random.randint", new_callable=MagicMock())
    def test_response_with_fw(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        self.assertEqual(
            create_response("10,7@2"), "@TestUser \n9, 9 ===> -2\n(2 - 2 = 0 FP) QS: 1"
        )
        self.assertEqual(
            create_response("!6,9,6@3"),
            "@TestUser \n9, 9, 9 ===> -6\n(3 - 6 = -3 FP) QS: 0 FAIL",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_response_with_modifier(self, mock_randint: MagicMock):
        mock_randint.return_value = 10
        self.assertEqual(
            create_response("10,7@2+3"),
            "@TestUser \n10, 10 ===> 0\n(2 - 0 = 2 FP) QS: 1",
        )
        self.assertEqual(
            create_response("!12,10,14@7-1"),
            "@TestUser \n10, 10, 10 ===> -1\n(7 - 1 = 6 FP) QS: 2",
        )
        self.assertEqual(
            create_response("!12,12,12@12 - 1"),
            "@TestUser \n10, 10, 10 ===> 0\n(12 - 0 = 12 FP) QS: 4",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_response_with_comment(self, mock_randint: MagicMock):
        mock_randint.return_value = 10
        self.assertEqual(
            create_response("! 12,12,12 @ 12 + 2 Sinnesschärfe"),
            "@TestUser Sinnesschärfe\n10, 10, 10 ===> 0\n(12 - 0 = 12 FP) QS: 4",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_response_with_crit_and_fail(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        self.assertEqual(
            create_response("!12,12,12 @ 12 - 3"),
            "@TestUser \n1, 1, 1 ===> 0\n(12 - 0 = 12 FP) QS: 4\nKritischer Erfolg!",
        )

        mock_randint.return_value = 20
        self.assertEqual(
            create_response("!14,15,16 @ 12 + 3"),
            "@TestUser \n20, 20, 20 ===> -6\n(12 - 6 = 6 FP) QS: 2\nPatzer!",
        )
