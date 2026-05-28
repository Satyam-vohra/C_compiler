from flask import Flask, render_template, request, jsonify
import os
import io
import sys
import traceback
from compiler import Compiler

app = Flask(__name__)

# Base directory for the file explorer (current directory)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files', methods=['GET'])
def get_files():
    """Returns a list of files and directories for the file explorer"""
    path = request.args.get('path', '')
    
    # Security: prevent directory traversal outside BASE_DIR
    target_dir = os.path.abspath(os.path.join(BASE_DIR, path))
    if not target_dir.startswith(BASE_DIR):
        return jsonify({"error": "Access denied"}), 403
        
    if not os.path.exists(target_dir):
        return jsonify({"error": "Directory not found"}), 404

    items = []
    try:
        for item in os.listdir(target_dir):
            if item.startswith('.') or item == '__pycache__':
                continue # Skip hidden files and pycache
            
            item_path = os.path.join(target_dir, item)
            is_dir = os.path.isdir(item_path)
            
            # Relative path from BASE_DIR
            rel_path = os.path.relpath(item_path, BASE_DIR).replace('\\', '/')
            
            items.append({
                "name": item,
                "path": rel_path,
                "is_dir": is_dir
            })
            
        # Sort directories first, then files
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return jsonify({"items": items, "current_path": path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/file', methods=['GET'])
def get_file_content():
    """Returns the content of a specific file"""
    path = request.args.get('path', '')
    if not path:
        return jsonify({"error": "No path provided"}), 400
        
    target_file = os.path.abspath(os.path.join(BASE_DIR, path))
    if not target_file.startswith(BASE_DIR):
        return jsonify({"error": "Access denied"}), 403
        
    if not os.path.isfile(target_file):
        return jsonify({"error": "File not found"}), 404
        
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run', methods=['POST'])
def run_compiler():
    """Compiles the code and runs the AST interpreter"""
    data = request.json
    source_code = data.get('code', '')
    
    if not source_code.strip():
        return jsonify({"error": "Empty source code"}), 400

    # Redirect standard output to capture compiler print statements
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    compiler_instance = None
    execution_output = []
    syntax_errors = []
    generated_code = ""
    error_occurred = False
    
    try:
        compiler_instance = Compiler(source_code)
        generated_code = compiler_instance.compile()
        execution_output = getattr(compiler_instance, 'execution_output', [])
    except Exception as e:
        print(f"\n[ERROR] An exception occurred:\n{str(e)}")
        traceback.print_exc(file=sys.stdout)
        error_occurred = True
    finally:
        # Restore standard output
        sys.stdout = old_stdout
        
    output_str = redirected_output.getvalue()
    
    # Extract syntax errors if any
    if compiler_instance and hasattr(compiler_instance, 'parser') and compiler_instance.parser.errors:
        syntax_errors = compiler_instance.parser.errors

    return jsonify({
        "compiler_logs": output_str,
        "execution_output": "\n".join(execution_output) if execution_output else "",
        "generated_code": generated_code,
        "syntax_errors": syntax_errors,
        "has_error": error_occurred or len(syntax_errors) > 0
    })

if __name__ == '__main__':
    print("Starting Premium Web GUI on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
