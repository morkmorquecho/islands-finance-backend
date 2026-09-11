from rest_framework import serializers

from portfolio.models import Island
from ledger.models import Transaction
from .models import Goal, GoalCompletion


class GoalCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalCompletion
        fields = [
            "id", "goal", "expected_date", "completed_date",
            "actual_amount", "transaction",
        ]
        read_only_fields = ["id", "goal", "expected_date"]


class GoalSerializer(serializers.ModelSerializer):
    island = serializers.PrimaryKeyRelatedField(queryset=Island.objects.none())

    class Meta:
        model = Goal
        fields = [
            "id", "island", "target_amount", "frequency_days",
            "start_date", "active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            # a user can only attach a goal to their own island
            self.fields["island"].queryset = Island.objects.filter(user=request.user)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class GoalCompletionMarkSerializer(serializers.Serializer):
    """Payload to mark a specific expected period as fulfilled.

    Two ways to use this:
    - `transaction_id` given: link an existing deposit the user already
      logged in the ledger (no new transaction is created — avoids double-
      counting the money).
    - `transaction_id` omitted: a new deposit Transaction is created
      automatically for `actual_amount` (or the goal's target_amount if not
      given) and then linked. This is what makes "marking complete" mean
      something financially, instead of being just a label.
    """
    expected_date = serializers.DateField()
    transaction_id = serializers.PrimaryKeyRelatedField(
        queryset=Transaction.objects.none(), source="transaction",
        required=False, allow_null=True,
    )
    actual_amount = serializers.DecimalField(
        max_digits=18, decimal_places=2, required=False, allow_null=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            # only allow linking a transaction that belongs to the user
            self.fields["transaction_id"].queryset = Transaction.objects.filter(
                user=request.user
            )