#!/usr/bin/env python3
"""
Breath-first development check tool.

Ensures commits align with Lamina OS conscious development principles.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any


class BreathChecker:
    """Check files for breath-first development compliance."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_file(self, file_path: Path) -> bool:
        """Check a single file for breath-first compliance."""
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        if file_path.suffix == '.py':
            return self._check_python_file(file_path, content)
        elif file_path.suffix in ['.yaml', '.yml']:
            return self._check_yaml_file(file_path, content)
        elif file_path.suffix == '.md':
            return self._check_markdown_file(file_path, content)
        
        return True
    
    def _check_python_file(self, file_path: Path, content: str) -> bool:
        """Check Python file for breath-aware patterns."""
        lines = content.split('\n')
        
        # Check for reactive patterns
        reactive_patterns = [
            r'\.poll\(\)',
            r'while.*True:.*sleep\(0\)',
            r'asyncio\.sleep\(0\)',
            r'time\.sleep\(0\)',
        ]
        
        for i, line in enumerate(lines):
            for pattern in reactive_patterns:
                if re.search(pattern, line):
                    self.warnings.append(
                        f"{file_path}:{i+1}: Consider breath-aware alternative to reactive pattern: {line.strip()}"
                    )
        
        # Check for breath-positive patterns
        breath_patterns = [
            r'conscious_pause',
            r'breath_rhythm',
            r'mindful_wait',
            r'present_moment',
        ]
        
        has_breath_awareness = any(
            any(re.search(pattern, line) for pattern in breath_patterns)
            for line in lines
        )
        
        # Check for missing docstrings in classes/functions
        class_func_pattern = r'^(class |def |async def )'
        docstring_pattern = r'^\s*"""'
        
        for i, line in enumerate(lines):
            if re.match(class_func_pattern, line.strip()):
                # Look for docstring in next few lines
                has_docstring = False
                for j in range(i+1, min(i+4, len(lines))):
                    if re.match(docstring_pattern, lines[j]):
                        has_docstring = True
                        break
                    elif lines[j].strip() and not lines[j].strip().startswith('#'):
                        break
                
                if not has_docstring and 'test_' not in file_path.name:
                    self.issues.append(
                        f"{file_path}:{i+1}: Missing docstring for {line.strip()}"
                    )
        
        return len(self.issues) == 0
    
    def _check_yaml_file(self, file_path: Path, content: str) -> bool:
        """Check YAML file for breath-aware configuration."""
        if 'agent.yaml' in file_path.name or 'sanctuary' in str(file_path):
            # Check for required breath-aware fields
            required_patterns = [
                r'essence:',
                r'breath_rhythm:',
                r'vows:',
            ]
            
            missing_patterns = []
            for pattern in required_patterns:
                if not re.search(pattern, content):
                    missing_patterns.append(pattern.replace(':', ''))
            
            if missing_patterns:
                self.warnings.append(
                    f"{file_path}: Agent configuration missing breath-aware fields: {', '.join(missing_patterns)}"
                )
        
        return True
    
    def _check_markdown_file(self, file_path: Path, content: str) -> bool:
        """Check Markdown for conscious documentation practices."""
        lines = content.split('\n')
        
        # Check for rushed language
        rushed_phrases = [
            r'\bquickly\b',
            r'\bfast\b(?! food)',
            r'\brapid\b',
            r'\bimmediate\b',
            r'\binstant\b',
            r'\basap\b',
        ]
        
        for i, line in enumerate(lines):
            for pattern in rushed_phrases:
                if re.search(pattern, line, re.IGNORECASE):
                    self.warnings.append(
                        f"{file_path}:{i+1}: Consider breath-aware alternative to rushed language: {line.strip()}"
                    )
        
        # Check for breath-positive language
        breath_phrases = [
            r'\bconscious\b',
            r'\bmindful\b',
            r'\bdeliberate\b',
            r'\bthoughtful\b',
            r'\bpresent\b',
            r'\bbreath\b',
        ]
        
        has_breath_language = any(
            any(re.search(pattern, line, re.IGNORECASE) for pattern in breath_phrases)
            for line in lines
        )
        
        return True


def main():
    """Main entry point for breath checker."""
    if len(sys.argv) < 2:
        print("Usage: breath_check.py <file1> [file2] ...")
        sys.exit(1)
    
    checker = BreathChecker()
    all_passed = True
    
    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)
        if file_path.exists() and file_path.is_file():
            passed = checker.check_file(file_path)
            if not passed:
                all_passed = False
    
    # Report issues
    if checker.issues:
        print("🚫 Breath-first issues found:")
        for issue in checker.issues:
            print(f"  {issue}")
        print()
    
    if checker.warnings:
        print("⚠️  Breath-first suggestions:")
        for warning in checker.warnings:
            print(f"  {warning}")
        print()
    
    if not checker.issues and not checker.warnings:
        print("✅ All files align with breath-first development principles")
    elif not checker.issues:
        print("✅ No blocking issues found, only suggestions for deeper breath-awareness")
    
    # Only fail on issues, not warnings
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()