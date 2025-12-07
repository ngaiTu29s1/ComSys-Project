"""
Script chạy toàn bộ test suite và báo cáo kết quả tổng hợp.
Chạy: python scripts/run_all_tests.py
"""

import subprocess
import sys
from pathlib import Path

# Danh sách các test files cần chạy (theo thứ tự)
TEST_FILES = [
    "tests/smoke_env.py",
    "tests/test_decision_logic.py",
    "tests/test_simulation.py",
    "tests/test_schemas.py",
    "tests/test_ml_inference.py",
]

# Test cần API server (chạy riêng)
API_TESTS = [
    "tests/test_api.py",
]


def run_test_file(test_file: str) -> tuple[bool, str]:
    """Chạy một test file và trả về kết quả"""
    print(f"\n{'='*70}")
    print(f"📝 Running: {test_file}")
    print('='*70)
    
    try:
        result = subprocess.run(
            ["pytest", test_file, "-v"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # In output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        
        return success, status
        
    except subprocess.TimeoutExpired:
        return False, "⏱️ TIMEOUT"
    except Exception as e:
        return False, f"💥 ERROR: {str(e)}"


def main():
    print("🚀 Running Full Test Suite")
    print("="*70)
    
    results = {}
    failed_tests = []
    
    # Chạy các test thông thường
    for test_file in TEST_FILES:
        success, status = run_test_file(test_file)
        results[test_file] = status
        
        if not success:
            failed_tests.append(test_file)
    
    # Báo cáo tổng hợp
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for test_file, status in results.items():
        print(f"{status:15} {test_file}")
    
    # Test API (cần server riêng)
    print("\n" + "="*70)
    print("⚠️  API Tests (require running server):")
    for api_test in API_TESTS:
        print(f"   {api_test}")
    print("   Run separately: pytest tests/test_api.py -v")
    print("="*70)
    
    # Kết quả cuối
    total = len(TEST_FILES)
    passed = total - len(failed_tests)
    
    print(f"\n{'='*70}")
    print(f"📈 FINAL RESULT: {passed}/{total} test files passed")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
        print("="*70)
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        print("="*70)
        sys.exit(0)


if __name__ == "__main__":
    main()
