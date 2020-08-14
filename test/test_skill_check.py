from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.checks import SkillCheck


class MockAuthor:
    def __init__(self, name):
        self.mention = "@{}".format(name)


class TestSkillCheck(TestCase):
    def test_parse(self):
        self.assertIsNotNone(SkillCheck("13 14 15@2", MockAuthor("TestUser")))
        self.assertIsNotNone(SkillCheck("1,12,18@18", MockAuthor("TestUser")))
        self.assertIsNotNone(SkillCheck("8 19 1400@0 + 14", MockAuthor("TestUser")))
        self.assertIsNotNone(SkillCheck("2 2,2, @1400-2-2-2", MockAuthor("TU")))
        self.assertIsNotNone(SkillCheck("!13 1 12@2 +1+1 Test", MockAuthor("TestUser")))
        self.assertIsNotNone(SkillCheck("! 1,12,18@18 Krit", MockAuthor("TestUser")))

        with self.assertRaises(ValueError):
            SkillCheck("!!13 1@2", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("!  1 13@0", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("!?4", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("#2,2,2@2", MockAuthor("TestUser"))

    def test_parse_with_other_commands(self):
        with self.assertRaises(ValueError):
            SkillCheck("d3", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("note:foobar", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("SUMMON", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("BEGONE", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("DIE", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("13,13,13+1", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            SkillCheck("13", MockAuthor("TestUser"))

    @patch("random.randint", new_callable=MagicMock())
    def test_quality_level(self, mock_randint: MagicMock):
        mock_randint.return_value = 2
        sc = SkillCheck("11,9,9@0", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 0)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck("11,9,9@1", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 1)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck("11,9,9@2", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 2)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck("11,9,9@3", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 3)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck("11,9,9@4", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(sc.ql(sc.skill_points), 2)

        sc = SkillCheck("11,9,9@5", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 5)
        self.assertEqual(sc.ql(sc.skill_points), 2)

        sc = SkillCheck("11,9,9@6", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 6)
        self.assertEqual(sc.ql(sc.skill_points), 2)

        sc = SkillCheck("11,9,9@7", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 7)
        self.assertEqual(sc.ql(sc.skill_points), 3)

        sc = SkillCheck("11,9,9@8", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 8)
        self.assertEqual(sc.ql(sc.skill_points), 3)

        sc = SkillCheck("11,9,9@9", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 9)
        self.assertEqual(sc.ql(sc.skill_points), 3)

        sc = SkillCheck("11,9,9@10", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 10)
        self.assertEqual(sc.ql(sc.skill_points), 4)

        sc = SkillCheck("11,9,9@16", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 16)
        self.assertEqual(sc.ql(sc.skill_points), 6)

        sc = SkillCheck("11,9,9@26", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 26)
        self.assertEqual(sc.ql(sc.skill_points), 6)

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        sc = SkillCheck("11,9,9@4", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [11, 9, 9])
        self.assertEqual(sc.data["EAV"], [11, 9, 9])
        self.assertEqual(sc.data["SR"], 4)
        self.assertEqual(sc.data["modifier"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible, False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(
            str(sc),
            "@TestUser \n"
            "```py\n"
            "EEW:     11   9   9\n"
            "Würfel:   9   9   9\n"
            "FW 4                = 4 FP\n"
            "Bestanden mit QS 2\n"
            "```",
        )

        sc = SkillCheck("!13 14 15@6-2 Sinnesschärfe", MockAuthor("TU"))
        self.assertEqual(sc.data["attributes"], [13, 14, 15])
        self.assertEqual(sc.data["EAV"], [11, 12, 13])
        self.assertEqual(sc.data["SR"], 6)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["comment"], "Sinnesschärfe")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible, False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 6)
        self.assertEqual(
            str(sc),
            "@TU Sinnesschärfe\n"
            "```py\n"
            "EEW:     11  12  13\n"
            "Würfel:   9   9   9\n"
            "FW 6                = 6 FP\n"
            "Bestanden mit QS 2\n"
            "```",
        )

        sc = SkillCheck("!5 3, 4,@16 +1+1 -2- 2 🎉-1", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [5, 3, 4])
        self.assertEqual(sc.data["EAV"], [3, 1, 2])
        self.assertEqual(sc.data["SR"], 16)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["comment"], "🎉-1")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible, False)
        self.assertEqual(sc.diffs, [-6, -8, -7])
        self.assertEqual(sc.skill_points, -5)
        self.assertEqual(
            str(sc),
            "@TestUser 🎉-1\n"
            "```py\n"
            "EEW:      3   1   2\n"
            "Würfel:   9   9   9\n"
            "FW 16    -6  -8  -7 = -5 FP\n"
            "Nicht bestanden\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_crit_botch(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        sc = SkillCheck("2,3,4@4", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [2, 3, 4])
        self.assertEqual(sc.data["EAV"], [2, 3, 4])
        self.assertEqual(sc.data["SR"], 4)
        self.assertEqual(sc.data["modifier"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [1, 1, 1])
        self.assertEqual(sc.data["rolls"].critical_success, True)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible, False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(
            str(sc),
            "@TestUser \n"
            "```py\n"
            "EEW:      2   3   4\n"
            "Würfel:   1   1   1\n"
            "FW 4                = 4 FP\n"
            "Kritischer Erfolg! (QS 2)\n"
            "```",
        )

        mock_randint.return_value = 20
        sc = SkillCheck("14 18 18@3 + 2", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [14, 18, 18])
        self.assertEqual(sc.data["EAV"], [16, 20, 20])
        self.assertEqual(sc.data["SR"], 3)
        self.assertEqual(sc.data["modifier"], 2)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [20, 20, 20])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, True)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible, False)
        self.assertEqual(sc.diffs, [-4, 0, 0])
        self.assertEqual(sc.skill_points, -1)
        self.assertEqual(
            str(sc),
            "@TestUser \n"
            "```py\n"
            "EEW:     16  20  20\n"
            "Würfel:  20  20  20\n"
            "FW 3     -4         = -1 FP\n"
            "Patzer!\n"
            "```",
        )

        mock_randint.return_value = 20
        sc = SkillCheck("18,18 18@3 + 2", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [18, 18, 18])
        self.assertEqual(sc.data["EAV"], [20, 20, 20])
        self.assertEqual(sc.data["SR"], 3)
        self.assertEqual(sc.data["modifier"], 2)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [20, 20, 20])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, True)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible, False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 3)
        self.assertEqual(
            str(sc),
            "@TestUser \n"
            "```py\n"
            "EEW:     20  20  20\n"
            "Würfel:  20  20  20\n"
            "FW 3                = 3 FP\n"
            "Patzer! - Automatisch nicht bestanden\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_routine_impossible(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        sc = SkillCheck("14, 14, 14 @ 7 + 1", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [14, 14, 14])
        self.assertEqual(sc.data["EAV"], [15, 15, 15])
        self.assertEqual(sc.data["SR"], 7)
        self.assertEqual(sc.data["modifier"], 1)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.routine, True)
        self.assertEqual(sc.impossible, False)
        self.assertEqual(
            str(sc), "@TestUser \n```py\n" "Routineprobe: 4 FP = QS 2\n```",
        )

        sc = SkillCheck("2,3,4@4-2", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [2, 3, 4])
        self.assertEqual(sc.data["EAV"], [0, 1, 2])
        self.assertEqual(sc.data["SR"], 4)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible, True)
        self.assertEqual(
            str(sc), "@TestUser \n```py\nEEW:   0   1   2\nProbe nicht möglich\n```",
        )
