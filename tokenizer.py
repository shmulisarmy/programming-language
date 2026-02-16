"""
tokenizer.py

Minimal but structured Python tokenizer.

Each token contains:
- type
- value
- pos (line + column)
- file_name

Supported:
- Keywords
- Identifiers
- Integers & floats
- Strings (single/double quotes, no escapes)
- Operators
- Punctuation
- Newlines

Not supported:
- Indentation (INDENT / DEDENT)
- Comments
- Triple-quoted strings
- Escaped string characters
- Full Python grammar
"""

from colors import blue
import re
from dataclasses import dataclass
from typing import List
from enum import Enum


class TokenType(Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    ID = "ID"
    OP = "OP"
    PUNCT = "PUNCT"
    NEWLINE = "NEWLINE"
    SKIP = "SKIP"
    MISMATCH = "MISMATCH"
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    PUNCTUATION = "PUNCTUATION"
    ASSIGNMENT = "ASSIGNMENT"
    
# ============================================================
# Position
# ============================================================

@dataclass(frozen=True)
class Pos:
    line: int
    col: int

    def pos_link(self) -> str:
        f = "code.py"
        return blue(f"{f}:{self.line}:{self.col}")


# ============================================================
# Token
# ============================================================

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    pos: Pos
    file_name: str
    def get_pos(self):
        return self.pos

    def pos_link(self):
        return blue(f"{self.file_name}:{self.pos.line}:{self.pos.col}")


    def __str__(self):
        return f"{self.value}"


# ============================================================
# Tokenizer
# ============================================================

class Tokenizer:

    KEYWORDS = {
        "if", "else", "elif",
        "for", "while",
        "def", "return",
        "class", "import",
        "from", "as",
        "True", "False", "None",
        "and", "or", "not",
        "in", "is",
        "var", "catch",
    }

    TOKEN_SPEC = [
        ("PROVIDE",     r"\^"),
        ("COMMENT",     r"#.*\n"),
        ("NUMBER",      r"\d+(\.\d+)?"),
        ("STRING",      r"'[^']*'|\"[^\"]*\""),
        ("ID",          r"[A-Za-z_][A-Za-z_0-9]*"),
        ("OP",          r"==|!=|<=|>=|\+|\-|\*|\/|<|>"),
        ("PUNCT",       r"[()\[\]{}.,:;]"),
        ("NEWLINE",     r"\n"),
        ("SKIP",        r"[ \t]+"),
        ("MISMATCH",    r"."),
        ("ASSIGNMENT",  r"="),
    ]

    def __init__(self, code: str, file_name: str = "<stdin>"):
        self.code = code
        self.file_name = file_name
        self.tokens: List[Token] = []
        self.master_pattern = self._build_master_pattern()

        # Position tracking
        self.line = 1
        self.col = 1

    def _build_master_pattern(self):
        parts = []
        for name, pattern in self.TOKEN_SPEC:
            parts.append(f"(?P<{name}>{pattern})")
        return re.compile("|".join(parts))

    def _advance_position(self, text: str):
        for char in text:
            if char == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1

    def tokenize(self) -> List[Token]:
        for match in self.master_pattern.finditer(self.code):
            kind = match.lastgroup
            value = match.group()

            start_line = self.line
            start_col = self.col


            if value == "=":
                self.tokens.append(
                    Token(TokenType.ASSIGNMENT, value, Pos(start_line, start_col), self.file_name)
                )
                self._advance_position(value)
                continue

            if kind == "NEWLINE":
                self.tokens.append(
                    Token(TokenType.NEWLINE, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "NUMBER":
                self.tokens.append(
                    Token(TokenType.NUMBER, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "STRING":
                self.tokens.append(
                    Token(TokenType.STRING, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "ID":
                token_type = TokenType.KEYWORD if value in self.KEYWORDS else TokenType.IDENTIFIER
                self.tokens.append(
                    Token(token_type, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "OP":
                self.tokens.append(
                    Token(TokenType.OPERATOR, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "PUNCT":
                self.tokens.append(
                    Token(TokenType.PUNCTUATION, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "ASSIGNMENT":
                self.tokens.append(
                    Token(TokenType.ASSIGNMENT, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "PROVIDE":
                self.tokens.append(
                    Token(TokenType.PUNCTUATION, value, Pos(start_line, start_col), self.file_name)
                )

            elif kind == "SKIP":
                self._advance_position(value)
                continue

            elif kind == "MISMATCH":
                raise SyntaxError(
                    f"{self.file_name}:{start_line}:{start_col} "
                    f"Unexpected character {value!r}"
                )

            self._advance_position(value)

        return self.tokens


# ============================================================
# CLI Test Entry
# ============================================================




if __name__ == "__main__":
    tokenizer = Tokenizer("var a = 1", "example.py")
    expected_types = [TokenType.KEYWORD, TokenType.IDENTIFIER, TokenType.ASSIGNMENT, TokenType.NUMBER]
    tokens = tokenizer.tokenize()
    for i, token in enumerate(tokens):
        assert token.type == expected_types[i], f"{i = } Expected {expected_types[i]}, got {token.type} ({token.value})" 
    print("All tests passed!")