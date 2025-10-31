# 🎼 AI Symphony

AI Symphony is an agentic framework designed to turn a high-level software idea into a pull request. It uses a crew of specialized AI agents (Product Manager, Developer, Reviewer) to specify, implement, and review code in a target repository.

## Quickstart

1.  Follow the `install_guide.md`.
2.  Activate the environment: `source .venv/bin/activate`
3.  Run the symphony: `uv run python src/main.py 'Your idea here'`

## Architecture

- **Orchestration**: `crewai` manages the agents and tasks.
- **Configuration**: Agents, models, and roles are defined in `src/config/agents.yaml`.
- **State Management**: A temporary `WorkspaceManager` clones the target repo, allowing agents to perform real file I/O and Git operations.

## Scaling the Symphony

The default workflow is `Process.sequential`. For more complex tasks, you can switch to a managed approach:

- **Hierarchical Process**: In `src/main.py`, change `process=Process.sequential` to `process=Process.hierarchical` and assign a `manager_llm` to the `Crew`. This introduces a master conductor to delegate tasks dynamically.
- **Observability**: For deeper insights into agent performance, integrate tools like LangSmith to trace and debug agent interactions.
# AI-Symphony
