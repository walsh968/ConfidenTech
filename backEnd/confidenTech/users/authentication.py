"""
Custom authentication classes for API endpoints
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication that bypasses CSRF for API endpoints
    """
    def enforce_csrf(self, request):
        """
        Bypass CSRF enforcement for API endpoints
        """
        return  # Skip CSRF enforcement
