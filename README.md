# 🎼 AI Symphony
> **Autonomous AI Teams That Ship Production-Ready Code – Or Spark Your Next Big Idea**

[![CI](https://github.com/traali/AI-Symphony/actions/workflows/ci.yml/badge.svg)](https://github.com/traali/AI-Symphony/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/Powered%20by-CrewAI-orange)](https://www.crewai.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen)](tests/)

**AI Symphony** is an advanced agentic framework that orchestrates a team of specialized AI agents to autonomously plan, code, and review software features.

**One prompt → A full AI crew (Product Manager → Developer → Reviewer) → Real Pull Request in your repo.**

> **Note**: This branch (`feature/business-mode`) includes the experimental **Business Idea Sparrer**.
> The `main` branch is dedicated to the core **Code Symphony** workflow. Switch branches to toggle between pure coding and business validation.

---

## 🚀 Why Developers & Founders Are Obsessed

| Your Current Pain                          | AI Symphony's Solution                                               |
|--------------------------------------------|----------------------------------------------------------------------|
| Copy-pasting AI code → context loss & bugs | Agents clone your repo, write real files, commit & open PRs          |
| PRs from tools like Devin are $500+/month  | Open-source, free with local LLMs – mix Claude, Grok-4, or free Qwen |
| Business ideas die in notebooks            | **New: Business Mode** – AI crew spars ideas into actionable plans   |
| Rigid agent setups (one role per tool)     | YAML-configurable crews: Swap roles, add agents, tweak prompts       |
| "Just one tweak" turns into a weekend      | Iteration loops: Reviewer rejects → Developer fixes → Tests pass     |

---

## ⚡ Dual Modes: Code Like a Pro, Think Like a Founder

### Mode 1: Code Symphony (The Original – Ship Features 10x Faster)
Turn vague ideas into tested, documented code. Perfect for indie hackers, side projects, or accelerating teams.

```bash
ai-symphony "Create a Streamlit leaderboard for top volleyball players by points, with Plotly charts and dark mode"
```
*   **Crew Flow**: Product Manager specs it → Developer codes & commits → Reviewer polishes → PR opens
*   **Output**: Real GitHub Pull Request with files, tests, docs. Merge in one click.

### Mode 2: Business Idea Sparrer (Validate & Monetize Ideas)
Got a startup spark? Let an AI debate team refine it: Optimist hypes the upside, Critic pokes holes, Financial Modeler crunches numbers.

```bash
ai-symphony --mode business "Idea: Subscription-based AI coach for amateur volleyball teams analyzing game footage"
```
*   **Crew Flow**:
    1.  **Positive Agent (Optimist)**: "This could disrupt youth sports – 10M users, viral growth via team shares!"
    2.  **Critical Agent (Devil's Advocate)**: "Market saturation? Privacy risks with video uploads? Churn from inaccurate AI?"
    3.  **Business Calculator Agent**: Builds a model – "Year 1: $500K revenue at 20% margins; Break-even in 18 months."
*   **Output**: Markdown report with pitch deck outline, risk matrix, and 5-year projections.

---

## 🛠️ Real-World Examples That Ship Today

### Code Mode
*   **"Upgrade to FastAPI 0.112 + fix async bugs"** → Migrates your entire backend.
*   **"Add Stripe subscriptions with webhooks"** → Boilerplate + tests done.
*   **"Convert Jupyter notebooks to Streamlit app"** → Interactive dashboard PR.

### Business Mode (Sparrer in Action)
*   **Input**: "App for remote team icebreakers using AR filters"
*   **Optimist**: "Huge B2B play – Slack integration could hit 1M DAU like Donut.ai!"
*   **Critic**: "AR dev costs $200K+; Zoom fatigue means low adoption – pivot to async?"
*   **Calculator**: "Freemium: $2M ARR Year 2 (10K teams @ $20/mo); 3x ROI on seed."
*   **Output**: Full plan PDF + "Build MVP? Y/N" decision matrix.

---

## ⚡ Quick Start

### Prerequisites
*   Python 3.10+
*   `uv` (recommended) or `pip`
*   GitHub Personal Access Token (PAT)
*   OpenRouter API Key

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/traali/AI-Symphony.git
    cd AI-Symphony
    ```

2.  **Set up environment**
    ```bash
    cp .env.example .env
    # Edit .env with your API keys and Repo URL
    ```

3.  **Install dependencies**
    ```bash
    uv sync
    ```

### Usage

Conduct the symphony with a single command:

```bash
# Code mode (default) - generate code and create a PR
ai-symphony "Create a landing page with a dark mode toggle"

# Business mode - validate and analyze a business idea
ai-symphony --mode business "Subscription-based AI coach for amateur sports teams"

# Debug mode - keep workspace files for inspection
ai-symphony --debug "Add user authentication with JWT"

# Dry-run mode - preview what would happen without calling LLMs
ai-symphony --dry-run "Create a REST API"

# Budget limit - stop if costs exceed threshold
ai-symphony --budget 0.50 "Add unit tests for the API"
```

### Web Dashboard

Run the Streamlit dashboard for a visual interface:

```bash
streamlit run src/dashboard.py
```

### Docker

```bash
# Run the web dashboard
docker-compose up dashboard

# Run CLI in Docker
docker-compose run cli "Your idea here"
```

---

## 🏗️ Architecture

AI Symphony is built on a robust, modular architecture designed for reliability and scalability.

*   **Orchestration Engine**: Powered by `crewai`, managing agent lifecycle, task delegation, and context sharing.
*   **Workspace Manager**: A custom context manager that handles ephemeral Git cloning, file operations, and cleanup.
*   **Tool Abstraction**: Custom `BaseTool` implementations for `FileRead`, `CodeWrite`, and `GitHubPR` operations.
*   **Configuration**: Centralized agent definitions in `src/config/agents.yaml` allow for easy tuning of prompts and models.
*   **Cost Tracking**: Built-in OpenRouter cost tracking with budget enforcement.

---

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for details on how to join the orchestra.

---

<div align="center">
  <b>Built with ❤️ by the AI Symphony Team</b>
</div>
