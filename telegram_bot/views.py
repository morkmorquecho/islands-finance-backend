import hmac
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import TelegramLink

logger = logging.getLogger(__name__)


class TelegramWebhookView(APIView):
    """Called by Telegram. Authenticated with the secret_token set in setWebhook."""
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    def post(self, request):
        expected = (settings.TELEGRAM_WEBHOOK_SECRET or "").encode()
        received = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "").encode()
        if not expected or not hmac.compare_digest(received, expected):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if isinstance(request.data, dict):
            try:
                services.handle_update(request.data)
            except Exception:
                # Always answer 200: Telegram would retry the same update endlessly.
                logger.exception("Failed to process Telegram update")
        return Response({"ok": True})


class TelegramLinkCodeView(APIView):
    """POST -> generate a single-use code (and deep link) to connect Telegram."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = services.create_link_code(request.user)
        username = settings.TELEGRAM_BOT_USERNAME
        return Response({
            "code": code,
            "expires_in": int(services.LINK_CODE_TTL.total_seconds()),
            "deep_link": f"https://t.me/{username}?start={code}" if username else None,
        })


class TelegramLinkView(APIView):
    """GET -> link status. DELETE -> unlink."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        link = TelegramLink.objects.select_related("default_island").filter(user=request.user).first()
        if link is None:
            return Response({"linked": False})
        island = link.default_island
        return Response({
            "linked": True,
            "telegram_username": link.telegram_username or None,
            "default_island": {"id": str(island.pk), "name": island.name} if island else None,
        })

    def delete(self, request):
        TelegramLink.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
