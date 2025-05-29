#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Model Manager CLI

Command-line interface for managing models in the Lamina LLM cache.
Provides tools for listing, validating, and downloading models.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add package to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from lamina_llm_serve.backends import list_available_backends, validate_backend_setup
from lamina_llm_serve.downloader import ModelDownloader
from lamina_llm_serve.model_manager import ModelManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def cmd_list_models(manager: ModelManager, args):
    """List all models in the manifest"""
    models = manager.list_models()

    if not models:
        print("No models found in manifest")
        return

    print(f"📋 Found {len(models)} models:")

    for model_name in models:
        model_info = manager.get_model_info(model_name)
        available = "✅" if manager.is_model_available(model_name) else "❌"
        backend = model_info.get("backend", "unknown")
        size = model_info.get("size", "unknown")

        print(f"  {available} {model_name}")
        print(f"     Backend: {backend} | Size: {size}")

        if args.verbose:
            description = model_info.get("description", "No description")
            path = model_info.get("path", "No path")
            print(f"     Description: {description}")
            print(f"     Path: {path}")
        print()


def cmd_validate_models(manager: ModelManager, args):
    """Validate all models in the manifest"""
    print("🔍 Validating models...")

    validation = manager.validate_models()
    missing = manager.get_missing_models()

    print("\n📊 Validation Results:")
    print(f"   Total models: {len(validation)}")
    print(f"   Available: {sum(validation.values())}")
    print(f"   Missing: {len(missing)}")

    if missing:
        print("\n❌ Missing models:")
        for model_name in missing:
            model_info = manager.get_model_info(model_name)
            path = model_info.get("path", "unknown")
            print(f"   {model_name} -> {path}")

    if args.verbose:
        print("\n📈 Detailed validation:")
        for model_name, available in validation.items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"   {model_name}: {status}")


def cmd_check_backends(manager: ModelManager, args):
    """Check backend availability"""
    print("🔧 Checking backends...")

    backend_configs = manager.backends
    available_backends = list_available_backends(backend_configs)
    validation_results = validate_backend_setup(backend_configs)

    print("\n📊 Backend Status:")
    print(f"   Configured: {len(backend_configs)}")
    print(f"   Available: {len(available_backends)}")

    for backend_name, result in validation_results.items():
        status = "✅" if result["available"] else "❌"
        executable = result.get("executable", "unknown")

        print(f"\n   {status} {backend_name}")
        print(f"      Executable: {executable}")

        if "error" in result:
            print(f"      Error: {result['error']}")

        if args.verbose and "config" in result:
            config = result["config"]
            if "default_args" in config:
                print(f"      Default args: {config['default_args']}")


def cmd_stats(manager: ModelManager, args):
    """Show statistics about the model collection"""
    stats = manager.get_model_stats()

    print("📈 Model Collection Statistics:")
    print(f"   Total models: {stats['total_models']}")
    print(f"   Available models: {stats['available_models']}")
    print(f"   Missing models: {stats['missing_models']}")
    print(f"   Categories: {len(stats['categories'])}")
    print(f"   Backends: {len(stats['backends'])}")
    print(f"   Use cases: {len(stats['use_cases'])}")

    if args.verbose:
        print(f"\n📂 Categories: {', '.join(stats['categories'])}")
        print(f"🔧 Backends: {', '.join(stats['backends'])}")
        print(f"🎯 Use cases: {', '.join(stats['use_cases'])}")


def cmd_suggest_model(manager: ModelManager, args):
    """Suggest a model based on requirements"""
    requirements = {}

    if args.use_case:
        requirements["use_case"] = args.use_case

    if args.category:
        requirements["category"] = args.category

    suggested = manager.suggest_model(requirements)

    if suggested:
        model_info = manager.get_model_info(suggested)
        print(f"💡 Suggested model: {suggested}")
        print(f"   Backend: {model_info.get('backend')}")
        print(f"   Size: {model_info.get('size')}")
        print(f"   Description: {model_info.get('description')}")

        if not manager.is_model_available(suggested):
            print("   ⚠️  Model not available on filesystem")
    else:
        print("❌ No suitable model found")


def cmd_model_info(manager: ModelManager, args):
    """Show detailed information about a specific model"""
    model_name = args.model
    model_info = manager.get_model_info(model_name)

    if not model_info:
        print(f"❌ Model '{model_name}' not found in manifest")
        return

    available = manager.is_model_available(model_name)
    status = "✅ Available" if available else "❌ Missing"

    print(f"📋 Model Information: {model_name}")
    print(f"   Status: {status}")
    print(f"   Backend: {model_info.get('backend', 'unknown')}")
    print(f"   Path: {model_info.get('path', 'unknown')}")
    print(f"   Size: {model_info.get('size', 'unknown')}")
    print(f"   Quantization: {model_info.get('quantization', 'unknown')}")
    print(f"   Description: {model_info.get('description', 'No description')}")


def cmd_list_downloadable(manager: ModelManager, args):
    """List models available for download"""
    downloader = ModelDownloader(manager.models_dir, manager.manifest)
    downloadable = downloader.list_downloadable_models()

    # Filter by source if specified
    if args.source:
        if args.source in downloadable:
            downloadable = {args.source: downloadable[args.source]}
        else:
            downloadable = {}

    print("📥 Models available for download:")

    for source_type, models in downloadable.items():
        print(f"\n🔹 {source_type.title()} models:")
        for model in models:
            name = model["name"]
            size = model.get("size", "unknown")
            description = model.get("description", "No description")
            print(f"   {name} ({size}) - {description}")


def cmd_download_model(manager: ModelManager, args):
    """Download a specific model"""
    model_name = args.model
    source = args.source

    downloader = ModelDownloader(manager.models_dir, manager.manifest)

    # Get download configuration
    download_config = downloader.get_download_config(model_name, source)
    if not download_config:
        print(f"❌ Model '{model_name}' not available for download from {source}")

        # Show available models
        downloadable = downloader.list_downloadable_models()
        if source in downloadable:
            print(f"\n💡 Available {source} models:")
            for model in downloadable[source]:
                print(f"   {model['name']}")
        return

    print(f"📥 Downloading {model_name} from {source}...")
    print(f"   Size: {download_config.get('size', 'unknown')}")
    print(f"   Description: {download_config.get('description', 'No description')}")

    # Start download
    success = downloader.download_model(model_name, download_config)

    if success:
        print(f"✅ Successfully downloaded {model_name}")

        # Check if it's now available
        manager.reload_manifest()  # Reload in case paths changed
        if manager.is_model_available(model_name):
            print("🎯 Model is now available for use")
        else:
            print("⚠️  Model downloaded but may need path configuration in models.yaml")
    else:
        print(f"❌ Failed to download {model_name}")


def cmd_install_model(manager: ModelManager, args):
    """Install a model from local path"""
    model_name = args.model
    source_path = args.path

    downloader = ModelDownloader(manager.models_dir, manager.manifest)

    config = {"type": "local", "source_path": source_path}

    print(f"📦 Installing {model_name} from local path: {source_path}")

    success = downloader.download_model(model_name, config)

    if success:
        print(f"✅ Successfully installed {model_name}")

        # Check if it's now available
        manager.reload_manifest()
        if manager.is_model_available(model_name):
            print("🎯 Model is now available for use")
        else:
            print("⚠️  Model installed but may need path configuration in models.yaml")
    else:
        print(f"❌ Failed to install {model_name}")


def main():
    parser = argparse.ArgumentParser(description="Lamina LLM Model Manager")
    parser.add_argument("--manifest", default="models.yaml", help="Path to model manifest")
    parser.add_argument("--models-dir", default="models", help="Path to models directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List all models")
    list_parser.set_defaults(func=cmd_list_models)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate model availability")
    validate_parser.set_defaults(func=cmd_validate_models)

    # Backends command
    backends_parser = subparsers.add_parser("backends", help="Check backend availability")
    backends_parser.set_defaults(func=cmd_check_backends)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show collection statistics")
    stats_parser.set_defaults(func=cmd_stats)

    # Suggest command
    suggest_parser = subparsers.add_parser("suggest", help="Suggest a model")
    suggest_parser.add_argument(
        "--use-case", choices=["conversational", "analytical", "security", "reasoning"]
    )
    suggest_parser.add_argument("--category", choices=["lightweight", "balanced", "reasoning"])
    suggest_parser.set_defaults(func=cmd_suggest_model)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show model information")
    info_parser.add_argument("model", help="Model name")
    info_parser.set_defaults(func=cmd_model_info)

    # List downloadable command
    list_dl_parser = subparsers.add_parser("list-downloadable", help="List downloadable models")
    list_dl_parser.add_argument(
        "--source", choices=["huggingface", "ollama"], help="Filter by source"
    )
    list_dl_parser.set_defaults(func=cmd_list_downloadable)

    # Download command
    download_parser = subparsers.add_parser("download", help="Download a model")
    download_parser.add_argument("model", help="Model name to download")
    download_parser.add_argument(
        "--source", choices=["huggingface", "ollama"], help="Download source"
    )
    download_parser.set_defaults(func=cmd_download_model)

    # Install command
    install_parser = subparsers.add_parser("install", help="Install model from local path")
    install_parser.add_argument("model", help="Model name")
    install_parser.add_argument("path", help="Local path to model files")
    install_parser.set_defaults(func=cmd_install_model)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create model manager
    try:
        manager = ModelManager(args.manifest, args.models_dir)
    except Exception as e:
        logger.error(f"Failed to initialize model manager: {e}")
        sys.exit(1)

    # Execute command
    try:
        args.func(manager, args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
