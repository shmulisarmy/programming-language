
from dataclasses import dataclass
from byte_code import Op
from colors import yellow
from Module import Module
from parser import Parser












@dataclass
class Address:
    offset: int
    is_global: bool

    



@dataclass
class StackFrame:
    return_address: int
    local_stack_top: int


def execute_instructions(instructions: list[Instruction], pc: int):
    stack = [0] * 10
    frames = [
        StackFrame(len(instructions), 0)
    ]  
    saved_stack_start_for_next_function_calls = []  
    while pc < len(instructions):
        instruction = instructions[pc]
        # print(f'pc: {pc} instruction: {instruction.op} {instruction.args} at {instruction.pos.pos_link()} generated at {instruction.generated_at}')
        # print(f'{stack = }')
        
        match instruction.op:
            case Op.LoadConst:
                stack.append(instruction.args[0])
            case Op.IntMath:
                b = stack.pop()
                a = stack.pop()
                match instruction.args[0]:
                    case "+":
                        stack.append(a + b)
                    case "-":
                        stack.append(a - b)
                    case "*":
                        stack.append(a * b)
                    case "/":
                        stack.append(a / b)
                    case "<":
                        stack.append(a < b)
                    case ">":
                        stack.append(a > b)
                    case "==":
                        stack.append(a == b)
                    case "!=":
                        stack.append(a != b)
                    case _:
                        raise Exception(f"Unknown op {instruction.args[0]}")
            case Op.StringAdd:
                raise Exception("StringAdd not implemented")
            case Op.SaveStackStartForNextFunctionCall:
                saved_stack_start_for_next_function_calls.append(len(stack))
            case Op.BuiltinFunctionCall:
                function_name = instruction.args[0]
                arg_count = instruction.args[1]
                # print(f'{arg_count = }')
                
                args = stack[-arg_count:] if arg_count > 0 else []
                # print(f'{stack = }')
                
                if arg_count > 0:
                    stack = stack[:-arg_count]
                # print(f'{stack = }')
                match function_name:
                    case "print":
                        print(yellow(args))
                    case "unreachable":
                        raise Exception("unreachable")
                    case "fail":
                        print(f'failing with {args}')
                        last_frame = frames.pop()
                        stack = stack[:last_frame.local_stack_top]
                        pc = last_frame.return_address+1 # skip the jump that goes over the catch block
                        continue
                        # raise Exception("fail")
            case Op.FunctionCall:
                start_address = instruction.args[0]
                frames.append(StackFrame(pc+1, saved_stack_start_for_next_function_calls.pop()))
                pc = start_address                
                continue
            case Op.ReturnWithValue:

                print(f'{stack = }')
                print(f'{frames = }')
                
                value = stack.pop()
                pc = frames[-1].return_address
                stack = stack[:frames[-1].local_stack_top]
                frames.pop()
                stack.append(value)

                print(f'{stack = }')
                continue
            case Op.VoidReturn:
                print(f'{frames = }')

                pc = frames[-1].return_address
                stack = stack[:frames[-1].local_stack_top]
                frames.pop()
                continue
            case Op.LoadLocal:
                # print(f'{frames = }')
                # print(f'{instruction.args = }')
                # print(f'{stack = }')
                
                stack.append(stack[frames[-1].local_stack_top + instruction.args[0]])
            case Op.StoreLocal:
                stack[frames[-1].local_stack_top + instruction.args[0]] = stack.pop()
            case Op.JumpIfFalse:
                jump_by = instruction.args[0]
                if not stack.pop():
                    pc += jump_by
                    continue
            case Op.Jump:
                jump_by = instruction.args[0]
                pc += jump_by
                continue
            case _:
                raise Exception(f"Unknown op {instruction.op}")
            
        pc += 1


if __name__ == "__main__":
    # with open("code.py", "r") as f:
    #     tokens = Tokenizer(f.read()).tokenize()
    #     print(f'tokens:')
    #     for token in tokens:
    #         print(f"\t{token}")
    parser = Parser.from_file("code.py")
    module: Module = parser.parse_file()

    instructions = module.compile()
    print(f'instructions:')
    for instruction in instructions:
        print(instruction)
    
    execute_instructions(instructions, module.function_instruction_start_addresses["main"])
    
