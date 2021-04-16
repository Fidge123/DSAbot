import operator
import random
from pyparsing import (
    ParserElement,
    pyparsing_common as ppc,
    oneOf,
    infixNotation,
    opAssoc,
)

ParserElement.enablePackrat()


def dice_roll(amount: int, sides: int) -> int:
    aggregate = 0
    for _ in range(int(amount)):
        roll = random.randint(1, int(sides))
        aggregate += roll
    return aggregate


class EvalBase:
    def __init__(self, tokens):
        self.value = tokens[0]


class EvalConstant(EvalBase):
    def eval(self):
        return float(self.value)


class EvalSignOp:
    def __init__(self, tokens):
        self.sign, self.value = tokens[0]

    def eval(self) -> float:
        mult = {"+": 1, "-": -1}[self.sign]
        return mult * self.value.eval()


class EvalDieOp:
    def __init__(self, tokens):
        self.sign, self.value = tokens[0]

    def eval(self) -> int:
        return dice_roll(1, self.value.eval())


class EvalDiceOp(EvalBase):
    def eval(self) -> int:
        res = self.value[0].eval()

        it = iter(self.value[1:])
        for op, val in zip(it, it):
            res = dice_roll(res, val.eval())
        return res


class EvalInfixOp(EvalBase):
    opn = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    def eval(self) -> float:
        res = self.value[0].eval()

        it = iter(self.value[1:])
        for op, val in zip(it, it):
            res = self.opn[op](res, val.eval())
        return res


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


def calc(math_string: str) -> float:
    return grammar.parseString(math_string)[0].eval()
