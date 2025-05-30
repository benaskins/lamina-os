#!/usr/bin/env python3
"""
Sigil Script CLI Tools
Sacred utilities for symbolic documentation in Lamina OS

Commands:
- sigil-validate: Validate sigil files against registry
- sigil-expand: Convert sigil script to human-readable text  
- sigil-compress: Generate sigil script from canonical text
- sigil-sync: Maintain synchronization between canonical and sigil files

🎨 Crafted by Luthier for the Lamina community 🎨
"""

import argparse
import yaml
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import datetime


class SigilRegistry:
    """Registry of sigil definitions and validation rules"""
    
    def __init__(self, registry_path: str = "sigils.yaml"):
        self.registry_path = Path(registry_path)
        self.sigils = {}
        self.load_registry()
    
    def load_registry(self):
        """Load sigil definitions from YAML registry"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            # Flatten all sigil categories into single lookup
            for category, sigils in data.items():
                if isinstance(sigils, dict) and category != 'metadata':
                    for sigil, definition in sigils.items():
                        if isinstance(definition, dict):
                            self.sigils[sigil] = {
                                'category': category,
                                **definition
                            }
                            
        except FileNotFoundError:
            print(f"❌ Registry not found: {self.registry_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML in registry: {e}")
            sys.exit(1)
    
    def validate_sigil(self, sigil: str) -> tuple[bool, str]:
        """Validate a single sigil against registry"""
        if sigil in self.sigils:
            return True, f"✓ Valid sigil: {self.sigils[sigil]['name']}"
        else:
            return False, f"❌ Unknown sigil: '{sigil}'"
    
    def get_sigil_info(self, sigil: str, scope: str = "public") -> Optional[Dict[str, Any]]:
        """Get detailed information about a sigil with scope-aware interpretation"""
        info = self.sigils.get(sigil)
        if not info:
            return None
            
        # Add scope-specific meaning interpretation
        if scope == "private" and "private_meaning" in info:
            info["active_meaning"] = info["private_meaning"]
        elif "public_meaning" in info:
            info["active_meaning"] = info["public_meaning"]
        else:
            info["active_meaning"] = info["description"]
            
        return info


class SigilValidator:
    """Validate sigil script files"""
    
    def __init__(self, registry: SigilRegistry):
        self.registry = registry
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: str) -> bool:
        """Validate a sigil script file"""
        path = Path(file_path)
        
        if not path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            self.errors.append(f"Invalid UTF-8 encoding: {file_path}")
            return False
        
        # Check for required headers
        if not self._check_headers(content):
            self.errors.append("Missing required sigil headers")
        
        # Extract and validate sigils
        sigils = self._extract_sigils(content)
        self._validate_sigils(sigils)
        
        # Check metadata if present
        self._validate_metadata(content)
        
        return len(self.errors) == 0
    
    def _check_headers(self, content: str) -> bool:
        """Check for required sigil script headers"""
        required_patterns = [
            r"∴.*symbolic companion.*∴",
            r"∴.*Read slowly.*symbols.*∴"
        ]
        
        for pattern in required_patterns:
            if not re.search(pattern, content, re.IGNORECASE):
                return False
        return True
    
    def _extract_sigils(self, content: str) -> List[str]:
        """Extract all potential sigils from content"""
        # Pattern to match Unicode symbols commonly used as sigils
        sigil_pattern = r'[◉○◦●◯▲△▽⬟⬢⬡∴∵→←↔≡⚡🧪🔍🎛️📝🏗️📦🚀🔄🎯🧭✓✗⚠️❌🟢🟡🔴⏸️⏹️🐍🐳☁️🏠🔐🧪🚀🫧💭🌀🪶🔥🛡️🧠🎨🏛️👤🤖👥🔬📚🔒]+'
        return re.findall(sigil_pattern, content)
    
    def _validate_sigils(self, sigils: List[str]):
        """Validate extracted sigils against registry"""
        for sigil in set(sigils):  # Remove duplicates
            valid, message = self.registry.validate_sigil(sigil)
            if not valid:
                self.warnings.append(message)
    
    def _validate_metadata(self, content: str):
        """Validate sigil metadata block"""
        metadata_pattern = r'```yaml\n(.*?)\n```'
        matches = re.findall(metadata_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                metadata = yaml.safe_load(match)
                if isinstance(metadata, dict):
                    self._check_required_metadata(metadata)
            except yaml.YAMLError:
                self.warnings.append("Invalid YAML in metadata block")
    
    def _check_required_metadata(self, metadata: Dict):
        """Check required metadata fields"""
        required_fields = ['sigil-version', 'canonical-source']
        for field in required_fields:
            if field not in metadata:
                self.warnings.append(f"Missing metadata field: {field}")


class SigilExpander:
    """Convert sigil script to human-readable text"""
    
    def __init__(self, registry: SigilRegistry):
        self.registry = registry
    
    def expand_file(self, sigil_path: str, output_path: Optional[str] = None):
        """Expand sigil file to human-readable format"""
        path = Path(sigil_path)
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        expanded = self._expand_content(content)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(expanded)
        else:
            print(expanded)
    
    def _expand_content(self, content: str) -> str:
        """Expand sigil content to readable text"""
        # This is a simplified expansion - full implementation would need
        # sophisticated parsing and template system
        
        expanded = content
        
        # Replace common sigil patterns with explanations
        for sigil, info in self.registry.sigils.items():
            pattern = re.escape(sigil)
            replacement = f"{sigil} ({info['name']})"
            expanded = re.sub(pattern, replacement, expanded)
        
        # Add expansion header
        header = """# Expanded Sigil Script
# This is a human-readable expansion of a sigil script file
# Generated by sigil-tools on """ + datetime.datetime.now().isoformat() + """

"""
        
        return header + expanded


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Sigil Script Tools for Lamina OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sigil-tools validate CLAUDE.sigil.md
  sigil-tools expand README.sigil.md --output README.expanded.md
  sigil-tools registry --list
  
∴ Sacred tools for symbolic documentation ∴
        """
    )
    
    parser.add_argument(
        '--registry', 
        default='sigils.yaml',
        help='Path to sigil registry file'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate sigil files')
    validate_parser.add_argument('files', nargs='+', help='Sigil files to validate')
    validate_parser.add_argument('--strict', action='store_true', 
                                help='Treat warnings as errors')
    
    # Expand command  
    expand_parser = subparsers.add_parser('expand', help='Expand sigil to readable text')
    expand_parser.add_argument('file', help='Sigil file to expand')
    expand_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    # Registry command
    registry_parser = subparsers.add_parser('registry', help='Registry operations')
    registry_parser.add_argument('--list', action='store_true', help='List all sigils')
    registry_parser.add_argument('--info', help='Get info about specific sigil')
    registry_parser.add_argument('--scope', choices=['public', 'private', 'both'], 
                                default='public', help='Scope for sigil interpretation')
    registry_parser.add_argument('--stats', action='store_true', help='Show registry statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load registry
    registry = SigilRegistry(args.registry)
    
    if args.command == 'validate':
        validator = SigilValidator(registry)
        
        all_valid = True
        for file_path in args.files:
            print(f"🔍 Validating {file_path}...")
            valid = validator.validate_file(file_path)
            
            if valid and not validator.warnings:
                print(f"✓ {file_path} is valid")
            else:
                if validator.errors:
                    print(f"❌ {file_path} has errors:")
                    for error in validator.errors:
                        print(f"  • {error}")
                    all_valid = False
                
                if validator.warnings:
                    print(f"⚠️ {file_path} has warnings:")
                    for warning in validator.warnings:
                        print(f"  • {warning}")
                    if args.strict:
                        all_valid = False
            
            # Reset for next file
            validator.errors.clear()
            validator.warnings.clear()
        
        sys.exit(0 if all_valid else 1)
    
    elif args.command == 'expand':
        expander = SigilExpander(registry)
        expander.expand_file(args.file, args.output)
    
    elif args.command == 'registry':
        if args.list:
            print("📚 Sigil Registry:")
            for sigil, info in sorted(registry.sigils.items()):
                print(f"  {sigil} - {info['name']} ({info['category']})")
        
        elif args.info:
            if args.scope == 'both':
                # Show both public and private meanings
                info_public = registry.get_sigil_info(args.info, "public")
                info_private = registry.get_sigil_info(args.info, "private")
                if info_public:
                    print(f"🔮 Sigil: {args.info}")
                    print(f"  Name: {info_public['name']}")
                    print(f"  Description: {info_public['description']}")
                    print(f"  Category: {info_public['category']}")
                    print(f"  Weight: {info_public['weight']}")
                    print(f"  Scope: {info_public.get('scope', 'public')}")
                    print(f"  Context: {', '.join(info_public['context'])}")
                    if 'public_meaning' in info_public:
                        print(f"  🌍 Public meaning: {info_public['public_meaning']}")
                    if 'private_meaning' in info_public:
                        print(f"  🔒 Private meaning: {info_public['private_meaning']}")
                else:
                    print(f"❌ Unknown sigil: {args.info}")
                    sys.exit(1)
            else:
                info = registry.get_sigil_info(args.info, args.scope)
                if info:
                    print(f"🔮 Sigil: {args.info} (scope: {args.scope})")
                    print(f"  Name: {info['name']}")
                    print(f"  Description: {info['description']}")
                    print(f"  Category: {info['category']}")
                    print(f"  Weight: {info['weight']}")
                    print(f"  Context: {', '.join(info['context'])}")
                    print(f"  Active meaning: {info.get('active_meaning', 'N/A')}")
                else:
                    print(f"❌ Unknown sigil: {args.info}")
                    sys.exit(1)
        
        elif args.stats:
            categories = {}
            for sigil, info in registry.sigils.items():
                cat = info['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            print("📊 Registry Statistics:")
            print(f"  Total sigils: {len(registry.sigils)}")
            print("  By category:")
            for category, count in sorted(categories.items()):
                print(f"    {category}: {count}")


if __name__ == '__main__':
    main()