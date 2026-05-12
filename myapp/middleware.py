from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.cache import patch_response_headers
import logging

from .notification_utils import dashboard_url_for_user, notification_url_for_user, role_key

logger = logging.getLogger(__name__)


ROLE_PREFIXES = {'administrator', 'staff', 'proponent', 'beneficiary'}


class RoleBoundaryMiddleware(MiddlewareMixin):
    """Keep authenticated users inside their role-specific app area."""

    def process_request(self, request):
        user = getattr(request, 'user', None)
        path = request.path_info or request.path or '/'
        segments = [segment for segment in path.strip('/').split('/') if segment]
        if not segments:
            return None
        first_segment = segments[0]

        protected_legacy_admin_area = first_segment == 'projects'
        if (first_segment in ROLE_PREFIXES or protected_legacy_admin_area) and (not user or not user.is_authenticated):
            return redirect(reverse('index_url'))

        user_role = role_key(user)

        if first_segment in ROLE_PREFIXES and first_segment != user_role:
            section = segments[1] if len(segments) > 1 else 'dashboard'
            if section == 'dashboard':
                return redirect(dashboard_url_for_user(user))
            return redirect(notification_url_for_user(user, section))

        # The legacy administrator project module is mounted at /projects/.
        # Non-admin roles must use their own project list URLs.
        if first_segment == 'projects' and user_role != 'administrator':
            return redirect(notification_url_for_user(user, 'projects'))

        return None


class CacheControlMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Only cache safe/read requests
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response

        request_path = request.path.lower()

        # Long cache for static assets
        if request_path.startswith('/static/'):
            patch_response_headers(response, cache_timeout=31536000)

        # Short cache for API responses
        elif request_path.startswith('/api/'):
            patch_response_headers(response, cache_timeout=300)

        # Dynamic HTML should not be cached
        else:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    Helps protect against common web vulnerabilities.
    """
    def process_response(self, request, response):
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # XSS Protection (legacy browsers)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (restrict certain browser features)
        response['Permissions-Policy'] = 'geolocation=(self), microphone=(), camera=()'
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests for auditing purposes.
    Useful for debugging and security monitoring.
    """
    def process_request(self, request):
        # Log request details (only for authenticated users to avoid spam)
        if request.user.is_authenticated:
            logger.info(
                f"Request: {request.method} {request.path} | "
                f"User: {request.user.username} | "
                f"IP: {self.get_client_ip(request)}"
            )
    
    def get_client_ip(self, request):
        """Get the real client IP, handling proxy servers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to catch and handle unexpected errors gracefully.
    Logs errors and returns user-friendly responses.
    """
    def process_exception(self, request, exception):
        # Log the error with full details
        logger.error(
            f"Unhandled exception: {type(exception).__name__}: {str(exception)} | "
            f"Path: {request.path} | "
            f"User: {request.user.username if request.user.is_authenticated else 'anonymous'} | "
            f"IP: {request.META.get('REMOTE_ADDR', 'unknown')}",
            exc_info=True
        )
        
        # For AJAX requests, return JSON error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': 'An unexpected error occurred. Please try again later.'
            }, status=500)
        
        # For regular requests, let Django's error handling take over
        return None
