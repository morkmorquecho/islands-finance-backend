from rest_framework import serializers

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
    class Meta:
        model = Module
        fields = ["id", "name", "type", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        # user is never trusted from the client, always taken from the request
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class IslandSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.none())
    template = serializers.PrimaryKeyRelatedField(
        queryset=IslandTemplate.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Island
        fields = [
            "id", "module", "template", "name", "kind", "currency", "symbol",
            "interest_type", "annual_rate", "color", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            # a user can only attach an island to their own module
            self.fields["module"].queryset = Module.objects.filter(user=request.user)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, attrs):
        kind = attrs.get("kind", getattr(self.instance, "kind", None))
        currency = attrs.get("currency", getattr(self.instance, "currency", None))
        symbol = attrs.get("symbol", getattr(self.instance, "symbol", None))

        if kind == Island.Kind.CASH and not currency:
            raise serializers.ValidationError(
                {"currency": "Required for cash islands."}
            )
        if kind == Island.Kind.ASSET and not symbol:
            raise serializers.ValidationError(
                {"symbol": "Required for asset islands."}
            )
        return attrs