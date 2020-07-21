import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch

from DSAbot import on_message


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

    def message(self, msg):
        return MockMessage(msg, self.testauthor, self.testchannel, AsyncMock())

    @patch("random.randint", new_callable=MagicMock())
    def test_smoke(self, mock_randint: MagicMock):
        # Set Up
        mock_randint.return_value = 1
        summon = self.message("SUMMON")
        roll = self.message("5d10")

        # Test SUMMON
        self.loop.run_until_complete(on_message(summon))

        # Test rolling
        self.loop.run_until_complete(on_message(roll))

        # assert
        mock_randint.assert_called_with(1, 10)
        roll.channel.send.assert_called_with("<@1337>\n1, 1, 1, 1, 1")
