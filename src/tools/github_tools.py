import os
import uuid
from github import Github
from crewai.tools import BaseTool
from typing import Optional
from .workspace_tools import WorkspaceManager

class CreatePRTool(BaseTool):
    name: str = "GitHub PR Creation Tool"
    description: str = "Commits changes in the workspace and creates a GitHub Pull Request."
    workspace: Optional[WorkspaceManager] = None
    github_client: Optional[Github] = None
    repo_name: Optional[str] = None

    def _run(self, title: str, body: str) -> str:
        if not self.workspace.repo.is_dirty(untracked_files=True):
            return "No changes detected in the workspace. Nothing to commit."

        repo = self.github_client.get_repo(self.repo_name)
        
        # Create a unique branch name to avoid collisions
        branch = f"feature/ai-symphony-{uuid.uuid4().hex[:8]}"
        
        # Commit and Push
        self.workspace.repo.git.add(A=True)
        self.workspace.repo.index.commit(f"feat: {title}")
        
        new_branch = self.workspace.repo.create_head(branch)
        new_branch.checkout()

        origin = self.workspace.repo.remote(name='origin')
        # This push is non-forceful and targets a new, unique branch.
        origin.push(refspec=f'{branch}:{branch}')

        # Create PR
        pr = repo.create_pull(title=title, body=body, head=branch, base=repo.default_branch)
        return f"PR created successfully: {pr.html_url}"
