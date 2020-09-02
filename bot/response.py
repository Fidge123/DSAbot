class Response:
    def __init__(self, send=None, *args, **kwargs):
        self.messages = []
        if send is not None:
            self.append(send, *args, **kwargs)

    def append(self, send, *args, **kwargs) -> None:
        self.messages.append({"send": send, "args": args, "kwargs": kwargs})

    async def send(self) -> None:
        for message in self.messages:
            send = message["send"]
            await send(*message["args"], **message["kwargs"])
