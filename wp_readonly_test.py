import requests
import sys

def test_wordpress_readonly_access():
    """Test if we can access WordPress REST API without authentication for read operations"""
    
    print("🔍 Testing WordPress REST API Read-Only Access")
    print("=" * 50)
    
    base_url = "https://www.cvlture.it/wp-json/wp/v2"
    
    # Test basic site info
    try:
        response = requests.get(f"{base_url}")
        print(f"✅ Site Info: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Site: {data.get('name', 'Unknown')}")
            print(f"   Description: {data.get('description', 'No description')}")
    except Exception as e:
        print(f"❌ Site Info Error: {e}")
    
    # Test posts endpoint
    try:
        response = requests.get(f"{base_url}/posts", params={"per_page": 3})
        print(f"✅ Posts: Status {response.status_code}")
        if response.status_code == 200:
            posts = response.json()
            print(f"   Found {len(posts)} posts")
            for post in posts[:2]:
                print(f"   - {post.get('title', {}).get('rendered', 'No title')}")
    except Exception as e:
        print(f"❌ Posts Error: {e}")
    
    # Test products endpoint (WooCommerce)
    try:
        response = requests.get(f"{base_url}/product", params={"per_page": 3})
        print(f"✅ Products: Status {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"   Found {len(products)} products")
            for product in products[:2]:
                print(f"   - {product.get('title', {}).get('rendered', 'No title')}")
        elif response.status_code == 404:
            print("   WooCommerce products endpoint not available (404)")
    except Exception as e:
        print(f"❌ Products Error: {e}")
    
    # Test events endpoint
    try:
        response = requests.get(f"{base_url}/events", params={"per_page": 3})
        print(f"✅ Events: Status {response.status_code}")
        if response.status_code == 200:
            events = response.json()
            print(f"   Found {len(events)} events")
        elif response.status_code == 404:
            print("   Events custom post type not available (404)")
    except Exception as e:
        print(f"❌ Events Error: {e}")

if __name__ == "__main__":
    test_wordpress_readonly_access()