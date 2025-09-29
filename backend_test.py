import requests
import sys
import json
from datetime import datetime

class WordPressAPITester:
    def __init__(self, base_url="https://wp-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.config_created = False

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params or {})
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
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text[:300]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_wp_config_without_setup(self):
        """Test getting WordPress config when none exists"""
        return self.run_test("Get WP Config (No Setup)", "GET", "wp-config", 404)

    def test_test_connection_without_setup(self):
        """Test connection when no config exists"""
        return self.run_test("Test Connection (No Setup)", "GET", "test-connection", 400)

    def test_create_wp_config_invalid(self):
        """Test creating WordPress config with invalid credentials"""
        invalid_config = {
            "site_url": "https://www.cvlture.it",
            "username": "invalid_user",
            "app_password": "invalid_password"
        }
        return self.run_test("Create WP Config (Invalid)", "POST", "wp-config", 400, data=invalid_config)

    def test_create_wp_config_valid(self):
        """Test creating WordPress config with valid site URL (no credentials for read-only)"""
        # Using the actual site URL but with dummy credentials for testing
        # This will likely fail but we can test the endpoint structure
        valid_config = {
            "site_url": "https://www.cvlture.it",
            "username": "test_user",
            "app_password": "test_password"
        }
        success, response = self.run_test("Create WP Config (Test)", "POST", "wp-config", 400, data=valid_config)
        # We expect this to fail due to invalid credentials, but it tests the endpoint
        return success, response

    def test_posts_without_config(self):
        """Test getting posts when no config exists"""
        return self.run_test("Get Posts (No Config)", "GET", "posts", 404)

    def test_products_without_config(self):
        """Test getting products when no config exists"""
        return self.run_test("Get Products (No Config)", "GET", "products", 404)

    def test_events_without_config(self):
        """Test getting events when no config exists"""
        return self.run_test("Get Events (No Config)", "GET", "events", 404)

    def test_site_info_without_config(self):
        """Test getting site info when no config exists"""
        return self.run_test("Get Site Info (No Config)", "GET", "site-info", 404)

    def test_create_product_without_config(self):
        """Test creating product when no config exists"""
        product_data = {
            "title": "Test Product",
            "content": "Test product description",
            "status": "draft"
        }
        return self.run_test("Create Product (No Config)", "POST", "products", 404, data=product_data)

    def test_create_event_without_config(self):
        """Test creating event when no config exists"""
        event_data = {
            "title": "Test Event",
            "content": "Test event description",
            "location": "Test Location",
            "event_date": "2024-12-31T18:00:00"
        }
        return self.run_test("Create Event (No Config)", "POST", "events", 404, data=event_data)

    def test_invalid_endpoints(self):
        """Test invalid endpoints return 404"""
        success1, _ = self.run_test("Invalid Endpoint 1", "GET", "invalid-endpoint", 404)
        success2, _ = self.run_test("Invalid Endpoint 2", "GET", "nonexistent", 404)
        return success1 and success2

    def test_method_not_allowed(self):
        """Test method not allowed scenarios"""
        # Try POST on GET-only endpoints
        success1, _ = self.run_test("POST on GET endpoint", "POST", "posts", 404, data={})
        return success1

def main():
    print("🚀 Starting WordPress Management API Tests")
    print("=" * 60)
    
    # Setup
    tester = WordPressAPITester()
    
    # Test basic connectivity
    print("\n📡 BASIC CONNECTIVITY TESTS")
    print("-" * 40)
    tester.test_root_endpoint()
    
    # Test endpoints without configuration
    print("\n🔒 TESTS WITHOUT WORDPRESS CONFIGURATION")
    print("-" * 40)
    tester.test_wp_config_without_setup()
    tester.test_test_connection_without_setup()
    tester.test_posts_without_config()
    tester.test_products_without_config()
    tester.test_events_without_config()
    tester.test_site_info_without_config()
    tester.test_create_product_without_config()
    tester.test_create_event_without_config()
    
    # Test configuration creation
    print("\n⚙️  WORDPRESS CONFIGURATION TESTS")
    print("-" * 40)
    tester.test_create_wp_config_invalid()
    tester.test_create_wp_config_valid()
    
    # Test invalid endpoints
    print("\n🚫 INVALID ENDPOINT TESTS")
    print("-" * 40)
    tester.test_invalid_endpoints()
    tester.test_method_not_allowed()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())