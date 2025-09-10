# Data Generator Dockerfile for ReactorSync
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd --create-home --shell /bin/bash generator
RUN chown -R generator:generator /app
USER generator

# Set Python path
ENV PYTHONPATH=/app/src

CMD ["python", "src/data_generator.py"]
