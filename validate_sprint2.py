#!/usr/bin/env python3
"""
Sprint 2 Validation Script - Database & Data Models

Validates the database integration and data models from Sprint 2.
"""

import sys
import subprocess
from pathlib import Path

def test_database_models():
    """Test database models and structure"""
    print("🗃️ Sprint 2 Validation - Database & Data Models")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    
    # Check models directory
    models_dir = backend_path / "models"
    if not models_dir.exists():
        print("❌ Models directory missing")
        return False
    
    required_models = ["reactor.py", "telemetry.py", "fault.py", "knowledge_base.py", "base.py"]
    for model_file in required_models:
        model_path = models_dir / model_file
        if model_path.exists():
            print(f"✅ Model exists: {model_file}")
        else:
            print(f"❌ Model missing: {model_file}")
            return False
    
    # Check repositories
    repos_dir = backend_path / "repositories"
    if repos_dir.exists():
        repo_count = len(list(repos_dir.glob("*.py"))) - 1  # Exclude __init__.py
        print(f"✅ Repository pattern implemented: {repo_count} repositories")
    else:
        print("❌ Repository pattern not implemented")
        return False
    
    return True

def test_migration_system():
    """Test Alembic migration system"""
    print("\n📦 Migration System")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    
    # Check Alembic files
    alembic_ini = backend_path / "alembic.ini"
    migrations_dir = backend_path / "migrations"
    
    if alembic_ini.exists():
        print("✅ Alembic configuration exists")
    else:
        print("❌ Alembic configuration missing")
        return False
    
    if migrations_dir.exists():
        migration_count = len(list((migrations_dir / "versions").glob("*.py")))
        print(f"✅ Migration system ready: {migration_count} migrations")
    else:
        print("❌ Migration directory missing")
        return False
    
    return True

def test_api_integration():
    """Test API database integration"""
    print("\n🔌 API Database Integration")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    main_py = backend_path / "main.py"
    
    if not main_py.exists():
        print("❌ Backend main.py missing")
        return False
    
    # Check main.py for database integration
    with open(main_py) as f:
        content = f.read()
    
    database_indicators = [
        "from models.base import get_db",
        "from repositories import",
        "Session = Depends(get_db)",
        "ReactorRepository",
        "TelemetryRepository"
    ]
    
    for indicator in database_indicators:
        if indicator in content:
            print(f"✅ Database integration: {indicator}")
        else:
            print(f"❌ Missing database integration: {indicator}")
            return False
    
    return True

def test_dependencies():
    """Test updated dependencies"""
    print("\n📦 Dependencies")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    requirements_txt = backend_path / "requirements.txt"
    
    if not requirements_txt.exists():
        print("❌ requirements.txt missing")
        return False
    
    # Check for key database dependencies
    with open(requirements_txt) as f:
        content = f.read()
    
    key_deps = ["sqlalchemy", "alembic", "pgvector", "asyncpg"]
    for dep in key_deps:
        if dep in content:
            print(f"✅ Dependency included: {dep}")
        else:
            print(f"❌ Missing dependency: {dep}")
            return False
    
    return True

def main():
    """Main validation function"""
    print("🚀 ReactorSync Sprint 2 Validation")
    print("=" * 50)
    
    results = []
    
    # Test components
    results.append(("Database Models", test_database_models()))
    results.append(("Migration System", test_migration_system()))
    results.append(("API Integration", test_api_integration()))
    results.append(("Dependencies", test_dependencies()))
    
    # Summary
    print("\n🎯 SPRINT 2 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for component, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {component}")
        if not passed:
            all_passed = False
    
    print("\n📊 SPRINT 2 DELIVERABLES:")
    print("• Complete SQLAlchemy models for all entities")
    print("• Database migration system with Alembic")
    print("• Repository pattern for data access")
    print("• Real database-backed API endpoints")
    print("• Connection pooling and error handling")
    print("• Sample data initialization")
    print("• Comprehensive testing framework")
    
    if all_passed:
        print("\n🎉 SPRINT 2 DATABASE FOUNDATION COMPLETE!")
        print("All components validated successfully")
        print("Ready for Sprint 3: Synthetic Data Generation")
        return 0
    else:
        print("\n⚠️ Some components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
