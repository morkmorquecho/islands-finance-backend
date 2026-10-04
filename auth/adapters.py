import re
from allauth.account.models import EmailAddress

import unicodedata
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.contrib.auth import get_user_model
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from google.oauth2 import id_token
from django.conf import settings
from google.auth.transport import requests as google_requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
User = get_user_model()

class CustomFacebookOAuth2Adapter(FacebookOAuth2Adapter):
    """Adaptador profesional con generación de username único garantizado"""
    
    def complete_login(self, request, app, token, **kwargs):
        login = super().complete_login(request, app, token, **kwargs)
        
        extra_data = login.account.extra_data        
        # Solo generar username si el usuario es nuevo o no tiene username válido
        if login.user and (not login.user.pk or not login.user.username or login.user.username.strip() == ''):
            username = self._generate_unique_username(extra_data, User)
            login.user.username = username
        
        return login
    
    def _generate_unique_username(self, data, User):
        """
        Genera un username único garantizado.
        """
        base_username = self._get_base_username_from_name(data)
        
        if not base_username:
            email = data.get('email', '')
            if email and '@' in email:
                base_username = email.split('@')[0]
                base_username = self._sanitize_username(base_username)
        
        if not base_username:
            return f"fb{data.get('id', 'user')}"
        
        return self._ensure_unique_username(base_username, User)
    
    def _get_base_username_from_name(self, data):
        """Extrae y sanitiza el nombre para usar como base del username"""
        name = data.get('name', '').strip()
        if name:
            username = self._sanitize_username(name)
            if username:
                return username
        
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        if first_name or last_name:
            full_name = f"{first_name}{last_name}".strip()
            username = self._sanitize_username(full_name)
            if username:
                return username
        
        return None
    
    def _sanitize_username(self, name):
        """
        Sanitiza el nombre para convertirlo en username válido:
        - Normaliza Unicode (á→a, ñ→n)
        - Solo letras y números
        - Minúsculas
        - Máximo 30 caracteres (dejamos espacio para sufijos)
        """
        username = unicodedata.normalize('NFKD', name)
        username = username.encode('ascii', 'ignore').decode('ascii')
        
        username = username.lower()
        username = re.sub(r'[^a-z0-9]', '', username)
        
        username = username[:30]
        
        return username if username else None
    
    def _ensure_unique_username(self, base_username, User):
        """
        Garantiza que el username sea único agregando sufijo numérico.
        """
        username = base_username
        
        if not User.objects.filter(username=username).exists():
            return username
        
        counter = 1
        max_attempts = 9999  
        
        while counter < max_attempts:
            username = f"{base_username}{counter}"
            
            if not User.objects.filter(username=username).exists():
                return username
            
            counter += 1
        
        import time
        return f"{base_username}{int(time.time())}"
    


# accounts/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class AutoLinkSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        email = (sociallogin.user.email or '').strip().lower()
        if not email:
            return

        email_verified = any(
            e.verified and e.email.lower() == email
            for e in sociallogin.email_addresses
        ) or bool(sociallogin.account.extra_data.get('email_verified'))
        if not email_verified:
            return

        existing_user = User.objects.filter(email__iexact=email).first()
        if not existing_user:
            return

        # Google ya verificó este correo: marcarlo antes de que corran los stages
        address = EmailAddress.objects.filter(
            user=existing_user, email__iexact=email
        ).first()
        if address:
            if not address.verified:
                address.verified = True
                address.save(update_fields=['verified'])
        else:
            EmailAddress.objects.create(
                user=existing_user,
                email=email,
                verified=True,
                primary=not EmailAddress.objects.filter(
                    user=existing_user, primary=True
                ).exists(),
            )

        sociallogin.connect(request, existing_user)

    def save_user(self, request, sociallogin, form=None):
        if sociallogin.user.pk:
            return sociallogin.user
        return super().save_user(request, sociallogin, form)
    
class GoogleIDTokenAdapter(GoogleOAuth2Adapter):
    """
    Verifica el ID Token de Google localmente (sin llamar a userinfo).
    Extrae los claims del JWT directamente.
    """
    def get_client_id(self):
        return settings.GOOGLE_OAUTH2_CLIENT_ID
    
    def validate_token(self, token):
        """Valida que el token venga de cualquiera de nuestras apps."""
        import google.auth.transport.requests
        from google.oauth2 import id_token
        
        allowed_ids = settings.GOOGLE_OAUTH2_ALLOWED_CLIENT_IDS
        
        for client_id in allowed_ids:
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    google.auth.transport.requests.Request(),
                    client_id
                )
                return idinfo
            except ValueError:
                continue
        
        raise ValueError("Token no válido para ningún client_id registrado")

    def complete_login(self, request, app, token, **kwargs):
        id_token_str = token.token

        try:
            idinfo = self.validate_token(id_token_str) 
        except ValueError as e:
            raise OAuth2Error(f"ID token inválido: {e}")

        extra_data = {
            'id': idinfo['sub'],
            'email': idinfo.get('email'),
            'verified_email': idinfo.get('email_verified', False),
            'name': idinfo.get('name'),
            'given_name': idinfo.get('given_name'),
            'family_name': idinfo.get('family_name'),
            'picture': idinfo.get('picture'),
        }

        return self.get_provider().sociallogin_from_response(request, extra_data)