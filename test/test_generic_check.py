from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.checks import GenericCheck


class MockAuthor:
    def __init__(self, name):
        self.mention = "@{}".format(name)


class TestGenericCheck(TestCase):
    def test_parse(self):
        gc = GenericCheck("13", MockAuthor("TestUser"))
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["attributes"], [13])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("1,12,18", MockAuthor("TestUser"))
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["attributes"], [1, 12, 18])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("8 19 1400", MockAuthor("TestUser"))
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["attributes"], [8, 19, 1400])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("2 2, 2, 2,2,2", MockAuthor("TestUser"))
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["attributes"], [2, 2, 2, 2, 2, 2])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

    def test_parse_with_prefix(self):
        gc = GenericCheck("!13 1", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [13, 1])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("! 1,12,18", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [1, 12, 18])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

        with self.assertRaises(ValueError):
            GenericCheck("!!13 1", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            GenericCheck("!  1 13", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            GenericCheck("!?4", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            GenericCheck("#2,2,2", MockAuthor("TestUser"))

    def test_parse_with_large_numbers(self):
        gc = GenericCheck("1337", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [1337])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("100000 100000 1000000", MockAuthor("TU"))
        self.assertEqual(gc.data["attributes"], [100000, 100000, 1000000])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("999999988888888", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [999999988888888])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")

    def test_parse_with_modifiers(self):
        gc = GenericCheck("8,9,10-4", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [8, 9, 10])
        self.assertEqual(gc.data["modifier"], -4)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("!1 + 1 - 4", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [1])
        self.assertEqual(gc.data["modifier"], -3)
        self.assertEqual(gc.data["comment"], "")

        gc = GenericCheck("!1+1- 4 +3 -   9 ", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [1])
        self.assertEqual(gc.data["modifier"], -9)
        self.assertEqual(gc.data["comment"], "")

    def test_parse_with_comment(self):
        gc = GenericCheck("12 test", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [12])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "test")

        gc = GenericCheck("!12,12+3 this is a comment", MockAuthor(""))
        self.assertEqual(gc.data["attributes"], [12, 12])
        self.assertEqual(gc.data["modifier"], +3)
        self.assertEqual(gc.data["comment"], "this is a comment")

        gc = GenericCheck("!12,12-6 lolololol", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [12, 12])
        self.assertEqual(gc.data["modifier"], -6)
        self.assertEqual(gc.data["comment"], "lolololol")

        gc = GenericCheck("20 + 1 - 4 can I put anything here? 🤔", MockAuthor(""))
        self.assertEqual(gc.data["attributes"], [20])
        self.assertEqual(gc.data["modifier"], -3)
        self.assertEqual(gc.data["comment"], "can I put anything here? 🤔")

    def test_parse_with_other_commands(self):
        with self.assertRaises(ValueError):
            GenericCheck("d3", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            GenericCheck("note:foobar", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            GenericCheck("SUMMON", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            GenericCheck("BEGONE", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            GenericCheck("DIE", MockAuthor("TestUser"))

        # Careful, these are not None. Execution order matters!
        # with self.assertRaises(ValueError):
        #     GenericCheck("!13,13,13@13+3 Foobar", MockAuthor("TestUser"))
        # with self.assertRaises(ValueError):
        #     GenericCheck("!3w6", MockAuthor("TestUser"))
        # with self.assertRaises(ValueError):
        #     GenericCheck("12d12+2", MockAuthor("TestUser"))

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end(self, mock_randint: MagicMock):
        mock_randint.return_value = 8
        gc = GenericCheck("1", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [1])
        self.assertEqual(gc.data["EAV"], [1])
        self.assertEqual(gc.data["modifier"], 0)
        self.assertEqual(gc.data["comment"], "")
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["rolls"].rolls, [8])
        self.assertEqual(gc.data["rolls"].critical_success, False)
        self.assertEqual(gc.data["rolls"].botch, False)
        self.assertEqual(gc.impossible, False)
        self.assertEqual(
            str(gc),
            "@TestUser \n"
            "```py\n"
            "EEW:      1\n"
            "Würfel:   8\n"
            "Nicht bestanden\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_modifier(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        gc = GenericCheck("11,13,13-2 Sinnesschärfe", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [11, 13, 13])
        self.assertEqual(gc.data["EAV"], [9, 11, 11])
        self.assertEqual(gc.data["modifier"], -2)
        self.assertEqual(gc.data["comment"], "Sinnesschärfe")
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(gc.data["rolls"].critical_success, False)
        self.assertEqual(gc.data["rolls"].botch, False)
        self.assertEqual(gc.impossible, False)
        self.assertEqual(
            str(gc),
            "@TestUser Sinnesschärfe\n"
            "```py\n"
            "EEW:      9  11  11\n"
            "Würfel:   9   9   9\n"
            "Bestanden\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_impossible(self, mock_randint: MagicMock):
        mock_randint.return_value = 8
        gc = GenericCheck("!111 1337 42 1 1 +1 - 2 -4 🎉", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [111, 1337, 42, 1, 1])
        self.assertEqual(gc.data["EAV"], [106, 1332, 37, -4, -4])
        self.assertEqual(gc.data["modifier"], -5)
        self.assertEqual(gc.data["comment"], "🎉")
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["rolls"].rolls, [8, 8, 8, 8, 8])
        self.assertEqual(gc.data["rolls"].critical_success, False)
        self.assertEqual(gc.data["rolls"].botch, False)
        self.assertEqual(gc.impossible, True)
        self.assertEqual(
            str(gc),
            "@TestUser 🎉\n"
            "```py\n"
            "EEW: 1061332  37  -4  -4\n"
            "Probe nicht möglich\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_crit(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        gc = GenericCheck("!12 15 16 -4 🎉", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [12, 15, 16])
        self.assertEqual(gc.data["EAV"], [8, 11, 12])
        self.assertEqual(gc.data["modifier"], -4)
        self.assertEqual(gc.data["comment"], "🎉")
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["rolls"].rolls, [1, 1, 1])
        self.assertEqual(gc.data["rolls"].critical_success, True)
        self.assertEqual(gc.data["rolls"].botch, False)
        self.assertEqual(gc.impossible, False)
        self.assertEqual(
            str(gc),
            "@TestUser 🎉\n"
            "```py\n"
            "EEW:      8  11  12\n"
            "Würfel:   1   1   1\n"
            "Kritischer Erfolg!\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_botch(self, mock_randint: MagicMock):
        mock_randint.return_value = 20
        gc = GenericCheck("!18 18 19 +3 💥", MockAuthor("TestUser"))
        self.assertEqual(gc.data["attributes"], [18, 18, 19])
        self.assertEqual(gc.data["EAV"], [21, 21, 22])
        self.assertEqual(gc.data["modifier"], +3)
        self.assertEqual(gc.data["comment"], "💥")
        self.assertEqual(gc.data["author"], "@TestUser")
        self.assertEqual(gc.data["rolls"].rolls, [20, 20, 20])
        self.assertEqual(gc.data["rolls"].critical_success, False)
        self.assertEqual(gc.data["rolls"].botch, True)
        self.assertEqual(gc.impossible, False)
        self.assertEqual(
            str(gc),
            "@TestUser 💥\n"
            "```py\n"
            "EEW:     21  21  22\n"
            "Würfel:  20  20  20\n"
            "Patzer!\n"
            "```",
        )
