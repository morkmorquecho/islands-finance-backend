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
    # Not required at the API level: when `template` is given, these are
    # auto-filled in create() from the template. Still required overall —
    # validate() enforces that, one way or another, they end up set.
    name = serializers.CharField(required=False)
    kind = serializers.ChoiceField(choices=Island.Kind.choices, required=False)

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

        template = validated_data.get("template")
        if template is not None:
            # Auto-fill from template so the user doesn't re-type known data.
            # These are COPIED (not referenced live) — see model docstring:
            # if the template's default rate changes later, existing islands
            # keep the rate they were created with.
            validated_data.setdefault("kind", template.kind)
            validated_data.setdefault("name", template.name)
            validated_data.setdefault("color", template.color)
            if template.kind == Island.Kind.CASH:
                validated_data.setdefault("annual_rate", template.default_rate)
            elif template.kind == Island.Kind.ASSET:
                validated_data.setdefault("symbol", template.symbol)

        return super().create(validated_data)

    def validate(self, attrs):
        template = attrs.get("template")
        # Effective kind: explicit value wins, otherwise fall back to the
        # template's kind, otherwise the existing instance's (on update).
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

        if kind == Island.Kind.CASH and not currency:
            raise serializers.ValidationError(
                {"currency": "Required for cash islands."}
            )
        if kind == Island.Kind.ASSET and not symbol:
            raise serializers.ValidationError(
                {"symbol": "Required for asset islands (or pick a template that has one)."}
            )
        return attrs