import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Register the Telegram webhook. Run after the first deploy or whenever the URL changes."

    def add_arguments(self, parser):
        parser.add_argument("--url", required=True,
                            help="Public HTTPS URL, e.g. https://api.example.com/api/telegram/webhook/")
        parser.add_argument("--keep-pending", action="store_true",
                            help="Do not drop updates queued while the webhook was down")

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_WEBHOOK_SECRET:
            raise CommandError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET first.")

        response = requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook",
            json={
                "url": options["url"],
                "secret_token": settings.TELEGRAM_WEBHOOK_SECRET,
                "allowed_updates": ["message", "callback_query"],
                "drop_pending_updates": not options["keep_pending"],
            },
            timeout=10,
        )
        if not response.ok or not response.json().get("ok"):
            raise CommandError(f"Telegram rejected the webhook: {response.text}")
        self.stdout.write(self.style.SUCCESS(response.json().get("description", "Webhook set")))
