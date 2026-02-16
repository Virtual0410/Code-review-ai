"""
Analyzer Factory
Routes code to appropriate language-specific analyzer
"""

from typing import Optional
from .base_analyzer import BaseAnalyzer, Issue
from .python_analyzer import PythonAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer
from .java_analyzer import JavaAnalyzer
from .language_detector import LanguageDetector


class AnalyzerFactory:
    """Factory for creating language-specific analyzers"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self._analyzers = {
            'python': PythonAnalyzer,
            'javascript': JavaScriptAnalyzer,
            'typescript': JavaScriptAnalyzer,  # Use JS analyzer for TS
            'java': JavaAnalyzer,
        }
    
    def get_analyzer(self, language: str) -> Optional[BaseAnalyzer]:
        """Get appropriate analyzer for language"""
        analyzer_class = self._analyzers.get(language.lower())
        
        if analyzer_class:
            return analyzer_class(self.ai_client)
        
        return None
    
    def analyze_code(self, code: str, filename: Optional[str] = None, language: Optional[str] = None):
        """
        Analyze code using appropriate language expert
        
        Returns: (language_detected, static_issues, ai_issues)
        """
        # Detect language if not provided
        if not language:
            language = LanguageDetector.detect(code, filename)
        
        # Get analyzer
        analyzer = self.get_analyzer(language)
        
        if not analyzer:
            # Fallback to generic analysis
            return language, [], self._generic_analysis(code)
        
        # Run static analysis first (fast, no API)
        static_issues = []
        if hasattr(analyzer, 'analyze_static'):
            static_issues = analyzer.analyze_static(code)
        
        # Run AI analysis (language-specific)
        ai_issues = analyzer.analyze(code)
        
        return language, static_issues, ai_issues
    
    def _generic_analysis(self, code: str):
        """Fallback generic analysis for unsupported languages"""
        from .base_analyzer import Severity, Issue
        
        issues = []
        
        # Basic security checks
        if 'eval(' in code or 'exec(' in code:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category="Security",
                message="Use of eval() or exec() detected",
                suggestion="Avoid dynamic code execution"
            ))
        
        if any(word in code.lower() for word in ['password', 'secret', 'api_key']):
            if '"' in code or "'" in code:
                issues.append(Issue(
                    severity=Severity.HIGH,
                    category="Security",
                    message="Possible hardcoded credentials",
                    suggestion="Use environment variables or secrets manager"
                ))
        
        return issues
    
    @staticmethod
    def get_supported_languages():
        """Return list of languages with dedicated analyzers"""
        return ['python', 'javascript', 'typescript', 'java']
