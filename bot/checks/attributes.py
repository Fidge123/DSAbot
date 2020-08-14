class Attributes(list):
    def __str__(self) -> str:
        return "".join("{:>4}".format(attr) for attr in self)
