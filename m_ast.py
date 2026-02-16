from typing import TypeAlias
from ast import Expression
from tokenizer import TokenType, Token
from dataclasses import dataclass



Statement: TypeAlias = "Return | Var | FunctionDef | Import"
    

@dataclass(slots=True)
class Operation :
    left: Token
    op: Token
    right: Token


    def get_pos(self):
        return self.op.pos


    def __repr__(self):
        return f"({self.left.value if type(self.left) == Token else self.left} {self.op.value if self.op.type == TokenType.OPERATOR else self.op} {self.right.value if type(self.right) == Token else self.right})"


@dataclass(slots=True)
class FunctionCall :
    function_ref: Token
    args: list
    catch_block: list[Statement] | None = None


    def as_is(self):
        return f"FunctionCall {self.function_ref.value}({', '.join([str(arg) for arg in self.args])}) {self.catch_block = }"

    def pos_link(self):
        return  self.function_ref.pos


    def __repr__(self):
        args_str = ", ".join([str(arg) for arg in self.args])
        return f"{self.function_ref.value}({args_str})"

@dataclass(slots=True)
class FieldAccess :
    left: Token
    right: Token


    def __repr__(self):
        return f"{self.left.value if type(self.left) == Token else self.left}.{self.right.value if type(self.right) == Token else self.right}"



@dataclass(slots=True)
class If:
    condition: Expression
    body: list[Statement]
    else_body: list[Statement] | None

    def __repr__(self):
        return f"if {self.condition} {self.body} else {self.else_body}"

@dataclass(slots=True)
class While:
    condition: Expression
    body: list[Statement]

    def __repr__(self):
        return f"while {self.condition} {self.body}"


@dataclass(slots=True)
class Return:
    value: Expression | None

    def __repr__(self):
        return f"return {self.value}"


@dataclass(slots=True)
class Type:
    name: Token

    def __repr__(self):
        return self.name.value


@dataclass(slots=True)
class Var:
    name: Token
    type_hint: Type
    default_value: Expression | None

    def __repr__(self):
        return f"var {self.name.value}{' ' + self.type_hint.value if self.type_hint else ''}{' = ' + str(self.default_value) if self.default_value else ''}"


@dataclass(slots=True)
class Assignment:
    name: Token
    value: Expression

    def __repr__(self):
        return f"{self.name.value} = {self.value}"


@dataclass(slots=True)
class Provide:
    value: Expression

    def __repr__(self):
        return f"^ {self.value}"


@dataclass(slots=True)
class FunctionDef:
    name: Token
    params: list[Var]
    body: list[Statement]

    def get_local_type(self, module, name: str) -> Type | None:
        from Module import Module
        for param in self.params:
            if param.name.value == name:
                if param.type_hint is not None:
                    return param.type_hint
                assert param.default_value is not None, f"Default value for parameter {name} is not set"
                return self.get_expression_type(param.default_value)
        for stmt in self.body:
            if isinstance(stmt, Var):
                if stmt.name.value == name:
                    if stmt.type_hint is not None:
                        return stmt.type_hint
                    assert stmt.default_value is not None, f"Default value for variable {name} is not set"
                    return module.get_expression_type(self, stmt.default_value)
        raise Exception(f"Local variable {name} not found")


    def get_local_address(self, name: str) -> int:
        for i, param in enumerate(self.params):
            if param.name.value == name:
                return i
        var_upto = len(self.params) 
        for stmt in self.body:
            if isinstance(stmt, Var):
                if stmt.name.value == name:
                    return var_upto
                var_upto += 1
        raise Exception(f"Local variable {name} not found")

    def __repr__(self):
        return f"def {self.name.value}({', '.join([str(param) for param in self.params])}) {self.body}"


@dataclass(slots=True)
class Import:
    name: Token

    def __repr__(self):
        return f"import {self.name.value}"




@dataclass(slots=True)
class ClassDef:
    name: Token
    fields: list[Var]
    methods: list[FunctionDef]

