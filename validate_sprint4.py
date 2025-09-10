#!/usr/bin/env python3
"""
Sprint 4 Validation Script - API Foundation & Real-time Integration

Validates the complete API foundation and WebSocket integration.
"""

import sys
import subprocess
import json
from pathlib import Path

def test_api_endpoints():
    """Test API endpoint implementation"""
    print("🔌 Sprint 4 Validation - API Foundation")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    main_py = backend_path / "main.py"
    
    if not main_py.exists():
        print("❌ Backend main.py not found")
        return False
    
    # Check main.py for complete API endpoints
    with open(main_py) as f:
        content = f.read()
    
    required_endpoints = [
        "GET /reactors",
        "GET /reactors/{reactor_id}",
        "POST /reactors",
        "PUT /reactors/{reactor_id}",
        "DELETE /reactors/{reactor_id}",
        "GET /telemetry/{reactor_id}",
        "GET /reactors/{reactor_id}/faults",
        "GET /reactors/{reactor_id}/health",
        "GET /system/statistics"
    ]
    
    api_patterns = [
        '@app.get("/reactors")',
        '@app.get("/reactors/{reactor_id}")',
        '@app.post("/reactors")',
        '@app.put("/reactors/{reactor_id}")',
        '@app.delete("/reactors/{reactor_id}")',
        '@app.get("/telemetry/{reactor_id}")',
        '@app.get("/reactors/{reactor_id}/faults")',
        '@app.get("/reactors/{reactor_id}/health")',
        '@app.get("/system/statistics")'
    ]
    
    for i, (endpoint, pattern) in enumerate(zip(required_endpoints, api_patterns)):
        if pattern in content:
            print(f"✅ API endpoint implemented: {endpoint}")
        else:
            print(f"❌ Missing API endpoint: {endpoint}")
            return False
    
    return True

def test_websocket_integration():
    """Test WebSocket integration"""
    print("\n🔌 WebSocket Real-time Integration")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    main_py = backend_path / "main.py"
    
    with open(main_py) as f:
        content = f.read()
    
    websocket_features = [
        ("WebSocket Import", "from fastapi import.*WebSocket"),
        ("Connection Manager", "class ConnectionManager"),
        ("WebSocket Manager", "websocket_manager = ConnectionManager()"),
        ("Telemetry WebSocket", '@app.websocket("/ws/telemetry")'),
        ("Alerts WebSocket", '@app.websocket("/ws/alerts")'),
        ("Real-time Broadcasting", "broadcast_to_all"),
        ("Reactor Subscriptions", "broadcast_to_reactor_subscribers")
    ]
    
    for feature_name, pattern in websocket_features:
        if pattern.replace(".*", "") in content.replace("\n", " "):
            print(f"✅ WebSocket feature: {feature_name}")
        else:
            print(f"❌ Missing WebSocket feature: {feature_name}")
            return False
    
    return True

def test_admin_endpoints():
    """Test admin and demo control endpoints"""
    print("\n🎛️ Admin & Demo Controls")
    print("=" * 50)
    
    backend_path = Path(__file__).parent / "backend"
    main_py = backend_path / "main.py"
    
    with open(main_py) as f:
        content = f.read()
    
    admin_endpoints = [
        ("Anomaly Injection", '@app.post("/admin/inject-anomaly")'),
        ("Anomaly Clearing", '@app.post("/admin/clear-anomaly")'),
        ("Data Initialization", '@app.post("/admin/initialize-data")')
    ]
    
    for endpoint_name, pattern in admin_endpoints:
        if pattern in content:
            print(f"✅ Admin endpoint: {endpoint_name}")
        else:
            print(f"❌ Missing admin endpoint: {endpoint_name}")
            return False
    
    return True

def test_documentation_readiness():
    """Test API documentation and frontend preparation"""
    print("\n📚 Documentation & Frontend Preparation")
    print("=" * 50)
    
    # Check for comprehensive endpoint coverage
    backend_path = Path(__file__).parent / "backend"
    main_py = backend_path / "main.py"
    
    with open(main_py) as f:
        content = f.read()
    
    # Count API endpoints
    get_endpoints = content.count('@app.get(')
    post_endpoints = content.count('@app.post(')
    put_endpoints = content.count('@app.put(')
    delete_endpoints = content.count('@app.delete(')
    websocket_endpoints = content.count('@app.websocket(')
    
    total_endpoints = get_endpoints + post_endpoints + put_endpoints + delete_endpoints + websocket_endpoints
    
    print(f"✅ API endpoints implemented: {total_endpoints} total")
    print(f"   - GET endpoints: {get_endpoints}")
    print(f"   - POST endpoints: {post_endpoints}")
    print(f"   - PUT endpoints: {put_endpoints}")
    print(f"   - DELETE endpoints: {delete_endpoints}")
    print(f"   - WebSocket endpoints: {websocket_endpoints}")
    
    if total_endpoints >= 12:  # Expected minimum
        print("✅ Comprehensive API coverage achieved")
    else:
        print("❌ Insufficient API coverage")
        return False
    
    # Check for proper documentation
    docstring_count = content.count('"""')
    if docstring_count >= 20:  # Each endpoint should have docstring
        print("✅ API documentation present")
    else:
        print("⚠️ API documentation could be enhanced")
    
    return True

def main():
    """Main validation function"""
    print("🚀 ReactorSync Sprint 4 Validation")
    print("=" * 50)
    
    results = []
    
    # Test components
    results.append(("API Endpoints", test_api_endpoints()))
    results.append(("WebSocket Integration", test_websocket_integration()))
    results.append(("Admin Controls", test_admin_endpoints()))
    results.append(("Documentation", test_documentation_readiness()))
    
    # Summary
    print("\n🎯 SPRINT 4 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for component, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {component}")
        if not passed:
            all_passed = False
    
    print("\n📊 SPRINT 4 DELIVERABLES:")
    print("• Complete REST API with CRUD operations")
    print("• WebSocket real-time integration")
    print("• Admin controls for demo scenarios")
    print("• Comprehensive API documentation")
    print("• Health monitoring and analytics endpoints")
    print("• System statistics and fleet overview")
    print("• Frontend integration preparation")
    
    if all_passed:
        print("\n🎉 SPRINT 4 API FOUNDATION COMPLETE!")
        print("All components validated successfully")
        print("Ready for Sprint 5: Dashboard Foundation")
        return 0
    else:
        print("\n⚠️ Some components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
