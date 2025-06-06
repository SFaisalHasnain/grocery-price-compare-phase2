import requests
import sys
import uuid
import time
from datetime import datetime

class GroceryAppTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user = None
        self.test_password = "TestPass123!"
        self.product_ids = []
        self.store_ids = []
        self.shopping_list_id = None
        self.basket_item_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    print(f"Error: {error_detail}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )

    def test_register(self):
        """Test user registration"""
        # Generate a unique email for testing
        self.test_user = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            201,
            data={
                "email": self.test_user,
                "password": self.test_password,
                "full_name": "Test User",
                "location": "London"
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_login(self):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user,
                "password": self.test_password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        return self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )

    def test_get_stores(self):
        """Test getting stores"""
        success, response = self.run_test(
            "Get Stores",
            "GET",
            "stores",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            # Save store IDs for later tests
            self.store_ids = [store['id'] for store in response[:2]]
            return True
        return False

    def test_get_categories(self):
        """Test getting product categories"""
        return self.run_test(
            "Get Product Categories",
            "GET",
            "products/categories",
            200
        )

    def test_search_products(self):
        """Test searching products"""
        success, response = self.run_test(
            "Search Products",
            "GET",
            "products/search",
            200,
            params={"q": "milk"}
        )
        
        if success and 'products' in response and len(response['products']) > 0:
            # Save product IDs for later tests
            self.product_ids = [product['id'] for product in response['products'][:2]]
            return True
        return False

    def test_guest_search_products(self):
        """Test guest search products"""
        # Temporarily remove token
        temp_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Guest Search Products",
            "GET",
            "products/guest-search",
            200,
            params={"q": "bread"}
        )
        
        # Restore token
        self.token = temp_token
        return success and 'products' in response

    def test_create_shopping_list(self):
        """Test creating a shopping list"""
        success, response = self.run_test(
            "Create Shopping List",
            "POST",
            "shopping-lists",
            201,
            data={
                "name": "Test Shopping List",
                "description": "Created for testing"
            }
        )
        
        if success and 'id' in response:
            self.shopping_list_id = response['id']
            return True
        return False

    def test_add_item_to_shopping_list(self):
        """Test adding item to shopping list"""
        if not self.shopping_list_id:
            print("❌ Shopping list ID not available")
            return False
            
        return self.run_test(
            "Add Item to Shopping List",
            "POST",
            f"shopping-lists/{self.shopping_list_id}/items",
            201,
            data={
                "product_name": "Test Item",
                "quantity": 2,
                "unit": "each",
                "category": "Dairy & Eggs"
            }
        )[0]

    def test_get_shopping_lists(self):
        """Test getting shopping lists"""
        return self.run_test(
            "Get Shopping Lists",
            "GET",
            "shopping-lists",
            200
        )[0]

    def test_add_to_basket(self):
        """Test adding item to basket"""
        if not self.product_ids or not self.store_ids:
            print("❌ Product or store IDs not available")
            return False
            
        success, response = self.run_test(
            "Add to Basket",
            "POST",
            "basket/items",
            201,
            data={
                "product_id": self.product_ids[0],
                "store_id": self.store_ids[0],
                "quantity": 1
            }
        )
        
        if success and 'items' in response and len(response['items']) > 0:
            self.basket_item_id = response['items'][0]['id']
            return True
        return False

    def test_get_basket(self):
        """Test getting basket"""
        return self.run_test(
            "Get Basket",
            "GET",
            "basket",
            200
        )[0]

    def test_update_basket_item(self):
        """Test updating basket item"""
        if not self.basket_item_id:
            print("❌ Basket item ID not available")
            return False
            
        return self.run_test(
            "Update Basket Item",
            "PUT",
            f"basket/items/{self.basket_item_id}",
            200,
            data={
                "quantity": 3
            }
        )[0]

    def test_get_basket_summary(self):
        """Test getting basket summary"""
        return self.run_test(
            "Get Basket Summary",
            "GET",
            "basket/summary",
            200
        )[0]

    def test_remove_from_basket(self):
        """Test removing item from basket"""
        if not self.basket_item_id:
            print("❌ Basket item ID not available")
            return False
            
        return self.run_test(
            "Remove from Basket",
            "DELETE",
            f"basket/items/{self.basket_item_id}",
            200
        )[0]

    def test_clear_basket(self):
        """Test clearing basket"""
        return self.run_test(
            "Clear Basket",
            "DELETE",
            "basket",
            200
        )[0]

    def test_delete_shopping_list(self):
        """Test deleting shopping list"""
        if not self.shopping_list_id:
            print("❌ Shopping list ID not available")
            return False
            
        return self.run_test(
            "Delete Shopping List",
            "DELETE",
            f"shopping-lists/{self.shopping_list_id}",
            204
        )[0]

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Grocery App API Tests")
        
        # Health check
        self.test_health_check()
        
        # Authentication tests
        self.test_register()
        self.test_login()
        self.test_get_current_user()
        
        # Store and product tests
        self.test_get_stores()
        self.test_get_categories()
        self.test_search_products()
        self.test_guest_search_products()
        
        # Shopping list tests
        self.test_create_shopping_list()
        self.test_add_item_to_shopping_list()
        self.test_get_shopping_lists()
        
        # Basket tests
        self.test_add_to_basket()
        self.test_get_basket()
        self.test_update_basket_item()
        self.test_get_basket_summary()
        self.test_remove_from_basket()
        self.test_clear_basket()
        
        # Cleanup
        self.test_delete_shopping_list()
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/self.tests_run*100:.1f}%)")
        return self.tests_passed == self.tests_run

def main():
    # Get backend URL from environment
    backend_url = "https://6b8fe609-8c4a-4904-adc1-b052bf1c0543.preview.emergentagent.com"
    
    print(f"Testing API at: {backend_url}")
    
    # Run tests
    tester = GroceryAppTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
