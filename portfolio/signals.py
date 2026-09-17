from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Module, Island


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_cash(sender, instance, created, **kwargs):
    if not created:
        return

    module, _ = Module.objects.get_or_create(
        user=instance,
        system_key="cash",
        defaults={
            "name": "Efectivo",
            "type": Module.Type.CASH,
            "order": 0,
        },
    )

    Island.objects.get_or_create(
        user=instance,
        system_key="cash",
        defaults={
            "module": module,
            "name": "Efectivo",
            "kind": Island.Kind.CASH,
            "currency": Island.Currency.MXN,
            "color": "#22C55E",
        },
    )