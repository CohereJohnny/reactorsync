# ReactorSync Validation Guide

This guide provides multiple ways to validate, test, and verify the Sprint 1 implementation.

## 🔍 Quick Validation Checklist

### 1. Project Structure Validation
```bash
# Check all required directories exist
ls -la | grep -E "(frontend|backend|mcp-server|data-generator|db|helm|docs|specs|sprints)"

# Verify essential files
ls -la | grep -E "(README.md|docker-compose.yml|.env.example)"

# Check GitHub Actions workflows
ls -la .github/workflows/
```

### 2. Docker Compose Validation
```bash
# Validate configuration syntax
docker compose config

# Check service definitions
docker compose config --services

# Verify environment variable substitution
docker compose config | grep -A 5 -B 5 "COHERE_API_KEY"
```

### 3. Frontend Validation
```bash
cd frontend

# Check package.json and dependencies
cat package.json | jq '.dependencies | keys[]' | grep -E "(next|react|typescript)"

# Verify ShadCN components are installed
ls src/components/ui/

# Test build process (without starting)
npm run build --dry-run || npx tsc --noEmit

# Check NextJS configuration
cat next.config.ts
```

### 4. Backend Validation
```bash
cd backend

# Check Python dependencies
cat requirements.txt | grep -E "(fastapi|uvicorn|sqlalchemy|cohere)"

# Verify main application structure
python -c "import ast; ast.parse(open('main.py').read()); print('✅ main.py syntax is valid')"

# Check Dockerfile
docker build --target development -t reactorsync-backend-test . && echo "✅ Backend Docker build successful"
```

### 5. Database Schema Validation
```bash
# Check database initialization script
cat db/init.sql | grep -E "(CREATE TABLE|INSERT INTO)" | wc -l

# Verify pgvector extension setup
grep -n "CREATE EXTENSION.*vector" db/init.sql

# Check sample data
grep -n "INSERT INTO reactors" db/init.sql
```

## 🚀 Full Environment Testing

### Method A: Individual Service Testing
```bash
# Test database only (on different port to avoid conflicts)
docker run -d --name test-reactorsync-db \
  -e POSTGRES_DB=reactorsync \
  -e POSTGRES_USER=reactorsync \
  -e POSTGRES_PASSWORD=reactorsync \
  -p 5433:5432 \
  -v $(pwd)/db/init.sql:/docker-entrypoint-initdb.d/init.sql \
  pgvector/pgvector:pg16

# Wait for startup and test
sleep 10
docker exec test-reactorsync-db psql -U reactorsync -d reactorsync -c "SELECT COUNT(*) FROM reactors;"

# Cleanup
docker stop test-reactorsync-db && docker rm test-reactorsync-db
```

### Method B: Full Stack Testing (when ports are available)
```bash
# Stop any conflicting services first
docker stop $(docker ps -q --filter "publish=3000" --filter "publish=5432" --filter "publish=8000") 2>/dev/null || true

# Start all services
docker compose up -d

# Wait for services to be ready
sleep 30

# Test each service
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/reactors | jq '.reactors | length'
curl -s http://localhost:3000 | grep -o "<title>[^<]*</title>"

# Check service logs
docker compose logs --tail=10 backend
docker compose logs --tail=10 frontend

# Cleanup
docker compose down
```

### Method C: Build-Only Testing (No Port Conflicts)
```bash
# Build all images without starting services
docker compose build

# Verify images were created
docker images | grep reactorsync

# Test backend container without port binding
docker run --rm reactorsync-backend python -c "
import main
from fastapi.testclient import TestClient
client = TestClient(main.app)
response = client.get('/health')
print('✅ Backend health check:', response.json())
"
```

## 🔧 Development Workflow Testing

### Hot Reload Testing
```bash
# Start services in development mode
docker compose up -d

# Test frontend hot reload
echo "// Test change" >> frontend/src/app/page.tsx
# Check if change triggers rebuild in logs
docker compose logs -f frontend

# Test backend hot reload  
echo "# Test comment" >> backend/main.py
# Check if change triggers reload in logs
docker compose logs -f backend

# Cleanup
git checkout -- frontend/src/app/page.tsx backend/main.py
docker compose down
```

### CI/CD Pipeline Testing
```bash
# Validate GitHub Actions workflow syntax
docker run --rm -v $(pwd)/.github/workflows:/workflows \
  rhymond/github-action-validate-yaml /workflows/*.yml

# Test workflow steps locally (if act is installed)
# act -n  # Dry run
```

## 📊 Code Quality Validation

### Frontend Code Quality
```bash
cd frontend

# ESLint check
npm run lint

# TypeScript check
npx tsc --noEmit

# Check for security vulnerabilities
npm audit --audit-level moderate
```

### Backend Code Quality
```bash
cd backend

# Python syntax check
python -m py_compile main.py

# Import validation
python -c "
try:
    import fastapi, uvicorn, sqlalchemy, structlog
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

# Check for security vulnerabilities
pip-audit --desc || echo "pip-audit not installed, skipping security check"
```

## 🎯 Sprint 1 Success Criteria Validation

### Infrastructure Checklist
- [ ] Repository structure follows project_structure.md
- [ ] Docker Compose defines all required services
- [ ] NextJS frontend with TypeScript and ShadCN
- [ ] FastAPI backend with structured logging
- [ ] PostgreSQL with pgvector and sample data
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Comprehensive documentation

### Integration Checklist
- [ ] Docker Compose configuration validates
- [ ] All containers build successfully
- [ ] Services can communicate (when running)
- [ ] Database schema loads correctly
- [ ] Frontend serves default page
- [ ] Backend API responds to health checks
- [ ] Hot reload works in development mode

## 🐛 Troubleshooting Common Issues

### Port Conflicts
```bash
# Find what's using ports
lsof -i :3000
lsof -i :5432
lsof -i :8000

# Kill conflicting processes
kill $(lsof -ti:3000,5432,8000)
```

### Docker Issues
```bash
# Clean Docker environment
docker system prune -f
docker volume prune -f

# Rebuild from scratch
docker compose build --no-cache
```

### Permission Issues
```bash
# Fix file permissions
chmod +x scripts/test-environment.sh

# Fix Docker socket permissions (if needed)
sudo chmod 666 /var/run/docker.sock
```

## 📈 Performance Validation

### Build Time Testing
```bash
# Time the build process
time docker compose build

# Check image sizes
docker images | grep reactorsync | awk '{print $1, $7}'
```

### Startup Time Testing
```bash
# Time service startup
time docker compose up -d --wait

# Check service readiness
docker compose ps
```

## ✅ Final Validation Report

After running the validations, you should see:

1. **Structure**: All directories and essential files present
2. **Configuration**: Docker Compose validates without errors
3. **Dependencies**: All packages correctly specified and installable
4. **Build**: All containers build successfully
5. **Integration**: Services can communicate when running
6. **Documentation**: Comprehensive setup and usage guides
7. **CI/CD**: GitHub Actions workflows validate

**Sprint 1 is complete when all these validations pass!**
