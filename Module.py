from ast import stmt
import re
from m_ast import Provide
from m_ast import Assignment, While, If
from byte_code import Op
from tokenizer import TokenType
from m_ast import ClassDef
from m_ast import Return
from m_ast import Statement
from byte_code import Instruction
from m_ast import Var, FunctionDef, Import, Operation, FunctionCall, Token, Expression  
from dataclasses import dataclass, field

Symbol = Var | FunctionDef | Import

def same_type(a: Token | str, b: Token | str) -> bool:
    if isinstance(a, Token):
         a = a.value
    if isinstance(b, Token):
         b = b.value
    return a == b

@dataclass
class Module:
    name: str
    symbols: dict[str, Symbol] = field(default_factory=dict)
    function_instruction_start_addresses: dict[str, int] = field(default_factory=dict)



    def code_block_can_fail(self, code_block: list[Statement]) -> bool:
        for stmt in code_block:
            match stmt:
                case FunctionCall(function_reference):
                    if function_reference.value == "fail":
                        return True
                case If(condition, body, else_body):
                    return self.code_block_can_fail(body) or (self.code_block_can_fail(else_body) if else_body else False)
                case While(condition, body):
                    return self.code_block_can_fail(body)
        return False

    def function_can_fail(self, function_def: FunctionDef) -> bool:
        return self.code_block_can_fail(function_def.body)

    def infer_block_return_type(self, function_def: FunctionDef) -> str:
        match stmt:
            case If(value):
                return self.get_expression_type(function_def, value)
            case Return(value):
                if value is None:
                    return "void"
                return self.get_expression_type(function_def, value)
    def infer_return_type(self, function_def: FunctionDef) -> str:
        return_type = self.infer_block_return_type(function_def)
        if return_type:
            return return_type
        return "void"




    def get_expression_type(self, function_def: FunctionDef, expression: Expression) -> str:
        match expression:
            case Token(TokenType.NUMBER):
                return "number"
            case Token(TokenType.STRING):
                return "string"
            case Token(TokenType.IDENTIFIER):
                return function_def.get_local_type(self, expression.value)
            case Operation(left, op, right):
                assert same_type(self.get_expression_type(function_def, left), self.get_expression_type(function_def, right)), f"Operands must be of the same type, got {left} at {left.pos_link()} of type {self.get_expression_type(function_def, left)} and {right} at {right.pos_link()} of type {self.get_expression_type(function_def, right)}"
                return self.get_expression_type(function_def, left)
            case FunctionCall(function, args):
                function = self.symbols[function.value]
                assert isinstance(function, FunctionDef)
                assert len(args) == len(function.params)
                for i, arg in enumerate(args):
                    assert same_type(self.get_expression_type(function_def, arg), function.params[i].type_hint), f"Argument {arg} of type {self.get_expression_type(function_def, arg)} at {arg.pos_link()} does not match parameter {function.params[i]} of type {function.params[i].type_hint} at {function.params[i].name.pos_link()}"
                return self.infer_return_type(function)
            case _:
                raise Exception(f"Unexpected expression type {type(expression)}")


    def make_expression_instructions(self, function_def: FunctionDef, expression: Expression) -> list[Instruction]:
        instructions = []
        match expression:
            case Token(TokenType.NUMBER):
                instructions.append(Instruction(Op.LoadConst, [int(expression.value)], expression.pos))
            case Token(TokenType.STRING):
                instructions.append(Instruction(Op.LoadConst, [expression.value], expression.pos))
            case Token(TokenType.IDENTIFIER):
                instructions.append(Instruction(Op.LoadLocal, [function_def.get_local_address(expression.value)], expression.pos))
            case Operation(left, op, right):
                if not same_type(self.get_expression_type(function_def, left), self.get_expression_type(function_def, right)):
                    raise Exception(f"Operands must be of the same type, got {left} at {left.pos_link()} of type {self.get_expression_type(function_def, left)} and {right} at {right.pos_link()} of type {self.get_expression_type(function_def, right)}")
                instructions.extend(self.make_expression_instructions(function_def, left))
                instructions.extend(self.make_expression_instructions(function_def, right))
                left_type = self.get_expression_type(function_def, left)
                if left_type == "number" or left_type.value == "number":
                    instructions.append(Instruction(Op.IntMath, [op.value], op.pos))
                else:
                    assert expression.op == "+"
                    instructions.append(Instruction(Op.StringAdd, [], op.pos))
            case FunctionCall(function_reference, args):
                built_in_functions = ["print", "fail", "unreachable"]
                if function_reference.value in built_in_functions:
                    for arg in args:
                        instructions.extend(self.make_expression_instructions(function_def, arg))
                    instructions.append(Instruction(Op.BuiltinFunctionCall, [function_reference.value, len(args)], expression.function_ref.pos))
                else:
                    function = self.symbols[function_reference.value]
                    assert isinstance(function, FunctionDef)
                    assert len(args) == len(function.params)
                    instructions.append(Instruction(Op.SaveStackStartForNextFunctionCall, []))
                    for i, arg in enumerate(args):
                        assert same_type(self.get_expression_type(function_def, arg), function.params[i].type_hint), f"Argument {arg} of type {self.get_expression_type(function_def, arg)} at {arg.pos_link()} does not match parameter {function.params[i]} of type {function.params[i].type_hint} at {function.params[i].name.pos_link()}"
                    instructions.append(Instruction(Op.SaveStackStartForNextFunctionCall, []))
                    for arg in args:
                        instructions.extend(self.make_expression_instructions(function_def, arg))
                    if self.function_can_fail(function) and not expression.catch_block:
                        raise Exception(f"Function {function_reference.value} can fail but no catch block at {expression.function_ref.pos_link()} {expression.as_is() = }")
                    if not self.function_can_fail(function) and expression.catch_block:
                        raise Exception(f"Function {function_reference.value} cannot fail but catch block at {expression.function_ref.pos_link()}")
                    if expression.catch_block:
                        instructions.append(Instruction(Op.FunctionCall, [self.get_function_address(function_reference.value), len(args), "catch"], expression.function_ref.pos))
                        instructions.append(Instruction(Op.Jump, [1+len(expression.catch_block)], expression.function_ref.pos))
                        instructions.extend(self.make_code_block_instructions(function_def, expression.catch_block))
                    else:
                        instructions.append(Instruction(Op.FunctionCall, [self.get_function_address(function_reference.value), len(args)], expression.function_ref.pos))
            case If():
                instructions.extend(self.compile_if_statement(function_def, expression))
                
            case _:
                raise Exception(f"Unexpected expression type {type(expression)}")
        return instructions





    def make_function_instructions(self, function_def: FunctionDef) -> list[Instruction]:
        instructions = self.make_code_block_instructions(function_def, function_def.body)
        instructions.append(Instruction(Op.VoidReturn, [], function_def.name.pos))
        return instructions


    def make_code_block_instructions(self, function_def: FunctionDef, block: list[Statement]) -> list[Instruction]:
        instructions = []
        for stmt in block:
            match stmt:
                case Return():
                    if stmt.value is None:
                        instructions.append(Instruction(Op.ReturnVoid, [], stmt.pos))
                    else:
                        instructions.extend(self.make_expression_instructions(function_def, stmt.value))
                        instructions.append(Instruction(Op.ReturnWithValue, [], stmt.value.get_pos()))
                case FunctionCall():  
                    instructions.extend(self.make_expression_instructions(function_def, stmt))
                case Assignment(name, value):
                    instructions.extend(self.make_expression_instructions(function_def, value))
                    instructions.append(Instruction(Op.StoreLocal, [function_def.get_local_address(name.value)], name.pos))
                case Var():
                    if stmt.default_value is not None:
                        instructions.extend(self.make_expression_instructions(function_def, stmt.default_value))
                        instructions.append(Instruction(Op.StoreLocal, [function_def.get_local_address(stmt.name.value)], stmt.name.pos))
                case While(condition, body):
                    start_instruction_address = len(instructions)
                    instructions.extend(self.make_expression_instructions(function_def, condition))
                    instructions.append(Instruction(Op.JumpIfFalse, [], condition.get_pos()))
                    first_jump_location = len(instructions)-1
                    block_instructions = self.make_code_block_instructions(function_def, body)
                    instructions.extend(block_instructions)
                    instructions[first_jump_location].args.append(len(block_instructions)+2) # +1 for the jump instruction
                    amount_to_minus_to_get_to_start_instruction_address = len(instructions) - start_instruction_address
                    instructions.append(Instruction(Op.Jump, [-amount_to_minus_to_get_to_start_instruction_address], stmt.condition.get_pos()))
                case If():
                    instructions.extend(self.compile_if_statement(function_def, stmt))
                case Provide():
                    instructions.extend(self.make_expression_instructions(function_def, stmt.value))
                case _:
                    raise Exception(f"Unexpected statement type {type(stmt)}")
        return instructions
    
    def compile_if_statement(self, function_def: FunctionDef, if_node: If):
        instructions = []
        instructions.extend(self.make_expression_instructions(function_def, if_node.condition))
        instructions.append(Instruction(Op.JumpIfFalse, []))
        first_jump_location = len(instructions)-1
        block_instructions = self.make_code_block_instructions(function_def, if_node.body)
        instructions.extend(block_instructions)
        instructions[first_jump_location].args.append(len(block_instructions)+2) # +1 for the jump instruction
        if if_node.else_body:
            instructions.append(Instruction(Op.Jump, []))
            jump_over_else_index = len(instructions)-1
            instructions[first_jump_location].args[0]
            else_instructions = self.make_code_block_instructions(function_def, if_node.else_body)
            instructions.extend(else_instructions)
            instructions[jump_over_else_index].args.append((len(instructions)-jump_over_else_index)+1)
        return instructions

    def get_function_address(self, function_name: str) -> int:
        return self.function_instruction_start_addresses[function_name]


    def compile(self) -> list[Instruction]:
        instructions = []
        for symbol in self.symbols.values():
            match symbol:
                case FunctionDef():
                    f_instructions = self.make_function_instructions(symbol)
                    self.function_instruction_start_addresses[symbol.name.value] = len(instructions)
                    instructions.extend(f_instructions)
                case ClassDef():
                    pass
                case Import():
                    pass
                case _:
                    raise Exception(f"Unexpected symbol type {type(symbol)}")
        return instructions