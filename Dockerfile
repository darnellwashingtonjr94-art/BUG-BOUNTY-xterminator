# ==============================================================================
# BUG-Bounty-Xterminator Python Microservice Dockerfile
# ==============================================================================
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install common requirements
COPY packages/llmx/ requirements.txt* ./ 
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install core asynchronous event bus and utility packages
RUN pip install --no-cache-dir redis httpx asyncpg scikit-learn numpy

# Copy application source code
COPY . .

# Default command (overridden in docker-compose.yml per service)
CMD ["python3", "main.py"]
