import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from server import (
    WordPressConfigCreate,
    CreateEventRequest,
    CreateProductRequest,
    sanitize_html,
    validate_wordpress_url
)
from pydantic import ValidationError

class TestValidationHelpers:
    """Test validation helper functions"""
    
    def test_sanitize_html_removes_dangerous_tags(self):
        """Test HTML sanitization removes dangerous tags"""
        dangerous_html = '<script>alert("xss")</script><p>Safe content</p><img src="x" onerror="alert(1)">'
        sanitized = sanitize_html(dangerous_html)
        
        assert '<script>' not in sanitized
        assert 'alert' not in sanitized
        assert '<p>Safe content</p>' in sanitized
        assert 'onerror' not in sanitized
    
    def test_sanitize_html_keeps_safe_tags(self):
        """Test HTML sanitization keeps safe tags"""
        safe_html = '<p>This is <strong>bold</strong> and <em>italic</em> text.</p>'
        sanitized = sanitize_html(safe_html)
        
        assert sanitized == safe_html
    
    def test_validate_wordpress_url_valid_urls(self):
        """Test WordPress URL validation with valid URLs"""
        valid_urls = [
            'https://example.com',
            'http://test-site.co.uk',
            'https://www.cvlture.it',
            'https://subdomain.example.org'
        ]
        
        for url in valid_urls:
            result = validate_wordpress_url(url)
            assert result.startswith(('http://', 'https://'))
            assert not result.endswith('/')
    
    def test_validate_wordpress_url_invalid_urls(self):
        """Test WordPress URL validation with invalid URLs"""
        invalid_urls = [
            'not-a-url',
            'ftp://example.com',
            'javascript:alert(1)',
            'http://',
            'https://',
            ''
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                validate_wordpress_url(url)

class TestWordPressConfigValidation:
    """Test WordPress configuration validation"""
    
    def test_valid_config(self):
        """Test valid WordPress configuration"""
        valid_config = WordPressConfigCreate(
            site_url='https://www.cvlture.it',
            username='admin',
            app_password='abcd efgh ijkl mnop qrst uvwx'
        )
        
        assert valid_config.site_url == 'https://www.cvlture.it'
        assert valid_config.username == 'admin'
        assert len(valid_config.app_password) >= 10
    
    def test_invalid_site_url(self):
        """Test invalid site URL validation"""
        with pytest.raises(ValidationError):
            WordPressConfigCreate(
                site_url='not-a-url',
                username='admin',
                app_password='abcd efgh ijkl mnop qrst uvwx'
            )
    
    def test_short_username(self):
        """Test short username validation"""
        with pytest.raises(ValidationError):
            WordPressConfigCreate(
                site_url='https://example.com',
                username='ab',
                app_password='abcd efgh ijkl mnop qrst uvwx'
            )
    
    def test_short_password(self):
        """Test short password validation"""
        with pytest.raises(ValidationError):
            WordPressConfigCreate(
                site_url='https://example.com',
                username='admin',
                app_password='short'
            )
    
    def test_username_xss_cleaning(self):
        """Test username XSS cleaning"""
        config = WordPressConfigCreate(
            site_url='https://example.com',
            username='<script>alert(1)</script>admin',
            app_password='abcd efgh ijkl mnop qrst uvwx'
        )
        
        assert '<script>' not in config.username
        assert 'admin' in config.username

class TestEventRequestValidation:
    """Test event creation request validation"""
    
    def test_valid_event_request(self):
        """Test valid event request"""
        valid_event = CreateEventRequest(
            title='Test Event',
            content='<p>This is a test event.</p>',
            location='Test Location',
            event_date='2024-12-25T15:30'
        )
        
        assert valid_event.title == 'Test Event'
        assert '<p>' in valid_event.content
        assert valid_event.location == 'Test Location'
    
    def test_event_xss_cleaning(self):
        """Test event XSS cleaning"""
        event = CreateEventRequest(
            title='<script>alert(1)</script>Test Event',
            content='<script>alert(1)</script><p>Safe content</p>',
            location='<script>alert(1)</script>Test Location',
            event_date='2024-12-25T15:30'
        )
        
        assert '<script>' not in event.title
        assert '<script>' not in event.content
        assert '<script>' not in event.location
        assert 'Test Event' in event.title
        assert '<p>Safe content</p>' in event.content
    
    def test_invalid_event_date_format(self):
        """Test invalid event date format"""
        with pytest.raises(ValidationError):
            CreateEventRequest(
                title='Test Event',
                content='Content',
                location='Location',
                event_date='invalid-date'
            )
    
    def test_long_title_validation(self):
        """Test long title validation"""
        with pytest.raises(ValidationError):
            CreateEventRequest(
                title='A' * 300,  # Too long
                content='Content',
                location='Location',
                event_date='2024-12-25T15:30'
            )

class TestProductRequestValidation:
    """Test product creation request validation"""
    
    def test_valid_product_request(self):
        """Test valid product request"""
        valid_product = CreateProductRequest(
            title='Test Product',
            content='<p>Product description</p>',
            status='draft'
        )
        
        assert valid_product.title == 'Test Product'
        assert valid_product.status == 'draft'
    
    def test_invalid_product_status(self):
        """Test invalid product status"""
        with pytest.raises(ValidationError):
            CreateProductRequest(
                title='Test Product',
                content='Content',
                status='invalid_status'
            )
    
    def test_product_xss_cleaning(self):
        """Test product XSS cleaning"""
        product = CreateProductRequest(
            title='<script>alert(1)</script>Test Product',
            content='<script>alert(1)</script><p>Safe content</p>',
            status='draft'
        )
        
        assert '<script>' not in product.title
        assert '<script>' not in product.content
        assert 'Test Product' in product.title
        assert '<p>Safe content</p>' in product.content

if __name__ == "__main__":
    pytest.main([__file__])