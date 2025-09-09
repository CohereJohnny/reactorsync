# Sprint 2 Test Plan - Database & Data Models

## Overview
This test plan validates the database integration and data model implementation for ReactorSync, ensuring proper SQLAlchemy integration, CRUD operations, and API-database connectivity.

## Test Environment
- **Local Development**: Docker Compose with PostgreSQL + pgvector
- **Test Database**: Separate test instance with fixtures
- **Prerequisites**: Sprint 1 infrastructure, working Docker environment

## Test Categories

### 1. Database Model Tests
**Objective**: Verify SQLAlchemy models work correctly with PostgreSQL

#### Test 1.1: Model Creation and Validation
- [ ] Verify all models (Reactor, Telemetry, Fault, KnowledgeBase) can be created
- [ ] Check model field validation and constraints
- [ ] Test model relationships and foreign keys
- [ ] Validate model serialization/deserialization

#### Test 1.2: Database Schema Migration
- [ ] Verify Alembic migrations run successfully
- [ ] Check schema matches SQLAlchemy model definitions
- [ ] Test migration rollback functionality
- [ ] Validate index creation and constraints

#### Test 1.3: pgvector Integration
- [ ] Verify pgvector extension works with SQLAlchemy
- [ ] Test vector field creation and storage
- [ ] Check vector similarity search operations
- [ ] Validate embedding storage and retrieval

### 2. CRUD Operations Tests
**Objective**: Ensure all database operations work correctly

#### Test 2.1: Reactor Operations
- [ ] Test reactor creation with all fields
- [ ] Verify reactor retrieval by ID and filters
- [ ] Check reactor update operations
- [ ] Test reactor deletion and cascade effects
- [ ] Validate reactor list with pagination and sorting

#### Test 2.2: Telemetry Operations
- [ ] Test telemetry data insertion
- [ ] Verify time-series data retrieval
- [ ] Check telemetry filtering by date ranges
- [ ] Test bulk telemetry operations
- [ ] Validate telemetry data aggregation

#### Test 2.3: Fault Operations
- [ ] Test fault creation and logging
- [ ] Verify fault retrieval and filtering
- [ ] Check fault status updates
- [ ] Test fault-reactor relationships
- [ ] Validate fault history tracking

### 3. API-Database Integration Tests
**Objective**: Verify backend APIs work with real database

#### Test 3.1: Reactor API Endpoints
- [ ] Test GET /reactors returns database data
- [ ] Verify POST /reactors creates database entries
- [ ] Check PUT /reactors/{id} updates database
- [ ] Test DELETE /reactors/{id} removes from database
- [ ] Validate API error handling for database errors

#### Test 3.2: Telemetry API Endpoints
- [ ] Test GET /telemetry/{reactor_id} returns real data
- [ ] Verify telemetry filtering and pagination
- [ ] Check time range queries work correctly
- [ ] Test telemetry data aggregation endpoints
- [ ] Validate API response formats match models

#### Test 3.3: Health and Status APIs
- [ ] Test /health endpoint includes database status
- [ ] Verify database connection health checks
- [ ] Check API responses during database downtime
- [ ] Test database reconnection handling
- [ ] Validate error responses for database issues

### 4. Database Performance Tests
**Objective**: Ensure database operations perform adequately

#### Test 4.1: Query Performance
- [ ] Test reactor list queries with large datasets (1000+ reactors)
- [ ] Verify telemetry queries with time ranges perform well
- [ ] Check complex filter queries meet performance targets
- [ ] Test database index effectiveness
- [ ] Validate connection pooling behavior

#### Test 4.2: Concurrent Operations
- [ ] Test multiple simultaneous database connections
- [ ] Verify concurrent read/write operations
- [ ] Check database locking behavior
- [ ] Test connection pool limits
- [ ] Validate transaction isolation

### 5. Data Integrity Tests
**Objective**: Ensure data consistency and validation

#### Test 5.1: Data Validation
- [ ] Test model field validation (required fields, formats)
- [ ] Verify database constraints are enforced
- [ ] Check foreign key relationships work correctly
- [ ] Test data type validation and conversion
- [ ] Validate business logic constraints

#### Test 5.2: Transaction Handling
- [ ] Test database transaction rollback on errors
- [ ] Verify atomic operations work correctly
- [ ] Check concurrent transaction handling
- [ ] Test deadlock detection and recovery
- [ ] Validate data consistency after failures

### 6. Sample Data and Fixtures Tests
**Objective**: Verify data loading and test fixtures work

#### Test 6.1: Sample Data Loading
- [ ] Test automated sample data loading scripts
- [ ] Verify sample data matches expected schema
- [ ] Check data loading is idempotent
- [ ] Test data loading in different environments
- [ ] Validate sample data relationships

#### Test 6.2: Test Fixtures
- [ ] Test database fixture creation for tests
- [ ] Verify fixture cleanup after tests
- [ ] Check fixture data isolation between tests
- [ ] Test fixture performance and reliability
- [ ] Validate fixture data consistency

## Test Execution Checklist

### Pre-Test Setup
- [ ] Clean database environment (`docker compose down -v`)
- [ ] Ensure latest code is checked out on `sprint-2` branch
- [ ] Install any new Python dependencies
- [ ] Run database migrations

### Test Execution
- [ ] Run model tests: `pytest tests/models/`
- [ ] Run CRUD tests: `pytest tests/crud/`
- [ ] Run API integration tests: `pytest tests/api/`
- [ ] Run performance tests: `pytest tests/performance/`
- [ ] Document any failures with logs and screenshots

### Post-Test Validation
- [ ] Verify test database cleanup
- [ ] Check no test data pollution in development database
- [ ] Validate all tests pass in CI/CD pipeline
- [ ] Review test coverage reports

## Success Criteria
- [ ] All model tests pass with 100% success rate
- [ ] CRUD operations work reliably with proper error handling
- [ ] API endpoints return real database data instead of static responses
- [ ] Database queries perform within acceptable limits (<500ms for typical queries)
- [ ] No data integrity issues or constraint violations
- [ ] Sample data loads correctly and consistently
- [ ] Test coverage >80% for new database code

## Performance Targets
- **Reactor List API**: <200ms for 100 reactors
- **Telemetry Query**: <500ms for 1 week of data per reactor
- **Database Connection**: <100ms connection establishment
- **Concurrent Users**: Support 10+ simultaneous database connections

## Known Issues & Workarounds
*This section will be updated with any discovered issues during testing and their workarounds.*

## Test Results Log
*This section will be populated with actual test results during sprint execution.*
