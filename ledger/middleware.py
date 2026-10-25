from django.http import HttpResponseForbidden
from .access import is_driver
from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone
from django.utils.cache import add_never_cache_headers

class SessionExpiryMiddleware:
    """Browser-session cookies plus server-enforced inactivity expiry."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authenticated = request.user.is_authenticated
        if authenticated:
            now = timezone.now().timestamp()
            last_seen = request.session.get('last_activity', now)
            if now - last_seen > settings.SESSION_IDLE_TIMEOUT:
                logout(request)
            else:
                request.session['last_activity'] = now
                request.session.set_expiry(0)
        response = self.get_response(request)
        if authenticated or request.user.is_authenticated:
            add_never_cache_headers(response)
        return response

class DriverAccessMiddleware:
    """Enforce driver permissions at every application entry point."""
    allowed = {'dashboard', 'expense_add', 'settings', 'set_language', 'downloads',
               'password_change', 'password_change_done', 'logout', 'login', 'manifest', 'service_worker', 'session_activity'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view, args, kwargs):
        if is_driver(request.user) and request.resolver_match.url_name not in self.allowed:
            return HttpResponseForbidden('Driver accounts can access their assigned vehicle, add expenses, and manage their own account.')
