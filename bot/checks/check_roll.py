import random


class CheckRolls:
    def __init__(self, num):
        self.rolls = []
        for _ in range(num):
            self.rolls.append(random.randint(1, 20))

    @property
    def critical_success(self):
        return len(self) == 3 and self.rolls.count(1) >= 2

    @property
    def botch(self):
        return len(self) == 3 and self.rolls.count(20) >= 2

    def __len__(self):
        return len(self.rolls)

    def __getitem__(self, key):
        return self.rolls[key]

    def __str__(self):
        return "".join("{:>4}".format(roll) for roll in self.rolls)

        # return ", ".join(str(roll) for roll in self.rolls)

    def __format__(self, spec):
        if spec in ["", "s"]:
            return str(self)
        else:
            raise TypeError
