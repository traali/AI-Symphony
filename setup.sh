#!/bin/bash
set -e
echo "🎼 Tuning AI Symphony..."

# Secure .env handling
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ Created .env from example."
  echo "🛑 IMPORTANT: Open .env and add your API keys and the target REPO_URL."
  open .env # Opens in your default editor
  read -p "Press [Enter] after saving your keys and repo URL..."
fi

# Validate keys are not placeholders and repo is accessible
if grep -q "your_openrouter_key_here\|ghp_your_github_pat_here\|YOUR_TARGET_REPO" .env; then
  echo "❌ Keys or REPO_URL are not set. Edit .env and rerun."
  exit 1
fi
chmod 600 .env # Secure the file
source .env
REPO_NAME=$(basename "$REPO_URL" .git)
USER_NAME=$(echo "$REPO_URL" | cut -d'/' -f4)
if ! gh repo view "$USER_NAME/$REPO_NAME" > /dev/null 2>&1; then
    echo "❌ Error: Cannot access repository '$USER_NAME/$REPO_NAME'. Ensure it exists and your GITHUB_PAT has correct permissions."
    exit 1
fi
echo "✅ Successfully validated access to repository."

# Create Python virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate
echo "Compiling and syncing dependencies..."
uv pip compile requirements.in -o requirements.txt
uv pip sync requirements.txt

# Install optional dependencies for tools like Serper
uv pip install "crewai[tools]"

echo "✅ Symphony tuned! Activate with 'source .venv/bin/activate'."
