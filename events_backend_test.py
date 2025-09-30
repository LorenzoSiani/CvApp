import requests
import sys
import json
from datetime import datetime

class EventsAPITester:
    def __init__(self, base_url="https://wp-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_event_id = None

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
                        if len(response_data) > 0:
                            print(f"   First item: {response_data[0]}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text[:300]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_events(self):
        """Test GET /api/events - Should fetch events from /wp-json/wp/v2/eventi"""
        return self.run_test("GET Events", "GET", "events", 200, params={"per_page": 10})

    def test_get_single_event_nonexistent(self):
        """Test GET /api/events/{id} - Get single event by ID (nonexistent)"""
        return self.run_test("GET Single Event (Nonexistent)", "GET", "events/99999", 404)

    def test_create_event(self):
        """Test POST /api/events - Create new event"""
        event_data = {
            "title": "Test Event from API",
            "content": "This is a test event created via the API to test the eventi endpoint integration.",
            "location": "Milan, Italy",
            "event_date": "2024-12-31T18:00:00",
            "featured_image_url": "https://example.com/test-image.jpg"
        }
        success, response = self.run_test("POST Create Event", "POST", "events", 200, data=event_data)
        if success and 'id' in response:
            self.created_event_id = response['id']
            print(f"   Created event ID: {self.created_event_id}")
        return success, response

    def test_get_single_event_existing(self):
        """Test GET /api/events/{id} - Get single event by ID (existing)"""
        if not self.created_event_id:
            print("❌ Skipping - No event ID available")
            return False, {}
        return self.run_test("GET Single Event (Existing)", "GET", f"events/{self.created_event_id}", 200)

    def test_update_event(self):
        """Test PUT /api/events/{id} - Update existing event"""
        if not self.created_event_id:
            print("❌ Skipping - No event ID available")
            return False, {}
        
        updated_event_data = {
            "title": "Updated Test Event",
            "content": "This event has been updated via the API.",
            "location": "Rome, Italy",
            "event_date": "2024-12-31T20:00:00",
            "featured_image_url": "https://example.com/updated-image.jpg"
        }
        return self.run_test("PUT Update Event", "PUT", f"events/{self.created_event_id}", 200, data=updated_event_data)

    def test_delete_event(self):
        """Test DELETE /api/events/{id} - Delete event"""
        if not self.created_event_id:
            print("❌ Skipping - No event ID available")
            return False, {}
        return self.run_test("DELETE Event", "DELETE", f"events/{self.created_event_id}", 200)

    def test_test_events_endpoint(self):
        """Test GET /api/test-events - Test connectivity to eventi endpoint"""
        return self.run_test("Test Events Endpoint", "GET", "test-events", 200)

    def test_create_event_invalid_data(self):
        """Test creating event with invalid data"""
        invalid_event_data = {
            "title": "",  # Empty title should fail
            "content": "Test content",
            "location": "Test Location",
            "event_date": "invalid-date"  # Invalid date format
        }
        return self.run_test("POST Create Event (Invalid Data)", "POST", "events", 422, data=invalid_event_data)

    def test_create_event_missing_fields(self):
        """Test creating event with missing required fields"""
        incomplete_event_data = {
            "title": "Test Event"
            # Missing required fields: content, location, event_date
        }
        return self.run_test("POST Create Event (Missing Fields)", "POST", "events", 422, data=incomplete_event_data)

def main():
    print("🚀 Starting Events API Comprehensive Tests")
    print("=" * 60)
    
    # Setup
    tester = EventsAPITester()
    
    # Test events functionality
    print("\n📅 EVENTS ENDPOINT TESTS")
    print("-" * 40)
    tester.test_get_events()
    tester.test_test_events_endpoint()
    
    print("\n🔧 EVENTS CRUD OPERATIONS")
    print("-" * 40)
    tester.test_get_single_event_nonexistent()
    tester.test_create_event()
    tester.test_get_single_event_existing()
    tester.test_update_event()
    
    print("\n❌ ERROR HANDLING TESTS")
    print("-" * 40)
    tester.test_create_event_invalid_data()
    tester.test_create_event_missing_fields()
    
    print("\n🗑️  CLEANUP")
    print("-" * 40)
    tester.test_delete_event()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All events tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())