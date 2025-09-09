# Backend Specifications for ReactorSync

## Overview
The backend handles API logic, Cohere integrations, data processing, and streaming orchestration using FastAPI. It serves the frontend and MCP server, focusing on synthetic data management for demo realism.

## Key Modules
- **API Endpoints**: RESTful (e.g., /reactors, /telemetry/{id}, /trigger-anomaly); WebSockets for real-time (/ws/telemetry).
- **AI Pipelines**: Haystack for RAG: Embed reactor docs/logs, Rerank faults, Command A for diagnostics/reports.
- **Data Processing**: Synthetic generation (NumPy scripts); anomaly injection (perturbations); forecasting (Darts).
- **Streaming**: Kafka producers/consumers for telemetry feeds.
- **Persistence**: SQLAlchemy for Postgres interactions (e.g., reactor metadata).

## Package Management
- **UV**: Manage dependencies with `uv pip install` (e.g., `uv pip install fastapi cohere sqlalchemy`); lockfile via `uv pip compile requirements.in > requirements.txt`.
- **Setup**: Initialize virtual env with `uv venv`; install deps with `uv pip sync requirements.txt`.
- **MCP SDK**: Install north-mcp-python-sdk via `uv pip install git+ssh://git@github.com/cohere-ai/north-mcp-python-sdk.git`.

## Best Practices
- **Error Handling**: Custom exceptions; logging with structlog.
- **Performance**: Async endpoints; caching with Redis if added.
- **Testing**: Pytest for unit/integration; mock Cohere calls (e.g., `pytest --cov`).
- **Dependency Management**: Use `uv pip check` for conflicts; update lockfile with `uv pip compile`.