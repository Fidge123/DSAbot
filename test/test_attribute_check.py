from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.checks import AttributeCheck
from test.mocks import MockAuthor

author = MockAuthor("TestUser")


class TestAttributeCheck(TestCase):
    def test_parse(self):
        self.assertIsNotNone(AttributeCheck(author, "13"))
        self.assertIsNotNone(AttributeCheck(author, "1"))
        self.assertIsNotNone(AttributeCheck(author, "1400+14"))
        self.assertIsNotNone(AttributeCheck(author, "2 -2-2-2"))
        self.assertIsNotNone(AttributeCheck(author, "!13  +1+1 Test"))
        self.assertIsNotNone(AttributeCheck(author, "! 1 Krit"))

        with self.assertRaises(ValueError):
            AttributeCheck(author, "!!13 ")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "!  1 ")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "!?4")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "#2")

    def test_parse_with_other_commands(self):
        with self.assertRaises(ValueError):
            AttributeCheck(author, "d3")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "note:foobar")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "SUMMON")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "BEGONE")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "DIE")
        with self.assertRaises(ValueError):
            AttributeCheck(author, "13,13,13+1")

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_crit_botch(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        ac = AttributeCheck(author, "!12 -4 🎉")
        self.assertEqual(ac.data["attributes"], [12])
        self.assertEqual(ac.data["EAV"], [8])
        self.assertEqual(ac.data["modifier"], -4)
        self.assertEqual(ac.data["comment"], "🎉")
        self.assertEqual(ac.data["rolls"].rolls, [1])
        self.assertEqual(ac.data["rolls"].confirmation_roll, 1)
        self.assertEqual(ac.data["rolls"].critical_success, True)
        self.assertEqual(ac.data["rolls"].botch, False)
        self.assertEqual(ac.impossible(), False)
        self.assertEqual(
            str(ac),
            " 🎉\n"
            "```py\n"
            "EEW:      8\n"
            "Würfel:   1 --> 1\n"
            "Kritischer Erfolg!\n"
            "```",
        )

        mock_randint.return_value = 20
        ac = AttributeCheck(author, "!18 💥")
        self.assertEqual(ac.data["attributes"], [18])
        self.assertEqual(ac.data["EAV"], [18])
        self.assertEqual(ac.data["modifier"], 0)
        self.assertEqual(ac.data["comment"], "💥")
        self.assertEqual(ac.data["rolls"].rolls, [20])
        self.assertEqual(ac.data["rolls"].confirmation_roll, 20)
        self.assertEqual(ac.data["rolls"].critical_success, False)
        self.assertEqual(ac.data["rolls"].botch, True)
        self.assertEqual(ac.impossible(), False)
        self.assertEqual(
            str(ac),
            " 💥\n" "```py\n" "EEW:     18\n" "Würfel:  20 --> 20\n" "Patzer!\n" "```",
        )

        ac = AttributeCheck(author, "!18 +3 💥")
        self.assertEqual(ac.data["attributes"], [18])
        self.assertEqual(ac.data["EAV"], [21])
        self.assertEqual(ac.data["modifier"], +3)
        self.assertEqual(ac.data["comment"], "💥")
        self.assertEqual(ac.data["rolls"].rolls, [20])
        self.assertEqual(ac.data["rolls"].confirmation_roll, 20)
        self.assertEqual(ac.data["rolls"].critical_success, False)
        self.assertEqual(ac.data["rolls"].botch, True)
        self.assertEqual(ac.impossible(), False)
        self.assertEqual(
            str(ac),
            " 💥\n"
            "```py\n"
            "EEW:     21\n"
            "Würfel:  20 --> 20\n"
            "Unbestätigter Patzer\n"
            "```",
        )
