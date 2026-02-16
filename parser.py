
from Module import Module
from tokenizer import Tokenizer
from m_ast import *
from tokenizer import TokenType, Token
from dataclasses import dataclass


@dataclass
class Parser:
    tokens: list
    pos: int = 0

    @staticmethod
    def from_file(file_name: str) -> 'Parser':
        with open(file_name, "r") as f:
            return Parser(Tokenizer(f.read(), file_name).tokenize())

    def next_token(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def current_token(self) -> Token:
        if not self.in_range():
            raise Exception(f"Unexpected end of file at {self.tokens[self.pos-1].pos_link()} {len(self.tokens) = } {self.pos = }")
        c = self.tokens[self.pos]
        return c

    def optionally_expect_string(self, value: str) -> bool:
        if self.current_token().value != value:
            return False
        self.next_token()
        return True

    def optionally_expect_token(self, token_type: TokenType) -> bool:
        if self.current_token().type == token_type:
            self.next_token()
            return True
        return False
    def expect_token(self, token_type: TokenType) -> Token:
        if self.current_token().type != token_type:
            raise Exception(f"Expected {token_type}, got {self.current_token().type} at {self.current_token().pos_link()} ")
        return self.next_token()


    def in_range(self) -> bool:
        return self.pos < len(self.tokens)



        

    def parse_term(self) -> Token:
        t = self.next_token()
        if t.value == "if":
            condition = self.parse_expression()
            true_block = self.parse_code_block()
            self.expect_string("else")
            false_block = self.parse_code_block()
            assert type(true_block[-1]) == Provide and type(false_block[-1]) == Provide, f"If statement at {t.pos_link()} must provide a value in both branches"
            return If(condition, true_block, false_block)
        assert t.type in [TokenType.NUMBER, TokenType.STRING, TokenType.IDENTIFIER], f"Expected number, string or identifier, got {t.type} at {t.pos_link()}"
        if t.type != TokenType.IDENTIFIER:
            return t
        expr = t
        while self.in_range():
            match self.current_token().value:
                case ".":
                    self.next_token()
                    return FieldAccess(expr, self.expect_token(TokenType.IDENTIFIER))
                case "(":
                    f = FunctionCall(expr, self.parse_expression_list("(", ")"))
                    if self.optionally_expect_string("catch"):
                        f.catch_block = self.parse_code_block()
                    return f
                case _:
                    break
        return expr
    def expect_string(self, value: str) -> None:
        if self.current_token().value != value:
            raise Exception(f"Expected {value}, got {self.current_token().value} at {self.current_token().pos_link()}")
        self.next_token()
    
    def parse_expression_list(self, start_string: str, end_string: str):
        return self.parse_custom_parse_list(start_string, end_string, self.parse_expression)

    def parse_custom_parse_list(self, start_string: str, end_string: str, parse_func: callable):
        delim = ","
        self.expect_string(start_string)
        args = []
        while self.in_range() and self.current_token().value != end_string:
            print(f'{self.current_token() = }')
            
            args.append(parse_func())
            if not self.optionally_expect_string(delim):
                break
        self.expect_string(end_string)
        return args
    def parse_expression(self):
        print(f'expression at: {self.current_token().pos_link()}')
        
        left = self.parse_term()
        while self.in_range() and self.current_token().type == TokenType.OPERATOR:
            op = self.expect_token(TokenType.OPERATOR)
            right = self.parse_expression()
            left = Operation(left, op, right)
        return left


    def eat_lines(self):
        while self.in_range() and self.current_token().type == TokenType.NEWLINE:
            self.next_token()

    def parse_file(self):
        m = Module("example.py")
        self.eat_lines()
        while self.in_range():
            token = self.expect_token(TokenType.KEYWORD)
            match token.value:
                case "var":
                    v = self.parse_var()
                    m.symbols[v.name] = v
                case "def":
                    f = self.parse_function()
                    assert type(f.name) == Token
                    m.symbols[f.name.value] = f
                case "import":
                    i = self.parse_import()
                    m.symbols[i.name] = i
                case "class":
                    c = self.parse_class()
                    m.symbols[c.name] = c
                case _:
                    raise Exception(f"Unexpected token {token.value} at {token.pos.pos_link()}")
            # self.parse_expression()
            self.eat_lines()
        return m
            

    def parse_code_block(self):
        body = []
        self.expect_string("{")
        self.eat_lines()
        while self.in_range() and self.current_token().value != "}":
            stmt = self.parse_statement()
            body.append(stmt)
            self.eat_lines()
        self.expect_string("}")
        return body
    def parse_assignment(self):
        name = self.expect_token(TokenType.IDENTIFIER)
        self.expect_token(TokenType.ASSIGNMENT)
        value = self.parse_expression()
        return Assignment(name, value)
    def parse_statement(self):
        token = self.current_token()
        if token.value == "^":
            self.next_token()
            return Provide(self.parse_expression())
        if token.type != TokenType.KEYWORD:

            assert token.type == TokenType.IDENTIFIER, f"Expected keyword or identifier, got {token.type} at {token.pos_link()}"

            saved_pos = self.pos
            try:
                return self.parse_assignment()
            except Exception:
                self.pos = saved_pos
                pass
            expr = self.parse_expression()
            assert type(expr) == FunctionCall, f"Expected function call, got {expr} at {expr.pos_link()}"
            return expr
        self.next_token() # consume the keyword
        match token.value:
            case "return":
                if self.optionally_expect_token(TokenType.NEWLINE):
                    return Return(None)
                return Return(self.parse_expression())
            case "var":
                return self.parse_var()
            case "def":
                return self.parse_function()
            case "import":
                return self.parse_import()
            case "while":
                return While(self.parse_expression(), self.parse_code_block())
            case "if":
                i =  If(self.parse_expression(), self.parse_code_block(), None)
                if self.optionally_expect_string("else"):
                    i.else_body = self.parse_code_block()
                return i
            case _:
                raise Exception(f"Unexpected token {token.value} at {token.pos_link()}")
    def parse_var(self):
        name = self.expect_token(TokenType.IDENTIFIER)
        if self.current_token().type == TokenType.IDENTIFIER:
            type_hint = Type(self.expect_token(TokenType.IDENTIFIER))
        else:
            type_hint = None
        if self.optionally_expect_token(TokenType.ASSIGNMENT):
            default_value = self.parse_expression()
        else:
            default_value = None
        assert type_hint or default_value, f"Var (name: {name.value} at {name.pos_link()}) must have type hint or default value"
        return Var(name, type_hint, default_value)
    def parse_param(self):
        return self.parse_var()

    def parse_function(self):
        name = self.expect_token(TokenType.IDENTIFIER)
        params = self.parse_custom_parse_list("(", ")", self.parse_param)
        body = self.parse_code_block()
        return FunctionDef(name, params, body)

    def parse_import(self):
        name = self.expect_token(TokenType.IDENTIFIER)
        return Import(name)


    def parse_class(self):
        c = ClassDef(self.expect_token(TokenType.IDENTIFIER), [], [])
        self.expect_string("{")
        self.eat_lines()
        while self.in_range() and self.current_token().value != "}":
            if self.looks_like_a_function():
                c.methods.append(self.parse_function())
            else:
                c.fields.append(self.parse_field())
            self.eat_lines()
        self.expect_string("}")
        return c

    def parse_field(self):
        return self.parse_var()


    def looks_like_a_function(self):
        return self.current_token().type == TokenType.IDENTIFIER and self.tokens[self.pos + 1].value == "("
        




if __name__ == "__main__":
    parser = Parser.from_file("function_example.py")
    file = parser.parse_file()
    print(f'{file = }')
    
    function_ = file.symbols["add"]
    assert function_.name.value == "add"
    expected_param_names = ["a", "b"]
    assert all(p.name.value == expected_param_names[i] for i, p in enumerate(function_.params))
    assert type(function_.body[0]) == Return

    ############
    parser = Parser.from_file("class_example.py")
    file = parser.parse_file()
    