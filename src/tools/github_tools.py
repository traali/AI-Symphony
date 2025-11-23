import uuid
import logging
from github import Github, GithubException
from crewai.tools import BaseTool
from typing import Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from .workspace_tools import WorkspaceManager

logger = logging.getLogger(__name__)


class CreatePRTool(BaseTool):
    """Tool for creating GitHub Pull Requests with automatic retry logic.

    This tool commits all changes in the workspace, pushes to a new branch,
    and creates a Pull Request. Includes retry logic for network failures.

    Attributes:
        name: Tool name for agent identification
        description: Tool description for agent understanding
        workspace: WorkspaceManager instance
        github_client: Authenticated GitHub client
        repo_name: Repository name in format "owner/repo"
        max_retries: Maximum number of retry attempts (default: 3)
    """

    name: str = "GitHub PR Creation Tool"
    description: str = "Commits changes in the workspace and creates a GitHub Pull Request. Provide title and body parameters."
    workspace: Optional[WorkspaceManager] = None
    github_client: Optional[Github] = None
    repo_name: Optional[str] = None
    max_retries: int = 3

    def _run(self, title: str, body: str) -> str:
        """Create a Pull Request with the workspace changes.

        Args:
            title: PR title (will be used in commit message)
            body: PR description/body

        Returns:
            str: PR URL or error message
        """
        # Validate inputs
        if not title or not title.strip():
            error_msg = "PR title cannot be empty"
            logger.error(error_msg)
            return error_msg

        if not body or not body.strip():
            error_msg = "PR body cannot be empty"
            logger.error(error_msg)
            return error_msg

        # Check for changes
        if not self.workspace.repo.is_dirty(untracked_files=True):
            logger.warning("No changes detected in workspace")
            return "No changes detected in the workspace. Nothing to commit."

        try:
            return self._create_pr_with_retry(title, body)
        except Exception as e:
            error_msg = f"Failed to create PR after {self.max_retries} attempts: {e}"
            logger.error(error_msg)
            return error_msg

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GithubException, ConnectionError, TimeoutError)),
        reraise=True,
    )
    def _create_pr_with_retry(self, title: str, body: str) -> str:
        """Create PR with automatic retry on network failures.

        Uses exponential backoff: 2s, 4s, 8s between retries.

        Args:
            title: PR title
            body: PR body

        Returns:
            str: PR URL

        Raises:
            GithubException: On GitHub API errors
            ConnectionError: On network errors
        """
        logger.info(f"Creating PR: {title}")

        # Get repository
        repo = self.github_client.get_repo(self.repo_name)

        # Create unique branch name
        branch = f"feature/ai-symphony-{uuid.uuid4().hex[:8]}"
        logger.debug(f"Using branch name: {branch}")

        # Commit changes
        self.workspace.repo.git.add(A=True)
        commit_message = f"feat: {title}"
        self.workspace.repo.index.commit(commit_message)
        logger.info(f"Committed changes: {commit_message}")

        # Create and checkout new branch
        new_branch = self.workspace.repo.create_head(branch)
        new_branch.checkout()
        logger.debug(f"Checked out branch: {branch}")

        # Push to remote with retry
        self._push_with_retry(branch)

        # Create Pull Request
        pr = repo.create_pull(
            title=title, body=body, head=branch, base=repo.default_branch
        )

        success_msg = f"PR created successfully: {pr.html_url}"
        logger.info(success_msg)
        return success_msg

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def _push_with_retry(self, branch: str):
        """Push branch to remote with retry logic.

        Args:
            branch: Branch name to push

        Raises:
            ConnectionError: On network errors
        """
        logger.info(f"Pushing branch {branch} to remote")
        origin = self.workspace.repo.remote(name="origin")
        origin.push(refspec=f"{branch}:{branch}")
        logger.info(f"Successfully pushed {branch}")
