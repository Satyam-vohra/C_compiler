import re
from typing import List, Dict, Any
from datetime import datetime

class HoneypotLogger:
    """
    =========================================================================
    HONEYPOT LOGGER
    =========================================================================
    Simulates honeypot-inspired attack detection and logging.
    
    When unsafe functions are detected, this logger records suspicious
    activity for security monitoring and analysis.
    =========================================================================
    """
    
    def __init__(self):
        self.logs: List[str] = []
        self.attack_patterns: List[Dict[str, Any]] = []
    
    def log_vulnerability(self, vuln: Dict[str, Any]):
        func_match = re.search(r"(\w+)\s*\(", vuln['message'])
        func_name = func_match.group(1) if func_match else "unknown"
        
        self.attack_patterns.append({
            'function': func_name,
            'line': vuln['line'],
            'severity': vuln['severity'],
            'category': vuln['category'],
            'timestamp': self._timestamp()
        })
        
        self.logs.append(f"[ALERT] Suspicious function detected: {func_name}()")
        self.logs.append(f"[LOG] Potential attack pattern recorded at line {vuln['line']}")
        self.logs.append(f"[INFO] Data stored for security monitoring")
    
    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def display_logs(self):
        print("\n" + "="*70)
        print("HONEYPOT LOG OUTPUT")
        print("="*70)
        
        if not self.logs:
            print("\n  [INFO] No suspicious activity detected")
            print("-" * 70)
            return
        
        print("\n")
        for log in self.logs:
            print(f"  {log}")
        
        print("\n" + "-" * 70)
    
    def get_logs(self) -> List[str]:
        return self.logs
