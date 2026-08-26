from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)

from auth.docs.request import RESEND_CONFIRMATION_EMAIL_REQUEST
from auth.docs.response import JWT_SUCCES_RESPONSE
from auth.serializers import GoogleIDTokenSerializer, UserCreateSerializer

from core.docs.response import (
    RESPONSE_400_OAUTH,
    RESPONSE_401,
    RESPONSE_404,
    RESPONSE_409,
    response_400,
    response_429,
)

from core.responses.messages import AuthMessages, UserMessages


THROTTLE_HOUR = 3600


# ========================================== JWT VIEWS ================================================

LOGIN_SCHEMA = dict(
    tags=["auth"],
    summary="Iniciar Sesión",
    description=(
        "Autenticación con **username o email** + contraseña.\n\n"
        "Retorna access y refresh tokens.\n\n"
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "example": "chupapi muñaño",
                    "description": "Username o email del usuario",
                },
                "email": {
                    "type": "string",
                    "example": "usuario@example.com",
                    "description": "Email del usuario (alternativa a username)",
                },
                "password": {
                    "type": "string",
                    "example": "password123",
                },
            },
            "required": ["password"],
        }
    },
    responses={
        200: JWT_SUCCES_RESPONSE,
        400: lambda source: response_400(source),
        401: RESPONSE_401,
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)


TOKEN_REFRESH = dict(
    summary="Renovar access token",
    description=(
        "Genera un nuevo **access token** usando un **refresh token válido**.\n\n"
    ),
    tags=["auth"],
)


TOKEN_VERIFY = dict(
    summary="Verificar token JWT",
    tags=["auth"],
)


LOGOUT = dict(
    tags=["auth"],
    summary="Cerrar sesión",
    description=(
        "Invalida el refresh token agregándolo a la blacklist.\n\n"
    ),
    responses={
        200: OpenApiResponse(description="Logout exitoso"),
        400: OpenApiResponse(description="Token inválido"),
    },
)


# ========================================== SOCIAL VIEWS ================================================

GOOGLE = dict(
    summary="Autenticación con Google",
    tags=["auth"],
    description=(
        "El endpoint espera recibir el id token. "
        "Autentica o registra usuarios mediante Google.\n\n"
        "El email se verifica automáticamente.\n\n"
    ),
    request=GoogleIDTokenSerializer,
    responses={
        200: JWT_SUCCES_RESPONSE,
        400: RESPONSE_400_OAUTH,
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)


FACEBOOK = extend_schema(
    summary="Autenticación con Facebook",
    tags=["auth"],
    description=(
        "Autentica o registra usuarios mediante Facebook.\n\n"
        "El email se verifica automáticamente.\n\n"
    ),
    request=GoogleIDTokenSerializer,
    responses={
        200: JWT_SUCCES_RESPONSE,
        400: RESPONSE_400_OAUTH,
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)


# ========================================== PASSWORD VIEWS ================================================

PASSWORD_RESET_REQUEST = dict(
    summary="Solicitar restablecimiento de contraseña",
    tags=["auth"],
    description=(
        "Solicita el restablecimiento de contraseña.\n\n"
        "Por seguridad, no revela si el email existe.\n\n"
    ),
    responses={
        200: OpenApiResponse(
            description=UserMessages.EMAIL_SENT_IF_EXISTS
        ),
        400: lambda source: response_400(source),
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)


PASSWORD_RESET_CONFIRM = dict(
    summary="Confirmar nueva contraseña",
    tags=["auth"],
    description=(
        "Actualiza la contraseña usando el token de restablecimiento.\n\n"
    ),
    responses={
        200: OpenApiResponse(
            description=AuthMessages.PASSWORD_RESET_SUCCESS
        ),
        400: lambda source: response_400(source),
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)


CHANGE_PASSWORD = {
    "summary": "Cambiar contraseña",
    "description": (
        "Permite a usuarios autenticados cambiar su contraseña. "
        "Es necesario incluir su contraseña actual."
    ),
    "tags": ["auth"],
    "responses": {
        200: OpenApiResponse(
            description=AuthMessages.PASSWORD_RESET_SUCCESS
        ),
        400: lambda source: response_400(source),
        401: RESPONSE_401,
    },
}


# ========================================== USER VIEWS ================================================

REGISTRATION = dict(
    summary="Registrarse/Crear usuario",
    tags=["auth"],
    description=(
        "Crea un nuevo usuario en estado inactivo.\n\n"
        "Se envía un correo de verificación para activar la cuenta.\n\n"
        "Accesible para cualquier usuario (registro público).\n\n"
    ),
    request=UserCreateSerializer,
    responses={
        201: OpenApiResponse(
            description=UserMessages.USER_CREATED
        ),
        400: lambda source: response_400(source),
        409: RESPONSE_409,
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)


VERIFY_USER = dict(
    summary="Verificar Cuenta",
    tags=["auth"],
    description=(
        "Este endpoint se utiliza después de crear un usuario.\n\n"
        "Confirma la cuenta de un usuario mediante un token "
        "enviado por correo electrónico.\n\n"
        "El token se envía como query parameter y se valida "
        "para activar la cuenta.\n\n"
        "Este endpoint no requiere autenticación.\n\n"
    ),
    parameters=[
        OpenApiParameter(
            name="token",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Token de verificación enviado por correo",
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            description=UserMessages.EMAIL_SENT_IF_EXISTS
        ),
        400: lambda source: response_400(source),
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)


RESEND_TOKEN = dict(
    summary="Reenviar correo de verificación",
    tags=["auth"],
    description=(
        "Se reenvía al usuario el token para verificar su cuenta "
        "(activarla) por correo.\n\n"
        "Pensado para ser utilizado en casos donde al usuario "
        "no le llegó este correo al crear su cuenta.\n\n"
    ),
    responses={
        200: OpenApiResponse(
            description=UserMessages.VERIFICATION_EMAIL_SENT
        ),
        400: lambda source: response_400(source),
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
    request=RESEND_CONFIRMATION_EMAIL_REQUEST,
)


VERIFY_EMAIL = dict(
    summary="Verificar Cuenta/EMAIL",
    tags=["users"],
    description=(
        "Este endpoint se utiliza como método de seguridad para "
        "confirmar tokens provenientes de un correo.\n\n"
        "Como el caso de confirmar el correo de un usuario después "
        "de crearlo o modificar su correo.\n\n"
        "Confirma la cuenta de un usuario mediante un token "
        "enviado por correo electrónico.\n\n"
        "El token se envía como query parameter y se valida "
        "para activar la cuenta.\n\n"
        "Este endpoint no requiere autenticación.\n\n"
    ),
    parameters=[
        OpenApiParameter(
            name="token",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Token de verificación enviado por correo",
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            description=UserMessages.USER_VERIFIED
        ),
        400: lambda source: response_400(source),
        404: RESPONSE_404,
        429: lambda source: response_429(THROTTLE_HOUR, source),
    },
)