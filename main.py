grammer = """?start: if_expr

?if_expr: "if" logic_expr "then" action ("else" action)?

?logic_expr: expr
           | logic_expr "and" logic_expr   -> and_
           | logic_expr "or" logic_expr    -> or_
           | "not" logic_expr              -> not_

?expr: term
     | expr "+" term       -> add
     | expr "-" term       -> sub

?term: factor
     | term "*" factor     -> mul
     | term "/" factor     -> div

?factor: NUMBER            -> number
       | NAME              -> var
       | "(" logic_expr ")"
       | expr comparison_op expr -> compare

?comparison_op: "<" -> lt
              | ">" -> gt
              | "==" -> eq
              | "!=" -> ne
              | "<=" -> le
              | ">=" -> ge

?action: NAME "(" ")"      -> call

%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS
%ignore WS
"""

from lark import Lark, Transformer

class LogicalTransformer(Transformer):
    def __init__(self, variables=None, functions=None):
        self.vars = variables or {}
        self.funcs = functions or {}

    def number(self, items):
        return float(items[0])

    def var(self, items):
        name = str(items[0])
        return self.vars.get(name, 0)

    # Arithmetic
    def add(self, items): return items[0] + items[1]
    def sub(self, items): return items[0] - items[1]
    def mul(self, items): return items[0] * items[1]
    def div(self, items): return items[0] / items[1]

    # Comparison
    def compare(self, items):
        left, op, right = items[0], items[1], items[2]
        return op(left, right)

    def lt(self, _): return lambda a, b: a < b
    def gt(self, _): return lambda a, b: a > b
    def eq(self, _): return lambda a, b: a == b
    def ne(self, _): return lambda a, b: a != b
    def le(self, _): return lambda a, b: a <= b
    def ge(self, _): return lambda a, b: a >= b

    # Logical
    def and_(self, items): return items[0] and items[1]
    def or_(self, items): return items[0] or items[1]
    def not_(self, items): return not items[0]

    # Function call
    def call(self, items):
        name = str(items[0])
        return self.funcs.get(name, lambda: None)()

    # if-then-else
    def if_expr(self, items):
        condition = items[0]
        if condition:
            return items[1]
        elif len(items) == 3:
            return items[2]
        return None

def action1():
    print("Action 1 executed!")
    return "A1"

def action2():
    print("Action 2 executed!")
    return "A2"

variables = {
    "a": 2,
    "b": 4,
    "c": 5,
    "d": 10
}

functions = {
    "action1": action1,
    "action2": action2
}

grammar = """(paste the grammar here)"""

parser = Lark(grammar, parser='lalr', transformer=LogicalTransformer(variables, functions))

code = "if a < b and c + (b - 3) < d then action1() else action2()"
result = parser.parse(code)
print("Result:", result)

"""
start: conditional

conditional: "IF" condition "THEN" action ("ELSE" action)?
condition: expr (LOGICAL_OP expr)*

expr: group | comparison
group: "(" condition ")"
comparison: operand COMP_OP operand

operand: attribute | NUMBER
attribute: CNAME ("." CNAME)*

action: CNAME "(" ")"     -> call_action

LOGICAL_OP: "AND" | "OR"
COMP_OP: ">" | "<" | ">=" | "<=" | "==" | "!="

%import common.CNAME
%import common.NUM

"""
from lark import Transformer

class ConditionTransformer(Transformer):
    def conditional(self, items):
        result = {
            "condition": None,
            "then": None,
            "else": None
        }
        result["condition"] = self.flatten_condition(items[0])
        result["then"] = items[1]
        if len(items) == 3:
            result["else"] = items[2]
        return result

    def call_action(self, items):
        return str(items[0])

    def attribute(self, items):
        return ".".join(str(i) for i in items)

    def comparison(self, items):
        return f"{items[0]} {items[1]} {items[2]}"

    def expr(self, items):
        return items[0]

    def group(self, items):
        return f"({items[0]})"

    def condition(self, items):
        # example: [expr1, "AND", expr2, "OR", expr3]
        output = str(items[0])
        for i in range(1, len(items), 2):
            output += f" {items[i]} {items[i+1]}"
        return output

    def operand(self, items):
        return items[0]

    def LOGICAL_OP(self, token):
        return token.value

    def COMP_OP(self, token):
        return token.value

    def NUMBER(self, token):
        return token.value

    def flatten_condition(self, condition):
        # if already a string, return as-is
        return condition if isinstance(condition, str) else str(condition)
from lark import Lark

grammar = """[put the full grammar from above here]"""

parser = Lark(grammar, parser='lalr', transformer=ConditionTransformer())

text = 'IF (WS.AgeOfConstruction <= 3) AND (PSF > 150) THEN ONE() ELSE TWO()'

parsed = parser.parse(text)
print(parsed)
"""start: "IF" condition "THEN" action ("ELSE" action)?

condition: expr (LOGICAL_OP expr)*

?expr: group | comparison
group: "(" condition ")"
comparison: operand COMP_OP operand

?operand: attribute | NUMBER
attribute: CNAME ("." CNAME)*
action: CNAME "(" ")"

LOGICAL_OP: "AND" | "OR"
COMP_OP: "<=" | ">=" | "==" | "!=" | "<" | ">"

%import common.CNAME
%import common.NUMBER
%import common.WS
%ignore WS

"""
from lark import Lark, Transformer

class EvalTransformer(Transformer):
    def __init__(self, context):
        self.context = context  # dict of values like {"WS.Age": 3, "PSF": 150}

    def start(self, items):
        condition_result = items[0]
        then_action = items[1]
        else_action = items[2] if len(items) == 3 else None
        return then_action if condition_result else else_action

    def condition(self, items):
        result = items[0]
        for i in range(1, len(items), 2):
            op = items[i].lower()
            right = items[i+1]
            if op == 'and':
                result = result and right
            elif op == 'or':
                result = result or right
        return result

    def group(self, items):
        return items[0]

    def comparison(self, items):
        left, op, right = items
        if op == '<': return left < right
        if op == '>': return left > right
        if op == '<=': return left <= right
        if op == '>=': return left >= right
        if op == '==': return left == right
        if op == '!=': return left != right

    def operand(self, items):
        return items[0]

    def attribute(self, items):
        key = ".".join(str(i) for i in items)
        return self.context.get(key, 0)  # default 0 if not found

    def NUMBER(self, token):
        return float(token)

    def action(self, items):
        return str(items[0])

grammar = open("rule_grammar.lark").read()
parser = Lark(grammar, parser='lalr')

# input condition
text = "IF (WS.Age <= 3) AND (PSF > 150) THEN ONE() ELSE TWO()"

# context to evaluate with
context = {
    "WS.Age": 3,
    "PSF": 140
}

# parse and evaluate
tree = parser.parse(text)
transformer = EvalTransformer(context)
result = transformer.transform(tree)

print(result)  # ➜ "TWO"
