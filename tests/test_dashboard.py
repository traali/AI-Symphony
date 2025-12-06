"""
Tests for the Streamlit Dashboard.

These are functional tests that verify the dashboard components work correctly.
"""

import os
import queue
from unittest.mock import patch


class TestDashboardFunctions:
    """Tests for dashboard utility functions."""

    def test_check_environment_returns_missing_vars(self):
        """Test that check_environment identifies missing variables."""
        # Import here to avoid Streamlit initialization issues
        from src.dashboard import check_environment

        with patch.dict(os.environ, {}, clear=True):
            missing = check_environment()
            assert "OPENROUTER_API_KEY" in missing
            assert "GITHUB_PAT" in missing
            assert "REPO_URL" in missing

    def test_check_environment_returns_empty_when_all_set(self):
        """Test that check_environment returns empty when all vars are set."""
        from src.dashboard import check_environment

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test_key",
                "GITHUB_PAT": "test_pat",
                "REPO_URL": "https://github.com/test/repo.git",
            },
        ):
            missing = check_environment()
            assert missing == []


class TestStreamlitLogHandler:
    """Tests for the custom log handler."""

    def test_log_handler_puts_messages_in_queue(self):
        """Test that the log handler puts formatted messages in the queue."""
        import logging

        from src.dashboard import StreamlitLogHandler

        log_queue = queue.Queue()
        handler = StreamlitLogHandler(log_queue)

        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Check that message was added to queue
        msg = log_queue.get_nowait()
        assert "Test message" in msg
        assert "INFO" in msg


class TestRunSymphonyThread:
    """Tests for the symphony execution thread."""

    @patch("src.dashboard.ignite_symphony")
    def test_thread_puts_done_marker(self, mock_ignite):
        """Test that the thread puts __DONE__ marker when complete."""
        from src.dashboard import run_symphony_thread

        mock_ignite.return_value = None
        log_queue = queue.Queue()

        run_symphony_thread("Test idea", "code", False, log_queue)

        # Collect all messages
        messages = []
        while not log_queue.empty():
            messages.append(log_queue.get_nowait())

        assert "__DONE__" in messages

    @patch("src.dashboard.ignite_symphony")
    def test_thread_logs_mode_and_idea(self, mock_ignite):
        """Test that the thread logs the mode and idea."""
        from src.dashboard import run_symphony_thread

        mock_ignite.return_value = None
        log_queue = queue.Queue()

        run_symphony_thread("My test idea", "business", False, log_queue)

        messages = []
        while not log_queue.empty():
            messages.append(log_queue.get_nowait())

        assert any("BUSINESS" in msg for msg in messages)
        assert any("My test idea" in msg for msg in messages)

    @patch("src.dashboard.ignite_symphony")
    def test_thread_handles_exceptions(self, mock_ignite):
        """Test that the thread handles exceptions gracefully."""
        from src.dashboard import run_symphony_thread

        mock_ignite.side_effect = ValueError("Test error")
        log_queue = queue.Queue()

        run_symphony_thread("Test idea", "code", False, log_queue)

        messages = []
        while not log_queue.empty():
            messages.append(log_queue.get_nowait())

        assert any("Error" in msg or "error" in msg for msg in messages)
        assert "__DONE__" in messages
