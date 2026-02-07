# 🎼 AI Symphony

> **Autonomous AI Teams That Ship Production-Ready Code – Or Spark Your Next Big Idea**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![CrewAI](https://img.shields.io/badge/Powered%20by-CrewAI-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/traali/AI-Symphony/ci.yml?branch=main&style=for-the-badge&label=CI)

## 1. Problem
Developers and founders often face a "blank page" problem or get bogged down in boilerplate code. Existing AI tools often lack repository context, leading to manual copy-pasting, context loss, and high subscription costs for "black box" agentic services.

## 2. Solution
**AI Symphony** is an open-source, agentic framework that orchestrates specialized AI teams (Product Manager, Developer, Reviewer) to autonomously plan, code, and review software features. It operates directly on your repository, creating real Pull Requests without manual intervention. It also features a "Business Mode" for rapid startup idea validation.

## 3. Architecture
AI Symphony is built on a modular architecture designed for reliability and transparency.

- **Orchestration Engine**: Powered by `CrewAI`, managing agent roles, task delegation, and context sharing.
- **LLM Backend**: Uses `LiteLLM` via OpenRouter to support 100+ models (Claude, GPT, Gemini, Llama).
- **Workspace Manager**: A custom context manager for ephemeral Git cloning and secure file operations.
- **Custom Tools**: Specialized tools for `FileRead`, `CodeWrite`, and `GitHubPR` operations.

See [architecture.md](docs/architecture.md) for a deeper dive.

---

## 🚀 Why Developers & Founders Are Obsessed

| Your Current Pain                          | AI Symphony's Solution                                               |
|--------------------------------------------|----------------------------------------------------------------------|
| Copy-pasting AI code → context loss & bugs | Agents clone your repo, write real files, commit & open PRs          |
| PRs from tools like Devin are $500+/month  | Open-source, free with local LLMs – mix Claude, GPT-4, or Qwen|
| Business ideas die in notebooks            | **New: Business Mode** – AI crew spars ideas into actionable plans   |
| Rigid agent setups (one role per tool)     | YAML-configurable crews: Swap roles, add agents, tweak prompts       |

---

## ⚡ Dual Modes: Code Like a Pro, Think Like a Founder

### Mode 1: Code Symphony (Ship Features 10x Faster)
```bash
uv run python src/main.py "Create a Streamlit leaderboard for top volleyball players by points, with Plotly charts and dark mode"
```
*   **Yields**: Real GitHub Pull Request with files, tests, and docs.

### Mode 2: Business Idea Sparrer (Validate & Monetize)
```bash
uv run python src/main.py --mode business "Idea: Subscription-based AI coach for teams"
```
*   **Yields**: Markdown report with pitch deck outline, risk matrix, and 5-year projections.

📂 See [samples/business_mode_example.md](samples/business_mode_example.md) for a complete example output.

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`
- GitHub Personal Access Token (PAT)
- OpenRouter API Key

> [!CAUTION]
> **Security: GitHub PAT Scoping**  
> When creating your GitHub Personal Access Token, use **minimal permissions**:
> - ✅ `repo` (for private repos) or `public_repo` (for public repos only)
> - ❌ Do NOT grant `admin`, `delete_repo`, or `workflow` permissions
> - ❌ Never commit your `.env` file or share your token
> 
> Treat your PAT like a password. Rotate it regularly.

### Installation & Setup

**Option 1: Clone & Run (Recommended)**
```bash
git clone https://github.com/traali/AI-Symphony.git
cd AI-Symphony
cp .env.example .env  # Add your keys
uv sync
uv run python src/main.py "Your idea here"
```

**Option 2: Install via pip**
```bash
pip install git+https://github.com/traali/AI-Symphony.git
```

---

## 🤖 Using Local LLMs (Free & Private)

AI Symphony supports local LLMs through LiteLLM, enabling cost-free and fully private operation.

### Ollama Setup
```bash
# 1. Install Ollama: https://ollama.ai
# 2. Pull a model
ollama pull qwen2.5:14b

# 3. Update your .env
OPENROUTER_API_KEY=ollama  # Use 'ollama' as placeholder
LITELLM_MODEL=ollama/qwen2.5:14b
```

### LM Studio Setup
```bash
# 1. Download LM Studio: https://lmstudio.ai
# 2. Load any GGUF model and start the local server
# 3. Update your .env
OPENROUTER_API_KEY=lm-studio  # Placeholder
LITELLM_MODEL=openai/local-model
LITELLM_API_BASE=http://localhost:1234/v1
```

> [!TIP]
> For best results with code generation, use models with 14B+ parameters like `qwen2.5:14b`, `codellama:34b`, or `deepseek-coder:33b`.

---

## 🧪 Testing

The repository includes several test scripts to verify your setup:

```bash
# Verify LLM connectivity
uv run python test_llm.py

# Test workspace tools directly
uv run python test_tools_directly.py

# Run a minimal end-to-end test (creates a PR)
uv run python minimal_test.py
```

CI status is automatically verified on every push. See the badge above for current status.

---

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for details on how to join the orchestra.

---

<div align="center">
  <b>Built with ❤️ by Arto Oinonen</b>
</div>
