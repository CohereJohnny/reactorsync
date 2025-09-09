# Technology Stack for ReactorSync

## Frontend
- **Framework**: NextJS 14+ (SSR, routing, API routes).
- **UI Libraries**: ShadCN for components (cards, tables, badges); TanStack Table for dynamic tables.
- **Visualization**: react-plotly.js for time series charts; React-Leaflet for maps.
- **State/Data**: SWR or React Query for fetching; Socket.io-client for real-time.
- **Build/Tools**: Vite (integrated), TypeScript.
- **Package Manager**: Yarn (for dependency management, e.g., `yarn add react-plotly.js`).

## Backend
- **Framework**: FastAPI (async APIs, auto-docs).
- **AI Integration**: Cohere Python SDK; Haystack for RAG pipelines (Embed/Rerank/Command A).
- **Time Series/Anomalies**: Darts/sktime for forecasting; NumPy/SciPy for synthetics; PySAD for detection.
- **Streaming**: kafka-python for pub/sub.
- **Package Manager**: UV (for dependency management, e.g., `uv pip install fastapi cohere`).

## MCP Server
- **SDK**: north-mcp-python-sdk (from GitHub repo).
- **Exposure**: FastAPI-integrated for tool registration.
- **Package Manager**: UV (e.g., `uv pip install git+ssh://git@github.com/cohere-ai/north-mcp-python-sdk.git`).

## Database
- **Core**: Postgres with pgvector (for embeddings).

## Containers/Deployment
- **Containerization**: Docker (base images: node:20, python:3.12).
- **Orchestration**: Docker Compose (local); Helm (prod, with YAML templates).
- **Other**: MinIO (optional for files), Redis (caching if needed).

## General Tools
- **Testing**: Pytest (backend), Cypress/Jest (frontend).
- **CI/CD**: GitHub Actions (implied for repo).