from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.checks import AttributeCheck


class TestAttributeCheck(TestCase):
    def test_parse(self):
        self.assertIsNotNone(AttributeCheck("13", "@TestUser"))
        self.assertIsNotNone(AttributeCheck("1", "@TestUser"))
        self.assertIsNotNone(AttributeCheck("1400+14", "@TestUser"))
        self.assertIsNotNone(AttributeCheck("2 -2-2-2", "@TU"))
        self.assertIsNotNone(AttributeCheck("!13  +1+1 Test", "@TestUser"))
        self.assertIsNotNone(AttributeCheck("! 1 Krit", "@TestUser"))

        with self.assertRaises(ValueError):
            AttributeCheck("!!13 ", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("!  1 ", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("!?4", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("#2", "@TestUser")

    def test_parse_with_other_commands(self):
        with self.assertRaises(ValueError):
            AttributeCheck("d3", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("note:foobar", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("SUMMON", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("BEGONE", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("DIE", "@TestUser")
        with self.assertRaises(ValueError):
            AttributeCheck("13,13,13+1", "@TestUser")

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_crit_botch(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        ac = AttributeCheck("!12 -4 🎉", "@TestUser")
        self.assertEqual(ac.data["attributes"], [12])
        self.assertEqual(ac.data["EAV"], [8])
        self.assertEqual(ac.data["modifier"], -4)
        self.assertEqual(ac.data["comment"], "🎉")
        self.assertEqual(ac.data["mention"], "@TestUser")
        self.assertEqual(ac.data["rolls"].rolls, [1])
        self.assertEqual(ac.data["rolls"].confirmation_roll, 1)
        self.assertEqual(ac.data["rolls"].critical_success, True)
        self.assertEqual(ac.data["rolls"].botch, False)
        self.assertEqual(ac.impossible, False)
        self.assertEqual(
            str(ac),
            "@TestUser 🎉\n"
            "```py\n"
            "EEW:      8\n"
            "Würfel:   1 --> 1\n"
            "Kritischer Erfolg!\n"
            "```",
        )

        mock_randint.return_value = 20
        ac = AttributeCheck("!18 💥", "@TestUser")
        self.assertEqual(ac.data["attributes"], [18])
        self.assertEqual(ac.data["EAV"], [18])
        self.assertEqual(ac.data["modifier"], 0)
        self.assertEqual(ac.data["comment"], "💥")
        self.assertEqual(ac.data["mention"], "@TestUser")
        self.assertEqual(ac.data["rolls"].rolls, [20])
        self.assertEqual(ac.data["rolls"].confirmation_roll, 20)
        self.assertEqual(ac.data["rolls"].critical_success, False)
        self.assertEqual(ac.data["rolls"].botch, True)
        self.assertEqual(ac.impossible, False)
        self.assertEqual(
            str(ac),
            "@TestUser 💥\n"
            "```py\n"
            "EEW:     18\n"
            "Würfel:  20 --> 20\n"
            "Patzer!\n"
            "```",
        )

        ac = AttributeCheck("!18 +3 💥", "@TestUser")
        self.assertEqual(ac.data["attributes"], [18])
        self.assertEqual(ac.data["EAV"], [21])
        self.assertEqual(ac.data["modifier"], +3)
        self.assertEqual(ac.data["comment"], "💥")
        self.assertEqual(ac.data["mention"], "@TestUser")
        self.assertEqual(ac.data["rolls"].rolls, [20])
        self.assertEqual(ac.data["rolls"].confirmation_roll, 20)
        self.assertEqual(ac.data["rolls"].critical_success, False)
        self.assertEqual(ac.data["rolls"].botch, True)
        self.assertEqual(ac.impossible, False)
        self.assertEqual(
            str(ac),
            "@TestUser 💥\n"
            "```py\n"
            "EEW:     21\n"
            "Würfel:  20 --> 20\n"
            "Unbestätigter Patzer\n"
            "```",
        )
