# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Model Downloader - Fetch and install models from various sources

Supports downloading from:
- Hugging Face Hub
- Ollama registry
- Direct URLs
- Local file copying
"""

import logging
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ModelDownloader:
    """
    Downloads and installs models from various sources.

    Supports multiple download methods and provides progress tracking.
    """

    def __init__(self, models_dir: str = "models", manifest_data: dict[str, Any] = None):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.manifest_data = manifest_data or {}

        # Download sources registry
        self.sources = {
            "huggingface": self._download_from_huggingface,
            "ollama": self._download_from_ollama,
            "url": self._download_from_url,
            "local": self._copy_from_local,
        }

    def download_model(
        self,
        model_name: str,
        source_config: dict[str, Any],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> bool:
        """
        Download a model from the specified source.

        Args:
            model_name: Name of the model
            source_config: Configuration for the download source
            progress_callback: Optional callback for progress updates

        Returns:
            True if download successful, False otherwise
        """
        source_type = source_config.get("type")
        if source_type not in self.sources:
            logger.error(f"Unknown source type: {source_type}")
            return False

        try:
            logger.info(f"Starting download of {model_name} from {source_type}")

            download_func = self.sources[source_type]
            success = download_func(model_name, source_config, progress_callback)

            if success:
                logger.info(f"Successfully downloaded {model_name}")
            else:
                logger.error(f"Failed to download {model_name}")

            return success

        except Exception as e:
            logger.error(f"Error downloading {model_name}: {e}")
            return False

    def _download_from_huggingface(
        self, model_name: str, config: dict[str, Any], progress_callback: Callable | None = None
    ) -> bool:
        """Download model from Hugging Face Hub"""

        repo_id = config.get("repo_id")
        filename = config.get("filename")

        if not repo_id or not filename:
            logger.error("Hugging Face download requires 'repo_id' and 'filename'")
            return False

        try:
            # Try using huggingface_hub if available
            try:
                from huggingface_hub import hf_hub_download

                model_dir = self.models_dir / model_name
                model_dir.mkdir(exist_ok=True)

                logger.info(f"Downloading {filename} from {repo_id}")

                downloaded_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    cache_dir=str(model_dir),
                    local_dir=str(model_dir),
                    local_dir_use_symlinks=False,
                )

                # Move to expected location if needed
                target_path = model_dir / filename
                if Path(downloaded_path) != target_path:
                    shutil.move(downloaded_path, target_path)

                return True

            except ImportError:
                # Fall back to direct download
                return self._download_hf_direct(repo_id, filename, model_name, progress_callback)

        except Exception as e:
            logger.error(f"Hugging Face download failed: {e}")
            return False

    def _download_hf_direct(
        self,
        repo_id: str,
        filename: str,
        model_name: str,
        progress_callback: Callable | None = None,
    ) -> bool:
        """Direct download from Hugging Face without hub library"""

        url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"

        model_dir = self.models_dir / model_name
        model_dir.mkdir(exist_ok=True)
        target_path = model_dir / filename

        return self._download_file(url, target_path, progress_callback)

    def _download_from_ollama(
        self, model_name: str, config: dict[str, Any], progress_callback: Callable | None = None
    ) -> bool:
        """Download model using Ollama"""

        ollama_model = config.get("ollama_model")
        if not ollama_model:
            logger.error("Ollama download requires 'ollama_model'")
            return False

        try:
            # Check if ollama is available
            result = subprocess.run(["ollama", "--version"], capture_output=True, timeout=5)
            if result.returncode != 0:
                logger.error("Ollama not available")
                return False

            # Pull the model
            logger.info(f"Pulling {ollama_model} with ollama")
            result = subprocess.run(
                ["ollama", "pull", ollama_model],
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes timeout
            )

            if result.returncode != 0:
                logger.error(f"Ollama pull failed: {result.stderr}")
                return False

            # Find where ollama stored the model
            ollama_models_dir = self._find_ollama_models_dir()
            if not ollama_models_dir:
                logger.warning("Could not find ollama models directory")
                return True  # Model pulled but we can't copy it

            # Copy model to our cache
            return self._copy_ollama_model(ollama_model, model_name, ollama_models_dir)

        except subprocess.TimeoutExpired:
            logger.error("Ollama pull timed out")
            return False
        except Exception as e:
            logger.error(f"Ollama download failed: {e}")
            return False

    def _download_from_url(
        self, model_name: str, config: dict[str, Any], progress_callback: Callable | None = None
    ) -> bool:
        """Download model from direct URL"""

        url = config.get("url")
        filename = config.get("filename")

        if not url:
            logger.error("URL download requires 'url'")
            return False

        if not filename:
            # Extract filename from URL
            parsed = urlparse(url)
            filename = Path(parsed.path).name

        model_dir = self.models_dir / model_name
        model_dir.mkdir(exist_ok=True)
        target_path = model_dir / filename

        return self._download_file(url, target_path, progress_callback)

    def _copy_from_local(
        self, model_name: str, config: dict[str, Any], progress_callback: Callable | None = None
    ) -> bool:
        """Copy model from local filesystem"""

        source_path = config.get("source_path")
        if not source_path:
            logger.error("Local copy requires 'source_path'")
            return False

        source = Path(source_path)
        if not source.exists():
            logger.error(f"Source path does not exist: {source_path}")
            return False

        model_dir = self.models_dir / model_name
        model_dir.mkdir(exist_ok=True)

        try:
            if source.is_file():
                # Copy single file
                target_path = model_dir / source.name
                shutil.copy2(source, target_path)
                logger.info(f"Copied {source} to {target_path}")
            else:
                # Copy directory
                target_path = model_dir / source.name
                shutil.copytree(source, target_path, dirs_exist_ok=True)
                logger.info(f"Copied directory {source} to {target_path}")

            return True

        except Exception as e:
            logger.error(f"Local copy failed: {e}")
            return False

    def _download_file(
        self, url: str, target_path: Path, progress_callback: Callable | None = None
    ) -> bool:
        """Download a file with progress tracking"""

        try:
            logger.info(f"Downloading {url} to {target_path}")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(target_path, "wb") as f:
                if total_size > 0:
                    # Use tqdm for progress bar
                    with tqdm(
                        total=total_size, unit="B", unit_scale=True, desc=target_path.name
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            pbar.update(len(chunk))

                            if progress_callback:
                                progress_callback(pbar.n, total_size)
                else:
                    # No content length, just download
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            logger.info(f"Downloaded {target_path} ({target_path.stat().st_size} bytes)")
            return True

        except Exception as e:
            logger.error(f"Download failed: {e}")
            if target_path.exists():
                target_path.unlink()  # Clean up partial download
            return False

    def _find_ollama_models_dir(self) -> Path | None:
        """Find the ollama models directory"""

        # Common ollama model locations
        possible_paths = [
            Path.home() / ".ollama" / "models",
            Path("/opt/ollama/models"),
            Path("/usr/local/share/ollama/models"),
            Path("/tmp/ollama/models"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def _copy_ollama_model(self, ollama_model: str, model_name: str, ollama_dir: Path) -> bool:
        """Copy model from ollama cache to our cache"""

        try:
            # Find the model in ollama directory
            # Ollama stores models with hashed names, so we need to find the right one
            # This is simplified - in practice ollama's storage is more complex

            model_dir = self.models_dir / model_name
            model_dir.mkdir(exist_ok=True)

            # Create a reference file pointing to ollama
            reference_file = model_dir / "ollama_model.txt"
            with open(reference_file, "w") as f:
                f.write(f"ollama:{ollama_model}\n")
                f.write(f"Use 'ollama run {ollama_model}' to access this model\n")

            logger.info(f"Created reference to ollama model {ollama_model}")
            return True

        except Exception as e:
            logger.error(f"Failed to reference ollama model: {e}")
            return False

    def list_downloadable_models(self) -> dict[str, list[dict[str, Any]]]:
        """List models available for download from various sources"""

        downloadable = {"huggingface": [], "ollama": []}

        # Extract download configs from manifest
        models = self.manifest_data.get("models", {})

        for model_name, model_config in models.items():
            download_config = model_config.get("download", {})

            # Add HuggingFace downloads
            if "huggingface" in download_config:
                hf_config = download_config["huggingface"]
                downloadable["huggingface"].append(
                    {
                        "name": model_name,
                        "repo_id": hf_config.get("repo_id"),
                        "filename": hf_config.get("filename"),
                        "size": model_config.get("size", "unknown"),
                        "description": model_config.get("description", "No description"),
                    }
                )

            # Add Ollama downloads
            if "ollama" in download_config:
                ollama_config = download_config["ollama"]
                downloadable["ollama"].append(
                    {
                        "name": model_name,
                        "ollama_model": ollama_config.get("model"),
                        "size": model_config.get("size", "unknown"),
                        "description": model_config.get("description", "No description"),
                    }
                )

        return downloadable

    def get_download_config(self, model_name: str, source_type: str) -> dict[str, Any] | None:
        """Get download configuration for a specific model"""

        downloadable = self.list_downloadable_models()

        if source_type not in downloadable:
            return None

        for model in downloadable[source_type]:
            if model["name"] == model_name:
                config = model.copy()
                config["type"] = source_type
                return config

        return None
