from tkinter import *
from tkinter import ttk, scrolledtext
import os
import re
import subprocess
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Import compiler modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compiler import (
    LexicalAnalyzer, SyntaxAnalyzer, SemanticAnalyzer,
    Optimizer, CodeGenerator, Compiler, SecurityAnalyzer
)

# =============================================================================
# THEME COLORS
# =============================================================================
BG_DARK = '#1e1e1e'
BG_MEDIUM = '#282a36'
BG_LIGHT = '#44475a'
FG_TEXT = '#f8f8f2'
FG_COMMENT = '#6272a4'
GREEN = '#50fa7b'
CYAN = '#8be9fd'
PINK = '#FF79C6'
PURPLE = '#BD93F9'
YELLOW = '#F1FA8C'
RED = '#FF5555'
ORANGE = '#FFB86C'

TOKEN_TYPES = {
    'keyword': PINK,
    'identifier': FG_TEXT,
    'number': PURPLE,
    'string': YELLOW,
    'operator': RED,
    'comment': FG_COMMENT,
    'bracket': CYAN,
}

C_KEYWORDS = [
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
    'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',
    'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
    'volatile', 'while'
]

C_FUNCTIONS = [
    'printf', 'scanf', 'fprintf', 'fscanf', 'sprintf', 'sscanf',
    'perror', 'fopen', 'fclose', 'fread', 'fwrite', 'fgets', 'fputs',
    'putchar', 'getchar', 'puts', 'gets', 'feof', 'fseek', 'ftell',
    'rewind', 'fflush', 'malloc', 'calloc', 'realloc', 'free', 'exit',
    'system', 'abs', 'labs', 'atoi', 'atof', 'atol', 'rand', 'srand',
    'qsort', 'bsearch', 'strlen', 'strcpy', 'strncpy', 'strcat',
    'strncat', 'strcmp', 'strncmp', 'strchr', 'strrchr', 'strstr',
    'memcpy', 'memmove', 'memcmp', 'memset', 'ceil', 'floor', 'fabs',
    'sqrt', 'pow', 'exp', 'log', 'log10', 'sin', 'cos', 'tan',
]

C_HEADERS = [
    'stdio.h', 'stdlib.h', 'string.h', 'math.h', 'time.h', 'ctype.h',
    'stdbool.h', 'stdint.h', 'limits.h', 'float.h', 'stddef.h',
    'assert.h', 'errno.h', 'locale.h', 'signal.h',
]

TOKEN_PATTERNS = {
    'comment': r'//.*?$|/\*[\s\S]*?\*/',
    'string': r'"(?:\\.|[^"\\])*?"',
    'keyword': r'\b(?:' + '|'.join(C_KEYWORDS) + r')\b',
    'number': r'\b\d+(\.\d+)?\b',
    'operator': r'==|!=|<=|>=|\+\+|--|&&|\|\||\+=|-=|\*=|/=|[%&|^!<>]=?|[+\-*/%=]',
    'bracket': r'[\{\}\[\]\(\)]',
    'identifier': r'\b(?!' + '|'.join(C_KEYWORDS) + r'\b)[a-zA-Z_][a-zA-Z0-9_]*\b'
}


# =============================================================================
# ERROR SUGGESTION DATABASE
# =============================================================================
ERROR_SUGGESTIONS = {
    # Missing semicolon
    "expected.*SEMICOLON": (
        "Missing semicolon ';' at end of statement",
        "Har statement ke end mein ';' lagao.\n"
        "  Example:  int x = 10;   (not: int x = 10)"
    ),
    "expected.*';'": (
        "Missing semicolon",
        "Statement ke end mein ';' lagao."
    ),
    "expected ';'" : (
        "Missing semicolon ';' at end of statement",
        "Statement ke last mein ';' lagao.\n"
        "  Example:  int x = 5;"
    ),

    # Missing closing brace
    "expected.*RBRACE": (
        "Missing closing brace '}'",
        "Ek '}' bracket missing hai. Opening '{' ka matching '}' lagao.\n"
        "  Har { ke saath } lagana zaroori hai."
    ),
    "expected.*'}'": (
        "Missing closing brace '}'",
        "Opening '{' ka matching '}' lagao."
    ),

    # Missing closing parenthesis
    "expected.*RPAREN": (
        "Missing closing parenthesis ')'",
        "Ek ')' missing hai. Opening '(' ka matching ')' lagao.\n"
        "  Example:  if (x > 5) { ... }   (not: if (x > 5 { ... })"
    ),
    "expected.*')'": (
        "Missing closing parenthesis ')'",
        "Opening '(' ka matching ')' lagao."
    ),

    # Missing opening parenthesis
    "expected.*LPAREN": (
        "Missing opening parenthesis '('",
        "if/while/for ke baad '(' lagao.\n"
        "  Example:  if (condition) { ... }   (not: if condition { ... })"
    ),
    "expected.*'('": (
        "Missing opening parenthesis '('",
        "if/while/for ke baad '(' lagao."
    ),

    # Undeclared variable
    "not defined": (
        "Variable is not declared",
        "Ye variable declare nahi hua. Pehle declare karo:\n"
        "  Example:  int variable_name;"
    ),
    "undeclared": (
        "Undeclared variable",
        "Variable ko use karne se pehle declare karo."
    ),
    "undefined": (
        "Undefined variable or function",
        "Is naam ka koi variable/function declare nahi hai.\n"
        "  Spelling check karo ya pehle declare karo."
    ),

    # Type mismatch
    "type mismatch": (
        "Type mismatch error",
        "Dono sides ka type same hona chahiye.\n"
        "  int mein int assign karo, float mein float."
    ),
    "incompatible types": (
        "Incompatible types",
        "Galat type ka value assign kar rahe ho.\n"
        "  Example: int x = \"hello\";  // ERROR: string cannot be assigned to int"
    ),
    "cannot assign": (
        "Assignment type error",
        "Right side ka type left side se match nahi karta.\n"
        "  Type conversion ki zaroorat hai."
    ),

    # Arithmetic errors
    "arithmetic operation": (
        "Arithmetic operand error",
        "Arithmetic operations ke liye numeric values chahiye.\n"
        "  int ya float type ka value use karo."
    ),
    "numeric operands": (
        "Numeric operand required",
        "+, -, *, / operators ke liye numbers chahiye."
    ),

    # Missing return
    "control reaches end of non-void function": (
        "Non-void function must return a value",
        "Function ka return type int/float hai toh return statement lagao.\n"
        "  Example:  return 0;"
    ),
    "return": (
        "Return statement issue",
        "Function mein return statement check karo."
    ),

    # Missing header
    "implicitly declaring library function": (
        "Missing #include header",
        "Ye function use karne ke liye header file include karo.\n"
        "  printf/scanf ke liye:  #include <stdio.h>\n"
        "  malloc/free ke liye:   #include <stdlib.h>\n"
        "  strlen/strcpy ke liye: #include <string.h>"
    ),
    "undeclared.*printf": (
        "printf not declared - missing #include <stdio.h>",
        "File ke sabse upar ye line likho:\n"
        "  #include <stdio.h>"
    ),
    "undeclared.*scanf": (
        "scanf not declared - missing #include <stdio.h>",
        "File ke sabse upar ye line likho:\n"
        "  #include <stdio.h>"
    ),

    # Unused variable
    "unused variable": (
        "Unused variable warning",
        "Ye variable declare kiya hai par use nahi kiya.\n"
        "  Ya toh use karo ya hata do."
    ),

    # Duplicate declaration
    "redefinition": (
        "Variable already defined",
        "Ye variable pehle se declared hai. Dobara declare mat karo.\n"
        "  Alag naam use karo."
    ),
    "already defined": (
        "Duplicate declaration",
        "Is naam ka variable/function pehle se hai."
    ),

    # Missing main
    "undefined reference to.*main": (
        "main() function missing",
        "Har C program mein main() function hona zaroori hai.\n"
        "  Example:  int main() { return 0; }"
    ),
    "ld returned": (
        "Linker error - main() function missing ya library issue",
        "main() function likho ya library link karo."
    ),

    # Division by zero
    "division by zero": (
        "Division by zero error",
        "Zero se divide nahi kar sakte.\n"
        "  Pehle check karo divisor zero toh nahi hai."
    ),

    # Expected expression
    "expected expression": (
        "Expected expression",
        "Yahan ek value/variable/expression chahiye.\n"
        "  Example:  int x = ;  // ERROR: expression missing after ="
    ),
    "expected.*expression": (
        "Expression expected",
        "Operator ke baad ek value chahiye."
    ),

    # Stray/extra characters
    "stray": (
        "Stray character in program",
        "Koi extra/wrong character hai code mein.\n"
        "  Special characters check karo."
    ),

    # Missing brace at end
    "expected declaration or statement": (
        "Expected declaration or statement",
        "Yahan koi valid code likhna hai.\n"
        "  Extra '}' ya galat jagah pe code likh rahe ho."
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_tkinter_index(text_widget, char_index):
    line = text_widget.index(f"1.0+{char_index}c").split(".")
    return f"{line[0]}.{line[1]}"


def highlight_code(text_widget, code):
    for token in TOKEN_TYPES.keys():
        text_widget.tag_remove(token, "1.0", END)
    for token_type, pattern in TOKEN_PATTERNS.items():
        for match in re.finditer(pattern, code, re.MULTILINE):
            start, end = match.span()
            start_index = get_tkinter_index(text_widget, start)
            end_index = get_tkinter_index(text_widget, end)
            text_widget.tag_add(token_type, start_index, end_index)
            text_widget.tag_configure(token_type, foreground=TOKEN_TYPES[token_type])
    return code


def compute_lps(pattern):
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_prefix_match(text, pattern):
    lps = compute_lps(pattern)
    i = j = 0
    while i < len(text) and j < len(pattern):
        if text[i] == pattern[j]:
            i += 1
            j += 1
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1
    return j == len(pattern)


def autocomplete_kmp(prefix, keyword_list):
    return [word for word in keyword_list if kmp_prefix_match(word, prefix)]


def get_suggestion(error_text):
    """Find matching suggestion for an error message"""
    error_lower = error_text.lower()
    for pattern, (title, suggestion) in ERROR_SUGGESTIONS.items():
        if re.search(pattern.lower(), error_lower):
            return title, suggestion
    return None, None


def get_line_source_code(code, line_num):
    """Get the source code for a specific line"""
    lines = code.split('\n')
    if 1 <= line_num <= len(lines):
        return lines[line_num - 1]
    return ""


def count_braces(code):
    """Count opening and closing braces to detect mismatch"""
    opens = code.count('{')
    closes = code.count('}')
    return opens, closes


def count_parens(code):
    """Count opening and closing parentheses"""
    opens = code.count('(')
    closes = code.count(')')
    return opens, closes


def check_missing_semicolons(code):
    """Check for lines that likely need semicolons"""
    errors = []
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('#'):
            continue
        # Lines that end without ; and are not block starters
        if (stripped and not stripped.endswith(';') and not stripped.endswith('{')
                and not stripped.endswith('}') and not stripped.endswith('(')
                and not stripped.endswith(',') and not stripped.endswith('\\')
                and not re.match(r'^(if|else|for|while|do|switch|return\s*$|int|float|char|void)\b.*\)\s*$', stripped)
                and not stripped.startswith('else')
                and not re.match(r'^(int|float|char|void)\s+\w+\s*\(', stripped)  # function decl
                ):
            # Check if it looks like a statement that needs ;
            if re.match(r'^(int|float|char|void)\s+\w+', stripped) or \
               re.match(r'^\w+\s*=', stripped) or \
               re.match(r'^return\s+', stripped) or \
               re.match(r'^(printf|scanf)\s*\(', stripped) or \
               re.match(r'^\w+\s*\([^)]*\)\s*$', stripped):
                errors.append(i)
    return errors


# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================

class CCompilerIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("C Compiler IDE")
        self.root.configure(bg=BG_DARK)

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}")
        self.root.resizable(True, True)

        self.current_file = None
        self.font_config = ('Consolas', 16)
        self.font_bold = ('Consolas', 12, 'bold')
        self.tokens_cache = None
        self.ast_cache = None
        self.all_errors = []
        self._error_debounce = None

        self._build_toolbar()
        self._build_phase_buttons()
        self._build_paned_layout()
        self._build_autocomplete()
        self._build_menubar()

        self.update_line_numbers()
        self.set_default_code()

    # -------------------------------------------------------------------------
    # TOOLBAR
    # -------------------------------------------------------------------------
    def _build_toolbar(self):
        toolbar = Frame(self.root, bg=BG_MEDIUM, height=35)
        toolbar.pack(fill=X, side=TOP)

        Button(toolbar, text="FILE", padx=15, pady=2, bg=GREEN, fg=BG_MEDIUM,
               activebackground=CYAN, activeforeground=BG_MEDIUM, borderwidth=0,
               font=self.font_bold, command=self._show_file_menu).pack(side=LEFT, padx=(10, 5), pady=3)

        Label(toolbar, text="C Compiler IDE", bg=BG_MEDIUM, fg=GREEN,
              font=('Consolas', 14, 'bold')).pack(side=LEFT, padx=20)

        # Error count badge
        self.error_badge = Label(toolbar, text=" 0 Errors ", bg=BG_MEDIUM, fg=GREEN,
                                 font=('Consolas', 10, 'bold'))
        self.error_badge.pack(side=RIGHT, padx=15)

        # Status label
        self.status_label = Label(toolbar, text="Ready", bg=BG_MEDIUM, fg=FG_COMMENT,
                                  font=('Consolas', 10))
        self.status_label.pack(side=RIGHT, padx=15)

    # -------------------------------------------------------------------------
    # PANED LAYOUT (Editor + Terminal with drag resize)
    # -------------------------------------------------------------------------
    def _build_paned_layout(self):
        # Main vertical PanedWindow
        self.paned = PanedWindow(self.root, orient=VERTICAL, bg=BG_MEDIUM,
                                 sashwidth=8, sashrelief=FLAT, sashcursor='sb_v_double_arrow')
        self.paned.pack(fill=BOTH, expand=True, padx=5, pady=2)

        # ---- TOP PANE: Code Editor ----
        editor_frame = Frame(self.paned, bg=BG_MEDIUM)
        self.paned.add(editor_frame, minsize=150)

        self.line_numbers = Text(editor_frame, width=5, padx=8, pady=8,
                                 bg=BG_DARK, fg=FG_COMMENT, insertbackground='white',
                                 font=self.font_config, state=DISABLED, relief=FLAT)
        self.line_numbers.pack(side=LEFT, fill=Y)

        self.text_area = Text(editor_frame, padx=8, pady=8, bg=BG_DARK, fg=FG_TEXT,
                              insertbackground='white', selectbackground=BG_LIGHT,
                              font=self.font_config, wrap="none", relief=FLAT, undo=True)

        scrollbar = ttk.Scrollbar(editor_frame, command=self._sync_scroll)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.text_area.pack(side=LEFT, fill=BOTH, expand=True)
        self.text_area.configure(yscrollcommand=lambda *a: (scrollbar.set(*a), self._scroll_ln(*a)))

        # Bindings
        self.text_area.bind("<KeyRelease>", self._on_key_release)
        self.text_area.bind("<MouseWheel>", self._on_mousewheel)
        self.line_numbers.bind("<MouseWheel>", self._on_mousewheel)
        self.text_area.bind("<Escape>", lambda e: self._hide_autocomplete())
        self.text_area.bind("<Down>", self._focus_autocomplete)
        self.text_area.bind("<Tab>", self._insert_tab)
        self.text_area.tag_configure("error_line", background='#5a2020', foreground='#ff9999')
        self.text_area.tag_configure("error_underline", underline=True, underlinefg=RED)

        # ---- BOTTOM PANE: Output Terminal ----
        term_frame = Frame(self.paned, bg=BG_MEDIUM)
        self.paned.add(term_frame, minsize=80)

        # Terminal header with drag hint
        term_header = Frame(term_frame, bg=BG_MEDIUM)
        term_header.pack(fill=X)
        Label(term_header, text="OUTPUT", bg=BG_MEDIUM, fg=GREEN,
              font=('Consolas', 10, 'bold')).pack(side=LEFT, padx=5, pady=(3, 0))
        Label(term_header, text="[ drag border to resize ]", bg=BG_MEDIUM, fg=FG_COMMENT,
              font=('Consolas', 9)).pack(side=RIGHT, padx=5, pady=(3, 0))

        self.terminal = scrolledtext.ScrolledText(
            term_frame, height=8, bg=BG_DARK, fg=FG_TEXT,
            insertbackground='white', font=('Consolas', 11),
            wrap="word", relief=FLAT
        )
        self.terminal.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))
        self.terminal.config(state=DISABLED)

        # Configure tags for colored output
        self.terminal.tag_configure("phase_header", foreground=GREEN, font=('Consolas', 11, 'bold'))
        self.terminal.tag_configure("phase_sub", foreground=CYAN, font=('Consolas', 10, 'bold'))
        self.terminal.tag_configure("token_type", foreground=PINK)
        self.terminal.tag_configure("token_val", foreground=YELLOW)
        self.terminal.tag_configure("ast_node", foreground=PURPLE)
        self.terminal.tag_configure("symbol", foreground=ORANGE)
        self.terminal.tag_configure("error", foreground=RED, font=('Consolas', 10, 'bold'))
        self.terminal.tag_configure("error_line_ref", foreground=ORANGE, font=('Consolas', 11, 'bold'))
        self.terminal.tag_configure("success", foreground=GREEN)
        self.terminal.tag_configure("warning", foreground=YELLOW)
        self.terminal.tag_configure("code_out", foreground=CYAN, font=('Consolas', 11))
        self.terminal.tag_configure("suggestion", foreground='#bd93f9', font=('Consolas', 10, 'italic'))
        self.terminal.tag_configure("error_code", foreground=ORANGE, font=('Consolas', 11))

    def _insert_tab(self, event):
        self.text_area.insert(INSERT, "    ")
        return "break"

    # -------------------------------------------------------------------------
    # PHASE BUTTONS
    # -------------------------------------------------------------------------
    def _build_phase_buttons(self):
        btn_frame = Frame(self.root, bg=BG_DARK, height=40)
        btn_frame.pack(fill=X, padx=5, pady=(2, 0))

        phases = [
            ("LEXER", self._run_lexer, CYAN),
            ("PARSER", self._run_parser, PINK),
            ("SEMANTIC", self._run_semantic, PURPLE),
            ("SECURITY", self._run_security, RED),
            ("OPTIMIZE", self._run_optimizer, YELLOW),
            ("COMPILE", self._run_compile, ORANGE),
            ("RUN (GCC)", self._run_gcc, GREEN),
        ]

        for text, cmd, color in phases:
            b = Button(btn_frame, text=text, padx=12, pady=3,
                       bg=color, fg=BG_MEDIUM, activebackground=color,
                       activeforeground=BG_MEDIUM, borderwidth=0,
                       font=('Consolas', 11, 'bold'), command=cmd)
            b.pack(side=LEFT, padx=(0, 5), pady=2)

        Button(btn_frame, text="CLEAR", padx=10, pady=3,
               bg=RED, fg='white', activebackground=RED, activeforeground='white',
               borderwidth=0, font=('Consolas', 10, 'bold'),
               command=self._clear_terminal).pack(side=RIGHT, padx=(0, 5), pady=2)


    def _write_terminal(self, text, tag=None):
        self.terminal.config(state=NORMAL)
        if tag:
            self.terminal.insert(END, text, tag)
        else:
            self.terminal.insert(END, text)
        self.terminal.see(END)
        self.terminal.config(state=DISABLED)

    def _clear_terminal(self):
        self.terminal.config(state=NORMAL)
        self.terminal.delete("1.0", END)
        self.terminal.config(state=DISABLED)
        self.status_label.config(text="Output cleared")

    # -------------------------------------------------------------------------
    # AUTOCOMPLETE
    # -------------------------------------------------------------------------
    def _build_autocomplete(self):
        self.autocomplete_lb = Listbox(self.root, height=6, bg=BG_DARK, fg=FG_TEXT,
                                       font=('Consolas', 12), highlightthickness=0,
                                       selectbackground=BG_LIGHT)
        self.autocomplete_lb.place_forget()
        self.autocomplete_lb.bind("<Return>", self._insert_autocomplete)
        self.autocomplete_lb.bind("<ButtonRelease-1>", self._insert_autocomplete)

    def _hide_autocomplete(self):
        self.autocomplete_lb.place_forget()

    def _show_autocomplete(self):
        cursor = self.text_area.index(INSERT)
        line, col = map(int, cursor.split('.'))
        line_text = self.text_area.get(f"{line}.0", f"{line}.end")
        match = re.search(r'\w*$', line_text[:col])
        if not match:
            self._hide_autocomplete()
            return
        prefix = match.group(0)
        if not prefix or not prefix.isalpha():
            self._hide_autocomplete()
            return

        if line_text.strip().startswith("#include"):
            suggestions = autocomplete_kmp(prefix, C_HEADERS)
        else:
            suggestions = autocomplete_kmp(prefix, C_KEYWORDS + C_FUNCTIONS)

        if not suggestions:
            self._hide_autocomplete()
            return

        self.autocomplete_lb.delete(0, END)
        for word in suggestions:
            self.autocomplete_lb.insert(END, word)

        bbox = self.text_area.bbox(cursor)
        if not bbox:
            self._hide_autocomplete()
            return
        x, y, _, h = bbox
        self.autocomplete_lb.place(x=self.text_area.winfo_rootx() + x,
                                   y=self.text_area.winfo_rooty() + y + h)
        self.autocomplete_lb.lift()

    def _insert_autocomplete(self, event=None):
        if self.autocomplete_lb.size() == 0:
            return
        selected = self.autocomplete_lb.get(ACTIVE)
        cursor = self.text_area.index(INSERT)
        line, col = map(int, cursor.split('.'))
        line_text = self.text_area.get(f"{line}.0", f"{line}.end")
        match = re.search(r'\w*$', line_text[:col])
        if match:
            sc = match.start()
            self.text_area.delete(f"{line}.{sc}", f"{line}.{col}")
            self.text_area.insert(f"{line}.{sc}", selected)
        self._hide_autocomplete()
        self.text_area.focus_set()
        return "break"

    def _focus_autocomplete(self, event):
        if self.autocomplete_lb.winfo_ismapped():
            self.autocomplete_lb.focus_set()
            self.autocomplete_lb.selection_set(0)
            return "break"

    # -------------------------------------------------------------------------
    # MENUBAR
    # -------------------------------------------------------------------------
    def _build_menubar(self):
        self.file_menu = Menu(self.root, tearoff=0, bg=BG_LIGHT, fg=FG_TEXT,
                              activebackground=BG_LIGHT, activeforeground=FG_TEXT,
                              font=('Consolas', 10))
        self.file_menu.add_command(label="New File    Ctrl+N", command=self.new_file)
        self.file_menu.add_command(label="Open        Ctrl+O", command=self.open_file)
        self.file_menu.add_command(label="Save        Ctrl+S", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as_file)

        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-r>", lambda e: self._run_gcc())

    def _show_file_menu(self):
        try:
            self.file_menu.tk_popup(self.root.winfo_rootx() + 15,
                                    self.root.winfo_rooty() + 35)
        finally:
            self.file_menu.grab_release()

    # -------------------------------------------------------------------------
    # SCROLL / LINE NUMBERS
    # -------------------------------------------------------------------------
    def _sync_scroll(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def _scroll_ln(self, *args):
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def _on_mousewheel(self, event):
        self.text_area.yview_scroll(-1 * (event.delta // 120), "units")
        self.line_numbers.yview_scroll(-1 * (event.delta // 120), "units")

    def update_line_numbers(self):
        self.line_numbers.config(state=NORMAL)
        self.line_numbers.delete(1.0, END)
        lines = self.text_area.index('end-1c').split('.')[0]
        ln = "\n".join(str(i) for i in range(1, int(lines) + 1))
        self.line_numbers.insert(END, ln)
        self.line_numbers.config(state=DISABLED)
        self._scroll_ln()

    def _on_key_release(self, event=None):
        self.update_line_numbers()
        code = self.text_area.get("1.0", END)
        highlight_code(self.text_area, code)
        # Debounce error checking - only check after 500ms pause
        if self._error_debounce:
            self.root.after_cancel(self._error_debounce)
        self._error_debounce = self.root.after(600, lambda: self._check_all_errors(code))
        self._show_autocomplete()

    # =========================================================================
    # COMPREHENSIVE ERROR CHECKING
    # =========================================================================

    def _check_all_errors(self, code):
        """Run all error checks and highlight + display errors"""
        self.all_errors = []
        self.text_area.tag_remove("error_line", "1.0", END)
        self.text_area.tag_remove("error_underline", "1.0", END)

        if not code.strip():
            self._update_error_badge(0)
            return

        # 1. Check GCC errors
        gcc_errors = self._get_gcc_errors(code)
        self.all_errors.extend(gcc_errors)

        # 2. Check custom compiler parser errors
        parser_errors = self._get_parser_errors(code)
        self.all_errors.extend(parser_errors)

        # 3. Check brace/paren mismatch
        brace_errors = self._check_brace_paren_errors(code)
        self.all_errors.extend(brace_errors)

        # 4. Check missing semicolons (custom check)
        semi_errors = self._check_semicolon_errors(code)
        self.all_errors.extend(semi_errors)

        # 5. Check missing headers
        header_errors = self._check_missing_headers(code)
        self.all_errors.extend(header_errors)

        # Highlight error lines in editor
        seen_lines = set()
        for err in self.all_errors:
            line = err.get('line', 0)
            if line > 0 and line not in seen_lines:
                seen_lines.add(line)
                self.text_area.tag_add("error_line", f"{line}.0", f"{line}.end")

        self._update_error_badge(len(self.all_errors))

    def _get_gcc_errors(self, code):
        """Get errors from GCC compiler"""
        errors = []
        try:
            with open("temp_live.c", "w") as f:
                f.write(code)
            proc = subprocess.run(
                ["gcc", "-fsyntax-only", "temp_live.c"],
                capture_output=True, text=True
            )
            if proc.stderr:
                for line in proc.stderr.splitlines():
                    m = re.search(r"temp_live\.c:(\d+):(\d+):\s*(error|warning):\s*(.*)", line)
                    if m:
                        line_num = int(m.group(1))
                        col_num = int(m.group(2))
                        err_type = m.group(3)
                        msg = m.group(4).strip()
                        title, suggestion = get_suggestion(msg)
                        errors.append({
                            'line': line_num,
                            'column': col_num,
                            'type': err_type,
                            'message': msg,
                            'title': title or msg,
                            'suggestion': suggestion or "Code check karo aur error fix karo.",
                            'source': 'gcc'
                        })
        except FileNotFoundError:
            pass
        return errors

    def _get_parser_errors(self, code):
        """Get errors from custom compiler parser"""
        errors = []
        try:
            lexer = LexicalAnalyzer(code)
            tokens = lexer.tokenize()
            parser = SyntaxAnalyzer(tokens)

            buf = io.StringIO()
            with redirect_stdout(buf):
                parser.parse()

            for err in parser.errors:
                line = err.get('line', 0)
                col = err.get('column', 0)
                msg = err.get('message', '')
                expected = err.get('expected', '')
                got = err.get('got', '')

                title, suggestion = get_suggestion(msg)
                if not suggestion:
                    # Generate a generic suggestion based on expected/got
                    suggestion = self._generate_suggestion(expected, got, code, line)

                errors.append({
                    'line': line,
                    'column': col,
                    'type': 'error',
                    'message': msg,
                    'title': title or f"Syntax Error: Expected {expected}",
                    'suggestion': suggestion,
                    'source': 'parser'
                })
        except Exception:
            pass
        return errors

    def _generate_suggestion(self, expected, got, code, line):
        """Generate a helpful suggestion based on context"""
        line_src = get_line_source_code(code, line)

        if 'SEMICOLON' in expected:
            return (
                f"Is line ke end mein ';' lagao.\n"
                f"  Current line: {line_src.strip()}\n"
                f"  Fix: {line_src.strip()};"
            )
        if 'RBRACE' in expected or '}' in expected:
            opens, closes = count_braces(code)
            return (
                f"Closing '}}' bracket missing hai.\n"
                f"  Total '{{' : {opens}, Total '}}' : {closes}\n"
                f"  {opens - closes} aur '}}' lagao."
            )
        if 'RPAREN' in expected or ')' in expected:
            opens, closes = count_parens(code)
            return (
                f"Closing ')' bracket missing hai.\n"
                f"  Total '(' : {opens}, Total ')' : {closes}\n"
                f"  {opens - closes} aur ')' lagao."
            )
        if 'LPAREN' in expected:
            return "if/while/for ke baad '(' lagao.\n  Example: if (condition) { ... }"
        if got == 'EOF_TOKEN':
            return "File end ho gayi par code incomplete hai.\n  Missing '}' ya ';' check karo."

        return f"Line {line} pe '{expected}' expected hai par '{got}' mila."

    def _check_brace_paren_errors(self, code):
        """Check for mismatched braces and parentheses"""
        errors = []
        # Remove strings and comments before counting
        clean = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        clean = re.sub(r'/\*[\s\S]*?\*/', '', clean)
        clean = re.sub(r'"(?:\\.|[^"\\])*?"', '', clean)

        opens_b = clean.count('{')
        closes_b = clean.count('}')
        if opens_b != closes_b:
            diff = opens_b - closes_b
            # Find the last opening brace line
            last_open_line = 0
            for i, line in enumerate(code.split('\n'), 1):
                if '{' in line:
                    last_open_line = i
            if diff > 0:
                errors.append({
                    'line': last_open_line,
                    'column': 1,
                    'type': 'error',
                    'message': f"Missing {diff} closing brace(s) '}}'",
                    'title': f"Bracket mismatch: {diff} '}}' missing",
                    'suggestion': (
                        f"{diff} closing '}}' bracket missing hai.\n"
                        f"  Total '{{' : {opens_b}, Total '}}' : {closes_b}\n"
                        f"  Sabse last wali '{{' ke liye '}}' lagao."
                    ),
                    'source': 'bracket_check'
                })

        opens_p = clean.count('(')
        closes_p = clean.count(')')
        if opens_p != closes_p:
            diff = opens_p - closes_p
            last_paren_line = 0
            for i, line in enumerate(code.split('\n'), 1):
                if '(' in line:
                    last_paren_line = i
            if diff > 0:
                errors.append({
                    'line': last_paren_line,
                    'column': 1,
                    'type': 'error',
                    'message': f"Missing {diff} closing parenthesis ')'",
                    'title': f"Parenthesis mismatch: {diff} ')' missing",
                    'suggestion': (
                        f"{diff} closing ')' bracket missing hai.\n"
                        f"  Total '(' : {opens_p}, Total ')' : {closes_p}\n"
                        f"  Har '(' ke saath ')' lagao."
                    ),
                    'source': 'bracket_check'
                })

        return errors

    def _check_semicolon_errors(self, code):
        """Check for lines that are missing semicolons"""
        errors = []
        bad_lines = check_missing_semicolons(code)
        for ln in bad_lines:
            line_src = get_line_source_code(code, ln)
            errors.append({
                'line': ln,
                'column': len(line_src),
                'type': 'error',
                'message': "Possible missing semicolon ';'",
                'title': "Missing semicolon ';' ?",
                'suggestion': (
                    f"Is line mein ';' lagana zaroori ho sakta hai.\n"
                    f"  Line: {line_src.strip()}\n"
                    f"  Fix:  {line_src.strip()};"
                ),
                'source': 'semicolon_check'
            })
        return errors

    def _check_missing_headers(self, code):
        """Check if used functions need headers"""
        errors = []
        header_funcs = {
            'printf': 'stdio.h', 'scanf': 'stdio.h', 'fprintf': 'stdio.h',
            'fopen': 'stdio.h', 'fclose': 'stdio.h', 'fgets': 'stdio.h',
            'puts': 'stdio.h', 'gets': 'stdio.h', 'putchar': 'stdio.h',
            'getchar': 'stdio.h', 'sprintf': 'stdio.h',
            'malloc': 'stdlib.h', 'calloc': 'stdlib.h', 'realloc': 'stdlib.h',
            'free': 'stdlib.h', 'exit': 'stdlib.h', 'system': 'stdlib.h',
            'atoi': 'stdlib.h', 'atof': 'stdlib.h', 'rand': 'stdlib.h',
            'strlen': 'string.h', 'strcpy': 'string.h', 'strcmp': 'string.h',
            'strcat': 'string.h', 'strncpy': 'string.h', 'memcpy': 'string.h',
            'memset': 'string.h',
            'sqrt': 'math.h', 'pow': 'math.h', 'sin': 'math.h',
            'cos': 'math.h', 'abs': 'math.h', 'ceil': 'math.h', 'floor': 'math.h',
        }

        # Find used functions
        for func, header in header_funcs.items():
            if re.search(r'\b' + func + r'\s*\(', code):
                if f'#include <{header}>' not in code and f'#include "{header}"' not in code:
                    # Find the line where this function is used
                    for i, line in enumerate(code.split('\n'), 1):
                        if re.search(r'\b' + func + r'\s*\(', line):
                            errors.append({
                                'line': i,
                                'column': 1,
                                'type': 'error',
                                'message': f"'{func}' undeclared - missing #include <{header}>",
                                'title': f"Missing header: #include <{header}>",
                                'suggestion': (
                                    f"File ke sabse upar ye line likho:\n"
                                    f"  #include <{header}>\n"
                                    f"'{func}' function ke liye '{header}' header chahiye."
                                ),
                                'source': 'header_check'
                            })
                            break
        return errors

    def _update_error_badge(self, count):
        """Update the error count badge in toolbar"""
        if count == 0:
            self.error_badge.config(text=" 0 Errors ", bg=BG_MEDIUM, fg=GREEN)
            self.status_label.config(text="No errors")
        elif count == 1:
            self.error_badge.config(text=" 1 Error ", bg='#5a2020', fg=RED)
            self.status_label.config(text="1 error found")
        else:
            self.error_badge.config(text=f" {count} Errors ", bg='#5a2020', fg=RED)
            self.status_label.config(text=f"{count} errors found")

    def _display_errors_in_terminal(self, errors):
        """Display all errors with suggestions in terminal"""
        if not errors:
            self._write_terminal("  No errors found. Code is clean!\n\n", "success")
            return

        self._write_terminal(f"  Found {len(errors)} error(s):\n\n", "error")

        seen = set()
        for i, err in enumerate(errors, 1):
            line = err.get('line', 0)
            key = (line, err.get('message', ''))
            if key in seen:
                continue
            seen.add(key)

            # Error header
            self._write_terminal(f"  Error #{i}", "error")
            if line > 0:
                self._write_terminal(f"  [Line {line}]", "error_line_ref")
            self._write_terminal(f"\n", "error")

            # Error message
            self._write_terminal(f"  {err.get('title', err.get('message', 'Unknown error'))}\n", "error")

            # Show the problematic source code line
            code = self._get_code()
            line_src = get_line_source_code(code, line)
            if line_src:
                self._write_terminal(f"  Code: {line_src.strip()}\n", "error_code")

            # Show suggestion
            suggestion = err.get('suggestion', '')
            if suggestion:
                self._write_terminal(f"  Fix:\n", "suggestion")
                for s_line in suggestion.split('\n'):
                    self._write_terminal(f"    {s_line}\n", "suggestion")

            self._write_terminal(f"\n", None)

    # -------------------------------------------------------------------------
    # FILE OPERATIONS
    # -------------------------------------------------------------------------
    def new_file(self):
        fp = self._ask_save("Create New File")
        if fp:
            with open(fp, "w") as f:
                f.write("")
            self.current_file = fp
            self.text_area.delete("1.0", END)
            self.status_label.config(text=f"New: {os.path.basename(fp)}")

    def open_file(self):
        from tkinter import filedialog
        fp = filedialog.askopenfilename(
            filetypes=[("C Files", "*.c"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if fp:
            with open(fp, "r") as f:
                self.text_area.delete("1.0", END)
                self.text_area.insert("1.0", f.read())
            self.current_file = fp
            self.status_label.config(text=f"Opened: {os.path.basename(fp)}")
            highlight_code(self.text_area, self.text_area.get("1.0", END))
            self.update_line_numbers()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w") as f:
                f.write(self.text_area.get("1.0", END))
            self.status_label.config(text=f"Saved: {os.path.basename(self.current_file)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        fp = self._ask_save("Save As")
        if fp:
            with open(fp, "w") as f:
                f.write(self.text_area.get("1.0", END))
            self.current_file = fp
            self.status_label.config(text=f"Saved: {os.path.basename(fp)}")

    def _ask_save(self, title):
        from tkinter import filedialog
        return filedialog.asksaveasfilename(
            defaultextension=".c",
            filetypes=[("C Files", "*.c"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title=title)

    # -------------------------------------------------------------------------
    # GET SOURCE CODE
    # -------------------------------------------------------------------------
    def _get_code(self):
        return self.text_area.get("1.0", END)

    # =========================================================================
    # COMPILER PHASE RUNNERS
    # =========================================================================

    def _run_lexer(self):
        code = self._get_code()
        if not code.strip():
            return

        self._clear_terminal()
        self.status_label.config(text="Running Lexer...")

        buf = io.StringIO()
        with redirect_stdout(buf):
            lexer = LexicalAnalyzer(code)
            self.tokens_cache = lexer.tokenize()

        self._display_lexer_output(self.tokens_cache)
        self.status_label.config(text=f"Lexer: {len(self.tokens_cache) - 1} tokens")

    def _display_lexer_output(self, tokens):
        self._write_terminal("=" * 70 + "\n", "phase_header")
        self._write_terminal("  PHASE 1: LEXICAL ANALYSIS (TOKENIZATION)\n", "phase_header")
        self._write_terminal("=" * 70 + "\n\n", "phase_header")
        self._write_terminal(f"  Total Tokens: {len(tokens) - 1}\n\n", "success")
        self._write_terminal(f"  {'Line':<8} {'Col':<8} {'Type':<20} {'Value'}\n", "phase_sub")
        self._write_terminal("  " + "-" * 65 + "\n")

        for t in tokens[:-1]:
            self._write_terminal(f"  {t.line:<8} {t.column:<8} ")
            self._write_terminal(f"{t.type.name:<20} ", "token_type")
            self._write_terminal(f"{t.value}\n", "token_val")

        self._write_terminal("  " + "-" * 65 + "\n\n", "phase_sub")

    def _run_parser(self):
        code = self._get_code()
        if not code.strip():
            return

        if not self.tokens_cache:
            lexer = LexicalAnalyzer(code)
            self.tokens_cache = lexer.tokenize()

        self._clear_terminal()
        self.status_label.config(text="Running Parser...")

        buf = io.StringIO()
        with redirect_stdout(buf):
            parser = SyntaxAnalyzer(self.tokens_cache)
            self.ast_cache = parser.parse()

        self._display_lexer_output(self.tokens_cache)
        self._display_parser_output(self.ast_cache, parser)

        # Show errors if any
        if parser.errors:
            self._write_terminal("=" * 70 + "\n", "phase_header")
            self._write_terminal("  SYNTAX ERRORS FOUND\n", "error")
            self._write_terminal("=" * 70 + "\n\n", "phase_header")
            self._display_errors_in_terminal(parser.errors)
            self.status_label.config(text=f"Parser: {len(parser.errors)} errors")
        else:
            self.status_label.config(text="Parser: AST generated (no errors)")

    def _display_parser_output(self, ast, parser=None):
        self._write_terminal("=" * 70 + "\n", "phase_header")
        self._write_terminal("  PHASE 2: SYNTAX ANALYSIS (PARSING)\n", "phase_header")
        self._write_terminal("=" * 70 + "\n\n", "phase_header")
        self._write_terminal("  Abstract Syntax Tree:\n\n", "phase_sub")
        self._print_ast_tree(ast, indent=2)
        self._write_terminal("\n")

    def _print_ast_tree(self, node, indent=0):
        if node is None:
            return
        prefix = "  " * indent
        if node.node_type.name in ('LITERAL',):
            self._write_terminal(f"{prefix}|-- {node.node_type.value}: {node.value} (type: {node.data_type})\n", "ast_node")
        elif node.node_type.name in ('VARIABLE',):
            self._write_terminal(f"{prefix}|-- {node.node_type.value}: {node.value}\n", "ast_node")
        elif node.node_type.name in ('BINARY_EXPR', 'UNARY_EXPR', 'ASSIGN_EXPR'):
            self._write_terminal(f"{prefix}|-- {node.node_type.value}: {node.value}\n", "ast_node")
        else:
            self._write_terminal(f"{prefix}|-- {node.node_type.value}\n", "ast_node")
        for child in node.children:
            self._print_ast_tree(child, indent + 1)

    def _run_semantic(self):
        code = self._get_code()
        if not code.strip():
            return

        if not self.tokens_cache:
            lexer = LexicalAnalyzer(code)
            self.tokens_cache = lexer.tokenize()
        if not self.ast_cache:
            parser = SyntaxAnalyzer(self.tokens_cache)
            self.ast_cache = parser.parse()

        self._clear_terminal()
        self.status_label.config(text="Running Semantic Analysis...")

        buf = io.StringIO()
        with redirect_stdout(buf):
            semantic = SemanticAnalyzer(self.ast_cache)
            self.semantic_ast = semantic.analyze()

        self._display_lexer_output(self.tokens_cache)
        self._display_parser_output(self.ast_cache)
        self._display_semantic_output(semantic)
        self.status_label.config(text=f"Semantic: {len(semantic.errors)} errors, {len(semantic.warnings)} warnings")

    def _display_semantic_output(self, semantic):
        self._write_terminal("=" * 70 + "\n", "phase_header")
        self._write_terminal("  PHASE 3: SEMANTIC ANALYSIS (TYPE CHECKING)\n", "phase_header")
        self._write_terminal("=" * 70 + "\n\n", "phase_header")

        # Symbol Table
        self._write_terminal("  SYMBOL TABLE\n", "phase_sub")
        self._write_terminal("  " + "-" * 55 + "\n")
        self._write_terminal(f"  {'Name':<20} {'Type':<15} {'Data Type':<15}\n", "phase_sub")
        self._write_terminal("  " + "-" * 55 + "\n")
        for name, sym in semantic.symbol_table.items():
            self._write_terminal(f"  {name:<20} {sym.symbol_type.name:<15} {sym.data_type:<15}\n", "symbol")
        self._write_terminal("  " + "-" * 55 + "\n")
        self._write_terminal(f"  Total symbols: {len(semantic.symbol_table)}\n\n", "success")

        # Errors with suggestions
        if semantic.errors:
            self._write_terminal("  SEMANTIC ERRORS:\n", "error")
            for err in semantic.errors:
                self._write_terminal(f"    [X] {err}\n", "error")
                title, suggestion = get_suggestion(err)
                if suggestion:
                    for s_line in suggestion.split('\n'):
                        self._write_terminal(f"        {s_line}\n", "suggestion")

        # Warnings
        if semantic.warnings:
            self._write_terminal("\n  WARNINGS:\n", "warning")
            for w in semantic.warnings:
                self._write_terminal(f"    [!] {w}\n", "warning")
                title, suggestion = get_suggestion(w)
                if suggestion:
                    for s_line in suggestion.split('\n'):
                        self._write_terminal(f"        {s_line}\n", "suggestion")

        if not semantic.errors:
            self._write_terminal("\n  [PASSED] Semantic analysis completed successfully!\n", "success")
        self._write_terminal("\n")

    # =========================================================================
    # SECURITY ANALYZER
    # =========================================================================
    def _run_security(self):
        code = self._get_code()
        if not code.strip():
            return

        self._clear_terminal()
        self.status_label.config(text="Running Security Analysis...")

        buf = io.StringIO()
        with redirect_stdout(buf):
            security = SecurityAnalyzer(code)
            vulns = security.analyze()

        self._display_security_output(vulns)

        critical = sum(1 for v in vulns if v['severity'] == 'CRITICAL')
        high = sum(1 for v in vulns if v['severity'] == 'HIGH')
        if vulns:
            self.status_label.config(text=f"Security: {critical} CRITICAL, {high} HIGH issues")
        else:
            self.status_label.config(text="Security: No vulnerabilities found")

    def _display_security_output(self, vulns):
        self._write_terminal("=" * 70 + "\n", "phase_header")
        self._write_terminal("  SECURITY ANALYSIS\n", "phase_header")
        self._write_terminal("=" * 70 + "\n\n", "phase_header")

        if not vulns:
            self._write_terminal("  [PASSED] No security vulnerabilities found!\n", "success")
            self._write_terminal("  Code is safe from common vulnerabilities.\n\n", "success")
            return

        # Summary counts
        critical = sum(1 for v in vulns if v['severity'] == 'CRITICAL')
        high = sum(1 for v in vulns if v['severity'] == 'HIGH')
        medium = sum(1 for v in vulns if v['severity'] == 'MEDIUM')
        low = sum(1 for v in vulns if v['severity'] == 'LOW')

        self._write_terminal(f"  Found {len(vulns)} vulnerability(ies):\n", "error")
        self._write_terminal(f"  CRITICAL: {critical}   HIGH: {high}   MEDIUM: {medium}   LOW: {low}\n\n", "warning")

        # Severity icons
        sev_tags = {
            'CRITICAL': 'error',
            'HIGH': 'error',
            'MEDIUM': 'warning',
            'LOW': 'phase_sub'
        }
        sev_icons = {
            'CRITICAL': '[!!]',
            'HIGH': '[!]',
            'MEDIUM': '[~]',
            'LOW': '[-]'
        }

        shown_lines = set()
        for i, v in enumerate(vulns, 1):
            sev = v['severity']
            tag = sev_tags.get(sev, 'error')
            icon = sev_icons.get(sev, '[?]')

            # Header
            self._write_terminal(f"  {icon} Vulnerability #{i}", tag)
            self._write_terminal(f"  [{sev}]", tag)
            if v['line'] > 0:
                self._write_terminal(f"  Line {v['line']}", "error_line_ref")
            self._write_terminal(f"\n", tag)

            # Category + Message
            self._write_terminal(f"  Category: {v['category']}\n", "warning")
            self._write_terminal(f"  Problem:  {v['message']}\n", "error")

            # Show problematic code line
            if v.get('code_line'):
                self._write_terminal(f"  Code:     {v['code_line']}\n", "error_code")

            # FIX SUGGESTION (highlighted)
            self._write_terminal(f"  How to fix:\n", "success")
            for fix_line in v['fix'].split('\n'):
                self._write_terminal(f"    {fix_line}\n", "suggestion")

            # Show fix example code
            if v.get('fix_example'):
                self._write_terminal(f"  Fixed code:\n", "success")
                for ex_line in v['fix_example'].split('\n'):
                    self._write_terminal(f"    {ex_line}\n", "code_out")

            self._write_terminal(f"\n", None)

        # Highlight vulnerable lines in editor
        self.text_area.tag_remove("error_line", "1.0", END)
        seen = set()
        for v in vulns:
            line = v['line']
            if line > 0 and line not in seen:
                seen.add(line)
                self.text_area.tag_add("error_line", f"{line}.0", f"{line}.end")

    def _run_optimizer(self):
        code = self._get_code()
        if not code.strip():
            return

        if not self.tokens_cache:
            lexer = LexicalAnalyzer(code)
            self.tokens_cache = lexer.tokenize()
        if not self.ast_cache:
            parser = SyntaxAnalyzer(self.tokens_cache)
            self.ast_cache = parser.parse()

        self._clear_terminal()
        self.status_label.config(text="Running Optimizer...")

        buf = io.StringIO()
        with redirect_stdout(buf):
            semantic = SemanticAnalyzer(self.ast_cache)
            self.semantic_ast = semantic.analyze()

        self._display_lexer_output(self.tokens_cache)
        self._display_parser_output(self.ast_cache)
        self._display_semantic_output(semantic)

        buf = io.StringIO()
        with redirect_stdout(buf):
            optimizer = Optimizer(self.semantic_ast)
            self.optimized_ast = optimizer.optimize()

        self._display_optimizer_output(optimizer)
        self.status_label.config(text=f"Optimizer: {len(optimizer.optimizations_applied)} optimizations")

    def _display_optimizer_output(self, optimizer):
        self._write_terminal("=" * 70 + "\n", "phase_header")
        self._write_terminal("  PHASE 4: CODE OPTIMIZATION\n", "phase_header")
        self._write_terminal("=" * 70 + "\n\n", "phase_header")

        cf = sum(1 for x in optimizer.optimizations_applied if 'Constant Folding' in x)
        cse = sum(1 for x in optimizer.optimizations_applied if 'CSE' in x)
        dce = sum(1 for x in optimizer.optimizations_applied if 'Dead Code' in x)

        self._write_terminal(f"  Constant Folding:                {cf} optimizations\n", "success")
        self._write_terminal(f"  Common Subexpression Elimination: {cse} optimizations\n", "success")
        self._write_terminal(f"  Dead Code Elimination:            {dce} optimizations\n\n", "success")

        self._write_terminal(f"  Total optimizations: {len(optimizer.optimizations_applied)}\n", "phase_sub")

        if optimizer.optimizations_applied:
            self._write_terminal("\n  Details:\n", "phase_sub")
            for i, opt in enumerate(optimizer.optimizations_applied, 1):
                self._write_terminal(f"    {i}. {opt}\n")
        self._write_terminal("\n")

    def _run_compile(self):
        code = self._get_code()
        if not code.strip():
            return

        if not self.tokens_cache:
            lexer = LexicalAnalyzer(code)
            self.tokens_cache = lexer.tokenize()
        if not self.ast_cache:
            parser = SyntaxAnalyzer(self.tokens_cache)
            self.ast_cache = parser.parse()

        self._clear_terminal()
        self.status_label.config(text="Running full compilation...")

        self._display_lexer_output(self.tokens_cache)
        self._display_parser_output(self.ast_cache)

        buf = io.StringIO()
        with redirect_stdout(buf):
            semantic = SemanticAnalyzer(self.ast_cache)
            self.semantic_ast = semantic.analyze()
        self._display_semantic_output(semantic)

        buf = io.StringIO()
        with redirect_stdout(buf):
            optimizer = Optimizer(self.semantic_ast)
            self.optimized_ast = optimizer.optimize()
        self._display_optimizer_output(optimizer)

        buf = io.StringIO()
        with redirect_stdout(buf):
            codegen = CodeGenerator(self.optimized_ast)
            generated = codegen.generate()

        self._display_codegen_output(generated)
        self.status_label.config(text="Compilation complete")

    def _display_codegen_output(self, generated_code):
        self._write_terminal("=" * 70 + "\n", "phase_header")
        self._write_terminal("  PHASE 5: CODE GENERATION\n", "phase_header")
        self._write_terminal("=" * 70 + "\n\n", "phase_header")
        self._write_terminal("  Generated Code:\n", "phase_sub")
        self._write_terminal("  " + "-" * 55 + "\n")
        for line in generated_code.split('\n'):
            self._write_terminal(f"  {line}\n", "code_out")
        self._write_terminal("  " + "-" * 55 + "\n\n", "phase_sub")
        self._write_terminal("  [PASSED] All compiler phases completed successfully!\n", "success")

    # =========================================================================
    # GCC RUN (compile + execute)
    # =========================================================================
    def _run_gcc(self):
        code = self._get_code()
        self._clear_terminal()

        if not code.strip():
            self._write_terminal("  No code to compile.\n", "error")
            return

        self._write_terminal("=" * 70 + "\n", "phase_header")
        self._write_terminal("  GCC COMPILE & RUN\n", "phase_header")
        self._write_terminal("=" * 70 + "\n\n", "phase_header")

        # First run error check
        self._check_all_errors(code)
        if self.all_errors:
            self._write_terminal(f"  {len(self.all_errors)} error(s) found before compilation:\n\n", "error")
            self._display_errors_in_terminal(self.all_errors)
            self._write_terminal("  Fix errors above before compiling.\n", "warning")
            self.status_label.config(text=f"Cannot compile: {len(self.all_errors)} errors")
            return

        self._write_terminal("  No errors found. Compiling...\n\n", "success")
        self.status_label.config(text="Compiling with GCC...")

        with open("temp.c", "w") as f:
            f.write(code)

        executable = "a.exe" if os.name == 'nt' else "a.out"

        try:
            proc = subprocess.run(
                ["gcc", "temp.c", "-o", executable],
                capture_output=True, text=True)
        except FileNotFoundError:
            self._write_terminal("  Error: 'gcc' not found. Install GCC and add to PATH.\n", "error")
            self.status_label.config(text="GCC not found")
            return

        if proc.returncode != 0:
            self._write_terminal("  Compilation Error:\n", "error")
            # Parse GCC errors with suggestions
            for line in proc.stderr.splitlines():
                m = re.search(r"temp\.c:(\d+):(\d+):\s*(error|warning):\s*(.*)", line)
                if m:
                    line_num = int(m.group(1))
                    msg = m.group(4).strip()
                    title, suggestion = get_suggestion(msg)
                    self._write_terminal(f"  Line {line_num}: {msg}\n", "error")
                    if suggestion:
                        for s_line in suggestion.split('\n'):
                            self._write_terminal(f"    {s_line}\n", "suggestion")
                    self._write_terminal("\n")
                else:
                    self._write_terminal(f"  {line}\n", "error")
            self.status_label.config(text="Compilation failed")
            return

        self._write_terminal("  [PASSED] Compilation successful!\n\n", "success")
        self._write_terminal("  Running program...\n", "phase_sub")
        self._write_terminal("  " + "-" * 55 + "\n\n")

        try:
            run_proc = subprocess.run(
                [f"./{executable}"] if os.name != 'nt' else [executable],
                capture_output=True, text=True, timeout=10)
            if run_proc.stdout:
                self._write_terminal(f"  {run_proc.stdout}\n", "code_out")
            if run_proc.stderr:
                self._write_terminal(f"  Runtime Error: {run_proc.stderr}\n", "error")
            self._write_terminal(f"\n  Program exited with code: {run_proc.returncode}\n", "phase_sub")
            self.status_label.config(text=f"Program exited: {run_proc.returncode}")
        except subprocess.TimeoutExpired:
            self._write_terminal("  Execution timed out (10s limit)\n", "error")
            self.status_label.config(text="Execution timed out")

        self._write_terminal("  " + "-" * 55 + "\n")

    # -------------------------------------------------------------------------
    # DEFAULT CODE
    # -------------------------------------------------------------------------
    def set_default_code(self):
        default = """\
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
        self.text_area.insert("1.0", default)
        highlight_code(self.text_area, default)
        self.update_line_numbers()


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    root = Tk()
    app = CCompilerIDE(root)
    root.mainloop()
