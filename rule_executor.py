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
            right = items[i + 1]
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


class RuleExecutor:

    def __init__(self, r):

        self.associated_rules = r
        self.excluded_rules = []
        self.grammar = """
        start: "IF" condition "THEN" action ("ELSE" action)?
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
        self.parser = Lark(self.grammar, parser='lalr')

    def _as_context(self,atomic_rule):
        return {x['key']:x['value'] for x in atomic_rule if x.get('dynamic')}

    def execute_rules(self):

        for r in self.associated_rules:
            try:
                print("============START================")
                expression = " ".join([x['key'] for x in r])
                print("EVALUATING EXPRESSION", expression)
                tree = self.parser.parse(expression)
                context = self._as_context(r)
                transformer = EvalTransformer(context)
                result = transformer.transform(tree)
                print("INTERPOLATED VALUE", " ".join([str(x['value']) for x in r]))
                print(result)
                if result == "Exit":
                    print("skipping...")
                    break
                print("============END================")

            except Exception as e:
                print(e)
                self.excluded_rules.append(r)


if __name__ == "__main__":
    r = [
        [
            {"key": "IF", "value": "IF"},
            {"key": "(", "value": "("},
            {"key": "PSR", "value": 2, "dynamic":True},
            {"key": "<", "value": "<"},
            {"key": "constant", "value": 4, "dynamic":True},
            {"key": ")", "value": ")"},
            {"key": "THEN", "value": "THEN"},
            {
                "key": "action1()", "value": "action1()"
            },
            {"key": "ELSE", "value": "ELSE"},
            {
                "key": "action2()", "value": "action2()"
            },
        ],
        [
            {"key": "IF", "value": "IF"},
            {"key": "(", "value": "("},
            {"key": "PSR", "value": 5, "dynamic": True},
            {"key": "<", "value": "<"},
            {"key": "constant", "value": 4, "dynamic": True},
            {"key": "AND", "value": "AND"},
            {"key": "N", "value": 10, "dynamic": True},
            {"key": "<", "value": "<"},
            {"key": "Y", "value": 8, "dynamic": True},
            {"key": ")", "value": ")"},
            {"key": "THEN", "value": "THEN"},
            {
                "key": "GoTo()", "value": "GoTo()"
            },
            {"key": "ELSE", "value": "ELSE"},
            {
                "key": "Exit()", "value": "Exit()"
            },
        ],
        [
            {"key": "IF", "value": "IF"},
            {"key": "(", "value": "("},
            {"key": "PSR", "value": 5,"dynamic":True},
            {"key": "<", "value": "<"},
            {"key": "constant", "value": 4,"dynamic":True},
            {"key": ")", "value": ")"},
            {"key": "THEN", "value": "THEN"},
            {
                "key": "action1()", "value": "action1()"
            },
            {"key": "ELSE", "value": "ELSE"},
            {
                "key": "action2()", "value": "action2()"
            },
        ],
        [
            {"key": "IF", "value": "IF"},
            {"key": "(", "value": "("},
            {"key": "PSR", "value": 5, "dynamic": True},
            {"key": "<", "value": "<"},
            {"key": "constant", "value": 4, "dynamic": True},
            {"key": "AND", "value": "AND"},
            {"key": "N", "value": 10, "dynamic": True},
            {"key": "<", "value": "<"},
            {"key": "Y", "value": 8, "dynamic": True},
            {"key": ")", "value": ")"},
            {"key": "THEN", "value": "THEN"},
            {
                "key": "action1()", "value": "action1()"
            },
            {"key": "ELSE", "value": "ELSE"},
            {
                "key": "action2()", "value": "action2()"
            },
        ],

    ]
    RuleExecutor(r).execute_rules()
