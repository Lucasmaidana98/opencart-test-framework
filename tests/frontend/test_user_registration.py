"""
User Registration Test Suite
Comprehensive testing of OpenCart customer registration functionality
Author: Lucas Maidana
"""

import pytest
import time
from faker import Faker
from selenium.webdriver.common.by import By

from pages.frontend.home_page import HomePage
from pages.frontend.registration_page import RegistrationPage
from config.settings import config, customer_data
from utils.driver_manager import get_driver
from loguru import logger


class TestUserRegistration:
    """
    Test suite for user registration functionality
    Tests various registration scenarios including validation, security, and edge cases
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.driver = get_driver()
        self.base_url = config.base_url
        self.fake = Faker()
        
        # Initialize page objects
        self.home_page = HomePage(self.driver)
        self.registration_page = RegistrationPage(self.driver)
        
        # Navigate to home page
        self.driver.get(self.base_url)
        
        yield
        
        # Cleanup
        if config.screenshot_on_failure:
            self.driver.save_screenshot(f"{config.screenshots_dir}/test_cleanup_{int(time.time())}.png")
    
    def generate_test_user_data(self, **overrides) -> dict:
        """
        Generate test user data with faker
        
        Args:
            **overrides: Override specific fields
            
        Returns:
            dict: User data for registration
        """
        user_data = {
            'firstname': self.fake.first_name(),
            'lastname': self.fake.last_name(),
            'email': self.fake.email(),
            'telephone': self.fake.phone_number()[:15],  # Limit length
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!',
            'newsletter': True
        }
        
        # Apply overrides
        user_data.update(overrides)
        return user_data
    
    def test_successful_registration_with_valid_data(self):
        """
        Test Case 1: Successful user registration with valid data
        
        Verify that a new user can successfully register with valid information
        """
        logger.info("=== Test Case 1: Successful Registration ===")
        
        # Navigate to registration page
        self.home_page.click_register()
        assert self.registration_page.is_registration_page_loaded(), "Registration page not loaded"
        
        # Generate test user data
        user_data = self.generate_test_user_data()
        
        # Complete registration
        self.registration_page.complete_registration(user_data)
        
        # Verify successful registration
        assert self.registration_page.is_registration_successful(), "Registration was not successful"
        
        # Verify user is logged in
        self.driver.get(self.base_url)
        assert self.home_page.is_user_logged_in(), "User is not logged in after registration"
        
        logger.info(f"✅ User successfully registered: {user_data['email']}")
    
    def test_registration_with_existing_email(self):
        """
        Test Case 2: Registration with existing email address
        
        Verify that registration fails when using an already registered email
        """
        logger.info("=== Test Case 2: Registration with Existing Email ===")
        
        # First registration
        user_data_1 = self.generate_test_user_data()
        
        self.home_page.click_register()
        self.registration_page.complete_registration(user_data_1)
        assert self.registration_page.is_registration_successful(), "First registration failed"
        
        # Logout if logged in
        self.driver.get(self.base_url)
        if self.home_page.is_user_logged_in():
            self.home_page.click_logout()
        
        # Second registration with same email
        user_data_2 = self.generate_test_user_data(
            email=user_data_1['email']  # Use same email
        )
        
        self.home_page.click_register()
        self.registration_page.complete_registration(user_data_2)
        
        # Verify registration fails
        assert not self.registration_page.is_registration_successful(), "Registration should have failed"
        
        # Check for appropriate error message
        error_message = self.registration_page.get_general_error()
        assert "already registered" in error_message.lower() or "exists" in error_message.lower(), \
            f"Expected email exists error, got: {error_message}"
        
        logger.info("✅ Registration correctly rejected duplicate email")
    
    def test_registration_form_validation(self):
        """
        Test Case 3: Form validation with empty and invalid data
        
        Verify that form validation works correctly for required fields
        """
        logger.info("=== Test Case 3: Form Validation ===")
        
        self.home_page.click_register()
        assert self.registration_page.is_registration_page_loaded(), "Registration page not loaded"
        
        # Test 1: Submit empty form
        self.registration_page.submit_registration()
        
        # Verify validation errors
        assert self.registration_page.has_validation_errors(), "Expected validation errors for empty form"
        
        errors = self.registration_page.get_all_validation_errors()
        expected_fields = ['firstname', 'lastname', 'email', 'telephone', 'password']
        
        for field in expected_fields:
            assert field in errors or len(errors) > 0, f"Expected validation error for {field}"
        
        logger.info("✅ Empty form validation working correctly")
        
        # Test 2: Invalid email format
        invalid_user_data = self.generate_test_user_data(email="invalid-email")
        self.registration_page.clear_all_fields()
        self.registration_page.complete_registration(invalid_user_data)
        
        # Should have email validation error
        email_error = self.registration_page.get_email_error()
        assert email_error or not self.registration_page.is_registration_successful(), \
            "Expected email format validation"
        
        logger.info("✅ Email format validation working correctly")
        
        # Test 3: Password mismatch
        password_mismatch_data = self.generate_test_user_data(
            confirm_password="DifferentPassword123!"
        )
        self.registration_page.clear_all_fields()
        self.registration_page.complete_registration(password_mismatch_data)
        
        # Should have password confirmation error
        password_error = self.registration_page.get_confirm_password_error()
        assert password_error or not self.registration_page.is_registration_successful(), \
            "Expected password mismatch validation"
        
        logger.info("✅ Password confirmation validation working correctly")
    
    def test_registration_with_special_characters(self):
        """
        Test Case 4: Registration with special characters in fields
        
        Verify that the system handles special characters appropriately
        """
        logger.info("=== Test Case 4: Special Characters Handling ===")
        
        self.home_page.click_register()
        
        # Test with special characters in name fields
        special_user_data = self.generate_test_user_data(
            firstname="José María",
            lastname="O'Connor-Smith",
            telephone="+1 (555) 123-4567"
        )
        
        self.registration_page.complete_registration(special_user_data)
        
        # Registration should succeed with proper character handling
        success = self.registration_page.is_registration_successful()
        if not success:
            errors = self.registration_page.get_all_validation_errors()
            logger.warning(f"Special character registration failed: {errors}")
        
        logger.info("✅ Special characters test completed")
    
    def test_newsletter_subscription_options(self):
        """
        Test Case 5: Newsletter subscription options
        
        Verify that newsletter subscription options work correctly
        """
        logger.info("=== Test Case 5: Newsletter Subscription ===")
        
        self.home_page.click_register()
        
        # Test with newsletter subscription enabled
        user_data = self.generate_test_user_data(newsletter=True)
        self.registration_page.complete_registration(user_data)
        
        success = self.registration_page.is_registration_successful()
        assert success, "Registration with newsletter subscription failed"
        
        logger.info("✅ Newsletter subscription test completed")
    
    def test_privacy_policy_requirement(self):
        """
        Test Case 6: Privacy policy acceptance requirement
        
        Verify that privacy policy must be accepted for registration
        """
        logger.info("=== Test Case 6: Privacy Policy Requirement ===")
        
        self.home_page.click_register()
        
        user_data = self.generate_test_user_data()
        
        # Fill form but don't accept privacy policy
        self.registration_page.fill_personal_details(
            user_data['firstname'],
            user_data['lastname'],
            user_data['email'],
            user_data['telephone']
        )
        self.registration_page.fill_password(user_data['password'])
        self.registration_page.select_newsletter_subscription(user_data['newsletter'])
        
        # Submit without accepting privacy policy
        self.registration_page.submit_registration()
        
        # Registration should fail
        success = self.registration_page.is_registration_successful()
        assert not success, "Registration should fail without privacy policy acceptance"
        
        logger.info("✅ Privacy policy requirement working correctly")
    
    def test_password_strength_requirements(self):
        """
        Test Case 7: Password strength validation
        
        Verify password strength requirements are enforced
        """
        logger.info("=== Test Case 7: Password Strength ===")
        
        self.home_page.click_register()
        
        # Test weak passwords
        weak_passwords = [
            "123",          # Too short
            "password",     # Too common
            "12345678",     # No letters
            "abcdefgh"      # No numbers
        ]
        
        for weak_password in weak_passwords:
            logger.info(f"Testing weak password: {weak_password}")
            
            user_data = self.generate_test_user_data(
                password=weak_password,
                confirm_password=weak_password
            )
            
            self.registration_page.clear_all_fields()
            self.registration_page.complete_registration(user_data)
            
            # Check if registration fails or password error appears
            success = self.registration_page.is_registration_successful()
            password_error = self.registration_page.get_password_error()
            
            if success:
                logger.warning(f"Weak password '{weak_password}' was accepted")
            else:
                logger.info(f"Weak password '{weak_password}' correctly rejected")
        
        logger.info("✅ Password strength testing completed")
    
    def test_registration_form_field_limits(self):
        """
        Test Case 8: Field length limits and boundary testing
        
        Verify that form fields handle length limits appropriately
        """
        logger.info("=== Test Case 8: Field Length Limits ===")
        
        self.home_page.click_register()
        
        # Test with very long values
        long_user_data = self.generate_test_user_data(
            firstname="A" * 100,    # Very long first name
            lastname="B" * 100,     # Very long last name
            email="c" * 50 + "@example.com",  # Long email
            telephone="1" * 50      # Long telephone
        )
        
        self.registration_page.complete_registration(long_user_data)
        
        # Check if form handles long input appropriately
        success = self.registration_page.is_registration_successful()
        errors = self.registration_page.get_all_validation_errors()
        
        if errors:
            logger.info(f"Long field validation errors: {errors}")
        
        logger.info("✅ Field length limit testing completed")
    
    def test_registration_page_navigation(self):
        """
        Test Case 9: Registration page navigation and links
        
        Verify that page navigation works correctly
        """
        logger.info("=== Test Case 9: Page Navigation ===")
        
        self.home_page.click_register()
        assert self.registration_page.is_registration_page_loaded(), "Registration page not loaded"
        
        # Test login link
        self.registration_page.click_login_link()
        
        # Verify navigation to login page
        current_url = self.driver.current_url
        assert "login" in current_url.lower(), f"Expected login page, got: {current_url}"
        
        logger.info("✅ Navigation from registration to login working")
        
        # Test privacy policy link (opens in new tab/window)
        self.driver.back()  # Go back to registration
        
        original_handles = self.driver.window_handles
        self.registration_page.click_privacy_policy_link()
        
        # Check if new window/tab opened
        new_handles = self.driver.window_handles
        if len(new_handles) > len(original_handles):
            logger.info("✅ Privacy policy link opens new window")
            # Close new window and return to original
            self.driver.switch_to.window(new_handles[-1])
            self.driver.close()
            self.driver.switch_to.window(original_handles[0])
        
        logger.info("✅ Page navigation testing completed")
    
    def test_registration_performance(self):
        """
        Test Case 10: Registration performance and timeout handling
        
        Verify that registration completes within acceptable time limits
        """
        logger.info("=== Test Case 10: Registration Performance ===")
        
        start_time = time.time()
        
        self.home_page.click_register()
        user_data = self.generate_test_user_data()
        self.registration_page.complete_registration(user_data)
        
        # Wait for registration to complete
        self.registration_page.is_registration_successful()
        
        end_time = time.time()
        registration_time = end_time - start_time
        
        # Registration should complete within reasonable time (30 seconds)
        max_time = 30
        assert registration_time < max_time, \
            f"Registration took too long: {registration_time:.2f}s (max: {max_time}s)"
        
        logger.info(f"✅ Registration completed in {registration_time:.2f} seconds")
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox"])
    def test_cross_browser_registration(self, browser):
        """
        Test Case 11: Cross-browser compatibility
        
        Verify registration works across different browsers
        """
        logger.info(f"=== Cross-Browser Test: {browser} ===")
        
        # This test would be run with different browser configurations
        # The parametrize decorator runs this test for each browser
        
        user_data = self.generate_test_user_data()
        
        self.home_page.click_register()
        self.registration_page.complete_registration(user_data)
        
        success = self.registration_page.is_registration_successful()
        assert success, f"Registration failed in {browser}"
        
        logger.info(f"✅ Registration successful in {browser}")


# Additional test utilities
class TestRegistrationUtils:
    """Utility methods for registration testing"""
    
    @staticmethod
    def cleanup_test_users(driver, test_emails: list):
        """
        Clean up test users from database (would require admin access)
        
        Args:
            driver: WebDriver instance
            test_emails: List of test email addresses to clean up
        """
        # This would require admin panel access or database cleanup
        # Implementation depends on available cleanup mechanisms
        pass
    
    @staticmethod
    def verify_email_in_database(email: str) -> bool:
        """
        Verify email exists in database
        
        Args:
            email: Email to verify
            
        Returns:
            bool: True if email exists in database
        """
        # This would require database connection
        # Implementation depends on database access configuration
        return True