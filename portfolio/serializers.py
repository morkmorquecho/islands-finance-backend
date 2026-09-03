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

    class Meta:
        model = Module
        fields = ["id", "name", "type", "order", "total_value",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "total_value", "created_at", "updated_at"]

    def get_total_value(self, obj):
        # Computed on every read, never stored — sums each island's own
        # on-read value (interest_engine). Cheap at this project's scale;
        # see project notes on why we don't cache/persist this.
        return sum(
            (get_island_summary(island)["value"] for island in obj.islands.all()),
            start=0,
        )

    def create(self, validated_data):
        # user is never trusted from the client, always taken from the request
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
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "summary", "created_at", "updated_at"]

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
                # asset_type NOT on the template — user must supply it,
                # since a symbol like "SPY" vs a crypto ticker isn't
                # inferable from the template alone.

        return super().create(validated_data)

    def validate(self, attrs):
        template = attrs.get("template")
        kind = attrs.get("kind") \
            or (template.kind if template else None) \
            or getattr(self.instance, "kind", None)

        if kind is None:
            raise serializers.ValidationError(
                {"kind": "Required when no template is given."}
            )
        if not attrs.get("name") and not template and not self.instance:
            raise serializers.ValidationError(
                {"name": "Required when no template is given."}
            )

        currency = attrs.get("currency", getattr(self.instance, "currency", None))
        symbol = attrs.get("symbol") \
            or (template.symbol if template else None) \
            or getattr(self.instance, "symbol", None)
        asset_type = attrs.get("asset_type", getattr(self.instance, "asset_type", None))

        if kind == Island.Kind.CASH and not currency:
            raise serializers.ValidationError(
                {"currency": "Required for cash islands."}
            )
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