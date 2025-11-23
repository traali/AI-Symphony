import os
import shutil
import tempfile
import logging
from git import Repo
from crewai.tools import BaseTool
from typing import Optional

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """Manages a Git workspace for agents.

    Provides context manager interface for safe workspace creation and cleanup.
    Handles Git cloning with authentication and configurable cleanup behavior.

    Args:
        repo_url: HTTPS URL to Git repository
        pat: GitHub Personal Access Token
        debug_mode: If True, keeps workspace for inspection. If False, uses temp directory

    Example:
        with WorkspaceManager(url, token) as ws:
            # Use ws.path for file operations
            pass
    """

    def __init__(self, repo_url: str, pat: str, debug_mode: bool = False):
        """Initialize workspace manager with repository URL and authentication.

        Args:
            repo_url: HTTPS URL to the Git repository
            pat: GitHub Personal Access Token for authentication
            debug_mode: Whether to keep workspace for debugging (default: False)
        """
        self.repo_url = repo_url.replace("https://", f"https://oauth2:{pat}@")
        self.debug_mode = debug_mode

        if self.debug_mode:
            # Use fixed path for debugging and inspection
            self.path = os.path.abspath("./workspace_debug")

            # Clear previous run's workspace if it exists
            if os.path.exists(self.path):
                try:
                    shutil.rmtree(self.path)
                    logger.debug(f"Cleared existing debug workspace at {self.path}")
                except Exception as e:
                    logger.warning(f"Could not clear old workspace: {e}")

            os.makedirs(self.path, exist_ok=True)
        else:
            # Use temporary directory for production
            self.path = tempfile.mkdtemp(prefix="ai-symphony-")
            logger.debug(f"Created temporary workspace at {self.path}")

        self.repo = self._clone_repo()

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and cleanup resources."""
        self.cleanup()

    def _clone_repo(self) -> Repo:
        """Clone the repository into the workspace.

        Returns:
            Repo: GitPython Repo object
        """
        logger.info(f"Cloning repository into {self.path}")
        return Repo.clone_from(self.repo_url, self.path)

    def cleanup(self):
        """Clean up workspace based on debug mode setting."""
        if self.debug_mode:
            logger.info(f"Debug mode: Workspace kept at {self.path}")
        else:
            try:
                shutil.rmtree(self.path)
                logger.info(f"Cleaned up workspace at {self.path}")
            except Exception as e:
                logger.error(f"Failed to cleanup workspace: {e}")


class FileReadTool(BaseTool):
    """Tool for reading file contents from the workspace.

    Attributes:
        name: Tool name for agent identification
        description: Tool description for agent understanding
        workspace: WorkspaceManager instance
    """

    name: str = "File Read Tool"
    description: str = (
        "Reads the content of a file in the workspace. Provide the relative file path."
    )
    workspace: Optional[WorkspaceManager] = None

    def _run(self, file_path: str) -> str:
        """Read and return the contents of a file.

        Args:
            file_path: Relative path to the file within the workspace

        Returns:
            str: File contents or error message
        """
        full_path = os.path.join(self.workspace.path, file_path)
        logger.debug(f"Reading file: {file_path}")

        try:
            with open(full_path, "r") as f:
                content = f.read()
            logger.info(f"Successfully read {file_path} ({len(content)} bytes)")
            return content
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {e}"
            logger.error(error_msg)
            return error_msg


class CodeWriterTool(BaseTool):
    """Tool for writing code files to the workspace.

    Attributes:
        name: Tool name for agent identification
        description: Tool description for agent understanding
        workspace: WorkspaceManager instance
    """

    name: str = "Code Writer Tool"
    description: str = "Writes or overwrites a file in the workspace with new code. Provide file_path and content parameters."
    workspace: Optional[WorkspaceManager] = None

    def _run(self, file_path: str, content: str) -> str:
        """Write content to a file in the workspace.

        Args:
            file_path: Relative path to the file within the workspace
            content: Content to write to the file

        Returns:
            str: Success message or error message
        """
        logger.info(f"Writing to file: {file_path}")
        full_path = os.path.join(self.workspace.path, file_path)

        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            with open(full_path, "w") as f:
                f.write(content)
            success_msg = f"Successfully wrote to {file_path} ({len(content)} bytes)"
            logger.info(success_msg)
            return success_msg
        except Exception as e:
            error_msg = f"Error writing file {file_path}: {e}"
            logger.error(error_msg)
            return error_msg
