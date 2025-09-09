#!/bin/bash

# ReactorSync Environment Test Script
# This script validates the complete development environment setup

set -e

echo "🚀 ReactorSync Environment Validation"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

test_fail() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

test_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "1. Testing Prerequisites..."

# Check Docker
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        test_pass "Docker is running"
    else
        test_fail "Docker daemon is not running. Please start Docker Desktop."
    fi
else
    test_fail "Docker is not installed"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    test_pass "Node.js is installed: $NODE_VERSION"
else
    test_fail "Node.js is not installed"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    test_pass "Python is installed: $PYTHON_VERSION"
else
    test_fail "Python3 is not installed"
fi

# Check UV
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    test_pass "UV is installed: $UV_VERSION"
else
    test_warn "UV is not installed globally (will be installed in containers)"
fi

echo ""
echo "2. Testing Project Structure..."

# Check essential directories
for dir in frontend backend mcp-server data-generator db helm docs; do
    if [ -d "$dir" ]; then
        test_pass "Directory exists: $dir"
    else
        test_fail "Missing directory: $dir"
    fi
done

# Check essential files
for file in README.md docker-compose.yml .env.example docs/setup.md; do
    if [ -f "$file" ]; then
        test_pass "File exists: $file"
    else
        test_fail "Missing file: $file"
    fi
done

# Check frontend structure
if [ -f "frontend/package.json" ] && [ -f "frontend/Dockerfile" ]; then
    test_pass "Frontend structure is valid"
else
    test_fail "Frontend structure is incomplete"
fi

# Check backend structure
if [ -f "backend/main.py" ] && [ -f "backend/requirements.txt" ] && [ -f "backend/Dockerfile" ]; then
    test_pass "Backend structure is valid"
else
    test_fail "Backend structure is incomplete"
fi

echo ""
echo "3. Testing Docker Configuration..."

# Validate Docker Compose
if docker compose config > /dev/null 2>&1; then
    test_pass "Docker Compose configuration is valid"
else
    test_fail "Docker Compose configuration has errors"
fi

echo ""
echo "4. Testing Environment Configuration..."

# Check .env file
if [ -f ".env" ]; then
    test_pass ".env file exists"
    
    # Check for required environment variables
    if grep -q "COHERE_API_KEY" .env; then
        test_pass "COHERE_API_KEY is configured"
    else
        test_warn "COHERE_API_KEY not found in .env"
    fi
    
    if grep -q "SERVER_SECRET" .env; then
        test_pass "SERVER_SECRET is configured"
    else
        test_warn "SERVER_SECRET not found in .env"
    fi
else
    test_warn ".env file not found (copy from .env.example)"
fi

echo ""
echo "5. Testing Docker Services (if Docker is available)..."

# Test database service
echo "Testing database service..."
if docker compose up -d db --wait; then
    test_pass "Database service started successfully"
    
    # Wait a moment for initialization
    sleep 5
    
    # Test database connection
    if docker compose exec -T db psql -U reactorsync -d reactorsync -c "SELECT 1;" > /dev/null 2>&1; then
        test_pass "Database connection successful"
        
        # Test pgvector extension
        if docker compose exec -T db psql -U reactorsync -d reactorsync -c "SELECT * FROM pg_extension WHERE extname='vector';" | grep -q vector; then
            test_pass "pgvector extension is installed"
        else
            test_warn "pgvector extension not found"
        fi
        
        # Test sample data
        REACTOR_COUNT=$(docker compose exec -T db psql -U reactorsync -d reactorsync -t -c "SELECT COUNT(*) FROM reactors;" | tr -d ' \n')
        if [ "$REACTOR_COUNT" -gt 0 ]; then
            test_pass "Sample reactor data loaded ($REACTOR_COUNT reactors)"
        else
            test_warn "No sample reactor data found"
        fi
    else
        test_fail "Database connection failed"
    fi
    
    # Cleanup database
    docker compose down db
else
    test_fail "Database service failed to start"
fi

# Test Redis service
echo "Testing Redis service..."
if docker compose up -d redis --wait; then
    test_pass "Redis service started successfully"
    
    # Test Redis connection
    if docker compose exec -T redis redis-cli ping | grep -q PONG; then
        test_pass "Redis connection successful"
    else
        test_fail "Redis connection failed"
    fi
    
    # Cleanup Redis
    docker compose down redis
else
    test_fail "Redis service failed to start"
fi

echo ""
echo "6. Testing Build Process..."

# Test frontend build (if Node.js is available)
if [ -d "frontend" ]; then
    echo "Testing frontend dependencies..."
    cd frontend
    if npm ci > /dev/null 2>&1; then
        test_pass "Frontend dependencies installed successfully"
        
        # Test build
        if npm run build > /dev/null 2>&1; then
            test_pass "Frontend builds successfully"
        else
            test_warn "Frontend build failed (may need environment setup)"
        fi
    else
        test_warn "Frontend dependency installation failed"
    fi
    cd ..
fi

# Test backend dependencies (if Python/UV is available)
if [ -d "backend" ] && command -v python3 &> /dev/null; then
    echo "Testing backend dependencies..."
    cd backend
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        if python -c "import fastapi" > /dev/null 2>&1; then
            test_pass "Backend dependencies are available"
            
            # Test basic import
            if python -c "from main import app" > /dev/null 2>&1; then
                test_pass "Backend main module imports successfully"
            else
                test_warn "Backend main module import failed"
            fi
        else
            test_warn "Backend dependencies not installed in venv"
        fi
    else
        test_warn "Backend virtual environment not found"
    fi
    cd ..
fi

echo ""
echo "7. Summary..."

echo -e "${GREEN}Environment validation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Ensure Docker Desktop is running"
echo "2. Copy .env.example to .env and configure API keys"
echo "3. Run 'docker compose up -d' to start all services"
echo "4. Visit http://localhost:3000 (frontend) and http://localhost:8000/docs (backend API)"
echo ""
echo "For detailed setup instructions, see docs/setup.md"
