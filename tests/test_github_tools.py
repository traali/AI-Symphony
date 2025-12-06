"""
Unit tests for src/tools/github_tools.py

Tests for:
- CreatePRTool input validation
- CreatePRTool change detection
- CreatePRTool PR creation flow (mocked)
"""

from unittest.mock import MagicMock

from src.tools.github_tools import CreatePRTool


def create_mock_pr_tool(workspace, github_client, repo_name="test/repo"):
    """Create a CreatePRTool instance with mocked dependencies, bypassing Pydantic validation."""
    # Use model_construct to bypass validation
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


class TestCreatePRToolValidation:
    """Tests for CreatePRTool input validation."""

    def test_empty_title_returns_error(self, mock_workspace_manager, mock_github_client):
        """Test that empty PR title returns an error message."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        result = tool._run("", "Some body text")

        assert "title cannot be empty" in result.lower()

    def test_whitespace_title_returns_error(self, mock_workspace_manager, mock_github_client):
        """Test that whitespace-only PR title returns an error message."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        result = tool._run("   ", "Some body text")

        assert "title cannot be empty" in result.lower()

    def test_empty_body_returns_error(self, mock_workspace_manager, mock_github_client):
        """Test that empty PR body returns an error message."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        result = tool._run("Some title", "")

        assert "body cannot be empty" in result.lower()

    def test_whitespace_body_returns_error(self, mock_workspace_manager, mock_github_client):
        """Test that whitespace-only PR body returns an error message."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        result = tool._run("Some title", "   \n\t  ")

        assert "body cannot be empty" in result.lower()


class TestCreatePRToolChangeDetection:
    """Tests for CreatePRTool change detection."""

    def test_no_changes_returns_message(self, mock_workspace_manager, mock_github_client):
        """Test that no changes in workspace returns appropriate message."""
        # Configure mock to report no dirty files
        mock_workspace_manager.repo.is_dirty.return_value = False

        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        result = tool._run("My PR Title", "My PR Description")

        assert "no changes" in result.lower()


class TestCreatePRToolCreation:
    """Tests for CreatePRTool PR creation flow."""

    def test_successful_pr_creation(self, mock_workspace_manager, mock_github_client):
        """Test successful PR creation returns PR URL."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        # Setup mock for branch checkout
        mock_branch = MagicMock()
        mock_workspace_manager.repo.create_head.return_value = mock_branch

        # Setup mock for remote push
        mock_origin = MagicMock()
        mock_workspace_manager.repo.remote.return_value = mock_origin

        result = tool._run("Add new feature", "This adds a cool feature")

        assert "PR created successfully" in result
        assert "https://github.com/test/repo/pull/1" in result

    def test_pr_creation_commits_changes(self, mock_workspace_manager, mock_github_client):
        """Test that PR creation commits all changes."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        # Setup mocks
        mock_branch = MagicMock()
        mock_workspace_manager.repo.create_head.return_value = mock_branch
        mock_origin = MagicMock()
        mock_workspace_manager.repo.remote.return_value = mock_origin

        tool._run("Add feature", "Description")

        # Verify git add was called
        mock_workspace_manager.repo.git.add.assert_called_once_with(A=True)

        # Verify commit was made
        mock_workspace_manager.repo.index.commit.assert_called_once()

    def test_pr_creation_creates_feature_branch(self, mock_workspace_manager, mock_github_client):
        """Test that PR creation creates a feature branch."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        # Setup mocks
        mock_branch = MagicMock()
        mock_workspace_manager.repo.create_head.return_value = mock_branch
        mock_origin = MagicMock()
        mock_workspace_manager.repo.remote.return_value = mock_origin

        tool._run("Add feature", "Description")

        # Verify branch was created with feature/ prefix
        call_args = mock_workspace_manager.repo.create_head.call_args
        branch_name = call_args[0][0]
        assert branch_name.startswith("feature/ai-symphony-")

    def test_pr_creation_pushes_to_remote(self, mock_workspace_manager, mock_github_client):
        """Test that PR creation pushes branch to remote."""
        tool = create_mock_pr_tool(mock_workspace_manager, mock_github_client)

        # Setup mocks
        mock_branch = MagicMock()
        mock_workspace_manager.repo.create_head.return_value = mock_branch
        mock_origin = MagicMock()
        mock_workspace_manager.repo.remote.return_value = mock_origin

        tool._run("Add feature", "Description")

        # Verify push was called
        mock_origin.push.assert_called_once()


class TestCreatePRToolRetryMethods:
    """Tests for CreatePRTool retry method existence."""

    def test_has_create_pr_with_retry_method(self):
        """Test that CreatePRTool has the retry-decorated method."""
        assert hasattr(CreatePRTool, "_create_pr_with_retry")

    def test_has_push_with_retry_method(self):
        """Test that CreatePRTool has the push retry method."""
        assert hasattr(CreatePRTool, "_push_with_retry")
