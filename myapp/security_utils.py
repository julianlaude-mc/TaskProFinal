# Security Optimization Module
# Add to myapp/security_utils.py (create new file)

import re
import logging
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

# ==================== INPUT VALIDATION & SANITIZATION ====================

class SecureInputValidator:
    """Efficient input validation to prevent security vulnerabilities"""
    
    # Regex patterns for common validations
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    PHONE_PATTERN = re.compile(r'^\+?1?\d{9,15}$')
    URL_PATTERN = re.compile(r'^https?://')
    PROJECT_CODE_PATTERN = re.compile(r'^DOST-\d{4}-\d{3}$')
    
    @staticmethod
    def validate_email(email):
        """Validate email format efficiently"""
        if not email or len(email) > 254:
            raise ValidationError("Invalid email format")
        if not SecureInputValidator.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email address")
        return email
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets security requirements"""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain uppercase letter")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain special character")
        return password
    
    @staticmethod
    def validate_field_value(value, field_type='text', max_length=255):
        """Generic field validation"""
        if not value:
            return value
        
        if len(str(value)) > max_length:
            raise ValidationError(f"Field exceeds maximum length of {max_length}")
        
        if field_type == 'text':
            # Allow text but prevent injection
            if '<script>' in value.lower() or 'javascript:' in value.lower():
                raise ValidationError("Suspicious content detected")
        
        elif field_type == 'alphanumeric':
            if not SecureInputValidator.ALPHANUMERIC_PATTERN.match(value):
                raise ValidationError("Only alphanumeric characters allowed")
        
        elif field_type == 'phone':
            if not SecureInputValidator.PHONE_PATTERN.match(value):
                raise ValidationError("Invalid phone number format")
        
        elif field_type == 'url':
            if not SecureInputValidator.URL_PATTERN.match(value):
                raise ValidationError("Invalid URL format")
        
        return value
    
    @staticmethod
    def sanitize_string(text, allow_html=False):
        """Sanitize string input to prevent XSS"""
        if not text:
            return text
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Escape HTML if not explicitly allowed
        if not allow_html:
            text = escape(text)
        
        return text

# ==================== SECURE QUERY EXECUTION ====================

class SecureQuery:
    """Execute queries with built-in protection against SQL injection"""
    
    @staticmethod
    def execute_parametrized(sql, params):
        """
        Execute query using parametrized statements (prevents SQL injection)
        
        Example:
            SecureQuery.execute_parametrized(
                "SELECT * FROM myapp_user WHERE email = %s",
                ['user@example.com']
            )
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise
    
    @staticmethod
    def validate_sql_injection(value):
        """Check for common SQL injection patterns"""
        suspicious_patterns = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION', 'SELECT',
            'exec', 'execute', 'script', 'javascript'
        ]
        
        value_upper = str(value).upper()
        for pattern in suspicious_patterns:
            if pattern in value_upper:
                logger.warning(f"Potential SQL injection attempt detected: {value[:50]}")
                raise ValidationError("Invalid input detected")
        
        return value

# ==================== PRODUCTION LOGGING SAFEGUARDS ====================

class ProductionLogger:
    """Minimize logging in production to reduce performance impact and data leaks"""
    
    # List of sensitive fields to exclude from logs
    SENSITIVE_FIELDS = [
        'password', 'token', 'secret', 'api_key', 'credit_card',
        'ssn', 'pin', 'access_token', 'refresh_token'
    ]
    
    @staticmethod
    def configure_production_logging():
        """Configure logging to be minimal and secure in production"""
        if settings.DEBUG:
            log_level = logging.DEBUG
        else:
            log_level = logging.WARNING  # Only warnings and errors in production
        
        # Update root logger configuration
        logger.setLevel(log_level)
        
        return log_level
    
    @staticmethod
    def log_safe(message, data=None, level='info'):
        """
        Log messages safely, removing sensitive data
        
        Example:
            ProductionLogger.log_safe(
                "User login attempt",
                {'user_id': 123, 'password': '****'},
                level='info'
            )
        """
        if data:
            data = ProductionLogger._mask_sensitive_data(data)
        
        log_func = getattr(logger, level, logger.info)
        
        if data:
            log_func(f"{message} - {data}")
        else:
            log_func(message)
    
    @staticmethod
    def _mask_sensitive_data(data):
        """Remove or mask sensitive fields from dict"""
        if not isinstance(data, dict):
            return data
        
        masked_data = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ProductionLogger.SENSITIVE_FIELDS):
                masked_data[key] = '***REDACTED***'
            else:
                masked_data[key] = value
        
        return masked_data
    
    @staticmethod
    def disable_debug_toolbar():
        """Ensure debug toolbar disabled in production"""
        if not settings.DEBUG:
            if 'debug_toolbar' in settings.INSTALLED_APPS:
                settings.INSTALLED_APPS.remove('debug_toolbar')
            return True
        return False

# ==================== RATE LIMITING & BRUTE FORCE PROTECTION ====================

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from time import time

class RateLimiter:
    """Prevent brute force attacks with rate limiting"""
    
    @staticmethod
    def check_rate_limit(key, max_attempts=5, time_window=300):
        """
        Check if request exceeds rate limit
        
        Args:
            key: Cache key (e.g., user_id, IP address)
            max_attempts: Max attempts allowed
            time_window: Time window in seconds
        
        Returns:
            bool: True if within limit, False if exceeded
        """
        from django.core.cache import cache
        
        cache_key = f"rate_limit_{key}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            return False
        
        cache.set(cache_key, attempts + 1, time_window)
        return True
    
    @staticmethod
    def rate_limit_required(max_attempts=5, time_window=300):
        """Decorator for rate limiting views"""
        def decorator(func):
            def wrapper(request, *args, **kwargs):
                # Use IP address as key
                client_ip = request.META.get('REMOTE_ADDR', 'unknown')
                
                if not RateLimiter.check_rate_limit(client_ip, max_attempts, time_window):
                    from django.http import HttpResponse
                    return HttpResponse("Too many requests. Please try again later.", status=429)
                
                return func(request, *args, **kwargs)
            return wrapper
        return decorator

# ==================== CSRF & XSS PROTECTION ====================

class SecurityHeaders:
    """Add security headers to responses"""
    
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
        'Referrer-Policy': 'no-referrer',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        for header, value in SecurityHeaders.SECURITY_HEADERS.items():
            response[header] = value
        return response

# ==================== USAGE EXAMPLES ====================

"""
# Usage Examples:

# 1. Validate user input
try:
    email = SecureInputValidator.validate_email(user_email)
    password = SecureInputValidator.validate_password_strength(user_password)
except ValidationError as e:
    # Handle validation error

# 2. Sanitize string input
sanitized_text = SecureInputValidator.sanitize_string(user_input)

# 3. Execute secure query
results = SecureQuery.execute_parametrized(
    "SELECT * FROM myapp_user WHERE email = %s",
    [user_email]
)

# 4. Safe logging
ProductionLogger.log_safe(
    "User login",
    {'user_id': user.id, 'timestamp': now()},
    level='info'
)

# 5. Rate limiting
@RateLimiter.rate_limit_required(max_attempts=5, time_window=300)
def login_view(request):
    # Login logic

# 6. Add security headers
response = SecurityHeaders.add_security_headers(response)
"""
