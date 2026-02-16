"""
Java Expert Analyzer
Specializes in Java code review
"""

from .base_analyzer import BaseAnalyzer, Issue, Severity
from typing import List


class JavaAnalyzer(BaseAnalyzer):
    """Expert Java code analyzer"""
    
    def __init__(self, ai_client):
        super().__init__(ai_client)
        self.language_name = "Java"
    
    def get_language_patterns(self) -> List[str]:
        return [
            "Proper exception handling with try-catch-finally",
            "Use of interfaces and abstract classes",
            "Generic types for type safety",
            "Stream API for collections (Java 8+)",
            "Lambda expressions and functional interfaces",
            "Proper use of synchronized blocks for thread safety",
            "Builder pattern for complex objects",
            "Dependency injection patterns",
            "Use of Optional to avoid null checks"
        ]
    
    def get_common_pitfalls(self) -> List[str]:
        return [
            "Not closing resources (missing try-with-resources)",
            "String concatenation in loops (use StringBuilder)",
            "Comparing strings with == instead of .equals()",
            "Not overriding hashCode() when overriding equals()",
            "Catching generic Exception instead of specific ones",
            "Using raw types instead of generics",
            "Thread safety issues in concurrent code",
            "Memory leaks from unclosed connections/streams",
            "NullPointerException from not checking null",
            "Using float/double for financial calculations"
        ]
    
    def get_best_practices(self) -> List[str]:
        return [
            "Follow Java naming conventions (camelCase for variables)",
            "Use try-with-resources for AutoCloseable resources",
            "Prefer composition over inheritance",
            "Make classes and methods as private as possible",
            "Use StringBuilder for string concatenation in loops",
            "Always override toString(), equals(), and hashCode() together",
            "Use @Override annotation",
            "Prefer immutable objects when possible",
            "Use enums instead of integer constants",
            "Document public APIs with Javadoc",
            "Use Optional instead of returning null",
            "Prefer ArrayList over LinkedList unless needed"
        ]
    
    def get_security_checks(self) -> List[str]:
        return [
            "SQL injection via string concatenation",
            "Hardcoded passwords or credentials",
            "Insecure deserialization",
            "Path traversal vulnerabilities",
            "XML External Entity (XXE) attacks",
            "Insecure random number generation",
            "Unvalidated redirects and forwards",
            "Missing authentication/authorization checks",
            "Exposure of sensitive data in exceptions",
            "Command injection vulnerabilities",
            "Weak cryptographic algorithms"
        ]
    
    def analyze_static(self, code: str) -> List[Issue]:
        """Quick static analysis before AI review"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for == on Strings
            if 'String' in line and ' == ' in line:
                issues.append(Issue(
                    severity=Severity.HIGH,
                    category="Bug",
                    message="Comparing Strings with == instead of .equals()",
                    line_number=i,
                    suggestion="Use .equals() or .equalsIgnoreCase() for String comparison"
                ))
            
            # Check for catch Exception
            if 'catch' in line and 'Exception' in line and 'catch (Exception' in line:
                issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category="Best Practice",
                    message="Catching generic Exception",
                    line_number=i,
                    suggestion="Catch specific exceptions like IOException, SQLException"
                ))
            
            # Check for hardcoded passwords
            if 'password' in line.lower() and '=' in line:
                if '"' in line or "'" in line:
                    issues.append(Issue(
                        severity=Severity.CRITICAL,
                        category="Security",
                        message="Hardcoded password detected",
                        line_number=i,
                        suggestion="Use configuration files or environment variables"
                    ))
            
            # Check for SQL concatenation
            if 'SELECT' in line and '+' in line:
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category="Security",
                    message="Potential SQL injection via string concatenation",
                    line_number=i,
                    suggestion="Use PreparedStatement with parameterized queries"
                ))
            
            # Check for missing try-with-resources
            if 'new FileInputStream' in line or 'new Connection' in line:
                # Look back for try-with-resources pattern
                if i > 1 and 'try (' not in lines[i-2]:
                    issues.append(Issue(
                        severity=Severity.MEDIUM,
                        category="Best Practice",
                        message="Resource not using try-with-resources",
                        line_number=i,
                        suggestion="Use try-with-resources: try (Resource r = ...) { }"
                    ))
        
        return issues
