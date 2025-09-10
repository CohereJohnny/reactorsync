# ReactorSync Testing & Validation Guide

This guide describes the standardized testing and validation approach for ReactorSync development.

## 🎯 Validation Naming Convention

We use a consistent Python-based validation system that avoids bash path issues:

### Sprint-Specific Validation
- `validate_sprint1.py` - Infrastructure Foundation
- `validate_sprint2.py` - Database & Data Models  
- `validate_sprint3.py` - Synthetic Data Generation
- `validate_sprint4.py` - Basic API Foundation (future)
- `validate_sprint5.py` - Dashboard Foundation (future)

### Master Validation
- `validate.py` - Unified validation interface

### Integration Testing
- `test_integration.sh` - Full environment integration testing
- `test_quick.sh` - Quick structure and configuration testing

## 🚀 How to Use

### Validate Individual Sprints
```bash
# Validate specific sprint
python validate.py 1           # Sprint 1: Infrastructure
python validate.py 2           # Sprint 2: Database
python validate.py 3           # Sprint 3: Data generation

# Or run directly
python validate_sprint1.py     # Infrastructure foundation
python validate_sprint2.py     # Database & data models
python validate_sprint3.py     # Synthetic data generation
```

### Validate All Completed Sprints
```bash
python validate.py --all       # Validate all sprints
```

### Integration Testing
```bash
./test_integration.sh          # Full environment test (requires Docker)
./test_quick.sh               # Quick structure validation
```

### Help and Options
```bash
python validate.py             # Show usage options
```

## 📊 What Each Validation Tests

### Sprint 1 Validation
- ✅ Project structure and directories
- ✅ Docker Compose configuration
- ✅ Frontend structure (NextJS, ShadCN, TypeScript)
- ✅ Backend structure (FastAPI, dependencies)

### Sprint 2 Validation  
- ✅ Database models (SQLAlchemy)
- ✅ Migration system (Alembic)
- ✅ API database integration
- ✅ Repository pattern implementation
- ✅ Dependencies (pgvector, asyncpg, etc.)

### Sprint 3 Validation
- ✅ Data generator components (nuclear physics engine)
- ✅ Anomaly injection system
- ✅ WebSocket integration
- ✅ Docker containerization
- ✅ Streaming infrastructure

## ✅ Validation Success Criteria

Each sprint validation must show:
- **100% Component Pass Rate**: All tested components working
- **No Critical Errors**: Import and initialization successful
- **Proper Integration**: Components connect correctly
- **Docker Ready**: Containerization working

## 🔧 Troubleshooting

### Import Errors
- Python validation scripts handle path issues automatically
- Each script sets up proper import paths for its components
- Virtual environments are handled appropriately

### Docker Issues
- Use `test_integration.sh` for full Docker testing
- Individual validations test structure without requiring running containers
- Docker Compose validation tests configuration syntax

### Performance Testing
- Use integration tests for performance validation
- Individual validations focus on correctness, not performance
- Full load testing should be done with running environment

## 🎯 Best Practices

1. **Run sprint validation after each sprint completion**
2. **Use master validation (`python validate.py --all`) before major demos**
3. **Use integration tests when testing with live data/streaming**
4. **Individual validations for debugging specific components**

## 📈 Validation Evolution

As we add more sprints, we'll extend this system:
- `validate_sprint4.py` - API Foundation validation
- `validate_sprint5.py` - Dashboard Foundation validation
- Additional integration tests for complex scenarios

This standardized approach ensures reliable validation across the entire ReactorSync development lifecycle.
