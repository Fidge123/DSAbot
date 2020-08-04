import operator
from pyparsing import (
    ParserElement,
    pyparsing_common,
    oneOf,
    infixNotation,
    opAssoc,
)

ParserElement.enablePackrat()

operand = pyparsing_common.integer

signop = oneOf("+ -")
multop = oneOf("* /")
plusop = oneOf("+ -")

opn = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


def evaluate(s):
    if isinstance(s, int):
        return s
    if len(s) == 1:
        return evaluate(s[0])
    if len(s) == 2 and s[0] == "-":
        return -s[1]
    if len(s) == 2 and s[0] == "+":
        return s[1]
    if len(s) == 3 and s[1] in "+-*/":
        return opn[s[1]](evaluate(s[0]), evaluate(s[2]))
    if len(s) > 3 and s[1] in "+-*/":
        return evaluate([opn[s[1]](evaluate(s[0]), evaluate(s[2]))] + s[3:])
    else:
        raise Exception("Can't parse this! {}".format(s))


def calc(input):
    expr = infixNotation(
        operand,
        [
            (signop, 1, opAssoc.RIGHT),
            (multop, 2, opAssoc.LEFT),
            (plusop, 2, opAssoc.LEFT),
        ],
    )
    return evaluate(expr.parseString(input))
