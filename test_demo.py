#!/usr/bin/env python3
"""
Demo Test - Quick validation of framework functionality
Author: Lucas Maidana
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.driver_manager import DriverManager
from config.settings import config
import time

def test_framework_demo():
    """Simple demo test to validate framework setup"""
    print("🚀 Testing OpenCart Test Framework...")
    
    # Initialize driver manager
    driver_manager = DriverManager('chrome')
    
    try:
        # Create driver
        print("📱 Creating WebDriver...")
        driver = driver_manager.create_driver()
        
        # Navigate to Google (since we don't have OpenCart running)
        print("🌐 Navigating to Google...")
        driver.get("https://www.google.com")
        
        # Verify page loaded
        assert "Google" in driver.title
        print(f"✅ Page loaded successfully: {driver.title}")
        
        # Take a screenshot
        screenshot_path = driver_manager.take_screenshot("demo_test.png")
        print(f"📸 Screenshot taken: {screenshot_path}")
        
        # Wait a moment
        time.sleep(2)
        
        print("✅ Framework demo test completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo test failed: {str(e)}")
        raise
    
    finally:
        # Cleanup
        driver_manager.quit_driver()
        print("🧹 WebDriver cleaned up")

if __name__ == "__main__":
    test_framework_demo()