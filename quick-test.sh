#!/bin/bash

# ReactorSync Quick Validation Script
# This script provides a fast way to validate the Sprint 1 setup

echo "🚀 ReactorSync Quick Validation"
echo "==============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✅ $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo "1. Project Structure..."
[ -d "frontend" ] && pass "Frontend directory exists" || fail "Frontend directory missing"
[ -d "backend" ] && pass "Backend directory exists" || fail "Backend directory missing"
[ -f "docker-compose.yml" ] && pass "Docker Compose file exists" || fail "Docker Compose file missing"
[ -f "README.md" ] && pass "README exists" || fail "README missing"

echo -e "\n2. Configuration Files..."
[ -f ".env.example" ] && pass "Environment template exists" || fail "Environment template missing"
[ -f "docs/setup.md" ] && pass "Setup documentation exists" || fail "Setup documentation missing"
[ -d ".github/workflows" ] && pass "CI/CD workflows exist" || fail "CI/CD workflows missing"

echo -e "\n3. Docker Compose Validation..."
if docker compose config > /dev/null 2>&1; then
    pass "Docker Compose configuration is valid"
else
    fail "Docker Compose configuration has errors"
fi

echo -e "\n4. Frontend Validation..."
if [ -f "frontend/package.json" ] && [ -f "frontend/next.config.ts" ]; then
    pass "Frontend structure is correct"
else
    fail "Frontend structure is incomplete"
fi

if [ -d "frontend/src/components/ui" ]; then
    UI_COMPONENTS=$(ls frontend/src/components/ui/ | wc -l)
    pass "ShadCN UI components installed ($UI_COMPONENTS components)"
else
    warn "ShadCN UI components not found"
fi

echo -e "\n5. Backend Validation..."
if [ -f "backend/main.py" ] && [ -f "backend/requirements.txt" ]; then
    pass "Backend structure is correct"
else
    fail "Backend structure is incomplete"
fi

if python -c "import ast; ast.parse(open('backend/main.py').read())" 2>/dev/null; then
    pass "Backend Python syntax is valid"
else
    fail "Backend Python syntax errors"
fi

echo -e "\n6. Database Schema..."
TABLES=$(grep -c "CREATE TABLE" db/init.sql 2>/dev/null || echo 0)
REACTORS=$(grep -c "INSERT INTO reactors" db/init.sql 2>/dev/null || echo 0)
if [ "$TABLES" -gt 0 ] && [ "$REACTORS" -gt 0 ]; then
    pass "Database schema with $TABLES tables and sample data ready"
else
    fail "Database schema incomplete"
fi

echo -e "\n7. Docker Build Test..."
echo "   Testing frontend build..."
if docker build -q --target development -t reactorsync-frontend-test ./frontend > /dev/null 2>&1; then
    pass "Frontend Docker build successful"
else
    fail "Frontend Docker build failed"
fi

echo "   Testing backend build..."
if docker build -q --target development -t reactorsync-backend-test ./backend > /dev/null 2>&1; then
    pass "Backend Docker build successful"
else
    fail "Backend Docker build failed"
fi

echo -e "\n🎯 FULL INTEGRATION TEST (Optional)"
echo "To test the complete environment when ports are available:"
echo "  1. Stop any conflicting services: docker stop \$(docker ps -q --filter 'publish=3000' --filter 'publish=5432' --filter 'publish=8000') 2>/dev/null"
echo "  2. Start all services: docker compose up -d"
echo "  3. Wait 30 seconds for startup: sleep 30"
echo "  4. Test endpoints:"
echo "     - curl http://localhost:8000/health"
echo "     - curl http://localhost:8000/reactors"
echo "     - curl http://localhost:3000"
echo "  5. Clean up: docker compose down"

echo -e "\n✅ Quick validation complete!"
echo "For comprehensive testing, see VALIDATION_GUIDE.md"
