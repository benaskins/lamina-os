# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Test configuration and fixtures for Lamina Core testing strategy.

This module implements the ADR-0010 comprehensive testing strategy with
real AI model integration via lamina-llm-serve.
"""

import logging
import os
import time
from collections.abc import Generator
from pathlib import Path

import pytest
import requests

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Add custom pytest command line options for test tiers."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests with real AI models",
    )
    parser.addoption(
        "--e2e", action="store_true", default=False, help="Run end-to-end tests with full system"
    )
    parser.addoption(
        "--all-tests",
        action="store_true",
        default=False,
        help="Run all test tiers (unit + integration + e2e)",
    )
    parser.addoption(
        "--llm-server-url",
        action="store",
        default="http://localhost:8000",
        help="URL of lamina-llm-serve instance for integration tests",
    )


def pytest_collection_modifyitems(config, items):
    """Mark tests based on ADR-0010 test tiers."""
    if (
        not config.getoption("--integration")
        and not config.getoption("--e2e")
        and not config.getoption("--all-tests")
    ):
        # Default: Skip integration and e2e tests
        skip_integration = pytest.mark.skip(reason="need --integration option to run")
        skip_e2e = pytest.mark.skip(reason="need --e2e option to run")

        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)

    elif config.getoption("--integration") and not config.getoption("--e2e"):
        # Integration only: Skip e2e tests
        skip_e2e = pytest.mark.skip(reason="need --e2e option to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)


class LLMTestServer:
    """Test server manager for lamina-llm-serve integration."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.model_name = "llama3.2-1b-q4_k_m"
        self.is_running = False
        self.server_info = None

    def start(self) -> bool:
        """Start or verify LLM server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.is_running = True
                logger.info(f"✅ LLM server already running at {self.base_url}")

                # Try to start the model for testing
                server_info = self.start_model()
                if server_info:
                    logger.info(f"✅ Model {self.model_name} started successfully")
                    self.server_info = server_info
                    return True
                else:
                    logger.warning(f"⚠️  Could not start model {self.model_name}")
                    return False
        except requests.ConnectionError:
            pass

        # Try to start server (this would be environment-specific)
        logger.warning(f"⚠️  LLM server not running at {self.base_url}")
        logger.info("To run integration tests, start lamina-llm-serve:")
        logger.info("  cd ../lamina-llm-serve && uv run python -m lamina_llm_serve.server")
        return False

    def stop(self):
        """Stop the LLM server (if we started it)."""
        self.is_running = False

    def wait_for_readiness(self, timeout: int = 30) -> bool:
        """Wait for server to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    return True
            except requests.ConnectionError:
                pass
            time.sleep(1)
        return False

    def is_model_available(self, model_name: str = None) -> bool:
        """Check if specific model is available."""
        model = model_name or self.model_name
        try:
            response = requests.get(f"{self.base_url}/models/{model}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("available", False)
        except requests.ConnectionError:
            pass
        return False

    def start_model(self, model_name: str = None) -> dict:
        """Start the model server via lamina-llm-serve and get server details."""
        model = model_name or self.model_name
        try:
            # Start the model
            response = requests.post(f"{self.base_url}/models/{model}/start", timeout=30)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Started model {model}: {data}")

                # Get the server details
                response = requests.get(f"{self.base_url}/models/{model}", timeout=5)
                if response.status_code == 200:
                    model_info = response.json()
                    if "server" in model_info:
                        server_info = model_info["server"]
                        logger.info(f"✅ Model server details: {server_info}")
                        return server_info
                    else:
                        logger.warning(f"⚠️  Model {model} started but no server info available")
                else:
                    logger.warning(f"⚠️  Could not get model {model} server details")
            else:
                logger.warning(
                    f"⚠️  Failed to start model {model}: {response.status_code} {response.text}"
                )
        except requests.ConnectionError as e:
            logger.error(f"❌ Connection error starting model {model}: {e}")
        except Exception as e:
            logger.error(f"❌ Error starting model {model}: {e}")
        return None


@pytest.fixture(scope="session")
def llm_server_url(request) -> str:
    """Get LLM server URL from command line or environment."""
    # Environment variable takes precedence over default, but command line still overrides
    default_url = os.getenv("LLM_SERVER_URL", "http://localhost:8000")
    url = request.config.getoption("--llm-server-url")
    if url == "http://localhost:8000":  # This is the default, check env
        url = default_url
    logger.info(f"🔧 LLM Server URL: {url} (env: {os.getenv('LLM_SERVER_URL', 'not set')})")
    return url


@pytest.fixture(scope="session")
def llm_test_server(llm_server_url: str) -> Generator[LLMTestServer, None, None]:
    """Session-scoped LLM test server fixture."""
    server = LLMTestServer(llm_server_url)

    if not server.start():
        pytest.skip(f"LLM server not available at {llm_server_url}")

    if not server.wait_for_readiness():
        pytest.skip("LLM server failed to become ready")

    yield server
    server.stop()


@pytest.fixture(scope="function")
def integration_backend_config(llm_test_server: LLMTestServer) -> dict:
    """Configuration for real backend integration tests."""
    if llm_test_server.server_info:
        # Use the actual model server details
        host = llm_test_server.base_url.split("//")[1].split(":")[0]  # Extract host from base_url
        model_base_url = f"http://{host}:{llm_test_server.server_info['port']}"
        logger.info(f"🔧 Using model server at {model_base_url}")
        return {
            "base_url": model_base_url,
            "model": llm_test_server.model_name,
            "timeout": 30,
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 100,  # Keep responses short for testing
            },
        }
    else:
        # Fallback to management server
        logger.warning("⚠️  No model server info available, using management server")
        return {
            "base_url": llm_test_server.base_url,
            "model": llm_test_server.model_name,
            "timeout": 30,
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 100,  # Keep responses short for testing
            },
        }


@pytest.fixture
def test_artifacts_dir() -> Path:
    """Directory for test artifacts (logs, traces, etc.)."""
    artifacts_dir = Path("test_artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    return artifacts_dir


class TestArtifactLogger:
    """Test artifact logging per Ansel's suggestion."""

    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir
        self.test_logs = []

    def log_response(self, test_name: str, prompt: str, response: str, metadata: dict = None):
        """Log AI response for analysis."""
        log_entry = {
            "timestamp": time.time(),
            "test_name": test_name,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {},
        }
        self.test_logs.append(log_entry)

    def log_model_info(self, model_name: str, model_hash: str = None, version: str = None):
        """Log model information per Vesna's guidance."""
        model_info = {
            "model_name": model_name,
            "model_hash": model_hash,
            "version": version,
            "timestamp": time.time(),
        }

        log_file = self.artifacts_dir / "model_info.log"
        with open(log_file, "a") as f:
            f.write(f"{model_info}\n")

    def save_artifacts(self, test_name: str):
        """Save test artifacts to disk."""
        if self.test_logs:
            log_file = self.artifacts_dir / f"{test_name}_responses.log"
            with open(log_file, "w") as f:
                for entry in self.test_logs:
                    f.write(f"{entry}\n")


@pytest.fixture
def artifact_logger(test_artifacts_dir: Path) -> TestArtifactLogger:
    """Test artifact logger fixture."""
    return TestArtifactLogger(test_artifacts_dir)


# High Council feedback integration fixtures


@pytest.fixture
def breath_validation_criteria() -> dict:
    """Validation criteria for breath-aligned responses per Clara's feedback."""
    return {
        "presence_indicators": ["mindful", "present", "responsive", "attuned"],
        "rushed_indicators": ["quickly", "immediately", "urgent", "fast"],
        "vow_adherence": {
            "no_human_simulation": ["I am", "I feel", "I experience"],
            "grounded_responses": ["based on", "according to", "research shows"],
        },
        "tone_markers": {
            "helpful": ["happy to help", "glad to assist"],
            "thoughtful": ["let me consider", "thinking about", "reflecting on"],
        },
    }


@pytest.fixture
def symbolic_trace_validator() -> callable:
    """Symbolic trace validation per Luna's feedback."""

    def validate_symbolic_traces(response: str, expected_agent: str, intent_type: str) -> dict:
        """Validate symbolic coherence in routing decisions."""
        issues = []

        # Check for agent consistency
        if expected_agent not in response.lower():
            issues.append(f"Response missing expected agent reference: {expected_agent}")

        # Check for intent alignment
        intent_markers = {
            "analytical": ["research", "analyze", "study", "investigate"],
            "creative": ["create", "imagine", "write", "design"],
            "conversational": ["help", "assist", "support"],
        }

        markers = intent_markers.get(intent_type, [])
        if not any(marker in response.lower() for marker in markers):
            issues.append(f"Response lacks {intent_type} intent markers")

        return {"valid": len(issues) == 0, "issues": issues, "symbolic_coherence": len(issues) == 0}

    return validate_symbolic_traces


@pytest.fixture
def real_test_agents(integration_backend_config: dict) -> dict:
    """Real test agents for integration testing."""
    return {
        "researcher": {
            "name": "researcher",
            "description": "Research and analysis agent",
            "personality_traits": ["analytical", "thorough", "methodical"],
            "expertise_areas": ["research", "analysis", "investigation"],
            "backend_config": integration_backend_config,
        },
        "creative": {
            "name": "creative",
            "description": "Creative and artistic agent",
            "personality_traits": ["creative", "imaginative", "expressive"],
            "expertise_areas": ["writing", "art", "storytelling", "design"],
            "backend_config": integration_backend_config,
        },
    }


# Test markers for ADR-0010 test tiers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
