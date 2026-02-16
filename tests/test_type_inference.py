import pytest
from tokenizer import Token, TokenType, Pos
from m_ast import Operation, FunctionCall, FunctionDef, Var, Type, Return, Token as ASTToken
from Module import Module

def create_token(kind, value):
    return Token(kind, value, Pos(1, 1), "test.py")

def test_get_expression_type_literals():
    m = Module("test")
    f = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [], [])
    
    # Number literal
    num_token = create_token(TokenType.NUMBER, "123")
    assert m.get_expression_type(f, num_token) == "number"
    
    # String literal
    str_token = create_token(TokenType.STRING, '"hello"')
    assert m.get_expression_type(f, str_token) == "string"

def test_get_expression_type_identifier():
    m = Module("test")
    # Define a variable in the function
    var_name = create_token(TokenType.IDENTIFIER, "x")
    type_hint = Type(create_token(TokenType.IDENTIFIER, "number"))
    v = Var(var_name, type_hint, None)
    
    f = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [v], [])
    
    # Identifier lookup
    id_token = create_token(TokenType.IDENTIFIER, "x")
    # get_local_type returns the Type object or inferred type
    res = m.get_expression_type(f, id_token)
    assert str(res) == "number"

def test_get_expression_type_operation():
    m = Module("test")
    f = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [], [])
    
    t1 = create_token(TokenType.NUMBER, "1")
    t2 = create_token(TokenType.NUMBER, "2")
    op_token = create_token(TokenType.OPERATOR, "+")
    
    op = Operation(t1, op_token, t2)
    assert m.get_expression_type(f, op) == "number"

def test_get_expression_type_operation_mismatch():
    m = Module("test")
    f = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [], [])
    
    t1 = create_token(TokenType.NUMBER, "1")
    t2 = create_token(TokenType.STRING, '"a"')
    op_token = create_token(TokenType.OPERATOR, "+")
    
    op = Operation(t1, op_token, t2)
    with pytest.raises(AssertionError):
        m.get_expression_type(f, op)

def test_get_expression_type_function_call():
    m = Module("test")
    
    # Define a function 'add' that returns 'number'
    # Note: infer_return_type is currently broken but let's see how it behaves
    param_a = Var(create_token(TokenType.IDENTIFIER, "a"), Type(create_token(TokenType.IDENTIFIER, "number")), None)
    # We need to mock the return type inference or ensure it works
    # Currently infer_return_type calls infer_block_return_type which is broken
    
    # Let's try to test a simple case and see if it fails due to the bug
    add_func = FunctionDef(create_token(TokenType.IDENTIFIER, "add"), [param_a], [])
    m.symbols["add"] = add_func
    
    f_main = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [], [])
    call = FunctionCall(create_token(TokenType.IDENTIFIER, "add"), [create_token(TokenType.NUMBER, "1")])
    
    # Add a return statement to 'add' so it can infer return type
    ret_stmt = Return(create_token(TokenType.NUMBER, "0"))
    add_func.body.append(ret_stmt)
    
    res = m.get_expression_type(f_main, call)
    assert res == "number"

def test_get_expression_type_nested_operation():
    m = Module("test")
    f = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [], [])
    
    # (1 + 2) * 3
    t1 = create_token(TokenType.NUMBER, "1")
    t2 = create_token(TokenType.NUMBER, "2")
    t3 = create_token(TokenType.NUMBER, "3")
    op1 = Operation(t1, create_token(TokenType.OPERATOR, "+"), t2)
    op2 = Operation(op1, create_token(TokenType.OPERATOR, "*"), t3)
    
    assert m.get_expression_type(f, op2) == "number"

def test_get_expression_type_string_concatenation():
    m = Module("test")
    f = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [], [])
    
    s1 = create_token(TokenType.STRING, '"hello"')
    s2 = create_token(TokenType.STRING, '" world"')
    op = Operation(s1, create_token(TokenType.OPERATOR, "+"), s2)
    
    assert m.get_expression_type(f, op) == "string"

def test_get_expression_type_complex_function_call():
    m = Module("test")
    
    # def identity(x number) { return x }
    param_x = Var(create_token(TokenType.IDENTIFIER, "x"), Type(create_token(TokenType.IDENTIFIER, "number")), None)
    identity_func = FunctionDef(create_token(TokenType.IDENTIFIER, "identity"), [param_x], [Return(create_token(TokenType.IDENTIFIER, "x"))])
    m.symbols["identity"] = identity_func
    
    f_main = FunctionDef(create_token(TokenType.IDENTIFIER, "main"), [], [])
    
    # identity(1 + 2)
    arg = Operation(create_token(TokenType.NUMBER, "1"), create_token(TokenType.OPERATOR, "+"), create_token(TokenType.NUMBER, "2"))
    call = FunctionCall(create_token(TokenType.IDENTIFIER, "identity"), [arg])
    
    from Module import same_type
    assert same_type(m.get_expression_type(f_main, call), "number")
