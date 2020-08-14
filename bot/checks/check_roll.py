import random


class CheckRolls:
    def __init__(self, num: int):
        self.rolls = [random.randint(1, 20) for _ in range(num)]
        if num == 1 and (self.critical_success or self.botch):
            self.confirmation_roll = random.randint(1, 20)

    def reroll(self, i: int) -> None:
        self.rolls[i] = random.randint(1, 20)

    @property
    def critical_success(self) -> bool:
        check = len(self) == 3 and self.rolls.count(1) >= 2
        roll = len(self) == 1 and self.rolls[0] == 1
        return check or roll

    @property
    def botch(self) -> bool:
        check = len(self) == 3 and self.rolls.count(20) >= 2
        roll = len(self) == 1 and self.rolls[0] == 20
        return check or roll

    def __len__(self) -> int:
        return len(self.rolls)

    def __getitem__(self, key: int) -> int:
        return self.rolls[key]

    def __str__(self) -> str:
        if hasattr(self, "confirmation_roll"):
            return "{roll:>4} --> {confirm}".format(
                roll=self.rolls[0], confirm=self.confirmation_roll
            )
        else:
            return "".join("{:>4}".format(roll) for roll in self.rolls)

    def __format__(self, spec: str) -> str:
        if spec in ["", "s"]:
            return str(self)
        else:
            raise TypeError
