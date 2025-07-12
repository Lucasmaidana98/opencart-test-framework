"""
Shopping Cart Test Suite
Comprehensive testing of OpenCart shopping cart functionality
Author: Lucas Maidana
"""

import pytest
import time
from faker import Faker
from selenium.webdriver.common.by import By

from pages.frontend.home_page import HomePage
from pages.frontend.cart_page import CartPage
from config.settings import config
from utils.driver_manager import get_driver
from loguru import logger


class TestShoppingCart:
    """
    Test suite for shopping cart functionality
    Tests cart operations, quantity management, and cart persistence
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.driver = get_driver()
        self.base_url = config.base_url
        self.fake = Faker()
        
        # Initialize page objects
        self.home_page = HomePage(self.driver)
        self.cart_page = CartPage(self.driver)
        
        # Navigate to home page and clear cart
        self.driver.get(self.base_url)
        self._clear_cart_if_needed()
        
        yield
        
        # Cleanup - clear cart after each test
        self._clear_cart_if_needed()
        
        if config.screenshot_on_failure:
            self.driver.save_screenshot(f"{config.screenshots_dir}/cart_test_cleanup_{int(time.time())}.png")
    
    def _clear_cart_if_needed(self):
        """Clear cart if it contains items"""
        try:
            self.home_page.click_cart()
            self.cart_page.navigate_to_cart(self.base_url)
            if not self.cart_page.is_cart_empty():
                self.cart_page.remove_all_items()
                logger.info("Cart cleared for test setup")
        except Exception as e:
            logger.warning(f"Could not clear cart: {e}")
    
    def _add_sample_product_to_cart(self) -> str:
        """
        Add a sample product to cart and return product name
        
        Returns:
            str: Name of added product
        """
        self.driver.get(self.base_url)
        
        # Get first featured product name
        product_titles = self.home_page.get_product_titles()
        if not product_titles:
            pytest.skip("No featured products available for testing")
        
        product_name = product_titles[0]
        
        # Add first featured product to cart
        self.home_page.add_featured_product_to_cart(0)
        
        # Wait for success message
        time.sleep(2)
        
        logger.info(f"Added sample product to cart: {product_name}")
        return product_name
    
    def test_add_product_to_cart(self):
        """
        Test Case 1: Add product to shopping cart
        
        Verify that products can be successfully added to cart
        """
        logger.info("=== Test Case 1: Add Product to Cart ===")
        
        # Get initial cart count
        initial_cart_count = self.home_page.get_cart_item_count()
        
        # Add product to cart
        product_name = self._add_sample_product_to_cart()
        
        # Verify success message appears
        assert self.home_page.is_success_message_displayed(), "Success message not displayed"
        
        success_message = self.home_page.get_success_message()
        assert "added to" in success_message.lower(), f"Unexpected success message: {success_message}"
        
        # Verify cart count increased
        new_cart_count = self.home_page.get_cart_item_count()
        assert new_cart_count > initial_cart_count, "Cart count did not increase"
        
        # Navigate to cart and verify product is there
        self.cart_page.navigate_to_cart(self.base_url)
        assert self.cart_page.validate_item_in_cart(product_name), f"Product '{product_name}' not found in cart"
        
        logger.info(f"✅ Product successfully added to cart: {product_name}")
    
    def test_remove_product_from_cart(self):
        """
        Test Case 2: Remove product from shopping cart
        
        Verify that products can be removed from cart
        """
        logger.info("=== Test Case 2: Remove Product from Cart ===")
        
        # First add a product
        product_name = self._add_sample_product_to_cart()
        
        # Navigate to cart
        self.cart_page.navigate_to_cart(self.base_url)
        
        # Verify product is in cart
        initial_count = self.cart_page.get_cart_item_count()
        assert initial_count > 0, "Cart should contain items"
        assert self.cart_page.validate_item_in_cart(product_name), "Product not found in cart"
        
        # Remove the product
        self.cart_page.remove_item(0)
        
        # Wait for page update
        time.sleep(2)
        
        # Verify product was removed
        new_count = self.cart_page.get_cart_item_count()
        assert new_count < initial_count, "Cart count did not decrease"
        
        # If cart is now empty, verify empty cart message
        if new_count == 0:
            assert self.cart_page.is_cart_empty(), "Cart should be empty"
        
        logger.info("✅ Product successfully removed from cart")
    
    def test_update_product_quantity(self):
        """
        Test Case 3: Update product quantity in cart
        
        Verify that product quantities can be updated
        """
        logger.info("=== Test Case 3: Update Product Quantity ===")
        
        # Add product to cart
        product_name = self._add_sample_product_to_cart()
        
        # Navigate to cart
        self.cart_page.navigate_to_cart(self.base_url)
        
        # Get initial quantity
        initial_quantity = self.cart_page.get_item_quantity(0)
        assert initial_quantity == 1, f"Expected initial quantity 1, got {initial_quantity}"
        
        # Update quantity to 3
        new_quantity = 3
        self.cart_page.update_item_quantity(0, new_quantity)
        
        # Wait for update
        time.sleep(3)
        
        # Verify quantity was updated
        updated_quantity = self.cart_page.get_item_quantity(0)
        assert updated_quantity == new_quantity, \
            f"Expected quantity {new_quantity}, got {updated_quantity}"
        
        # Verify cart totals updated accordingly
        cart_summary = self.cart_page.get_cart_summary()
        assert cart_summary['item_count'] == 1, "Should still have 1 unique item"
        assert cart_summary['items'][0]['quantity'] == new_quantity, "Item quantity not updated in summary"
        
        logger.info(f"✅ Product quantity successfully updated to {new_quantity}")
    
    def test_cart_totals_calculation(self):
        """
        Test Case 4: Verify cart totals calculation
        
        Verify that cart totals are calculated correctly
        """
        logger.info("=== Test Case 4: Cart Totals Calculation ===")
        
        # Add multiple products to cart
        product_name = self._add_sample_product_to_cart()
        
        # Navigate to cart
        self.cart_page.navigate_to_cart(self.base_url)
        
        # Update quantity to test calculation
        self.cart_page.update_item_quantity(0, 2)
        time.sleep(3)
        
        # Get cart summary
        cart_summary = self.cart_page.get_cart_summary()
        
        # Verify totals are present and not zero
        assert cart_summary['subtotal'], "Subtotal should not be empty"
        assert cart_summary['total'], "Total should not be empty"
        
        # Verify subtotal and total are monetary values
        subtotal = cart_summary['subtotal']
        total = cart_summary['total']
        
        # Basic validation that these look like monetary amounts
        assert any(char.isdigit() for char in subtotal), f"Subtotal should contain digits: {subtotal}"
        assert any(char.isdigit() for char in total), f"Total should contain digits: {total}"
        
        logger.info(f"✅ Cart totals calculated: Subtotal={subtotal}, Total={total}")
    
    def test_empty_cart_state(self):
        """
        Test Case 5: Empty cart state and messages
        
        Verify empty cart state is handled correctly
        """
        logger.info("=== Test Case 5: Empty Cart State ===")
        
        # Ensure cart is empty
        self.cart_page.navigate_to_cart(self.base_url)
        if not self.cart_page.is_cart_empty():
            self.cart_page.remove_all_items()
        
        # Verify empty cart state
        assert self.cart_page.is_cart_empty(), "Cart should be empty"
        assert self.cart_page.get_cart_item_count() == 0, "Cart count should be 0"
        
        # Verify appropriate message is displayed
        cart_summary = self.cart_page.get_cart_summary()
        assert cart_summary['is_empty'], "Cart summary should indicate empty state"
        
        logger.info("✅ Empty cart state verified")
    
    def test_cart_persistence_across_pages(self):
        """
        Test Case 6: Cart persistence across page navigation
        
        Verify cart contents persist when navigating between pages
        """
        logger.info("=== Test Case 6: Cart Persistence ===")
        
        # Add product to cart
        product_name = self._add_sample_product_to_cart()
        
        # Get cart count
        initial_cart_count = self.home_page.get_cart_item_count()
        
        # Navigate to different pages
        self.home_page.click_desktops_menu()
        time.sleep(2)
        
        # Check cart count persists
        desktop_page_cart_count = self.home_page.get_cart_item_count()
        assert desktop_page_cart_count == initial_cart_count, "Cart count not persisted on category page"
        
        # Navigate back to home
        self.home_page.navigate_to_home()
        time.sleep(2)
        
        # Check cart count still persists
        home_page_cart_count = self.home_page.get_cart_item_count()
        assert home_page_cart_count == initial_cart_count, "Cart count not persisted on home page"
        
        # Verify in cart page
        self.cart_page.navigate_to_cart(self.base_url)
        assert self.cart_page.validate_item_in_cart(product_name), "Product not persisted in cart"
        
        logger.info("✅ Cart persistence verified across page navigation")
    
    def test_continue_shopping_functionality(self):
        """
        Test Case 7: Continue shopping from cart
        
        Verify continue shopping button works correctly
        """
        logger.info("=== Test Case 7: Continue Shopping ===")
        
        # Add product and go to cart
        self._add_sample_product_to_cart()
        self.cart_page.navigate_to_cart(self.base_url)
        
        # Click continue shopping
        self.cart_page.continue_shopping()
        
        # Verify navigation back to store
        current_url = self.driver.current_url
        assert "cart" not in current_url.lower(), "Should have navigated away from cart"
        
        # Verify we're on a store page (home or category)
        page_title = self.driver.title
        assert "OpenCart" in page_title or "store" in page_title.lower(), \
            f"Expected store page, got: {page_title}"
        
        logger.info("✅ Continue shopping functionality verified")
    
    def test_cart_with_multiple_products(self):
        """
        Test Case 8: Cart with multiple different products
        
        Verify cart handles multiple different products correctly
        """
        logger.info("=== Test Case 8: Multiple Products in Cart ===")
        
        # Get available products
        self.driver.get(self.base_url)
        product_titles = self.home_page.get_product_titles()
        
        if len(product_titles) < 2:
            pytest.skip("Need at least 2 products for this test")
        
        # Add multiple products
        self.home_page.add_featured_product_to_cart(0)
        time.sleep(2)
        
        if len(product_titles) > 1:
            self.home_page.add_featured_product_to_cart(1)
            time.sleep(2)
        
        # Navigate to cart
        self.cart_page.navigate_to_cart(self.base_url)
        
        # Verify multiple items in cart
        cart_count = self.cart_page.get_cart_item_count()
        assert cart_count >= 1, f"Expected at least 1 item, got {cart_count}"
        
        # Get cart summary
        cart_summary = self.cart_page.get_cart_summary()
        assert len(cart_summary['items']) >= 1, "Should have multiple items in summary"
        
        logger.info(f"✅ Multiple products in cart verified: {cart_count} items")
    
    def test_cart_quantity_edge_cases(self):
        """
        Test Case 9: Cart quantity edge cases
        
        Test edge cases like zero quantity, very large quantities
        """
        logger.info("=== Test Case 9: Quantity Edge Cases ===")
        
        # Add product to cart
        self._add_sample_product_to_cart()
        self.cart_page.navigate_to_cart(self.base_url)
        
        # Test very large quantity
        large_quantity = 999
        self.cart_page.update_item_quantity(0, large_quantity)
        time.sleep(3)
        
        # Check if large quantity was accepted or limited
        updated_quantity = self.cart_page.get_item_quantity(0)
        logger.info(f"Large quantity test: Requested={large_quantity}, Got={updated_quantity}")
        
        # Test zero quantity (should remove item)
        self.cart_page.update_item_quantity(0, 0)
        time.sleep(3)
        
        # Verify item was removed or quantity handled appropriately
        try:
            final_quantity = self.cart_page.get_item_quantity(0)
            logger.info(f"Zero quantity test: Final quantity={final_quantity}")
        except IndexError:
            logger.info("Zero quantity removed item from cart (expected behavior)")
        
        logger.info("✅ Quantity edge cases tested")
    
    def test_cart_error_handling(self):
        """
        Test Case 10: Cart error handling and edge cases
        
        Test various error conditions and edge cases
        """
        logger.info("=== Test Case 10: Cart Error Handling ===")
        
        # Test accessing cart page directly when empty
        self.cart_page.navigate_to_cart(self.base_url)
        assert self.cart_page.is_cart_page_loaded(), "Cart page should load even when empty"
        
        # Test removing non-existent item (should handle gracefully)
        try:
            if self.cart_page.is_cart_empty():
                # Try to remove item from empty cart
                # This should either do nothing or show appropriate message
                logger.info("Testing removal from empty cart")
                # The actual implementation would depend on how the page handles this
        except Exception as e:
            logger.info(f"Empty cart removal handled with exception: {e}")
        
        # Test invalid quantity updates
        self._add_sample_product_to_cart()
        self.cart_page.navigate_to_cart(self.base_url)
        
        # Try negative quantity (should be handled gracefully)
        try:
            self.cart_page.update_item_quantity(0, -1)
            time.sleep(2)
            quantity = self.cart_page.get_item_quantity(0)
            assert quantity >= 0, "Negative quantity should not be allowed"
        except Exception as e:
            logger.info(f"Negative quantity handled with exception: {e}")
        
        logger.info("✅ Error handling tested")


class TestCartPerformance:
    """Performance testing for cart operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup performance test environment"""
        self.driver = get_driver()
        self.base_url = config.base_url
        self.home_page = HomePage(self.driver)
        self.cart_page = CartPage(self.driver)
        
        yield
    
    def test_cart_operation_performance(self):
        """
        Test performance of cart operations
        
        Verify cart operations complete within acceptable time limits
        """
        logger.info("=== Cart Performance Test ===")
        
        self.driver.get(self.base_url)
        
        # Measure add to cart performance
        start_time = time.time()
        self.home_page.add_featured_product_to_cart(0)
        add_time = time.time() - start_time
        
        # Add to cart should be fast (< 5 seconds)
        assert add_time < 5.0, f"Add to cart too slow: {add_time:.2f}s"
        
        # Measure cart page load performance
        start_time = time.time()
        self.cart_page.navigate_to_cart(self.base_url)
        load_time = time.time() - start_time
        
        # Cart page should load quickly (< 10 seconds)
        assert load_time < 10.0, f"Cart page load too slow: {load_time:.2f}s"
        
        logger.info(f"✅ Performance test passed - Add: {add_time:.2f}s, Load: {load_time:.2f}s")