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


def run_command(cmd: list, description: str, cwd: Path = None) -> bool:
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=cwd)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(cmd)}")
        if cwd:
            print(f"   Working directory: {cwd}")
        print(f"   Exit code: {e.returncode}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False


def main():
    """Main release validation and execution."""
    root_dir = Path(__file__).parent.parent

    print("🚀 Lamina OS Release Process")
    print("=" * 50)

    # Step 1: Link validation
    print("\n📋 Step 1: Link Validation")
    if not run_command(
        ["uv", "run", "python", "scripts/validate-links.py"], "Validating all documentation links"
    ):
        print("\n❌ RELEASE BLOCKED: Broken links found")
        print("Fix the broken links before proceeding with release.")
        sys.exit(1)

    # Step 2: Comprehensive Testing
    print("\n📋 Step 2: Comprehensive Testing")

    # Test lamina-core unit tests
    if not run_command(
        ["uv", "run", "pytest", "packages/lamina-core/tests/", "-v"],
        "Running lamina-core unit tests",
    ):
        print("\n❌ RELEASE BLOCKED: lamina-core unit tests failed")
        sys.exit(1)

    # Test lamina-core integration tests
    if not run_command(
        [
            "uv",
            "run",
            "pytest",
            "packages/lamina-core/tests/",
            "-v",
            "--integration",
            "-k",
            "not real_",
        ],
        "Running lamina-core integration tests",
    ):
        print("\n❌ RELEASE BLOCKED: lamina-core integration tests failed")
        sys.exit(1)

    # Test lamina-llm-serve package import
    if not run_command(
        [
            "uv",
            "run",
            "python",
            "-c",
            "import lamina_llm_serve; print(f'lamina-llm-serve v{lamina_llm_serve.__version__} imported successfully')",
        ],
        "Testing lamina-llm-serve package import",
    ):
        print("\n❌ RELEASE BLOCKED: lamina-llm-serve import test failed")
        sys.exit(1)

    # Step 3: Code quality checks
    print("\n📋 Step 3: Code Quality")
    if not run_command(
        ["uv", "run", "ruff", "check", "packages/lamina-core/"], "Running linter checks"
    ):
        print("\n❌ RELEASE BLOCKED: Linting errors found")
        sys.exit(1)

    # Step 4: Package Build
    print("\n📋 Step 4: Package Build")
    # Clean previous builds
    dist_dir = root_dir / "dist"
    if dist_dir.exists():
        import shutil

        shutil.rmtree(dist_dir)

    # Build lamina-core
    lamina_core_dir = root_dir / "packages" / "lamina-core"
    if not run_command(
        ["uv", "build"], f"Building lamina-core from {lamina_core_dir}", cwd=lamina_core_dir
    ):
        print("\n❌ RELEASE BLOCKED: lamina-core build failed")
        sys.exit(1)

    # Build lamina-llm-serve
    lamina_llm_serve_dir = root_dir / "packages" / "lamina-llm-serve"
    if not run_command(
        ["uv", "build"],
        f"Building lamina-llm-serve from {lamina_llm_serve_dir}",
        cwd=lamina_llm_serve_dir,
    ):
        print("\n❌ RELEASE BLOCKED: lamina-llm-serve build failed")
        sys.exit(1)

    # Step 5: Final validation
    print("\n📋 Step 5: Final Package Validation")
    core_files = list(dist_dir.glob("lamina_core-*"))
    serve_files = list(dist_dir.glob("lamina_llm_serve-*"))

    if not core_files:
        print("❌ RELEASE BLOCKED: No lamina-core packages found")
        sys.exit(1)

    if not serve_files:
        print("❌ RELEASE BLOCKED: No lamina-llm-serve packages found")
        sys.exit(1)

    print("✅ Built packages:")
    for file in core_files + serve_files:
        print(f"   • {file.name} ({file.stat().st_size} bytes)")

    print("\n" + "=" * 50)
    print("✅ RELEASE VALIDATION PASSED")
    print("All checks completed successfully. Ready for publication!")
    print("\nTo publish:")
    print("   uv publish --token $PYPI_TOKEN dist/lamina_core-*")
    print("\nTo create git tag and release:")
    version = core_files[0].name.split("-")[1]
    print(f"   git tag -a v{version} -m 'Release v{version}'")
    print(f"   git push origin v{version}")
    print("\nDon't forget to:")
    print(f"   1. Create docs/RELEASE_NOTES_v{version}.md")
    print(
        f"   2. Create GitHub release at https://github.com/benaskins/lamina-os/releases/new?tag=v{version}"
    )
    print("   3. Attach release notes and announce the release")


if __name__ == "__main__":
    main()
