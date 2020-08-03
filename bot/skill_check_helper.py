import random


def get_attributes(input: str):
    return input.strip().replace(",", " ").replace("  ", " ").split(" ")


def roll_for_attr(attr: [int]):
    return list(
        map(lambda attr: {"attr": int(attr), "roll": random.randint(1, 20),}, attr)
    )


def rolls_to_str(rolls):
    return ", ".join(map(lambda x: str(x["roll"]), rolls))


def calc_skill_req(rolls, add, sub):
    return sum(
        map(
            lambda x: max([x["roll"] - x["attr"] - int(add or 0) + int(sub or 0), 0]),
            rolls,
        )
    )
