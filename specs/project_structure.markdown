# Project Structure for ReactorSync

## GitHub Repo Layout
The repository is organized to separate specifications, code, documentation, and deployment configurations for clarity and vibe coding efficiency. Specifications reside in `/specs`, while user-facing documentation (e.g., README, guides) is in `/docs`.

- **/**: Root directory
  - `README.md`: Project overview and setup instructions.
  - `.gitignore`: Ignores build artifacts, .env, node_modules, etc.
  - `docker-compose.yml`: Defines local container orchestration.
  - `/helm/`: Helm charts for Kubernetes deployment
    - `reactorsync/`: Chart with templates/ (e.g., deployment.yaml), values.yaml.
- **/specs/**: Specification markdown files for requirements and design.
  - `prd.md`: Product requirements document.
  - `architecture.md`: System architecture with Mermaid diagrams.
  - `techstack.md`: Frameworks, libraries, and tools.
  - `frontend.md`: Frontend design, components, and styleguide.
  - `backend.md`: Backend logic and APIs.
  - `containers.md`: Container configurations.
  - `datamodel.md`: Data schema and subjects.
  - `api_spec.md`: API endpoints and MCP tools.
  - `project_structure.md`: This file.
  - `personas.md`: User personas.
  - `user_stories.md`: User stories.
  - `llm_prompts.md`: Cohere LLM prompts.
  - `telemetry.md`: Telemetry metrics and KPIs.
  - `deployment.md`: Deployment configurations.
  - `testing.md`: Testing strategies.
  - `demo_script.md`: Demo narrative.
- **/docs/**: User-facing documentation.
  - `setup.md`: Developer setup guide (e.g., Docker, IDE).
  - `user_guide.md`: How to use ReactorSync (e.g., dashboard navigation).
  - `api_docs.md`: Auto-generated OpenAPI docs (from FastAPI).
- **/frontend/**: NextJS application.
  - `pages/`: Routes (e.g., dashboard.tsx, reactor/[id].tsx).
  - `components/`: React components (e.g., ReactorCard.tsx, TelemetryChart.tsx).
  - `public/`: Static assets (e.g., images, favicon).
  - `styles/`: CSS modules or global styles.
  - `package.json`, `next.config.js`: Dependencies and config.
- **/backend/**: FastAPI application.
  - `main.py`: Entry point with app setup.
  - `routers/`: API routes (e.g., reactors.py, telemetry.py).
  - `models/`: Pydantic/SQLAlchemy models.
  - `services/`: Business logic (e.g., data generation, Cohere calls).
  - `requirements.txt`: Python dependencies.
- **/mcp-server/**: MCP server for AI agent exposure.
  - `main.py`: NorthMCP SDK setup and tool registration.
  - `requirements.txt`: SDK dependencies.
- **/data-generator/**: Synthetic data generation scripts.
  - `scripts/`: Python scripts (e.g., generate.py for telemetry).
  - `requirements.txt`: Dependencies (e.g., NumPy, Pandas).
- **/db/**: Database migrations and initialization.
  - `migrations/`: SQLAlchemy migration scripts.
  - `init.sql`: Initial schema setup (e.g., pgvector extension).

## IDE Local Filesystem
- Mirrors repo structure for consistency.
- **Additional Files**:
  - `.env`: Local secrets (e.g., COHERE_API_KEY, SERVER_SECRET).
  - `/volumes/`: Persistent data for db, streaming (mapped in Docker Compose).
- **Development Setup**: Use Cursor IDE; mount /frontend, /backend for hot-reload; /volumes for data persistence.