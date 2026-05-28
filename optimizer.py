from typing import Dict, List, Optional, Any
from parser_module import ASTNode, ASTNodeType

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
        print("\n" + "="*70)
        print("PHASE 4: CODE OPTIMIZATION")
        print("="*70)
        
        self.optimizations_applied = []
        self.common_subexpressions = {}
        
        print("\nApplying optimizations...")
        
        self._constant_folding(self.ast)
        print(f"  [PASSED] Constant Folding: {sum(1 for x in self.optimizations_applied if 'Constant Folding' in x)} optimizations")
        
        self._common_subexpression_elimination(self.ast)
        print(f"  [PASSED] Common Subexpression Elimination: {sum(1 for x in self.optimizations_applied if 'CSE' in x)} optimizations")
        
        self._dead_code_elimination(self.ast)
        print(f"  [PASSED] Dead Code Elimination: {sum(1 for x in self.optimizations_applied if 'Dead Code' in x)} optimizations")
        
        self._display_optimization_summary()
        
        return self.ast
    
    def _constant_folding(self, node: ASTNode) -> ASTNode:
        if node is None:
            return node
        
        for i, child in enumerate(node.children):
            node.children[i] = self._constant_folding(child)
        
        if node.left:
            node.left = self._constant_folding(node.left)
        if node.right:
            node.right = self._constant_folding(node.right)
        
        if node.node_type == ASTNodeType.BINARY_EXPR:
            result = self._fold_binary_expr(node)
            if result is not None:
                node.node_type = ASTNodeType.LITERAL
                node.value = result
                node.data_type = self._get_result_type(node.left, node.right, node.value)
                self.optimizations_applied.append(f"Constant Folding: {node.left.value} {node.value} {node.right.value} -> {result}")
                node.left = None
                node.right = None
        
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
        if not node.left or not node.right:
            return None
        
        if node.left.node_type != ASTNodeType.LITERAL or node.right.node_type != ASTNodeType.LITERAL:
            return None
        
        try:
            left_val = self._to_number(node.left.value)
            right_val = self._to_number(node.right.value)
            op = node.value
            
            if op == '+': return left_val + right_val
            elif op == '-': return left_val - right_val
            elif op == '*': return left_val * right_val
            elif op == '/': return left_val // right_val if right_val != 0 else None
            elif op == '%': return left_val % right_val if right_val != 0 else None
            elif op == '==': return 1 if left_val == right_val else 0
            elif op == '!=': return 1 if left_val != right_val else 0
            elif op == '<': return 1 if left_val < right_val else 0
            elif op == '>': return 1 if left_val > right_val else 0
            elif op == '<=': return 1 if left_val <= right_val else 0
            elif op == '>=': return 1 if left_val >= right_val else 0
            elif op == '&&': return 1 if (left_val and right_val) else 0
            elif op == '||': return 1 if (left_val or right_val) else 0
        except (TypeError, ValueError):
            pass
        
        return None
    
    def _fold_unary_expr(self, node: ASTNode) -> Optional[Any]:
        if not node.right or node.right.node_type != ASTNodeType.LITERAL:
            return None
        
        try:
            val = self._to_number(node.right.value)
            if node.value == '-': return -val
            elif node.value == '!': return 0 if val else 1
        except (TypeError, ValueError):
            pass
        
        return None
    
    def _to_number(self, value: Any) -> Optional[int]:
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        return None
    
    def _get_result_type(self, left: ASTNode, right: ASTNode, result: Any) -> str:
        if isinstance(result, float) or (isinstance(result, str) and '.' in str(result)):
            return 'float'
        return 'int'
    
    def _common_subexpression_elimination(self, node: ASTNode) -> ASTNode:
        if node is None:
            return node
        
        for i, child in enumerate(node.children):
            node.children[i] = self._common_subexpression_elimination(child)
        
        if node.left:
            node.left = self._common_subexpression_elimination(node.left)
        if node.right:
            node.right = self._common_subexpression_elimination(node.right)
        
        if node.node_type == ASTNodeType.BINARY_EXPR:
            expr_key = self._get_expr_key(node)
            
            if expr_key in self.common_subexpressions:
                original = self.common_subexpressions[expr_key]
                self.optimizations_applied.append(f"CSE: Replaced duplicate expression with variable '{original.value}'")
                
                node.node_type = ASTNodeType.VARIABLE
                node.value = original.value
                node.left = None
                node.right = None
            else:
                var_name = f"_t{len(self.common_subexpressions)}"
                self.common_subexpressions[expr_key] = ASTNode(ASTNodeType.VARIABLE, var_name)
        
        return node
    
    def _get_expr_key(self, node: ASTNode) -> str:
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
        if node is None:
            return node
        
        for i, child in enumerate(node.children):
            node.children[i] = self._dead_code_elimination(child)
        
        if node.left:
            node.left = self._dead_code_elimination(node.left)
        if node.right:
            node.right = self._dead_code_elimination(node.right)
        
        if node.node_type == ASTNodeType.IF_STMT and len(node.children) >= 2:
            condition = node.children[0]
            
            if condition.node_type == ASTNodeType.LITERAL:
                cond_value = self._to_number(condition.value)
                
                if cond_value == 0:
                    if len(node.children) > 2 and node.children[2]:
                        self.optimizations_applied.append("Dead Code: Removed if-statement with always-false condition")
                        node.node_type = node.children[2].node_type
                        node.value = node.children[2].value
                        node.children = node.children[2].children
                    else:
                        return None
                
                elif cond_value != 0:
                    self.optimizations_applied.append("Dead Code: Removed always-true condition from if-statement")
                    then_branch = node.children[1]
                    node.node_type = then_branch.node_type
                    node.value = then_branch.value
                    node.children = then_branch.children
        
        if node.node_type == ASTNodeType.WHILE_STMT and len(node.children) >= 1:
            condition = node.children[0]
            
            if condition.node_type == ASTNodeType.LITERAL:
                cond_value = self._to_number(condition.value)
                
                if cond_value == 0:
                    self.optimizations_applied.append("Dead Code: Removed while-loop with always-false condition")
                    return None
        
        return node
    
    def _display_optimization_summary(self):
        print("\n" + "-" * 70)
        print("OPTIMIZATION SUMMARY")
        print("-" * 70)
        print(f"\nTotal optimizations applied: {len(self.optimizations_applied)}")
        
        if self.optimizations_applied:
            print("\nDetails:")
            for i, opt in enumerate(self.optimizations_applied, 1):
                print(f"  {i}. {opt}")
        
        print("-" * 70)
