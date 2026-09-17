from decimal import Decimal

from rest_framework import serializers

from interest_engine.services import get_island_summary
from .models import IslandTemplate, Module, Island


class IslandTemplateSerializer(serializers.ModelSerializer):
    """Read-only for regular users — templates are admin-managed."""

    class Meta:
        model = IslandTemplate
        fields = [
            "id", "name", "kind", "symbol",
            "default_rate", "logo_url", "color",
        ]
        read_only_fields = fields


class ModuleSerializer(serializers.ModelSerializer):
    total_value = serializers.SerializerMethodField()
    has_unavailable_prices = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ["id", "name", "type", "order", "total_value",
                  "has_unavailable_prices", "created_at", "updated_at"]
        read_only_fields = ["id", "total_value", "has_unavailable_prices",
                            "created_at", "updated_at", "is_system"]

    def get_total_value(self, obj):
        total = Decimal("0")
        for island in obj.islands.all():
            value = get_island_summary(island).get("value_base")
            if value is not None:
                total += value
        return total

    def get_has_unavailable_prices(self, obj):
        return any(
            get_island_summary(island).get("price_unavailable")
            for island in obj.islands.all()
            if island.kind == "asset"
        )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class IslandSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.none())
    template = serializers.PrimaryKeyRelatedField(
        queryset=IslandTemplate.objects.all(), required=False, allow_null=True
    )
    name = serializers.CharField(required=False)
    kind = serializers.ChoiceField(choices=Island.Kind.choices, required=False)
    asset_type = serializers.ChoiceField(
        choices=Island.AssetType.choices, required=False, allow_null=True
    )
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Island
        fields = [
            "id", "module", "template", "name", "kind", "currency", "symbol",
            "asset_type", "interest_type", "annual_rate", "color", "summary",
            "created_at", "updated_at","mic_code",
        ]
        read_only_fields = ["id", "summary", "created_at", "updated_at", "is_system"]

    def get_summary(self, obj):
        return get_island_summary(obj)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            self.fields["module"].queryset = Module.objects.filter(user=request.user)


    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user

        template = validated_data.get("template")
        if template is not None:
            validated_data.setdefault("kind", template.kind)
            validated_data.setdefault("name", template.name)
            validated_data.setdefault("color", template.color)
            if template.kind == Island.Kind.CASH:
                validated_data.setdefault("annual_rate", template.default_rate)
            elif template.kind == Island.Kind.ASSET:
                validated_data.setdefault("symbol", template.symbol)
                validated_data.setdefault("asset_type", template.asset_type)  # <-- nuevo

        return super().create(validated_data)


    def validate(self, attrs):
        template = attrs.get("template")
        kind = attrs.get("kind") \
            or (template.kind if template else None) \
            or getattr(self.instance, "kind", None)

        if kind is None:
            raise serializers.ValidationError({"kind": "Required when no template is given."})
        if not attrs.get("name") and not template and not self.instance:
            raise serializers.ValidationError({"name": "Required when no template is given."})

        currency = attrs.get("currency", getattr(self.instance, "currency", None))
        symbol = attrs.get("symbol") \
            or (template.symbol if template else None) \
            or getattr(self.instance, "symbol", None)
        asset_type = attrs.get("asset_type") \
            or (template.asset_type if template else None) \
            or getattr(self.instance, "asset_type", None)

        if kind == Island.Kind.CASH and not currency:
            raise serializers.ValidationError({"currency": "Required for cash islands."})
        if kind == Island.Kind.ASSET:
            if not symbol:
                raise serializers.ValidationError(
                    {"symbol": "Required for asset islands (or pick a template that has one)."}
                )
            if not asset_type:
                raise serializers.ValidationError(
                    {"asset_type": "Required for asset islands (crypto or stock)."}
                )
        return attrs