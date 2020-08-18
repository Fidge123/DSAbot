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

    @patch("random.randint", new_callable=MagicMock())
    def test_end2end(self, mock_randint: MagicMock):
        mock_randint.return_value = 13
        cc = CumulativeCheck(
            "!Sammelprobe 5x2 Tage 12 14 10 @ 3", MockAuthor("TestUser")
        )
        self.assertEqual(
            str(cc),
            "@TestUser \n"
            "```py\n"
            "Runde  1: EEW  12  14  10  Würfel  13  13  13  FW3  -1      -3=-1FP  Nicht bestanden\n"
            "Runde  2: EEW  11  13   9  Würfel  13  13  13  FW3  -2      -4=-3FP  Nicht bestanden\n"
            "Runde  3: EEW  10  12   8  Würfel  13  13  13  FW3  -3  -1  -5=-6FP  Nicht bestanden\n"
            "Runde  4: EEW   9  11   7  Würfel  13  13  13  FW3  -4  -2  -6=-9FP  Nicht bestanden\n"
            "Runde  5: EEW   8  10   6  Würfel  13  13  13  FW3  -5  -3  -7=-12FP  Nicht bestanden\n\n"
            "Probe fehlgeschlagen nach 5 Runden (10Tage)\n"
            "```",
        )

        mock_randint.return_value = 13
        cc = CumulativeCheck(
            "!Sammelprobe 5x2 Tage 12 14 10 @ 5", MockAuthor("TestUser")
        )
        self.assertEqual(
            str(cc),
            "@TestUser \n"
            "```py\n"
            "Runde  1: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  2: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  3: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  4: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  5: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n\n"
            "Probe fehlgeschlagen nach 5 Runden (10Tage)\n"
            "```",
        )

        mock_randint.return_value = 13
        cc = CumulativeCheck(
            "!Sammelprobe 6x2 Tage 12 14 10 @ 5", MockAuthor("TestUser")
        )
        self.assertEqual(
            str(cc),
            "@TestUser \n"
            "```py\n"
            "Runde  1: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  2: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  3: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  4: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  5: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n"
            "Runde  6: EEW  12  14  10  Würfel  13  13  13  FW5  -1      -3= 1FP  QS1\n\n"
            "Teilerfolg nach 6 Runden (12Tage)\n"
            "```",
        )

        mock_randint.return_value = 13
        cc = CumulativeCheck(
            "!Sammelprobe 5x2 Tage 12 14 10 @ 10", MockAuthor("TestUser")
        )
        self.assertEqual(
            str(cc),
            "@TestUser \n"
            "```py\n"
            "Runde  1: EEW  12  14  10  Würfel  13  13  13  FW10  -1      -3= 6FP  QS2\n"
            "Runde  2: EEW  12  14  10  Würfel  13  13  13  FW10  -1      -3= 6FP  QS2\n"
            "Runde  3: EEW  12  14  10  Würfel  13  13  13  FW10  -1      -3= 6FP  QS2\n"
            "Runde  4: EEW  12  14  10  Würfel  13  13  13  FW10  -1      -3= 6FP  QS2\n"
            "Runde  5: EEW  12  14  10  Würfel  13  13  13  FW10  -1      -3= 6FP  QS2\n\n"
            "Probe erfolgreich nach 5 Runden (10Tage)\n"
            "```",
        )

        mock_randint.return_value = 13
        cc = CumulativeCheck(
            "!Sammelprobe 5x2 Tage 12 14 10 @ 11", MockAuthor("TestUser")
        )
        self.assertEqual(
            str(cc),
            "@TestUser \n"
            "```py\n"
            "Runde  1: EEW  12  14  10  Würfel  13  13  13  FW11  -1      -3= 7FP  QS3\n"
            "Runde  2: EEW  12  14  10  Würfel  13  13  13  FW11  -1      -3= 7FP  QS3\n"
            "Runde  3: EEW  12  14  10  Würfel  13  13  13  FW11  -1      -3= 7FP  QS3\n"
            "Runde  4: EEW  12  14  10  Würfel  13  13  13  FW11  -1      -3= 7FP  QS3\n\n"
            "Probe erfolgreich nach 4 Runden (8Tage)\n"
            "```",
        )

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
            "@TestUser Test\n"
            "```py\n"
            "Runde  1: EEW  11  11  11  Würfel   1   1   1  FW5            = 5FP  Kritischer Erfolg! (QS4)\n"
            "Runde  2: EEW  11  11  11  Würfel   1   1   1  FW5            = 5FP  Kritischer Erfolg! (QS4)\n"
            "Runde  3: EEW  11  11  11  Würfel   1   1   1  FW5            = 5FP  Kritischer Erfolg! (QS4)\n\n"
            "Probe erfolgreich nach 3 Runden (15KR)\n"
            "```",
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
            "@TestUser \n"
            "```py\n"
            "Runde  1: EEW  17  16  10  Würfel  20  20  20  FW10  -3  -4 -10=-7FP  Patzer!\n\n"
            "Probe fehlgeschlagen nach 1 Runden (4h)\n"
            "```",
        )
