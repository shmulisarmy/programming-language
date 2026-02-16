import pytest
from tokenizer import Tokenizer
from parser import Parser
from Module import Module, same_type
from m_ast import FunctionDef, Return, Assignment, Var

def parse_to_module(code):
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    return parser.parse_file()

def test_e2e_literal_inference():
    code = """
    def main() {
        return 123
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    ret_stmt = main_func.body[0]
    
    expr_type = module.get_expression_type(main_func, ret_stmt.value)
    assert same_type(expr_type, "number")

def test_e2e_variable_inference():
    code = """
    def main(x number) {
        return x
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    ret_stmt = main_func.body[0]
    
    expr_type = module.get_expression_type(main_func, ret_stmt.value)
    assert same_type(expr_type, "number")

def test_e2e_operation_inference():
    code = """
    def main() {
        return 1 + 2 * 3
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    ret_stmt = main_func.body[0]
    
    expr_type = module.get_expression_type(main_func, ret_stmt.value)
    assert same_type(expr_type, "number")

def test_e2e_string_inference():
    code = """
    def main() {
        return "hello" + " world"
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    ret_stmt = main_func.body[0]
    
    expr_type = module.get_expression_type(main_func, ret_stmt.value)
    assert same_type(expr_type, "string")

def test_e2e_function_call_inference():
    code = """
    def add(a number, b number) {
        return a + b
    }
    def main() {
        return add(1, 2)
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    ret_stmt = main_func.body[0]
    
    expr_type = module.get_expression_type(main_func, ret_stmt.value)
    assert same_type(expr_type, "number")

def test_e2e_local_var_inference():
    code = """
    def main() {
        var x number = 10
        return x
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    # body[0] is Var, body[1] is Return
    ret_stmt = main_func.body[1]
    
    expr_type = module.get_expression_type(main_func, ret_stmt.value)
    assert same_type(expr_type, "number")

def test_e2e_mismatched_types_error():
    code = """
    def main() {
        return 1 + "string"
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    ret_stmt = main_func.body[0]
    
    with pytest.raises(AssertionError):
        module.get_expression_type(main_func, ret_stmt.value)

def test_e2e_nested_function_calls():
    code = """
    def double(n number) {
        return n * 2
    }
    def main() {
        return double(double(5))
    }
    """
    module = parse_to_module(code)
    main_func = module.symbols["main"]
    ret_stmt = main_func.body[0]
    
    expr_type = module.get_expression_type(main_func, ret_stmt.value)
    assert same_type(expr_type, "number")
