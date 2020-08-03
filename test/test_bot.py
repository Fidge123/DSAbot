import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot.bot import on_message
from bot import persistence


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class MockChannel:
    send: AsyncMock

    def __init__(self, channel_id, send):
        self.id = channel_id
        self.send = send


class MockAuthor:
    mention: AsyncMock

    def __init__(self, channel_id, send):
        self.name = channel_id
        self.mention = send

    def __eq__(self, other):
        return str(self) == other

    def __str__(self):
        return self.name


class MockMessage:
    channel: MockChannel

    def __init__(
        self, content, author, channel, add_reaction,
    ):
        self.content = content
        self.author = author
        self.channel = channel
        self.add_reaction = add_reaction


# noinspection PyTypeChecker
class TestBot(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loop = asyncio.get_event_loop()
        cls.testchannel = MockChannel(1, AsyncMock())
        cls.testauthor = MockAuthor("Author", "<@1337>")
        persistence.init_db()

    def message(self, msg):
        return MockMessage(msg, self.testauthor, self.testchannel, AsyncMock())

    def skill_check(self, msg, result):
        messages = ["SUMMON", msg, "BEGONE"]

        for m in messages:
            with self.subTest(msg=m):
                m = self.message(m)
                self.loop.run_until_complete(on_message(m))
                if msg in m.content:
                    m.channel.send.assert_called_with(result)

    @patch("random.randint", new_callable=MagicMock())
    def test_smoke(self, mock_randint: MagicMock):
        # Set Up
        mock_randint.return_value = 1
        messages = ["SUMMON", "5d10", "5w10+5", "12,12,12@10 -3 Verbergen", "BEGONE"]

        for m in messages:
            with self.subTest(msg=m):
                m = self.message(m)
                self.loop.run_until_complete(on_message(m))
                if "d" in m.content.lower():
                    mock_randint.assert_called_with(1, 10)
                    m.channel.send.assert_called_with("<@1337> \n1 + 1 + 1 + 1 + 1 = 5")

                if "w" in m.content.lower():
                    mock_randint.assert_called_with(1, 10)
                    m.channel.send.assert_called_with(
                        "<@1337> \n1 + 1 + 1 + 1 + 1 (+5) = 10"
                    )

                if "@" in m.content:
                    mock_randint.assert_called_with(1, 20)
                    m.channel.send.assert_called_with(
                        "<@1337> Verbergen\n1, 1, 1 ===> 0\n(10 - 0 = 10 FP) QS: 4\n**Kritischer Erfolg!**"
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
        messages = ["SUMMON", "note:blub->7", "note:klik->8", "note:klik->9", "BEGONE"]

        for m in messages:
            with self.subTest(msg=m):
                m = self.message(m)
                self.loop.run_until_complete(on_message(m))
                if "blub" in m.content.lower():
                    m.channel.send.assert_called_with("blub is now 7")
                elif "8" in m.content.lower():
                    m.channel.send.assert_called_with("klik is now 8")
                elif "9" in m.content.lower():
                    m.channel.send.assert_called_with("klik is now 17")
