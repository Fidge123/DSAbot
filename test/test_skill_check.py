from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.checks import SkillCheck
from test.mocks import MockAuthor


class TestSkillCheck(TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.author = MockAuthor("TestUser")

    def test_parse(self):
        self.assertIsNotNone(SkillCheck(self.author, "13 14 15@2"))
        self.assertIsNotNone(SkillCheck(self.author, "1,12,18@18"))
        self.assertIsNotNone(SkillCheck(self.author, "8 19 1400@0 + 14"))
        self.assertIsNotNone(SkillCheck(self.author, "2 2,2, @1400-2-2-2"))
        self.assertIsNotNone(SkillCheck(self.author, "!13 1 12@2 +1+1 Test"))
        self.assertIsNotNone(SkillCheck(self.author, "! 1,12,18@18 Krit"))
        self.assertIsNotNone(SkillCheck(self.author, "14 14 14@5+2FP Spezialisierung"))
        self.assertIsNotNone(SkillCheck(self.author, "14 14 14 @ 5 -2 +3 -5FP +3FP"))

        with self.assertRaises(ValueError):
            SkillCheck(self.author, "!!13 1@2")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "!  1 13@0")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "!?4")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "#2,2,2@2")

    def test_parse_with_other_commands(self):
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "d3")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "note:foobar")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "SUMMON")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "BEGONE")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "DIE")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "13,13,13+1")
        with self.assertRaises(ValueError):
            SkillCheck(self.author, "13")

    @patch("random.randint", new_callable=MagicMock())
    def test_quality_level(self, mock_randint: MagicMock):
        mock_randint.return_value = 2
        sc = SkillCheck(self.author, "11,9,9@0")
        self.assertEqual(sc.skill_points, 0)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck(self.author, "11,9,9@1")
        self.assertEqual(sc.skill_points, 1)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck(self.author, "11,9,9@2")
        self.assertEqual(sc.skill_points, 2)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck(self.author, "11,9,9@3")
        self.assertEqual(sc.skill_points, 3)
        self.assertEqual(sc.ql(sc.skill_points), 1)

        sc = SkillCheck(self.author, "11,9,9@4")
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(sc.ql(sc.skill_points), 2)

        sc = SkillCheck(self.author, "11,9,9@5")
        self.assertEqual(sc.skill_points, 5)
        self.assertEqual(sc.ql(sc.skill_points), 2)

        sc = SkillCheck(self.author, "11,9,9@6")
        self.assertEqual(sc.skill_points, 6)
        self.assertEqual(sc.ql(sc.skill_points), 2)

        sc = SkillCheck(self.author, "11,9,9@7")
        self.assertEqual(sc.skill_points, 7)
        self.assertEqual(sc.ql(sc.skill_points), 3)

        sc = SkillCheck(self.author, "11,9,9@8")
        self.assertEqual(sc.skill_points, 8)
        self.assertEqual(sc.ql(sc.skill_points), 3)

        sc = SkillCheck(self.author, "11,9,9@9")
        self.assertEqual(sc.skill_points, 9)
        self.assertEqual(sc.ql(sc.skill_points), 3)

        sc = SkillCheck(self.author, "11,9,9@10")
        self.assertEqual(sc.skill_points, 10)
        self.assertEqual(sc.ql(sc.skill_points), 4)

        sc = SkillCheck(self.author, "11,9,9@16")
        self.assertEqual(sc.skill_points, 16)
        self.assertEqual(sc.ql(sc.skill_points), 6)

        sc = SkillCheck(self.author, "11,9,9@26")
        self.assertEqual(sc.skill_points, 26)
        self.assertEqual(sc.ql(sc.skill_points), 6)

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        sc = SkillCheck(self.author, "11,9,9@4")
        self.assertEqual(sc.data["attributes"], [11, 9, 9])
        self.assertEqual(sc.data["EAV"], [11, 9, 9])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 4)
        self.assertEqual(sc.data["modifier"], 0)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(
            str(sc),
            " \n"
            "```py\n"
            "EEW:      11   9   9\n"
            "Würfel:    9   9   9\n"
            "FW 4                 = 4 FP\n"
            "Bestanden mit QS 2\n"
            "```",
        )

        sc = SkillCheck(self.author, "!13 14 15@6-2 Sinnesschärfe")
        self.assertEqual(sc.data["attributes"], [13, 14, 15])
        self.assertEqual(sc.data["EAV"], [11, 12, 13])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 6)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "Sinnesschärfe")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 6)
        self.assertEqual(
            str(sc),
            " Sinnesschärfe\n"
            "```py\n"
            "EEW:      11  12  13\n"
            "Würfel:    9   9   9\n"
            "FW 6                 = 6 FP\n"
            "Bestanden mit QS 2\n"
            "```",
        )

        sc = SkillCheck(self.author, "!5 3, 4,@16 +1+1 -2- 2 🎉-1")
        self.assertEqual(sc.data["attributes"], [5, 3, 4])
        self.assertEqual(sc.data["EAV"], [3, 1, 2])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 16)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "🎉-1")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [-6, -8, -7])
        self.assertEqual(sc.skill_points, -5)
        self.assertEqual(
            str(sc),
            " 🎉-1\n"
            "```py\n"
            "EEW:       3   1   2\n"
            "Würfel:    9   9   9\n"
            "FW 16     -6  -8  -7 = -5 FP\n"
            "Nicht bestanden\n"
            "```",
        )

        sc = SkillCheck(self.author, "14 14 14@5-5FP Spezialisierung")
        self.assertEqual(sc.data["attributes"], [14, 14, 14])
        self.assertEqual(sc.data["EAV"], [14, 14, 14])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 5)
        self.assertEqual(sc.data["modifier"], 0)
        self.assertEqual(sc.data["modifierFP"], -5)
        self.assertEqual(sc.data["comment"], "Spezialisierung")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 0)
        self.assertEqual(
            str(sc),
            " Spezialisierung\n"
            "```py\n"
            "EEW:      14  14  14\n"
            "Würfel:    9   9   9\n"
            "FW 5 -5              = 0 FP\n"
            "Bestanden mit QS 1\n"
            "```",
        )

        sc = SkillCheck(self.author, "7 5 6 @ 16 -1 -3 -1FP +6FP +3FP test")
        self.assertEqual(sc.data["attributes"], [7, 5, 6])
        self.assertEqual(sc.data["EAV"], [3, 1, 2])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 16)
        self.assertEqual(sc.data["modifier"], -4)
        self.assertEqual(sc.data["modifierFP"], 8)
        self.assertEqual(sc.data["comment"], "test")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [-6, -8, -7])
        self.assertEqual(sc.skill_points, 3)
        self.assertEqual(
            str(sc),
            " test\n"
            "```py\n"
            "EEW:       3   1   2\n"
            "Würfel:    9   9   9\n"
            "FW 16+8   -6  -8  -7 = 3 FP\n"
            "Bestanden mit QS 1\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_crit_botch(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        sc = SkillCheck(self.author, "2,3,4@4")
        self.assertEqual(sc.data["attributes"], [2, 3, 4])
        self.assertEqual(sc.data["EAV"], [2, 3, 4])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 4)
        self.assertEqual(sc.data["modifier"], 0)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [1, 1, 1])
        self.assertEqual(sc.data["rolls"].critical_success, True)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(
            str(sc),
            " \n"
            "```py\n"
            "EEW:       2   3   4\n"
            "Würfel:    1   1   1\n"
            "FW 4                 = 4 FP\n"
            "Kritischer Erfolg! (QS 2)\n"
            "```",
        )

        mock_randint.return_value = 20
        sc = SkillCheck(self.author, "14 18 18@3 + 2")
        self.assertEqual(sc.data["attributes"], [14, 18, 18])
        self.assertEqual(sc.data["EAV"], [16, 20, 20])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 3)
        self.assertEqual(sc.data["modifier"], 2)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [20, 20, 20])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, True)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [-4, 0, 0])
        self.assertEqual(sc.skill_points, -1)
        self.assertEqual(
            str(sc),
            " \n"
            "```py\n"
            "EEW:      16  20  20\n"
            "Würfel:   20  20  20\n"
            "FW 3      -4         = -1 FP\n"
            "Patzer!\n"
            "```",
        )

        mock_randint.return_value = 20
        sc = SkillCheck(self.author, "18,18 18@3 + 2")
        self.assertEqual(sc.data["attributes"], [18, 18, 18])
        self.assertEqual(sc.data["EAV"], [20, 20, 20])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 3)
        self.assertEqual(sc.data["modifier"], 2)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["rolls"].rolls, [20, 20, 20])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, True)
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 3)
        self.assertEqual(
            str(sc),
            " \n"
            "```py\n"
            "EEW:      20  20  20\n"
            "Würfel:   20  20  20\n"
            "FW 3                 = 3 FP\n"
            "Patzer! - Automatisch nicht bestanden\n"
            "```",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_routine_impossible(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        sc = SkillCheck(self.author, "14, 14, 14 @ 7 + 1")
        self.assertEqual(sc.data["attributes"], [14, 14, 14])
        self.assertEqual(sc.data["EAV"], [15, 15, 15])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 7)
        self.assertEqual(sc.data["modifier"], 1)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.routine, True)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(
            str(sc),
            " \n```py\n" "Routineprobe: 4 FP = QS 2\n```",
        )

        sc = SkillCheck(self.author, "!force 13 14 15 @ 10 Sinnesschärfe")
        self.assertEqual(sc.data["attributes"], [13, 14, 15])
        self.assertEqual(sc.data["EAV"], [13, 14, 15])
        self.assertEqual(sc.data["force"], True)
        self.assertEqual(sc.data["SR"], 10)
        self.assertEqual(sc.data["modifier"], 0)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "Sinnesschärfe")
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.routine, True)
        self.assertEqual(sc.impossible(), False)
        self.assertEqual(sc.diffs, [0, 0, 0])
        self.assertEqual(sc.skill_points, 10)
        self.assertEqual(
            str(sc),
            " Sinnesschärfe\n"
            "```py\n"
            "EEW:      13  14  15\n"
            "Würfel:    9   9   9\n"
            "FW 10                = 10 FP\n"
            "Bestanden mit QS 4\n"
            "```",
        )

        sc = SkillCheck(self.author, "2,3,4@4-2")
        self.assertEqual(sc.data["attributes"], [2, 3, 4])
        self.assertEqual(sc.data["EAV"], [0, 1, 2])
        self.assertEqual(sc.data["force"], False)
        self.assertEqual(sc.data["SR"], 4)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["modifierFP"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.routine, False)
        self.assertEqual(sc.impossible(), True)
        self.assertEqual(
            str(sc),
            " \n```py\nEEW:   0   1   2\nProbe nicht möglich\n```",
        )
