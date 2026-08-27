import uuid
from django.conf import settings
from django.db import models

from core.models import BaseModel


class IslandTemplate(BaseModel):
    """Admin-managed catalog: Nu, Mercado Pago, S&P 500, Bitcoin, etc."""

    class Kind(models.TextChoices):
        CASH = "cash", "Cash"
        ASSET = "asset", "Asset"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    symbol = models.CharField(max_length=20, null=True, blank=True,
                               help_text="Ticker for asset kind, e.g. SPY, BTC-USD")
    default_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True,
                                        help_text="Suggested annual rate, cash kind only")
    logo_url = models.URLField(null=True, blank=True)
    color = models.CharField(max_length=7, default="#2563EB")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Module(BaseModel):
    """Top-level grouping: savings, emergency fund, investments, leisure, expenses."""

    class Type(models.TextChoices):
        SAVINGS = "savings", "Savings"
        EMERGENCY = "emergency", "Emergency"
        INVESTMENT = "investment", "Investment"
        LEISURE = "leisure", "Leisure"
        EXPENSES = "expenses", "Expenses"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="modules")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=Type.choices)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.name} ({self.user_id})"


class Island(BaseModel):
    """A single account/holding inside a module (e.g. 'Nu savings', 'Bitcoin')."""

    class Kind(models.TextChoices):
        CASH = "cash", "Cash"
        ASSET = "asset", "Asset"

    class InterestType(models.TextChoices):
        SIMPLE = "simple", "Simple"
        COMPOUND = "compound", "Compound"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="islands")
    # Denormalized on purpose: direct security filtering + RLS-friendly + avoids
    # joining through module on every query. See project notes on denormalization.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="islands")
    template = models.ForeignKey(IslandTemplate, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name="islands")
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    currency = models.CharField(max_length=10, null=True, blank=True,
                                 help_text="Cash islands, e.g. MXN, USD")
    symbol = models.CharField(max_length=20, null=True, blank=True,
                               help_text="Asset islands, e.g. BTC-USD, SPY")
    interest_type = models.CharField(max_length=10, choices=InterestType.choices,
                                      null=True, blank=True, help_text="Cash islands only")
    annual_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True,
                                       help_text="Current annual rate, cash islands only")
    color = models.CharField(max_length=7, default="#0EA5E9")

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} [{self.kind}]"