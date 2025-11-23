"""
Direct test to verify CodeWriterTool works
"""
import tempfile
import os
from src.tools.workspace_tools import WorkspaceManager, CodeWriterTool

# Create a temp directory
temp_dir = tempfile.mkdtemp(prefix="test_tool_")
print(f"Testing in: {temp_dir}")

# Create a fake workspace
class FakeWorkspace:
    def __init__(self, path):
        self.path = path

workspace = FakeWorkspace(temp_dir)

# Create and use the tool
tool = CodeWriterTool(workspace=workspace)
result = tool._run("hello.py", "print('Hello World!')")
print(f"Tool result: {result}")

# Verify file exists
hello_path = os.path.join(temp_dir, "hello.py")
if os.path.exists(hello_path):
    with open(hello_path, 'r') as f:
        print(f"✅ File created successfully!")
        print(f"Contents: {f.read()}")
else:
    print("❌ File was NOT created")

# Cleanup
import shutil
shutil.rmtree(temp_dir)
