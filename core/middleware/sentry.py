# core/middleware/sentry.py
import sentry_sdk
from rest_framework.exceptions import APIException


class SentryReportingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, APIException):
            return None

        with sentry_sdk.push_scope() as scope:
            scope.set_context("request", {
                "ip": request.META.get('REMOTE_ADDR'),
                "path": request.path,
                "method": request.method,
            })
            # Agregar usuario si existe, igual que el mixin
            if hasattr(request, 'user') and request.user.is_authenticated:
                scope.set_user({
                    'id': request.user.id,
                    'email': request.user.email,
                    'username': request.user.username,
                })
            scope.set_tag('source', 'middleware_fallback')  # para diferenciar en Sentry de los reportes del mixin
            sentry_sdk.capture_exception(exception)
        return None