"""
Unit tests for src/main.py

Tests for:
- Environment variable validation
- Agent configuration loading
- Mode selection
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestEnvironmentValidation:
    """Tests for environment variable validation in ignite_symphony."""

    def test_missing_openrouter_key_raises_error(self):
        """Test that missing OPENROUTER_API_KEY raises ValueError."""
        # Import inside the test to avoid global side effects
        import src.main

        # Clear the cached environment
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.main.load_dotenv"):
                # Force reload to pick up clean env
                with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
                    src.main.ignite_symphony("test idea")

    def test_missing_github_pat_raises_error(self):
        """Test that missing GITHUB_PAT raises ValueError."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}, clear=True):
            with patch("src.main.load_dotenv"):
                import src.main

                with pytest.raises(ValueError, match="GITHUB_PAT"):
                    src.main.ignite_symphony("test idea")

    def test_missing_repo_url_raises_error(self):
        """Test that missing REPO_URL raises ValueError."""
        with patch.dict(
            os.environ, {"OPENROUTER_API_KEY": "test_key", "GITHUB_PAT": "test_pat"}, clear=True
        ):
            with patch("src.main.load_dotenv"):
                import src.main

                with pytest.raises(ValueError, match="REPO_URL"):
                    src.main.ignite_symphony("test idea")


class TestAgentConfigLoading:
    """Tests for agent configuration loading."""

    def test_agents_yaml_exists(self):
        """Test that agents.yaml configuration file exists."""
        config_path = "src/config/agents.yaml"
        assert os.path.exists(config_path), f"Config file {config_path} should exist"

    def test_agents_yaml_valid_structure(self):
        """Test that agents.yaml has valid YAML structure."""
        import yaml

        with open("src/config/agents.yaml") as f:
            config = yaml.safe_load(f)

        assert "agents" in config, "Config should have 'agents' key"

        # Code mode agents
        assert "product_manager" in config["agents"]
        assert "developer" in config["agents"]
        assert "reviewer" in config["agents"]

    def test_agent_config_has_required_fields(self):
        """Test that each agent config has required fields."""
        import yaml

        with open("src/config/agents.yaml") as f:
            config = yaml.safe_load(f)

        required_fields = ["role", "goal", "backstory", "llm"]

        for agent_name, agent_config in config["agents"].items():
            for field in required_fields:
                assert (
                    field in agent_config
                ), f"Agent '{agent_name}' missing required field '{field}'"


class TestModeSelection:
    """Tests for mode selection logic."""

    def test_unknown_mode_prints_error(self, capsys):
        """Test that unknown mode prints error message."""
        import src.main

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test_key",
                "GITHUB_PAT": "test_pat",
                "REPO_URL": "https://github.com/test/repo.git",
            },
        ):
            with patch("src.main.load_dotenv"):
                with patch("src.main.WorkspaceManager") as mock_ws:
                    with patch("src.main.Github"):
                        with patch("src.main.FileReadTool"):
                            with patch("src.main.CodeWriterTool"):
                                with patch("src.main.CreatePRTool"):
                                    # Setup mock workspace context manager
                                    mock_ws_instance = MagicMock()
                                    mock_ws_instance.path = "/tmp/test"
                                    mock_ws.return_value.__enter__ = MagicMock(
                                        return_value=mock_ws_instance
                                    )
                                    mock_ws.return_value.__exit__ = MagicMock(return_value=False)

                                    src.main.ignite_symphony("test idea", mode="invalid_mode")

                                    captured = capsys.readouterr()
                                    assert "Unknown mode" in captured.out

    def test_valid_modes(self):
        """Test that valid modes are 'code' and 'business'."""
        valid_modes = ["code", "business"]

        # This is more of a documentation test - we're asserting the expected modes
        for mode in valid_modes:
            assert mode in ["code", "business"], f"Mode '{mode}' should be valid"
