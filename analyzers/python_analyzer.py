"""
Python Expert Analyzer
Specializes in Python-specific code review
"""

from .base_analyzer import BaseAnalyzer, Issue, Severity
from typing import List


class PythonAnalyzer(BaseAnalyzer):
    """Expert Python code analyzer"""
    
    def __init__(self, ai_client):
        super().__init__(ai_client)
        self.language_name = "Python"
    
    def get_language_patterns(self) -> List[str]:
        return [
            "Proper use of context managers (with statements)",
            "List/dict/set comprehensions vs loops",
            "Generator expressions for memory efficiency",
            "Proper exception handling (specific exceptions, not bare except)",
            "Use of __init__, __str__, __repr__ in classes",
            "Proper use of @property, @staticmethod, @classmethod decorators",
            "Type hints and annotations (Python 3.5+)",
            "Async/await patterns for concurrent operations"
        ]
    
    def get_common_pitfalls(self) -> List[str]:
        return [
            "Mutable default arguments (def func(x=[]))",
            "Late binding closures in loops",
            "Modifying list while iterating over it",
            "Using 'is' for value comparison instead of '=='",
            "Circular imports",
            "Not closing files/resources (missing 'with' statements)",
            "Using eval() or exec() with user input",
            "Catching Exception or BaseException (too broad)",
            "Using global variables excessively",
            "Not using enumerate() when needing index and value"
        ]
    
    def get_best_practices(self) -> List[str]:
        return [
            "Follow PEP 8 style guide",
            "Use virtual environments",
            "Write docstrings for functions/classes (PEP 257)",
            "Use f-strings for string formatting (Python 3.6+)",
            "Prefer pathlib over os.path",
            "Use 'with' statements for file operations",
            "Prefer list comprehensions over map()/filter()",
            "Use context managers for resource management",
            "Keep functions small and focused (single responsibility)",
            "Use meaningful variable names (snake_case)",
            "Avoid wildcard imports (from module import *)",
            "Use logging instead of print() for production code"
        ]
    
    def get_security_checks(self) -> List[str]:
        return [
            "SQL injection via string concatenation",
            "Use of eval(), exec(), compile() with untrusted input",
            "Hardcoded credentials/secrets/API keys",
            "Unsafe deserialization (pickle with untrusted data)",
            "Path traversal vulnerabilities",
            "Command injection via os.system() or subprocess",
            "XXE vulnerabilities in XML parsing",
            "Insecure random number generation (use secrets module)",
            "Exposure of sensitive data in logs/errors",
            "Missing input validation",
            "Use of assert for security checks (can be optimized away)"
        ]
    
    def analyze_static(self, code: str) -> List[Issue]:
        """Quick static analysis before AI review"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for common issues
            if 'eval(' in line or 'exec(' in line:
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category="Security",
                    message="Dangerous use of eval() or exec()",
                    line_number=i,
                    suggestion="Avoid eval/exec. Use safer alternatives like ast.literal_eval() or JSON parsing"
                ))
            
            if 'password' in line.lower() and ('=' in line or ':' in line):
                if '"' in line or "'" in line:
                    issues.append(Issue(
                        severity=Severity.HIGH,
                        category="Security",
                        message="Possible hardcoded password",
                        line_number=i,
                        suggestion="Use environment variables or a secrets manager"
                    ))
            
            if line_stripped.startswith('except:'):
                issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category="Best Practice",
                    message="Bare except clause catches all exceptions",
                    line_number=i,
                    suggestion="Catch specific exceptions: except ValueError:"
                ))
            
            if 'def ' in line and '=[]' in line.replace(' ', ''):
                issues.append(Issue(
                    severity=Severity.HIGH,
                    category="Bug",
                    message="Mutable default argument",
                    line_number=i,
                    suggestion="Use None as default, then initialize: if x is None: x = []"
                ))
        
        return issues
