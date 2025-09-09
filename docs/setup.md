# ReactorSync Development Setup Guide

This guide provides comprehensive instructions for setting up the ReactorSync development environment locally.

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (latest version)
- **Node.js** 20+ with npm
- **Python** 3.12+
- **Git** (latest version)
- **UV** Python package manager (will be installed automatically)

### System Requirements

- **macOS**: 10.15+ (Catalina or later)
- **Windows**: Windows 10/11 with WSL2
- **Linux**: Ubuntu 20.04+ or equivalent
- **RAM**: Minimum 8GB, recommended 16GB
- **Storage**: At least 10GB free space

## Quick Start (Recommended)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd reactorsync
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your configuration
# At minimum, you need to set:
# COHERE_API_KEY=your_cohere_api_key_here
# SERVER_SECRET=your_mcp_server_secret_here
```

### 3. Start Development Environment

```bash
# Start all services with Docker Compose
docker-compose up -d

# Wait for all services to be healthy (2-3 minutes)
docker-compose ps
```

### 4. Verify Installation

Once all services are running, verify the installation:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. View Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

## Manual Development Setup

If you prefer to run services individually or need to debug specific components:

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# The frontend will be available at http://localhost:3000
```

### Backend Setup

```bash
cd backend

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Start development server
python main.py

# The backend will be available at http://localhost:8000
```

### Database Setup

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name reactorsync-db \
  -e POSTGRES_DB=reactorsync \
  -e POSTGRES_USER=reactorsync \
  -e POSTGRES_PASSWORD=reactorsync \
  -p 5432:5432 \
  -v ./db/init.sql:/docker-entrypoint-initdb.d/init.sql \
  pgvector/pgvector:pg16
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Required - Cohere API Configuration
COHERE_API_KEY=your_cohere_api_key_here

# Required - MCP Server Configuration
SERVER_SECRET=your_mcp_server_secret_here

# Optional - Database Configuration
DATABASE_URL=postgresql://reactorsync:reactorsync@localhost:5432/reactorsync

# Optional - Redis Configuration
REDIS_URL=redis://localhost:6379

# Optional - Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Optional - Development Settings
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Getting API Keys

#### Cohere API Key
1. Visit [Cohere Dashboard](https://dashboard.cohere.ai/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your `.env` file

#### MCP Server Secret
Generate a secure random string for the MCP server:

```bash
# Generate a random secret
openssl rand -hex 32
```

## Development Workflow

### Making Changes

1. **Frontend Changes**: Edit files in `frontend/src/` - hot reload is enabled
2. **Backend Changes**: Edit files in `backend/` - auto-reload is enabled in development
3. **Database Changes**: Update `db/init.sql` and recreate the database container

### Running Tests

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
source .venv/bin/activate
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Building for Production

```bash
# Build all services
docker-compose -f docker-compose.yml build

# Or build individually
cd frontend && npm run build
cd backend && docker build -t reactorsync-backend .
```

## Troubleshooting

### Common Issues

#### Port Conflicts
If ports 3000, 8000, or 5432 are already in use:

```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Stop conflicting services or change ports in docker-compose.yml
```

#### Docker Issues
```bash
# Clean up Docker resources
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Connect to database directly
docker exec -it reactorsync-db-1 psql -U reactorsync -d reactorsync

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Frontend Build Issues
```bash
cd frontend

# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run build
```

#### Backend Dependency Issues
```bash
cd backend

# Recreate virtual environment
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Performance Issues

#### Slow Docker Startup
- Increase Docker Desktop memory allocation to 8GB+
- Enable Docker Desktop's "Use gRPC FUSE for file sharing"
- Consider using Docker Desktop alternatives like OrbStack (macOS)

#### Database Performance
- Ensure PostgreSQL has sufficient memory allocated
- Check that indexes are being used with `EXPLAIN ANALYZE`
- Monitor connection pool usage

### Development Tips

#### Hot Reloading
- Frontend: Changes to React components trigger automatic reload
- Backend: FastAPI auto-reloads on file changes in development mode
- Database: Schema changes require container restart

#### Debugging
- Use browser DevTools for frontend debugging
- Backend logs are available via `docker-compose logs backend`
- Database queries can be monitored in PostgreSQL logs

#### Code Quality
```bash
# Frontend linting
cd frontend && npm run lint

# Backend formatting
cd backend && black . && isort .

# Type checking
cd backend && mypy .
```

## IDE Configuration

### VS Code / Cursor

Recommended extensions:
- Python
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- Docker
- PostgreSQL

### Settings
Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

## Next Steps

After completing the setup:

1. Explore the API documentation at http://localhost:8000/docs
2. Review the project structure in the root README.md
3. Check current sprint tasks in `sprints/sprint_1/sprint_1_tasks.md`
4. Run the test suite to ensure everything is working
5. Start developing according to the sprint plan

## Getting Help

- **Documentation**: Check the `/docs` directory for additional guides
- **API Reference**: Visit http://localhost:8000/docs when running
- **Sprint Planning**: See `sprints/v1.0.0-sprintplan.md` for development roadmap
- **Issues**: Check logs first, then refer to troubleshooting section above

## Contributing

Please follow the established sprint workflow and ensure all tests pass before committing changes. See the main README.md for contribution guidelines.
