"""
Registration Page Object Model
Customer registration functionality for OpenCart frontend
Author: Lucas Maidana
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from loguru import logger


class RegistrationPage(BasePage):
    """
    Registration page object model for OpenCart frontend
    Handles customer account creation and form validation
    """
    
    # Page locators
    PAGE_TITLE = (By.CSS_SELECTOR, "h1")
    
    # Personal Details section
    FIRSTNAME_INPUT = (By.ID, "input-firstname")
    LASTNAME_INPUT = (By.ID, "input-lastname")
    EMAIL_INPUT = (By.ID, "input-email")
    TELEPHONE_INPUT = (By.ID, "input-telephone")
    
    # Password section
    PASSWORD_INPUT = (By.ID, "input-password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "input-confirm")
    
    # Newsletter subscription
    NEWSLETTER_YES_RADIO = (By.CSS_SELECTOR, "input[name='newsletter'][value='1']")
    NEWSLETTER_NO_RADIO = (By.CSS_SELECTOR, "input[name='newsletter'][value='0']")
    
    # Privacy Policy and Terms
    PRIVACY_POLICY_CHECKBOX = (By.NAME, "agree")
    PRIVACY_POLICY_LINK = (By.CSS_SELECTOR, "a[href*='information/information']")
    
    # Form submission
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "input[type='submit'][value='Continue']")
    
    # Error messages
    FIRSTNAME_ERROR = (By.ID, "error-firstname")
    LASTNAME_ERROR = (By.ID, "error-lastname")
    EMAIL_ERROR = (By.ID, "error-email")
    TELEPHONE_ERROR = (By.ID, "error-telephone")
    PASSWORD_ERROR = (By.ID, "error-password")
    CONFIRM_PASSWORD_ERROR = (By.ID, "error-confirm")
    GENERAL_ERROR = (By.CSS_SELECTOR, ".alert.alert-danger")
    
    # Success elements
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-success")
    SUCCESS_PAGE_TITLE = (By.CSS_SELECTOR, "h1")
    
    # Navigation
    LOGIN_LINK = (By.LINK_TEXT, "login page")
    BREADCRUMB = (By.CSS_SELECTOR, ".breadcrumb")
    
    def __init__(self, driver):
        """Initialize registration page"""
        super().__init__(driver)
    
    def navigate_to_registration(self, base_url: str):
        """
        Navigate to registration page
        
        Args:
            base_url: Base URL of OpenCart installation
        """
        registration_url = f"{base_url}/index.php?route=account/register"
        self.driver.get(registration_url)
        logger.info("Navigated to registration page")
        return self
    
    def is_registration_page_loaded(self) -> bool:
        """
        Verify registration page is loaded
        
        Returns:
            bool: True if registration page is loaded
        """
        try:
            page_title = self.get_element_text(self.PAGE_TITLE)
            is_loaded = "Register Account" in page_title
            logger.info(f"Registration page loaded: {is_loaded}")
            return is_loaded
        except:
            logger.error("Failed to verify registration page load")
            return False
    
    # ====================
    # FORM FILLING
    # ====================
    
    def fill_personal_details(self, firstname: str, lastname: str, email: str, telephone: str):
        """
        Fill personal details section
        
        Args:
            firstname: Customer first name
            lastname: Customer last name
            email: Customer email address
            telephone: Customer phone number
        """
        self.enter_text(self.FIRSTNAME_INPUT, firstname)
        self.enter_text(self.LASTNAME_INPUT, lastname)
        self.enter_text(self.EMAIL_INPUT, email)
        self.enter_text(self.TELEPHONE_INPUT, telephone)
        
        logger.info(f"Filled personal details for: {firstname} {lastname}")
        return self
    
    def fill_password(self, password: str, confirm_password: str = None):
        """
        Fill password fields
        
        Args:
            password: Password
            confirm_password: Password confirmation (defaults to same as password)
        """
        if confirm_password is None:
            confirm_password = password
        
        self.enter_text(self.PASSWORD_INPUT, password)
        self.enter_text(self.CONFIRM_PASSWORD_INPUT, confirm_password)
        
        logger.info("Filled password fields")
        return self
    
    def select_newsletter_subscription(self, subscribe: bool = True):
        """
        Select newsletter subscription option
        
        Args:
            subscribe: True to subscribe, False to not subscribe
        """
        if subscribe:
            self.click_element(self.NEWSLETTER_YES_RADIO)
            logger.info("Selected newsletter subscription: Yes")
        else:
            self.click_element(self.NEWSLETTER_NO_RADIO)
            logger.info("Selected newsletter subscription: No")
        return self
    
    def accept_privacy_policy(self):
        """Accept privacy policy checkbox"""
        if not self.is_checkbox_checked(self.PRIVACY_POLICY_CHECKBOX):
            self.click_element(self.PRIVACY_POLICY_CHECKBOX)
            logger.info("Accepted privacy policy")
        return self
    
    def is_checkbox_checked(self, locator: tuple) -> bool:
        """
        Check if checkbox is checked
        
        Args:
            locator: Checkbox locator
            
        Returns:
            bool: True if checkbox is checked
        """
        element = self.find_element(locator)
        return element.is_selected()
    
    def submit_registration(self):
        """Submit registration form"""
        self.click_element(self.CONTINUE_BUTTON)
        logger.info("Submitted registration form")
        return self
    
    def complete_registration(self, user_data: dict):
        """
        Complete full registration process
        
        Args:
            user_data: Dictionary containing user information
                - firstname: str
                - lastname: str  
                - email: str
                - telephone: str
                - password: str
                - confirm_password: str (optional)
                - newsletter: bool (optional, defaults to True)
        """
        # Fill personal details
        self.fill_personal_details(
            user_data['firstname'],
            user_data['lastname'],
            user_data['email'],
            user_data['telephone']
        )
        
        # Fill password
        confirm_password = user_data.get('confirm_password', user_data['password'])
        self.fill_password(user_data['password'], confirm_password)
        
        # Newsletter subscription
        newsletter = user_data.get('newsletter', True)
        self.select_newsletter_subscription(newsletter)
        
        # Accept privacy policy
        self.accept_privacy_policy()
        
        # Submit form
        self.submit_registration()
        
        logger.info(f"Completed registration for: {user_data['email']}")
        return self
    
    # ====================
    # VALIDATION METHODS
    # ====================
    
    def get_firstname_error(self) -> str:
        """Get first name validation error"""
        try:
            return self.get_element_text(self.FIRSTNAME_ERROR)
        except:
            return ""
    
    def get_lastname_error(self) -> str:
        """Get last name validation error"""
        try:
            return self.get_element_text(self.LASTNAME_ERROR)
        except:
            return ""
    
    def get_email_error(self) -> str:
        """Get email validation error"""
        try:
            return self.get_element_text(self.EMAIL_ERROR)
        except:
            return ""
    
    def get_telephone_error(self) -> str:
        """Get telephone validation error"""
        try:
            return self.get_element_text(self.TELEPHONE_ERROR)
        except:
            return ""
    
    def get_password_error(self) -> str:
        """Get password validation error"""
        try:
            return self.get_element_text(self.PASSWORD_ERROR)
        except:
            return ""
    
    def get_confirm_password_error(self) -> str:
        """Get confirm password validation error"""
        try:
            return self.get_element_text(self.CONFIRM_PASSWORD_ERROR)
        except:
            return ""
    
    def get_general_error(self) -> str:
        """Get general form error message"""
        try:
            return self.get_element_text(self.GENERAL_ERROR)
        except:
            return ""
    
    def has_validation_errors(self) -> bool:
        """
        Check if form has any validation errors
        
        Returns:
            bool: True if validation errors are present
        """
        errors = [
            self.get_firstname_error(),
            self.get_lastname_error(),
            self.get_email_error(),
            self.get_telephone_error(),
            self.get_password_error(),
            self.get_confirm_password_error(),
            self.get_general_error()
        ]
        
        has_errors = any(error for error in errors)
        logger.info(f"Validation errors present: {has_errors}")
        return has_errors
    
    def get_all_validation_errors(self) -> dict:
        """
        Get all validation errors as dictionary
        
        Returns:
            dict: Dictionary of field names and error messages
        """
        errors = {
            'firstname': self.get_firstname_error(),
            'lastname': self.get_lastname_error(),
            'email': self.get_email_error(),
            'telephone': self.get_telephone_error(),
            'password': self.get_password_error(),
            'confirm_password': self.get_confirm_password_error(),
            'general': self.get_general_error()
        }
        
        # Filter out empty errors
        errors = {key: value for key, value in errors.items() if value}
        logger.info(f"Validation errors: {errors}")
        return errors
    
    # ====================
    # SUCCESS VALIDATION
    # ====================
    
    def is_registration_successful(self) -> bool:
        """
        Check if registration was successful
        
        Returns:
            bool: True if registration successful
        """
        try:
            # Check for success message or redirect to success page
            success_message = self.is_element_visible(self.SUCCESS_MESSAGE, timeout=5)
            success_title = "Account" in self.get_page_title()
            
            is_successful = success_message or success_title
            logger.info(f"Registration successful: {is_successful}")
            return is_successful
        except:
            logger.error("Failed to verify registration success")
            return False
    
    def get_success_message(self) -> str:
        """Get registration success message"""
        try:
            return self.get_element_text(self.SUCCESS_MESSAGE)
        except:
            return ""
    
    # ====================
    # FIELD VALIDATION
    # ====================
    
    def clear_all_fields(self):
        """Clear all form fields"""
        fields = [
            self.FIRSTNAME_INPUT,
            self.LASTNAME_INPUT,
            self.EMAIL_INPUT,
            self.TELEPHONE_INPUT,
            self.PASSWORD_INPUT,
            self.CONFIRM_PASSWORD_INPUT
        ]
        
        for field in fields:
            element = self.find_element(field)
            element.clear()
        
        logger.info("Cleared all form fields")
        return self
    
    def get_field_value(self, field_locator: tuple) -> str:
        """
        Get current value of form field
        
        Args:
            field_locator: Field locator
            
        Returns:
            str: Current field value
        """
        return self.get_element_attribute(field_locator, "value")
    
    def is_field_required(self, field_locator: tuple) -> bool:
        """
        Check if field has required attribute
        
        Args:
            field_locator: Field locator
            
        Returns:
            bool: True if field is required
        """
        required_attr = self.get_element_attribute(field_locator, "required")
        return required_attr is not None
    
    # ====================
    # NAVIGATION
    # ====================
    
    def click_login_link(self):
        """Navigate to login page"""
        self.click_element(self.LOGIN_LINK)
        logger.info("Navigated to login page")
        return self
    
    def click_privacy_policy_link(self):
        """Open privacy policy page"""
        self.click_element(self.PRIVACY_POLICY_LINK)
        logger.info("Opened privacy policy page")
        return self