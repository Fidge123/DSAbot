from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.skill_check import SkillCheck


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
        self.assertEqual(sc.quality_level, 1)

        sc = SkillCheck("11,9,9@1", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 1)
        self.assertEqual(sc.quality_level, 1)

        sc = SkillCheck("11,9,9@2", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 2)
        self.assertEqual(sc.quality_level, 1)

        sc = SkillCheck("11,9,9@3", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 3)
        self.assertEqual(sc.quality_level, 1)

        sc = SkillCheck("11,9,9@4", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(sc.quality_level, 2)

        sc = SkillCheck("11,9,9@5", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 5)
        self.assertEqual(sc.quality_level, 2)

        sc = SkillCheck("11,9,9@6", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 6)
        self.assertEqual(sc.quality_level, 2)

        sc = SkillCheck("11,9,9@7", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 7)
        self.assertEqual(sc.quality_level, 3)

        sc = SkillCheck("11,9,9@8", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 8)
        self.assertEqual(sc.quality_level, 3)

        sc = SkillCheck("11,9,9@9", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 9)
        self.assertEqual(sc.quality_level, 3)

        sc = SkillCheck("11,9,9@10", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 10)
        self.assertEqual(sc.quality_level, 4)

        sc = SkillCheck("11,9,9@16", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 16)
        self.assertEqual(sc.quality_level, 6)

        sc = SkillCheck("11,9,9@26", MockAuthor("TestUser"))
        self.assertEqual(sc.skill_points, 26)
        self.assertEqual(sc.quality_level, 6)

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end(self, mock_randint: MagicMock):
        mock_randint.return_value = 9
        sc = SkillCheck("11,9,9@4", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [11, 9, 9])
        self.assertEqual(sc.data["SR"], 4)
        self.assertEqual(sc.data["modifier"], 0)
        self.assertEqual(sc.data["comment"], "")
        self.assertEqual(sc.data["skill_req"], 0)
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.skill_points, 4)
        self.assertEqual(sc.quality_level, 2)
        self.assertEqual(str(sc), "@TestUser \n9, 9, 9 ===> 0\n(4 - 0 = 4 FP) QS: 2")

        sc = SkillCheck("!13 14 15@6-2 Sinnesschärfe", MockAuthor("TU"))
        self.assertEqual(sc.data["attributes"], [13, 14, 15])
        self.assertEqual(sc.data["SR"], 6)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["comment"], "Sinnesschärfe")
        self.assertEqual(sc.data["skill_req"], 0)
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.skill_points, 6)
        self.assertEqual(sc.quality_level, 2)
        self.assertEqual(
            str(sc), "@TU Sinnesschärfe\n9, 9, 9 ===> 0\n(6 - 0 = 6 FP) QS: 2"
        )

        sc = SkillCheck("!5 3, 4,@16 +1+1 -2- 2 🎉-1", MockAuthor("TestUser"))
        self.assertEqual(sc.data["attributes"], [5, 3, 4])
        self.assertEqual(sc.data["SR"], 16)
        self.assertEqual(sc.data["modifier"], -2)
        self.assertEqual(sc.data["comment"], "🎉-1")
        self.assertEqual(sc.data["skill_req"], 21)
        self.assertEqual(sc.data["rolls"].rolls, [9, 9, 9])
        self.assertEqual(sc.data["rolls"].critical_success, False)
        self.assertEqual(sc.data["rolls"].botch, False)
        self.assertEqual(sc.skill_points, -5)
        self.assertEqual(sc.quality_level, 1)
        self.assertEqual(
            str(sc),
            "@TestUser 🎉-1\n9, 9, 9 ===> 21\n(16 - 21 = -5 FP) Nicht bestanden",
        )
