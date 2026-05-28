// Initialize Monaco Editor
let editor;
let currentPath = '';

require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' }});
require(['vs/editor/editor.main'], function() {
    editor = monaco.editor.create(document.getElementById('monaco-editor'), {
        value: [
            'int main() {',
            '    char buffer[50];',
            '    gets(buffer);   // unsafe function (honeypot trigger)',
            '',
            '    int a = 5;',
            '    int b = 10;',
            '    int result = a + b * 2;',
            '',
            '    print(result);  // New execution print feature!',
            '',
            '    if (result > 20) {',
            '        return 1;',
            '    } else {',
            '        return 0;',
            '    }',
            '}'
        ].join('\n'),
        language: 'c',
        theme: 'vs-dark',
        automaticLayout: true,
        fontFamily: 'Consolas, monospace',
        fontSize: 14,
        minimap: { enabled: false },
        padding: { top: 15, bottom: 15 },
        scrollBeyondLastLine: false
    });

    // Load initial file tree
    fetchFiles();
});

// UI Elements
const fileTree = document.getElementById('fileTree');
const refreshBtn = document.getElementById('refreshBtn');
const runBtn = document.getElementById('runBtn');
const currentFileName = document.getElementById('currentFileName');
const tabBtns = document.querySelectorAll('.tab-btn');
const toast = document.getElementById('toast');

// Events
refreshBtn.addEventListener('click', () => fetchFiles(currentPath));

runBtn.addEventListener('click', async () => {
    if (!editor) return;
    
    const code = editor.getValue();
    if (!code.trim()) {
        showToast('Source code cannot be empty!', 'error');
        return;
    }

    runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running...';
    runBtn.disabled = true;

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        
        const result = await response.json();
        
        document.getElementById('compiler-logs').querySelector('pre').textContent = result.compiler_logs || 'No logs generated.';
        document.getElementById('execution-output').querySelector('pre').textContent = result.execution_output || 'No output from execution.';
        document.getElementById('generated-code').querySelector('pre').textContent = result.generated_code || 'No code generated.';
        
        // Handle Monaco editor markers (red squiggly lines)
        const markers = [];
        if (result.syntax_errors && result.syntax_errors.length > 0) {
            result.syntax_errors.forEach(err => {
                markers.push({
                    startLineNumber: err.line || 1,
                    startColumn: err.column || 1,
                    endLineNumber: err.line || 1,
                    endColumn: (err.column || 1) + (err.value ? err.value.length : 1),
                    message: `Syntax Error: ${err.message}`,
                    severity: monaco.MarkerSeverity.Error
                });
            });
            showToast(`Found ${result.syntax_errors.length} syntax errors!`, 'error');
        } else if (result.has_error) {
            showToast('Compilation failed with errors.', 'error');
        } else {
            showToast('Compilation and execution successful!', 'success');
            // Switch to execution output tab automatically
            document.querySelector('[data-target="execution-output"]').click();
        }
        
        // Apply markers to editor
        const model = editor.getModel();
        monaco.editor.setModelMarkers(model, "owner", markers);
        
    } catch (error) {
        showToast('Failed to connect to server.', 'error');
        console.error(error);
    } finally {
        runBtn.innerHTML = '<i class="fa-solid fa-play"></i> Compile & Run';
        runBtn.disabled = false;
    }
});

// Tabs logic
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all
        tabBtns.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Add to clicked
        btn.classList.add('active');
        document.getElementById(btn.getAttribute('data-target')).classList.add('active');
    });
});

// File Explorer Functions
async function fetchFiles(path = '') {
    try {
        const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        renderFileTree(data.items, path);
    } catch (error) {
        showToast(`Failed to load files: ${error.message}`, 'error');
    }
}

function renderFileTree(items, currentDirPath) {
    fileTree.innerHTML = '';
    
    // Add "Up" directory if not at root
    if (currentDirPath) {
        const upItem = document.createElement('div');
        upItem.className = 'file-item directory';
        upItem.innerHTML = '<i class="fa-solid fa-level-up-alt"></i> ..';
        upItem.onclick = () => {
            const parts = currentDirPath.split('/');
            parts.pop();
            fetchFiles(parts.join('/'));
        };
        fileTree.appendChild(upItem);
    }
    
    items.forEach(item => {
        const el = document.createElement('div');
        el.className = `file-item ${item.is_dir ? 'directory' : 'file'}`;
        
        let icon = item.is_dir ? 'fa-folder' : 'fa-file-code';
        if (item.name.endsWith('.md')) icon = 'fa-file-lines';
        if (item.name.endsWith('.json')) icon = 'fa-file-code';
        if (item.name.endsWith('.html')) icon = 'fa-file-code';
        
        el.innerHTML = `<i class="fa-solid ${icon}"></i> ${item.name}`;
        
        el.onclick = () => {
            if (item.is_dir) {
                fetchFiles(item.path);
            } else {
                loadFile(item.path, item.name, el);
            }
        };
        
        fileTree.appendChild(el);
    });
}

async function loadFile(path, name, element) {
    try {
        const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        // Update active state
        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
        if (element) element.classList.add('active');
        
        // Set editor content
        editor.setValue(data.content);
        currentFileName.innerHTML = `<i class="fa-solid fa-file-code"></i> ${name}`;
        
        // Clear previous markers
        monaco.editor.setModelMarkers(editor.getModel(), "owner", []);
        
        // Detect language
        let lang = 'plaintext';
        if (name.endsWith('.c') || name.endsWith('.h')) lang = 'c';
        else if (name.endsWith('.py')) lang = 'python';
        else if (name.endsWith('.js')) lang = 'javascript';
        else if (name.endsWith('.html')) lang = 'html';
        else if (name.endsWith('.css')) lang = 'css';
        else if (name.endsWith('.json')) lang = 'json';
        else if (name.endsWith('.md')) lang = 'markdown';
        
        monaco.editor.setModelLanguage(editor.getModel(), lang);
        
    } catch (error) {
        showToast(`Failed to load file: ${error.message}`, 'error');
    }
}

function showToast(message, type = 'success') {
    let icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> ${message}`;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}
