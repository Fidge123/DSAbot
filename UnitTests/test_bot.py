import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch

from DSAbot import on_message
from persistence import init_db


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
class TestDSABot(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loop = asyncio.get_event_loop()
        cls.testchannel = MockChannel(1, AsyncMock())
        cls.testauthor = MockAuthor("Author", "<@1337>")
        init_db()

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
        messages = ["SUMMON", "5d10", "5w10+5", "BEGONE"]

        for m in messages:
            with self.subTest(msg=m):
                m = self.message(m)
                self.loop.run_until_complete(on_message(m))
                if "d" in m.content.lower():
                    mock_randint.assert_called_with(1, 10)
                    m.channel.send.assert_called_with("<@1337>\n1, 1, 1, 1, 1 = 5")

                if "w" in m.content.lower():
                    mock_randint.assert_called_with(1, 10)
                    m.channel.send.assert_called_with("<@1337>\n1, 1, 1, 1, 1 = 10")

    @patch("random.randint", new_callable=MagicMock())
    def test_skillcheck(self, mock_randint: MagicMock):
        mock_randint.return_value = 14
        self.skill_check(
            "!13,14,8@12", "<@1337>\n14, 14, 14 ===> -7\n(12 - 7 = 5 FP) QS: 2"
        )
        self.skill_check("!13,14,8", "<@1337>\n14, 14, 14 ===> -7")
        self.skill_check(
            "13, 14, 8 @ 12", "<@1337>\n14, 14, 14 ===> -7\n(12 - 7 = 5 FP) QS: 2"
        )
        self.skill_check(
            "8, 8, 8 @ 0", "<@1337>\n14, 14, 14 ===> -18\n(0 - 18 = -18 FP) QS: 0 FAIL"
        )
        self.skill_check(
            "!13,14,8@12+2", "<@1337>\n14, 14, 14 ===> -4\n(12 - 4 = 8 FP) QS: 3"
        )
        self.skill_check("!13,14,8-3", "<@1337>\n14, 14, 14 ===> -16")
        self.skill_check(
            "13, 14, 8 @ 12 + 1", "<@1337>\n14, 14, 14 ===> -5\n(12 - 5 = 7 FP) QS: 3"
        )
        self.skill_check(
            "8, 8, 8 @ 0 + 6", "<@1337>\n14, 14, 14 ===> 0\n(0 - 0 = 0 FP) QS: 1",
        )
        self.skill_check("8", "<@1337>\n14 ===> -6")
        self.skill_check(
            "14 14 14 14 14 @ 0",
            "<@1337>\n14, 14, 14, 14, 14 ===> 0\n(0 - 0 = 0 FP) QS: 1",
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
