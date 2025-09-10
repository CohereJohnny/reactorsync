#!/usr/bin/env python3
"""
Sprint 1 Validation Script - Infrastructure Foundation

Validates the core infrastructure setup from Sprint 1.
"""

import sys
from pathlib import Path
import subprocess

def test_project_structure():
    """Test project structure and files"""
    print("🏗️ Sprint 1 Validation - Infrastructure Foundation")
    print("=" * 50)
    
    required_dirs = ["frontend", "backend", "mcp-server", "data-generator", "db", "helm", "docs"]
    required_files = ["README.md", "docker-compose.yml", ".env.example", "docs/setup.md"]
    
    project_root = Path(__file__).parent
    
    # Check directories
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ Directory exists: {dir_name}")
        else:
            print(f"❌ Directory missing: {dir_name}")
            return False
    
    # Check files
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ File exists: {file_name}")
        else:
            print(f"❌ File missing: {file_name}")
            return False
    
    return True

def test_docker_compose():
    """Test Docker Compose configuration"""
    print("\n🐳 Docker Compose Validation")
    print("=" * 50)
    
    try:
        result = subprocess.run(["docker", "compose", "config"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Docker Compose configuration is valid")
            return True
        else:
            print(f"❌ Docker Compose validation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Docker Compose test error: {e}")
        return False

def test_frontend_structure():
    """Test frontend structure"""
    print("\n⚛️ Frontend Structure")
    print("=" * 50)
    
    frontend_path = Path(__file__).parent / "frontend"
    
    required_files = ["package.json", "next.config.ts", "Dockerfile"]
    for file_name in required_files:
        file_path = frontend_path / file_name
        if file_path.exists():
            print(f"✅ Frontend file exists: {file_name}")
        else:
            print(f"❌ Frontend file missing: {file_name}")
            return False
    
    # Check ShadCN components
    ui_components = frontend_path / "src" / "components" / "ui"
    if ui_components.exists():
        component_count = len(list(ui_components.glob("*.tsx")))
        print(f"✅ ShadCN UI components installed: {component_count} components")
    else:
        print("❌ ShadCN UI components not found")
        return False
    
    return True

def test_backend_structure():
    """Test backend structure"""
    print("\n🔧 Backend Structure")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    
    required_files = ["main.py", "requirements.txt", "Dockerfile"]
    for file_name in required_files:
        file_path = backend_path / file_name
        if file_path.exists():
            print(f"✅ Backend file exists: {file_name}")
        else:
            print(f"❌ Backend file missing: {file_name}")
            return False
    
    # Check models directory (Sprint 2)
    models_dir = backend_path / "models"
    if models_dir.exists():
        model_count = len(list(models_dir.glob("*.py"))) - 1  # Exclude __init__.py
        print(f"✅ Database models implemented: {model_count} models")
    else:
        print("⚠️ Database models not yet implemented (Sprint 2)")
    
    return True

def main():
    """Main validation function"""
    print("🚀 ReactorSync Sprint 1 Validation")
    print("=" * 50)
    
    results = []
    
    # Test components
    results.append(("Project Structure", test_project_structure()))
    results.append(("Docker Compose", test_docker_compose()))
    results.append(("Frontend Structure", test_frontend_structure()))
    results.append(("Backend Structure", test_backend_structure()))
    
    # Summary
    print("\n🎯 SPRINT 1 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for component, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {component}")
        if not passed:
            all_passed = False
    
    print("\n📊 SPRINT 1 DELIVERABLES:")
    print("• Complete repository structure")
    print("• Docker Compose orchestration")
    print("• NextJS frontend with TypeScript & ShadCN")
    print("• FastAPI backend with structured logging")
    print("• PostgreSQL database with pgvector")
    print("• CI/CD pipeline with GitHub Actions")
    print("• Comprehensive documentation")
    
    if all_passed:
        print("\n🎉 SPRINT 1 INFRASTRUCTURE FOUNDATION COMPLETE!")
        print("All components validated successfully")
        print("Ready for Sprint 2: Database & Data Models")
        return 0
    else:
        print("\n⚠️ Some components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
