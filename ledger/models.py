import uuid
from django.conf import settings
from django.db import models

from core.models import BaseModel
from portfolio.models import  Island


class Transaction(BaseModel):
    """Unified ledger entry. Replaces separate 'expenses' table:
    an expense is simply type=EXPENSE with a category set.

    Cash islands use `amount`. Asset islands use `quantity` + `price_at_tx`.
    """

    class Type(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        EXPENSE = "expense", "Expense"
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"

    class Category(models.TextChoices):
        FOOD = "food", "Food"
        TRANSPORT = "transport", "Transport"
        SUBSCRIPTIONS = "subscriptions", "Subscriptions"
        HOUSING = "housing", "Housing"
        LEISURE = "leisure", "Leisure"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    island = models.ForeignKey(Island, on_delete=models.CASCADE, related_name="transactions")
    # Denormalized, same rationale as Island.user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="transactions")
    type = models.CharField(max_length=12, choices=Type.choices)
    date = models.DateField()

    # Cash islands
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    # Asset islands
    quantity = models.DecimalField(max_digits=24, decimal_places=8, null=True, blank=True)
    price_at_tx = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True,
                                       help_text="Asset price at time of transaction")

    # Only used when type = EXPENSE
    category = models.CharField(max_length=20, choices=Category.choices,
                                 null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["island", "date"]),
            models.Index(fields=["user", "date"]),
        ]

    def __str__(self):
        value = self.amount if self.amount is not None else self.quantity
        return f"{self.type} {value} on {self.date} ({self.island_id})"