import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.bot import on_message
from bot import persistence


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class MockChannel:
    def __init__(self, channel_id, send: AsyncMock):
        self.id = channel_id
        self.send = send


class MockAuthor:
    def __init__(self, channel_id, send: AsyncMock):
        self.name = channel_id
        self.mention = send

    def __hash__(self):
        return 123456789

    def __eq__(self, other):
        return str(self) == other

    def __str__(self):
        return self.name


class MockMessage:
    def __init__(
        self, content, author, channel: MockChannel, add_reaction,
    ):
        self.content = content
        self.author = author
        self.channel = channel
        self.add_reaction = add_reaction


class TestBot(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loop = asyncio.get_event_loop()
        cls.testchannel = MockChannel(1, AsyncMock())
        cls.testauthor = MockAuthor("Author", "<@1337>")
        persistence.init_db()

    def message(self, msg):
        return MockMessage(msg, self.testauthor, self.testchannel, AsyncMock())

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
                    m.channel.send.assert_called_with(
                        "<@1337> \n1 + 1 + 1 + 1 + 1 = 5", embed=None
                    )
                if i == 2:
                    mock_randint.assert_called_with(1, 10)
                    m.channel.send.assert_called_with(
                        "<@1337> \n1 + 1 + 1 + 1 + 1 (+5) = 10", embed=None
                    )
                if i == 3:
                    mock_randint.assert_called_with(1, 20)
                    m.channel.send.assert_called_with(
                        "<@1337> Verbergen\n"
                        "```py\n"
                        "EEW:      9   9   9\n"
                        "Würfel:   1   1   1\n"
                        "FW 10               = 10 FP\n"
                        "Kritischer Erfolg! (QS 4)\n"
                        "```",
                        embed=None,
                    )
                if i == 4:
                    mock_randint.assert_called_with(1, 20)
                    m.channel.send.assert_called_with(
                        "<@1337> Schwimmen\n"
                        "```py\n"
                        "EEW:     14  14\n"
                        "Würfel:   1   1\n"
                        "Bestanden\n"
                        "```",
                        embed=None,
                    )
                if i == 5:
                    mock_randint.assert_called_with(1, 20)
                    m.channel.send.assert_called_with(
                        "<@1337> Breitschwert\n"
                        "```py\n"
                        "EEW:     14\n"
                        "Würfel:   1 --> 1\n"
                        "Kritischer Erfolg!\n"
                        "```",
                        embed=None,
                    )

    def test_debug(self):
        messages = ["SUMMON", "debug:cache", "debug:fullCache", "BEGONE"]

        for m in messages:
            with self.subTest(msg=m):
                m = self.message(m)
                self.loop.run_until_complete(on_message(m))
                if "full" in m.content.lower():
                    m.channel.send.assert_called_with("fullCache")
                elif "cache" in m.content.lower():
                    m.channel.send.assert_called_with("cache")

    def test_notes(self):
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
                    m.channel.send.assert_called_with(
                        "<@1337> test_blub ist jetzt 7.", embed=None
                    )
                if i == 2:
                    m.channel.send.assert_called_with(
                        "<@1337> test_klik ist jetzt 8.", embed=None
                    )
                if i == 3:
                    m.channel.send.assert_called_with(
                        "<@1337> test_klik ist jetzt 17.", embed=None
                    )
                if i == 4:
                    m.channel.send.assert_called_with(
                        "<@1337>\n```test_blub :  7\ntest_klik : 17```", embed=None
                    )
                if i == 5:
                    m.channel.send.assert_called_with(
                        "<@1337> test_blub war 7 und wurde nun gelöscht.", embed=None
                    )
                if i == 6:
                    m.channel.send.assert_called_with(
                        "<@1337> test_klik war 17 und wurde nun gelöscht.", embed=None
                    )
                if i == 7:
                    m.channel.send.assert_called_with(
                        "<@1337> Es gibt keine Notiz test_klik.", embed=None
                    )
