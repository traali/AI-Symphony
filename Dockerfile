# AI Symphony Docker Image
# Multi-stage build for smaller final image

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv for fast dependency installation
RUN pip install uv

# Copy requirements and install dependencies
COPY requirements.in .
RUN uv pip install --system -r requirements.in

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install git (required for GitPython)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Create non-root user for security
RUN useradd -m -u 1000 symphony && \
    chown -R symphony:symphony /app
USER symphony

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_FORMAT=json

# Expose Streamlit port
EXPOSE 8501

# Default command runs the CLI
ENTRYPOINT ["python", "-m", "src.main"]

# Alternative: Run Streamlit dashboard
# CMD ["streamlit", "run", "src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
