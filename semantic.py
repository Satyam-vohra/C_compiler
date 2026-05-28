from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Any
from parser_module import ASTNode, ASTNodeType

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
    =========================================================================
    """
    
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.symbol_table: Dict[str, Symbol] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def analyze(self) -> ASTNode:
        print("\n" + "="*70)
        print("PHASE 3: SEMANTIC ANALYSIS (TYPE CHECKING)")
        print("="*70)
        
        self._analyze_node(self.ast)
        self._display_symbol_table()
        
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
        if node is None:
            return
        
        for child in node.children:
            self._analyze_node(child)
        
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
        elif node.node_type == ASTNodeType.CALL_EXPR:
            self._analyze_call_expr(node)
    
    def _analyze_call_expr(self, node: ASTNode):
        func_name = node.value
        if func_name not in self.symbol_table:
            self.warnings.append(f"Implicit declaration of function '{func_name}'")
        node.data_type = 'int'
    
    def _analyze_program(self, node: ASTNode):
        print("\nBuilding symbol table...")
    
    def _analyze_variable_decl(self, node: ASTNode):
        var_name = node.value
        var_type = node.data_type
        
        if var_name in self.symbol_table:
            self.errors.append(f"Variable '{var_name}' is already defined")
            return
        
        symbol = Symbol(var_name, SymbolType.VARIABLE, var_type, line=1)
        self.symbol_table[var_name] = symbol
        
        if node.children:
            init = node.children[0]
            if init and init.data_type != "unknown":
                if not self._is_compatible(var_type, init.data_type):
                    self.warnings.append(f"Type mismatch: cannot convert '{init.data_type}' to '{var_type}'")
    
    def _analyze_function_decl(self, node: ASTNode):
        func_name = node.children[1].value if len(node.children) > 1 else node.value
        return_type = node.children[0].value if node.children else "void"
        
        symbol = Symbol(func_name, SymbolType.FUNCTION, return_type, line=1)
        self.symbol_table[func_name] = symbol
    
    def _analyze_binary_expr(self, node: ASTNode):
        left_type = node.left.data_type if node.left else "unknown"
        right_type = node.right.data_type if node.right else "unknown"
        operator = node.value
        
        if operator in ['+', '-', '*', '/', '%']:
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                if left_type == 'float' or right_type == 'float':
                    node.data_type = 'float'
                else:
                    node.data_type = 'int'
            else:
                self.errors.append(f"Arithmetic operation '{operator}' requires numeric operands")
                node.data_type = 'error'
        
        elif operator in ['==', '!=', '<', '>', '<=', '>=']:
            node.data_type = 'int'
            if not self._is_compatible(left_type, right_type):
                self.warnings.append(f"Comparing incompatible types '{left_type}' and '{right_type}'")
        
        elif operator in ['&&', '||']:
            if left_type != 'int' or right_type != 'int':
                self.errors.append(f"Logical operation '{operator}' requires integer operands")
            node.data_type = 'int'
    
    def _analyze_unary_expr(self, node: ASTNode):
        operand_type = node.right.data_type if node.right else "unknown"
        if node.value == '!':
            node.data_type = 'int'
        elif node.value == '-':
            node.data_type = operand_type
    
    def _analyze_assign_expr(self, node: ASTNode):
        if node.left and node.left.node_type == ASTNodeType.VARIABLE:
            var_name = node.left.value
            
            if var_name not in self.symbol_table:
                self.errors.append(f"Variable '{var_name}' is not defined")
            
            if node.right:
                left_type = self.symbol_table.get(var_name, Symbol("", SymbolType.VARIABLE, "unknown")).data_type
                right_type = node.right.data_type
                
                if not self._is_compatible(left_type, right_type):
                    self.errors.append(f"Cannot assign '{right_type}' to variable of type '{left_type}'")
                
                node.data_type = left_type
    
    def _analyze_variable(self, node: ASTNode):
        var_name = node.value
        if var_name not in self.symbol_table:
            self.errors.append(f"Variable '{var_name}' is not defined")
            node.data_type = 'error'
            return
        
        symbol = self.symbol_table[var_name]
        node.data_type = symbol.data_type
    
    def _analyze_if_stmt(self, node: ASTNode):
        if node.children:
            condition = node.children[0]
            if condition.data_type != 'int':
                self.warnings.append("If condition should evaluate to integer (non-zero = true)")
    
    def _analyze_while_stmt(self, node: ASTNode):
        if node.children:
            condition = node.children[0]
            if condition.data_type != 'int':
                self.warnings.append("While condition should evaluate to integer")
    
    def _analyze_for_stmt(self, node: ASTNode):
        if len(node.children) > 1:
            condition = node.children[1]
            if condition.data_type not in ['int', 'error']:
                self.warnings.append("For condition should evaluate to integer")
    
    def _is_compatible(self, type1: str, type2: str) -> bool:
        if type1 == type2:
            return True
        if type1 == 'float' and type2 == 'int':
            return True
        return False
    
    def _display_symbol_table(self):
        print("\n" + "-" * 70)
        print("SYMBOL TABLE")
        print("-" * 70)
        print(f"{'Name':<20} {'Type':<15} {'Data Type':<15} {'Line':<10}")
        print("-" * 70)
        for name, symbol in self.symbol_table.items():
            print(f"{name:<20} {symbol.symbol_type.name:<15} {symbol.data_type:<15} {symbol.line:<10}")
        print("-" * 70)
        print(f"Total symbols: {len(self.symbol_table)}")
