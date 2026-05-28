from typing import List
from parser_module import ASTNode, ASTNodeType

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
        if node is None:
            return
        
        indent = "    " * self.indent_level
        
        if node.node_type == ASTNodeType.PROGRAM:
            for child in node.children:
                self._generate_node(child)
        
        elif node.node_type == ASTNodeType.VARIABLE_DECL:
            type_str = node.data_type
            var_name = node.value
            
            if node.children and node.children[0].node_type == ASTNodeType.LITERAL and '[]' in type_str:
                size = node.children[0].value
                base_type = type_str.replace('[]', '')
                self.code.append(f"{indent}{base_type} {var_name}[{size}];")
            elif node.children:
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
            
        elif node.node_type == ASTNodeType.CALL_EXPR:
            args = ", ".join([self._generate_expr(child) for child in node.children])
            return f"{node.value}({args})"
        
        return ""
