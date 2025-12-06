"""
Shared pytest fixtures for AI Symphony tests.
"""

import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_workspace():
    """Create a temporary directory for testing file operations."""
    temp_dir = tempfile.mkdtemp(prefix="test_ai_symphony_")
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_git_repo():
    """Create a mock GitPython Repo object."""
    mock_repo = MagicMock()
    mock_repo.is_dirty.return_value = True
    mock_repo.git.add = MagicMock()
    mock_repo.index.commit = MagicMock()
    mock_repo.create_head = MagicMock()
    mock_repo.remote = MagicMock()
    return mock_repo


@pytest.fixture
def mock_github_client():
    """Create a mock PyGitHub client."""
    mock_client = MagicMock()
    mock_repo = MagicMock()
    mock_repo.default_branch = "main"
    mock_pr = MagicMock()
    mock_pr.html_url = "https://github.com/test/repo/pull/1"
    mock_repo.create_pull.return_value = mock_pr
    mock_client.get_repo.return_value = mock_repo
    return mock_client


@pytest.fixture
def mock_workspace_manager(temp_workspace, mock_git_repo):
    """Create a mock WorkspaceManager that passes Pydantic validation.

    This uses patch to avoid actual git clone operations.
    """
    from src.tools.workspace_tools import WorkspaceManager

    with patch.object(WorkspaceManager, "_clone_repo", return_value=mock_git_repo):
        # Create a real WorkspaceManager but with mocked clone
        ws = object.__new__(WorkspaceManager)
        ws.repo_url = "https://oauth2:fake@github.com/test/repo.git"
        ws.debug_mode = False
        ws.path = temp_workspace
        ws.repo = mock_git_repo
        yield ws
