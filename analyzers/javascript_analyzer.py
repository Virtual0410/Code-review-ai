"""
JavaScript Expert Analyzer
Specializes in JavaScript/TypeScript code review
"""

from .base_analyzer import BaseAnalyzer, Issue, Severity
from typing import List


class JavaScriptAnalyzer(BaseAnalyzer):
    """Expert JavaScript/TypeScript code analyzer"""
    
    def __init__(self, ai_client):
        super().__init__(ai_client)
        self.language_name = "JavaScript"
    
    def get_language_patterns(self) -> List[str]:
        return [
            "Proper use of const, let (never var)",
            "Arrow functions vs function declarations",
            "Promise chains and async/await patterns",
            "Destructuring assignments",
            "Template literals for strings",
            "Spread operator usage",
            "Optional chaining (?.) and nullish coalescing (??)",
            "Module imports/exports (ES6+)",
            "Proper 'this' binding (arrow functions, .bind())"
        ]
    
    def get_common_pitfalls(self) -> List[str]:
        return [
            "Using var instead of const/let",
            "Callback hell / pyramid of doom",
            "Not handling Promise rejections",
            "Incorrect 'this' context in callbacks",
            "Mutating state directly in React",
            "Memory leaks from event listeners",
            "Using == instead of ===",
            "Not sanitizing user input in innerHTML",
            "Blocking the event loop with synchronous operations",
            "Forgetting to return values from array methods",
            "Modifying arrays during iteration"
        ]
    
    def get_best_practices(self) -> List[str]:
        return [
            "Use strict mode ('use strict')",
            "Always use === and !== for comparisons",
            "Prefer const, use let only when reassignment needed",
            "Use async/await over Promise chains when possible",
            "Handle all Promise rejections",
            "Use arrow functions for callbacks to preserve 'this'",
            "Avoid nested callbacks (use async/await or Promises)",
            "Use meaningful variable names (camelCase)",
            "Keep functions pure when possible",
            "Use destructuring for object/array access",
            "Prefer template literals over string concatenation",
            "Use optional chaining for nested object access"
        ]
    
    def get_security_checks(self) -> List[str]:
        return [
            "XSS vulnerabilities (innerHTML with user data)",
            "eval() usage with untrusted input",
            "SQL injection in database queries",
            "Insecure direct object references",
            "Missing input validation",
            "Hardcoded API keys or secrets",
            "Unsafe use of dangerouslySetInnerHTML in React",
            "CORS misconfigurations",
            "JWT token exposure in localStorage",
            "Prototype pollution vulnerabilities",
            "Command injection via child_process"
        ]
    
    def analyze_static(self, code: str) -> List[Issue]:
        """Quick static analysis before AI review"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for var usage
            if line_stripped.startswith('var '):
                issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category="Best Practice",
                    message="Using 'var' instead of 'const' or 'let'",
                    line_number=i,
                    suggestion="Use 'const' for values that don't change, 'let' for variables"
                ))
            
            # Check for eval
            if 'eval(' in line:
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category="Security",
                    message="Dangerous use of eval()",
                    line_number=i,
                    suggestion="Avoid eval(). Use JSON.parse() or safer alternatives"
                ))
            
            # Check for innerHTML with potential user data
            if 'innerHTML' in line and ('input' in line.lower() or 'user' in line.lower()):
                issues.append(Issue(
                    severity=Severity.HIGH,
                    category="Security",
                    message="Potential XSS vulnerability with innerHTML",
                    line_number=i,
                    suggestion="Use textContent or sanitize input with DOMPurify"
                ))
            
            # Check for == comparison
            if ' == ' in line or '== ' in line or ' ==' in line:
                issues.append(Issue(
                    severity=Severity.LOW,
                    category="Best Practice",
                    message="Using == instead of ===",
                    line_number=i,
                    suggestion="Use === for type-safe comparison"
                ))
            
            # Check for hardcoded secrets
            if any(word in line.lower() for word in ['apikey', 'api_key', 'secret', 'password', 'token']):
                if '"' in line or "'" in line:
                    issues.append(Issue(
                        severity=Severity.HIGH,
                        category="Security",
                        message="Possible hardcoded secret or API key",
                        line_number=i,
                        suggestion="Use environment variables (process.env.API_KEY)"
                    ))
        
        return issues
