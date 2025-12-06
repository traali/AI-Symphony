"""
Unit tests for src/tools/workspace_tools.py

Tests for:
- WorkspaceManager (initialization, cleanup, context manager)
- FileReadTool
- CodeWriterTool
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

from src.tools.workspace_tools import (
    CodeWriterTool,
    FileReadTool,
    WorkspaceManager,
)


class TestFileReadTool:
    """Tests for FileReadTool."""

    def test_read_existing_file(self, mock_workspace_manager):
        """Test reading an existing file returns its contents."""
        # Create a test file
        test_file = "test.txt"
        test_content = "Hello, World!"
        file_path = os.path.join(mock_workspace_manager.path, test_file)
        with open(file_path, "w") as f:
            f.write(test_content)

        # Create tool and read file
        tool = FileReadTool(workspace=mock_workspace_manager)
        result = tool._run(test_file)

        assert result == test_content

    def test_read_nonexistent_file(self, mock_workspace_manager):
        """Test reading a non-existent file returns an error message."""
        tool = FileReadTool(workspace=mock_workspace_manager)
        result = tool._run("nonexistent.txt")

        assert "Error reading file" in result

    def test_read_file_in_subdirectory(self, mock_workspace_manager):
        """Test reading a file in a subdirectory."""
        # Create subdirectory and file
        subdir = os.path.join(mock_workspace_manager.path, "subdir")
        os.makedirs(subdir)
        test_content = "Nested content"
        with open(os.path.join(subdir, "nested.txt"), "w") as f:
            f.write(test_content)

        tool = FileReadTool(workspace=mock_workspace_manager)
        result = tool._run("subdir/nested.txt")

        assert result == test_content


class TestCodeWriterTool:
    """Tests for CodeWriterTool."""

    def test_write_new_file(self, mock_workspace_manager):
        """Test writing a new file creates it with correct content."""
        tool = CodeWriterTool(workspace=mock_workspace_manager)

        result = tool._run("hello.py", "print('Hello!')")

        assert "Successfully wrote" in result

        # Verify file exists and has correct content
        file_path = os.path.join(mock_workspace_manager.path, "hello.py")
        assert os.path.exists(file_path)
        with open(file_path) as f:
            assert f.read() == "print('Hello!')"

    def test_write_file_creates_directories(self, mock_workspace_manager):
        """Test writing to a file in a non-existent directory creates the directory."""
        tool = CodeWriterTool(workspace=mock_workspace_manager)

        result = tool._run("src/utils/helpers.py", "# helpers")

        assert "Successfully wrote" in result

        # Verify directory was created
        dir_path = os.path.join(mock_workspace_manager.path, "src", "utils")
        assert os.path.isdir(dir_path)

    def test_overwrite_existing_file(self, mock_workspace_manager):
        """Test writing to an existing file overwrites it."""
        file_path = os.path.join(mock_workspace_manager.path, "existing.txt")
        with open(file_path, "w") as f:
            f.write("old content")

        tool = CodeWriterTool(workspace=mock_workspace_manager)
        result = tool._run("existing.txt", "new content")

        assert "Successfully wrote" in result
        with open(file_path) as f:
            assert f.read() == "new content"

    def test_write_returns_byte_count(self, mock_workspace_manager):
        """Test that success message includes byte count."""
        tool = CodeWriterTool(workspace=mock_workspace_manager)
        content = "12345"  # 5 bytes

        result = tool._run("count.txt", content)

        assert "5 bytes" in result


class TestWorkspaceManager:
    """Tests for WorkspaceManager initialization and cleanup.

    Note: These tests mock git clone operations to avoid network calls.
    """

    @patch("src.tools.workspace_tools.Repo")
    def test_debug_mode_uses_workspace_debug_path(self, mock_repo_class):
        """Test that debug mode uses the workspace_debug directory."""
        mock_repo_class.clone_from.return_value = MagicMock()

        # Use a fake repo URL (won't actually clone due to mock)
        ws = WorkspaceManager(
            repo_url="https://github.com/test/repo.git", pat="fake_token", debug_mode=True
        )

        try:
            assert "workspace_debug" in ws.path
        finally:
            # Don't actually cleanup since we mocked everything
            pass

    @patch("src.tools.workspace_tools.Repo")
    def test_production_mode_uses_temp_directory(self, mock_repo_class):
        """Test that production mode uses a temp directory."""
        mock_repo_class.clone_from.return_value = MagicMock()

        ws = WorkspaceManager(
            repo_url="https://github.com/test/repo.git", pat="fake_token", debug_mode=False
        )

        try:
            assert ws.path.startswith(tempfile.gettempdir())
            assert "ai-symphony-" in ws.path
        finally:
            # Cleanup the temp directory we created
            if os.path.exists(ws.path):
                os.rmdir(ws.path)

    @patch("src.tools.workspace_tools.Repo")
    def test_context_manager_calls_cleanup(self, mock_repo_class):
        """Test that exiting context manager triggers cleanup."""
        mock_repo_class.clone_from.return_value = MagicMock()

        with patch.object(WorkspaceManager, "cleanup") as mock_cleanup:
            with WorkspaceManager(
                repo_url="https://github.com/test/repo.git", pat="fake_token", debug_mode=False
            ):
                pass

            mock_cleanup.assert_called_once()

    @patch("src.tools.workspace_tools.Repo")
    def test_repo_url_includes_pat(self, mock_repo_class):
        """Test that the repo URL is modified to include PAT for authentication."""
        mock_repo_class.clone_from.return_value = MagicMock()

        ws = WorkspaceManager(
            repo_url="https://github.com/test/repo.git", pat="my_secret_token", debug_mode=False
        )

        try:
            # Check that clone_from was called with OAuth URL
            call_args = mock_repo_class.clone_from.call_args
            assert "oauth2:my_secret_token@" in call_args[0][0]
        finally:
            if os.path.exists(ws.path):
                os.rmdir(ws.path)
