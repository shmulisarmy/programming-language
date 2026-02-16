import pytest
from tokenizer import Tokenizer
from parser import Parser
from m_ast import *

def parse_code(code):
    tokens = Tokenizer(code).tokenize()
    return Parser(tokens)

def test_parse_var():
    code = "var x int = 10"
    parser = parse_code(code)
    parser.expect_string("var")
    v = parser.parse_var()
    assert v.name.value == "x"
    assert v.type_hint.name.value == "int"
    assert v.default_value.value == "10"

def test_parse_expression():
    code = "1 + 2 * 3"
    parser = parse_code(code)
    expr = parser.parse_expression()
    # Note: The current parser seems to handle precedence by recursion but let's see
    # parse_expression calls parse_term, then loops for operators.
    # It's a simple left-to-right parser for now?
    # 1 + 2 * 3 -> (1 + (2 * 3)) or ((1 + 2) * 3)?
    # Looking at parse_expression:
    # left = self.parse_term()
    # while ...:
    #   op = ...
    #   right = self.parse_expression()
    #   left = Operation(left, op, right)
    # This is right-associative: 1 + (2 * 3)
    assert isinstance(expr, Operation)
    assert expr.left.value == "1"
    assert expr.op.value == "+"
    assert isinstance(expr.right, Operation)
    assert expr.right.left.value == "2"
    assert expr.right.op.value == "*"
    assert expr.right.right.value == "3"

def test_parse_function_def():
    code = """
def add(a int, b int) {
    return a + b
}
"""
    parser = parse_code(code)
    # Need to eat the newline first if there is one
    parser.eat_lines()
    parser.expect_string("def")
    f = parser.parse_function()
    assert f.name.value == "add"
    assert len(f.params) == 2
    assert f.params[0].name.value == "a"
    assert f.params[1].name.value == "b"
    assert isinstance(f.body[0], Return)

def test_parse_if_statement():
    code = """
if x > 0 {
    return 1
} else {
    return 0
}
"""
    # Note: parse_statement handles 'if'
    parser = parse_code(code)
    parser.eat_lines()
    stmt = parser.parse_statement()
    assert isinstance(stmt, If)
    assert isinstance(stmt.condition, Operation)
    assert len(stmt.body) == 1
    assert isinstance(stmt.body[0], Return)
    assert len(stmt.else_body) == 1
    assert isinstance(stmt.else_body[0], Return)

def test_parse_while_statement():
    code = """
while x < 10 {
    x = x + 1
}
"""
    parser = parse_code(code)
    parser.eat_lines()
    stmt = parser.parse_statement()
    assert isinstance(stmt, While)
    assert isinstance(stmt.condition, Operation)
    assert len(stmt.body) == 1
    assert isinstance(stmt.body[0], Assignment)
