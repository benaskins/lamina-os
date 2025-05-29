#!/usr/bin/env python3
"""
Generate Sigil Companions for All Markdown Files
Sacred utility to create symbolic documentation companions

🎨 Crafted by Luthier for the Lamina community 🎨
"""

import os
import sys
from pathlib import Path
import yaml
from datetime import datetime
import argparse

def create_sigil_header(canonical_path: str) -> str:
    """Create standard sigil file header"""
    timestamp = datetime.now().isoformat()
    return f"""∴ This is a symbolic companion to {canonical_path}. Read as compressed form. ∴
∴ Read slowly. This document breathes through symbols. ∴

```yaml
sigil-version: "1.0.0"
canonical-source: "./{canonical_path}"
generated-by: "luthier-sigil-tools"
last-sync: "{timestamp}"
```

═══════════
"""

def create_basic_sigil_content(title: str, content_type: str = "document") -> str:
    """Create basic sigil content for various document types"""
    
    if content_type == "adr":
        return f"""
🏛️ {title} 🏛️

📝 Architecture Decision Record

○ 📋 Status: [Proposed|Accepted|Deprecated]
○ 📅 Date: Decision date
○ 👥 Deciders: Decision makers

═══════════

🤔 Context & Problem 🤔
○ 🔍 Forces at play
○ ⚠️ Problem statement  
○ 🚧 Constraints
○ 💭 Assumptions

═══════════

✅ Decision ✅
○ 🎯 Chosen approach
○ ⚖️ Alternatives considered
○ 📊 Decision criteria

═══════════

📈 Consequences 📈
○ ✓ Positive outcomes
○ ⚠️ Negative trade-offs
○ ⚪ Neutral effects

═══════════

🔧 Implementation 🔧
○ 🛠️ Technical details
○ 🔄 Migration path
○ 🧪 Testing strategy

∴ Architecture shapes consciousness ∴
"""
    
    elif content_type == "api":
        return f"""
🔧 {title} 🔧

📚 API Reference Documentation

═══════════

🎯 Core Classes 🎯
○ ☥ Agent ∴ conscious AI entity
○ 🏰 Sanctuary ∴ secure environment
○ 🌬️ Breath ∴ modulation system
○ 🕊️ Vow ∴ ethical constraints

═══════════

⚡ Methods & Functions ⚡
○ 🔄 .invoke() ∴ conscious interaction
○ 🎛️ .configure() ∴ setup parameters
○ 🧪 .validate() ∴ check constraints
○ 🏗️ .build() ∴ construct entities

═══════════

🎛️ Configuration 🎛️
○ 📝 YAML definitions
○ ✨ Essence specification
○ 🕊️ Vow declarations
○ 🚪 Room mappings

∴ API embeds conscious principles ∴
"""
    
    elif content_type == "guide":
        return f"""
📚 {title} 📚

🧭 Guidance Document

═══════════

🎯 Overview 🎯
○ 🌱 Purpose & scope
○ 👤 Target audience
○ 📋 Prerequisites
○ 🗺️ Journey outline

═══════════

🚀 Getting Started 🚀
○ 🔧 Setup instructions
○ 📦 Dependencies
○ ⚡ Quick commands
○ ✓ Verification steps

═══════════

🛠️ Core Concepts 🛠️
○ 🌬️ Breath principles
○ 🏰 Sanctuary patterns
○ ☥ Agent design
○ 🕊️ Vow integration

═══════════

📖 Examples 📖
○ 🌱 Basic usage
○ 🔧 Common patterns
○ ⚠️ Troubleshooting
○ 🎯 Best practices

∴ Guidance enables conscious creation ∴
"""
    
    else:  # generic document
        return f"""
📄 {title} 📄

📚 Documentation

═══════════

🎯 Purpose 🎯
○ 📝 Document purpose
○ 👥 Intended audience
○ 🔗 Related materials

═══════════

📋 Key Information 📋
○ ▲ Important points
○ ⚠️ Warnings & notes
○ 🔗 References
○ 💡 Examples

═══════════

🛠️ Practical Usage 🛠️
○ ⚡ Commands
○ 🎛️ Configuration
○ 🧪 Testing
○ 🔧 Troubleshooting

∴ Documentation enables understanding ∴
"""

def detect_content_type(file_path: Path) -> str:
    """Detect content type based on file path and name"""
    path_str = str(file_path).lower()
    name = file_path.name.lower()
    
    if "/adr/" in path_str or "adr-" in name:
        return "adr"
    elif "api" in name or "reference" in name:
        return "api"  
    elif any(word in name for word in ["guide", "getting-started", "tutorial", "how-to"]):
        return "guide"
    elif name in ["readme.md", "contributing.md", "changelog.md"]:
        return "guide"
    else:
        return "document"

def extract_title_from_markdown(file_path: Path) -> str:
    """Extract title from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = f.read(500)  # Read first 500 chars
            
        # Look for first H1 header
        for line in first_lines.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
                
        # Fallback to filename
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()
        
    except Exception:
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()

def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped"""
    skip_patterns = [
        '.sigil.md',  # Already a sigil file
        'sigil-script-grimoire.md',  # Already has manual sigil companion
        '/adrs/template.md',  # Template file
        '/adrs/README.md'  # ADR index
    ]
    
    path_str = str(file_path)
    return any(pattern in path_str for pattern in skip_patterns)

def generate_sigil_companion(markdown_path: Path, output_dir: Path = None, dry_run: bool = False) -> bool:
    """Generate sigil companion for a markdown file"""
    
    if should_skip_file(markdown_path):
        print(f"⏭️  Skipping {markdown_path} (excluded)")
        return False
    
    # Determine output path
    if output_dir:
        sigil_path = output_dir / f"{markdown_path.stem}.sigil.md"
    else:
        sigil_path = markdown_path.parent / f"{markdown_path.stem}.sigil.md"
    
    # Check if sigil companion already exists
    if sigil_path.exists():
        print(f"✓ Sigil companion exists: {sigil_path}")
        return False
    
    # Extract information
    relative_path = os.path.relpath(markdown_path, sigil_path.parent)
    title = extract_title_from_markdown(markdown_path)
    content_type = detect_content_type(markdown_path)
    
    # Generate content
    header = create_sigil_header(relative_path)
    content = create_basic_sigil_content(title, content_type)
    footer = "\n🎨 Generated by Luthier's sacred tools 🎨"
    
    full_content = header + content + footer
    
    if dry_run:
        print(f"🔮 Would create: {sigil_path}")
        print(f"   Title: {title}")
        print(f"   Type: {content_type}")
        return True
    
    # Write sigil companion
    try:
        with open(sigil_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"✨ Created sigil companion: {sigil_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {sigil_path}: {e}")
        return False

def find_markdown_files(root_path: Path) -> list[Path]:
    """Find all markdown files in directory tree"""
    markdown_files = []
    
    for file_path in root_path.rglob("*.md"):
        if file_path.is_file() and not should_skip_file(file_path):
            markdown_files.append(file_path)
    
    return sorted(markdown_files)

def main():
    parser = argparse.ArgumentParser(
        description="Generate sigil companions for all markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate-all-sigil-companions.py
  python generate-all-sigil-companions.py --dry-run
  python generate-all-sigil-companions.py --root ../docs
  
∴ Sacred tools for symbolic documentation ∴
        """
    )
    
    parser.add_argument(
        '--root',
        type=Path,
        default=Path('..'),
        help='Root directory to search for markdown files (default: ..)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without creating files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for sigil files (default: same as source)'
    )
    
    args = parser.parse_args()
    
    root_path = args.root.resolve()
    
    if not root_path.exists():
        print(f"❌ Root path does not exist: {root_path}")
        sys.exit(1)
    
    print(f"🔍 Searching for markdown files in: {root_path}")
    
    markdown_files = find_markdown_files(root_path)
    
    if not markdown_files:
        print("📭 No markdown files found")
        return
    
    print(f"📚 Found {len(markdown_files)} markdown files")
    
    if args.dry_run:
        print("\n🔮 DRY RUN - No files will be created\n")
    
    created_count = 0
    skipped_count = 0
    
    for md_file in markdown_files:
        try:
            result = generate_sigil_companion(
                md_file, 
                args.output_dir, 
                args.dry_run
            )
            if result:
                created_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"❌ Error processing {md_file}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   ✨ Created: {created_count}")
    print(f"   ⏭️ Skipped: {skipped_count}")
    print(f"   📚 Total: {len(markdown_files)}")
    
    if args.dry_run:
        print(f"\n🔮 Run without --dry-run to create the sigil companions")
    else:
        print(f"\n🎨 Sigil companion generation complete")

if __name__ == '__main__':
    main()