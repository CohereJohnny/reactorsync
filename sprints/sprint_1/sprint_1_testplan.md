# Sprint 1 Test Plan - Project Bootstrap & Infrastructure

## Overview
This test plan validates the foundational infrastructure setup for ReactorSync, ensuring all core services can be deployed and communicate properly in the development environment.

## Test Environment
- **Local Development**: Docker Compose on macOS/Linux
- **Prerequisites**: Docker Desktop, Git, Node.js 20+, Python 3.12+

## Test Categories

### 1. Repository Structure Tests
**Objective**: Verify proper project organization and documentation

#### Test 1.1: Directory Structure Validation
- [ ] Verify all required directories exist: `/frontend`, `/backend`, `/mcp-server`, `/data-generator`, `/db`, `/helm`
- [ ] Check `.gitignore` excludes appropriate files (node_modules, .env, __pycache__, dist/)
- [ ] Validate `README.md` contains setup instructions and project overview

#### Test 1.2: Documentation Completeness  
- [ ] Verify `docs/setup.md` exists with comprehensive setup guide
- [ ] Check troubleshooting section covers common issues
- [ ] Validate contributor guidelines are present

### 2. Docker Compose Tests
**Objective**: Ensure containerized environment works correctly

#### Test 2.1: Service Definition Validation
- [ ] Verify `docker-compose.yml` defines all required services
- [ ] Check service dependencies are correctly configured
- [ ] Validate volume mounts for development and persistence
- [ ] Confirm port mappings: frontend (3000), backend (8000), db (5432)

#### Test 2.2: Container Startup Tests
- [ ] Execute `docker-compose up -d` successfully
- [ ] Verify all services start without errors
- [ ] Check health checks pass for all services
- [ ] Validate service logs show successful initialization

#### Test 2.3: Service Connectivity Tests
- [ ] Test frontend container responds on port 3000
- [ ] Verify backend container responds on port 8000
- [ ] Check database accepts connections on port 5432
- [ ] Validate inter-service network communication

### 3. Frontend Foundation Tests
**Objective**: Validate NextJS setup and basic functionality

#### Test 3.1: NextJS Application Tests
- [ ] Verify NextJS development server starts successfully
- [ ] Check TypeScript compilation works without errors
- [ ] Validate ShadCN components can be imported and used
- [ ] Test TailwindCSS styling applies correctly

#### Test 3.2: Development Environment Tests
- [ ] Verify hot-reload works for component changes
- [ ] Check build process completes successfully (`yarn build`)
- [ ] Validate production build serves correctly
- [ ] Test package.json scripts execute properly

### 4. Backend Foundation Tests  
**Objective**: Ensure FastAPI setup and basic functionality

#### Test 4.1: FastAPI Application Tests
- [ ] Verify FastAPI server starts successfully
- [ ] Check auto-generated docs available at `/docs`
- [ ] Validate CORS configuration allows frontend requests
- [ ] Test basic health check endpoint responds

#### Test 4.2: Development Environment Tests
- [ ] Verify UV dependency management works
- [ ] Check requirements.txt generation from requirements.in
- [ ] Validate hot-reload works for code changes
- [ ] Test logging configuration outputs structured logs

### 5. Database Tests
**Objective**: Validate PostgreSQL and pgvector setup

#### Test 5.1: Database Connectivity Tests
- [ ] Verify PostgreSQL container starts successfully
- [ ] Check database accepts connections with configured credentials
- [ ] Validate pgvector extension is installed and available
- [ ] Test basic SQL operations work correctly

#### Test 5.2: Schema and Migration Tests
- [ ] Verify initial schema creation scripts execute
- [ ] Check SQLAlchemy connection configuration works
- [ ] Validate database connection pooling functions
- [ ] Test migration framework setup (if implemented)

### 6. Integration Tests
**Objective**: Verify end-to-end system functionality

#### Test 6.1: Full Stack Integration
- [ ] Start complete Docker Compose environment
- [ ] Verify frontend can make requests to backend
- [ ] Check backend can connect to database
- [ ] Validate all services remain stable under basic load

#### Test 6.2: Development Workflow Tests
- [ ] Test code changes trigger appropriate rebuilds
- [ ] Verify debugging capabilities work in development
- [ ] Check logs are accessible and meaningful
- [ ] Validate environment variable configuration

## Test Execution Checklist

### Pre-Test Setup
- [ ] Clean Docker environment (`docker system prune`)
- [ ] Ensure latest code is checked out on `sprint-1` branch
- [ ] Verify all required environment variables are set

### Test Execution
- [ ] Run tests in order (Repository → Docker → Frontend → Backend → Database → Integration)
- [ ] Document any failures with screenshots and logs
- [ ] Record test execution times and performance observations

### Post-Test Validation
- [ ] Verify all services can be stopped cleanly (`docker-compose down`)
- [ ] Check no orphaned containers or volumes remain
- [ ] Validate cleanup procedures work correctly

## Success Criteria
- [ ] All test categories pass with 100% success rate
- [ ] Complete Docker Compose environment starts in <2 minutes
- [ ] Frontend and backend respond to requests within 5 seconds
- [ ] Database connections establish within 10 seconds
- [ ] No critical errors in service logs during startup
- [ ] Development hot-reload works within 3 seconds of changes

## Known Issues & Workarounds
*This section will be updated with any discovered issues during testing and their workarounds.*

## Test Results Log
*This section will be populated with actual test results during sprint execution.*
