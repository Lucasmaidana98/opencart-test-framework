"""
Home Page Object Model
Frontend home page interactions for OpenCart
Author: Lucas Maidana
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from loguru import logger


class HomePage(BasePage):
    """
    Home page object model for OpenCart frontend
    Handles navigation, search, and main page interactions
    """
    
    # Page locators
    LOGO = (By.CSS_SELECTOR, "#logo a")
    SEARCH_INPUT = (By.NAME, "search")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".btn.btn-light.btn-lg")
    CART_BUTTON = (By.ID, "header-cart")
    CART_TOTAL = (By.CSS_SELECTOR, "#header-cart .btn")
    ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, ".nav-item.dropdown")
    LOGIN_LINK = (By.LINK_TEXT, "Login")
    REGISTER_LINK = (By.LINK_TEXT, "Register")
    LOGOUT_LINK = (By.LINK_TEXT, "Logout")
    MY_ACCOUNT_LINK = (By.LINK_TEXT, "My Account")
    WISHLIST_LINK = (By.ID, "wishlist-total")
    
    # Navigation menu
    MENU_NAVBAR = (By.CSS_SELECTOR, ".navbar-nav")
    DESKTOPS_MENU = (By.LINK_TEXT, "Desktops")
    LAPTOPS_MENU = (By.LINK_TEXT, "Laptops & Notebooks")
    COMPONENTS_MENU = (By.LINK_TEXT, "Components")
    TABLETS_MENU = (By.LINK_TEXT, "Tablets")
    SOFTWARE_MENU = (By.LINK_TEXT, "Software")
    PHONES_MENU = (By.LINK_TEXT, "Phones & PDAs")
    CAMERAS_MENU = (By.LINK_TEXT, "Cameras")
    
    # Featured products
    FEATURED_PRODUCTS = (By.CSS_SELECTOR, ".product-thumb")
    PRODUCT_TITLES = (By.CSS_SELECTOR, ".product-thumb h4 a")
    PRODUCT_PRICES = (By.CSS_SELECTOR, ".product-thumb .price")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, ".product-thumb button[onclick*='cart.add']")
    ADD_TO_WISHLIST_BUTTONS = (By.CSS_SELECTOR, ".product-thumb button[onclick*='wishlist.add']")
    COMPARE_BUTTONS = (By.CSS_SELECTOR, ".product-thumb button[onclick*='compare.add']")
    
    # Footer links
    FOOTER = (By.TAG_NAME, "footer")
    ABOUT_US_LINK = (By.LINK_TEXT, "About Us")
    CONTACT_US_LINK = (By.LINK_TEXT, "Contact Us")
    RETURNS_LINK = (By.LINK_TEXT, "Returns")
    SITE_MAP_LINK = (By.LINK_TEXT, "Site Map")
    
    # Alert messages
    SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert.alert-success")
    ERROR_ALERT = (By.CSS_SELECTOR, ".alert.alert-danger")
    WARNING_ALERT = (By.CSS_SELECTOR, ".alert.alert-warning")
    INFO_ALERT = (By.CSS_SELECTOR, ".alert.alert-info")
    
    def __init__(self, driver):
        """Initialize home page"""
        super().__init__(driver)
        self.url = f"{self.driver.current_url.split('/')[0]}//{self.driver.current_url.split('/')[2]}"
    
    def navigate_to_home(self):
        """Navigate to home page"""
        self.driver.get(self.url)
        logger.info("Navigated to home page")
        return self
    
    def click_logo(self):
        """Click on site logo to return to home"""
        self.click_element(self.LOGO)
        logger.info("Clicked on logo")
        return self
    
    # ====================
    # SEARCH FUNCTIONALITY
    # ====================
    
    def search_product(self, search_term: str):
        """
        Search for a product using the search box
        
        Args:
            search_term: Product name or keyword to search
        """
        self.enter_text(self.SEARCH_INPUT, search_term)
        self.click_element(self.SEARCH_BUTTON)
        logger.info(f"Searched for product: '{search_term}'")
        return self
    
    def get_search_input_value(self) -> str:
        """Get current value in search input"""
        return self.get_element_attribute(self.SEARCH_INPUT, "value")
    
    # ====================
    # ACCOUNT NAVIGATION
    # ====================
    
    def open_account_dropdown(self):
        """Open account dropdown menu"""
        self.click_element(self.ACCOUNT_DROPDOWN)
        logger.info("Opened account dropdown")
        return self
    
    def click_login(self):
        """Navigate to login page"""
        self.open_account_dropdown()
        self.click_element(self.LOGIN_LINK)
        logger.info("Navigated to login page")
        return self
    
    def click_register(self):
        """Navigate to registration page"""
        self.open_account_dropdown()
        self.click_element(self.REGISTER_LINK)
        logger.info("Navigated to registration page")
        return self
    
    def click_logout(self):
        """Logout from account"""
        self.open_account_dropdown()
        self.click_element(self.LOGOUT_LINK)
        logger.info("Logged out from account")
        return self
    
    def click_my_account(self):
        """Navigate to my account page"""
        self.open_account_dropdown()
        self.click_element(self.MY_ACCOUNT_LINK)
        logger.info("Navigated to my account page")
        return self
    
    def is_user_logged_in(self) -> bool:
        """
        Check if user is currently logged in
        
        Returns:
            bool: True if user is logged in
        """
        self.open_account_dropdown()
        is_logged_in = self.is_element_visible(self.LOGOUT_LINK, timeout=2)
        logger.info(f"User logged in status: {is_logged_in}")
        return is_logged_in
    
    # ====================
    # CART FUNCTIONALITY
    # ====================
    
    def click_cart(self):
        """Open shopping cart"""
        self.click_element(self.CART_BUTTON)
        logger.info("Opened shopping cart")
        return self
    
    def get_cart_total(self) -> str:
        """
        Get cart total amount
        
        Returns:
            str: Cart total text
        """
        total_text = self.get_element_text(self.CART_TOTAL)
        logger.info(f"Cart total: {total_text}")
        return total_text
    
    def get_cart_item_count(self) -> int:
        """
        Extract item count from cart total
        
        Returns:
            int: Number of items in cart
        """
        total_text = self.get_cart_total()
        # Extract number from text like "2 item(s) - $202.00"
        try:
            count = int(total_text.split()[0])
            logger.info(f"Cart item count: {count}")
            return count
        except (ValueError, IndexError):
            logger.warning(f"Could not parse cart count from: {total_text}")
            return 0
    
    # ====================
    # PRODUCT INTERACTIONS
    # ====================
    
    def get_featured_products(self) -> list:
        """
        Get list of featured products on home page
        
        Returns:
            list: List of product elements
        """
        products = self.find_elements(self.FEATURED_PRODUCTS)
        logger.info(f"Found {len(products)} featured products")
        return products
    
    def get_product_titles(self) -> list:
        """
        Get titles of all featured products
        
        Returns:
            list: List of product titles
        """
        title_elements = self.find_elements(self.PRODUCT_TITLES)
        titles = [element.text for element in title_elements]
        logger.info(f"Product titles: {titles}")
        return titles
    
    def add_featured_product_to_cart(self, product_index: int = 0):
        """
        Add featured product to cart by index
        
        Args:
            product_index: Index of product to add (0-based)
        """
        add_to_cart_buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        if product_index < len(add_to_cart_buttons):
            add_to_cart_buttons[product_index].click()
            logger.info(f"Added featured product {product_index} to cart")
        else:
            raise IndexError(f"Product index {product_index} out of range")
        return self
    
    def add_featured_product_to_wishlist(self, product_index: int = 0):
        """
        Add featured product to wishlist by index
        
        Args:
            product_index: Index of product to add (0-based)
        """
        wishlist_buttons = self.find_elements(self.ADD_TO_WISHLIST_BUTTONS)
        if product_index < len(wishlist_buttons):
            wishlist_buttons[product_index].click()
            logger.info(f"Added featured product {product_index} to wishlist")
        else:
            raise IndexError(f"Product index {product_index} out of range")
        return self
    
    def click_product_title(self, product_index: int = 0):
        """
        Click on product title to view product details
        
        Args:
            product_index: Index of product to click (0-based)
        """
        product_titles = self.find_elements(self.PRODUCT_TITLES)
        if product_index < len(product_titles):
            product_titles[product_index].click()
            logger.info(f"Clicked on product title {product_index}")
        else:
            raise IndexError(f"Product index {product_index} out of range")
        return self
    
    # ====================
    # NAVIGATION MENU
    # ====================
    
    def hover_menu_item(self, menu_locator: tuple):
        """
        Hover over menu item to show dropdown
        
        Args:
            menu_locator: Locator for menu item
        """
        self.hover_over_element(menu_locator)
        logger.info(f"Hovered over menu item: {menu_locator}")
        return self
    
    def click_desktops_menu(self):
        """Click on Desktops menu"""
        self.click_element(self.DESKTOPS_MENU)
        logger.info("Clicked Desktops menu")
        return self
    
    def click_laptops_menu(self):
        """Click on Laptops menu"""
        self.click_element(self.LAPTOPS_MENU)
        logger.info("Clicked Laptops menu")
        return self
    
    # ====================
    # ALERT HANDLING
    # ====================
    
    def get_success_message(self) -> str:
        """
        Get success alert message
        
        Returns:
            str: Success message text
        """
        try:
            message = self.get_element_text(self.SUCCESS_ALERT)
            logger.info(f"Success message: {message}")
            return message
        except:
            return ""
    
    def get_error_message(self) -> str:
        """
        Get error alert message
        
        Returns:
            str: Error message text
        """
        try:
            message = self.get_element_text(self.ERROR_ALERT)
            logger.info(f"Error message: {message}")
            return message
        except:
            return ""
    
    def is_success_message_displayed(self) -> bool:
        """Check if success message is displayed"""
        return self.is_element_visible(self.SUCCESS_ALERT, timeout=5)
    
    def is_error_message_displayed(self) -> bool:
        """Check if error message is displayed"""
        return self.is_element_visible(self.ERROR_ALERT, timeout=5)
    
    # ====================
    # PAGE VALIDATION
    # ====================
    
    def is_home_page_loaded(self) -> bool:
        """
        Verify that home page is properly loaded
        
        Returns:
            bool: True if home page is loaded
        """
        try:
            # Check for key elements that should be present on home page
            logo_present = self.is_element_visible(self.LOGO, timeout=10)
            search_present = self.is_element_visible(self.SEARCH_INPUT, timeout=5)
            cart_present = self.is_element_visible(self.CART_BUTTON, timeout=5)
            
            is_loaded = logo_present and search_present and cart_present
            logger.info(f"Home page loaded status: {is_loaded}")
            return is_loaded
        except:
            logger.error("Failed to verify home page load status")
            return False