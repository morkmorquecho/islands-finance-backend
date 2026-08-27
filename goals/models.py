import uuid
from django.conf import settings
from django.db import models

from core.models import BaseModel
from portfolio.models import  Island
from ledger.models import Transaction


class Goal(BaseModel):
    """A recurring saving rule, e.g. 'deposit $1500 every 15 days into Nu'.
    This is intent/plan only — it never moves money by itself.
    """
    island = models.ForeignKey(Island, on_delete=models.CASCADE, related_name="goals")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="goals")
    target_amount = models.DecimalField(max_digits=18, decimal_places=2)
    frequency_days = models.PositiveIntegerField(help_text="e.g. 15 for biweekly")
    start_date = models.DateField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.target_amount} every {self.frequency_days}d -> {self.island_id}"


class GoalCompletion(BaseModel):
    """One expected period for a Goal, and whether it was fulfilled.
    Rows can be generated on-read (no cron needed) by walking
    start_date + n*frequency_days up to today; persisted once
    marked completed so history is queryable (e.g. 'compliance rate').
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="completions")
    expected_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    actual_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name="goal_completions")

    class Meta:
        ordering = ["expected_date"]
        unique_together = ("goal", "expected_date")

    def __str__(self):
        status = "done" if self.completed_date else "pending"
        return f"{self.goal_id} @ {self.expected_date} [{status}]"