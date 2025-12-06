"""
Error handling tests for AI Symphony.

Tests for:
- Retry logic failure scenarios
- Network/API error handling
- File operation error handling
"""

from unittest.mock import MagicMock, patch

from github import GithubException

from src.tools.github_tools import CreatePRTool
from src.tools.workspace_tools import CodeWriterTool, WorkspaceManager


def create_mock_pr_tool(workspace, github_client, repo_name="test/repo"):
    """Create a CreatePRTool instance with mocked dependencies."""
    tool = CreatePRTool.model_construct(
        _fields_set=set(),
        name="GitHub PR Creation Tool",
        description="Test tool",
        workspace=workspace,
        github_client=github_client,
        repo_name=repo_name,
        max_retries=3,
    )
    return tool


class TestCreatePRToolErrorHandling:
    """Tests for CreatePRTool error handling."""

    def test_github_exception_returns_error_message(
        self, mock_workspace_manager, mock_github_client
    ):
        """Test that GitHub API errors are caught and returned as error messages."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        # Setup mocks
        mock_branch = MagicMock()
        mock_workspace_manager.repo.create_head.return_value = mock_branch
        mock_origin = MagicMock()
        mock_workspace_manager.repo.remote.return_value = mock_origin

        # Make GitHub API throw an exception
        mock_github_client.get_repo.side_effect = GithubException(
            status=403, data={"message": "Rate limit exceeded"}, headers={}
        )

        result = tool._run("Test PR", "Test description")

        assert "Failed to create PR" in result
        assert "3 attempts" in result  # max_retries

    def test_connection_error_returns_error_message(
        self, mock_workspace_manager, mock_github_client
    ):
        """Test that connection errors are caught and returned as error messages."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        # Setup mocks
        mock_branch = MagicMock()
        mock_workspace_manager.repo.create_head.return_value = mock_branch
        mock_origin = MagicMock()
        mock_workspace_manager.repo.remote.return_value = mock_origin

        # Make GitHub API throw a connection error
        mock_github_client.get_repo.side_effect = ConnectionError("Network unreachable")

        result = tool._run("Test PR", "Test description")

        assert "Failed to create PR" in result


class TestWorkspaceManagerErrorHandling:
    """Tests for WorkspaceManager error handling."""

    @patch("src.tools.workspace_tools.Repo")
    @patch("src.tools.workspace_tools.shutil.rmtree")
    def test_cleanup_error_in_production_mode(self, mock_rmtree, mock_repo_class):
        """Test that cleanup errors in production mode are handled gracefully."""
        mock_repo_class.clone_from.return_value = MagicMock()
        mock_rmtree.side_effect = PermissionError("Cannot delete workspace")

        ws = WorkspaceManager(
            repo_url="https://github.com/test/repo.git", pat="fake_token", debug_mode=False
        )

        # Cleanup should not raise, just log the error
        ws.cleanup()  # Should not raise

        # Verify rmtree was called
        mock_rmtree.assert_called()

    @patch("src.tools.workspace_tools.Repo")
    @patch("src.tools.workspace_tools.os.path.exists", return_value=True)
    @patch("src.tools.workspace_tools.shutil.rmtree")
    def test_debug_mode_clear_workspace_error(self, mock_rmtree, mock_exists, mock_repo_class):
        """Test that errors clearing debug workspace are handled gracefully."""
        mock_repo_class.clone_from.return_value = MagicMock()
        mock_rmtree.side_effect = PermissionError("Cannot delete")

        # Should not raise, should continue with workspace creation
        ws = WorkspaceManager(
            repo_url="https://github.com/test/repo.git", pat="fake_token", debug_mode=True
        )

        # Verify workspace was still created despite error
        assert "workspace_debug" in ws.path

    @patch("src.tools.workspace_tools.Repo")
    def test_debug_mode_keeps_workspace_on_cleanup(self, mock_repo_class):
        """Test that debug mode doesn't delete workspace on cleanup."""
        mock_repo_class.clone_from.return_value = MagicMock()

        ws = WorkspaceManager(
            repo_url="https://github.com/test/repo.git", pat="fake_token", debug_mode=True
        )

        with patch("src.tools.workspace_tools.shutil.rmtree") as mock_rmtree:
            ws.cleanup()
            # rmtree should NOT be called in debug mode
            mock_rmtree.assert_not_called()


class TestCodeWriterToolErrorHandling:
    """Tests for CodeWriterTool error handling."""

    def test_write_permission_error(self, mock_workspace_manager):
        """Test that permission errors are caught and returned."""

        tool = CodeWriterTool(workspace=mock_workspace_manager)

        # Make the path read-only by patching open
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = tool._run("test.txt", "content")

        assert "Error writing file" in result
        assert "Permission denied" in result

    def test_write_to_readonly_filesystem(self, mock_workspace_manager):
        """Test handling of readonly filesystem errors."""

        tool = CodeWriterTool(workspace=mock_workspace_manager)

        with patch("builtins.open", side_effect=OSError("Read-only file system")):
            result = tool._run("test.txt", "content")

        assert "Error writing file" in result
