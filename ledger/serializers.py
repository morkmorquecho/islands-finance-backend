from rest_framework import serializers

from portfolio.models import Island
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    island = serializers.PrimaryKeyRelatedField(queryset=Island.objects.none())

    class Meta:
        model = Transaction
        fields = [
            "id", "island", "type", "date",
            "amount", "quantity", "price_at_tx",
            "category", "note", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            # a user can only post transactions against their own islands
            self.fields["island"].queryset = Island.objects.filter(user=request.user)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, attrs):
        island = attrs.get("island", getattr(self.instance, "island", None))
        tx_type = attrs.get("type", getattr(self.instance, "type", None))
        amount = attrs.get("amount", getattr(self.instance, "amount", None))
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", None))
        price_at_tx = attrs.get("price_at_tx", getattr(self.instance, "price_at_tx", None))
        category = attrs.get("category", getattr(self.instance, "category", None))

        if island is None:
            return attrs  # let the required-field error surface first

        cash_types = {Transaction.Type.DEPOSIT, Transaction.Type.WITHDRAWAL,
                      Transaction.Type.EXPENSE}
        asset_types = {Transaction.Type.BUY, Transaction.Type.SELL}

        if island.kind == Island.Kind.CASH:
            if tx_type not in cash_types:
                raise serializers.ValidationError(
                    {"type": f"Cash islands only accept: {', '.join(cash_types)}."}
                )
            if amount is None:
                raise serializers.ValidationError(
                    {"amount": "Required for cash island transactions."}
                )
            if quantity is not None or price_at_tx is not None:
                raise serializers.ValidationError(
                    "quantity/price_at_tx are not applicable to cash islands."
                )

        elif island.kind == Island.Kind.ASSET:
            if tx_type not in asset_types:
                raise serializers.ValidationError(
                    {"type": f"Asset islands only accept: {', '.join(asset_types)}."}
                )
            if quantity is None or price_at_tx is None:
                raise serializers.ValidationError(
                    "quantity and price_at_tx are both required for asset island transactions."
                )
            if amount is not None:
                raise serializers.ValidationError(
                    "amount is not applicable to asset islands, use quantity/price_at_tx."
                )

        if tx_type != Transaction.Type.EXPENSE and category:
            raise serializers.ValidationError(
                {"category": "Only allowed when type='expense'."}
            )

        return attrs