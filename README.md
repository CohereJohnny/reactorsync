# ReactorSync

A Generative AI-enabled Nuclear Reactor Management Application designed to demonstrate collaborative excellence in managing CANDU reactors and Small Modular Reactors (SMRs), aligned with Conexus Nuclear's mission.

## Overview

ReactorSync is a demo-focused platform that simulates reactor oversight, predictive maintenance, and SMR deployment planning using Cohere's foundation models. The application emphasizes a containerized architecture for local development and scalable production deployment.

### Key Features

- **Multi-View Dashboard**: Card, table, and map views of reactor status with real-time updates
- **AI Diagnostics**: Cohere-powered diagnostic reports and recommendations
- **Anomaly Simulation**: Demo-focused fault injection and resolution capabilities
- **MCP Integration**: Exposes APIs as tools for AI agents via Model Context Protocol
- **SMR Planning**: Deployment simulation and regulatory compliance tools

## Architecture

ReactorSync follows a microservices architecture with clear separation:

- **Frontend**: NextJS 14+ with ShadCN components, React-Leaflet maps, Plotly charts
- **Backend**: FastAPI with Cohere integration and Haystack for RAG pipelines
- **MCP Server**: Exposes APIs as tools using north-mcp-python-sdk
- **Database**: PostgreSQL with pgvector for embeddings
- **Streaming**: Kafka for real-time telemetry data
- **Data Generator**: Synthetic nuclear telemetry generation

## Quick Start

### Prerequisites

- Docker Desktop
- Node.js 20+
- Python 3.12+
- Git

### Development Setup

1. **Clone and setup the repository:**
   ```bash
   git clone <repository-url>
   cd reactorsync
   ```

2. **Environment Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your Cohere API key and other configurations
   ```

3. **Start the development environment:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Development Setup

For detailed manual setup instructions, see [docs/setup.md](docs/setup.md).

## Technology Stack

- **Frontend**: NextJS, TypeScript, ShadCN, TailwindCSS, React-Plotly, React-Leaflet
- **Backend**: FastAPI, Cohere SDK, Haystack, SQLAlchemy, UV package manager
- **Database**: PostgreSQL with pgvector extension
- **Deployment**: Docker Compose (local), Helm charts (production)
- **AI/ML**: Cohere Command A, Embed, Rerank models

## Project Structure

```
reactorsync/
├── frontend/           # NextJS application
├── backend/            # FastAPI application  
├── mcp-server/         # MCP server for AI agents
├── data-generator/     # Synthetic data generation
├── db/                 # Database migrations and setup
├── helm/               # Kubernetes deployment charts
├── docs/               # Documentation
├── specs/              # Technical specifications
└── sprints/            # Sprint planning and tracking
```

## Development Workflow

This project follows a structured sprint methodology. See [sprints/v1.0.0-sprintplan.md](sprints/v1.0.0-sprintplan.md) for the complete development roadmap.

Current sprint progress can be tracked in `sprints/sprint_x/sprint_x_tasks.md`.

## Demo Scenarios

ReactorSync is designed for compelling demonstrations:

1. **Healthy State**: View dashboard with all reactors operating normally
2. **Anomaly Injection**: Trigger faults to simulate emergency scenarios  
3. **AI Diagnosis**: Use AI-powered diagnostics to identify and resolve issues
4. **SMR Planning**: Demonstrate deployment planning and site selection

## Contributing

Please read our contributing guidelines and follow the established sprint workflow. All development should be done on feature branches with proper testing and documentation.

## License

[License information to be added]

## Support

For setup issues or questions, please refer to:
- [Setup Guide](docs/setup.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Sprint Planning](sprints/v1.0.0-sprintplan.md)

---

**Note**: This is a demonstration application using synthetic data only. It is not intended for production use with real nuclear facilities.
