import uuid
from django.db import models


class PriceCache(models.Model):
    """Optional DB cache for asset prices, only needed if you're not using
    Redis/in-memory caching. Keeps calls to the public market API cheap.
    Not required by the core data model — safe to skip for MVP.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20, db_index=True)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fetched_at"]

    def __str__(self):
        return f"{self.symbol}: {self.price} @ {self.fetched_at}"