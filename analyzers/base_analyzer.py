"""
Base Language Analyzer Interface
All language-specific analyzers inherit from this
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"
    INFO = "ℹ️  INFO"


@dataclass
class Issue:
    severity: Severity
    category: str
    message: str
    line_number: int = None
    suggestion: str = None
    code_snippet: str = None


class BaseAnalyzer(ABC):
    """Base class for language-specific analyzers"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.language_name = "Unknown"
    
    @abstractmethod
    def get_language_patterns(self) -> List[str]:
        """Return list of code patterns specific to this language"""
        pass
    
    @abstractmethod
    def get_common_pitfalls(self) -> List[str]:
        """Return list of common mistakes in this language"""
        pass
    
    @abstractmethod
    def get_best_practices(self) -> List[str]:
        """Return list of best practices for this language"""
        pass
    
    @abstractmethod
    def get_security_checks(self) -> List[str]:
        """Return list of security issues specific to this language"""
        pass
    
    def build_expert_prompt(self, code: str) -> str:
        """Build language-specific expert prompt"""
        patterns = self.get_language_patterns()
        pitfalls = self.get_common_pitfalls()
        practices = self.get_best_practices()
        security = self.get_security_checks()
        
        prompt = f"""You are an expert {self.language_name} developer and code reviewer.

Analyze this {self.language_name} code for issues specific to {self.language_name}.

KEY {self.language_name.upper()} PATTERNS TO CHECK:
{chr(10).join(f"- {p}" for p in patterns)}

COMMON {self.language_name.upper()} PITFALLS:
{chr(10).join(f"- {p}" for p in pitfalls)}

{self.language_name.upper()} BEST PRACTICES:
{chr(10).join(f"- {p}" for p in practices)}

{self.language_name.upper()} SECURITY CONCERNS:
{chr(10).join(f"- {s}" for s in security)}

CODE TO REVIEW:
```{self.language_name.lower()}
{code}
```

Return ONLY a JSON array of issues found:
[
  {{
    "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
    "category": "Bug|Security|Performance|Style|Best Practice",
    "message": "Clear description",
    "line_number": <number or null>,
    "suggestion": "How to fix"
  }}
]

Focus on {self.language_name}-SPECIFIC issues. Be thorough but concise.
If no issues, return: []
"""
        return prompt
    
    def analyze(self, code: str) -> List[Issue]:
        """Analyze code using language-specific knowledge"""
        prompt = self.build_expert_prompt(code)
        
        try:
            response = self.ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {self.language_name} code reviewer. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return self._parse_response(response.choices[0].message.content)
        
        except Exception as e:
            return [Issue(
                severity=Severity.CRITICAL,
                category="Error",
                message=f"Analysis failed: {str(e)}"
            )]
    
    def _parse_response(self, response: str) -> List[Issue]:
        """Parse AI response into Issue objects"""
        import json
        
        # Clean response
        response = response.strip()
        if response.startswith("```"):
            lines = response.split('\n')
            response = '\n'.join(lines[1:-1])
        
        try:
            data = json.loads(response)
            issues = []
            
            for item in data:
                try:
                    issues.append(Issue(
                        severity=Severity[item['severity']],
                        category=item['category'],
                        message=item['message'],
                        line_number=item.get('line_number'),
                        suggestion=item.get('suggestion')
                    ))
                except (KeyError, ValueError):
                    continue
            
            return issues
        
        except json.JSONDecodeError:
            return [Issue(
                severity=Severity.INFO,
                category="Parse Error",
                message="Could not parse AI response"
            )]
