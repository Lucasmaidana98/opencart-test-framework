"""
Base Page Object Model
Foundation class for all page objects with common functionality
Author: Lucas Maidana
"""

import time
from typing import List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException
)
from loguru import logger

from config.settings import config


class BasePage:
    """
    Base page object providing common functionality for all page objects
    Implements advanced WebDriver operations with robust error handling
    """
    
    def __init__(self, driver):
        """
        Initialize base page with WebDriver instance
        
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, config.explicit_wait)
        self.actions = ActionChains(driver)
    
    # ====================
    # ELEMENT INTERACTION
    # ====================
    
    def find_element(self, locator: Tuple[str, str], timeout: int = None) -> object:
        """
        Find element with explicit wait and error handling
        
        Args:
            locator: Tuple of (By, value)
            timeout: Optional timeout override
            
        Returns:
            WebElement: Found element
            
        Raises:
            TimeoutException: If element not found within timeout
        """
        timeout = timeout or config.explicit_wait
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            logger.debug(f"Element found: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Element not found within {timeout}s: {locator}")
            raise
    
    def find_elements(self, locator: Tuple[str, str], timeout: int = None) -> List[object]:
        """
        Find multiple elements with explicit wait
        
        Args:
            locator: Tuple of (By, value)
            timeout: Optional timeout override
            
        Returns:
            List[WebElement]: List of found elements
        """
        timeout = timeout or config.explicit_wait
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            elements = self.driver.find_elements(*locator)
            logger.debug(f"Found {len(elements)} elements: {locator}")
            return elements
        except TimeoutException:
            logger.warning(f"No elements found within {timeout}s: {locator}")
            return []
    
    def click_element(self, locator: Tuple[str, str], timeout: int = None):
        """
        Click element with retry mechanism and advanced error handling
        
        Args:
            locator: Tuple of (By, value)
            timeout: Optional timeout override
        """
        timeout = timeout or config.explicit_wait
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.element_to_be_clickable(locator))
                
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)  # Brief pause for scroll animation
                
                element.click()
                logger.debug(f"Element clicked successfully: {locator}")
                return
                
            except ElementClickInterceptedException:
                # Try JavaScript click as fallback
                logger.warning(f"Click intercepted, trying JavaScript click: {locator}")
                element = self.find_element(locator, timeout)
                self.driver.execute_script("arguments[0].click();", element)
                return
                
            except TimeoutException:
                if attempt == max_retries - 1:
                    logger.error(f"Element not clickable after {max_retries} attempts: {locator}")
                    raise
                logger.warning(f"Click attempt {attempt + 1} failed, retrying: {locator}")
                time.sleep(1)
    
    def enter_text(self, locator: Tuple[str, str], text: str, clear_first: bool = True):
        """
        Enter text into input field with validation
        
        Args:
            locator: Tuple of (By, value)
            text: Text to enter
            clear_first: Whether to clear field before entering text
        """
        element = self.find_element(locator)
        
        if clear_first:
            element.clear()
        
        element.send_keys(text)
        
        # Validate text was entered correctly
        entered_text = element.get_attribute('value')
        if entered_text != text:
            logger.warning(f"Text validation failed. Expected: '{text}', Got: '{entered_text}'")
        
        logger.debug(f"Text entered: '{text}' into {locator}")
    
    def get_element_text(self, locator: Tuple[str, str], timeout: int = None) -> str:
        """
        Get text content of element
        
        Args:
            locator: Tuple of (By, value)
            timeout: Optional timeout override
            
        Returns:
            str: Element text content
        """
        element = self.find_element(locator, timeout)
        text = element.text.strip()
        logger.debug(f"Element text retrieved: '{text}' from {locator}")
        return text
    
    def get_element_attribute(self, locator: Tuple[str, str], attribute: str, timeout: int = None) -> str:
        """
        Get element attribute value
        
        Args:
            locator: Tuple of (By, value)
            attribute: Attribute name
            timeout: Optional timeout override
            
        Returns:
            str: Attribute value
        """
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        logger.debug(f"Attribute '{attribute}' value: '{value}' from {locator}")
        return value
    
    def select_dropdown_by_text(self, locator: Tuple[str, str], text: str):
        """
        Select dropdown option by visible text
        
        Args:
            locator: Tuple of (By, value)
            text: Visible text to select
        """
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_visible_text(text)
        logger.debug(f"Dropdown option selected: '{text}' in {locator}")
    
    def select_dropdown_by_value(self, locator: Tuple[str, str], value: str):
        """
        Select dropdown option by value
        
        Args:
            locator: Tuple of (By, value)
            value: Value to select
        """
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_value(value)
        logger.debug(f"Dropdown value selected: '{value}' in {locator}")
    
    # ====================
    # WAIT CONDITIONS
    # ====================
    
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = None) -> object:
        """
        Wait for element to be visible
        
        Args:
            locator: Tuple of (By, value)
            timeout: Optional timeout override
            
        Returns:
            WebElement: Visible element
        """
        timeout = timeout or config.explicit_wait
        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.visibility_of_element_located(locator))
        logger.debug(f"Element visible: {locator}")
        return element
    
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = None) -> object:
        """
        Wait for element to be clickable
        
        Args:
            locator: Tuple of (By, value)
            timeout: Optional timeout override
            
        Returns:
            WebElement: Clickable element
        """
        timeout = timeout or config.explicit_wait
        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.element_to_be_clickable(locator))
        logger.debug(f"Element clickable: {locator}")
        return element
    
    def wait_for_text_in_element(self, locator: Tuple[str, str], text: str, timeout: int = None) -> bool:
        """
        Wait for specific text to appear in element
        
        Args:
            locator: Tuple of (By, value)
            text: Text to wait for
            timeout: Optional timeout override
            
        Returns:
            bool: True if text found
        """
        timeout = timeout or config.explicit_wait
        wait = WebDriverWait(self.driver, timeout)
        result = wait.until(EC.text_to_be_present_in_element(locator, text))
        logger.debug(f"Text '{text}' found in element: {locator}")
        return result
    
    def wait_for_url_contains(self, url_fragment: str, timeout: int = None) -> bool:
        """
        Wait for URL to contain specific fragment
        
        Args:
            url_fragment: URL fragment to wait for
            timeout: Optional timeout override
            
        Returns:
            bool: True if URL contains fragment
        """
        timeout = timeout or config.explicit_wait
        wait = WebDriverWait(self.driver, timeout)
        result = wait.until(EC.url_contains(url_fragment))
        logger.debug(f"URL contains: '{url_fragment}'")
        return result
    
    # ====================
    # UTILITY METHODS
    # ====================
    
    def is_element_present(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """
        Check if element is present without throwing exception
        
        Args:
            locator: Tuple of (By, value)
            timeout: Timeout for check
            
        Returns:
            bool: True if element present
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """
        Check if element is visible without throwing exception
        
        Args:
            locator: Tuple of (By, value)
            timeout: Timeout for check
            
        Returns:
            bool: True if element visible
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def scroll_to_element(self, locator: Tuple[str, str]):
        """
        Scroll element into view
        
        Args:
            locator: Tuple of (By, value)
        """
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Brief pause for scroll animation
        logger.debug(f"Scrolled to element: {locator}")
    
    def hover_over_element(self, locator: Tuple[str, str]):
        """
        Hover mouse over element
        
        Args:
            locator: Tuple of (By, value)
        """
        element = self.find_element(locator)
        self.actions.move_to_element(element).perform()
        logger.debug(f"Hovered over element: {locator}")
    
    def switch_to_frame(self, locator: Tuple[str, str] = None, frame_index: int = None):
        """
        Switch to iframe
        
        Args:
            locator: Frame element locator
            frame_index: Frame index
        """
        if locator:
            frame_element = self.find_element(locator)
            self.driver.switch_to.frame(frame_element)
        elif frame_index is not None:
            self.driver.switch_to.frame(frame_index)
        
        logger.debug(f"Switched to frame: {locator or frame_index}")
    
    def switch_to_default_content(self):
        """Switch back to main content from iframe"""
        self.driver.switch_to.default_content()
        logger.debug("Switched to default content")
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        url = self.driver.current_url
        logger.debug(f"Current URL: {url}")
        return url
    
    def get_page_title(self) -> str:
        """Get current page title"""
        title = self.driver.title
        logger.debug(f"Page title: {title}")
        return title
    
    def refresh_page(self):
        """Refresh current page"""
        self.driver.refresh()
        logger.debug("Page refreshed")
    
    def navigate_back(self):
        """Navigate back in browser history"""
        self.driver.back()
        logger.debug("Navigated back")
    
    def navigate_forward(self):
        """Navigate forward in browser history"""
        self.driver.forward()
        logger.debug("Navigated forward")
    
    def execute_javascript(self, script: str, *args):
        """
        Execute JavaScript code
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to script
            
        Returns:
            Any: Script execution result
        """
        result = self.driver.execute_script(script, *args)
        logger.debug(f"JavaScript executed: {script[:50]}...")
        return result
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        Take screenshot of current page
        
        Args:
            filename: Optional filename
            
        Returns:
            str: Screenshot file path
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = filename or f"screenshot_{timestamp}.png"
        
        import os
        os.makedirs(config.screenshots_dir, exist_ok=True)
        filepath = os.path.join(config.screenshots_dir, filename)
        
        self.driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath