from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.checks import SkillCheck, GenericCheck, AttributeCheck
from bot import check, note


class MockAuthor:
    def __init__(self, name):
        self.mention = "@{}".format(name)

    def __str__(self):
        return "TestUser#123456789"


class TestSkillCheck(TestCase):
    def test_parse(self):
        user = MockAuthor("TestUser")
        self.assertIsInstance(check.create_check("13 14 15@2", user), SkillCheck)
        self.assertIsInstance(check.create_check("13", user), AttributeCheck)
        self.assertIsInstance(check.create_check("13 @2", user), AttributeCheck)
        self.assertIsInstance(check.create_check("13 14 -2", user), GenericCheck)
        self.assertIsInstance(check.create_check("13 14 @2", user), GenericCheck)

    @patch("random.randint", new_callable=MagicMock())
    def test_fate(self, mock_randint: MagicMock):
        user = MockAuthor("TestUser")
        note.create_note("schips_{}".format(str(user)), 3, user)

        mock_randint.return_value = 12
        first = check.create_response("11,9,9@4", user)
        self.assertEqual(
            first,
            "@TestUser \n"
            "```py\n"
            "EEW:     11   9   9\n"
            "Würfel:  12  12  12\n"
            "FW 4     -1  -3  -3 = -3 FP\n"
            "Nicht bestanden\n"
            "```",
        )
        check.create_response("11,9,9@6", MockAuthor("NotTestUser"))

        mock_randint.return_value = 2
        second = check.create_response("schips rrr", user)
        self.assertEqual(
            second,
            "@TestUser \n"
            "```py\n"
            "EEW:     11   9   9\n"
            "Würfel:   2   2   2\n"
            "FW 4                = 4 FP\n"
            "Bestanden mit QS 2\n"
            "```",
        )
        mock_randint.return_value = 10
        third = check.create_response("schips rkk", user)
        self.assertEqual(
            third,
            "@TestUser \n"
            "```py\n"
            "EEW:     11   9   9\n"
            "Würfel:  10   2   2\n"
            "FW 4                = 4 FP\n"
            "Bestanden mit QS 2\n"
            "```",
        )
        mock_randint.return_value = 10
        fourth = check.create_response("schips rkk", user)
        self.assertEqual(
            fourth,
            "@TestUser \n"
            "```py\n"
            "EEW:     11   9   9\n"
            "Würfel:  10   2   2\n"
            "FW 4                = 4 FP\n"
            "Bestanden mit QS 2\n"
            "```",
        )
        mock_randint.return_value = 10
        fifth = check.create_response("schips rkk", user)
        self.assertEqual(fifth, "@TestUser Keine Schips übrig!")

        note.delete_note(user, "schips_{}".format(str(user)))

    @patch("random.randint", new_callable=MagicMock())
    def test_force(self, mock_randint: MagicMock):
        user = MockAuthor("TestUser")
        mock_randint.return_value = 12
        first = check.create_response("14,14,14@12", user)
        self.assertEqual(
            first, "@TestUser \n```py\nRoutineprobe: 6 FP = QS 2\n```",
        )
        second = check.create_response("force", user)
        self.assertEqual(
            second,
            "@TestUser \n"
            "```py\n"
            "EEW:     14  14  14\n"
            "Würfel:  12  12  12\n"
            "FW 12               = 12 FP\n"
            "Bestanden mit QS 4\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_retry_repeat(self, mock_randint: MagicMock):
        user = MockAuthor("TestUser")
        mock_randint.return_value = 12
        first = check.create_response("11,9,9@4", user)
        self.assertEqual(
            first,
            "@TestUser \n"
            "```py\n"
            "EEW:     11   9   9\n"
            "Würfel:  12  12  12\n"
            "FW 4     -1  -3  -3 = -3 FP\n"
            "Nicht bestanden\n"
            "```",
        )
        mock_randint.return_value = 10
        second = check.create_response("repeat", user)
        self.assertEqual(
            second,
            "@TestUser \n"
            "```py\n"
            "EEW:     11   9   9\n"
            "Würfel:  10  10  10\n"
            "FW 4         -1  -1 = 2 FP\n"
            "Bestanden mit QS 1\n"
            "```",
        )
        mock_randint.return_value = 9
        third = check.create_response("retry", user)
        self.assertEqual(
            third,
            "@TestUser \n"
            "```py\n"
            "EEW:     10   8   8\n"
            "Würfel:   9   9   9\n"
            "FW 4         -1  -1 = 2 FP\n"
            "Bestanden mit QS 1\n"
            "```",
        )
