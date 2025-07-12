#!/usr/bin/env python3
"""
Framework Structure Test - Validate framework components without browser
Author: Lucas Maidana
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_framework_imports():
    """Test that all framework components can be imported"""
    print("🔧 Testing OpenCart Test Framework Structure...")
    
    try:
        # Test config imports
        print("📋 Testing config imports...")
        from config.settings import config, TestConfig, BrowserConfig
        print("✅ Config imports successful")
        
        # Test page object imports
        print("📄 Testing page object imports...")
        from pages.base_page import BasePage
        from pages.frontend.home_page import HomePage
        from pages.frontend.registration_page import RegistrationPage
        from pages.frontend.cart_page import CartPage
        print("✅ Page object imports successful")
        
        # Test utils imports
        print("🛠️ Testing utils imports...")
        from utils.driver_manager import DriverManager
        print("✅ Utils imports successful")
        
        # Test configuration
        print("⚙️ Testing configuration...")
        print(f"  Base URL: {config.base_url}")
        print(f"  Current browser: {config.current_browser}")
        print(f"  Implicit wait: {config.implicit_wait}")
        print(f"  Available browsers: {list(config.browsers.keys())}")
        print("✅ Configuration validated")
        
        # Test pytest configuration
        print("🧪 Testing pytest configuration...")
        import pytest
        print(f"  Pytest version: {pytest.__version__}")
        print("✅ Pytest configuration validated")
        
        print("\n🎉 All framework components imported and validated successfully!")
        print("📦 Framework is ready for testing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Framework structure test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test that all required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'config',
        'pages',
        'pages/frontend', 
        'tests',
        'tests/frontend',
        'utils',
        'scripts',
        '.github/workflows'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - Missing")
            return False
    
    print("✅ Directory structure validated")
    return True

def test_required_files():
    """Test that all required files exist"""
    print("\n📄 Testing required files...")
    
    required_files = [
        'requirements.txt',
        'pytest.ini', 
        'conftest.py',
        'README.md',
        'config/settings.py',
        'utils/driver_manager.py',
        'pages/base_page.py',
        'tests/frontend/test_user_registration.py',
        'tests/frontend/test_shopping_cart.py',
        '.github/workflows/opencart-tests.yml'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            return False
    
    print("✅ Required files validated")
    return True

def test_test_matrix_generator():
    """Test the test matrix generator script"""
    print("\n📊 Testing test matrix generator...")
    
    try:
        sys.path.append('scripts')
        from generate_test_matrix import TestMatrixGenerator
        
        generator = TestMatrixGenerator()
        
        # Test smoke matrix generation
        smoke_matrix = generator.generate_smoke_matrix()
        print(f"  Smoke matrix jobs: {smoke_matrix['total_jobs']}")
        
        # Test cross-browser matrix
        cross_browser_matrix = generator.generate_cross_browser_matrix()
        print(f"  Cross-browser matrix jobs: {cross_browser_matrix['total_jobs']}")
        
        # Test full matrix
        full_matrix = generator.generate_matrix(test_suite='all', browser='all', max_parallel=20)
        print(f"  Full matrix jobs: {full_matrix['total_jobs']}")
        print(f"  Estimated time: {full_matrix['estimated_total_time']} minutes")
        
        print("✅ Test matrix generator validated")
        return True
        
    except Exception as e:
        print(f"❌ Test matrix generator failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 OpenCart Test Framework Structure Validation")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run all validation tests
    all_tests_passed &= test_directory_structure()
    all_tests_passed &= test_required_files()
    all_tests_passed &= test_framework_imports()
    all_tests_passed &= test_test_matrix_generator()
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - Framework is ready!")
        print("🚀 You can now run: pytest tests/frontend/test_user_registration.py")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Framework needs fixes")
        sys.exit(1)