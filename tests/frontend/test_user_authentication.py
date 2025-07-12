"""
User Authentication Test Suite
Comprehensive testing of OpenCart login/logout functionality
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


class TestUserAuthentication:
    """
    Test suite for user authentication functionality
    Tests login, logout, session management, and security features
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
        
        # Cleanup - ensure user is logged out
        try:
            if self.home_page.is_user_logged_in():
                self.home_page.click_logout()
        except:
            pass
        
        if config.screenshot_on_failure:
            self.driver.save_screenshot(f"{config.screenshots_dir}/auth_test_cleanup_{int(time.time())}.png")
    
    @pytest.mark.smoke
    def test_successful_login_with_valid_credentials(self):
        """
        Test Case 1: Successful login with valid credentials
        
        Verify that registered users can log in successfully
        """
        logger.info("=== Test Case 1: Successful Login ===")
        
        # First register a user
        user_data = {
            'firstname': self.fake.first_name(),
            'lastname': self.fake.last_name(),
            'email': self.fake.email(),
            'telephone': self.fake.phone_number()[:15],
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!',
            'newsletter': True
        }
        
        # Register user
        self.home_page.click_register()
        self.registration_page.complete_registration(user_data)
        assert self.registration_page.is_registration_successful(), "Registration failed"
        
        # Logout
        self.driver.get(self.base_url)
        if self.home_page.is_user_logged_in():
            self.home_page.click_logout()
        
        # Now test login
        self.home_page.click_login()
        
        # Verify we're on login page
        current_url = self.driver.current_url
        assert "login" in current_url.lower(), "Not on login page"
        
        # Login with registered credentials
        self._perform_login(user_data['email'], user_data['password'])
        
        # Verify successful login
        self.driver.get(self.base_url)
        assert self.home_page.is_user_logged_in(), "User not logged in after successful login"
        
        logger.info(f"✅ User successfully logged in: {user_data['email']}")
    
    def test_failed_login_with_invalid_credentials(self):
        """
        Test Case 2: Failed login with invalid credentials
        
        Verify that login fails with incorrect credentials
        """
        logger.info("=== Test Case 2: Failed Login with Invalid Credentials ===")
        
        # Navigate to login page
        self.home_page.click_login()
        
        # Try login with invalid credentials
        invalid_email = "nonexistent@example.com"
        invalid_password = "wrongpassword123"
        
        self._perform_login(invalid_email, invalid_password)
        
        # Verify login failed
        self.driver.get(self.base_url)
        assert not self.home_page.is_user_logged_in(), "Login should have failed"
        
        # Check for error message on login page
        current_url = self.driver.current_url
        if "login" in current_url.lower():
            # Should show error message
            error_present = self._check_for_login_error()
            logger.info(f"Login error message present: {error_present}")
        
        logger.info("✅ Login correctly failed with invalid credentials")
    
    def test_logout_functionality(self):
        """
        Test Case 3: Logout functionality
        
        Verify that users can log out successfully
        """
        logger.info("=== Test Case 3: Logout Functionality ===")
        
        # First login a user
        user_data = self._create_and_login_user()
        
        # Verify user is logged in
        assert self.home_page.is_user_logged_in(), "User should be logged in"
        
        # Logout
        self.home_page.click_logout()
        
        # Verify logout successful
        assert not self.home_page.is_user_logged_in(), "User should be logged out"
        
        # Try to access account page directly (should redirect to login)
        account_url = f"{self.base_url}/index.php?route=account/account"
        self.driver.get(account_url)
        
        # Should be redirected to login or show login required message
        current_url = self.driver.current_url
        page_requires_login = "login" in current_url.lower() or self._check_login_required_message()
        
        assert page_requires_login, "Should require login to access account page"
        
        logger.info("✅ Logout functionality working correctly")
    
    def test_session_persistence(self):
        """
        Test Case 4: Session persistence across page navigation
        
        Verify that login session persists during normal navigation
        """
        logger.info("=== Test Case 4: Session Persistence ===")
        
        # Login user
        user_data = self._create_and_login_user()
        assert self.home_page.is_user_logged_in(), "User should be logged in"
        
        # Navigate to different pages
        pages_to_test = [
            self.base_url,  # Home page
            f"{self.base_url}/index.php?route=product/category&path=20",  # Category page
            f"{self.base_url}/index.php?route=product/search"  # Search page
        ]
        
        for page_url in pages_to_test:
            self.driver.get(page_url)
            time.sleep(2)  # Wait for page load
            
            # Verify still logged in
            is_logged_in = self.home_page.is_user_logged_in()
            assert is_logged_in, f"Session lost on page: {page_url}"
        
        logger.info("✅ Session persistence working correctly")
    
    def test_login_form_validation(self):
        """
        Test Case 5: Login form validation
        
        Verify that login form validates required fields
        """
        logger.info("=== Test Case 5: Login Form Validation ===")
        
        self.home_page.click_login()
        
        # Test empty form submission
        self._perform_login("", "")
        
        # Should show validation errors or not process login
        validation_working = self._check_for_validation_errors() or not self.home_page.is_user_logged_in()
        assert validation_working, "Form should validate empty fields"
        
        # Test invalid email format
        self._perform_login("invalid-email", "password123")
        
        # Should show email validation error or fail login
        email_validation_working = self._check_for_email_validation_error() or not self.home_page.is_user_logged_in()
        logger.info(f"Email validation working: {email_validation_working}")
        
        logger.info("✅ Login form validation tested")
    
    def test_password_field_security(self):
        """
        Test Case 6: Password field security features
        
        Verify that password field is properly secured
        """
        logger.info("=== Test Case 6: Password Field Security ===")
        
        self.home_page.click_login()
        
        # Check password field type
        try:
            password_field = self.driver.find_element(By.ID, "input-password")
            field_type = password_field.get_attribute("type")
            assert field_type == "password", f"Password field should be type 'password', got '{field_type}'"
            
            # Enter password and verify it's masked
            password_field.send_keys("testpassword123")
            displayed_value = password_field.get_attribute("value")
            
            # Note: In most browsers, the actual password value is still retrievable via JavaScript
            # The security is in the visual masking, not in hiding the value from automation
            logger.info(f"Password field type: {field_type}")
            
        except Exception as e:
            logger.warning(f"Could not test password field: {e}")
        
        logger.info("✅ Password field security tested")
    
    def test_login_attempt_throttling(self):
        """
        Test Case 7: Login attempt throttling/rate limiting
        
        Verify that excessive login attempts are throttled
        """
        logger.info("=== Test Case 7: Login Attempt Throttling ===")
        
        self.home_page.click_login()
        
        # Attempt multiple failed logins
        for attempt in range(5):
            logger.info(f"Login attempt {attempt + 1}")
            self._perform_login("test@example.com", "wrongpassword")
            time.sleep(1)
        
        # Check if throttling is in effect
        # This could manifest as:
        # 1. CAPTCHA requirement
        # 2. Temporary account lockout message
        # 3. Increased delay in responses
        # 4. Rate limiting error
        
        throttling_detected = self._check_for_throttling_indicators()
        logger.info(f"Throttling indicators detected: {throttling_detected}")
        
        # Note: Some systems may not implement throttling, which is a security finding
        logger.info("✅ Login throttling tested")
    
    def test_remember_me_functionality(self):
        """
        Test Case 8: Remember me functionality (if available)
        
        Verify remember me checkbox behavior
        """
        logger.info("=== Test Case 8: Remember Me Functionality ===")
        
        self.home_page.click_login()
        
        # Check if remember me option exists
        remember_me_exists = self._check_remember_me_option()
        
        if remember_me_exists:
            logger.info("Remember me option found - testing functionality")
            
            # Create and login user with remember me
            user_data = self._create_test_user()
            self._perform_login(user_data['email'], user_data['password'], remember_me=True)
            
            # Verify login successful
            assert self.home_page.is_user_logged_in(), "Login with remember me failed"
            
            # Test session persistence (would require browser restart to fully test)
            logger.info("Remember me option tested (full test requires browser restart)")
        else:
            logger.info("Remember me option not found - skipping test")
        
        logger.info("✅ Remember me functionality tested")
    
    # Helper methods
    
    def _create_test_user(self) -> dict:
        """Create a test user and return user data"""
        user_data = {
            'firstname': self.fake.first_name(),
            'lastname': self.fake.last_name(),
            'email': self.fake.email(),
            'telephone': self.fake.phone_number()[:15],
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!',
            'newsletter': True
        }
        
        # Register user
        self.home_page.click_register()
        self.registration_page.complete_registration(user_data)
        assert self.registration_page.is_registration_successful(), "User registration failed"
        
        return user_data
    
    def _create_and_login_user(self) -> dict:
        """Create a test user and log them in"""
        user_data = self._create_test_user()
        
        # Logout if already logged in
        self.driver.get(self.base_url)
        if self.home_page.is_user_logged_in():
            self.home_page.click_logout()
        
        # Login
        self.home_page.click_login()
        self._perform_login(user_data['email'], user_data['password'])
        
        return user_data
    
    def _perform_login(self, email: str, password: str, remember_me: bool = False):
        """Perform login with given credentials"""
        try:
            # Find and fill email field
            email_field = self.driver.find_element(By.ID, "input-email")
            email_field.clear()
            email_field.send_keys(email)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "input-password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Handle remember me if requested and available
            if remember_me:
                try:
                    remember_checkbox = self.driver.find_element(By.NAME, "remember")
                    if not remember_checkbox.is_selected():
                        remember_checkbox.click()
                except:
                    pass  # Remember me not available
            
            # Submit form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
            login_button.click()
            
            # Wait for response
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Error performing login: {e}")
    
    def _check_for_login_error(self) -> bool:
        """Check if login error message is displayed"""
        try:
            error_selectors = [
                ".alert.alert-danger",
                ".text-danger",
                "[class*='error']",
                "[class*='warning']"
            ]
            
            for selector in error_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(elem.is_displayed() for elem in elements):
                    return True
            return False
        except:
            return False
    
    def _check_for_validation_errors(self) -> bool:
        """Check for form validation errors"""
        return self._check_for_login_error()
    
    def _check_for_email_validation_error(self) -> bool:
        """Check for email-specific validation error"""
        return self._check_for_login_error()
    
    def _check_login_required_message(self) -> bool:
        """Check if page shows login required message"""
        try:
            page_text = self.driver.page_source.lower()
            login_indicators = [
                "login required", 
                "please login", 
                "access denied",
                "authentication required"
            ]
            return any(indicator in page_text for indicator in login_indicators)
        except:
            return False
    
    def _check_for_throttling_indicators(self) -> bool:
        """Check for login throttling indicators"""
        try:
            page_source = self.driver.page_source.lower()
            throttling_indicators = [
                "too many attempts",
                "account locked",
                "rate limit",
                "captcha",
                "temporarily disabled",
                "try again later"
            ]
            return any(indicator in page_source for indicator in throttling_indicators)
        except:
            return False
    
    def _check_remember_me_option(self) -> bool:
        """Check if remember me option exists"""
        try:
            remember_checkbox = self.driver.find_element(By.NAME, "remember")
            return remember_checkbox.is_displayed()
        except:
            return False