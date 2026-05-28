import re
from dataclasses import dataclass
from typing import List, Any
from enum import Enum, auto

class TokenType(Enum):
    """Enumeration of all token types in our language"""
    # Keywords
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    VOID = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    
    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()
    
    # Operators
    PLUS = auto()       # +
    MINUS = auto()      # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()     # /
    MODULO = auto()     # %
    EQUAL = auto()      # =
    EQUAL_EQ = auto()   # ==
    NOT_EQ = auto()     # !=
    LESS = auto()       # <
    GREATER = auto()    # >
    LESS_EQ = auto()    # <=
    GREATER_EQ = auto() # >=
    AND = auto()        # &&
    OR = auto()         # ||
    NOT = auto()        # !
    
    # Delimiters
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    SEMICOLON = auto()  # ;
    COMMA = auto()      # ,
    
    # Special
    EOF_TOKEN = auto()
    ERROR = auto()

@dataclass
class Token:
    """Represents a single token in the source code"""
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"

class LexicalAnalyzer:
    """
    =========================================================================
    LEXICAL ANALYZER (TOKENIZER)
    =========================================================================
    Responsible for converting source code into a stream of tokens.
    - Tracks line and column numbers for error reporting
    - Handles comments and whitespace
    =========================================================================
    """
    
    KEYWORDS = {
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'char': TokenType.CHAR,
        'void': TokenType.VOID,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'return': TokenType.RETURN,
    }
    
    OPERATOR_MAP = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '%': TokenType.MODULO,
        '=': TokenType.EQUAL,
        '==': TokenType.EQUAL_EQ,
        '!=': TokenType.NOT_EQ,
        '<': TokenType.LESS,
        '>': TokenType.GREATER,
        '<=': TokenType.LESS_EQ,
        '>=': TokenType.GREATER_EQ,
        '&&': TokenType.AND,
        '||': TokenType.OR,
        '!': TokenType.NOT,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        ';': TokenType.SEMICOLON,
        ',': TokenType.COMMA,
    }
    
    TOKEN_PATTERNS = [
        (r'//[^\n]*', None),                      # Single-line comment
        (r'/\*[\s\S]*?\*/', None),                 # Multi-line comment
        (r'"(?:[^"\\]|\\.)*"', TokenType.STRING),  # String literals
        (r'\d+\.\d+', TokenType.NUMBER),            # Float numbers
        (r'\d+', TokenType.NUMBER),                # Integer numbers
        (r'==|!=|<=|>=|&&|\|\|', TokenType.IDENTIFIER), # Compound operators
        (r'[+\-*/%=<>!&|]', TokenType.IDENTIFIER), # Operators
        (r'[(){}\[\];,]', TokenType.IDENTIFIER),   # Delimiters
        (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER), # Identifiers
        (r'\s+', None),                            # Whitespace
    ]
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def tokenize(self) -> List[Token]:
        print("\n" + "="*70)
        print("PHASE 1: LEXICAL ANALYSIS (TOKENIZATION)")
        print("="*70)
        
        while self.pos < len(self.source_code):
            if self.pos >= len(self.source_code):
                break
                
            matched = False
            
            for pattern, token_type in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.source_code, self.pos)
                
                if match:
                    value = match.group(0)
                    
                    if token_type is not None:
                        if token_type == TokenType.IDENTIFIER:
                            if value in self.KEYWORDS:
                                token_type = self.KEYWORDS[value]
                            elif value in self.OPERATOR_MAP:
                                token_type = self.OPERATOR_MAP[value]
                        
                        if token_type is not None:
                            token = Token(token_type, value, self.line, self.column)
                            self.tokens.append(token)
                    
                    self.pos = match.end()
                    newlines = value.count('\n')
                    if newlines > 0:
                        self.line += newlines
                        last_nl = value.rfind('\n')
                        self.column = len(value) - last_nl
                    else:
                        self.column += len(value)
                        
                    matched = True
                    break
                    
            if not matched:
                self.pos += 1
                self.column += 1
        
        self.tokens.append(Token(TokenType.EOF_TOKEN, '', self.line, self.column))
        self._display_tokens()
        return self.tokens
    
    def _display_tokens(self):
        print(f"\nTotal tokens generated: {len(self.tokens) - 1}")
        print("-" * 70)
        print(f"{'Line':<6} {'Col':<6} {'Type':<20} {'Value':<20}")
        print("-" * 70)
        for token in self.tokens[:-1]:
            print(f"{token.line:<6} {token.column:<6} {token.type.name:<20} {str(token.value):<20}")
        print("-" * 70)
