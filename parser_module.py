from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from lexer import Token, TokenType

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
    =========================================================================
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
        self.errors: List[Dict[str, Any]] = []
        
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
    
    def expect(self, token_type: TokenType) -> Optional[Token]:
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
        print("\n" + "="*70)
        print("PHASE 2: SYNTAX ANALYSIS (PARSING)")
        print("="*70)
        
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF_TOKEN:
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        
        program = ASTNode(ASTNodeType.PROGRAM, children=statements)
        self._display_ast(program)
        
        if self.errors:
            print("\nSyntax Errors:")
            for err in self.errors:
                print(f"  Line {err['line']}, Col {err['column']}: {err['message']}")
        
        return program
    
    def declaration(self) -> Optional[ASTNode]:
        if self.current_token and self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.VOID]:
            type_token = self.current_token
            self.advance()
            
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                name_token = self.current_token
                self.advance()
                
                if self.current_token and self.current_token.type == TokenType.LPAREN:
                    self.advance()
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
                    var_node = ASTNode(ASTNodeType.VARIABLE_DECL, name_token.value)
                    var_node.data_type = type_token.value
                    
                    if self.current_token and self.current_token.type == TokenType.LBRACKET:
                        self.advance()
                        if self.current_token and self.current_token.type == TokenType.NUMBER:
                            size = ASTNode(ASTNodeType.LITERAL, self.current_token.value)
                            size.data_type = 'int'
                            var_node.children.append(size)
                            self.advance()
                        self.expect(TokenType.RBRACKET)
                        var_node.data_type = f"{type_token.value}[]"
                        
                    elif self.current_token and self.current_token.type == TokenType.EQUAL:
                        self.advance()
                        init = self.expression()
                        var_node.children.append(init)
                    
                    self.expect(TokenType.SEMICOLON)
                    return var_node
        
        return self.statement()
    
    def params(self) -> ASTNode:
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
        self.expect(TokenType.LBRACE)
        compound = ASTNode(ASTNodeType.COMPOUND_STMT)
        
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            if self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.VOID]:
                decl = self.declaration()
                if decl:
                    compound.children.append(decl)
            else:
                stmt = self.statement()
                if stmt:
                    compound.children.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return compound
    
    def statement(self) -> Optional[ASTNode]:
        if not self.current_token:
            return None
            
        token_type = self.current_token.type
        
        if token_type == TokenType.IF: return self.if_stmt()
        if token_type == TokenType.WHILE: return self.while_stmt()
        if token_type == TokenType.FOR: return self.for_stmt()
        if token_type == TokenType.RETURN: return self.return_stmt()
        if token_type == TokenType.LBRACE: return self.compound_stmt()
        
        return self.expr_stmt()
    
    def if_stmt(self) -> ASTNode:
        self.advance()
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
        self.advance()
        self.expect(TokenType.LPAREN)
        condition = self.expression()
        self.expect(TokenType.RPAREN)
        body = self.statement()
        
        while_node = ASTNode(ASTNodeType.WHILE_STMT)
        while_node.children = [condition, body]
        return while_node
    
    def for_stmt(self) -> ASTNode:
        self.advance()
        self.expect(TokenType.LPAREN)
        init = self.expression()
        self.expect(TokenType.SEMICOLON)
        condition = self.expression()
        self.expect(TokenType.SEMICOLON)
        update = self.expression()
        self.expect(TokenType.RPAREN)
        body = self.statement()
        
        for_node = ASTNode(ASTNodeType.FOR_STMT)
        for_node.children = [init, condition, update, body]
        return for_node
    
    def return_stmt(self) -> ASTNode:
        self.advance()
        return_node = ASTNode(ASTNodeType.RETURN_STMT)
        
        if self.current_token and self.current_token.type != TokenType.SEMICOLON:
            expr = self.expression()
            return_node.children.append(expr)
        
        self.expect(TokenType.SEMICOLON)
        return return_node
    
    def expr_stmt(self) -> ASTNode:
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
            return ASTNode(ASTNodeType.EXPRESSION_STMT)
        
        expr = self.expression()
        self.expect(TokenType.SEMICOLON)
        
        expr_stmt = ASTNode(ASTNodeType.EXPRESSION_STMT)
        expr_stmt.children = [expr]
        return expr_stmt
    
    def expression(self) -> ASTNode:
        return self.assignment_expr()
    
    def assignment_expr(self) -> ASTNode:
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
        if self.current_token and self.current_token.value in ['!', '-']:
            op = self.current_token.value
            self.advance()
            operand = self.unary_expr()
            unary = ASTNode(ASTNodeType.UNARY_EXPR, op)
            unary.right = operand
            return unary
        return self.primary()
    
    def primary(self) -> ASTNode:
        if not self.current_token:
            return ASTNode(ASTNodeType.LITERAL, "ERROR")
        
        token_type = self.current_token.type
        
        if token_type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            literal = ASTNode(ASTNodeType.LITERAL, value)
            literal.data_type = "float" if '.' in str(value) else "int"
            return literal
        
        if token_type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            literal = ASTNode(ASTNodeType.LITERAL, value)
            literal.data_type = "char*"
            return literal
        
        if token_type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                call_node = ASTNode(ASTNodeType.CALL_EXPR, name)
                if self.current_token and self.current_token.type != TokenType.RPAREN:
                    arg = self.expression()
                    call_node.children.append(arg)
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                        arg = self.expression()
                        call_node.children.append(arg)
                self.expect(TokenType.RPAREN)
                return call_node
            
            return ASTNode(ASTNodeType.VARIABLE, name)
        
        if token_type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        self.advance()
        return ASTNode(ASTNodeType.LITERAL, "ERROR")
    
    def _display_ast(self, node: ASTNode, indent: int = 0):
        prefix = "  " * indent
        if node.node_type == ASTNodeType.LITERAL:
            print(f"{prefix}|-- {node.node_type.value}: {node.value} (type: {node.data_type})")
        elif node.node_type in [ASTNodeType.VARIABLE, ASTNodeType.BINARY_EXPR, ASTNodeType.UNARY_EXPR, ASTNodeType.ASSIGN_EXPR]:
            print(f"{prefix}|-- {node.node_type.value}: {node.value}")
        else:
            print(f"{prefix}|-- {node.node_type.value}")
        
        for child in node.children:
            self._display_ast(child, indent + 1)
