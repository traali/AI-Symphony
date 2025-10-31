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
            llm = ChatOpenAI(model=config["llm"], api_key=openrouter_api_key, base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)")
            tools = [tool_mapping[t] for t in config.get("tools", [])]
            agents[name] = Agent(
                role=config["role"], goal=config["goal"], backstory=config["backstory"],
                llm=llm, tools=tools, verbose=True, allow_delegation=False
            )

        spec_task = Task(
            description=f"Generate a detailed technical specification for the idea: '{idea}'. The spec must be a clear, step-by-step plan for the developer, including file names and the logic to be implemented.",
            agent=agents["product_manager"],
            expected_output="A markdown document with the full technical specification."
        )
        
        code_task = Task(
            description="Implement the code based *only* on the technical specification. Use the Code Writer Tool to create or modify files. Read existing files first if necessary.",
            agent=agents["developer"],
            context=[spec_task],
            expected_output="The full implementation of the code in the workspace."
        )
        
        review_task = Task(
            description="Review the implemented code. Read the files to ensure they match the spec. Once satisfied, create a Pull Request with a clear title and summary.",
            agent=agents["reviewer"],
            context=[code_task],
            expected_output="A URL to the created Pull Request on GitHub."
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py \"Your project idea\"")
        sys.exit(1)
    
    project_idea = " ".join(sys.argv[1:])
    ignite_symphony(project_idea)
