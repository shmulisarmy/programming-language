import pytest
from tokenizer import Tokenizer, TokenType, Pos

def test_basic_tokens():
    code = "var a = 123"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    assert len(tokens) == 4
    assert tokens[0].type == TokenType.KEYWORD
    assert tokens[0].value == "var"
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "a"
    assert tokens[2].type == TokenType.ASSIGNMENT
    assert tokens[2].value == "="
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == "123"

def test_strings():
    code = '"hello" \'world\''
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == '"hello"'
    assert tokens[1].type == TokenType.STRING
    assert tokens[1].value == "'world'"

def test_operators_and_punctuation():
    code = "+ - * / ( ) { } [ ] , . : ; == != <= >="
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    expected_values = ["+", "-", "*", "/", "(", ")", "{", "}", "[", "]", ",", ".", ":", ";", "==", "!=", "<=", ">="]
    assert [t.value for t in tokens] == expected_values

def test_position_tracking():
    code = "var a = 1\nvar b = 2"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    # var a = 1
    assert tokens[0].pos == Pos(1, 1)  # var
    assert tokens[1].pos == Pos(1, 5)  # a
    assert tokens[2].pos == Pos(1, 7)  # =
    assert tokens[3].pos == Pos(1, 9)  # 1
    
    # NEWLINE
    assert tokens[4].type == TokenType.NEWLINE
    
    # var b = 2
    assert tokens[5].pos == Pos(2, 1)  # var
    assert tokens[6].pos == Pos(2, 5)  # b
    assert tokens[7].pos == Pos(2, 7)  # =
    assert tokens[8].pos == Pos(2, 9)  # 2

def test_comments():
    code = "var a = 1 # this is a comment\nvar b = 2"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    # The tokenizer currently handles comments by matching them but not adding them to tokens list?
    # Let's check tokenizer.py again.
    # kind == "SKIP" calls _advance_position and continues.
    # kind == "COMMENT" is in TOKEN_SPEC but not handled in the loop?
    # Wait, let me check tokenizer.py loop.
    
    # In tokenizer.py:
    # if kind == "NEWLINE": ...
    # elif kind == "NUMBER": ...
    # ...
    # elif kind == "SKIP": ...
    # ...
    # It doesn't have an 'elif kind == "COMMENT"'.
    # So it will fall through to nothing? No, it will just not be added to self.tokens.
    # But it won't call _advance_position either unless it's SKIP.
    # Actually, it will call self._advance_position(value) at the end of the loop if it doesn't 'continue'.
    
    # Let's see:
    # if kind == "NEWLINE": ... (no continue)
    # ...
    # elif kind == "SKIP":
    #     self._advance_position(value)
    #     continue
    # ...
    # self._advance_position(value)
    
    # So for COMMENT, it will not match any if/elif, and then call _advance_position(value).
    # This is correct for skipping but might be cleaner to handle it explicitly.
    
    assert "a" in [t.value for t in tokens]
    assert "b" in [t.value for t in tokens]
    assert "# this is a comment" not in [t.value for t in tokens]

def test_mismatch():
    code = "var a = @"
    tokenizer = Tokenizer(code)
    with pytest.raises(SyntaxError):
        tokenizer.tokenize()
