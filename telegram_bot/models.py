from django.conf import settings
from django.db import models

from core.models import BaseModel
from ledger.models import Transaction
from portfolio.models import Island


class TelegramLink(BaseModel):
    """Binds one Island Finance user to one private Telegram chat.
    Unlinking deletes the row, so a chat can be re-linked to another account.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="telegram_link")
    chat_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=64, blank=True)
    default_island = models.ForeignKey(Island, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name="+",
                                       help_text="Cash island used when the message has no @island")

    def __str__(self):
        return f"{self.user_id} <-> {self.chat_id}"


class TelegramLinkCode(BaseModel):
    """Single-use, short-lived code used to link a chat. Only the hash is stored."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="telegram_link_codes")
    code_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"link code for {self.user_id} (expires {self.expires_at})"


class PendingTransaction(BaseModel):
    """A parsed message waiting for the user to press ✅ or ❌."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"
        UNDONE = "undone", "Undone"

    link = models.ForeignKey(TelegramLink, on_delete=models.CASCADE, related_name="pending")
    island = models.ForeignKey(Island, on_delete=models.CASCADE, related_name="+")
    type = models.CharField(max_length=12)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    category = models.CharField(max_length=20, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="+")
    expires_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["link", "status"])]

    def __str__(self):
        return f"{self.type} {self.amount} [{self.status}]"


class TelegramUpdate(BaseModel):
    """Processed Telegram update ids, for idempotency against webhook retries.
    Rows can be purged after a few days.
    """
    update_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return str(self.update_id)
