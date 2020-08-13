import random


class CheckRolls:
    def __init__(self, num):
        self.rolls = []
        for _ in range(num):
            self.rolls.append(random.randint(1, 20))

        if num == 1 and (self.critical_success or self.botch):
            self.confirmation_roll = random.randint(1, 20)

    @property
    def critical_success(self):
        check = len(self) == 3 and self.rolls.count(1) >= 2
        roll = len(self) == 1 and self.rolls[0] == 1
        return check or roll

    @property
    def botch(self):
        check = len(self) == 3 and self.rolls.count(20) >= 2
        roll = len(self) == 1 and self.rolls[0] == 20
        return check or roll

    def __len__(self):
        return len(self.rolls)

    def __getitem__(self, key):
        return self.rolls[key]

    def __str__(self):
        if hasattr(self, "confirmation_roll"):
            return "{roll:>4} --> {confirm}".format(
                roll=self.rolls[0], confirm=self.confirmation_roll
            )
        else:
            return "".join("{:>4}".format(roll) for roll in self.rolls)

    def __format__(self, spec):
        if spec in ["", "s"]:
            return str(self)
        else:
            raise TypeError
