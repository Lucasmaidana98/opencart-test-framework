"""
Shopping Cart Page Object Model
Shopping cart functionality for OpenCart frontend
Author: Lucas Maidana
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from loguru import logger


class CartPage(BasePage):
    """
    Shopping cart page object model for OpenCart frontend
    Handles cart operations, quantity updates, and checkout navigation
    """
    
    # Page elements
    PAGE_TITLE = (By.CSS_SELECTOR, "h1")
    CART_TABLE = (By.CSS_SELECTOR, ".table.table-bordered")
    
    # Cart items
    CART_ITEMS = (By.CSS_SELECTOR, ".table tbody tr")
    ITEM_IMAGE = (By.CSS_SELECTOR, "td:nth-child(1) img")
    ITEM_NAME = (By.CSS_SELECTOR, "td:nth-child(2) a")
    ITEM_MODEL = (By.CSS_SELECTOR, "td:nth-child(3)")
    ITEM_QUANTITY_INPUT = (By.CSS_SELECTOR, "td:nth-child(4) input[name^='quantity']")
    ITEM_UNIT_PRICE = (By.CSS_SELECTOR, "td:nth-child(5)")
    ITEM_TOTAL_PRICE = (By.CSS_SELECTOR, "td:nth-child(6)")
    REMOVE_ITEM_BUTTON = (By.CSS_SELECTOR, "td:nth-child(7) button")
    UPDATE_QUANTITY_BUTTON = (By.CSS_SELECTOR, "button[title='Update']")
    
    # Cart totals
    CART_TOTALS_SECTION = (By.CSS_SELECTOR, ".col-sm-4.offset-sm-8")
    SUBTOTAL = (By.CSS_SELECTOR, "tr:contains('Sub-Total') td:last-child")
    SHIPPING_COST = (By.CSS_SELECTOR, "tr:contains('Shipping') td:last-child")
    TAX_AMOUNT = (By.CSS_SELECTOR, "tr:contains('Tax') td:last-child")
    TOTAL_AMOUNT = (By.CSS_SELECTOR, "tr:contains('Total') td:last-child")
    
    # Action buttons
    CONTINUE_SHOPPING_BUTTON = (By.LINK_TEXT, "Continue Shopping")
    CHECKOUT_BUTTON = (By.LINK_TEXT, "Checkout")
    
    # Coupon section
    COUPON_SECTION = (By.ID, "collapse-coupon")
    COUPON_CODE_INPUT = (By.ID, "input-coupon")
    APPLY_COUPON_BUTTON = (By.ID, "button-coupon")
    COUPON_TOGGLE = (By.CSS_SELECTOR, "a[href='#collapse-coupon']")
    
    # Shipping estimate
    SHIPPING_SECTION = (By.ID, "collapse-shipping")
    SHIPPING_TOGGLE = (By.CSS_SELECTOR, "a[href='#collapse-shipping']")
    COUNTRY_SELECT = (By.ID, "input-country")
    REGION_SELECT = (By.ID, "input-zone")
    POSTCODE_INPUT = (By.ID, "input-postcode")
    GET_QUOTES_BUTTON = (By.ID, "button-quote")
    
    # Messages
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-danger")
    WARNING_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-warning")
    
    # Empty cart
    EMPTY_CART_MESSAGE = (By.CSS_SELECTOR, ".text-center p")
    
    def __init__(self, driver):
        """Initialize cart page"""
        super().__init__(driver)
    
    def navigate_to_cart(self, base_url: str):
        """
        Navigate to shopping cart page
        
        Args:
            base_url: Base URL of OpenCart installation
        """
        cart_url = f"{base_url}/index.php?route=checkout/cart"
        self.driver.get(cart_url)
        logger.info("Navigated to cart page")
        return self
    
    def is_cart_page_loaded(self) -> bool:
        """
        Verify cart page is loaded
        
        Returns:
            bool: True if cart page is loaded
        """
        try:
            page_title = self.get_element_text(self.PAGE_TITLE)
            is_loaded = "Shopping Cart" in page_title
            logger.info(f"Cart page loaded: {is_loaded}")
            return is_loaded
        except:
            logger.error("Failed to verify cart page load")
            return False
    
    # ====================
    # CART ITEMS MANAGEMENT
    # ====================
    
    def get_cart_items(self) -> list:
        """
        Get all cart items
        
        Returns:
            list: List of cart item elements
        """
        items = self.find_elements(self.CART_ITEMS)
        logger.info(f"Found {len(items)} items in cart")
        return items
    
    def get_cart_item_count(self) -> int:
        """
        Get number of items in cart
        
        Returns:
            int: Number of items in cart
        """
        items = self.get_cart_items()
        count = len(items)
        logger.info(f"Cart item count: {count}")
        return count
    
    def is_cart_empty(self) -> bool:
        """
        Check if cart is empty
        
        Returns:
            bool: True if cart is empty
        """
        try:
            empty_message = self.is_element_visible(self.EMPTY_CART_MESSAGE, timeout=5)
            item_count = self.get_cart_item_count()
            is_empty = empty_message or item_count == 0
            logger.info(f"Cart empty: {is_empty}")
            return is_empty
        except:
            return True
    
    def get_item_name(self, item_index: int = 0) -> str:
        """
        Get name of cart item by index
        
        Args:
            item_index: Index of item (0-based)
            
        Returns:
            str: Item name
        """
        items = self.get_cart_items()
        if item_index < len(items):
            item_row = items[item_index]
            name_element = item_row.find_element(*self.ITEM_NAME)
            name = name_element.text
            logger.info(f"Item {item_index} name: {name}")
            return name
        else:
            raise IndexError(f"Item index {item_index} out of range")
    
    def get_item_quantity(self, item_index: int = 0) -> int:
        """
        Get quantity of cart item by index
        
        Args:
            item_index: Index of item (0-based)
            
        Returns:
            int: Item quantity
        """
        items = self.get_cart_items()
        if item_index < len(items):
            item_row = items[item_index]
            quantity_input = item_row.find_element(*self.ITEM_QUANTITY_INPUT)
            quantity = int(quantity_input.get_attribute("value"))
            logger.info(f"Item {item_index} quantity: {quantity}")
            return quantity
        else:
            raise IndexError(f"Item index {item_index} out of range")
    
    def update_item_quantity(self, item_index: int, new_quantity: int):
        """
        Update quantity of cart item
        
        Args:
            item_index: Index of item (0-based)
            new_quantity: New quantity value
        """
        items = self.get_cart_items()
        if item_index < len(items):
            item_row = items[item_index]
            quantity_input = item_row.find_element(*self.ITEM_QUANTITY_INPUT)
            quantity_input.clear()
            quantity_input.send_keys(str(new_quantity))
            
            # Click update button
            update_button = item_row.find_element(*self.UPDATE_QUANTITY_BUTTON)
            update_button.click()
            
            logger.info(f"Updated item {item_index} quantity to {new_quantity}")
        else:
            raise IndexError(f"Item index {item_index} out of range")
        return self
    
    def remove_item(self, item_index: int = 0):
        """
        Remove item from cart by index
        
        Args:
            item_index: Index of item to remove (0-based)
        """
        items = self.get_cart_items()
        if item_index < len(items):
            item_row = items[item_index]
            remove_button = item_row.find_element(*self.REMOVE_ITEM_BUTTON)
            remove_button.click()
            logger.info(f"Removed item {item_index} from cart")
        else:
            raise IndexError(f"Item index {item_index} out of range")
        return self
    
    def remove_all_items(self):
        """Remove all items from cart"""
        while not self.is_cart_empty():
            self.remove_item(0)
            # Wait for page to update
            self.wait_for_element_visible((By.CSS_SELECTOR, "body"), timeout=5)
        logger.info("Removed all items from cart")
        return self
    
    # ====================
    # CART TOTALS
    # ====================
    
    def get_subtotal(self) -> str:
        """
        Get cart subtotal
        
        Returns:
            str: Subtotal amount
        """
        try:
            subtotal = self.get_element_text(self.SUBTOTAL)
            logger.info(f"Cart subtotal: {subtotal}")
            return subtotal
        except:
            return "0.00"
    
    def get_total_amount(self) -> str:
        """
        Get cart total amount
        
        Returns:
            str: Total amount
        """
        try:
            total = self.get_element_text(self.TOTAL_AMOUNT)
            logger.info(f"Cart total: {total}")
            return total
        except:
            return "0.00"
    
    def get_shipping_cost(self) -> str:
        """
        Get shipping cost
        
        Returns:
            str: Shipping cost
        """
        try:
            shipping = self.get_element_text(self.SHIPPING_COST)
            logger.info(f"Shipping cost: {shipping}")
            return shipping
        except:
            return "0.00"
    
    def get_tax_amount(self) -> str:
        """
        Get tax amount
        
        Returns:
            str: Tax amount
        """
        try:
            tax = self.get_element_text(self.TAX_AMOUNT)
            logger.info(f"Tax amount: {tax}")
            return tax
        except:
            return "0.00"
    
    # ====================
    # COUPON FUNCTIONALITY
    # ====================
    
    def expand_coupon_section(self):
        """Expand coupon code section"""
        if not self.is_element_visible(self.COUPON_CODE_INPUT, timeout=2):
            self.click_element(self.COUPON_TOGGLE)
            logger.info("Expanded coupon section")
        return self
    
    def apply_coupon(self, coupon_code: str):
        """
        Apply coupon code
        
        Args:
            coupon_code: Coupon code to apply
        """
        self.expand_coupon_section()
        self.enter_text(self.COUPON_CODE_INPUT, coupon_code)
        self.click_element(self.APPLY_COUPON_BUTTON)
        logger.info(f"Applied coupon code: {coupon_code}")
        return self
    
    # ====================
    # SHIPPING ESTIMATION
    # ====================
    
    def expand_shipping_section(self):
        """Expand shipping estimation section"""
        if not self.is_element_visible(self.COUNTRY_SELECT, timeout=2):
            self.click_element(self.SHIPPING_TOGGLE)
            logger.info("Expanded shipping section")
        return self
    
    def estimate_shipping(self, country: str, region: str = "", postcode: str = ""):
        """
        Estimate shipping cost
        
        Args:
            country: Country name
            region: State/region name
            postcode: Postal code
        """
        self.expand_shipping_section()
        
        # Select country
        self.select_dropdown_by_text(self.COUNTRY_SELECT, country)
        
        # Select region if provided
        if region:
            self.select_dropdown_by_text(self.REGION_SELECT, region)
        
        # Enter postcode if provided
        if postcode:
            self.enter_text(self.POSTCODE_INPUT, postcode)
        
        # Get quotes
        self.click_element(self.GET_QUOTES_BUTTON)
        
        logger.info(f"Estimated shipping for: {country}, {region}, {postcode}")
        return self
    
    # ====================
    # NAVIGATION
    # ====================
    
    def continue_shopping(self):
        """Continue shopping - return to store"""
        self.click_element(self.CONTINUE_SHOPPING_BUTTON)
        logger.info("Continued shopping")
        return self
    
    def proceed_to_checkout(self):
        """Proceed to checkout page"""
        self.click_element(self.CHECKOUT_BUTTON)
        logger.info("Proceeded to checkout")
        return self
    
    # ====================
    # MESSAGE HANDLING
    # ====================
    
    def get_success_message(self) -> str:
        """Get success message"""
        try:
            return self.get_element_text(self.SUCCESS_MESSAGE)
        except:
            return ""
    
    def get_error_message(self) -> str:
        """Get error message"""
        try:
            return self.get_element_text(self.ERROR_MESSAGE)
        except:
            return ""
    
    def get_warning_message(self) -> str:
        """Get warning message"""
        try:
            return self.get_element_text(self.WARNING_MESSAGE)
        except:
            return ""
    
    def is_success_message_displayed(self) -> bool:
        """Check if success message is displayed"""
        return self.is_element_visible(self.SUCCESS_MESSAGE, timeout=5)
    
    def is_error_message_displayed(self) -> bool:
        """Check if error message is displayed"""
        return self.is_element_visible(self.ERROR_MESSAGE, timeout=5)
    
    # ====================
    # VALIDATION METHODS
    # ====================
    
    def validate_item_in_cart(self, product_name: str) -> bool:
        """
        Validate that specific product is in cart
        
        Args:
            product_name: Name of product to validate
            
        Returns:
            bool: True if product is in cart
        """
        items = self.get_cart_items()
        for i in range(len(items)):
            item_name = self.get_item_name(i)
            if product_name.lower() in item_name.lower():
                logger.info(f"Product '{product_name}' found in cart")
                return True
        
        logger.info(f"Product '{product_name}' not found in cart")
        return False
    
    def get_cart_summary(self) -> dict:
        """
        Get complete cart summary
        
        Returns:
            dict: Cart summary with items and totals
        """
        summary = {
            'item_count': self.get_cart_item_count(),
            'items': [],
            'subtotal': self.get_subtotal(),
            'shipping': self.get_shipping_cost(),
            'tax': self.get_tax_amount(),
            'total': self.get_total_amount(),
            'is_empty': self.is_cart_empty()
        }
        
        # Get item details
        for i in range(summary['item_count']):
            item = {
                'name': self.get_item_name(i),
                'quantity': self.get_item_quantity(i)
            }
            summary['items'].append(item)
        
        logger.info(f"Cart summary: {summary}")
        return summary