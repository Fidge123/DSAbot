from unittest.mock import MagicMock


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class MockChannel:
    def __init__(self, channel_id=123456789, send=AsyncMock()):
        self.id = channel_id
        self.send = send
        self.guild = MockGuild(123456789)


class MockAuthor:
    def __init__(self, name):
        self.name = name
        self.mention = "@{}".format(name)
        self.guild = MockGuild(123456789)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return str(self) == other

    def __str__(self):
        return "{}#123456789".format(self.name)


class MockGuild:
    def __init__(self, id):
        self.id = id


class MockMessage:
    def __init__(
        self,
        author,
        content="foobar",
        channel=MockChannel(),
        add_reaction=AsyncMock(),
    ):
        self.content = content
        self.author = author
        self.channel = channel
        self.guild = MockGuild(123456789)
        self.add_reaction = add_reaction
