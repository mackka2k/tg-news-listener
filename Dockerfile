# --- 1. Build Stage ---
FROM python:3.11-slim-bookworm AS builder

# Prevent python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies (for compilation if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install depenencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# --- 2. Final/Runtime Stage ---
FROM python:3.11-slim-bookworm

# Metadata
LABEL maintainer="Telegram News Bot Team"
LABEL version="2.0.0"
LABEL description="Production-ready Telegram News Bot"

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create directories and set permissions
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Environment variables with defaults
# (Should be overridden at runtime)
ENV ENVIRONMENT="production"
ENV LOG_LEVEL="INFO"
ENV DATABASE_PATH="/app/data/bot.db"
ENV LOG_FILE="/app/logs/bot.log"
ENV MAX_POSTS_PER_DAY="5"
ENV KEYWORDS="_DISABLED_"
ENV POST_MODE="direct"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose metrics/health port
EXPOSE 8080

# Run the bot
CMD ["python", "-m", "bot.main"]
