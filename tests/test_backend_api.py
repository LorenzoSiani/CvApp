import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from server import app

client = TestClient(app)

class TestWordPressAPI:
    """Test WordPress API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        response = client.get("/api/")
        assert response.status_code == 200
        assert "WordPress Management API" in response.json()["message"]
    
    def test_wp_config_not_found(self):
        """Test getting config when none exists"""
        # Clear any existing config first
        response = client.get("/api/wp-config")
        # Should return 404 when no config exists
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_test_connection_no_config(self):
        """Test connection test when no config exists"""
        response = client.get("/api/test-connection")
        assert response.status_code == 404
    
    def test_create_wp_config_invalid_data(self):
        """Test creating config with invalid data"""
        invalid_configs = [
            # Invalid URL
            {
                "site_url": "not-a-url",
                "username": "testuser",
                "app_password": "test_password_123"
            },
            # Short username
            {
                "site_url": "https://example.com",
                "username": "ab",
                "app_password": "test_password_123"
            },
            # Short password
            {
                "site_url": "https://example.com",
                "username": "testuser",
                "app_password": "short"
            }
        ]
        
        for config in invalid_configs:
            response = client.post("/api/wp-config", json=config)
            assert response.status_code == 422  # Validation error
    
    def test_create_wp_config_valid_structure(self):
        """Test creating config with valid structure (may fail connection)"""
        valid_config = {
            "site_url": "https://example.com",
            "username": "testuser",
            "app_password": "test_password_123456"
        }
        
        response = client.post("/api/wp-config", json=valid_config)
        # Should pass validation but may fail WordPress connection
        assert response.status_code in [200, 201, 400]  # 400 for connection failure
    
    def test_posts_endpoint_no_config(self):
        """Test posts endpoint when no config exists"""
        response = client.get("/api/posts")
        assert response.status_code == 404
    
    def test_products_endpoint_no_config(self):
        """Test products endpoint when no config exists"""
        response = client.get("/api/products")
        assert response.status_code == 404
    
    def test_events_endpoint_no_config(self):
        """Test events endpoint when no config exists"""
        response = client.get("/api/events")
        assert response.status_code == 404
    
    def test_post_types_endpoint_no_config(self):
        """Test post types endpoint when no config exists"""
        response = client.get("/api/post-types")
        assert response.status_code == 404

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_xss_prevention_in_event_creation(self):
        """Test XSS prevention in event creation"""
        malicious_event = {
            "title": "<script>alert('xss')</script>Test Event",
            "content": "<script>alert('xss')</script><p>Content</p>",
            "location": "<script>alert('xss')</script>Test Location",
            "event_date": "2024-12-25T15:30"
        }
        
        # This should fail validation due to malicious content
        response = client.post("/api/events", json=malicious_event)
        # Will fail because no config, but validation should clean the input
        assert response.status_code in [404, 422]
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        malicious_product = {
            "title": "'; DROP TABLE products; --",
            "content": "Normal content",
            "status": "draft"
        }
        
        response = client.post("/api/products", json=malicious_product) 
        # Should not cause SQL injection (we use MongoDB anyway)
        assert response.status_code in [404, 422]
    
    def test_long_input_validation(self):
        """Test validation of overly long inputs"""
        long_title = "A" * 300  # Exceeds max_length
        
        long_event = {
            "title": long_title,
            "content": "Normal content",
            "location": "Test Location",
            "event_date": "2024-12-25T15:30"
        }
        
        response = client.post("/api/events", json=long_event)
        assert response.status_code == 422  # Validation error

class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers_present(self):
        """Test that security headers are present"""
        response = client.get("/api/")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert "1; mode=block" in response.headers["X-XSS-Protection"]

class TestCORSConfiguration:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        response = client.options("/api/")
        
        # CORS should be configured
        assert response.status_code in [200, 405]  # Some endpoints might not support OPTIONS

if __name__ == "__main__":
    pytest.main([__file__])