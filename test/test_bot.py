import asyncio
from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.bot import on_message
from bot import persistence
from test.mocks import MockAuthor, MockChannel, MockMessage, AsyncMock


class TestBot(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loop = asyncio.get_event_loop()
        cls.testchannel = MockChannel(1, AsyncMock())
        cls.testauthor = MockAuthor("Author")
        persistence.on_ready()

    def message(self, msg):
        return MockMessage(
            author=self.testauthor,
            content=msg,
            channel=self.testchannel,
            add_reaction=AsyncMock(),
        )

    @patch("random.randint", new_callable=MagicMock())
    def test_smoke(self, mock_randint: MagicMock):
        mock_randint.return_value = 1
        messages = [
            "SUMMON",
            "5d10",
            "5w10+5",
            "12,12,12@10 -3 Verbergen",
            "12,12-3 + 5 Schwimmen",
            "!12-3 + 5 Breitschwert",
            "BEGONE",
        ]

        for i, m in enumerate(messages):
            with self.subTest(msg=m):
                m = self.message(m)
                self.loop.run_until_complete(on_message(m))
                if i == 1:
                    mock_randint.assert_called_with(1, 10)
                    m.channel.send.assert_called_with("@Author \n1 + 1 + 1 + 1 + 1 = 5")
                if i == 2:
                    mock_randint.assert_called_with(1, 10)
                    m.channel.send.assert_called_with(
                        "@Author \n1 + 1 + 1 + 1 + 1 (+5) = 10"
                    )
                if i == 3:
                    mock_randint.assert_called_with(1, 20)
                    m.channel.send.assert_called_with(
                        "@Author Verbergen\n"
                        "```py\n"
                        "EEW:      9   9   9\n"
                        "Würfel:   1   1   1\n"
                        "FW 10               = 10 FP\n"
                        "Kritischer Erfolg! (QS 4)\n"
                        "```"
                    )
                if i == 4:
                    mock_randint.assert_called_with(1, 20)
                    m.channel.send.assert_called_with(
                        "@Author Schwimmen\n"
                        "```py\n"
                        "EEW:     14  14\n"
                        "Würfel:   1   1\n"
                        "Bestanden\n"
                        "```"
                    )
                if i == 5:
                    mock_randint.assert_called_with(1, 20)
                    m.channel.send.assert_called_with(
                        "@Author Breitschwert\n"
                        "```py\n"
                        "EEW:     14\n"
                        "Würfel:   1 --> 1\n"
                        "Kritischer Erfolg!\n"
                        "```"
                    )

    @patch("bot.note.datetime")
    def test_notes(self, mock_dt: MagicMock):
        mock_dt.utcnow = MagicMock(return_value=datetime(2019, 1, 1))
        messages = [
            "SUMMON",
            "note:test_blub->7",
            "note:test_klik->8",
            "note:test_klik->9",
            "notes",
            "delete note test_blub",
            "delete note test_klik",
            "delete note test_klik",
            "BEGONE",
        ]

        for i, m in enumerate(messages):
            with self.subTest(msg=m):
                m = self.message(m)
                self.loop.run_until_complete(on_message(m))
                if i == 1:
                    m.channel.send.assert_called_with("@Author test_blub ist jetzt 7.")
                if i == 2:
                    m.channel.send.assert_called_with("@Author test_klik ist jetzt 8.")
                if i == 3:
                    m.channel.send.assert_called_with("@Author test_klik ist jetzt 17.")
                if i == 4:
                    m.channel.send.assert_called_with(
                        "@Author\n```test_blub :  7 (01.01.19)\ntest_klik : 17 (01.01.19)```"
                    )
                if i == 5:
                    m.channel.send.assert_called_with(
                        "@Author test_blub war 7 und wurde nun gelöscht."
                    )
                if i == 6:
                    m.channel.send.assert_called_with(
                        "@Author test_klik war 17 und wurde nun gelöscht."
                    )
                if i == 7:
                    m.channel.send.assert_called_with(
                        "@Author Es gibt keine Notiz test_klik."
                    )
