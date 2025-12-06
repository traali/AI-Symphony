"""
Integration tests for the AI Symphony workflow.

These tests validate the full execution path of ignite_symphony
with mocked external dependencies (LLM, GitHub API, Git operations).
"""

import os
from unittest.mock import MagicMock, patch


class TestIgniteSymphonyCodeMode:
    """Integration tests for code mode workflow."""

    @patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "test_key",
            "GITHUB_PAT": "test_pat",
            "REPO_URL": "https://github.com/test/repo.git",
            "DEBUG_MODE": "false",
            "MAX_RETRIES": "1",
        },
    )
    @patch("src.main.load_dotenv")
    @patch("src.main.WorkspaceManager")
    @patch("src.main.Github")
    @patch("src.main.FileReadTool")
    @patch("src.main.CodeWriterTool")
    @patch("src.main.CreatePRTool")
    @patch("src.main.ChatOpenAI")
    @patch("src.main.Crew")
    @patch("src.main.Agent")
    @patch("src.main.Task")
    def test_code_mode_happy_path(
        self,
        mock_task,
        mock_agent,
        mock_crew,
        mock_llm,
        mock_create_pr,
        mock_code_writer,
        mock_file_reader,
        mock_github,
        mock_workspace_manager,
        mock_dotenv,
        capsys,
    ):
        """Test that code mode executes successfully with all mocks."""
        import src.main

        # Setup workspace mock
        mock_ws_instance = MagicMock()
        mock_ws_instance.path = "/tmp/test_workspace"
        mock_workspace_manager.return_value.__enter__ = MagicMock(return_value=mock_ws_instance)
        mock_workspace_manager.return_value.__exit__ = MagicMock(return_value=False)

        # Setup crew mock
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "PR created: https://github.com/test/repo/pull/1"
        mock_crew.return_value = mock_crew_instance

        # Execute
        src.main.ignite_symphony("Create a hello world app", mode="code")

        # Verify crew was created and executed
        mock_crew.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()

        # Verify output
        captured = capsys.readouterr()
        assert "Code Symphony" in captured.out or "Symphony Complete" in captured.out


class TestIgniteSymphonyBusinessMode:
    """Integration tests for business mode workflow."""

    @patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "test_key",
            "GITHUB_PAT": "test_pat",
            "REPO_URL": "https://github.com/test/repo.git",
            "DEBUG_MODE": "false",
            "MAX_RETRIES": "1",
        },
    )
    @patch("src.main.load_dotenv")
    @patch("src.main.WorkspaceManager")
    @patch("src.main.Github")
    @patch("src.main.FileReadTool")
    @patch("src.main.CodeWriterTool")
    @patch("src.main.CreatePRTool")
    @patch("src.main.ChatOpenAI")
    @patch("src.main.Crew")
    @patch("src.main.Agent")
    @patch("src.main.Task")
    def test_business_mode_happy_path(
        self,
        mock_task,
        mock_agent,
        mock_crew,
        mock_llm,
        mock_create_pr,
        mock_code_writer,
        mock_file_reader,
        mock_github,
        mock_workspace_manager,
        mock_dotenv,
        capsys,
    ):
        """Test that business mode executes successfully with all mocks."""
        import src.main

        # Setup workspace mock
        mock_ws_instance = MagicMock()
        mock_ws_instance.path = "/tmp/test_workspace"
        mock_workspace_manager.return_value.__enter__ = MagicMock(return_value=mock_ws_instance)
        mock_workspace_manager.return_value.__exit__ = MagicMock(return_value=False)

        # Setup crew mock
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Business validation complete"
        mock_crew.return_value = mock_crew_instance

        # Execute
        src.main.ignite_symphony("AI-powered pet food delivery", mode="business")

        # Verify crew was created and executed
        mock_crew.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()

        # Verify output
        captured = capsys.readouterr()
        assert "Business Idea Sparrer" in captured.out or "Symphony Complete" in captured.out


class TestAgentCreation:
    """Tests for agent creation logic."""

    @patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "test_key",
            "GITHUB_PAT": "test_pat",
            "REPO_URL": "https://github.com/test/repo.git",
        },
    )
    @patch("src.main.load_dotenv")
    @patch("src.main.WorkspaceManager")
    @patch("src.main.Github")
    @patch("src.main.FileReadTool")
    @patch("src.main.CodeWriterTool")
    @patch("src.main.CreatePRTool")
    @patch("src.main.ChatOpenAI")
    @patch("src.main.Crew")
    @patch("src.main.Agent")
    @patch("src.main.Task")
    def test_code_mode_creates_three_agents(
        self,
        mock_task,
        mock_agent,
        mock_crew,
        mock_llm,
        mock_create_pr,
        mock_code_writer,
        mock_file_reader,
        mock_github,
        mock_workspace_manager,
        mock_dotenv,
    ):
        """Test that code mode creates PM, developer, and reviewer agents."""
        import src.main

        # Setup workspace mock
        mock_ws_instance = MagicMock()
        mock_ws_instance.path = "/tmp/test_workspace"
        mock_workspace_manager.return_value.__enter__ = MagicMock(return_value=mock_ws_instance)
        mock_workspace_manager.return_value.__exit__ = MagicMock(return_value=False)

        # Setup crew mock
        mock_crew_instance = MagicMock()
        mock_crew.return_value = mock_crew_instance

        # Execute
        src.main.ignite_symphony("Test idea", mode="code")

        # Verify 3 agents were created (PM, developer, reviewer)
        assert mock_agent.call_count == 3

    @patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "test_key",
            "GITHUB_PAT": "test_pat",
            "REPO_URL": "https://github.com/test/repo.git",
        },
    )
    @patch("src.main.load_dotenv")
    @patch("src.main.WorkspaceManager")
    @patch("src.main.Github")
    @patch("src.main.FileReadTool")
    @patch("src.main.CodeWriterTool")
    @patch("src.main.CreatePRTool")
    @patch("src.main.ChatOpenAI")
    @patch("src.main.Crew")
    @patch("src.main.Agent")
    @patch("src.main.Task")
    def test_business_mode_creates_three_agents(
        self,
        mock_task,
        mock_agent,
        mock_crew,
        mock_llm,
        mock_create_pr,
        mock_code_writer,
        mock_file_reader,
        mock_github,
        mock_workspace_manager,
        mock_dotenv,
    ):
        """Test that business mode creates optimist, critic, and financial modeler agents."""
        import src.main

        # Setup workspace mock
        mock_ws_instance = MagicMock()
        mock_ws_instance.path = "/tmp/test_workspace"
        mock_workspace_manager.return_value.__enter__ = MagicMock(return_value=mock_ws_instance)
        mock_workspace_manager.return_value.__exit__ = MagicMock(return_value=False)

        # Setup crew mock
        mock_crew_instance = MagicMock()
        mock_crew.return_value = mock_crew_instance

        # Execute
        src.main.ignite_symphony("Test business idea", mode="business")

        # Verify 3 agents were created (optimist, critic, financial_modeler)
        assert mock_agent.call_count == 3
