"""
Test Configuration Settings
Centralized configuration management for the OpenCart test framework
Author: Lucas Maidana
"""

import os
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class BrowserConfig:
    """Browser configuration settings"""
    name: str
    headless: bool = True
    window_size: str = "1920,1080"
    download_directory: str = "./downloads"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'headless': self.headless,
            'window_size': self.window_size,
            'download_directory': self.download_directory
        }


@dataclass 
class TestConfig:
    """Main test configuration"""
    # Application URLs
    base_url: str = os.getenv('OPENCART_BASE_URL', 'http://localhost/opencart')
    admin_url: str = os.getenv('OPENCART_ADMIN_URL', 'http://localhost/opencart/admin')
    
    # Database Configuration
    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_name: str = os.getenv('DB_NAME', 'opencart')
    db_user: str = os.getenv('DB_USER', 'opencart_user')
    db_password: str = os.getenv('DB_PASSWORD', 'password')
    
    # Test Data Configuration
    test_data_file: str = './test_data/test_data.yaml'
    
    # Timeouts (in seconds)
    implicit_wait: int = 10
    explicit_wait: int = 20
    page_load_timeout: int = 30
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: int = 1
    
    # Screenshot and Reporting
    screenshot_on_failure: bool = True
    video_recording: bool = False
    screenshots_dir: str = './reports/screenshots'
    videos_dir: str = './reports/videos'
    reports_dir: str = './reports'
    
    # Parallel Execution
    parallel_tests: bool = True
    max_workers: int = 4
    
    # Browser Configurations
    browsers: Dict[str, BrowserConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.browsers:
            self.browsers = {
                'chrome': BrowserConfig('chrome'),
                'firefox': BrowserConfig('firefox'),
                'edge': BrowserConfig('edge')
            }
    
    @property
    def current_browser(self) -> str:
        """Get current browser from environment or default to chrome"""
        return os.getenv('BROWSER', 'chrome').lower()
    
    @property
    def is_ci_environment(self) -> bool:
        """Check if running in CI environment"""
        return os.getenv('CI', 'false').lower() == 'true'
    
    @property
    def log_level(self) -> str:
        """Get log level from environment or default to INFO"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()


@dataclass
class AdminTestData:
    """Admin test data configuration"""
    username: str = os.getenv('ADMIN_USERNAME', 'admin')
    password: str = os.getenv('ADMIN_PASSWORD', 'admin123')
    email: str = os.getenv('ADMIN_EMAIL', 'admin@opencart.local')


@dataclass
class CustomerTestData:
    """Customer test data configuration"""
    firstname: str = 'Test'
    lastname: str = 'Customer'
    email: str = 'test.customer@example.com'
    password: str = 'TestPassword123!'
    telephone: str = '+1234567890'
    address: str = '123 Test Street'
    city: str = 'Test City'
    postcode: str = '12345'
    country: str = 'United States'
    region: str = 'Florida'


# Global configuration instance
config = TestConfig()
admin_data = AdminTestData()
customer_data = CustomerTestData()


class TestEnvironments:
    """Environment-specific configurations"""
    
    LOCAL = {
        'base_url': 'http://localhost/opencart',
        'admin_url': 'http://localhost/opencart/admin',
        'db_host': 'localhost'
    }
    
    DOCKER = {
        'base_url': 'http://opencart:80',
        'admin_url': 'http://opencart:80/admin',
        'db_host': 'opencart-db'
    }
    
    STAGING = {
        'base_url': 'https://staging.opencart.example.com',
        'admin_url': 'https://staging.opencart.example.com/admin',
        'db_host': 'staging-db.example.com'
    }
    
    @classmethod
    def get_environment(cls, env_name: str = None) -> Dict[str, str]:
        """Get environment configuration by name"""
        env_name = env_name or os.getenv('TEST_ENVIRONMENT', 'LOCAL')
        return getattr(cls, env_name.upper(), cls.LOCAL)


# API Configuration
API_CONFIG = {
    'timeout': 30,
    'retry_count': 3,
    'base_headers': {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
}

# Email Configuration for notifications
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'email_user': os.getenv('EMAIL_USER', ''),
    'email_password': os.getenv('EMAIL_PASSWORD', ''),
    'enable_notifications': os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
}

# Performance Testing Configuration
PERFORMANCE_CONFIG = {
    'max_response_time': 3.0,  # seconds
    'max_page_load_time': 5.0,  # seconds
    'memory_threshold': 100,  # MB
    'cpu_threshold': 80  # percentage
}

# Security Testing Configuration
SECURITY_CONFIG = {
    'sql_injection_payloads': [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --"
    ],
    'xss_payloads': [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>"
    ]
}