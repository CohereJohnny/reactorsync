#!/usr/bin/env python3
"""
ReactorSync Master Validation Script

Provides a unified interface for validating all sprints and components.
"""

import sys
import argparse
from pathlib import Path

def run_sprint_validation(sprint_number):
    """Run validation for a specific sprint"""
    script_path = Path(__file__).parent / f"validate_sprint{sprint_number}.py"
    
    if not script_path.exists():
        print(f"❌ Validation script for Sprint {sprint_number} not found")
        return False
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running Sprint {sprint_number} validation: {e}")
        return False

def validate_all_sprints():
    """Validate all completed sprints"""
    print("🚀 ReactorSync Complete Validation")
    print("=" * 50)
    
    sprints = [1, 2, 3]  # Add more as we complete them
    results = []
    
    for sprint in sprints:
        print(f"\n🎯 Validating Sprint {sprint}...")
        success = run_sprint_validation(sprint)
        results.append((sprint, success))
    
    # Summary
    print("\n📊 OVERALL VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for sprint, passed in results:
        status = "✅ COMPLETE" if passed else "❌ ISSUES"
        print(f"{status} Sprint {sprint}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL SPRINTS VALIDATED!")
        print("ReactorSync development on track")
        return 0
    else:
        print("\n⚠️ Some sprints need attention")
        return 1

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ReactorSync Sprint Validation")
    parser.add_argument("sprint", nargs="?", type=int, 
                       help="Sprint number to validate (1, 2, 3, etc.)")
    parser.add_argument("--all", action="store_true",
                       help="Validate all completed sprints")
    
    args = parser.parse_args()
    
    if args.all:
        return validate_all_sprints()
    elif args.sprint:
        success = run_sprint_validation(args.sprint)
        return 0 if success else 1
    else:
        print("🚀 ReactorSync Validation Options:")
        print("=" * 50)
        print("python validate.py 1           # Validate Sprint 1")
        print("python validate.py 2           # Validate Sprint 2") 
        print("python validate.py 3           # Validate Sprint 3")
        print("python validate.py --all       # Validate all sprints")
        print("")
        print("Individual sprint validation:")
        print("python validate_sprint1.py     # Infrastructure foundation")
        print("python validate_sprint2.py     # Database & data models")
        print("python validate_sprint3.py     # Synthetic data generation")
        print("")
        print("Integration testing:")
        print("./test_integration.sh          # Full environment test")
        print("./test_quick.sh               # Quick structure test")
        return 0

if __name__ == "__main__":
    sys.exit(main())
