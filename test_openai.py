import os
import sys
import yaml
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from src.tools.workspace_tools import WorkspaceManager, CodeWriterTool, FileReadTool
from src.tools.github_tools import CreatePRTool
from github import Github, Auth

load_dotenv()

def test_with_openai(idea: str):
    """Test with native OpenAI API"""
    
    openai_api_key = os.getenv("OPENAI_API_KEY")  # You'll need to add this to .env
    github_pat = os.getenv("GITHUB_PAT")
    repo_url = os.getenv("REPO_URL")
    repo_name = "/".join(repo_url.split("/")[-2:]).replace(".git", "")
    
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        print("Add: OPENAI_API_KEY=sk-...")
        return
    
    with WorkspaceManager(repo_url=repo_url, pat=github_pat) as workspace:
        github_client = Github(auth=Auth.Token(github_pat))
        
        # Create tools
        code_writer = CodeWriterTool(workspace=workspace)
        file_reader = FileReadTool(workspace=workspace)
        create_pr = CreatePRTool(workspace=workspace, github_client=github_client, repo_name=repo_name)
        
        # Use native OpenAI (proven tool calling)
        llm = ChatOpenAI(
            model="gpt-4o-mini",  # cheaper but still great at tools
            api_key=openai_api_key,
            temperature=0
        )
        
        # Single developer agent
        developer = Agent(
            role="Developer",
            goal="Create the requested code file",
            backstory="You are a developer. You MUST use the Code Writer Tool to save files.",
            llm=llm,
            tools=[code_writer, file_reader],
            verbose=True,
            allow_delegation=False
        )
        
        # Simple task
        task = Task(
            description=f"Create a file for: {idea}. Use the Code Writer Tool to save the file.",
            agent=developer,
            expected_output="Confirmation that the file was written"
        )
        
        crew = Crew(
            agents=[developer],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        print("🚀 Running with native OpenAI...")
        result = crew.kickoff()
        print(f"\n✅ Result: {result}")
        
        # Debug: list files
        print("\n🔍 Files in workspace:")
        for root, dirs, files in os.walk(workspace.path):
            for file in files:
                if not file.startswith('.'):
                    print(f"  - {os.path.join(root, file)}")

if __name__ == "__main__":
    idea = "hello.html with Hello World message"
    test_with_openai(idea)
