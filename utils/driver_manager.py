"""
WebDriver Manager
Professional WebDriver management with support for multiple browsers
and execution environments (local, CI/CD, Docker)
Author: Lucas Maidana
"""

import os
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from loguru import logger

from config.settings import config


class DriverManager:
    """
    Advanced WebDriver manager supporting multiple browsers and execution environments
    Implements singleton pattern for efficient resource management
    """
    
    _instances = {}
    
    def __new__(cls, browser_name: str = None):
        """Singleton implementation with browser-specific instances"""
        browser_name = browser_name or config.current_browser
        if browser_name not in cls._instances:
            cls._instances[browser_name] = super().__new__(cls)
        return cls._instances[browser_name]
    
    def __init__(self, browser_name: str = None):
        """Initialize driver manager for specific browser"""
        if not hasattr(self, 'initialized'):
            self.browser_name = browser_name or config.current_browser
            self.driver: Optional[webdriver.Remote] = None
            self.initialized = True
            logger.info(f"DriverManager initialized for {self.browser_name}")
    
    def create_driver(self) -> webdriver.Remote:
        """
        Create and configure WebDriver instance based on browser type and environment
        
        Returns:
            webdriver.Remote: Configured WebDriver instance
        """
        try:
            if self.browser_name.lower() == 'chrome':
                self.driver = self._create_chrome_driver()
            elif self.browser_name.lower() == 'firefox':
                self.driver = self._create_firefox_driver()
            elif self.browser_name.lower() == 'edge':
                self.driver = self._create_edge_driver()
            else:
                raise ValueError(f"Unsupported browser: {self.browser_name}")
            
            self._configure_driver()
            logger.info(f"WebDriver created successfully: {self.browser_name}")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to create WebDriver for {self.browser_name}: {str(e)}")
            raise
    
    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver with optimized options"""
        options = ChromeOptions()
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')  # Remove for JS-heavy tests
        
        # Memory optimizations
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # CI/CD optimizations
        if config.is_ci_environment:
            options.add_argument('--headless=new')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--silent')
        
        # Browser configuration
        browser_config = config.browsers.get('chrome')
        if browser_config.headless:
            options.add_argument('--headless=new')
        
        options.add_argument(f'--window-size={browser_config.window_size}')
        
        # Download configuration
        prefs = {
            'download.default_directory': os.path.abspath(browser_config.download_directory),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        }
        options.add_experimental_option('prefs', prefs)
        
        # Security configurations
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Create service
        service = ChromeService(ChromeDriverManager().install())
        
        return webdriver.Chrome(service=service, options=options)
    
    def _create_firefox_driver(self) -> webdriver.Firefox:
        """Create Firefox WebDriver with optimized options"""
        options = FirefoxOptions()
        
        # Performance optimizations
        options.set_preference('dom.webnotifications.enabled', False)
        options.set_preference('media.volume_scale', '0.0')
        options.set_preference('dom.push.enabled', False)
        
        # CI/CD optimizations
        browser_config = config.browsers.get('firefox')
        if browser_config.headless or config.is_ci_environment:
            options.add_argument('--headless')
        
        # Download configuration
        options.set_preference('browser.download.folderList', 2)
        options.set_preference('browser.download.dir', 
                             os.path.abspath(browser_config.download_directory))
        options.set_preference('browser.helperApps.neverAsk.saveToDisk', 
                             'application/octet-stream')
        
        # Create service
        service = FirefoxService(GeckoDriverManager().install())
        
        return webdriver.Firefox(service=service, options=options)
    
    def _create_edge_driver(self) -> webdriver.Edge:
        """Create Edge WebDriver with optimized options"""
        options = EdgeOptions()
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        
        # CI/CD optimizations
        browser_config = config.browsers.get('edge')
        if browser_config.headless or config.is_ci_environment:
            options.add_argument('--headless')
        
        options.add_argument(f'--window-size={browser_config.window_size}')
        
        # Create service
        service = EdgeService(EdgeChromiumDriverManager().install())
        
        return webdriver.Edge(service=service, options=options)
    
    def _configure_driver(self):
        """Configure WebDriver with timeouts and other settings"""
        if self.driver:
            # Set timeouts
            self.driver.implicitly_wait(config.implicit_wait)
            self.driver.set_page_load_timeout(config.page_load_timeout)
            
            # Maximize window if not headless
            if not config.browsers.get(self.browser_name).headless:
                self.driver.maximize_window()
            
            logger.info(f"WebDriver configured with timeouts: "
                       f"implicit={config.implicit_wait}s, "
                       f"page_load={config.page_load_timeout}s")
    
    def get_driver(self) -> webdriver.Remote:
        """
        Get current WebDriver instance or create new one if doesn't exist
        
        Returns:
            webdriver.Remote: WebDriver instance
        """
        if self.driver is None:
            self.driver = self.create_driver()
        return self.driver
    
    def quit_driver(self):
        """Safely quit WebDriver and clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info(f"WebDriver quit successfully: {self.browser_name}")
            except Exception as e:
                logger.warning(f"Error quitting WebDriver: {str(e)}")
            finally:
                self.driver = None
    
    def restart_driver(self) -> webdriver.Remote:
        """Restart WebDriver (useful for recovering from crashes)"""
        logger.info(f"Restarting WebDriver: {self.browser_name}")
        self.quit_driver()
        time.sleep(2)  # Wait for cleanup
        return self.create_driver()
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        Take screenshot of current page
        
        Args:
            filename: Optional filename for screenshot
            
        Returns:
            str: Path to saved screenshot
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = filename or f"screenshot_{timestamp}.png"
        
        # Ensure screenshots directory exists
        os.makedirs(config.screenshots_dir, exist_ok=True)
        
        filepath = os.path.join(config.screenshots_dir, filename)
        self.driver.save_screenshot(filepath)
        
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
    
    @classmethod
    def cleanup_all_drivers(cls):
        """Clean up all WebDriver instances"""
        for browser_name, instance in cls._instances.items():
            if hasattr(instance, 'driver') and instance.driver:
                instance.quit_driver()
        cls._instances.clear()
        logger.info("All WebDriver instances cleaned up")


# Convenience functions for common operations
def get_driver(browser_name: str = None) -> webdriver.Remote:
    """Get WebDriver instance for specified browser"""
    manager = DriverManager(browser_name)
    return manager.get_driver()

def quit_driver(browser_name: str = None):
    """Quit WebDriver for specified browser"""
    manager = DriverManager(browser_name)
    manager.quit_driver()

def take_screenshot(filename: str = None, browser_name: str = None) -> str:
    """Take screenshot with specified browser"""
    manager = DriverManager(browser_name)
    return manager.take_screenshot(filename)