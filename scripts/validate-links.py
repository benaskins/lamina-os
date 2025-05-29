#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Link Validation Script for Lamina OS Release Process

Validates all links in documentation to prevent broken references
in PyPI and GitHub releases.
"""

import re
import sys
from pathlib import Path

import requests


def find_markdown_files(root_dir: Path) -> list[Path]:
    """Find all markdown files in the project."""
    markdown_files = []

    # Core package README
    core_readme = root_dir / "packages" / "lamina-core" / "README.md"
    if core_readme.exists():
        markdown_files.append(core_readme)

    # Main repository README
    main_readme = root_dir / "README.md"
    if main_readme.exists():
        markdown_files.append(main_readme)

    # Documentation files
    docs_dirs = [root_dir / "docs", root_dir / "packages" / "lamina-core" / "docs"]

    for docs_dir in docs_dirs:
        if docs_dir.exists():
            markdown_files.extend(docs_dir.glob("**/*.md"))

    return markdown_files


def extract_links(content: str) -> list[tuple[str, str]]:
    """Extract markdown links from content."""
    # Match [text](url) pattern
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    return re.findall(link_pattern, content)


def validate_url(url: str) -> bool:
    """Validate that a URL is accessible."""
    try:
        if url.startswith("mailto:"):
            return True  # Don't validate email links

        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code < 400
    except Exception:
        return False


def validate_local_file(file_path: str, base_path: Path) -> bool:
    """Validate that a local file exists."""
    if file_path.startswith("/"):
        # Absolute path
        return Path(file_path).exists()
    else:
        # Relative path
        full_path = base_path.parent / file_path
        return full_path.exists()


def validate_github_file(
    file_path: str, repo_base: str = "https://github.com/benaskins/lamina-os"
) -> bool:
    """Validate that a file exists in the GitHub repository."""
    if not file_path.startswith(repo_base):
        return True  # Not a GitHub link

    # Convert GitHub blob URL to raw URL for HEAD request
    if "/blob/main/" in file_path:
        raw_url = file_path.replace("github.com", "raw.githubusercontent.com").replace(
            "/blob/main/", "/main/"
        )
        return validate_url(raw_url)

    return validate_url(file_path)


def main():
    """Main validation function."""
    root_dir = Path(__file__).parent.parent
    markdown_files = find_markdown_files(root_dir)

    print("🔗 Validating links in Lamina OS documentation...")
    print(f"Found {len(markdown_files)} markdown files to check")

    all_links: dict[str, list[tuple[str, str, Path]]] = {}
    broken_links = []

    # Extract all links
    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            links = extract_links(content)

            for text, url in links:
                if url not in all_links:
                    all_links[url] = []
                all_links[url].append((text, url, md_file))
        except Exception as e:
            print(f"❌ Error reading {md_file}: {e}")
            continue

    print(f"Found {len(all_links)} unique links to validate")

    # Validate each unique link
    for url, occurrences in all_links.items():
        print(f"Checking: {url}")

        is_valid = True

        if url.startswith("http://") or url.startswith("https://"):
            # External URL - validate with HTTP request
            if url.startswith("https://github.com/benaskins/lamina-os"):
                is_valid = validate_github_file(url)
            else:
                is_valid = validate_url(url)
        elif url.startswith("#"):
            # Anchor link - skip for now
            continue
        else:
            # Relative link - check if file exists
            # Use first occurrence to determine base path
            base_path = occurrences[0][2]
            is_valid = validate_local_file(url, base_path)

        if not is_valid:
            print(f"❌ BROKEN: {url}")
            for text, _, file_path in occurrences:
                broken_links.append((url, text, file_path))
                print(f"   Used in: {file_path} as '{text}'")
        else:
            print(f"✅ OK: {url}")

    # Report results
    print("\n" + "=" * 60)
    if broken_links:
        print(f"❌ VALIDATION FAILED: {len(broken_links)} broken links found")
        print("\nBroken links:")
        for url, text, file_path in broken_links:
            print(f"  • {url}")
            print(f"    Text: '{text}'")
            print(f"    File: {file_path}")
            print()
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED: All links are working!")
        print("Safe to proceed with release.")


if __name__ == "__main__":
    main()
