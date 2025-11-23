import os
import shutil
import tempfile
from git import Repo
from crewai.tools import BaseTool
from typing import Optional

class WorkspaceManager:
    """Manages a Git workspace for agents."""
    def __init__(self, repo_url: str, pat: str):
        self.repo_url = repo_url.replace("https://", f"https://oauth2:{pat}@")
        
        # FIX: Use a fixed path so you can inspect files after the run
        self.path = os.path.abspath("./workspace_debug")
        
        # Clear previous run's workspace if it exists
        if os.path.exists(self.path):
            try:
                shutil.rmtree(self.path)
            except Exception as e:
                print(f"⚠️ Warning: Could not clear old workspace: {e}")

        os.makedirs(self.path, exist_ok=True)
        self.repo = self._clone_repo()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def _clone_repo(self) -> Repo:
        print(f"Cloning {self.repo_url} into {self.path}...")
        return Repo.clone_from(self.repo_url, self.path)

    def cleanup(self):
        # FIX: Commented out cleanup to keep files for inspection
        print(f"🧹 Workspace KEPT for debugging at: {self.path}")
        # shutil.rmtree(self.path) 

class FileReadTool(BaseTool):
    name: str = "File Read Tool"
    description: str = "Reads the content of a file in the workspace."
    workspace: Optional[WorkspaceManager] = None

    def _run(self, file_path: str) -> str:
        full_path = os.path.join(self.workspace.path, file_path)
        try:
            with open(full_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

class CodeWriterTool(BaseTool):
    name: str = "Code Writer Tool"
    description: str = "Writes or overwrites a file in the workspace with new code."
    workspace: Optional[WorkspaceManager] = None

    def _run(self, file_path: str, content: str) -> str:
        print(f"📝 WRITING TO FILE: {file_path}")
        full_path = os.path.join(self.workspace.path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        try:
            with open(full_path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
