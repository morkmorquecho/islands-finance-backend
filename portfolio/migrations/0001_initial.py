from decimal import Decimal

from django.db import migrations


def seed_island_templates(apps, schema_editor):
    IslandTemplate = apps.get_model("portfolio", "IslandTemplate")

    templates = [
        {
            "name": "Mercado Pago",
            "kind": "cash",
            "symbol": None,
            "default_rate": Decimal("0.1200"),
            "logo_url": None,
            "color": "#01AEF2",
        },
        {
            "name": "Nu",
            "kind": "cash",
            "symbol": None,
            "default_rate": Decimal("0.1300"),
            "logo_url": None,
            "color": "#8A40DA",
        },
        {
            "name": "Revolut",
            "kind": "cash",
            "symbol": None,
            "default_rate": Decimal("0.1500"),
            "logo_url": None,
            "color": "#000000",
        },
        {
            "name": "DiDi",
            "kind": "cash",
            "symbol": None,
            "default_rate": Decimal("0.1500"),
            "logo_url": None,
            "color": "#FF7F41",
        },
        {
            "name": "Openbank",
            "kind": "cash",
            "symbol": None,
            "default_rate": Decimal("0.1300"),
            "logo_url": None,
            "color": "#EC0000",
        },
        {
            "name": "Bitcoin",
            "kind": "asset",
            "symbol": "BTC",
            "default_rate": None,
            "logo_url": None,
            "color": "#F7931A",
        },
        {
            "name": "VOO S&P 500",
            "kind": "asset",
            "symbol": "VOO",
            "default_rate": None,
            "logo_url": None,
            "color": "#424EE0",
        },
    ]

    IslandTemplate.objects.bulk_create(
        [IslandTemplate(**template) for template in templates]
    )


def remove_island_templates(apps, schema_editor):
    IslandTemplate = apps.get_model("portfolio", "IslandTemplate")

    IslandTemplate.objects.filter(
        name__in=[
            "Mercado Pago",
            "Nu",
            "Revolut",
            "DiDi",
            "Openbank",
            "Bitcoin",
            "VOO S&P 500",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "000X_previous_migration"),
    ]

    operations = [
        migrations.RunPython(
            seed_island_templates,
            remove_island_templates,
        ),
    ]