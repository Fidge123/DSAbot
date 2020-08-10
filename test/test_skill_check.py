from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot import skill_check


class MockAuthor:
    def __init__(self, name):
        self.mention = "@{}".format(name)


def create_response(input):
    return str(skill_check.create_skill_check(input, MockAuthor("TestUser")))


class TestSkillCheck(TestCase):
    def test_parse(self):
        self.assertIsNotNone(skill_check.create_skill_check("13", MockAuthor("")))
        self.assertIsNotNone(skill_check.create_skill_check("1,12,18", MockAuthor("")))
        self.assertIsNotNone(
            skill_check.create_skill_check("8 19 1400", MockAuthor(""))
        )
        self.assertIsNotNone(
            skill_check.create_skill_check("2 2, 2, 2,2,2", MockAuthor(""))
        )

    def test_parse_with_fw(self):
        self.assertIsNotNone(skill_check.create_skill_check("13@2", MockAuthor("")))
        self.assertIsNotNone(
            skill_check.create_skill_check("1,12,18@18", MockAuthor(""))
        )
        self.assertIsNotNone(
            skill_check.create_skill_check("8 19 1400@0", MockAuthor(""))
        )
        self.assertIsNotNone(
            skill_check.create_skill_check("2 2, 2, 2,2,2@1400", MockAuthor(""))
        )

    def test_parse_with_prefix(self):
        self.assertIsNotNone(skill_check.create_skill_check("!13 1@2", MockAuthor("")))
        self.assertIsNotNone(
            skill_check.create_skill_check("! 1,12,18@18", MockAuthor(""))
        )

        self.assertIsNone(skill_check.create_skill_check("!!13 1@2", MockAuthor("")))
        self.assertIsNone(skill_check.create_skill_check("!  1 13@0", MockAuthor("")))
        self.assertIsNone(skill_check.create_skill_check("!?4", MockAuthor("")))
        self.assertIsNone(skill_check.create_skill_check("#2,2,2@2", MockAuthor("")))

    def test_parse_with_large_numbers(self):
        self.assertIsNotNone(
            skill_check.create_skill_check("1337@1337", MockAuthor(""))
        )
        self.assertIsNotNone(
            skill_check.create_skill_check(
                "100000 100000 1000000 @ 1000000", MockAuthor("")
            )
        )
        self.assertIsNotNone(
            skill_check.create_skill_check("9999999@88888888", MockAuthor(""))
        )

    def test_parse_with_modifiers(self):
        self.assertIsNotNone(
            skill_check.create_skill_check("12 12 12@8+3", MockAuthor(""))
        )
        self.assertIsNotNone(skill_check.create_skill_check("8,9,10-4", MockAuthor("")))
        self.assertIsNotNone(
            skill_check.create_skill_check("!4 5 16 18@17-4", MockAuthor(""))
        )
        self.assertIsNotNone(
            skill_check.create_skill_check("!1 + 1 - 4", MockAuthor(""))
        )

    def test_parse_with_comment(self):
        self.assertIsNotNone(skill_check.create_skill_check("12 test", MockAuthor("")))
        self.assertIsNotNone(
            skill_check.create_skill_check(
                "!12,12@8+3 this is a comment", MockAuthor("")
            )
        )
        self.assertIsNotNone(
            skill_check.create_skill_check("!12,12@8-6 lolololol", MockAuthor(""))
        )
        self.assertIsNotNone(
            skill_check.create_skill_check(
                "20 + 1 - 4 can I put anything here? 🤔", MockAuthor("")
            )
        )

    def test_parse_with_other_commands(self):
        self.assertIsNone(skill_check.create_skill_check("d3", MockAuthor("")))
        self.assertIsNone(skill_check.create_skill_check("note:foobar", MockAuthor("")))
        self.assertIsNone(skill_check.create_skill_check("SUMMON", MockAuthor("")))
        self.assertIsNone(skill_check.create_skill_check("BEGONE", MockAuthor("")))
        self.assertIsNone(skill_check.create_skill_check("DIE", MockAuthor("")))

        # Careful, these are not None. Execution order matters!
        # self.assertIsNone(skill_check.parse("!3w6"))
        # self.assertIsNone(skill_check.parse("12d12+2"))

    # def test_parse_results(self):
    #     parsed = skill_check.create_skill_check("11,13,13@7-2 Sinnesschärfe", MockAuthor(""))
    #     self.assertEqual(parsed.group("attr"), "11,13,13")
    #     self.assertEqual(parsed.group("FW"), "7")
    #     self.assertEqual(parsed.group("mod"), "-2")
    #     self.assertEqual(parsed.group("comment"), "Sinnesschärfe")

    #     parsed = skill_check.create_skill_check("1," "")
    #     self.assertEqual(parsed.group("attr"), "1")
    #     self.assertEqual(parsed.group("FW"), None)
    #     self.assertEqual(parsed.group("mod"), MockAuthor(""))
    #     self.assertEqual(parsed.group("comment"), MockAuthor(""))

    #     parsed = skill_check.create_skill_check("!111 1337 42 1 1 @ 27 +1 - 2 🎉," "")
    #     self.assertEqual(parsed.group("attr"), "111 1337 42 1 1 ")
    #     self.assertEqual(parsed.group("FW"), "27")
    #     self.assertEqual(parsed.group("mod"), "+1 - 2")
    #     self.assertEqual(parsed.group("comment"), "🎉")

    @patch("random.randint", new_callable=MagicMock())
    def test_response(self, mock_randint: MagicMock):
        mock_randint.return_value = 8
        self.assertEqual(create_response("4"), "@TestUser \n8 ===> -4")
        self.assertEqual(create_response("12, 13, 6"), "@TestUser \n8, 8, 8 ===> -2")

    @patch("random.randint", new_callable=MagicMock())
    def test_response_with_fw(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        self.assertEqual(
            create_response("10,7@2"), "@TestUser \n9, 9 ===> 2\n(2 - 2 = 0 FP) QS: 1"
        )
        self.assertEqual(
            create_response("!6,9,6@3"),
            "@TestUser \n9, 9, 9 ===> 6\n(3 - 6 = -3 FP) Nicht bestanden",
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
            "@TestUser \n10, 10, 10 ===> 1\n(7 - 1 = 6 FP) QS: 2",
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
            "@TestUser \n1, 1, 1 ===> 0\n(12 - 0 = 12 FP) QS: 4\n**Kritischer Erfolg!**",
        )

        # mock_randint.side_effect = [1, 9]
        # self.assertEqual(
        #     create_response("12 - 3"),
        #     "@TestUser \n1 ===> 0\nBestätigungswurf: 9\n**Kritischer Erfolg!**",
        # )

        # mock_randint.side_effect = [1, 11]
        # self.assertEqual(
        #     create_response("12 - 3"),
        #     "@TestUser \n1 ===> 0\nBestätigungswurf: 11\n**Erfolg!**",
        # )

        mock_randint.return_value = 20
        self.assertEqual(
            create_response("!14,15,16 @ 12 + 3"),
            "@TestUser \n20, 20, 20 ===> 6\n(12 - 6 = 6 FP) Automatisch nicht bestanden\n**Patzer!**",
        )

        # mock_randint.side_effect = [20, 18]
        # self.assertEqual(
        #     create_response("!14 + 3"),
        #     "@TestUser \n20 ===> -3\nBestätigungswurf: 18\n**Patzer!**",
        # )

        # mock_randint.side_effect = [20, 15]
        # self.assertEqual(
        #     create_response("!14 + 3"),
        #     "@TestUser \n20 ===> -3\nBestätigungswurf: 15\nNicht bestanden",
        # )
