import sys
from antlr4 import *
from dist.ToggleRuleGrammerLexer import ToggleRuleGrammerLexer
from dist.ToggleRuleGrammerParser import ToggleRuleGrammerParser
from dist.ToggleRuleGrammerVisitor import ToggleRuleGrammerVisitor
import json


class ToggleRuleVisitor(ToggleRuleGrammerVisitor):
    def __init__(self):
        self.current_context = None
        self.state = {}

    def visitNumberExpr(self, ctx):
        value = ctx.getText()
        return int(value)

    def visitParenExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitString(self, ctx: ToggleRuleGrammerParser.StringContext):
        return ctx.getText().replace('"', "")

    def visitNumericConstraintExpr(
        self, ctx: ToggleRuleGrammerParser.NumericConstraintExprContext
    ):
        l = self.visit(ctx.left)
        r = self.visit(ctx.right)

        op = ctx.op.text

        operation = {
            "NUM_EQ": lambda: l == r,
            "NUM_LTE": lambda: l <= r,
            "NUM_LT": lambda: l < r,
            "NUM_GT": lambda: l > r,
            "NUM_GTE": lambda: l >= r,
        }
        return operation.get(op, lambda: None)()

    def visitNumericExpr(self, ctx: ToggleRuleGrammerParser.NumericExprContext):
        super().visitNumericExpr(ctx)
        return float(ctx.getText().replace('"', ""))

    def visitStratExpr(self, ctx: ToggleRuleGrammerParser.StratExprContext):
        return super().visitStratExpression(ctx)

    def visitOrExpr(self, ctx: ToggleRuleGrammerParser.OrExprContext):
        return self.visit(ctx.left) or self.visit(ctx.right)

    def visitAndExpr(self, ctx: ToggleRuleGrammerParser.AndExprContext):
        return self.visit(ctx.left) and self.visit(ctx.right)

    def visitContext(self, ctx: ToggleRuleGrammerParser.ContextContext):
        data = self.visit(ctx.data)
        super().visitContext(ctx)
        return float(self.current_context[data])

    def visitContainsConstraintExpr(
        self, ctx: ToggleRuleGrammerParser.ContainsConstraintExprContext
    ):
        l = self.visit(ctx.left)
        r = self.visit(ctx.right)

        op = ctx.op.text

        operation = {
            "IN": lambda: l in r,
            "NOT_IN": lambda: l not in r,
        }
        return operation.get(op, lambda: None)()

    def visitListy(self, ctx: ToggleRuleGrammerParser.ListyContext):
        list_content = ctx.getText()
        if list_content.startswith("\""):
            list_content = list_content[1:]
        if list_content.endswith("\""):
            list_content = list_content[:-2]
        return json.loads(list_content)

    def visitBoolExpr(self, ctx: ToggleRuleGrammerParser.BoolExprContext):
        super().visitBoolExpr(ctx)
        return ctx.getText() == "true"

    def visit_with_state(self, tree, context):
        self.current_context = context
        return self.visit(tree)


def squash_strategy(strategy):
    strategy_name = strategy["name"]
    if strategy_name == "default":
        return "true"
    content = strategy["parameters"]["userIds"]
    return f'contextValue("userId") IN [{content}]'


def squash_toggle(toggle):
    return " OR ".join(
        x for x in [squash_strategy(x) for x in toggle["strategies"]] if x
    )


class ToggleEngine:
    def __init__(self):
        self.evaluators = {}
        self.toggles = {}

    def build_evaluator(self, toggle):
        toggle_rule = squash_toggle(toggle)
        if toggle_rule:
            print("Rule enabled:", toggle_rule)
            return EnabledRule(toggle_rule)
        else:
            print("Rule on:", toggle_rule)
            return AlwaysOnRule()

    def update(self, toggles):
        self.toggles = {toggle["name"]: toggle for toggle in toggles}
        for toggle in toggles:
            self.evaluators[toggle["name"]] = self.build_evaluator(toggle)

    def is_enabled(self, feature_name, context):
        try:

            toggle = self.toggles[feature_name]
            evaluator = self.evaluators[feature_name]
            enabled = toggle["enabled"]
            if not enabled:
                return False
            else:
                return evaluator.eval(context)
        except Exception as e:
            print("---BAD DATA---")
            print(e)
            return False


class AlwaysOnRule:
    def eval(self, _context):
        return True


class EnabledRule:
    def __init__(self, rule):
        self.rule = rule
        data = InputStream(self.rule)

        lexer = ToggleRuleGrammerLexer(data)
        stream = CommonTokenStream(lexer)
        parser = ToggleRuleGrammerParser(stream)

        self.tree = parser.expr()
        self.visitor = ToggleRuleVisitor()

    def eval(self, context):
        return self.visitor.visit_with_state(self.tree, context)
