"""
Pytest Configuration and Fixtures
Global test configuration for OpenCart test framework
Author: Lucas Maidana
"""

import os
import pytest
import time
from datetime import datetime
from typing import Generator
from selenium import webdriver

from config.settings import config, TestEnvironments
from utils.driver_manager import DriverManager, get_driver, quit_driver
from loguru import logger


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--browser", 
        action="store", 
        default="chrome",
        help="Browser to run tests on: chrome, firefox, edge"
    )
    parser.addoption(
        "--base-url",
        action="store", 
        default=config.base_url,
        help="Base URL for OpenCart application"
    )
    parser.addoption(
        "--environment",
        action="store",
        default="LOCAL",
        help="Test environment: LOCAL, DOCKER, STAGING"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Run browsers in headless mode"
    )
    parser.addoption(
        "--slow",
        action="store_true", 
        help="Run slow tests"
    )
    parser.addoption(
        "--smoke-only",
        action="store_true",
        help="Run only smoke tests"
    )


def pytest_configure(config_obj):
    """Configure pytest environment"""
    # Set environment variables from command line options
    os.environ['BROWSER'] = config_obj.getoption('--browser')
    os.environ['BASE_URL'] = config_obj.getoption('--base-url')
    os.environ['TEST_ENVIRONMENT'] = config_obj.getoption('--environment')
    
    if config_obj.getoption('--headless'):
        os.environ['HEADLESS'] = 'true'
    
    # Create report directories
    os.makedirs(config.reports_dir, exist_ok=True)
    os.makedirs(config.screenshots_dir, exist_ok=True)
    
    # Configure logging
    logger.add(
        f"{config.reports_dir}/test_execution.log",
        rotation="10 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    
    logger.info("=== Test Execution Started ===")
    logger.info(f"Browser: {os.environ.get('BROWSER', 'chrome')}")
    logger.info(f"Base URL: {os.environ.get('BASE_URL', config.base_url)}")
    logger.info(f"Environment: {os.environ.get('TEST_ENVIRONMENT', 'LOCAL')}")


def pytest_collection_modifyitems(config_obj, items):
    """Modify test collection based on command line options"""
    if config_obj.getoption("--smoke-only"):
        # Run only smoke tests
        selected_items = []
        for item in items:
            if "smoke" in item.keywords:
                selected_items.append(item)
        items[:] = selected_items
    
    if not config_obj.getoption("--slow"):
        # Skip slow tests unless explicitly requested
        skip_slow = pytest.mark.skip(reason="Slow test skipped (use --slow to run)")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def test_config():
    """
    Session-scoped test configuration
    
    Returns:
        dict: Test configuration
    """
    env_config = TestEnvironments.get_environment(
        os.environ.get('TEST_ENVIRONMENT', 'LOCAL')
    )
    
    test_config = {
        'base_url': os.environ.get('BASE_URL', env_config['base_url']),
        'admin_url': os.environ.get('ADMIN_URL', env_config['admin_url']),
        'browser': os.environ.get('BROWSER', 'chrome'),
        'headless': os.environ.get('HEADLESS', 'false').lower() == 'true',
        'environment': os.environ.get('TEST_ENVIRONMENT', 'LOCAL')
    }
    
    logger.info(f"Test configuration: {test_config}")
    return test_config


@pytest.fixture(scope="function")
def driver(test_config) -> Generator[webdriver.Remote, None, None]:
    """
    Function-scoped WebDriver fixture
    
    Args:
        test_config: Test configuration from session fixture
        
    Yields:
        webdriver.Remote: WebDriver instance
    """
    browser = test_config['browser']
    driver_instance = None
    
    try:
        # Create driver instance
        driver_manager = DriverManager(browser)
        driver_instance = driver_manager.create_driver()
        
        logger.info(f"WebDriver created for test: {browser}")
        yield driver_instance
        
    except Exception as e:
        logger.error(f"Failed to create WebDriver: {e}")
        raise
    
    finally:
        # Cleanup
        if driver_instance:
            try:
                driver_manager.quit_driver()
                logger.info("WebDriver cleaned up after test")
            except Exception as e:
                logger.warning(f"Error during WebDriver cleanup: {e}")


@pytest.fixture(scope="class")
def class_driver(test_config) -> Generator[webdriver.Remote, None, None]:
    """
    Class-scoped WebDriver fixture for test classes that need persistent driver
    
    Args:
        test_config: Test configuration from session fixture
        
    Yields:
        webdriver.Remote: WebDriver instance
    """
    browser = test_config['browser']
    driver_instance = None
    
    try:
        driver_manager = DriverManager(browser)
        driver_instance = driver_manager.create_driver()
        
        logger.info(f"Class-scoped WebDriver created: {browser}")
        yield driver_instance
        
    finally:
        if driver_instance:
            driver_manager.quit_driver()
            logger.info("Class-scoped WebDriver cleaned up")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Create test report and handle failure screenshots
    
    Args:
        item: Test item
        call: Test call info
    """
    outcome = yield
    report = outcome.get_result()
    
    # Add test metadata
    report.test_name = item.name
    report.test_file = item.fspath
    report.test_markers = [marker.name for marker in item.iter_markers()]
    
    # Handle test failure
    if report.when == "call" and report.failed:
        logger.error(f"Test failed: {item.name}")
        
        # Take screenshot on failure if driver is available
        if config.screenshot_on_failure:
            try:
                # Try to get driver from test fixtures
                if hasattr(item, "funcargs") and "driver" in item.funcargs:
                    driver_instance = item.funcargs["driver"]
                elif hasattr(item, "funcargs") and "class_driver" in item.funcargs:
                    driver_instance = item.funcargs["class_driver"]
                else:
                    # Try to get driver from driver manager
                    driver_manager = DriverManager()
                    driver_instance = driver_manager.driver
                
                if driver_instance:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_name = f"FAILED_{item.name}_{timestamp}.png"
                    screenshot_path = os.path.join(config.screenshots_dir, screenshot_name)
                    
                    driver_instance.save_screenshot(screenshot_path)
                    logger.info(f"Failure screenshot saved: {screenshot_path}")
                    
                    # Add screenshot to report
                    report.screenshot_path = screenshot_path
                
            except Exception as e:
                logger.warning(f"Could not take failure screenshot: {e}")
    
    # Log test results
    if report.when == "call":
        duration = report.duration
        if report.passed:
            logger.info(f"✅ Test passed: {item.name} ({duration:.2f}s)")
        elif report.failed:
            logger.error(f"❌ Test failed: {item.name} ({duration:.2f}s)")
        elif report.skipped:
            logger.warning(f"⏭️  Test skipped: {item.name}")


@pytest.fixture(autouse=True)
def test_timing():
    """Auto-used fixture to log test timing"""
    start_time = time.time()
    yield
    end_time = time.time()
    duration = end_time - start_time
    logger.debug(f"Test execution time: {duration:.2f} seconds")


@pytest.fixture
def wait_time():
    """Fixture providing standard wait times for tests"""
    return {
        'short': 2,
        'medium': 5,
        'long': 10,
        'extra_long': 30
    }


@pytest.fixture
def test_data():
    """Fixture providing test data"""
    from faker import Faker
    fake = Faker()
    
    return {
        'user': {
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'email': fake.email(),
            'telephone': fake.phone_number()[:15],
            'password': 'TestPassword123!',
        },
        'product': {
            'name': 'Test Product',
            'model': 'TEST-001',
            'price': '99.99'
        },
        'address': {
            'address': fake.street_address(),
            'city': fake.city(),
            'postcode': fake.zipcode(),
            'country': 'United States',
            'region': 'Florida'
        }
    }


def pytest_sessionstart(session):
    """Called after Session object has been created"""
    logger.info("=== Test Session Started ===")
    logger.info(f"Python version: {session.config.getini('python_version')}")
    logger.info(f"Pytest version: {pytest.__version__}")


def pytest_sessionfinish(session, exitstatus):
    """Called after test session finishes"""
    # Cleanup all drivers
    DriverManager.cleanup_all_drivers()
    
    # Log session summary
    if hasattr(session, 'testscollected'):
        logger.info(f"Tests collected: {session.testscollected}")
    
    if hasattr(session, 'testsfailed'):
        logger.info(f"Tests failed: {session.testsfailed}")
    
    logger.info(f"Session exit status: {exitstatus}")
    logger.info("=== Test Session Finished ===")


# Custom markers for test organization
pytest_plugins = [
    "pytest_html",
    "pytest_json_report",
]