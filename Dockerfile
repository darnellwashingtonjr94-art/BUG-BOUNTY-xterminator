FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy root requirements if present
COPY requirements.txt* ./

# Upgrade pip and install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy all repository files into the container
COPY . .

CMD ["python", "packages/mlx/main.py"]
