class Attributes:
    def __init__(self, attributes: int):
        self.attributes = attributes

    def __len__(self) -> int:
        return len(self.attributes)

    def __getitem__(self, key: int) -> int:
        return self.attributes[key]

    def __str__(self) -> str:
        return "".join("{:>4}".format(attr) for attr in self.attributes)

    def __format__(self, spec: str) -> str:
        if spec in ["", "s"]:
            return str(self)
        else:
            raise TypeError
