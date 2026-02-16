from m_ast import *
from tokenizer import Token, TokenType, Pos

def test_operation_repr():
    t1 = Token(TokenType.NUMBER, "1", Pos(1, 1), "test.py")
    t2 = Token(TokenType.NUMBER, "2", Pos(1, 5), "test.py")
    op_token = Token(TokenType.OPERATOR, "+", Pos(1, 3), "test.py")
    op = Operation(t1, op_token, t2)
    assert repr(op) == "(1 + 2)"

def test_function_call_repr():
    func_ref = Token(TokenType.IDENTIFIER, "print", Pos(1, 1), "test.py")
    arg1 = Token(TokenType.STRING, '"hello"', Pos(1, 7), "test.py")
    call = FunctionCall(func_ref, [arg1])
    assert repr(call) == 'print("hello")'

def test_var_repr():
    name = Token(TokenType.IDENTIFIER, "x", Pos(1, 5), "test.py")
    type_name = Token(TokenType.IDENTIFIER, "int", Pos(1, 7), "test.py")
    type_hint = Type(type_name)
    val = Token(TokenType.NUMBER, "10", Pos(1, 13), "test.py")
    v = Var(name, type_hint, val)
    assert repr(v) == "var x int = 10"
