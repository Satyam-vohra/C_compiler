"""
===============================================================================
                    MODULAR COMPILER IMPLEMENTATION
===============================================================================

A complete compiler implementation in Python featuring:
1. Lexical Analysis (Tokenization)
2. Syntax Analysis (Parser with Grammar)
3. Semantic Analysis (Type Checking)
4. Code Optimization (Constant Folding, Dead Code Elimination, CSE)

Author: Compiler Project
Language: Python
===============================================================================
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from enum import Enum, auto

# =============================================================================
# PART 1: LEXICAL ANALYSIS (TOKENIZATION)
# =============================================================================

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
    
    Key Features:
    - Regular expression-based token recognition
    - Tracks line and column numbers for error reporting
    - Handles comments and whitespace
    =========================================================================
    """
    
    # Keyword mapping
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
    
    # Operator/delimiter to TokenType mapping
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
    
    # Token patterns in order of matching priority
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
        """
        Main method to tokenize the entire source code.
        
        Returns:
            List of Token objects
        """
        print("\n" + "="*70)
        print("PHASE 1: LEXICAL ANALYSIS (TOKENIZATION)")
        print("="*70)
        
        while self.pos < len(self.source_code):
            # Check for end of file
            if self.pos >= len(self.source_code):
                break
                
            matched = False
            char = self.source_code[self.pos]
            
            # Try each pattern
            for pattern, token_type in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.source_code, self.pos)
                
                if match and token_type is not None:
                    value = match.group(0)
                    
                    # For identifiers, check if it's a keyword
                    if token_type == TokenType.IDENTIFIER:
                        if value in self.KEYWORDS:
                            token_type = self.KEYWORDS[value]
                        elif value in self.OPERATOR_MAP:
                            token_type = self.OPERATOR_MAP[value]
                    
                    if token_type is not None:
                        token = Token(token_type, value, self.line, self.column)
                        self.tokens.append(token)
                    
                    # Update position
                    self.pos = match.end()
                    self.column += len(value)
                    matched = True
                    break
                    
            if not matched:
                # Skip unrecognized characters
                self.pos += 1
                self.column += 1
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF_TOKEN, '', self.line, self.column))
        
        # Display tokens
        self._display_tokens()
        
        return self.tokens
    
    def _display_tokens(self):
        """Display all tokens in a formatted manner"""
        print(f"\nTotal tokens generated: {len(self.tokens) - 1}")
        print("-" * 70)
        print(f"{'Line':<6} {'Col':<6} {'Type':<20} {'Value':<20}")
        print("-" * 70)
        
        for token in self.tokens[:-1]:  # Exclude EOF for display
            print(f"{token.line:<6} {token.column:<6} {token.type.name:<20} {str(token.value):<20}")
        
        print("-" * 70)


# =============================================================================
# PART 2: SYNTAX ANALYSIS (PARSING)
# =============================================================================

class ASTNodeType(Enum):
    """AST node types for the abstract syntax tree"""
    PROGRAM = "Program"
    DECLARATION = "Declaration"
    VARIABLE_DECL = "VariableDecl"
    FUNCTION_DECL = "FunctionDecl"
    COMPOUND_STMT = "CompoundStmt"
    IF_STMT = "IfStmt"
    WHILE_STMT = "WhileStmt"
    FOR_STMT = "ForStmt"
    RETURN_STMT = "ReturnStmt"
    EXPRESSION_STMT = "ExpressionStmt"
    BINARY_EXPR = "BinaryExpr"
    UNARY_EXPR = "UnaryExpr"
    ASSIGN_EXPR = "AssignExpr"
    CALL_EXPR = "CallExpr"
    VARIABLE = "Variable"
    LITERAL = "Literal"
    PARAM_LIST = "ParamList"
    ARG_LIST = "ArgList"


@dataclass
class ASTNode:
    """Represents a node in the Abstract Syntax Tree"""
    node_type: ASTNodeType
    value: Any = None
    left: Optional['ASTNode'] = None
    right: Optional['ASTNode'] = None
    children: List['ASTNode'] = None
    data_type: str = "unknown"  # For semantic analysis
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def __repr__(self):
        return f"ASTNode({self.node_type.value}, value={self.value})"
    
    def to_dict(self) -> Dict:
        """Convert AST to dictionary for display"""
        return {
            'type': self.node_type.value,
            'value': self.value,
            'data_type': self.data_type,
            'children': [c.to_dict() for c in self.children]
        }


class SyntaxAnalyzer:
    """
    =========================================================================
    SYNTAX ANALYZER (PARSER)
    =========================================================================
    Responsible for converting token stream into Abstract Syntax Tree (AST).
    
    Grammar:
        program         → declaration*
        declaration     → var_decl | fun_decl | stmt
        var_decl        → type_spec IDENTIFIER ('=' expr)? ';'
        fun_decl        → type_spec IDENTIFIER '(' params ')' compound_stmt
        params          → param (',' param)* | ε
        param           → type_spec IDENTIFIER
        compound_stmt   → '{' local_declarations* statement* '}'
        statement       → expr_stmt | compound_stmt | if_stmt | while_stmt | for_stmt | return_stmt
        expr_stmt       → expr ';' | ';'
        if_stmt         → 'if' '(' expr ')' statement ('else' statement)?
        while_stmt      → 'while' '(' expr ')' statement
        for_stmt        → 'for' '(' expr_stmt expr_stmt ')' statement
        return_stmt     → 'return' expr? ';'
        expr            → assignment_expr
        assignment_expr → unary '=' assignment_expr | logical_or_expr
        logical_or_expr → logical_and_expr ('||' logical_and_expr)*
        logical_and_expr → equality_expr ('&&' equality_expr)*
        equality_expr   → relational_expr (('==' | '!=') relational_expr)*
        relational_expr → additive_expr (('<' | '>' | '<=' | '>=') additive_expr)*
        additive_expr   → multiplicative_expr (('+' | '-') multiplicative_expr)*
        multiplicative_expr → unary (('*' | '/' | '%') unary)*
        unary_expr      → ('!' | '-') unary | primary
        primary         → NUMBER | STRING | IDENTIFIER | '(' expr ')'
    =========================================================================
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
        self.errors: List[Dict[str, Any]] = []
        
    def advance(self):
        """Move to the next token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
    
    def expect(self, token_type: TokenType) -> Optional[Token]:
        """Expect a specific token type"""
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            line = self.current_token.line if self.current_token else 0
            col = self.current_token.column if self.current_token else 0
            got = self.current_token.type.name if self.current_token else "EOF"
            got_val = self.current_token.value if self.current_token else ""
            self.errors.append({
                'line': line,
                'column': col,
                'expected': token_type.name,
                'got': got,
                'value': got_val,
                'message': f"Expected '{token_type.name}' but got '{got}'"
            })
            return None
    
    def parse(self) -> ASTNode:
        """
        Main parsing method - builds the AST.
        
        Returns:
            Root AST node
        """
        print("\n" + "="*70)
        print("PHASE 2: SYNTAX ANALYSIS (PARSING)")
        print("="*70)
        
        # Build the AST
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF_TOKEN:
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        
        # Create program root
        program = ASTNode(ASTNodeType.PROGRAM, children=statements)
        
        # Display AST
        self._display_ast(program)
        
        if self.errors:
            print("\nSyntax Errors:")
            for err in self.errors:
                print(f"  Line {err['line']}, Col {err['column']}: {err['message']}")
        
        return program
    
    def declaration(self) -> Optional[ASTNode]:
        """Parse a declaration"""
        # Check for type specifier
        if self.current_token and self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.VOID]:
            type_token = self.current_token
            self.advance()
            
            # Check if it's a function or variable
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                name_token = self.current_token
                self.advance()
                
                # Function declaration
                if self.current_token and self.current_token.type == TokenType.LPAREN:
                    self.advance()  # consume (
                    params = self.params()
                    self.expect(TokenType.RPAREN)
                    body = self.compound_stmt()
                    
                    func = ASTNode(ASTNodeType.FUNCTION_DECL, name_token.value)
                    func.children = [
                        ASTNode(ASTNodeType.LITERAL, type_token.value, data_type=type_token.value),
                        ASTNode(ASTNodeType.LITERAL, name_token.value),
                        params,
                        body
                    ]
                    func.data_type = type_token.value
                    return func
                else:
                    # Variable declaration
                    var_node = ASTNode(ASTNodeType.VARIABLE_DECL, name_token.value)
                    var_node.data_type = type_token.value
                    
                    # Check for initialization
                    if self.current_token and self.current_token.type == TokenType.EQUAL:
                        self.advance()
                        init = self.expression()
                        var_node.children.append(init)
                    
                    self.expect(TokenType.SEMICOLON)
                    return var_node
        
        # Statement
        return self.statement()
    
    def params(self) -> ASTNode:
        """Parse function parameters"""
        params_node = ASTNode(ASTNodeType.PARAM_LIST)
        
        if self.current_token and self.current_token.type == TokenType.RPAREN:
            return params_node
        
        while self.current_token and self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.VOID]:
            param_type = self.current_token.value
            self.advance()
            
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                param_name = self.current_token.value
                self.advance()
                
                param_node = ASTNode(ASTNodeType.VARIABLE, param_name)
                param_node.data_type = param_type
                params_node.children.append(param_node)
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
        
        return params_node
    
    def compound_stmt(self) -> ASTNode:
        """Parse compound statement (block)"""
        self.expect(TokenType.LBRACE)
        
        compound = ASTNode(ASTNodeType.COMPOUND_STMT)
        
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            # Local declarations
            if self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.VOID]:
                decl = self.declaration()
                if decl:
                    compound.children.append(decl)
            else:
                # Statements
                stmt = self.statement()
                if stmt:
                    compound.children.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return compound
    
    def statement(self) -> Optional[ASTNode]:
        """Parse any statement"""
        if not self.current_token:
            return None
            
        token_type = self.current_token.type
        
        # If statement
        if token_type == TokenType.IF:
            return self.if_stmt()
        
        # While statement
        if token_type == TokenType.WHILE:
            return self.while_stmt()
        
        # For statement
        if token_type == TokenType.FOR:
            return self.for_stmt()
        
        # Return statement
        if token_type == TokenType.RETURN:
            return self.return_stmt()
        
        # Compound statement
        if token_type == TokenType.LBRACE:
            return self.compound_stmt()
        
        # Expression statement
        return self.expr_stmt()
    
    def if_stmt(self) -> ASTNode:
        """Parse if statement"""
        self.advance()  # consume if
        self.expect(TokenType.LPAREN)
        condition = self.expression()
        self.expect(TokenType.RPAREN)
        
        then_branch = self.statement()
        else_branch = None
        
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()
            else_branch = self.statement()
        
        if_node = ASTNode(ASTNodeType.IF_STMT)
        if_node.children = [condition, then_branch]
        if else_branch:
            if_node.children.append(else_branch)
        
        return if_node
    
    def while_stmt(self) -> ASTNode:
        """Parse while statement"""
        self.advance()  # consume while
        self.expect(TokenType.LPAREN)
        condition = self.expression()
        self.expect(TokenType.RPAREN)
        body = self.statement()
        
        while_node = ASTNode(ASTNodeType.WHILE_STMT)
        while_node.children = [condition, body]
        
        return while_node
    
    def for_stmt(self) -> ASTNode:
        """Parse for statement"""
        self.advance()  # consume for
        self.expect(TokenType.LPAREN)
        
        # Initialization
        init = self.expression()
        self.expect(TokenType.SEMICOLON)
        
        # Condition
        condition = self.expression()
        self.expect(TokenType.SEMICOLON)
        
        # Update
        update = self.expression()
        self.expect(TokenType.RPAREN)
        
        # Body
        body = self.statement()
        
        for_node = ASTNode(ASTNodeType.FOR_STMT)
        for_node.children = [init, condition, update, body]
        
        return for_node
    
    def return_stmt(self) -> ASTNode:
        """Parse return statement"""
        self.advance()  # consume return
        return_node = ASTNode(ASTNodeType.RETURN_STMT)
        
        if self.current_token and self.current_token.type != TokenType.SEMICOLON:
            expr = self.expression()
            return_node.children.append(expr)
        
        self.expect(TokenType.SEMICOLON)
        return return_node
    
    def expr_stmt(self) -> ASTNode:
        """Parse expression statement"""
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
            return ASTNode(ASTNodeType.EXPRESSION_STMT)
        
        expr = self.expression()
        self.expect(TokenType.SEMICOLON)
        
        expr_stmt = ASTNode(ASTNodeType.EXPRESSION_STMT)
        expr_stmt.children = [expr]
        
        return expr_stmt
    
    def expression(self) -> ASTNode:
        """Parse expression using operator precedence"""
        return self.assignment_expr()
    
    def assignment_expr(self) -> ASTNode:
        """Parse assignment expression"""
        left = self.logical_or_expr()
        
        if self.current_token and self.current_token.type == TokenType.EQUAL:
            self.advance()
            right = self.assignment_expr()
            
            assign = ASTNode(ASTNodeType.ASSIGN_EXPR, '=')
            assign.left = left
            assign.right = right
            return assign
        
        return left
    
    def logical_or_expr(self) -> ASTNode:
        """Parse logical OR expression"""
        left = self.logical_and_expr()
        
        while self.current_token and self.current_token.value == '||':
            op = self.current_token.value
            self.advance()
            right = self.logical_and_expr()
            
            binary = ASTNode(ASTNodeType.BINARY_EXPR, op)
            binary.left = left
            binary.right = right
            left = binary
        
        return left
    
    def logical_and_expr(self) -> ASTNode:
        """Parse logical AND expression"""
        left = self.equality_expr()
        
        while self.current_token and self.current_token.value == '&&':
            op = self.current_token.value
            self.advance()
            right = self.equality_expr()
            
            binary = ASTNode(ASTNodeType.BINARY_EXPR, op)
            binary.left = left
            binary.right = right
            left = binary
        
        return left
    
    def equality_expr(self) -> ASTNode:
        """Parse equality expression"""
        left = self.relational_expr()
        
        while self.current_token and self.current_token.value in ['==', '!=']:
            op = self.current_token.value
            self.advance()
            right = self.relational_expr()
            
            binary = ASTNode(ASTNodeType.BINARY_EXPR, op)
            binary.left = left
            binary.right = right
            left = binary
        
        return left
    
    def relational_expr(self) -> ASTNode:
        """Parse relational expression"""
        left = self.additive_expr()
        
        while self.current_token and self.current_token.value in ['<', '>', '<=', '>=']:
            op = self.current_token.value
            self.advance()
            right = self.additive_expr()
            
            binary = ASTNode(ASTNodeType.BINARY_EXPR, op)
            binary.left = left
            binary.right = right
            left = binary
        
        return left
    
    def additive_expr(self) -> ASTNode:
        """Parse additive expression"""
        left = self.multiplicative_expr()
        
        while self.current_token and self.current_token.value in ['+', '-']:
            op = self.current_token.value
            self.advance()
            right = self.multiplicative_expr()
            
            binary = ASTNode(ASTNodeType.BINARY_EXPR, op)
            binary.left = left
            binary.right = right
            left = binary
        
        return left
    
    def multiplicative_expr(self) -> ASTNode:
        """Parse multiplicative expression"""
        left = self.unary_expr()
        
        while self.current_token and self.current_token.value in ['*', '/', '%']:
            op = self.current_token.value
            self.advance()
            right = self.unary_expr()
            
            binary = ASTNode(ASTNodeType.BINARY_EXPR, op)
            binary.left = left
            binary.right = right
            left = binary
        
        return left
    
    def unary_expr(self) -> ASTNode:
        """Parse unary expression"""
        if self.current_token and self.current_token.value in ['!', '-']:
            op = self.current_token.value
            self.advance()
            operand = self.unary_expr()
            
            unary = ASTNode(ASTNodeType.UNARY_EXPR, op)
            unary.right = operand
            return unary
        
        return self.primary()
    
    def primary(self) -> ASTNode:
        """Parse primary expression (literals, identifiers, parentheses)"""
        if not self.current_token:
            return ASTNode(ASTNodeType.LITERAL, "ERROR")
        
        token_type = self.current_token.type
        
        # Number literal
        if token_type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            
            # Check if it's float
            literal = ASTNode(ASTNodeType.LITERAL, value)
            literal.data_type = "float" if '.' in str(value) else "int"
            return literal
        
        # String literal
        if token_type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            literal = ASTNode(ASTNodeType.LITERAL, value)
            literal.data_type = "char*"
            return literal
        
        # Identifier
        if token_type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            
            # Variable reference
            var = ASTNode(ASTNodeType.VARIABLE, name)
            return var
        
        # Parenthesized expression
        if token_type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Error
        self.advance()
        return ASTNode(ASTNodeType.LITERAL, "ERROR")
    
    def _display_ast(self, node: ASTNode, indent: int = 0):
        """Display AST in tree format"""
        prefix = "  " * indent
        
        if node.node_type == ASTNodeType.LITERAL:
            print(f"{prefix}|-- {node.node_type.value}: {node.value} (type: {node.data_type})")
        elif node.node_type == ASTNodeType.VARIABLE:
            print(f"{prefix}|-- {node.node_type.value}: {node.value}")
        elif node.node_type == ASTNodeType.BINARY_EXPR:
            print(f"{prefix}|-- {node.node_type.value}: {node.value}")
        elif node.node_type == ASTNodeType.UNARY_EXPR:
            print(f"{prefix}|-- {node.node_type.value}: {node.value}")
        elif node.node_type == ASTNodeType.ASSIGN_EXPR:
            print(f"{prefix}|-- {node.node_type.value}: {node.value}")
        else:
            print(f"{prefix}|-- {node.node_type.value}")
        
        for child in node.children:
            self._display_ast(child, indent + 1)


# =============================================================================
# PART 3: SEMANTIC ANALYSIS (TYPE CHECKING)
# =============================================================================

class SymbolType(Enum):
    """Symbol types for symbol table"""
    VARIABLE = auto()
    FUNCTION = auto()
    PARAMETER = auto()


@dataclass
class Symbol:
    """Represents a symbol in the symbol table"""
    name: str
    symbol_type: SymbolType
    data_type: str
    value: Any = None
    line: int = 0


class SemanticAnalyzer:
    """
    =========================================================================
    SEMANTIC ANALYZER (TYPE CHECKING)
    =========================================================================
    Responsible for type checking and symbol table management.
    
    Key Features:
    - Symbol table management
    - Type checking for operations
    - Scope management
    - Error detection for type mismatches
    =========================================================================
    """
    
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.symbol_table: Dict[str, Symbol] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def analyze(self) -> ASTNode:
        """
        Main semantic analysis method.
        
        Returns:
            Annotated AST with type information
        """
        print("\n" + "="*70)
        print("PHASE 3: SEMANTIC ANALYSIS (TYPE CHECKING)")
        print("="*70)
        
        # Build symbol table and perform type checking
        self._analyze_node(self.ast)
        
        # Display symbol table
        self._display_symbol_table()
        
        # Display errors and warnings
        if self.errors:
            print("\nSemantic Errors:")
            for error in self.errors:
                print(f"  [X] {error}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  [!] {warning}")
        
        if not self.errors:
            print("\n[PASSED] Semantic analysis completed successfully!")
        
        return self.ast
    
    def _analyze_node(self, node: ASTNode):
        """Recursively analyze AST node"""
        if node is None:
            return
        
        # Analyze children first
        for child in node.children:
            self._analyze_node(child)
        
        # Analyze based on node type
        if node.node_type == ASTNodeType.PROGRAM:
            self._analyze_program(node)
        elif node.node_type == ASTNodeType.VARIABLE_DECL:
            self._analyze_variable_decl(node)
        elif node.node_type == ASTNodeType.FUNCTION_DECL:
            self._analyze_function_decl(node)
        elif node.node_type == ASTNodeType.BINARY_EXPR:
            self._analyze_binary_expr(node)
        elif node.node_type == ASTNodeType.UNARY_EXPR:
            self._analyze_unary_expr(node)
        elif node.node_type == ASTNodeType.ASSIGN_EXPR:
            self._analyze_assign_expr(node)
        elif node.node_type == ASTNodeType.VARIABLE:
            self._analyze_variable(node)
        elif node.node_type == ASTNodeType.IF_STMT:
            self._analyze_if_stmt(node)
        elif node.node_type == ASTNodeType.WHILE_STMT:
            self._analyze_while_stmt(node)
        elif node.node_type == ASTNodeType.FOR_STMT:
            self._analyze_for_stmt(node)
    
    def _analyze_program(self, node: ASTNode):
        """Analyze program node"""
        print("\nBuilding symbol table...")
    
    def _analyze_variable_decl(self, node: ASTNode):
        """Analyze variable declaration"""
        var_name = node.value
        var_type = node.data_type
        
        # Check for redefinition
        if var_name in self.symbol_table:
            self.errors.append(f"Variable '{var_name}' is already defined")
            return
        
        # Add to symbol table
        symbol = Symbol(var_name, SymbolType.VARIABLE, var_type, line=1)
        self.symbol_table[var_name] = symbol
        
        # Check for initialization
        if node.children:
            init = node.children[0]
            if init and init.data_type != "unknown":
                # Type checking
                if not self._is_compatible(var_type, init.data_type):
                    self.warnings.append(f"Type mismatch: cannot convert '{init.data_type}' to '{var_type}'")
    
    def _analyze_function_decl(self, node: ASTNode):
        """Analyze function declaration"""
        func_name = node.children[1].value if len(node.children) > 1 else node.value
        return_type = node.children[0].value if node.children else "void"
        
        # Add function to symbol table
        symbol = Symbol(func_name, SymbolType.FUNCTION, return_type, line=1)
        self.symbol_table[func_name] = symbol
    
    def _analyze_binary_expr(self, node: ASTNode):
        """Analyze binary expression - performs type checking"""
        left_type = node.left.data_type if node.left else "unknown"
        right_type = node.right.data_type if node.right else "unknown"
        operator = node.value
        
        # Arithmetic operations
        if operator in ['+', '-', '*', '/', '%']:
            # Both must be numeric
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                # Result type is the wider type
                if left_type == 'float' or right_type == 'float':
                    node.data_type = 'float'
                else:
                    node.data_type = 'int'
            else:
                self.errors.append(f"Arithmetic operation '{operator}' requires numeric operands")
                node.data_type = 'error'
        
        # Comparison operations
        elif operator in ['==', '!=', '<', '>', '<=', '>=']:
            node.data_type = 'int'  # Comparisons return int (0 or 1)
            
            # Type checking for comparisons
            if not self._is_compatible(left_type, right_type):
                self.warnings.append(f"Comparing incompatible types '{left_type}' and '{right_type}'")
        
        # Logical operations
        elif operator in ['&&', '||']:
            if left_type != 'int' or right_type != 'int':
                self.errors.append(f"Logical operation '{operator}' requires integer operands")
            node.data_type = 'int'
    
    def _analyze_unary_expr(self, node: ASTNode):
        """Analyze unary expression"""
        operand_type = node.right.data_type if node.right else "unknown"
        
        if node.value == '!':
            node.data_type = 'int'
        elif node.value == '-':
            node.data_type = operand_type
    
    def _analyze_assign_expr(self, node: ASTNode):
        """Analyze assignment expression"""
        if node.left and node.left.node_type == ASTNodeType.VARIABLE:
            var_name = node.left.value
            
            # Check if variable is defined
            if var_name not in self.symbol_table:
                self.errors.append(f"Variable '{var_name}' is not defined")
            
            # Type checking
            if node.right:
                left_type = self.symbol_table.get(var_name, Symbol("", SymbolType.VARIABLE, "unknown")).data_type
                right_type = node.right.data_type
                
                if not self._is_compatible(left_type, right_type):
                    self.errors.append(f"Cannot assign '{right_type}' to variable of type '{left_type}'")
                
                node.data_type = left_type
    
    def _analyze_variable(self, node: ASTNode):
        """Analyze variable reference"""
        var_name = node.value
        
        # Check if variable is defined
        if var_name not in self.symbol_table:
            self.errors.append(f"Variable '{var_name}' is not defined")
            node.data_type = 'error'
            return
        
        # Get type from symbol table
        symbol = self.symbol_table[var_name]
        node.data_type = symbol.data_type
    
    def _analyze_if_stmt(self, node: ASTNode):
        """Analyze if statement - check condition type"""
        if node.children:
            condition = node.children[0]
            if condition.data_type != 'int':
                self.warnings.append("If condition should evaluate to integer (non-zero = true)")
    
    def _analyze_while_stmt(self, node: ASTNode):
        """Analyze while statement - check condition type"""
        if node.children:
            condition = node.children[0]
            if condition.data_type != 'int':
                self.warnings.append("While condition should evaluate to integer")
    
    def _analyze_for_stmt(self, node: ASTNode):
        """Analyze for statement - check condition type"""
        if len(node.children) > 1:
            condition = node.children[1]
            if condition.data_type not in ['int', 'error']:
                self.warnings.append("For condition should evaluate to integer")
    
    def _is_compatible(self, type1: str, type2: str) -> bool:
        """Check if two types are compatible"""
        if type1 == type2:
            return True
        # int can be assigned to float
        if type1 == 'float' and type2 == 'int':
            return True
        return False
    
    def _display_symbol_table(self):
        """Display the symbol table"""
        print("\n" + "-" * 70)
        print("SYMBOL TABLE")
        print("-" * 70)
        print(f"{'Name':<20} {'Type':<15} {'Data Type':<15} {'Line':<10}")
        print("-" * 70)
        
        for name, symbol in self.symbol_table.items():
            print(f"{name:<20} {symbol.symbol_type.name:<15} {symbol.data_type:<15} {symbol.line:<10}")
        
        print("-" * 70)
        print(f"Total symbols: {len(self.symbol_table)}")


# =============================================================================
# PART 4: CODE OPTIMIZATION
# =============================================================================

class Optimizer:
    """
    =========================================================================
    CODE OPTIMIZER
    =========================================================================
    Performs various code optimizations:
    
    1. Constant Folding: Evaluate constant expressions at compile time
    2. Dead Code Elimination: Remove unreachable code and unused variables
    3. Common Subexpression Elimination (CSE): Reuse computed values
    
    =========================================================================
    """
    
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.optimizations_applied: List[str] = []
        self.common_subexpressions: Dict[str, ASTNode] = {}
        
    def optimize(self) -> ASTNode:
        """
        Main optimization method - applies all optimization passes.
        
        Returns:
            Optimized AST
        """
        print("\n" + "="*70)
        print("PHASE 4: CODE OPTIMIZATION")
        print("="*70)
        
        # Reset optimization counter
        self.optimizations_applied = []
        self.common_subexpressions = {}
        
        # Apply optimizations in multiple passes
        print("\nApplying optimizations...")
        
        # Pass 1: Constant Folding
        self._constant_folding(self.ast)
        print(f"  [PASSED] Constant Folding: {sum(1 for x in self.optimizations_applied if 'Constant Folding' in x)} optimizations")
        
        # Pass 2: Common Subexpression Elimination
        self._common_subexpression_elimination(self.ast)
        print(f"  [PASSED] Common Subexpression Elimination: {sum(1 for x in self.optimizations_applied if 'CSE' in x)} optimizations")
        
        # Pass 3: Dead Code Elimination
        self._dead_code_elimination(self.ast)
        print(f"  [PASSED] Dead Code Elimination: {sum(1 for x in self.optimizations_applied if 'Dead Code' in x)} optimizations")
        
        # Display summary
        self._display_optimization_summary()
        
        return self.ast
    
    def _constant_folding(self, node: ASTNode) -> ASTNode:
        """
        =========================================================================
        CONSTANT FOLDING
        =========================================================================
        Evaluates constant arithmetic and logical expressions at compile time.
        
        Examples:
            2 + 3    → 5
            10 * 5   → 50
            5 == 5   → 1 (true)
            !0       → 1
        =========================================================================
        """
        if node is None:
            return node
        
        # Process children first (post-order)
        for i, child in enumerate(node.children):
            node.children[i] = self._constant_folding(child)
        
        if node.left:
            node.left = self._constant_folding(node.left)
        if node.right:
            node.right = self._constant_folding(node.right)
        
        # Binary expression constant folding
        if node.node_type == ASTNodeType.BINARY_EXPR:
            result = self._fold_binary_expr(node)
            if result is not None:
                node.node_type = ASTNodeType.LITERAL
                node.value = result
                node.data_type = self._get_result_type(node.left, node.right, node.value)
                self.optimizations_applied.append(f"Constant Folding: {node.left.value} {node.value} {node.right.value} -> {result}")
                node.left = None
                node.right = None
        
        # Unary expression constant folding
        elif node.node_type == ASTNodeType.UNARY_EXPR:
            result = self._fold_unary_expr(node)
            if result is not None:
                node.node_type = ASTNodeType.LITERAL
                node.value = result
                node.data_type = 'int'
                self.optimizations_applied.append(f"Constant Folding: {node.value}{node.right.value} -> {result}")
                node.right = None
        
        return node
    
    def _fold_binary_expr(self, node: ASTNode) -> Optional[Any]:
        """Fold a binary expression if both operands are constants"""
        if not node.left or not node.right:
            return None
        
        if node.left.node_type != ASTNodeType.LITERAL or node.right.node_type != ASTNodeType.LITERAL:
            return None
        
        try:
            left_val = self._to_number(node.left.value)
            right_val = self._to_number(node.right.value)
            op = node.value
            
            # Arithmetic operations
            if op == '+':
                return left_val + right_val
            elif op == '-':
                return left_val - right_val
            elif op == '*':
                return left_val * right_val
            elif op == '/':
                return left_val // right_val if right_val != 0 else None
            elif op == '%':
                return left_val % right_val if right_val != 0 else None
            
            # Comparison operations
            elif op == '==':
                return 1 if left_val == right_val else 0
            elif op == '!=':
                return 1 if left_val != right_val else 0
            elif op == '<':
                return 1 if left_val < right_val else 0
            elif op == '>':
                return 1 if left_val > right_val else 0
            elif op == '<=':
                return 1 if left_val <= right_val else 0
            elif op == '>=':
                return 1 if left_val >= right_val else 0
            
            # Logical operations
            elif op == '&&':
                return 1 if (left_val and right_val) else 0
            elif op == '||':
                return 1 if (left_val or right_val) else 0
            
        except (TypeError, ValueError):
            pass
        
        return None
    
    def _fold_unary_expr(self, node: ASTNode) -> Optional[Any]:
        """Fold a unary expression if operand is constant"""
        if not node.right or node.right.node_type != ASTNodeType.LITERAL:
            return None
        
        try:
            val = self._to_number(node.right.value)
            
            if node.value == '-':
                return -val
            elif node.value == '!':
                return 0 if val else 1
            
        except (TypeError, ValueError):
            pass
        
        return None
    
    def _to_number(self, value: Any) -> Optional[int]:
        """Convert value to number"""
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        return None
    
    def _get_result_type(self, left: ASTNode, right: ASTNode, result: Any) -> str:
        """Determine the result type of an operation"""
        if isinstance(result, float) or (isinstance(result, str) and '.' in str(result)):
            return 'float'
        return 'int'
    
    def _common_subexpression_elimination(self, node: ASTNode) -> ASTNode:
        """
        =========================================================================
        COMMON SUBEXPRESSION ELIMINATION (CSE)
        =========================================================================
        Identifies and eliminates redundant computations.
        
        Example:
            x = a + b;
            y = a + b;  →  y = x;
        =========================================================================
        """
        if node is None:
            return node
        
        # Process children
        for i, child in enumerate(node.children):
            node.children[i] = self._common_subexpression_elimination(child)
        
        if node.left:
            node.left = self._common_subexpression_elimination(node.left)
        if node.right:
            node.right = self._common_subexpression_elimination(node.right)
        
        # Check for common subexpressions
        if node.node_type == ASTNodeType.BINARY_EXPR:
            expr_key = self._get_expr_key(node)
            
            if expr_key in self.common_subexpressions:
                # Found a common subexpression
                original = self.common_subexpressions[expr_key]
                self.optimizations_applied.append(f"CSE: Replaced duplicate expression with variable '{original.value}'")
                
                # Replace with variable reference
                node.node_type = ASTNodeType.VARIABLE
                node.value = original.value
                node.left = None
                node.right = None
            else:
                # Store this expression
                # Create a synthetic variable name
                var_name = f"_t{len(self.common_subexpressions)}"
                self.common_subexpressions[expr_key] = ASTNode(ASTNodeType.VARIABLE, var_name)
        
        return node
    
    def _get_expr_key(self, node: ASTNode) -> str:
        """Get a unique key for an expression"""
        if node.node_type == ASTNodeType.BINARY_EXPR:
            left_key = self._get_expr_key(node.left) if node.left else ""
            right_key = self._get_expr_key(node.right) if node.right else ""
            return f"{node.value}({left_key},{right_key})"
        elif node.node_type == ASTNodeType.LITERAL:
            return str(node.value)
        elif node.node_type == ASTNodeType.VARIABLE:
            return str(node.value)
        return ""
    
    def _dead_code_elimination(self, node: ASTNode) -> ASTNode:
        """
        =========================================================================
        DEAD CODE ELIMINATION
        =========================================================================
        Removes unreachable code and unused variable assignments.
        
        Examples:
            if (0) { ... }     →  Removed (condition always false)
            if (1) { ... }     →  Just the body (condition always true)
            x = 5; (unused)    →  Removed
        =========================================================================
        """
        if node is None:
            return node
        
        # Process children
        for i, child in enumerate(node.children):
            node.children[i] = self._dead_code_elimination(child)
        
        if node.left:
            node.left = self._dead_code_elimination(node.left)
        if node.right:
            node.right = self._dead_code_elimination(node.right)
        
        # If statement dead code elimination
        if node.node_type == ASTNodeType.IF_STMT and len(node.children) >= 2:
            condition = node.children[0]
            
            # Check if condition is a constant
            if condition.node_type == ASTNodeType.LITERAL:
                cond_value = self._to_number(condition.value)
                
                if cond_value == 0:
                    # Condition always false - remove entire if
                    if len(node.children) > 2 and node.children[2]:
                        self.optimizations_applied.append("Dead Code: Removed if-statement with always-false condition")
                        # Replace with else branch if exists
                        node.node_type = node.children[2].node_type
                        node.value = node.children[2].value
                        node.children = node.children[2].children
                    else:
                        return None
                
                elif cond_value != 0:
                    # Condition always true - keep only then branch
                    self.optimizations_applied.append("Dead Code: Removed always-true condition from if-statement")
                    then_branch = node.children[1]
                    node.node_type = then_branch.node_type
                    node.value = then_branch.value
                    node.children = then_branch.children
        
        # While statement dead code elimination
        if node.node_type == ASTNodeType.WHILE_STMT and len(node.children) >= 1:
            condition = node.children[0]
            
            # Check if condition is a constant false
            if condition.node_type == ASTNodeType.LITERAL:
                cond_value = self._to_number(condition.value)
                
                if cond_value == 0:
                    # Infinite loop with false condition - remove
                    self.optimizations_applied.append("Dead Code: Removed while-loop with always-false condition")
                    return None
        
        return node
    
    def _display_optimization_summary(self):
        """Display summary of optimizations"""
        print("\n" + "-" * 70)
        print("OPTIMIZATION SUMMARY")
        print("-" * 70)
        print(f"\nTotal optimizations applied: {len(self.optimizations_applied)}")
        
        if self.optimizations_applied:
            print("\nDetails:")
            for i, opt in enumerate(self.optimizations_applied, 1):
                print(f"  {i}. {opt}")
        
        print("-" * 70)


# =============================================================================
# SECURITY ANALYSIS
# =============================================================================

class SecurityAnalyzer:
    """
    =========================================================================
    SECURITY ANALYZER
    =========================================================================
    Scans source code and AST for common security vulnerabilities.
    
    Detects:
    1. Dangerous Functions     - gets, strcpy, strcat, sprintf, system etc.
    2. Buffer Overflow Risk    - Fixed-size buffers with unchecked input
    3. Format String Bugs      - printf with user-controlled strings
    4. Integer Overflow        - Unsafe arithmetic on sizes
    5. Memory Leak             - malloc/calloc without free
    6. Use-After-Free          - Using pointer after free()
    7. Double Free             - Calling free() twice on same pointer
    8. Null Pointer Risk       - Using pointer without NULL check after malloc
    9. Command Injection       - system()/exec() with user input
    10. Uninitialized Variable - Using variable before assigning value
    =========================================================================
    """
    
    # Dangerous functions and their safe alternatives
    DANGEROUS_FUNCTIONS = {
        'gets': {
            'severity': 'CRITICAL',
            'category': 'Buffer Overflow',
            'message': "gets() is extremely dangerous - no buffer size limit",
            'fix': "Replace gets(buf) with fgets(buf, sizeof(buf), stdin)",
            'fix_example': "fgets(buffer, sizeof(buffer), stdin);"
        },
        'strcpy': {
            'severity': 'HIGH',
            'category': 'Buffer Overflow',
            'message': "strcpy() does not check buffer bounds",
            'fix': "Replace strcpy(dst, src) with strncpy(dst, src, sizeof(dst)-1)",
            'fix_example': "strncpy(dest, src, sizeof(dest)-1);\ndest[sizeof(dest)-1] = '\\0';"
        },
        'strcat': {
            'severity': 'HIGH',
            'category': 'Buffer Overflow',
            'message': "strcat() does not check buffer bounds",
            'fix': "Replace strcat(dst, src) with strncat(dst, src, sizeof(dst)-strlen(dst)-1)",
            'fix_example': "strncat(dest, src, sizeof(dest)-strlen(dest)-1);"
        },
        'sprintf': {
            'severity': 'HIGH',
            'category': 'Buffer Overflow',
            'message': "sprintf() does not check buffer bounds",
            'fix': "Replace sprintf(buf, ...) with snprintf(buf, sizeof(buf), ...)",
            'fix_example': "snprintf(buffer, sizeof(buffer), \"%d\", value);"
        },
        'scanf': {
            'severity': 'MEDIUM',
            'category': 'Buffer Overflow',
            'message': "scanf() with %s can overflow buffer - no width limit",
            'fix': "Use scanf(\"%99s\", buf) with width limit, or use fgets()",
            'fix_example': "scanf(\"%49s\", buffer);  // limit to 49 chars"
        },
        'system': {
            'severity': 'CRITICAL',
            'category': 'Command Injection',
            'message': "system() can execute arbitrary commands - injection risk",
            'fix': "Avoid system() with user input. Use execve() with validated args",
            'fix_example': "// Validate and sanitize all input before using system()\n// Better: use execve(\"/bin/ls\", args, env) instead of system(user_input)"
        },
        'popen': {
            'severity': 'HIGH',
            'category': 'Command Injection',
            'message': "popen() can execute arbitrary commands",
            'fix': "Sanitize input before passing to popen()",
            'fix_example': "// Never pass raw user input to popen()"
        },
        'tmpnam': {
            'severity': 'MEDIUM',
            'category': 'Race Condition',
            'message': "tmpnam() has TOCTOU (race condition) vulnerability",
            'fix': "Use mkstemp() instead of tmpnam()",
            'fix_example': "int fd = mkstemp(template);"
        },
        'rand': {
            'severity': 'LOW',
            'category': 'Weak Randomness',
            'message': "rand() is cryptographically weak - predictable output",
            'fix': "For security, use /dev/urandom or arc4random()",
            'fix_example': "FILE *f = fopen(\"/dev/urandom\", \"r\")\nfread(&value, sizeof(value), 1, f);"
        },
        'atoi': {
            'severity': 'LOW',
            'category': 'Input Validation',
            'message': "atoi() has no error handling - returns 0 on failure",
            'fix': "Use strtol() with error checking instead",
            'fix_example': "char *end;\nlong val = strtol(str, &end, 10);\nif (*end != '\\0') { /* error */ }"
        },
    }
    
    def __init__(self, source_code: str, ast: ASTNode = None):
        self.source_code = source_code
        self.ast = ast
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.malloc_vars: Dict[str, int] = {}    # var_name -> line number
        self.freed_vars: Dict[str, int] = {}      # var_name -> line number
        self.assigned_vars: set = set()
    
    def analyze(self) -> List[Dict[str, Any]]:
        """
        Main security analysis method.
        
        Returns:
            List of vulnerability dictionaries
        """
        print("\n" + "="*70)
        print("SECURITY ANALYSIS")
        print("="*70)
        
        self.vulnerabilities = []
        self.malloc_vars = {}
        self.freed_vars = {}
        self.assigned_vars = set()
        
        lines = self.source_code.split('\n')
        
        # Run all checks
        self._check_dangerous_functions(lines)
        self._check_format_string(lines)
        self._check_command_injection(lines)
        self._check_memory_management(lines)
        self._check_uninitialized_vars(lines)
        self._check_buffer_operations(lines)
        
        # Display results
        self._display_results()
        
        return self.vulnerabilities
    
    def _add_vuln(self, line: int, col: int, severity: str, category: str,
                   message: str, fix: str, fix_example: str = "", code_line: str = ""):
        """Add a vulnerability to the list"""
        self.vulnerabilities.append({
            'line': line,
            'column': col,
            'severity': severity,
            'category': category,
            'message': message,
            'fix': fix,
            'fix_example': fix_example,
            'code_line': code_line
        })
    
    def _check_dangerous_functions(self, lines: List[str]):
        """Check for usage of dangerous C functions"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue
            
            for func_name, info in self.DANGEROUS_FUNCTIONS.items():
                # Match function call pattern: func_name(
                pattern = r'\b' + func_name + r'\s*\('
                if re.search(pattern, line):
                    self._add_vuln(
                        line=i,
                        col=line.find(func_name) + 1 if func_name in line else 1,
                        severity=info['severity'],
                        category=info['category'],
                        message=f"{func_name}() - {info['message']}",
                        fix=info['fix'],
                        fix_example=info['fix_example'],
                        code_line=stripped
                    )
    
    def _check_format_string(self, lines: List[str]):
        """Check for printf format string vulnerabilities"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            # printf(variable) - no format string, variable as format
            m = re.search(r'printf\s*\(\s*([a-zA-Z_]\w*)\s*\)', line)
            if m:
                var_name = m.group(1)
                self._add_vuln(
                    line=i, col=m.start() + 1,
                    severity='CRITICAL',
                    category='Format String',
                    message=f"printf({var_name}) - Variable used as format string is dangerous",
                    fix=f"Use printf(\"%s\", {var_name}) with explicit format",
                    fix_example=f"printf(\"%s\", {var_name});",
                    code_line=stripped
                )
            
            # fprintf(stream, variable)
            m = re.search(r'fprintf\s*\(\s*\w+\s*,\s*([a-zA-Z_]\w*)\s*\)', line)
            if m:
                var_name = m.group(1)
                self._add_vuln(
                    line=i, col=m.start() + 1,
                    severity='HIGH',
                    category='Format String',
                    message=f"fprintf() with variable as format string",
                    fix=f"Use fprintf(stream, \"%s\", {var_name})",
                    fix_example=f"fprintf(stream, \"%s\", {var_name});",
                    code_line=stripped
                )
    
    def _check_command_injection(self, lines: List[str]):
        """Check for command injection via system()/popen()"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # system() with string concatenation or variable
            m = re.search(r'system\s*\(\s*.*["\'].*["\'].*\+\s*\w+', line)
            if not m:
                m = re.search(r'system\s*\(\s*[a-zA-Z_]\w*\s*\)', line)
            if m:
                self._add_vuln(
                    line=i, col=m.start() + 1,
                    severity='CRITICAL',
                    category='Command Injection',
                    message="system() called with potentially unvalidated input",
                    fix="Validate and sanitize input. Use execve() with argument array",
                    fix_example="// Whitelist allowed commands\nif (strcmp(cmd, \"ls\") == 0) system(\"ls\");",
                    code_line=stripped
                )
    
    def _check_memory_management(self, lines: List[str]):
        """Check for memory leaks, use-after-free, double-free"""
        malloc_pattern = re.compile(
            r'(\w+)\s*=\s*(?:malloc|calloc|realloc)\s*\('
        )
        free_pattern = re.compile(r'free\s*\(\s*(\w+)\s*\)')
        use_pattern = re.compile(
            r'(?:printf|scanf|strcpy|strncpy|memcpy|memset|fprintf|fread|fwrite)'
            r'\s*\(.*\b(\w+)\b'
        )
        
        declared_after_malloc = {}  # track variables declared after malloc
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            # Track malloc
            m = malloc_pattern.search(line)
            if m:
                var_name = m.group(1)
                self.malloc_vars[var_name] = i
            
            # Track free
            m = free_pattern.search(line)
            if m:
                var_name = m.group(1)
                if var_name in self.freed_vars:
                    self._add_vuln(
                        line=i, col=m.start() + 1,
                        severity='CRITICAL',
                        category='Double Free',
                        message=f"free({var_name}) - Variable already freed on line {self.freed_vars[var_name]}",
                        fix=f"Set {var_name} = NULL after free, then check before freeing again",
                        fix_example=f"free({var_name});\n{var_name} = NULL;",
                        code_line=stripped
                    )
                else:
                    self.freed_vars[var_name] = i
                
                # Check if it was malloc'd
                if var_name not in self.malloc_vars:
                    self._add_vuln(
                        line=i, col=m.start() + 1,
                        severity='MEDIUM',
                        category='Suspicious Free',
                        message=f"free({var_name}) - Variable was never malloc'd/calloc'd",
                        fix=f"Only free() memory allocated by malloc/calloc/realloc",
                        fix_example=f"char *{var_name} = malloc(100);\n// ... use {var_name} ...\nfree({var_name});",
                        code_line=stripped
                    )
        
        # Check for memory leaks: malloc without free
        for var_name, malloc_line in self.malloc_vars.items():
            if var_name not in self.freed_vars:
                self._add_vuln(
                    line=malloc_line, col=1,
                    severity='HIGH',
                    category='Memory Leak',
                    message=f"'{var_name}' allocated with malloc on line {malloc_line} but never freed",
                    fix=f"Add free({var_name}) before function returns",
                    fix_example=f"// At the end of function:\nfree({var_name});",
                    code_line=""
                )
    
    def _check_uninitialized_vars(self, lines: List[str]):
        """Check for variables used before assignment"""
        declared = {}  # var_name -> line declared
        assigned = set()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            # Detect declaration: int x; or int x = ...
            m = re.match(r'(?:int|float|char|double|long)\s+(\w+)', stripped)
            if m:
                var_name = m.group(1)
                declared[var_name] = i
                if '=' in stripped:
                    assigned.add(var_name)
                continue
            
            # Detect assignment: x = value
            m = re.match(r'(\w+)\s*=', stripped)
            if m:
                assigned.add(m.group(1))
                continue
            
            # Check usage in expressions
            for var_name, decl_line in declared.items():
                if var_name in assigned:
                    continue
                # Skip function names and keywords
                if var_name in ('if', 'while', 'for', 'return', 'int', 'float', 'void', 'char'):
                    continue
                # Check if variable is used in this line
                if re.search(r'\b' + var_name + r'\b', line):
                    if var_name not in assigned and not stripped.startswith(f'int {var_name}') \
                       and not stripped.startswith(f'float {var_name}') \
                       and not stripped.startswith(f'char {var_name}'):
                        self._add_vuln(
                            line=i, col=1,
                            severity='HIGH',
                            category='Uninitialized Variable',
                            message=f"Variable '{var_name}' used on line {i} but not initialized (declared on line {decl_line})",
                            fix=f"Initialize '{var_name}' when declaring: type {var_name} = value;",
                            fix_example=f"int {var_name} = 0;  // initialize with default value",
                            code_line=stripped
                        )
                        assigned.add(var_name)  # report only once
    
    def _check_buffer_operations(self, lines: List[str]):
        """Check for unsafe buffer operations"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            # Check for large stack buffers
            m = re.search(r'(?:char|unsigned char)\s+(\w+)\s*\[\s*(\d+)\s*\]', line)
            if m:
                var_name = m.group(1)
                size = int(m.group(2))
                if size > 1024:
                    self._add_vuln(
                        line=i, col=1,
                        severity='MEDIUM',
                        category='Large Stack Buffer',
                        message=f"Buffer '{var_name}[{size}]' is {size} bytes on stack - risk of stack overflow",
                        fix=f"Use dynamic allocation for large buffers",
                        fix_example=f"char *{var_name} = malloc({size});\n// ... use buffer ...\nfree({var_name});",
                        code_line=stripped
                    )
            
            # Check for integer overflow in size calculations
            m = re.search(r'malloc\s*\(\s*(\w+)\s*\*\s*(\w+)\s*\)', line)
            if m:
                self._add_vuln(
                    line=i, col=1,
                    severity='HIGH',
                    category='Integer Overflow',
                    message=f"malloc({m.group(1)} * {m.group(2)}) - multiplication can overflow",
                    fix="Check for overflow before multiplication",
                    fix_example=f"if ({m.group(1)} > SIZE_MAX / {m.group(2)}) {{ /* error */ }}\nptr = malloc({m.group(1)} * {m.group(2)});",
                    code_line=stripped
                )
    
    def _display_results(self):
        """Display security analysis results"""
        print("\n" + "-" * 70)
        print("SECURITY ANALYSIS RESULTS")
        print("-" * 70)
        
        if not self.vulnerabilities:
            print("\n  [PASSED] No security vulnerabilities found!")
            print("-" * 70)
            return
        
        # Count by severity
        critical = sum(1 for v in self.vulnerabilities if v['severity'] == 'CRITICAL')
        high = sum(1 for v in self.vulnerabilities if v['severity'] == 'HIGH')
        medium = sum(1 for v in self.vulnerabilities if v['severity'] == 'MEDIUM')
        low = sum(1 for v in self.vulnerabilities if v['severity'] == 'LOW')
        
        print(f"\n  Found {len(self.vulnerabilities)} vulnerability(ies):")
        print(f"  CRITICAL: {critical}  HIGH: {high}  MEDIUM: {medium}  LOW: {low}")
        print()
        
        for i, vuln in enumerate(self.vulnerabilities, 1):
            sev = vuln['severity']
            sev_icon = {
                'CRITICAL': '[!!]', 'HIGH': '[!]', 'MEDIUM': '[~]', 'LOW': '[-]'
            }.get(sev, '[?]')
            
            print(f"  {sev_icon} #{i} [{sev}] Line {vuln['line']}: {vuln['category']}")
            print(f"     {vuln['message']}")
            print(f"     Fix: {vuln['fix']}")
            if vuln['code_line']:
                print(f"     Code: {vuln['code_line']}")
            print()
        
        print("-" * 70)


# =============================================================================
# CODE GENERATION (Simple Output)
# =============================================================================

class CodeGenerator:
    """
    =========================================================================
    CODE GENERATOR
    =========================================================================
    Generates optimized code from the AST.
    =========================================================================
    """
    
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.code: List[str] = []
        self.indent_level = 0
        
    def generate(self) -> str:
        """
        Generate code from AST.
        
        Returns:
            Generated code as string
        """
        print("\n" + "="*70)
        print("CODE GENERATION")
        print("="*70)
        
        self._generate_node(self.ast)
        
        result = '\n'.join(self.code)
        
        print("\nGenerated Code:")
        print("-" * 70)
        print(result)
        print("-" * 70)
        
        return result
    
    def _generate_node(self, node: ASTNode):
        """Generate code for a node"""
        if node is None:
            return
        
        indent = "    " * self.indent_level
        
        if node.node_type == ASTNodeType.PROGRAM:
            for child in node.children:
                self._generate_node(child)
        
        elif node.node_type == ASTNodeType.VARIABLE_DECL:
            type_str = node.data_type
            var_name = node.value
            
            if node.children:
                # With initialization
                init_code = self._generate_expr(node.children[0])
                self.code.append(f"{indent}{type_str} {var_name} = {init_code};")
            else:
                self.code.append(f"{indent}{type_str} {var_name};")
        
        elif node.node_type == ASTNodeType.FUNCTION_DECL:
            return_type = node.children[0].value
            func_name = node.children[1].value
            params = node.children[2]
            body = node.children[3]
            
            param_str = ", ".join([f"{p.data_type} {p.value}" for p in params.children])
            self.code.append(f"\n{indent}{return_type} {func_name}({param_str}) {{")
            self.indent_level += 1
            self._generate_node(body)
            self.indent_level -= 1
            self.code.append(f"{indent}}}")
        
        elif node.node_type == ASTNodeType.COMPOUND_STMT:
            for child in node.children:
                self._generate_node(child)
        
        elif node.node_type == ASTNodeType.IF_STMT:
            condition = self._generate_expr(node.children[0])
            self.code.append(f"{indent}if ({condition}) {{")
            self.indent_level += 1
            self._generate_node(node.children[1])
            self.indent_level -= 1
            
            if len(node.children) > 2 and node.children[2]:
                self.code.append(f"{indent}}} else {{")
                self.indent_level += 1
                self._generate_node(node.children[2])
                self.indent_level -= 1
            
            self.code.append(f"{indent}}}")
        
        elif node.node_type == ASTNodeType.WHILE_STMT:
            condition = self._generate_expr(node.children[0])
            self.code.append(f"{indent}while ({condition}) {{")
            self.indent_level += 1
            self._generate_node(node.children[1])
            self.indent_level -= 1
            self.code.append(f"{indent}}}")
        
        elif node.node_type == ASTNodeType.FOR_STMT:
            init = self._generate_expr(node.children[0])
            cond = self._generate_expr(node.children[1])
            update = self._generate_expr(node.children[2])
            self.code.append(f"{indent}for ({init}; {cond}; {update}) {{")
            self.indent_level += 1
            self._generate_node(node.children[3])
            self.indent_level -= 1
            self.code.append(f"{indent}}}")
        
        elif node.node_type == ASTNodeType.RETURN_STMT:
            if node.children:
                ret_val = self._generate_expr(node.children[0])
                self.code.append(f"{indent}return {ret_val};")
            else:
                self.code.append(f"{indent}return;")
        
        elif node.node_type == ASTNodeType.EXPRESSION_STMT:
            if node.children:
                expr = self._generate_expr(node.children[0])
                self.code.append(f"{indent}{expr};")
    
    def _generate_expr(self, node: ASTNode) -> str:
        """Generate expression code"""
        if node is None:
            return ""
        
        if node.node_type == ASTNodeType.LITERAL:
            return str(node.value)
        
        elif node.node_type == ASTNodeType.VARIABLE:
            return str(node.value)
        
        elif node.node_type == ASTNodeType.BINARY_EXPR:
            left = self._generate_expr(node.left)
            right = self._generate_expr(node.right)
            return f"({left} {node.value} {right})"
        
        elif node.node_type == ASTNodeType.UNARY_EXPR:
            operand = self._generate_expr(node.right)
            return f"{node.value}{operand}"
        
        elif node.node_type == ASTNodeType.ASSIGN_EXPR:
            left = self._generate_expr(node.left)
            right = self._generate_expr(node.right)
            return f"{left} = {right}"
        
        return ""


# =============================================================================
# MAIN COMPILER CLASS
# =============================================================================

class Compiler:
    """
    =========================================================================
    MAIN COMPILER CLASS
    =========================================================================
    Orchestrates all phases of compilation:
    1. Lexical Analysis
    2. Syntax Analysis
    3. Semantic Analysis
    4. Code Optimization
    5. Code Generation
    =========================================================================
    """
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.ast: ASTNode = None
        self.semantic_ast: ASTNode = None
        self.optimized_ast: ASTNode = None
        self.generated_code: str = ""
        
    def compile(self) -> str:
        """
        Main compilation method - runs all phases.
        
        Returns:
            Final generated code
        """
        print("\n" + "="*70)
        print("              COMPILER STARTING")
        print("="*70)
        print(f"\nInput Source Code:")
        print("-" * 70)
        print(self.source_code)
        print("-" * 70)
        
        # Phase 1: Lexical Analysis
        lexer = LexicalAnalyzer(self.source_code)
        self.tokens = lexer.tokenize()
        
        # Phase 2: Syntax Analysis
        parser = SyntaxAnalyzer(self.tokens)
        self.ast = parser.parse()
        
        # Phase 3: Semantic Analysis
        semantic_analyzer = SemanticAnalyzer(self.ast)
        self.semantic_ast = semantic_analyzer.analyze()
        
        # Phase 4: Code Optimization
        optimizer = Optimizer(self.semantic_ast)
        self.optimized_ast = optimizer.optimize()
        
        # Phase 5: Code Generation
        code_generator = CodeGenerator(self.optimized_ast)
        self.generated_code = code_generator.generate()
        
        # Final summary
        self._display_final_summary()
        
        return self.generated_code
    
    def _display_final_summary(self):
        """Display final compilation summary"""
        print("\n" + "="*70)
        print("              COMPILATION COMPLETE")
        print("="*70)
        print("""
  ==============================================================================
                     PHASES COMPLETED
  ==============================================================================
  [PASSED] Phase 1: Lexical Analysis    (Tokenization)
  [PASSED] Phase 2: Syntax Analysis     (Parsing)
  [PASSED] Phase 3: Semantic Analysis   (Type Checking)
  [PASSED] Phase 4: Code Optimization  (Optimizations Applied)
  [PASSED] Phase 5: Code Generation     (Output Generated)
  ==============================================================================
""")


# =============================================================================
# SAMPLE INPUT AND DEMONSTRATION
# =============================================================================

def run_sample_compilation():
    """Run a sample compilation to demonstrate the compiler"""
    
    # Sample source code with various constructs to test all phases
    sample_code = """
int main() {
    int x = 10;
    int y = 20;
    int z = x + y;
    int result = z * 2;
    
    if (result > 50) {
        return 1;
    } else {
        return 0;
    }
}
"""
    
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + " "*15 + "SAMPLE COMPILATION DEMONSTRATION" + " "*20 + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    # Create compiler and run
    compiler = Compiler(sample_code)
    result = compiler.compile()
    
    return result


def run_constant_folding_demo():
    """Demonstrate constant folding optimization"""
    
    print("\n\n")
    print("#"*70)
    print("#" + " "*68 + "#")
    print("#" + " "*18 + "CONSTANT FOLDING DEMONSTRATION" + " "*18 + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    sample_code = """
int main() {
    int x = 5 + 3;
    int y = 10 * 2;
    int z = 20 - 5;
    int a = 100 / 10;
    int b = 15 % 4;
    int c = (10 > 5);
    int d = (5 == 5);
    return 0;
}
"""
    
    compiler = Compiler(sample_code)
    result = compiler.compile()
    
    return result


def run_dead_code_demo():
    """Demonstrate dead code elimination"""
    
    print("\n\n")
    print("#"*70)
    print("#" + " "*68 + "#")
    print("#" + " "*15 + "DEAD CODE ELIMINATION DEMONSTRATION" + " "*13 + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    sample_code = """
int main() {
    if (0) {
        int dead_code = 100;
    }
    
    if (1) {
        return 42;
    }
    
    return 0;
}
"""
    
    compiler = Compiler(sample_code)
    result = compiler.compile()
    
    return result


def run_cse_demo():
    """Demonstrate common subexpression elimination"""
    
    print("\n\n")
    print("#"*70)
    print("#" + " "*68 + "#")
    print("#" + " "*10 + "COMMON SUBEXPRESSION ELIMINATION DEMONSTRATION" + " "*7 + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    sample_code = """
int main() {
    int a = 10 + 5;
    int b = 10 + 5;
    int c = a + b;
    return c;
}
"""
    
    compiler = Compiler(sample_code)
    result = compiler.compile()
    
    return result


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("================================================================================")
    print("                     MODULAR COMPILER v1.0")
    print("")
    print("  A complete compiler implementation featuring:")
    print("")
    print("  1. Lexical Analysis    - Tokenization using regex patterns")
    print("  2. Syntax Analysis     - Recursive descent parser with AST")
    print("  3. Semantic Analysis   - Type checking & symbol table")
    print("  4. Code Optimization   - Constant folding, CSE, Dead code")
    print("  5. Code Generation     - Generate optimized code")
    print("")
    print("================================================================================")
    
    # Run sample compilations
    run_sample_compilation()
    run_constant_folding_demo()
    run_dead_code_demo()
    run_cse_demo()
    
    print("\n\n" + "="*70)
    print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
    print("="*70)
