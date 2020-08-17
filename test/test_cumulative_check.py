from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.checks import CumulativeCheck


class MockAuthor:
    def __init__(self, name):
        self.mention = "@{}".format(name)


class TestCumulativeCheck(TestCase):
    def test_parse(self):
        self.assertIsNotNone(
            CumulativeCheck("S5x5KR 13 13 13 @ 5", MockAuthor("TestUser"))
        )
        self.assertIsNotNone(
            CumulativeCheck(
                "!Sammelprobe 15x120 Stunden 13,13,13@15 - 2 +1 Kommentar",
                MockAuthor("TestUser"),
            )
        )

        with self.assertRaises(ValueError):
            CumulativeCheck("!!13 ", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("!  1 ", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("!?4", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("#2", MockAuthor("TestUser"))

    def test_parse_with_other_commands(self):
        with self.assertRaises(ValueError):
            CumulativeCheck("d3", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("note:foobar", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("SUMMON", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("BEGONE", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("DIE", MockAuthor("TestUser"))
        with self.assertRaises(ValueError):
            CumulativeCheck("13,13,13+1", MockAuthor("TestUser"))

    # @patch("random.randint", new_callable=MagicMock())
    # def test_end2end_botch(self, mock_randint: MagicMock):
    #     mock_randint.return_value = 12
    #     cc = CumulativeCheck(
    #         "!Sammelprobe 5x3Tage 12 14 10 @ 3", MockAuthor("TestUser")
    #     )
    #     self.assertEqual(cc.data["attributes"], [17, 16, 10])
    #     self.assertEqual(cc.data["EAV"], [17, 16, 10])
    #     self.assertEqual(cc.data["modifier"], 0)
    #     self.assertEqual(cc.data["SR"], 10)
    #     self.assertEqual(cc.data["comment"], "")
    #     self.assertEqual(cc.data["author"], "@TestUser")
    #     self.assertEqual(cc.data["rolls"].rolls, [20, 20, 20])
    #     self.assertEqual(cc.data["rolls"].critical_success, False)
    #     self.assertEqual(cc.data["rolls"].botch, True)
    #     self.assertEqual(cc.impossible, False)
    #     self.assertEqual(
    #         str(cc),
    #         "@TestUser \n\n"
    #         "Runde 1: EEW  17  16  10  Würfel  20  20  20  FW10  -3  -4 -10=-7FP  Patzer!\n\n"
    #         "Probe fehlgeschlagen nach 1 Runden (4h)",
    #     )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_crit(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        cc = CumulativeCheck("S5x5KR 13 13 13 @ 5 -2 Test", MockAuthor("TestUser"))
        self.assertEqual(cc.data["attributes"], [13, 13, 13])
        self.assertEqual(cc.data["EAV"], [11, 11, 11])
        self.assertEqual(cc.data["modifier"], -2)
        self.assertEqual(cc.data["SR"], 5)
        self.assertEqual(cc.data["comment"], "Test")
        self.assertEqual(cc.data["author"], "@TestUser")
        self.assertEqual(cc.data["rolls"].rolls, [1, 1, 1])
        self.assertEqual(cc.data["rolls"].critical_success, True)
        self.assertEqual(cc.data["rolls"].botch, False)
        self.assertEqual(cc.impossible, False)
        self.assertEqual(
            str(cc),
            "@TestUser Test\n\n"
            "Runde 1: EEW  11  11  11  Würfel   1   1   1  FW5            =5FP  Kritischer Erfolg! (QS4)\n"
            "Runde 2: EEW  11  11  11  Würfel   1   1   1  FW5            =5FP  Kritischer Erfolg! (QS4)\n"
            "Runde 3: EEW  11  11  11  Würfel   1   1   1  FW5            =5FP  Kritischer Erfolg! (QS4)\n\n"
            "Probe erfolgreich nach 3 Runden (15KR)",
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end_botch(self, mock_randint: MagicMock):
        mock_randint.return_value = 20
        cc = CumulativeCheck("S10 * 4 h 17 16 10 @ 10", MockAuthor("TestUser"))
        self.assertEqual(cc.data["attributes"], [17, 16, 10])
        self.assertEqual(cc.data["EAV"], [17, 16, 10])
        self.assertEqual(cc.data["modifier"], 0)
        self.assertEqual(cc.data["SR"], 10)
        self.assertEqual(cc.data["comment"], "")
        self.assertEqual(cc.data["author"], "@TestUser")
        self.assertEqual(cc.data["rolls"].rolls, [20, 20, 20])
        self.assertEqual(cc.data["rolls"].critical_success, False)
        self.assertEqual(cc.data["rolls"].botch, True)
        self.assertEqual(cc.impossible, False)
        self.assertEqual(
            str(cc),
            "@TestUser \n\n"
            "Runde 1: EEW  17  16  10  Würfel  20  20  20  FW10  -3  -4 -10=-7FP  Patzer!\n\n"
            "Probe fehlgeschlagen nach 1 Runden (4h)",
        )
