from parser_module import ASTNode, ASTNodeType

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class ASTInterpreter:
    """Executes the AST to provide real output"""
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}
        self.functions = {}
        self.output = []
        
    def execute(self):
        print("\n" + "="*70)
        print("              EXECUTION ENGINE")
        print("="*70)
        
        if self.ast and self.ast.node_type == ASTNodeType.PROGRAM:
            for child in self.ast.children:
                if child.node_type == ASTNodeType.FUNCTION_DECL:
                    func_name = child.children[1].value
                    self.functions[func_name] = child
                    
        if "main" in self.functions:
            try:
                self._execute_function("main", [])
            except ReturnException as e:
                self.output.append(f"[Program exited with return value: {e.value}]")
        else:
            self.output.append("[Warning: No 'main' function found]")
        
        for line in self.output:
            print(line)
        return self.output
        
    def _execute_function(self, name, args):
        func_node = self.functions.get(name)
        if not func_node:
            if name == "print":
                val = str(args[0]) if args else ""
                self.output.append(val)
                return 0
            elif name == "gets":
                self.output.append("[System] gets() called. Input simulated.")
                return 0
            return 0
            
        body = func_node.children[3]
        self._execute_node(body)
        return 0

    def _execute_node(self, node):
        if not node: return None
        
        if node.node_type == ASTNodeType.COMPOUND_STMT:
            for child in node.children:
                self._execute_node(child)
                
        elif node.node_type == ASTNodeType.VARIABLE_DECL:
            var_name = node.value
            if len(node.children) > 0:
                init_val = 0
                if node.children[-1].node_type != ASTNodeType.LITERAL or (node.children[-1].node_type == ASTNodeType.LITERAL and '[]' not in getattr(node, 'data_type', '')):
                    init_val = self._evaluate_expr(node.children[-1])
                self.variables[var_name] = init_val
            else:
                self.variables[var_name] = 0
                
        elif node.node_type == ASTNodeType.EXPRESSION_STMT:
            if node.children:
                self._evaluate_expr(node.children[0])
                
        elif node.node_type == ASTNodeType.IF_STMT:
            cond = self._evaluate_expr(node.children[0])
            if cond:
                self._execute_node(node.children[1])
            elif len(node.children) > 2 and node.children[2]:
                self._execute_node(node.children[2])
                
        elif node.node_type == ASTNodeType.WHILE_STMT:
            while self._evaluate_expr(node.children[0]):
                self._execute_node(node.children[1])
                
        elif node.node_type == ASTNodeType.RETURN_STMT:
            val = None
            if node.children:
                val = self._evaluate_expr(node.children[0])
            raise ReturnException(val)

    def _evaluate_expr(self, node):
        if not node: return 0
        if node.node_type == ASTNodeType.LITERAL:
            try:
                return int(node.value)
            except:
                try: return float(node.value)
                except: return str(node.value).strip('"')
                
        elif node.node_type == ASTNodeType.VARIABLE:
            return self.variables.get(node.value, 0)
            
        elif node.node_type == ASTNodeType.ASSIGN_EXPR:
            val = self._evaluate_expr(node.right)
            var_name = node.left.value
            self.variables[var_name] = val
            return val
            
        elif node.node_type == ASTNodeType.BINARY_EXPR:
            left = self._evaluate_expr(node.left)
            right = self._evaluate_expr(node.right)
            op = node.value
            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == '/': return left / right if right != 0 else 0
            elif op == '>': return left > right
            elif op == '<': return left < right
            elif op == '>=': return left >= right
            elif op == '<=': return left <= right
            elif op == '==': return left == right
            elif op == '!=': return left != right
            
        elif node.node_type == ASTNodeType.CALL_EXPR:
            args = [self._evaluate_expr(c) for c in node.children]
            return self._execute_function(node.value, args)
            
        return 0
