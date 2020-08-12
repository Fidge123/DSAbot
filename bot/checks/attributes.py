class Attributes:
    def __init__(self, attributes):
        self.attributes = attributes

    def __len__(self):
        return len(self.attributes)

    def __getitem__(self, key):
        return self.attributes[key]

    def __str__(self):
        return "".join("{:>4}".format(attr) for attr in self.attributes)

    def __format__(self, spec):
        if spec in ["", "s"]:
            return str(self)
        else:
            raise TypeError
