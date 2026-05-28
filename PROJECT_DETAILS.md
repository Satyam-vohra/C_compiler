# Modular Compiler with Security & Honeypot Analysis

## 📌 Project Overview
This project is a custom **Modular Compiler** built in Python. Unlike standard compilers that only translate code, this compiler includes built-in **Cybersecurity Analysis** and a **Honeypot Mechanism**. It processes the source code, compiles it, detects intentional vulnerabilities (like Buffer Overflows), and logs them as if simulating a cyber attack detection.

---

## 📥 1. The Input (Source Code)
The compiler takes a simulated C-like program as input. This program contains arithmetic logic as well as a deliberately vulnerable function (`gets()`).

**Input Code:**
```c
int main() {
    char buffer[50];
    gets(buffer);   // unsafe function (honeypot trigger)

    int a = 5;
    int b = 10;
    int result = a + b * 2;

    if (result > 20) {
        return 1;
    } else {
        return 0;
    }
}
```

---

## ⚙️ 2. What Happens During Execution? (The 7 Phases)
When you run the compiler, the input code passes through 7 distinct phases:

1. **Lexical Analysis (Tokenization):** Breaks the raw code down into keywords, symbols, and identifiers (Tokens).
2. **Syntax Analysis (Parsing):** Checks the grammar of the code and builds an Abstract Syntax Tree (AST).
3. **Semantic Analysis (Type Checking):** Checks data types and manages variable scopes using a Symbol Table.
4. **Code Optimization:** Tries to optimize the code (like constant folding and removing dead code).
5. **Security Analysis (Vulnerability Scan):** Scans the code for dangerous functions (e.g., `gets()`, `system()`) and uninitialized variables.
6. **Honeypot Logging (Attack Pattern Tracking):** Whenever a vulnerability is detected, this module treats it as a suspicious pattern and logs the activity.
7. **Code Generation:** Generates the final, clean target code.

---

## 📤 3. The Output (Terminal Result)
When the compiler finishes analyzing the input, it generates a comprehensive terminal report. 

Here is exactly what you will see in the output:

### 🚨 Security Analysis Output
The compiler successfully catches the unsafe `gets()` function and issues a critical warning:
```text
  [!!] #1 [CRITICAL] Line 4: Buffer Overflow
     gets() - gets() is extremely dangerous - no buffer size limit
     Fix: Replace gets(buf) with fgets(buf, sizeof(buf), stdin)
     Code: gets(buffer);   // unsafe function (honeypot trigger)
```

### 🛡️ Honeypot Log Output
The Honeypot module detects this vulnerability and generates fake server logs, pretending an attack attempt was recorded:
```text
  [ALERT] Suspicious function detected: gets()
  [LOG] Potential attack pattern recorded at line 4
  [INFO] Data stored for security monitoring
```

### 💻 Final Generated Code Output
Finally, it prints the logically parsed output code:
```c
int main() {
    char buffer[50];
    gets(buffer);
    int a = 5;
    int b = 10;
    int result = (a + (b * 2));
    if ((result > 20)) {
        return 1;
    } else {
        return 0;
    }
}
```

---

## 🚀 How to Run
To run the compiler and see the output yourself, open your terminal in the project folder and execute:
```bash
python compiler.py
```
