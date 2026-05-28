import re
from typing import List, Dict, Any
from parser_module import ASTNode

class SecurityAnalyzer:
    """
    =========================================================================
    SECURITY ANALYZER
    =========================================================================
    Scans source code and AST for common security vulnerabilities.
    =========================================================================
    """
    
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
        self.malloc_vars: Dict[str, int] = {}    
        self.freed_vars: Dict[str, int] = {}      
        self.assigned_vars: set = set()
    
    def analyze(self) -> List[Dict[str, Any]]:
        print("\n" + "="*70)
        print("SECURITY ANALYSIS")
        print("="*70)
        
        self.vulnerabilities = []
        self.malloc_vars = {}
        self.freed_vars = {}
        self.assigned_vars = set()
        
        lines = self.source_code.split('\n')
        
        self._check_dangerous_functions(lines)
        self._check_format_string(lines)
        self._check_command_injection(lines)
        self._check_memory_management(lines)
        self._check_uninitialized_vars(lines)
        self._check_buffer_operations(lines)
        
        self._display_results()
        
        return self.vulnerabilities
    
    def _add_vuln(self, line: int, col: int, severity: str, category: str,
                   message: str, fix: str, fix_example: str = "", code_line: str = ""):
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
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue
            
            for func_name, info in self.DANGEROUS_FUNCTIONS.items():
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
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
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
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
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
        malloc_pattern = re.compile(r'(\w+)\s*=\s*(?:malloc|calloc|realloc)\s*\(')
        free_pattern = re.compile(r'free\s*\(\s*(\w+)\s*\)')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            m = malloc_pattern.search(line)
            if m:
                var_name = m.group(1)
                self.malloc_vars[var_name] = i
            
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
        declared = {}  
        assigned = set()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            m = re.match(r'(?:int|float|char|double|long)\s+(\w+)', stripped)
            if m:
                var_name = m.group(1)
                declared[var_name] = i
                if '=' in stripped:
                    assigned.add(var_name)
                continue
            
            m = re.match(r'(\w+)\s*=', stripped)
            if m:
                assigned.add(m.group(1))
                continue
            
            for var_name, decl_line in declared.items():
                if var_name in assigned:
                    continue
                if var_name in ('if', 'while', 'for', 'return', 'int', 'float', 'void', 'char'):
                    continue
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
                        assigned.add(var_name)  
    
    def _check_buffer_operations(self, lines: List[str]):
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
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
        print("\n" + "-" * 70)
        print("SECURITY ANALYSIS RESULTS")
        print("-" * 70)
        
        if not self.vulnerabilities:
            print("\n  [PASSED] No security vulnerabilities found!")
            print("-" * 70)
            return
        
        critical = sum(1 for v in self.vulnerabilities if v['severity'] == 'CRITICAL')
        high = sum(1 for v in self.vulnerabilities if v['severity'] == 'HIGH')
        medium = sum(1 for v in self.vulnerabilities if v['severity'] == 'MEDIUM')
        low = sum(1 for v in self.vulnerabilities if v['severity'] == 'LOW')
        
        print(f"\n  Found {len(self.vulnerabilities)} vulnerability(ies):")
        print(f"  CRITICAL: {critical}  HIGH: {high}  MEDIUM: {medium}  LOW: {low}")
        print()
        
        for i, vuln in enumerate(self.vulnerabilities, 1):
            sev = vuln['severity']
            sev_icon = {'CRITICAL': '[!!]', 'HIGH': '[!]', 'MEDIUM': '[~]', 'LOW': '[-]'}.get(sev, '[?]')
            
            print(f"  {sev_icon} #{i} [{sev}] Line {vuln['line']}: {vuln['category']}")
            print(f"     {vuln['message']}")
            print(f"     Fix: {vuln['fix']}")
            if vuln['code_line']:
                print(f"     Code: {vuln['code_line']}")
            print()
        
        print("-" * 70)
