# Architecture Overview for ReactorSync

## High-Level Architecture
ReactorSync follows a microservices-inspired, containerized architecture with clear separation: Frontend (NextJS for UI), Backend (FastAPI for logic/APIs), MCP Server (for AI agent exposure), Data Generation/Streaming (for synthetic telemetry), and Database (Postgres for persistence). All components communicate via REST/WebSockets; Cohere APIs are proxied through the backend. The system is designed for local Docker Compose runs and Helm-based Kubernetes deployment.

### Component Diagram
```mermaid
graph TD
    A[User/AI Agent] -->|HTTP/WS| B[Frontend Container: NextJS]
    A -->|MCP Protocol| C[MCP Server Container: NorthMCP SDK]
    B -->|REST API| D[Backend Container: FastAPI]
    C -->|Internal Calls| D
    D -->|API Calls| E[Cohere Services: Command A, Embed, Rerank]
    D -->|SQL| F[DB Container: Postgres/pgvector]
    D -->|Pub/Sub| G[Streaming Container: Kafka]
    H[Data Generator Container: Python Scripts] -->|Produces Data| G
```

### Data Flow Diagram
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant MCP
    participant Cohere
    participant DB
    participant Streaming

    User->>Frontend: View Dashboard
    Frontend->>Backend: Fetch Reactors/Telemetry
    Backend->>DB: Query Data
    Backend->>Streaming: Subscribe to Updates
    Backend->>Frontend: Return Data with Status
    User->>Frontend: Trigger Anomaly (Admin)
    Frontend->>Backend: POST /trigger-anomaly
    Backend->>Streaming: Inject Perturbation
    Streaming->>Backend: Updated Telemetry
    Backend->>Cohere: Embed/Rerank for Diagnostics
    Backend->>Frontend: Alert/Update UI
    alt AI Agent Path
        User->>MCP: Query via Agent
        MCP->>Backend: Tool Call (e.g., get_telemetry)
        Backend->>Cohere: Generate Response
        MCP->>User: Agent Output
    end
```

## Key Architectural Principles
- **Modularity**: Each container handles one concern; easy to scale (e.g., multiple backend pods).
- **Data Handling**: Synthetic telemetry streamed via Kafka for real-time; persisted in Postgres for queries.
- **AI Layer**: Backend orchestrates Cohere calls; MCP exposes as tools (e.g., "diagnose_fault").
- **Scalability**: Local: Docker Compose. Prod: Helm with HPA, StatefulSets for DB/Streaming.
- **Resilience**: Retry logic in backend for Cohere; synthetic data ensures demo reliability.