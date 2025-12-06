<div align="center">

# 🎼 AI Symphony

**Autonomous AI Agents That Ship Production-Ready Code**

[![CI/CD](https://github.com/traali/AI-Symphony/actions/workflows/ci.yml/badge.svg)](https://github.com/traali/AI-Symphony/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage 81%](https://img.shields.io/badge/Coverage-81%25-brightgreen)](tests/)
[![License MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ed?logo=docker&logoColor=white)](docker-compose.yml)

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🎯 What is AI Symphony?

AI Symphony orchestrates a team of specialized AI agents to autonomously **plan, code, review, and ship** software features. Give it a prompt, and it delivers a real GitHub Pull Request.

```
Your Idea → Product Manager → Developer → Code Reviewer → Pull Request ✨
```

### Why AI Symphony?

| Problem | Solution |
|---------|----------|
| Copy-pasting AI code loses context | Agents work directly in your repo with full context |
| AI coding tools are expensive ($500+/mo) | Open-source, use any LLM via OpenRouter |
| Code from AI needs heavy review | Built-in Code Reviewer agent ensures quality |
| Hard to validate business ideas | Business Mode analyzes viability with multiple perspectives |

---

## ✨ Features

### 🔧 **Dual Operating Modes**

<table>
<tr>
<td width="50%">

**Code Mode** (Default)

Turn ideas into production code:
- Product Manager creates specs
- Developer implements the code
- Reviewer ensures quality & opens PR

```bash
ai-symphony "Add dark mode toggle"
```

</td>
<td width="50%">

**Business Mode**

Validate startup ideas:
- Optimist highlights opportunities
- Critic identifies risks
- Financial Modeler calculates projections

```bash
ai-symphony --mode business "AI coach app"
```

</td>
</tr>
</table>

### 🛡️ **Built-in Safeguards**

| Feature | Description |
|---------|-------------|
| **Cost Tracking** | Real-time API cost monitoring with budget limits |
| **Dry Run Mode** | Preview actions without making LLM calls |
| **Debug Mode** | Preserve workspace files for inspection |
| **Retry Logic** | Automatic retries for GitHub API operations |

### 🖥️ **Multiple Interfaces**

- **CLI** — Full-featured command-line interface
- **Web Dashboard** — Streamlit UI with real-time streaming logs
- **Docker** — Containerized deployment ready

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token ([create one](https://github.com/settings/tokens))
- OpenRouter API Key ([get one](https://openrouter.ai/keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/traali/AI-Symphony.git
cd AI-Symphony

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Install dependencies (using uv - recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Configuration

Edit your `.env` file:

```env
# Required
OPENROUTER_API_KEY=your_openrouter_key
GITHUB_PAT=ghp_your_github_pat
REPO_URL=https://github.com/you/your-repo.git

# Optional
DEBUG_MODE=false
MAX_RETRIES=3
LOG_LEVEL=INFO
```

---

## 📖 Usage

### Command Line Interface

```bash
# Basic usage - generate code and create a PR
ai-symphony "Create a REST API with user authentication"

# Business mode - validate a startup idea
ai-symphony --mode business "Subscription fitness app for remote teams"

# Set a budget limit (stops if costs exceed threshold)
ai-symphony --budget 0.50 "Add comprehensive unit tests"

# Dry run - preview actions without calling LLMs
ai-symphony --dry-run "Refactor the database layer"

# Debug mode - keep workspace files for inspection
ai-symphony --debug "Add Stripe payment integration"
```

### Web Dashboard

Launch the Streamlit dashboard for a visual interface:

```bash
streamlit run src/dashboard.py
```

Features:
- 📝 Input your idea
- 🔄 Select mode (Code/Business)
- 📊 Real-time streaming logs
- 🔗 Direct link to created PR

### Docker Deployment

```bash
# Start the web dashboard
docker-compose up dashboard

# Run a CLI command
docker-compose run cli "Your idea here"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Symphony                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Product   │  │  Developer  │  │  Reviewer   │  Code Mode   │
│  │   Manager   │──│             │──│             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Optimist   │  │   Critic    │  │  Financial  │  Business    │
│  │             │──│             │──│   Modeler   │  Mode        │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                         Core Services                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  Workspace   │ │    Cost      │ │   GitHub     │             │
│  │   Manager    │ │   Tracker    │ │   Tools      │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Description |
|-----------|-------------|
| **CrewAI Orchestration** | Manages agent lifecycle, task delegation, and context |
| **Workspace Manager** | Handles ephemeral Git cloning, file operations, cleanup |
| **Cost Tracker** | Monitors OpenRouter API costs with budget enforcement |
| **GitHub Tools** | Commits changes, pushes branches, creates Pull Requests |

### Agent Configuration

Agents are defined in `src/config/agents.yaml`:

```yaml
agents:
  product_manager:
    role: Product Manager
    goal: Create clear, actionable technical specifications
    llm: "openrouter/anthropic/claude-3-5-sonnet-20241022"

  developer:
    role: Full-Stack Developer
    goal: Implement specifications into clean code
    tools: [code_writer, file_reader]
```

---

## 🧪 Testing

AI Symphony has comprehensive test coverage:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Current coverage: 81%
```

| Module | Coverage |
|--------|----------|
| `github_tools.py` | 100% |
| `workspace_tools.py` | 97% |
| `cost_tracker.py` | 93% |
| `main.py` | 64% |

---

## 📁 Project Structure

```
ai-symphony/
├── src/
│   ├── main.py              # CLI entry point & orchestration
│   ├── dashboard.py         # Streamlit web UI
│   ├── cost_tracker.py      # API cost monitoring
│   ├── config/
│   │   └── agents.yaml      # Agent definitions
│   └── tools/
│       ├── workspace_tools.py  # File operations
│       └── github_tools.py     # PR creation
├── tests/                   # Comprehensive test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.in
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install dev dependencies
uv pip install -r requirements.in

# Run linting
ruff check src/

# Run tests
pytest tests/ -v
```

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using [CrewAI](https://www.crewai.io/) and [OpenRouter](https://openrouter.ai/)**

[Report Bug](https://github.com/traali/AI-Symphony/issues) • [Request Feature](https://github.com/traali/AI-Symphony/issues)

</div>
