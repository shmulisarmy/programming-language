
import inspect
from colors import blue
from tokenizer import Pos
from dataclasses import field
from enum import Enum, auto
from dataclasses import dataclass

class Op(Enum):
    IntMath = auto()
    StringAdd = auto()
    FunctionCall = auto()
    ReturnWithValue = auto()
    VoidReturn = auto()
    Jump = auto()
    JumpIfFalse = auto()
    JumpIfTrue = auto()
    LoadGlobal = auto()
    StoreGlobal = auto()
    LoadLocal = auto()
    StoreLocal = auto()
    LoadConst = auto()

    LoadAddress = auto()
    OffsetTopAddress = auto()
    StoreAddress = auto()
    LoadFromAddress = auto()
    SaveStackStartForNextFunctionCall = auto()
    BuiltinFunctionCall = auto()
    
    
    


    

def get_caller_file_and_line():
    stack = inspect.stack()
    return stack[2].filename, stack[2].lineno

@dataclass
class Instruction:
    op: Op
    args: list[int] = field(default_factory=list)
    pos: Pos = field(default_factory=lambda: Pos(0, 0))
    generated_at: tuple[str, int] = field(default_factory=get_caller_file_and_line)

    