from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from core.mixins import SentryErrorHandlerMixin, ViewSetSentryMixin
from core.permission import IsOwner
from core.responses.messages import UserMessages
from users.docs.schemas import  EMAIL_UPDATE
from users.serializers import EmailUpdateSerializer
from auth.services import UsersRegisterService
from core.services.email_service import EmailUpdatedEmail
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()

@EMAIL_UPDATE
class EmailUpdateAPIView(SentryErrorHandlerMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailUpdateSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = request.user
       
        
        # Si el email ya está registrado, solo avisar (no enviar email)
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": UserMessages.EMAIL_SENT_IF_EXISTS}, 
                status=status.HTTP_200_OK
            )
        
        # Si es un email nuevo, enviar confirmación
        confirm_url = UsersRegisterService.get_confirmation_url(user, email)
        EmailUpdatedEmail.send_email(
            to_email=email,
            confirm_url=confirm_url,
            nombre=user.username
        )
        self.logger.info(f'Enviando email de confirmación a {user.username} a su nuevo correo {email}')
        
        return Response(
            {"message": UserMessages.EMAIL_SENT_IF_EXISTS},
            status=status.HTTP_200_OK
        )


    
