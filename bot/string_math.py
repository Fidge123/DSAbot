import operator
import random
from typing import Any

from pyparsing import (
    ParserElement,
    pyparsing_common as ppc,
    oneOf,
    infixNotation,
    opAssoc,
)

ParserElement.enablePackrat()


def dice_roll(amount: int, sides: int, rolls: list[Any]) -> (int, list[Any]):
    aggregate = 0
    results = []
    for _ in range(int(amount)):
        roll = random.randint(1, int(sides))
        results.append(roll)
        aggregate += roll

    rolls.append((int(sides), results))

    return (aggregate, rolls)


class EvalBase:
    def __init__(self, tokens):
        self.value = tokens[0]


class EvalConstant(EvalBase):
    def eval(self, rolls):
        return float(self.value), rolls


class EvalSignOp:
    def __init__(self, tokens):
        self.sign, self.value = tokens[0]

    def eval(self, rolls) -> (float, list[Any]):
        mult = {"+": 1, "-": -1}[self.sign]
        res, rolls = self.value.eval(rolls)
        return (mult * res, rolls)


class EvalDieOp:
    def __init__(self, tokens):
        self.sign, self.value = tokens[0]

    def eval(self, rolls) -> (int, list[Any]):
        sides, rolls = self.value.eval(rolls)
        return dice_roll(1, sides, rolls)


class EvalDiceOp(EvalBase):
    def eval(self, rolls) -> (int, list[Any]):
        amount, rolls = self.value[0].eval(rolls)

        it = iter(self.value[1:])
        for op, val in zip(it, it):
            sides, rolls = val.eval(rolls)
            res, rolls = dice_roll(amount, sides, rolls)
        return (res, rolls)


class EvalInfixOp(EvalBase):
    opn = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    def eval(self, rolls) -> (float, list[Any]):
        res, rolls = self.value[0].eval(rolls)

        it = iter(self.value[1:])
        for op, val in zip(it, it):
            res2, rolls = val.eval(rolls)
            res = self.opn[op](res, res2)
        return res, rolls


grammar = infixNotation(
    ppc.integer.setParseAction(EvalConstant),
    [
        (oneOf("d w D W"), 1, opAssoc.RIGHT, EvalDieOp),
        (oneOf("+ -"), 1, opAssoc.RIGHT, EvalSignOp),
        (oneOf("d w D W"), 2, opAssoc.LEFT, EvalDiceOp),
        (oneOf("* /"), 2, opAssoc.LEFT, EvalInfixOp),
        (oneOf("+ -"), 2, opAssoc.LEFT, EvalInfixOp),
    ],
)


def calc(math_string: str) -> (float, list[Any]):
    return grammar.parseString(math_string)[0].eval([])
