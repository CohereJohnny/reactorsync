# Backend Dockerfile for ReactorSync
FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Production target
FROM base AS production

# Copy requirements and install dependencies
COPY requirements.txt .
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development target
FROM base AS development

# Copy requirements and install dependencies
COPY requirements.txt .
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy application code
COPY . .

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
