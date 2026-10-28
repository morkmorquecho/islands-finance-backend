from django.urls import path

from .views import TelegramLinkCodeView, TelegramLinkView, TelegramWebhookView

urlpatterns = [
    path("webhook/", TelegramWebhookView.as_view(), name="telegram-webhook"),
    path("link-code/", TelegramLinkCodeView.as_view(), name="telegram-link-code"),
    path("link/", TelegramLinkView.as_view(), name="telegram-link"),
]
