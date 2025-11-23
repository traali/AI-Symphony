"""
Minimal test: Create hello.html and push to GitHub
"""
import os
import uuid
from dotenv import load_dotenv
from github import Github, Auth
from src.tools.workspace_tools import WorkspaceManager

load_dotenv()

github_pat = os.getenv("GITHUB_PAT")
repo_url = os.getenv("REPO_URL")
repo_name = "/".join(repo_url.split("/")[-2:]).replace(".git", "")

print("🚀 Starting minimal test...")

with WorkspaceManager(repo_url=repo_url, pat=github_pat) as workspace:
    print(f"✅ Workspace created at: {workspace.path}")
    
    # Manually create hello.html
    hello_path = os.path.join(workspace.path, "hello.html")
    with open(hello_path, "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Hello World</title>
</head>
<body>
    <h1>Hello World!</h1>
    <p>This is a minimal test from AI Symphony.</p>
</body>
</html>
""")
    print(f"✅ Created hello.html")
    
    # Check if file exists
    if os.path.exists(hello_path):
        print(f"✅ File verified at: {hello_path}")
    
    # Git operations
    if workspace.repo.is_dirty(untracked_files=True):
        print("✅ Changes detected")
        
        # Add and commit
        workspace.repo.git.add(A=True)
        workspace.repo.index.commit("feat: Add hello.html test file")
        print("✅ Changes committed")
        
        # Create branch
        branch_name = f"feature/minimal-test-{uuid.uuid4().hex[:8]}"
        new_branch = workspace.repo.create_head(branch_name)
        new_branch.checkout()
        print(f"✅ Created branch: {branch_name}")
        
        # Push
        origin = workspace.repo.remote(name='origin')
        origin.push(refspec=f'{branch_name}:{branch_name}')
        print(f"✅ Pushed to {branch_name}")
        
        # Create PR
        github_client = Github(auth=Auth.Token(github_pat))
        repo = github_client.get_repo(repo_name)
        pr = repo.create_pull(
            title="Minimal Test: Hello World HTML",
            body="This is a minimal test to verify the workflow works.",
            head=branch_name,
            base=repo.default_branch
        )
        print(f"✅ PR created: {pr.html_url}")
    else:
        print("❌ No changes detected")

print("🎉 Minimal test complete!")
