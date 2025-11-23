import os
import sys
import yaml
import logging
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from github import Github, Auth

from src.tools.workspace_tools import WorkspaceManager, CodeWriterTool, FileReadTool
from src.tools.github_tools import CreatePRTool

load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def ignite_symphony(idea: str):
    """Execute the AI Symphony workflow to turn an idea into a Pull Request.

    Args:
        idea: High-level project idea or feature description
    """
    logger.info("🎼 Starting AI Symphony")
    logger.debug(f"Project idea: {idea}")

    # Load agent configuration
    with open("src/config/agents.yaml", "r") as f:
        agents_config = yaml.safe_load(f)["agents"]

    # Get environment variables
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    github_pat = os.getenv("GITHUB_PAT")
    repo_url = os.getenv("REPO_URL")
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    max_retries = int(os.getenv("MAX_RETRIES", "3"))

    # Validate required environment variables
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment")
        raise ValueError("OPENROUTER_API_KEY is required")

    if not github_pat:
        logger.error("GITHUB_PAT not found in environment")
        raise ValueError("GITHUB_PAT is required")

    if not repo_url:
        logger.error("REPO_URL not found in environment")
        raise ValueError("REPO_URL is required")

    repo_name = "/".join(repo_url.split("/")[-2:]).replace(".git", "")
    logger.info(f"Target repository: {repo_name}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Max retries: {max_retries}")

    # Use context manager for robust workspace setup and cleanup
    with WorkspaceManager(
        repo_url=repo_url, pat=github_pat, debug_mode=debug_mode
    ) as workspace:
        logger.info(f"Workspace initialized at: {workspace.path}")

        github_client = Github(auth=Auth.Token(github_pat))

        # Initialize tools
        tool_mapping = {
            "file_reader": FileReadTool(workspace=workspace),
            "code_writer": CodeWriterTool(workspace=workspace),
            "create_pr": CreatePRTool(
                workspace=workspace,
                github_client=github_client,
                repo_name=repo_name,
                max_retries=max_retries,
            ),
        }
        logger.debug("Tools initialized")

        # Create agents
        agents = {}
        for name, config in agents_config.items():
            logger.debug(f"Creating agent: {name}")

            # Configure LLM with OpenRouter
            llm_config = {
                "model": config["llm"],
                "api_key": openrouter_api_key,
                "base_url": "https://openrouter.ai/api/v1",
                "default_headers": {
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "AI Symphony",
                },
            }

            # Use temperature 0 for developer (deterministic code generation)
            if name == "developer":
                llm_config["temperature"] = 0

            llm = ChatOpenAI(**llm_config)

            # Create agent (tools assigned at task level)
            agents[name] = Agent(
                role=config["role"],
                goal=config["goal"],
                backstory=config["backstory"],
                llm=llm,
                verbose=True,
                allow_delegation=False,
            )

        logger.info(f"Created {len(agents)} agents")

        # Define tasks
        spec_task = Task(
            description=f"Generate a detailed technical specification for the idea: '{idea}'. The spec must be a clear, step-by-step plan for the developer, including file names and the logic to be implemented.",
            agent=agents["product_manager"],
            expected_output="A markdown document with the full technical specification.",
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
            tools=[tool_mapping["code_writer"], tool_mapping["file_reader"]],
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
            tools=[tool_mapping["create_pr"], tool_mapping["file_reader"]],
        )

        # Create and run crew
        crew = Crew(
            agents=list(agents.values()),
            tasks=[spec_task, code_task, review_task],
            process=Process.sequential,
            verbose=True,
        )

        logger.info("🚀 Igniting AI Symphony...")
        result = crew.kickoff()

        logger.info("🎼 Symphony Complete!")
        logger.info(f"Final result: {result}")

        # Debug: List workspace contents
        if debug_mode:
            logger.debug("Workspace contents:")
            for root, dirs, files in os.walk(workspace.path):
                for file in files:
                    logger.debug(f"  - {os.path.join(root, file)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python src/main.py "Your project idea"')
        sys.exit(1)

    project_idea = " ".join(sys.argv[1:])

    try:
        ignite_symphony(project_idea)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
