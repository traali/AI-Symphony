import argparse
import json
import logging
import os
import sys
from datetime import datetime

import yaml
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
from github import Auth, Github
from langchain_openai import ChatOpenAI

from src.tools.github_tools import CreatePRTool
from src.tools.workspace_tools import CodeWriterTool, FileReadTool, WorkspaceManager

load_dotenv()


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production environments."""

    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)


def setup_logging():
    """Configure logging based on environment variables."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()

    handler = logging.StreamHandler()

    if log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.handlers = []
    root_logger.addHandler(handler)


# Configure logging on module load
setup_logging()
logger = logging.getLogger(__name__)


def ignite_symphony(idea: str, mode: str = "code", debug_mode: bool = True):
    """Execute the AI Symphony workflow to turn an idea into a Pull Request.

    Args:
        idea: High-level project idea or feature description
        mode: 'code' or 'business'
        debug_mode: Enable debug logging
    """
    logger.info("🎼 Starting AI Symphony")
    logger.debug(f"Project idea: {idea}")

    # Load agent configuration
    with open("src/config/agents.yaml") as f:
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
    with WorkspaceManager(repo_url=repo_url, pat=github_pat, debug_mode=debug_mode) as workspace:
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

        # Helper to create agents
        def create_agent(name):
            config = agents_config[name]
            llm_config = {
                "model": config["llm"],
                "api_key": openrouter_api_key,
                "base_url": "https://openrouter.ai/api/v1",
                "default_headers": {"HTTP-Referer": "http://localhost", "X-Title": "AI Symphony"},
            }
            # Set temperature=0 for deterministic agents
            if name in ["developer", "financial_modeler"]:
                llm_config["temperature"] = 0

            llm = ChatOpenAI(**llm_config)

            return Agent(
                role=config["role"],
                goal=config["goal"],
                backstory=config["backstory"],
                llm=llm,
                verbose=True,
                allow_delegation=False,
            )

        if mode == "code":
            print("🎻 Starting Code Symphony...")
            pm = create_agent("product_manager")
            dev = create_agent("developer")
            rev = create_agent("reviewer")

            spec_task = Task(
                description=f"Generate a detailed technical specification for the idea: '{idea}'. The spec must be a clear, step-by-step plan for the developer, including file names and the logic to be implemented.",
                agent=pm,
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
                agent=dev,
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
                agent=rev,
                context=[code_task],
                expected_output="The URL of the created Pull Request.",
                tools=[tool_mapping["create_pr"], tool_mapping["file_reader"]],
            )

            crew = Crew(
                agents=[pm, dev, rev],
                tasks=[spec_task, code_task, review_task],
                process=Process.sequential,
                verbose=True,
            )

        elif mode == "business":
            print("💼 Starting Business Idea Sparrer...")
            optimist = create_agent("optimist")
            critic = create_agent("critic")
            finance = create_agent("financial_modeler")

            hype_task = Task(
                description=f"Analyze the business idea: '{idea}'. Identify the massive upside, potential viral loops, and why this could be a billion-dollar company. Be enthusiastic!",
                agent=optimist,
                expected_output="A high-energy pitch deck outline highlighting the best-case scenario.",
            )

            roast_task = Task(
                description=f"Analyze the same idea: '{idea}'. Ruthlessly critique it. Find the fatal flaws, regulatory risks, and reasons it might fail. Be the 'Devil's Advocate'.",
                agent=critic,
                expected_output="A critical risk assessment report.",
            )

            model_task = Task(
                description="""Synthesize the Optimist's pitch and the Critic's risks.
Then, build a realistic 3-year revenue model.
Calculate:
1. Customer Acquisition Cost (CAC) assumptions
2. Lifetime Value (LTV) assumptions
3. Break-even point
4. Monthly Recurring Revenue (MRR) projections

Finally, produce a 'Verdict' report: Should we build this? (Yes/No/Pivot)""",
                agent=finance,
                context=[hype_task, roast_task],
                expected_output="A comprehensive Business Validation Report with financial projections and a final verdict.",
                tools=[tool_mapping["code_writer"]],  # To save the report
            )

            crew = Crew(
                agents=[optimist, critic, finance],
                tasks=[hype_task, roast_task, model_task],
                process=Process.sequential,
                verbose=True,
            )

        else:
            print(f"❌ Unknown mode: {mode}")
            return

        print(f"🚀 Igniting AI Symphony in {mode.upper()} mode...")
        result = crew.kickoff()
        print("\n🎼 Symphony Complete!")
        print(f"Final result: {result}")

        # Debug: List workspace contents
        if debug_mode:
            logger.debug("Workspace contents:")
            for root, _dirs, files in os.walk(workspace.path):
                for file in files:
                    logger.debug(f"  - {os.path.join(root, file)}")


def cli():
    """Command-line interface entry point for ai-symphony."""
    parser = argparse.ArgumentParser(
        prog="ai-symphony",
        description="AI Symphony - Autonomous Agent Teams for Code Generation",
        epilog="Examples:\n  ai-symphony 'Create a REST API for user management'\n  ai-symphony --mode business 'AI-powered pet food delivery'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("idea", help="The idea to build or validate")
    parser.add_argument(
        "--mode",
        choices=["code", "business"],
        default="code",
        help="Mode: 'code' for shipping features, 'business' for validating ideas",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (keeps workspace after completion)",
    )

    args = parser.parse_args()

    try:
        ignite_symphony(args.idea, args.mode, debug_mode=args.debug)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
