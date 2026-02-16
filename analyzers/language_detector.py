"""
Language Detector
Automatically detects programming language from code or filename
"""

import re
from typing import Optional


class LanguageDetector:
    """Detect programming language from code content or filename"""
    
    # File extension mappings
    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
    }
    
    # Language patterns in code
    LANGUAGE_PATTERNS = {
        'python': [
            r'^import\s+\w+',
            r'^from\s+\w+\s+import',
            r'def\s+\w+\s*\(',
            r'class\s+\w+\s*:',
            r'if\s+__name__\s*==\s*["\']__main__["\']',
        ],
        'javascript': [
            r'const\s+\w+\s*=',
            r'let\s+\w+\s*=',
            r'function\s+\w+\s*\(',
            r'=>',
            r'console\.log',
            r'require\s*\(',
            r'import\s+.*\s+from',
        ],
        'java': [
            r'public\s+class',
            r'private\s+\w+\s+\w+',
            r'public\s+static\s+void\s+main',
            r'System\.out\.println',
            r'@Override',
            r'extends\s+\w+',
        ],
        'cpp': [
            r'#include\s*<',
            r'std::',
            r'cout\s*<<',
            r'namespace\s+\w+',
            r'template\s*<',
        ],
        'c': [
            r'#include\s*<',
            r'printf\s*\(',
            r'malloc\s*\(',
            r'struct\s+\w+',
        ],
        'go': [
            r'package\s+main',
            r'func\s+\w+\s*\(',
            r'import\s+\(',
            r':=',
            r'fmt\.Print',
        ],
        'rust': [
            r'fn\s+\w+\s*\(',
            r'let\s+mut\s+',
            r'impl\s+\w+',
            r'println!',
            r'use\s+std::',
        ],
        'ruby': [
            r'def\s+\w+',
            r'end$',
            r'puts\s+',
            r'require\s+["\']',
            r'class\s+\w+\s*<',
        ],
        'php': [
            r'<\?php',
            r'\$\w+\s*=',
            r'function\s+\w+\s*\(',
            r'echo\s+',
            r'namespace\s+\w+',
        ],
    }
    
    @staticmethod
    def detect_from_filename(filename: str) -> Optional[str]:
        """Detect language from file extension"""
        if not filename:
            return None
        
        filename_lower = filename.lower()
        
        for ext, lang in LanguageDetector.EXTENSION_MAP.items():
            if filename_lower.endswith(ext):
                return lang
        
        return None
    
    @staticmethod
    def detect_from_code(code: str) -> str:
        """Detect language from code content"""
        if not code or not code.strip():
            return 'unknown'
        
        scores = {}
        
        # Score each language based on pattern matches
        for lang, patterns in LanguageDetector.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE):
                    score += 1
            
            if score > 0:
                scores[lang] = score
        
        # Return language with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return 'unknown'
    
    @staticmethod
    def detect(code: str, filename: Optional[str] = None) -> str:
        """
        Detect language from both filename and code
        Filename takes priority if available
        """
        # Try filename first
        if filename:
            lang = LanguageDetector.detect_from_filename(filename)
            if lang:
                return lang
        
        # Fall back to code analysis
        return LanguageDetector.detect_from_code(code)
    
    @staticmethod
    def get_supported_languages() -> list:
        """Return list of supported languages"""
        langs = set(LanguageDetector.EXTENSION_MAP.values())
        langs.update(LanguageDetector.LANGUAGE_PATTERNS.keys())
        return sorted(list(langs))
