#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Lamina OS Release Script

Performs comprehensive validation before package release to prevent
broken links and other issues from reaching PyPI.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Exit code: {e.returncode}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False


def main():
    """Main release validation and execution."""
    root_dir = Path(__file__).parent.parent
    package_dir = root_dir / "packages" / "lamina-core"
    
    print("🚀 Lamina OS Release Process")
    print("=" * 50)
    
    # Step 1: Link validation
    print("\n📋 Step 1: Link Validation")
    if not run_command(
        ["uv", "run", "python", "scripts/validate-links.py"],
        "Validating all documentation links"
    ):
        print("\n❌ RELEASE BLOCKED: Broken links found")
        print("Fix the broken links before proceeding with release.")
        sys.exit(1)
    
    # Step 2: Run tests
    print("\n📋 Step 2: Test Suite")
    if not run_command(
        ["uv", "run", "pytest", "packages/lamina-core/tests/", "-v"],
        "Running test suite"
    ):
        print("\n❌ RELEASE BLOCKED: Tests failed")
        sys.exit(1)
    
    # Step 3: Code quality checks
    print("\n📋 Step 3: Code Quality")
    if not run_command(
        ["uv", "run", "ruff", "check", "packages/lamina-core/"],
        "Running linter checks"
    ):
        print("\n❌ RELEASE BLOCKED: Linting errors found")
        sys.exit(1)
    
    # Step 4: Build package
    print("\n📋 Step 4: Package Build")
    # Clean previous builds
    dist_dir = root_dir / "dist"
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
    
    if not run_command(
        ["uv", "build"],
        f"Building package from {package_dir}"
    ):
        print("\n❌ RELEASE BLOCKED: Package build failed")
        sys.exit(1)
    
    # Step 5: Final validation
    print("\n📋 Step 5: Final Package Validation")
    built_files = list(dist_dir.glob("lamina_core-*"))
    if not built_files:
        print("❌ RELEASE BLOCKED: No built packages found")
        sys.exit(1)
    
    print(f"✅ Built packages:")
    for file in built_files:
        print(f"   • {file.name} ({file.stat().st_size} bytes)")
    
    print("\n" + "=" * 50)
    print("✅ RELEASE VALIDATION PASSED")
    print("All checks completed successfully. Ready for publication!")
    print("\nTo publish:")
    print(f"   uv publish --token $PYPI_TOKEN dist/lamina_core-*")
    print("\nTo create git tag and release:")
    version = built_files[0].name.split("-")[1]
    print(f"   git tag -a v{version} -m 'Release v{version}'")
    print(f"   git push origin v{version}")
    print(f"\nDon't forget to:")
    print(f"   1. Create docs/RELEASE_NOTES_v{version}.md")
    print(f"   2. Create GitHub release at https://github.com/benaskins/lamina-os/releases/new?tag=v{version}")
    print(f"   3. Attach release notes and announce the release")


if __name__ == "__main__":
    main()