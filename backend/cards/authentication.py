from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication without CSRF checks for development.
    In production, use standard SessionAuthentication.
    """
    def enforce_csrf(self, request):
        return  # Skip CSRF check
