"""
Vistas para restablecimiento de contraseña.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from auth.base import BaseAuthenticationView
from auth.docs.schemas import CHANGE_PASSWORD, PASSWORD_RESET_CONFIRM, PASSWORD_RESET_REQUEST
from auth.serializers import (
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer
)
from auth.services import PasswordResetService, ChangePasswordService
from drf_spectacular.utils import extend_schema

from core.docs.schema_utils import auto_schema
from core.responses.messages import AuthMessages, UserMessages
from rest_framework.permissions import IsAuthenticated

@auto_schema(**PASSWORD_RESET_REQUEST)
class PasswordResetRequestView(BaseAuthenticationView, generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        PasswordResetService.request_reset(email, request)

        # Log genérico (sin revelar si existe)
        self.log_auth_event(
            'password_reset_requested',
            success=True,
            email_provided=True
        )

        return Response(
            {"detail": UserMessages.EMAIL_SENT_IF_EXISTS},
            status=status.HTTP_200_OK
        )


@auto_schema(**PASSWORD_RESET_CONFIRM)
class PasswordResetConfirmView(BaseAuthenticationView, generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = PasswordResetService.confirm_reset(
            uidb64=serializer.validated_data['uidb64'],
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password']
        )

        self.log_auth_event(
            'password_reset_completed',
            user=user,
            success=True
        )

        return Response(
            {'detail': AuthMessages.PASSWORD_RESET_SUCCESS},
            status=status.HTTP_200_OK
        )


@auto_schema(**CHANGE_PASSWORD)
class ChangePasswordView(BaseAuthenticationView, generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ChangePasswordService.change_password(
            user=request.user,
            current_password=serializer.validated_data['current_password'],
            new_password=serializer.validated_data['new_password'],
        )

        self.log_auth_event(
            'password_changed',
            user=request.user,
            success=True
        )

        return Response(
            {'detail': AuthMessages.PASSWORD_CHANGED_SUCCESS},
            status=status.HTTP_200_OK
        )