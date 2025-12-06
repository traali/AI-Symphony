"""
AI Symphony Web Dashboard

A Streamlit-based web interface for running AI Symphony workflows.
Provides real-time log streaming and easy mode selection.
"""

import logging
import os
import queue
import sys
import threading
from io import StringIO

import streamlit as st
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import ignite_symphony

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Symphony",
    page_icon="🎼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .log-container {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.85rem;
        height: 400px;
        overflow-y: auto;
    }
    .success-box {
        background-color: #1e3a1e;
        border: 1px solid #2e7d32;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


class StreamlitLogHandler(logging.Handler):
    """Custom log handler that captures logs for Streamlit display."""

    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
        self.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
        )

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)


def check_environment():
    """Check if required environment variables are set."""
    required_vars = ["OPENROUTER_API_KEY", "GITHUB_PAT", "REPO_URL"]
    missing = [var for var in required_vars if not os.getenv(var)]
    return missing


def run_symphony_thread(idea: str, mode: str, debug_mode: bool, log_queue: queue.Queue):
    """Run AI Symphony in a separate thread."""
    # Setup logging to capture to queue
    handler = StreamlitLogHandler(log_queue)
    handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    try:
        log_queue.put("🎼 Starting AI Symphony...")
        log_queue.put(f"Mode: {mode.upper()}")
        log_queue.put(f"Idea: {idea}")
        log_queue.put("-" * 50)

        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        try:
            ignite_symphony(idea, mode=mode, debug_mode=debug_mode)
            result = "✅ Symphony completed successfully!"
        except Exception as e:
            result = f"❌ Error: {str(e)}"

        # Restore stdout/stderr and capture output
        stdout_output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        if stdout_output:
            for line in stdout_output.split("\n"):
                if line.strip():
                    log_queue.put(line)

        log_queue.put("-" * 50)
        log_queue.put(result)
        log_queue.put("__DONE__")

    except Exception as e:
        log_queue.put(f"❌ Fatal error: {str(e)}")
        log_queue.put("__DONE__")
    finally:
        root_logger.removeHandler(handler)


def main():
    """Main dashboard UI."""
    # Header
    st.title("🎼 AI Symphony")
    st.markdown("**Autonomous AI Teams That Ship Production-Ready Code**")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Keys section - allow override in UI
        st.markdown("### 🔑 API Keys")
        st.caption("Keys entered here are stored in session only, not saved to disk.")

        # Get from environment or session state
        openrouter_key = st.text_input(
            "OpenRouter API Key",
            value=os.getenv("OPENROUTER_API_KEY", ""),
            type="password",
            help="Get your key at openrouter.ai",
            key="openrouter_key",
        )

        github_pat = st.text_input(
            "GitHub PAT",
            value=os.getenv("GITHUB_PAT", ""),
            type="password",
            help="Personal Access Token with repo access",
            key="github_pat",
        )

        repo_url = st.text_input(
            "Repository URL",
            value=os.getenv("REPO_URL", ""),
            help="Full HTTPS URL to target repo",
            key="repo_url",
        )

        # Validate keys are provided
        missing_keys = []
        if not openrouter_key:
            missing_keys.append("OpenRouter API Key")
        if not github_pat:
            missing_keys.append("GitHub PAT")
        if not repo_url:
            missing_keys.append("Repository URL")

        if missing_keys:
            st.warning(f"Missing: {', '.join(missing_keys)}")
        else:
            st.success("✅ All keys configured")
            # Set in environment for this session
            os.environ["OPENROUTER_API_KEY"] = openrouter_key
            os.environ["GITHUB_PAT"] = github_pat
            os.environ["REPO_URL"] = repo_url

        st.divider()

        # Mode selection
        mode = st.selectbox(
            "Mode",
            options=["code", "business"],
            format_func=lambda x: "🎻 Code Mode" if x == "code" else "💼 Business Mode",
            help="Code mode generates PRs. Business mode validates ideas.",
        )

        # Debug mode
        debug_mode = st.checkbox(
            "Debug Mode",
            value=False,
            help="Keep workspace files after completion for inspection",
        )

        st.divider()

        # Info
        st.markdown("### 📊 Current Settings")
        repo_name = "/".join(repo_url.split("/")[-2:]).replace(".git", "") if repo_url else "N/A"
        st.text(f"Repository: {repo_name}")
        st.text(f"Mode: {mode}")
        st.text(f"Debug: {debug_mode}")

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💡 Your Idea")
        idea = st.text_area(
            "Describe what you want to build or validate",
            placeholder="Example: Create a REST API for user management with JWT authentication",
            height=120,
            label_visibility="collapsed",
        )

    with col2:
        st.header("🎯 Quick Examples")
        examples = {
            "code": [
                "Create a Streamlit dashboard for sales data",
                "Add user authentication with JWT tokens",
                "Build a REST API for todo list management",
            ],
            "business": [
                "AI-powered meal planning app for families",
                "SaaS tool for freelancer invoicing",
                "Subscription box for pet treats",
            ],
        }
        for example in examples[mode]:
            if st.button(example, key=example, use_container_width=True):
                st.session_state["idea_input"] = example
                st.rerun()

    # Run button
    st.divider()

    if "running" not in st.session_state:
        st.session_state.running = False
    if "logs" not in st.session_state:
        st.session_state.logs = []

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_button = st.button(
            "🚀 Launch Symphony",
            type="primary",
            use_container_width=True,
            disabled=not idea or st.session_state.running,
        )

    # Log display
    if run_button and idea:
        st.session_state.running = True
        st.session_state.logs = []

        log_queue = queue.Queue()

        # Start symphony in thread
        thread = threading.Thread(
            target=run_symphony_thread, args=(idea, mode, debug_mode, log_queue), daemon=True
        )
        thread.start()

        # Display logs in real-time
        log_container = st.empty()
        logs = []

        while True:
            try:
                msg = log_queue.get(timeout=0.5)
                if msg == "__DONE__":
                    break
                logs.append(msg)
                log_container.code("\n".join(logs), language="text")
            except queue.Empty:
                if not thread.is_alive():
                    break
                continue

        st.session_state.logs = logs
        st.session_state.running = False
        st.success("Symphony complete! Check your GitHub repo for the PR.")

    elif st.session_state.logs:
        st.subheader("📋 Last Run Logs")
        st.code("\n".join(st.session_state.logs), language="text")


if __name__ == "__main__":
    main()
