import operator
from pyparsing import (
    ParserElement,
    pyparsing_common as ppc,
    oneOf,
    infixNotation,
    opAssoc,
)

ParserElement.enablePackrat()


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
        (oneOf("+ -"), 1, opAssoc.RIGHT, EvalSignOp),
        (oneOf("* /"), 2, opAssoc.LEFT, EvalInfixOp),
        (oneOf("+ -"), 2, opAssoc.LEFT, EvalInfixOp),
    ],
)


def calc(math_string: str) -> float:
    return grammar.parseString(math_string)[0].eval()
