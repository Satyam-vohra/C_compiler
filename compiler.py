from typing import List
from lexer import LexicalAnalyzer, Token
from parser_module import SyntaxAnalyzer, ASTNode
from semantic import SemanticAnalyzer
from optimizer import Optimizer
from security import SecurityAnalyzer
from honeypot import HoneypotLogger
from codegen import CodeGenerator
from interpreter import ASTInterpreter

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
    5. Security Analysis
    6. Honeypot Logging
    7. Code Generation
    8. Execution Engine
    =========================================================================
    """
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.ast: ASTNode = None
        self.semantic_ast: ASTNode = None
        self.optimized_ast: ASTNode = None
        self.generated_code: str = ""
        self.execution_output: List[str] = []
        self.parser: SyntaxAnalyzer = None
        
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
        self.parser = SyntaxAnalyzer(self.tokens)
        self.ast = self.parser.parse()
        
        # Phase 3: Semantic Analysis
        semantic_analyzer = SemanticAnalyzer(self.ast)
        self.semantic_ast = semantic_analyzer.analyze()
        
        # Phase 4: Code Optimization
        optimizer = Optimizer(self.semantic_ast)
        self.optimized_ast = optimizer.optimize()
        
        # Phase 5: Security Analysis
        security_analyzer = SecurityAnalyzer(self.source_code, self.optimized_ast)
        vulns = security_analyzer.analyze()
        
        # Phase 6: Honeypot Logging
        honeypot = HoneypotLogger()
        for vuln in vulns:
            honeypot.log_vulnerability(vuln)
        if vulns:
            honeypot.display_logs()
        
        # Phase 7: Code Generation
        code_generator = CodeGenerator(self.optimized_ast)
        self.generated_code = code_generator.generate()
        
        # Phase 8: Execution Engine
        interpreter = ASTInterpreter(self.optimized_ast)
        self.execution_output = interpreter.execute()
        
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
  [PASSED] Phase 4: Code Optimization   (Optimizations Applied)
  [PASSED] Phase 5: Security Analysis   (Vulnerability Scan)
  [PASSED] Phase 6: Honeypot Logging    (Attack Pattern Tracking)
  [PASSED] Phase 7: Code Generation     (Output Generated)
  [PASSED] Phase 8: Execution Engine    (AST Evaluated)
  ==============================================================================
""")

if __name__ == '__main__':
    demo_code = """int main() {
    char buffer[50];
    gets(buffer);   // unsafe function (honeypot trigger)

    int a = 5;
    int b = 10;
    int result = a + b * 2;

    print(result);  // print intermediate value

    if (result > 20) {
        return 1;
    } else {
        return 0;
    }
}"""
    compiler = Compiler(demo_code)
    compiler.compile()

