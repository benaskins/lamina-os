#!/usr/bin/env python3
"""
ADR Validation Tool for Lamina OS
Part of ADR-0015 Phase 0 Implementation

Validates ADR markdown files against the established schema and conventions.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of validating a single ADR"""
    adr_number: str
    filename: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, any]


class ADRValidator:
    """Validates ADR markdown files for consistency and completeness"""
    
    REQUIRED_METADATA = {
        'Status': r'^\*\*Status:\*\*\s+(DRAFT|PROPOSED|ACCEPTED|DEPRECATED|SUPERSEDED)',
        'Date': r'^\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})',
        'Authors': r'^\*\*Authors?:\*\*\s+(.+)',
        'Reviewed By': r'^\*\*Reviewed By:\*\*\s+(.+)',
    }
    
    REQUIRED_SECTIONS = [
        ('Context', r'^#{1,2}\s+Context'),
        ('Decision', r'^#{1,2}\s+Decision'),
        ('Consequences', r'^#{1,2}\s+Consequences'),
    ]
    
    RECOMMENDED_SECTIONS = [
        ('Decision Drivers', r'^#{1,2}\s+Decision Drivers'),
        ('Considered Options', r'^#{1,2}\s+(Considered Options|Alternatives?)'),
        ('Breath-First Alignment', r'^#{1,2}\s+Breath-First'),
        ('Implementation Plan', r'^#{1,2}\s+Implementation'),
        ('Success Metrics', r'^#{1,2}\s+Success Metrics'),
        ('High Council Review', r'^#{1,2}\s+High Council Review'),
    ]
    
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path
        self.schema = None
        if schema_path and schema_path.exists():
            with open(schema_path) as f:
                self.schema = json.load(f)
    
    def validate_file(self, filepath: Path) -> ValidationResult:
        """Validate a single ADR file"""
        content = filepath.read_text()
        lines = content.split('\n')
        
        # Extract ADR number from filename
        adr_match = re.match(r'(\d{4})-.*\.md$', filepath.name)
        if not adr_match:
            return ValidationResult(
                adr_number="????",
                filename=filepath.name,
                is_valid=False,
                errors=[f"Invalid filename format: {filepath.name}"],
                warnings=[],
                metadata={}
            )
        
        adr_number = adr_match.group(1)
        errors = []
        warnings = []
        metadata = {'number': adr_number}
        
        # Check title
        title_match = re.search(r'^#\s+ADR-' + adr_number + r':\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            errors.append(f"Missing or incorrect title format (expected: # ADR-{adr_number}: ...)")
        else:
            metadata['title'] = title_match.group(1)
        
        # Check required metadata
        for field, pattern in self.REQUIRED_METADATA.items():
            match = re.search(pattern, content, re.MULTILINE)
            if not match:
                # Special case for retrospectives
                if field == 'Reviewed By' and 'retrospective' in content.lower():
                    warnings.append(f"Missing {field} (may be acceptable for retrospective)")
                else:
                    errors.append(f"Missing required metadata: {field}")
            else:
                metadata[field.lower().replace(' ', '_')] = match.group(1) if match.lastindex else True
        
        # Check for Related field
        related_match = re.search(r'^\*\*Related:\*\*\s+(.+)$', content, re.MULTILINE)
        if related_match:
            metadata['related'] = related_match.group(1)
        else:
            warnings.append("Consider adding Related field to link associated ADRs")
        
        # Check required sections
        for section_name, pattern in self.REQUIRED_SECTIONS:
            if not re.search(pattern, content, re.MULTILINE):
                # Special handling for retrospectives
                if 'retrospective' in content.lower() and section_name in ['Considered Options']:
                    warnings.append(f"Missing {section_name} section (may be acceptable for retrospective)")
                else:
                    errors.append(f"Missing required section: {section_name}")
        
        # Check recommended sections
        for section_name, pattern in self.RECOMMENDED_SECTIONS:
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                warnings.append(f"Missing recommended section: {section_name}")
        
        # Check for Breath-First Alignment specifically
        if not re.search(r'breath.?first', content, re.IGNORECASE):
            warnings.append("No mention of breath-first principles found")
        
        # Validate status format
        status_match = re.search(self.REQUIRED_METADATA['Status'], content, re.MULTILINE)
        if status_match:
            status = status_match.group(1)
            if status not in ['DRAFT', 'PROPOSED', 'ACCEPTED', 'DEPRECATED', 'SUPERSEDED']:
                errors.append(f"Invalid status format: {status} (must be uppercase)")
        
        # Check date format
        date_match = re.search(self.REQUIRED_METADATA['Date'], content, re.MULTILINE)
        if date_match:
            try:
                datetime.strptime(date_match.group(1), '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format: {date_match.group(1)}")
        
        # Check for consistent section separators
        separator_count = content.count('\n---\n')
        if separator_count < 2:
            warnings.append("Consider using --- separators between major sections")
        
        # Determine validity
        is_valid = len(errors) == 0
        
        return ValidationResult(
            adr_number=adr_number,
            filename=filepath.name,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )
    
    def validate_directory(self, directory: Path) -> Tuple[List[ValidationResult], Dict[str, any]]:
        """Validate all ADR files in a directory"""
        results = []
        
        # Find all ADR files
        adr_files = sorted([f for f in directory.glob('*.md') 
                           if re.match(r'\d{4}-.*\.md$', f.name)])
        
        for filepath in adr_files:
            if filepath.name not in ['README.md', 'template.md']:
                result = self.validate_file(filepath)
                results.append(result)
        
        # Generate summary statistics
        summary = {
            'total_adrs': len(results),
            'valid_adrs': sum(1 for r in results if r.is_valid),
            'invalid_adrs': sum(1 for r in results if not r.is_valid),
            'total_errors': sum(len(r.errors) for r in results),
            'total_warnings': sum(len(r.warnings) for r in results),
            'missing_breath_first': sum(1 for r in results 
                                       if any('breath-first' in w.lower() for w in r.warnings)),
            'status_distribution': {}
        }
        
        # Count status distribution
        for result in results:
            status = result.metadata.get('status', 'UNKNOWN')
            summary['status_distribution'][status] = summary['status_distribution'].get(status, 0) + 1
        
        return results, summary


def print_validation_report(results: List[ValidationResult], summary: Dict[str, any]):
    """Print a formatted validation report"""
    print("=" * 80)
    print("ADR VALIDATION REPORT")
    print("=" * 80)
    print()
    print(f"Total ADRs scanned: {summary['total_adrs']}")
    print(f"✅ Valid: {summary['valid_adrs']}")
    print(f"❌ Invalid: {summary['invalid_adrs']}")
    print(f"Total errors: {summary['total_errors']}")
    print(f"Total warnings: {summary['total_warnings']}")
    print()
    
    print("Status Distribution:")
    for status, count in summary['status_distribution'].items():
        print(f"  {status}: {count}")
    print()
    
    # Print detailed results
    for result in sorted(results, key=lambda r: r.adr_number):
        status_icon = "✅" if result.is_valid else "❌"
        print(f"{status_icon} ADR-{result.adr_number}: {result.filename}")
        
        if result.errors:
            print("  Errors:")
            for error in result.errors:
                print(f"    - {error}")
        
        if result.warnings:
            print("  Warnings:")
            for warning in result.warnings:
                print(f"    - {warning}")
        
        if result.is_valid and not result.warnings:
            print("  ✨ Perfect compliance!")
        print()
    
    # Summary recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if summary['missing_breath_first'] > 0:
        print(f"⚠️  {summary['missing_breath_first']} ADRs missing Breath-First Alignment section")
    
    if summary['invalid_adrs'] > 0:
        print(f"🔧 {summary['invalid_adrs']} ADRs require immediate fixes")
    
    if summary['total_warnings'] > 0:
        print(f"💡 {summary['total_warnings']} total warnings to consider addressing")
    
    print()
    print("Next steps:")
    print("1. Fix all validation errors")
    print("2. Add Breath-First Alignment sections where missing")
    print("3. Consider addressing warnings for better consistency")
    print("4. Run validation again to confirm compliance")


def main():
    """Main entry point"""
    # Determine ADR directory
    if len(sys.argv) > 1:
        adr_dir = Path(sys.argv[1])
    else:
        # Try to find ADR directory relative to script
        adr_dir = Path(__file__).parent.parent
    
    if not adr_dir.exists():
        print(f"Error: ADR directory not found: {adr_dir}")
        sys.exit(1)
    
    # Look for schema file
    schema_path = Path(__file__).parent / 'adr-schema.json'
    
    # Create validator and run validation
    validator = ADRValidator(schema_path if schema_path.exists() else None)
    results, summary = validator.validate_directory(adr_dir)
    
    # Print report
    print_validation_report(results, summary)
    
    # Exit with error code if any ADRs are invalid
    sys.exit(0 if summary['invalid_adrs'] == 0 else 1)


if __name__ == '__main__':
    main()