import os
import sys
import yaml
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from github import Github, Auth

from src.tools.workspace_tools import WorkspaceManager, CodeWriterTool, FileReadTool
from src.tools.github_tools import CreatePRTool

load_dotenv()

def ignite_symphony(idea: str):
    with open("src/config/agents.yaml", "r") as f:
        agents_config = yaml.safe_load(f)["agents"]

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    github_pat = os.getenv("GITHUB_PAT")
    repo_url = os.getenv("REPO_URL")
    repo_name = "/".join(repo_url.split("/")[-2:]).replace(".git", "")

    # Use a 'with' statement for robust workspace setup and cleanup
    with WorkspaceManager(repo_url=repo_url, pat=github_pat) as workspace:
        github_client = Github(auth=Auth.Token(github_pat))
        
        tool_mapping = {
            "file_reader": FileReadTool(workspace=workspace),
            "code_writer": CodeWriterTool(workspace=workspace),
            "create_pr": CreatePRTool(workspace=workspace, github_client=github_client, repo_name=repo_name)
        }

        agents = {}
        for name, config in agents_config.items():
            # Force litellm to use openrouter
            llm_config = {
                "model": config["llm"],
                "api_key": openrouter_api_key,
                "base_url": "https://openrouter.ai/api/v1",
                "default_headers": {"HTTP-Referer": "http://localhost", "X-Title": "AI Symphony"}
            }
            if name == "developer":
                llm_config["temperature"] = 0
            llm = ChatOpenAI(**llm_config)
            # Don't assign tools at agent level
            agents[name] = Agent(
                role=config["role"], goal=config["goal"], backstory=config["backstory"],
                llm=llm, verbose=True, allow_delegation=False
            )

        spec_task = Task(
            description=f"Generate a detailed technical specification for the idea: '{idea}'. The spec must be a clear, step-by-step plan for the developer, including file names and the logic to be implemented.",
            agent=agents["product_manager"],
            expected_output="A markdown document with the full technical specification."
        )
        
        code_task = Task(
            description="""YOU MUST use the Code Writer Tool to create files. Follow these steps:
1. Read the technical specification from the previous task
2. For EACH file mentioned in the spec, YOU MUST call the 'Code Writer Tool' 
3. Use file_path parameter for the filename and content parameter for the code
4. DO NOT just describe the code - you MUST actually call the tool to write each file
5. Verify each file was written by checking the tool's response

CRITICAL: If you don't use the Code Writer Tool, the files will NOT be created.""",
            agent=agents["developer"],
            context=[spec_task],
            expected_output="Confirmation that all files were written using the Code Writer Tool.",
            tools=[tool_mapping["code_writer"], tool_mapping["file_reader"]]
        )
        
        review_task = Task(
            description="""Review the implemented code:
1. Use the File Read Tool to read the files created by the developer
2. Ensure they match the specification
3. Once satisfied, YOU MUST use the Create PR Tool to create a Pull Request
4. The PR title should be clear and descriptive
5. The PR body should summarize what was implemented

CRITICAL: You MUST call the Create PR Tool - don't just describe what the PR should contain.""",
            agent=agents["reviewer"],
            context=[code_task],
            expected_output="The URL of the created Pull Request.",
            tools=[tool_mapping["create_pr"], tool_mapping["file_reader"]]
        )

        crew = Crew(
            agents=list(agents.values()),
            tasks=[spec_task, code_task, review_task],
            process=Process.sequential,
            verbose=True
        )
        
        print("🚀 Igniting AI Symphony...")
        result = crew.kickoff()
        print("\n🎼 Symphony Complete!")
        print(f"Final result: {result}")
        
        print("\n🔍 Debug: Checking workspace contents...")
        for root, dirs, files in os.walk(workspace.path):
            for file in files:
                print(f"  - {os.path.join(root, file)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py \"Your project idea\"")
        sys.exit(1)
    
    project_idea = " ".join(sys.argv[1:])
    ignite_symphony(project_idea)
