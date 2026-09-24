import logging
from smtplib import SMTPException
from requests.exceptions import Timeout, ConnectionError, RequestException
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, DatabaseError

from core.error_codes import DEFAULT_CODE_MAP, ErrorCodes
import sentry_sdk
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status


logger = logging.getLogger(__name__)

try:
    from oauthlib.oauth2 import OAuth2Error  # ajusta el import a tu librería OAuth real
except ImportError:
    OAuth2Error = None


def _capture_to_sentry(exc, level, tags, request=None, extra=None):
    with sentry_sdk.push_scope() as scope:
        scope.level = level
        for k, v in tags.items():
            scope.set_tag(k, str(v))
        for k, v in (extra or {}).items():
            scope.set_extra(k, v)
        if request is not None:
            scope.set_context("request", {
                "ip": request.META.get('REMOTE_ADDR'),
                "user_agent": request.META.get('HTTP_USER_AGENT', '')[:200],
                "path": request.path,
                "method": request.method,
            })
            if hasattr(request, 'user') and request.user.is_authenticated:
                scope.set_user({
                    'id': request.user.id,
                    'email': request.user.email,
                    'username': request.user.username,
                })
        sentry_sdk.capture_exception(exc)


def _base_tags(context):
    view = context.get('view')
    request = context.get('request')
    return {
        'view': view.__class__.__name__ if view else 'unknown',
        'method': request.method if request else 'unknown',
    }


def custom_exception_handler(exc, context):
    request = context.get('request')
    view = context.get('view')
    tags = _base_tags(context)

    # 1. Excepciones que DRF sabe traducir (APIException, Http404, PermissionDenied)
    response = drf_exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, Throttled):
            response.data = {
                "code": ErrorCodes.THROTTLED,
                "detail": {
                    "message": "Has excedido el límite de peticiones permitidas.",
                    "retry_after_seconds": int(exc.wait) if exc.wait else 60,
                },
            }
            response["Retry-After"] = int(exc.wait) if exc.wait else 60
            return response

        raw_code = getattr(exc, "code", None) or getattr(exc, "default_code", None)
        code = DEFAULT_CODE_MAP.get(raw_code, raw_code.upper() if raw_code else ErrorCodes.UNKNOWN)

        response.data = {"code": code, "detail": response.data}
        return response

    # 2. Excepciones que DRF NO traduce (antes caían al catch-all del mixin)

    if OAuth2Error and isinstance(exc, OAuth2Error):
        logger.warning(f"OAuth error en {tags['view']}: {exc}", exc_info=True)
        if view and hasattr(view, 'log_auth_event'):
            try:
                view.log_auth_event(
                    'google_oauth_error',
                    user=None,
                    success=False,
                    error_type='OAuth2Error',
                    error_message=str(exc),
                    ip=request.META.get('REMOTE_ADDR') if request else None,
                )
            except Exception:
                pass
        _capture_to_sentry(exc, "warning", {**tags, 'error_type': 'oauth'}, request)
        return Response(
            {"code": ErrorCodes.OAUTH_ERROR, "detail": "Error de autenticación OAuth."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, DjangoValidationError):
        logger.warning(f"Django ValidationError en {tags['view']}: {exc}")
        detail = exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
        return Response(
            {"code": ErrorCodes.VALIDATION_ERROR, "detail": detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # OJO: IntegrityError es subclase de DatabaseError -> debe ir ANTES
    if isinstance(exc, IntegrityError):
        logger.info(f"IntegrityError en {tags['view']}: {exc}")
        msg = str(exc).lower()
        if 'unique' in msg or 'duplicate' in msg:
            code, http_status = ErrorCodes.RESOURCE_EXISTS, status.HTTP_409_CONFLICT
        elif 'foreign key' in msg:
            code, http_status = ErrorCodes.INVALID_REFERENCE, status.HTTP_400_BAD_REQUEST
        else:
            code, http_status = ErrorCodes.DATA_INTEGRITY_ERROR, status.HTTP_400_BAD_REQUEST
        return Response({"code": code, "detail": "Error de integridad de datos."}, status=http_status)

    if isinstance(exc, DatabaseError):
        logger.error(f"DatabaseError en {tags['view']}: {exc}", exc_info=True)
        _capture_to_sentry(exc, "error", {**tags, 'error_type': 'database'}, request)
        return Response(
            {"code": ErrorCodes.DATABASE_ERROR, "detail": "Error de base de datos."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, SMTPException):
        logger.warning(f"SMTPException en {tags['view']}: {exc}", exc_info=True)
        _capture_to_sentry(exc, "warning", {**tags, 'error_type': 'email'}, request)
        return Response(
            {"code": ErrorCodes.SERVER_ERROR, "detail": "Notificación por correo pendiente."},
            status=status.HTTP_200_OK,
        )

    # Timeout y ConnectionError son subclases de RequestException -> deben ir antes
    if isinstance(exc, Timeout):
        logger.warning(f"Timeout en {tags['view']}: {exc}", exc_info=True)
        _capture_to_sentry(exc, "warning", {**tags, 'error_type': 'timeout'}, request)
        return Response(
            {"code": ErrorCodes.SERVICE_TIMEOUT, "detail": "Servicio externo no respondió a tiempo."},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, ConnectionError):
        logger.error(f"ConnectionError en {tags['view']}: {exc}", exc_info=True)
        _capture_to_sentry(exc, "error", {**tags, 'error_type': 'connection'}, request)
        return Response(
            {"code": ErrorCodes.SERVICE_UNAVAILABLE, "detail": "Servicio externo no disponible."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, RequestException):
        logger.error(f"RequestException en {tags['view']}: {exc}", exc_info=True)
        _capture_to_sentry(exc, "error", {**tags, 'error_type': 'external_api'}, request)
        return Response(
            {"code": ErrorCodes.EXTERNAL_API_ERROR, "detail": "Error al comunicarse con servicio externo."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # 3. Cualquier otra cosa: error genuinamente inesperado.
    # Se maneja aquí mismo (no se retorna None) para que SIEMPRE pase
    # por StandardJSONRenderer con el mismo envelope, y para no duplicar
    # el reporte a Sentry vía la integración automática de Django.
    logger.critical(f"Error inesperado en {tags['view']}: {exc.__class__.__name__}", exc_info=True)
    _capture_to_sentry(exc, "error", {**tags, 'error_type': 'unexpected'}, request)
    return Response(
        {"code": ErrorCodes.UNEXPECTED_ERROR, "detail": "Ocurrió un error inesperado."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )